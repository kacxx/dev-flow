---
name: capture
description: Use when the owner has a new idea, feature or problem to turn into a GitHub issue, before any design or code. Writes the issue and picks the lightest path to tickets.
---

# Capture

Turn an idea into one GitHub issue (problem, idea, open questions) and decide how much process it needs. The issue is the start of the idea → tickets flow; `grill`, `proposal` and `to-tickets` pick it up from here.

## 1. Find the repo, and check the idea isn't already captured

Work in the repo the owner names, or the current one (`gh api repos/{owner}/{repo}`; on a phone session, confirm which repo first).

Search **all** issues and PRs, open and closed, for the same idea before writing anything. Pass the query with `-f` so `gh` encodes it (`#`, `&` and spaces would break a hand-built URL):

```bash
gh api -X GET search/issues -f q='repo:OWNER/REPO KEYWORDS' --jq '.items[] | "#\(.number) [\(if .pull_request then (if .pull_request.merged_at then "PR, merged" else "PR, \(.state)" end) else "issue, \(.state)" end)] \(.title)"'
```

Results mix issues and PRs: a PR is the work for an issue, not a duplicate of it. If an issue matches, show it with its state and offer to continue that one instead: an open one gets the new detail added (step 5), and a closed one, or a merged PR, may mean it's already done. Two write-ups of one idea is the failure this step prevents.

## 2. Get the idea straight, not the design

If the problem or the idea is unclear, ask one short question. Don't interview: settling the design is `grill`'s job. Look up facts yourself (files, existing behaviour, other issues); never ask the owner for something you can read.

## 3. Draft the issue

The sections always appear in this order (leave out the optional ones that don't apply):

```markdown
## Problem

<what goes wrong today, with a concrete example if there is one>

## Idea

<the proposed change, in a few lines or a short list>

## Open questions

1. <a decision the owner has to make, phrased as a question>
2. …

## Acceptance criteria        ← ready path only

- [ ] …

## To check                   ← only if there are facts you couldn't look up

- …
```

Idea says **what** changes, not **how**. Any "how" that isn't already settled (names, mechanisms, formats, where things live) is an open question, not part of the Idea. Settling it is `grill`'s job.

Open questions are **decisions**, not facts. A fact you can look up goes into Problem or Idea, already looked up. If there are none, write "None."

If a fact matters but you can't look it up in this session (no repo access, no shell), don't turn it into an open question. List it under `## To check`, so `grill` looks it up before asking anything.

## 4. Pick the path

Check these in order and take the **first** that matches, then state the result and the reason under the draft:

1. **Full** if the idea needs design: a new interface or command, a cross-cutting change, or more than about three tickets. This applies even when there are no open questions; the design questions just haven't been asked yet. Next: `grill`, then `proposal` (a decided doc), then `to-tickets`.
2. **Short** if there are open questions the owner can answer now. Next: `grill` in the issue; the decisions go into the issue body as `D1`, `D2` … No proposal doc.
3. **Ready** otherwise (no open questions, no design). Add `## Acceptance criteria` and label it `ready-for-agent`: the issue *is* the ticket.

Write it as: `Path: full, because <reason>. Reply "ready", "short" or "full" to override.`

**Overrides:** "short" and "full" always apply. "Ready" only applies once Open questions says "None": if questions remain, say which ones, and ask the owner to answer them (they become decisions in the issue body) or drop them. Never post a `ready-for-agent` issue with undecided questions.

## 5. Post it after the owner approves

Show the draft and the path. Post only after the owner says yes. Write through `gh api` (not `gh issue`, which fails in cloud sessions), and pipe the body in so no file is left behind:

```bash
gh api repos/OWNER/REPO/issues --method POST -f title='<title>' -F body=@- <<'BODY'
<the drafted issue body>
BODY
```

On the **ready** path, add `-f 'labels[]=ready-for-agent'`, creating the label first if the repo hasn't got it (`gh api repos/OWNER/REPO/labels -f name=ready-for-agent`).

**Adding to an existing open issue** (step 1 found a match): fold the new detail into its body under the right section, show the owner the change, then replace the body with the edited version:

```bash
gh api repos/OWNER/REPO/issues/NUMBER --jq .body     # current body, to edit
gh api repos/OWNER/REPO/issues/NUMBER --method PATCH -F body=@- <<'BODY'
<the edited body>
BODY
```

Edit the body rather than adding a comment: detail left in comments is how decisions got lost before.

## 6. Hand off

Give the issue link and the next step:
- **Ready:** "ready to implement".
- **Short or full:** run `grill` on the issue. If the `grill` skill isn't installed yet, settle the open questions by hand in the issue instead: ask them as one numbered list with a recommendation each, and write each answer into the issue body as `D1`, `D2` ….
- **Full:** after the decisions, a proposal doc (`proposal`) and then tickets (`to-tickets`). If those skills aren't installed yet, say so and stop at the decisions.
