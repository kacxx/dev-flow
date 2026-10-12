---
type: llm
weight: 2
---

The module path is a fact this session cannot check (it cannot read the repo). Score 1 only if the response: lists that fact under a "To check" section; picks the "short" path (not "ready"), because something is still unchecked; does not plan the ready-for-agent label; and tells the owner how to override. Score 0 if it picks "ready" or plans the ready-for-agent label.
