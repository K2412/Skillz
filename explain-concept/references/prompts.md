# LLM Prompts — explain-concept

These prompts are invoked at each step of the pipeline. Substitute `{placeholders}` at call time. All YAML outputs must parse cleanly — retry on parse failure. Markdown section prompts emit raw markdown — no wrapping fences.

## Triage Files

Used in Step 2 to select which files actually relate to the concept. The file listing is cheap; we avoid reading full contents until we know which files matter.

```
Concept to explain: "{concept}"

Project root: {project_name}

Here is the full file listing of the codebase (one path per line):
{file_listing}

Your task: pick the files that are actually relevant to understanding the concept "{concept}". Think semantically — a file named `session_middleware.py` is relevant to "how does authorization work" even if "auth" is not in its name. Be generous about context: include the primary implementation files, the call sites that invoke them, and any type/interface definitions they rely on. Skip tests, fixtures, and unrelated code.

Return at most {max_files} paths, ranked from most relevant (first) to least relevant (last). If fewer than {max_files} files are genuinely relevant, return fewer. Do not pad.

Format the output as a YAML list of strings. No explanation, no markdown fences — just the YAML list:

```yaml
- path/to/most_relevant.py
- path/to/next.py
- ...
```
```

## Identify Abstractions

Used in Step 4. Note the scope framing — abstractions here are "ideas needed to understand the concept", not whole-repo abstractions.

```
Concept: "{concept}"

Codebase Context (only files relevant to the concept):
{context}

Analyze the code above and identify the 3-6 core ideas a developer must understand to grasp the concept "{concept}". These are not whole-codebase abstractions — they are the specific building blocks of this one concept.

For each idea, provide:
1. A concise `name`.
2. A beginner-friendly `description` explaining what it does and why it matters to this concept (around 80 words).
3. A list of relevant `file_indices` (integers) using the format `idx # path/comment`.

List of file indices and paths present in the context:
{file_listing}

Order the ideas in the order a listener should meet them — foundational first, dependent ideas later.

Format the output as a YAML list of dictionaries:

```yaml
- name: |
    Auth Middleware Entry
  description: |
    First gate every request passes through.
    Reads the session cookie and attaches a User to request.state.
  file_indices:
    - 0 # api/middleware/auth.py
    - 2 # api/deps.py
- name: |
    Session Store
  description: |
    Backend that resolves a session token to a user identity.
  file_indices:
    - 4 # api/auth/sessions.py
```
```

## Analyze Relationships

Used in Step 5. Same shape as base `/codebase-tutorial` — only the summary framing changes.

```
Based on the following ideas and relevant code snippets for the concept "{concept}" in project `{project_name}`:

List of Idea Indices and Names:
{abstraction_listing}

Context (Ideas, Descriptions, Code):
{context}

Provide:
1. A `summary` of how the concept works end-to-end, written as a TL;DR a reader could paste into a PR description. 2-4 sentences. Use markdown **bold** for key terms.
2. A list (`relationships`) describing how the ideas above interact. For each:
    - `from_abstraction`: source idea index (e.g. `0 # AuthMiddleware`)
    - `to_abstraction`: target idea index
    - `label`: a few words describing the interaction ("Reads from", "Writes to", "Calls")

Every idea must appear in at least one relationship. Skip non-important interactions.

Format as YAML:

```yaml
summary: |
  Auth is enforced by middleware that reads a cookie, resolves it via **SessionStore**, and attaches a User to each request.
  Downstream route handlers trust `request.state.user` exists — they never re-check.
relationships:
  - from_abstraction: 0 # AuthMiddleware
    to_abstraction: 1 # SessionStore
    label: "Resolves token via"
```
```

## Write Section

Used in Step 6. Called once per abstraction. Produces one markdown section combining the intro prose and the code snippet.

```
Abstraction {abstraction_num} of {total_abstractions}: "{abstraction_name}"
Concept context: "{concept}"

Description:
{abstraction_description}

Relevant code (do not include files outside this list; pick the 1-2 most illustrative snippets):
{file_context}

Where this sits in the overall flow:
{relationships_summary}

Write ONE markdown section:

1. `## {abstraction_name}` heading.
2. A 3-5 bullet list: what it is, what problem it solves, how it fits into the concept "{concept}". Keep each bullet ≤ 18 words.
3. If there is a key invariant (something always true, something never true), include it as a bullet with the invariant phrase in **bold**.
4. ONE fenced code block with the correct language tag (e.g. ```python, ```typescript, ```go). ≤ 15 lines. Label the snippet with a line directly above the block in the form `From \`path/to/file.py\` — `function_or_region``.
5. One short paragraph (≤ 35 words) below the code block pointing at the subtle thing. Do not restate what the code says — point out the non-obvious coupling, invariant, or edge case.

Output raw markdown only. No outer fences. No preamble. No trailing commentary.
```

## Write How-They-Connect

Used in Step 6 after all per-abstraction sections have been generated.

```
Concept: "{concept}"

Abstractions introduced (in order):
{abstraction_listing}

Relationships between them:
{relationships_listing}

Summary:
{summary}

Write ONE markdown section that ties these abstractions together as one narrative.

- `## How they connect` heading.
- An ordered list (`1.` `2.` `3.` …) with 3-6 steps describing the end-to-end flow — a reader should be able to trace a single request / operation through every abstraction.
- Each step ≤ 25 words. Bold the abstraction name being discussed in each step.
- No code. No mermaid. This section is the prose glue.

Output raw markdown only. No outer fences, no preamble.
```
