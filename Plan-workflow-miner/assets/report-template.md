# Workflow Mining Report

**Generated**: {generated_at}
**Log Sources**: {log_sources}
**Sessions Analysed**: {sessions_analysed}
**Events Processed**: {events_processed}

---

## Recommended Custom Commands

Add these to `.claude/commands/` (or equivalent):

| Command | Triggers | Frequency | Confidence |
|---|---|---|---|
| `/{name}` | `{trigger_pattern}` | {frequency}x | {confidence} |

---

## Recommended Post-Edit Hooks

Add to `.claude/settings.json` under `hooks.PostToolUse`:

```json
{hook}
```

---

## Recommended Auto-Allow Rules

Add to `allowedTools` in settings:

| Rule | Approval Rate | Frequency | Safe? | Notes |
|---|---|---|---|---|
| `{rule}` | {approval_rate}% | {frequency}x | {safe} | {warning} |

---

## Top Repeated Sequences

| Sequence | Count |
|---|---|
| `{sequence}` | {frequency}x |

---

## Approval Spam

Tools you approved every single time:

| Tool | Approvals | Denials |
|---|---|---|
| `{tool}` | {approval_count} | {denied_count} |
