#!/usr/bin/env python3
"""Tests for state.py. Run: python3 -I skills/status/scripts/test_state.py (or `python` on Windows)

Each file in fixtures/ is recorded `gh api` output, keyed by API path (state.py --record
writes the same format), with the stage and next action it must come out as. A path
the script asks for that the fixture doesn't hold fails the test, so a fixture can't
silently answer with nothing.
"""
import base64
import copy
import glob
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import state  # noqa: E402

FIXTURES = sorted(glob.glob(os.path.join(HERE, "fixtures", "*.json")))


def load(name):
    with open(os.path.join(HERE, "fixtures", name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def replay(fx):
    def fetch(path):
        if path not in fx["api"]:
            raise AssertionError(f"fixture has no response for {path}")
        return copy.deepcopy(fx["api"][path])
    return state.compute(fetch, fx["repo"], fx["number"])


class Fixtures(unittest.TestCase):
    def test_each_fixture_comes_out_as_recorded(self):
        self.assertTrue(FIXTURES)
        for path in FIXTURES:
            with self.subTest(os.path.basename(path)):
                with open(path, encoding="utf-8") as f:
                    fx = json.load(f)
                out = replay(fx)
                self.assertEqual(out["stage"], fx["expect"]["stage"])
                self.assertEqual(out["next_action"], fx["expect"]["next_action"])
                self.assertTrue(out["evidence"])
                self.assertTrue(out["steps"])
                for step in out["steps"]:
                    self.assertIn(step["who"], ("owner", "agent"))

    def test_every_stage_has_a_fixture(self):
        stages = set()
        for path in FIXTURES:
            with open(path, encoding="utf-8") as f:
                stages.add(json.load(f)["expect"]["stage"])
        self.assertEqual(stages, set(state.PRECEDENCE))

    def test_aside_jot_95(self):
        """The case that motivated status (proposal D4, D7)."""
        out = replay(load("revision-in-progress-aside-jot-95"))
        self.assertEqual(out["stage"], "revision in progress")
        self.assertEqual(out["next_action"], "merge aside-jot#100, then update #97–#99")
        self.assertEqual([s["who"] for s in out["steps"]], ["owner", "agent"])
        # it matches several stages; precedence picks the first
        self.assertIn("in progress", out["also_matched"])
        self.assertIn("decided, short path", out["also_matched"])


def issue(number, body="", state_="open", labels=(), title="t"):
    return {"number": number, "title": title, "state": state_, "body": body, "labels": [{"name": n} for n in labels]}


def content(path, text):
    return {"path": path, "type": "file", "encoding": "base64", "content": base64.b64encode(text.encode()).decode()}


R = "repos/o/r"


def api(body="", state_="open", labels=(), comments=(), subs=(), flagged=(), prs=(), files=None, docs=None):
    """A minimal recorded state for o/r#1."""
    a = {
        f"{R}/issues/1": issue(1, body, state_, labels),
        f"{R}/issues/1/comments?per_page=100": [{"body": c} for c in comments],
        f"{R}/issues/1/sub_issues?per_page=100": list(subs),
        f"{R}/issues?state=open&labels=needs-decision&per_page=100": list(flagged),
        f"{R}/pulls?state=open&per_page=100": list(prs),
        f"{R}/contents/docs/proposals": None,
    }
    for number, names in (files or {}).items():
        a[f"{R}/pulls/{number}/files?per_page=100"] = [{"filename": n} for n in names]
    if docs:
        a[f"{R}/contents/docs/proposals"] = [{"name": p.split("/")[-1], "path": p, "type": "file"} for p in docs if "?ref=" not in p]
        for p, text in docs.items():
            a[f"{R}/contents/{p}"] = content(p.split("?")[0], text)
    return a


def run(a):
    return state.compute(lambda p: copy.deepcopy(a[p]), "o/r", 1)


DOC = "Status: **decided**. Ready to merge.\nSource: #1\n"


class Markers(unittest.TestCase):
    def test_code_pr_mentioning_the_issue_is_not_a_doc_pr(self):
        pr = {"number": 5, "title": "code", "body": "Refs #1", "head": {"sha": "abc"}}
        out = run(api(subs=[issue(2)], prs=[pr], files={5: ["cmd/main.go"]}, docs={"docs/proposals/x.md": DOC}))
        self.assertEqual(out["stage"], "in progress")
        self.assertEqual(out["doc_prs"], [])

    def test_refs_must_name_this_issue(self):
        pr = {"number": 5, "title": "doc", "body": "Refs #10", "head": {"sha": "abc"}}
        out = run(api(subs=[issue(2)], prs=[pr], docs={"docs/proposals/x.md": DOC}))
        self.assertEqual(out["stage"], "in progress")

    def test_doc_found_by_source_line_only(self):
        other = "Status: **2 open**.\nSource: #12\n"
        out = run(api(body="## Open questions\n\n1. Which?\n", docs={"docs/proposals/other.md": other}))
        self.assertEqual(out["stage"], "questions open")
        self.assertIsNone(out["doc"])

    def test_doc_not_decided_is_proposal_drafted(self):
        out = run(api(docs={"docs/proposals/x.md": "Status: **decided, 1 facts unchecked**.\nSource: #1\n"}))
        self.assertEqual(out["stage"], "proposal drafted")
        self.assertEqual(out["next_action"], "finish docs/proposals/x.md with `proposal`")

    def test_decided_doc_pr_is_for_the_owner_to_merge(self):
        pr = {"number": 5, "title": "doc", "body": "Refs #1", "head": {"sha": "abc"}}
        out = run(api(prs=[pr], files={5: ["docs/proposals/x.md"]}, docs={"docs/proposals/x.md?ref=abc": DOC}))
        self.assertEqual(out["stage"], "proposal drafted")
        self.assertEqual(out["steps"], [{"who": "owner", "do": "review and merge r#5"}])

    def test_reopened_line_in_doc(self):
        doc = DOC.replace("decided", "1 open") + "\n### D2: x\nStatus: reopened — fact-check: wrong\n"
        out = run(api(docs={"docs/proposals/x.md": doc}))
        self.assertEqual(out["stage"], "reopened")

    def test_superseded_reopened_line_does_not_count(self):
        doc = DOC + "\n### D2: x\n<details><summary>Superseded</summary>\nStatus: reopened — old\n</details>\n"
        out = run(api(docs={"docs/proposals/x.md": doc}))
        self.assertEqual(out["stage"], "decided, full path")

    def test_needs_decision_issue_pointing_back(self):
        flagged = [issue(9, "Implements: D1 — #1\nParent: #1\n", labels=["needs-decision"])]
        out = run(api(subs=[issue(2)], flagged=flagged))
        self.assertEqual(out["stage"], "reopened")
        self.assertEqual(out["next_action"], "settle the reopened decision in #9 with `grill`")

    def test_needs_decision_elsewhere_does_not_count(self):
        flagged = [issue(9, "Parent: #10\n", labels=["needs-decision"])]
        out = run(api(subs=[issue(2)], flagged=flagged))
        self.assertEqual(out["stage"], "in progress")

    def test_open_questions_none_is_not_open(self):
        out = run(api(body="## Decisions\n\n### D1: x\n\n## Open questions\n\nNone.\n"))
        self.assertEqual(out["stage"], "decided, short path")
        self.assertEqual(out["next_action"], "slice #1 with `to-tickets`")

    def test_to_check_keeps_short_path_open(self):
        out = run(api(body="## Decisions\n\n### D1: x\n\n## Open questions\n\nNone.\n\n## To check\n\n- a fact\n"))
        self.assertIsNone(out["stage"])

    def test_skipped_in_grill_record(self):
        record = "## Decisions (grill, 2026-10-15)\n\n### D1: x\nyes\n\n### Skipped\n\n- Q3, the name\n"
        out = run(api(comments=[record]))
        self.assertEqual(out["also_matched"], ["questions open"])
        self.assertEqual(out["stage"], "decided, awaiting proposal")

    def test_closed_issue_is_done_without_a_step(self):
        out = run(api(body="## Decisions\n\n### D1: x\n", state_="closed"))
        self.assertEqual(out["stage"], "done")
        self.assertIsNone(out["next_action"])

    def test_in_progress_lists_waiting_tickets(self):
        subs = [issue(2, "Blocked by: None (can start immediately)", state_="closed"),
                issue(3, "Blocked by: #2", labels=["ready-for-agent"]),
                issue(4, "Blocked by: #2, #3")]
        out = run(api(subs=subs))
        self.assertEqual(out["steps"], [{"who": "agent", "do": "implement #3"}])
        self.assertEqual(out["later"], ["#4 waits on #3"])

    def test_no_ready_ticket_goes_to_the_owner(self):
        out = run(api(subs=[issue(2, "Blocked by: None (can start immediately)")]))
        self.assertEqual(out["steps"][0]["who"], "owner")

    def test_ticket_points_at_its_parent(self):
        out = run(api(body="Implements: D1 — docs/proposals/x.md\nBlocked by: None\nParent: #7\n"))
        self.assertIsNone(out["stage"])
        self.assertIn("run status on #7", out["evidence"][0])


class Helpers(unittest.TestCase):
    def test_numbers(self):
        self.assertEqual(state.numbers([99, 97, 98]), "#97–#99")
        self.assertEqual(state.numbers([97, 98, 102]), "#97, #98, #102")
        self.assertEqual(state.numbers([]), "")

    def test_parse_target(self):
        self.assertEqual(state.parse_target("kacxx/aside-jot#95"), ("kacxx/aside-jot", 95))
        self.assertEqual(state.parse_target("aside-jot#95"), (None, None))

    def test_paginated_pages_are_merged(self):
        class P:
            returncode, stderr = 0, ""
            stdout = '[{"a": 1}]\n[{"a": 2}]'
        real = state.subprocess.run
        state.subprocess.run = lambda *a, **k: P()
        try:
            self.assertEqual(state.gh_fetch("x"), [{"a": 1}, {"a": 2}])
        finally:
            state.subprocess.run = real

    def test_404_is_none(self):
        class P:
            returncode, stdout = 1, ""
            stderr = "gh: Not Found (HTTP 404)"
        real = state.subprocess.run
        state.subprocess.run = lambda *a, **k: P()
        try:
            self.assertIsNone(state.gh_fetch("x"))
        finally:
            state.subprocess.run = real


if __name__ == "__main__":
    unittest.main()
