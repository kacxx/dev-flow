"""Tests for build_account_skills.py. Run: python3 -I scripts/test_build_account_skills.py"""
import os
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
        notice = os.path.join(self.tmp, "NOTICE"); open(notice, "w").write("MIT")
        out = b.build(d, os.path.join(self.tmp, "out"), notice)
        names = sorted(zipfile.ZipFile(out).namelist())
        self.assertEqual(names, ["grill/NOTICE", "grill/SKILL.md", "grill/scripts/x.py"])

    def test_real_phone_set_passes_checks(self):
        root = os.path.join(b.ROOT, "skills")
        for n in b.PHONE_SET:
            self.assertEqual(b.check(os.path.join(root, n)), [], n)


if __name__ == "__main__":
    unittest.main(verbosity=1)
