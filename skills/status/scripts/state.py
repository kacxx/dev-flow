#!/usr/bin/env python3
"""Read an idea's state on GitHub and name its dev-flow stage and next action.

  python3 state.py OWNER/REPO#N [--record FILE]   (or the issue URL instead of OWNER/REPO#N)

Prints one JSON object: the stage, the evidence for it, the other stages that
also matched, the tickets, the doc PRs, the proposal doc, the next action as
steps, each with who takes it (owner or agent), the review comments posted
since dev-flow last wrote on the issue, and the mechanical fixes to offer the
owner, each with the write it would make, and the batch: the agent's steps and
the fixes offered together for the owner's yes, each naming its writes. Read-only: GET requests through
`gh api` only; the fixes are applied by the skill after the owner's yes. --record also writes every response it read to FILE,
keyed by API path, which is the fixture format test_state.py replays.

Stages and markers are D4 of docs/proposals/status.md (dev-flow). When several
match, the first in PRECEDENCE wins (the proposal's Shape 2). Review comments
are D4's last paragraph; the relabelling fix is D2; the batch is D6.
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
# settle's decisions record; records from before the rename are headed (grill, …) (#56 D1)
RECORD_HEADINGS = ("## Decisions (settle", "## Decisions (grill")


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
    """Questions a settle record lists as skipped or still open (any heading naming them)."""
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

    def doc_files(pr):
        """The proposal docs a PR that names this issue changes; none for a code PR (D4)."""
        if not refs.search(pr.get("body") or ""):
            return []
        files = [f["filename"] for f in fetch(f"{r}/pulls/{pr['number']}/files?per_page=100") or []]
        return [f for f in files if f.startswith(PROPOSALS + "/") and f.endswith(".md")]

    doc_prs = []
    for pr in fetch(f"{r}/pulls?state=open&per_page=100") or []:
        docs = doc_files(pr)
        if not docs:
            continue
        texts = {d: decoded(fetch(f"{r}/contents/{d}?ref={pr['head']['sha']}")) for d in docs}  # "" if deleted
        doc_prs.append({"number": pr["number"], "title": pr["title"], "created_at": pr.get("created_at"),
                        "docs": {d: doc_status(t) for d, t in texts.items()},
                        "reopened": any(reopened_line(t) for t in texts.values())})
    # Merged doc PRs don't set a stage, but each is a dev-flow write: what the
    # issue said before it merged was answered by it (D4, review comments).
    merged_docs = [{"number": pr["number"], "merged_at": pr["merged_at"]}
                   for pr in fetch(f"{r}/pulls?state=closed&per_page=100") or []
                   if pr.get("merged_at") and doc_files(pr)]

    doc = None
    source = re.compile(r"(?m)^Source: #%d\b" % n)
    for entry in fetch(f"{r}/contents/{PROPOSALS}") or []:
        if entry.get("type") != "file" or not entry["name"].endswith(".md"):
            continue
        text = decoded(fetch(f"{r}/contents/{entry['path']}"))
        if source.search(text):
            doc = {"path": entry["path"], "status": doc_status(text), "reopened": reopened_line(text)}
            break
    return issue, comments, subs, flagged, doc_prs, merged_docs, doc


# --- naming the stage -------------------------------------------------------

def compute(fetch, repo, n):
    issue, comments, subs, flagged, doc_prs, merged_docs, doc = read(fetch, repo, n)
    name = repo.split("/")[1]
    body = issue.get("body") or ""
    labels = [lb["name"] for lb in issue.get("labels", [])]
    parent = re.compile(r"(?m)^Parent: #%d\s*$" % n)
    open_subs = [s for s in subs if s["state"] == "open"]
    sub_numbers = {s["number"] for s in subs}
    needs = sorted({i["number"] for i in flagged if not i.get("pull_request")
                    and (i["number"] in sub_numbers or parent.search(i.get("body") or ""))}
                   | {s["number"] for s in open_subs if NEEDS_DECISION in [lb["name"] for lb in s.get("labels", [])]})
    records = [c for c in comments if (c.get("body") or "").startswith(RECORD_HEADINGS)]
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
        ev["decided, awaiting proposal"] = ["a ## Decisions (settle, …) comment", "no proposal doc or doc PR"]
    if short_decisions and not open_questions and not to_check:
        ev["decided, short path"] = ["## Decisions in the body", "nothing under Open questions or To check"]
    if (open_questions or (record and skipped_in_record(record))) and not doc and not doc_prs:
        ev["questions open"] = ((["questions listed under Open questions"] if open_questions else [])
                                + (["questions skipped in the latest settle record"] if record and skipped_in_record(record) else []))

    matched = [s for s in PRECEDENCE if s in ev]
    stage = matched[0] if matched else None

    tickets = [{"number": s["number"], "title": s["title"], "state": s["state"],
                "labels": [lb["name"] for lb in s.get("labels", [])], "blocked_by": blocked_by(s.get("body"))}
               for s in sorted(subs, key=lambda s: s["number"])]
    blocker_state = {s["number"]: s["state"] for s in subs}
    for b in sorted({b for t in tickets for b in t["blocked_by"]} - set(blocker_state)):
        other = fetch(f"repos/{repo}/issues/{b}")  # a blocker outside the sub-issues
        blocker_state[b] = other["state"] if other else None
    fixes = relabel_fixes(repo, stage, tickets, blocker_state)
    steps, later = next_steps(stage, n, name, issue, labels, tickets, doc_prs, doc, needs,
                              relabelled={f["ticket"] for f in fixes})
    last_write = latest_write(issue, records, doc_prs, merged_docs, subs, name)
    return {
        "issue": f"{repo}#{n}",
        "title": issue["title"],
        "stage": stage,
        "evidence": ev.get(stage, [no_stage(body)]),
        "also_matched": matched[1:],
        # With no step left, the relabelling fixes in the batch are the next action.
        "next_action": (", then ".join(s["do"] for s in steps)
                        or (f"add {READY} to {numbers(f['ticket'] for f in fixes)}" if fixes else None)),
        "steps": steps,
        "later": later,
        "tickets": tickets,
        "doc_prs": doc_prs,
        "doc": doc,
        "last_write": last_write,
        "review_comments": review_comments(comments, last_write),
        "fixes": fixes,
        "batch": batch(steps, fixes),
    }


def latest_write(issue, records, doc_prs, merged_docs, subs, name):
    """dev-flow's last write on the issue (D4): the latest decisions record, doc PR or published tickets.

    An open doc PR counts from when it opened, a merged one from when it merged, and
    the tickets from the newest. With none of those, `capture` opening the issue is the write.
    """
    writes = ([(c.get("created_at"), "the decisions record") for c in records]
              + [(p.get("created_at"), f"doc PR {name}#{p['number']} opened") for p in doc_prs]
              + [(p.get("merged_at"), f"doc PR {name}#{p['number']} merged") for p in merged_docs]
              + [(s.get("created_at"), f"ticket #{s['number']} published") for s in subs])
    writes = [w for w in writes if w[0]]
    if not writes:
        return {"at": issue.get("created_at"), "what": "the issue opened"} if issue.get("created_at") else None
    at, what = max(writes)  # ISO 8601 UTC timestamps sort as text
    return {"at": at, "what": what}


def is_devflow_comment(body):
    """A comment dev-flow itself posts: settle's decisions record, or flag-decision's pointer."""
    return body.startswith(RECORD_HEADINGS) or re.match(r"D\d+ flagged by #\d+", body) is not None


def review_comments(comments, last_write):
    """Comments posted since dev-flow's last write, whoever wrote them (D4). They go first under "blocking now"."""
    since = last_write["at"] if last_write else None
    out = []
    for c in comments:
        body = (c.get("body") or "").strip()
        if is_devflow_comment(body) or not c.get("created_at") or (since and c["created_at"] <= since):
            continue
        first = next((ln.strip() for ln in body.splitlines() if ln.strip()), "")
        out.append({"author": (c.get("user") or {}).get("login"), "created_at": c["created_at"],
                    "url": c.get("html_url"), "first_line": first[:200]})
    return out


def batch(steps, fixes):
    """D6: the owner's pending approvals, offered together: the agent's steps, then the fixes.

    Owner steps (merging a PR, closing an issue) are never in it: status doesn't do them.
    Each item names every write it would make. `shows_draft` items still show their
    draft and wait for the owner's yes before writing; the selection is the yes for the rest.
    """
    items = [{"from": "step", "do": s["do"], "writes": s["writes"], "shows_draft": s["shows_draft"]}
             for s in steps if s["who"] == "agent"]
    items += [{"from": "fix", "do": f["write"], "why": f["why"], "writes": [f["write"]], "shows_draft": False,
               "command": f["command"]} for f in fixes]
    return items


def relabel_fixes(repo, stage, tickets, blocker_state):
    """D2: add ready-for-agent to an open ticket whose `Blocked by:` names issues that are all closed.

    Never while a revision is in progress. A ticket that names no blocker (`Blocked by: None`)
    and has no label was paused on purpose, and a needs-decision ticket waits on `settle`:
    both are left alone. Each fix names the write it would make; nothing here makes it.
    """
    if stage == "revision in progress":
        return []
    fixes = []
    for t in tickets:
        if (t["state"] != "open" or not t["blocked_by"] or READY in t["labels"] or NEEDS_DECISION in t["labels"]
                or any(blocker_state.get(b) != "closed" for b in t["blocked_by"])):
            continue
        fixes.append({
            "fix": "relabel",
            "ticket": t["number"],
            "why": f"#{t['number']}'s blockers have all closed: {numbers(t['blocked_by'])}",
            "write": f"add the {READY} label to #{t['number']}",
            "command": f"gh api repos/{repo}/issues/{t['number']}/labels --method POST -f \"labels[]={READY}\"",
        })
    return fixes


def no_stage(body):
    m = re.search(r"(?m)^Parent: #(\d+)\s*$", body)
    if m and re.search(r"(?m)^Implements:", body):
        return f"no D4 marker matched: this is a ticket under #{m.group(1)}, so run status on #{m.group(1)}"
    return "no D4 marker matched"


def next_steps(stage, n, name, issue, labels, tickets, doc_prs, doc, needs, relabelled=frozenset()):
    owner = lambda do: {"who": "owner", "do": do}  # noqa: E731

    def agent(do, writes, shows_draft):
        """An agent step names every write it would make (D6), and whether its skill shows a draft first."""
        return {"who": "agent", "do": do, "writes": writes, "shows_draft": shows_draft}

    def tickets_writes():
        return [f"new issues for the tickets, as sub-issues of #{n}",
                f"the {READY} label on the tickets with no open blockers"]
    open_t = [t for t in tickets if t["state"] == "open"]
    prs = ", ".join(f"{name}#{p['number']}" for p in doc_prs)
    later = []
    if stage == "reopened":
        where = numbers(needs) if needs else (doc["path"] if doc and doc["reopened"] else f"#{n}")
        steps = [owner(f"run `settle` on the reopened decision in {where}")]
    elif stage == "revision in progress":
        nums = numbers(t["number"] for t in open_t)
        steps = [owner(f"merge {prs}")] + ([agent(f"update {nums}", [f"edits to the bodies of {nums} to match the merged doc"],
                                                  True)] if open_t else [])
    elif stage == "done":
        steps = [owner(f"close #{n}")] if issue["state"] == "open" else []
    elif stage == "in progress":
        ready = [t["number"] for t in open_t if READY in t["labels"]]
        closed = {t["number"] for t in tickets if t["state"] == "closed"}
        if ready:
            steps = [agent(f"implement {numbers(ready)}", [f"a branch and a pull request for #{r}" for r in ready], False)]
        elif relabelled:
            steps = []  # the relabelling fixes in the batch are the decision; "pick a ticket" would contradict them
        else:
            steps = [owner(f"pick the next ticket: none of {numbers(t['number'] for t in open_t)} is {READY}")]
        for t in open_t:
            waiting = [b for b in t["blocked_by"] if b not in closed]
            if t["number"] not in ready and waiting:
                later.append(f"#{t['number']} waits on {numbers(waiting)}")
    elif stage == "decided, full path":
        steps = [agent(f"run `slice` on {doc['path']}", tickets_writes(), True)]
    elif stage == "proposal drafted":
        ready_prs = [p for p in doc_prs if all(s == "decided" for s in p["docs"].values())]
        reopened_prs = [p for p in doc_prs if p["reopened"]]
        if reopened_prs:  # settle decides a reopened decision before proposal re-checks the doc
            steps = [owner("run `settle` on the reopened decision in " + ", ".join(f"{name}#{p['number']}" for p in reopened_prs))]
        elif ready_prs:
            ready = ", ".join(f"{name}#{p['number']}" for p in ready_prs)
            steps = [owner(f"run a fresh code review (such as `/code-review`) on {ready}, then merge it")]
        elif doc_prs:
            steps = [agent(f"finish {prs} with `proposal`", [f"commits to the doc on {prs}'s branch"], True)]
        else:
            steps = [agent(f"finish {doc['path']} with `proposal`", [f"a branch and a draft doc PR updating {doc['path']}"],
                           True)]
    elif stage == "decided, awaiting proposal":
        steps = [agent(f"write the proposal for #{n} with `proposal`",
                       [f"a branch and a draft doc PR adding a doc under {PROPOSALS}/"], True)]
    elif stage == "decided, short path":
        steps = ([agent(f"implement #{n}", [f"a branch and a pull request for #{n}"], False)] if READY in labels
                 else [agent(f"slice #{n} with `slice`", tickets_writes(), True)])
    elif stage == "questions open":
        steps = [owner(f"answer #{n}'s open questions with `settle`")]
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
