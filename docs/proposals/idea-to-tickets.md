# Idea → tickets flow (#1): proposal

Status: **decided (D1–D6). Ready to merge, then slice into tickets.**

## Problem

Ideas get from "I want X" to "here are the tickets" ad hoc. aside-jot #78 / PR 79 is the example. Its open questions were answered in an issue comment that never reached the doc, nobody checked the doc's claims against the code, and the doc PR was reviewed with `/code-review`, which looks for code bugs.

## Decisions

### D1: Ticket target
GitHub issues only for v1. Tickets are described in neutral fields (title, problem, acceptance criteria, which decision it implements, what blocks it), so a Jira writer can be added later without a redesign.

### D2: Short path
`capture` decides the path and says why; the owner can override in one word.
- **No open questions:** the issue becomes the ticket (acceptance criteria added, labelled `ready`).
- **Open questions answerable in one sitting:** grill them in the issue and write the decisions into the issue body. No proposal doc.
- **Needs design** (a new interface or command, a cross-cutting change, or more than about three tickets): the full path, ending in a proposal doc.

The three-ticket cut-off gets tuned after the pilots.

### D3: Linking
Decisions get stable IDs (`D1`, `D2`, …): headings in the proposal doc or, on the short path, in the issue body. Every ticket opens with:
```
Implements: D2, D4 — docs/proposals/<name>.md
Blocked by: #12
```
An agent can check the header with one search, and IDs don't change when the doc is edited.

### D4: Way back
1. The implementing agent stops and flags. It comments with the evidence and the decision it breaks, and labels the ticket `needs-decision`. It doesn't redesign inside the ticket.
2. The decision gets `Status: reopened — #<ticket>`, is grilled on its own, and is revised under the same ID with the old text kept as superseded.
3. Open tickets that say `Implements: D<n>` are re-sliced, and the owner approves the list.

Flow 2 needs a one-line rule: stop and flag, don't redesign.

### D5: Devices (revised 12 Oct, after the fact-check)
- **Mac and Windows:** a Claude Code plugin from this private repo. Mac first; Windows confirmed with one install.
- **Phone:** cloud sessions started from the Code tab in the phone app. Cloud sessions don't load plugins, so after the pilots the phone-friendly skills (`capture`, `grill`) get uploaded to the claude.ai account. Cloud sessions load account skills, and so does terminal Claude Code, through a one-way sync.
- **The Android chat app:** out of v1. Whether it loads account skills is undocumented.

<details><summary>Superseded (12 Oct): "claude.ai account skills for the Android app"</summary>

The original D5 put `capture` and `grill` in the Android chat app. The fact-check found that the docs don't say the chat app loads account skills, while cloud sessions (Code tab) do.
</details>

### D6: Starting point (revised 12 Oct, after the fact-check reopened it)
Adapt Matt Pocock's skills (MIT, with the notice in `NOTICE`):
- **`grill`:** his `grilling` **frontier rounds**, used as they are. Each round asks every question whose prerequisites are already settled, numbered, each with a recommended answer and worded so "yes" accepts it. The agent looks up facts with sub-agents and never asks the user for them. Additions: each answer is recorded under a `D<n>` ID (D3), and the session ends by writing a decisions record, since the manual run showed nothing else captures them.
- **`to-tickets`:** from his `to-tickets`, adding the `Implements:`/`Blocked by:` header (D3) and GitHub-issues output (D1).
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
  NOTICE                            # Matt Pocock's MIT notice for the adapted skills
```

- **GitHub access:** the skills read and write issues with `gh api repos/{owner}/{repo}/issues…`, not `gh issue`/`gh pr`. That works both locally and in cloud sessions, where GraphQL is blocked.
- **Updates:** bump `version` in `plugin.json` on each change. Installed plugins only update when the version changes.
- **Tests:** each skill must reproduce issue #1's manual run (capture → the six questions → D1–D6 → this doc).

## Fact-check

| Claim | Result | Source |
|---|---|---|
| A private repo can be a plugin marketplace (`/plugin marketplace add kacxx/dev-flow`) | ✅ Uses the existing git credentials (`gh auth setup-git` or SSH); `GITHUB_TOKEN` alone doesn't cover background updates | code.claude.com/docs/en/plugins/host-marketplace |
| Plugin = `marketplace.json` + `plugin.json` + `skills/<name>/SKILL.md` | ✅ Matches Matt's repo (`source: "./"`, explicit `skills` list) | create-marketplace docs; mattpocock/skills `.claude-plugin/` |
| The same plugin works on Windows | ⚠️ Native and WSL are both supported, but the docs don't say install is identical. WSL is a separate home directory, so a separate install | code.claude.com/docs/en/setup |
| The phone can use the skills | ⚠️ Through cloud sessions (Code tab): yes, via account skills or a repo's `.claude/skills/`. Through the Android chat app: undocumented | cloud-environments docs; support article 11869629 |
| Cloud sessions load plugins | ❌ No. They load committed `.claude/skills/` and claude.ai account skills | cloud-environments "what carries over" |
| Cloud sessions can use issues on a private repo | ✅ Via the GitHub proxy and `gh api`; `gh issue` fails (GraphQL blocked) | cloud-environments "github-proxy" |
| One install reaches every device | ❌ Two separate paths (plugin, account skills). Account skills do sync into terminal Claude Code | code.claude.com/docs/en/skills |
| claude.ai skill upload limits | `name` ≤ 64 chars, `description` ≤ 200 chars, ZIP with the skill folder at the root, code execution enabled | support article 12512198 |
| Matt's licence allows adapting | ✅ MIT | mattpocock/skills LICENSE |
| Matt's `grilling` is one question at a time | ❌ Frontier rounds (see D6) | mattpocock/skills `skills/productivity/grilling` |
| Matt's `to-tickets` has blocking links and a ready label | ✅ `Blocked by`, `ready-for-agent`, sub-issues. It needs his setup skill for the tracker, so ours targets GitHub directly | mattpocock/skills `skills/engineering/to-tickets` |

## Out of scope (v1)
Jira; the Android chat app (D5); cross-session or cross-repo ticket discovery; automating the retro step (done by hand after each pilot).

## Risks
- **The skills and the account-skill copy drift**, once the phone path exists. The plugin stays the source; account-skill zips are built from it.
- **The fact-check depends on doc pages**, and some were secondhand (third-party issue trackers). Each ⚠️ row gets confirmed by one real install before the phone ticket is closed.
