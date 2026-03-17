---
name: Plan-workflow-miner
description: >-
  Parses Claude Code, Codex CLI, and OpenCode session logs to mine repeated tool sequences and approval-spam commands, then outputs automation recommendations. Use when asked to "mine my workflows", "find what I keep approving", "automate my repetitive agent commands", or "analyse my session logs".
---

# Workflow Miner

Parse AI coding session logs, find repeated patterns, and get concrete automation recommendations — custom commands, post-edit hooks, and auto-allow permission rules.

## Quick Start

```bash
# Auto-detect log format
python3 scripts/workflow_miner.py --logs ~/.claude/projects/ --target auto

# Explicit target
python3 scripts/workflow_miner.py --logs ~/.cursor/logs/ --target claude_code --since 7d

# Output to file
python3 scripts/workflow_miner.py --logs . --out workflow_insights.json
```

## CLI Reference

```
workflow_miner.py [OPTIONS]

Options:
  --target {claude_code|codex_cli|opencode|auto}
                        Log format to parse (default: auto)
  --logs PATH           Directory containing log files (default: .)
  --since DURATION      Only parse logs from last N days/hours (e.g. 7d, 48h)
  --out PATH            Write JSON report to this path (default: stdout)
  --redact              Redact file paths and content from output
```

## Pipeline

```
Parse → Normalize → Segment episodes → Mine sequences → LLM label → Emit recommendations
```

1. **Parse** — Format-specific adapters extract tool calls from raw logs (see `scripts/adapters/`)
2. **Normalize** — All events converted to `NormalizedEvent` schema (see `references/normalized-schema.md`)
3. **Segment** — Events grouped into work episodes by time gap and context switch
4. **Mine** — Frequent sequential patterns extracted; approval-spam commands identified
5. **LLM label** — Aggregated patterns (not raw logs) sent to LLM for human-readable labels
6. **Emit** — Recommendations written in `workflow_insights.json` format (see `references/output-schema.md`)

## Output

Three recommendation categories:

- **Custom commands** — slash commands to replace repeated multi-step sequences
- **Post-edit hooks** — shell commands to auto-run after editing specific file patterns
- **Auto-allow rules** — permission patterns safe to auto-approve (with deny-list guardrails)

See `references/safe-commands.md` for the allow/deny framework.

## Privacy

`--redact` strips file paths and file content from all log events before processing. Aggregated patterns (tool names and sequences) are sent to the LLM — raw log content never leaves your machine.

## Reference Files

- [references/normalized-schema.md](references/normalized-schema.md) — NormalizedEvent field definitions
- [references/output-schema.md](references/output-schema.md) — workflow_insights.json format
- [references/safe-commands.md](references/safe-commands.md) — auto-allow allowlist/denylist rules
