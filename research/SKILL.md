---
name: research
description: Investigate a question against high-trust primary sources, web search, site scraping and crawling (Firecrawl), and Mobbin UI examples, then capture findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, a whole doc site read, UI patterns explored, or reading legwork delegated to a background agent.
---

Spin up a **background agent** to do the research, so you keep working while it reads.

This is a utility other stages call, not just a standalone: [`grill`](../grill/SKILL.md) and
[`spec`](../spec/SKILL.md) call it when *pinning requirements* needs an outside fact. It answers "is
it true / what exists / what do others do" — facts with citations, not a recommendation.

Its job:

1. Investigate the question against **primary sources** — official docs, source code, specs, first-party APIs — not a secondary write-up of them. Follow every claim back to the source that owns it.
2. **Web search** for supplementary context, recent changes, or community consensus — but always trace any claim back to a primary source before including it.
3. **Read deeply with Firecrawl.** Web search *finds* a page; Firecrawl *reads* it. Reach for it whenever `WebFetch` hands back an SPA shell, a JS-rendered page, a paywall stub, or one page isn't enough and you need a whole doc site. Match the tool to the operation:
   - `mcp__firecrawl__firecrawl_search` — search the web and get clean, scraped markdown back in one call; the default when you're both finding *and* reading.
   - `mcp__firecrawl__firecrawl_scrape` — one known URL to clean markdown, with JS rendered. Use over `WebFetch` when the page is dynamic or `WebFetch` returned nothing useful.
   - `mcp__firecrawl__firecrawl_map` — enumerate every URL under a site *without* fetching their content, to find the right pages before you read them.
   - `mcp__firecrawl__firecrawl_crawl` — collect many pages across a doc site or section at once (async; poll `mcp__firecrawl__firecrawl_check_crawl_status`).
   - `mcp__firecrawl__firecrawl_extract` — pull the same structured fields across one or more pages when you need data, not prose.

   Firecrawl only changes *how* you read a source — cite it by its URL exactly as you would a `WebFetch`, and still trace every claim back to a primary source.
4. **Search Mobbin** for real-world UI/UX examples when the question touches design, flows, or patterns. Use all three tools as relevant:
   - `mcp__mobbin__search_flows` — end-to-end user flows (onboarding, checkout, auth, etc.)
   - `mcp__mobbin__search_screens` — individual screen layouts and patterns
   - `mcp__mobbin__search_sections` — specific UI components or sections within screens
   Include relevant examples in the findings with the app name and flow context as the citation.
5. Write the findings to a single Markdown file, citing each claim's source (URL for web/docs, app name + flow for Mobbin).
6. Save it where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible and say where.
