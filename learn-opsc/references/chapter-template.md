# Lesson Template

Use this structure for each `learn-opsc` lesson. The directory must mirror `learn-course` ergonomics:

```text
01-lessons/NN-slug/
  README.md
  source-map.md
  exercises/
    01-name.ext
  tests/
    01-name.test.ext
  .solutions/
    01-name.solution.ext
```

`README.md`:

```markdown
# NNN — <Conceptual Commit Title>

## Goal

What this lesson adds to the reconstruction.

## The pressure

What problem appears if this abstraction does not exist?

## Conceptual commit

> Add <thing> so that <capability>.

## Before this lesson

What the reconstruction can already do.

## After this lesson

What new behavior exists.

## Minimal implementation

Small, readable implementation or pseudocode. Prefer clarity over completeness.

```language
// code here
```

## How the real project does it

| Real file | Why it matters |
| --- | --- |
| `path/to/file` | Short explanation |

## Exercises

1. **Exercise name** — `exercises/01-name.ext`
   Short behavior-oriented task description.

Each starter file must contain rich comments and `TODO` markers. Each exercise must have a matching executable test and hidden solution.

## Checkpoints

After this lesson, the learner should be able to answer:

- Question 1
- Question 2
- Question 3

## What we are intentionally ignoring

Production details omitted from the simplified reconstruction.
```

`source-map.md`:

```markdown
# Lesson Source Map

| Real file | Read for |
| --- | --- |
| `repo/path` | Why this file matters for the lesson |
```
