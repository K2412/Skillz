# skillz

A curated collection of 34 skills for Claude Code / Codex CLI — a mix of skills I've built and ones I've discovered and found useful. Organized by category prefix.

## Restore

```bash
bash install.sh
```

Copies all skill dirs to `~/.agents/skills/` (or `$AGENTS_HOME/skills`). Restart Claude Code afterward.

---

## Categories

### Design- (18 skills)

| Skill | Description |
|-------|-------------|
| Design-adapt | Adapt designs to work across different screen sizes, devices, contexts, or platforms |
| Design-animate | Enhance features with purposeful animations, micro-interactions, and motion effects |
| Design-audit | Comprehensive audit of interface quality across accessibility, performance, theming, and responsive design |
| Design-bolder | Amplify safe or boring designs to make them more visually interesting and stimulating |
| Design-clarify | Improve unclear UX copy, error messages, microcopy, labels, and instructions |
| Design-colorize | Add strategic color to features that are too monochromatic or lack visual interest |
| Design-context | One-time setup that gathers design context and saves it to your AI config file |
| Design-critique | Evaluate design effectiveness from a UX perspective with actionable feedback |
| Design-delight | Add moments of joy, personality, and unexpected touches that make interfaces memorable |
| Design-distill | Strip designs to their essence by removing unnecessary complexity |
| Design-extract | Extract and consolidate reusable components, design tokens, and patterns into your design system |
| Design-frontend | Create distinctive, production-grade frontend interfaces with high design quality |
| Design-harden | Improve interface resilience through better error handling, i18n support, and edge case management |
| Design-normalize | Normalize design to match your design system and ensure consistency |
| Design-onboard | Design or improve onboarding flows, empty states, and first-time user experiences |
| Design-optimize | Improve interface performance across loading speed, rendering, animations, and bundle size |
| Design-polish | Final quality pass before shipping — fixes alignment, spacing, consistency, and detail issues |
| Design-quieter | Tone down overly bold or visually aggressive designs while maintaining impact |

### Code- (4 skills)

| Skill | Description |
|-------|-------------|
| Code-ai-audit | Audits a repository for AI-agent-friendliness and produces a prioritised improvement plan |
| Code-architecture | Explore a codebase to find opportunities for architectural improvement and deeper modules |
| Code-tdd | Test-driven development with red-green-refactor loop |
| Code-tutor | Generate a beginner-friendly Markdown tutorial from any local codebase or GitHub repository |

### Plan- (5 skills)

| Skill | Description |
|-------|-------------|
| Plan-issues | Break a PRD into independently-grabbable GitHub issues using tracer-bullet vertical slices |
| Plan-ralph-loop | AFK continuous autonomous loop that processes GitHub Issues one by one |
| Plan-ralph-once | Human-in-the-loop single-iteration issue processor — runs one ralph pass then stops |
| Plan-super | Converts an idea into repo artifacts and dependency-aware tickets using a 7-phase framework |
| Plan-workflow-miner | Mines session logs for repeated tool sequences and outputs automation recommendations |

### Domain- (2 skills)

| Skill | Description |
|-------|-------------|
| Domain-dagster | Expert guidance for working with Dagster and the dg CLI |
| Domain-python | Production Python coding standards with automatic version detection (3.10–3.13) |

### Learn- (2 skills)

| Skill | Description |
|-------|-------------|
| Learn-socratic | Socratic coaching mode — guides learning through questions instead of direct answers |
| Learn-track | Generate a text-based programming course from a local directory corpus |

### Meta- (3 skills)

| Skill | Description |
|-------|-------------|
| Meta-create | Guide for creating effective new skills |
| Meta-find | Discover and install agent skills for tasks you want to extend |
| Meta-install | Install Codex skills into `$CODEX_HOME/skills` from a curated list or GitHub repo |
