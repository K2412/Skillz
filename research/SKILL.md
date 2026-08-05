---
name: research
description: Investigate a question against high-trust primary sources, web search, and Mobbin UI examples, then capture findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, UI patterns explored, or reading legwork delegated to a background agent.
---

Spin up a **background agent** to do the research, so you keep working while it reads.

This is a utility other stages call, not just a standalone: [`grill`](../grill/SKILL.md) and
[`spec`](../spec/SKILL.md) call it when *pinning requirements* needs an outside fact. It answers "is
it true / what exists / what do others do" — facts with citations, not a recommendation.

Its job:

1. Investigate the question against **primary sources** — official docs, source code, specs, first-party APIs — not a secondary write-up of them. Follow every claim back to the source that owns it.
2. **Web search** for supplementary context, recent changes, or community consensus — but always trace any claim back to a primary source before including it.
3. **Search Mobbin** for real-world UI/UX examples when the question touches design, flows, or patterns. Use all three tools as relevant:
   - `mcp__mobbin__search_flows` — end-to-end user flows (onboarding, checkout, auth, etc.)
   - `mcp__mobbin__search_screens` — individual screen layouts and patterns
   - `mcp__mobbin__search_sections` — specific UI components or sections within screens
   Include relevant examples in the findings with the app name and flow context as the citation.
4. Write the findings to a single Markdown file, citing each claim's source (URL for web/docs, app name + flow for Mobbin).
5. Save it where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible and say where.
