---
name: review-change
description: Review a code change on two independent axes at once — Standards (does it follow this repo's conventions and the Fowler smell baseline?) and Spec (does it match the GitHub issue acceptance criteria?) — each run as its own subagent so they don't pollute each other. Use when the user wants a change reviewed against both quality and intent: "review my changes", "review this diff against the spec", "two-axis review", "did the build match the plan?", or as the final stage of /pair. For reviewing a GitHub PR by number use the PR-review tooling instead; this reviews the working diff against the plan's issues.
---

# Review Change — two-axis (Standards + Spec)

Run a two-axis review in parallel: **Standards** (does the code follow this repo's conventions and smell baseline?) and **Spec** (does it match the issue acceptance criteria?). Both axes run as separate sub-agents so they don't pollute each other's context.

## Setup — gather inputs before spawning

```bash
# Pin the diff base (use merge-base so feature-branch noise is excluded)
git diff origin/dev...HEAD        # or origin/main...HEAD
git log origin/dev..HEAD --oneline

# Check configured thresholds for the Standards axis
cat pyproject.toml 2>/dev/null | grep -A 30 "\[tool.ruff"
cat ruff.toml 2>/dev/null

# Fetch issue acceptance criteria for the Spec axis (see ../spec/GITHUB-ISSUES.md)
gh issue view -R K2412/planning <epic-n> --json title,body
gh api repos/<owner/repo>/issues/<epic-n>/sub_issues --jq '.[] | "#\(.number) \(.title)"'
gh issue view -R K2412/planning <task-n> --json title,body   # for each task
```

Confirm the diff is non-empty before spawning — an empty diff should fail here, not inside a sub-agent.

The **spec source** is the task issues (each has acceptance criteria in its body). If there's no epic (standalone review of a diff with no plan), run the Standards axis alone and say the Spec axis was skipped for lack of a spec.

## Spawn both sub-agents in parallel

Send a single message with two Agent tool calls (`subagent_type: "claude"`).

---

**Standards sub-agent prompt:**

```
Review the diff below against (a) this repo's documented standards and (b) the Fowler smell baseline.

## Diff
<paste: git diff origin/dev...HEAD>

## Commits
<paste: git log origin/dev..HEAD --oneline>

## Repo standards
Check pyproject.toml / ruff.toml for configured thresholds. If not set, use:
- File length: 300 lines
- Function length: 50 lines
- Cyclomatic complexity: 10
- Function arguments: 5

For Reflex projects (files touching rx.State subclasses):
- State classes hold UI state, expose event handlers, delegate work — no inline business logic.
- Data transformations belong in service modules, not State methods.
- Computed vars: simple derivations only.
- Check docs/Arch/reflex-patterns.md if present.

## Fowler smell baseline (always applies; repo standards override where they conflict)
- Mysterious Name — rename; if no honest name exists, the design is murky.
- Duplicated Code — extract the shared shape.
- Feature Envy — a method reaching into another object's data more than its own; move it.
- Data Clumps — the same fields travelling together; bundle into one type.
- Primitive Obsession — a primitive standing in for a domain concept; give it its own type.
- Repeated Switches — same switch/if-cascade on the same type; replace with polymorphism.
- Shotgun Surgery — one logical change forcing edits across many files; consolidate.
- Divergent Change — one file edited for several unrelated reasons; split by responsibility.
- Speculative Generality — abstraction added for needs the spec doesn't have; delete it.
- Message Chains — long a.b().c() navigation; hide the walk behind one method.
- Middle Man — a class that mostly just delegates; cut it, call the real target.
- Refused Bequest — a subclass ignoring most of what it inherits; use composition.

## Brief
Per file/hunk: (a) every documented-standard violation — cite the rule; (b) any smell — name it and quote the hunk. Documented standards override the baseline. Smells are judgement calls, not hard violations. Skip anything tooling already enforces. Under 400 words.

For each finding use:
### [blocker | should-fix | nit] File:Line — Principle
**What:** one sentence
**Why it matters:** two to three sentences tied to this specific code
**Refactor:** before/after snippet
**The pattern to notice next time:** one sentence
```

---

**Spec sub-agent prompt:**

```
Review the diff below against the bead acceptance criteria.

## Diff
<paste: git diff origin/dev...HEAD>

## Commits
<paste: git log origin/dev..HEAD --oneline>

## Issue acceptance criteria (the approved spec)
<paste: each task issue title + body + acceptance criteria>

## Brief
Report: (a) acceptance criteria that are missing or only partially implemented — quote the criterion; (b) behaviour in the diff that no issue asked for (scope creep); (c) criteria that appear implemented but where the implementation looks wrong. Under 400 words.
```

---

## Aggregate results

Present the two reports side by side under `## Standards` and `## Spec`. Do not merge or rerank findings across axes — a change can pass one axis and fail the other, and that distinction matters.

End with one line per axis: finding count and worst issue within that axis.

**Gate after review:**

```
question: "Review complete. What next?"
options:
  - "Present findings — I'll decide what to fix (Recommended)"
  - "Accept as-is — close the epic"
```

If all findings resolved or accepted and this ran against an epic, close it:
```bash
gh issue close -R K2412/planning <epic-n>
```

Show a final summary: epic closed (if any), tasks completed, any open follow-up issues, deferred decisions.
