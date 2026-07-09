---
name: understand-knowledge
description: Analyze a Markdown knowledge base and generate linked Markdown topic, entity, and source pages
argument-hint: [path]
---

# /understand-knowledge

Analyze a Markdown knowledge base and produce a linked Markdown knowledge map under `.knowledge-map/`.

## Instructions

1. Resolve the knowledge-base path from `$ARGUMENTS` or the current working directory.
2. Scan Markdown files for topics, entities, claims, sources, and recurring terms.
3. Write or update:
   - `.knowledge-map/README.md` — top-level topic navigation.
   - `.knowledge-map/topics/README.md` — topic clusters.
   - `.knowledge-map/entities/README.md` — entities and aliases.
   - `.knowledge-map/source/README.md` — source document index.
   - `.knowledge-map/decisions.md` — interpretation choices, uncertainties, and conflicts.
4. Use purposeful cross-links and cite original Markdown files.
5. Do not emit graph JSON; linked Markdown is the primary artifact.
