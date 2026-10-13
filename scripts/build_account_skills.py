#!/usr/bin/env python3
"""Build claude.ai account-skill ZIPs from this plugin's skill folders.

  python3 -I scripts/build_account_skills.py [skill ...]   # default: the phone set (D5)

Writes dist/account-skills/<name>.zip for each skill and checks what claude.ai
requires: the skill folder at the ZIP root, its name matching the frontmatter
`name`, `name` ≤ 64 characters and `description` ≤ 200. Each ZIP also carries the
repo's NOTICE, because some skills adapt MIT-licensed text that must travel with
every copy. Exits non-zero, building nothing, if any skill fails a check.
"""
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHONE_SET = ["capture", "grill", "flag-decision"]  # D5
MAX_NAME, MAX_DESC = 64, 200
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESERVED = ("anthropic", "claude")


def _unquote(v):
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def frontmatter(text):
    """Top-level `key: value` pairs, including quoted values and `>`/`|` block scalars."""
    m = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return None
    fields, lines, i = {}, m.group(1).splitlines(), 0
    while i < len(lines):
        k, sep, v = lines[i].partition(":")
        i += 1
        if not sep or lines[i - 1][:1].isspace():
            continue
        v = v.strip()
        if v in (">", ">-", ">+", "|", "|-", "|+"):
            block = []
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            joined = (" " if v.startswith(">") else "\n").join(x for x in block if x) if v.startswith(">") else "\n".join(block).strip("\n")
            fields[k.strip()] = joined
        else:
            fields[k.strip()] = _unquote(v)
    return fields


def check(skill_dir):
    """Problems with one skill folder, as a list of strings (empty when it's fine)."""
    name = os.path.basename(skill_dir.rstrip("/"))
    path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(path):
        return [f"{name}: no SKILL.md"]
    fm = frontmatter(open(path, encoding="utf-8-sig").read())
    if fm is None:
        return [f"{name}: SKILL.md has no frontmatter"]
    problems = []
    if fm.get("name") != name:
        problems.append(f"{name}: frontmatter name {fm.get('name')!r} doesn't match the folder")
    fname = fm.get("name", "")
    if len(fname) > MAX_NAME:
        problems.append(f"{name}: name is over {MAX_NAME} characters")
    if not NAME_RE.match(fname):
        problems.append(f"{name}: name must be lowercase letters, digits and hyphens")
    if any(w in fname for w in RESERVED):
        problems.append(f"{name}: name contains a reserved word ({', '.join(RESERVED)})")
    desc = fm.get("description", "")
    if not desc:
        problems.append(f"{name}: no description")
    elif len(desc) > MAX_DESC:
        problems.append(f"{name}: description is {len(desc)} characters (max {MAX_DESC})")
    if re.search(r"<[^>]+>", desc):
        problems.append(f"{name}: description contains an XML-style tag")
    return problems


def build(skill_dir, out_dir, notice):
    """ZIP one skill. `notice` is required: the MIT notice must travel with every copy."""
    name = os.path.basename(skill_dir.rstrip("/"))
    if not os.path.isfile(notice):
        raise FileNotFoundError(f"NOTICE not found at {notice}: refusing to build without it")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{name}.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(skill_dir):
            dirs[:] = sorted(d for d in dirs if d not in ("__pycache__",) and not d.startswith("."))
            for f in sorted(files):
                if f.startswith(".") or f.endswith(".pyc"):
                    continue
                full = os.path.join(base, f)
                z.write(full, os.path.join(name, os.path.relpath(full, skill_dir)))
        own = os.path.isfile(os.path.join(skill_dir, "NOTICE"))
        z.write(notice, os.path.join(name, "NOTICE.dev-flow" if own else "NOTICE"))
    return out


def main(argv):
    names = argv[1:] or PHONE_SET
    dirs = [os.path.join(ROOT, "skills", n) for n in names]
    problems = [p for d in dirs for p in check(d)]
    if problems:
        print("not built:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    out_dir = os.path.join(ROOT, "dist", "account-skills")
    notice = os.path.join(ROOT, "NOTICE")
    if not os.path.isfile(notice):
        print(f"not built: NOTICE not found at {notice}", file=sys.stderr)
        return 1
    if os.path.isdir(out_dir):  # stale ZIPs from earlier runs would be uploaded by mistake
        for f in os.listdir(out_dir):
            if f.endswith(".zip"):
                os.remove(os.path.join(out_dir, f))
    for d in dirs:
        print(build(d, out_dir, notice))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
