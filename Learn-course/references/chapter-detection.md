# Chapter detection

Step 2 of generate mode has two paths for deciding where the source splits into lesson-sized chunks. This file explains both, when each fires, and how to debug surprises.

## The two paths

### Smart path (default) — `references/chunking-prompt.md` + `scripts/apply_chunks.py`

A `general-purpose` subagent reads the line-numbered source and returns boundary line ranges. `apply_chunks.py` validates the ranges (contiguous, in-bounds, no gaps) and slices the **original file** byte-for-byte at those lines. The subagent never produces content — only decides where to cut.

The subagent is allowed to:

- Split a single H1 chapter into two lessons when it covers two distinct concepts.
- Fuse two adjacent H2 sections into one lesson when they form one topic with a worked example.
- Treat preamble before the first heading as its own chunk if it contains real content.
- Push a boundary slightly off a heading to avoid splitting a fenced code block, worked example, or exercise mid-flow.

### Deterministic path (fallback) — `scripts/chunk_markdown.py`

Pure regex. Tries this list of patterns in order; the first that yields 2+ chapter splits wins. If none match, falls back to size-based paragraph splitting.

1. `^Chapter\s+\d+[.:]\s*.+$` — "Chapter 1: Title"
2. `^#\s+.+$` — Markdown H1 (`# Title`)
3. `^Part\s+\d+[.:]\s*.+$` — "Part 1: Title"
4. `^Section\s+\d+[.:]\s*.+$` — "Section 1: Title"
5. `^\d+\.\s+[A-Z].+$` — "1. Numbered Section"
6. `^##\s+.+$` — Markdown H2 (fallback for docs that use H2 as top-level)

All patterns are line-anchored (multiline mode) and case-insensitive for the keyword forms. H1 is preferred over H2 — if a doc has both, H1 chapters are the right grain and H2s are subsections folded into the chapter body.

## When each path fires

- **Smart by default.** Step 2a always tries the subagent first.
- **Deterministic when:**
  - The user passes `--fast` (or equivalent).
  - The source is mostly machine-generated reference docs where headings already match topic boundaries cleanly (the smart pass adds latency without changing the result).
  - The smart subagent returned invalid JSON or `apply_chunks.py` exit-coded 2 twice in a row.
- **Hybrid for very large inputs.** Sources over ~150,000 characters get pre-split with the deterministic chunker first (so the smart subagent's context isn't overwhelmed), then the smart pass runs *within each pre-chunk*, and the results are merged.

## Size constants (deterministic path)

- `TARGET_CHUNK_SIZE = 16000` characters — preferred chunk size.
- A chunk larger than `1.5 × TARGET_CHUNK_SIZE` (24,000 chars) gets sub-split at paragraph boundaries (`\n{2,}`).

The source platform's `ChunkContentAction` had a `MIN_CHUNK_SIZE = 4000` that merged tiny chapters into the previous chunk to save backend LLM calls. This skill drops that merge: each detected chapter becomes its own chunk regardless of size. Preserving the source's chapter structure in the output course directory is worth the cost of one extra subagent call per small chapter.

## Size constants (smart path)

The chunker prompt asks the subagent to aim for **8,000–20,000 characters per chunk**, never over 30,000. These are guidelines the model follows, not enforced limits — `apply_chunks.py` will accept whatever ranges the subagent returns as long as they cover the file contiguously.

If you find the smart chunker consistently returning chunks that are too big or too small for your source domain, edit the size guidance in `references/chunking-prompt.md` rather than enforcing in `apply_chunks.py`. The model is better at respecting natural topic boundaries than at hitting precise character targets, and rejecting valid boundaries because they're 1KB too big would just push the work back to a regex.

## Debugging

### Smart path

- **Subagent returns invalid JSON.** It probably wrapped the answer in code fences or apologized. Retry once with a stricter "JSON only, no fences" reminder; after the second failure, fall through to deterministic.
- **Validation fails (`apply_chunks.py` exits 2).** Read stderr — it names the offending chunk. Common causes: subagent dropped the last line of the file (`prev_end != total_lines`), or skipped a region (`start_line {N} does not follow previous end_line {M} contiguously`). Both indicate the subagent miscounted; retry once with the same prompt, then fall through.
- **Boundaries are technically valid but lessons feel arbitrary.** The subagent is splitting where regex would, ignoring the semantic guidance. Re-read `references/chunking-prompt.md` and check whether the rules section is intact — point 3 ("split on semantic topic shifts, not just headings") is the one that matters most.

### Deterministic path

- **One chunk for the whole document.** No pattern matched twice. Either the source has no headings, or the headings use a form not in the list (e.g. `===` setext H1s — these are not handled). Convert the source's headings to ATX style (`# Title`) or add a pattern.
- **Way too many chunks.** A pattern that wasn't supposed to fire matched many lines. Most likely cause: a numbered list (`1. foo`, `2. bar`) at the top level of the document. The numbered-section pattern requires a capital letter after the digit-period-space, but list items often start with a capital. If this happens, comment out pattern #5 in `chunk_markdown.py`.
- **Chunk titles look wrong.** The detection captures the matched line as the chapter title. If your source uses long compound headings ("# Lesson 4: Variables — Part Two of Three"), the full line becomes the title. The scaffolder slugifies these into safe directory names.
