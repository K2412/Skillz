---
name: agent-browser
description: "Browser testing and automation using the agent-browser CLI. Use this skill whenever the user wants to test a URL, check a webpage, verify UI behavior, open something in a browser, do browser automation, test if a site works, verify a page loads correctly, test form submissions, check responsive layout, monitor network requests, or mentions agent-browser directly. Also trigger when the user says 'check the page', 'test the frontend', 'does the site work', 'open localhost', 'test in browser', 'verify the deploy', 'screenshot the page', or any browser-related testing task. Even if the user doesn't say 'browser' explicitly — if they want to verify something works at a URL, this is the skill to use."
---

# agent-browser — Browser Testing & Automation

`agent-browser` is a fast CLI for browser automation, designed for AI agents. It manages a persistent browser daemon so commands chain naturally without reopening Chrome each time.

## Discovery First

If you're unsure about a subcommand or its flags, run:

```bash
agent-browser --help
```

This is cheap and fast. Don't guess at flags — check first. The help output is comprehensive and always up to date.

## Core Workflow: Snapshot-First

The fundamental pattern is: **open → snapshot → interact → verify**.

The accessibility snapshot (`snapshot -i`) is your primary way to "see" the page. It returns a tree of elements with `@ref` identifiers you use to target interactions. This is far more reliable than guessing CSS selectors.

```bash
# 1. Open the page
agent-browser open https://example.com

# 2. Get interactive elements (the -i flag filters to only interactive elements — use it!)
agent-browser snapshot -i

# 3. Interact using @refs from the snapshot
agent-browser fill @e3 "user@example.com"
agent-browser fill @e4 "password123"
agent-browser click @e5

# 4. Verify the result
agent-browser snapshot -i
agent-browser get url
agent-browser screenshot result.png
```

Why `-i`? Without it, `snapshot` returns *every* element on the page — headings, paragraphs, images, everything. With `-i`, you get only interactive elements (buttons, inputs, links), which keeps output manageable and focused on what you can act on.

## Command Chaining

The browser persists via a daemon, so chain commands with `&&`:

```bash
agent-browser open https://example.com && agent-browser snapshot -i
```

```bash
agent-browser fill @e1 "test@example.com" && agent-browser fill @e2 "secret" && agent-browser click @e3
```

This is the preferred way to run multi-step sequences — one shell call, multiple actions.

## Common Testing Patterns

### Verify a page loads and has expected content

```bash
agent-browser open <url> && agent-browser snapshot -i
agent-browser get title
agent-browser get text <selector-or-ref>
```

### Fill and submit a form

```bash
agent-browser open <url> && agent-browser snapshot -i
# Read the snapshot output to identify @refs for each field
agent-browser fill @e1 "value1" && agent-browser fill @e2 "value2"
agent-browser click @e3   # submit button
agent-browser wait 2000   # wait for navigation/response
agent-browser snapshot -i # verify result
```

### Visual regression / screenshots

```bash
agent-browser open <url>
agent-browser wait 1000                    # let page settle
agent-browser screenshot page.png          # viewport only
agent-browser screenshot --full full.png   # full page scroll
agent-browser screenshot --annotate labeled.png  # labeled for vision models
```

The `--annotate` flag adds element labels to the screenshot — useful if you're passing images to a vision model for analysis.

### Check element state

```bash
agent-browser is visible @e1
agent-browser is enabled @e2
agent-browser is checked @e3
```

### Network monitoring

```bash
# Start HAR recording before navigating
agent-browser network har start
agent-browser open <url>
agent-browser network requests --filter "api/"   # see API calls
agent-browser network har stop recording.har      # save full HAR

# Mock a route (useful for testing error states)
agent-browser network route "*/api/users" --body '{"error": "not found"}'
```

### Navigate and verify redirects

```bash
agent-browser open <url>
agent-browser wait 2000
agent-browser get url    # check final URL after redirects
agent-browser get title  # verify page title
```

### Scroll and find content below the fold

```bash
agent-browser open <url>
agent-browser scroll down 500
agent-browser snapshot -i
# Or scroll a specific element into view
agent-browser scrollintoview "footer"
```

### Find elements by role or text (when you don't have @refs yet)

```bash
agent-browser find role button click --name "Submit"
agent-browser find text "Sign in" click
agent-browser find placeholder "Email address" fill "user@test.com"
```

### Run JavaScript for custom checks

```bash
agent-browser eval "document.querySelectorAll('.error').length"
agent-browser eval "window.performance.timing.loadEventEnd - window.performance.timing.navigationStart"
```

## Waiting

Pages aren't always ready instantly. Use `wait` to handle async content:

```bash
agent-browser wait ".loading-spinner"  # wait for element to appear
agent-browser wait 2000                # wait 2 seconds
```

If a page is slow or has animations, wait before taking snapshots or screenshots.

## Connecting to an Existing Browser

```bash
agent-browser --cdp 9222 snapshot        # connect via CDP port
agent-browser --auto-connect snapshot    # auto-discover running Chrome
agent-browser --profile Default open gmail.com  # reuse Chrome login state
```

## Cleanup

Always close the browser when done testing:

```bash
agent-browser close        # close current session
agent-browser close --all  # close all sessions
```

This frees resources. If you forget, the daemon keeps Chrome running in the background.

## Tips

- **Snapshot first, always.** Don't guess at selectors. Run `snapshot -i`, read the refs, then interact.
- **Chain with `&&`** for multi-step flows. One shell call = atomic sequence.
- **Use `-i`** on snapshot. Full snapshots are noisy; interactive-only is what you need 90% of the time.
- **Wait for slow pages.** A `wait 1000-2000` after `open` prevents flaky interactions.
- **Check `--help`** when uncertain. `agent-browser <subcommand> --help` works too.
- **Close when done.** Don't leave browser sessions hanging.
