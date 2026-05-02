---
name: explain-concept
description: Generate a self-contained markdown walkthrough explaining a single concept or cross-cutting concern inside an existing codebase (e.g. "how does authorization work", "how does the cache layer invalidate entries", "how do scorecards flow from loader to UI"). Use this whenever the user wants a focused written walkthrough of one topic in a codebase rather than a full tutorial — trigger on phrases like "explain how X works", "walk me through X", "give me a writeup on X in this codebase", "/explain-concept", or any request for a markdown explainer about a specific concept in code. Prefer this over the full /codebase-tutorial when the user names a specific concept.
---

# explain-concept

Generates a single markdown file that explains one concept in an existing codebase. The doc is scoped — it only covers files actually relevant to the concept, not the whole repo.

## Input

Parse the user's argument string for:

- `concept` (required, positional) — the concept phrase in quotes. Example: `"how does authorization work"`.
- `--source=<path>` (optional) — root of the codebase. Default: current working directory.
- `--out=<path>` (optional) — output markdown path. Default: `./output/<project>/<slug>.md` where `<slug>` is the concept slugified (lowercase, non-alphanumerics → `_`, truncated to 60 chars).
- `--max-files=<n>` (optional) — hard cap on files fed to the section-write step. Default: 15.

If `concept` is missing, ask the user what concept they want explained.

## Pipeline

Seven steps. Run in order. Each step builds on the previous.

### Step 1: File listing

Run the crawl script with `--list-only` to get a cheap file listing (no content read yet):

```bash
python3 <skill-dir>/scripts/crawl_files.py --list-only <source>
```

This prints one relative path per line. Read into a list.

If zero files come back, tell the user the source path looks wrong or empty, and stop.

### Step 2: LLM file triage

Feed the file listing + concept to yourself (the LLM) via the **Triage Files** prompt in [references/prompts.md](references/prompts.md). Return at most `max_files` paths ranked by relevance.

If the LLM returns more than `max_files`, keep the top-ranked N and warn the user which were dropped.

If the LLM returns zero relevant files, tell the user the concept term likely doesn't match anything in this codebase and suggest rephrasing.

### Step 3: Read triaged files

Run the crawl script again, this time passing the triaged paths to read their contents:

```bash
python3 <skill-dir>/scripts/crawl_files.py --paths-from=/tmp/triaged.txt <source>
```

Output is JSON `{files: {path: content}, count: N}`. Build an indexed context string, same format as base `/codebase-tutorial`:

```
--- File Index 0: path/to/file1.py ---
<content>
```

### Step 4: Identify abstractions

Use the **Identify Abstractions** prompt from [references/prompts.md](references/prompts.md). Ask for 3–6 abstractions scoped to the concept, not whole-repo abstractions. Each abstraction = one idea the listener needs to understand the concept.

Parse YAML. Validate: each item has `name`, `description`, `file_indices`. Store as a list.

### Step 5: Analyze relationships

Use the **Analyze Relationships** prompt. Same format as base skill but scope emphasized. Parse YAML into `{summary, details: [{from, to, label}]}`. The summary becomes the TL;DR content.

### Step 6: Write section content

For each abstraction (in the order returned — they already came back in reading order from step 4), generate one markdown section via the **Write Section** prompt:

- `## {abstraction name}` heading
- 3-5 bullets: what it is, what problem it solves, how it fits into the concept. Bold any key invariant.
- One fenced code block, ≤ 15 lines, with the correct language tag (e.g. ` ```python `). Pick the 1-2 most illustrative snippets from the relevant files.
- One short paragraph pointing at the subtle thing to notice — do not restate what the code says.

Also generate a final **How they connect** section via the **Write How-They-Connect** prompt: an ordered list of 3-6 steps describing the end-to-end flow, each step bolding the relevant abstraction name.

### Step 7: Assemble markdown and write file

Compose the final `.md` content in this fixed order (see [references/output-template.md](references/output-template.md) for the skeleton):

1. `# {concept phrase}` — title H1
2. `_{project} · {YYYY-MM-DD}_` — subtitle italic line
3. `## TL;DR` — summary from Step 5
4. Mermaid overview in a ` ```mermaid ` fenced block (no surrounding heading)
5. `## {Abstraction name}` × N — per-abstraction sections in reading order
6. `## How they connect` — prose walkthrough from Step 6
7. `## Further reading` — bulleted list of files referenced, plus a link to base `/codebase-tutorial` output if it exists

Ensure the parent directory of `--out` exists (`mkdir -p`), then write the composed markdown to that path using the Write tool.

## Fixed section order (concept mode)

Section count = `4 + N + 2` where N = abstraction count. (Title, subtitle, TL;DR, mermaid, N abstractions, How they connect, Further reading.)

## Output

Print to the user:
- Output markdown path
- Section count
- List of files the doc references

Do not auto-open the file — user may prefer to `mv` the file or view it manually.

## Error handling

- Invalid YAML at any LLM step → retry up to 3 times with the parse error included in the retry prompt.
- If triage returns > `max_files` → keep top-N, warn which were dropped.
- If concept slug collides with an existing file at `--out=` → append `-2`, `-3`, etc.

## Related

- Base `/codebase-tutorial` — whole-codebase multi-chapter markdown tutorial. Use that when the user wants to learn the whole repo, not a concept slice.
- Sibling `/explain-diff` — same markdown format but scoped to a git branch diff instead of a concept.
