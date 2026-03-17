---
name: Plan-ralph-once
description: >-
  Human-in-the-loop single-iteration issue processor. Use when asked to "run ralph once", "do one ralph pass", or "process this issue with ralph". Runs exactly one iteration of the ralph agent loop — picks the next eligible issue, creates a branch, runs the agent, applies feedback gates, commits, opens a PR, then stops for human review. Best for complex, large, or unfamiliar issues.
---

# Ralph Once

Single-pass version of the ralph loop. Runs one iteration and stops — you review, steer, then re-run.

## Quick Start

```bash
# Process the next eligible issue
bash scripts/ralph-once.sh

# Target a specific issue
RALPH_ISSUE_NUMBER=42 bash scripts/ralph-once.sh
```

## When to Use This vs ralph-loop

| Situation | Use |
|---|---|
| Routine, well-defined S/M issues | `ralph-loop` |
| Complex, large (L), or unfamiliar issues | `ralph-once` |
| First time running ralph on a repo | `ralph-once` |
| Issue was `blocked` and needs a fresh start | `ralph-once` |
| You want to review before merging | `ralph-once` |

## Mechanics

Identical to `ralph-loop` but exits after one iteration:

1. Select next eligible issue (or use `RALPH_ISSUE_NUMBER` override)
2. Create branch `ralph/issue-{n}/iter-{i}`
3. Run agent with [references/prompt.md](references/prompt.md) + progress history
4. Run feedback gates
5. Commit changes and open PR
6. Comment on issue with PR link
7. **Stop** — output summary for human review

## Configuration

Same environment variables as `ralph-loop` — copy `assets/config.env.example` and source it.

`RALPH_ISSUE_NUMBER` — if set, targets that specific issue instead of auto-selecting.
