---
name: surfer-optimize-content
description: >-
  Use when the user has existing content, a URL or a draft, and wants to improve its Surfer SEO
  Score, AI Search Score, or both. Triggers include "optimize my article", "improve this page's
  content score", "auto-optimize this", "make this rank better", "optimize for SEO and AI search",
  and "improve my AI or LLM visibility". For writing a new article from scratch, use
  surfer-write-article instead.
license: MIT
---

# Surfer: Optimize Existing Content

## Overview

Raise the Surfer score dimensions the user selected for a page or draft, working through a Content
Editor. Treat the unified Content Score as a diagnostic snapshot. Optimize against the explicit SEO
or AI Search targets the user cares about.

## Prerequisites

- Resolve the transport: with the Surfer MCP server connected, call its tools directly; otherwise
  run over REST with `surfer-api`; with neither, connect one via `surfer-connect`. If no transport
  can run a required capability, name it and stop. Do not improvise raw HTTP or assume an endpoint.
- Resolve an active `workspace_id` with `workspace__list`.
- Require a target keyword and either an import URL or raw HTML or Markdown. Ask for a missing
  keyword rather than guessing it from the page alone.
- Ask which dimensions matter: SEO, AI Search, or both. If the user says only "optimize", default to
  SEO 70+. If they ask for both and give no targets, default to 70+ for each and say so. A missing
  AI Search score does not mean zero.
- Treat brand knowledge, content type or template, custom instructions, and competitor selection as
  Content Editor setup, collected before the create: the brand profile is applied through the
  `use_brand_knowledge` toggle and cannot be inspected or edited from here, the content type is one
  `custom_template_id` or `surfer_template` (mutually exclusive), instructions go in
  `custom_instructions`, and competitors are read and changed through `seo_guidelines__get` and
  `seo_guidelines__update_competitors`.

Use bounded waits only. On an explicit failure, an unavailable score, or a timeout, report the id
and state. Never poll indefinitely.

## Playbook

1. **Create or reuse a Content Editor.** Reuse a matching editor through `content_editor__list` when
   the user supplies one or asks to continue it. Omit `workspace_id` on that list call for an
   org-wide search. Otherwise call `content_editor__create` once with `main_keyword`, location,
   device, the full initial setup, and `import_content_url` for a live page. For pasted text, omit
   the import URL and load the body after initialization. Do not blindly retry a create; after a
   timeout or ambiguous failure, list recent editors with `content_editor__list` (sort
   `inserted_at` desc) and reuse one matching the keyword instead of creating again.

2. **Wait and verify the setup.** Await the completion signal or poll `content_editor__get` until
   ready. Read `content_editor__get`. If the user asked to review competitors, read the
   `competitors` block of `seo_guidelines__get`. Report the effective brand toggle, template or
   voice, instructions, and competitors. Apply changes only after user approval, with
   `content_editor__update` or `seo_guidelines__update_competitors`, then re-read the affected
   guidelines.

3. **Load content and establish the baseline.** For a pasted draft, call `content__update`, then
   re-fetch with `content__get`. Read `content_score__get` for the unified `total` plus the `seo`
   and `ai_search` subscores. Wait through `loading` or `calculating` until each selected subscore's
   `status` is `ready`, but treat `ai_search` `error` and `unavailable` as terminal: report them and
   stop waiting. Record the `seo` and `ai_search` `calculated_at` before the next mutation; the
   `total` carries none.

4. **Read only the guidance needed.** For SEO, read `seo_guidelines__get`, one brief that carries the
   structure targets, terms, topics, questions, and competitors. For AI Search, use
   `ai_search_guidelines__list_facts`, or `ai_search_guidelines__get` for the facts plus the score.
   Retain every fact's source URL and `cited_by` context.

5. **Choose an optimization path**, and ask when the user has no preference.
   - Auto-optimize runs `auto_optimize__run`, which changes the editor directly. Poll
     `auto_optimize__get` by job id. Treat `optimized` and `nothing_to_optimize` as completed
     results. Stop on a quota, failed, or cancelled state.
   - A guided edit revises the draft against the selected guidelines, without keyword stuffing or
     unsupported claims, then calls `content__update`. Preserve source attribution for AI Search
     facts, and re-fetch the canonical stored body with `content__get` because Surfer sanitizes it.

6. **Recalculate and compare.** After either path, re-read the stored content and all selected scores
   with `content_score__get`. After a direct content update, trust a subscore only once its `status`
   is `ready` and its `calculated_at` has advanced past the pre-mutation value; the `total` has no
   `calculated_at`, so gate it on `status` alone. A `loading` or `calculating` status may carry the
   stale score. If AI Search reports `error` or `unavailable`, report why and do not claim the
   combined target was reached.

7. **Iterate with a stopping rule.** Address the largest remaining SEO or AI Search gap, then repeat
   steps 4 to 6. Stop when every selected target is met, when auto-optimize reports
   `nothing_to_optimize`, when the last useful gain is under about one point, or after 3 to 4 rounds.
   Report the baseline and final values for the SEO, AI Search, and unified Content Score separately.
