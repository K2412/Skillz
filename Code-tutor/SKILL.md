---
name: Code-tutor
description: Generate a beginner-friendly Markdown tutorial from any local codebase or GitHub repository. Combines structural abstraction mapping with git-grounded history investigation to explain both what the code does and why it was built that way. Use when the user wants to understand, document, or onboard to a codebase. Triggers: "generate tutorial", "explain this codebase", "create docs for", "run codebase-tutor", "/codebase-tutor", "analyse this repo", "onboard to", "understand the code in", "where does X live", "why was X built this way", "navigate this repo".
---

# Code-tutor

Generates a multi-chapter Markdown tutorial that explains a codebase from first principles — identifying core abstractions, their relationships, and writing each chapter as if explaining to a beginner. Enriches every chapter with git-grounded context so readers understand not just *what* the code does but *why* it was built that way.

## Workflow

### Phase 1: Git Investigation Pre-Pass

Before running the pipeline, conduct a read-only git investigation to build evolutionary context:

- Use `git log --oneline --follow <file>` and `git log --stat` to identify which modules have changed most
- Use `git blame` and `git show <hash>` to surface the rationale behind key decisions
- Use `rg` for cross-cutting pattern discovery
- Every substantive claim must be backed by evidence (file references + commit hashes when relevant)
- If evidence is incomplete, note the uncertainty explicitly — do not invent rationale

Save findings as a structured `git-context.md` summary covering:
- Key architectural decisions and the commits/PRs that introduced them
- Modules with significant churn (likely pain points or active areas)
- Patterns that evolved over time (e.g. a refactor from X to Y)

### Phase 2: Ask the user for pipeline inputs

Collect:
- Source: local directory path (`--dir`) OR GitHub URL (`--repo`)
- Project name (optional — auto-derived if omitted)
- Any custom include/exclude patterns (optional)
- Number of abstractions / chapters (default: 10)

Confirm the assembled command before running.

### Phase 3: Run the pipeline

```bash
bash /Users/kevinkab/.agents/skills/Code-tutor/scripts/run.sh \
  --dir <path> \
  --name <name> \
  [--include "*.py" --include "*.ts"] \
  [--exclude "**/node_modules/**"] \
  [--max-abstractions 10]
```

### Phase 4: Append "Evolution & Design Decisions" chapter

After the pipeline completes, Claude authors an additional chapter using the `git-context.md` from Phase 1. This chapter covers:

- Why the core abstractions exist (not just what they do)
- How the architecture evolved and what drove changes
- Areas of high churn and what that signals
- Key decisions that shaped the current design

Append this chapter to the pipeline output directory as `evolution-and-design-decisions.md`.

### Phase 5: Report

List all generated files and their locations, including the appended chapter.

## Operating Rules

- Default to read-only investigation in Phase 1
- Do not run destructive or state-changing git commands
- Every claim in the Evolution chapter must cite a file or commit hash
- For GitHub repos, set `GITHUB_TOKEN` in `.env` or pass `--token`

## Important Notes

- The pipeline makes multiple LLM calls (one per chapter + overhead). Expect 5–20 minutes for large repos.
- Rate limits may trigger automatic retries with backoff — this is normal.
- Output goes to `./output/<name>/` relative to the skill project directory.
- See [references/options.md](references/options.md) for all pipeline options.
- See [references/command-catalog.md](references/command-catalog.md) for approved git investigation commands.

## Example Commands

Local directory:
```bash
bash scripts/run.sh --dir /path/to/project --name my-project
```

GitHub repo:
```bash
bash scripts/run.sh --repo https://github.com/owner/repo --name repo-name
```

With file filtering:
```bash
bash scripts/run.sh \
  --dir /path/to/project \
  --name my-project \
  --include "*.py" --include "*.ts" --include "*.sql" \
  --exclude "**/node_modules/**" --exclude "**/.venv/**" \
  --max-abstractions 8
```
