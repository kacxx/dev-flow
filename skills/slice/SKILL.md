---
name: slice
description: Use when a design doc is decided, or a short-path issue's decisions are settled, and the work needs splitting into GitHub issues. Writes vertical tickets linked to their decisions.
---

# Slice

Break a decided proposal, or a short-path issue's decisions, into **tickets**: tracer-bullet vertical slices, each naming the decisions it implements and the tickets that **block** it. Adapted from Matt Pocock's `to-tickets` (MIT, see `NOTICE`).

## 1. Check the source is decided

Work from what the owner names: a proposal doc (`docs/proposals/<name>.md`) or a short-path issue. Read it in full, plus the source issue's body and every comment:

```bash
gh api repos/OWNER/REPO/issues/N --jq .body
gh api --paginate repos/OWNER/REPO/issues/N/comments --jq '.[].body'
```

Only slice something decided:
- **Proposal doc:** its Status line must read exactly `**decided**`. Anything else means stop, including `decided, M facts unchecked` (it starts with "decided" but isn't), `N open` and `N open, M facts unchecked`. Say what's open and that `proposal` needs to finish first.
- **Short-path issue:** it must have a `## Decisions` section with `### D<n>:` headings, and nothing left under Open questions or To check. If it already carries `ready-for-agent` and fits in one ticket, it **is** the ticket: say so and stop, because slicing it would put the same work up twice. Slice it only if it needs more than one ticket; step 6 then takes the label off the source issue.

Also stop if a decision is flagged: the source issue itself carries `needs-decision` (a short-path issue that was its own ticket), or any open issue labelled `needs-decision` has `Parent: #N` in its body. Either means a decision behind this source has been reopened by `flag-decision`, even though the doc's Status still says `decided`. Name it and point to `settle`.

```bash
gh api -X GET search/issues -f q='repo:OWNER/REPO is:issue is:open label:needs-decision "Parent: #N"' --jq '.items[] | "#\(.number) \(.title)"'
```

If search is refused (cloud sessions' GitHub proxy can block it), list the open `needs-decision` issues and filter on the body instead:

```bash
gh api --paginate 'repos/OWNER/REPO/issues?state=open&labels=needs-decision&per_page=100' --jq '.[] | select(.pull_request | not) | select(.body // "" | test("(?m)^Parent: #N\\s*$")) | "#\(.number) \(.title)"'
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

Give each ticket the decisions it implements and its **blocking edges**: the tickets that must finish before it can start. A ticket with no blockers can start immediately. Every decision should be implemented by at least one ticket; say so if one isn't (it may be out of scope, or need a ticket). Every ticket implements a decision: work none covers (an undecided risk, a gap you spot) is a question for the owner, not a ticket.

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

Iterate until the owner approves. **Stop here until they do:** no cold read, and nothing published.

## 5. Cold read

Once the owner has approved the breakdown, and before publishing, a fresh reader reads the tickets cold. Skip this step if the source has `Path: ready`.

**Write the full bodies** of the approved tickets in the step 6 template, with `T<n>` and `B<n>` for issue numbers. The reader reads these, and the owner approves them.

**Send them to a fresh reader:** a sub-agent given only what an implementer would have: the bodies, the decisions or doc their `Implements:` line points to, and the repo's name or path. Nothing from this conversation. Its prompt:

```
You're about to implement these tickets in <OWNER/REPO>, and nobody is around to ask. Read only: don't build, edit or post anything. Read the tickets, the decisions they point to, and the code. For each ticket, say:
1. What would you build?
2. Where would you build it?
3. How would you know you're done?
4. Every point where you'd have to guess or ask, one per line.
List the guesses; don't answer them.

<the drafted ticket bodies>

<the decisions or doc they point to>
```

With no sub-agent tool, the owner runs the prompt in a fresh session. If the findings are already given, sort them without sending another reader.

**Sort the findings,** one line each, every line labelled with its group, even under a heading per group:

```
- **real gap:** T1 — <finding>. <the decision the owner has to make>
- **default:** T2 — <something a developer would otherwise pick alone>. Proposed: <value>
- **known blocker:** T1 — <something outside the tickets that isn't true yet>. Track: <title> (<owner>)
```

Show the sort, then the full bodies with their `## Defaults`, even while real gaps are open, and ask the owner to confirm the sort and the values, or to move items. **Publish nothing until they confirm.**

**Defaults** go after Acceptance criteria as `## Defaults`, one line each, with no D-numbers; a ticket with none has no section. An implementer who finds one wrong changes it and says so in the PR, not through `flag-decision`.

**Real gaps** go to `settle`, run in this session with the gaps as its questions, without writing them under Open questions first. Tell it not to set `Path: ready` or `ready-for-agent` on the source issue.
- **Short path:** once they're decided, redraft the affected tickets, get the breakdown approved again (step 4), and read again.
- **Full path:** stop. `slice` is re-run once `settle` and `proposal` have the doc decided again. List the gaps under **Your decisions**, and write nothing else.

**Known blockers** go on the ticket's `Blocked by:`: a tracking issue proposed with the sort, titled with the blocker and who owns it, drafted as `B<n>`, or the issue the owner says already tracks it. One outside this repo is a full link or the tracker's key, never `owner/repo#N`, nor `#` right before a digit (write `AB 1234`): `status` reads every `#N` as an issue here.

**Rounds.** A round is one read and its sort, including one after a redraft. Stop when a round raises only defaults and blockers already recorded, and publish. If real gaps remain after round 2, ask the owner whether to continue.

If the owner stops, write the remaining gaps into the source issue body's `## Open questions` (`status` reads only the body). Then publish, leaving `ready-for-agent` off every ticket a remaining gap was cited against, and name them in the hand-off. Known gap: on the full path, `status` ignores the source's Open questions once a doc exists.

## 6. Publish

Publish the tickets the owner confirmed in step 5 as GitHub issues **in dependency order** (blockers first), so each `Blocked by:` can name a real issue number: replace each `T<n>` and `B<n>` with its recorded number. Each body uses this template:

```markdown
Implements: D2, D4 — docs/proposals/<name>.md
Blocked by: #12
Parent: #N

## What to build

<the end-to-end behaviour this ticket makes work, from the user's side, not a layer-by-layer task list>

## Acceptance criteria

- [ ] <criterion>
- [ ] <criterion>

## Defaults

- <a default the owner approved in step 5>
```

- `Implements:` points at the proposal doc, or at the issue on the short path (`Implements: D2 — #N`).
- `Blocked by:` lists real issue numbers and external links, or `None (can start immediately)`.
- `## Defaults` only when step 5 approved some for this ticket.
- Avoid file paths and code snippets in the body: they go stale fast. The exception is a snippet a prototype produced that states a decision more precisely than prose (a schema, a state machine); trim it to the decision-rich part and say it came from a prototype.

**Labels.** `ready-for-agent` means an agent can start it now, so only tickets with **no** open blockers get it, and none held back in step 5. A blocked ticket gets the label when its blockers close; the report lists which. The owner labels one whose only blockers are external by hand.

Write through `gh api` (not `gh issue`, which uses GraphQL and fails in cloud sessions).

**Before the first ticket**, make sure the label exists, and check what's already published, so a re-run after a failure doesn't duplicate anything:

```bash
gh api repos/OWNER/REPO/labels/ready-for-agent --silent \
  || gh api repos/OWNER/REPO/labels --method POST -f name=ready-for-agent   # create only if missing; a real error stops here
gh api --paginate repos/OWNER/REPO/issues/N/sub_issues --jq '.[] | "#\(.number) \(.title)"'   # children already published
gh api --paginate 'repos/OWNER/REPO/issues?state=all&per_page=100' --jq '.[] | select(.body // "" | contains("Blocks a ticket under #N.")) | "#\(.number) \(.state) \(.title)"'   # tracking issues
```

A ticket whose title is already a child of `#N` was published by an earlier run: reuse its number, don't create it again.

**Tracking issues** come first, so tickets can cite their `#N`; record `B<n> → #<number>`. Reuse one listed above for the same blocker, open or closed (closed means resolved). Otherwise create one with no labels, no `Parent:` and no sub-issue link, so `status` skips it. Its body names only the source issue (`Blocks a ticket under #N.`); the owner closes it.

**Then, for each ticket in dependency order**, create it, link it, and record `T<n> → #<number>` before moving on:

```bash
TITLE=$(cat <<'TITLE'
<ticket title>
TITLE
)
gh api repos/OWNER/REPO/issues --method POST -f title="$TITLE" -F body=@- --jq '"\(.number) \(.id)"' <<'BODY'
<ticket body, with each T<n> and B<n> replaced by its recorded #number>
BODY
# only if no open blockers here or elsewhere, and not held back in step 5:
gh api repos/OWNER/REPO/issues/<number>/labels --method POST -f 'labels[]=ready-for-agent'
# link it under the source issue: sub_issue_id is the new issue's id (not its number)
gh api repos/OWNER/REPO/issues/N/sub_issues --method POST -F sub_issue_id=<id>
```

If any call fails, **stop**: report the `T<n>` and `B<n>` mapping so far and the error. A re-run picks up from the existing children and tracking issues. If only the sub-issue link fails (the repo may not have sub-issues enabled), keep the `Parent: #N` line, say the link failed, and carry on.

**The source issue** isn't closed or rewritten, except for step 5's early-stop edit. If it's a short-path issue carrying `ready-for-agent`, remove the label once the children are published, so the work can't be picked up twice:

```bash
gh api repos/OWNER/REPO/issues/N/labels/ready-for-agent --method DELETE
```

## 7. Report and hand off

Check the target repo's agent instructions for the `flag-decision` pointer line (the one copy is in `skills/flag-decision/SKILL.md`). It's the main bridge into flow 2: the skill's own description can trigger it too, but the line makes a Superpowers or Matt Pocock flow-2 agent (or Codex, via its fallback sentence) stop and flag rather than redesign. Run the bundled script from this skill's base directory:

```bash
python3 -I scripts/check_pointer.py OWNER/REPO
```

On Windows, run it with `python` if `python3` is the Microsoft Store stub (it exits 126 with "Permission denied").

It reads `CLAUDE.md`, `.claude/CLAUDE.md` and `AGENTS.md`, follows their `@….md` imports, and prints one result. Act on it:
- `present in <file>`: say nothing.
- `outdated in <file>`: the pointer predates the fallback sentence. Offer the current wording.
- `missing line`: offer the line, in the file that `CLAUDE.md` imports if it's just an import (e.g. `AGENTS.md`).
- `no instruction file`: offer to create `CLAUDE.md` with it.
- `could not check: …`: report the files and reasons it gives. Don't offer a line.

List the published tickets with their numbers, what each implements and what blocks it. Then say what's next.

**What's next**, in this order:
1. **Blocking now:** what's blocking, and who acts.
2. **Your decisions:** the owner's decisions, asked together.
3. **Then:** what the agent does once they're answered.
4. **Later:** later items, one line each.

Leave out a part with nothing in it.

- **Blocking now:** each open tracking issue, naming who owns it.
- **Your decisions:** any decision no ticket implements, named, and the pointer line or file offered above. The real gaps a full-path step 5 stopped on.
- **Then:** the tickets that can start now (labelled `ready-for-agent`), for an agent to implement, and writing the pointer once the owner says yes. After that stop: `settle`, `proposal`, then `slice` again.
- **Later:** each blocked ticket, one line each, saying it gets the label when its blockers close; one that also has an external blocker waits for the owner to label it by hand, so say no to `status`'s offer. Each ticket step 5 held back or whose only blockers are external, with its blocker or open question. For a proposal doc, also that the owner updates its Status line to `Status: **decided**. Merged and sliced into tickets (#…).`, naming the published tickets: `slice` doesn't edit the doc itself.
