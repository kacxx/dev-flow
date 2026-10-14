# Path tuning (D2)

One entry per idea that went through `capture`, appended after each pilot. D2's "more than about three tickets" cut-off is revised through `grill` when these show it's wrong.

| Date | Repo / issue | Path capture picked | Tickets it became | Right path? | Note |
|---|---|---|---|---|---|
| 2026-10-12 | kacxx/dev-flow#1 | full (by hand, before `capture` existed) | 8 (#5–#12) | yes | |
| 2026-10-13 | kacxx/aside-jot#78 | full (captured by hand; `proposal` run on PR #79) | 5 (#82–#86) | yes | D3 reopened by the fact-check; built in about 4h40m from tickets to merged (below) |

## Outcomes

### kacxx/aside-jot#78: jot status check (`activity`), 2026-10-14

Times are UTC, from the GitHub record.

- **Proposal:** #78 was opened on 2026-10-12 06:59. The proposal PR (#79) merged on 2026-10-14 00:02, about 41 hours later, including the day the pilot's rewritten doc sat unpushed (#11).
- **Tickets:** `to-tickets` published 5 tickets at 00:10. The chain is #82 (CLI) → #84 (MCP tool) → #85 ("update jot X") → #86 ("update all"), with #83 (Codex hook) independent.
- **Build:**
  - all five PRs (#87–#91) opened between 01:15 and 01:21, about 1h10m after the tickets;
  - #87 and #88 merged at 02:27, and #89–#91 between 04:43 and 04:48.
  - Tickets to all merged took **about 4h40m**, most of it waiting for review and merge. The release PR (#92, 0.3.0) followed.
- **Estimate without slicing:** owner, on kacxx/dev-flow#29: compared with earlier features across aside-jot, shipledger and dev-flow, all built with AI coding, this one was "way faster to implement". No number.
- **`flag-decision`:** not triggered. No `needs-decision` label and no flag comment in the repo, so it's still unproven in a live run.
- **Live `gh` writes:**
  - Issue creation, the `ready-for-agent` label at publish (#82, #83) and the 5 sub-issue links all worked.
  - The label swap for blocked tickets never happened: #84–#86 never got `ready-for-agent`. Their PRs were opened stacked on the blockers' PRs while #82 and #83 were still open, so for one implementer doing a whole run, the blocking edges set the PR order and the label didn't gate anything.
