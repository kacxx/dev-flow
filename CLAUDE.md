# dev-flow

- If a ticket's work shows a decision it implements (on its `Implements:` line, or in its own `### D<n>` decisions) is wrong, impossible or contradicted, run the `flag-decision` skill and stop. If that skill isn't available, stop anyway and comment on the ticket saying which decision is wrong and why. Don't redesign inside the ticket.
- When you post a PR review, post it as a formal review, not a plain comment: `gh api repos/OWNER/REPO/pulls/N/reviews -f event=COMMENT -f commit_id=SHA -f body=…`, with `commit_id` set to the commit you actually read. Left out, it defaults to the head when the review is posted.
