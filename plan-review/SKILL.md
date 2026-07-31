---
name: plan-review
description: Review a GitHub plan (an epic issue and its child task sub-issues) with a senior-engineer eye before any code is written — checking for DRY violations, non-atomic or over-large tasks, missing dependency edges, and structural problems in the approach. Use when the user wants a plan sanity-checked: "review this plan", "review these issues/tickets", "is this breakdown atomic?", "poke holes in this plan before we build", or as the stage after /spec in /pair. Reviews the plan, not code. Do NOT write or execute anything — this stage only surfaces findings and gates.
---

# Plan Review — senior-engineer review of a GitHub plan

Review the plan with a senior-engineer eye **before any code is written**. Fetch the task list
(the user gives the epic number, or find the most recent open `spec:epic`). Per
[../spec/GITHUB-ISSUES.md](../spec/GITHUB-ISSUES.md):

```bash
gh api repos/<owner/repo>/issues/<epic-n>/sub_issues --jq '.[] | "#\(.number) [\(.state)] \(.title) | \((.labels|map(.name))|join(","))"'
```

Evaluate for: DRY violations in the plan, over-stuffed tasks that aren't atomic, missing dependency edges, tasks too large for a single TDD slice, structural issues in the proposed approach.

For each finding use this structure:
```
### [blocker | should-fix | nit] — Principle
**What:** one sentence
**Why it matters:** two to three sentences tied to this specific plan
**Fix:** concrete change to the task scope or split
```

**Gate after review:**

```
question: "Plan review complete. How do you want to proceed?"
options:
  - "Plan looks good — proceed (Recommended)"
  - "Revise plan — loop back to grill with these findings"
  - "Accept with caveats — annotate the issues and proceed"
```

If "loop back": carry the findings as the opening context for a new [`grill`](../grill/SKILL.md) session. Update the task issues after the revised grill (via [`spec`](../spec/SKILL.md)). Re-run this review. Repeat until the plan passes or the user explicitly accepts.
