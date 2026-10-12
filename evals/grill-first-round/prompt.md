---
max_turns: 10
allowed_tools: [Skill]
---

Here is issue #78 from my repo kacxx/aside-jot (this session can't reach GitHub, so I've pasted it). It's on the full path.

<issue>
## The problem

A jot often gets done in the very session it was captured in. Example: in a Claude Desktop session I jotted `>> get code reviews on the new skill PRs`, then carried on in that session, and it went on to work through the review comments on four PRs. The jot (#31) stayed open in the inbox. Nothing connects "this session later did the thing" to the jot, so I close it by hand, or another agent reading the inbox can't tell it is finished.

## Idea

`update jot X` (and `update all`): look at the jot's session after the jot was captured and decide whether it was actioned. If so, propose `aside done X --note "<evidence>"`.

aside is a plain store with no LLM, so the judging belongs to the agent, not to aside. aside would only expose the session's activity after the jot (a read-only `activity <id>` tool and command, reusing the transcript reader behind `promote --with-reply`), and the aside skill would get an "update" routine. The agent proposes each `done`; I approve.

The design is in the proposal PR (docs/proposals/jot-status-check.md), with open questions to settle in review.

## Open questions

- Should the agent only propose closures, or may it close clear cases itself (needs relaxing the skill's no-`done` rule)?
- Jots actioned in a different session: out of v1?
- Codex jots probably have no transcript (`transcript_path` is null in the recorded payload): accept "can't tell"?
- Command name: `activity`, `since` or `transcript`.
</issue>

Grill me on its open questions. Don't post anything.
