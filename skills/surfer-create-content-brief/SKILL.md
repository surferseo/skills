---
name: surfer-create-content-brief
description: >-
  Use when the user wants a writer-ready content brief grounded in Surfer's SEO and AI Search
  guidance — e.g. "make a content brief", "brief a writer for this keyword", "what should an
  article cover", or "give me an SEO and AI Search brief". Creates or reuses a manual Content
  Editor, assembles its outline, SEO guidelines, and source-attributed AI Search facts into a
  concise brief. For research-only SERP analysis use surfer-serp-research; for an outline alone
  use surfer-create-outline; for an article draft use surfer-write-article.
---

# Surfer: Create a Content Brief

## Overview

Turn a keyword into an evidence-aware writing specification. The output is a brief for a human or
agent writer, not a generic article and not a claim that an empty editor already has a good score.

## Inputs and setup

- Require `main_keyword`; ask for it when missing. Resolve the workspace and validate location
  and device as in `surfer-create-outline`.
- Reuse an existing `content_editor_id` when it matches the intended keyword and scope; otherwise
  create one in manual-writing mode with one logical idempotency key.
- Collect brand knowledge, content type/template, voice, custom instructions, and competitor
  choices before creation whenever they must shape the initial outline. Use the setup mapping in
  `surfer-capabilities`' `content-workflows.md`.
- Resolve the active transport under `surfer-capabilities`; stop at an unsupported capability
  rather than inventing a route or response shape.

## Playbook

1. **Initialize the Content Editor.** Call `content_editor.create` with the complete initial
   setup when no suitable editor exists. Await initialization through its completion event or a
   bounded `content_editor.get` poll. On failure or timeout, report the editor id and stop.

2. **Inspect the effective setup.** Read `content_editor.get`; read
   `seo_guidelines.get_competitors` only when competitor selection matters. State the effective
   brand toggle, template/voice, instructions, and competitor set. Change a setting only with an
   explicit user request, using `content_editor.update` or
   `seo_guidelines.update_competitors`.

3. **Collect the brief inputs.** Fetch the smallest useful components rather than the full
   guidelines payload:
   - `outline.get` in Markdown;
   - `seo_guidelines.get_structure`, `seo_guidelines.get_terms`, and
     `seo_guidelines.get_topics_and_questions`;
   - `ai_search.get_facts`, and `ai_search.get_score` only to report whether the analysis is
     ready, not to grade an empty draft.

   If the outline is pending, wait; if it failed, call `outline.regenerate` only as a retry for
   that failure. Follow the successful-outline limitation in `surfer-create-outline` when a
   post-creation setup change would need a fresh outline.

4. **Write the brief, not a data dump.** Organize it into:
   - search intent, primary keyword, location/device, and audience/brand constraints;
   - a proposed title and the Surfer-derived outline;
   - word-count and structural targets, with target ranges rather than hard quotas;
   - priority terms, distinguishing heading terms from body coverage;
   - required subtopics and questions;
   - AI Search facts as candidate claims, each retaining its source URL and `cited_by` context;
   - explicit constraints, unresolved questions, and the Content Editor link/id.

5. **Preserve evidence boundaries.** Do not call an AI Search fact true merely because it was
   suggested or cited by an engine. Attribute it, ask the writer to verify material claims, and
   call out unavailable or incomplete AI Search analysis instead of fabricating facts.

6. **Hand off deliberately.** Stop after the brief unless the user also asks for drafting. Pass
   the accepted outline and brief to `surfer-write-article`; do not automatically start
   `ai_article.generate`.
