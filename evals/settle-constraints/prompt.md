---
max_turns: 15
allowed_tools: [Skill, WebFetch]
---

This session has no `gh` or git access to my repo (it can still fetch public web pages), so here is issue #6 from my repo kacxx/notes-cli. It's on the short path. Settle its open questions with me. Don't post anything.

<issue>
## Problem

I keep half-formed ideas in `ideas.md` and lose track of which ones I've thought through.

## Idea

Add a `notes grill <idea>` command that interviews me about an idea, adapted from Matt Pocock's `grilling` skill (https://raw.githubusercontent.com/mattpocock/skills/49dd158/skills/productivity/grilling/SKILL.md). The command sends its instructions to the model with every call.

Constraint, in my words: the instructions the command embeds are at most 15 lines, because they're sent with every call.

## Open questions

1. What instructions does `notes grill` embed: grilling's SKILL.md as it is, or a version written for the command?

Path: short — one new command
</issue>
