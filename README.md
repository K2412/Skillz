# skillz

A curated collection of agent skills — the source of truth for my Claude Code,
Codex, and OpenCode setup. Each skill is a directory with a `SKILL.md`.

## Install / sync

```bash
bash install.sh
```

`install.sh` treats `~/.agents/skills/` as the single source of truth and:

- copies every skill dir here into `~/.agents/skills/` (replacing prior copies so
  removed files don't linger),
- regenerates `~/.agents/AGENTS.md` and symlinks `~/.claude/CLAUDE.md` to it,
- symlinks each skill into `~/.claude/skills/` and `~/.codex/skills/` (dirs that
  don't exist are skipped),
- installs the orchestrator-only instruction modules to `~/.pi/agent/instructions/`.

OpenCode reads `~/.agents/skills/` natively. Override the source-of-truth location
with `AGENTS_HOME` if needed. Restart Claude Code / OpenCode afterward to pick up
changes.

## Skills

| Skill | Description |
|-------|-------------|
| **code-review** | Review a change and give one clear merge verdict with plain-English findings and paste-ready PR comments; also builds a teaching explainer on request. Stage 5 of pair; also standalone: "review my changes against the spec", "explain this PR". |
| **grill** | Interview you relentlessly to shared understanding while maintaining the domain model (CONTEXT.md + ADRs). Asks round-by-round — the whole settled-prerequisite frontier per round — not one question at a time. Stage 1 of pair; also standalone: "grill me on this", "help me nail down the design". |
| **implement** | Execute a pre-approved GitHub plan (epic issue + task sub-issues) with strict TDD via a fresh subagent, red→green, one slice at a time. Stage 4 of pair; also standalone: "implement this plan", "build from these tickets". |
| **Learn-course** | Turn a markdown source (textbook, transcript, docs) into a directory-based course with chapters, lessons, and fill-in-the-blank exercises, then tutor you through it lesson by lesson. |
| **pair** | Orchestrator that chains the engineering skills in sequence with a human gate between each: optional research → grill → optional prototype → spec → plan-review → implement → code-review. Triggers on `/pair`, "pair with me", or describing a feature to build end-to-end. |
| **plan-review** | Senior-engineer review of a GitHub plan before any code — DRY, atomicity, missing dep edges, over-large tasks. Stage 3 of pair; also standalone: "review this plan", "poke holes in this breakdown". |
| **prototype** | Build a throwaway, interactive artifact — a driveable logic module or several radically different UI variants — to answer a design question *before* implementing, so you can feel how it behaves and decide if it's what you want. The forward bookend of code-review. Triggers on "prototype/spike/mock this up", "let me see it working first", or "does this state model feel right?". |
| **research** | Investigate a question against high-trust primary sources, web search, and Mobbin UI examples, then capture findings as a Markdown file in the repo. Optional Stage 0 of pair; also standalone. |
| **sketch-change** | Coarse, forward-looking HTML sketch of how the agent *intends* to build something — data flow, load-bearing pseudo-code, the design decisions to contest, and where it's still guessing — so you steer before any code. The forward twin of code-review; optional Stage 0.5 of pair (seeds/shortens the grill). Triggers on "sketch how you'd approach this", "show me your plan of attack first", "let me see your reasoning before you code". |
| **skill-creator** | Create, modify, and improve skills; run evals and benchmark skill performance; optimize a skill's description for better triggering. |
| **spec** | Synthesise a discussion, grill log, or resolved wayfinder map into a written spec, then open a GitHub epic issue with atomic task sub-issues in the code repo. Stage 2 of pair; also standalone: "spec this out", "turn this into tickets". |
| **to-pr** | Open a draft PR for the current branch (default base `dev`), body distilled from a code-review explainer — generating one for the whole branch first if none exists. Triggers on `/to-pr`, "make a PR for this branch", or pointing at an explainer file and wanting it made into a PR. |
| **wait-what** | User-invoked corrective for when a message didn't land — the agent re-pitches its last message with the missing context, in plain English, using your `CONTEXT.md` vocabulary. Names your state ("wait, you lost me"), not the output ("be brief"). Triggers on `/wait-what`, "wait, what?", "you lost me", "back up". |
| **wayfinder** | Plan work too big for one session as a map of decision tickets (research / prototype / grilling / task) — GitHub issues in the private `K2412/planning` repo, branch-independent, no noise in shared repos. Charts the fog, resolves tickets one per session, hands a dense map to `spec`. User-invoked: "chart a map for X", "help me wayfind this", "this is too big to plan in one go". |

## Instruction modules (`instructions/`)

Orchestrator-only guidance installed to `~/.pi/agent/instructions/` (not registered
as standalone skills): `fortify-development`, `inertia-svelte-development`,
`laravel-best-practices`, `laravel-docs-lookup`, `pest-testing`,
`tailwindcss-development`, `wayfinder-development`.
