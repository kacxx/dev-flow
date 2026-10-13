#!/usr/bin/env python3
"""Run every test_*.py in the repo, each in its own isolated interpreter.

  python3 -I scripts/run_tests.py   (or `python` on Windows)

Finds the files itself, so a new test file runs without editing CI (#25, D4).
Exits non-zero if any file fails, or if none are found.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "dist", "__pycache__", "node_modules"}


def find_tests(root=None):
    found = []
    for base, dirs, files in os.walk(root or ROOT):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
        found += [os.path.join(base, f) for f in sorted(files) if f.startswith("test_") and f.endswith(".py")]
    return found


def main():
    tests = find_tests()
    if not tests:
        print("no test_*.py files found", file=sys.stderr)
        return 1
    failed = []
    for path in tests:
        rel = os.path.relpath(path, ROOT)
        print(f"== {rel}", flush=True)
        if subprocess.run([sys.executable, "-I", path], cwd=ROOT).returncode != 0:
            failed.append(rel)
    print(f"\n{len(tests) - len(failed)} of {len(tests)} test files passed")
    for rel in failed:
        print(f"FAILED: {rel}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
