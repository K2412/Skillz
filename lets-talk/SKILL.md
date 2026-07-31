---
name: lets-talk
description: Think a decision, tradeoff, or open question through *with* the user in conversation — grounded in the real artifacts, opinionated, and deliberately producing understanding and a recommendation rather than code or files. Use whenever the user wants to reason rather than build: "let's talk about…", "I want to discuss…", "what do you think about…", "should we X or Y?", "help me think through…", "evaluate our current X against Y", "is it worth doing Z?", "I'm torn between…", "poke holes in this idea", or any strategic/architectural/design dilemma posed for deliberation. This is the anti-pair and the third bookend of the understanding loop — explain-diff for a change, research for a topic, lets-talk for a *decision*. Do NOT use it when the user wants something built, fixed, implemented, or executed — that's /pair, /prototype, or just doing the task. If a request is really an action dressed as a question, drop this and act.
---

# Lets Talk — reason a decision through, don't build it

A discussion mode. The user has a question, a tradeoff, or a fork in the road and wants to *think*
it through with you. The deliverable is a **decision the user can act on** — a recommendation, a
sharpened understanding, a ruled-out option — not a file, not code, not an artifact. This is the
**anti-pair**: `pair` goes idea → shipped code; `lets-talk` goes fuzzy question → clear decision,
and stops there. It's the third bookend of the understanding loop — `explain-diff` makes a *change*
legible, `research` makes a *topic* legible, `lets-talk` makes a *decision* legible.

The whole value is the quality of the thinking. Everything below serves that.

## First — are they thinking, or asking you to act?

A question posed for deliberation ("should we split these into separate skills?") wants discussion.
A question that's really an instruction ("should we rename this to `foo`?" when they've clearly
decided) wants action. Read the intent: if they want the thing *done*, drop this skill and do it,
or hand off to `/pair` or `/prototype`. `lets-talk` earns its place only when the user genuinely
wants to reason before committing.

## Ground before you opine

This is the highest-leverage move, and the one most often skipped. **Before forming a view, go read
the real thing** — the actual code, the actual skill file, the actual doc, the actual external
source. Read the `pair` skill before critiquing it; fetch the repo before comparing against it;
open the blog post before invoking its argument. Use Explore for breadth, Read for the specific
file, WebFetch/WebSearch for outside sources.

An opinion built on a remembered or assumed version of the artifact is a strawman, and the user can
tell. Grounding is also what earns you the right to disagree with them — you can only say "your code
already does X" if you looked. When you can't ground something (private system, their intent), say
so and ask, rather than guessing.

Two kinds of grounding, and only one is this skill's job to *do*:
- **Light, inline** — read the file that's in front of you, fetch the one URL, skim the module. Do
  it yourself, synchronously, in the conversation. This is most grounding.
- **Heavy, delegatable** — a real multi-source question ("what's the current state of X across these
  five libraries?"). That's not discussion, it's [`research`](../research/SKILL.md): spawn it as a
  background agent, keep talking, and fold its cited findings in when they land. `lets-talk` never
  *does* research — it *dispatches* it when a decision hangs on facts you don't have.

## Take a position

Recommend, don't survey. A neutral list of options is a cop-out — the user came for judgment. Form a
view, put the recommended option first, and explain the **why** in terms of *their* specifics, not
generic pros and cons. Surface the real tradeoff rather than pretending one doesn't exist.

Disagree when the evidence warrants it — a discussion partner who only validates is useless. And
actively **connect things the user hasn't connected**: "you already do X in your spec template",
"this is the same pattern as Y you built last month". Those links are where the value compounds.

Calibrate depth to the stakes. A two-way-door decision gets a quick take; an architectural or
hard-to-reverse one gets the tradeoffs laid out and stress-tested.

## Move toward a decision

A discussion that never converges is just talk. Track the open threads, and drive toward resolution:
name what's still undecided, and when the path forward genuinely forks on the user's preference or
knowledge, ask — one question at a time, using AskUserQuestion when the options are concrete enough
to pick from. Don't manufacture questions you could answer by grounding; ask only what actually
turns on the user's call. Summarise where things land so the decision is captured, not lost in the
scroll.

## Stay in discussion — resist the build reflex

Keep everything in the conversation. No files, no code changes, no artifacts, no branches — the point
is the thinking, and writing something is how a discussion prematurely calcifies into the first idea.
The pull to open an editor is the signal you've reached the edge of the discussion — that's the
handoff, not a step you take here. (Grounding reads are fine; producing deliverables is not.)

If the user explicitly asks for something written down mid-discussion — notes, a summary, a decision
log — that's a real request; honour it. The guardrail is against *drifting* into building, not
against an asked-for artifact.

## Hand off when it resolves

When the discussion produces an action, name the skill that does it and offer to switch — don't start
doing the work inside `lets-talk`:

- Direction decided, now pin the exact requirements → `/grill` (then `/spec`)
- Direction decided but the work is too big/foggy for one session → `/wayfinder` (map it over many)
- Build a feature end-to-end → `/pair`
- See a design running before committing → `/prototype`
- Create or change a skill → `/skill-creator`
- Gather facts from sources → `/research`
- Understand a change already made → `/explain-diff`

`lets-talk` sits at the top of a **commitment ladder**, each rung narrowing the question:

```
research    is it true?          (facts)
lets-talk   should we? / what?   (open — a legit outcome is "don't build")
grill       what exactly?        (direction chosen; pin requirements — one session)
 └ wayfinder  …when it's too big for one session (map decision tickets over many)
/pair       make it              (spec → plan-review → implement → review-change)
```

This skill owns the "should we? / what?" rung. When it resolves to "yes, build X", hand off *down*
the ladder — `/grill` to pin it, or `/pair` for the whole build. End the way this skill is meant to:
the user holds a decision they didn't have before, and knows the next move.
