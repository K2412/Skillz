---
name: pair
description: Full spec-to-ship pipeline that orchestrates the individual engineering skills in sequence with a human gate between each — optional research, then grill, optional prototype, spec, plan review, TDD implementation, two-axis review, and a final scrub. Use when the user says /pair, "pair with me", "pair on this", "let's build this together", "walk me through building", or wants to go from idea to reviewed code in one guided session. Also trigger when the user describes a feature or fix they want to implement end-to-end with quality gates. Each stage is its own skill you can also run alone; pair chains them, pauses at every boundary for approval, and can loop back if reviews fail.
---

# /pair — Spec-to-Ship Pipeline (orchestrator)

`pair` doesn't do the work itself — it **sequences the individual skills** and holds the human gates
and loop-backs between them. Each stage is a standalone skill; `pair` invokes it, waits for the gate,
and moves on. The detail lives in each skill, not here.

```
[research] → grill → [prototype] → spec → plan-review → implement → review-change → scrub
```

Bracketed stages are optional and fire only when they earn their place. Run each stage by invoking
its skill and following it to completion, then apply the transition below before the next.

`pair` presumes the decision to build is **already made** — it's the commitment end of a longer arc.
If whether to build (or what) is still open, settle that *before* `pair`, not as a stage inside it —
`pair` doesn't reopen the question of whether to build:

```
(should we? / what?)  →  /pair { [research] → grill → [prototype] → spec → plan-review → implement → review-change → scrub }
```

When the *planning itself* is too big for one session — foggy, dependent decisions, work you'd want to
parallelise — the front of this pipeline (grill) is replaced by [`wayfinder`](../wayfinder/SKILL.md),
which maps decision tickets over many sessions and hands `spec` a resolved map. Then `pair` picks up
from spec onward. `wayfinder` is the plan-phase orchestrator; `pair` is the build-phase one.

## Stage 0 — Research (optional)

If the idea hinges on facts you don't have — an unfamiliar API, a library choice, domain knowledge,
real-world UI patterns — grounding the grill in facts beats grilling on guesses. Offer it:

```
question: "This depends on <the unknown>. Research it first so we grill on facts, not guesses?"
options:
  - "Yes, research first (Recommended)"
  - "No, I know enough — start grilling"
```

If yes, run [`research`](../research/SKILL.md) (it works AFK in a background agent and writes cited
findings to a file); carry those findings into the grill. If the idea is well-understood already,
skip straight to Stage 1.

## Stage 1 — Grill

Run [`grill`](../grill/SKILL.md) to reach shared understanding and maintain the domain model. It
finishes with a decision log plus any CONTEXT.md / ADR updates. Those feed the spec.

## Stage 1.5 — Prototype (optional)

Most decisions resolve in the grill. Some — **"how should it look?"**, **"how should it behave?"**,
**"does this state model feel right?"** — are guesses until you see them running. When the grill hits
one that's *load-bearing* and you'd be guessing without a running artifact, offer it:

```
question: "One decision here — <the design question> — is hard to settle in the abstract. Prototype it before we spec?"
options:
  - "Yes, prototype it (Recommended)" → run the prototype skill
  - "No, I can decide from discussion" → carry the decision into the spec as prose
  - "Not sure — talk it through first" → keep grilling, re-offer if it stays fuzzy
```

If it's cheap to describe in words, skip it — the discussion already resolved it (Litt's fidelity
ladder: pay for a prototype only where a running artifact tells you something prose can't). If yes,
run [`prototype`](../prototype/SKILL.md); it captures the verdict durably (and lifts any validated
logic module into place) without ever branching or committing the throwaway artifact. The verdict —
plus the knob settings it depends on — joins the decision log and rides into the spec, so `implement`
builds against a settled design.

## Stage 2 — Spec

Run [`spec`](../spec/SKILL.md) to synthesise the grill decision log (and any prototype verdict) into
a spec and a GitHub epic issue with atomic child task sub-issues (in the code repo). It hands back the
epic number.

## Stage 3 — Plan Review

Run [`plan-review`](../plan-review/SKILL.md) on the epic. Transition on its gate:
- **Looks good** → Stage 4.
- **Loop back** → re-run `grill` with the findings as opening context, update the plan via `spec`,
  then re-run `plan-review`. Repeat until it passes or the user explicitly accepts.
- **Accept with caveats** → annotate the issues and proceed.

## Stage 4 — Implement

Run [`implement`](../implement/SKILL.md) — it spawns a fresh TDD subagent from the issue data (and the
prototype branch if present). Wait for it to return. If it hits a `needs-human` task, surface the
reason and wait for approval.

## Stage 5 — Review Change

Run [`review-change`](../review-change/SKILL.md) — two-axis Standards + Spec review of the diff
against the epic. On acceptance it closes the epic and shows the final summary.

## Stage 6 — Scrub

Run [`scrub`](../scrub/SKILL.md) on the accepted diff as the final polish before it leaves the
session for a team PR. `review-change` is an internal gate; scrub is what makes the change read as
team-written rather than agent-driven — stripping bead ids and bead-speak, ticket references,
local-artifact mentions (`PLAN.md`, `NOTES.md`), agent-to-user chatter, and comments the code already
says, keeping only the load-bearing WHY. This is the last stage: after it the change is ready for a
human to open the PR (e.g. via `to-pr`).

## Escape hatches

- **"stop pair"** / **"exit pair"**: save current state (which stage, which issues exist) and hand back control.
- **"skip to execution"**: jump to Stage 4 using whatever task issues currently exist. Warn that the plan hasn't been reviewed.
- **"pair resume"**: find the most recent open epic via `gh issue list -R K2412/planning --label spec:epic --state open --json number,title,url` and pick up from the last completed stage.
