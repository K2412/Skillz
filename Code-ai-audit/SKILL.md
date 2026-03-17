---
name: Code-ai-audit
description: >-
  Audits a repository for AI-agent-friendliness and produces a prioritised improvement plan. Use when asked to "audit this codebase for AI", "make this repo more agent-friendly", "score codebase for ralph", or "improve AI navigability". Scores on Feedback Loops, Navigability, Deep Modules, Boundary Integrity, and Grey-box Tests, then outputs quick wins and structural recommendations.
---

# Codebase AI Love

Audit a repository for AI-agent-friendly structure and produce an actionable improvement plan.

## Audit Dimensions

Score each dimension 0–5 using [references/rubric.md](references/rubric.md):

| Dimension | What it measures |
|---|---|
| **Feedback Loops** | How quickly an agent can verify a change (typecheck, lint, test speed) |
| **Navigability** | How easy it is to find code, understand structure, follow flows |
| **Deep Modules** | Whether interfaces hide complexity; public APIs vs. implementation ratio |
| **Boundary Integrity** | Whether module/layer contracts are enforced and explicit |
| **Grey-box Tests** | Whether seam tests exist at internal boundaries |

## Workflow

1. **Survey** — Read `README.md`, directory tree, `composer.json`/`pyproject.toml`/`package.json`.
2. **Score** — Evaluate each dimension against the rubric.
3. **Generate report** — Use `assets/report-template.md` as structure.
4. **Prioritise** — Output three tiers:
   - **Quick wins** (1–2 days): low effort, high agent-friendliness gain
   - **Medium refactors** (1–2 weeks): meaningful structural improvements
   - **Structural changes** (2+ weeks): architectural shifts

## Output Format

Always produce:

1. **Scorecard** — Table with score/5 per dimension and brief justification
2. **Top Issues** — 3–5 most impactful problems
3. **Quick Wins** — Ordered list with effort estimate
4. **Medium Refactors** — Ordered list with rationale
5. **Structural Changes** — Long-term recommendations

Use `assets/report-template.md` as the base structure.

## Reference Files

- [references/rubric.md](references/rubric.md) — Scoring criteria for each dimension
- [references/deep-modules.md](references/deep-modules.md) — What makes a deep module; how to split shallow ones
- [references/grey-boxing.md](references/grey-boxing.md) — Seam tests, interface-first testing
- [references/laravel.md](references/laravel.md) — Laravel-specific guidance (domain modules, Actions, Pipelines)
