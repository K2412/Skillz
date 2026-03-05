---
name: codebase-guide
description: Git-grounded codebase navigation and onboarding skill. Use when users ask where code lives, how modules work, why decisions were made, or request quick project onboarding with evidence from files and read-only git history.
---

# Codebase Guide

Use this skill to understand unfamiliar repositories quickly and explain findings with verifiable evidence.

## When to use

Use when a user asks:
- Where a feature is implemented
- How a component or flow works
- Why behavior changed over time
- How to onboard quickly to a project

## Operating rules

- Default to read-only investigation.
- Prefer `rg` for discovery and `git log/show/blame/grep` for history and rationale.
- Do not run destructive or state-changing git commands unless explicitly requested.
- Every substantive claim must include evidence (file references and, when relevant, commit hashes).
- If evidence is incomplete, state uncertainty explicitly.

## Workflow

Follow [references/workflow.md](references/workflow.md) for the end-to-end investigation loop.

## Command patterns

Use approved command patterns from [references/command-catalog.md](references/command-catalog.md).

## Response contract

Format answers using [references/answer-format.md](references/answer-format.md).

## Safety boundaries

Apply guardrails in [references/safety-boundaries.md](references/safety-boundaries.md).
