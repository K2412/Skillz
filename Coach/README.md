# Codebase Guide Skill

A Git-grounded investigation skill for quickly understanding unfamiliar repositories and explaining conclusions with verifiable evidence.

## Purpose

Use this skill when someone asks:
- where a feature is implemented
- how a component or flow works
- why behavior changed over time
- how to onboard quickly to a project

The skill is designed for read-first repository analysis with strong evidence standards.

## Core Behavior

- Defaults to read-only investigation.
- Uses fast code search and inspection first (`rg`, `ls`, `sed`, `cat`).
- Adds read-only Git history (`git log`, `git show`, `git blame`, `git grep`) when timeline/rationale matters.
- Requires concrete citations for substantive claims.
- Explicitly labels uncertainty and inference.

## Investigation Workflow

1. Clarify scope
- Restate the question in technical terms.
- Define in-scope/out-of-scope boundaries.

2. Map the codebase
- Find entrypoints, related modules, and tests.
- Build a candidate file map before deep reading.

3. Trace behavior
- Read files in execution order.
- Track interfaces, data flow, side effects, and error paths.

4. Add Git context
- Use read-only history to explain changes and ownership.

5. Synthesize for onboarding
- Answer directly.
- Provide evidence and a practical "read next" path.
- Call out unknowns and assumptions.

## Response Contract

A complete answer should include:
1. Direct answer (shortest correct conclusion first)
2. Evidence (files, lines, commits, and relevant commands)
3. Explanation (facts vs. inference)
4. Onboarding path (next 2-5 files/commands)
5. Unknowns and assumptions

## Safety Boundaries

- Treat analysis as read-only by default.
- Avoid history-altering or destructive Git commands unless explicitly requested.
- Do not invent files, symbols, commits, or outcomes.
- Do not expose secrets; redact sensitive values.
- If mutation is required, request explicit confirmation and prefer reversible steps.

## Files in This Skill

- `SKILL.md` — skill definition and usage trigger
- `references/workflow.md` — end-to-end investigation loop
- `references/command-catalog.md` — preferred command patterns
- `references/answer-format.md` — required output structure
- `references/safety-boundaries.md` — guardrails and escalation posture

## Quick Start

1. Run `rg --files` to learn project layout.
2. Run targeted `rg -n "<pattern>" <path>` searches for symbols and call sites.
3. Inspect key files with `sed -n '<start>,<end>p' <file>`.
4. Add Git context with `git log -- <path>` and `git show <commit>`.
5. Return conclusions with evidence and clearly marked assumptions.
