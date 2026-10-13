# dev-flow

Lightweight workflow skills for getting from an idea to tickets someone can implement.

## Flows

1. **idea → tickets** (this repo): capture the idea, settle the open questions, write a
   decided proposal, slice it into tickets that link back to their decisions.
2. **tickets → merged code**: covered elsewhere (Superpowers, Matt Pocock's skills).
3. **merged → released**: per project.
4. **retro**: after each run, fix what was clumsy.

## Status

Designing flow 1 by running it by hand on itself (issue #1), then piloting on
aside-jot and shipledger. Skills get written from what the manual runs show.

## Using it in a project

Install the plugin (`/plugin marketplace add kacxx/dev-flow`, then `/plugin install dev-flow@dev-flow`), and add the one-line pointer from [`skills/flag-decision/SKILL.md`](skills/flag-decision/SKILL.md#the-claudemd-pointer) to the project's `CLAUDE.md`. Then an agent implementing a ticket stops instead of redesigning when a decision turns out wrong.

## On the phone (claude.ai account skills)

Cloud sessions started from the phone's Code tab don't load plugins, but they do load claude.ai account skills (D5). The phone set is `capture`, `grill` and `flag-decision`:

1. Build the ZIPs: `python3 -I scripts/build_account_skills.py` (`python` on Windows, where `python3` is often the Microsoft Store stub) writes `dist/account-skills/<name>.zip`, after checking the folder name, `name` ≤ 64, `description` ≤ 200, and that the frontmatter is valid YAML (an unquoted `: ` breaks it).
2. Upload each ZIP on claude.ai under **Customize → Skills** (code execution must be enabled).
3. Re-upload after a skill changes: account skills don't follow plugin versions.

Phone sessions start on a fresh `claude/…` branch, so check out the branch you need before working.

