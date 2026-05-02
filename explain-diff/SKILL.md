---
name: explain-diff
description: Generate a self-contained markdown walkthrough of the changes on a git branch. Use this whenever the user wants a breakdown of branch changes, a PR walkthrough doc, a pre-review writeup, or any "what changed and why" summary for a feature branch. Trigger on phrases like "breakdown of all changes in this branch", "summarize this branch for review", "walk me through my changes", "PR walkthrough doc", "explain this diff", "/explain-diff", or any request for a markdown summary of a git diff. Prefer this over /explain-concept when the user references a branch, diff, PR, or their recent work — even without naming the skill.
---

# explain-diff

Generates a single markdown file that walks a reviewer through the changes on a git branch. The doc is scoped to the diff — it groups changed files into themes, shows unified diffs for the most important ones, and calls out risks and things reviewers should verify.

## Input

Parse the user's argument string for:

- `--base=<ref>` (optional) — base ref to diff against. If omitted, auto-detect (see Step 1).
- `--paths=<glob>` (optional) — restrict the diff to paths matching this glob.
- `--source=<path>` (optional) — repo root. Default: current working directory.
- `--out=<path>` (optional) — output markdown path. Default: `./output/<project>/diff-<base>-<head_short>.md`.
- `--max-files=<n>` (optional) — hard cap on files fed to section-write. Default: 30.

## Pipeline

Seven steps. Run in order.

### Step 1: Resolve base ref

If `--base` was supplied, use it. Otherwise auto-detect in order:
1. `git symbolic-ref refs/remotes/origin/HEAD | sed 's|^refs/remotes/origin/||'` → if non-empty, use it.
2. Check local branches in priority order — `dev`, `main`, `master`. First one that exists wins.
3. If none exist, tell the user explicitly that base detection failed and ask for `--base=<ref>`.

Also compute the short head SHA: `git rev-parse --short HEAD`.

### Step 2: List changed files

Run the diff script:

```bash
python3 <skill-dir>/scripts/diff_files.py --base <base> --source <source> [--paths <glob>]
```

Output is JSON `{files: [{path, status, adds, dels}], base: "<base>", head: "<sha>"}`.

If `files` is empty, tell the user there are no changes vs `<base>` and stop.

If `len(files) > max_files`, proceed — Step 3's triage will cap it.

### Step 3: LLM expand + triage

Feed the diff file list + stats to the LLM via the **Triage Diff Files** prompt in [references/prompts.md](references/prompts.md). The LLM:
1. Keeps the changed files that matter for understanding (drops trivial renames, generated files, lockfile churn).
2. Adds up to 5 unchanged context files that make the diff legible (callers, interface definitions).

Cap output at `max_files`. Warn the user if files were dropped and show which.

### Step 4: Read file contents and diffs

For each triaged path, grab:
- Current content: read the file.
- Diff hunks: `git diff <base>...HEAD -- <path>`.

Build an indexed context string with each file's diff (or current content for unchanged context files). Label unchanged context files as "context" in the index.

### Step 5: Identify change themes

Use the **Identify Change Themes** prompt from [references/prompts.md](references/prompts.md). Themes are not files — they are coherent groups of changes that share a motivation (e.g. "schema migration for tenant field", "UI chrome refactor", "new scorecard chip component"). Aim for 3-6 themes.

Parse YAML. Each theme has `name`, `description`, `file_indices`, `risk_level` (`low|medium|high`).

### Step 6: Analyze flow & write section content

Use the **Analyze Diff Flow** prompt to produce an overall narrative summary and a mermaid diagram showing which modules the themes touch (not detailed relationships — just a map).

For each theme, use the **Write Theme Section** prompt to produce one markdown section containing:
- `## {theme name}` heading
- 3-5 bullet intro: what changed, why, what operational difference it makes, risk callout if `high` risk
- One unified-diff fenced block (` ```diff `) with the representative hunks, ≤ 25 lines
- One short paragraph pointing at the non-obvious thing

Also generate two framing sections via dedicated prompts:
- **Risks & testing section** — roll up risks across all themes, explicitly list manual test paths.
- **Reviewer checklist section** — actionable markdown list of things the reviewer should verify.

No speaker notes — prose carries all the context directly. Anything that used to go in `<aside class="notes">` ("what was tried and rejected", "what to watch post-merge") gets folded into the section prose itself.

### Step 7: Assemble markdown and write file

Compose the final `.md` content in this fixed order (see [references/output-template.md](references/output-template.md) for the skeleton):

1. `# {branch} vs {base}` — title H1
2. `_{N} files · +{adds}/-{dels} · HEAD {head_sha}_` — stats italic line
3. `## Summary` — narrative summary from Step 6
4. Mermaid module map in a ` ```mermaid ` fenced block (no surrounding heading — reads as an inline diagram)
5. `## {Theme name}` × N — per-theme sections in reviewer-priority order
6. `## Risks & testing`
7. `## Reviewer checklist`

Ensure the parent directory of `--out` exists (`mkdir -p`), then write the composed markdown to that path using the Write tool.

## Fixed section order (diff mode)

Section count = `4 + N + 2` where N = theme count. (Title, stats, Summary, mermaid, N themes, Risks & testing, Reviewer checklist.)

## Output

Print to the user:
- Output markdown path
- Number of themes, section count
- Base ref used and how it was resolved
- Any files dropped due to `--max-files` cap

Do not auto-open the file.

## Error handling

- Not a git repo → tell the user explicitly.
- `git diff` returns 0 files → "no changes vs `<base>`, nothing to explain".
- `>max_files` files → keep top-N as ranked by LLM, warn which were dropped. Suggest `--paths=` to narrow.
- Invalid YAML at any LLM step → retry up to 3 times.

## Related

- Sibling `/explain-concept` — same markdown format but scoped to a code concept instead of a branch diff.
- Base `/codebase-tutorial` — whole-codebase tutorial written as multi-chapter markdown. Different scope, similar output medium.
