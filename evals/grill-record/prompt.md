---
max_turns: 10
allowed_tools: [Skill]
---

Here is issue #1 from my repo kacxx/dev-flow (this session can't reach GitHub, so I've pasted it). It's on the full path.

<issue>
## Problem

Ideas get from "I want X" to "here are the tickets" ad hoc. aside-jot #78 / PR 79 is an example: an issue, then a doc PR, then `/code-review` run on a doc that has no code. Open questions were answered in an issue comment but never made it into the doc, and nobody checked the doc's claims against the code.

Superpowers' brainstorming adds process before value. Matt Pocock's grill → spec → tickets is closer, but it assumes his tracker setup and doesn't fact-check.

## Idea

Four small skills, each with a fixed output:

1. `capture`: idea → issue (problem, idea, open questions)
2. `grill`: one question at a time until every open question is decided, with a reason for each
3. `proposal`: write the decided doc and check its factual claims against the code (the review step for doc PRs)
4. `to-tickets`: slice it into small end-to-end issues that link back to the decision each implements

Implementation (flow 2) takes over from the tickets. The skills are plain `SKILL.md` files, so they work in Claude Code on the Mac and the Windows PC, and on the Android phone through claude.ai account skills. Piloted on aside-jot and shipledger first.

## Open questions

1. Ticket target: GitHub issues only for now, or design for Jira from the start?
2. Short path: how does a one-line idea skip grill and proposal, and who decides it's small?
3. Linking: what format does a ticket use to point back to its decision?
4. Way back: when flow 2 finds a decision was wrong, how does it reopen it?
5. Devices: what can each surface actually load (Claude Code plugin, claude.ai skills on Android, cloud sessions)? Not verified yet.
6. Starting point: adapt Matt's `grill-me` / `to-spec` / `to-tickets` text (licence permitting), or write from scratch?
</issue>

Earlier in this session you asked me this round:

❓ **Q1 - Ticket target**: GitHub issues only for now, or design for Jira from the start?

➡️ GitHub issues only for v1, with tickets described in neutral fields so a Jira writer can be added later. Both pilot repos use GitHub issues.

---

❓ **Q2 - Short path**: how does a one-line idea skip grill and proposal, and who decides it's small?

➡️ `capture` decides the path (ready / short / full) and says why; the owner can override in one word. It keeps the decision at the cheapest point.

---

❓ **Q3 - Linking**: what format does a ticket use to point back to its decision?

➡️ Decisions get stable IDs (D1, D2 …) and every ticket opens with "Implements: D<n> — <source>" / "Blocked by: #<n>". The header can be checked with one search.

---

❓ **Q4 - Way back**: when flow 2 finds a decision was wrong, how does it reopen it?

➡️ The agent stops and flags it, the decision is reopened and revised under the same ID, and affected tickets are re-sliced with the owner's approval. It stops silent redesign inside a ticket.

---

❓ **Q5 - Devices**: what can each surface load?

➡️ v1 is a Claude Code plugin on the Mac, with Windows confirmed by one install; the phone comes later. It keeps v1 to one packaging path.

---

❓ **Q6 - Starting point**: adapt Matt's grill-me / to-spec / to-tickets text, or write from scratch?

➡️ Adapt Matt Pocock's skills (MIT) for grill and to-tickets, and write capture and proposal new. His frontier rounds and slicing already work.

Answer "yes" to accept all, or per question: "1 yes, 2 no: X, 3 skip".

My answer: yes

Don't post anything.
