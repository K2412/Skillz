---
name: explain-this-like-I-am-an-intern
description: >
  User-invoked way to get clarity on anything — a subject you want to finally understand, or a
  message of mine that just didn't land. It re-explains from scratch as if to a bright intern on
  their first day: someone sharp but brand-new, who shares none of this thread's history and none
  of its jargon. It leads with the missing premise and the *why*, spells out every acronym and
  domain term on first use, drops to plain English and a concrete example — and *then* probes with
  a question or two, because a nod is not understanding and the point is that you hold it, not that
  it merely sounded clear. Reach for it with "/explain-this-like-I-am-an-intern", "eli-intern",
  "explain this like I'm an intern", "you lost me", "wait, what?", "I'm lost", "that didn't land",
  "back up", "break this down for me from scratch", "I want to actually understand X". User-invoked
  only — the agent never reaches for this on its own, because only you know when you stopped
  following.
disable-model-invocation: true
argument-hint: "What should I explain? (or nothing — I'll re-pitch whatever lost you)"
---

# explain-this-like-I-am-an-intern

You've asked to actually understand something — either a subject you named, or something I just
said that didn't land. Your one job now is to make it *click*, then check that it did.

The frame is **a bright intern on their first day**: sharp, capable, quick — but brand-new here.
They share none of this thread's history and none of its jargon. Explain to *them*. Then, because
a nod is cheap and understanding is not, ask them something back.

## 1. Find the real thing to explain

- **If they named a subject** ("break down how our auth flow works"), explain that — grounded in
  the actual sources (their codebase, the real docs), not your memory of how such things usually go.
- **If they just said "you lost me"**, don't re-pitch only your last sentence. Go back as far as
  the thread that lost them — the point where the premise stopped being visible — and re-pitch from
  *there*. Usually what's missing isn't the conclusion; it's the question you were answering and how
  you got here.

When unsure which, ask one short question before launching. A crisp "explain X" beats a fluent
answer to the wrong X.

## 2. Explain it — to the intern

- **Lead with the why and the premise they were missing.** What question is this answering? How did
  we get to a place where this matters? The conclusion comes *after* the setup, never instead of it.
- **Assume zero prior knowledge.** Spell out every acronym and tool the first time it appears.
  Define each domain term as you use it. If the project has a `CONTEXT.md` / glossary (or
  `CONTEXT-MAP.md` in a multi-context repo), still reach for its exact terms — but *gloss* each one
  the first time; don't assume the intern already holds it.
- **Plain English, ASD-STE100 style.** Short sentences. Common words. One idea per sentence.
- **Reach for a concrete example or a plain analogy before any abstraction.** Intuition lives in the
  concrete — small real inputs they can hold in their head beat a correct abstract definition. For a
  genuinely abstract idea, give *two* varied examples, so they strip the idea from the surface of any
  one case.
- **Name the trap.** Say the misconception a smart newcomer is *likely* to form here, and head it
  off — "you'd think X, but watch: …". The wrong guess they were about to make is the most useful
  thing to pre-empt.
- **Verify, don't confabulate.** The intern will believe you, which makes a confident wrong answer
  worse than a gap. On anything you'd otherwise state from memory — an API, a number, a name, how
  *their* code actually behaves — check the real source first and say so.
- **Shorter *and* clearer.** Add the premise back and define the terms, *and* cut the fog. Clarity
  isn't fewer words or more words; it's the right words with nothing assumed.

## 3. Then probe — check it landed

Explaining is half the job. The other half is finding out whether it actually stuck, and that only
happens when *they* produce something, not when they nod.

- After the explanation, ask **one or two** short questions that make them use the idea, not just
  echo it: "so what would break if we dropped this?", "given that, what would you expect X to do?",
  "where else have you seen this shape?". Aim just past what you just said — a small reach, not a
  quiz on the definition.
- **Don't validate to be nice.** If their answer is off, say so plainly and re-explain *the sticky
  part a different way* — a new analogy, smaller numbers, a different angle. The same explanation
  repeated louder rarely helps; a different one often does.
- **Stop when they've got it.** A grip they can put in their own words is the finish line. You're
  done — no ledger, no lesson file, no schedule. This is a quick clarity call, not a course.

## What this is not

Deliberately lightweight and stateless. It doesn't open a workspace, track reps, write a lesson, or
persist anything. One call, real understanding, move on. If they want the long-haul, multi-session,
build-lasting-mastery version, that's a different kind of engagement — this one is the fast
"wait, *actually*, help me get this" you reach for mid-flow.
