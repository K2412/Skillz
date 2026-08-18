# soc enforcement hook

Makes soc's answer-withholding **structural** instead of willpower: while a soc session is active, the
agent physically cannot use `Edit`/`Write`/`NotebookEdit` on your work.

## How it works

- `/soc` drops a sentinel file `~/.claude/.soc-active` when a session starts and removes it at the end.
- A `PreToolUse` hook on `Edit|Write|NotebookEdit` runs [`soc-write-guard.sh`](soc-write-guard.sh):
  if the sentinel is present (and fresh), it **denies** the write with a message telling the agent to
  guide instead of type. No sentinel → every edit passes untouched. Writes under
  `~/Documents/Learning/ledger/` are always allowed — that's soc's bookkeeping, not the user's work.
- **Fail-open:** any error, or no sentinel, allows the edit. A sentinel older than 6h is treated as a
  crashed session, ignored, and cleaned up — soc-mode can never get stuck on.

## Deploy (one-time)

The script must live at a stable path and be registered in `~/.claude/settings.json`:

```bash
mkdir -p ~/.claude/hooks
cp soc-write-guard.sh ~/.claude/hooks/soc-write-guard.sh
chmod +x ~/.claude/hooks/soc-write-guard.sh
```

Then add this entry to `hooks.PreToolUse` in `~/.claude/settings.json` (alongside any existing ones):

```json
{
  "matcher": "Edit|Write|NotebookEdit",
  "hooks": [
    { "type": "command", "command": "~/.claude/hooks/soc-write-guard.sh", "statusMessage": "soc write-guard..." }
  ]
}
```

Restart Claude Code to load the hook.

## Known v1 limitation

The guard blocks the easy write path (`Edit`/`Write`/`NotebookEdit`). A determined agent could still
write a file through a `Bash` heredoc, which isn't guarded (guarding arbitrary shell is fragile and
risks blocking legit commands). soc's SKILL.md discipline covers that gap; the hook removes the
frictionless path, which is what the model actually reaches for.

## Escape hatch

Stuck in soc-mode? `rm ~/.claude/.soc-active` lifts it immediately.
