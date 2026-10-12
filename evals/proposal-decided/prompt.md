---
max_turns: 20
allowed_tools: [Skill]
---

This session can't reach GitHub, so here is issue #4 from my repo kacxx/notes-cli and its decisions comment. Write the proposal doc for it. Show me the doc; don't write files or open a PR.

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

### D2: Questions
The questions come from a fixed list in `questions.md`, asked in order.

### D3: Storage
Answers are saved under the idea's heading in `ideas.md`.
</comment>

Facts I've checked myself: `notes` is a Go CLI built with cobra, so a new subcommand is a new file under `cmd/`; `ideas.md` has one `## ` heading per idea; `questions.md` doesn't exist yet, and this work creates it; there is no `grill` command yet.
