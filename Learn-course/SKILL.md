---
name: Learn-course
description: Convert a markdown source (textbook, lecture transcript, open-source library docs) into a directory-based learning course with chapters, lessons, and fill-in-the-blank coding exercises, then act as a terminal tutor that walks the learner through each lesson. Use this whenever the user wants to generate a course from a `.md` file, scaffold a hands-on curriculum from documentation, build practice problems out of a tutorial, or be coached lesson-by-lesson through a generated course directory. Trigger even when the user does not say "course" — phrases like "turn this into lessons", "make exercises from this book", "teach me from these docs", or "I want to learn this hands-on" all qualify.
---

# Learn-course

This skill has two modes:

- **Generate mode** — turn a `.md` file into a course directory.
- **Teach mode** — once a course exists, walk the learner through it interactively.

Pick the mode based on what the user is asking. If they hand you a `.md` and ask for a course / lessons / exercises, generate. If they're sitting inside a generated course directory (one with `_TEACHER.md` and `_meta.json` at the root) and ask to start, continue, or check work, teach.

## Generate mode

### Step 1 — Validate input and gather settings

1. Confirm the input `.md` path exists. If the user gave a relative path, resolve it.
2. Use `AskUserQuestion` to pick the **target programming language**: Python, JavaScript, TypeScript, Go, or Other. The language drives file extensions, the test runner, and starter-code idioms — the rest of the pipeline depends on it, so don't skip this even if the user named a language in passing. Confirm before moving on.
3. Default the output directory to `./<course-slug>/` in the user's CWD. The slug is the input filename minus extension, lowercased and dasherized. Mention the path in your reply so the user can override it.
4. **Optional companion repo.** If the user has a GitHub repo (or a local clone) that accompanies the source markdown — the canonical case is "this textbook has an example repo on GitHub" — accept it as `--repo <url-or-path>`. When set, lessons are grounded in real project idiom: starter code mirrors the repo's conventions, solutions can cite real files, and the lesson author has actual examples to learn from rather than imagining them. See Step 2.5 for the wiring. Skip this if no repo was provided — the md-only path remains the default and stays unchanged.

### Step 2 — Chunk the markdown (smart, with deterministic fallback)

The goal of chunking is to find lesson-sized units — ideally on **semantic topic shifts**, not just heading regex. Sometimes one H1 chapter actually covers two concepts that deserve separate lessons; sometimes two adjacent H2s are really one topic with a worked example after it. A regex pass can't tell. So by default, use a small subagent to decide boundaries, and fall back to the deterministic chunker if the subagent fails or the user asks for it.

#### 2a — Smart chunker (default)

1. Read the input `.md`. If it is over ~150,000 characters, the boundary subagent's context will get tight; pre-split with `scripts/chunk_markdown.py` first and run the smart chunker per pre-chunk, merging the results. Otherwise feed the whole file.
2. Prepend line numbers to every line of the input — the format `<NNNN>: <line>` (zero-padded width is fine). The subagent returns line ranges, so it needs a stable index. Save the line-numbered text to a temp file.
3. Spawn one `general-purpose` subagent with:
   - The full system prompt from `references/chunking-prompt.md` (read it verbatim — do not paraphrase).
   - The line-numbered text as the task input.
   - Instructions to return **JSON only** — no prose, no fences. The schema is `{"chunks": [{"title", "start_line", "end_line", "rationale"}, ...]}`.
4. Save the subagent's JSON to `/tmp/boundaries.json`, then slice the original file:
   ```bash
   python3 scripts/apply_chunks.py /path/to/input.md --boundaries /tmp/boundaries.json > /tmp/chunks.json
   ```
   `apply_chunks.py` validates the ranges (contiguous, in-bounds, no gaps) and slices the original file byte-for-byte at the line numbers — the LLM never gets to rewrite content, only to pick boundaries. If validation fails it exits with code 2.
5. **If the subagent returns invalid JSON, or if `apply_chunks.py` exits non-zero**, retry the subagent once with a stricter "JSON only, contiguous ranges, no gaps" reminder. After a second failure, fall through to 2b.

**Why boundaries-only and not full-content rewriting:** an LLM asked to "split this textbook" will quietly summarize, drop sentences, or rephrase code. By restricting the subagent to line ranges and slicing in Python, the source content is preserved exactly. The intelligence is spent on *where* to cut, not *what* to emit.

#### 2b — Deterministic fallback

Use this path when the user passes `--fast` (or equivalent), when the source is mostly machine-generated reference docs where headings already match topic boundaries cleanly, or when the smart path failed twice in 2a:

```bash
python3 scripts/chunk_markdown.py /path/to/input.md > /tmp/chunks.json
```

`chunk_markdown.py` splits by heading regex (H1/H2, `Chapter N`, `Part N`, etc.) into ~16KB chunks. Pure text processing, no LLM. See `references/chapter-detection.md` for the patterns and debugging tips.

#### Output shape

Both paths produce `/tmp/chunks.json` in the same shape: `{"chunks": [{"index": 0, "title": "...", "content": "...", "token_estimate": N}, ...]}`. Step 3 is agnostic to which chunker ran. If `chunks` is empty, the input file is empty or unreadable — surface the error and stop.

### Step 2.5 — Companion repo grounding (only if `--repo` was set)

Skip this entire step if the user did not pass `--repo` in Step 1. The md-only flow goes straight to Step 3.

When a repo is provided, this step builds a per-chunk file-relevance map so each lesson subagent in Step 3 receives the source chunk **plus** a small set of repo files that ground the lesson in real project idiom.

1. **Index the repo.** Run:
   ```bash
   python3 scripts/index_repo.py <url-or-path> --language <lang> > /tmp/repo_index.json
   ```
   `index_repo.py` clones via `gh repo clone` (or `git clone --depth 1`) into `/tmp/learn-course-repos/<owner>__<repo>/` if given a URL, or treats the argument as a local path. It walks the tree, skips `node_modules`/`vendor`/`build`/`.git`/etc., filters by extensions for the chosen language plus universal config/doc files (README, package.json, pyproject.toml, .md), and emits a JSON index with each file's path, size, line count, and first ~30 lines as a head preview. It caps at 500 files; oversize files (>200KB) and binaries are skipped with counts in `skipped`.
2. **Build a chunks summary.** For each chunk in `/tmp/chunks.json`, take `index`, `title`, and the first ~500 characters of `content` as a `summary`. This is what the matchmaker subagent will read — full chunk bodies would blow its context for no benefit. Save to `/tmp/chunks_summary.json`.
3. **Spawn the matchmaker subagent** (one subagent total — not per chunk). Pass:
   - The full system prompt from `references/repo-match-prompt.md` (read it verbatim).
   - The user message template, substituting `repo_root`, `language`, `tree`, `files_json` (from `/tmp/repo_index.json`), and `chunks_summary_json`.
   - Instructions to return **JSON only** matching `{"matches": [{"chunk_index", "files", "rationale"}, ...]}`.
4. **Validate.** The result must:
   - Have one entry per chunk (matchmaker may return them in any order).
   - Reference only paths that exist in the repo index — drop any that don't and log a warning. A small drift (1–2 invented paths) is recoverable; >20% invalid means retry the matchmaker once with a stricter "use only paths from the index" reminder, then if still bad, fall through to ungrounded mode (continue Step 3 with no reference files).
   - Cap at 5 files per chunk — if the matchmaker returns more, keep the first 5.
5. **Save** the validated map to `/tmp/repo_matches.json` keyed by `chunk_index`.

**Why a single matchmaker subagent and not per-chunk:** matching is a global decision — the matchmaker should be able to see all chunks at once to avoid assigning the same heavy core file to ten different chunks when only two of them really need it. One pass over the repo index is also cheaper than N independent passes.

**Why the matchmaker doesn't read full file contents:** the `head` preview from `index_repo.py` is enough to recognize what each file is about (its imports, its top-level declarations, its module docstring). Reading every file in full would mean the matchmaker's context contains the entire repo, which both costs tokens and crowds out the actual mapping task. The per-lesson subagent in Step 3 reads matched files in full — but only the small set the matchmaker selected.

### Step 3 — Generate lessons per chunk via subagents

For each chunk, spawn a `general-purpose` Agent subagent in parallel. Each subagent gets:

- The full system prompt from `references/lesson-prompt.md` (substitute `{language}` with the chosen language)
- The schema from `references/lesson-schema.md`
- The chunk's `content` and `title`
- **If `/tmp/repo_matches.json` exists** (Step 2.5 ran): for this chunk's `chunk_index`, read each matched file from the indexed repo root in full and inline them as a `REFERENCE FILES` block in the user message, formatted exactly as shown in `references/lesson-prompt.md`'s "USER MESSAGE TEMPLATE" section. If the matchmaker returned an empty list for this chunk, omit the block entirely — do not send an empty `REFERENCE FILES:` heading, since that confuses the model into hunting for files that aren't there.
- Instructions to return **JSON only** matching the schema — no prose, no markdown fences

**Why subagents instead of an inline Anthropic API call:** the user is already paying for this Claude Code session, the API key lives wherever Claude Code is configured, and large textbooks would otherwise blow main-thread context. Subagents do the chunk work in their own context windows and return only the validated JSON.

**Why each lesson subagent reads files from disk rather than getting them in the prompt as base64 or similar:** files often exceed the lesson chunk's own size, and inlining them in the message inflates token usage on every retry. Pasting the file contents inline (as the user-message block above) is the right call when matched files are small (≤8KB each, total under ~30KB); for chunks with larger matches, instruct the subagent to read files from `<repo_root>/<path>` itself and proceed.

Run them in parallel — issue all subagent calls in a single turn. If one returns invalid JSON, retry that single chunk once with a stricter "JSON only, no fences" instruction. After two failures, drop that chunk and continue (note it in the final summary).

Combine all returned `lessons` arrays in chunk order, renumbering `order` fields globally if needed. Save the combined JSON to `/tmp/course.json`.

### Step 4 — Scaffold the course directory

```bash
python3 scripts/scaffold_course.py /tmp/course.json <output-dir> --language <lang> --source <input.md>
```

The script reads templates from `assets/`, writes the directory tree, expands starter/test/solution code into language-correct files, and emits `_meta.json` (with `test_command`) and `_TEACHER.md`. Solutions go into `.solutions/` (dot-prefixed — the leading dot keeps them out of casual `ls` and out of grep-by-default).

### Step 5 — Summarize

Print:
- Course path
- Chapter / lesson / exercise counts
- The exact next command for the learner: `cd <course> && claude`, then "start lesson 1"

Don't dump the generated content into chat — point at the directory.

## Teach mode

When a user is inside a directory with `_TEACHER.md` and `_meta.json`, or says things like "start lesson 1", "check my exercise", "next exercise", "give me a hint" — read `references/teacher-loop.md` and follow it. The short version:

1. Read `_meta.json` and `.progress.json` (create the latter if missing).
2. Read the lesson `README.md` and present a **concise** summary in chat. The lesson is intentionally light on prose — most learning is in the exercises, so don't over-explain.
3. Point the learner at the current exercise's starter file and wait.
4. On "check": read the learner's file, **run the tests** with the runtime in `_meta.json.test_command`, and either confirm or give a hint. Read `.solutions/` privately to ground the hint, but don't show it unless the learner explicitly says "show me the answer".
5. Update `.progress.json` on pass.

## Files in this skill

- `references/lesson-prompt.md` — the LLM system prompt used in Step 3 of generate mode. Read every time you spawn a lesson subagent. Includes the optional repo-grounding section the model uses when reference files are provided.
- `references/lesson-schema.md` — the JSON schema each lesson subagent must conform to. Pass to the subagent verbatim.
- `references/chunking-prompt.md` — the LLM system prompt used in Step 2a (smart chunker). Read every time you spawn the boundary subagent.
- `references/chapter-detection.md` — explains both chunking paths (smart and deterministic), the regex patterns used by the fallback, and how to debug surprising chunk counts.
- `references/repo-match-prompt.md` — the LLM system prompt used in Step 2.5 (companion-repo matchmaker). Read it when wiring the matchmaker subagent.
- `references/teacher-loop.md` — the full teach-mode loop, including grading, hints, and progress tracking.
- `scripts/chunk_markdown.py` — deterministic regex chunker. Used as the fallback in Step 2b and as a pre-splitter for very large inputs.
- `scripts/apply_chunks.py` — validates LLM-returned line ranges and slices the source file at those lines. Used in Step 2a.
- `scripts/index_repo.py` — clones (or accepts a local path to) a companion repo and emits a filtered, head-previewed index for the matchmaker. Used in Step 2.5.
- `scripts/scaffold_course.py` — turns a combined JSON of lessons into the on-disk course tree.
- `assets/*.template.md` — markdown templates the scaffolder fills in.

## Design principles to preserve when editing

- **Heavy stubs, light prose.** Lessons are concise — 4–8 short paragraphs in the README. The cognitive load lives in 3–4 exercises per lesson, with rich header comments and multiple `# TODO:` markers in `starter_code`. If the LLM starts producing wall-of-text lessons with one trivial exercise, the prompt has drifted — fix `references/lesson-prompt.md`.
- **Hidden solutions.** `.solutions/` is private. Teach mode reads it to ground hints; it does not show it.
- **Real test execution.** Teach mode actually runs the tests with the local runtime, so feedback is grounded in real failures rather than Claude's read-only opinion. If the runtime is missing, say so and fall back to a code review.
- **One language per course.** Mixed-language courses muddy file extensions and test commands. If the user wants two languages, generate two courses.
