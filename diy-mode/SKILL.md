---
name: diy-mode
description: A muscle-building mode that gates the agent at the execution boundary — the agent does all the normal reasoning, planning, and code-reading, but instead of executing the work it writes a generalized markdown to-do list to ./DIY_TODO.md for the human to follow by hand. Use this skill whenever the user says /diy, "diy mode", "diy on", "guide me", "guide-mode", "don't write the code", "don't do the work", "just tell me what to do", "make me do it", "practice mode", "training wheels", "no auto-coding", "tell me the steps so I write it myself", or any phrasing that means "stop executing and just point me at what to build". Trigger even when the user doesn't say "diy" — if they want a to-do list of work *for them to do* (rather than for the agent to do), this is the skill. Once activated, the mode persists across every subsequent turn until the user explicitly says "/exit-diy", "diy off", or "stop diy"; do not silently drop the mode just because the request looks innocuous.
---

# diy-mode

The user feels their engineering skills are atrophying because the agent is doing the actual coding for them. This skill is a **gate at the execution boundary** of the normal agent workflow. Reasoning, reading the codebase, asking clarifying questions, grilling the plan, writing Beads tasks — all of that proceeds exactly as it would normally. The only difference is the final step: **instead of editing files, the agent writes a generalized to-do list and hands the work back to the human.**

The point is muscle-building. Every line of code the agent writes is a rep the user didn't do. So diy-mode is unapologetically strict about that boundary, while staying maximally useful as a *thinking partner*.

## When this skill is active

Treat the mode as a **persistent flag on the conversation**. Once any trigger phrase fires (`/diy`, "diy mode", "guide me", "don't write the code", "practice mode", etc.), every subsequent turn in the same conversation operates under the rules in this file — including turns where the user's next message looks like an ordinary coding request. Do not drop the mode because the user said "ok now add X" without re-invoking; that's the most common failure mode and it defeats the whole point. The mode only ends when the user explicitly types `/exit-diy`, "diy off", "stop diy", or an equivalent unambiguous exit phrase.

When in doubt about whether the mode is active, err on the side of *staying in diy-mode*. The cost of refusing to write code when the user actually wanted you to is a five-second exit phrase. The cost of silently writing code when the user wanted to practice is the entire purpose of the skill, lost.

## The gate: what's blocked vs what's allowed

The agent's behavior outside the execution step is unchanged. Read freely, think freely, plan freely. The blocked operations are specifically the ones that *do the work for the user*.

**Blocked (the gate):**
- `Edit`, `Write`, `MultiEdit`, `NotebookEdit` on any source file in the user's codebase
- Mutating git operations: `git commit`, `git push`, `git merge`, `git rebase`, `git reset --hard`, `git checkout -- ...`, branch deletion
- Running migrations, seeders, codegen, formatters that rewrite files, or any script whose effect is to modify the repo
- Installing or updating dependencies (`pnpm add`, `npm install <pkg>`, `pip install`, `cargo add`, etc.) — that's part of the work
- Anything else whose primary effect is to leave the repo in a different state than it started

**Allowed (still useful):**
- `Read`, `Grep`, `Glob` — read the codebase as much as needed to ground the to-do
- `Bash` for read-only commands: `git status`, `git log`, `git diff`, `git blame`, `ls`, `pwd`, `which`, etc.
- Running tests, linters, type-checkers, and other verifiers — these *inspect* state, they don't change it. If the user wants to verify their own work, the agent can run `pnpm test` for them.
- `WebFetch` / `WebSearch` for documentation lookups
- Invoking other read-only skills (e.g., `grill-me`, planning skills, codebase explanation skills)
- Writing to Beads (`bd create`, `bd update`, `bd dep add`) — the durable plan lives there
- Writing to `./DIY_TODO.md` — this is the skill's own output artifact, *not* source

**The one explicit exception:** `./DIY_TODO.md` itself. That file *is* the output of diy-mode. Writing to it is not "doing the work" — it's the deliverable.

## Producing the to-do list

The deliverable is `./DIY_TODO.md` at the repo root. The agent should always print a brief summary in chat as well, but the file is canonical.

**File lifecycle.** A single rolling file. Each invocation appends a new dated section — do not overwrite prior sessions, the user wants the history. If the file doesn't exist yet, create it with a one-line header. If `./.gitignore` doesn't already list `DIY_TODO.md`, ask the user once whether they want it gitignored; if yes, add the line. Don't ask again on subsequent invocations in the same session.

**Section format.** Append a section like this for each new request:

```
## YYYY-MM-DD HH:MM — <one-line summary of the task>

- [ ] <imperative verb> <what> in <where>: <one-line constraint or why>
- [ ] ...
```

Use the current date/time from the environment context (the system provides "Today's date"). The `HH:MM` can be omitted if the agent has no reliable clock — date alone is enough to keep history readable.

**Granularity.** One checkbox per file-or-function change. Specific enough that the user knows where to look and what to do; vague enough that they still have to think.

Good:
- `add created_at TIMESTAMPTZ column to users table in db/schema.ts (default now(), not null)`
- `add formatRelativeDate(date) helper in lib/date.ts — needs to handle null and future dates`
- `wire the new column into the response shape in app/api/users/route.ts`

Too coarse (do not do this):
- `add user timestamps`
- `update the UI`

Too detailed (do not do this):
- Anything with a code block, snippet, function body, type signature, regex, JSON shape, or pseudo-code
- "Here's the migration file: ```sql ...```"
- "The function should be: `function formatDate(d: Date | null): string`"

The whole point is that the user writes the code. If the to-do contains the code, the user is just transcribing.

**No code, anywhere.** Not in fences, not inline as backticked identifiers used to *teach*. Backticked identifiers used to *name* an existing file, column, or symbol are fine — `db/schema.ts` and `created_at` are names, not implementations. If you find yourself writing what amounts to pseudo-code in prose, stop and rewrite as a constraint.

**When the plan came from Beads.** If the user has already grilled the plan and there are Beads tasks for this work, render the DIY_TODO.md section *from the Beads tasks* — one checkbox per child task, preserving order. Note dependencies in the bullet text (e.g., "after #2"). Beads remains the durable record; DIY_TODO.md is the working surface the user actually ticks through.

## When the user comes back to you

The user works through the list by hand, then returns saying things like "done with #3", "stuck on #5", "is this right?", "I added the column but the test fails". Stay in diy-mode. The agent's job in these turns:

1. **Read what the user did.** `git diff`, read the relevant files, run tests if they want. The agent can investigate freely.
2. **Review honestly.** Point at issues directly. If the column they added doesn't have the constraint the to-do mentioned, say so. If the test is failing because of a typo on line 42, name the line.
3. **Hint, don't fix.** When the user is stuck, give **prose hints only**: concepts to look up, patterns by name, what to read, the *shape* of the answer in plain English. No code, no type signatures, no pseudo-code, no copy-pasteable snippets. Naming a function or column the user already has on screen is fine (that's pointing); inventing the signature of a function they haven't written yet is not (that's doing).
4. **Tick the box.** When the user confirms they've finished an item, edit `./DIY_TODO.md` to change `- [ ]` to `- [x]` for that item. This is allowed — same exception as creating the file.
5. **Surface the next item.** Read the next unchecked item from `./DIY_TODO.md` and remind the user what it is.

If during review the user's approach is genuinely wrong (not just different from how the agent would do it), explain *why* in prose. The user might want to update the to-do — that's fine, edit `DIY_TODO.md` to reflect the new plan.

## The escape hatch (there isn't one)

Users will, at some point, get frustrated and say "just write it for me" or "do #5, I'm tired". This is exactly the moment the skill exists for. **Hard refuse.** A response like:

> I'm staying in diy-mode — that's the whole point. If you genuinely want me to write the code, say `/exit-diy` (or "diy off") first and I'll switch back to normal behavior on the next turn. Otherwise tell me where you're stuck and I'll hint.

Do not negotiate, do not partially comply, do not write "just this once". The friction is the feature. The user can drop the mode in one phrase if they really want to; making them say it explicitly is the entire muscle-building mechanism.

## Exiting diy-mode

Only an explicit exit phrase ends the mode:

- `/exit-diy`
- "diy off"
- "stop diy"
- "exit diy mode"
- or any other phrasing that unambiguously says *end the mode*

After exit, the next turn returns to normal agent behavior. The agent can acknowledge the exit briefly ("Back to normal mode") but should not retroactively complete any of the DIY_TODO.md items the user hadn't ticked off — those stay in the file as a record.

## Why this works

The mode is intentionally annoying in exactly one direction: it refuses to write code. Everything else — reading, reasoning, reviewing, hinting, running tests, grilling plans, tracking work in Beads — is unchanged. That keeps the agent useful as a thinking partner while forcing every keystroke of actual code through the user's fingers. Over time, those keystrokes are the muscle.
