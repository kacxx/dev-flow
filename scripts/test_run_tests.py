#!/usr/bin/env python3
"""Tests for run_tests.py. Run: python3 -I scripts/test_run_tests.py (or `python` on Windows)"""
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_tests as r  # noqa: E402


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class RunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_finds_nested_tests_and_skips_build_and_hidden_dirs(self):
        for rel in ("scripts/test_a.py", "skills/x/scripts/test_b.py", "dist/test_c.py",
                    ".git/test_d.py", "scripts/helper.py", "scripts/test_e.txt"):
            write(os.path.join(self.tmp, rel), "")
        found = [os.path.relpath(p, self.tmp).replace(os.sep, "/") for p in r.find_tests(self.tmp)]
        self.assertEqual(found, ["scripts/test_a.py", "skills/x/scripts/test_b.py"])

    def test_failing_file_fails_the_run(self):
        write(os.path.join(self.tmp, "test_ok.py"), "")
        write(os.path.join(self.tmp, "test_bad.py"), "raise SystemExit(1)")
        with mock.patch.object(r, "ROOT", self.tmp), mock.patch("sys.stdout"), mock.patch("sys.stderr"):
            self.assertEqual(r.main(), 1)

    def test_all_passing_succeeds(self):
        write(os.path.join(self.tmp, "test_ok.py"), "")
        with mock.patch.object(r, "ROOT", self.tmp), mock.patch("sys.stdout"):
            self.assertEqual(r.main(), 0)

    def test_no_tests_fails(self):
        with mock.patch.object(r, "ROOT", self.tmp), mock.patch("sys.stderr"):
            self.assertEqual(r.main(), 1)


if __name__ == "__main__":
    unittest.main(verbosity=1)
