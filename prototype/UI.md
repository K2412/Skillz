# UI Prototype

Generate **several radically different UI variations** on a single route, switchable from a floating
bar. The user flips between variants in the browser, picks one (or steals bits from each), then
throws the rest away. Use this when the question is **what should this look like** — appearance,
layout, information hierarchy.

If the question is about logic or state rather than appearance — wrong branch. Use [LOGIC.md](LOGIC.md).

## When this is the right shape

- "What should this page look like?"
- "I want to see a few options for this dashboard before committing."
- "Try a different layout for the settings screen."
- Any time the user would otherwise burn a day picking between three vague mockups in their head.

## Two sub-shapes — strongly prefer sub-shape A

A UI prototype is far easier to judge when it's **butting up against the rest of the app** — real
header, real sidebar, real data, real density. A route on its own is a vacuum where every variant
looks fine. Default to A whenever there's a plausible existing page to host the variants.

### Sub-shape A — adjustment to an existing page (preferred)

The route already exists. Variants render **on the same route**, gated by a `?variant=` URL search
param. Existing data fetching, params, and auth all stay — only the rendered subtree swaps. If the
thing being prototyped doesn't have a page yet but *would naturally live inside one* (a new section
of a dashboard, a new card, a new step in a flow), that's still sub-shape A — mount the variants
inside the host page.

### Sub-shape B — a new page (last resort)

Only when the thing genuinely has no existing page to live inside — an entirely new top-level
surface, or a flow that can't embed anywhere sensible. Create a **throwaway route** following the
project's existing routing convention (don't invent a new top-level structure); name it so it's
obviously a prototype (include `prototype` in the path). Same `?variant=` pattern. Before committing
to B, sanity-check that there's really no page to embed in — an empty route hides design problems a
populated one would expose.

## Process

### 1. State the question and pick N

Default to **3 variants**. Past 5 they stop being radically different and start being noise — cap
there. Write the plan in one line at the prototype's location: *"Three variants of the settings page,
switchable via `?variant=`, on the existing `/settings` route."*

### 2. Generate radically different variants

Variants must be **structurally different** — different layout, information hierarchy, primary
affordance — not just different colours. Three tweaked card grids isn't a prototype, it's wallpaper.
If two drafts come out too similar, redo one with explicit "do not use a card grid" guidance. Hold
each variant to the page's purpose, the data it has access to, and the project's component/styling
system (Tailwind, shadcn, MUI, plain CSS — whatever's there). Give each a clear exported name
(`VariantA`, `VariantB`, …).

### 3. Wire them together

One switcher on the route:

```tsx
// pseudo-code — adapt to the project's framework
const variant = searchParams.get('variant') ?? 'A';
return (
  <>
    {variant === 'A' && <VariantA {...data} />}
    {variant === 'B' && <VariantB {...data} />}
    {variant === 'C' && <VariantC {...data} />}
    <PrototypeSwitcher variants={['A', 'B', 'C']} current={variant} />
  </>
);
```

Sub-shape A: keep all existing data fetching above the switcher; only the rendered subtree changes.
Sub-shape B: the throwaway route mounts the same switcher.

### 4. Build the floating switcher

A small fixed bar at bottom-centre with three pieces: a **left arrow** (previous variant, wraps), a
**variant label** (current key + exported name, e.g. `B — Sidebar layout`), and a **right arrow**
(next, wraps).

- Clicking an arrow updates the URL search param via the framework's router (`router.replace`,
  `navigate`, …) so the variant is shareable and survives reload.
- `<-` / `->` arrow keys also cycle — but don't intercept them when an `<input>`, `<textarea>`, or
  `[contenteditable]` is focused.
- Visually distinct from the page (high-contrast pill, subtle shadow) so it's obviously not part of
  the design being evaluated.
- Hidden in production builds — gate on `process.env.NODE_ENV !== 'production'` or equivalent, so a
  stray merge can't ship the bar.

Put the switcher in one shared component both sub-shapes reuse, wherever shared UI lives.

### 5. Hand it over

Surface the URL and the `?variant=` keys. The most valuable feedback is usually **"I want the header
from B with the sidebar from C"** — that's the actual design they want.

### 6. Capture the answer and clean up

Once a variant wins, capture the answer and the prototype the way [SKILL.md](SKILL.md) describes.
The UI-specific mapping:

- **Sub-shape A** — fold the winner into the existing page (rewritten properly — it was built under
  prototype constraints); the losing variants and the switcher move to the `prototype/<slug>` branch,
  not into main.
- **Sub-shape B** — promote the winning variant to a real route; the throwaway route and switcher
  move to the branch.

The full set of variants is the primary source, so it lands on the branch as runnable evidence —
variants and a switcher left in main rot fast and confuse the next reader. Record the verdict (which
variant, and why) and the one thing you now understand about the design that the mockups-in-your-head
couldn't have told you.

## Anti-patterns

- **Variants that differ only in colour or copy.** That's a tweak. Real variants disagree about
  structure.
- **Sharing too much between variants.** A shared `<Header>` is fine; a shared `<Layout>` defeats
  the point — each variant should be free to throw out the layout.
- **Wiring variants to real mutations.** Read-only is fine; point any needed mutation at a stub. The
  question is "what should this look like", not "does the backend work".
- **Promoting prototype code straight to production.** Rewrite it properly when you fold the winner
  in.
