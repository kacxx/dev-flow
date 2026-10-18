# An MVP check before design (#67): proposal

Status: **decided**. Slice into tickets once merged.
Source: #67

## Problem

Over-design happens before review can catch it. Review is a pressure test: it strengthens the design in front of it. Each round finds a real edge case and adds to the design. Nothing asks whether the design is the right size for the problem, so a design that has already ballooned only grows in review.

Case study: kacxx/notebook#7, tracked in kacxx/notebook#8. The ask was a way to tell whether a PR had been reviewed. It went straight from chat to a note, with no `capture` and no `settle`. In two review rounds it grew from a label idea into a workflow with live head lookups, `commit_id` pinning, a per-PR concurrency group and then a fix for that, plus rules for leaving bot PRs out of the metrics. None of it ran. On 2026-10-18, four fresh reviewers each recommended a smaller version (formal reviews with `commit_id`, checked by hand), and #7 was closed unmerged in its favour.

kacxx/notebook#8's pencil trial (stopped 2026-10-18, four rows) found that written wording in `settle` didn't reliably find the smaller version, a reader reviewing a round's recorded answer did (#51), and fresh reviewers asked "is there a smaller version?" did when the material already held its parts (#7).

## Decisions

Recorded by `settle` on #67: D1–D9 on 2026-10-17, D10–D13 on 2026-10-18. D4, D8, D10 and D11 were revised in the owner's review of PR #79.

### D1: The chat-started gap is in scope
Work that starts in chat and never reaches `capture` is in scope for this issue.

### D2: Skill changes wait for the pencil trial
No skill changes until kacxx/notebook#8's pencil trial reports (four sessions, or sooner if the pattern is clear). The trial is the smallest version and is already running; building the `settle` step first would repeat the mistake this issue is about.

### D3: Runs alongside #59
The MVP check comes first, and #59 stays parked. They ask different things (is it the right size, vs. does it work); the trial will show whether #59 is still needed.

### D4: Required on the short and full paths (revised 2026-10-18)
The check is required on the short and full paths only. Ready-path ideas are small by definition, so the check has nothing to shrink there. Having `capture` ask the three questions would cut against #68, where `capture`'s job is to record the idea and not shape it. For an idea that's already small, the answer is "this is the smallest version".

<details><summary>Superseded (2026-10-18)</summary>

The check is required on every path (ready, short, full). For an idea that's already small, the answer is "this is the smallest version".

Reason: the ready path never reaches `settle` (`capture` labels a ready issue `ready-for-agent` and the issue is the ticket), so a check that lives in `settle` can't run there (consistency). Settled in the owner's review of PR #79.
</details>

### D5: The answers are the first decision
The three answers are recorded as the first decision in the record, wherever the record lives: the issue body on the short path, the proposal doc on the full path.

### D6: Smallest version triable today → stop
When the smallest version can be tried today, `settle` stops and hands off "try it first", recording the signal that would justify going bigger.

### D7: Chat-side check: not a standing rule; choose after the trial
A standing rule in instructions or memory is ruled out: the CI-trial case in kacxx/notebook#8 broke exactly that kind of rule. The choice is between three options, made after the pencil trial using what it shows:
- (b) a hook that fires before an agent creates new files, CI or secrets;
- (c) the agent offers `capture` when a chat turns to building;
- (d) a proportionality question in the review prompt.

### D8: Evals only if a round skips the check (revised 2026-10-18)
Shape 1 and 2 ship first: one question in `settle` and one sentence in `proposal`. The evals are built only if a round skips the check.

<details><summary>Superseded (2026-10-18)</summary>

Tested with evals built from kacxx/notebook#7's starting ask and the CI-trial ask, each graded on whether the first round names the smallest version before any design.

Reason: the evals were the biggest build in the doc (two cases with LLM graders, made from paraphrased asks). The owner's review of PR #79 applied the MVP check to the doc itself.
</details>

### D9: Full path
Full path: the change crosses `settle`, `capture` and possibly hooks or review.

### D10: The chat-side check is (d), a proportionality question in the review prompt (revised 2026-10-18)
D7's choice is (d). It's the only option the trial tested, and on kacxx/notebook#7, the expensive chat-started case, it found and recommended the smaller version 4 of 4 times. But #7's material already held the smaller version, and on #51 it was 0 of 5. (b) and (c) are untested.

<details><summary>Superseded (2026-10-18)</summary>

D7's choice is (d). It's the only option the trial tested, and on kacxx/notebook#7, the expensive chat-started case, it found and recommended the smaller version 4 of 4 times. (b) and (c) are untested.

Reason: "4 of 4" read stronger than the evidence without its caveat. Owner's review of PR #79.
</details>

### D11: D4–D6 stand after the trial (revised 2026-10-18)
The MVP check still goes into `settle` as decided: required on the short and full paths, recorded as the first decision, and stopping when the smallest version can be tried today. The step costs one question, and its recorded answer is what a reviewer can challenge: #51's smaller version was found by a reader reviewing the round's own "can't be tried today".

<details><summary>Superseded (2026-10-18)</summary>

The MVP check still goes into `settle` as decided: required on every path, recorded as the first decision, and stopping when the smallest version can be tried today. The step costs one question, and its recorded answer is what a reviewer can challenge: #51's smaller version was found by a reader reviewing the round's own "can't be tried today".

Reason: D4 was revised to the short and full paths; D11 restates it (consistency).
</details>

### D12: Where (d)'s question goes
`proposal`'s review hand-off now, plus asking it by hand in chat review requests for now. A new review prompt only if a chat-started design grows again without the question being asked. The hand-off change is one sentence, and the by-hand part can be tried today.

### D13: #73 stays open
#73 is settled separately. #67 records only that its chat-side check is a question in the review prompt, not a spun-off agent loop. Whether to automate the fresh reader is #73's question.

## Shape

1. **`skills/settle/SKILL.md`: the MVP check opens the first round** (D4, D5, D6, D11). On the first `settle` run for an issue, Q1 of the first round is the MVP check, asked before any design question, with its three parts: what is the smallest version that answers the stated problem; can it be tried today without building anything; what signal would justify going bigger. The rest of the frontier is asked in the same round, as today. An idea that's already small answers "this is the smallest version".
   - **Recorded** as the first `### D<n>:` of that run's record (D5): in the issue body on the short path, in the `## Decisions (settle, …)` comment on the full path, which `proposal` then carries into the doc. A later `settle` run on the same issue doesn't ask it again.
   - **Stopping** (D6): when the answer is that the smallest version can be tried today, `settle` records the decision with its signal for going bigger, leaves the remaining questions under Open questions, and stops with a "try it first" hand-off. No label; a marker is added only if `status` misreads it.
   - **The ready path** doesn't run the check (D4).
2. **`skills/proposal/SKILL.md` step 7: the review request asks the proportionality question** (D10, D12). The **Blocking now** bullet's fresh code review of the doc PR also asks "…whether a smaller version answers the stated problem, including a smaller Shape for the same decisions." The check runs on the idea in `settle` (Shape 1), but a Shape can grow afterwards, while `proposal` turns the decisions into steps; this covers that second point. One sentence; the shared "what's next" block is unchanged, so `scripts/test_handoff_shape.py` still passes.
3. **Chat review requests** (D1, D12): nothing is built. The owner adds the question by hand when asking for a review in chat. A new review prompt is built only on D12's signal.
4. **Version** bumped in `.claude-plugin/plugin.json`.

No evals in this change (D8).

## Fact-check

Checked on 2026-10-18, main @ f741c0e.

| Claim | Result | Source |
|---|---|---|
| `settle`'s steps don't ask about the size of an idea | ✅ no "smallest", "MVP", "proportion" or "size" in the skill | `grep -i` on `skills/settle/SKILL.md` |
| The ready path never reaches `settle`: the issue is the ticket | ✅ "Add `## Acceptance criteria` and label it `ready-for-agent`: the issue *is* the ticket" | `skills/capture/SKILL.md:75` |
| #68: `capture`'s job is to record the idea, not shape it (D4) | ✅ a `capture` agent "pre-filled its own MVP answers and scope ('hand-apply a label for a week') into the idea"; the owner's feedback: "it needs to be the idea, not your interpretation of what's right" | #68 body |
| `status` names a next action from Open questions | ✅ an issue with questions under Open questions is "questions open", next action "answer … with `settle`" | `skills/status/SKILL.md` stage table; `state.py` output on #73, 2026-10-18 |
| The only review request dev-flow writes is in `proposal`'s hand-off, reaching doc PRs only | ✅ "the owner running a fresh code review of the doc PR (such as `/code-review`)", added by #60 (closed 2026-10-16) | `skills/proposal/SKILL.md:176`; #60 |
| The hand-off test checks only the shared "what's next" block, not the bullets after it | ✅ it counts and locates the `SHAPE` string in each `skills/*/SKILL.md` | `scripts/test_handoff_shape.py:16`, `:51` |
| #59 is parked | ✅ labelled `parked`, open | `gh api repos/kacxx/dev-flow/issues/59` |
| The pencil trial has reported (D2's condition) | ✅ "## Trial result (2026-10-18)": stopped at four rows | kacxx/notebook#8 body |
| On #7, fresh reviewers recommended the smaller version 4 of 4 times, with or without the permission line (D10) | ✅ | kacxx/notebook#8, Trial result |
| On #51, the smaller version was found by a reader reviewing the round (D11), and no context-free agent recommended it (0 of 5) | ✅ row 2: "A second agent (Chief of Staff) reviewing the round found the no-build version"; "0 of 5" | kacxx/notebook#8, table row 2 and Trial result |
| The CI-trial case broke a standing rule (D7) | ✅ "the agent had a standing memory rule saying almost exactly this … and broke it anyway" | kacxx/notebook#8, second case |
| If the evals are built (D8), the two starting asks are recorded word for word | ⚠️ not on GitHub: #7's ask is in paraphrase (kacxx/notebook#8, kacxx/notebook PR #7's body); the CI trial's idea is #62's Idea and kacxx/notebook#3. Nothing in this change depends on it | kacxx/notebook#8; kacxx/notebook PR #7; #62; kacxx/notebook#3 |

## Out of scope

- #59's challenge (D3) and #73's fresh-agent skill (D13).
- A hook (b) or a `capture` offer (c) for chat-started work (D10).
- A dedicated review prompt or skill, until D12's signal.
- Evals, until a round skips the check (D8).

## Risks

- **A written step may not find the smaller version.** The trial showed this (#51 missed on a clean snapshot). D11 keeps the step for its recorded answer, which a reviewer can challenge; D12's review question covers what the settling agent misses.
- **`status` after a "try it first" stop.** The remaining questions stay under Open questions, so `status` will likely report "questions open" and name `settle` as the next action, not "try it first". That would be the misread that justifies a marker (Shape 1).
- **No eval guards the step.** Until one is built (D8), a round that skips the check is caught only by the owner or a reviewer.
