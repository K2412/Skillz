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

- **`/diagnosing-bugs`** — Diagnosis loop for hard bugs and performance regressions.
- **`/find-skills`** — Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or…
- **`/Learn-course`** — Convert a markdown source (textbook, lecture transcript, open-source library docs) into a directory-based learning course with chapters, lessons, and…
- **`/pair`** — Full spec-to-ship pipeline with built-in grilling, plan review, subagent execution, and code review.
- **`/research`** — Investigate a question against high-trust primary sources, web search, and Mobbin UI examples, then capture findings as a Markdown file in the repo.
- **`/skill-creator`** — Create new skills, modify and improve existing skills, and measure skill performance.
- **`/to-pr`** — Turn an explain-diff explainer HTML file into a Markdown PR description and open a draft pull request for the current branch.

> Skill source of truth: `~/.agents/skills/` — managed via the Skillz repo. Run its `install.sh` to sync.
<!-- /skillz:available-skills -->
