---
max_turns: 15
allowed_tools: [Skill]
---

This session can't reach GitHub, so here is short-path issue #12 from my repo kacxx/catalog-sync, with its decisions. Slice it into tickets.

<issue>
## Problem

The sync job copies product records from the catalog team's feed into our search index. A record with a category we don't recognise lands in the index anyway and breaks the category filters.

## Idea

A strict mode that rejects records whose category isn't one we recognise.

## Open questions

None.

## Decisions

### D1: Strict mode
In strict mode, a record whose `category` isn't on the allowed list is rejected instead of indexed.

### D2: Allowed list
The allowed list of categories lives in `sync.yaml`, next to the job's other settings.

### D3: Turning it on
Strict mode is off by default and turned on per environment with the `strict_mode` flag.

### D4: Rejects
Each rejected record is written to a rejects log with its id and category.

Path: short — the decisions are the design, so next is `slice`.
</issue>

Earlier in this session you showed me this breakdown, and I approved it:

**T1 — Strict mode rejects records with an unknown category**
- **Implements:** D1, D2, D3
- **Blocked by:** none
- **What it delivers:** with `strict_mode` on, a record whose category isn't in `sync.yaml`'s allowed list is not indexed; with it off, nothing changes.

**T2 — Rejected records go to a rejects log**
- **Implements:** D4
- **Blocked by:** T1
- **What it delivers:** each record strict mode rejects is written to the rejects log with its id and category.

A fresh agent then read the drafted tickets cold, with only the ticket bodies, the decisions above and the code. Here is what it raised:

1. The staging catalog has 3 of production's 40 categories, so strict mode passing on staging says nothing about production. Where is it shown to work?
2. `sync.yaml` is also read by the mobile app's sync job. Adding the allowed list there changes what that job does too. Is that intended?
3. The catalog team is adding a new category value next quarter. With a fixed allowed list, every record carrying it would be rejected. What should happen when they add one?
4. The rejects log: one line per rejected record, or one line per category with a count?
5. The rejects log has no size limit. Should it be capped?
6. The catalog team hasn't published `category` in the production feed yet; it ships in their next release. T1 can't be checked in production until it does.
7. Where does the command that flips `strict_mode` live: in this repo, or in the deploy config?

Carry on slicing from there, with the `slice` skill.
