---
name: understand-diff
description: Analyze git diffs or pull requests against the linked Markdown knowledge map to explain changes, affected components, and risks
---

# /understand-diff

Analyze current code changes using git, source files, and `.knowledge-map/` Markdown.

## Instructions

1. Check for `.knowledge-map/README.md`. If missing, continue from git/source directly but recommend running `/understand` afterward.
2. Determine changed files:
   - uncommitted work: `git diff --name-only`
   - branch work: `git diff main...HEAD --name-only` or user-specified base
   - PR: use the PR diff if available
3. Read relevant map indexes: root, features, processes, source, entrypoints, and decisions.
4. Match changed files to map pages by source links and feature/process descriptions.
5. Read changed files and nearby callers/importers where needed.
6. Report:
   - Changed components
   - Affected features/processes
   - Affected source modules
   - Risks and review focus
   - Suggested tests or manual checks
7. Optionally write a focused diff map under `.knowledge-map/explain/diffs/<base>-to-<head>/README.md` with supporting pages.
