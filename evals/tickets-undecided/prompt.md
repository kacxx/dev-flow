---
max_turns: 15
allowed_tools: [Skill]
---

This session can't reach GitHub, so here is the proposal from my repo kacxx/notes-cli; its source issue is #4. Slice it into tickets. Don't publish anything.

<doc>
# notes grill (#4): proposal

Status: **1 open**. Don't merge yet: D2 is reopened.

## Problem
My notes CLI has no way to think an idea through.

## Decisions

### D1: Command
The command is `notes grill <idea>`.

### D2: Questions
Status: reopened — consistency: D2 and D3 disagree on where answers go.

The questions come from a fixed list in `questions.md`, asked in order.

### D3: Storage
Answers are saved under the idea's heading in `ideas.md`.

## Shape
A new cobra subcommand under `cmd/`; reads `questions.md`; appends answers under the matching `## ` heading in `ideas.md`.

## Fact-check
| Claim | Result | Source |
|---|---|---|
| `notes` is a Go CLI built with cobra | ✅ | owner, issue #4 |

## Out of scope
Editing questions from the CLI.

## Risks
An idea heading that appears twice.
</doc>
