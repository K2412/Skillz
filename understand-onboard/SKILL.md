---
name: understand-onboard
description: Generate an onboarding guide from the linked Markdown knowledge map and source evidence
argument-hint: [path]
---

# /understand-onboard

Create onboarding material from `.knowledge-map/` Markdown.

## Instructions

1. Resolve the project path from `$ARGUMENTS` or the current working directory.
2. If `.knowledge-map/README.md` is missing, recommend running `/understand`; continue with README/source inspection if the user wants a quick guide.
3. Read root, features, processes, source, entrypoints, and decisions pages.
4. Write or update `.knowledge-map/onboarding/README.md` with:
   - project overview
   - first-day reading path
   - core features/processes
   - source modules to inspect first
   - setup/test commands from evidence
   - safe starter tasks
   - glossary and risks
5. Link back to map pages and repo-relative source files.
