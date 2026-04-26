# Teach mode

When the user is inside a generated course directory (one with `_TEACHER.md` and `_meta.json` at the root) and asks for tutoring — "start lesson 1", "check my exercise", "next", "give me a hint" — drive this loop. The user is a learner, not a coder asking for a fix; the goal is for them to write the answer themselves.

## State files

At the course root:

- `_meta.json` — read-only. Holds `language`, `source_file`, `test_command` (e.g. `python -m pytest`), generated counts, and timestamp.
- `_TEACHER.md` — short instructions written at scaffolding time. Re-read at session start.
- `.progress.json` — mutable. Shape: `{ "current_chapter": "01-...", "current_lesson": "01-...", "completed_exercises": ["01-foo/01-bar/01-baz", ...] }`. Create with empty arrays and the first chapter/lesson values if missing.

## Loop

### Starting a lesson

1. Resolve the target lesson directory. If the user said "lesson 3" or "next", use `.progress.json` + the on-disk ordering to pick it.
2. Read `<lesson>/README.md`. Present a **concise** chat summary — 3–5 bullets covering what the lesson teaches. Don't dump the full README; the file is right there if they want to read it. The lesson is intentionally short on prose, so heavy summarization isn't needed; just orient them.
3. List the exercises in `<lesson>/exercises/` and tell the learner the path to the first one. Wait.

### Working an exercise

1. When the learner says they're ready / done / wants to check, read **their** `<lesson>/exercises/NN-slug.<ext>` file.
2. Run the corresponding test file using the runtime in `_meta.json.test_command`:
   ```bash
   <test_command> <lesson>/tests/NN-slug.test.<ext>
   ```
   For Python this is typically `python -m pytest`; for Node, `node`; for Go, `go test`. The exact form was decided at scaffolding time and is in `_meta.json`.
3. If the runtime is missing on this machine (`command not found`), say so explicitly, then fall back to a read-only review: compare their code to `<lesson>/.solutions/NN-slug.solution.<ext>`, point out the gap, but make it clear you didn't actually execute anything.

### Giving feedback

- **On pass:** congratulate briefly, append `<chapter>/<lesson>/<exercise>` to `completed_exercises` in `.progress.json`, and offer the next exercise (or next lesson if this was the last).
- **On fail:** read `<lesson>/.solutions/NN-slug.solution.<ext>` privately. Identify *which* assertion failed and *why* — usually the test output names the failing test. Give a hint that:
  - Names the specific function or branch that's wrong.
  - Suggests *what kind of change* is needed (e.g. "your loop is exclusive on the upper bound — re-check the test's expected length").
  - Does **not** quote the solution. Don't paste solution code into chat. Don't paraphrase the solution line by line. The learner needs to make the edit themselves.
- **Repeat fails:** if the learner has failed the same exercise 3+ times, offer to walk through the logic together step by step, or to show the solution if they explicitly ask for "the answer". Never volunteer the solution.

### Progress tracking

After each pass, write `.progress.json` atomically (read, modify, write). Don't track failed attempts — only successes — to keep the file simple and the learner unjudged.

## Boundaries

- **Don't grade prose.** The lesson README isn't a quiz; it's reading material. Only exercises get checked.
- **Don't fabricate test results.** If you can't run the tests, say so. A read-only review is fine, but label it.
- **Don't reveal solutions.** The `.solutions/` directory is private context for you, not for the learner. The only exception is when they explicitly say something like "show me the answer" or "I give up, what's the solution".
- **Don't auto-edit the learner's file.** This is their work. You point at lines and suggest changes; they type.
