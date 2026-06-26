---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.

Ask the questions one at a time. For EVERY question, you MUST use the AskUserQuestion tool so the user can pick from selectable options instead of typing free-text answers.

For each question:
- Generate 2-4 concrete answer options.
- Put your recommended answer first and append "(Recommended)" to its label.
- Make options mutually exclusive and specific to this plan (no generic "Option A / B").
- Keep the question text tight; put nuance in each option's description field.
- Users will always have "Other" available, so don't force a fit when the answer space is genuinely open.

If a question can be answered by exploring the codebase, explore the codebase instead of asking.

## Output: write the accepted plan to Beads

When the interview has resolved every open branch and the user signals they're ready to execute (phrases like "let's go", "ship it", "ready", "do it", or any clear go-ahead), the **default output is a Beads-backed task graph** — not a markdown summary. The whole point of grilling is to surface the decision tree; the most durable place to put that tree is Beads, where each decision becomes a tracked task with explicit dependencies and human gates.

Before writing anything, **confirm with the user via AskUserQuestion** that they want the plan committed to Beads (offer "Yes, write to Beads (Recommended)" / "Just summarize in chat, no Beads" / "Both"). Skip this only if the user explicitly said "save to Beads" already.

### Beads conventions (match the rest of this codebase)

1. **Init if needed.** If `.beads/` doesn't exist in the working directory, run `bd init --quiet`. If `bd` isn't on PATH, fall back to the markdown summary and tell the user what to install (`brew install beads-tools/beads/bd` or the equivalent — confirm with `which bd` first).
2. **Parent epic.** One epic per grilled plan. Title is the original task (truncate to ~180 chars). Description includes the full list of resolved decisions in `Q: ... / A: ...` form.
   ```
   bd create "<task title>" -t epic -p 1 \
     --description "<decision log>" \
     --labels "grill-me,accepted-plan" --json
   ```
   Capture the parent ID from the JSON output.
3. **Child tasks.** One child per atomic, independently-shippable scope — not one per question. A child should map to a single TDD slice (red → green → refactor). Don't create one giant child.
   ```
   bd create "<child title>" -t task -p 1 \
     --parent <parent-id> \
     --description "<scope, acceptance criteria, decisions relevant to this slice>" \
     --labels "grill-me,agent-task" --json
   ```
4. **Dependency edges.** Whenever the interview surfaced ordering ("A must land before B"), record it:
   ```
   bd dep add <blocked-child> <blocking-child>
   ```
5. **Human gates.** For irreversible or high-blast-radius decisions (production migrations, schema changes, deletes, external API keys), create a gate so execution can't proceed without explicit approval:
   ```
   bd gate create --type=human --blocks <child-id> \
     --reason "Human approval required before proceeding"
   ```
   Tag the gated child with the `human-gate` label.
6. **Report back.** After writing, show the user a compact tree: epic ID, child IDs with one-line titles, and any dependency/gate edges. They should be able to start work immediately with `bd ready --json`.

### Markdown fallback

If `bd` is unavailable, produce the same structure as a markdown checklist (Epic → children → blockers → gates) and explicitly note that Beads was skipped because the CLI was missing. Don't silently degrade — the user should know they got the fallback so they can install `bd` later if they want the durable version.
