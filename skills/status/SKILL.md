---
name: status
description: Use when the owner asks where an idea is or what's next for it (/dev-flow:status owner/repo#N). Names its stage, the next action and who takes it, and offers the relabelling fix.
---

# Status

Tell the owner where an idea is and what happens next. A bundled script reads the source issue's state on GitHub and names its stage; you turn that into the hand-off. The only write is a mechanical fix the script names, and only after the owner says yes to it.

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
- `fixes`: mechanical fixes to offer the owner, each with `why`, the `write` it makes and the `command` that makes it. Today the only one is the relabelling fix: adding `ready-for-agent` to an open ticket whose `Blocked by:` names issues that have all closed. The script never offers it while a revision is in progress, nor for a `Blocked by: None` ticket with no label (paused on purpose) or a `needs-decision` one;
- `tickets`, `doc_prs`, `doc`: what it read.

If it prints `{"error": …}`, report the error and stop. Don't work the stage out by hand: the script is the one tested reading of the markers.

Stages, in the order that decides when several match (`docs/proposals/status.md`, D4):

| Stage | What it means |
|---|---|
| reopened | a decision was flagged (`needs-decision`) or reopened in the doc |
| revision in progress | a doc PR is open on an idea that already has tickets |
| done | every ticket is closed, or the issue itself is |
| in progress | tickets exist and some are open |
| decided, full path | the doc on `main` is decided, no tickets yet |
| proposal drafted | a doc PR is open, or the doc on `main` isn't decided |
| decided, awaiting proposal | `grill`'s record is a comment, no doc yet |
| decided, short path | decisions in the issue body, nothing open |
| questions open | open questions, no doc yet |

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

Unanswered `review_comments` come first under **Blocking now**, one line each with its author and link: the owner decides how each is answered. They don't change the stage. Then the owner steps, with the link (a PR to merge, an issue to close). An owner step that is answering questions (`grill`'s) goes under **Your decisions**, and so do the `fixes`, each with its `why` and the `write` it makes ("add `ready-for-agent` to #38: its blocker #37 has closed"). Agent steps go under **Then**, and `later` under **Later**. Offer to run the agent's step; don't run it until the owner says yes.

## 3. Apply the fixes the owner says yes to

Run a fix's `command` only after the owner says yes to that fix, and only the ones they named. Never offer a fix the script didn't list, and don't add `ready-for-agent` by hand to a ticket it left out: a `Blocked by: None` ticket with no label was paused on purpose. Tell the owner which labels you added; if a command fails, say which and why.
