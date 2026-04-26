# Chapter detection

`scripts/chunk_markdown.py` decides where to split the input by trying a list of heading patterns in order. The first pattern that produces 2+ matches wins; if none match, the script falls back to size-based splitting at paragraph boundaries.

This file documents what the patterns are so you can debug surprises (one giant chunk, or fifty tiny chunks).

## Patterns, in order

1. `^Chapter\s+\d+[.:]\s*.+$` — "Chapter 1: Title"
2. `^#\s+.+$` — Markdown H1 (`# Title`)
3. `^Part\s+\d+[.:]\s*.+$` — "Part 1: Title"
4. `^Section\s+\d+[.:]\s*.+$` — "Section 1: Title"
5. `^\d+\.\s+[A-Z].+$` — "1. Numbered Section"
6. `^##\s+.+$` — Markdown H2 (fallback for docs that use H2 as top-level)

All patterns are line-anchored (multiline mode) and case-insensitive for the keyword forms. H1 is preferred over H2 — if a doc has both, H1 chapters are the right grain and H2s are subsections folded into the chapter body. Falling through to H2 only happens when no H1 split worked.

## Size constants

- `TARGET_CHUNK_SIZE = 16000` characters — preferred chunk size.
- A chunk larger than `1.5 × TARGET_CHUNK_SIZE` (24,000 chars) gets sub-split at paragraph boundaries (`\n{2,}`).

The source platform's `ChunkContentAction` had a `MIN_CHUNK_SIZE = 4000` that merged tiny chapters into the previous chunk to save backend LLM calls. This skill drops that merge: each detected chapter becomes its own chunk regardless of size. Preserving the source's chapter structure in the output course directory is worth the cost of one extra subagent call per small chapter.

## Debugging

- **One chunk for the whole document.** No pattern matched twice. Either the source has no headings, or the headings use a form not in the list (e.g. `===` setext H1s — these are not handled). Convert the source's headings to ATX style (`# Title`) or add a pattern.
- **Way too many chunks.** A pattern that wasn't supposed to fire matched many lines. Most likely cause: a numbered list (`1. foo`, `2. bar`) at the top level of the document. The numbered-section pattern requires a capital letter after the digit-period-space, but list items often start with a capital. If this happens, comment out pattern #3 in `chunk_markdown.py`.
- **Chunk titles look wrong.** The detection captures the matched line as the chapter title. If your source uses long compound headings ("# Lesson 4: Variables — Part Two of Three"), the full line becomes the title. The scaffolder slugifies these into safe directory names.
