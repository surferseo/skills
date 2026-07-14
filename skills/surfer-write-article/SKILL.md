---
name: surfer-write-article
description: >-
  Use when the user wants Surfer to produce a brand-new article or blog post from a keyword or
  topic — e.g. "write an SEO article about X", "draft optimized content for this keyword",
  "generate a Surfer AI article", or "write for SEO and AI Search". Not for improving content
  that already exists (use surfer-optimize-content), a writer brief (use
  surfer-create-content-brief), or SERP research without drafting (use surfer-serp-research).
license: MIT
---

# Surfer: Write an Optimized Article

## Overview

Turn a keyword into a new, AI-authored draft grounded in Surfer's SEO and AI Search analysis.
Create a manual Content Editor and stop before `ai_article.generate` when the user wants only an
outline or brief.

## Prerequisites

- Resolve the active transport under `surfer-capabilities`; it owns auth, call mechanics, and
  async handling. If a required capability is unsupported, name it and stop.
- Resolve one active `workspace_id` with `workspace.list`.
- Require `main_keyword`; accept up to 19 secondary keywords. Default location to United States
  and device to mobile after validating location with `locations.list`.
- Collect optional `target_word_count`, SEO and/or AI Search score targets, `manual_outline`, and
  full editor setup before creation. For the sketch's brand knowledge, content type, instructions,
  and competitors, use `surfer-capabilities`' `content-workflows.md`.
- Treat "AI writing mode" as `ai_article.generate`, not a `content_editor.create` field. Leave it
  out for manual work.

## Playbook

1. **Create the fully configured Content Editor.** Call `content_editor.create` once with keyword,
   locale/device, selected brand toggle, template or voice, and custom instructions. Reuse the
   logical idempotency key on retry. If neither template is selected, retain Surfer's asynchronously
   chosen template rather than inventing a content type.

2. **Wait for initialization.** Await `content_editor.initialization.completed` or poll
   `content_editor.get` until ready. Report a failure or bounded timeout with the editor id.

3. **Review the content plan before drafting.** Read only the necessary SEO guidance:
   `seo_guidelines.get_terms`, `seo_guidelines.get_structure`, and
   `seo_guidelines.get_topics_and_questions`; read `ai_search.get_facts` when AI Search is a goal.
   Read `content_editor.get` to verify the brand toggle, template/voice, and instructions. If the
   user asks to change competitors, inspect `seo_guidelines.get_competitors`, apply an approved
   `seo_guidelines.update_competitors`, then re-read affected guidelines before generating.

4. **Choose outline behavior.** `outline.get` supplies the read-only SERP outline. Only retry it
   with `outline.regenerate` after an actual outline failure. For a reviewable AI outline, set
   `manual_outline: true` when calling `ai_article.generate`; that is separate from the SERP
   outline and pauses before prose is written.

5. **Generate the AI article.** Call `ai_article.generate`. If an article already exists, use
   `ai_article.list` and `ai_article.get` to rejoin it rather than creating another. Handle states:
   `waiting_for_user_input` means fetch `ai_article.get_outline`, present it, and submit only the
   user-approved version via `ai_article.submit_outline`; generating/writing means wait; failed
   means report and stop.

6. **Read the canonical draft and score snapshot.** Await `content_editor.ai_article.completed` or
   poll `ai_article.get`. Fetch `content_editor.get_content`, then read `content_editor.get` for
   unified Content Score plus `seo_guidelines.get_score` and `ai_search.get_score`. Trust an
   individual score only when it is ready; call out an unavailable AI Search score rather than
   treating it as a pass.

7. **Iterate only toward user-selected targets.** If a target is set and not met, use the relevant
   SEO guidance and/or sourced AI Search facts to improve the draft, write it with
   `content_editor.update_content`, re-fetch the sanitized stored version, and wait for the
   selected score timestamps to advance. Stop after 3–5 rounds or after a plateau; do not chase a
   unified Content Score target.

8. **Deliver and hand off.** Return the canonical content, separate SEO/AI Search/unified scores,
   the Content Editor id, and an edit/share link from `permalinks`, `permalink.list`, or
   `permalink.reset`. For a recommendation-led workflow, return control to
   `surfer-content-recommendations`; for publishing, require its WordPress-capable adapter stage.
