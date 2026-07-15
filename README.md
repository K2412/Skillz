# skillz

A curated collection of agent skills — the source of truth for my Claude Code,
Codex, and OpenCode setup. Each skill is a directory with a `SKILL.md`.

## Install / sync

```bash
bash install.sh
```

`install.sh` treats `~/.agents/skills/` as the single source of truth and:

- copies every skill dir here into `~/.agents/skills/` (replacing prior copies so
  removed files don't linger),
- regenerates `~/.agents/AGENTS.md` and symlinks `~/.claude/CLAUDE.md` to it,
- symlinks each skill into `~/.claude/skills/` and `~/.codex/skills/` (dirs that
  don't exist are skipped),
- installs the orchestrator-only instruction modules to `~/.pi/agent/instructions/`.

OpenCode reads `~/.agents/skills/` natively. Override the source-of-truth location
with `AGENTS_HOME` if needed. Restart Claude Code / OpenCode afterward to pick up
changes.

## Skills

| Skill | Description |
|-------|-------------|
| **diagnosing-bugs** | Diagnosis loop for hard bugs and performance regressions. Triggers on "diagnose"/"debug this" or reports of something broken/throwing/failing/slow. |
| **find-skills** | Discover and install agent skills when you ask "how do I do X", "find a skill for X", or want to extend capabilities. |
| **Learn-course** | Turn a markdown source (textbook, transcript, docs) into a directory-based course with chapters, lessons, and fill-in-the-blank exercises, then tutor you through it lesson by lesson. |
| **pair** | Full spec-to-ship pipeline: grilling, plan review, subagent execution, and code review, pausing at every stage boundary for approval. Triggers on `/pair`, "pair with me", or describing a feature to build end-to-end. |
| **research** | Investigate a question against high-trust primary sources, web search, and Mobbin UI examples, then capture findings as a Markdown file in the repo. |
| **skill-creator** | Create, modify, and improve skills; run evals and benchmark skill performance; optimize a skill's description for better triggering. |
| **to-pr** | Turn an explain-diff explainer HTML file into a Markdown PR description and open a draft PR for the current branch (default base `dev`). Triggers on `/to-pr` or pointing at an explainer file and wanting it made into a PR. |

## Instruction modules (`instructions/`)

Orchestrator-only guidance installed to `~/.pi/agent/instructions/` (not registered
as standalone skills): `fortify-development`, `inertia-svelte-development`,
`laravel-best-practices`, `laravel-docs-lookup`, `pest-testing`,
`tailwindcss-development`, `wayfinder-development`.
