---
name: capture
description: Use when the owner has a new idea, feature or problem to turn into a GitHub issue, before any design or code. Writes the issue and picks the lightest path to tickets.
---

# Capture

Turn an idea into one GitHub issue (problem, idea, open questions) and decide how much process it needs. The issue is the start of the idea → tickets flow; `settle`, `proposal` and `slice` pick it up from here.

## 1. Find the repo, and check the idea isn't already captured

Work in the repo the owner names, or the current one (`gh api repos/{owner}/{repo}`; on a phone session, confirm which repo first).

Search **all** issues and PRs, open and closed, for the same idea before writing anything. Pass the query with `-f` so `gh` encodes it (`#`, `&` and spaces would break a hand-built URL):

```bash
gh api -X GET search/issues -f q='repo:OWNER/REPO KEYWORDS' --jq '.items[] | "#\(.number) [\(if .pull_request then (if .pull_request.merged_at then "PR, merged" else "PR, \(.state)" end) else "issue, \(.state)" end)] \(.title)"'
```

If the search call fails (the GitHub proxy in cloud sessions can refuse `search/issues`), list every issue and PR instead and filter their titles and bodies on the same key words, written as a case-insensitive regex (`KEYWORDS` becomes e.g. `CI|workflow`):

```bash
gh api --paginate 'repos/OWNER/REPO/issues?state=all&per_page=100' --jq '.[] | select((.title + "\n" + (.body // "")) | test("KEYWORDS"; "i")) | "#\(.number) [\(if .pull_request then (if .pull_request.merged_at then "PR, merged" else "PR, \(.state)" end) else "issue, \(.state)" end)] \(.title)"'
```

Results mix issues and PRs: a PR is the work for an issue, not a duplicate of it. If an issue matches, show it with its state and offer to continue that one instead: an open one gets the new detail added (step 5), and a closed one, or a merged PR, may mean it's already done. Two write-ups of one idea is the failure this step prevents.

## 2. Get the idea straight, not the design

If the problem or the idea is unclear, ask one short question. Don't interview: settling the design is `settle`'s job. Look up facts yourself (files, existing behaviour, other issues); never ask the owner for something you can read.

If the idea turns on a key term with more than one reasonable meaning (what counts as "reviewed", "done", "stale"), that's unclear too: ask what the owner means, as your one question, and wait for the answer before drafting. Don't pick a meaning from context, and don't write the question down and carry on.

## 3. Draft the issue

The sections always appear in this order (leave out the optional ones that don't apply):

```markdown
## Problem

<what the owner said goes wrong, quoted or restated with nothing added>

Facts looked up:
- <a fact, with its source (file and commit, issue, command)>

## Idea

<the proposed change, in a few lines or a short list>

## Open questions

1. <a decision the owner has to make, phrased as a question>
2. …

## Acceptance criteria        ← ready path only

- [ ] …

## To check                   ← only if there are facts you couldn't look up

- …

Path: <ready|short|full> — <one-line reason>
```

The last line records the settled path in the issue, so `settle` and `proposal` in a later session can see it. It has no override prompt: that's for the owner in chat, not for the issue.

Problem opens with what the owner said, quoted or restated with nothing added: no framing of your own, and none borrowed from earlier issues or the chat. Facts you looked up go under `Facts looked up:` beneath it, each with its source and no framing sentence. Leave the list out if there are none.

Idea says **what** changes, not **how**: restate the outcome the owner asked for and any constraints they gave, and add nothing of your own. Every detail you would add (a behaviour, safeguard, name, mechanism, format, or where something lives) goes into Open questions as a choice, even when the answer seems obvious. Settling it is `settle`'s job, where it gets recorded as a decision.

Open questions are **decisions**, not facts. A fact you can look up goes under `Facts looked up:`, already looked up. If there are none, write "None."

An open question asks the question. List options only if the owner named them; don't offer designs from earlier issues, other repos or the chat. `settle` brings its own recommendation when it asks.

If a fact matters but you can't look it up in this session (no repo access, no shell), don't turn it into an open question. List it under `## To check`, so `settle` looks it up before asking a question that rests on it. An issue with anything under To check is never `ready-for-agent`: an implementer would be working on an unchecked assumption.

## 4. Pick the path

Check these in order and take the **first** that matches, then state the result and the reason under the draft:

1. **Full** if the idea, as the owner stated it, needs design: a new interface or command, a cross-cutting change, or more than about three tickets. This applies even when there are no open questions; the design questions just haven't been asked yet. Judge the idea as stated, not a version you imagine: "may need a new command" doesn't count. When in doubt, it's short. Next: `settle`, then `proposal` (a decided doc), then `slice`.
2. **Short** if there are open questions the owner can answer now. Next: `settle` in the issue; the decisions go into the issue body as `### D<n>:` headings. No proposal doc.
3. **Ready** only if there are no open questions, nothing under To check, and no design. Add `## Acceptance criteria` and label it `ready-for-agent`: the issue *is* the ticket. If To check is the only thing in the way, it's **short**: `settle` looks the facts up first.

Tell the owner, in chat (not in the issue): `Path: full, because <reason>. Reply "ready", "short" or "full" to override.`

**Overrides.** When the owner replies with a path, rebuild the draft for that path and show it again before posting:
- **→ ready:** only allowed when Open questions is "None" and To check is empty. Otherwise name what's in the way and ask the owner to answer the questions (each becomes a `D<n>` decision in the body) or drop them. Then add `## Acceptance criteria`, plan the `ready-for-agent` label, and set the Path line.
- **→ short or full:** remove `## Acceptance criteria` and the label, and set the Path line.

Never post a `ready-for-agent` issue with undecided questions or unchecked facts.

## 5. Post it after the owner approves

Show the draft and the path. Post only after the owner says yes. Write through `gh api` (not `gh issue`, which fails in cloud sessions), and pipe the body in so no file is left behind:

```bash
TITLE=$(cat <<'TITLE'
<title>
TITLE
)
gh api repos/OWNER/REPO/issues --method POST -f title="$TITLE" -F body=@- <<'BODY'
<the drafted issue body, ending with its Path line>
BODY
```

The quoted heredocs keep quotes, backticks and `$()` in the title and body literal; `"$TITLE"` expands the variable without re-expanding what's in it.

On the **ready** path, add `-f 'labels[]=ready-for-agent'`. Create the label first if the repo hasn't got it: `gh api repos/OWNER/REPO/labels --method POST -f name=ready-for-agent`. Creating an issue with a missing label fails with 422. Don't use `gh label create`: it uses GraphQL, which fails in cloud sessions.

**Adding to an existing open issue** (step 1 found a match): fold the new detail into its body under the right section, show the owner the change, then replace the body with the edited version:

```bash
gh api repos/OWNER/REPO/issues/NUMBER --jq .body     # current body, to edit
gh api repos/OWNER/REPO/issues/NUMBER --method PATCH -F body=@- <<'BODY'
<the edited body>
BODY
```

Edit the body rather than adding a comment: detail left in comments is how decisions got lost before.

**Parking an idea.** If the owner puts the idea on hold ("park it", "not now"), add the `parked` label to the issue, so `status` reports it as parked with no next action instead of naming work. Say why in one comment, with what would unpark it. Create the label first if the repo hasn't got it. Remove the label when the owner unparks it.

```bash
gh api repos/OWNER/REPO/labels/parked --silent \
  || gh api repos/OWNER/REPO/labels --method POST -f name=parked -f description="On hold by the owner"
gh api repos/OWNER/REPO/issues/N/labels --method POST -f 'labels[]=parked'
# to unpark:
gh api repos/OWNER/REPO/issues/N/labels/parked --method DELETE
```

## 6. Hand off

Give the issue link, then what's next.

**What's next**, in this order:
1. **Blocking now:** what's blocking, and who acts.
2. **Your decisions:** the owner's decisions, asked together.
3. **Then:** what the agent does once they're answered.
4. **Later:** later items, one line each.

Leave out a part with nothing in it.

A new issue has nothing blocking it, and its open questions are `settle`'s to ask, so a hand-off from `capture` is usually **Then** and **Later** only:
- **Ready:** **Then:** "ready to implement".
- **Short:** **Then:** run `settle` on the issue. If the `settle` skill isn't installed yet, settle the open questions by hand in the issue instead, under **Your decisions**: ask them as one numbered list with a recommendation each, and write each answer into the issue body under `## Decisions` as `### D1: <title>` headings.
- **Full:** **Then:** run `settle`, as on the short path. **Later:** after the decisions, a proposal doc (`proposal`) and then tickets (`slice`). If those skills aren't installed yet, say so and stop at the decisions.
