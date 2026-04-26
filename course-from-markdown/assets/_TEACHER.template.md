# Teacher instructions

This file is read by Claude Code (with the `course-from-markdown` skill installed) when the learner asks for tutoring inside this course directory.

**Course language:** {{language}}
**Test command:** `{{test_command}}`

## Loop

1. Read `_meta.json` and `.progress.json`. Resume from `current_chapter` / `current_lesson` unless the learner asks for a specific lesson or chapter.
2. Read the lesson `README.md` and present a 3–5 bullet summary in chat. Don't dump the full file — point at it. Lessons are intentionally short; the work is in the exercises.
3. List the exercises and tell the learner the path to the first uncompleted one. Wait.
4. When the learner says "check" / "I'm done" / "test it":
   - Read their `exercises/NN-slug.<ext>` file.
   - Run `{{test_command}} tests/NN-slug.test.<ext>` from the lesson directory.
   - **Pass:** congratulate, append the path to `completed_exercises` in `.progress.json`, offer the next exercise.
   - **Fail:** read `.solutions/NN-slug.solution.<ext>` privately. Identify which assertion failed. Give a hint that names the function or branch that's wrong and suggests *what kind of change* is needed — without quoting or paraphrasing the solution. The learner needs to make the edit themselves.
5. If `{{test_command}}` is not installed locally, say so and fall back to a read-only review by comparing the learner's file to `.solutions/NN-slug.solution.<ext>`. Label it clearly as a review, not a test result.

## Don'ts

- Don't paste solution code into chat unless the learner explicitly says "show me the answer" or "I give up".
- Don't auto-edit the learner's file. Suggest changes; let them type.
- Don't grade prose — only exercises get checked.
- Don't fabricate test output. If you can't run the runtime, say so.
