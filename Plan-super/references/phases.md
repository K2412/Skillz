# Super Plan — Phase Reference

## Phase Decision Rules

Read the user's request and answer these questions to decide which phases to run:

| Question | If YES, include phase |
|---|---|
| Is the idea ambiguous or under-specified? | Phase 1 (Idea) |
| Are there external dependencies, APIs, or unfamiliar patterns? | Phase 2 (Research) |
| Is the technical approach uncertain or risky? | Phase 3 (Prototype) |
| Is scope > 3 tickets or involves multiple stakeholders? | Phase 4 (PRD) |
| Are there > 1 implementation task? | Phase 5 (Tickets) — always |
| Does the agent need per-ticket guidance? | Phase 6 (Execution) |
| Is there no existing test coverage for the area? | Phase 7 (QA) |

Minimum viable plan: Phase 1 + Phase 5 + Phase 7.
Full plan: All 7 phases.

---

## Phase 1: Idea Clarification

**Goal**: Lock down intent, constraints, and success criteria before any work begins.

**Outputs**:
- One-sentence goal statement
- In-scope / out-of-scope list
- Success criteria (measurable)
- Known constraints (time, tech, team)

**Trigger questions**:
- "What does success look like in 1 sentence?"
- "What are we explicitly NOT doing?"
- "What constraints are non-negotiable?"

---

## Phase 2: Research

**Goal**: Gather relevant prior art, existing patterns, and external dependencies.

**Outputs**: Research cache document (`docs/research/{topic}.md`)

**What to research**:
- Existing code in the repo that's relevant
- Third-party packages/APIs involved
- Prior decisions in `git log` or docs
- Known gotchas or constraints

**Cache format**: See `references/templates.md`.

---

## Phase 3: Prototype

**Goal**: Validate the technical approach with a throwaway spike.

**Outputs**: Spike branch, findings doc

**When to skip**: Approach is well-understood, team has done it before, risk is low.

**Prototype constraints**:
- Time-boxed (1 day max)
- Not merged to main
- Findings documented, code discarded

---

## Phase 4: PRD (Product Requirements Document)

**Goal**: Single source of truth for what is being built and why.

**Outputs**: `docs/prd/{feature}.md`

**Sections**: Overview, Problem, Goals, Non-Goals, Requirements, Open Questions

**When to skip**: Scope is < 3 tickets and requirements are obvious.

---

## Phase 5: Tickets

**Goal**: Ordered, dependency-aware implementation units that can be picked up independently.

**Outputs**: Ticket plan (inline or in `docs/tickets/{feature}.md`)

**Rules**:
- Each ticket delivers a vertical slice (not a layer)
- Tickets ordered by dependency DAG
- Each ticket has clear, verifiable AC
- No ticket takes more than 1 week

**Always include Phase 5.** It's the core output of every super-plan run.

---

## Phase 6: Execution Guidance

**Goal**: Per-ticket hints to unblock the implementing agent.

**Outputs**: Notes appended to each ticket

**Include when**: Agent will implement without human oversight (ralph-loop scenarios).

---

## Phase 7: QA

**Goal**: Verifiable acceptance tests that prove the feature works.

**Outputs**: QA checklist per ticket (or feature-level)

**Format**: Checkboxes with exact steps and expected outcomes.
