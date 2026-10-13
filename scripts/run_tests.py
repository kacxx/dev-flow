#!/usr/bin/env python3
"""Run every test_*.py in the repo, each in its own isolated interpreter.

  python3 -I scripts/run_tests.py   (or `python` on Windows)

Finds the files itself, so a new test file runs without editing CI (#25, D4).
Each file's tests are loaded with unittest rather than run as a script, so a
file that forgets `unittest.main()` still runs. Exits non-zero if any file
fails, runs no tests, or takes longer than TIMEOUT seconds, or if no files are found.
"""
import importlib.util
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "dist", "__pycache__", "node_modules"}
TIMEOUT = 300


def find_tests(root=None):
    found = []
    for base, dirs, files in os.walk(root or ROOT):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        found += [os.path.join(base, f) for f in sorted(files) if f.startswith("test_") and f.endswith(".py")]
    return found


def run_file(path):
    """Load one test file as a module and run its tests. Zero tests is a failure on every Python."""
    spec = importlib.util.spec_from_file_location(os.path.splitext(os.path.basename(path))[0], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromModule(module))
    if result.testsRun == 0:
        print("no tests ran", file=sys.stderr)
        return 1
    return 0 if result.wasSuccessful() else 1


def main():
    tests = find_tests()
    if not tests:
        print("no test_*.py files found", file=sys.stderr)
        return 1
    failed = []
    for path in tests:
        rel = os.path.relpath(path, ROOT)
        print(f"== {rel}", flush=True)
        try:
            code = subprocess.run([sys.executable, "-I", os.path.abspath(__file__), "--file", path],
                                  cwd=ROOT, timeout=TIMEOUT).returncode
        except subprocess.TimeoutExpired:
            print(f"timed out after {TIMEOUT}s", file=sys.stderr)
            code = 1
        if code != 0:
            failed.append(rel)
    print(f"\n{len(tests) - len(failed)} of {len(tests)} test files passed")
    for rel in failed:
        print(f"FAILED: {rel}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["--file"]:
        sys.exit(run_file(sys.argv[2]))
    sys.exit(main())
