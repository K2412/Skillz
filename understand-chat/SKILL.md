---
name: understand-chat
description: Use when you need to ask questions about a codebase using the linked Markdown knowledge map
argument-hint: [query]
---

# /understand-chat

Answer questions about this codebase using `.knowledge-map/` Markdown files.

## Instructions

1. Check that `.knowledge-map/README.md` exists. If not, tell the user to run `/understand` first.
2. Read `.knowledge-map/README.md` for project context and navigation.
3. Search `.knowledge-map/` for the query terms from `$ARGUMENTS`.
4. Follow purposeful links from matched pages to related feature, process, source, entrypoint, and decision pages.
5. Read linked source files only when the map evidence is insufficient or the user asks for code-level detail.
6. Answer with Markdown links to map pages and repo-relative source files.
7. If the map has no useful match, say so and suggest the most relevant pages to inspect or ask the user to rerun `/understand --full`.
