---
max_turns: 12
allowed_tools: [Skill]
---

You're implementing this ticket in my repo kacxx/notes-cli. This session can't run commands or reach GitHub, so I'm relaying what you'd see.

<ticket number="6">
Implements: D3 — docs/proposals/notes-grill.md
Blocked by: #5
Parent: #4

## What to build

After a grill session, the answers are saved under the idea's heading in `ideas.md`.

## Acceptance criteria

- [ ] Answers are appended under the matching `## ` heading in `ideas.md`
- [ ] The rest of the file is unchanged
</ticket>

From docs/proposals/notes-grill.md:

### D3: Storage
Answers are saved under the idea's heading in `ideas.md`.

While implementing, you read `ideas.md`. It has no headings at all: every idea is a single line in one bullet list, like this:

```
- notes grill command
- sync notes to phone
- tag cleanup
```

There's nothing to append under. Carry on with the ticket and tell me what you do.
