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

Also stop if a decision is flagged: the source issue itself carries `needs-decision` (a short-path issue that was its own ticket), or any open issue labelled `needs-decision` has `Parent: #N` in its body. Either means a decision behind this source has been reopened by `flag-decision`, even though the doc's Status still says `decided`. Name it and point to `grill`.

```bash
gh api -X GET search/issues -f q='repo:OWNER/REPO is:issue is:open label:needs-decision "Parent: #N"' --jq '.items[] | "#\(.number) \(.title)"'
```

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

Check the target repo's `CLAUDE.md` (root and `.claude/`) for the `flag-decision` pointer line (see `skills/flag-decision/SKILL.md`). It's the main bridge into flow 2: the skill's own description can trigger it too, but the line makes a Superpowers or Matt Pocock flow-2 agent stop and flag rather than redesign. The check tells apart *present*, *missing line*, *no file* and *couldn't check*, so an error isn't mistaken for a missing pointer:

```bash
# reads a repo file; prints its text, or "MISSING" on 404; any other error goes to stderr and returns 1
read_file() { local out; if out=$(gh api "repos/OWNER/REPO/contents/$1" --jq '.content | @base64d' 2>&1); then printf '%s' "$out";
  elif printf '%s' "$out" | grep -q 'HTTP 404'; then echo MISSING; else echo "$1: $out" >&2; return 1; fi; }
has_pointer() { grep -qE 'run the `flag-decision` skill.*and stop'; }

repo_out=$(gh api "repos/OWNER/REPO" --silent 2>&1) || { echo "could not check: repo OWNER/REPO: $repo_out"; exit 0; }
result="no CLAUDE.md: offer to create one with the pointer"
for f in CLAUDE.md .claude/CLAUDE.md; do
  text=$(read_file "$f") || { result="could not check"; break; }
  [ "$text" = MISSING ] && continue
  result="CLAUDE.md has no flag-decision pointer: offer the line"
  if printf '%s' "$text" | has_pointer; then result="pointer present in $f"; break; fi
  # follow @file imports one level (e.g. CLAUDE.md containing "@AGENTS.md")
  for imp in $(printf '%s\n' "$text" | sed -n 's/^@\([^[:space:]]*\).*/\1/p'); do
    sub=$(read_file "$imp") || { result="could not check"; break 2; }
    [ "$sub" != MISSING ] && printf '%s' "$sub" | has_pointer && { result="pointer present in $imp (imported by $f)"; break 2; }
  done
done
echo "$result"
```

Act on the result: present, say nothing; missing line, offer it; no file, offer to create `CLAUDE.md` with it; couldn't check, report the error. `@file` imports are followed one level (a `CLAUDE.md` that is just `@AGENTS.md` is common). If the line might arrive another way (a deeper import, or a branch not yet merged), ask before offering a duplicate.


List the published tickets with their numbers, what each implements and what blocks it, and which can start now (labelled `ready-for-agent`). For each blocked ticket, say it gets the label when its blockers close. Name any decision no ticket implements.
