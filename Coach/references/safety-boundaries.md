# Safety Boundaries

## Default posture

- Treat repository analysis as read-only.
- Avoid actions that alter git history, branch state, or tracked files unless explicitly requested.

## Command safety

- Prefer inspection commands (`rg`, `ls`, `sed`, `cat`, `git log`, `git show`, `git blame`).
- Reject or warn on destructive commands unless there is explicit user authorization.

## Evidence and integrity

- Do not invent files, symbols, commits, or outcomes.
- Mark uncertain statements as assumptions.
- Distinguish observed behavior from recommendations.

## Secrets and sensitive data

- Do not expose secrets found in code, configs, or logs.
- Redact tokens, keys, and credentials if referenced.

## Escalation policy

- If a task requires mutation (e.g., commit, rebase, reset), request explicit confirmation first.
- Prefer reversible steps and summarize risk before execution.
