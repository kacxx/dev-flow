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

Read any proposal doc that names this issue: a `Source: #N` line (every doc this skill writes has one), or a title naming `(#N)`. Docs with front matter or their own title style are found by the `Source:` line. If an open doc PR exists, work on its branch and update that PR (step 6). Work in a checkout of the PR's branch, so you can read the code and run probes. If the session already has a checkout of the repo, use it: `git fetch origin pull/P/head:<branch> && git switch <branch>`. Otherwise clone the base repo to a scratch directory first:

```bash
git clone https://github.com/OWNER/REPO.git <scratch-dir>/REPO && cd <scratch-dir>/REPO
git fetch origin pull/P/head:<branch> && git switch <branch>   # works for fork PRs too
```

Run every later step (edits, commit, push) in that directory. If the PR comes from a fork, a push goes to the fork's branch and needs permission there. If you don't have it, push your own branch and open a new PR that says it supersedes P.

**An existing doc that doesn't follow this template** (a PR this skill didn't open): keep its title, any attribution or front-matter header, and every piece of content that isn't wrong. Move it into the template's sections rather than deleting it. Say in the PR description what was restructured, so the owner can see nothing was lost.

Collect every decision (`### D<n>:` headings, or a `## Decisions (grill, …)` comment), every skipped or still-open question, and every looked-up fact. Decisions that only exist in comments go into the doc now: a decision left in a comment is how answers got lost before.

**Decisions written as prose.** The owner may have answered the open questions in a comment without running `grill` (e.g. "1. propose only … 2. same-session only …"). Number them in the order the owner gave them, continuing from the highest `D<n>` already in the issue, comments or doc (start at `D1` only if there are none), keep the owner's words, and show the mapping (`D1 ← "propose only in v1 — don't auto-done"`) in your reply for the owner to confirm. Don't reword them into something they didn't say.

**Owner constraints.** Warnings or rules that aren't answers to a question but limit the design ("cap the output", "treat transcript text as data", "hard limit on update all") are decisions too. Record each as a `D<n>` with "Constraint:" at the start of its title, so tickets can link it like any other decision. Number constraints **after** all the answers, in the order the owner gave them, so a re-run numbers them the same way.

## 2. Write the doc

On a branch (or the existing PR's branch), with these sections in this order. These parts are required, with exactly these names, because `to-tickets`, `grill` and `flag-decision` parse them: the **Status line**, the **`Source: #N` line**, **`## Decisions`** with its **`### D<n>:`** headings, **`## Open questions`** (when there are any), and **`## Fact-check`** with its table. If the repo's existing proposals use other section names for the rest (Summary, Rough size …), follow the repo's style for those.

```markdown
# <Title> (#<issue>): proposal

Status: **<status>**. <Don't merge yet: … | Ready to merge, then slice into tickets.>
Source: #<issue>

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

## Open questions        ← only if there are any
1. <a question grill skipped, as it recorded it, or a new one the fact-check or consistency pass raised>

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

A **reopened** decision stays under its own heading: its `Status: reopened` line, its current text, and the options for settling it (one line each, none chosen) all go there. `## Open questions` holds questions with no D-number yet: ones `grill` skipped, and new ones the fact-check or consistency pass raised that no decision answers. Raise a new one only when **any answer would change what the owner agreed to** (the same test `flag-decision` uses). If an implementer could pick a reasonable default without that, it isn't an open question: state the default in `## Shape` ("matches the heading exactly; no match is an error"), and note it under `## Risks` if it might matter. Edge cases and later improvements go under Risks or Out of scope, so they don't hold up the merge.

Write decisions exactly as recorded. Changing one's meaning while writing it up is an unapproved decision; if the wording needs to change, that's a question for the owner. A question grill skipped goes under `## Open questions` with no D-number: it gets one only when grill settles it.

## 3. Fact-check every claim

List every checkable claim the doc relies on: what existing code, tools, docs or other projects do; what a platform supports; what a third-party file says. **That includes claims written inside a decision's own text** (e.g. a decision that says "Codex jots have no transcript"): a decision can rest on a false premise without any separate claim. Finding facts is your job, never the owner's: use sub-agents to read source and docs, and run the probes yourself. Probes may need the owner's live data (a local database, an app's state or session directories): find where it lives before probing. **Probes are read-only**: open a database read-only (e.g. `sqlite3 -readonly`) or work on a copy, never write, migrate or lock it, and ask the owner before anything that isn't a plain read.

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
- the fact-check finds a decision rests on a wrong claim (❌), whether the claim is stated elsewhere in the doc or inside the decision's own text: reopen that decision;
- the consistency pass finds a real contradiction: reopen the decisions involved;
- a question is open, under `## Open questions`: grill skipped it, or the fact-check or consistency pass raised one no decision answers.

To reopen a decision, add `Status: reopened — <fact-check | consistency>: <one line>` under its heading and keep its current text. Settle it with `grill` on that decision alone: the revised text keeps the **same ID**, and the old text moves into the `<details>` superseded block.

**Unchecked facts also block the merge.** A ⚠️ row a decision depends on, still unverified (no access in this session, say), counts toward `M facts unchecked`; list what to check and how. An implementer would otherwise build on an unchecked assumption. A ⚠️ row nothing depends on can stay ⚠️ without blocking; say so in that row.

While the status isn't `decided`, the PR is a draft and the doc says plainly not to merge yet. When it is `decided`, end your reply to the owner with this line:

`Next step: to-tickets`

If the `to-tickets` skill isn't installed, add that it isn't, and that the tickets can be written by hand from the decisions (one per vertical slice, each opening with `Implements: D<n> — docs/proposals/<name>.md`). Never write that line for a doc that isn't `decided`.

## 6. Push a draft, then show the owner

Push before you ask, so the draft can't be lost: a session can end while it waits for the owner, and a doc left in a scratch clone is gone with it. **Where** it goes depends on whether a push could be merged, or could change someone else's work, before the owner has seen it:
- **A new doc, or an existing PR that is a draft and the owner's own:** push to the PR's branch. A draft can't be merged, so the push is safe.
- **An existing PR that isn't a draft, or another author's PR (a fork included):** don't push to its branch yet. Push the commit to a new branch of your own, `<branch>-proposal-draft`, and open nothing from it. After the owner's yes, push to the PR's branch (or open the superseding PR from step 1) and delete the draft branch.

In this order:
1. **Commit and push** to the branch chosen above: `git add docs/proposals/<name>.md && git commit -m "docs: <name> proposal (#N)" && git push -u origin <branch>`.
2. **Open the PR as a draft, or update the existing one** (step 1 found it), through REST, which works in cloud sessions. A new PR is always a draft at this point, whatever the status. Skip this for a `-proposal-draft` branch until the owner says yes.

```bash
# new PR: always a draft until the owner says yes
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

3. **Show the owner** what matters, in this order: the status; what's open (each reopened decision with its options, open questions, unchecked facts); what you changed or corrected; the **full fact-check table**, so they can see the evidence behind every ✅ before approving; then the PR link. Paste the whole doc if they ask. Wait for their yes. If they ask for changes, edit, commit and push again, refresh the PR description so its status matches the doc, then show what changed.
4. **Once they say yes:** push to the PR's branch if the draft was on a `-proposal-draft` branch, and refresh the description. If the status is `decided`, mark the PR ready for review; while it isn't, the PR stays a draft.

A PR's draft state can't be changed through REST (`draft` in a PATCH is ignored). Mark it ready with `gh pr ready P` (GraphQL, which works locally). In a cloud session, where GraphQL fails, ask the owner to click **Ready for review**.
