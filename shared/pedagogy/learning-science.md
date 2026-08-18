# Learning Science

The universal core of how people actually retain and build skill — shared by every teaching skill in this repo (`teach`, `Learn-course`). It is deliberately format-agnostic: it says *what* makes learning stick, not *how* a given skill delivers it (interactive HTML lessons, fill-in-the-blank exercises, whatever). Each skill applies these principles in its own medium; none of them should contradict what's here.

Grounded in Mollick & Mollick, *Using AI to Implement Effective Teaching Strategies* (SSRN 4391243) and the desirable-difficulty literature (Bjork).

## Fluency vs. storage strength

The distinction underneath everything.

- **Fluency strength** — in-the-moment recall. It produces an *illusion* of mastery: the learner nods, it all makes sense, and it's gone by Tuesday. Re-reading and worked examples build fluency.
- **Storage strength** — durable, long-term retention. This is the real goal, and it is built only by *desirable difficulty* — making the learner work to retrieve, not just recognise.

When a design choice trades short-term ease for long-term retention, take the retention. That is the whole game.

## Desirable difficulty — the three levers

1. **Retrieval practice.** Recalling from memory (not re-reading) is itself the act that strengthens memory. Every unit of teaching should make the learner *produce* the answer, not receive it.
2. **Spacing.** Distributing that retrieval over time — on an expanding schedule — beats massing it. This only works if something *schedules* the return; see `review-queue-format.md`.
3. **Interleaving.** Mixing related-but-different topics in practice (rather than blocking one topic until "done") builds flexible, transferable skill. Applies to skill practice more than to first-time knowledge acquisition.

A note on load: for **knowledge acquisition**, difficulty is the *enemy* — it eats the working memory needed to understand, so keep the load low while teaching something new. For **skill durability**, difficulty is the *tool*. Don't confuse the two phases.

## The five research-backed strategies

Treat these as a design checklist for any lesson, exercise, or explanation:

1. **Multiple examples for abstract concepts.** Several varied examples let the learner strip the idea from the surface details, which drives recall and transfer. One example teaches the example; many teach the concept.
2. **Varied explanations and analogies, aimed at the likely misconception.** Tune to the learner's prior knowledge and name the wrong mental model explicitly — the trap most learners fall into — rather than only stating the right one.
3. **Frequent low-stakes retrieval checks.** Build in questions that make the learner recall. Use a **hinge question** that *gates* progression: if they can't recall the load-bearing idea, don't move on. Keep answer options matched in length and register so formatting never leaks the answer.
4. **Gap diagnosis.** A wrong answer is data, not a failure. Read it for the misconception behind it and adapt what comes next. Record misconceptions so they steer future sessions.
5. **Distributed (spaced) practice.** Re-surface earlier material on an expanding schedule rather than teaching-and-moving-on. Retrieval + spacing are the two highest-evidence techniques in the whole literature.

## How the skills apply this

- **`teach`** — delivers retrieval checks as in-lesson quiz widgets (`quiz.js`), diagnoses gaps in conversation, and schedules spacing in each workspace's `review-queue.md`.
- **`Learn-course`** — delivers retrieval as runnable fill-in-the-blank exercises with real test execution, and (as of the shared-pedagogy adoption) schedules spacing in each course's `review-queue.md`, resurfacing earlier exercises before new lessons.

The medium differs; the science does not.
