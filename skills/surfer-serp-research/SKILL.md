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
- An API key is required for every call except `locations.list` (see surfer-api).
- The SERP Analyzer is v1 and workspace-scoped via the `Workspace-Id` header (defaults to the org's oldest active workspace). To target a specific workspace, resolve an active id via `workspace.list` first.

## Playbook

1. **Confirm keyword(s), location, device.** Validate the location against `locations.list` (public, no key; returns display-name strings like "United States"); it is paginated, so page through it before concluding a location is unavailable. If the location isn't listed, pick the closest and say so. Device defaults to `mobile`.

2. **Submit the analysis.**
   - One keyword: `serp_analyzer.analyze` → `{ id, state: scheduled }`.
   - Many keywords: `serp_analyzer.analyze_batch` → array of `{ id, state }`; per-item rejects come back inline as `{ error, input }`. Retry transient rejects (e.g. `rate_limit_exceeded`); treat `quota_exceeded`/`validation_error` as terminal and report them.
   - Capture every returned `id`, plus the `Workspace-Id` you submitted under.

3. **Await completion.** No SERP-Analyzer webhooks exist, so poll `serp_analyzer.list` (a workspace-wide CSV of recent queries; match rows by the `id`s from step 2) with backoff and an overall timeout (e.g. ~10 min). A query is terminal at top-level `state` `completed` (list states: `scheduled`, `completed`). When every captured `id` is terminal or times out, proceed to step 4 with the `completed` subset; if none completed, stop and report the failures/quota issues.

4. **Pull results** for each `completed` query (both CSV):
   - `serp_analyzer.get_search_results` — per-URL SERP factors for up to the top 50 competitors (structural counts, keyword usage, content score, page speed). Each row carries its own crawl `state` (`scheduled`/`failed`/`completed`); skip non-`completed` rows. If a query has no `completed` rows, exclude it from the brief and note the SERP couldn't be analyzed.
   - `serp_analyzer.get_prominent_terms` — prominent words/phrases with coverage and density. Only populated when the country has NLP disabled; if empty (NLP on), derive common terms from the search-results keyword-usage columns.

5. **Interpret the SERP.** Synthesize which competitors rank and how they differ (depth, format), flagging outliers (forums, video, brand pages) that shouldn't anchor the plan; recurring topical vocabulary with density; and structure norms as ranges (min/avg/max), not single numbers.

6. **Produce the brief.** Deliver inline: angle/intent, target word-count range, heading outline from competitor structure, priority terms, and subtopics/questions. Do not write the article.

   *Optional richer brief (only if the user explicitly wants it):* For Surfer's curated, scored guidelines (term ranges, topics & questions, per-factor structural targets), create a Content Editor via `content_editor.create` and wait for state `completed` — relevant event `content_editor.initialization.completed`, else poll `content_editor.get`. If it reaches `failed`, fall back to the inline brief above. Then read `seo_guidelines.get_competitors`, `seo_guidelines.get_terms`, `seo_guidelines.get_topics_and_questions`, `seo_guidelines.get_structure` (all require `completed`).

7. **Hand off.** To produce a draft, hand off to **surfer-write-article** with the keyword, location, and brief. To improve existing content, point to **surfer-optimize-content**. For AI-search / LLM visibility on the same keyword, point to **surfer-ai-search**.

## Calling Surfer
Run every capability through **surfer-api**; fetch the live doc it points to for exact request/response shapes before each call.
