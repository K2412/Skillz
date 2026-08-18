# review-queue.md Format

`review-queue.md` is the spaced-repetition schedule for a body of learning (a `teach` mission or a `Learn-course` course). It exists because the two highest-evidence learning techniques — **retrieval practice** (recalling from memory) and **spacing** (distributing that recall over time) — only work if something _schedules_ the re-surfacing. Fluency fades; a scheduled return is what converts it into durable storage strength.

This file is the single reason a stateful teacher beats a stateless one: at the **start of every session**, before teaching anything new, you check it for items that are due and open a session with a quick retrieval check on them.

It lives at the root of the workspace / course directory, alongside the other state files. Create it lazily — the first time an item earns a review.

## Structure

A table, most-due first:

```md
# Review Queue

| Due        | Item                          | Last seen  | Interval | Notes |
|------------|-------------------------------|------------|----------|-------|
| 2026-08-24 | White cross (LR-0002)         | 2026-08-17 | 7d       | shaky on edge orientation |
| 2026-09-01 | F2L notation (GLOSSARY: F, U) | 2026-08-18 | 14d      | solid |
```

- **Item** names what to recall and links to where it's defined (a learning record, a glossary term, a lesson, or — in `Learn-course` — the exercise that proved it). Recall the _idea_, not "re-read lesson 3."
- **Interval** is the current spacing gap. On a successful recall, roughly double it (1d → 3d → 7d → 14d → 30d → 90d). On a failed or shaky recall, drop it back to the previous rung — the item wasn't as solid as it looked.
- **Due** = last seen + interval. Recompute when you update the row.

## Rules

- **Add an item when the learner demonstrates it** — passes the exercise, or recalls the concept correctly. This is alongside (not instead of) whatever else records the win (a learning record in `teach`, `completed_exercises` in `Learn-course`). Those say _that_ they learned it; the queue schedules _keeping_ it.
- **Expanding intervals, not fixed.** The point of spacing is that each successful recall earns a longer gap. Fixed daily review wastes effort on solid material and is not what the evidence supports.
- **Interleave when you can.** When several items are due, mix related ones in the same check rather than blocking them one-topic-at-a-time — interleaving builds flexible, transferable skill (for skills practice; less so for first-time knowledge).
- **A due review outranks new material.** If items are due, run them first. Re-teaching from scratch later costs far more than a 60-second recall now.
- **Retire mastered items.** Once something survives the 90d rung cleanly, it can graduate out of the queue. Note it and drop the row.
