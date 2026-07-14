---
name: surfer-optimize-content
description: >-
  Use when the user has existing content — a URL or draft — and wants to improve its Surfer SEO
  Score, AI Search Score, or both. Triggers: "optimize my article", "improve this page's content
  score", "auto-optimize this", "make this rank better", or "optimize for SEO and AI search".
  Not for writing a new article (use surfer-write-article) or an AI-Search-only fact/citation
  investigation (use surfer-ai-search).
license: MIT
---

# Surfer: Optimize Existing Content

## Overview

Raise the selected Surfer score dimensions for a page or draft through a Content Editor. Treat the
unified Content Score as a diagnostic snapshot; optimize against the explicit SEO and/or AI Search
targets the user cares about.

## Prerequisites

- Resolve the active transport under `surfer-capabilities`. If no adapter can execute a required
  capability, name it and stop; do not improvise raw HTTP or assume an endpoint.
- Resolve an active `workspace_id` with `workspace.list`.
- Require a target keyword and either an import URL or raw HTML/Markdown. Ask for a missing
  keyword; do not guess it from the page alone.
- Ask which dimensions matter: SEO, AI Search, or both. If the user says only "optimize" default
  to SEO 70+; if they explicitly ask for both and give no targets, default to 70+ for each and say
  so. A missing AI Search score is not equivalent to zero.
- Treat brand knowledge, content type/template, custom instructions, and competitor selection as
  Content Editor setup. Load the mapping in `surfer-capabilities`' `content-workflows.md` before
  creating or changing an editor.

Use bounded waits only. On an explicit failure, unavailable score, or timeout, report the id and
state; never poll indefinitely.

## Playbook

1. **Create or reuse a Content Editor.** Reuse a matching editor through `content_editor.list` or
   `content_editor.list_all` when the user supplies one or clearly asks to continue it. Otherwise
   call `content_editor.create` once with `main_keyword`, location/device, the full initial setup,
   and `import_content_url` for a live page. For pasted text, omit the import URL and load the body
   after initialization. Reuse the same logical idempotency key if creation must retry.

2. **Wait and verify the setup.** Await initialization or poll `content_editor.get` to ready. Read
   `content_editor.get`; if competitor review was requested, read
   `seo_guidelines.get_competitors`. Report the effective brand toggle, template/voice,
   instructions, and competitors. Apply changes only after user approval with
   `content_editor.update` or `seo_guidelines.update_competitors`, then re-read the affected
   guidelines.

3. **Load content and establish the baseline.** For a pasted draft, call
   `content_editor.update_content`, then re-fetch with `content_editor.get_content`. Read
   `content_editor.get` for the unified Content Score; read `seo_guidelines.get_score` and/or
   `ai_search.get_score` for every selected dimension. Wait until each selected score is `ready`.
   Record each score's `calculated_at` before the next mutation.

4. **Read only the guidance needed.** For SEO, use `seo_guidelines.get_terms`,
   `seo_guidelines.get_structure`, and `seo_guidelines.get_topics_and_questions`. For AI Search,
   use `ai_search.get_facts`; retain every fact's source URL and `cited_by` context. Use
   `seo_guidelines.get` or `ai_search.get` only when the unified payload is actually needed.

5. **Choose an optimization path.** Ask when the user has no preference:
   - **Auto-optimize:** run `auto_optimize.run`; it changes the editor directly. Poll
     `auto_optimize.get` by job id (or `auto_optimize.get_latest` only when the job id is lost).
     Treat `optimized` and `nothing_to_optimize` as completed results; stop on quota, failed, or
     cancelled states.
   - **Guided edit:** revise the draft against the selected guidelines without keyword stuffing or
     unsupported claims, then use `content_editor.update_content`. Preserve source attribution for
     AI Search facts and re-fetch the canonical stored body because Surfer sanitizes it.

6. **Recalculate and compare.** After either path, re-read the stored content and all selected
   scores. After a direct content update, trust a score only once it is `ready` and its
   `calculated_at` advanced past the pre-mutation value; `calculating` may carry the stale score.
   If AI Search is unavailable, report why and do not claim the combined target was reached.

7. **Iterate with a stopping rule.** Address the largest remaining SEO or AI Search gap, then
   repeat steps 4–6. Stop when every selected target is met, auto-optimize reports
   `nothing_to_optimize`, the last useful gain is under about one point, or after 3–4 rounds.
   Report baseline-to-final SEO, AI Search, and unified Content Score separately.

8. **Use an audit only for broader page signals.** When requested, run `audit.create` and await
   `audit.get`; it supplements the Content Editor loop and does not replace content scoring.
