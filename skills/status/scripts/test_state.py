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
                self.assertEqual([c["created_at"] for c in out["review_comments"]], fx["expect"]["review_comments"])
                self.assertEqual([f["ticket"] for f in out["fixes"]], fx["expect"]["fixes"])
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
        # the review comment came before aside-jot#100, which answers it
        self.assertEqual(out["review_comments"], [])
        self.assertEqual(out["last_write"]["what"], "doc PR aside-jot#100 opened")

    def test_blockers_closed_offers_the_relabel(self):
        """dev-flow#35 once #37 closed: #38, #40 and #41 had no label (proposal D2)."""
        out = replay(load("in-progress-blockers-closed"))
        self.assertEqual([f["ticket"] for f in out["fixes"]], [38, 40, 41])
        self.assertEqual(out["fixes"][0]["command"],
                         'gh api repos/kacxx/dev-flow/issues/38/labels --method POST -f "labels[]=ready-for-agent"')
        self.assertEqual(out["later"], ["#39 waits on #38"])

    def test_aside_jot_97_pause_is_left_alone(self):
        """#97 says `Blocked by: None` and its label was removed on purpose (proposal D2)."""
        out = replay(load("in-progress-aside-jot-97-pause"))
        self.assertEqual(out["stage"], "in progress")
        self.assertEqual(out["fixes"], [])

    def test_only_get_requests(self):
        """Nothing is written without the owner's yes: the script never sends a method but GET."""
        calls = []

        class P:
            returncode, stdout, stderr = 0, "[]", ""
        real = state.subprocess.run
        state.subprocess.run = lambda args, **k: calls.append(args) or P()
        try:
            for path in FIXTURES:
                with open(path, encoding="utf-8") as f:
                    fx = json.load(f)
                fetched = []
                state.compute(lambda p: fetched.append(p) or copy.deepcopy(fx["api"][p]), fx["repo"], fx["number"])
                for p in fetched:
                    state.gh_fetch(p)
        finally:
            state.subprocess.run = real
        self.assertTrue(calls)
        for args in calls:
            self.assertEqual(args[:3], ["gh", "api", "--paginate"])
            self.assertFalse({"--method", "-X", "-f", "-F", "--field", "--raw-field", "--input"} & set(args), args)


def issue(number, body="", state_="open", labels=(), title="t", created_at=None):
    i = {"number": number, "title": title, "state": state_, "body": body, "labels": [{"name": n} for n in labels]}
    if created_at:
        i["created_at"] = created_at
    return i


def comment(body, at, login="someone"):
    return {"body": body, "created_at": at, "user": {"login": login}, "html_url": f"https://github.com/o/r/issues/1#{at}"}


def content(path, text):
    return {"path": path, "type": "file", "encoding": "base64", "content": base64.b64encode(text.encode()).decode()}


R = "repos/o/r"
READY = state.READY


def api(body="", state_="open", labels=(), comments=(), subs=(), flagged=(), prs=(), files=None, docs=None, closed=()):
    """A minimal recorded state for o/r#1."""
    a = {
        f"{R}/issues/1": issue(1, body, state_, labels),
        f"{R}/issues/1/comments?per_page=100": [c if isinstance(c, dict) else {"body": c} for c in comments],
        f"{R}/issues/1/sub_issues?per_page=100": list(subs),
        f"{R}/issues?state=open&labels=needs-decision&per_page=100": list(flagged),
        f"{R}/pulls?state=open&per_page=100": list(prs),
        f"{R}/pulls?state=closed&per_page=100": list(closed),
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

    def test_closes_and_fixes_count_like_refs(self):
        for word in ("Closes", "Fixes"):
            pr = {"number": 5, "title": "doc", "body": f"{word} #1", "head": {"sha": "abc"}}
            out = run(api(prs=[pr], files={5: ["docs/proposals/x.md"]}, docs={"docs/proposals/x.md?ref=abc": DOC}))
            self.assertEqual(out["stage"], "proposal drafted", word)

    def test_reopened_line_in_doc_pr_goes_to_grill(self):
        doc = DOC.replace("decided", "1 open") + "\n### D2: x\nStatus: reopened — consistency: no stage\n"
        pr = {"number": 5, "title": "doc", "body": "Refs #1", "head": {"sha": "abc"}}
        out = run(api(prs=[pr], files={5: ["docs/proposals/x.md"]}, docs={"docs/proposals/x.md?ref=abc": doc}))
        self.assertEqual(out["stage"], "proposal drafted")
        self.assertEqual(out["steps"], [{"who": "owner", "do": "settle the reopened decision in r#5 with `grill`"}])

    def test_doc_pr_that_deletes_the_doc(self):
        pr = {"number": 5, "title": "doc", "body": "Refs #1", "head": {"sha": "abc"}}
        a = api(prs=[pr], files={5: ["docs/proposals/x.md"]})
        a[f"{R}/contents/docs/proposals/x.md?ref=abc"] = None  # 404 at the head: the file is gone there
        out = run(a)
        self.assertEqual(out["stage"], "proposal drafted")
        self.assertEqual(out["doc_prs"][0]["docs"], {"docs/proposals/x.md": None})
        self.assertEqual(out["next_action"], "finish r#5 with `proposal`")

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

    def test_superseded_to_check_does_not_count(self):
        body = "## Decisions\n\n### D1: x\n\n## Open questions\n\nNone.\n\n<details>\n\n## To check\n\n- old fact\n\n</details>\n"
        self.assertEqual(run(api(body=body))["stage"], "decided, short path")

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


RECORD = "## Decisions (grill, 2026-10-15)\n\n### D1: x\nyes\n"


class ReviewComments(unittest.TestCase):
    def test_comments_after_the_decisions_record_are_listed(self):
        out = run(api(comments=[comment("before", "2026-10-15T08:00:00Z"), comment(RECORD, "2026-10-15T09:00:00Z"),
                                comment("Review: D1 misses the Windows case.\n\nmore", "2026-10-15T10:00:00Z", "rev")]))
        self.assertEqual(out["last_write"], {"at": "2026-10-15T09:00:00Z", "what": "the decisions record"})
        self.assertEqual([(c["author"], c["first_line"]) for c in out["review_comments"]],
                         [("rev", "Review: D1 misses the Windows case.")])

    def test_published_tickets_answer_earlier_comments(self):
        subs = [issue(2, created_at="2026-10-15T11:00:00Z")]
        out = run(api(subs=subs, comments=[comment(RECORD, "2026-10-15T09:00:00Z"), comment("x", "2026-10-15T10:00:00Z"),
                                           comment("after", "2026-10-15T12:00:00Z")]))
        self.assertEqual(out["last_write"]["what"], "ticket #2 published")
        self.assertEqual([c["first_line"] for c in out["review_comments"]], ["after"])

    def test_merged_doc_pr_is_a_write(self):
        merged = {"number": 5, "title": "doc", "body": "Refs #1", "merged_at": "2026-10-15T11:00:00Z"}
        code = {"number": 6, "title": "code", "body": "Refs #1", "merged_at": "2026-10-15T13:00:00Z"}
        out = run(api(closed=[merged, code], files={5: ["docs/proposals/x.md"], 6: ["main.go"]},
                      docs={"docs/proposals/x.md": DOC},
                      comments=[comment("x", "2026-10-15T10:00:00Z"), comment("y", "2026-10-15T12:00:00Z")]))
        self.assertEqual(out["last_write"]["what"], "doc PR r#5 merged")
        self.assertEqual([c["first_line"] for c in out["review_comments"]], ["y"])

    def test_without_a_write_every_comment_counts(self):
        a = api(body="## Open questions\n\n1. Which?\n", comments=[comment("x", "2026-10-15T10:00:00Z")])
        a[f"{R}/issues/1"]["created_at"] = "2026-10-15T09:00:00Z"
        out = run(a)
        self.assertEqual(out["last_write"]["what"], "the issue opened")
        self.assertEqual(len(out["review_comments"]), 1)

    def test_flag_decision_pointer_is_not_a_review_comment(self):
        out = run(api(comments=[comment(RECORD, "2026-10-15T09:00:00Z"),
                                comment("D1 flagged by #4: wrong. See #4 for the evidence.", "2026-10-15T10:00:00Z")]))
        self.assertEqual(out["review_comments"], [])


class Relabel(unittest.TestCase):
    def fixes(self, subs, **kw):
        return [f["ticket"] for f in run(api(subs=subs, **kw))["fixes"]]

    def test_all_blockers_closed(self):
        subs = [issue(2, "Blocked by: None", "closed"), issue(3, "Blocked by: #2", "closed"),
                issue(4, "Blocked by: #2, #3"), issue(5, "Blocked by: #2, #4")]
        self.assertEqual(self.fixes(subs), [4])

    def test_blocked_by_none_without_label_is_a_pause(self):
        self.assertEqual(self.fixes([issue(2, "Blocked by: None (can start immediately)"), issue(3, "x", "closed")]), [])

    def test_already_labelled(self):
        self.assertEqual(self.fixes([issue(2, "Blocked by: None", "closed"), issue(3, "Blocked by: #2", labels=[READY])]), [])

    def test_needs_decision_ticket_waits_on_grill(self):
        subs = [issue(2, "Blocked by: None", "closed"), issue(3, "Blocked by: #2", labels=["needs-decision"])]
        self.assertEqual(self.fixes(subs), [])

    def test_not_while_a_revision_is_in_progress(self):
        subs = [issue(2, "Blocked by: None", "closed"), issue(3, "Blocked by: #2")]
        pr = {"number": 5, "title": "doc", "body": "Refs #1", "head": {"sha": "abc"}}
        out = run(api(subs=subs, prs=[pr], files={5: ["docs/proposals/x.md"]}, docs={"docs/proposals/x.md?ref=abc": DOC}))
        self.assertEqual(out["stage"], "revision in progress")
        self.assertEqual(out["fixes"], [])
        self.assertEqual(self.fixes(subs), [3])  # the same tickets, with no revision open

    def test_blocker_outside_the_sub_issues(self):
        a = api(subs=[issue(2, "Blocked by: #9")])
        a[f"{R}/issues/9"] = issue(9, state_="closed")
        self.assertEqual([f["ticket"] for f in run(a)["fixes"]], [2])
        a[f"{R}/issues/9"] = None  # not found: can't say it's closed
        self.assertEqual(run(a)["fixes"], [])


class Helpers(unittest.TestCase):
    def test_numbers(self):
        self.assertEqual(state.numbers([99, 97, 98]), "#97–#99")
        self.assertEqual(state.numbers([97, 98, 102]), "#97, #98, #102")
        self.assertEqual(state.numbers([]), "")

    def test_parse_target(self):
        self.assertEqual(state.parse_target("kacxx/aside-jot#95"), ("kacxx/aside-jot", 95))
        self.assertEqual(state.parse_target("https://github.com/kacxx/aside-jot/issues/95"), ("kacxx/aside-jot", 95))
        self.assertEqual(state.parse_target("https://github.com/kacxx/aside-jot/pull/100"), (None, None))
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
