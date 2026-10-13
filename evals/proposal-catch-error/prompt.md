---
max_turns: 20
allowed_tools: [Skill, WebFetch]
---

This session has no `gh` or git access to my repo (it can still fetch public web pages), so here is issue #4 from my repo kacxx/notes-cli and its decisions comment. Write the proposal doc for it. Paste the full doc in your reply; don't write files or open a PR.

<issue>
## Problem

My notes CLI (`notes`) has no way to think an idea through. I keep half-formed ideas in `ideas.md` and lose track of which ones I've thought through.

## Idea

Add a `notes grill <idea>` command that interviews me about an idea and saves the answers.
</issue>

<comment>
## Decisions (grill, 2026-10-10)

### D1: Command
The command is `notes grill <idea>`.

### D2: Interview style
Adapt Matt Pocock's `grilling` skill (github.com/mattpocock/skills, skills/productivity/grilling/SKILL.md), which asks one question at a time.

### D3: Storage
Answers are saved under the idea's heading in `ideas.md`.
</comment>
