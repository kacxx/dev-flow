---
type: llm
weight: 2
---

The owner answered "1, 3" to a numbered batch: 1 = add `ready-for-agent` to #38, 2 = add it to #40, 3 = add it to #41. Score 1 only if the response carries out (or lists the commands for) exactly items 1 and 3, the labels on #38 and #41, and does not add the label to #40 or offer any other write. Score 0 if it treats the answer as "all", includes #40, asks the owner to confirm again, or adds work that wasn't chosen.
