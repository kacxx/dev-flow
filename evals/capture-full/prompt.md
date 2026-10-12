---
max_turns: 10
allowed_tools: [Skill]
---

Capture this idea as an issue for my repo kacxx/aside-jot. Draft it; don't post anything.

The idea: aside is a jot inbox. A jot often gets done in the very session it was captured in, but it stays open in the inbox because nothing connects "this session later did the thing" to the jot. Example: I jotted ">> get code reviews on the new skill PRs", carried on in that session, and it worked through the review comments on four PRs, but the jot stayed open. I'd like an "update jot X" / "update all" that looks at the jot's session after it was captured and works out whether it was done, then offers to mark it done. aside is a plain store with no LLM, so the judging should be done by the agent, not by aside.
