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


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep:
            fields[k.strip()] = v.strip()
    return fields


def check(skill_dir):
    """Problems with one skill folder, as a list of strings (empty when it's fine)."""
    name = os.path.basename(skill_dir.rstrip("/"))
    path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(path):
        return [f"{name}: no SKILL.md"]
    fm = frontmatter(open(path, encoding="utf-8").read())
    if fm is None:
        return [f"{name}: SKILL.md has no frontmatter"]
    problems = []
    if fm.get("name") != name:
        problems.append(f"{name}: frontmatter name {fm.get('name')!r} doesn't match the folder")
    if len(fm.get("name", "")) > MAX_NAME:
        problems.append(f"{name}: name is over {MAX_NAME} characters")
    desc = fm.get("description", "")
    if not desc:
        problems.append(f"{name}: no description")
    elif len(desc) > MAX_DESC:
        problems.append(f"{name}: description is {len(desc)} characters (max {MAX_DESC})")
    return problems


def build(skill_dir, out_dir, notice=None):
    name = os.path.basename(skill_dir.rstrip("/"))
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
        if notice and os.path.isfile(notice):
            z.write(notice, os.path.join(name, "NOTICE"))
    return out


def main(argv):
    names = argv[1:] or PHONE_SET
    dirs = [os.path.join(ROOT, "skills", n) for n in names]
    problems = [p for d in dirs for p in check(d)]
    if problems:
        print("not built:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    out_dir = os.path.join(ROOT, "dist", "account-skills")
    for d in dirs:
        print(build(d, out_dir, os.path.join(ROOT, "NOTICE")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
