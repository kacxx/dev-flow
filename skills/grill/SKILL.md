---
name: grill
description: Use when an idea, issue or plan has open questions to settle before it can be specified or ticketed. Settles them in rounds with the owner and records each answer as a D<n> decision.
---

# Grill

Settle every open question on an idea with the owner, in rounds, and record each answer as a numbered decision (`D1`, `D2` …) that later steps link to. Adapted from Matt Pocock's `grilling` (MIT, see `NOTICE`).

## 1. Load the questions and the facts

Work from the issue the owner names (`gh api repos/OWNER/REPO/issues/N --jq .body`, plus its comments), or the current conversation. Collect:
- its **Open questions**;
- its **To check** list (facts `capture` couldn't look up);
- any **existing decisions** (`D1`, `D2` …) in the body or comments. New decisions continue the numbering; never reuse an ID.

Look up every To check fact **before** the first round, with sub-agents (repo files, issues, docs). Finding facts is your job, never the owner's. A fact that answers a question settles it without asking; a fact that changes a question changes the round.

## 2. Map the questions

Treat the questions as a **design tree**: some answers depend on others. The **frontier** is every question whose prerequisites are already settled, so it can be asked now without guessing at an answer you haven't heard yet. Add any question the facts or earlier answers raise; drop any they settle.

## 3. Ask a round

Ask the **whole frontier at once**, numbered, each with your recommended answer, worded so "yes" accepts it:

```
❓ **Q1 - <question title>**: <question, with the options if there are several>

➡️ <your recommended answer, and why in one line>

---

❓ **Q2 - …**
```

Every open question the issue lists must appear in this round, unless it depends on another question in this round (it waits for a later round) or a fact you found settles it. Say which, in one line, for each question you hold back: never drop one silently, even if it looks trivial (a name is still a decision). End the round with: *Answer "yes" to accept all, or per question: "1 yes, 2 no: X, 3 skip".*

Accept answers in any form: "yes" (all recommendations), shorthand ("1 yes, 2 no: use labels, 3 skip"), or prose. "Skip" leaves the question open; say so in the record. If an answer is ambiguous, ask about that one question only.

## 4. Record, then repeat

After each round, record every settled answer as a decision:

```
**D<n>: <short title>.** <the decision, stated as fact>. <one line of why, if the owner gave or accepted a reason>.
```

A decision says exactly what the owner accepted or answered, and nothing more. Don't add reasons, mechanisms, names or consequences that weren't in the question, the recommendation or the owner's answer: anything extra is an unapproved decision. If the answer leaves something genuinely open, that's a new question for the next round.

Recompute the frontier: settled decisions unblock questions that depended on them. Ask the next round. Stop when the frontier is empty: every question decided or explicitly skipped, nothing silently assumed.

**Reopening a decision** (from `flag-decision`): grill that decision alone. The new answer keeps the **same ID**; keep the old text under a `Superseded (<date>)` note with the reason it changed.

## 5. Write the decisions record

Show the record to the owner and write it after they say yes. The record lists every decision, any skipped question, and the path for what comes next:

- **Short path** (no proposal doc): put the decisions into the **issue body** under `## Decisions`, replacing the answered Open questions. Edit the body, don't comment:
  ```bash
  gh api repos/OWNER/REPO/issues/N --jq .body          # current body, to edit
  gh api repos/OWNER/REPO/issues/N --method PATCH -F body=@- <<'BODY'
  <the edited body>
  BODY
  ```
  If nothing is left open, the issue can become `ready-for-agent` (add acceptance criteria; see `capture`).
- **Full path**: post the record as **one comment** on the issue, headed `## Decisions (grill, <date>)`. It's the record until `proposal` writes the decided doc.
  ```bash
  gh api repos/OWNER/REPO/issues/N/comments --method POST -F body=@- <<'BODY'
  <the decisions record>
  BODY
  ```

Use `gh api`, never `gh issue` (GraphQL fails in cloud sessions). Then give the next step: `proposal` (full path) or "ready to implement" (short path, nothing open).
