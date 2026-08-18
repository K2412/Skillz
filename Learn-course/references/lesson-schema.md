# Lesson output schema

Every per-chunk subagent must return JSON matching this shape **exactly**. Pass this file to the subagent alongside the system prompt.

## Schema

```json
{
  "lessons": [
    {
      "title": "string — concise, descriptive lesson title (e.g. 'List comprehensions in Python')",
      "content": "string — Markdown lesson body (4–8 short paragraphs, see lesson-prompt.md)",
      "order": "integer — 1-based, globally ordered across the course; the orchestrator may renumber later",
      "exercises": [
        {
          "title": "string — short exercise title (e.g. 'Filter even numbers')",
          "instructions": "string — Markdown task description: 1–2 sentence goal + bulleted requirements + I/O examples",
          "starter_code": "string — full source file for the learner to edit, with header comment and # TODO: markers",
          "solution_code": "string — full working source file (hidden from learner)",
          "test_code": "string — runnable test file using the language's conventional test runner",
          "order": "integer — 1-based within the lesson"
        }
      ],
      "animation": "object | omit — optional step-through walk (see Animation below). Omit the key entirely when the gate does not fire."
    }
  ]
}
```

## Field rules

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `lessons` | array | yes | Length 1+. One chunk usually maps to 1–3 lessons. |
| `lessons[].title` | string | yes | Plain text, no Markdown. |
| `lessons[].content` | string | yes | Markdown. Aim 4–8 short paragraphs. |
| `lessons[].order` | int | yes | Start from the value the user message specifies (`starting_order`); increment per lesson. |
| `lessons[].exercises` | array | yes | Length 3–4. |
| `lessons[].exercises[].title` | string | yes | Plain text. |
| `lessons[].exercises[].instructions` | string | yes | Markdown. |
| `lessons[].exercises[].starter_code` | string | yes | Source code with `# TODO:` markers; must parse in the target language. |
| `lessons[].exercises[].solution_code` | string | yes | Source code; tests must pass against it. |
| `lessons[].exercises[].test_code` | string | yes | Source code; runnable. |
| `lessons[].exercises[].order` | int | yes | 1-based per lesson. |
| `lessons[].animation` | object | no | Step-through walk. Omit the key when a static figure / the README already makes the idea obvious. |

## Animation (optional)

A walk is a stepped animation of the lesson's runtime: source on one side, the machine's state on the other, one beat per keypress. Emit one only when a paragraph is not enough **and** at least one holds:

- **Stateful over time** — event loop, reducer, state machine, scheduler, interpreter.
- **A sequence of mechanical steps** — a request through middleware, a lock changing hands.
- **Hard to believe without seeing** — concurrency, blocking vs yielding.

Skip syntax, types, and "write a function that returns X". Fill JSON only — the scaffolder injects it into a shared player. Do not invent HTML or JavaScript.

```json
{
  "title": "create_task schedules work before the first await",
  "lede": "Two fetches overlap only if both tasks exist before anyone waits.",
  "panes": [
    {
      "id": "code",
      "title": "Python thread",
      "kind": "code",
      "lines": ["async def main():", "    t = asyncio.create_task(work())"]
    },
    { "id": "loop", "title": "Event loop", "kind": "world" }
  ],
  "steps": [
    {
      "caption": "asyncio.run starts the loop and enters main.",
      "highlight": { "code": [1] },
      "world": {
        "loop": [
          {
            "id": "main",
            "title": "main()",
            "status": "running",
            "lines": ["async def main():", "    t = asyncio.create_task(work())"],
            "highlight": [1]
          }
        ]
      }
    }
  ]
}
```

- `panes[].kind` is `"code"` (full short listing in `lines`) or `"world"` (a column of cards). One code pane plus one or two world panes.
- Card `status`: `ready` · `running` · `suspended` · `complete` · `io`. Keep `id` stable across steps.
- 8–24 steps. Each caption is one teaching sentence. Every beat must change a highlight, a status, or which cards are present.
- `highlight` maps pane id → 1-based line indexes. `world` maps world-pane id → the card list at that beat.

## Hard rules

- Return **only** the JSON object. No `\`\`\`json` fences, no prose.
- All strings are JSON strings — newlines escape as `\n`, quotes escape as `\"`.
- All `*_code` fields are full, self-contained source files (with imports if needed). Do **not** put `<...>` placeholders in code that's supposed to compile.
- `solution_code` must make `test_code` pass. If the orchestrator detects a mismatch later, the chunk gets retried.

## Example (Python, single short lesson)

```json
{
  "lessons": [
    {
      "title": "Slicing strings in Python",
      "content": "## Slicing\n\nPython strings support a slice syntax `s[start:end]` that returns a substring without modifying the original. Indexes are zero-based and the `end` index is exclusive.\n\n## Negative indexes\n\nNegative indexes count from the right. `s[-3:]` returns the last three characters.\n\n## Step\n\nA third value sets the step: `s[::2]` keeps every other character. `s[::-1]` reverses the string.",
      "order": 1,
      "exercises": [
        {
          "title": "Last four characters",
          "instructions": "Write a function `last_four(s)` that returns the last four characters of `s`. If `s` is shorter than four characters, return `s` unchanged.\n\n- Input: a string\n- Output: a string of length min(4, len(s))",
          "starter_code": "# Lesson 1, Exercise 1: Last four characters\n# Implement last_four(s) below.\n# Hint: use Python's slice syntax with a negative start index.\n\ndef last_four(s):\n    # TODO: return the last four chars of s, or s itself if shorter than four\n    pass\n",
          "solution_code": "def last_four(s):\n    return s[-4:]\n",
          "test_code": "from solution import last_four\n\ndef test_normal():\n    assert last_four('hello world') == 'orld'\n\ndef test_short():\n    assert last_four('hi') == 'hi'\n\ndef test_empty():\n    assert last_four('') == ''\n",
          "order": 1
        }
      ]
    }
  ]
}
```
