# Surfer API capability map

The REST binding for every capability ID, plus the REST async and poll semantics. Capability IDs are
the Surfer MCP server's tool names. surfer-api is the secondary transport. The Surfer MCP server is
primary, and when it is connected each tool carries its own description of async behavior, poll
targets, and status values. A REST caller has no such description in context, so this file supplies
it. The extension IDs owned by `surfer-content-recommendations` have no REST binding.

This file has two parts.

1. **Async operations & polling** lists which IDs are asynchronous and how a REST caller polls for
   terminal state. An MCP caller reads this from each tool's description. A REST caller cannot, so it
   lives here.
2. **The method and path map** gives each ID's HTTP verb, path, workspace scoping, and per-resource
   Live doc. Its columns are:
   - **Capability ID** is the tool-name ID with a REST binding.
   - **REST method+path** is the HTTP verb and path. Workspace-scoped paths are flagged.
   - **Workspace-scoped?** says whether the path sits under `/api/v2/workspaces/{workspace_id}/...`.
   - **Live-doc URL** is the per-resource doc to fetch before calling, per the SKILL.md standing
     rule: `https://app.surferseo.com/llms/<resource>.txt`.

All 37 contract capability IDs are bound below, all v2. The contract is grounded in the Surfer MCP
tool surface. The REST API also exposes endpoints outside that surface: audit, SERP analyzer, AI
detector, humanizer, locations, `_v1` variants, editor delete, and permalink reset. Those are not
contract capabilities and have no row. Report a request for one as out of contract rather than
binding a path. `server__info` is MCP-transport meta and has no REST binding.

## Async operations & polling

An async op returns non-terminal and finishes later. Poll the listed GET until it reaches a terminal
state. Back off between polls, starting near 1 to 5 seconds and capping near 10 to 60 seconds, and
stop at a hard cap. On reaching the cap, report the job as indeterminate. REST can also push
`content_editor.*` webhooks, described in SKILL.md, but polling is always available. Terminal
vocabulary differs by resource, so never assume `completed`.

| Capability ID | Poll-via | Poll field | Terminal value(s) |
|---|---|---|---|
| `content_editor__create` | `content_editor__get` | `state` | success `completed`; failure `failed` |
| `content__update` (triggers score recalc) | `content_score__get` | `status` (each subscore) | `ready` (each) |
| `auto_optimize__run` | `auto_optimize__get` | `state` (+`result`) | success `completed` (`result` = `optimized` / `nothing_to_optimize`); failure `failed` |
| `ai_article__generate` | `ai_article__get` | `state` | success `completed`; pause `waiting_for_user_input`; failure `failed` |
| `ai_article__submit_outline` (resumes) | `ai_article__get` | `state` | success `completed`; failure `failed` |
| `outline__regenerate` | `content_editor__get` | `outline.status` | terminal once it leaves `scheduled` or `executing`, then read `outline__get`; conflict if one is already running |
| `seo_guidelines__load_more_competitors` | `seo_guidelines__get` | `load_more_status` | `idle` |

Every other capability ID is a synchronous read or write. Four reads are status-gated:
`content_score__get`, `seo_guidelines__get`, `ai_search_guidelines__get`, and
`ai_search_guidelines__list_facts`. Each payload carries a lifecycle `status`. A score is
trustworthy only when its `status` is `ready` and its `calculated_at` has advanced past the value
captured before the mutation. A `calculating` response can still carry the stale prior score.

## Workspaces

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `workspace__list` | GET `/api/v2/workspaces` | No | https://app.surferseo.com/llms/workspaces.txt |

## Content Editors

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `content_editor__list` | GET `/api/v2/workspaces/{workspace_id}/content_editors` (omit `workspace_id` → org-wide `/api/v2/content_editors`) | Yes (or org-wide) | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor__create` | POST `/api/v2/workspaces/{workspace_id}/content_editors` | Yes | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor__get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{id}` | Yes | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor__update` | PATCH `/api/v2/workspaces/{workspace_id}/content_editors/{id}` | Yes | https://app.surferseo.com/llms/content-editors.txt |

## Content

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `content__get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/content` (Accept `text/markdown` or `text/html`) | Yes | https://app.surferseo.com/llms/content-editors.txt |
| `content__update` | PUT `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/content` (Content-Type `text/markdown` or `text/html`) | Yes | https://app.surferseo.com/llms/content-editors.txt |

## Content Score

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `content_score__get` | **Composite.** Read the unified `total` from GET `/api/v2/workspaces/{workspace_id}/content_editors/{id}` (`content_score.total`), the `seo` subscore from GET `.../content_editors/{content_editor_id}/seo_guidelines/score`, and the `ai_search` subscore from GET `.../content_editors/{content_editor_id}/ai_search_guidelines/score` | Yes | https://app.surferseo.com/llms/content-editors.txt |

## Auto-Optimize

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `auto_optimize__run` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/auto_optimize` | Yes | https://app.surferseo.com/llms/auto-optimize.txt |
| `auto_optimize__get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/auto_optimize/{job_id}` | Yes | https://app.surferseo.com/llms/auto-optimize.txt |

## AI Articles

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `ai_article__list` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_articles` | Yes | https://app.surferseo.com/llms/ai-articles.txt |
| `ai_article__generate` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_articles` | Yes | https://app.surferseo.com/llms/ai-articles.txt |
| `ai_article__get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_articles/{article_id}` | Yes | https://app.surferseo.com/llms/ai-articles.txt |
| `ai_article__get_outline` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_articles/outline` (Accept `text/markdown`) | Yes | https://app.surferseo.com/llms/ai-articles.txt |
| `ai_article__submit_outline` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_articles/outline` (Content-Type `text/markdown`) | Yes | https://app.surferseo.com/llms/ai-articles.txt |

## SEO Guidelines

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `seo_guidelines__get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines__update_structure` | PATCH `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/structure` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines__update_terms` | PATCH `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/terms` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines__update_topics_and_questions` | PATCH `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/topics_and_questions` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines__update_competitors` | PATCH `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/competitors` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines__load_more_competitors` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/competitors/load_more` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |

## AI Search Guidelines

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `ai_search_guidelines__get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_search_guidelines` | Yes | https://app.surferseo.com/llms/ai-search.txt |
| `ai_search_guidelines__list_facts` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_search_guidelines/facts` | Yes | https://app.surferseo.com/llms/ai-search.txt |

## Outline

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `outline__get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/outline` (Accept `text/markdown`) | Yes | https://app.surferseo.com/llms/outline.txt |
| `outline__regenerate` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/outline/regenerate` | Yes | https://app.surferseo.com/llms/outline.txt |

## Content Templates

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `content_template__list` | GET `/api/v2/workspaces/{workspace_id}/content_templates` | Yes | https://app.surferseo.com/llms/content-templates.txt |
| `content_template__create` | POST `/api/v2/workspaces/{workspace_id}/content_templates` | Yes | https://app.surferseo.com/llms/content-templates.txt |
| `content_template__get` | GET `/api/v2/workspaces/{workspace_id}/content_templates/{id}` | Yes | https://app.surferseo.com/llms/content-templates.txt |
| `content_template__update` | PATCH or PUT `/api/v2/workspaces/{workspace_id}/content_templates/{id}` | Yes | https://app.surferseo.com/llms/content-templates.txt |
| `content_template__delete` | DELETE `/api/v2/workspaces/{workspace_id}/content_templates/{id}` | Yes | https://app.surferseo.com/llms/content-templates.txt |

## Custom Voices

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `custom_voice__list` | GET `/api/v2/workspaces/{workspace_id}/custom_voices` | Yes | https://app.surferseo.com/llms/custom-voices.txt |
| `custom_voice__create` | POST `/api/v2/workspaces/{workspace_id}/custom_voices` | Yes | https://app.surferseo.com/llms/custom-voices.txt |
| `custom_voice__get` | GET `/api/v2/workspaces/{workspace_id}/custom_voices/{id}` | Yes | https://app.surferseo.com/llms/custom-voices.txt |
| `custom_voice__update` | PATCH or PUT `/api/v2/workspaces/{workspace_id}/custom_voices/{id}` | Yes | https://app.surferseo.com/llms/custom-voices.txt |
| `custom_voice__delete` | DELETE `/api/v2/workspaces/{workspace_id}/custom_voices/{id}` | Yes | https://app.surferseo.com/llms/custom-voices.txt |

## Surfer Content Templates

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `surfer_content_template__list` | GET `/api/v2/surfer_content_templates` | No | https://app.surferseo.com/llms/surfer-content-templates.txt |

## Permalinks

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `permalink__list` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/permalinks` | Yes | https://app.surferseo.com/llms/permalinks.txt |
