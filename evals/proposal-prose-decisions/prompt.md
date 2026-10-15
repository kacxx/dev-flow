---
max_turns: 20
allowed_tools: [Skill, WebFetch]
---

This session has no `gh` or git access to my repo (it can still fetch public web pages), so here is issue #4 from my repo kacxx/notes-cli and my comment on it. I answered the open questions myself; I didn't run settle. Write the proposal doc for it. Paste the full doc in your reply; don't write files or open a PR.

<issue>
## Problem

My notes CLI (`notes`) has no way to think an idea through. I keep half-formed ideas in `ideas.md` and lose track of which ones I've thought through.

## Idea

Add a `notes grill <idea>` command that interviews me about an idea and saves the answers.

## Open questions

1. What's the command called?
2. What should the interview be based on?
3. Where do the answers go?
</issue>

<comment author="owner">
Good idea, build it. My answers:
1. `notes grill <idea>`.
2. Base it on Matt Pocock's grilling skill (github.com/mattpocock/skills, skills/productivity/grilling/SKILL.md), since it asks one question at a time.
3. Save them under the idea's heading in `ideas.md`.

Watch out: cap an interview at 10 questions so it never runs forever.
</comment>
