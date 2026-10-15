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

PARTS = ("Blocking now", "Your decisions", "Then", "Later")
PART_REF = re.compile(r"\*\*(?:%s)(?::\*\*|\*\*)" % "|".join(PARTS))


def headings(text):
    """(offset, title) of each `## ` heading, skipping lines inside ``` fences (templates)."""
    found, fenced, offset = [], False, 0
    for line in text.splitlines(keepends=True):
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced and line.startswith("## "):
            found.append((offset, line[3:].strip()))
        offset += len(line)
    return found


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
    start = text.index(SHAPE)
    before = [title for offset, title in headings(text) if offset < start]
    if not before or "hand off" not in before[-1].lower():
        return "shared shape isn't under a '## … Hand off' heading"
    after = [offset for offset, _ in headings(text) if offset > start]
    rest = text[start + len(SHAPE):after[0] if after else len(text)]
    if not PART_REF.search(rest):
        return "nothing after the shared shape says what goes in which part"
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
        good = "## 6. Hand off\n\n" + SHAPE + "\n- **Then:** run `grill`.\n"
        self.assertIsNone(problem(good))
        self.assertIsNone(problem(good.replace("\n", "\r\n")))
        for old, new in [("asked together", "asked at once"),
                         ("**Later:**", "**Afterwards:**"),
                         ("Leave out a part with nothing in it.\n", "")]:
            with self.subTest(change=old):
                self.assertIsNotNone(problem(good.replace(old, new)))

    def test_missing_or_misplaced_fails(self):
        mapping = "\n- **Then:** run `grill`.\n"
        self.assertIsNotNone(problem("## 6. Hand off\n\nGive the issue link.\n"))
        self.assertIsNotNone(problem("## 2. Draft\n\n" + SHAPE + mapping))
        self.assertIsNotNone(problem("## 6. Hand off\n\n" + SHAPE + "\n" + SHAPE + mapping))

    def test_needs_a_mapping_in_its_own_section(self):
        self.assertIsNotNone(problem("## 6. Hand off\n\n" + SHAPE + "\nGive the link.\n"))
        self.assertIsNotNone(problem("## 6. Hand off\n\n" + SHAPE + "\n## 7. Other\n\n- **Then:** x\n"))
        self.assertIsNone(problem("## 6. Hand off\n\n" + SHAPE + "\nAgent steps go under **Then**.\n"))

    def test_headings_in_fences_are_ignored(self):
        text = "## 6. Hand off\n\n```markdown\n## Problem\n```\n\n" + SHAPE + "\n- **Later:** x\n"
        self.assertIsNone(problem(text))

if __name__ == "__main__":
    unittest.main()
