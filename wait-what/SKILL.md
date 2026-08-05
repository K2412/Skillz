---
name: wait-what
description: >
  User-invoked corrective for when a message didn't land — you type it the moment you notice
  you're skimming, lost in invented jargon, or reading a decision whose premise you never saw.
  The agent re-pitches its last message: adds the missing context, drops to plain English, and
  reaches for the project's own vocabulary. Triggers on "/wait-what", "wait, what?", "you lost
  me", "I'm lost", "that didn't land", "re-pitch that", "back up". User-invoked only — the agent
  never reaches for this on its own, because only you know when you stopped following.
disable-model-invocation: true
---

Wait — I don't understand where you've got to here. Re-pitch **that** (not just the last sentence —
go back as far as the thread that lost me): give me the context I was missing, write in ASD-STE100
Simplified Technical English, and use the ubiquitous language from `CONTEXT.md` (and `CONTEXT-MAP.md`
if this is a multi-context repo). Shorter **and** clearer — add the premise back, don't just delete words.
