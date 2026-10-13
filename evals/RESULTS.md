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

Not exercised: the publish step (`gh api` issue creation, labels, sub-issue link, partial-publish recovery); the eval sandbox can't grant Bash here. The label-exists and list-children calls were checked live against this repo.

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
