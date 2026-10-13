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


def write(path, text, encoding="utf-8"):
    with open(path, "w", encoding=encoding) as f:
        f.write(text)


def skill(root, name, fm_name=None, desc="Use when testing.", extra=None):
    d = os.path.join(root, name)
    os.makedirs(d)
    with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(f"---\nname: {fm_name or name}\ndescription: {desc}\n---\n\n# body\n")
    for rel, text in (extra or {}).items():
        os.makedirs(os.path.dirname(os.path.join(d, rel)) or d, exist_ok=True)
        write(os.path.join(d, rel), text)
    return d


class Build(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.notice = os.path.join(self.tmp, "NOTICE")
        write(self.notice, "MIT")

    def test_valid_skill_has_no_problems(self):
        self.assertEqual(b.check(skill(self.tmp, "capture")), [])

    def test_name_mismatch(self):
        self.assertIn("doesn't match", b.check(skill(self.tmp, "capture", fm_name="capturer"))[0])

    def test_description_too_long(self):
        self.assertIn("201 characters", b.check(skill(self.tmp, "grill", desc="x" * 201))[0])

    def test_no_frontmatter(self):
        d = os.path.join(self.tmp, "x"); os.makedirs(d); write(os.path.join(d, "SKILL.md"), "# no fm")
        self.assertIn("no frontmatter", b.check(d)[0])

    def test_zip_has_folder_at_root_and_notice(self):
        d = skill(self.tmp, "grill", extra={"scripts/x.py": "print(1)"})
        out = b.build(d, os.path.join(self.tmp, "out"), self.notice)
        names = sorted(zipfile.ZipFile(out).namelist())
        self.assertEqual(names, ["grill/NOTICE", "grill/SKILL.md", "grill/scripts/x.py"])

    def test_missing_notice_fails(self):
        d = skill(self.tmp, "capture")
        with self.assertRaises(FileNotFoundError):
            b.build(d, os.path.join(self.tmp, "out"), os.path.join(self.tmp, "nope"))

    def test_own_notice_not_duplicated(self):
        d = skill(self.tmp, "grill", extra={"NOTICE": "own"})
        out = b.build(d, os.path.join(self.tmp, "out"), self.notice)
        names = zipfile.ZipFile(out).namelist()
        self.assertEqual(sorted(names), ["grill/NOTICE", "grill/NOTICE.dev-flow", "grill/SKILL.md"])

    def test_folded_description_measured_in_full(self):
        d = os.path.join(self.tmp, "grill"); os.makedirs(d)
        write(os.path.join(d, "SKILL.md"), "---\nname: grill\ndescription: >-\n  " + "word " * 50 + "\n  more\n---\n")
        self.assertTrue(any("characters" in p for p in b.check(d)), b.check(d))

    def test_quoted_name(self):
        self.assertEqual(b.check(skill(self.tmp, "grill", fm_name='"grill"')), [])

    def test_bad_name_characters(self):
        self.assertTrue(any("lowercase" in p for p in b.check(skill(self.tmp, "Flag_Decision"))))

    def test_reserved_word(self):
        self.assertTrue(any("reserved" in p for p in b.check(skill(self.tmp, "claude-helper"))))

    def test_bom_is_accepted(self):
        d = os.path.join(self.tmp, "capture"); os.makedirs(d)
        write(os.path.join(d, "SKILL.md"), "---\nname: capture\ndescription: Use when x.\n---\n", "utf-8-sig")
        self.assertEqual(b.check(d), [])

    def test_unquoted_colon_space_rejected(self):
        d = skill(self.tmp, "flag-decision", desc="Use when the Implements: line is wrong.")
        self.assertTrue(any("invalid YAML" in p for p in b.check(d)), b.check(d))

    def test_quoted_colon_space_accepted(self):
        self.assertEqual(b.check(skill(self.tmp, "flag-decision", desc='"Use when the Implements: line is wrong."')), [])

    def test_unquoted_comment_rejected(self):
        self.assertTrue(any("invalid YAML" in p for p in b.check(skill(self.tmp, "grill", desc="Use when x #1 is open."))))

    def test_every_real_skill_passes_checks(self):
        # all of them, not just the phone set: the plugin loads every skill
        root = os.path.join(b.ROOT, "skills")
        for n in sorted(os.listdir(root)):
            self.assertEqual(b.check(os.path.join(root, n)), [], n)


if __name__ == "__main__":
    unittest.main(verbosity=1)
