---
name: taste-review
description: >
  Make a taste call — an independent judgment call on something ambiguous where you'd otherwise
  guess: UI polish, prose phrasing, naming, formatting, tone, layout. Shells out to a fresh
  `claude -p` for a second opinion untainted by this session's context, grounded in the target
  repo's own `design-patterns/patterns.md` so the verdict respects house style. Use whenever you
  hit a fuzzy "which reads better / which name is right / does this feel polished" decision and
  want a grounded outside call instead of picking blind — "make a taste call on this", "get a
  judgment call on the wording", "which of these is more on-brand", "is this UI polished enough".
---

You hit something fuzzy — a call on UI polish, prose phrasing, naming, formatting, tone — and you'd
otherwise just guess. Get an **independent** judgment instead: shell out to a fresh `claude -p` that
hasn't been anchored by this session's back-and-forth, and ground its call in the target repo's own
design patterns so the answer respects house style rather than generic taste.

Do this in order — the grounding step comes **before** the taste call, because an ungrounded verdict
is the thing this skill exists to avoid.

## 1. Read the design patterns from the target repo

Read `design-patterns/patterns.md` at the **root of the repo this skill is being run against** — the
codebase under `pwd`, not the Skillz repo the skill ships from. That file is the house style the
judgment must respect.

## 2. If `design-patterns/patterns.md` is absent — warn and pause

If the file does not exist, **stop and ask the user before shelling out**. Do not silently skip the
grounding, and do not hard-fail. Tell them the file is absent and offer the two paths:

> `design-patterns/patterns.md` isn't in this repo, so I have no house style to ground the taste
> call in. Do you want me to **(a)** make the call ungrounded — generic taste, no house style — or
> **(b)** create `design-patterns/patterns.md` first so this and future calls stay on-brand?

Wait for their answer.
- **(a)** → proceed to step 3 with an empty pattern context, and say in the prompt that no house
  style was available so the call is on general taste.
- **(b)** → create `design-patterns/patterns.md` with them first, then proceed with it as the
  context.

## 3. Shell out for the independent call

Run from the repo root so `claude` can read files by relative path.

Inject the patterns content into the prompt as the design-pattern context the judgment must respect —
that is the whole point of the grounding: the outside call weighs your options against *this repo's*
conventions, not taste in the abstract.

Run outside the sandbox when required, requesting reusable approval for the `claude -p` prefix. On
macOS, use the optional long-lived subscription OAuth token from Keychain when present. Otherwise,
fall back to that machine's normal Claude authentication.

Substitute your question, the file paths, and the contents of `design-patterns/patterns.md` (or a
line noting its absence) into the placeholders below.

```bash
prompt="$(cat <<'EOF'
<your question, stated plainly>

Files to consider: <paths, if any>

Design patterns this repo follows (from design-patterns/patterns.md — respect these over generic taste):
<paste the full contents of design-patterns/patterns.md here,
 or write "None found — design-patterns/patterns.md is absent; judge on general taste." if the user chose to proceed ungrounded>

Weigh a few options against those patterns, give your recommendation, and share the others as
alternatives considered. Call out any tension between a pattern and what looks best. Length is up to
you — a design call may warrant several paragraphs; a naming call may not. Match the depth to the
decision.
EOF
)"

if [[ "$(uname)" == "Darwin" ]] &&
  oauth_token="$(
    security find-generic-password \
      -a "$USER" \
      -s "Claude Code skill OAuth" \
      -w 2>/dev/null
  )"; then
  CLAUDE_CODE_OAUTH_TOKEN="$oauth_token" claude -p "$prompt"
else
  claude -p "$prompt"
fi
```

## 4. Apply the call

Report the independent verdict, note it was grounded in `design-patterns/patterns.md` (or flag that
it wasn't, if the user chose to proceed ungrounded), then apply it.

---

*Adapted from the [`taste-review`](https://github.com/bholmesdev/hubble.md/blob/main/.agents/skills/taste-review/SKILL.md)
skill in [hubble.md](https://github.com/bholmesdev/hubble.md) by Ben Holmes, used under the MIT
License. The `claude -p` shell-out with Keychain OAuth handling is from that original; the
`design-patterns/patterns.md` grounding is added here.*
