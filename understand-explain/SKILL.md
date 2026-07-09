---
name: understand-explain
description: Use when you need a deep-dive explanation of a specific file, function, module, feature, or process using the Markdown knowledge map
argument-hint: [target]
---

# /understand-explain

Explain a target using `.knowledge-map/` plus source evidence.

## Instructions

1. Check for `.knowledge-map/README.md`; if absent, inspect source directly and recommend `/understand` for a durable map.
2. Search `.knowledge-map/` for `$ARGUMENTS`.
3. Read the best matching feature/process/source pages and their `Related`/`Evidence` links.
4. Read target source files when needed.
5. Explain:
   - What the target does
   - Where it fits in the feature/process map
   - Important dependencies and entrypoints
   - Risks, tradeoffs, and common modification points
6. Link to map pages and repo-relative source files.
7. If useful, write a focused explanation under `.knowledge-map/explain/concepts/<slug>/README.md`.
