---
name: check-work
description: "Verify uncommitted local changes by inspecting the git diff and then driving the change in a real, visible browser via agent-browser. Use this skill whenever the user wants to check their work, verify a change actually works, sanity-check before committing, or asks things like 'check my work', 'did my change work', 'verify what I just did', 'test these uncommitted changes', 'look at my diff and make sure it works', 'open the page so I can see my change', or anything else that means 'I just made an edit, prove it does what I think it does.' Trigger this even when the user doesn't say 'browser' — the point is to verify uncommitted work end-to-end with the browser visible (NOT headless), so the user can watch."
---

# check-work — Verify uncommitted changes in a real browser

The goal of this skill is to close the loop between "I made some edits" and "those edits actually do the thing I wanted." It does that by reading the git diff, figuring out what's testable in a browser, then driving the change in `agent-browser` with `--headed` so the user can see it happen.

## Why this skill exists

When you've been editing for a while it's easy to *think* a change works because the code looks right, the types check, and the tests pass — but the actual rendered UI is the only ground truth. This skill forces that last check, with the browser window visible so the user can spot regressions or weirdness that automated assertions wouldn't catch.

## Workflow

### 1. Read the uncommitted changes

Start by getting a full picture of what's actually different on disk. Run these in parallel:

```bash
git status --short
git diff --stat
git diff
git diff --cached     # staged-but-uncommitted
```

Untracked files (`??` in `git status`) also count — diff won't show them, so read them directly with the Read tool if they look UI-relevant.

Note what changed: which files, which routes/components/templates, and what the change is *trying* to do. If the diff is huge, focus on UI-facing files (anything under `pages/`, `components/`, `views/`, `templates/`, `app/`, `resources/views/`, `*.tsx`, `*.vue`, `*.svelte`, `*.blade.php`, etc.).

### 2. Decide what to verify

From the diff, infer:

- **What route/URL exercises the change.** Do real grep work before guessing:
  - If the changed file is a page/route file (e.g. `pages/checkout.tsx`, `routes/web.php`, `app/checkout/page.tsx`), the route is usually obvious from the path or the route definition itself.
  - If it's a component, view, or partial, grep the project for imports/usages (`grep -r "import.*ChangedComponent" .`, or for Blade/Rails partials, search the partial name) to find which pages render it. Pick the page that most directly exercises the change.
  - Check the project's routing config (`routes/web.php`, `app/**/page.tsx`, `pages/**/*.tsx`, `urls.py`, `routes.rb`) to confirm the URL path.
  - Only fall back to asking the user if grep genuinely turns up nothing usable — and when you do ask, share what you searched so the user understands why you're stuck.
- **What the change is supposed to do.** Is it a new button? A copy fix? A layout tweak? A bug fix for a specific interaction? This determines what to actually click/observe.
- **The dev server URL.** Default to `http://localhost:3000` for Next, `http://localhost:5173` for Vite, `http://localhost:8000` for Laravel/Django, etc. — but check the project's README, package.json scripts, or `.env` if unsure. If a server isn't running, **ask the user** to start it; don't try to start it yourself unless they explicitly say so.

### 3. Drive the browser with `--headed`

The whole point is for the user to *watch*. Always pass `--headed` so the Chrome window is visible. Chain commands with `&&` for atomicity:

```bash
agent-browser --headed open http://localhost:3000/checkout && agent-browser snapshot -i
```

Then follow the standard agent-browser pattern: **open → snapshot → interact → verify** (see the `browser-agent` skill for full details). Use `wait` after navigation if the page is slow. Take a `screenshot` at the end so there's a visual record.

If the change involves a flow (login → form → submit), walk the whole flow, not just the landing page. If it's a visual-only tweak (copy change, color, spacing), a snapshot + screenshot is enough.

### 4. Report what you saw

After driving the change, summarize for the user:

- **What was changed** (1 line per file, taken from the diff)
- **What you verified in the browser** (the route(s) you visited and the interactions you performed)
- **What looked right** and **anything that looked wrong or surprising** — be honest. If the change doesn't appear to have taken effect (e.g., the new button isn't there, or the layout still looks broken), say so directly so the user can fix it before committing.

Leave the browser open at the end unless the user said to close it — the user may want to poke at it themselves.

## When this skill doesn't fit

- **Backend-only changes with no UI surface** (e.g., a migration, a CLI script, a pure refactor of internal helpers). Tell the user this skill won't add signal and suggest running the tests or the relevant CLI command instead.
- **The diff is empty.** If `git status` shows no uncommitted changes, say so and stop — don't invent something to verify.
- **The user wants a code review, not a browser check.** That's `senior-eng` or `code-review`, not this skill.

## Tips

- **Always `--headed`.** Headless defeats the point — the user wants to watch.
- **Don't assume the dev server is running.** If `agent-browser open` fails with a connection error, ask the user to start it rather than guessing the command.
- **Prefer one well-chosen route over five shallow ones.** Walking the actual flow that exercises the change beats opening five tangentially-related pages.
- **Use `git diff` output to drive your interactions.** If the diff added a button labeled "Save draft", your verification should include clicking that button — not just confirming the page loads.
