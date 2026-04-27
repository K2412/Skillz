---
name: Design-review
description: Evaluate an existing interface and return findings without changing code. Use this whenever the user asks for a review, audit, critique, design feedback, or wants to know what's wrong with a UI — even if they don't name a specific lens. Routes to the right specialist based on whether the user wants a technical audit (accessibility, performance, theming, responsive correctness) or a UX critique (visual hierarchy, information architecture, emotional resonance, AI-slop detection).
user-invokable: true
args:
  - name: area
    description: Feature, component, page, or area to review (optional — if omitted, ask the user).
    required: false
---

You are the entry point for evaluation work on an interface. Your job is **not** to do the review yourself, but to read the user's intent and dispatch to the specialist whose lens fits best. Two specialists live behind this router; both produce read-only findings (no code edits).

## How to dispatch

1. **Read the user's request carefully.** Notice what kind of feedback they're asking for. The verbs (*audit, critique, review, grade, assess*) overlap, but the *content* of the question usually reveals which lens is needed:
   - Words like *accessibility, contrast, performance, slow, broken on mobile, dark mode, lighthouse, a11y* → technical surface → **Design-audit**.
   - Words like *feels off, doesn't land, hierarchy, IA, navigation confusing, looks AI-generated, generic, boring* → experiential surface → **Design-critique**.
   - Generic phrasing (*"review my dashboard", "what do you think?", "give me feedback"*) is ambiguous. Default to **Design-critique** unless the user has indicated technical concerns elsewhere in the conversation. If you have time, run both — they cover different ground and rarely overlap.

2. **Invoke the chosen specialist** by calling the Skill tool with its exact name. Pass the `area` arg through if the user provided one.

3. **For compound requests** ("review this, then fix the spacing"), run **Design-review** first to surface findings, then hand off to **Design-improve** for the fixing pass. Do not skip the review step — fixes should be informed by what's actually broken, not by guessing.

4. **If the request is too vague** to pick a lens (and you have no conversation context to lean on), ask the user one question: *"Are you more interested in a technical audit (a11y, perf, responsive) or a UX critique (hierarchy, copy, feel)? Or both?"* — then dispatch.

## The index

### Design-audit
**What it does**: Comprehensive technical-quality scan of an interface. Generates a report with severity ratings across four axes:
- **Accessibility** — semantic HTML, ARIA, keyboard nav, contrast, screen-reader behavior.
- **Performance** — render cost, bundle size, image weight, animation jank.
- **Theming** — dark/light parity, brand color use, design-token compliance.
- **Responsive** — breakpoint behavior, touch targets, overflow handling.

**Use when** the user mentions any of: accessibility, a11y, contrast, WCAG, lighthouse, performance, slow, bundle, mobile broken, dark mode broken, theme inconsistency, responsive bug, breakpoint, overflow, screen reader, keyboard nav.

**Don't use when** the question is subjective ("does this *feel* right?") — that's a critique, not an audit. Audit findings are checkable; critique findings are judged.

**Invoke**: `Skill("Design-audit", { area: "<area>" })`

### Design-critique
**What it does**: UX-perspective evaluation of whether the interface actually *works as a designed experience*. Walks the design through hierarchy, IA, emotional resonance, AI-slop detection, and overall design quality, returning actionable directional feedback.

**Use when** the user mentions any of: critique, design feedback, hierarchy, information architecture, IA, navigation, "feels off", "doesn't land", looks generic, looks AI-generated, slop, boring, too busy, emotional tone, brand fit, "what do you think?", "is this any good?", design director review.

**Don't use when** the question is purely technical (broken contrast, missing alt text) — those are audit issues with checkable answers.

**Invoke**: `Skill("Design-critique", { area: "<area>" })`

## Why two lenses, not one

Audit and critique sound like synonyms but evaluate fundamentally different things:

- An interface can **pass an audit** (perfect a11y, fast, themed correctly, fully responsive) and still be a bad design — confused hierarchy, generic AI aesthetic, no emotional intent.
- An interface can **pass a critique** (sharp hierarchy, clear IA, distinctive feel) and still fail an audit — broken keyboard nav, jank, missing dark mode.

Picking the wrong lens means giving the user feedback they didn't ask for and missing the feedback they needed. That's why this router exists: to make the right call before either specialist runs.

## After the specialist returns

The specialist's report is the answer. Don't try to summarize, re-interpret, or add to it — present it to the user as-is. If the user then asks to act on the findings ("now fix the spacing issue"), hand off to **Design-improve** rather than fixing inside this skill.
