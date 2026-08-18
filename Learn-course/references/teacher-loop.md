# Teach mode

When the user is inside a generated course directory (one with `_TEACHER.md` and `_meta.json` at the root) and asks for tutoring — "start lesson 1", "check my exercise", "next", "give me a hint" — drive this loop. The user is a learner, not a coder asking for a fix; the goal is for them to write the answer themselves.

## State files

At the course root:

- `_meta.json` — read-only. Holds `language`, `source_file`, `test_command` (e.g. `python -m pytest`), generated counts, and timestamp.
- `_TEACHER.md` — short instructions written at scaffolding time. Re-read at session start.
- `.progress.json` — mutable. Shape: `{ "current_chapter": "01-...", "current_lesson": "01-...", "completed_exercises": ["01-foo/01-bar/01-baz", ...] }`. Create with empty arrays and the first chapter/lesson values if missing.
- `review-queue.md` — mutable, created lazily. The spaced-repetition schedule: which earlier ideas are due to be recalled, and when. This is the one thing a static course can't do on its own, and it's where most retention is won or lost — passing an exercise once builds *fluency*, but only scheduled re-recall builds *storage strength*. Format and expanding-interval logic: `references/pedagogy/review-queue-format.md` (shared with the `teach` skill). If the file is absent, treat it as an empty queue.

## Loop

### Opening a session — run due reviews first

Before starting or resuming a lesson, read `review-queue.md` (if it exists) and check for items whose **Due** date is today or earlier. If any are due, run them *before* new material:

1. Pick the due item(s) and ask the learner to recall the idea from memory — not "re-read lesson 3", but "without looking, what does `R' D' R D` actually do to a corner?" Interleave related due items into one quick check rather than marching through them singly.
2. Judge the recall with them. On a clean recall, advance that item's interval (roughly double it: 1d → 3d → 7d → 14d → 30d → 90d) and recompute its Due date. On a shaky or failed recall, drop it back a rung and, if it's genuinely gone, point them at the lesson to re-read. Update the row per `references/pedagogy/review-queue-format.md`.
3. Then continue to the lesson.

This is short by design — a 60-second recall, not a re-teach. Skip silently when nothing is due; don't manufacture reviews.

### Starting a lesson

1. Resolve the target lesson directory. If the user said "lesson 3" or "next", use `.progress.json` + the on-disk ordering to pick it.
2. Read `<lesson>/README.md`. Present a **concise** chat summary — 3–5 bullets covering what the lesson teaches. Don't dump the full README; the file is right there if they want to read it. The lesson is intentionally short on prose, so heavy summarization isn't needed; just orient them.
3. If `<lesson>/animation.html` exists, `open` it and tell the learner to step through it (← →, one beat per keypress) **before** the first exercise. The walk is how they see the runtime take turns; the exercises are how they prove they can write it. If the file is absent, skip this — not every lesson needs a walk.
4. List the exercises in `<lesson>/exercises/` and tell the learner the path to the first one. Wait.

### Working an exercise

1. When the learner says they're ready / done / wants to check, read **their** `<lesson>/exercises/NN-slug.<ext>` file.
2. Run the corresponding test file using the runtime in `_meta.json.test_command`:
   ```bash
   <test_command> <lesson>/tests/NN-slug.test.<ext>
   ```
   For Python this is typically `python -m pytest`; for Node, `node`; for Go, `go test`. The exact form was decided at scaffolding time and is in `_meta.json`.
3. If the runtime is missing on this machine (`command not found`), say so explicitly, then fall back to a read-only review: compare their code to `<lesson>/.solutions/NN-slug.solution.<ext>`, point out the gap, but make it clear you didn't actually execute anything.

### Giving feedback

After every check (pass or fail) the learner has to decide what to do next. Use `AskUserQuestion` so they pick from buttons instead of typing — this keeps the loop fast.

- **On pass:** congratulate briefly, append `<chapter>/<lesson>/<exercise>` to `completed_exercises` in `.progress.json`, **and schedule a spaced review**: add a row to `review-queue.md` naming the *idea* the exercise proved (not the file path) with the first-rung interval (3d) and a Due date 3 days out. Passing once is fluency; the scheduled recall is what makes it stick. Then ask via `AskUserQuestion` (header "Next", `multiSelect: false`):
  - "Next exercise" — first, "(Recommended)". If this was the final exercise in the lesson, replace with "Next lesson".
  - "Do a quick review (N due)" — include this option *only* when `review-queue.md` has items due today or earlier, and make it the recommended one when 3+ are due (a backlog of due recalls matters more than new ground).
  - "Re-read the lesson README".
  - "Stop here for now".

- **On fail:** read `<lesson>/.solutions/NN-slug.solution.<ext>` privately. Identify *which* assertion failed and *why* — usually the test output names the failing test. Give a hint that:
  - Names the specific function or branch that's wrong.
  - Suggests *what kind of change* is needed (e.g. "your loop is exclusive on the upper bound — re-check the test's expected length").
  - Does **not** quote the solution. Don't paste solution code into chat. Don't paraphrase the solution line by line. The learner needs to make the edit themselves.

  Then ask via `AskUserQuestion` (header "What now", `multiSelect: false`):
  - "I'll try again" — first, "(Recommended)".
  - "Give me another hint".
  - "Walk me through it step by step" — only include after 2+ failures on this exercise.
  - "Show the solution" — only include after 3+ failures, and never as the recommended option.

- **Repeat fails:** the on-fail `AskUserQuestion` already escalates as failure count grows — that's how "walk through" and "show solution" become available. Never volunteer the solution as the default choice.

### Progress tracking

After each pass, write `.progress.json` atomically (read, modify, write). Don't track failed attempts — only successes — to keep the file simple and the learner unjudged.

`review-queue.md` is the other stateful file, and it's edited in two places: appended on a pass (new item, 3d rung), and updated when a due item is recalled at session open (interval advances on success, drops a rung on a miss). It's a plain markdown table — edit it in place. See `references/pedagogy/review-queue-format.md`.

## Boundaries

- **Don't grade prose.** The lesson README isn't a quiz; it's reading material. Only exercises get checked.
- **Don't fabricate test results.** If you can't run the tests, say so. A read-only review is fine, but label it.
- **Don't reveal solutions.** The `.solutions/` directory is private context for you, not for the learner. The only exception is when they explicitly say something like "show me the answer" or "I give up, what's the solution".
- **Don't auto-edit the learner's file.** This is their work. You point at lines and suggest changes; they type.
