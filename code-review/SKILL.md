---
name: code-review
description: >
  Review a code change and give one clear answer — ship it, or here's what to fix — in a short,
  plain-English report a tired reviewer can act on in two minutes. Resolves a PR, a branch, or the
  working diff; reads the goal from Linear + the PR + any planning epic; runs a Standards and a Spec
  review in parallel; then reports a merge verdict, a four-beat orientation (the goal → what it
  touches → how the author attempted it → the issues that surfaced), only the findings worth blocking
  on (blockers + should-fixes, never nits), each explained to a bright intern with a ready-to-paste
  PR comment in your own voice. Use whenever the user wants a change reviewed or a merge call:
  "review this PR", "review my changes", "should I merge this", "review PR #214", "review this branch",
  "did the build match the plan", "code review", or as the review stage of /pair. It also holds the
  explainer: if the review doesn't land, or the user asks to "explain this diff / help me understand
  this change / walk me through this PR", it builds the full teaching artifact (background → intuition
  → literate diff → quiz) — the same HTML that /to-pr distils into a PR body. Prefer this skill over a
  raw `git diff` any time the user wants to understand or judge a change.
---

# Code Review — one answer: ship it, or here's what to fix

This skill does one job well: look at a change and tell the user, in plain words, **whether it's safe
to merge and what to fix if not**. The output is short on purpose. A reviewer at the end of the day
should get the verdict in one line, understand the change in four short beats, and see only the
findings that actually matter — each explained so clearly they don't have to ask "wait, what?".

It has two modes:

- **Review** (default) — the verdict pass. Runs below.
- **Explain** — the teaching pass. Builds the full HTML explainer + quiz. Triggered when the user
  asks to *understand* rather than *judge* ("explain this diff", "help me understand this change",
  "walk me through this PR"), or when a review didn't land and they want the deep dive. Jump to
  [`references/explainer.md`](references/explainer.md) and follow it; skip the rest of this file.

The two axes of the review — **Standards** and **Spec** — run as separate subagents so their contexts
never bleed into each other. A change can pass one and fail the other, and keeping them apart is what
lets that show. Everything else (resolving the target, writing the goal, distilling the findings) is
done in the main thread.

## What "concise" means here (read this first)

The point of this skill is to fight two failure modes at once: **too slow** and **too much to read**.
So the discipline is:

- **Verdict first.** The very first line after the title is the merge call. Everything else is there
  to justify it, and the user can stop reading once they trust it.
- **Only should-fixes and blockers.** A finding earns a place only if you'd genuinely ask for the
  change before merge. **Drop every nit** — style tooling already catches, wording of a comment or
  UI string, "the pattern to notice next time", speculative "you could also". Nits are not made
  concise by shortening them; they're removed. Say *how many* you dropped so the omission reads as a
  choice, not an oversight.
- **Explain to a bright intern.** This is the core fix for the "I read the finding and still don't
  know what it means" problem. Every finding is written for someone sharp but new: no unglossed
  jargon (if you must say "race condition" or "N+1 query", say what it means in the same breath),
  lead with the concrete consequence ("if two people hit save at the same moment, the second one
  silently wins"), not the abstract principle ("this violates atomicity"). Two or three sentences,
  no more.
- **No walls of text.** Four short orientation beats, then the findings. If a beat needs a paragraph,
  it's too long — cut it to the load-bearing sentence.

## Step 1 — Resolve the target and gather the goal

Work out what to review, in this order. Ask only if genuinely ambiguous.

- **A GitHub PR** (URL or number) — the primary case:
  ```bash
  gh pr view <n> --json title,body,author,baseRefName,headRefName,url,files,closingIssuesReferences
  gh pr diff <n>
  ```
- **A branch** ("this branch", a branch name) → `git diff <base>...HEAD`; infer the base from
  `git symbolic-ref refs/remotes/origin/HEAD` or the merge-base.
- **The working diff** ("my changes", "what I just did") → `git diff HEAD` and `git status`.

Pin the base with a **three-dot merge-base** (`origin/dev...HEAD` or `origin/main...HEAD`) so
feature-branch noise is excluded, and grab the commit list (`git log <base>..HEAD --oneline`).
**Confirm the diff is non-empty in the main thread** — an empty or bad ref should fail here, not
inside a subagent.

Then gather **the goal** — what this change set out to do. This is both the Spec axis's yardstick and
the first orientation beat, so collect it once:

- **The PR description** (from `gh pr view` above).
- **Linked Linear tickets.** A PR body or branch name often carries a ticket id (e.g. `SIG-520`). Pull
  the ticket to read what was asked. **Read-only** — never comment on, edit, or move a Linear ticket;
  what appears there is the user's to write.
- **A linked planning epic.** If the change references a `K2412/planning` epic, pull its acceptance
  criteria: `gh issue view -R K2412/planning <n> --json title,body,labels`. This is the approved
  spec when it exists.

If there are **no** acceptance criteria anywhere, the Spec axis runs in reduced mode against the PR's
*stated intent* only — say so plainly rather than inventing a spec.

Read the epic's `stack:*` labels if a planning epic is in play — a `stack:react` / `stack:dagster`
label routes the matching `best-practices` lens into the Standards axis (Step 2).

## Step 2 — Run Standards and Spec in parallel

Send **one message with two `Agent` calls** (`subagent_type: "claude"`). They share the diff, commit
list, and goal from Step 1; each gets its own clean context. Keep each subagent's brief **under 400
words of output** — they feed a concise report, so a sprawling subagent return defeats the purpose.

**Experts lane is off by default** — it's the main source of the old overload. Only add it when the
user explicitly asks for a domain deep-dive ("hold this to the experts", "run the experts pass") or
passes `--experts`; then follow [`references/experts-lane.md`](references/experts-lane.md) as a third
subagent.

---

**Standards subagent prompt:**

```
Review the diff below against (a) this repo's documented standards and (b) the Fowler smell baseline.

## Diff
<paste: git diff <base>...HEAD>

## Commits
<paste: git log <base>..HEAD --oneline>

## Repo standards
Check pyproject.toml / ruff.toml (or the repo's linter config) for configured thresholds. If none:
- File length: 300 lines · Function length: 50 lines · Cyclomatic complexity: 10 · Arguments: 5
For Reflex projects (files touching rx.State subclasses): State holds UI state, exposes event
handlers, delegates work — no inline business logic; transformations live in service modules;
computed vars are simple derivations. Check docs/Arch/reflex-patterns.md if present.

## Stack best-practices (only if the epic carries a stack:* label)
<Include only when the epic has stack:react or stack:dagster; otherwise omit this section.>
Invoke the `best-practices` skill via the Skill tool with the stack from the label (`react` and/or
`dagster`). Hold the diff to those rules and cite the rule the way that skill asks (e.g. Vercel
section "1.5 Promise.all() for Independent Operations").

## Fowler smell baseline (always applies; repo standards override where they conflict)
Each smell is a judgement call, not a hard violation. Skip anything tooling already enforces.
- Mysterious Name — a name that doesn't reveal what it does/holds → rename; if no honest name comes, the design's murky.
- Duplicated Code — the same logic shape in more than one hunk → extract it, call from both.
- Feature Envy — a method reaching into another object's data more than its own → move it onto that data.
- Data Clumps — the same fields travelling together → bundle into one type.
- Primitive Obsession — a primitive standing in for a domain concept → give it its own small type.
- Repeated Switches — the same switch/if-cascade on the same type → replace with polymorphism.
- Shotgun Surgery — one logical change forcing scattered edits → gather what changes together.
- Divergent Change — one file edited for several unrelated reasons → split by responsibility.
- Speculative Generality — abstraction for needs the spec doesn't have → delete it.
- Message Chains — long a.b().c() navigation → hide the walk behind one method.
- Middle Man — a class that mostly just delegates → cut it, call the real target.
- Refused Bequest — a subclass ignoring most of what it inherits → use composition.

## Brief
Per file/hunk, report: (a) every documented-standard violation — cite the rule; (b) any stack
best-practice violation if that lens applies — cite the rule; (c) any smell — name it and quote the
hunk. Documented standards override the baseline; smells are judgement calls. Skip anything tooling
enforces. For EACH finding, classify severity honestly:
- blocker  = a correctness defect that ships broken behaviour to a user.
- should-fix = a real design/maintainability problem a careful reviewer would ask to change first.
- nit = style, wording, or "pattern to notice" — anything you would not block a merge on.
Give each finding as: [severity] File:Line — one plain sentence on what's wrong · one plain sentence
on the concrete consequence · (for blocker/should-fix) a one-line before→after or the fix in words.
No jargon without a gloss. Under 400 words.
```

---

**Spec subagent prompt:**

```
Review the diff below against the goal it was meant to satisfy.

## Diff
<paste: git diff <base>...HEAD>

## Commits
<paste: git log <base>..HEAD --oneline>

## The goal (the approved spec)
<paste: PR description + linked Linear ticket(s) + planning-epic acceptance criteria — whichever exist.
If none exist, say so and review against the PR's stated intent only.>

## Brief
Report: (a) acceptance criteria (or stated intent) that are missing or only partially implemented —
quote the criterion; (b) behaviour in the diff that nothing asked for (scope creep); (c) criteria
that look implemented but where the implementation looks wrong. Classify each as blocker /
should-fix / nit using the same definitions the Standards reviewer uses (blocker = broken behaviour
shipped to a user). Write each finding in plain English — lead with the consequence, gloss any
jargon. Under 400 words.
```

## Step 3 — Distil to the concise report

Both lanes have returned. Now write the report the user actually reads. **Do not paste the subagent
returns.** They are raw material; your job is to distil them into the structure below, dropping every
nit and rewriting each surviving finding for a bright intern.

Build the four orientation beats yourself from the inputs you already gathered (the diff, the goal,
the changed files) — this is the "here's the story of this change" framing that makes the findings
land, because the reader is oriented before they hit a single problem. Keep each beat to one to three
sentences.

Use this exact shape:

````
# Review — <plain-words title of what the change does>
<source → base · N files> · <Linear id / epic ref if any>

**🟢 Ship it** — nothing here blocks merge.
   — or —
**🟡 Fix first** — <n> should-fix(es) below, no hard blockers.
   — or —
**🔴 Don't merge yet** — <n> blocker(s): <the one-line worst>.

## The goal
<1–2 sentences, plain English: what problem this change set out to solve. From Linear + the PR.>

## What it touches
<1–3 sentences: the parts of the system this change reaches and how they connect — the files/modules
and the seam between them. Enough that the findings below have somewhere to land.>

## The attempt
<1–3 sentences: how the author went about it — the approach and the one or two load-bearing changes.
This is the "here's what they did" beat, in words, not a diff dump.>

## The issues
<Only blockers and should-fixes. If there are none: "None worth blocking on." Otherwise, per finding:>

### 🔴 Blocker · `path/file.py:42`   (or  ### 🟡 Should fix · `path/file.py:88`)
<Plain English, intern-level: what's wrong, no unglossed jargon — 1 sentence.>
Why it matters: <the concrete consequence, in real terms — what actually goes wrong for a user or the
next engineer — 1 sentence.>
```
<the ready-to-paste PR comment, in the user's voice — see below>
```

## What I left out
<n> nit(s) and wording note(s), not shown — say the word if you want them. <If the experts lane
wasn't run:> Domain-standards (experts) pass not run — ask for `--experts` if you want it.

## Want the deep dive?
If any of the above didn't land, say "explain it" and I'll build the full walkthrough — background →
intuition → literate diff → a short quiz — the same explainer /to-pr distils into a PR body.
````

**The paste comment — write it in the user's voice, not the report's.** The finding's prose above is
teaching (for the reader's understanding); the fenced comment is what they drop onto the PR for the
author. The house default, drawn from how this user actually comments:

- One line. No headers, no bold, no severity label, no before/after snippet, no praise padding.
- Lowercase start, symbols in backticks, a space before the closing ` ?`.
- Phrased as a **question that invites the author to check**, not a directive — "is it possible to
  reuse `X` ?", "can you double check the per-tenant isolation if this errors ?", "do you think this
  breaks on a daylight-savings switch ?". The author usually knows something you don't; the question
  leaves them room to say so.

If you're reviewing in a repo whose owner comments differently, read their last few and match them:
`gh api repos/<owner>/<repo>/pulls/<n>/comments --jq '.[] | select(.user.login=="<them>")'`.

Order the findings by how much they matter, worst first.

## Step 4 — Gate

```
question: "Review done. What next?"
options:
  - "Present findings — I'll decide what to act on (Recommended)"
  - "Explain it — build the full walkthrough + quiz"
  - "Post the comments as a PR review"
  - "Accept as-is"
```

- **Explain it** → switch to explain mode: follow [`references/explainer.md`](references/explainer.md)
  on the same change, then hand back the HTML path.
- **Post to the PR** is outward-facing and stays the user's call — only run
  `gh pr review <n> --comment` (or `--request-changes`) if they pick it. The paste blocks exist so the
  user can post in their own hands; that's the default path.
- **Accept as-is**, when this ran against a planning epic and all findings are resolved or accepted,
  closes the epic: `gh issue close -R K2412/planning <epic-n>`. Then show a one-line summary — epic
  closed, what shipped, any deferred follow-ups.

## Pipeline notes (when called from /pair)

`code-review` is the review stage of `/pair`, replacing the old two-axis stage. Two behaviours carry
over from that role:

- **Intent trace.** If a design sketch exists in `docs/sketches/` (from `sketch-change`, written
  before the build), read it as intent-origin: what the change set out to be. Narrate intent →
  outcome in **The attempt** beat — which contested decisions landed, where the direction changed.
  Deliberate course-corrections are the story, not a fault; only flag drift with **no** trace to a
  grill decision or spec choice. The epic stays the acceptance bar, not the sketch.
- **Stack labels** route `best-practices` into the Standards lane (Step 1/2), not as a separate stage.

## Done when

The verdict is the first line and it's unambiguous (ship / fix first / don't merge). The four beats
orient a newcomer to the change before any finding. Every surfaced finding is a blocker or should-fix,
written so a bright intern gets it without asking, and carries a one-line paste comment in the user's
voice. The nits are counted, not shown. A lane that had nothing to say says so — a silent lane must
never read as a clean bill of health. The report ends with the offer to go deeper, so understanding is
always one word away.
