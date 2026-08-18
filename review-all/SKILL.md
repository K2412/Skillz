---
name: review-all
description: One command to both evaluate and explain a pull request. Given a PR (URL, number, "this PR", a branch, or the working diff), it fans out four independent subagents in parallel — Standards (repo conventions + Fowler smells + stack best-practices), Experts (the experts MCP domain corpus), Spec (does it match the PR description + linked issues?), and Explain (an explain-diff HTML explainer + quiz, and a step-through walk when the change is runtime behaviour) — then aggregates them into one report. Use whenever the user wants a PR reviewed AND made legible in a single pass: "review PR #214", "review this PR", "evaluate and explain this pull request", "run the full review on this PR", "review-all", or hands you a GitHub PR link and wants both a quality verdict and an understanding artifact. For the working diff against a planning epic use /review-change; to only explain (no evaluation) use /explain-diff — review-all is the combined evaluate-and-explain pass over a PR.
---

# review-all — evaluate **and** explain a pull request, in one parallel pass

`review-all` is an orchestrator. It resolves a PR once, then fans out **four independent subagents in
a single message** so their contexts never pollute each other, and aggregates the results. Nothing
here is done in the main thread except gathering shared inputs and stitching the reports together.

```
resolve PR ──┬─▶ Standards  (repo conventions + Fowler smells + stack best-practices)
             ├─▶ Experts    (experts MCP domain corpus — routed to the owning expert)
             ├─▶ Spec       (PR description + linked issues → missing/partial criteria, scope creep)
             └─▶ Explain    (explain-diff HTML explainer + quiz, plus a step-through walk when the change is runtime behaviour)
                        │
                        ▼
                   aggregate → one report
```

The **Standards** and **Spec** lanes *are* the two axes of [`review-change`](../review-change/SKILL.md)
— reuse those prompts rather than reinventing them, so the Fowler baseline, thresholds, and finding
format stay single-sourced. `review-all` adapts their inputs to a PR and adds two lanes review-change
doesn't have: **Experts** (pulled out here as its own lane, so drop the experts section from the
Standards prompt to avoid double-reporting) and **Explain**.

## Step 1 — Resolve the PR and gather shared context

Figure out what to review, in this order of preference. Ask only if genuinely ambiguous.

- **A GitHub PR** (URL or number) — the primary case. Gather:
  ```bash
  gh pr view <n> --json title,body,author,baseRefName,headRefName,url,files,closingIssuesReferences
  gh pr diff <n>
  ```
- **A branch** ("this branch", a branch name) → `git diff <base>...<branch>`; infer base from
  `git symbolic-ref refs/remotes/origin/HEAD` or the merge-base.
- **Uncommitted work** ("what I just did") → `git diff HEAD` and `git status`.

Then settle the two things the lanes need:

- **The diff and commit list** — pin the base with a merge-base (`origin/main...HEAD` /
  `origin/dev...HEAD`) so feature-branch noise is excluded. **Confirm the diff is non-empty here** —
  an empty diff should fail in the main thread, not inside a subagent.
- **The spec source** — for a PR this is its **description + linked issues** (the
  `closingIssuesReferences` from `gh pr view`, plus any issue the body references). If the PR
  references a `K2412/planning` epic, pull its acceptance criteria too
  (`gh issue view -R K2412/planning <n> --json title,body`). If there are **no** acceptance criteria
  anywhere, the Spec lane runs in reduced mode — say so rather than inventing intent.

Also read the epic's `stack:*` labels if a planning epic is in play — a `stack:react` /
`stack:dagster` label routes the matching `best-practices` lens into the Standards lane (see below).

## Step 2 — Fan out four subagents in parallel

Send **one message with four `Agent` calls** (`subagent_type: "claude"`). They share the diff and
commit list gathered above; each gets its own clean context.

**Lane 1 — Standards.** Reuse the **Standards sub-agent prompt** from
[`review-change`](../review-change/SKILL.md) verbatim, with three adaptations:
1. the `## Diff` and `## Commits` come from the PR (Step 1), not `origin/dev...HEAD`;
2. **omit the "Experts standards" section entirely** — Experts is Lane 2 here;
3. keep the "Stack best-practices" section only if a planning epic carried a `stack:*` label.

**Lane 2 — Experts.** Spawn with this prompt:

```
Hold the change below to the relevant expert's domain standards from the `experts` MCP.

## Diff
<paste the PR diff>

## What to do
1. Summarise the diff in 1–2 sentences (what domain does it touch — software engineering, Python,
   Laravel, AI engineering, data engineering/analysis, GTM, zettelkasten?).
2. If the owning domain is obvious, call `review(artifact=<that summary>, expert=<domain>)` directly.
   If it's ambiguous or spans domains, call `route(artifact=<that summary>)` first to get the owning
   expert plus cross-domain challengers, then `review(expert=<the winner>)`; weigh the challengers too.
3. The corpus holds no LLM — the tools return Standards, supporting passages, a rubric, and a Finding
   schema for YOU to reason over. Do the judging yourself.

## Honesty rules
- Honour `low_confidence`: if the tools return it, the corpus has little to say here — report that
  plainly and DO NOT invent findings to fill space.
- If the `experts` MCP server isn't connected or a call errors, say so in one line and stop — never
  fail the review over a missing experts server.

## Brief
Per finding, cite the returned **Standard id** the way you'd cite a repo rule. Use review-change's
finding format ([blocker | should-fix | nit] File:Line — Principle / What / Why it matters /
Refactor / The pattern to notice next time). Under 350 words. If nothing clears the bar, say the
experts corpus surfaced no domain-standard issues on this change.
```

**Lane 3 — Spec.** Reuse the **Spec sub-agent prompt** from
[`review-change`](../review-change/SKILL.md), with the `## Diff`/`## Commits` from the PR and the
acceptance criteria replaced by the **spec source** from Step 1 (PR description + linked issues, or
the planning epic if referenced). If Step 1 found no acceptance criteria, tell the subagent to review
the diff against the PR description's *stated intent* only and flag that no formal criteria existed.

**Lane 4 — Explain.** Spawn a subagent that invokes the [`explain-diff`](../explain-diff/SKILL.md)
skill on this PR (it handles `gh pr diff <n>` natively) in **reviewer mode**, and returns the path to
the HTML explainer (and the walk file when one was warranted). Prompt:

```
Invoke the `explain-diff` skill (via the Skill tool) on <the PR — number/URL/branch> in reviewer
mode. Follow it to completion: build the mental model, write the explainer in teaching order, and
author the five-question quiz.

If the change is about *how the machine takes turns* — control flow, an event loop, a state
machine, concurrency, blocking vs yielding, or a multi-step migration — also emit the
**step-through walk** explain-diff describes (code pane + live runtime cards, one keypress per
beat). Follow `explain-diff/references/step-through.md`. Return both HTML paths. If the gate does
not fire, say "no walk — <one-line why>" so a missing walk reads as a choice.

Hold to explain-diff's default audience — **a bright intern on their first day** (zero assumed prior
knowledge, every acronym and term glossed on first use, Simplified Technical English, a generous
Background block). Don't tighten it: this reader is new to the codebase.

If an intent sketch exists in `docs/sketches/` (from `sketch-change`, produced before the build), read it
as the design *origin* and narrate intent → outcome: what we set out to build, and where the shipped
change went somewhere else. Deliberate course-corrections are expected — call them out as the story,
not as faults. If no sketch is present, skip this; it's optional context, not a requirement.

When done, return the explainer path, the walk path (or "no walk — <why>"), and a one-line note of
what the change does. Do not summarise the diff back to me.
```

## Step 3 — Aggregate

Stitch the four returns into one report. **Do not merge or rerank findings across lanes** — a PR can
pass one lane and fail another, and that distinction is the point.

```
# review-all — <PR title>
<source → base · N files> · explainer: explanations/explain-<slug>-<date>.html

## Standards
<Lane 1 findings>

## Experts
<Lane 2 findings — citing Standard ids, or "no domain-standard issues" / low_confidence note>

## Spec
<Lane 3 findings — or "no formal acceptance criteria; reviewed against stated intent">

## Explanation
Opened explanations/explain-<slug>-<date>.html — walk it and take the quiz before you sign off.
If a step-through exists, it is explanations/explain-<slug>-<date>-walk.html — step it before the
quiz; one question depends on it.
(Author mode rule from explain-diff still holds: don't approve a PR whose quiz you can't pass.)
```

End with **one line per lane**: finding count and the worst issue within that lane.

Then a short **synthesis** — this is where the lanes' independence pays off, so make it deliberate,
not incidental:

- **Convergence.** Name any finding that **two or more lanes caught independently** (e.g. a smell the
  Standards lane and a named Experts Standard both flag). Cross-lane agreement is a confidence
  signal — the lanes don't share context, so when they land on the same line the finding is very
  likely real. Say which lanes converged; don't merge or renumber the underlying findings.
- **Top blockers.** Pull out the **one to three findings you'd actually block the merge on**, across
  all lanes. Separate a genuine user-visible bug (a correctness defect that ships to a user) from a
  design or style call (defensible either way) — a reviewer needs to know which is which. If a
  blocker was inferred rather than observed (the Spec lane reasoning from two call sites, say), flag
  that it should be confirmed against real data before it's treated as certain.

## Step 4 — Ready-to-post comments

The report above is for the reviewer's own understanding: it explains, cites, and shows before/after.
That is the wrong register to paste at a colleague. So **always** close the report with a final
section the user can copy straight onto the PR, one comment at a time.

**What makes the cut.** Blockers and should-fixes only. Drop every nit. Drop any finding whose whole
substance is comment, docstring or UI-copy *wording* — a teammate reads that as nitpicking, and it
costs more goodwill than the fix is worth. A stale docstring that documents removed behaviour is
still just wording; a stale docstring that hides a real bug goes in as the bug. Where two lanes
caught the same thing, post **one** comment, not two.

**Voice.** Write these in the reviewing engineer's own voice, not the report's. The house default,
drawn from how this user actually comments:

- One line. No headers, no bold, no severity labels, no before/after snippets, no praise padding.
- Lowercase start, symbols in backticks, a space before the closing ` ?`.
- Phrased as a **question that invites the author to check**, not a directive — "is it possible to
  reuse `X` ?", "can you double check the per tenant isolation in the event of an error ?", "do you
  think this can pose an issue on Daylight savings time ?". The author usually knows something you
  don't; the question leaves them room to say so.
- State the observation, then ask. Never assert the fix is required.

If you are reviewing in a repo whose owner comments differently, read their last few first and match
them instead: `gh api repos/<owner>/<repo>/pulls/<n>/comments --jq '.[] | select(.user.login=="<them>")'`.

**Shape.** A fenced block per comment, with the anchor on the line above so it can be pasted into the
right place:

````
## Comments to post

**`path/to/file.py:123`**
```
one-line comment in the user's voice ?
```
````

Order them by how much they matter, most first. Close with a one-line note of what you deliberately
left out (the nits, the wording findings) so the user knows the omission was a choice.

Then gate:

```
question: "Review complete. What next?"
options:
  - "Present findings — I'll decide what to act on (Recommended)"
  - "Post the findings as a PR review comment"
  - "Accept as-is"
```

Only post to the PR (`gh pr review <n> --comment` / `--request-changes`) if the user picks that
option — writing to a PR is outward-facing and stays the user's call. The paste block exists so the
user can post in their own hands without you writing to the PR at all; that is the default path.

## Done when

All four lanes have returned, the explainer HTML is open in front of the user (and the step-through
walk too, when the gate fired), the three finding
sections are presented side by side without cross-lane merging, and each lane carries its one-line
count. A lane that had nothing to say (empty diff domain, `low_confidence` experts, missing spec, a
downed MCP) says so explicitly rather than being silently dropped — a missing lane should never read
as a clean bill of health. The report ends with the copy-paste comment block, nits and wording
findings excluded.
