---
name: capture
description: Use when the owner has a new idea, feature or problem to turn into a GitHub issue, before any design or code. Writes the issue and picks the lightest path to tickets.
---

# Capture

Turn an idea into one GitHub issue (problem, idea, open questions) and decide how much process it needs. The issue is the start of the idea → tickets flow; `grill`, `proposal` and `to-tickets` pick it up from here.

## 1. Find the repo, and check the idea isn't already captured

Work in the repo the owner names, or the current one (`gh api repos/{owner}/{repo}`; on a phone session, confirm which repo first).

Search open issues and PRs for the same idea before writing anything:

```bash
gh api "search/issues?q=repo:OWNER/REPO+is:open+KEYWORDS" --jq '.items[] | "#\(.number) \(.title)"'
```

If one matches, show it and offer to continue that one instead. Two parallel write-ups of one idea is the failure this step prevents.

## 2. Get the idea straight, not the design

If the problem or the idea is unclear, ask one short question. Don't interview: settling the design is `grill`'s job. Look up facts yourself (files, existing behaviour, other issues); never ask the owner for something you can read.

## 3. Draft the issue

```markdown
## Problem

<what goes wrong today, with a concrete example if there is one>

## Idea

<the proposed change, in a few lines or a short list>

## Open questions

1. <a decision the owner has to make, phrased as a question>
2. …
```

Idea says **what** changes, not **how**. Any "how" that isn't already settled (names, mechanisms, formats, where things live) is an open question, not part of the Idea. Settling it is `grill`'s job.

Open questions are **decisions**, not facts. A fact you can look up goes into Problem or Idea, already looked up. If there are none, write "None."

If a fact matters but you can't look it up in this session (no repo access, no shell), don't turn it into an open question. List it under a `## To check` heading after Open questions, so `grill` looks it up before asking anything.

## 4. Pick the path

Apply this test to every idea, and state the result and the reason under the draft:

| The idea has… | Path | What happens next |
|---|---|---|
| no open questions | **ready** | Add an `## Acceptance criteria` checklist to the issue and label it `ready-for-agent`. The issue *is* the ticket. |
| open questions the owner can answer now | **short** | Run `grill` in the issue; the decisions go into the issue body as `D1`, `D2` … No proposal doc. |
| anything needing design: a new interface or command, a cross-cutting change, or more than about three tickets | **full** | `grill`, then `proposal` (a decided doc), then `to-tickets`. |

Write it as: `Path: full, because <reason>. Reply "ready", "short" or "full" to override.`

## 5. Post it after the owner approves

Show the draft and the path. Post only after the owner says yes, and write through `gh api` (not `gh issue`, which fails in cloud sessions):

```bash
gh api repos/OWNER/REPO/issues --method POST -f title="<title>" -F body=@body.md
```

On the **ready** path, add `-f "labels[]=ready-for-agent"`, creating the label first if the repo hasn't got it.

Then give the issue link and the next step: `grill` (short or full path) or "ready to implement" (ready path).
