---
name: laravel-docs-lookup
description: Proactively look up official Laravel documentation and best practices before and during work on any Laravel application. Use this skill whenever the user is working on Laravel — controllers, models, Eloquent, migrations, routes, middleware, queues, jobs, events, service providers, policies, form requests, validation, Blade, Artisan, config, testing (Pest/PHPUnit), Fortify, Sanctum, Passport, Horizon, Telescope, Octane, Reverb, Cashier, Scout, Pulse, Pennant, Folio, Volt, Vite integration, or any first-party laravel/* package. Activate even if the user didn't explicitly ask for docs — the skill exists because the user removed Laravel's MCP servers (including laravel/boost) and wants the agent to default to looking things up against the current stable docs rather than relying on training-data recall. Also trigger on phrases like "how do I do X in Laravel", "what's the Laravel way", "latest Laravel", "Laravel 11/12/13 syntax", or when modifying files under app/, routes/, database/migrations/, config/, or tests/ in a Laravel project.
---

# Laravel Docs Lookup

## Why this skill exists

Laravel moves fast. Major versions ship yearly, APIs shift (streamlined application structure, new defaults, renamed helpers, deprecated traits), and first-party packages (Fortify, Sanctum, Horizon, Pulse, Reverb, Pennant, Folio, Volt) change independently. Model training data lags behind the current stable release, so writing Laravel code from memory produces subtly wrong results — old facade calls, removed config keys, outdated testing helpers, superseded patterns.

The user has intentionally removed MCP servers (including `laravel/boost`) that previously streamed live docs into context. **This skill replaces that capability.** Your job is to treat `laravel.com/docs` as the source of truth and fetch it on demand.

## Core behavior

**Look up docs BEFORE writing non-trivial Laravel code, not only when you get stuck.** Cheap lookup now beats debugging wrong code later. A "non-trivial" task is anything beyond a trivial rename or comment edit — creating/modifying a controller, migration, Eloquent relationship, queue job, test, service provider registration, middleware, validation rule, policy, or config change all qualify.

Trivial edits that don't need a lookup: fixing a typo, renaming a variable, formatting, adding a dd()/logger() call, pure business-logic inside a method whose surrounding Laravel scaffolding you already confirmed is correct.

## Step 1: Detect the installed Laravel version

Before fetching docs, pin the version so you read the right page.

1. Read `composer.lock` in the project root. Search for `"name": "laravel/framework"` and grab the `"version"` field next to it (e.g., `"v13.2.0"`).
2. If `composer.lock` is missing, fall back to `composer.json` and read the `require."laravel/framework"` constraint (e.g., `"^13.0"` → treat as 13.x).
3. Map that to the docs version slug used in URLs: `laravel.com/docs/13.x/...`, `laravel.com/docs/12.x/...`, etc.
4. If you can't determine the version, default to the current stable branch shown at `laravel.com/docs` and note the assumption to the user.

Also check for first-party packages the task touches (`laravel/fortify`, `laravel/sanctum`, `laravel/horizon`, etc.) — those have their own version lines in `composer.lock` and their own docs pages (often with a package-specific version slug).

## Step 2: Fetch the right page

Use `WebFetch` against the version-pinned URL. Common entry points:

- Framework topic page: `https://laravel.com/docs/{version}/{topic}` — e.g., `/13.x/eloquent-relationships`, `/13.x/validation`, `/13.x/queues`, `/13.x/middleware`, `/13.x/testing`.
- First-party packages: `https://laravel.com/docs/{version}/{package}` — e.g., `/13.x/fortify`, `/13.x/sanctum`, `/13.x/horizon`, `/13.x/pulse`.
- API reference (when you need exact method signatures): `https://api.laravel.com/docs/{version}/`.

If you don't know the exact slug, use `WebSearch` with a query like `site:laravel.com/docs/13.x eloquent hasManyThrough` and then `WebFetch` the top hit.

Prefer fetching the single topic page over scraping the whole docs. Topic pages are self-contained.

## Step 3: Supplement with other authoritative sources

When `laravel.com/docs` is thin on a topic, reach (in this order) for:

1. **Official package README on GitHub** — `github.com/laravel/{package}` (e.g., `github.com/laravel/fortify`). Good for install/config steps and version-compatibility matrices.
2. **Laravel source code** — `github.com/laravel/framework/tree/{version}/src/...`. Use when you need the exact signature/behavior of a method that's under-documented. Link to the specific file + line.
3. **Laravel News** (`laravel-news.com`) — good for release notes, "what's new in 13.x", and migration guides between major versions.
4. **Taylor Otwell / core maintainer posts** — reliable when docs are out of date around a fresh release.

Avoid: random Medium posts, StackOverflow answers from before the current major version, and tutorial sites that don't date-stamp content. If you must use them, cross-check against the official docs before using the information.

## Step 4: Apply and cite

When you use a fact pulled from docs, tell the user where it came from. A short inline citation is enough:

> Per `laravel.com/docs/13.x/eloquent-relationships#has-many-through`, the `hasManyThrough` signature is `hasManyThrough(related, through, firstKey, secondKey, localKey, secondLocalKey)`.

Citations matter because they let the user verify the claim themselves and because they force you to actually open the page instead of paraphrasing from memory.

For code you write, match the conventions shown in the docs for the pinned version (e.g., Laravel 11+ uses the streamlined `bootstrap/app.php` and `routes/console.php` — don't generate `app/Console/Kernel.php` code on a fresh 11+ project).

## When to lookup vs. when to skip

**Lookup:**
- Any method signature or config key you're not 100% sure exists in this version.
- Anything that changed across recent majors (middleware registration, exception handling, scheduling, broadcasting auth, mail configuration, queue serialization).
- First-party packages you haven't touched in this session — their APIs drift independently of framework version.
- Testing helpers — Pest/PHPUnit integration, HTTP test assertions, and browser-test APIs (Dusk/Pest 4 browser) change often.
- Deprecations — if you're about to use a helper and a voice in your head says "is this still a thing?", it probably isn't. Check.

**Skip lookup:**
- Pure PHP language features (use your PHP knowledge directly).
- Logic inside a method body where the surrounding Laravel API has already been confirmed this session.
- Trivial edits (formatting, renames, comments).
- Things already documented in the project's own `CLAUDE.md` / `README.md` for this exact version.

## Pairing with other skills

This skill is the **research** layer. Pair it with:
- `laravel-best-practices` (project-level) — patterns and conventions for writing idiomatic Laravel. Use docs-lookup to verify APIs, then best-practices to decide structure.
- `fortify-development`, `wayfinder-development`, `pest-testing`, `inertia-svelte-development` — domain skills. When they trigger, still do a docs-lookup for the specific APIs you'll touch; the domain skills assume docs knowledge, they don't replace it.

## Caching within a session

Don't re-fetch the same page repeatedly inside one conversation. Once you've pulled a doc page, the relevant facts are in context — refer back to them. Re-fetch only when the user switches to a different Laravel version, a different package, or enough turns have passed that the page may have scrolled out of your context window.
