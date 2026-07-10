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

## Stage 1 — Grill (with active domain modelling)

Interview the user relentlessly about every aspect of the plan until reaching shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one at a time. **Alongside the interview, actively maintain the project's domain model** — challenge fuzzy terms, invent edge-case scenarios, and capture terminology and irreversible decisions to disk as they crystallise.

**Interview rules:**
- Ask questions one at a time. For EVERY question use AskUserQuestion so the user picks from options instead of typing free-text.
- Generate 2–4 concrete, mutually exclusive options per question. Put the recommended answer first and append "(Recommended)" to its label. Put nuance in the description field.
- If a question can be answered by exploring the codebase, explore instead of asking.
- Users always have "Other" available — don't force a fit when the answer space is genuinely open.

### Load the domain model at the start

Before the first question, check for existing domain files:
- **`CONTEXT-MAP.md`** at repo root → multi-context repo; use it to route to the right sub-context's `CONTEXT.md` and ADR directory.
- **`CONTEXT.md`** at repo root or under a subdirectory → single-context; read it so you can challenge conflicting terms.
- **`docs/adr/`** (or context-specific ADR directory) → scan for existing decisions relevant to this area.
- If none of the above exist, that's fine — create them lazily when the first term or ADR is warranted.

### During the grill — active modelling behaviours

Apply these alongside the normal interview:

- **Challenge against the glossary.** If the user uses a term that conflicts with an existing `CONTEXT.md` entry, call it out immediately: "Your glossary defines X as A, but you seem to mean B — which is it?"
- **Sharpen fuzzy language.** If the user uses vague or overloaded terms, propose a precise canonical term: "You said 'account' — do you mean Customer or User? They're different things."
- **Discuss concrete scenarios.** When domain relationships come up, stress-test them with specific edge-case scenarios that force precision about boundaries.
- **Cross-reference with code.** If the user states how something works, check the code. If it disagrees, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline (do not batch)

The moment a term is resolved, write it to `CONTEXT.md` immediately. Format:

```md
# {Context Name}

{One or two sentence description of what this context is.}

## Language

**Order**:
{One or two sentences — what it IS, not what it does.}
_Avoid_: Purchase, transaction
```

Rules:
- Be **opinionated**. When multiple words exist for the same concept, pick the best and list the rest under `_Avoid_`.
- **Tight definitions** — one or two sentences max.
- **Only project-specific terms.** General programming concepts (timeouts, utilities) don't belong even if used often. Ask: is this concept unique to this context, or general programming? Only the former belongs.
- **CONTEXT.md is a glossary. Nothing else.** No specs, no implementation notes, no decisions. Decisions go in ADRs.

Create `CONTEXT.md` lazily — the first time a term is resolved.

### Offer ADRs sparingly

Only offer to create an ADR when **all three** are true:

1. **Hard to reverse** — cost of changing your mind later is meaningful.
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **Result of a real trade-off** — genuine alternatives existed and you picked one for specific reasons.

If any of the three is missing, skip it. Easy-to-reverse decisions get reversed; unsurprising decisions need no note; no-alternative decisions have nothing to record.

**Qualifies:** architectural shape, integration patterns between contexts, tech choices with lock-in, boundary/scope decisions, deliberate deviations from the obvious path, invisible constraints (compliance, SLOs), non-obvious rejected alternatives.

**ADR format** — live in `docs/adr/`, sequential numbering (`0001-slug.md`, `0002-slug.md`, ...). Scan for the highest existing number and increment. Template:

```md
# {Short title of the decision}

{1–3 sentences: context, decision, why.}
```

That's it. Add `Status` frontmatter, `Considered Options`, or `Consequences` sections **only** when they add genuine value.

### Finishing

Continue until the user signals completion ("ready", "ship it", "let's go", "do it", or any clear go-ahead). Before moving to Stage 2, capture:
- The full decision log — every Q/A pair resolved.
- Any new/updated `CONTEXT.md` entries.
- Any new ADR file paths.

Stage 2's spec synthesis uses all three.

---

## Stage 2 — Spec + Beads

Confirm with AskUserQuestion before writing anything:

```
question: "Grill complete. Synthesise into a spec and commit to Beads?"
options:
  - "Yes, write spec and Beads (Recommended)" → proceed
  - "Revise something first" → loop back to Stage 1 with current decisions as context
  - "Summarise in chat only, skip Beads" → produce markdown checklist and stop
```

**Step 2a — Explore the repo**

Before writing anything, read the codebase to understand current state. Use the project's domain vocabulary throughout the spec. Respect any ADRs in the area being touched. Do not interview the user — synthesise from the grill log and what you find.

**Step 2b — Identify test seams**

Identify the seams at which the feature will be tested:
- Prefer existing seams over new ones.
- Use the highest seam possible — the fewer seams the better; the ideal is one.
- Propose new seams only when unavoidable, at the highest point you can.

Confirm the seams with the user via AskUserQuestion before proceeding.

**Step 2c — Write the spec**

Synthesise the grill log and codebase understanding into a spec using this template:

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

Show the spec to the user. Ask if anything needs adjusting before committing to Beads.

**Step 2d — Write to Beads**

1. Check `which bd` — if missing, fall back to markdown and tell the user to install `bd`.
2. If `.beads/` doesn't exist, run `bd init --quiet`.
3. Create one epic. Title = original task (≤180 chars). Description = the full spec from Step 2c.
   ```
   bd create "<task title>" -t epic -p 1 \
     --description "<spec>" \
     --labels "pair,accepted-plan" --json
   ```
   Capture the parent ID.
4. Create one child task per atomic, independently-shippable TDD slice derived from the spec's Implementation Decisions and User Stories. Each child description includes: scope, acceptance criteria (tied to user stories), and the confirmed test seam.
   ```
   bd create "<child title>" -t task -p 1 \
     --parent <parent-id> \
     --description "<scope + acceptance criteria + seam>" \
     --labels "pair,agent-task" --json
   ```
5. Add `bd dep add` edges for any ordering the spec surfaced.
6. Add human gates for irreversible operations (migrations, schema changes, external API writes):
   ```
   bd gate create --type=human --blocks <child-id> \
     --reason "Human approval required before proceeding"
   ```
7. Show the user the compact task tree (epic ID, child IDs + one-line titles, dep edges, gates).

**Markdown fallback:** If `bd` is unavailable, produce the spec + task list as a markdown checklist and note that Beads was skipped so the user knows to install `bd` later.

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

## Stage 5 — Code Review (Two-Axis)

After the subagent returns, run a two-axis review in parallel: **Standards** (does the code follow this repo's conventions and smell baseline?) and **Spec** (does it match the bead acceptance criteria?). Both axes run as separate sub-agents so they don't pollute each other's context.

### Setup — gather inputs before spawning

```bash
# Pin the diff base (use merge-base so feature-branch noise is excluded)
git diff origin/dev...HEAD        # or origin/main...HEAD
git log origin/dev..HEAD --oneline

# Check configured thresholds for the Standards axis
cat pyproject.toml 2>/dev/null | grep -A 30"\[tool.ruff"
cat ruff.toml 2>/dev/null

# Fetch bead acceptance criteria for the Spec axis
bd list --parent <epic-id> --json
bd get <child-id> --json   # for each child
```

Confirm the diff is non-empty before spawning — an empty diff should fail here, not inside a sub-agent.

The **spec source** is the bead tasks from Stage 2 (each task has acceptance criteria in its description). No external issue or PRD lookup needed.

### Spawn both sub-agents in parallel

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

## Bead acceptance criteria (the approved spec)
<paste: each bead title + description + acceptance criteria>

## Brief
Report: (a) acceptance criteria that are missing or only partially implemented — quote the criterion; (b) behaviour in the diff that no bead asked for (scope creep); (c) criteria that appear implemented but where the implementation looks wrong. Under 400 words.
```

---

### Aggregate results

Present the two reports side by side under `## Standards` and `## Spec`. Do not merge or rerank findings across axes — a change can pass one axis and fail the other, and that distinction matters.

End with one line per axis: finding count and worst issue within that axis.

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
