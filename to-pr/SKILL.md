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

Translate an `explain-diff` explainer (a self-contained HTML learning artifact) into a clean
Markdown PR description, then open a **draft** PR for the current branch.

The explainer is written to *teach* — it carries CSS styling, a color-coded literate diff, and an
interactive quiz. GitHub renders none of that: PR bodies are GitHub-Flavored Markdown that strips
`<style>`, `<script>`, `class`/`id`, and inline `style=`. So this skill **re-expresses** the
explainer as Markdown rather than pasting the HTML. The goal is a PR body a reviewer can skim and
trust — the same informative summary, minus the personal-learning scaffolding.

## Inputs

Parse these from the user's invocation; ask only if the explainer path is missing.

- **Explainer path** (required) — the `.html` file to convert (e.g. `docs/explain-<slug>-<date>.html`).
- **Base branch** (default `dev`) — the PR target. Honor an explicit "base X" / "into X" / "against X".
- **Draft** (default true) — always open as a draft unless the user clearly asks for a ready PR.
- **Title** (optional) — if the user gives one, use it; otherwise derive from the explainer's `<h1>`.

## Steps

1. **Read the explainer HTML** at the given path. If it isn't there, stop and tell the user.

2. **Extract the PR title.** Use the user-provided title if any; else the `<h1>` text. If the
   explainer's `.meta` line or title carries a ticket id (e.g. `SIG-520`), keep it in the title so
   the PR links back. Keep the title one line.

3. **Convert the body to Markdown**, section by section, in the explainer's own order. Translate —
   don't transcribe raw HTML. Mapping:
   - `<h2>` → `##`, `<h3>` → `###`.
   - Paragraphs / `.lede` → plain paragraphs. `<blockquote>` → `>` Markdown quote.
   - `.callout` blocks → a blockquote led by the bold label, e.g. `> **Intuition** — …`.
   - `details.bg` (the collapsible "Background") → keep it collapsible with the HTML GitHub
     *does* support, converting the inner content to Markdown:
     ```
     <details>
     <summary>How this works today (skip if you know it)</summary>

     …markdown…

     </details>
     ```
   - Each `.filehdr` + `<pre class="diff">` pair → a fenced ```` ```diff ```` block. The `.add` /
     `.del` / `.ctx` spans already carry their leading `+` / `-` / space, so emit each span's text
     on its own line. Precede the block with the filename as bold text or an `###` heading.
   - **Unescape HTML entities** in all extracted text: `&lt;`→`<`, `&gt;`→`>`, `&amp;`→`&`,
     `&quot;`→`"`, `&#39;`/`&apos;`→`'`. Diff blocks are full of `&lt;`/`&gt;` — get these right.
   - **Quiz → reviewer self-check.** Don't drop the quiz — reviewers find it useful for probing
     their own understanding. The interactive scoring can't survive (GitHub strips the `<script>`),
     but the questions can, with each answer hidden behind a `<details>` toggle so a reviewer reads
     the question, thinks, then expands to check. Read the questions and options from the `QUIZ`
     array in the explainer's `<script>`. Render each as:
     ```
     **1. <question stem>**

     - A. <option>
     - B. <option>
     - C. <option>
     - D. <option>

     <details><summary>Answer & why</summary>

     **Correct: <letter>** — <why the correct option is right>

     - A — <why> · B — <why> · C — <why> · D — <why>

     </details>
     ```
     List options in a stable A–D order (their order doesn't matter once the answer is revealed).
   - **Drop entirely:** the `<script>` scoring logic, the scorebar, and any `<style>`/`<head>`
     content — none of it renders on GitHub.

4. **Assemble the body.** Lead with the "ask"/summary so a reviewer gets the point immediately.
   Keep the literate diff walkthrough — it's the part that makes the review legible. Put the quiz
   self-check near the end, under a heading like `## Reviewer self-check` so it reads as optional.
   If the branch already has a PR with hand-written notes (e.g. `Closes <TICKET>`, merge-order
   caveats, test counts), graft those lines into the new body rather than discarding them. End the
   body with, on its own line:
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

- **Drafts by default.** This user always opens PRs as drafts and marks them ready manually — do
  not use `--web` or open a non-draft unless explicitly told.
- **Don't paste the raw HTML.** It will render as broken, unstyled text with a dead quiz. Always
  convert. If the user insists on embedding HTML, only `<details>`, `<summary>`, `<table>`,
  `<img>`, `<a>`, `<kbd>`, `<sub>`, `<sup>`, and `<br>` survive GitHub's sanitizer.
- **The body is for reviewers.** Favor the summary, the "why", and the diff walkthrough. When in
  doubt about a teaching aside, keep it short or cut it — a PR description earns trust by being
  scannable.
