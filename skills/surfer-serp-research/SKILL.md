---
name: surfer-serp-research
description: >-
  Use when the user wants to analyze the SERP or research keywords with Surfer to plan content
  before writing — e.g. "analyze the SERP for X", "what do the top-ranking pages cover", "run the
  SERP analyzer", "competitor terms for this keyword", "build a content brief". Not for writing the
  article itself (use surfer-write-article).
license: MIT
---

# Surfer SERP Research

## Overview
Analyze the live SERP for one or many keywords in a location, then turn the top-ranking competitors, common terms, and structural norms into a content brief. Use before writing; not for drafting the article.

## Prerequisites
- **Capabilities & transport.** Each step names a Surfer capability ID (e.g. `content_editor.create`); none names a transport. At the first execution step, resolve the *active Surfer transport* (an adapter actually usable this session — not just files in a checkout). Exactly one usable → use it; several with none pinned → the default; **none usable → stop and ask the user which Surfer transport to install or use, and never improvise raw HTTP or assume an endpoint.** Don't mistake a missing credential for a missing transport. The active adapter owns auth, conventions, async waits, errors, idempotency, and pre-call doc/schema lookup; resolution rules and async/poll semantics live in `surfer-capabilities`.
- The SERP Analyzer is workspace-scoped and defaults to the org's oldest active workspace. To target a specific workspace, resolve an active id via `workspace.list` first.

## Playbook

1. **Confirm keyword(s), location, device.** Validate the location against `locations.list` (returns display-name strings like "United States"); it is paginated, so page through it before concluding a location is unavailable. If the location isn't listed, pick the closest and say so. Device defaults to `mobile`.

2. **Submit the analysis.**
   - One keyword: `serp_analyzer.analyze` → `{ id, state: scheduled }`.
   - Many keywords: `serp_analyzer.analyze_batch` → array of `{ id, state }`; per-item rejects come back inline as `{ error, input }`. Retry transient rejects (e.g. `rate_limit_exceeded`); treat `quota_exceeded`/`validation_error` as terminal and report them.
   - Capture every returned `id`, plus the workspace you submitted under.

3. **Await completion.** No SERP-Analyzer webhooks exist, so poll `serp_analyzer.list` (a workspace-wide CSV of recent queries; match rows by the `id`s from step 2) with backoff and an overall timeout (e.g. ~10 min). A query is terminal at top-level `state` `completed` (list states: `scheduled`, `completed`). When every captured `id` is terminal or times out, proceed to step 4 with the `completed` subset; if none completed, stop and report the failures/quota issues.

4. **Pull results** for each `completed` query (both CSV):
   - `serp_analyzer.get_search_results` — per-URL SERP factors for up to the top 50 competitors (structural counts, keyword usage, content score, page speed). Each row carries its own crawl `state` (`scheduled`/`failed`/`completed`); skip non-`completed` rows. If a query has no `completed` rows, exclude it from the brief and note the SERP couldn't be analyzed.
   - `serp_analyzer.get_prominent_terms` — prominent words/phrases with coverage and density. Only populated when the country has NLP disabled; if empty (NLP on), derive common terms from the search-results keyword-usage columns.

5. **Interpret the SERP.** Synthesize which competitors rank and how they differ (depth, format), flagging outliers (forums, video, brand pages) that shouldn't anchor the plan; recurring topical vocabulary with density; and structure norms as ranges (min/avg/max), not single numbers.

6. **Produce the brief.** Deliver inline: angle/intent, target word-count range, heading outline from competitor structure, priority terms, and subtopics/questions. Do not write the article.

   *Optional richer brief (only if the user explicitly wants it):* For Surfer's curated, scored guidelines (term ranges, topics & questions, per-factor structural targets), create a Content Editor via `content_editor.create` and wait for state `completed` — relevant event `content_editor.initialization.completed`, else poll `content_editor.get`. If it reaches `failed`, fall back to the inline brief above. Then read `seo_guidelines.get_competitors`, `seo_guidelines.get_terms`, `seo_guidelines.get_topics_and_questions`, `seo_guidelines.get_structure` (all require `completed`).

7. **Hand off.** To produce a draft, hand off to **surfer-write-article** with the keyword, location, and brief. To improve existing content, point to **surfer-optimize-content**. For AI-search / LLM visibility on the same keyword, point to **surfer-ai-search**.
