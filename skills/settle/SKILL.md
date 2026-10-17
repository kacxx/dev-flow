---
name: settle
description: Use when an idea, issue or plan has open questions to settle before it can be specified or ticketed. Settles them in rounds with the owner and records each answer as a numbered decision (D1, D2…).
---

# Settle

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

**Full path, before a proposal doc exists:** post the record as **one comment** headed `## Decisions (settle, YYYY-MM-DD)`, with the `### D<n>:` headings, the facts you looked up, and any skipped questions. It's the record until `proposal` writes the doc.

```bash
gh api repos/OWNER/REPO/issues/N/comments --method POST -F body=@- <<'BODY'
<the decisions record>
BODY
```

**Full path, once the proposal doc exists:** decisions live in the doc, so edit the `### D<n>:` headings there (on a branch, through a PR), never in a new comment. Two records of the same ID is the failure this rule prevents.

## 6. Hand off

Once the record is written, say what's next.

**What's next**, in this order:
1. **Blocking now:** what's blocking, and who acts.
2. **Your decisions:** the owner's decisions, asked together.
3. **Then:** what the agent does once they're answered.
4. **Later:** later items, one line each.

Leave out a part with nothing in it.

- **Your decisions:** the questions the owner skipped, if they want another round now.
- **Then:** `proposal` (full path, no doc yet), "ready to implement" (short path, nothing open), or, for a reopened decision, the next step in the section below.
- **Later:** on the full path, `slice` once the proposal is decided.

**Parking an idea.** If the owner puts the idea on hold ("park it", "not now"), add the `parked` label to the issue, so `status` reports it as parked with no next action instead of naming work. Say why in one comment, with what would unpark it. Create the label first if the repo hasn't got it. Remove the label when the owner unparks it.

```bash
gh api repos/OWNER/REPO/labels/parked --silent \
  || gh api repos/OWNER/REPO/labels --method POST -f name=parked -f description="On hold by the owner"
gh api repos/OWNER/REPO/issues/N/labels --method POST -f 'labels[]=parked'
# to unpark:
gh api repos/OWNER/REPO/issues/N/labels/parked --method DELETE
```

## Reopening a decision

A decision is reopened in one of two ways, each with its own marker:
- **During implementation, by `flag-decision`:** a ticket is labelled `needs-decision` and has an evidence comment headed `## Decision flagged: D<n>`. Nothing is written into the doc or issue until the decision is revised.
- **While a proposal is drafted, by `proposal`'s fact-check or consistency pass:** the doc has `Status: reopened — <fact-check | consistency>: <reason>` under the decision's heading, with the options for settling it.

Either way:

1. Read the evidence (the ticket's comment, or the `Status: reopened` line and the fact-check rows it points to), then settle **that decision alone**.
2. **Fact-check the revised text before writing it.** An answer can bring in a new claim about the code or a platform ("the hook already parses the path", "nothing else reads this field"). Check each one the way `proposal` step 3 does: a probe or the source first; a fact the owner states as checked counts as ✅ with the source "owner, <where they said it>". Ask again if one turns out wrong. Record each check where the decision's facts live: a row in the doc's `## Fact-check` table, or, on the short path, a line in the issue's Problem or Idea with its source.
3. Revise it **where it lives**. For a proposal doc that isn't merged yet, that's the open doc PR's branch (find it as `proposal` step 1 does: `Refs #N` in its body), checked out with `git fetch origin pull/P/head:<branch> && git switch <branch>`, never a fresh branch from `main`. A merged doc is edited on a new branch, through a PR. On the short path, it's the issue body.
   - The heading keeps the **same ID** and gets ` (revised YYYY-MM-DD)`, as `proposal`'s template does.
   - The old text moves into a superseded block, the same format `proposal` uses: `<details><summary>Superseded (YYYY-MM-DD)</summary>` + the old text + `Reason: <what was found> (#<ticket>, fact-check or consistency)` + `</details>`.
   - Remove the `Status: reopened` line. In a proposal doc, recount its Status line (`proposal`'s grammar) and update any part of Shape the revision changes.
4. **Check for tickets built on the decision**, every time, including after a draft-proposal reopen: tickets can be written by hand from a draft. If the search finds none, say so and skip the re-slice. Otherwise propose for each one whether it is updated, closed or split, including the flagged ticket itself. Change nothing until the owner approves the list:
   ```bash
   gh api -X GET search/issues -f q='repo:OWNER/REPO is:issue is:open "Implements:" D<n>' --jq '.items[] | "#\(.number) \(.title)"'
   ```
   If search is refused (cloud sessions' GitHub proxy can block it), list the open issues and filter on the `Implements:` line instead. D-numbers are only unique within one source, so the line must also name this decision's source: `docs/proposals/<name>.md`, or `#N` on the short path:
   ```bash
   gh api --paginate 'repos/OWNER/REPO/issues?state=open&per_page=100' --jq '.[] | select(.pull_request | not) | select(.body // "" | test("Implements:[^\\n]*\\bD<n>\\b[^\\n]*(docs/proposals/<name>\\.md|#N\\b)")) | "#\(.number) \(.title)"'
   ```
   Read each body to confirm its `Implements:` line names `D<n>` **and** this decision's source. Search matches loosely: a decision mentioned only in a comment matches, and so does the same `D<n>` from another proposal.
5. Once the owner approves, apply the changes. Then, for a `flag-decision` reopen, take the flagged ticket off hold: remove `needs-decision`, and if the ticket is still valid and has no open blockers, put `ready-for-agent` back so an agent picks it up again (a ticket left with neither label is stranded):
   ```bash
   gh api repos/OWNER/REPO/issues/TICKET/labels/needs-decision --method DELETE
   gh api repos/OWNER/REPO/issues/TICKET/labels --method POST -f 'labels[]=ready-for-agent'   # only if still valid and unblocked
   ```
6. **Next step**, handed off in the shape under Hand off above. For a proposal doc, push the revision to its PR and refresh the PR description, then hand back to `proposal` to re-run its fact-check and consistency pass on the revised doc and mark the PR ready if it's now `decided`. On the short path, the issue is "ready to implement" once nothing is open.
