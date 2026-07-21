---
name: surfer-write-article
description: >-
  Use when the user wants Surfer to produce a brand-new article or blog post from a keyword or topic.
  Triggers include "write an SEO article about X", "draft optimized content for this keyword",
  "generate a Surfer AI article", and "write for SEO and AI Search". To improve content that already
  exists, use surfer-optimize-content. For a writer brief without a draft, use
  surfer-create-content-brief.
license: MIT
---

# Surfer: Write an Optimized Article

## Overview

Turn a keyword into a new, AI-authored draft grounded in Surfer's SEO and AI Search analysis. When
the user wants only an outline or a brief, create a manual Content Editor and stop before
`ai_article__generate`.

## Prerequisites

- Resolve the transport: with the Surfer MCP server connected, call its tools directly; otherwise
  run over REST with `surfer-api`; with neither, connect one via `surfer-connect` rather than
  improvising raw HTTP. The active transport owns auth, call mechanics, and async handling. If a
  required capability is unsupported, name it and stop.
- Resolve one active `workspace_id` with `workspace__list`.
- Require `main_keyword` and accept up to 19 secondary keywords. Default the location to United
  States and the device to mobile. Location and device are inputs to `content_editor__create`.
- Before creation, collect the optional `target_word_count`, any SEO or AI Search score targets,
  `manual_outline`, and the full editor setup: the `use_brand_knowledge` toggle (it applies the
  workspace's brand profile, which cannot be inspected or edited from here), one
  `custom_template_id` or `surfer_template` as the content type (mutually exclusive; omitting both
  lets Surfer preselect a template during analysis, so a no-template request cannot be guaranteed),
  and `custom_instructions`. Omitting `custom_voice_id` applies the workspace default voice; send
  `custom_voice_id: null` to honor a no-voice request. Competitors are read from the
  `competitors` block of `seo_guidelines__get` and changed with `seo_guidelines__update_competitors`
  after initialization.
- Treat "AI writing mode" as the `ai_article__generate` call rather than a `content_editor__create`
  field. Leave it out for manual work.

## Playbook

1. **Create the fully configured Content Editor.** Call `content_editor__create` once with the
   keyword, locale, device, the selected brand toggle, a template or voice, and custom instructions.
   Do not blindly retry a create; after a timeout or ambiguous failure, list recent editors with
   `content_editor__list` (sort `inserted_at` desc) and reuse one matching the keyword instead of
   creating again. If no template is selected, keep the template Surfer chooses during analysis
   rather than inventing a content type.

2. **Wait for initialization.** Await the completion signal or poll `content_editor__get` until
   `state` is `completed`. Report a failure or a bounded timeout with the editor id.

3. **Review the content plan before drafting.** Read `seo_guidelines__get`, one brief with the terms,
   structure targets, topics, questions, and competitors. Read `ai_search_guidelines__list_facts`
   when AI Search is a goal. Read `content_editor__get` to verify the brand toggle, template or
   voice, and instructions. If the user asks to change competitors, inspect the `competitors` block
   of `seo_guidelines__get`, apply an approved `seo_guidelines__update_competitors`, then re-read the
   affected guidelines before generating.

4. **Choose outline behavior.** `outline__get` returns the read-only SERP outline.
   `outline__regenerate` rebuilds it from the SERP competitors with the editor's template,
   instructions, and brand knowledge. Use it after a setup change or a failed outline. For a
   reviewable AI outline, set `manual_outline: true` when calling `ai_article__generate`. That
   outline is separate from the SERP outline and pauses before prose is written.

5. **Generate the AI article.** Call `ai_article__generate`. If an article already exists, rejoin it
   with `ai_article__list` and `ai_article__get` rather than creating another. Handle the states as
   follows. On `waiting_for_user_input`, fetch `ai_article__get_outline`, present it, and submit only
   the user-approved version with `ai_article__submit_outline`. While it is generating or writing,
   wait. On `failed`, report and stop.

6. **Read the canonical draft and score snapshot.** Await the completion signal or poll
   `ai_article__get` until `completed`. Fetch `content__get`, then read `content_score__get` for the
   unified `total` plus the `seo` and `ai_search` subscores. Trust an individual score only when its
   `status` is `ready`; a `loading` or `calculating` status is still settling. Call out an `error` or
   `unavailable` AI Search score as terminal rather than treating it as a pass or polling for `ready`.

7. **Iterate only toward user-selected targets.** If a target is set and unmet, improve the draft
   with the relevant SEO guidance and the sourced AI Search facts, write it with `content__update`,
   re-fetch the sanitized stored version with `content__get`, and wait for the selected score
   timestamps to advance. Stop after 3 to 5 rounds or after a plateau. Do not chase a unified Content
   Score target.

8. **Deliver and hand off.** Return the canonical content, the SEO, AI Search, and unified scores
   separately, the Content Editor id, and an edit or share link from `permalink__list`.
