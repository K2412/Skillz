---
name: understand-domain
description: Extract business domain knowledge from a codebase and generate linked Markdown domain and process pages
argument-hint: [path]
---

# /understand-domain

Extract business/domain concepts into `.knowledge-map/` Markdown.

## Instructions

1. Resolve the project path from `$ARGUMENTS` or the current working directory.
2. Read existing `.knowledge-map/README.md` when present; otherwise gather evidence from README, docs, manifests, routes, models, services, schemas, tests, and source search.
3. Write or update:
   - `.knowledge-map/domain/README.md` — domain terms and bounded contexts.
   - `.knowledge-map/domain/entities.md` — entities, attributes, lifecycle notes, and source evidence.
   - `.knowledge-map/processes/README.md` — domain flows with links to feature and source pages.
4. Link domain pages back to `.knowledge-map/features/README.md`, `.knowledge-map/source/README.md`, and source files.
5. Do not create graph JSON. The durable output is linked Markdown.
