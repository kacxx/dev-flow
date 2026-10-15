---
max_turns: 8
allowed_tools: [Skill]
---

/dev-flow:status kacxx/aside-jot#95

This session can't run commands or reach GitHub, so here is what `state.py kacxx/aside-jot#95` printed, recorded on 2026-10-15 (fixture `revision-in-progress-aside-jot-95`). Use it as the script's output.

<state>
{
  "issue": "kacxx/aside-jot#95",
  "title": "Skill: offer an aside add for open follow-ups when closing a jot",
  "stage": "revision in progress",
  "evidence": [
    "doc PR aside-jot#100 is open",
    "3 sub-issues exist"
  ],
  "also_matched": [
    "in progress",
    "proposal drafted",
    "decided, short path"
  ],
  "next_action": "merge aside-jot#100, then update #97–#99",
  "steps": [
    {
      "who": "owner",
      "do": "merge aside-jot#100"
    },
    {
      "who": "agent",
      "do": "update #97–#99",
      "writes": [
        "edits to the bodies of #97–#99 to match the merged doc"
      ],
      "shows_draft": true
    }
  ],
  "later": [],
  "tickets": [
    {
      "number": 97,
      "title": "Offer a follow-up jot when closing a jot (macOS and Linux)",
      "state": "open",
      "labels": [],
      "blocked_by": []
    },
    {
      "number": 98,
      "title": "Windows follow-up form",
      "state": "open",
      "labels": [],
      "blocked_by": [
        97
      ]
    },
    {
      "number": 99,
      "title": "Follow-ups for partly done jots and in \"Update all\"",
      "state": "open",
      "labels": [],
      "blocked_by": [
        97
      ]
    }
  ],
  "doc_prs": [
    {
      "number": 100,
      "title": "docs(proposal): add D10-D15 from the #95 review",
      "created_at": "2026-10-14T10:30:00Z",
      "docs": {
        "docs/proposals/follow-up-jots.md": "decided"
      },
      "reopened": false
    }
  ],
  "doc": {
    "path": "docs/proposals/follow-up-jots.md",
    "status": "decided",
    "reopened": false
  },
  "last_write": {
    "at": "2026-10-14T10:30:00Z",
    "what": "doc PR aside-jot#100 opened"
  },
  "review_comments": [],
  "fixes": [],
  "batch": [
    {
      "from": "step",
      "do": "update #97–#99",
      "writes": [
        "edits to the bodies of #97–#99 to match the merged doc"
      ],
      "shows_draft": true
    }
  ]
}
</state>
