#!/usr/bin/env python3
"""Tests for build_account_skills.py. Run: python3 -I scripts/test_build_account_skills.py (or `python` on Windows)"""
import os
import shutil
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_account_skills as b  # noqa: E402

# Each frontmatter case runs against both parsers: PyYAML (when installed) and the strict fallback.
PARSERS = [False] + ([True] if b.yaml is not None else [])


def write(path, text, encoding="utf-8"):
    with open(path, "w", encoding=encoding) as f:
        f.write(text)


def skill(root, name, fm_name=None, desc="Use when testing.", extra=None):
    d = os.path.join(root, name)
    os.makedirs(d)
    write(os.path.join(d, "SKILL.md"), f"---\nname: {fm_name or name}\ndescription: {desc}\n---\n\n# body\n")
    for rel, text in (extra or {}).items():
        os.makedirs(os.path.dirname(os.path.join(d, rel)) or d, exist_ok=True)
        write(os.path.join(d, rel), text)
    return d


def raw(root, name, frontmatter_text, encoding="utf-8"):
    d = os.path.join(root, name)
    os.makedirs(d, exist_ok=True)
    write(os.path.join(d, "SKILL.md"), frontmatter_text, encoding)
    return d


class Build(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.notice = os.path.join(self.tmp, "NOTICE")
        write(self.notice, "MIT")

    def each_parser(self, d):
        """check() under every available parser, as (parser, problems) pairs."""
        return [("yaml" if y else "strict", b.check(d, use_yaml=y)) for y in PARSERS]

    def assertValid(self, d):
        for parser, problems in self.each_parser(d):
            self.assertEqual(problems, [], parser)

    def assertProblem(self, d, text):
        for parser, problems in self.each_parser(d):
            self.assertTrue(any(text in p for p in problems), f"{parser}: {problems}")

    def test_valid_skill_has_no_problems(self):
        self.assertValid(skill(self.tmp, "capture"))

    def test_name_mismatch(self):
        self.assertProblem(skill(self.tmp, "capture", fm_name="capturer"), "doesn't match")

    def test_description_too_long(self):
        self.assertProblem(skill(self.tmp, "settle", desc="x" * 201), "201 characters")

    def test_no_frontmatter(self):
        self.assertProblem(raw(self.tmp, "x", "# no fm"), "no frontmatter")

    def test_no_final_newline(self):
        self.assertValid(raw(self.tmp, "settle", "---\nname: settle\ndescription: Use when x.\n---"))

    def test_zip_has_folder_at_root_and_notice(self):
        d = skill(self.tmp, "settle", extra={"scripts/x.py": "print(1)"})
        out = b.build(d, os.path.join(self.tmp, "out"), self.notice)
        with zipfile.ZipFile(out) as z:
            self.assertEqual(sorted(z.namelist()), ["settle/NOTICE", "settle/SKILL.md", "settle/scripts/x.py"])

    def test_zip_leaves_out_tests_and_fixtures(self):
        d = skill(self.tmp, "status", extra={
            "scripts/state.py": "print(1)",
            "scripts/test_state.py": "import unittest",
            "scripts/fixtures/done.json": "{}",
            "scripts/fixtures/nested/x.json": "{}",
            "test_top.py": "import unittest",
            "fixtures/keep.json": "{}",  # only scripts/fixtures/ is test data
            "scripts/testing_notes.py": "print(2)",
        })
        out = b.build(d, os.path.join(self.tmp, "out"), self.notice)
        with zipfile.ZipFile(out) as z:
            self.assertEqual(sorted(z.namelist()), ["status/NOTICE", "status/SKILL.md", "status/fixtures/keep.json",
                                                    "status/scripts/state.py", "status/scripts/testing_notes.py"])

    def test_real_zips_carry_no_tests_or_fixtures(self):
        out = os.path.join(self.tmp, "out")
        for n in real_skills():
            with zipfile.ZipFile(b.build(os.path.join(b.ROOT, "skills", n), out, self.notice)) as z:
                for name in z.namelist():
                    self.assertFalse(os.path.basename(name).startswith("test_"), name)
                    self.assertNotIn("/scripts/fixtures/", name)

    def test_default_set_includes_status(self):
        self.assertEqual(b.DEFAULT_SET, ["capture", "settle", "flag-decision", "status"])
        for n in b.DEFAULT_SET:
            self.assertIn(n, real_skills())

    def test_missing_notice_fails(self):
        d = skill(self.tmp, "capture")
        with self.assertRaises(FileNotFoundError):
            b.build(d, os.path.join(self.tmp, "out"), os.path.join(self.tmp, "nope"))

    def test_own_notice_not_duplicated(self):
        d = skill(self.tmp, "settle", extra={"NOTICE": "own"})
        out = b.build(d, os.path.join(self.tmp, "out"), self.notice)
        with zipfile.ZipFile(out) as z:
            self.assertEqual(sorted(z.namelist()), ["settle/NOTICE", "settle/NOTICE.dev-flow", "settle/SKILL.md"])

    def test_folded_description_measured_in_full(self):
        d = raw(self.tmp, "settle", "---\nname: settle\ndescription: >-\n  " + "word " * 50 + "\n  more\n---\n")
        self.assertProblem(d, "characters")

    def test_block_header_with_indent_and_comment(self):
        for header in (">2", "|-2", ">- # folded"):
            d = raw(self.tmp, "settle", f"---\nname: settle\ndescription: {header}\n  " + "word " * 50 + "\n---\n")
            self.assertProblem(d, "characters")

    def test_plain_continuation_measured_in_full(self):
        d = raw(self.tmp, "settle", "---\nname: settle\ndescription: short\n  " + "word " * 50 + "\n---\n")
        self.assertProblem(d, "characters")

    def test_value_on_next_line(self):
        self.assertValid(raw(self.tmp, "settle", "---\nname: settle\ndescription:\n  Use when x.\n---\n"))

    def test_quoted_name(self):
        self.assertValid(skill(self.tmp, "settle", fm_name='"settle"'))

    def test_inline_comment_dropped(self):
        self.assertValid(skill(self.tmp, "settle", fm_name="settle  # phone set"))

    def test_single_quote_escape(self):
        self.assertValid(skill(self.tmp, "settle", desc="'Use when it''s time.'"))

    def test_bad_name_characters(self):
        self.assertProblem(skill(self.tmp, "Flag_Decision"), "lowercase")

    def test_reserved_word(self):
        self.assertProblem(skill(self.tmp, "claude-helper"), "reserved")

    def test_bom_is_accepted(self):
        self.assertValid(raw(self.tmp, "capture", "---\nname: capture\ndescription: Use when x.\n---\n", "utf-8-sig"))

    def test_quoted_colon_space_accepted(self):
        self.assertValid(skill(self.tmp, "flag-decision", desc='"Use when the Implements: line is wrong."'))

    def test_invalid_yaml_rejected(self):
        # each of these fails yaml.safe_load; the strict parser must reject it too
        bad = {
            "unquoted colon-space": "Use when the Implements: line is wrong.",
            "colon-space on a continuation line": "Use when x\n  and the Implements: line is wrong.",
            "unescaped apostrophe in single quotes": "'the ticket's Implements: line'",
            "text after the closing quote": '"a" b: c',
            "leading backtick": "`code` first",
            "leading flow indicator": "[a] b",
            "trailing colon": "Use when ready:",
        }
        for case, desc in bad.items():
            with self.subTest(case):
                d = skill(os.path.join(self.tmp, case.replace(" ", "-")), "settle", desc=desc)
                for parser, problems in self.each_parser(d):
                    self.assertTrue(problems, f"{parser} accepted {desc!r}")

    def test_strict_parser_agrees_with_yaml_on_real_skills(self):
        if b.yaml is None:
            self.skipTest("PyYAML not installed")
        root = os.path.join(b.ROOT, "skills")
        for n in real_skills():
            with open(os.path.join(root, n, "SKILL.md"), encoding="utf-8-sig") as f:
                text = f.read()
            strict, yml = b.frontmatter(text, use_yaml=False)[0], b.frontmatter(text)[0]
            self.assertEqual(strict, yml, n)

    def test_unsafe_key_name_is_just_a_key(self):
        d = raw(self.tmp, "settle", "---\nname: settle\ndescription: Use when x.\n_unsafe: abc\n---\n")
        self.assertValid(d)

    def test_every_real_skill_passes_checks(self):
        # all of them, not just the phone set: the plugin loads every skill
        root = os.path.join(b.ROOT, "skills")
        for n in real_skills():
            for parser, problems in self.each_parser(os.path.join(root, n)):
                self.assertEqual(problems, [], f"{n} ({parser})")

    def test_leftover_bytecode_folder_is_not_a_skill(self):
        root = os.path.join(self.tmp, "skills")
        for d in ("kept", os.path.join("old-name", "scripts", "__pycache__"), "no-skill-md"):
            os.makedirs(os.path.join(root, d))
        write(os.path.join(root, "kept", "SKILL.md"), "---\nname: kept\ndescription: Use when x.\n---\n")
        write(os.path.join(root, "old-name", "scripts", "__pycache__", "x.cpython-313.pyc"), "")
        write(os.path.join(root, "no-skill-md", "notes.txt"), "a real file")
        self.assertEqual(real_skills(root), ["kept", "no-skill-md"])

    def test_named_build_keeps_other_zips(self):
        out = os.path.join(b.ROOT, "dist", "account-skills")
        os.makedirs(out, exist_ok=True)
        keep = os.path.join(out, "capture.zip")
        existed = os.path.exists(keep)
        if not existed:
            write(keep, "placeholder")
            self.addCleanup(lambda: os.path.exists(keep) and os.remove(keep))
        self.assertEqual(b.main(["build", "settle"]), 0)
        self.assertTrue(os.path.exists(keep))


def only_bytecode(path):
    """A folder left behind by a renamed skill: no SKILL.md, nothing but __pycache__ folders (ignored by git)."""
    for dirpath, dirnames, filenames in os.walk(path):
        if os.path.basename(dirpath) == "__pycache__":
            dirnames[:] = []
            continue
        if filenames:
            return False
    return True


def real_skills(root=None):
    """Skill folders under skills/: directories only, skipping dotfiles such as .DS_Store and
    folders that hold only __pycache__ (an old checkout keeps one after a rename, as to-tickets did)."""
    root = root or os.path.join(b.ROOT, "skills")
    return sorted(n for n in os.listdir(root)
                  if not n.startswith(".") and os.path.isdir(os.path.join(root, n))
                  and (os.path.exists(os.path.join(root, n, "SKILL.md")) or not only_bytecode(os.path.join(root, n))))


if __name__ == "__main__":
    unittest.main(verbosity=1)
