#!/usr/bin/env python3
"""Every skill's hand-off carries the shared "what's next" shape, word for word. Run: python3 -I scripts/test_handoff_shape.py (or `python` on Windows)

The skills can't share a file (each account skill is its own ZIP), so the wording is
copied into each SKILL.md and this test keeps the copies identical
(docs/proposals/status.md, D3). Rewording it means changing every skill and SHAPE here.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
EXPECTED = {"capture", "grill", "proposal", "to-tickets", "flag-decision", "status"}

SHAPE = """\
**What's next**, in this order:
1. **Blocking now:** what's blocking, and who acts.
2. **Your decisions:** the owner's decisions, asked together.
3. **Then:** what the agent does once they're answered.
4. **Later:** later items, one line each.

Leave out a part with nothing in it.
"""

HEADING = re.compile(r"^## (.*)$", re.M)


def skill_files():
    return {name: os.path.join(SKILLS, name, "SKILL.md")
            for name in sorted(os.listdir(SKILLS))
            if os.path.isfile(os.path.join(SKILLS, name, "SKILL.md"))}


def problem(text):
    """Why the text doesn't carry the shape in a hand-off section, or None if it does."""
    text = text.replace("\r\n", "\n")  # a Windows checkout may have CRLF
    count = text.count(SHAPE)
    if count != 1:
        return f"shared shape found {count} times, expected once (missing or reworded?)"
    headings = [m for m in HEADING.finditer(text) if m.start() < text.index(SHAPE)]
    if not headings or "hand off" not in headings[-1].group(1).lower():
        return "shared shape isn't under a '## … Hand off' heading"
    return None


class HandoffShape(unittest.TestCase):
    def test_every_skill_has_the_shape(self):
        files = skill_files()
        self.assertLessEqual(EXPECTED, set(files), "a skill folder is missing")
        for name, path in files.items():
            with self.subTest(skill=name):
                with open(path, encoding="utf-8", newline="") as f:
                    self.assertIsNone(problem(f.read()))

    def test_rewording_fails(self):
        good = "## 6. Hand off\n\n" + SHAPE
        self.assertIsNone(problem(good))
        self.assertIsNone(problem(good.replace("\n", "\r\n")))
        for old, new in [("asked together", "asked at once"),
                         ("**Later:**", "**Afterwards:**"),
                         ("Leave out a part with nothing in it.\n", "")]:
            with self.subTest(change=old):
                self.assertIsNotNone(problem(good.replace(old, new)))

    def test_missing_or_misplaced_fails(self):
        self.assertIsNotNone(problem("## 6. Hand off\n\nGive the issue link.\n"))
        self.assertIsNotNone(problem("## 2. Draft\n\n" + SHAPE))
        self.assertIsNotNone(problem("## 6. Hand off\n\n" + SHAPE + "\n" + SHAPE))


if __name__ == "__main__":
    unittest.main()
