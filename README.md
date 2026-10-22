# dev-flow

Lightweight Claude Code skills for getting from an **idea** to **tickets an agent can implement**, with every design decision written down and linked to the tickets that build it.

It covers the part before the code: deciding what to build. Implementing the tickets is left to whatever you already use (Superpowers, Matt Pocock's skills, plain Claude Code). dev-flow comes back in only if the implementation shows a decision was wrong.

## The flow

Every idea starts with `capture`, which picks one of three paths:

| Path | When `capture` picks it | Steps |
|---|---|---|
| **ready** | no open questions, no design needed | `capture` → implement (the issue is the ticket) |
| **short** | a few questions to settle, no design doc | `capture` → `settle` → implement, or → `slice` if it needs several tickets |
| **full** | a new interface, a cross-cutting change, or more than about three tickets | `capture` → `settle` → `proposal` → `slice` → implement |

On any path, if implementing a ticket shows a decision is wrong: `flag-decision` → `settle` on that decision → the affected tickets are updated.

What each skill does:

1. **`capture`** turns the idea into one GitHub issue (Problem, Idea, Open questions), looks up the facts itself, and picks the path. The path is recorded in the issue, so later sessions know it.
2. **`settle`** works through the open questions with you in rounds. Each round asks every question that can be asked now, each with a recommended answer, so "yes" accepts them all. Before asking a question, it looks up the facts the question depends on, including claims in a pasted document, and checks each recommendation against your constraints (how much work, a performance budget, what mustn't break). Each answer becomes a numbered decision, `### D1: …`. On the short and full paths, the first round opens with an MVP check: the smallest version that answers the problem, whether it can be tried today without building anything, and what would justify going bigger. If it can be tried today, `settle` stops there, parks the issue and hands off "try it first".
3. **`proposal`** (full path only) writes the decisions up as `docs/proposals/<name>.md` and **fact-checks every claim** in it against the code, the docs or a live probe. A wrong claim reopens the decision it supports, and the doc can't merge until its status is exactly `decided`. `proposal` checks the facts; a fresh code review of the doc PR (such as `/code-review`) checks the design, and asks whether a smaller version would do. Run that review before saying yes, and answer its findings with `settle` or as wording fixes.
4. **`slice`** slices a decided doc, or a short-path issue that needs more than one ticket, into vertical, tracer-bullet tickets. Each ticket names the decisions it implements and the tickets that block it. Nothing is published until you approve the breakdown.
5. **`flag-decision`** is for the agent implementing a ticket. If the work shows a decision is wrong, impossible or contradicted by the code, it stops, posts the evidence, labels the ticket `needs-decision`, and hands the decision back to `settle`, so nothing gets quietly redesigned inside a ticket.
6. **`status`** tells you where an idea is and what's next, at any point. Given the source issue, a bundled script reads its state on GitHub (the issue, its comments, the doc PRs, the proposal doc and the tickets). `status` then names the stage and the next action, and says who takes it. It lists any review comments since dev-flow last wrote on the issue. It also offers mechanical fixes for your yes, such as adding `ready-for-agent` to a ticket whose blockers have all closed.

Every step that writes to GitHub shows you the draft first and waits for your yes.

## Running the skills

Each skill takes plain text: name the repo and the issue, doc or idea it should work on. Run it as a slash command, `/dev-flow:<skill> <what to work on>`, or just ask ("settle owner/repo#12"); the descriptions are written so Claude picks the right skill.

| Skill | Give it | Example |
|---|---|---|
| `capture` | the repo and the idea, in a sentence or two | `/dev-flow:capture owner/repo: let users export their data as CSV` |
| `settle` | the issue (or doc) with the open questions | `/dev-flow:settle owner/repo#12` |
| `settle` (reopen) | the decision and where it lives | `/dev-flow:settle D3 in docs/proposals/csv-export.md` |
| `proposal` | the source issue, or the doc PR to review | `/dev-flow:proposal owner/repo#12` |
| `slice` | the repo and the decided doc, or a short-path issue | `/dev-flow:slice owner/repo docs/proposals/csv-export.md` |
| `status` | the source issue | `/dev-flow:status owner/repo#12` |
| `flag-decision` | usually nothing: the agent implementing a ticket runs it, prompted by the `CLAUDE.md` pointer (see Install) | `/dev-flow:flag-decision owner/repo#15: D2 says exports stream from the database, but the ORM loads the whole table` |

What you answer back:
- **`capture`** shows the draft and the path it picked. Reply "yes" to post it, or "ready", "short" or "full" to change the path.
- **`settle`** asks a round of numbered questions, each with a recommendation. Reply "yes" to accept them all, or per question, for example `1 yes, 2 no: use labels, 3 skip`. "Skip" leaves that question open. It then shows the decisions record and writes it after your yes.
- **`proposal`** pushes the doc to a draft PR, then shows you the status, what changed and the full fact-check table. Reply "yes" when you're happy; it marks the PR ready only once the status is `decided`. Run a fresh code review of the doc PR (such as `/code-review`) before you reply "yes".
- **`slice`** shows the breakdown as T1, T2 …, with what each implements and what blocks it. Ask for merges or splits, or reply "yes" to publish.
- **`status`** gives the stage, then what's next. If it offers fixes, reply "yes" or name the ones you want. It writes only the fixes you pick, and runs the agent's next step only if you say yes.
- **`flag-decision`** stops on its own. Your part is the next step it names: `settle` on that decision.

## What the artefacts look like

**Decisions** are headings with IDs that never change once given: `### D3: Codex jots get "can't tell" in v1`. When one is revised, it keeps its ID, and the old text moves into a `<details>` "Superseded" block with the reason.

**Tickets** start with three lines that link them back:

```markdown
Implements: D2, D4 — docs/proposals/jot-status-check.md
Blocked by: #82
Parent: #78
```

**Labels:** `ready-for-agent` means an agent can start the ticket now. `needs-decision` means `flag-decision` has put it on hold until `settle` revises the decision.

**A proposal's status** is exactly one of `decided`, `decided, M facts unchecked`, `N open` or `N open, M facts unchecked`. Only `decided` can merge or be sliced.

## Example

kacxx/aside-jot#78, "is a jot done yet?", went the full path:
1. The proposal (aside-jot#79) recorded D1–D5. Its fact-check found that D3 rested on a false premise (Codex jots *do* have a transcript), and `grill` (now `settle`) settled D3 again.
2. `slice` sliced it into five tickets (aside-jot#82–#86).
3. All five PRs were open about 70 minutes after the tickets were published.

The timings are in [`docs/path-tuning.md`](docs/path-tuning.md#outcomes). dev-flow itself was designed the same way, by hand, in [#1](https://github.com/kacxx/dev-flow/issues/1); its decisions are in [`docs/proposals/idea-to-tickets.md`](docs/proposals/idea-to-tickets.md).

## Install

**Mac and Windows (Claude Code plugin):**

```bash
claude plugin marketplace add kacxx/dev-flow
```

```bash
claude plugin install dev-flow@dev-flow
```

To update after a new version (the version is in `.claude-plugin/plugin.json`), run `claude plugin marketplace update dev-flow`, then `claude plugin update dev-flow@dev-flow`, and restart Claude Code.

**In each project that uses it:** add the one-line pointer from [`skills/flag-decision/SKILL.md`](skills/flag-decision/SKILL.md#the-claudemd-pointer) to the project's `CLAUDE.md` (or the `AGENTS.md` it imports). It makes an implementing agent stop and flag a wrong decision instead of redesigning around it, even an agent without the plugin. `slice` checks for the line and offers it if it's missing.

Claude Code cloud sessions start on a fresh `claude/…` branch, and the local `main` can be behind. Bring the branch you need up to date first: `git fetch origin && git checkout BRANCH && git merge --ff-only origin/BRANCH`.

The skills use `gh api` (REST) everywhere, because `gh issue` and `gh pr` go through GraphQL, which fails in cloud sessions. Where cloud sessions block GitHub search, each skill falls back to listing issues and filtering them.

## Status

Beta. All six skills are built. `capture`, `settle`, `proposal`, `slice` and `flag-decision` have been run for real: on dev-flow itself, on aside-jot, natively on Windows, and from the phone. `status` has so far been run only on this Mac, on dev-flow#35 and aside-jot#95. Not tried live yet: `flag-decision` in a real implementation run, and WSL. Known gaps in `status`: it finds open code PRs for its tickets by hand, not in its script ([#51](https://github.com/kacxx/dev-flow/issues/51), D5), and it may not start when asked in plain words ([#52](https://github.com/kacxx/dev-flow/issues/52)). Nothing yet updates open tickets after a revision merges ([#46](https://github.com/kacxx/dev-flow/issues/46)), or closes the source issue when its tickets are done ([#47](https://github.com/kacxx/dev-flow/issues/47)).

## Developing

- **Layout:**
  - `skills/<name>/SKILL.md`, one folder per skill;
  - `evals/<case>/` for the `claude plugin eval` cases, with scores in [`evals/RESULTS.md`](evals/RESULTS.md);
  - `scripts/` for the ZIP builder and the test runner;
  - `docs/` for the proposal and the path-tuning log.
- **Tests:** `python3 -I scripts/run_tests.py` (`python` on Windows) runs every `test_*.py`. That includes a frontmatter check on every skill, and the jq filters in the skills' search fallbacks, run as written. CI runs the same command on every PR and on pushes to `main`, on Ubuntu and Windows, with and without PyYAML.
- **Releases:** bump `version` in `.claude-plugin/plugin.json` on every change, because installed plugins only update when it changes.
- **After each real run:** add a row to [`docs/path-tuning.md`](docs/path-tuning.md), and turn what was clumsy into an issue (`capture` works for that too).

## Credits

`settle` and `slice` are adapted from [Matt Pocock's skills](https://github.com/mattpocock/skills) (MIT); see [`NOTICE`](NOTICE). dev-flow is MIT licensed ([`LICENSE`](LICENSE)).
