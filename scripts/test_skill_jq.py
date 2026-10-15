#!/usr/bin/env python3
"""Tests for the jq filters written in the skills' search fallbacks. Run: python3 -I scripts/test_skill_jq.py (or `python` on Windows)

The filters are read from the SKILL.md files themselves, so what's tested is the text an
agent runs. Needs `jq` (gh runs the same filters through its built-in gojq). Skipped when
jq is missing locally; fails when it's missing in CI, so CI can't pass without running them.
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JQ = shutil.which("jq")


def fallback_filter(skill):
    """The --jq program of the skill's `issues?…` list-and-filter fallback."""
    with open(os.path.join(ROOT, "skills", skill, "SKILL.md"), encoding="utf-8") as f:
        text = f.read()
    found = re.findall(r"gh api --paginate 'repos/OWNER/REPO/issues\?[^']*' --jq '([^\n]*)'\n", text)
    if len(found) != 1:
        raise AssertionError(f"{skill}: expected one issues-list fallback, found {len(found)}")
    return found[0]


def run(program, issues):
    p = subprocess.run([JQ, "-r", program], input=json.dumps(issues), capture_output=True, text=True)
    if p.returncode != 0:
        raise AssertionError(f"jq failed: {p.stderr.strip()}\nprogram: {program}")
    return [line.split()[0] for line in p.stdout.splitlines() if line]


def issue(number, body, title="t", pr=None):
    d = {"number": number, "title": title, "body": body, "state": "open"}
    if pr is not None:
        d["pull_request"] = {"merged_at": pr}
    return d


@unittest.skipIf(JQ is None and not os.environ.get("CI"), "jq not installed")
class SkillJq(unittest.TestCase):
    def setUp(self):
        if JQ is None:
            self.fail("jq is required in CI")

    def test_capture_matches_title_or_body_case_insensitively(self):
        program = fallback_filter("capture").replace("KEYWORDS", "CI|workflow")
        issues = [
            issue(1, None, title="Add a ci pipeline"),
            issue(2, "This adds a Workflow for tests", title="Other title"),
            issue(3, "nothing related", title="Unrelated"),
            issue(4, "merged work on the workflow", title="PR", pr="2026-10-13T00:00:00Z"),
        ]
        self.assertEqual(run(program, issues), ["#1", "#2", "#4"])

    def test_grill_needs_the_decision_and_its_source_on_the_implements_line(self):
        program = fallback_filter("settle").replace("<n>", "2").replace("<name>", "a").replace("#N", "#1")
        issues = [
            issue(1, "Implements: D2 — docs/proposals/a.md\nParent: #1"),
            issue(2, "Implements: D2 — docs/proposals/b.md"),
            issue(3, "Implements: D12 — docs/proposals/a.md"),
            issue(4, "Implements: D2 — #1"),
            issue(5, "Implements: D2 — #12"),
            issue(6, "Implements: D1 — docs/proposals/a.md\nD2 comes up later"),
            issue(7, "Implements: D3, D2 — docs/proposals/a.md\r\nBlocked by: none"),
            issue(8, "Implements: D2 — docs/proposals/a.md", pr=None),
            issue(9, "Implements: D2 — docs/proposals/axmd"),
            issue(10, None),
        ]
        issues[7]["pull_request"] = {}  # a PR is never a ticket
        self.assertEqual(run(program, issues), ["#1", "#4", "#7"])

    def test_to_tickets_parent_line_matches_the_whole_number(self):
        program = fallback_filter("slice").replace("#N", "#1")
        issues = [
            issue(1, "Implements: D1 — docs/proposals/a.md\nParent: #1\n"),
            issue(2, "Parent: #12"),
            issue(3, "Implements: D1 — x\r\nParent: #1\r\n\r\n## What to build"),
            issue(4, "See Parent: #1 in the text"),
            issue(5, "Parent: #100\n"),
            issue(6, None),
        ]
        self.assertEqual(run(program, issues), ["#1", "#3"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
