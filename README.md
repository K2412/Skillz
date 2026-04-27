# skillz

A curated collection of 19 skills for Claude Code / Codex CLI — a mix of skills I've built and ones I've discovered and found useful. Organized by category prefix.

## Restore

```bash
bash install.sh
```

Copies all skill dirs to `~/.agents/skills/` (or `$AGENTS_HOME/skills`). Restart Claude Code afterward.

---

## Categories

### Design- (3 skills)

The design system is two routers plus a one-time setup skill. The 17 specialist prompts (audit, critique, polish, animate, etc.) live as bundled markdown inside the routers — they're loaded on demand, not registered as standalone skills.

| Skill | Description |
|-------|-------------|
| **Design-review** | Read-only evaluation of an existing UI. Loads `specialists/audit.md` (technical: a11y, perf, theming, responsive) or `specialists/critique.md` (UX: hierarchy, IA, slop detection) based on what the user asks for. |
| **Design-improve** | Active design work — polish, restyle, animate, recolor, simplify, harden, adapt, optimize, build new UI. Loads one of 16 specialists in `specialists/` (polish, harden, normalize, bolder, quieter, colorize, animate, delight, clarify, distill, adapt, onboard, optimize, extract, frontend) plus shared design principles in `specialists/frontend-reference/`. |
| Design-setup | One-time setup that gathers design context and saves it to your AI config file. |

**Architecture note**: previously each specialist was its own skill (18 total under `Design-*/`). Restructured so `git clone` + `bash install.sh` reliably yields only these three Design entry points — no version-dependent flags involved.

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
