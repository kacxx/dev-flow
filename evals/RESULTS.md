# Eval results

Run with `claude plugin eval . --no-publish --runs 3 --judge-model sonnet` (no-plugin baseline arm on). Raw results are gitignored; this file is the record.

## capture — 12 Oct 2026 (plugin 0.1.0, commit after review fixes)

| Case | Expected path | Score (baseline) | path | sections | decisions | idea | pathline |
|---|---|---|---|---|---|---|---|
| capture-ready | ready | 1.00 (0.17) | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| capture-unchecked | short (fact can't be checked) | 1.00 (0.17) | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| capture-short | short | 0.94 (0.00) | 3/3 | 3/3 | 2/3 | 3/3 | 3/3 |
| capture-full | full | 0.83 (0.00) | 3/3 | 3/3 | 3/3 | 0/3 | 3/3 |

Path selection: 12/12 with the plugin. Known gap: on the full case the Idea section sometimes adds small choices of its own; one of the three failing runs was a pure restatement, so the `idea` grader is also stricter than intended.

Not covered by `claude plugin eval` on this machine: steps that need Bash (`gh` search, post, label). The eval sandbox refuses Bash because the local AWS config uses `credential_process`. Duplicate detection was checked with a sub-agent running the skill against kacxx/dev-flow with read-only `gh`: given #1's idea, it found #1 and offered to continue it. Posting is owner-approved and not automated.

## grill — 13 Oct 2026 (plugin 0.2.0, after the #15 review)

3 runs per case, no-plugin baseline. The test rounds in the prompts use the skill's own format, with real recommendations and reasons.

| Case | Check (grader type) | With | Without |
|---|---|---|---|
| grill-first-round (aside-jot#78, 4 questions) | Q1–Q4 all in one message, asked or held back with a reason (regex) | 3/3 | 0/3 |
| | "answer yes to accept all" line (regex) | 3/3 | 0/3 |
| | a recommendation for every question (llm) | 3/3 | 0/3 |
| | no decisions recorded before answers (llm) | 3/3 | 3/3 |
| grill-record (dev-flow#1, all "yes") | `### D1:` … `### D6:` headings in order (regex) | 3/3 | 0/3 |
| | each heading followed by its accepted recommendation, in order (regex) | 3/3 | 0/3 |
| | `## Decisions (grill, YYYY-MM-DD)` header (regex) | 3/3 | 0/3 |
| | stops: no new round (llm) | 3/3 | 3/3 |
| grill-shorthand (aside-jot#78, "1 yes, 2 no: X, 3 skip, 4 yes") | accepted, alternative and skipped answers recorded correctly (llm) | 3/3 | 3/3 |
| | IDs: no reuse, skipped question has no ID and is listed open (llm) | 3/3 | 3/3 |
| | `### D<n>:` heading format (regex) | 3/3 | 0/3 |

Scores: first-round 1.00 (0.20), record 1.00 (0.20), shorthand 1.00 (0.75).

**Fidelity** (decisions contain nothing beyond what was accepted): checked by hand, because an LLM judge failed verbatim outputs in both arms on every run. In a sampled record, each of D1–D6 is the accepted recommendation word for word, reason line included. Earlier "fidelity failures" came from a test prompt whose recommendations had no reasons, so any reason the model added really was invented; that prompt is fixed.

**LLM judges** swung between 3/3 and 0/3 on near-identical outputs. Anything mechanical is checked by regex.

## proposal — 13 Oct 2026 (plugin 0.3.0, after the #16 review)

3 runs per case, no-plugin baseline. The cases use a neutral project (kacxx/notes-cli), so the skill can't read its own text as facts. `catch-error` allows WebFetch, so the fact-check reads the real file. Regexes were self-tested against good and bad documents before use.

| Case | Check (grader type) | With | Without |
|---|---|---|---|
| proposal-catch-error (D2 claims Matt's `grilling` asks one question at a time) | sections in order + fact-check table header (regex) | 3/3 | 0/3 |
| | `Status: reopened` inside D2's own section (regex) | 3/3 | 0/3 |
| | D3 *not* reopened (regex) | 3/3 | 3/3 |
| | fact-check row marks the claim ❌, says "rounds", cites the GitHub file (llm) | 3/3 | 0/3 |
| | status `N open[, M facts unchecked]` (regex) | 3/3 | 0/3 |
| | no `Next step: to-tickets` while open (regex) | 3/3 | 3/3 |
| proposal-consistency (D2 tags `#ready`, D3 lists `#thought-through`) | sections in order (regex) | 3/3 | 0/3 |
| | `Status: reopened — consistency` (regex) | 3/3 | 0/3 |
| | contradiction named and left to the owner (llm) | 3/3 | 3/3 |
| | status open, no `Next step: to-tickets` (regex) | 3/3 | 0/3, 3/3 |
| proposal-decided (clean decisions, facts confirmed by the owner) | sections in order (regex) | 3/3 | 0/3 |
| | D1–D3 full text verbatim, no D4 (regex) | 3/3 | 0/3 |
| | status `decided` (regex) | 3/3 | 0/3 |
| | `Next step: to-tickets` line (regex) | 3/3 | 0/3 |

Scores: catch-error 1.00 (0.25), consistency 1.00 (0.33), decided 1.00 (0.00).

This is #9's "catches the D6 error" test: fed the same false claim in an unrelated project, the skill fetched Matt's `grilling` file, marked the claim ❌ ("asks in rounds"), reopened that decision and only that one, and kept the doc open.

Not exercised: commit, push and the REST PR calls (the eval sandbox can't grant Bash on this machine). The `Refs #N` PR lookup was checked live against this repo.

## to-tickets — 13 Oct 2026 (plugin 0.4.0, after the #17 review)

3 runs per case, no-plugin baseline. Regexes were self-tested against good and bad documents before use.

| Case | Check (grader type) | With | Without |
|---|---|---|---|
| tickets-devflow (a decided version of dev-flow's proposal) | ≥6 tickets with `Implements: D<n>` (regex) | 3/3 | 3/3 |
| | ≥6 `Blocked by:` (regex) | 3/3 | 3/3 |
| | covers ≥7 of the 8 pieces #5–#12 were (llm) | 3/3 | 3/3 |
| | breakdown shown for approval, nothing published (llm) | 3/3 | 2/3 |
| tickets-neutral (kacxx/notes-cli, D1–D3) | `Implements: D<n>` on the tickets (regex) | 3/3 | 0/3 |
| | vertical slices; every decision covered (llm) | 2/3 | 0/3 |
| | `Blocked by` uses T-numbers, never `#n` (regex) | 2/3 | 0/3 |
| | approval first, nothing published (llm) | 3/3 | 3/3 |
| tickets-undecided (Status `1 open`, D2 reopened by fact-check) | no ticket drafted in any format (regex) | 3/3 | 2/3 |
| | names the open D2 and declines (llm) | 3/3 | 0/3 |

Scores: devflow 1.00 (0.94), neutral 0.83 (0.17), undecided 1.00 (0.44).

The devflow case meets #10's "reproduces #5–#12" test but barely discriminates: the doc itself describes the `Implements:` header and the ticket set. The neutral case is the real test.

Found while testing:
- The first slice was horizontal ("ask the questions, save nothing yet"); the first ticket must now be the thinnest path through every layer.
- "Blocked by: #1" before publishing read as an existing issue; the breakdown uses T1, T2 ….
- dev-flow's own proposal status was hand-edited to `decided`, but D5 depends on an unchecked fact (the Windows install, #8). It now reads `decided, 1 fact unchecked`, so the devflow case uses a decided variant of the doc as its fixture.

The eval sandbox can't grant Bash here, so the publish step is checked live instead. **Live (kacxx/aside-jot#78, 2026-10-14):** issue creation, `ready-for-agent` on the unblocked tickets and the sub-issue links all worked; the label-exists and list-children calls were also checked against this repo. Not exercised: partial-publish recovery. Not built: adding `ready-for-agent` when a blocker closes. The skill only lists it in the report (see `docs/path-tuning.md`).

## flag-decision — 13 Oct 2026 (plugin 0.5.0, after the #18 review)

3 runs per case, no-plugin baseline. The prompts never name the skill, so these also test that its description triggers it. The label regexes were self-tested, and they reject negations such as "I won't add needs-decision" and "no needs-decision label is needed".

| Case | Check (grader type) | With | Without |
|---|---|---|---|
| flag-contradiction (ticket implements D3 "under the idea's heading"; `ideas.md` has no headings) | `## Decision flagged: D3` heading (regex) | 3/3 | 0/3 |
| | `needs-decision` actually applied (regex) | 3/3 | 0/3 |
| | no workaround implemented; options left to the owner (llm) | 3/3 | 0/3 |
| | evidence: quotes D3, states the finding, says why it blocks (llm) | 3/3 | 0/3 |
| flag-not-needed (file uses CRLF; decision unaffected) | no flag heading, no label applied (regex) | 3/3 | 3/3 |
| | carries on and handles CRLF itself (llm) | 3/3 | 3/3 |

Scores: flag-contradiction 1.00 (0.00), flag-not-needed 1.00 (1.00).

Without the plugin, every run quietly worked around the broken decision: the silent redesign D4 exists to stop. With it, every run stopped and flagged. The not-needed case shows the skill doesn't over-flag.

Not exercised: the `gh api` comment and label calls (the eval sandbox can't grant Bash here). The to-tickets "open flag" search was run live against this repo.

## proposal pilot fixes — 13 Oct 2026 (plugin 0.6.0, from the #11 pilot, after the #19 review)

New case `proposal-prose-decisions` (kacxx/notes-cli; WebFetch allowed). The owner answers in a prose comment without grill; one answer embeds a false claim ("Matt's grilling asks one question at a time"); one line is a constraint ("cap an interview at 10 questions"). Every proposal prompt now asks for the full doc and says plainly that public pages can be fetched but there's no `gh`/git access.

| Check (grader type) | With | Without |
|---|---|---|
| prose answers numbered `### D1:` … `### D3:` (regex) | 3/3 | 0/3 |
| the constraint becomes a `### D<n>: Constraint…` decision (regex) | 3/3 | 0/3 |
| status `N open[, M facts unchecked]` (regex) | 3/3 | 0/3 |
| the embedded false premise reopens its decision, options under its own heading (llm) | 3/3 | 0/3 |
| mapping shown for the owner to confirm, owner's wording kept (llm) | 2/3 | 0/3 |

Scores after the review: prose-decisions 0.94 (0.00), catch-error 0.96 (0.25), consistency 0.94 (0.33), decided 1.00 (0.00).

Found while re-testing:
- The prompts said "this session can't reach GitHub", and some runs took that literally and never fetched the file, so they left the false claim unchecked. The prompts now say what's actually true.
- Widening `## Open questions` to cover questions the fact-check raises made `decided` unreachable: runs blocked on implementation details (how `<idea>` matches a heading). The bar is now flag-decision's: an open question only if any answer would change what the owner agreed to; otherwise state the default in Shape.
- A regex-only case keeps no response text, so `proposal-decided` has a 0.01-weight LLM grader just to keep its output visible.

## status — 15 Oct 2026 (plugin 0.8.0, #41)

New case `status-next-action`: the prompt runs `/dev-flow:status kacxx/aside-jot#95` and holds `state.py`'s output for the `revision-in-progress-aside-jot-95` fixture, so no Bash or `gh` is needed. 3 runs, no-plugin baseline, judge sonnet. Regexes were self-tested against a good hand-off and three bad ones (steps swapped, an empty "Your decisions" part kept, a wrong next action).

| Check (grader type) | With | Without |
|---|---|---|
| next action: merge aside-jot#100, then the #97–#99 update (regex) | 3/3 | 3/3 |
| who: the owner merges, the agent updates the tickets and only offers to (llm) | 3/3 | 2/3 |
| shape: **Blocking now** holds #100, **Then** holds #97–#99, in that order (regex) | 3/3 | 0/3 |
| shape: empty parts left out (no **Your decisions**, no **Later**) (regex) | 3/3 | 0/3 |

Score: status-next-action 1.00 (0.48).

The baseline gets the next action right because the script's `steps` already carry it, with `who`. What the skill adds is the four-part shape.

Found while testing: asked in plain words ("Where's kacxx/aside-jot#95 at, and what's next?") with the state pasted, the skill didn't trigger in 3/3 runs, and the plugin arm scored the same as the baseline (0.57). With the script's output already in hand the model answers directly. The case uses the documented `/dev-flow:status owner/repo#N` form instead, so plain-words triggering is untested.

### Re-run on 0.10.0 — 15 Oct 2026 (after #48 and #50)

The pasted `<state>` was regenerated from `main`'s `state.py`. It now has `last_write`, `review_comments: []`, `fixes: []` and the doc PR's `created_at`. A new test in `skills/status/scripts/test_state.py` fails if the pasted state stops matching what the script prints for the fixture. Two graders were fixed: `shape-order` accepts a `pull/100` link, and `shape-empty-parts` only fails a numbered or bulleted **Your decisions** or **Later** item, not a passing mention. Both were self-tested on six good and bad answers.

| Check (grader type) | With | Without |
|---|---|---|
| next action (regex) | 3/3 | 3/3 |
| who (llm) | 3/3 | 3/3 |
| shape order (regex) | 3/3 | 0/3 |
| shape: empty parts left out (regex) | 3/3 | 0/3 |

Score: status-next-action 1.00 (0.57), Δ +0.43.

## status batch — 15 Oct 2026 (plugin 0.11.0, #39)

Three new cases, plus `status-next-action` re-run. 3 runs each, no-plugin baseline, judge sonnet. Each prompt pastes `state.py`'s output for a fixture; `test_state.py` fails if a pasted state drifts from what the script prints.

| Case | With | Without | What it checks |
|---|---|---|---|
| status-batch | 1.00 | 0.29 | the batch as a numbered list, every write named, the shorthand offered, and no "pick a ticket" step contradicting the relabel offer |
| status-batch-shorthand | 1.00 | 1.00 | "1, 3" carries out exactly items 1 and 3 |
| status-batch-draft | 1.00 | 1.00 | choosing a content-producing item ("update #97–#99") still shows its draft first |
| status-next-action | 0.90 | 0.48 | next action, who takes it, the four-part shape |

`status-batch-shorthand` and `status-batch-draft` state the rule in the prompt, so the baseline passes too: they're regression checks, not evidence that the skill adds anything.

Found on the first run, before these fixes (0.90, 0.83, 1.00, 0.90 with the plugin):
- `state.py` gave the owner "pick the next ticket: none of #38–#41 is ready-for-agent" while the batch offered the labels that would make them ready, so answers contradicted themselves. With relabel fixes pending and no ticket ready, there's now no owner step; the next action is the relabelling.
- `shape-order` still expected #97–#99 under **Then**; the batch now puts them under **Your decisions**, so it accepts either.
- The `only-chosen` and `who` judges failed correct answers: one for adding a remark that wrote nothing, one for reading "which of these should I do?" as handing the work to the owner. Both graders now say what counts.
- Answers said they would run `to-tickets` to update #97–#99, which `to-tickets` won't do for an issue that already has tickets (#46). The skill now says to draft those edits directly and show them.

The remaining `status-next-action` failure (1 of 3) is fair: that run said it couldn't reach GitHub and would hand the owner the drafted edits to apply, giving the write to the owner.

### proposal-decided: review step — 16 Oct 2026 (0.12.1, PR #60)

New regex grader `review-step`: the hand-off asks for a fresh code review of the doc PR (such as `/code-review`) before the owner's yes. Run with 3 runs and a no-plugin baseline: with the plugin, every other grader passed and all 3 answers named the review before the yes; the baseline named it 0/3. (The first version of the grader used `(?i)`, which the eval's JavaScript regex rejects; the fixed pattern was checked against the 6 recorded answers.) Score: proposal-decided 1.00 (0.00).

## settle: facts and constraints — 22 Oct 2026 (0.16.0, #90)

Two new cases, both with Matt Pocock's public `grilling` SKILL.md pinned at 49dd158 as the fixture (fetched with WebFetch, run with `--allow-tools WebFetch`). Final run on the committed skill text (167 lines, 2,341 words) and graders: all five settle cases, 3 runs each, no-plugin baseline, judge sonnet. `settle-first-round` was re-run after its `recommendations` grader was fixed (below).

| Case | With | Without | What it checks |
|---|---|---|---|
| settle-check-facts | 1.00 | 0.80 | the issue's wrong claim ("grilling asks the user for any fact it needs") is corrected, the recommendation isn't built on it, and the round has its shape |
| settle-constraints | 0.92 | 0.67 | the 15-line constraint rules out embedding the 30-line file as it is: the recommendation fits, and the round says so |
| settle-first-round | 1.00 | 0.40 | |
| settle-record | 0.80 | 0.20 | |
| settle-shorthand | 1.00 | 0.50 | |

**The facts rule shows no measurable gain on Opus 5.5, because the model already checks.** In `settle-check-facts` the baseline corrected the claim and didn't build on it in every run of this final run. Across the five runs of this case on the way here, the facts graders alone (`claim-corrected`, `not-built-on-claim`) gave the plugin +0.27, 0, 0, −0.13 and 0. The plugin's steady lead is the round format (`one-round`). The case also allows no sub-agent, so the rule's sub-agent lookup never runs, and nothing tests that only the questions resting on a running lookup wait. A harder test is #94.

`settle-constraints`: the recommendation fitted the constraint in every run with and without the plugin. The plugin adds the round's shape and, more often, saying that the file as it is would break the constraint. One plugin miss was the closing "Answer yes" line.

Grader fixes in `settle-first-round`, which also failed on `main` (0.15.0) on the same day (0.40, 0/3):
- `all-four-in-one-message` expected `Q1 -` with a hyphen; runs write `–`, `—` or `**Q1** -`. It now accepts those, as `settle-check-facts`' `one-round` does.
- `no-premature-record` was an LLM judge that failed clean rounds. It's now a regex that fails on `## Decisions`, `### D<n>:` or `**D<n>:` at a line start (indented or `>`-quoted too), anywhere in the response. Self-tested on eight texts and the 6 recorded rounds from `main` and this branch.
- `recommendations` failed a round that asked for constraints with no recommended answer, which the skill now requires (#90 D13). A constraints question is now exempt.

Not graded: one `settle-first-round` run skipped the MVP check (from 0.14, not this change).

`settle-record` is flaky on both sides (6 runs each earlier the same day: `main` 0.63, branch 0.80): records reword an accepted recommendation, which the `decisions-in-order` phrases catch, plus the `done` judge (#94).

## slice: cold read — 23 Oct 2026 (0.17.0, #98)

New case `slice-cold-read` (#96 D14): a decided short-path issue, an approved breakdown, and seven cold-reader findings given in the prompt (two the owner has to decide, a size limit and a log format a developer would pick, a team that hasn't shipped a field yet, and so on). It grades the sort into the three groups (regex on the `**real gap:**`, `**default:**` and `**known blocker:**` labels), a `## Defaults` section with a value (regex), and that nothing is published (judge). Written and run on `main` before the skill changed. 3 runs per case, no-plugin baseline, judge sonnet.

| Case | `main` (0.16.0) | This branch | Without |
|---|---|---|---|
| slice-cold-read | 0.20 | 1.00 | 0.13 |
| slice-neutral | 1.00 (6 runs) | 0.83 | 0.06 |
| slice-devflow | 0.78 | 0.78 | 0.94 |
| slice-undecided | not re-run | 1.00 | 0.00 |

`main` columns are the plugin arm only, on the same prompts and graders as the branch.

**Fixes to the case while writing it:**
- The prompt first ended "Carry on from there". Every run, with and without the plugin, sent the seven findings to `settle` as questions, so `slice` never ran. It now ends "Carry on slicing from there, with the `slice` skill"; the `main` column is from after that fix.
- `three-groups` first accepted only `**real gap:**`. Runs with a correct sort wrote `**real gap: T1**` and `**Real gap: T1**`; it now accepts the ticket inside the bold and a capital first letter, and still fails on group headings alone (`**Real gaps**`). Self-tested on five texts (#94).

**Skill fixes the runs found:**
- Step 4's first wording ("nothing before the cold read either") let a `slice-neutral` run go on into the cold read without approval. Step 4 now stops until the owner approves.
- A run with open real gaps showed the sort but no ticket bodies, and another grouped findings under headings without labelling each line. Step 5 now says to show the bodies while gaps are open, and to label every line.
- With the new step, `slice-neutral` runs turned the doc's undecided risk (a duplicate heading) into a ticket that implements no decision, failing `implements-headers` (branch 0.61–0.89 across five batches). Step 3 now says every ticket implements a decision, and undecided work is raised as a question.

**Still open:** `slice-neutral` is below `main`. Its misses draft one ticket for D1–D3, which the two-ticket regexes (`implements-headers`, `t-numbering`) fail; whether one ticket is wrong here is a grader question as much as a skill one. `slice-devflow`'s `coverage` judge fails on `main` too (1 of 3 passes there).

**Fix round (PR #100 review):** the reader's prompt now says "Read only: don't build, edit or post anything", and step 5 was cut to its rules (SKILL.md 2,494 → 2,192 words). Then 3 more runs:

| Case | Runs | Scores | With | Without |
|---|---|---|---|---|
| slice-neutral | 3 more, on the shorter text | 0.67, 0.50, 0.50 | 0.56 | 0.11 |
| slice-neutral | all 6 (3 above + 3 in the table) | | 0.69 | 0.08 |
| slice-cold-read | 3, plugin arm only | 1.00 ×3 | 1.00 | not run |

Two of the three new `slice-neutral` runs drafted one ticket for D1–D3; the third drafted two and failed the `vertical` judge. The 6 runs span two versions of step 5's text. Graders unchanged.

**Not graded:** sending the reader. The eval can't run a sub-agent (every case allows only `Skill`), so whether the reader gets only the bodies, decisions and code is checked by hand on the first live run (#96 D14). Which group a finding lands in isn't graded either: across the kept runs, the staging-data finding was sorted as a real gap, a default and a known blocker.

**Bisect (PR #100 review, round 2).** Graders unchanged throughout.

| Variant | slice-neutral (with) | slice-cold-read (with) |
|---|---|---|
| `main` (0.16.0) | 1.00 (6 runs) | 0.20 |
| Fix round, step 5 inline (`f94950a`; the PR's content after the revert) | 0.69 (6 runs) | 1.00 |
| Same, step 3's "every ticket implements a decision" sentence reverted | 0.78 (1.00, 0.67, 0.67) | not run |
| Step 5's detail moved to `skills/slice/cold-read.md` (`bfef873`, reverted) | 0.83 (1.00, 1.00, 0.50) | 0.20, not measurable |

- Reverting the step 3 sentence didn't bring `slice-neutral` back: all three runs again made a ticket for the doc's undecided duplicate-heading risk, two of them with no D-number on its `Implements:` line.
- With step 5 in its own file, the one `slice-neutral` miss drafted a single ticket for D1–D3. `slice-cold-read` couldn't measure it: each run tried to read `cold-read.md` and the eval's "don't ask" mode denied Read (and Grep), so it sorted without the labels. The split was reverted so the case can measure step 5.

**Known issue, accepted for now:** `slice-neutral` is below `main` in every variant tried (0.69–0.83 against 1.00). The misses are a single ticket for D1–D3, or a ticket for the undecided risk. Followed up in its own issue.

## slice: known blockers — 24 Oct 2026 (0.17.1, #99)

Step 5's interim known-blocker rule is replaced: each known blocker gets a proposed tracking issue with the sort, or the link the owner gives (#96 D6, D11). No new case (#99 Defaults). 3 runs per case, no-plugin baseline, judge sonnet.

| Case | Scores (with) | With | Without |
|---|---|---|---|
| slice-neutral | 0.50, 1.00, 1.00 | 0.83 | 0.00 |
| slice-cold-read | 0.60, 0.60, 1.00 | 0.73 | 0.20 |
| slice-cold-read, 3 more (plugin arm only) | 1.00 ×3 | 1.00 | not run |
| slice-cold-read on `main` (0.17.0), same day (plugin arm only) | 1.00, 1.00, 0.20 | 0.73 | not run |

- `slice-neutral` stays above `main`'s 0.69 (#101). The one miss drafted a single ticket for D1–D3, as before.
- `slice-cold-read`'s two misses in the first batch grouped the findings under headings without labelling each line (`three-groups`). `main` missed the same way on the same day, and the next three branch runs all passed, so it reads as variance rather than this change.
- Every branch run proposed a tracking issue for the catalog team's `category` field, naming the team as its owner. Creating it, searching for a duplicate title and writing a full link aren't graded (the eval can't reach GitHub); they're checked by hand on the first live run.

**Fix round (pre-push review):** the tracking issue's body names only the source issue, and the ticket's `Blocked by:` links back through GitHub's cross-reference, with no edit after publishing. The skill's additions cut from +268 to +146 words (SKILL.md 2,338). Graders unchanged. 3 runs per case, no-plugin baseline:

| Case | Scores (with) | With | Without |
|---|---|---|---|
| slice-neutral | 1.00, 0.50, 0.67 | 0.72 | 0.06 |
| slice-cold-read | 1.00, 0.60, 1.00 | 0.87 | 0.20 |

- `slice-neutral` is still at or above `main`'s 0.69 (#101). One miss drafted a single ticket for D1–D3; the other failed the `vertical` judge.
- `slice-cold-read`'s miss bolded the whole finding (`**Known blocker: T1 — staging has …**`), which `three-groups` doesn't accept. All three runs proposed a tracking issue for the catalog team's field, naming the owner.
- Seen but not graded: the drafted bodies shown with the sort kept `Blocked by: None` for the ticket with a known blocker, since its tracking issue has no number yet. Whether the published ticket names it is checked on the first live run.

**Fix round (PR #103 review), 26 Oct 2026:** a proposed tracking issue is drafted as `B<n>` on the ticket's `Blocked by:`, and step 6 replaces `T<n>` and `B<n>` with their numbers, recording `B<n> → #<number>` in the mapping and the failure report. An existing tracking issue is found by its body (`Blocks a ticket under #N.`), open or closed; a closed one is resolved, and reused rather than created again. External blockers keep their links whole, but never put `#` right before a digit (`AB 1234`). The sort template shows `Track: <title> (<owner>)`, and the Later line and label comment use the reviewer's wording. SKILL.md 2,384 words. Graders unchanged. 3 runs per case, no-plugin baseline:

| Case | Scores (with) | With | Without |
|---|---|---|---|
| slice-neutral | 0.67, 0.50, 0.67 | 0.61 | 0.17 |
| slice-cold-read | 1.00 ×3 | 1.00 | 0.20 |
| slice-neutral on `main` (0.17.0), same day (plugin arm only) | 0.67 ×3 | 0.67 | not run |

- `slice-neutral` is below the 0.69 recorded for `main` in #101, but `main` scored 0.67 on the same day, and every miss is #101's pattern: two runs made a ticket for the doc's undecided risk (the duplicate heading) and failed `vertical`; one drafted a single ticket for D1–D3. This round changes steps 5–7, not step 3.
- `slice-cold-read`: every run drafted `Blocked by: B1` with a `Track:` line naming the catalog team.
- Not graded (the eval stops before publishing): replacing `B<n>`, the tracking-issue lookup, and reusing a closed one. The lookup command was run against kacxx/dev-flow: it parses and lists open and closed issues.

## slice: existing children — 26 Oct 2026 (0.18.0, #102)

Before the cold read, slice lists the source's open children (sub-issues and `Parent: #N` issues) and sorts each one the plan doesn't account for as an `existing child:` line: keep, move out or close. On `Path: ready` the lines go with the breakdown in step 4; step 6 closes or moves out each one as confirmed. The reader's input is unchanged (D3). SKILL.md 2,384 → 2,504 words (+120, D9). No new case, and graders unchanged. Neither slice case has existing children (the eval can't reach GitHub), so the new group isn't graded. Judge sonnet, all runs the same day.

| Case | Runs | Scores (with) | With | Without |
|---|---|---|---|---|
| slice-neutral | 3, no-plugin baseline | 0.67, 0.67, 0.50 | 0.61 | 0.17 |
| slice-neutral | 3 more, plugin arm only | 0.50, 0.67, 0.67 | 0.61 | not run |
| slice-neutral | all 6 | | 0.61 | |
| slice-cold-read | 3, no-plugin baseline | 1.00 ×3 | 1.00 | 0.13 |
| slice-neutral on `main` (0.17.1) | 3, plugin arm only | 0.67, 1.00, 1.00 | 0.89 | not run |
| slice-neutral on `main` (0.17.1) | 3 more, plugin arm only | 0.50, 0.67, 0.67 | 0.61 | not run |
| slice-neutral on `main` (0.17.1) | all 6 | | 0.75 | |

- **D10 not met on these runs:** `slice-neutral` is 0.61 over 6 runs, below `main`'s 0.69 in #101 and below `main`'s 0.75 the same day. Every miss on both sides is #101's pattern: a ticket for the doc's undecided duplicate-heading risk (`vertical`), or a single ticket for D1–D3 (`implements-headers`, `t-numbering`). No branch run mentioned existing children; each stopped at step 4. The second batches ran in parallel and scored the same on both (0.61), so the gap is the first batch, where `main` had two clean runs.
- `slice-cold-read` is unchanged at 1.00.
- Not graded (the eval stops before publishing and can't reach GitHub): listing the children, the `existing child:` lines, and closing or moving out in step 6. The two listing commands were run against kacxx/dev-flow #96 and #98: the sub-issue listing shows each child's state, and the `Parent: #N` filter parses.

**Fix round (PR #105 review), 26 Oct 2026:**
- **Listing and step 6 commands:** step 6's listing prints each child's `id`. Step 6 gives full commands for closing as not planned and for unlinking (only a child that's a sub-issue). Removing a `Parent: #N` line fetches the body and PATCHes it back with only that line gone, and doesn't PATCH if the fetch fails.
- **Step 4:** on `Path: ready`, step 4 now lists existing children and shows their lines with the breakdown, and step 5's skip sentence is back to its original wording.
- **Stop rule:** rounds stop when they raise only defaults, blockers and existing children already sorted.
- **Hand-off:** it lists the children closed or moved out.

#102's D9 was revised to about 2,580 words, and D10 to "within `main`'s same-day range over 6+ runs" (#101's latest comment). SKILL.md is 2,580 words. Graders unchanged. Branch and `main` ran 6 runs each in parallel, plugin arm only:

| Case | Scores (with) | With |
|---|---|---|
| slice-neutral (0.18.0) | 1.00, 1.00, 0.50, 0.67, 0.67, 0.67 | 0.75 |
| slice-neutral on `main` (0.17.1), same time | 0.50, 1.00, 0.67, 1.00, 0.67, 0.67 | 0.75 |

- **D10 (revised) is met:** the branch's 0.75 is level with `main`'s 0.75 in the same batch. It is also inside `main`'s range across today's batches: 0.61–0.89 per 3-run batch, and 0.75 for both of its 6-run sets. The first round's 0.61 (6 runs) is also inside that range.
- **The misses:** they are #101's pattern on both sides: a ticket for the undecided risk (`vertical`), or one ticket for D1–D3 (`implements-headers`, `t-numbering`). No branch run mentioned existing children.
- **Checked outside the eval:** the new `Parent: #N` filter was run with jq on a body that has CRLF line endings and trailing spaces. It removes only the exact `Parent: #4` lines and keeps `Parent: #40`. The listing with `id` was run against kacxx/dev-flow #96.
- **Not graded:** none of the step 6 writes have been tried on GitHub yet.
