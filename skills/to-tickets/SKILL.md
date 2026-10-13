---
name: to-tickets
description: Use when a design doc is decided, or a short-path issue's decisions are settled, and the work needs splitting into GitHub issues. Writes vertical tickets linked to their decisions.
---

# To Tickets

Break a decided proposal, or a short-path issue's decisions, into **tickets**: tracer-bullet vertical slices, each naming the decisions it implements and the tickets that **block** it. Adapted from Matt Pocock's `to-tickets` (MIT, see `NOTICE`).

## 1. Check the source is decided

Work from what the owner names: a proposal doc (`docs/proposals/<name>.md`) or a short-path issue. Read it in full, plus the source issue's body and every comment:

```bash
gh api repos/OWNER/REPO/issues/N --jq .body
gh api --paginate repos/OWNER/REPO/issues/N/comments --jq '.[].body'
```

Only slice something decided:
- **Proposal doc:** its Status line must read exactly `**decided**`. Anything else means stop, including `decided, M facts unchecked` (it starts with "decided" but isn't), `N open` and `N open, M facts unchecked`. Say what's open and that `proposal` needs to finish first.
- **Short-path issue:** it must have a `## Decisions` section with `### D<n>:` headings, and nothing left under Open questions or To check. If it already carries `ready-for-agent` and fits in one ticket, it **is** the ticket: say so and stop, because slicing it would put the same work up twice. Slice it only if it needs more than one ticket; step 5 then takes the label off the source issue.

Tickets built on undecided work end up rebuilt. That's the failure this check prevents.

## 2. Explore the codebase (optional)

If you haven't already, look at the current code so the tickets fit what's there. Look for prefactoring that makes the work easier: "make the change easy, then make the easy change". A prefactor is its own ticket, done first.

## 3. Draft vertical slices

Break the work into **tracer-bullet** tickets:

- Each slice cuts a narrow but **complete** path through every layer the feature needs (data, logic, interface, storage, tests): vertical, not one layer at a time.
- The **first** ticket is the thinnest path that goes all the way through, however crude (e.g. ask one question *and* save the answer). Later tickets widen it. A ticket that stops short of a layer the feature needs ("asks the questions but doesn't save yet") is horizontal, not vertical.
- A finished slice can be demonstrated or verified on its own.
- Each slice fits in one fresh agent context.
- Any prefactoring comes first.

Give each ticket the decisions it implements and its **blocking edges**: the tickets that must finish before it can start. A ticket with no blockers can start immediately. Every decision should be implemented by at least one ticket; say so if one isn't (it may be out of scope, or need a ticket).

**Wide refactors are the exception.** One mechanical change whose blast radius spans the codebase (renaming a shared field, retyping a common symbol) can't land green as one slice. Sequence it as **expand–contract**: expand (add the new form beside the old), migrate the call sites in batches (each its own ticket, blocked by the expand), then contract (remove the old form, blocked by every batch).

## 4. Get the breakdown approved

Show the breakdown as a list numbered **T1, T2 …** (not `#1`: before publishing, `#1` reads as an existing issue). For each ticket give:
- **Title**
- **Implements:** the `D<n>` it delivers
- **Blocked by:** other tickets as `T<n>`, or "none"
- **What it delivers:** the end-to-end behaviour it makes work

Ask the owner:
- Is the granularity right (too coarse, too fine)?
- Are the blocking edges right? Does each ticket only depend on tickets that genuinely gate it?
- Should any be merged or split?

Iterate until the owner approves. **Publish nothing before that.**

## 5. Publish

Publish the approved tickets as GitHub issues **in dependency order** (blockers first), so each `Blocked by:` can name a real issue number: replace each `T<n>` with the number the earlier ticket got. Each body uses this template:

```markdown
Implements: D2, D4 — docs/proposals/<name>.md
Blocked by: #12
Parent: #N

## What to build

<the end-to-end behaviour this ticket makes work, from the user's side, not a layer-by-layer task list>

## Acceptance criteria

- [ ] <criterion>
- [ ] <criterion>
```

- `Implements:` points at the proposal doc, or at the issue on the short path (`Implements: D2 — #N`).
- `Blocked by:` lists real issue numbers, or `None (can start immediately)`.
- Avoid file paths and code snippets in the body: they go stale fast. The exception is a snippet a prototype produced that states a decision more precisely than prose (a schema, a state machine); trim it to the decision-rich part and say it came from a prototype.

**Labels.** `ready-for-agent` means an agent can start it now, so only tickets with **no** open blockers get it. A blocked ticket gets the label when its blockers close; the report lists which.

Write through `gh api` (not `gh issue`, which uses GraphQL and fails in cloud sessions).

**Before the first ticket**, make sure the label exists, and check what's already published, so a re-run after a failure doesn't duplicate anything:

```bash
gh api repos/OWNER/REPO/labels/ready-for-agent --silent \
  || gh api repos/OWNER/REPO/labels --method POST -f name=ready-for-agent   # create only if missing; a real error stops here
gh api --paginate repos/OWNER/REPO/issues/N/sub_issues --jq '.[] | "#\(.number) \(.title)"'   # children already published
```

A ticket whose title is already a child of `#N` was published by an earlier run: reuse its number, don't create it again.

**Then, for each ticket in dependency order**, create it, link it, and record `T<n> → #<number>` before moving on:

```bash
TITLE=$(cat <<'TITLE'
<ticket title>
TITLE
)
gh api repos/OWNER/REPO/issues --method POST -f title="$TITLE" -F body=@- --jq '"\(.number) \(.id)"' <<'BODY'
<ticket body, with each Blocked by T<n> replaced by its recorded #number>
BODY
# only if this ticket has no open blockers:
gh api repos/OWNER/REPO/issues/<number>/labels --method POST -f 'labels[]=ready-for-agent'
# link it under the source issue: sub_issue_id is the new issue's id (not its number)
gh api repos/OWNER/REPO/issues/N/sub_issues --method POST -F sub_issue_id=<id>
```

If any call fails, **stop**: report the `T<n> → #<number>` mapping so far and the error. A re-run picks up from the existing children. If only the sub-issue link fails (the repo may not have sub-issues enabled), keep the `Parent: #N` line, say the link failed, and carry on.

**The source issue** isn't closed or rewritten. If it's a short-path issue carrying `ready-for-agent`, remove the label once the children are published, so the work can't be picked up twice:

```bash
gh api repos/OWNER/REPO/issues/N/labels/ready-for-agent --method DELETE
```

## 6. Report

List the published tickets with their numbers, what each implements and what blocks it, and which can start now (labelled `ready-for-agent`). For each blocked ticket, say it gets the label when its blockers close. Name any decision no ticket implements.
