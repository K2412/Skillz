---
name: implement
description: Execute a pre-approved GitHub plan using strict TDD — spawning a fresh subagent that works each task red→green, one vertical slice at a time, at confirmed test seams. Use when the user wants an existing plan built: "implement this plan", "build from these issues/tickets", "execute the plan with TDD", "start building this", or as the stage after /plan-review in /pair. Works from issue data, not conversation history. Do NOT design or re-plan here — this stage builds what the issues already specify.
---

# Implement — TDD execution from a GitHub plan

Execute a pre-approved plan of GitHub issues using strict TDD.

**Do not execute in the orchestrator's context.** Planning stages consume significant context —
spawn a subagent with a fresh window so execution starts clean.

Gate before spawning:

```
question: "Ready to execute. Spawn a subagent to build from the plan?"
options:
  - "Yes, spawn execution subagent (Recommended)"
  - "I'll execute manually — just show me the tasks"
  - "Pause here — I'll resume later"
```

If spawning, build the subagent prompt from issue data only — not from conversation history (see
[../spec/GITHUB-ISSUES.md](../spec/GITHUB-ISSUES.md)):

```bash
gh issue view <epic-n> --json title,body                                   # the spec
gh api repos/<owner/repo>/issues/<epic-n>/sub_issues                        # the tasks + state + labels
gh issue view <task-n> --json title,body,labels   # for each task (a `needs-human` label = stop and ask first)
```

If the epic has a `prototype/<slug>` branch-pointer comment, include it in the subagent prompt and
tell the subagent to check out and reference that branch — it holds validated, runnable design code
to copy from rather than re-derive. The prototype is throwaway scaffolding; the subagent lifts the
validated logic module or rebuilds the winning UI variant properly, it does not merge the prototype
branch.

Subagent prompt structure:
```
You are executing a pre-approved development plan using TDD. Work through each
task below in dependency order using the red → green loop. Follow the rules
below exactly — they are not suggestions.

If you encounter a human gate, stop and report back immediately.

## TDD Rules

### Before writing any test
Identify the seam for each task — the public boundary where behavior is
observable without reaching inside the implementation. Write down the seams
and confirm them before writing a single line of test or production code.
No test is written at an unconfirmed seam.

Ask: "What is the public interface, and which seams should I test?"

If CONTEXT.md exists at the repo root, read it — match test names and
interface vocabulary to the project's domain language.

### The red → green loop (one slice at a time)
1. **Red** — write one failing test at the confirmed seam. Run it. Confirm it fails for the right reason.
2. **Green** — write the minimum production code to make that test pass. Nothing more.
3. Repeat for the next behaviour slice.

Do not write multiple tests before implementing. Do not anticipate future slices.
Refactoring belongs to the review stage — keep the loop clean.

### Anti-patterns — never do these
- **Implementation-coupled**: mocking internal collaborators, testing private
  methods, or verifying through side channels (e.g. querying the DB instead of
  the public interface). Tell: the test breaks on refactor but behaviour hasn't changed.
- **Tautological**: asserting expected values that are computed the same way the
  code computes them. Expected values must come from an independent source —
  a known-good literal, a worked example, or the spec.
- **Horizontal slicing**: writing all tests first, then all implementation.
  Work in vertical slices — one test → one implementation → repeat.

### What a good test looks like
Tests verify behaviour through public interfaces, not implementation details.
A good test reads like a specification: "user can checkout with valid cart"
tells you exactly what capability exists and survives refactors.

## Tasks
<task issues as a numbered list with titles, bodies (scope + acceptance criteria + seam), and dep order>

## Acceptance
Each task is done when:
1. The seam was confirmed before any test was written.
2. Every test was written red-first and passes green.
3. Acceptance criteria from the task issue body pass.
4. `gh issue close <task-n>` succeeds.
```

Spawn via the Agent tool with `subagent_type: "claude"`. Wait for the subagent to return before proceeding.

If the subagent hits a human gate, surface the gate reason to the user and wait for explicit approval before continuing.

When the subagent returns, the changes are ready for [`review-change`](../review-change/SKILL.md).
