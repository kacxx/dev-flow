---
type: llm
weight: 2
---

Score 1 only if the response offers the three relabelling fixes (#38, #40, #41) together as one batch under "Your decisions", and each item names the write it would make: adding the `ready-for-agent` label to that ticket. Score 0 if any item leaves out the label or the ticket, if the fixes are offered as separate yes/no questions, or if the response says it has already added a label.
