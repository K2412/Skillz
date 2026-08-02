---
name: spec
description: Synthesise a discussion, grill log, rough idea, or a resolved wayfinder map into a written spec (problem, solution, user stories, implementation + testing decisions, scope), then commit it to GitHub as an epic issue with atomic child sub-issues. Use when the user wants to turn understanding into a plan: "write a spec for this", "spec this out", "turn this into issues/tickets", "break this into tasks", "spec this wayfinder map", or as the stage after /grill in /pair. Explores the repo and identifies test seams first. Do NOT interview the user here — that's /grill; this stage synthesises from what's already decided.
---

# Spec — synthesise understanding into a spec + GitHub plan

Turn shared understanding (a grill decision log, a discussion, or a rough idea the user hands you)
into a written spec and an atomic plan of **GitHub issues in the code repo**. **Don't interview
here** — that's [`grill`](../grill/SKILL.md). Synthesise from what's already decided plus what you
find in the code.

Confirm scope with AskUserQuestion before writing anything:

```
question: "Ready to synthesise into a spec and open the GitHub issues?"
options:
  - "Yes, write spec and issues (Recommended)" → proceed
  - "Revise something first" → resolve the open point (loop back to /grill if it needs interviewing)
  - "Summarise in chat only, skip issues" → produce markdown checklist and stop
```

## Step 0 — If the source is a wayfinder map

If you're synthesising from a [`wayfinder`](../wayfinder/SKILL.md) map (a `K2412/planning` issue with
closed decision tickets), pull every closed sub-issue's title, body, and **resolution comment** first —
those resolutions are the decisions. Build the spec from them, and **link each spec section back to the
ticket URL it came from** so the implementer can open the primary source instead of trusting a summary.
The map may hold far more decisions than a single grill; expect a dense spec.

## Step 1 — Explore the repo

Before writing anything, read the codebase to understand current state. Use the project's domain vocabulary throughout the spec. Respect any ADRs in the area being touched.

## Step 2 — Identify test seams

Identify the seams at which the feature will be tested:
- Prefer existing seams over new ones.
- Use the highest seam possible — the fewer seams the better; the ideal is one.
- Propose new seams only when unavoidable, at the highest point you can.

Confirm the seams with the user via AskUserQuestion before proceeding.

## Step 3 — Write the spec

Synthesise into a spec using this template:

```
## Problem Statement
The problem the user is facing, from the user's perspective.

## Solution
The solution, from the user's perspective.

## User Stories
A numbered list covering all aspects of the feature. Format:
1. As a <actor>, I want <feature>, so that <benefit>.
(Be exhaustive — every edge case, every actor.)

## Implementation Decisions
- Modules that will be built or modified
- Interface changes
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions
(No file paths or code snippets unless a prototype snippet encodes a decision
more precisely than prose — if so, inline only the decision-rich parts.)

## Testing Decisions
- What makes a good test for this feature (external behaviour, not internals)
- Which modules will be tested
- Prior art in the codebase (similar existing tests)

## Out of Scope
What this spec explicitly does not cover.

## Further Notes
Anything else relevant.
```

Show the spec to the user. Ask if anything needs adjusting before opening the issues.

## Step 4 — Write the GitHub plan

Follow [GITHUB-ISSUES.md](GITHUB-ISSUES.md) for the exact `gh` commands. In order:

1. **Ensure the labels exist** (`spec:epic`, `spec:task`, `blocked`, `needs-human`) — idempotent.
2. **Create one epic issue** (`spec:epic`), title = original task (≤180 chars), body = the full spec
   from Step 3. If a prototype settled a design question upstream, attach its branch pointer + verdict
   as a comment on the epic so it travels with the plan.
3. **Create one task sub-issue per atomic, independently-shippable TDD slice** derived from the spec's
   Implementation Decisions and User Stories. Each task body carries scope, acceptance criteria (tied
   to user stories, as a checklist), and the confirmed test seam. Link each as a sub-issue of the epic.
4. **Wire ordering and gates in a second pass:** add `blocked` (+ a `Blocked by #N` body line) for any
   task that depends on another; add `needs-human` to any task doing an irreversible operation
   (migration, schema change, external API write) so `implement` stops for approval there.
5. **Show the user the compact tree** — epic #, task #s + one-line titles, which are blocked, which are gated.

**No `gh`?** Produce the spec + task list as a Markdown checklist and tell the user GitHub tracking was
skipped. The issues *are* the plan — there's no local DB.

Hand back the epic number — [`plan-review`](../plan-review/SKILL.md) and [`implement`](../implement/SKILL.md) work from it.
