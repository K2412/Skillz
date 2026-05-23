---
name: learn-opsc
description: Build an Open-source Project Semantic Course from one or more GitHub repositories and optional documentation. Use when the user wants to understand a large open-source project under the hood by reconstructing it from first principles in logical semantic chapters, as if the project did not exist yet. Produces a directory-based course with source maps, conceptual commits, mini-implementations, exercises, and reading paths. Trigger for requests like "teach me this repo", "semantic reconstruction", "learn open source internals", "rebuild Laravel/Svelte/Inertia from scratch", or "turn this repo into a course".
---

# learn-opsc — Open-source Project Semantic Course

`learn-opsc` turns large open-source repositories into a **semantic reconstruction course**: a guided path that teaches how the project works by rebuilding its core ideas in logical order.

This is **not** a literal Git history course. Real commit histories are noisy. The skill creates educational “conceptual commits” instead: each chapter introduces one coherent piece of the system, references the real source files that inspired it, and optionally asks the learner to implement a small version.

## Core output

Create a course directory like:

```text
<project>-under-the-hood/
  README.md
  _meta.json
  source-map.md
  repos/
    manifest.json
  chapters/
    001-orientation/
      README.md
      source-map.md
      conceptual-commit.md
      exercise.md
    002-.../
  mini-project/
    README.md
    ... implementation scaffold ...
```

The course should help the learner answer:

1. What problem does this project solve?
2. What are the core runtime objects?
3. What is the request/render/compile/data lifecycle?
4. What abstractions hide complexity?
5. What would I build first if this project did not exist?
6. Which real source files should I read after learning the simplified version?

## When to use

Use this skill when the user gives one or more repositories and asks to understand them deeply, especially large frameworks or libraries:

- Laravel: `laravel/laravel` + `laravel/framework`
- Inertia: `inertiajs/inertia` + adapters like `inertiajs/inertia-laravel`
- Svelte: `sveltejs/svelte`
- Any framework, compiler, runtime, ORM, router, testing library, build tool, or SDK

## Inputs

Gather or infer:

- Project name
- Repo URLs, one or more
- Optional docs URLs or local `.md` sources
- Target learner language/ecosystem for exercises
- Desired depth: overview, practical, internals, or source-reader
- Whether to generate a mini-project scaffold or Markdown-only course

If the user has not specified scope, ask one concise `AskUserQuestion` before generation.

## Modes

### 1. Plan mode

Use this when the user is still deciding scope.

Output a proposed chapter map only. Do not create files unless the user asks to execute.

### 2. Generate mode

Use this when the user asks to create the course directory.

Steps:

1. Create or choose an output directory.
2. Clone/index the repos into a temp area or use existing local paths.
3. Read project docs if provided.
4. Identify major subsystems.
5. Order subsystems semantically, from smallest bootstrap concept to working system.
6. Generate chapter directories.
7. Add source maps linking each chapter to real files.
8. Add exercises or reconstruction tasks.
9. Add a final reading path for the real codebase.

### 3. Teach mode

If the user is inside a generated `learn-opsc` course and asks to start/continue, act as a tutor:

1. Read `_meta.json` and chapter progress if present.
2. Present the current chapter’s goal concisely.
3. Point to the source files and mini-project exercise.
4. On check, review the learner’s work and run tests if a test command exists.
5. Give hints before solutions.

## Analysis workflow

### Step 1 — Acquire sources

For each repository:

```bash
git clone --depth 1 <repo-url> /tmp/learn-opsc-repos/<slug>
```

If the repo is already local, use it directly.

Do not vendor huge repos into the generated course. Store only a manifest with repo URL, branch/ref, and local analysis path.

### Step 2 — Build a lightweight source map

Inspect:

- README / docs / contributing files
- package manifests: `composer.json`, `package.json`, `pnpm-workspace.yaml`, `tsconfig.json`, etc.
- top-level directories
- tests/examples
- public APIs and entrypoints
- package boundaries in monorepos

Prefer `rg`, `find`, and targeted file reads over dumping huge files.

Create a mental map:

```text
Subsystem -> Purpose -> Entry files -> Supporting files -> Tests/examples
```

### Step 3 — Find the semantic spine

Identify the “spine” of the project — the smallest path through the system that explains the whole architecture.

Examples:

Laravel spine:

```text
front controller -> application -> container -> providers -> request -> router -> middleware -> controller -> response -> facades -> config -> database -> ORM -> queues/events
```

Inertia spine:

```text
server response protocol -> page object -> client app boot -> router visits -> history state -> links/forms -> partial reloads -> deferred/merged props -> adapters
```

Svelte spine:

```text
component syntax -> compiler pipeline -> AST/analysis -> reactivity model -> runes -> template lowering -> DOM operations -> runtime scheduling -> stores/context/transitions
```

### Step 4 — Create conceptual commits

Each chapter should behave like a clean pedagogical commit:

```text
001 Add the front controller
002 Add a minimal application object
003 Add dependency injection container
004 Add service providers
...
```

For each chapter include:

- **Goal** — what this chapter adds
- **Why it exists** — what pressure forced this abstraction
- **Conceptual diff** — what changed from the previous chapter
- **Mini implementation** — simplified code or pseudocode
- **Real source map** — files/classes/functions in the actual repo
- **Reading assignment** — exact files to read next
- **Exercise** — one small reconstruction or tracing task
- **Checkpoints** — questions the learner should be able to answer

### Step 5 — Use docs as grounding, source as truth

Docs explain intent; source explains reality.

If docs are provided as local `.md` files, read from them first for terminology. Then verify against source.

For current web docs, use Firecrawl `scrape` for known URLs and `search` for discovery if available.

### Step 6 — Keep the mini-project small

The mini-project is not a clone of the real framework. It is a teaching skeleton.

Rules:

- Implement only the idea being taught.
- Avoid production-grade edge cases.
- Keep public interfaces small.
- Add tests only when they clarify behavior.
- Cite real source files for deeper reading.

## Course quality rules

- Prefer semantic order over historical order.
- Do not pretend the simplified implementation is production equivalent.
- Do not overwhelm chapters with too many source files; 3–7 files per chapter is enough.
- Always include source paths so the learner can jump into the real repo.
- Explain why abstractions exist, not just what they do.
- Start with a thin working vertical slice before adding subsystems.
- Use diagrams in Markdown when helpful.
- Keep chapters short enough to complete in one focused session.

## Suggested chapter counts

- Small library: 6–10 chapters
- Medium framework/package: 10–18 chapters
- Large framework/compiler: 18–30 chapters

If the user asks for Laravel/Svelte-scale projects, create a phase-based roadmap and generate the first phase unless they explicitly ask for the entire course at once.

## Output file templates

See `references/chapter-template.md` for the per-chapter structure.

## Pairing with other skills

- Use `understand` / `understand-chat` if a knowledge graph exists or the repo is large.
- Use `learn-course` if the final output should become an exercise-heavy course from generated Markdown.
- Use `tdd` if building the mini-project implementation with tests.
- Use `agent-browser` only if verifying generated HTML/course UI, not for source analysis.
