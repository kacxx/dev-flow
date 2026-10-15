#!/usr/bin/env python3
"""Build claude.ai account-skill ZIPs from this plugin's skill folders.

  python3 -I scripts/build_account_skills.py [skill ...]   # default: the account-skill set
  (on Windows, use `python` if `python3` is the Microsoft Store stub)

Writes dist/account-skills/<name>.zip for each skill and checks what claude.ai
requires: the skill folder at the ZIP root, its name matching the frontmatter
`name`, `name` ≤ 64 characters and `description` ≤ 200. The frontmatter must
parse as YAML: some Claude Code builds drop a skill whose frontmatter doesn't,
without a warning. With PyYAML installed it is parsed with `yaml.safe_load`;
without it, a strict parser accepts only the forms it can verify (one-line plain
or quoted values, plain continuation lines, `>`/`|` block scalars) and rejects
anything else, so a skill is never passed unchecked. Each ZIP also carries the
repo's NOTICE, because some skills adapt MIT-licensed text that must travel with
every copy. Test files (`test_*.py`) and `scripts/fixtures/` stay out of the
ZIPs: they're for CI, and status's fixtures alone are about 664 KB. Exits non-zero, building nothing, if any skill fails a check.
"""
import os
import re
import sys
import zipfile

try:
    import yaml
except ImportError:  # stdlib-only machines (e.g. a fresh Windows Python): strict fallback
    yaml = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# idea-to-tickets.md D5's phone set, plus status wherever the other account skills are (status.md D9)
DEFAULT_SET = ["capture", "grill", "flag-decision", "status"]
MAX_NAME, MAX_DESC = 64, 200
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESERVED = ("anthropic", "claude")

FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)
KEY_LINE = re.compile(r"^([A-Za-z0-9_-]+):(?:[ \t]+(.*?))?[ \t]*$")
BLOCK_HEADER = re.compile(r"^[>|](?:[1-9][+-]?|[+-][1-9]?)?(?:[ \t]+#.*)?$")
DOUBLE = re.compile(r'^"((?:[^"\\]|\\.)*)"(?:[ \t]+#.*)?$')
SINGLE = re.compile(r"^'((?:[^']|'')*)'(?:[ \t]+#.*)?$")
PLAIN_START = set("-?:,[]{}#&*!|>'\"%@`")
COMMENT = re.compile(r"(?:^|[ \t])#")


def _plain(v):
    """A plain scalar's value with any comment removed, or None if YAML would reject it."""
    v = COMMENT.split(v, 1)[0].rstrip()
    if not v or ": " in v or ":\t" in v or v.endswith(":"):
        return None
    if v[0] in PLAIN_START and not (v[0] in "-?:" and len(v) > 1 and not v[1].isspace()):
        return None
    return v


def _strict(body):
    """(fields, error): the forms this parser can verify, or an error naming the first line it can't."""
    fields, lines, i = {}, body.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = KEY_LINE.match(line)
        if not m:
            return None, f"line {i}: not a top-level `key: value` this check can verify"
        key, v = m.group(1), (m.group(2) or "")
        cont = []
        while i < len(lines) and (lines[i][:1] in (" ", "\t") or not lines[i].strip()):
            cont.append(lines[i].strip())
            i += 1
        if BLOCK_HEADER.match(v):
            parts = [x for x in cont if x] if v[0] == ">" else cont
            fields[key] = (" " if v[0] == ">" else "\n").join(parts).strip("\n")
            continue
        if v and v[0] in "\"'":
            m = (DOUBLE if v[0] == '"' else SINGLE).match(v)
            if not m or any(cont):
                return None, f"line {i - len(cont)}: `{key}` is quoted but not closed on its line, or has text after the closing quote"
            s = m.group(1)
            fields[key] = s.replace("''", "'") if v[0] == "'" else re.sub(r'\\(.)', lambda c: {"n": "\n", "t": "\t"}.get(c.group(1), c.group(1)), s)
            continue
        words = [x for x in [v] + cont if x]
        if not words:
            fields[key] = ""
            continue
        values = [_plain(x) for x in words]
        if any(x is None for x in values):
            return None, f"line {i - len(cont)}: `{key}` is invalid YAML unquoted (a `: `, a trailing `:`, or a leading indicator such as `[` or a backtick); quote the value"
        fields[key] = " ".join(values)
    return fields, None


def frontmatter(text, use_yaml=True):
    """(fields, error) for a SKILL.md's frontmatter. fields is None when there is none or it doesn't parse."""
    m = FRONTMATTER.match(text)
    if not m:
        return None, "SKILL.md has no frontmatter"
    if use_yaml and yaml is not None:
        try:
            data = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            return None, "frontmatter is invalid YAML: " + str(e).splitlines()[0]
        if not isinstance(data, dict):
            return None, "frontmatter is not a `key: value` mapping"
        return {str(k): "" if v is None else str(v) for k, v in data.items()}, None
    return _strict(m.group(1))


def check(skill_dir, use_yaml=True):
    """Problems with one skill folder, as a list of strings (empty when it's fine)."""
    name = os.path.basename(skill_dir.rstrip("/\\"))
    path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(path):
        return [f"{name}: no SKILL.md"]
    with open(path, encoding="utf-8-sig") as f:
        fm, error = frontmatter(f.read(), use_yaml)
    if fm is None:
        return [f"{name}: {error}"]
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


def is_test(filename):
    """A unit test file, which runs in CI from the repo and is left out of the ZIP."""
    return filename.startswith("test_") and filename.endswith(".py")


def is_fixtures(path):
    """A `scripts/fixtures/` folder: recorded test data, left out of the ZIP."""
    return os.path.basename(path) == "fixtures" and os.path.basename(os.path.dirname(path)) == "scripts"


def build(skill_dir, out_dir, notice):
    """ZIP one skill. `notice` is required: the MIT notice must travel with every copy."""
    name = os.path.basename(skill_dir.rstrip("/\\"))
    if not os.path.isfile(notice):
        raise FileNotFoundError(f"NOTICE not found at {notice}: refusing to build without it")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{name}.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(skill_dir):
            dirs[:] = sorted(d for d in dirs if d not in ("__pycache__",) and not d.startswith(".")
                             and not is_fixtures(os.path.join(base, d)))
            for f in sorted(files):
                if f.startswith(".") or f.endswith(".pyc") or is_test(f):
                    continue
                full = os.path.join(base, f)
                z.write(full, os.path.join(name, os.path.relpath(full, skill_dir)))
        own = os.path.isfile(os.path.join(skill_dir, "NOTICE"))
        z.write(notice, os.path.join(name, "NOTICE.dev-flow" if own else "NOTICE"))
    return out


def main(argv):
    names = argv[1:] or DEFAULT_SET
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
    # Stale ZIPs would be uploaded by mistake. A default build replaces the whole set (so a
    # skill dropped from it doesn't linger); a named build replaces only the ZIPs it names.
    if os.path.isdir(out_dir):
        for f in os.listdir(out_dir):
            if f.endswith(".zip") and (not argv[1:] or f[:-4] in names):
                os.remove(os.path.join(out_dir, f))
    for d in dirs:
        print(build(d, out_dir, notice))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
