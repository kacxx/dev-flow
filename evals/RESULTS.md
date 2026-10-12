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

## grill — 12 Oct 2026 (plugin 0.2.0)

3 runs per case, Sonnet judge, no-plugin baseline. `regex` graders for mechanical checks, `llm` for judgement.

| Case | Check | With | Without |
|---|---|---|---|
| grill-first-round (aside-jot#78, 4 questions) | every listed question asked in one round, or held back with a reason | 3/3 † | 0/3 |
| | "answer yes to accept all / shorthand" line (regex) | 3/3 | 0/3 |
| | a recommendation for every question | 3/3 | 0/3 |
| | no decisions recorded before answers | 3/3 | 3/3 |
| grill-record (dev-flow#1, all "yes") | D1–D6 recorded as settled facts | 2/3 | 2/3 |
| | `## Decisions (grill, YYYY-MM-DD)` header (regex) | 3/3 | 0/3 |
| | `**D6:` present (regex) | 3/3 | 3/3 |
| | stops (no new round) | 2/3 | 3/3 |
| grill-shorthand (aside-jot#78, "1 yes, 2 no: X, 3 skip, 4 yes") | accepted, alternative and skipped answers recorded correctly | 3/3 | 3/3 |
| | IDs: no reuse, skipped question has no ID and is listed open | 3/3 | 0/3 |
| both record cases | **fidelity**: no added reasons or details in decisions | 0/3 | 0/3 |

† After the "never drop a question silently" rule; before it, the command-name question vanished in 3/3 runs. With the rule, one run held it back with a reason ("holding until Q2 is settled, which changes which name fits"); two asked it.

Known: the `fidelity` LLM grader fails both arms every time, while the outputs read as faithful on manual inspection. The grader is likely too strict, but that's unconfirmed. LLM judges also swung from 3/3 to 0/3 on similar outputs between runs, so mechanical checks are regex wherever possible.
