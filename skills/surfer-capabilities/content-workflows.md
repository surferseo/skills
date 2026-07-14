# Content-workflow setup reference

Shared setup vocabulary for the surfer-* content workflows; use it with `surfer-capabilities`. Per-ID
semantics come from the active transport (the MCP tool description, or `surfer-api`'s
`capability-map.md`). The extension capabilities for the full workspace-to-publish loop live in
`surfer-content-recommendations`. If the active transport does not support an ID, stop at that
boundary rather than fabricating a call.

## Content Editor setup vocabulary

Collect setup decisions before `content_editor__create` whenever they affect the initial analysis. A
create consumes a Content Editor credit, so generate one logical idempotency key and reuse it on a
retry. After initialization, read the effective setup with `content_editor__get`. Change it only with
a user-approved `content_editor__update` or guideline update.

| Sketch term | Canonical meaning | Capability mapping |
|---|---|---|
| Brand knowledge | Whether the workspace's current brand profile is applied to this editor. | `use_brand_knowledge` on `content_editor__create` and `content_editor__update`. A transport can set the toggle but cannot inspect or edit the profile. |
| Content type | A reusable structural preference, set by a template choice. | Choose one `custom_template_id` or `surfer_template`. Neither means SERP-based structure. |
| Custom instructions | Per-editor editorial or factual direction. | `custom_instructions` on `content_editor__create` and `content_editor__update`. |
| Competitor selection | Included SERP pages that calculate SEO terms and structure. | Read the `competitors` block of `seo_guidelines__get`. Change it with `seo_guidelines__update_competitors` after initialization. |
| Manual versus AI writing | A workflow choice, decided by whether you call `ai_article__generate`. | For manual writing, do not call `ai_article__generate`. For AI writing, call it after the editor is ready. |

The default outline is generated during `content_editor__create`. `outline__regenerate` rebuilds the
outline from the SERP competitors and applies the editor's current template, custom instructions, and
brand knowledge. It returns a conflict when one is already in progress. Use it after a setup change or
a failed outline, not only to retry a failure.

## Current composable capabilities

The workflows' currently possible steps compose from these MCP tool IDs. The unified score is a single
read with `content_score__get`. The SEO brief is one read with `seo_guidelines__get` that already
covers every section.

| User need | Capability IDs |
|---|---|
| Create/import and inspect content | `content_editor__create`, `content_editor__get`, `content__get`, `content_editor__update`, `content__update` |
| Read all scores | `content_score__get`, one read returning `seo`, `ai_search`, and the unified `total`, each with `score` and `status` |
| Optimize automatically or with guidance | `auto_optimize__run`, `auto_optimize__get`; `seo_guidelines__get` for structure, terms, topics, questions, and competitors in one brief; `ai_search_guidelines__list_facts` |
| Write with AI | `ai_article__generate`, `ai_article__get`, `ai_article__get_outline`, `ai_article__submit_outline` |
| Build an outline or brief | `outline__get`, `outline__regenerate`; the `seo_guidelines__get` and `ai_search_guidelines__*` reads above |
| Manage custom templates and voices | `content_template__list`, `content_template__create`, `content_template__get`, `content_template__update`, `content_template__delete`, `surfer_content_template__list`; `custom_voice__*` |

A blank-editor score reflects analysis state only. Do not read it as evidence that a future article
will score well. (The active transport owns the stale-score rule for reading a score mid-recalc.)
