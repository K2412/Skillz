# Investigation Workflow

## 1. Clarify scope

- Restate the user's question in technical terms.
- Identify target area: feature, module, API, incident, or commit window.
- Confirm boundaries (what is in scope, what is not).

## 2. Map the codebase

- Build a quick map with `rg --files`, `ls`, and targeted `rg -n` searches.
- Locate entrypoints, related modules, and tests.
- Capture candidate files before deep inspection.

## 3. Trace behavior

- Read key files in execution order.
- Track interfaces, data flow, side effects, and error paths.
- Prefer public interfaces and call sites over isolated internals.

## 4. Add git context

- Use read-only git commands to explain rationale and timeline:
  - `git log -- <path>`
  - `git show <commit>`
  - `git blame <file>`
  - `git grep <pattern>`
- Use commit evidence only when it improves answer quality.

## 5. Synthesize for onboarding

- Answer directly first.
- Provide evidence list (files and git refs).
- Give a practical "read next" path for a new contributor.
- Call out unknowns or assumptions.
