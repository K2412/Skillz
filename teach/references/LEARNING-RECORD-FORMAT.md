# Learning Record Format

Learning records live in `./learning-records/`, numbered `0001-slug.md`, `0002-slug.md`, … They are the teaching equivalent of ADRs: they capture non-obvious lessons, key insights, and stated prior knowledge that steer future sessions. They are how you calculate the zone of proximal development — read them at the start of every session.

## Template

```md
# {Short title of what was learned or established}

{1-3 sentences: what was learned (or what prior knowledge was established), and why it
matters for future sessions.}
```

That is the whole format. A record can be a single paragraph. The value is recording _that_ this is now known and _why_ it changes what to teach next — not in filling out sections.

## When to write one

Write a record when any of these is true:

1. **The learner demonstrated genuine understanding of something non-trivial** — evidence they can _use_ the concept, not just that they saw it. This sets a new floor for what to teach next.
2. **The learner disclosed prior knowledge** — "I already know X." Record it (and the depth claimed) so future sessions don't re-teach it.
3. **A misconception was corrected** — they believed something wrong and now see why. High-value: these predict future stumbling blocks on related topics.
4. **The mission shifted in response to learning** — cross-link to `MISSION.md` and update it.

### What does _not_ qualify
- Material merely covered. Coverage is not learning — wait for evidence.
- Anything already captured tersely in `GLOSSARY.md`. Don't duplicate.
- Session activity logs. These are decision-grade insights, not a journal.

## Optional sections (use only when they add value)
- **Status** frontmatter (`active | superseded by LR-NNNN`) when an earlier understanding is replaced.
- **Evidence** — how they demonstrated it (a question answered, a drill completed). Useful if the claim may be revisited.
- **Implications** — what this unlocks or rules out next.

## Supersession
When a later record contradicts an earlier one, mark the old one `Status: superseded by LR-NNNN` rather than deleting it. The history of how understanding evolved is itself signal.
