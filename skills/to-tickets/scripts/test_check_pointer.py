#!/usr/bin/env python3
"""Tests for check_pointer.py. Run: python3 -I skills/to-tickets/scripts/test_check_pointer.py (or `python` on Windows)"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_pointer as cp  # noqa: E402

NEW = "- If a ticket's work shows a decision is wrong, run the `flag-decision` skill and stop. If that skill isn't available, stop anyway and comment. Don't redesign."
NEW_WITH_PLUGIN = "- run the `flag-decision` skill (dev-flow plugin) and stop. If that skill isn't available, stop anyway and comment."
OLD = "- If a ticket's work shows a decision is wrong, run the `flag-decision` skill and stop. Don't redesign inside the ticket."


def fake(files, errors=()):
    def fetch(path):
        if path in errors:
            return cp.ERROR, "HTTP 403: rate limit"
        if path in files:
            return cp.OK, files[path]
        return cp.MISSING, ""
    return fetch


class CheckPointer(unittest.TestCase):
    def test_present_in_root(self):
        self.assertEqual(cp.check(fake({"CLAUDE.md": NEW})), "present in CLAUDE.md")

    def test_present_with_plugin_note(self):
        self.assertEqual(cp.check(fake({"AGENTS.md": NEW_WITH_PLUGIN})), "present in AGENTS.md")

    def test_import_at_column_zero(self):
        self.assertEqual(cp.check(fake({"CLAUDE.md": "@AGENTS.md\n", "AGENTS.md": NEW})), "present in AGENTS.md")

    def test_import_resolved_relative_to_importer(self):
        files = {".claude/CLAUDE.md": "@AGENTS.md", ".claude/AGENTS.md": NEW}
        self.assertEqual(cp.check(fake(files)), "present in .claude/AGENTS.md")

    def test_dot_slash_import(self):
        files = {".claude/CLAUDE.md": "See @./rules/agents.md", ".claude/rules/agents.md": NEW}
        self.assertEqual(cp.check(fake(files)), "present in .claude/rules/agents.md")

    def test_import_in_list_and_inline(self):
        self.assertEqual(cp.check(fake({"CLAUDE.md": "- @docs/a.md\n  see @docs/b.md here", "docs/b.md": NEW})), "present in docs/b.md")

    def test_import_inside_code_fence_ignored(self):
        files = {"CLAUDE.md": "```\n@docs/x.md\n```\n", "docs/x.md": NEW}
        self.assertEqual(cp.check(fake(files)), "missing line")

    def test_at_mention_is_not_import(self):
        self.assertEqual(cp.check(fake({"CLAUDE.md": "@ mention the owner\nemail me@x.com"})), "missing line")

    def test_outdated_pointer(self):
        self.assertEqual(cp.check(fake({"CLAUDE.md": OLD})), "outdated in CLAUDE.md")

    def test_no_file(self):
        self.assertEqual(cp.check(fake({})), "no instruction file")

    def test_error_does_not_hide_pointer_elsewhere(self):
        self.assertEqual(cp.check(fake({".claude/CLAUDE.md": NEW}, errors={"CLAUDE.md"})), "present in .claude/CLAUDE.md")

    def test_error_reported_with_detail(self):
        r = cp.check(fake({"AGENTS.md": "nothing here"}, errors={"CLAUDE.md"}))
        self.assertTrue(r.startswith("could not check: CLAUDE.md: HTTP 403"), r)

    def test_file_whose_content_is_MISSING(self):
        self.assertEqual(cp.check(fake({"CLAUDE.md": "MISSING"})), "missing line")

    def test_import_cycle_terminates(self):
        self.assertEqual(cp.check(fake({"CLAUDE.md": "@AGENTS.md", "AGENTS.md": "@CLAUDE.md"})), "missing line")

    def test_escape_above_root_ignored(self):
        self.assertEqual(cp.imports_in("@../../etc/x.md", "CLAUDE.md"), [])


if __name__ == "__main__":
    unittest.main(verbosity=1)
