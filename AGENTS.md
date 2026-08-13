# Agent Instructions

## Non-Interactive Shell Commands

**ALWAYS use non-interactive flags** with file operations to avoid hanging on confirmation prompts.

Shell commands like `cp`, `mv`, and `rm` may be aliased to include `-i` (interactive) mode on some systems, causing the agent to hang indefinitely waiting for y/n input.

**Use these forms instead:**
```bash
# Force overwrite without prompting
cp -f source dest           # NOT: cp source dest
mv -f source dest           # NOT: mv source dest
rm -f file                  # NOT: rm file

# For recursive operations
rm -rf directory            # NOT: rm -r directory
cp -rf source dest          # NOT: cp -r source dest
```

**Other commands that may prompt:**
- `scp` - use `-o BatchMode=yes` for non-interactive
- `ssh` - use `-o BatchMode=yes` to fail instead of prompting
- `apt-get` - use `-y` flag
- `brew` - use `HOMEBREW_NO_AUTO_UPDATE=1` env var


---

<!-- Claude Code context (merged from CLAUDE.md) -->

# Project Instructions for AI Agents

This file provides instructions and context for AI coding agents working on this project.



## Build & Test

_Add your build and test commands here_

```bash
# Example:
# npm install
# npm test
```

## Architecture Overview

_Add a brief overview of your project architecture_

## Conventions & Patterns

_Add your project-specific conventions here_


<!-- skillz:available-skills -->
## Available Skills

Skills load automatically from `~/.agents/skills/` (shared across Claude Code, Codex, and OpenCode). Invoke with `/skill-name` or just describe what you need:

- **`/best-practices`** — Apply stack-specific engineering best-practices for a stack the caller names — Vercel's React/Next.js performance guidance for `react`, the…
- **`/data-viz-selection`** — Pick the right chart for a dataset and message, then design it well.
- **`/experts`** — Reach the `experts` MCP gateway from any message — a local server holding 11 domain corpora (software_engineer, python, laravel, ai_engineer,…
- **`/explain-diff`** — Generate a teaching-oriented HTML explainer for a code change — a diff, staged/unstaged work, a branch, a commit range, or a GitHub PR — that walks…
- **`/grill`** — Interview the user relentlessly about an idea until you reach shared understanding, while actively maintaining the project's domain model (glossary +…
- **`/implement`** — Execute a pre-approved GitHub plan using strict TDD — spawning a fresh subagent that works each task red→green, one vertical slice at a time, at…
- **`/Learn-course`** — Convert a markdown source (textbook, lecture transcript, open-source library docs) into a directory-based learning course with chapters, lessons, and…
- **`/pair`** — Full spec-to-ship pipeline that orchestrates the individual engineering skills in sequence with a human gate between each — optional research, then…
- **`/plan-review`** — Review a GitHub plan (an epic issue and its child task sub-issues) with a senior-engineer eye before any code is written — checking for DRY…
- **`/polish`** — Polish a change set clean and simple before it goes up for review — the final cleanup pass that makes a diff read like a careful teammate wrote it,…
- **`/prototype`** — Build a throwaway, interactive prototype that answers a design question BEFORE you commit to implementing — so you can engage with real running logic…
- **`/research`** — Investigate a question against high-trust primary sources, web search, site scraping and crawling (Firecrawl), and Mobbin UI examples, then capture…
- **`/review-all`** — One command to both evaluate and explain a pull request.
- **`/review-change`** — Review a code change on two independent axes at once — Standards (does it follow this repo's conventions and the Fowler smell baseline?) and Spec…
- **`/sketch-change`** — Generate a coarse, forward-looking HTML sketch of how you INTEND to build something — the data flow, the key state, pseudo-code for the load-bearing…
- **`/skill-creator`** — Create new skills, modify and improve existing skills, and measure skill performance.
- **`/spec`** — Synthesise a discussion, grill log, rough idea, or a resolved wayfinder map into a written spec (problem, solution, user stories, implementation +…
- **`/standup`** — Generate a standup update from recent activity.
- **`/taste-review`** — Make a taste call — an independent judgment call on something ambiguous where you'd otherwise guess: UI polish, prose phrasing, naming, formatting,…
- **`/to-pr`** — Open a draft pull request for the current branch, with a Markdown body distilled from an explain-diff explainer.
- **`/wait-what`** — User-invoked corrective for when a message didn't land — you type it the moment you notice you're skimming, lost in invented jargon, or reading a…
- **`/wayfinder`** — Plan a chunk of work too big for one session — wrapped in fog, where the way from here to the destination isn't visible yet — as a shared map of…

> Skill source of truth: `~/.agents/skills/` — managed via the Skillz repo. Run its `install.sh` to sync.
<!-- /skillz:available-skills -->
