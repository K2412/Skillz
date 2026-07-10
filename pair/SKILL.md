---
name: pair
description: Full spec-to-ship pipeline with built-in grilling, plan review, subagent execution, and code review. Use when the user says /pair, "pair with me", "pair on this", "let's build this together", "walk me through building", or wants to go from idea to reviewed code in one guided session. Also trigger when the user describes a feature or fix they want to implement end-to-end with quality gates. The pipeline pauses at every stage boundary for explicit approval and can loop back if reviews fail.
---

# /pair — Spec-to-Ship Pipeline

Five stages with a human gate between each.

```
grill → beads plan → plan review → subagent execution → code review
```

---

## Stage 1 — Grill

Interview the user relentlessly about every aspect of the plan until reaching shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one at a time.

**Rules:**
- Ask questions one at a time. For EVERY question use AskUserQuestion so the user picks from options instead of typing free-text.
- Generate 2–4 concrete, mutually exclusive options per question. Put the recommended answer first and append "(Recommended)" to its label. Put nuance in the description field.
- If a question can be answered by exploring the codebase, explore instead of asking.
- Users always have "Other" available — don't force a fit when the answer space is genuinely open.

Continue until the user signals completion ("ready", "ship it", "let's go", "do it", or any clear go-ahead). Capture the full decision log — every Q/A pair resolved — before moving to Stage 2.

---

## Stage 2 — Gate: Commit plan to Beads

Confirm with AskUserQuestion before writing anything:

```
question: "Grill complete. Commit this plan to Beads and move to execution planning?"
options:
  - "Yes, write to Beads (Recommended)" → proceed
  - "Revise something first" → loop back to Stage 1 with current decisions as context
  - "Summarise in chat only, skip Beads" → produce markdown checklist and stop
```

**If writing to Beads:**

1. Check `which bd` — if missing, fall back to markdown and tell the user to install `bd`.
2. If `.beads/` doesn't exist, run `bd init --quiet`.
3. Create one epic. Title = original task (≤180 chars). Description = full Q/A decision log.
   ```
   bd create "<task title>" -t epic -p 1 \
     --description "<decision log>" \
     --labels "pair,accepted-plan" --json
   ```
   Capture the parent ID.
4. Create one child task per atomic, independently-shippable TDD slice. Each child description includes: scope, acceptance criteria, and the decisions relevant to that slice.
   ```
   bd create "<child title>" -t task -p 1 \
     --parent <parent-id> \
     --description "<scope + acceptance criteria>" \
     --labels "pair,agent-task" --json
   ```
5. Add `bd dep add` edges for any ordering the interview surfaced.
6. Add human gates for irreversible operations (migrations, schema changes, external API writes):
   ```
   bd gate create --type=human --blocks <child-id> \
     --reason "Human approval required before proceeding"
   ```
7. Show the user the compact task tree (epic ID, child IDs + one-line titles, dep edges, gates).

**Markdown fallback:** If `bd` is unavailable, produce the same structure as a markdown checklist (Epic → children → blockers → gates) and note that Beads was skipped so the user knows to install `bd` later.

---

## Stage 3 — Plan Review

Review the beads plan with a senior-engineer eye before any code is written. Fetch the task list:

```bash
bd list --parent <epic-id> --json
```

Evaluate for: DRY violations in the plan, over-stuffed tasks that aren't atomic, missing dependency edges, tasks too large for a single TDD slice, structural issues in the proposed approach.

For each finding use this structure:
```
### [blocker | should-fix | nit] — Principle
**What:** one sentence
**Why it matters:** two to three sentences tied to this specific plan
**Fix:** concrete change to the bead scope or split
```

**Gate after review:**

```
question: "Plan review complete. How do you want to proceed?"
options:
  - "Plan looks good — proceed to execution (Recommended)"
  - "Revise plan — loop back to grill with these findings"
  - "Accept with caveats — annotate beads and proceed"
```

If "loop back": carry the findings as the opening context for a new grill session. Update bead tasks after the revised grill. Re-run the plan review. Repeat until the plan passes or the user explicitly accepts.

---

## Stage 4 — Subagent Execution (TDD)

**Do not execute in the orchestrator's context.** The grill + plan stages have consumed significant context. Spawn a subagent with a fresh window.

Gate before spawning:

```
question: "Ready to execute. Spawn a subagent to build from the beads plan?"
options:
  - "Yes, spawn execution subagent (Recommended)"
  - "I'll execute manually — just show me the bead tasks"
  - "Pause here — I'll resume later"
```

If spawning, build the subagent prompt from bead data only — not from conversation history:

```bash
bd list --parent <epic-id> --json
bd get <child-id> --json   # for each child
```

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
<bead tasks as a numbered list with titles, descriptions, and dep order>

## Acceptance
Each task is done when:
1. The seam was confirmed before any test was written.
2. Every test was written red-first and passes green.
3. Acceptance criteria from the bead description pass.
4. `bd update <id> --status done` succeeds.
```

Spawn via the Agent tool with `subagent_type: "claude"`. Wait for the subagent to return before proceeding.

If the subagent hits a human gate, surface the gate reason to the user and wait for explicit approval before continuing.

---

## Stage 5 — Code Review

Review the actual code diff after the subagent returns.

```bash
git diff origin/dev...HEAD        # or origin/main...HEAD
```

Before reviewing, check the project's configured thresholds:

```bash
cat pyproject.toml 2>/dev/null | grep -A 30 "\[tool.ruff"
cat ruff.toml 2>/dev/null
```

Look for: `lint.mccabe.max-complexity`, `lint.pylint.max-statements`, `line-length`. If not configured, use these defaults and say so:

| Metric | Default |
|---|---|
| File length | 300 lines |
| Function length | 50 lines |
| Cyclomatic complexity | 10 |
| Function arguments | 5 |

**Checklist — work through in order:**

**A. DRY** — 5+ line blocks repeated in 2+ places, parallel if/elif chains, repeated string literals or magic numbers, repeated try/except patterns.

**B. Reflex State discipline** (if any `rx.State` subclasses are touched — check `docs/Arch/reflex-patterns.md` at the repo root)
- State classes: hold UI state, expose event handlers, delegate work. No business logic inline.
- Data transformations belong in service modules, not State methods.
- Computed vars: simple derivations only, not orchestration.

**C. File length** — files over threshold: identify the seams, propose a split along responsibility lines.

**D. Function complexity and length** — over threshold: identify natural paragraphs, propose extraction. Arg count over threshold: propose a dataclass or TypedDict.

**E. Single Responsibility** — classes doing two unrelated jobs, functions with "and" in the name.

**F. Coupling** — modules importing from far across the codebase for one small thing, classes with 6+ collaborators in `__init__`.

For each finding:
```
### [blocker | should-fix | nit] File:Line — Principle
**What:** one sentence
**Why it matters:** two to three sentences specific to this code
**Refactor:**
  # Before
  ...
  # After
  ...
**The pattern to notice next time:** one sentence
```

Order: blockers → should-fix → nits. Group within each severity by file.

End with a verdict:
- **Green:** no blockers, ship it.
- **Yellow:** fix blockers before PR; should-fixes are reviewer's call.
- **Red:** restructure before this is reviewable.

Then: "The pattern that came up most in this branch was X."

**Gate after review:**

```
question: "Code review complete. What next?"
options:
  - "Present findings — I'll decide what to fix (Recommended)"
  - "Accept as-is — close the epic"
```

If all findings resolved or accepted: close the epic.
```bash
bd update <epic-id> --status done
```

Show a final summary: epic closed, tasks completed, any open follow-up beads, deferred decisions.

---

## Escape hatches

- **"stop pair"** / **"exit pair"**: save current state (stage + which beads exist) and hand back control.
- **"skip to execution"**: jump to Stage 4 using whatever beads currently exist. Warn that the plan hasn't been reviewed.
- **"pair resume"**: find the most recent open pair epic via `bd list --labels pair --status open --json` and pick up from the last completed stage.
