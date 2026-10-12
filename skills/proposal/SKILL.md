---
name: proposal
description: Use when an idea's decisions are settled and need writing up as a decided design doc, or when reviewing a design-doc PR (not /code-review). Writes the doc and fact-checks every claim.
---

# Proposal

Turn an issue's decisions into one decided design doc, `docs/proposals/<name>.md`, and check every factual claim in it before it merges. This is the review step for doc PRs: a design doc has no code for `/code-review` to check, but it has claims that can be wrong and decisions that can contradict each other.

## 1. Gather

Read the issue body and **every** comment:

```bash
gh api repos/OWNER/REPO/issues/N --jq .body
gh api --paginate repos/OWNER/REPO/issues/N/comments --jq '.[].body'
```

Find any existing doc or doc PR for this issue, so a second run updates it instead of creating a duplicate:

```bash
# open PRs that reference the issue (this skill writes "Refs #N" in every PR it opens)
gh api --paginate 'repos/OWNER/REPO/pulls?state=open' --jq '.[] | select(.body // "" | test("(Refs|Closes|Fixes) #N\\b")) | "#\(.number) \(.head.ref) \(.title)"'
# docs already on the default branch that name the issue in their title line
gh api 'repos/OWNER/REPO/contents/docs/proposals' --jq '.[].path' 2>/dev/null
```

Read any proposal doc whose first line names `(#N)`. If an open doc PR exists, work on its branch and update that PR (step 6).

Collect every decision (`### D<n>:` headings, or a `## Decisions (grill, …)` comment), every skipped or still-open question, and every looked-up fact. Decisions that only exist in comments go into the doc now: a decision left in a comment is how answers got lost before.

## 2. Write the doc

On a branch (or the existing PR's branch), with these sections in this order:

```markdown
# <Title> (#<issue>): proposal

Status: **<status>**. <Don't merge yet: … | Ready to merge, then slice into tickets.>

## Problem
<from the issue, with its concrete example>

## Decisions

### D1: <title>
<the decision, as recorded by grill: no new content>

### D2: <title> (revised YYYY-MM-DD)
<current text>

<details><summary>Superseded (YYYY-MM-DD)</summary>

<old text>

Reason: <what changed it>
</details>

## Open questions        ← only if grill skipped or left any open
1. <the question, as grill recorded it>

## Shape
<what gets built, at the level of components and interfaces: files, commands, data, how they connect. No more detail than the decisions settle.>

## Fact-check

| Claim | Result | Source |
|---|---|---|
| <a checkable statement the doc relies on> | ✅ / ⚠️ / ❌ + what was found | <file:line, URL, command run, or probe> |

## Out of scope
## Risks
```

The `<details>` block is the one superseded format; `grill` writes the same block when it revises a decision.

The `<status>` is exactly one of these, counted at the moment of writing:
- `decided`: nothing open, no fact a decision depends on is unchecked.
- `decided, M facts unchecked`: every decision settled, but M facts it depends on aren't checked yet.
- `N open`: N items open (reopened decisions plus open questions), and no unchecked facts.
- `N open, M facts unchecked`: both.

Use "fact" in the singular for 1. Only `decided` means the doc can merge.

Write decisions exactly as recorded. Changing one's meaning while writing it up is an unapproved decision; if the wording needs to change, that's a question for the owner. A question grill skipped goes under `## Open questions` with no D-number: it gets one only when grill settles it.

## 3. Fact-check every claim

List every checkable claim the doc relies on: what existing code, tools, docs or other projects do; what a platform supports; what a third-party file says. Check each one with sub-agents. Finding facts is your job, never the owner's.

Use the strongest evidence available, in this order:
1. **A probe in the real environment:** run it, call it, install it, read the actual file. Prefer this for anything testable: docs alone have been wrong about what an environment loads.
2. **The source:** code or files at a named commit.
3. **Official docs:** with the URL.
4. **Third-party reports:** mark ⚠️ and say so.

One row per claim. ✅ confirmed, ⚠️ partly confirmed or unverified (say what's missing), ❌ wrong (say what's true). Never leave a row without a source. A fact the owner states as checked counts as ✅ with the source "owner, <where they said it>".

## 4. Consistency pass

Read the decisions against each other, and against Shape and the tests. Look for one decision naming something another names differently (a label, a heading format, a file name), a test that can't pass given a decision, and a decision that assumes something another rules out. Each contradiction is either fixed, if it's a wording slip the owner already settled, or reopens the decision.

## 5. What blocks the merge

An item is **open** when:
- the fact-check finds a decision rests on a wrong claim (❌): reopen that decision;
- the consistency pass finds a real contradiction: reopen the decisions involved;
- grill skipped or left a question open: it's under `## Open questions`.

To reopen a decision, add `Status: reopened — <fact-check | consistency>: <one line>` under its heading and keep its current text. Settle it with `grill` on that decision alone: the revised text keeps the **same ID**, and the old text moves into the `<details>` superseded block.

**Unchecked facts also block the merge.** A ⚠️ row a decision depends on, still unverified (no access in this session, say), counts toward `M facts unchecked`; list what to check and how. An implementer would otherwise build on an unchecked assumption. A ⚠️ row nothing depends on can stay ⚠️ without blocking; say so in that row.

While the status isn't `decided`, the PR is a draft and the doc says plainly not to merge yet. When it is `decided`, end your reply to the owner with this line:

`Next step: to-tickets`

If the `to-tickets` skill isn't installed, add that it isn't, and that the tickets can be written by hand from the decisions (one per vertical slice, each opening with `Implements: D<n> — docs/proposals/<name>.md`). Never write that line for a doc that isn't `decided`.

## 6. Show, push, open or update the PR

In this order:
1. **Show the owner** the doc and the fact-check table. Wait for their yes.
2. **Commit and push** the branch: `git add docs/proposals/<name>.md && git commit -m "docs: <name> proposal (#N)" && git push -u origin <branch>`.
3. **Open the PR, or update the existing one** (step 1 found it), through REST, which works in cloud sessions:

```bash
# new PR, as a draft unless the status is decided
gh api repos/OWNER/REPO/pulls --method POST -f title='docs: <name> proposal' -f head=<branch> -f base=main -F draft=true -F body=@- <<'BODY'
Refs #N
<status, reopened decisions, open questions, unchecked facts>
BODY
# existing PR: the push already updated the diff; refresh its description
gh api repos/OWNER/REPO/pulls/P --method PATCH -F body=@- <<'BODY'
Refs #N
<…>
BODY
```

A PR's draft state can't be changed through REST (`draft` in a PATCH is ignored). When an existing draft becomes `decided`, mark it ready with `gh pr ready P` (GraphQL, which works locally). In a cloud session, where GraphQL fails, ask the owner to click **Ready for review**.
