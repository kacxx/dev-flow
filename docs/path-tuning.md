# Path tuning (D2)

One entry per idea that went through `capture`, appended after each pilot. D2's "more than about three tickets" cut-off is revised through `settle` when these show it's wrong.

| Date | Repo / issue | Path capture picked | Tickets it became | Right path? | Note |
|---|---|---|---|---|---|
| 2026-10-12 | kacxx/dev-flow#1 | full (by hand, before `capture` existed) | 8 (kacxx/dev-flow#5–#12) | yes | |
| 2026-10-13 | kacxx/aside-jot#78 | full (captured by hand; `proposal` run on PR kacxx/aside-jot#79) | 5 (kacxx/aside-jot#82–#86) | yes | D3 reopened by the fact-check; see [Outcomes](#kacxxaside-jot78-jot-status-check-activity) |

## Outcomes

### kacxx/aside-jot#78: jot status check (`activity`)

Captured 2026-10-13 (the table's date); sliced and built 2026-10-14.

Times are UTC, from the GitHub record.

- **Proposal (elapsed, not active time):** kacxx/aside-jot#78 was opened on 2026-10-12 06:59, and the proposal PR (kacxx/aside-jot#79) merged on 2026-10-14 00:02, about 41 hours later. That includes capture, the pilot's fixes to dev-flow itself (kacxx/dev-flow#19) and the day the rewritten doc sat unpushed (kacxx/dev-flow#11), so it overstates what the proposal step costs. Active time wasn't recorded.
- **Tickets:** `to-tickets` published 5 tickets at 00:10. The chain is kacxx/aside-jot#82 (CLI) → kacxx/aside-jot#84 (MCP tool) → kacxx/aside-jot#85 ("update jot X") → kacxx/aside-jot#86 ("update all"), with kacxx/aside-jot#83 (Codex hook) independent.
- **Build:**
  - all five PRs (kacxx/aside-jot#87–#91) opened between 01:15 and 01:21, about 1h10m after the tickets;
  - kacxx/aside-jot#87 and kacxx/aside-jot#88 merged at 02:27, and kacxx/aside-jot#89–#91 between 04:43 and 04:48.
  - Tickets to all merged took **about 4h40m**, most of it waiting for review and merge. The release PR (kacxx/aside-jot#92, 0.3.0) followed.
- **Estimate without slicing:** owner, on kacxx/dev-flow#29: compared with earlier features across aside-jot, shipledger and dev-flow, all built with AI coding, this one was "way faster to implement". No number.
- **`flag-decision`:** not triggered. No `needs-decision` label and no flag comment in the repo, so it's still unproven in a live run.
- **Live `gh` writes:**
  - Issue creation, the `ready-for-agent` label at publish (kacxx/aside-jot#82, kacxx/aside-jot#83) and the 5 sub-issue links all worked.
  - **Gap in `to-tickets` (fixed in 0.9.0 by kacxx/dev-flow#38 / kacxx/dev-flow#50: `status` now offers the relabelling fix):** nothing adds `ready-for-agent` when a blocker closes. The skill only lists in its report which tickets should get it. kacxx/aside-jot#82 merged at 02:27, which unblocked kacxx/aside-jot#84, and kacxx/aside-jot#84–#86 never got the label. Here it didn't matter, because one implementer stacked the PRs for kacxx/aside-jot#84–#86 on the PR chain they depend on (kacxx/aside-jot#88 → kacxx/aside-jot#89 → kacxx/aside-jot#90) while kacxx/aside-jot#82 was still open. But with more than one implementer, or a pause between tickets, blocked tickets would stay unlabelled and nobody would pick them up. The relabelling step needed a follow-up, which kacxx/dev-flow#38 / kacxx/dev-flow#50 added.
