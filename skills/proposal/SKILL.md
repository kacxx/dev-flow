---
name: proposal
description: Use when an idea's decisions are settled and need writing up as a decided design doc, or when reviewing a design-doc PR (not /code-review). Writes the doc and fact-checks every claim.
---

# Proposal

Turn an issue's decisions into one decided design doc, `docs/proposals/<name>.md`, and check every factual claim in it before it merges. This is the review step for doc PRs: a design doc has no code for `/code-review` to check, but it has claims that can be wrong and decisions that can contradict each other.

## 1. Gather

Read the issue body and **every** comment, and any existing proposal doc or doc PR for it:

```bash
gh api repos/OWNER/REPO/issues/N --jq .body
gh api --paginate repos/OWNER/REPO/issues/N/comments --jq '.[].body'
gh api -X GET search/issues -f q='repo:OWNER/REPO is:pr "docs/proposals"' --jq '.items[] | "#\(.number) [\(.state)] \(.title)"'
```

Collect every decision (`### D<n>:` headings, or a `## Decisions (grill, …)` comment), open question, skipped question and looked-up fact. If decisions only exist in comments, they go into the doc now: a decision left in a comment is how answers got lost before.

If an open doc PR already exists, update it rather than starting a second doc.

## 2. Write the doc

On a branch, with these sections in this order:

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

<details><summary>Superseded (YYYY-MM-DD): <one-line old version></summary>

<old text, and the reason it changed>
</details>

## Shape
<what gets built, at the level of components and interfaces: files, commands, data, how they connect. No more detail than the decisions settle.>

## Fact-check

| Claim | Result | Source |
|---|---|---|
| <a checkable statement the doc relies on> | ✅ / ⚠️ / ❌ + what was found | <file:line, URL, command run, or probe> |

## Out of scope
## Risks
```

The `<status>` is exactly one of these, counted at the moment of writing:
- `decided`: nothing open, no fact a decision depends on is unchecked.
- `decided, M facts unchecked`: every decision settled, but M facts it depends on aren't checked yet.
- `N decisions open`: N decisions reopened or skipped, and no unchecked facts.
- `N decisions open, M facts unchecked`: both.

Use "decision"/"fact" in the singular for 1. Only `decided` means the doc can merge.

Write decisions exactly as recorded. Changing one's meaning while writing it up is an unapproved decision; if the wording needs to change, that's a question for the owner.

## 3. Fact-check every claim

List every checkable claim the doc relies on: what existing code, tools, docs or other projects do; what a platform supports; what a third-party file says. Check each one with sub-agents. Finding facts is your job, never the owner's.

Use the strongest evidence available, in this order:
1. **A probe in the real environment:** run it, call it, install it, read the actual file. Prefer this for anything testable: docs alone have been wrong about what an environment loads.
2. **The source:** code or files at a named commit.
3. **Official docs:** with the URL.
4. **Third-party reports:** mark ⚠️ and say so.

One row per claim. ✅ confirmed, ⚠️ partly confirmed or unverified (say what's missing), ❌ wrong (say what's true). Never leave a row without a source. A fact the owner states as checked counts as ✅ with the source "owner, <where they said it>".

## 4. Consistency pass

Read the decisions against each other, and against Shape and the tests. Look for one decision naming something another names differently (a label, a heading format, a file name), a test that can't pass given a decision, and a decision that assumes something another rules out. Each contradiction is either fixed, if it's a wording slip the owner already settled, or becomes an open question.

## 5. Open decisions block the merge

A decision is **open** when the fact-check finds it rests on a wrong claim (❌), when the consistency pass finds a real contradiction, or when grill skipped it. For each one:
- Add `Status: reopened — <fact-check | consistency | skipped>: <one line>` under its heading, and keep the current text.
- Settle it with `grill` (on that decision alone). The revised text keeps the **same ID**, and the old text goes into a `Superseded (YYYY-MM-DD)` block with the reason.

While any decision is open:
- the Status line says `**N decisions open**`;
- the PR is a **draft**: open it with `"draft": true` (see step 6);
- say plainly that it shouldn't merge yet.

**Unchecked facts also block the merge.** If every decision is settled but a ⚠️ row a decision depends on is still unverified (no access in this session, say), the Status is `**decided, M facts unchecked**`, the PR stays a draft, and the doc lists what to check and how. An implementer would otherwise build on an unchecked assumption. A ⚠️ row nothing depends on can stay ⚠️ without blocking; say so in that row.

When nothing is open and no fact a decision depends on is unchecked: Status `**decided**`, mark the PR ready for review, and name the next step: `to-tickets`. Switching a PR between draft and ready uses GraphQL (`gh pr ready P`), which fails in cloud sessions. There, ask the owner to click **Ready for review**.

## 6. Open or update the PR

Commit the doc on its branch and open (or update) the PR through REST, which works in cloud sessions:

```bash
gh api repos/OWNER/REPO/pulls --method POST -f title='docs: <name> proposal' -f head=<branch> -f base=main -F draft=true -F body=@- <<'BODY'
<description>
BODY
```

Use `-F draft=false` when nothing is open. Its description names the issue (`Refs #N`), lists any decisions the fact-check or consistency pass reopened, and states whether it's ready to merge. Show the owner the doc and the fact-check table before pushing.
