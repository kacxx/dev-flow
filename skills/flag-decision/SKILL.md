---
name: flag-decision
description: "Use when implementing a ticket and the work shows a decision it implements (the ticket's Implements: line) is wrong, impossible or contradicted by the code. Stops and flags it instead of redesigning."
---

# Flag decision

You're implementing a ticket, and what you found means a decision it implements can't stand as written. **Stop and flag it. Don't redesign inside the ticket.** A quiet workaround makes the code disagree with the decision record, and every later ticket built on that decision inherits the mismatch.

## When this applies

Flag it when the work shows a decision the ticket implements is wrong, impossible or contradicted. That's a decision named on its `Implements:` line or, for a short-path issue that is itself the ticket, one of its own `### D<n>` decisions. The decision is:
- **wrong:** it rests on something that isn't true (a file, API or behaviour that doesn't exist or works differently);
- **impossible:** it can't be built as written without breaking something else;
- **contradicted:** another decision, the existing code, or a constraint you've found rules it out.

Don't flag implementation details the decision doesn't settle: a helper's name, error wording, an edge case the decision is silent on. Handle those in the ticket as normal. The test: would doing the work as decided give a result the owner didn't agree to? If not, it's not a flag.

## 1. Stop

Don't write code that works around the decision. If you have work in progress worth keeping, commit and push it on the ticket's branch as one commit titled `WIP: stopped at flag-decision D<n>, not a workaround`, and open no PR from it. Uncommitted work is lost when a cloud or phone session ends.

## 2. Post the evidence on the ticket

One comment, written so the owner can decide without re-investigating:

```markdown
## Decision flagged: D<n>

**Decision:** D<n>, "<title>", in <docs/proposals/<name>.md | #<issue>>: <the decision's text, quoted>

**What I found:** <the fact, stated plainly>

**Evidence:** <file:line, command and its output, test result or doc link>

**Why it blocks this ticket:** <what doing it as decided would produce, and why that isn't what was agreed>

**Options, not chosen:** <one line each, if any are obvious; the owner decides>

Stopped here; nothing was redesigned. Next: `grill` on D<n>.
```

## 3. Label the ticket

Swap the labels, so no other agent picks it up while the decision is open:

```bash
gh api repos/OWNER/REPO/labels/needs-decision --silent \
  || gh api repos/OWNER/REPO/labels --method POST -f name=needs-decision -f color=d93f0b
gh api repos/OWNER/REPO/issues/T/labels --method POST -f 'labels[]=needs-decision'
# remove ready-for-agent only if the ticket has it, so a real error (403, rate limit) isn't hidden
gh api repos/OWNER/REPO/issues/T/labels --jq '.[].name' | grep -qx ready-for-agent \
  && gh api repos/OWNER/REPO/issues/T/labels/ready-for-agent --method DELETE
```

If any of these fails, say so: a ticket left with `ready-for-agent` next to `needs-decision` can still be picked up.

Post the comment the same way (`gh api repos/OWNER/REPO/issues/T/comments --method POST -F body=@-` with a quoted heredoc). Use `gh api`, never `gh issue` (GraphQL fails in cloud sessions).

## 4. Point the source at it

On the source issue (the ticket's `Parent:`), add one comment so the decision's owner sees it. Skip this when the ticket is itself the source (a short-path issue):

```markdown
D<n> flagged by #T: <one line>. See #T for the evidence.
```

## 5. Hand off and stop

Tell the owner what you flagged and why, and the next steps, which belong to `grill` and the owner, not to you. The `needs-decision` label and your comment are the reopen marker; don't edit the doc or the decision yourself:
1. Run `grill` on D<n> alone. It revises the decision where it lives, keeping the **same ID** and the old text as superseded.
2. It proposes a re-slice of the open tickets that say `Implements: D<n>`, including #T, for the owner to approve.
3. It removes `needs-decision` from #T and puts `ready-for-agent` back if #T is still valid and unblocked.

Until then, `to-tickets` won't slice the source again.

Then stop working on the ticket.

## The CLAUDE.md pointer

This is the one copy of the line; the README links here. Projects that use these skills add it to their `CLAUDE.md`, or to the file it imports (e.g. `AGENTS.md`). The fallback sentence keeps it followable by agents without the plugin (Codex, or anyone who hasn't installed dev-flow):

```markdown
- If a ticket's work shows a decision it implements (on its `Implements:` line, or in its own `### D<n>` decisions) is wrong, impossible or contradicted, run the `flag-decision` skill and stop. If that skill isn't available, stop anyway and comment on the ticket saying which decision is wrong and why. Don't redesign inside the ticket.
```
