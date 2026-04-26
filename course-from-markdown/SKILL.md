---
name: course-from-markdown
description: Convert a markdown source (textbook, lecture transcript, open-source library docs) into a directory-based learning course with chapters, lessons, and fill-in-the-blank coding exercises, then act as a terminal tutor that walks the learner through each lesson. Use this whenever the user wants to generate a course from a `.md` file, scaffold a hands-on curriculum from documentation, build practice problems out of a tutorial, or be coached lesson-by-lesson through a generated course directory. Trigger even when the user does not say "course" — phrases like "turn this into lessons", "make exercises from this book", "teach me from these docs", or "I want to learn this hands-on" all qualify.
---

# course-from-markdown

This skill has two modes:

- **Generate mode** — turn a `.md` file into a course directory.
- **Teach mode** — once a course exists, walk the learner through it interactively.

Pick the mode based on what the user is asking. If they hand you a `.md` and ask for a course / lessons / exercises, generate. If they're sitting inside a generated course directory (one with `_TEACHER.md` and `_meta.json` at the root) and ask to start, continue, or check work, teach.

## Generate mode

### Step 1 — Validate input and gather settings

1. Confirm the input `.md` path exists. If the user gave a relative path, resolve it.
2. Use `AskUserQuestion` to pick the **target programming language**: Python, JavaScript, TypeScript, Go, or Other. The language drives file extensions, the test runner, and starter-code idioms — the rest of the pipeline depends on it, so don't skip this even if the user named a language in passing. Confirm before moving on.
3. Default the output directory to `./<course-slug>/` in the user's CWD. The slug is the input filename minus extension, lowercased and dasherized. Mention the path in your reply so the user can override it.

### Step 2 — Chunk the markdown deterministically

Run `scripts/chunk_markdown.py` with the input path. It splits the source by chapter (H1/H2 headings, `Chapter N`, `Part N`, etc.) into ~16KB chunks and prints JSON to stdout. No LLM call here — this is pure text processing, and it's important the same input produces the same chunks every time.

```bash
python3 scripts/chunk_markdown.py /path/to/input.md > /tmp/chunks.json
```

The JSON shape is `{"chunks": [{"index": 0, "title": "...", "content": "..."}, ...]}`. If the script returns zero chunks, the input file is empty or unreadable — surface the error and stop.

### Step 3 — Generate lessons per chunk via subagents

For each chunk, spawn a `general-purpose` Agent subagent in parallel. Each subagent gets:

- The full system prompt from `references/lesson-prompt.md` (substitute `{language}` with the chosen language)
- The schema from `references/lesson-schema.md`
- The chunk's `content` and `title`
- Instructions to return **JSON only** matching the schema — no prose, no markdown fences

**Why subagents instead of an inline Anthropic API call:** the user is already paying for this Claude Code session, the API key lives wherever Claude Code is configured, and large textbooks would otherwise blow main-thread context. Subagents do the chunk work in their own context windows and return only the validated JSON.

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

- `references/lesson-prompt.md` — the LLM system prompt used in Step 3 of generate mode. Read every time you spawn a subagent.
- `references/lesson-schema.md` — the JSON schema each subagent must conform to. Pass to the subagent verbatim.
- `references/chapter-detection.md` — explanation of how `chunk_markdown.py` detects chapters; consult if chunking returns surprising results.
- `references/teacher-loop.md` — the full teach-mode loop, including grading, hints, and progress tracking.
- `scripts/chunk_markdown.py` — deterministic markdown chunker (port of the source platform's `ChunkContentAction`).
- `scripts/scaffold_course.py` — turns a combined JSON of lessons into the on-disk course tree.
- `assets/*.template.md` — markdown templates the scaffolder fills in.

## Design principles to preserve when editing

- **Heavy stubs, light prose.** Lessons are concise — 4–8 short paragraphs in the README. The cognitive load lives in 3–4 exercises per lesson, with rich header comments and multiple `# TODO:` markers in `starter_code`. If the LLM starts producing wall-of-text lessons with one trivial exercise, the prompt has drifted — fix `references/lesson-prompt.md`.
- **Hidden solutions.** `.solutions/` is private. Teach mode reads it to ground hints; it does not show it.
- **Real test execution.** Teach mode actually runs the tests with the local runtime, so feedback is grounded in real failures rather than Claude's read-only opinion. If the runtime is missing, say so and fall back to a code review.
- **One language per course.** Mixed-language courses muddy file extensions and test commands. If the user wants two languages, generate two courses.
