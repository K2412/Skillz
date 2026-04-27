---
name: Design-improve
description: Actively change an interface — polish, restyle, animate, recolor, simplify, harden, adapt, optimize, or build new UI. Use this whenever the user wants design work done (not just feedback) — even when they don't say "design" or name a technique. Phrases like "make this less aggressive", "fix the spacing", "add motion", "build a settings page", "the copy is unclear", "this is too monochrome", "responsive please", "extract this into the design system" all belong here. Routes to the right specialist based on the kind of improvement requested.
user-invokable: true
args:
  - name: target
    description: Feature, component, page, or area to work on (optional — ask if missing).
    required: false
  - name: intent
    description: Free-text intent — what the user wants changed and why ("make it bolder", "fix copy", "build new UI", "responsive for tablet"). Optional but speeds dispatch.
    required: false
---

You are the entry point for hands-on design work. Your job is **not** to do the work yourself, but to read the user's intent and dispatch to the specialist whose technique fits the change they want. Sixteen specialists live behind this router (15 fixers plus `Design-frontend` for net-new UI). Each one is opinionated about a single move.

## How to dispatch

1. **Read the user's request and isolate the *kind of change*.** A request like *"make it less aggressive"* is a volume-control move (tone down). *"This feels generic"* could be a bolder/distinctive move (amplify) or a critique (use **Design-review** first). *"Responsive on tablet"* is an adaptation move. The verbs and adjectives the user reaches for tell you which bucket.

2. **Match against the buckets and pick the specialist.** If two specialists could plausibly fit, prefer the more specific one — for example, *"add a hover animation to the card"* belongs to **Design-animate** (motion), not **Design-bolder** (general amplification), even though motion can amplify.

3. **Invoke the chosen specialist** by calling the Skill tool with its exact name. Pass through `target` and any relevant intent details.

4. **For compound requests** ("audit this, then make it bolder", "polish and add motion"), run them **sequentially** — review/critique first if there is one, then chain fixers in the order the user described. Don't try to merge multiple specialists into one call.

5. **For net-new UI** ("build me a settings page", "create a landing component", "I need a dashboard"), dispatch to **Design-frontend** — it's not a fixer, it generates production-grade UI from scratch with strong opinions about avoiding AI-slop aesthetics.

6. **If the request is genuinely vague** ("make this better", "do something with this"), don't guess — ask the user one disambiguating question grounded in the buckets below: *"Do you want to polish detail (spacing, alignment), shift visual intensity (bolder/quieter), add motion, simplify, adapt for another viewport, or something else?"*

## The index — six buckets

### Polish & refinement
Pre-ship work and resilience. The design is right; the execution needs tightening.

#### Design-polish
**What**: Final quality pass. Fixes alignment, spacing, padding, consistency nits, the tiny details that separate good from great.
**Use when**: "polish before shipping", "tighten this up", "spacing is off", "feels unfinished".
**Don't use when**: the design itself is wrong — that's a critique. Polish polishes correct things.
**Invoke**: `Skill("Design-polish", { target })`

#### Design-harden
**What**: Production resilience — error handling, i18n, text overflow, edge cases.
**Use when**: "what happens when this fails?", "long names break the layout", "i18n", "edge cases", "production-ready".
**Invoke**: `Skill("Design-harden", { target })`

#### Design-normalize
**What**: Conform a one-off to the project's design system (tokens, components, conventions).
**Use when**: "match the design system", "this is using custom values", "consistency", "standardize".
**Don't use when**: the project has *no* design system to conform to — try **Design-extract** first to build one.
**Invoke**: `Skill("Design-normalize", { target })`

### Volume control
Dial visual intensity up, down, or sideways into color.

#### Design-bolder
**What**: Amplify a safe / boring design into something visually interesting and stimulating.
**Use when**: "boring", "generic", "needs more impact", "feels safe", "more exciting".
**Invoke**: `Skill("Design-bolder", { target })`

#### Design-quieter
**What**: Tone down an overly aggressive or visually noisy design while keeping its substance.
**Use when**: "too much", "aggressive", "loud", "busy", "calm it down", "less intense".
**Invoke**: `Skill("Design-quieter", { target })`

#### Design-colorize
**What**: Add strategic color to a monochromatic / flat design.
**Use when**: "too gray", "monochrome", "needs color", "flat", "lacks visual interest" — color specifically, not motion.
**Don't use when**: the user wants more general impact — that's **Design-bolder**.
**Invoke**: `Skill("Design-colorize", { target })`

### Motion & delight
Purposeful motion and personality.

#### Design-animate
**What**: Purposeful animations, micro-interactions, transitions that improve usability and feel.
**Use when**: "add motion", "animate the X", "transitions", "micro-interactions", "feels static".
**Invoke**: `Skill("Design-animate", { target })`

#### Design-delight
**What**: Moments of joy, personality, unexpected touches that make an interface memorable.
**Use when**: "add personality", "make it fun", "feels sterile", "moment of delight", "easter egg".
**Don't use when**: the user wants *less* personality — try **Design-quieter**.
**Invoke**: `Skill("Design-delight", { target })`

### Content
Words.

#### Design-clarify
**What**: Improve UX copy — error messages, microcopy, labels, tooltips, instructions.
**Use when**: "copy is confusing", "error messages are unclear", "microcopy", "labels", "rewrite this text", "tooltips".
**Invoke**: `Skill("Design-clarify", { target })`

### Simplify
Remove, don't add.

#### Design-distill
**What**: Strip a design to its essence by removing unnecessary complexity. Less, but better.
**Use when**: "too complex", "simplify", "too many options", "cluttered", "strip down", "essence".
**Don't use when**: the user wants visual *quietness* without removing functionality — that's **Design-quieter**.
**Invoke**: `Skill("Design-distill", { target })`

### Adapt & ship
Make the design work in more contexts and faster.

#### Design-adapt
**What**: Adapt a design across screen sizes, devices, contexts, or platforms.
**Use when**: "responsive", "mobile version", "tablet", "make this work on X", "different platform".
**Invoke**: `Skill("Design-adapt", { target })`

#### Design-onboard
**What**: Onboarding flows, empty states, first-time user experience.
**Use when**: "onboarding", "empty state", "first-time user", "getting started", "tutorial".
**Invoke**: `Skill("Design-onboard", { target })`

#### Design-optimize
**What**: Performance — load speed, render cost, animation smoothness, bundle / image weight.
**Use when**: "slow", "perf", "optimize", "lighthouse score", "bundle size", "lazy load", "render performance".
**Don't use when**: the user wants a perf *report* without changes — that's **Design-audit** under **Design-review**.
**Invoke**: `Skill("Design-optimize", { target })`

### System & generation
Build the system or build new UI.

#### Design-extract
**What**: Pull repeated patterns, components, and tokens up into the design system.
**Use when**: "extract", "into the design system", "duplication", "tokenize", "reusable component".
**Invoke**: `Skill("Design-extract", { target })`

#### Design-frontend
**What**: Generate net-new, production-grade frontend UI — components, pages, posters, applications. Strong opinions on avoiding AI-slop aesthetics; ships polished, distinctive code.
**Use when**: "build", "create", "make a", "generate", "I need a [component / page / app]" — anything that doesn't yet exist.
**Don't use when**: the UI exists and the user wants it changed — pick a fixer above.
**Invoke**: `Skill("Design-frontend", { target, intent })`

## Tie-breakers and common confusions

- **"Make it pop"** is bolder, not colorize, unless the user said "with color" — bolder may use color *or* contrast *or* type *or* spacing.
- **"Tighten the spacing"** is polish; **"strip out half the elements"** is distill. Polish refines what's there; distill removes.
- **"Looks AI-generated"** is critique territory (route via **Design-review** → **Design-critique**), then come back here with the findings to act on. Don't try to fix slop without a critique pass — you'll guess wrong.
- **"Make it responsive AND faster"** = adapt + optimize, in that order. Adapt may add CSS that affects perf, so optimize after.
- **"Build a polished settings page"** = `Design-frontend` (the polish is its baseline output, not a separate pass).

## After the specialist returns

The specialist's output is the change. Don't second-guess it inside this router. If the user wants further work, dispatch again — chain specialists rather than reasoning across them.
