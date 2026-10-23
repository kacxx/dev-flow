# Cold read (slice step 5)

Follow this once the owner has approved the breakdown, and before publishing. A fresh reader reads the drafted tickets cold, and what it finds is settled with the owner.

**Write the full bodies** of the approved tickets in the step 6 template, with `T<n>` for issue numbers. The reader reads these, and the owner approves them.

**Send them to a fresh reader:** a sub-agent given only what an implementer would have: the bodies, the decisions or doc their `Implements:` line points to, and the repo's name or path. Nothing from this conversation. Its prompt:

```
You're about to implement these tickets in <OWNER/REPO>, and nobody is around to ask. Read only: don't build, edit or post anything. Read the tickets, the decisions they point to, and the code. For each ticket, say:
1. What would you build?
2. Where would you build it?
3. How would you know you're done?
4. Every point where you'd have to guess or ask, one per line.
List the guesses; don't answer them.

<the drafted ticket bodies>

<the decisions or doc they point to>
```

With no sub-agent tool, the owner runs the prompt in a fresh session. If the findings are already given, sort them without sending another reader.

**Sort the findings,** one line each, every line labelled with its group, even under a heading per group:

```
- **real gap:** T1 — <finding>. <the decision the owner has to make>
- **default:** T2 — <something a developer would otherwise pick alone>. Proposed: <value>
- **known blocker:** T1 — <something outside the tickets that isn't true yet>. <what has to happen first>
```

Show the sort, then the full bodies with their `## Defaults`, even while real gaps are open, and ask the owner to confirm the sort and the values, or to move items. **Publish nothing until they confirm.**

**Defaults** go after Acceptance criteria as `## Defaults`, one line each, with no D-numbers; a ticket with none has no section. An implementer who finds one wrong changes it and says so in the PR, not through `flag-decision`.

**Real gaps** go to `settle`, run in this session with the gaps as its questions, without writing them under Open questions first. Tell it not to set `Path: ready` or `ready-for-agent` on the source issue.
- **Short path:** once they're decided, redraft the affected tickets, get the breakdown approved again (step 4), and read again.
- **Full path:** stop. `slice` is re-run once `settle` and `proposal` have the doc decided again. List the gaps under **Your decisions**, and write nothing else.

**Known blockers** (for now; dev-flow#99 replaces this): list each under **Later**, and publish its ticket without `ready-for-agent`.

**Rounds.** A round is one read and its sort, including one after a redraft. Stop when a round raises only defaults and blockers already recorded, and publish. If real gaps remain after round 2, ask the owner whether to continue.

If the owner stops, write the remaining gaps into the source issue body's `## Open questions` (`status` reads only the body). Then publish, leaving `ready-for-agent` off every ticket a remaining gap was cited against, and name them in the hand-off. Known gap: on the full path, `status` ignores the source's Open questions once a doc exists.
