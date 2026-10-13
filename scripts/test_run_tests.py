#!/usr/bin/env python3
"""Tests for run_tests.py. Run: python3 -I scripts/test_run_tests.py (or `python` on Windows)"""
import os
import functools
import shutil
import subprocess
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


PASSING = "import unittest\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n"


class RunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def run_main(self, timeout=None):
        # The child interpreters write to the real output streams; keep their failures out of this run's log.
        quiet = functools.partial(subprocess.run, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        patches = [mock.patch.object(r, "ROOT", self.tmp), mock.patch.object(r.subprocess, "run", quiet),
                   mock.patch("sys.stdout"), mock.patch("sys.stderr")]
        if timeout:
            patches.append(mock.patch.object(r, "TIMEOUT", timeout))
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        return r.main()

    def test_finds_nested_and_hidden_tests_and_skips_build_dirs(self):
        for rel in ("scripts/test_a.py", "skills/x/scripts/test_b.py", ".github/test_f.py", "dist/test_c.py",
                    ".git/test_d.py", "x/__pycache__/test_g.py", "node_modules/y/test_h.py",
                    "scripts/helper.py", "scripts/test_e.txt"):
            write(os.path.join(self.tmp, rel), "")
        found = [os.path.relpath(p, self.tmp).replace(os.sep, "/") for p in r.find_tests(self.tmp)]
        self.assertEqual(found, [".github/test_f.py", "scripts/test_a.py", "skills/x/scripts/test_b.py"])

    def test_failing_file_fails_the_run(self):
        write(os.path.join(self.tmp, "test_ok.py"), PASSING)
        write(os.path.join(self.tmp, "test_bad.py"), PASSING.replace("pass", "self.fail()"))
        self.assertEqual(self.run_main(), 1)

    def test_all_passing_succeeds(self):
        write(os.path.join(self.tmp, "test_ok.py"), PASSING)
        self.assertEqual(self.run_main(), 0)

    def test_file_without_unittest_main_still_runs(self):
        # No `unittest.main()` block, so running it as a script would exit 0 without testing.
        write(os.path.join(self.tmp, "test_bad.py"), PASSING.replace("pass", "self.fail()"))
        self.assertEqual(self.run_main(), 1)

    def test_file_with_no_tests_fails(self):
        write(os.path.join(self.tmp, "test_empty.py"), "import unittest\n")
        self.assertEqual(self.run_main(), 1)

    def test_hanging_file_times_out(self):
        write(os.path.join(self.tmp, "test_hang.py"), PASSING.replace("pass", "import time; time.sleep(60)"))
        self.assertEqual(self.run_main(timeout=2), 1)

    def test_no_tests_fails(self):
        self.assertEqual(self.run_main(), 1)


if __name__ == "__main__":
    unittest.main(verbosity=1)
