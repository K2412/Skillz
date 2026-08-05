---
name: to-pr
description: >
  Turn an explain-diff explainer HTML file into a Markdown PR description and open a draft
  pull request for the current branch. Use whenever the user wants to ship an explainer as a
  PR — "/to-pr", "make a draft PR from this explainer", "turn <explainer>.html into a PR
  description", "open a PR using this explainer", "convert my explainer to a PR body", or
  references an explain-diff HTML file (usually under docs/ or explanations/) together with
  wanting a PR. Trigger even if they don't say "to-pr" explicitly, as long as they point at an
  explainer file and want it become a PR. Default base branch is `dev` and PRs are always opened
  as drafts.
---

# to-pr

Translate an `explain-diff` explainer (a self-contained HTML learning artifact) into a clean,
**concise** Markdown PR description, then open a **draft** PR for the current branch.

The explainer is written to *teach*: it carries CSS styling, background, a color-coded literate
diff, illustrative figures, and an interactive quiz. A PR description has a different job — a
reviewer skims it to get oriented, then reads the real code in GitHub's own diff view. So this
skill **distils** the explainer; it does not transcribe it. Keep the summary, the "why", and any
figure that teaches — drop the scaffolding a teammate doesn't need.

**Keep it proportional.** A good PR body is *shorter* than the change it describes. If the
description is longer than the diff, cut. GitHub already renders the code and the diff — the body
earns trust by being scannable, not exhaustive.

## Inputs

Parse these from the user's invocation; ask only if the explainer path is missing.

- **Explainer path** (required) — the `.html` file to convert (e.g. `docs/explain-<slug>-<date>.html`).
- **Base branch** (default `dev`) — the PR target. Honor an explicit "base X" / "into X" / "against X".
- **Draft** (default true) — always open as a draft unless the user clearly asks for a ready PR.
- **Title** (optional) — if the user gives one, use it; otherwise derive from the explainer's `<h1>`.
- **Quiz** (default off) — leave the self-check quiz out unless the user asks to keep it.

## Steps

1. **Read the explainer HTML** at the given path. If it isn't there, stop and tell the user.

2. **Extract the PR title.** Use the user-provided title if any; else the `<h1>` text. If the
   explainer's `.meta` line or title carries a ticket id (e.g. `SIG-520`), keep it in the title so
   the PR links back. Keep the title one line.

3. **Convert the body to Markdown** — distilling, not transcribing. Work in the explainer's own
   order, but drop anything that doesn't help a reviewer orient. Mapping:
   - `<h2>` → `##`, `<h3>` → `###`.
   - Paragraphs / `.lede` → plain paragraphs. `<blockquote>` → `>` Markdown quote.
   - `.callout` blocks → a blockquote led by the bold label, e.g. `> **Intuition** — …`. Keep only
     the ones that carry real signal; skip teaching asides a teammate already knows.
   - `details.bg` (the collapsible "Background") → keep it collapsible, converting the inner content
     to Markdown, but trim it hard — a reviewer skips known background:
     ```
     <details>
     <summary>How this works today (skip if you know it)</summary>

     …short markdown…

     </details>
     ```
   - **Figures / diagrams → keep them; re-express as GitHub-native visuals.** The illustrative parts
     (a state machine, a flow, a before/after) are the most valuable thing to carry across — they
     convey what prose can't, and reviewers love them. GitHub strips inline `<svg>` and `<script>`,
     so re-express the figure as a ` ```mermaid ``` ` block (`stateDiagram-v2`, `flowchart`,
     `sequenceDiagram`) that renders natively. Read the figure's structure from the explainer's SVG
     or widget markup and reconstruct it faithfully. If a figure is purely decorative or can't be
     faithfully re-expressed, drop it rather than paste broken markup.
   - **Diff walkthrough → a short summary, not a re-paste.** GitHub already shows the full diff in
     the Files Changed tab, so don't reproduce it. Summarize the change as a few bullets grouped by
     file or by concern — *what* changed and *why*. Quote a fenced ` ```diff ``` ` snippet only for
     the one or two hunks that are genuinely load-bearing or non-obvious; never the whole diff.
   - **Unescape HTML entities** in any extracted text: `&lt;`→`<`, `&gt;`→`>`, `&amp;`→`&`,
     `&quot;`→`"`, `&#39;`/`&apos;`→`'`. Get these right in mermaid labels and any diff snippet.
   - **Quiz → drop by default.** The self-check quiz is personal-learning scaffolding and the single
     biggest source of PR-body bloat; leave it out unless the user explicitly asks to keep it. If
     they do, render each question under a `## Reviewer self-check` heading with its answer hidden
     behind a `<details>` toggle:
     ```
     **1. <question stem>**

     - A. <option>
     - B. <option>
     - C. <option>
     - D. <option>

     <details><summary>Answer & why</summary>

     **Correct: <letter>** — <why the correct option is right>

     </details>
     ```
   - **Drop entirely:** the `<script>` scoring logic, the scorebar, and any `<style>`/`<head>`
     content — none of it renders on GitHub.

4. **Assemble the body — lead with the ask, keep it tight.** Open with a 1–3 sentence summary so the
   reviewer gets the point immediately. Then the "why", any figure (as mermaid), and a short bullet
   summary of the key changes. That is usually the entire body. If the branch already has a PR with
   hand-written notes (e.g. `Closes <TICKET>`, merge-order caveats, test counts), graft those lines
   in rather than discarding them. End the body with, on its own line:
   ```
   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   ```
   Write the finished Markdown to a temp file (the session scratchpad, or `/tmp/to-pr-body.md`).

5. **Prepare the branch.** Confirm the current branch is not the base branch. Push it if it has no
   upstream: `git push -u origin HEAD`. If the working tree has uncommitted changes, surface that
   and let the user decide before creating the PR — don't commit on their behalf.

6. **Open the draft PR:**
   ```bash
   gh pr create --draft --base <base> --title "<title>" --body-file <body.md>
   ```
   If a PR already exists for this branch, `gh pr create` will say so — in that case offer to
   update the existing body instead: `gh pr edit --body-file <body.md>`.

7. **Report** the PR URL. Note that it opened as a draft and remind the user they mark it ready
   themselves.

## Notes

- **Shorter than the diff.** The reviewer reads the code on GitHub; the body just orients them. Lead
  with the summary and the "why", keep any figure, and cut the rest. If the body is longer than the
  change, you've over-written it.
- **Keep the visuals.** Re-expressing a state machine or flow as a `mermaid` block is worth the
  effort — it's the part reviewers most appreciate. Never paste raw `<svg>` (GitHub strips it).
- **Drafts by default.** This user always opens PRs as drafts and marks them ready manually — do
  not use `--web` or open a non-draft unless explicitly told.
- **Don't paste the raw HTML.** It renders as broken, unstyled text. Always convert. Only
  `<details>`, `<summary>`, `<table>`, `<img>`, `<a>`, `<kbd>`, `<sub>`, `<sup>`, `<br>`, and
  ` ```mermaid ``` ` fences survive GitHub's sanitizer.
