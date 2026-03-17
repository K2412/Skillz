---
name: Plan-super
description: >-
  Converts an idea into a durable set of repo artifacts and dependency-aware tickets using a 7-phase framework: Idea, Research, Prototype, PRD, Tickets, Execution, QA. Use when asked to "plan this", "create tickets for", "turn this into a project", "write a PRD", "create a product requirements document", "grill me", or "stress-test this plan". Each phase is optional based on scope — outputs Phase Decision, Deliverables, Ticket Plan, Risks, and Next Action.
---

# Plan-super

Turns any idea — from a one-liner to a vague direction — into a structured, executable plan with dependency-aware tickets and durable repo artifacts.

If the user only wants a PRD (and not a full plan), you can run only Phase 4 as a standalone path — see **PRD-Only Shortcut** below.

If the user wants to stress-test or be grilled on a plan, use **Grill Mode** below.

## Output Format (Always)

Every Plan-super run produces exactly these five sections:

1. **Phase Decision** — which phases to run and why (based on scope/uncertainty)
2. **Deliverables** — files/docs to create in the repo
3. **Ticket Plan** — ordered tickets with dependencies and acceptance criteria
4. **Risks & Unknowns** — top 3-5 things that could derail execution
5. **Next Action** — the single most important thing to do right now

## 7-Phase Framework

See [references/phases.md](references/phases.md) for when to run each phase and decision rules.

| Phase | Purpose | Skip when |
|---|---|---|
| 1. Idea | Clarify intent, constraints, success criteria | Idea is already clear |
| 2. Research | Gather prior art, existing patterns, dependencies | Problem is well-understood |
| 3. Prototype | Validate approach with throwaway code | Low technical risk |
| 4. PRD | Document requirements and non-requirements | Tiny scope (1-3 tickets) |
| 5. Tickets | Ordered, dependency-aware implementation units | Already have tickets |
| 6. Execution | Implementation guidance per ticket | Not needed (dev handles it) |
| 7. QA | Acceptance tests and verification steps | Covered by existing tests |

## Phase 4: PRD — User Interview Method

When running Phase 4 (or the PRD-Only Shortcut), use this structured interview process:

1. Ask the user for a long, detailed description of the problem they want to solve and any potential ideas for solutions.

2. Explore the repo to verify their assertions and understand the current state of the codebase.

3. Interview the user relentlessly about every aspect of this plan until you reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.

4. Sketch out the major modules you will need to build or modify. Actively look for opportunities to extract deep modules that can be tested in isolation.

   A **deep module** encapsulates a lot of functionality in a simple, testable interface that rarely changes (vs. a shallow module). Check with the user that these modules match their expectations and which they want tests written for.

5. Write the PRD using the template below, then submit it as a GitHub issue.

### PRD Template

```
## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format:

1. As an <actor>, I want a <feature>, so that <benefit>

This list should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:
- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets — they may become outdated quickly.

## Testing Decisions

A list of testing decisions that were made. Include:
- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this PRD.

## Further Notes

Any further notes about the feature.
```

## PRD-Only Shortcut

If the user says "write a PRD", "create a product requirements document", or wants only a PRD without full planning:
- Skip Phases 1–3 and 5–7
- Run Phase 4 only using the User Interview Method above
- Output is a GitHub issue with the PRD template filled in

## Grill Mode

If the user says "grill me", "stress-test this plan", or wants relentless questioning before committing to a direction:
- Skip all output sections (no deliverables, no tickets)
- Interview the user relentlessly about every aspect of their plan until you reach a shared understanding
- Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one
- If a question can be answered by exploring the codebase, explore it instead of asking
- Only exit Grill Mode when all branches are resolved — then offer to continue into the full 7-phase framework

## Ticket Format

Each ticket must include:

- **ID** — sequential reference (T-01, T-02 ...)
- **Title** — imperative verb phrase ("Add user authentication endpoint")
- **Depends on** — IDs of blocking tickets (empty if none)
- **Acceptance Criteria** — verifiable checklist
- **Size** — S / M / L

## Stack Defaults

See [references/defaults.md](references/defaults.md) for standard assumptions (Laravel, Inertia+Svelte 5, Saloon, etc.) to apply unless overridden.

## Templates

See [references/templates.md](references/templates.md) for:
- Research cache format
- PRD template
- Ticket template
- QA checklist template
