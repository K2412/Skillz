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
- when the sibling `agent-memory` checkout is present, installs its common stdio command, initializes
  keychain-backed encrypted storage, and idempotently registers it with all three clients.

OpenCode reads `~/.agents/skills/` natively. Override the source-of-truth location
with `AGENTS_HOME` if needed. Restart Claude Code / OpenCode afterward to pick up
changes.
Set `AGENT_MEMORY_SOURCE` when the memory-service checkout is not beside this repository.

## Skills

| Skill | Description |
|-------|-------------|
| **architecture** | Diagnose architecture from real change pressure, let the human choose between deeper module designs, encode the choice as an executable architecture contract, and checkpoint bounded agent work for drift. Standalone or conditional stage of pair. |
| **code-review** | Review a change and give one clear merge verdict with plain-English findings and paste-ready PR comments; also builds a teaching explainer on request. Stage 5 of pair; also standalone: "review my changes against the spec", "explain this PR". |
| **explain-this-like-I-am-an-intern** | User-invoked way to get clarity on anything — a subject you want to finally understand, or a message the agent just made that didn't land. Re-explains from scratch as if to a bright intern on their first day (missing premise + why first, every term glossed, plain English, a concrete example), then probes with a question or two to check it landed. Absorbs `wait-what` and folds in the teaching ethos of `soc`/`teach`. Triggers on `/explain-this-like-I-am-an-intern`, "eli-intern", "you lost me", "wait, what?", "explain this like I'm an intern". |
| **grill** | Interview you relentlessly to shared understanding while maintaining the domain model (CONTEXT.md + ADRs). Asks round-by-round — the whole settled-prerequisite frontier per round — not one question at a time. Stage 1 of pair; also standalone: "grill me on this", "help me nail down the design". |
| **implement** | Execute a pre-approved GitHub plan through fresh subagents, one test-backed behavioral batch at a time inside a human-approved architecture contract. Returns at human and architecture checkpoints. |
| **pair** | Orchestrator that chains understanding, an optional architecture fence, planning, bounded implementation batches, architecture checkpoints, and review. Triggers on `/pair`, "pair with me", or describing a feature to build end-to-end. |
| **plan-review** | Senior-engineer review of a GitHub plan before any code — DRY, atomicity, missing dep edges, over-large tasks. Stage 3 of pair; also standalone: "review this plan", "poke holes in this breakdown". |
| **prototype** | Build a throwaway, interactive artifact — a driveable logic module or several radically different UI variants — to answer a design question *before* implementing, so you can feel how it behaves and decide if it's what you want. The forward bookend of code-review. Triggers on "prototype/spike/mock this up", "let me see it working first", or "does this state model feel right?". |
| **research** | Investigate a question against high-trust primary sources, web search, and Mobbin UI examples, then capture findings as a Markdown file in the repo. Optional Stage 0 of pair; also standalone. |
| **sketch-change** | Coarse, forward-looking HTML sketch of how the agent *intends* to build something — data flow, load-bearing pseudo-code, the design decisions to contest, and where it's still guessing — so you steer before any code. The forward twin of code-review; optional Stage 0.5 of pair (seeds/shortens the grill). Triggers on "sketch how you'd approach this", "show me your plan of attack first", "let me see your reasoning before you code". |
| **skill-creator** | Create, modify, and improve skills; run evals and benchmark skill performance; optimize a skill's description for better triggering. |
| **spec** | Synthesise a discussion, grill log, architecture contract, or resolved wayfinder map into a written spec, then open a GitHub epic with bounded behavioral tasks in `K2412/planning`. |
| **to-pr** | Open a draft PR for the current branch (default base `dev`), body distilled from a code-review explainer — generating one for the whole branch first if none exists. Triggers on `/to-pr`, "make a PR for this branch", or pointing at an explainer file and wanting it made into a PR. |
| **wayfinder** | Plan work too big for one session as a map of decision tickets (research / prototype / grilling / task) — GitHub issues in the private `K2412/planning` repo, branch-independent, no noise in shared repos. Charts the fog, resolves tickets one per session, hands a dense map to `spec`. User-invoked: "chart a map for X", "help me wayfind this", "this is too big to plan in one go". |

## Instruction modules (`instructions/`)

Orchestrator-only guidance installed to `~/.pi/agent/instructions/` (not registered
as standalone skills): `fortify-development`, `inertia-svelte-development`,
`laravel-best-practices`, `laravel-docs-lookup`, `pest-testing`,
`tailwindcss-development`, `wayfinder-development`.
