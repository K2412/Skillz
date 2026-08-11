---
name: wait-what
description: >
  User-invoked corrective for when a message didn't land — you type it the moment you notice
  you're skimming, lost in invented jargon, or reading a decision whose premise you never saw.
  The agent re-pitches its last message as if explaining to a bright intern on their first day:
  it assumes no shared history, adds the missing context and the why, drops to plain English,
  and spells out every acronym and domain term on first use. Triggers on "/wait-what", "wait,
  what?", "you lost me", "I'm lost", "that didn't land", "re-pitch that", "back up", "explain
  like I'm new". User-invoked only — the agent never reaches for this on its own, because only
  you know when you stopped following.
disable-model-invocation: true
---

Wait — I don't understand where you've got to here. Re-pitch **that** (not just the last sentence —
go back as far as the thread that lost me) **as if you're explaining it to a bright intern on their
first day**: someone sharp but brand-new, who shares none of this thread's history and none of the
jargon.

- **Lead with the why and the premise I was missing** — what question we were answering and how we
  got here, not just the conclusion you landed on.
- **Assume zero prior knowledge of this work.** Spell out every acronym and tool the first time it
  appears, and define each domain term as you use it. Still reach for the ubiquitous language from
  `CONTEXT.md` (and `CONTEXT-MAP.md` in a multi-context repo) — but *gloss* each term, don't assume
  I already hold it.
- **Write in ASD-STE100 Simplified Technical English**, and prefer a concrete example or a plain
  analogy over an abstraction.
- Shorter **and** clearer — add the premise back and define the terms; don't just delete words.
