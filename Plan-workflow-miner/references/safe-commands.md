# Safe Commands — Auto-Allow Framework

Guidelines for determining which commands are safe to recommend for auto-allow, and which must never be auto-allowed.

## Decision Criteria

A command is safe to auto-allow if ALL of the following are true:

1. **Idempotent or read-only** — running it multiple times produces the same result, or it only reads
2. **No side effects outside the repo** — does not push to remote, send messages, or modify shared state
3. **Reversible** — any changes can be undone with `git checkout` or similar
4. **Approved 100% of the time** historically (no denials in session logs)
5. **Not in the denylist** below

## Allowlist Examples (safe to auto-allow)

| Pattern | Rationale |
|---|---|
| `Bash(pytest*)` | Read-only, local, idempotent |
| `Bash(mypy*)` | Read-only, analysis only |
| `Bash(ruff check*)` | Read-only, analysis only |
| `Bash(ruff format*)` | Local file change, reversible |
| `Bash(npm run test*)` | Local test runner |
| `Bash(php artisan test*)` | Local test runner |
| `Read(*)` | Always safe |
| `Glob(*)` | Always safe |
| `Grep(*)` | Always safe |

## Denylist (NEVER auto-allow)

These patterns must never be recommended for auto-allow regardless of historical approval rate:

| Pattern | Risk |
|---|---|
| `Bash(git push*)` | Pushes to remote — irreversible |
| `Bash(git push --force*)` | Destructive remote operation |
| `Bash(rm -rf*)` | Destructive file deletion |
| `Bash(curl * | bash*)` | Remote code execution |
| `Bash(wget * | sh*)` | Remote code execution |
| `Bash(npm publish*)` | Publishes to registry |
| `Bash(gh release*)` | Creates public release |
| `Bash(*production*)` | Targets production environment |
| `Bash(*deploy*)` | Deployment command |
| Any command with secrets/credentials | Credential leak risk |

## Confidence Threshold

Only recommend auto-allow for commands with:
- Approval rate = 100% (no denials)
- Frequency ≥ 5 (enough data)
- Confidence ≥ 0.90

Commands with 90-99% approval rate: recommend with a warning noting the denial cases.

## Output Format

When generating auto-allow recommendations, always include:

```json
{
  "rule": "Bash(pytest*)",
  "safe": true,
  "confidence": 0.99,
  "approval_rate": 1.0,
  "frequency": 52,
  "denylist_check": "passed",
  "warning": null
}
```

If the command is on the denylist, set `"safe": false` and include a `"warning"` explaining why.
