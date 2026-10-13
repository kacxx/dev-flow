#!/usr/bin/env python3
"""Tests for build_account_skills.py. Run: python3 -I scripts/test_build_account_skills.py"""
import os
import shutil
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_account_skills as b  # noqa: E402


def skill(root, name, fm_name=None, desc="Use when testing.", extra=None):
    d = os.path.join(root, name)
    os.makedirs(d)
    with open(os.path.join(d, "SKILL.md"), "w") as f:
        f.write(f"---\nname: {fm_name or name}\ndescription: {desc}\n---\n\n# body\n")
    for rel, text in (extra or {}).items():
        os.makedirs(os.path.dirname(os.path.join(d, rel)) or d, exist_ok=True)
        open(os.path.join(d, rel), "w").write(text)
    return d


class Build(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.notice = os.path.join(self.tmp, "NOTICE")
        open(self.notice, "w").write("MIT")

    def test_valid_skill_has_no_problems(self):
        self.assertEqual(b.check(skill(self.tmp, "capture")), [])

    def test_name_mismatch(self):
        self.assertIn("doesn't match", b.check(skill(self.tmp, "capture", fm_name="capturer"))[0])

    def test_description_too_long(self):
        self.assertIn("201 characters", b.check(skill(self.tmp, "grill", desc="x" * 201))[0])

    def test_no_frontmatter(self):
        d = os.path.join(self.tmp, "x"); os.makedirs(d); open(os.path.join(d, "SKILL.md"), "w").write("# no fm")
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
        open(os.path.join(d, "SKILL.md"), "w").write("---\nname: grill\ndescription: >-\n  " + "word " * 50 + "\n  more\n---\n")
        self.assertTrue(any("characters" in p for p in b.check(d)), b.check(d))

    def test_quoted_name(self):
        self.assertEqual(b.check(skill(self.tmp, "grill", fm_name='"grill"')), [])

    def test_bad_name_characters(self):
        self.assertTrue(any("lowercase" in p for p in b.check(skill(self.tmp, "Flag_Decision"))))

    def test_reserved_word(self):
        self.assertTrue(any("reserved" in p for p in b.check(skill(self.tmp, "claude-helper"))))

    def test_bom_is_accepted(self):
        d = os.path.join(self.tmp, "capture"); os.makedirs(d)
        open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8-sig").write("---\nname: capture\ndescription: Use when x.\n---\n")
        self.assertEqual(b.check(d), [])

    def test_real_phone_set_passes_checks(self):
        root = os.path.join(b.ROOT, "skills")
        for n in b.PHONE_SET:
            self.assertEqual(b.check(os.path.join(root, n)), [], n)


if __name__ == "__main__":
    unittest.main(verbosity=1)
