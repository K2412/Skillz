# LLM Prompts — explain-diff

Substitute `{placeholders}` at call time. All YAML outputs must parse cleanly — retry on parse failure. Markdown section prompts emit raw markdown — no wrapping fences.

## Triage Diff Files

Used in Step 3. The LLM keeps relevant changed files and optionally adds up to 5 unchanged context files to make the diff legible.

```
Branch `{head_branch}` vs base `{base_ref}` in project `{project_name}`.

Changed files (with line counts):
{diff_file_listing}

Unchanged file listing (for context selection — pick at most 5):
{unchanged_file_listing}

Your task:
1. Keep the changed files that matter for understanding the intent of this branch. Drop pure churn (lockfile bumps, generated code, mechanical renames, trivial formatting).
2. Optionally add up to 5 UNCHANGED files that a reviewer needs open to make sense of the diff — e.g. the interface being implemented, a caller whose behavior now depends on the new signature, a config key definition.

Return at most {max_files} total. Rank by importance — most load-bearing file first.

Format as YAML. Each entry has `path` and `role` (`changed` or `context`):

```yaml
- path: api/auth/middleware.py
  role: changed
- path: api/auth/sessions.py
  role: context
```
```

## Identify Change Themes

Used in Step 5. Themes are the unit of explanation — not files, but coherent groups of changes.

```
Branch `{head_branch}` vs base `{base_ref}`.

Context (file paths, diffs, and context files):
{context}

List of file indices and paths present in the context:
{file_listing}

Analyze the changes and group them into 3-6 coherent THEMES. A theme is a set of changes that share a single motivation — e.g. "add tenant_id to core schema", "replace polling with websocket push", "rename `user` to `principal` everywhere".

Avoid one theme per file. Avoid one theme for the whole branch.

For each theme, provide:
1. `name`: concise (3-6 words).
2. `description`: what changed and why it changed, 50-80 words.
3. `file_indices`: indices of files belonging to this theme.
4. `risk_level`: one of `low`, `medium`, `high`. Use `high` for schema/migration/auth changes, `medium` for API contract changes, `low` for refactors and UI polish.

Order themes by reviewer priority — read this first, read that last.

Format as YAML list:

```yaml
- name: |
    Add tenant_id to scorecard schema
  description: |
    Scorecards now belong to a tenant. Schema gains a NOT NULL tenant_id
    column (with backfill migration). Every read path gets a tenant filter.
  file_indices:
    - 3 # api/models/scorecard.py
    - 4 # api/migrations/0042_tenant_id.py
  risk_level: high
- name: |
    Scorecard chip component
  description: |
    New reusable chip for rendering scorecard status in lists.
  file_indices:
    - 7 # api/app/dashboard/dashboard/components/scorecard_chip.py
  risk_level: low
```
```

## Analyze Diff Flow

Used in Step 6 to produce the narrative summary and module map.

```
Branch `{head_branch}` vs base `{base_ref}`.

Themes (Index # Name, risk):
{theme_listing}

Context (themes with descriptions and relevant diffs):
{context}

Provide:
1. A `summary` the reviewer could paste into a PR description. 3-5 sentences. Use markdown **bold** for key terms. Be specific about what operationally changes.
2. A `module_map`: a mermaid flowchart showing which modules/directories are touched by which themes. Use theme index as node label shorthand (T0, T1, ...) and module/dir as node label.

Format as YAML:

```yaml
summary: |
  This branch adds **multi-tenant isolation** to scorecards.
  Schema grows a `tenant_id` column; all reads filter by it.
  The UI gains a tenant picker and a new scorecard chip component.
module_map: |
  flowchart LR
      T0["T0: tenant_id schema"] --> M_api["api/models"]
      T0 --> M_mig["api/migrations"]
      T1["T1: scorecard chip"] --> M_dash["api/app/dashboard"]
```
```

## Write Theme Section

Used in Step 6. Called once per theme. Produces one markdown section combining intent prose and a unified-diff code block.

```
Theme {theme_num} of {total_themes}: "{theme_name}" (risk: {risk_level})

Description:
{theme_description}

Relevant files & diffs (pick the 1-2 most illustrative hunks for the code block):
{file_context}

Where this theme sits in the overall branch:
{flow_summary}

Write ONE markdown section:

1. `## {theme_name}` heading.
2. A 3-5 bullet list explaining what changed, why it changed, and the user-visible or operational difference. Keep bullets ≤ 20 words each.
3. If `risk_level` is `high`, add a line **Risk:** <specific risk> right after the bullets (bold label, plain prose).
4. ONE fenced code block tagged ```diff containing the representative unified-diff hunks (≤ 25 lines total). Use `+` and `-` prefixes as emitted by `git diff`. Collapse unrelated hunks — pick the ones that tell the story.
   - If the change is a whole new file (no meaningful "before"), use a plain language-tagged block (e.g. ```python) and preface with a line saying "New file: `path`".
5. One short paragraph (≤ 40 words) below the code block pointing at the non-obvious thing — a correctness concern, an invariant shift, a subtle coupling. Fold in any reviewer context that would have gone in speaker notes ("we tried X, it broke because Y", "what to watch post-merge", "what the PR should claim").

Output raw markdown only. No outer fences. No preamble. No trailing commentary.
```

## Write Risks & Testing Section

Used in Step 6.

```
Themes with risk levels:
{theme_listing_with_risks}

Per-theme risk notes:
{risk_bullets}

Write ONE markdown section:

- `## Risks & testing` heading.
- A bulleted list — one bullet per `medium` or `high` risk theme. Each bullet names the specific risk and the test that would catch a regression. Skip `low` risk themes.
- If there is a migration or schema change anywhere in the branch, include a final line **Rollback:** <assessment> naming whether rollback is safe and how to perform it.
- Close with a short paragraph (≤ 50 words) naming the manual test path start-to-finish and production signals to watch post-merge.

Output raw markdown only. No outer fences, no preamble.
```

## Write Reviewer Checklist

Used at the end of Step 6 for the final section.

```
Branch summary: {summary}

Themes and risk levels:
{theme_listing_with_risks}

Known risks called out in theme sections:
{risk_bullets}

Write ONE markdown section:

- `## Reviewer checklist` heading.
- A markdown task-list (GitHub-style `- [ ]`) with 5-10 concrete verification items. Each item ≤ 20 words, starts with an imperative verb ("Check", "Verify", "Run").
- Order: correctness-critical items first (migrations, auth, schema), then API-contract, then UI/refactor.
- Below the list, add a short paragraph (≤ 40 words) naming what would block approval and what the author is least confident about (infer from theme descriptions).

Output raw markdown only. No outer fences, no preamble.
```
