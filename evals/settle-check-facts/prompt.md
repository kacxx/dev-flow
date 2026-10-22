---
max_turns: 15
allowed_tools: [Skill, WebFetch]
---

This session has no `gh` or git access to my repo (it can still fetch public web pages), so here is issue #5 from my repo kacxx/notes-cli. It's on the short path. Settle its open questions with me. Don't post anything.

<issue>
## Problem

I keep half-formed ideas in `ideas.md` and lose track of which ones I've thought through.

## Idea

Add a `notes grill <idea>` command that interviews me about an idea, adapted from Matt Pocock's `grilling` skill (https://raw.githubusercontent.com/mattpocock/skills/49dd158/skills/productivity/grilling/SKILL.md). Grilling asks the user for any fact it needs, so `notes grill` should work the same way.

## Open questions

1. When `notes grill` needs a fact about my notes (which file an idea came from, whether it has been grilled before), does it ask me or look it up?
2. Where are the answers saved?

Path: short — one new command
</issue>
