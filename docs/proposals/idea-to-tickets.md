# Proposal: idea → tickets flow

Source: [#1](https://github.com/kacxx/dev-flow/issues/1) (problem, idea, open questions) and
the [grill record](https://github.com/kacxx/dev-flow/issues/1#issuecomment-6121177568)
of 12 Oct 2026. Once this doc merges it replaces that comment as the record.

**Path (D2):** full. Four skills plus packaging needs design.

## Problem

Ideas get from "I want X" to "here are the tickets" ad hoc. aside-jot #78 / PR 79 is the
example: an issue, then a doc PR, then `/code-review` on a doc with no code. Answers given in
an issue comment never reached the doc, and nobody checked the doc's claims against the code.

## The flow

Four small skills, each with a fixed output:

| Skill | In | Out |
|---|---|---|
| `capture` | an idea | an issue (problem, idea, open questions) and a path choice (D2) |
| `grill` | the open questions | one `D<n>` decision per question, each with its reason |
| `proposal` | the decisions | `docs/proposals/<name>.md`, with its factual claims checked against the code |
| `to-tickets` | the proposal (or the issue, on the short path) | small end-to-end GitHub issues, each with an `Implements:` header (D3) |

Implementation (flow 2) takes over from the tickets.

## Decisions

### D1: Ticket target

Status: decided

GitHub issues only for v1. A ticket is described in neutral fields (title, problem,
acceptance criteria, decisions it implements, what blocks it), so a Jira writer can be added
later without a redesign.

### D2: Short path

Status: decided

`capture` picks the path and says why; the owner can override in one word.

- **No open questions:** the issue becomes the ticket (acceptance criteria added, labelled `ready`).
- **Open questions answerable in one sitting:** grill them in the issue and write the
  decisions into the issue body. No proposal doc.
- **Needs design** (a new interface or command, a cross-cutting change, or more than about
  three tickets): the full path to a proposal doc.

The three-ticket cut-off gets tuned after the pilots.

### D3: Linking

Status: decided

Decisions get stable IDs (`D1`, `D2`, …) as headings in the proposal doc or, on the short
path, in the issue body. Every ticket opens with:

```
Implements: D2, D4 — docs/proposals/<name>.md
Blocked by: #12
```

An agent can find a decision's tickets with one search, and the IDs survive edits to the doc.

### D4: Way back

Status: decided

Stop and flag:

1. The implementing agent doesn't redesign inside the ticket. It comments with the evidence,
   names the decision it breaks, and labels the ticket `needs-decision`.
2. The decision is marked `Status: reopened — #<ticket>`, grilled on its own, and revised
   under the same ID, with the old text kept as superseded.
3. Open tickets that say `Implements: D<n>` are re-sliced, and the owner approves the list.

Flow 2 needs a one-line rule to stop and flag instead of redesigning. Not yet decided: where
that rule lives, since flow 2 is someone else's skills (README). Recommendation: put it in
each piloted repo's `CLAUDE.md`, and have `to-tickets` repeat it in every ticket body so an
agent sees it without any setup.

### D5: Devices

Status: decided, device checks pending (see fact-check)

v1 is a Claude Code plugin, used on the work Mac first, with Windows confirmed by one
install. After the pilots, the Android phone gets `capture` and `grill` only, as claude.ai
account skills, unless cloud Claude Code sessions prove the better phone route.

### D6: Starting point

Status: decided, adjusted by the fact-check

Adapt Matt Pocock's skills ([mattpocock/skills](https://github.com/mattpocock/skills) at
`49dd158`, MIT) and keep his licence notice in a `NOTICE` file.

- `grill` ← `grilling` (`grill-me` is only a one-line wrapper that calls it). Add: record
  each answer under a `D<n>` ID with its reason. It already gives a recommendation per
  question, so nothing to add there.
- `to-tickets` ← `to-tickets`. Cut the `/setup-matt-pocock-skills` tracker setup, the
  local-file output and the glossary/ADR references. Add the `Implements:` header and move
  `Blocked by` up into it (his template has it as the last section).
- `capture` and `proposal` are new.

Each skill is tested by reproducing #1's manual run.

## Fact-check

Claims in #1 and the grill record, checked on 12 Oct 2026.

| Claim | Result | Evidence |
|---|---|---|
| Matt's skills are MIT | ✅ True | `LICENSE` and `plugin.json` (`"license": "MIT"`) at `49dd158` |
| Skills named `grill-me`, `grilling`, `to-spec`, `to-tickets` exist | ✅ True | `skills/productivity/{grill-me,grilling}`, `skills/engineering/{to-spec,to-tickets}` |
| `grill-me` has content to adapt | ⚠️ Corrected | It is one line: "Call the Skill tool with `grilling`". The content is all in `grilling`. |
| `grill` should ask one question at a time | ⚠️ Conflict | `grilling` asks the whole "frontier" (every question whose prerequisites are settled) in one numbered round. See question below. |
| Need to add a recommendation to each question | ⚠️ Corrected | `grilling` already does: "number each question and give your recommended answer". |
| Cut glossary, ADR and tracker parts from `grill` | ⚠️ Corrected | `grilling` has none. They live in `grill-with-docs` (adds `domain-modeling`) and in `to-tickets`, which is where the cuts apply. |
| `to-tickets` assumes his tracker setup | ✅ True | Requires `/setup-matt-pocock-skills`; outputs local files or tracker issues, sub-issues, `ready-for-agent` label |
| `to-tickets` lacks a link back to decisions | ✅ True | Template has Parent, What to build, Acceptance criteria, Blocked by; no decision link |
| Plain `SKILL.md` skills ship as a Claude Code plugin | ✅ True | Matt's repo does exactly this (`.claude-plugin/plugin.json` + `marketplace.json`); copy that layout |
| Cloud Claude Code sessions load plugins and claude.ai account skills | ✅ Observed | The cloud session that wrote this doc listed both installed plugin skills and the owner's own account skills |
| claude.ai account skills load in the Android app | ❓ Unverified | Needs one test on the phone: upload `capture`, invoke it from Android |
| Plugin installs and runs on Windows | ❓ Unverified | D5 already plans one install to confirm |

### Question raised by the fact-check

**One at a time, or a round at a time?** #1 says `grill` asks one question at a time;
`grilling` asks every currently answerable question in one round. Recommendation: keep
rounds. #1's own grill settled six questions in one sitting, rounds suit the phone (fewer
round trips), and dependent questions still wait for a later round. Word it as "one round at
a time" in the skill.

## Out of scope for v1

Jira output (D1), phone support for `proposal` and `to-tickets` (D5), and flow 2 itself
beyond the stop-and-flag rule (D4).

## Next

`to-tickets` on this doc. A likely slice: plugin skeleton + `NOTICE`; `capture`; `grill`;
`proposal`; `to-tickets`; Android check; then the aside-jot and shipledger pilots.
