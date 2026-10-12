---
type: llm
weight: 2
---

The response is a DRAFT GitHub issue (nothing posted). Score 1 only if all of these hold:

1. It has the sections "Problem", "Idea" and "Open questions", in that order (a "To check" list and, on the ready path, an "Acceptance criteria" section may follow; Open questions may say "None").
2. Problem is grounded in the concrete situation the user described.
3. Open questions, if any, are numbered DECISIONS for the owner (choices). Facts the agent could not check (this test session cannot read the repo) belong in a separate "To check" list, not among the open questions.
4. The Idea section says what changes, but does not settle how: specific mechanisms, formats, names or rules that would reasonably be open questions are not presented as already decided. Restating constraints or choices the user stated themselves in the prompt is fine; only choices the agent added on its own count against it.
