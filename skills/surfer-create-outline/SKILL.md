---
name: surfer-create-outline
description: >-
  Use when the user wants a Surfer-derived, SERP-informed article outline without a full draft —
  e.g. "create an outline for X", "plan headings for this keyword", "make a Surfer outline", or
  "outline an article before writing". Creates or reuses a Content Editor in manual-writing mode,
  returns its SEO-oriented outline, and can verify the requested brand, template, instructions,
  and competitor choices. For a writer-ready plan that also includes AI Search facts, use
  surfer-create-content-brief; for a complete AI-written draft, use surfer-write-article.
---

# Surfer: Create an Optimized Outline

## Overview

Produce the structural plan for a new article, not the article itself. The current REST outline is
SERP-derived; use the content-brief workflow to add AI Search facts to the writer's plan. A manual
Content Editor is the source of truth: do not invoke `ai_article.generate` unless the user changes
the request to a draft.

## Inputs

- Require `main_keyword`. Ask for it if it is missing.
- Use the user's `location` and `device`; otherwise default to United States and mobile after
  validating the location with `locations.list`.
- Accept a `workspace_id` or resolve one via `workspace.list`.
- Accept an existing `content_editor_id` to avoid spending another Content Editor credit.
- Treat brand knowledge, content type, custom instructions, template, voice, and competitor
  selection as setup choices. Follow the mapping and ordering rules in
  `surfer-capabilities`' `content-workflows.md`.

Resolve the active transport under `surfer-capabilities` before the first call. If it cannot run a
required capability, name that capability and stop; do not replace it with raw HTTP or a guessed
UI flow.

## Playbook

1. **Create or reuse the editor.** Reuse the supplied `content_editor_id` after confirming it
   targets the requested keyword and workspace. Otherwise call `content_editor.create` once with
   the complete initial setup: keyword, location/device, `use_brand_knowledge`, any selected
   template or voice, and `custom_instructions`. Reuse its logical idempotency key on a retry;
   creation consumes a credit.

2. **Wait for analysis.** Await `content_editor.initialization.completed` or poll
   `content_editor.get` until the editor is ready. On the matching failure event or a bounded
   timeout, report the editor id and terminal/indeterminate state instead of retrying forever.

3. **Verify setup without silently changing it.** Read `content_editor.get`; for a requested
   competitor review, read `seo_guidelines.get_competitors`. Report the effective brand toggle,
   template/voice, instructions, and included competitors. Apply a change only when the user
   requested it: use `content_editor.update` for editor settings and
   `seo_guidelines.update_competitors` for an explicit competitor selection.

4. **Retrieve the outline.** Request `outline.get` in Markdown. If it is still pending, wait on
   the editor's `outline.status`. If it failed, use `outline.regenerate` only as the documented
   retry for a failed outline, then wait again and re-read it. Do not call regeneration simply to
   refresh a successful outline.

5. **Handle the configuration boundary honestly.** The REST adapter generates the default outline
   during editor creation. It cannot regenerate a successful outline after a later template,
   instruction, or competitor change. Either keep the original setup, create a replacement editor
   with the new setup after the user accepts the additional credit, or use an adapter that supports
   the extension capability `outline.generate`.

6. **Deliver a usable plan.** Return the Markdown outline, Content Editor id, edit/share link if
   available, target keyword/location, and the setup choices that shaped it. Do not fill missing
   sections with generic headings; call out an empty or unavailable outline instead.

## Handoff

Use `surfer-create-content-brief` when the writer also needs terms, structural targets, questions,
and AI Search facts. Use `surfer-write-article` only after the outline has been accepted or when
the user explicitly asks for a draft.
