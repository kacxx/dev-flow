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

Install the plugin (`/plugin marketplace add kacxx/dev-flow`, then `/plugin install dev-flow@dev-flow`), and add this line to the project's `CLAUDE.md`, so an agent implementing a ticket stops instead of redesigning when a decision turns out wrong:

```markdown
- If a ticket's work shows a decision it implements (`Implements: D<n>`) is wrong, impossible or contradicted, run the `flag-decision` skill and stop. Don't redesign inside the ticket.
```
