---
name: understand
description: Analyze a codebase to produce a linked Markdown knowledge map for architecture, features, processes, and source modules
argument-hint: ["[path] [--full|--auto-update|--no-auto-update|--language <lang>]"]
---

# /understand

Analyze the current codebase and produce a linked Markdown knowledge map in `.knowledge-map/`.

The map is Markdown-first: no graph JSON, no visual map bundle, and no hidden prerequisite artifact.

## Output contract

Create or update:

- `.knowledge-map/README.md` — root navigation, project summary, important entrypoints, and reading paths.
- `.knowledge-map/features/README.md` — feature/process-facing index.
- `.knowledge-map/processes/README.md` — runtime flows, jobs, requests, commands, or data pipelines.
- `.knowledge-map/source/README.md` — source/module index grouped by layer or directory.
- `.knowledge-map/entrypoints.md` — public APIs, routes, CLIs, workers, app boot files, or integration points.
- `.knowledge-map/decisions.md` — architectural decisions, tradeoffs, risks, unknowns, and follow-up questions.
- `.knowledge-map/config.json` — at least `{ "autoUpdate": <boolean>, "outputLanguage": "<lang>" }` when options require it.
- `.knowledge-map/.knowledgeignore` — optional ignore file, same pattern style as `.gitignore`.

Use purposeful links only: related features, processes, source evidence, and decisions. Avoid dense wiki noise.

## Options

- `--full` — rebuild the Markdown map from scratch.
- `--auto-update` — set `autoUpdate: true` in `.knowledge-map/config.json`.
- `--no-auto-update` — set `autoUpdate: false` in `.knowledge-map/config.json`.
- `--language <lang>` — generate textual content in the requested language and persist it as `outputLanguage`.
- A directory path — analyze that directory instead of the current working directory.

## Workflow

1. Resolve `PROJECT_ROOT` from the optional path argument, otherwise use the current working directory.
2. If inside an ephemeral git worktree, prefer the main repository root unless explicitly told otherwise.
3. Create `.knowledge-map/` and `.knowledge-map/{features,processes,source}/`.
4. Create `.knowledge-map/.knowledgeignore` if missing. Seed it from built-in exclusions plus `.gitignore` suggestions, then ask the user to review before scanning if the project is large.
5. Gather evidence from:
   - README and docs.
   - package manifests and config files.
   - top-level directory tree.
   - common entrypoints for the project language/framework.
   - targeted source reads and searches.
   - git status and recent commits when useful.
6. Write the Markdown files listed in the output contract.
7. Every non-obvious claim should link to source evidence using repo-relative Markdown links.
8. End with a concise summary of files written and the best next reading path.

## Page style

- Start with what the reader can do with the page.
- Keep sections short and skimmable.
- Prefer tables for feature-to-source and process-to-step relationships.
- Each page should have a small `Related` section.
- Each feature/process page should include a small `Evidence` section with file links.
