#!/usr/bin/env python3
"""Check a GitHub repo's agent instructions for the flag-decision pointer line.

  python3 check_pointer.py OWNER/REPO [--ref BRANCH]

Prints exactly one result line:
  present in <file>                      the current pointer (with the fallback sentence)
  outdated in <file>                     an older pointer without the fallback: offer the new wording
  missing line                           instruction files exist, none has the pointer: offer the line
  no instruction file                    no CLAUDE.md / AGENTS.md: offer to create CLAUDE.md with it
  could not check: <file>: <reason>; …   errors, and no pointer found anywhere

Reads CLAUDE.md, .claude/CLAUDE.md and AGENTS.md, then follows `@path.md` imports
(resolved relative to the importing file, outside code fences, up to 3 levels).
A pointer found anywhere wins over errors elsewhere. Read-only: GET requests only.
"""
import posixpath
import re
import subprocess
import sys

CANDIDATES = ["CLAUDE.md", ".claude/CLAUDE.md", "AGENTS.md"]
POINTER = re.compile(r"run the `flag-decision` skill.*?and stop", re.S)
FALLBACK = re.compile(r"stop anyway", re.I)
IMPORT = re.compile(r"(?<![\w`@])@((?:\.{1,2}/)?[\w.-]+(?:/[\w.-]+)*\.md)\b")
MAX_DEPTH = 3

OK, MISSING, ERROR = "ok", "missing", "error"


def gh_fetch(repo, ref):
    def fetch(path):
        url = f"repos/{repo}/contents/{path}" + (f"?ref={ref}" if ref else "")
        p = subprocess.run(["gh", "api", url, "--jq", "if type == \"object\" and .type == \"file\" then .content | @base64d else error(\"not a file\") end"],
                           capture_output=True, text=True)
        if p.returncode == 0:
            return OK, p.stdout
        msg = (p.stderr or p.stdout).strip()
        if "HTTP 404" in msg:
            return MISSING, ""
        if "not a file" in msg:
            return MISSING, ""  # a directory at that path isn't an instruction file
        return ERROR, msg.splitlines()[-1] if msg else "unknown error"
    return fetch


def imports_in(text, from_path):
    """`@path.md` imports outside fenced code blocks, resolved relative to from_path."""
    found, in_fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in IMPORT.finditer(line):
            target = posixpath.normpath(posixpath.join(posixpath.dirname(from_path), m.group(1)))
            if not target.startswith(".."):
                found.append(target)
    return found


def check(fetch):
    queue = [(p, 0) for p in CANDIDATES]
    seen, errors, any_file, outdated = set(), [], False, None
    while queue:
        path, depth = queue.pop(0)
        if path in seen:
            continue
        seen.add(path)
        status, text = fetch(path)
        if status == ERROR:
            errors.append(f"{path}: {text}")
            continue
        if status == MISSING:
            continue
        any_file = True
        m = POINTER.search(text)
        if m:
            window = text[m.start(): m.end() + 200]
            if FALLBACK.search(window):
                return f"present in {path}"
            outdated = outdated or path
        if depth < MAX_DEPTH:
            queue.extend((t, depth + 1) for t in imports_in(text, path))
    if outdated:
        return f"outdated in {outdated}"
    if errors:
        return "could not check: " + "; ".join(errors)
    return "missing line" if any_file else "no instruction file"


def main(argv):
    if len(argv) < 2 or "/" not in argv[1]:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    ref = argv[argv.index("--ref") + 1] if "--ref" in argv else None
    repo = argv[1]
    p = subprocess.run(["gh", "api", f"repos/{repo}", "--silent"], capture_output=True, text=True)
    if p.returncode != 0:
        print(f"could not check: repo {repo}: {(p.stderr or p.stdout).strip()}")
        return 0
    print(check(gh_fetch(repo, ref)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
