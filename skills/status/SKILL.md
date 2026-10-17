---
name: status
description: Use when the owner asks where an idea is or what's next for it (/dev-flow:status owner/repo#N). Names its stage and next action, then batches the owner's approvals and carries them out.
---

# Status

Tell the owner where an idea is and what happens next. A bundled script reads the source issue's state on GitHub and names its stage; you turn that into the hand-off, offer the owner's pending approvals as one batch, and carry out the ones they choose. Nothing is written without the owner's yes.

## 1. Read the state

The owner names the source issue as `OWNER/REPO#N` or its URL (the issue `capture` wrote, not one of its tickets). Run the bundled script from this skill's base directory:

```bash
python3 -I scripts/state.py OWNER/REPO#N
```

On Windows, run it with `python` if `python3` is the Microsoft Store stub (it exits 126 with "Permission denied").

It reads the issue, its comments, its sub-issues, the open and merged doc PRs and the proposal doc through `gh api`, GET only, and prints one JSON object:
- `stage`: one of the stages below, or `null` if none matched;
- `evidence`: what on GitHub put it in that stage;
- `also_matched`: other stages whose markers are also present, which the first match outranks;
- `steps`: the next action as steps in order, each with `who` (`owner` or `agent`) and `do`; `next_action` is the same steps joined;
- `later`: tickets waiting on others, one line each;
- `review_comments`: comments on the source issue posted since dev-flow's last write there (`last_write`: the latest decisions record, doc PR or published tickets), whoever wrote them, each with `author`, `created_at`, `url` and `first_line`;
- `fixes`: mechanical fixes, offered in the `batch`, each with `why`, the `write` it makes and the `command` that makes it. Today the only one is the relabelling fix: adding `ready-for-agent` to an open ticket whose `Blocked by:` names issues that have all closed. The script never offers it while a revision is in progress, nor for a `Blocked by: None` ticket with no label (paused on purpose) or a `needs-decision` one;
- `batch`: the owner's pending approvals, offered together: the agent's steps, then the `fixes`. Owner steps are never in it. Each item has `do`, the `writes` it would make (every one of them), and `shows_draft`; a fix also has its `why` and `command`;
- `tickets`, `doc_prs`, `doc`: what it read.

If it prints `{"error": …}`, report the error and stop. Don't work the stage out by hand: the script is the one tested reading of the markers.

Stages, in the order that decides when several match (`docs/proposals/status.md`, D4):

| Stage | What it means |
|---|---|
| parked | the owner put the idea on hold (the issue is labelled `parked`) |
| reopened | a decision was flagged (`needs-decision`) or reopened in the doc |
| revision in progress | a doc PR is open on an idea that already has tickets |
| done | every ticket is closed, or the issue itself is |
| in progress | tickets exist and some are open |
| decided, full path | the doc on `main` is decided, no tickets yet |
| proposal drafted | a doc PR is open, or the doc on `main` isn't decided |
| decided, awaiting proposal | `settle`'s record (headed `settle` or, older, `grill`) is a comment, no doc yet |
| decided, short path | decisions in the issue body, nothing open |
| questions open | open questions, no doc yet |

If `stage` is `parked`, say the idea is on hold and give the evidence line. There's no next action and nothing to offer: don't suggest work on it. The owner unparks it by removing the label. Stop there.

If `stage` is `null`, say no stage matched and give the evidence line (for a ticket, it names the issue to run `status` on instead). Stop there.

## 2. Hand off

Lead with one line: the stage, and the evidence for it in plain words. Mention `also_matched` only if the owner asks why it isn't one of those.

Then say what's next, using the `steps` and `later` from the script. Name decisions by what they decide, with the ID alongside ("the Windows form (D9)"), never the ID alone.

**What's next**, in this order:
1. **Blocking now:** what's blocking, and who acts.
2. **Your decisions:** the owner's decisions, asked together.
3. **Then:** what the agent does once they're answered.
4. **Later:** later items, one line each.

Leave out a part with nothing in it.

Unanswered `review_comments` come first under **Blocking now**, one line each with its author and link: the owner decides how each is answered. At **done** they go under **Later** instead, after the script's `later` items, one line each with its author and link: a comment posted while the idea was being finished, such as the owner's own wrap-up, isn't blocking anything, but it may start a follow-up (dev-flow#61's D1). They don't change the stage. Then the owner steps, with the link (a PR to merge, an issue to close). Owner steps stay under **Blocking now**, never in the batch: you don't do them on the owner's behalf. An owner step that is answering questions (`settle`'s) goes under **Your decisions**, as a question of its own.

Before handing off an `implement` step, check its tickets for open code PRs: the script doesn't match them yet (dev-flow#51's D4). List the open PRs, GET only:

```bash
gh api --paginate 'repos/OWNER/REPO/pulls?state=open&per_page=100' --jq '.[] | "#\(.number)\(if .draft then " (draft)" else "" end) \(.title): \([(.body // "") | scan("(?i)\\b(?:refs|closes|fixes) #[0-9]+")] | join(", "))"'
```

An open PR belongs to ticket #T when its body says `Refs`, `Closes` or `Fixes #T`, the same rule as for doc PRs (`#40` is not `#401`). Only the first `#N` after each keyword counts, as in `state.py`: "Closes #40, #41" names #40 only. For each such ticket, put "merge #P (for #T)" under **Blocking now** as an owner step, with the PR's link, or "draft PR #P is open (for #T)" if the PR is a draft, and take #T out of the `implement` step and its writes; drop the step once no ticket is left in it. Say only that the PR exists: no CI result or review state.

The `batch` goes under **Your decisions**, as one question: one item per batch entry, in the script's order, each naming every one of its `writes` ("add `ready-for-agent` to #38: its blocker #37 has closed"; "update #97–#99: edits to their bodies, shown to you first"). For an item with `shows_draft`, say its draft comes first. Offer nothing that isn't in the batch. **Then** says what the agent does with the chosen items; a step that waits on an owner step (the merge before "update #97–#99") runs once that's done. `later` goes under **Later**.

How to ask:
- **2–4 items:** one multi-select question (`AskUserQuestion` with `multiSelect`), one option per item.
- **One item, more than four, or no multi-select** (it isn't in your tools, as in some cloud and phone sessions): the same batch as a numbered list, answered with shorthand: item numbers ("1, 3"), "all", or "none".

Read the answer strictly: "1, 3" chooses items 1 and 3 only, "all" every item, "none" nothing. If the answer is unclear or names a number that isn't in the list, ask again rather than guess.

## 3. Carry out the chosen items

The selection is the yes only for writes named in full up front. Carry out the chosen items in the batch's order:
- **A fix:** run its `command`. Never offer a fix the script didn't list, and don't add `ready-for-agent` by hand to a ticket it left out: a `Blocked by: None` ticket with no label was paused on purpose.
- **An agent step without `shows_draft`** (implementing a `ready-for-agent` ticket): carry it out.
- **An agent step with `shows_draft`** (`slice`'s ticket bodies, `proposal`'s doc): run the skill that carries it out. It still shows its draft and waits for the owner's yes before it writes; choosing the item isn't that yes.
- **Updating tickets after a revision** ("update #97–#99"): no skill does this yet (dev-flow#46), and `slice` won't re-slice an issue that already has tickets, so don't hand it to `slice`. Draft the edits to each ticket's body yourself from the merged doc, show them, and write them only after the owner's yes.
- A skill that needs the owner's answers, like `settle`'s questions, still asks them.

Don't carry out an item that isn't chosen, or a step whose owner step hasn't happened yet: say what it waits on. Tell the owner what you wrote (which labels you added, which PRs you opened); if a command fails, say which and why.
