# Step-through walks

A **walk** is a stepped animation of code running: source on one side, the machine's
state on the other, one beat per keypress. Corey Schafer's AsyncIO animations are the
canonical feel — you *see* the event loop take turns rather than being told that it does.

This file is the **single source of truth** for the mechanism. `code-review`'s explain mode writes a
walk next to an explainer when the gate fires. `learn-course` emits one per lesson that teaches
runtime behaviour. Fill
[`assets/stepper.html`](../assets/stepper.html); do not invent a new player.

The player is self-contained HTML (inline CSS/JS, `file://`-safe). You supply data. You
do not write JavaScript.

## The gate

Emit a walk only when a static figure has been ruled out **and** at least one holds:

- **Stateful over time** — an event loop, reducer, state machine, scheduler, interpreter.
- **A sequence of mechanical steps** — a migration, a multi-file refactor, a request
  travelling through middleware.
- **Hard to believe without seeing** — concurrency, blocking vs yielding, a perf claim.

Skip syntax, types, "write a function that returns X", and anything a paragraph already
makes obvious. A decorative walk is worse than none.

## Data you fill

Replace `__TITLE__`, `__LEDE__`, and `__ANIMATION_JSON__` in `assets/stepper.html`.
`__ANIMATION_JSON__` is a JSON object (not a string) of this shape:

```json
{
  "title": "create_task schedules work before the first await",
  "lede": "Two independent fetches overlap only if both tasks exist before anyone waits.",
  "panes": [
    {
      "id": "code",
      "title": "Python thread",
      "kind": "code",
      "lines": ["import asyncio", "", "async def main():", "    task = asyncio.create_task(work())"]
    },
    { "id": "loop", "title": "Event loop", "kind": "world" },
    { "id": "io", "title": "Background I/O", "kind": "world" }
  ],
  "steps": [
    {
      "caption": "asyncio.run starts the loop and enters main.",
      "highlight": { "code": [3] },
      "world": {
        "loop": [
          {
            "id": "main",
            "title": "main()",
            "status": "running",
            "lines": ["async def main():", "    task = asyncio.create_task(work())"],
            "highlight": [1]
          }
        ],
        "io": []
      }
    }
  ]
}
```

### Panes

- `kind: "code"` — a source listing. `lines` is the full file (keep it short: the example,
  not the repo). Highlighted at each step via `steps[].highlight[<pane id>]` (1-based).
- `kind: "world"` — a column of **cards**. Each step replaces the column's card list.

One code pane plus one or two world panes is the usual layout. Three code panes is a
slideshow of files, not a walk.

### Cards

| field | purpose |
|---|---|
| `id` | stable across steps so the same task doesn't look like a new one |
| `title` | `main()`, `fetch_data(1)`, `Timer: wake fetch_data(1)` |
| `status` | `ready` · `running` · `suspended` · `complete` · `io` |
| `lines` | optional mini-listing inside the card |
| `highlight` | 1-based indexes into that card's `lines` |
| `note` | one-line body when there is no code (a timer, a lock, a queue) |

`io` draws a spinner. Empty `world[paneId]` (or omitted) shows "Nothing scheduled."

### Steps

8–24 beats. Each caption is one teaching sentence — what *this* beat changes, not a
recap of the whole lesson. Advance with a visible change: a new highlight, a status
flip, a card appearing or leaving. A step that only restates the previous caption is
padding; cut it.

Prefer **Back** as well as Next. The player already binds ← → and Home.

## How each skill fills it

**code-review explain mode.** After the intuition section, if the gate fires, copy `assets/stepper.html`
to `explanations/explain-<slug>-<date>-walk.html`, substitute the three placeholders, and
link it from the explainer's figure slot (`Step through the change →`). Put one quiz
question that is only answerable after walking it. If the change is about control flow, state,
concurrency, or a multi-step migration, the explainer must include that walk file. If the gate does
not fire, say so — a missing walk should read as a choice, not an omission.

**learn-course.** Lesson JSON may include an optional `animation` object (same schema).
The scaffolder writes `animation.html` into the lesson directory from this same player.
Teach mode opens it before the first exercise whenever the file exists.

## Taste

The walk illustrates an idea already stated in prose. It is never the reader's first
contact with the change. If the interaction does not teach something the caption can't
say in one sentence, delete the walk.
