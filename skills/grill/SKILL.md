---
name: grill
description: Use when an idea, issue or plan has open questions to settle before it can be specified or ticketed. Settles them in rounds with the owner and records each answer as a D<n> decision.
---

# Grill

Settle every open question on an idea with the owner, in rounds, and record each answer as a numbered decision (`D1`, `D2` …) that later steps link to. Adapted from Matt Pocock's `grilling` (MIT, see `NOTICE`).

## 1. Load the questions, the decisions and the facts

Work from the issue the owner names, or the current conversation. Read the body **and every comment** (comments are paginated; without `--paginate` you only get the first 30):

```bash
gh api repos/OWNER/REPO/issues/N --jq .body
gh api --paginate repos/OWNER/REPO/issues/N/comments --jq '.[].body'
```

If the issue's Path line or a linked PR points at a proposal doc (`docs/proposals/<name>.md`), read that too: on the full path, decisions live there once it exists.

Collect:
- the **Open questions**;
- the **To check** list (facts `capture` couldn't look up);
- every **existing decision** (`### D<n>:` headings in the body, comments or proposal doc). New decisions continue the numbering from the highest ID found; never reuse an ID.

Look up every To check fact **before** the first round, with sub-agents (repo files, issues, docs). Finding facts is your job, never the owner's. A fact that answers a question settles it without asking; a fact that changes a question changes the round. Keep the facts you found: step 5 writes them back.

## 2. Map the questions

Treat the questions as a **design tree**: some answers depend on others. The **frontier** is every question whose prerequisites are already settled, so it can be asked now without guessing at an answer you haven't heard yet. Add any question the facts or earlier answers raise; drop any they settle.

## 3. Ask a round

Ask the **whole frontier at once**, numbered, each with your recommended answer, worded so "yes" accepts it:

```
❓ **Q1 - <question title>**: <question, with the options if there are several>

➡️ <your recommended answer>. <why, in one line>

---

❓ **Q2 - …**
```

Every open question the issue lists must appear in this round, unless it depends on another question in this round (it waits for a later round) or a fact you found settles it. Say which, in one line, for each question you hold back: never drop one silently, even if it looks trivial (a name is still a decision).

End the round with: *Answer "yes" to accept all, or per question: "1 yes, 2 no: X, 3 skip".*

Accept answers in any form: "yes" (all recommendations), shorthand ("1 yes, 2 no: use labels, 3 skip"), or prose. "Skip" leaves the question open; say so in the record. If an answer is ambiguous, ask about that one question only.

## 4. Record, then repeat

After each round, record every settled answer as a decision heading:

```markdown
### D<n>: <short title>

<the decision, stated as fact>
```

A decision contains only what the owner accepted or answered: the recommendation they said yes to (including its "why" line, if it had one), or their own alternative in their words. Add nothing else: no reasons, mechanisms, names or consequences that weren't in the question, the recommendation or the answer. Anything extra is an unapproved decision. If the answer leaves something open, that's a question for the next round.

Recompute the frontier: settled decisions unblock questions that depended on them. Ask the next round. Stop when the frontier is empty: every question decided or explicitly skipped, nothing silently assumed.

## 5. Write the decisions record

Show the record to the owner and write it after they say yes. Dates are `YYYY-MM-DD`. Write through `gh api`, never `gh issue` (GraphQL fails in cloud sessions).

**Short path** (no proposal doc): edit the **issue body**, don't comment:
1. Add `## Decisions` with the `### D<n>:` headings, and remove the answered questions from Open questions (write "None." if all are answered; list any skipped ones as still open).
2. Move each fact you looked up into Problem or Idea, and remove `## To check` once it's empty.
3. Update the `Path:` line. If nothing is left open (no open questions, no To check), set `Path: ready — <reason>`, add `## Acceptance criteria`, and label it `ready-for-agent`.

```bash
gh api repos/OWNER/REPO/issues/N --jq .body           # current body, to edit
gh api repos/OWNER/REPO/issues/N --method PATCH -F body=@- <<'BODY'
<the edited body>
BODY
# only when moving to ready:
gh api repos/OWNER/REPO/labels --method POST -f name=ready-for-agent 2>/dev/null || true   # create it if missing
gh api repos/OWNER/REPO/issues/N/labels --method POST -f 'labels[]=ready-for-agent'
```

**Full path, before a proposal doc exists:** post the record as **one comment** headed `## Decisions (grill, YYYY-MM-DD)`, with the `### D<n>:` headings, the facts you looked up, and any skipped questions. It's the record until `proposal` writes the doc.

```bash
gh api repos/OWNER/REPO/issues/N/comments --method POST -F body=@- <<'BODY'
<the decisions record>
BODY
```

**Full path, once the proposal doc exists:** decisions live in the doc, so edit the `### D<n>:` headings there (on a branch, through a PR), never in a new comment. Two records of the same ID is the failure this rule prevents.

Then give the next step: `proposal` (full path, no doc yet), "ready to implement" (short path, nothing open), or the re-slice below (a reopened decision).

## Reopening a decision (from `flag-decision`)

A ticket labelled `needs-decision` says decision `D<n>` is wrong (its evidence comment is headed `## Decision flagged: D<n>`). If the decision doesn't yet carry `Status: reopened — #<ticket>` where it lives, add that line first.

1. Read the ticket's evidence comment, then grill **that decision alone**.
2. Revise it **where it lives** (the proposal doc, or the issue body on the short path): the new text keeps the **same ID**, the old text moves into a superseded block (the same format `proposal` uses): `<details><summary>Superseded (YYYY-MM-DD)</summary>` + the old text + `Reason: <what the ticket found>` + `</details>`, and the `Status: reopened` line is removed.
3. Find the open tickets built on it, and propose for each one whether it is updated, closed or split. Change nothing until the owner approves the list:
   ```bash
   gh api -X GET search/issues -f q='repo:OWNER/REPO is:issue is:open "Implements:" D<n>' --jq '.items[] | "#\(.number) \(.title)"'
   ```
   Read each body to confirm its `Implements:` line names `D<n>`: search matches loosely (a decision mentioned in a comment also matches).
4. Once the owner approves, apply the changes, then remove `needs-decision` from the flagged ticket:
   ```bash
   gh api repos/OWNER/REPO/issues/TICKET/labels/needs-decision --method DELETE
   ```
