---
name: Plan-ralph-loop
description: >-
  AFK continuous autonomous loop that processes GitHub Issues one by one. Use when asked to "run ralph", "start the loop", or "process issues autonomously". Picks the next eligible issue labelled "ralph", creates a branch, runs the agent, applies feedback gates (typecheck, lint, test, coverage), commits, opens a PR, and repeats until no issues remain or the agent signals COMPLETE.
---

# Ralph Loop

Autonomous issue-processing loop. Runs unattended until all `ralph`-labelled issues are resolved or a stop condition is hit.

## Quick Start

```bash
# Run with defaults
bash scripts/ralph.sh

# With config overrides
RALPH_MAX_ITERATIONS=5 RALPH_DRAFT_PR=false bash scripts/ralph.sh
```

Configure via environment variables — see [references/config.md](references/config.md) for all options and defaults.

## Loop Mechanics

Each iteration:

1. **Select** — `gh issue list --search "is:open label:ralph -label:blocked"` picks the lowest-numbered eligible issue.
2. **Branch** — Creates `ralph/issue-{n}/iter-{i}`.
3. **Run agent** — Invokes Claude Code with [references/prompt.md](references/prompt.md) as system context, appending `progress.txt` history.
4. **Feedback gates** — Runs each enabled gate in order: typecheck → lint → test → coverage → duplication → entropy. Any failure aborts the iteration and logs the reason.
5. **Commit & PR** — Commits with `[ralph]` prefix, opens a draft PR (configurable), comments on the issue with the PR link.
6. **Persist** — Appends iteration summary to `progress.txt`.
7. **Check stop** — Halts if no more issues, max iterations reached, or agent output contains `<promise>COMPLETE</promise>`.

## Stop Conditions

- No issues match the selector
- `RALPH_MAX_ITERATIONS` reached
- Agent output or `progress.txt` tail contains `<promise>COMPLETE</promise>`
- Any feedback gate fails and `RALPH_HALT_ON_GATE_FAIL=true`

## Label Protocol

See [references/issue-labels.md](references/issue-labels.md) for the full label scheme (ralph, blocked, S/M/L sizing, etc.).

## Configuration

All behaviour is controlled via environment variables. Copy `assets/config.env.example` to `.env` and source it before running.

See [references/config.md](references/config.md) for the complete reference.
