# Idea → tickets flow (#1): proposal

Status: **decided**. Ready to merge, then slice into tickets.

## Problem

Ideas get from "I want X" to "here are the tickets" ad hoc. `kacxx/aside-jot#78` / `kacxx/aside-jot#79` is the example. Its open questions were answered in an issue comment that never reached the doc, nobody checked the doc's claims against the code, and the doc PR was reviewed with `/code-review`, which looks for code bugs.

## Decisions

### D1: Ticket target
GitHub issues only for v1. Tickets are described in neutral fields (title, problem, acceptance criteria, which decision it implements, what blocks it), so a Jira writer can be added later without a redesign.

### D2: Short path
`capture` decides the path and says why; the owner can override in one word.
- **No open questions:** the issue becomes the ticket (acceptance criteria added, labelled `ready-for-agent`, the same label `to-tickets` uses).
- **Open questions answerable in one sitting:** grill them in the issue and write the decisions into the issue body. No proposal doc.
- **Needs design** (a new interface or command, a cross-cutting change, or more than about three tickets): the full path, ending in a proposal doc.

The three-ticket cut-off gets tuned after the pilots.

### D3: Linking
Decisions get stable IDs (`D1`, `D2`, …): headings in the proposal doc or, on the short path, in the issue body. Every ticket opens with:
```
Implements: D2, D4 — docs/proposals/<name>.md
Blocked by: #12
```
On the short path there's no doc, so the header points at the issue holding the decisions: `Implements: D2 — #<issue>`. An agent can check the header with one search, and IDs don't change when the doc is edited.

### D4: Way back
1. The implementing agent stops and flags. It comments with the evidence and the decision it breaks, and labels the ticket `needs-decision`. It doesn't redesign inside the ticket.
2. The decision gets `Status: reopened — #<ticket>`, is grilled on its own, and is revised under the same ID with the old text kept as superseded.
3. Open tickets that say `Implements: D<n>` are re-sliced, and the owner approves the list.

The procedure lives in the plugin as a short **`flag-decision`** skill: comment with the evidence, add the `needs-decision` label, stop. Each project's `CLAUDE.md` gets a one-line pointer that triggers it ("if a ticket conflicts with a decision, run flag-decision; don't redesign"). The procedure exists once; only the trigger is per project. *(Added 12 Oct: PR #3 found that D4 didn't say where the rule lives.)*

### D5: Devices (revised again 12 Oct, after the phone probe)
- **Source:** this repo. Skills are written and versioned here.
- **Mac and Windows:** the Claude Code plugin while the skills are still changing. Mac first; Windows confirmed with one install.
- **Phone (Claude Code cloud sessions, from the Code tab):** once the skills have settled after the pilots, `capture`, `grill` and `flag-decision` are uploaded as **claude.ai account skills**. `flag-decision` is included because flow 2 also runs from the phone, and an agent implementing a ticket there has no plugin. The probe confirmed that cloud sessions load account skills. Account skills also sync into terminal Claude Code, so they reach every project (aside-jot, shipledger, …) without copying anything into each repo.
- **Not used:** copying the skills into each project's `.claude/skills/`. It works (the probe loaded one live from the branch), but every repo's copy would drift.
- **The Android chat app:** out of v1.

<details><summary>Superseded (12 Oct, first revision): "cloud sessions don't load plugins, so account skills"</summary>

The first revision rested on the docs. The phone probe found cloud sessions load account-synced plugins as well as account skills and repo-committed skills. The route (account skills for the phone) holds; the reasoning is now based on evidence.
</details>

<details><summary>Superseded (12 Oct, original): "claude.ai account skills for the Android app"</summary>

The original D5 put `capture` and `grill` in the Android chat app. The docs don't say the chat app loads account skills, while cloud sessions (Code tab) do.
</details>

### D6: Starting point (revised 12 Oct, after the fact-check reopened it)
Adapt Matt Pocock's skills (MIT, with the notice in `NOTICE`):
- **`grill`:** his `grilling` **frontier rounds**, used as they are. (His `grill-me` is a one-line wrapper that calls `grilling`, so there's nothing in it to adapt.) Each round asks every question whose prerequisites are already settled, numbered, each with a recommended answer and worded so "yes" accepts it. The agent looks up facts with sub-agents and never asks the user for them. Additions: shorthand answers for a whole round ("1 yes, 2 no: X, 3 skip"), since a round of six is long to answer on a phone; each answer is recorded under a `D<n>` ID (D3); and the session ends by writing a decisions record, since the manual run showed nothing else captures them.
- **`to-tickets`:** from his `to-tickets`. Cut the domain-glossary, ADR and `/setup-matt-pocock-skills` tracker references, and target GitHub issues directly (D1). It already has `Blocked by:` and `ready-for-agent`; add only the `Implements:` line (D3). *(Corrected 12 Oct per PR #3: the parts to cut are in `to-tickets`, not `grilling`.)*
- **`capture` and `proposal`:** new.

<details><summary>Superseded (12 Oct): "the one-question-at-a-time core"</summary>

The original D6 described Matt's grilling as asking one question at a time. The fact-check found it works in frontier rounds. Our manual run asked six independent questions in six turns where one round would have done.
</details>

## Shape

```
dev-flow/
  .claude-plugin/marketplace.json   # name, owner, plugins: [{ name: dev-flow, source: ./ }]
  .claude-plugin/plugin.json        # name, version, skills: [...]
  skills/capture/SKILL.md           # idea → issue, picks the path (D2)
  skills/grill/SKILL.md             # rounds, D<n> IDs, decisions record (D3, D6)
  skills/proposal/SKILL.md          # decided doc + fact-check of its claims
  skills/to-tickets/SKILL.md        # vertical slices, Implements:/Blocked by: header (D1, D3)
  skills/flag-decision/SKILL.md     # flow 2's way back: evidence comment, needs-decision label, stop (D4)
  NOTICE                            # Matt Pocock's MIT notice for the adapted skills
```

- **GitHub access:** the skills read and write issues with `gh api repos/{owner}/{repo}/issues…`, not `gh issue`/`gh pr`. That works both locally and in cloud sessions, where GraphQL is blocked.
- **Updates:** bump `version` in `plugin.json` on each change. Installed plugins only update when the version changes.
- **Tests:** each skill must reproduce issue #1's **outcomes**, not its turn count. `capture` produces #1's shape and path choice on comparable ideas, and, now that #1 exists, finds #1 and offers to continue it when given #1's idea again; `grill` reaches D1–D6 from #1's six open questions (in one or two rounds, where the manual run took six turns); `proposal` produces this doc's sections and catches the D6 error; `to-tickets` produces this ticket set. `flag-decision` has nothing in #1 to reproduce, so it gets its own scenario: a ticket whose work contradicts D3 → an evidence comment, the `needs-decision` label, and a stop with no redesign.

## Fact-check

| Claim | Result | Source |
|---|---|---|
| A private repo can be a plugin marketplace (`/plugin marketplace add kacxx/dev-flow`) | ✅ Uses the existing git credentials (`gh auth setup-git` or SSH); `GITHUB_TOKEN` alone doesn't cover background updates | code.claude.com/docs/en/plugins/host-marketplace |
| Plugin = `marketplace.json` + `plugin.json` + `skills/<name>/SKILL.md` | ✅ Matches Matt's repo (`source: "./"`, explicit `skills` list) | create-marketplace docs; mattpocock/skills `.claude-plugin/` |
| The same plugin works on Windows | ⚠️ Native and WSL are both supported, but the docs don't say install is identical. WSL is a separate home directory, so a separate install | code.claude.com/docs/en/setup |
| Cloud sessions load repo-committed skills | ✅ **Probe:** `dev-flow-probe` loaded live from the checked-out branch, after a short delay, no restart | Phone probe, PR #3 comment |
| Cloud sessions load claude.ai account skills | ✅ **Probe:** 15 account skills synced to `~/.claude/skills/synced/` | Phone probe |
| Cloud sessions load plugins | ⚠️ **Probe:** account-synced plugins load (`~/.claude/plugins/synced/`: engineering, design, …). The docs say machine-installed marketplace plugins don't. Not tested: adding a personal GitHub-marketplace plugin to the account | Phone probe; cloud-environments "what carries over" |
| Cloud sessions can write to a private repo | ✅ **Probe:** posted a comment on #1 and pushed a branch. The docs say `gh issue`/`gh pr` fail (GraphQL blocked), so the skills use `gh api` | Phone probe; cloud-environments "github-proxy" |
| A phone session starts on the requested branch | ❌ **Probe:** it started on a fresh `claude/…` branch from `main` and needed `git checkout` | Phone probe |
| The Android chat app loads account skills | Not tested, undocumented. Out of v1 | support article 11869629 |
| One install reaches every device | ❌ Two separate paths (plugin, account skills). Account skills do sync into terminal Claude Code | code.claude.com/docs/en/skills |
| claude.ai skill upload limits | `name` ≤ 64 chars, `description` ≤ 200 chars, ZIP with the skill folder at the root, code execution enabled | support article 12512198 |
| Matt's licence allows adapting | ✅ MIT | mattpocock/skills LICENSE |
| Matt's `grilling` is one question at a time | ❌ Frontier rounds (see D6) | mattpocock/skills `skills/productivity/grilling` |
| Matt's `to-tickets` has blocking links and a ready label | ✅ `Blocked by`, `ready-for-agent`, sub-issues. It needs his setup skill for the tracker, so ours targets GitHub directly | mattpocock/skills `skills/engineering/to-tickets` |
| The glossary/ADR/tracker parts to cut are in `grilling` | ❌ They're in `to-tickets` (and `grill-with-docs`); `grilling` has none (found by PR #3) | mattpocock/skills at `49dd158` |

## Second opinion

A phone-started cloud session wrote its own version of this proposal (PR #3, closed). It reached the same rounds-vs-one-question conflict independently, and caught the two corrections credited above (to-tickets, D4).

## Out of scope (v1)
Jira; the Android chat app (D5); cross-session or cross-repo ticket discovery; automating the retro step (done by hand after each pilot).

## Risks
- **The skills and the account-skill copy drift**, once the phone path exists. The plugin stays the source; account-skill zips are built from it.
- **The fact-check depends on doc pages**, and some were secondhand (third-party issue trackers). Each ⚠️ row gets confirmed by one real install before the phone ticket is closed.
