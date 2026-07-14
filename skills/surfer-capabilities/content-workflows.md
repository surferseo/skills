# Content-workflow capability catalog

Use this reference with `surfer-capabilities` for workflows derived from the MCP Skills 2 sketch.
It gives their semantic vocabulary and explicitly distinguishes capabilities a current adapter can
run from registered extensions that need a future app/MCP adapter.

## Adapter support and normalized outcomes

Before invoking an ID, make the active adapter resolve it as **supported**, **unsupported**, or
**not connected**. Unsupported means stop at that boundary; never fabricate a raw API call,
browser flow, or result shape.

Normalize native task states to one of these outcomes when an adapter exposes an asynchronous
operation:

| Normalized outcome | Meaning |
|---|---|
| `pending` / `running` | Accepted but not terminal; retain the operation and resource ids. |
| `awaiting_input` | Blocked on an explicit user choice, such as an AI-article outline review. |
| `succeeded` | Completed and the expected resource/result is available. |
| `failed` / `cancelled` | Terminal unsuccessful result; report the adapter's reason. |
| `indeterminate` | Poll/webhook window expired without a verified terminal result. |

An adapter implementing an extension must return a stable resource or operation id, support the
outcomes above, and declare its own wait mechanism before a workflow may rely on it.

## Content Editor setup vocabulary

Collect setup decisions before `content_editor.create` whenever they must affect initial analysis.
Create consumes a Content Editor credit, so generate one logical idempotency key and reuse it on a
retry. Use `content_editor.get` after initialization to report the effective setup; mutate only
with a user-approved `content_editor.update` or guideline update.

| Sketch term | Canonical meaning | Current REST binding |
|---|---|---|
| Brand knowledge | Whether the workspace's current brand profile is applied to this editor. | `use_brand_knowledge` on `content_editor.create` / `content_editor.update`. REST can report the toggle but cannot inspect or edit the profile. |
| Content type | Reusable structural preference, not an arbitrary enum. | Choose one `custom_template_id` or `surfer_template`; neither means SERP-based structure. |
| Custom instructions | Per-editor editorial or factual direction. | `custom_instructions` on `content_editor.create` / `content_editor.update`. |
| Competitor selection | Included SERP pages that calculate SEO terms and structure. | `seo_guidelines.get_competitors` / `seo_guidelines.update_competitors` after initialization. |
| Manual versus AI writing | A workflow choice, not a Content Editor field. | Manual: do not call `ai_article.generate`. AI: call it after the editor is ready. |

The default outline is generated during Content Editor creation. In the REST adapter,
`outline.regenerate` retries a **failed** outline only; it is not a general refresh after setup
changes. Use `outline.generate` below when an adapter supports a fresh generated outline.

## Current composable capabilities

The sketch's currently possible steps are already composed from these IDs; a "score snapshot" is
three reads, not a fictional monolithic endpoint.

| User need | Capability IDs |
|---|---|
| Create/import and inspect content | `content_editor.create`, `content_editor.get`, `content_editor.get_content`, `content_editor.update`, `content_editor.update_content` |
| Read all scores | `content_editor.get` for unified `content_score`; `seo_guidelines.get_score`; `ai_search.get_score` |
| Optimize automatically or with guidance | `auto_optimize.run`, `auto_optimize.get`; `seo_guidelines.get_terms`, `seo_guidelines.get_structure`, `seo_guidelines.get_topics_and_questions`; `ai_search.get_facts` |
| Write with AI | `ai_article.generate`, `ai_article.get`, `ai_article.get_outline`, `ai_article.submit_outline` |
| Build an outline or brief | `outline.get`, `outline.regenerate`; the SEO and AI Search reads above |
| Manage custom templates | `content_template.list`, `content_template.create`, `content_template.get`, `content_template.update`, `content_template.delete`, `surfer_content_template.list` |

Trust a new score only after its own readiness signal and a changed calculation timestamp; a
`calculating` response can still carry the old score. Treat a blank-editor score as analysis state,
not evidence that a future article is high quality.

## Registered extension capabilities

These IDs make the future half of the sketch addressable without falsely claiming current REST
support. `surfer-api` deliberately does not bind them.

| Capability ID | Semantic contract | Safety requirement |
|---|---|---|
| `workspace.create` | Create a branded workspace from name, site/GSC context, location/language, and members; return its active `workspace_id`. | Require the user to choose the organization/site context. |
| `brand_knowledge.get` | Return the single brand profile for a workspace and whether it is usable. | Read-only; do not infer its text from `use_brand_knowledge`. |
| `brand_knowledge.update` | Replace or patch the approved profile; return the effective version. | Show the material change before writing it. |
| `recommendation.list` | Return actionable site recommendations filtered by `optimize` or `write`, each with a stable id, rationale, priority, and URL/keyword context. | Read-only; do not silently select one. |
| `recommendation.execute` | Start the chosen recommendation and return its accepted action plus a `content_editor_id` when one was created. | Treat as credit-spending if it creates an editor; never create a duplicate editor. |
| `outline.generate` | Generate or rebuild an outline from the editor's current template, instructions, brand context, and selected competitors. | Expose an operation id and normalized terminal outcome. |
| `internal_link.suggest` | Return candidate internal links with source page, target, anchor, location, and rationale. | Require connected site/GSC context; make no content change. |
| `internal_link.apply` | Apply only selected link suggestions to a named Content Editor. | Present the exact changes and require approval immediately before applying. |
| `wordpress.list_destinations` | Return connected WordPress sites and writable post/page destinations. | Read-only; do not expose or inspect credentials. |
| `wordpress.publish` | Export a named editor's canonical content to a WordPress draft, existing item, or live item; return its URL and status. | Default to a new draft; require final explicit confirmation for a live publish or update to an existing published item. |

## Full-workflow routing

`surfer-content-recommendations` owns workspace/recommendation/internal-link/publish orchestration.
It hands a recommendation-created editor to `surfer-optimize-content` for `optimize` work and to
`surfer-write-article` for `write` work. Do not perform the sketch's duplicate Content Editor
creation in the Write path: a recommendation execution that returns an editor is the one to use.
