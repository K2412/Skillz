# Ralph Loop Configuration Reference

All configuration is via environment variables. Copy `assets/config.env.example` to `.env`, fill in values, and `source .env` before running.

## Core Settings

| Variable | Default | Description |
|---|---|---|
| `RALPH_MAX_ITERATIONS` | `20` | Hard cap on total loop iterations |
| `RALPH_DRAFT_PR` | `true` | Open PRs as draft |
| `RALPH_HALT_ON_GATE_FAIL` | `false` | Stop loop on any gate failure (vs. log and continue) |
| `RALPH_ISSUE_LABEL` | `ralph` | Label used to select eligible issues |
| `RALPH_BLOCKED_LABEL` | `blocked` | Label that excludes an issue from selection |
| `RALPH_PROGRESS_FILE` | `progress.txt` | Append-only memory file path |
| `RALPH_BRANCH_PREFIX` | `ralph` | Branch name prefix |

## Agent Settings

| Variable | Default | Description |
|---|---|---|
| `RALPH_AGENT_CMD` | `claude` | CLI command to invoke the agent |
| `RALPH_AGENT_TIMEOUT` | `600` | Seconds before agent session is killed |
| `RALPH_AGENT_MAX_TOKENS` | _(unset)_ | Token limit passed to agent if supported |

## Feedback Gate Settings

Each gate can be individually enabled/disabled and customised.

| Variable | Default | Description |
|---|---|---|
| `RALPH_GATE_TYPECHECK_ENABLED` | `true` | Run typecheck gate |
| `RALPH_TYPECHECK_CMD` | `mypy .` | Typecheck command |
| `RALPH_GATE_LINT_ENABLED` | `true` | Run lint gate |
| `RALPH_LINT_CMD` | `ruff check .` | Lint command |
| `RALPH_GATE_TEST_ENABLED` | `true` | Run test gate |
| `RALPH_TEST_CMD` | `pytest` | Test command |
| `RALPH_GATE_COVERAGE_ENABLED` | `false` | Run coverage gate |
| `RALPH_COVERAGE_CMD` | `pytest --cov` | Coverage command |
| `RALPH_COVERAGE_THRESHOLD` | `80` | Minimum coverage % |
| `RALPH_GATE_DUPLICATION_ENABLED` | `false` | Run duplication gate |
| `RALPH_DUPLICATION_CMD` | `jscpd .` | Duplication command |
| `RALPH_GATE_ENTROPY_ENABLED` | `false` | Run entropy gate |
| `RALPH_ENTROPY_CMD` | _(custom)_ | Entropy/complexity command |

## GitHub Settings

| Variable | Default | Description |
|---|---|---|
| `RALPH_GH_REPO` | _(auto)_ | `owner/repo` — defaults to current repo |
| `RALPH_PR_LABELS` | `ralph` | Comma-separated labels to apply to opened PRs |
| `RALPH_COMMIT_PREFIX` | `[ralph]` | Prefix for all ralph commits |
