# Content-workflow capability catalog

Use this reference with `surfer-capabilities` for the workflows in the MCP Skills 2 sketch. It gives
their setup vocabulary. It also separates the capabilities on the MCP tool surface, which a transport
runs today, from the registered extensions that need a fuller transport.

## Transport support and normalized outcomes

Before invoking an ID, have the active transport resolve it as supported, unsupported, or not
connected. Unsupported means stop at that boundary. Never fabricate a raw API call, a browser flow,
or a result shape.

When a transport exposes an asynchronous operation, normalize its native task state to one of these
outcomes:

| Normalized outcome | Meaning |
|---|---|
| `pending` / `running` | Accepted but not terminal. Retain the operation and resource ids. |
| `awaiting_input` | Blocked on an explicit user choice, such as an AI-article outline review. |
| `succeeded` | Completed, and the expected resource or result is available. |
| `failed` / `cancelled` | Terminal and unsuccessful. Report the transport's reason. |
| `indeterminate` | The poll or webhook window closed without a verified terminal result. |

A transport that implements an extension must return a stable resource or operation id, support the
outcomes above, and declare its wait mechanism before a workflow relies on it.

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
brand knowledge. It returns a conflict when one is already in progress. Use it after a setup change
or a failed outline, not only to retry a failure.

## Current composable capabilities

The sketch's currently possible steps compose from these MCP tool IDs. The unified score is a single
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

Trust a new score only after its readiness signal and a changed calculation timestamp. A
`calculating` response can still carry the old score. A blank-editor score reflects analysis state
only. Do not read it as evidence that a future article will score well.

## Registered extension capabilities

These IDs make the future half of the sketch addressable. No transport binds them yet.

| Capability ID | Semantic contract | Safety requirement |
|---|---|---|
| `workspace__create` | Create a branded workspace from a name, site or GSC context, location, language, and members. Return its active `workspace_id`. | Require the user to choose the organization and site context. |
| `brand_knowledge__get` | Return the single brand profile for a workspace and whether it is usable. | Read-only. Do not infer its text from `use_brand_knowledge`. |
| `brand_knowledge__update` | Replace or patch the approved profile. Return the effective version. | Show the material change before writing it. |
| `recommendation__list` | Return actionable site recommendations filtered by `optimize` or `write`, each with a stable id, rationale, priority, and URL or keyword context. | Read-only. Do not silently select one. |
| `recommendation__execute` | Start the chosen recommendation. Return its accepted action, plus a `content_editor_id` when one was created. | Treat it as credit-spending if it creates an editor. Never create a duplicate editor. |
| `internal_link__suggest` | Return candidate internal links with source page, target, anchor, location, and rationale. | Require connected site or GSC context. Make no content change. |
| `internal_link__apply` | Apply only selected link suggestions to a named Content Editor. | Present the exact changes and require approval immediately before applying. |
| `wordpress__list_destinations` | Return connected WordPress sites and writable post or page destinations. | Read-only. Do not expose or inspect credentials. |
| `wordpress__publish` | Export a named editor's canonical content to a WordPress draft, an existing item, or a live item. Return its URL and status. | Default to a new draft. Require final explicit confirmation before a live publish or before updating an existing published item. |

## Full-workflow routing

`surfer-content-recommendations` orchestrates the workspace, recommendation, internal-link, and
publish steps. It hands a recommendation-created editor to `surfer-optimize-content` for optimize
work and to `surfer-write-article` for write work. In the write path, do not create a second Content
Editor. When a recommendation execution returns an editor, use that one.
