#!/usr/bin/env python3
"""Read an idea's state on GitHub and name its dev-flow stage and next action.

  python3 state.py OWNER/REPO#N [--record FILE]   (or the issue URL instead of OWNER/REPO#N)

Prints one JSON object: the stage, the evidence for it, the other stages that
also matched, the tickets, the doc PRs, the proposal doc, and the next action
as steps, each with who takes it (owner or agent). Read-only: GET requests
through `gh api` only. --record also writes every response it read to FILE,
keyed by API path, which is the fixture format test_state.py replays.

Stages and markers are D4 of docs/proposals/status.md (dev-flow). When several
match, the first in PRECEDENCE wins (the proposal's Shape 2).
"""
import base64
import json
import re
import subprocess
import sys

PRECEDENCE = [
    "reopened",
    "revision in progress",
    "done",
    "in progress",
    "decided, full path",
    "proposal drafted",
    "decided, awaiting proposal",
    "decided, short path",
    "questions open",
]
PROPOSALS = "docs/proposals"
READY, NEEDS_DECISION = "ready-for-agent", "needs-decision"


class GhError(Exception):
    pass


def gh_fetch(path):
    """GET one API path through gh. Lists are paginated and merged; a 404 is None."""
    p = subprocess.run(["gh", "api", "--paginate", path], capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        msg = (p.stderr or p.stdout).strip()
        if "HTTP 404" in msg:
            return None
        raise GhError(f"{path}: {msg.splitlines()[-1] if msg else 'unknown error'}")
    # --paginate prints one JSON document per page, back to back.
    decoder, text, pos, pages = json.JSONDecoder(), p.stdout, 0, []
    while True:
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if pos >= len(text):
            break
        page, pos = decoder.raw_decode(text, pos)
        pages.append(page)
    if len(pages) == 1:
        return pages[0]
    if pages and all(isinstance(pg, list) for pg in pages):
        return [item for pg in pages for item in pg]
    return pages[0] if pages else None


# --- reading markdown -------------------------------------------------------

def strip_details(text):
    """Superseded decisions sit in <details> blocks; their markers no longer count."""
    return re.sub(r"<details>.*?</details>", "", text or "", flags=re.S | re.I)


def section(text, title_pattern, level=2):
    """Body of the first heading at `level` whose title matches, up to the next heading at that level or above."""
    lines, out, inside = (text or "").splitlines(), [], False
    head = re.compile(r"^(#{1,%d})\s+(.*?)\s*$" % level)
    for line in lines:
        m = head.match(line)
        if m:
            if inside:
                break
            if len(m.group(1)) == level and re.fullmatch(title_pattern, m.group(2), re.I):
                inside = True
            continue
        if inside:
            out.append(line)
    return "\n".join(out).strip() if inside else None


def is_open(content):
    """A section lists something still open: anything but nothing or "None."."""
    if content is None:
        return False
    text = re.sub(r"<!--.*?-->", "", content, flags=re.S).strip()
    return bool(text) and not re.match(r"none\b", text, re.I)


def skipped_in_record(record):
    """Questions a grill record lists as skipped or still open (any heading naming them)."""
    for level in (2, 3):
        for title in (r"open questions.*", r"skipped.*"):
            if is_open(section(record, title, level)):
                return True
    return False


def blocked_by(body):
    m = re.search(r"(?m)^Blocked by:(.*)$", body or "")
    return [int(n) for n in re.findall(r"#(\d+)", m.group(1))] if m else []


def doc_status(text):
    m = re.search(r"(?m)^Status: \*\*(.+?)\*\*", text or "")
    return m.group(1) if m else None


def reopened_line(text):
    """A decision reopened in the doc (`Status: reopened — …` under its heading), outside superseded blocks."""
    return bool(re.search(r"(?m)^Status: reopened\b", strip_details(text)))


def decoded(content):
    return base64.b64decode(content["content"]).decode("utf-8") if content and content.get("content") else ""


def numbers(nums):
    """#97–#99 for a run of three or more, else listed: #97, #98, #101."""
    nums, groups, i = sorted(nums), [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        if j - i >= 2:
            groups.append(f"#{nums[i]}–#{nums[j]}")
        else:
            groups.extend(f"#{n}" for n in nums[i:j + 1])
        i = j + 1
    return ", ".join(groups)


# --- reading GitHub ---------------------------------------------------------

def read(fetch, repo, n):
    r = f"repos/{repo}"
    issue = fetch(f"{r}/issues/{n}")
    if issue is None:
        raise GhError(f"{repo}#{n} not found")
    comments = fetch(f"{r}/issues/{n}/comments?per_page=100") or []
    subs = fetch(f"{r}/issues/{n}/sub_issues?per_page=100") or []
    flagged = fetch(f"{r}/issues?state=open&labels={NEEDS_DECISION}&per_page=100") or []

    refs = re.compile(r"(?i)\b(Refs|Closes|Fixes) #%d\b" % n)  # the forms `proposal` accepts
    doc_prs = []
    for pr in fetch(f"{r}/pulls?state=open&per_page=100") or []:
        if not refs.search(pr.get("body") or ""):
            continue
        files = [f["filename"] for f in fetch(f"{r}/pulls/{pr['number']}/files?per_page=100") or []]
        docs = [f for f in files if f.startswith(PROPOSALS + "/") and f.endswith(".md")]
        if not docs:
            continue  # a code PR that mentions the issue isn't a doc PR (D4)
        texts = {d: decoded(fetch(f"{r}/contents/{d}?ref={pr['head']['sha']}")) for d in docs}  # "" if deleted
        doc_prs.append({"number": pr["number"], "title": pr["title"],
                        "docs": {d: doc_status(t) for d, t in texts.items()},
                        "reopened": any(reopened_line(t) for t in texts.values())})

    doc = None
    source = re.compile(r"(?m)^Source: #%d\b" % n)
    for entry in fetch(f"{r}/contents/{PROPOSALS}") or []:
        if entry.get("type") != "file" or not entry["name"].endswith(".md"):
            continue
        text = decoded(fetch(f"{r}/contents/{entry['path']}"))
        if source.search(text):
            doc = {"path": entry["path"], "status": doc_status(text), "reopened": reopened_line(text)}
            break
    return issue, comments, subs, flagged, doc_prs, doc


# --- naming the stage -------------------------------------------------------

def compute(fetch, repo, n):
    issue, comments, subs, flagged, doc_prs, doc = read(fetch, repo, n)
    name = repo.split("/")[1]
    body = issue.get("body") or ""
    labels = [lb["name"] for lb in issue.get("labels", [])]
    parent = re.compile(r"(?m)^Parent: #%d\s*$" % n)
    open_subs = [s for s in subs if s["state"] == "open"]
    sub_numbers = {s["number"] for s in subs}
    needs = sorted({i["number"] for i in flagged if not i.get("pull_request")
                    and (i["number"] in sub_numbers or parent.search(i.get("body") or ""))}
                   | {s["number"] for s in open_subs if NEEDS_DECISION in [lb["name"] for lb in s.get("labels", [])]})
    records = [c for c in comments if (c.get("body") or "").startswith("## Decisions (grill")]
    record = records[-1]["body"] if records else None
    decided_doc = doc is not None and doc["status"] == "decided"

    open_questions = is_open(section(strip_details(body), r"open questions"))
    to_check = is_open(section(strip_details(body), r"to check"))
    short_decisions = re.search(r"(?m)^## Decisions\s*$", body) is not None

    ev = {}
    if needs or NEEDS_DECISION in labels or (doc and doc["reopened"]):
        ev["reopened"] = ([f"#{t} is labelled {NEEDS_DECISION}" for t in needs]
                          + ([f"#{n} is labelled {NEEDS_DECISION}"] if NEEDS_DECISION in labels else [])
                          + ([f"{doc['path']} has a Status: reopened line"] if doc and doc["reopened"] else []))
    if doc_prs and subs:
        ev["revision in progress"] = [f"doc PR {name}#{p['number']} is open" for p in doc_prs] + [f"{len(subs)} sub-issues exist"]
    if (subs and not open_subs) or issue["state"] == "closed":
        ev["done"] = [f"#{n} is closed"] if issue["state"] == "closed" else [f"all {len(subs)} sub-issues are closed"]
    if open_subs:
        ev["in progress"] = [f"{len(open_subs)} of {len(subs)} sub-issues are open: {numbers(s['number'] for s in open_subs)}"]
    if decided_doc and not subs:
        ev["decided, full path"] = [f"{doc['path']} on main says decided", "no sub-issues"]
    if doc_prs or (doc and not decided_doc):
        ev["proposal drafted"] = ([f"doc PR {name}#{p['number']} is open" for p in doc_prs]
                                  + ([f"{doc['path']} on main says {doc['status']}"] if doc and not decided_doc else []))
    if record and not doc and not doc_prs:
        ev["decided, awaiting proposal"] = ["a ## Decisions (grill, …) comment", "no proposal doc or doc PR"]
    if short_decisions and not open_questions and not to_check:
        ev["decided, short path"] = ["## Decisions in the body", "nothing under Open questions or To check"]
    if (open_questions or (record and skipped_in_record(record))) and not doc and not doc_prs:
        ev["questions open"] = ((["questions listed under Open questions"] if open_questions else [])
                                + (["questions skipped in the latest grill record"] if record and skipped_in_record(record) else []))

    matched = [s for s in PRECEDENCE if s in ev]
    stage = matched[0] if matched else None

    tickets = [{"number": s["number"], "title": s["title"], "state": s["state"],
                "labels": [lb["name"] for lb in s.get("labels", [])], "blocked_by": blocked_by(s.get("body"))}
               for s in sorted(subs, key=lambda s: s["number"])]
    steps, later = next_steps(stage, n, name, issue, labels, tickets, doc_prs, doc, needs)
    return {
        "issue": f"{repo}#{n}",
        "title": issue["title"],
        "stage": stage,
        "evidence": ev.get(stage, [no_stage(body)]),
        "also_matched": matched[1:],
        "next_action": ", then ".join(s["do"] for s in steps) or None,
        "steps": steps,
        "later": later,
        "tickets": tickets,
        "doc_prs": doc_prs,
        "doc": doc,
    }


def no_stage(body):
    m = re.search(r"(?m)^Parent: #(\d+)\s*$", body)
    if m and re.search(r"(?m)^Implements:", body):
        return f"no D4 marker matched: this is a ticket under #{m.group(1)}, so run status on #{m.group(1)}"
    return "no D4 marker matched"


def next_steps(stage, n, name, issue, labels, tickets, doc_prs, doc, needs):
    owner = lambda do: {"who": "owner", "do": do}  # noqa: E731
    agent = lambda do: {"who": "agent", "do": do}  # noqa: E731
    open_t = [t for t in tickets if t["state"] == "open"]
    prs = ", ".join(f"{name}#{p['number']}" for p in doc_prs)
    later = []
    if stage == "reopened":
        where = numbers(needs) if needs else (doc["path"] if doc and doc["reopened"] else f"#{n}")
        steps = [owner(f"settle the reopened decision in {where} with `grill`")]
    elif stage == "revision in progress":
        steps = [owner(f"merge {prs}")] + ([agent(f"update {numbers(t['number'] for t in open_t)}")] if open_t else [])
    elif stage == "done":
        steps = [owner(f"close #{n}")] if issue["state"] == "open" else []
    elif stage == "in progress":
        ready = [t["number"] for t in open_t if READY in t["labels"]]
        closed = {t["number"] for t in tickets if t["state"] == "closed"}
        steps = ([agent(f"implement {numbers(ready)}")] if ready
                 else [owner(f"pick the next ticket: none of {numbers(t['number'] for t in open_t)} is {READY}")])
        for t in open_t:
            waiting = [b for b in t["blocked_by"] if b not in closed]
            if t["number"] not in ready and waiting:
                later.append(f"#{t['number']} waits on {numbers(waiting)}")
    elif stage == "decided, full path":
        steps = [agent(f"run `to-tickets` on {doc['path']}")]
    elif stage == "proposal drafted":
        ready_prs = [p for p in doc_prs if all(s == "decided" for s in p["docs"].values())]
        reopened_prs = [p for p in doc_prs if p["reopened"]]
        if reopened_prs:  # grill settles a reopened decision before proposal re-checks the doc
            steps = [owner("settle the reopened decision in " + ", ".join(f"{name}#{p['number']}" for p in reopened_prs)
                           + " with `grill`")]
        elif ready_prs:
            steps = [owner("review and merge " + ", ".join(f"{name}#{p['number']}" for p in ready_prs))]
        elif doc_prs:
            steps = [agent(f"finish {prs} with `proposal`")]
        else:
            steps = [agent(f"finish {doc['path']} with `proposal`")]
    elif stage == "decided, awaiting proposal":
        steps = [agent(f"write the proposal for #{n} with `proposal`")]
    elif stage == "decided, short path":
        steps = [agent(f"implement #{n}")] if READY in labels else [agent(f"slice #{n} with `to-tickets`")]
    elif stage == "questions open":
        steps = [owner(f"answer #{n}'s open questions with `grill`")]
    else:
        steps = []
    return steps, later


def parse_target(arg):
    """OWNER/REPO#N, or the issue's URL."""
    m = (re.fullmatch(r"([\w.-]+/[\w.-]+)#(\d+)", arg or "")
         or re.fullmatch(r"https://github\.com/([\w.-]+/[\w.-]+)/issues/(\d+)/?", arg or ""))
    return (m.group(1), int(m.group(2))) if m else (None, None)


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # en dashes and ellipses on a Windows console
    args = list(argv[1:])
    record = None
    if "--record" in args:
        i = args.index("--record")
        record = args[i + 1] if i + 1 < len(args) else None
        del args[i:i + 2]
    repo, n = parse_target(args[0] if args else None)
    if not repo or ("--record" in argv and not record):
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    seen = {}

    def fetch(path):
        seen[path] = gh_fetch(path)
        return seen[path]

    try:
        result = compute(fetch, repo, n)
    except GhError as e:
        print(json.dumps({"error": str(e)}))
        return 1
    if record:
        with open(record, "w", encoding="utf-8") as f:
            json.dump({"repo": repo, "number": n, "api": seen}, f, indent=1, ensure_ascii=False)
            f.write("\n")
    print(json.dumps(result, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
