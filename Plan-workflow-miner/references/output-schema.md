# workflow_insights.json Output Schema

The final output of `workflow_miner.py`. Contains mined patterns and concrete automation recommendations.

## Top-level Structure

```json
{
  "generated_at": "2026-03-14T10:23:45Z",
  "log_sources": ["~/.claude/projects/my-project/"],
  "sessions_analysed": 42,
  "events_processed": 3847,
  "recommendations": {
    "custom_commands": [...],
    "post_edit_hooks": [...],
    "auto_allow_rules": [...]
  },
  "patterns": [...],
  "approval_spam": [...]
}
```

## recommendations.custom_commands

Commands to add to `.claude/commands/` or equivalent:

```json
{
  "name": "test-and-lint",
  "description": "Run tests then lint (appears 47 times in sessions)",
  "frequency": 47,
  "command": "pytest && ruff check .",
  "trigger_pattern": ["Bash:pytest", "Bash:ruff"],
  "confidence": 0.92
}
```

## recommendations.post_edit_hooks

Hooks to add to `.claude/settings.json` `hooks.PostToolUse`:

```json
{
  "name": "auto-format-python",
  "description": "Format Python files after every edit (approved 38 times)",
  "frequency": 38,
  "hook": {
    "matcher": "Edit|Write",
    "hooks": [{"type": "command", "command": "ruff format ${file}"}]
  },
  "file_pattern": "*.py",
  "confidence": 0.88
}
```

## recommendations.auto_allow_rules

Permission rules to add to `allowedTools` in settings:

```json
{
  "name": "allow-pytest",
  "description": "pytest was approved every time it was requested (52/52)",
  "frequency": 52,
  "approval_rate": 1.0,
  "rule": "Bash(pytest*)",
  "safe": true,
  "confidence": 0.99
}
```

## patterns

Raw mined sequences for inspection:

```json
{
  "sequence": ["Bash:git add", "Bash:git commit", "Bash:git push"],
  "frequency": 23,
  "episodes": ["ep-001", "ep-007", "..."],
  "label": "commit and push workflow"
}
```

## approval_spam

Tool calls that required approval every time:

```json
{
  "tool": "Bash",
  "command_pattern": "npm install",
  "approval_count": 31,
  "denied_count": 0,
  "recommendation": "add to auto_allow: Bash(npm install*)"
}
```
