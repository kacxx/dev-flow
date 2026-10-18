# Know where an idea is, and what's next (#35): proposal

Status: **decided**. Merged and sliced into tickets (#37–#41).
Source: #35
Renamed since: `grill` is now `settle` and `to-tickets` is now `slice` (0.12.0, #57); this doc keeps the old names as written.

## Problem

Once an idea is in flight, its state is spread across several places, and nothing puts it together:
- the proposal doc's Status line;
- the doc PRs, merged or open;
- the tickets, their `Blocked by:` lines and whether they carry `ready-for-agent`;
- review comments on the source issue;
- `needs-decision` issues pointing back at it.

To answer "what's next", the owner or an agent has to read all of them and reason it out.

Example (kacxx/aside-jot#95, 2026-10-14 and 15): after a review comment on #95, the next steps were split across:
- PR aside-jot#100 (open);
- three tickets with no label;
- an unfiled issue that the proposal's Risks asked for;
- a wrong fact in the issue body.

Working that out took a manual sweep of the repo, and the resulting to-do list was hard to act on:
- it mixed owners;
- it used internal labels ("D10's macOS chain");
- it buried the one blocking action (merge aside-jot#100);
- it scattered seven "say yes" items;
- it needed six separate approvals to get one ticket back to `ready-for-agent`.

Each skill also ends with its own "next step" wording, so the hand-off reads differently every time.

## Decisions

From the grill record on #35 (2026-10-15). D4 was revised and D9 added the same day after the consistency pass. D2, D4 and D6 were revised again after the review on PR #36, settled by grill on those decisions.

### D1: A skill that calls a bundled script
A skill that calls a bundled script. The script reads the GitHub state deterministically, so it can be tested in CI against recorded fixtures. The skill turns the result into the hand-off and asks the owner.

### D2: Report, and offer mechanical fixes (revised 2026-10-15)
It reports, and offers each mechanical fix for the owner's yes before applying it. That fixes #31's gap at the point where the state shows it. The relabelling fix (adding `ready-for-agent`) applies only to a ticket whose `Blocked by:` names at least one issue, all of them now closed, and only when no revision is in progress. A ticket marked `Blocked by: None` that has no label was paused on purpose, so it's left alone.

<details><summary>Superseded (2026-10-15)</summary>

It reports, and offers each mechanical fix (such as adding `ready-for-agent` to a ticket whose blockers have all closed) for the owner's yes before applying it. That fixes #31's gap at the point where the state shows it.

Reason: as written, it would relabel a ticket with `Blocked by: None` whose label had been removed on purpose (kacxx/aside-jot#97), undoing a deliberate pause. Found in the review on PR #36.
</details>

### D3: The shared "what's next" shape, in every skill (revised 2026-10-18)
In this order:
1. what's blocking now, and who acts;
2. the owner's decisions, asked together;
3. what the agent does once they're answered;
4. later items, one line each.

It's written into each skill's hand-off section in the same words, with a test that checks every SKILL.md has it. Each SKILL.md is what an agent loads, so the shape sits in the hand-off it governs rather than behind a pointer to another file; the test keeps the copies identical.

<details><summary>Superseded (2026-10-18)</summary>

It's written into each skill's hand-off section in the same words, with a test that checks every SKILL.md has it. The skills can't share a file, because the phone skills are separate ZIPs.

Reason: #72 dropped the phone route, so there are no phone ZIPs to keep apart, and both install routes carry the whole `skills/` folder. The copies stay: the shape is seven lines, no skill reads a file outside its own folder, and a shared file would add a read every agent has to remember to do. Settled in #77's D1.
</details>

### D4: Stages and their markers (revised 2026-10-15, twice; revised 2026-10-17, three times)
| Stage | Marker |
|---|---|
| questions open | anything still listed under the issue's Open questions (not "None."), or skipped in the latest grill record, while no proposal doc exists. Covers "captured" and "grilling", which look the same. Once a doc exists, its Status line decides |
| decided, short path | `## Decisions` in the body, and nothing left open |
| decided, awaiting proposal | a `## Decisions (grill, …)` comment on the issue, and no doc or doc PR for it. Next action: `proposal` |
| proposal drafted | an open doc PR, or a doc on `main` that isn't `decided` |
| decided, full path | the doc on `main` says `decided`, and there are no sub-issues |
| revision in progress | an open doc PR plus existing sub-issues. It goes ahead of "in progress", after "reopened". Next action: merge the revision, then update the tickets |
| in progress | sub-issues exist and some are open |
| done | every sub-issue is closed, or the ready issue itself is closed |
| reopened | a `needs-decision` child, or a `Status: reopened` line in the doc |
| parked | the source issue is open and labelled `parked`: the owner put it on hold. It goes ahead of every other stage, and has no next action |

A **doc PR** is an open PR that says `Refs #N`, `Closes #N` or `Fixes #N` **and** changes a file under `docs/proposals/`; a code PR that mentions the parent issue doesn't count.

**Review comments** on the source issue, posted since dev-flow's last write there (the latest decisions record, doc PR or published tickets), are listed as "unanswered review comments", whoever wrote them. They don't change the stage, but they come first in the "blocking now" part when there are any, except at done, where they go under "later", one line each.

<details><summary>Superseded (2026-10-17, third revision)</summary>

**Review comments** on the source issue, posted since dev-flow's last write there (the latest decisions record, doc PR or published tickets), are listed as "unanswered review comments", whoever wrote them. They don't change the stage, but they come first in the "blocking now" part when there are any.

Reason: at done, the last dev-flow write is the newest ticket being published, so the owner's wrap-up comment on closing came out as blocking (#35, reported in #61). Settled in #61's D1; the owner's own comments still count at every stage (#61's D2).
</details>

<details><summary>Superseded (2026-10-17, second revision)</summary>

The table above, without the `parked` row; everything else was the same.

Reason: parking an idea lived only in a comment, so `status` named a next action for issues the owner had put on hold (#45, #46, #47, #58 and #59 in the dev-flow audit, 2026-10-17). A `parked` label is now the marker. Approved by the owner with the audit's cleanup batches.
</details>

<details><summary>Superseded (2026-10-17)</summary>

| Stage | Marker |
|---|---|
| questions open | anything still listed under the issue's Open questions (not "None."), or skipped in the latest grill record, while no proposal doc exists. Covers "captured" and "grilling", which look the same. Once a doc exists, its Status line decides |
| decided, short path | `## Decisions` in the body, and nothing left open |
| decided, awaiting proposal | a `## Decisions (grill, …)` comment on the issue, and no doc or doc PR for it. Next action: `proposal` |
| proposal drafted | an open doc PR, or a doc on `main` that isn't `decided` |
| decided, full path | the doc on `main` says `decided`, and there are no sub-issues |
| revision in progress | an open doc PR plus existing sub-issues. It goes ahead of "in progress", after "reopened". Next action: merge the revision, then update the tickets |
| in progress | sub-issues exist and some are open |
| done | every sub-issue is closed, or the ready issue itself is closed |
| reopened | a `needs-decision` child, or a `Status: reopened` line in the doc |

A **doc PR** is an open PR that says `Refs #N` **and** changes a file under `docs/proposals/`; a code PR that mentions the parent issue doesn't count.

**Review comments** on the source issue, posted since dev-flow's last write there (the latest decisions record, doc PR or published tickets), are listed as "unanswered review comments", whoever wrote them. They don't change the stage, but they come first in the "blocking now" part when there are any.

Reason: `state.py` (`skills/status/scripts/state.py:156`) and `proposal` step 1 already accept `Refs|Closes|Fixes #N`, so D4's `Refs #N` alone disagreed with the code; settled for #45's question 3. The rest of D4 is unchanged.
</details>

<details><summary>Superseded (2026-10-15, second revision)</summary>

| Stage | Marker |
|---|---|
| questions open | an issue with a `Path:` line and no decisions record (covers both "captured" and "grilling", which look the same) |
| decided, short path | `## Decisions` in the body, and nothing left open |
| decided, awaiting proposal | a `## Decisions (grill, …)` comment on the issue, and no doc or doc PR for it. Next action: `proposal` |
| proposal drafted | an open PR that says `Refs #N`, or a doc on `main` that isn't `decided` |
| decided, full path | the doc on `main` says `decided`, and there are no sub-issues |
| in progress | sub-issues exist and some are open |
| done | every sub-issue is closed, or the ready issue itself is closed |
| reopened | a `needs-decision` child, or a `Status: reopened` line in the doc |

Reason: the review on PR #36 found that kacxx/aside-jot#95, the case that motivated `status`, came out as "in progress" with the wrong next action. There was no stage for a decided doc being revised after slicing; review comments weren't read; partly settled issues matched no stage; and a code PR mentioning the parent counted as a doc PR. Settled by grill on D4 alone.
</details>

<details><summary>Superseded (2026-10-15)</summary>

| Stage | Marker |
|---|---|
| questions open | an issue with a `Path:` line and no decisions record (covers both "captured" and "grilling", which look the same) |
| decided, short path | `## Decisions` in the body, and nothing left open |
| proposal drafted | an open PR that says `Refs #N`, or a doc on `main` that isn't `decided` |
| decided, full path | the doc on `main` says `decided`, and there are no sub-issues |
| in progress | sub-issues exist and some are open |
| done | every sub-issue is closed, or the ready issue itself is closed |
| reopened | a `needs-decision` child, or a `Status: reopened` line in the doc |

Reason: no stage covered the full path after `grill` and before `proposal`, where the decisions are in a `## Decisions (grill, …)` comment and there's no doc yet; #35 itself was in that state (consistency). Settled by grill on D4 alone: option (a), add the stage.
</details>

### D5: Named `status`
`status`, run as `/dev-flow:status owner/repo#12`. It says what it does, and doesn't clash with the other five.

### D6: Batched approvals (revised 2026-10-15)
It offers the owner's pending approvals as one multi-select, with every write each item would make named in it. The selection counts as the yes for those writes, and `status` then runs the skills that carry them out. A skill that needs the owner's answers, like `grill`'s questions, still asks them.

<details><summary>Superseded (2026-10-15)</summary>

It offers the owner's pending approvals as one multi-select, with every write each item would make named in it. The selection counts as the yes for those writes. A skill that needs the owner's answers, like `grill`'s questions, still asks them.

Reason: a recording slip. The owner's "yes" to the question on #35 covered "and then run the skills that carry them out", but the record left that half out. Found in the review on PR #36.
</details>

### D7: Testing
CI tests for the script, run on recorded `gh` JSON fixtures, one per stage, including the aside-jot#95 state. An eval case for the skill, with the script's recorded output in the prompt so no `gh` is needed, graded on the next action, who takes it, and the four-part shape.

### D8: #35 absorbs #31
D2 covers relabelling unblocked tickets, so #31 closes as covered by #35, with a link, and there's no second set of decisions for the same thing.

### D9: Available wherever the other skills are (revised 2026-10-18)
`status` is available wherever the other skills are.

<details><summary>Superseded (2026-10-18)</summary>

The owner's Windows Claude Code and the phone are the same account, so `status` is available wherever the other skills are.

Reason: the owner dropped the phone route: "the 'phone' is just my personal account" (#72). dev-flow's skills no longer ship as claude.ai account skills, so there's no phone set to be in. Settled in #72's D4.
</details>

## Shape


1. **`skills/status/SKILL.md`** (D1, D5). Given a source issue (`owner/repo#N`), it runs the script, then writes the hand-off in the D3 shape. It offers the owner's pending approvals and mechanical fixes as one batch (D2, D6), then runs the skills that carry them out.
2. **`skills/status/scripts/state.py`** (D1, D4). It reads the issue, its comments, its sub-issues and their labels and bodies, the open doc PRs (`Refs #N` and a change under `docs/proposals/`), and the proposal doc found by its `Source: #N` line. Everything goes through `gh api`, read-only. It prints one JSON object with these fields:
   - `stage`;
   - the evidence for the stage;
   - the tickets, each with its blockers and labels;
   - `review_comments`: comments on the source issue since dev-flow's last write there (D4);
   - `fixes`: mechanical fixes, such as a ticket whose `Blocked by:` names issues that are now all closed but which has no `ready-for-agent` (D2).

   Defaults the decisions don't settle:
   - When several stages match (aside-jot#95 has a ready Path line, a decided doc and open sub-issues), the stage is the **first** match in this order: parked, reopened, revision in progress, done, in progress, decided full path, proposal drafted, decided awaiting proposal, decided short path, questions open.
   - Blockers come from the `Blocked by:` lines `to-tickets` writes, not from GitHub's native issue dependencies.
3. **The D3 shape in every skill's hand-off** (D3). The same four-part wording goes into the hand-off section of all five skills and of `status`. A test (`scripts/test_handoff_shape.py`) checks that every `skills/*/SKILL.md` contains it word for word.
4. **Tests** (D7):
   - `skills/status/scripts/test_state.py` runs `state.py` against recorded `gh api` JSON under `skills/status/scripts/fixtures/`, one fixture per stage, including the aside-jot#95 state as recorded on 2026-10-15, whose expected stage is **revision in progress** with the next action "merge aside-jot#100, then update #97–#99". `scripts/run_tests.py` picks it up, so CI runs it.
   - An eval case, `evals/status-next-action/`, puts a recorded `state.py` output in the prompt. It's graded on the next action, who takes it, and the four-part shape.
5. **Where it's available** (D9): wherever the other skills are.
6. **README.** The Status section's known-gap line about #31 is replaced, and `status` is added to the skills list and the usage table.

## Fact-check

| Claim | Result | Source |
|---|---|---|
| Every D4 marker can be read through `gh api` | ✅ issue body and `Path:` line, comments (`## Decisions (grill, …)`), sub-issues with state and labels, open PRs filtered on `Refs #N`, and a doc's Status and `Source:` lines through the contents API | probe on kacxx/aside-jot#95 (body, sub-issues #97–#99, PR #100 `Refs #95`, `follow-up-jots.md` `Source: #95`, Status `decided`) and #78 |
| A bundled script travels in the account-skill ZIP (D1, D3) | ✅ the ZIP holds the whole skill folder | probe: `build()` on a `status/scripts/state.py` folder gave `status/SKILL.md`, `status/scripts/state.py`, `status/NOTICE`; `scripts/build_account_skills.py` |
| The phone skills are separate ZIPs and can't share a file (D3) | ✅ each skill is built into its own ZIP, holding only its own folder plus NOTICE | `scripts/build_account_skills.py` `build()` |
| Cloud sessions have Python to run the script (D1 in cloud sessions) | ✅ "Python 3.x with pip, …" is listed under installed tools | https://code.claude.com/docs/en/cloud-environments#installed-tools |
| An eval case can be graded without Bash or `gh` (D7) | ✅ the existing `proposal` and `tickets` cases put their inputs in the prompt and run with no Bash | `evals/RESULTS.md`; `evals/proposal-*/prompt.md` |
| A multi-select question is available (D6) | ⚠️ `AskUserQuestion` has `multiSelect` on the desktop and in the terminal, but the docs don't say whether cloud or mobile sessions have it. Nothing blocks: on the phone, the same batch can go as a numbered list answered with shorthand ("1, 3"), which `grill` already accepts | this session's tool list; https://code.claude.com/docs/en/tools-reference |
| The name `status` is free (D5) | ✅ no skill, script or eval uses it | `skills/`, `evals/` |
| `to-tickets` writes blockers only as `Blocked by:` lines (Shape 2) | ✅ | `skills/to-tickets/SKILL.md` step 5 |
| Ticket blockers exist only in the ticket body (issue #35's facts) | ❌ GitHub has native issue dependencies (`issues/N/dependencies/blocked_by`), but `to-tickets` doesn't set them, so they're empty on every dev-flow ticket. Nothing depends on this: Shape reads the `Blocked by:` lines | probe: `gh api repos/kacxx/aside-jot/issues/97/dependencies/blocked_by` → `[]`, `issue_dependencies_summary` all zero |
| `grill` records full-path decisions in a `## Decisions (grill, …)` comment before a doc exists (revised D4) | ✅ | `skills/grill/SKILL.md` step 5; #35's comment of 2026-10-15 |
| A doc PR can be told apart from a code PR by its files (revised D4) | ✅ the PR files API lists the changed paths; aside-jot#100 changes only `docs/proposals/follow-up-jots.md` | probe: `gh api repos/kacxx/aside-jot/pulls/100/files` |
| Comments since dev-flow's last write can be found (revised D4) | ✅ comments, PRs and sub-issues all carry `created_at` timestamps through the REST API | probe of #35's comments and aside-jot#95's sub-issues |
| A ticket paused on purpose looks like `Blocked by: None` with no label (revised D2) | ✅ aside-jot#97: `Blocked by: None (can start immediately)`, label removed after the review | probe of #97 |
| aside-jot#95 matches several D4 stages at once | ✅ a `Path: ready` line and `## Decisions` in the body, a decided doc on `main`, and three open sub-issues. That's why Shape 2 sets an order | probe of #95 |
| Issues captured by hand have no `Path:` line, so the revised D4 doesn't rely on one | ✅ aside-jot#78 has none | probe of #78's body |

## Out of scope
- Writing GitHub's native issue dependencies from `to-tickets`.
- Running on a schedule, or across every issue in a repo.
- Anything that writes without the owner's yes.

## Risks
- **Stage precedence:** a mixed issue like aside-jot#95 needs the order in Shape 2. A wrong order would name the wrong next action. The fixtures cover #95's state.
- **The shape test is word for word:** any rewording of the shared shape must change all six skills at once. That's the point of the test, but it makes small edits noisier.
