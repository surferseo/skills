---
name: surfer-ai-search
description: >-
  Use when the user wants better visibility in AI answer engines (AIO / GEO) — e.g. "optimize for
  AI search", "improve my AI/LLM visibility", "get my AI Search score", "help me get cited by
  ChatGPT / Perplexity / Gemini / Google AI Overviews". Not for classic SEO content-score
  optimization (use surfer-optimize-content).
license: MIT
---

# Surfer AI Search Optimization (AIO / GEO)

## Overview
Raise a page's Surfer AI Search score so generative answer engines (Google AI Overviews and AI Mode, Gemini, ChatGPT, Perplexity) are likelier to cite it; iterate to a target. For classic SEO content-score work hand off to surfer-optimize-content; to draft a new article, surfer-write-article.

## Prerequisites
- An active `workspace_id` (resolve via `workspace.list` if unknown).
- Either an existing Content Editor id, or content to bring in (a public URL to import, or raw text to push after creation).
- A target AI Search score — ask the user; if none given, default to 70+ and say so.
- If the user is unsure which keyword/location to target, hand off to surfer-serp-research first — facts and score are SERP/keyword-specific.

Async waits below: poll the matching GET (webhook events usable only if a receiver is configured). On timeout or any `failed`/`error` state, report and stop — don't poll forever.

## Playbook

1. **Get a completed Content Editor.** If the user has one, confirm `state` is `completed` via `content_editor.get`. Otherwise `content_editor.create` with the page's primary keyword as `main_keyword` plus `location`/`device` (optionally `import_content_url`); pick keyword + location to match the target SERP/engine pair (drives facts and score). Wait for `content_editor.initialization.completed` (first score computed during init); on `content_editor.initialization.failed` (or `state: failed`), stop and report. If bringing raw text (no import URL), the fresh editor has no body — after init, push it via `content_editor.update_content` and await recalc before step 2.

2. **Read the score** with `ai_search.get_score`. `status`: `ready` (current), `loading` (first calc, score null), `calculating` (recalc running, returned score is the stale prior value), `error`, `unavailable`. On `loading`/`calculating`, await `content_editor.ai_search_score.calculated`. On `.failed`/`error`, report and stop. `unavailable` means no score can be produced for this editor (e.g. unsupported keyword/locale or plan) — report and stop.

3. **Pull and interpret the facts** via `ai_search.get` (full payload incl. score) or `ai_search.get_facts` (facts only); they populate only when analysis `status` is `completed`. Each fact carries `sources[].url` and `cited_by` (`serp`, or a subset of `ai_mode`, `ai_overviews`, `gemini`, `openai`, `perplexity`). Report which facts the content covers, which it omits, and which are cited by AI engines (not just `serp`) — those cited by multiple AI engines are the highest-leverage gaps. Earn citations by covering them plainly, self-containedly, attributably.

4. **Revise, then recompute.** Read current content with `content_editor.get_content`, write the improved version with `content_editor.update_content`; it requires `completed` state (a `409 conflict` means the editor isn't ready — wait, then retry) and auto-triggers AI Search (and SEO) recalculation. Re-fetch `content_editor.get_content` to see what was stored. Await `content_editor.ai_search_score.calculated`; on `.failed`, report and stop the loop.

5. **Iterate.** Re-pull facts (they shift as content changes), target the next uncovered or AI-cited ones, revise, recompute. Stop when the score reaches the target, the user is satisfied, the gain over the prior round is under ~1 point, or after ~3–4 rounds. Report the final score, delta from baseline, and what changed.

## Calling Surfer
Execute every capability through surfer-api. Before each call, fetch the relevant live AI Search / Content Editors doc it points to.
