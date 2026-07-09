---
name: commit-summary
description: Summarize recent git commits in plain English. Use this skill whenever the user says "commit summary", "summarize commits", "what changed today", "what did I work on", "git summary", "show me recent changes", "what have I committed", or invokes /commit-summary. Also trigger when the user asks for a summary of recent work in a repo, even if they don't say "commit" explicitly.
---

# Commit Summary

Generate a clear, human-readable summary of recent git commits across one or more repositories.

## Step 1: Scan for repos

Run this to find all git repos on the system (capped at depth 6 to stay fast):

```bash
find ~ -maxdepth 6 -name ".git" -type d 2>/dev/null | sed 's|/.git||' | sort
```

## Step 2: Ask the user which repos to include

Use `AskUserQuestion` with `multiSelect: true`. Present each found repo as an option, using the short folder name as the label and the full path as the description. Cap at 20 repos — if more are found, prefer repos under `~/Developer`, `~/Projects`, `~/code`, `~/work`, or similar dev-looking directories, and note that you limited the list.

Example structure:
```
question: "Which repos would you like to summarize?"
header: "Repos"
multiSelect: true
options: [
  { label: "signal-lift", description: "~/Developer/signal-lift" },
  { label: "my-app",      description: "~/Projects/my-app" },
  ...
]
```

## Step 3: Ask the time scope

Use a second `AskUserQuestion` (single-select) to ask how far back to look:

```
question: "How far back should I look?"
header: "Time range"
options: [
  { label: "Last 24 hours",  description: "Commits since yesterday" },
  { label: "Last 7 days",    description: "This past week" },
  { label: "Last 30 days",   description: "This past month" },
  { label: "Last N commits", description: "I'll specify a number" }
]
```

If the user picks "Last N commits", follow up with a plain question asking for the number (you can just ask inline in chat — no need for another AskUserQuestion for a single free-text value).

## Step 4: Gather commits from each selected repo

For each selected repo path, run:

```bash
# Commits
git -C <repo-path> log --since="<time>" --pretty=format:"%h %s" --no-merges

# Most-touched files
git -C <repo-path> log --since="<time>" --name-only --pretty=format:"" --no-merges \
  | sort | uniq -c | sort -rn | head -10
```

For count-based scope, replace `--since` with `-n <N>`.

## Step 5: Summarize

For each repo, group commits by type and write a short plain-English summary:
- Features / new functionality
- Bug fixes
- Refactors / cleanup
- Config / tooling / deps
- Docs / tests

If a repo has no commits in the window, say so briefly and move on.

## Output format

```
# Commit Summary — [time range]

## [repo-name]
[Plain English description of the work, grouped by theme. 2-4 sentences max per group.]

Top files touched:
- path/to/file.ts (N changes)
- ...

[N commits]

---

## [next-repo]
...
```

If only one repo was selected, skip the per-repo header and just write the summary directly.
