---
name: surfer-optimize-content
description: >-
  Use when the user has existing content — a URL or draft — and wants it to score better against
  Surfer's SEO guidelines. Triggers: "optimize my article", "improve this page's content score",
  "auto-optimize this", "make this rank better". Not for writing new content (use
  surfer-write-article) or AI-search / LLM visibility (use surfer-ai-search).
license: MIT
---

# Surfer: Optimize Existing Content

## Overview
Raise the Surfer SEO score of content the user already has (a live URL or pasted draft) against a target keyword, via a Content Editor. If the content does not exist yet, hand off to surfer-write-article; for AI-search/LLM visibility, hand off to surfer-ai-search.

## Prerequisites
- An active `workspace_id` (via `workspace.list`).
- A target keyword (mandatory) AND either an import URL or raw HTML/Markdown. If the keyword is missing, ask the user; do not proceed.
- Optional: secondary keywords, location, device, target score (default 70+).

Async waits below: poll the named GET (webhook events need a configured receiver) on surfer-api's bounded-poll schedule; on timeout, a `failed` state, or auth/workspace failure, report and stop.

## Playbook

1. **Get or create the Content Editor.** Reuse an existing id (`content_editor.list`, or org-wide `content_editor.list_all`; both 90-day windowed), or `content_editor.create` with `main_keyword` plus, for a live page, `import_content_url`; pass secondary keywords/location/device as `secondary_keywords`/`location`/`device` (for pasted text omit `import_content_url`, load in step 3). Poll `content_editor.get` until `state` is `completed`, which most downstream calls require.

2. **Read the baseline.** SEO score: `seo_guidelines.get_score`. Targets: `seo_guidelines.get_terms` (each `included` term has `heading` and a `target_range`) and `seo_guidelines.get_structure` (absolute count = `target.avg × word_count`, the baseline `word_count`, not draft length). `seo_guidelines.get` returns everything at once but can be large.

3. **Ensure content is loaded.** URL-imported content is already present — inspect via `content_editor.get_content`. For pasted text, load it with `content_editor.update_content`, then re-read after recalc (step 5) before reading score.

4. **Optimize — pick a path:**
   - **A — Auto-optimize (hands-off):** `auto_optimize.run` applies changes directly (no review). Poll `auto_optimize.get` by `job_id` until `state` is `completed`, with `result` `optimized` or `nothing_to_optimize` (lost the id, use `auto_optimize.get_latest`). A `422` means nothing to optimize or quota exceeded — inspect the error body: on quota exceeded, abort and report (no retry); otherwise treat as nothing to optimize.
   - **B — Guided edit (control):** rewrite to satisfy step 2 — `included` terms within `target_range`, `heading: true` terms in headings, counts toward targets without stuffing — then push via `content_editor.update_content`.
   Combining is fine: auto-optimize, then hand-polish.

5. **Re-read after recalculation.** After auto-optimize, the `completed` job from 4A is the readiness signal; re-read `seo_guidelines.get_score`. After `content_editor.update_content` (4B), poll `seo_guidelines.get_score` until `status` is `ready` (`calculating` returns the prior stale score on recalc, `null` on a first score). `update_content` returns `204` and sanitizes the body — re-fetch `content_editor.get_content` to inspect what was stored.

6. **Iterate.** If short of target, re-read terms/structure for lagging factors and repeat steps 4–5. Stop when score ≥ target, `result` is `nothing_to_optimize`, the last gain is under ~2 points, or after ~3–4 iterations; report final score, delta from baseline, and what changed.

7. **Optional audit.** For signals beyond on-page coverage, `audit.create` (URL + keyword) then poll `audit.get`. Supplementary to the score loop.

If SERP-derived targets misfit intent, reshape before iterating with `seo_guidelines.update_competitors` (or `seo_guidelines.load_more_competitors` when `can_load_more_competitors` is true), `seo_guidelines.update_terms`, or `seo_guidelines.update_structure`, then re-read step 2.

## Calling Surfer
Run every capability through the surfer-api skill; fetch the capability's live doc before each call.
