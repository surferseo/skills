---
name: surfer-write-article
description: >-
  Use when the user wants Surfer to produce a brand-new article or blog post from a keyword or
  topic — e.g. "write an SEO article about X", "draft optimized content for this keyword",
  "generate a Surfer AI article". Not for improving content that already exists (use
  surfer-optimize-content) or SERP/keyword research without writing (use surfer-serp-research).
license: MIT
---

# Surfer: Write an SEO Article

## Overview
Turn a keyword or topic into a new, SEO-optimized draft. Use when the user wants Surfer to author fresh content; for improving existing content hand off to surfer-optimize-content.

## Prerequisites
- **Capabilities & transport.** Each step names a Surfer capability ID (e.g. `content_editor.create`); none names a transport. At the first execution step, resolve the *active Surfer transport* (an adapter actually usable this session — not just files in a checkout). Exactly one usable → use it; several with none pinned → the default; **none usable → stop and ask the user which Surfer transport to install or use, and never improvise raw HTTP or assume an endpoint.** Don't mistake a missing credential for a missing transport. The active adapter owns auth, conventions, async waits, errors, idempotency, and pre-call doc/schema lookup; resolution rules and async/poll semantics live in `surfer-capabilities`.
- An `active` `workspace_id` (`workspace.list` if unknown).
- Inputs: `main_keyword` (required) plus up to 19 secondary keywords; `location` (default United States; validate via `locations.list`) and device (mobile default, or desktop). Optional: `target_word_count`, target SEO score, `manual_outline`, custom voice, template. If the user names no voice/template, pass none (Surfer uses the workspace-default voice and SERP-preselected template); call `custom_voice.list` / `content_template.list` / `surfer_content_template.list` only to resolve a specifically requested one.

## Playbook

1. **Create the Content Editor** with `content_editor.create` (keywords, location/device, optional word count/voice/template/instructions). Returns `state: scheduled`.

2. **Wait for initialization.** Poll `content_editor.get` (or await `content_editor.initialization.completed`) until `state: completed`; treat any non-`completed`/`failed` state as in-progress, bail on `failed` or a sane timeout. Reads below need a `completed` editor.

3. **Read the SEO guidelines** — fetch only what you need: `seo_guidelines.get_terms` (terms + which belong in headings), `seo_guidelines.get_structure` (word/heading/paragraph/image targets), `seo_guidelines.get_topics_and_questions`, or `seo_guidelines.get` for all. Optionally refine via `seo_guidelines.update_terms` / `update_structure` / `update_topics_and_questions`.

4. **(Optional) Review the SERP outline.** `outline.get` returns the read-only, SERP-derived outline. Only when `outline.status` (on `content_editor.get`) is `failed`, call `outline.regenerate` and await `content_editor.outline.completed`; if status is `scheduled` a job is already queued (re-calling returns conflict) — just wait. Informational; the AI article builds its own outline.

5. **Generate the AI article** with `ai_article.generate`; it inherits the editor's template, voice, instructions, and word count. Pass `manual_outline: true` to approve/edit the outline first. States: `new → generating_outline → [waiting_for_user_input only if manual_outline] → writing → completed/failed`. If an article already exists, the error detail should carry `active_article_id` (the example body shows empty `details`, so fall back to `ai_article.list`); `ai_article.get` it and rejoin by state — generating/writing → step 7, `waiting_for_user_input` → step 6, `completed` → step 8, `failed` → report.

6. **Handle the manual-outline pause** (only with `manual_outline: true`). At `waiting_for_user_input` (`ai_article.get`), the body is not written yet. Fetch the proposal with `ai_article.get_outline`, surface it, then resume via `ai_article.submit_outline` (submit the proposal as-is or edited). Generation stays paused until you submit — a required decision, not a hang. Running unattended, either skip `manual_outline` or submit the proposal unchanged after a timeout.

7. **Await completion.** Await `content_editor.ai_article.completed` (else poll `ai_article.get`). On `content_editor.ai_article.failed`, report it.

8. **Read the result.** Fetch the draft with `content_editor.get_content` (request Markdown if wanted). Read the SEO score (0–100) via `seo_guidelines.get_score`; poll until `status: ready` (`calculating` means the value is stale) before reporting, and read the unified `content_score` via `content_editor.get`.

9. **Iterate toward the target (SEO score).** Iterate only if the user gave a target; otherwise read-and-report. While the SEO score is below target: diff the draft against `get_terms` / `get_structure` / `get_topics_and_questions`, edit, and write back with `content_editor.update_content` (it sanitizes server-side — re-fetch `content_editor.get_content`). It triggers recalculation: await `content_editor.seo_score.calculated` or poll `seo_guidelines.get_score` until `status: ready` and `calculated_at` advances, then re-read. Cap at 3–5 rounds and stop on no gain between two recalculations. Report `content_score`; don't iterate on it. For hands-off lifting use surfer-optimize-content; for LLM visibility use surfer-ai-search.

10. **Deliver** the final content, the SEO and unified scores, and a share/edit link: prefer the `permalinks` field on `content_editor.get`; if empty, `permalink.list`, then `permalink.reset` to mint one.

## Gotchas
- `ai_article.generate` may run before initialization finishes: the article waits in `new` until guidelines settle, then proceeds (or `failed` if they never complete).
- `content_editor.update_content` recalculates both scores; `content_editor.content_score.recalculated` fires only after SEO and AI Search both settle.
