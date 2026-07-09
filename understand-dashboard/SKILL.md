---
name: understand-dashboard
description: Open or point to the root Markdown knowledge map for a codebase
argument-hint: [project-path]
---

# /understand-dashboard

This command now acts as a Markdown-map navigator.

## Instructions

1. Determine the project directory from `$ARGUMENTS`, otherwise use the current working directory.
2. Check for `.knowledge-map/README.md` in that directory.
3. If it is missing, tell the user: `No Markdown knowledge map found. Run /understand first to analyze this project.`
4. If it exists, report the path and, when possible in the current environment, open it with the default Markdown-capable app or file browser.
5. Point the user to these likely next pages:
   - `.knowledge-map/features/README.md`
   - `.knowledge-map/processes/README.md`
   - `.knowledge-map/source/README.md`
   - `.knowledge-map/entrypoints.md`
   - `.knowledge-map/decisions.md`
