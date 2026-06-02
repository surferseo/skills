# Surfer API capability map

The canonical bridge the `surfer-*` workflow skills bind to. Workflow skills reference
**capability IDs**, never raw paths. Columns:

- **REST** — method + path. `{workspace_id}`-scoped paths are flagged under **WS**.
- **WS** — workspace-scoped (`/api/v2/workspaces/{workspace_id}/...`)? `Yes` / `No`.
- **Async event** — `content_editor.*` webhook events the op can emit; `—` if synchronous.
  When polling instead of using webhooks, use the **Poll via** target below.
- **Live doc** — per-resource doc to fetch before calling (see SKILL.md standing rule).

All 69 capability IDs are listed. Prefer v2; v1/`_v1` rows are legacy/deprecated, kept only
where no v2 equivalent exists.

### Poll-via targets (per async create/mutate op)

Read the named field on the GET capability; never assume the literal value `completed`.

| Async op | Poll via | Field | Terminal-success value |
|---|---|---|---|
| `content_editor.create` | `content_editor.get` | `state` | `completed` (no `failed` in body — see SKILL.md) |
| `content_editor.update_content` | `seo_guidelines.get_score` + `ai_search.get_score` | `status` | `ready` (each) |
| `ai_article.generate` | `ai_article.get` | `state` | `completed` (or `failed`) |
| `auto_optimize.run` | `auto_optimize.get` | `state` / `result` | `completed`; `result` = `optimized` / `nothing_to_optimize` |
| `seo_guidelines.get_score` (after content change) | `seo_guidelines.get_score` | `status` | `ready` |
| `ai_search.get_score` (after content change) | `ai_search.get_score` | `status` | `ready` |
| `outline.regenerate` | `content_editor.get` | `outline.status` | (poll until not `scheduled`/`executing`) |
| `seo_guidelines.load_more_competitors` | `seo_guidelines.get` | `load_more_status` | `idle` |

## Workspaces

| Capability ID | REST | WS | Async event | Live doc |
|---|---|---|---|---|
| `workspace.list` | GET `/api/v2/workspaces` | No | — | https://app.surferseo.com/llms/workspaces.txt |
| `workspace.list_v1` | GET `/api/v1/workspaces` (legacy) | No | — | https://app.surferseo.com/llms/other.txt |

## Content Editors

| Capability ID | REST | WS | Async event | Live doc |
|---|---|---|---|---|
| `content_editor.list_all` | GET `/api/v2/content_editors` (org-wide) | No | — | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.list` | GET `/api/v2/workspaces/{workspace_id}/content_editors` | Yes | — | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.create` | POST `/api/v2/workspaces/{workspace_id}/content_editors` | Yes | `content_editor.initialization.completed` / `.failed`; `content_editor.seo_score.calculated` / `.failed`; `content_editor.ai_search_score.calculated` / `.failed`; `content_editor.content_score.recalculated` | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{id}` | Yes | — | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.update` | PATCH `/api/v2/workspaces/{workspace_id}/content_editors/{id}` | Yes | — | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.delete` | DELETE `/api/v2/workspaces/{workspace_id}/content_editors/{id}` | Yes | — | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.get_content` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/content` | Yes | — | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.update_content` | PUT `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/content` | Yes | `content_editor.seo_score.calculated` / `.failed`; `content_editor.ai_search_score.calculated` / `.failed`; `content_editor.content_score.recalculated` | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.list_v1` | GET `/api/v1/content_editors` (legacy; `Workspace-Id` header) | No | — | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.create_v1` | POST `/api/v1/content_editors` (legacy; `Workspace-Id` header) | No | `content_editor.initialization.completed` / `.failed`; `content_editor.content_score.recalculated`; `content_editor.ai_article.completed` / `.waiting_for_user_input` / `.failed` | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.get_v1` | GET `/api/v1/content_editors/{id}` (legacy) | No | — | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.update_v1` | PATCH `/api/v1/content_editors/{id}` (legacy) | No | `content_editor.content_score.recalculated` | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.get_content_v1` | GET `/api/v1/content_editors/{id}/content` (legacy) | No | — | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.get_content_score_v1` | GET `/api/v1/content_editors/{id}/content_score` (legacy) | No | — | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.get_structural_guidelines_v1` | GET `/api/v1/content_editors/{id}/structural_guidelines` (legacy) | No | — | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.get_terms_v1` | GET `/api/v1/content_editors/{id}/terms` (legacy) | No | — | https://app.surferseo.com/llms/content-editors.txt |

## AI Articles

| Capability ID | REST | WS | Async event | Live doc |
|---|---|---|---|---|
| `ai_article.list` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_articles` | Yes | — | https://app.surferseo.com/llms/ai-articles.txt |
| `ai_article.generate` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_articles` | Yes | `content_editor.ai_article.waiting_for_user_input` / `.completed` / `.failed` | https://app.surferseo.com/llms/ai-articles.txt |
| `ai_article.get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_articles/{article_id}` | Yes | — | https://app.surferseo.com/llms/ai-articles.txt |
| `ai_article.get_outline` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_articles/outline` | Yes | — | https://app.surferseo.com/llms/ai-articles.txt |
| `ai_article.submit_outline` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_articles/outline` | Yes | — (resumes generation; completion webhooks belong to `ai_article.generate`) | https://app.surferseo.com/llms/ai-articles.txt |

## Auto-Optimize

| Capability ID | REST | WS | Async event | Live doc |
|---|---|---|---|---|
| `auto_optimize.get_latest` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/auto_optimize` | Yes | — | https://app.surferseo.com/llms/auto-optimize.txt |
| `auto_optimize.run` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/auto_optimize` | Yes | `content_editor.auto_optimize.completed` / `.failed` / `.cancelled` | https://app.surferseo.com/llms/auto-optimize.txt |
| `auto_optimize.get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/auto_optimize/{job_id}` | Yes | — | https://app.surferseo.com/llms/auto-optimize.txt |
| `auto_optimize.run_v1` | POST `/api/v1/content_editors/{id}/auto_optimize` (legacy) | No | `content_editor.auto_optimize.completed` / `.failed` / `.cancelled` | https://app.surferseo.com/llms/content-editors.txt |

## SEO Guidelines

| Capability ID | REST | WS | Async event | Live doc |
|---|---|---|---|---|
| `seo_guidelines.get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines` | Yes | `content_editor.seo_score.calculated` / `.failed` | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.get_status` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/status` | Yes | — | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.get_score` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/score` | Yes | `content_editor.seo_score.calculated` / `.failed` | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.get_structure` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/structure` | Yes | — | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.update_structure` | PATCH `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/structure` | Yes | — | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.get_terms` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/terms` | Yes | — | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.update_terms` | PATCH `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/terms` | Yes | — | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.get_topics_and_questions` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/topics_and_questions` | Yes | — | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.update_topics_and_questions` | PATCH `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/topics_and_questions` | Yes | — | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.get_competitors` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/competitors` | Yes | — | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.update_competitors` | PATCH `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/competitors` | Yes | — | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.load_more_competitors` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/competitors/load_more` | Yes | `content_editor.seo_guidelines.competitors.load_more.completed` / `.failed` | https://app.surferseo.com/llms/seo-guidelines.txt |

## AI Search

| Capability ID | REST | WS | Async event | Live doc |
|---|---|---|---|---|
| `ai_search.get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_search_guidelines` | Yes | `content_editor.ai_search_score.calculated` / `.failed` | https://app.surferseo.com/llms/ai-search.txt |
| `ai_search.get_facts` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_search_guidelines/facts` | Yes | — | https://app.surferseo.com/llms/ai-search.txt |
| `ai_search.get_score` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_search_guidelines/score` | Yes | `content_editor.ai_search_score.calculated` / `.failed` | https://app.surferseo.com/llms/ai-search.txt |

## Outline

| Capability ID | REST | WS | Async event | Live doc |
|---|---|---|---|---|
| `outline.get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/outline` | Yes | — | https://app.surferseo.com/llms/outline.txt |
| `outline.regenerate` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/outline/regenerate` | Yes | `content_editor.outline.completed` / `.failed` | https://app.surferseo.com/llms/outline.txt |

## Permalinks

| Capability ID | REST | WS | Async event | Live doc |
|---|---|---|---|---|
| `permalink.list` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/permalinks` | Yes | — | https://app.surferseo.com/llms/permalinks.txt |
| `permalink.reset` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/permalinks/reset` | Yes | — | https://app.surferseo.com/llms/permalinks.txt |

## Content Templates

| Capability ID | REST | WS | Async event | Live doc |
|---|---|---|---|---|
| `content_template.list` | GET `/api/v2/workspaces/{workspace_id}/content_templates` | Yes | — | https://app.surferseo.com/llms/content-templates.txt |
| `content_template.create` | POST `/api/v2/workspaces/{workspace_id}/content_templates` | Yes | — | https://app.surferseo.com/llms/content-templates.txt |
| `content_template.get` | GET `/api/v2/workspaces/{workspace_id}/content_templates/{id}` | Yes | — | https://app.surferseo.com/llms/content-templates.txt |
| `content_template.update` | PATCH or PUT `/api/v2/workspaces/{workspace_id}/content_templates/{id}` | Yes | — | https://app.surferseo.com/llms/content-templates.txt |
| `content_template.delete` | DELETE `/api/v2/workspaces/{workspace_id}/content_templates/{id}` | Yes | — | https://app.surferseo.com/llms/content-templates.txt |

## Custom Voices

| Capability ID | REST | WS | Async event | Live doc |
|---|---|---|---|---|
| `custom_voice.list` | GET `/api/v2/workspaces/{workspace_id}/custom_voices` | Yes | — | https://app.surferseo.com/llms/custom-voices.txt |
| `custom_voice.create` | POST `/api/v2/workspaces/{workspace_id}/custom_voices` | Yes | — | https://app.surferseo.com/llms/custom-voices.txt |
| `custom_voice.get` | GET `/api/v2/workspaces/{workspace_id}/custom_voices/{id}` | Yes | — | https://app.surferseo.com/llms/custom-voices.txt |
| `custom_voice.update` | PATCH or PUT `/api/v2/workspaces/{workspace_id}/custom_voices/{id}` | Yes | — | https://app.surferseo.com/llms/custom-voices.txt |
| `custom_voice.delete` | DELETE `/api/v2/workspaces/{workspace_id}/custom_voices/{id}` | Yes | — | https://app.surferseo.com/llms/custom-voices.txt |

## Surfer Content Templates

| Capability ID | REST | WS | Async event | Live doc |
|---|---|---|---|---|
| `surfer_content_template.list` | GET `/api/v2/surfer_content_templates` | No | — | https://app.surferseo.com/llms/surfer-content-templates.txt |

## Audit (v1)

| Capability ID | REST | WS | Async event | Live doc |
|---|---|---|---|---|
| `audit.create` | POST `/api/v1/audits` (`Workspace-Id` header; async — poll `audit.get`) | No | — | https://app.surferseo.com/llms/audit.txt |
| `audit.get` | GET `/api/v1/audits/{id}` (poll for state) | No | — | https://app.surferseo.com/llms/audit.txt |

## SERP Analyzer (v1)

| Capability ID | REST | WS | Async event | Live doc |
|---|---|---|---|---|
| `serp_analyzer.analyze` | POST `/api/v1/serp_analyzers` (`Workspace-Id` header; async) | No | — | https://app.surferseo.com/llms/serp-analyzer.txt |
| `serp_analyzer.analyze_batch` | POST `/api/v1/serp_analyzers/batch` (async; 10 req/min) | No | — | https://app.surferseo.com/llms/serp-analyzer.txt |
| `serp_analyzer.analyze_deprecated` | POST `/api/v1/serp_analyzer` (deprecated alias of `serp_analyzer.analyze`) | No | — | https://app.surferseo.com/llms/serp-analyzer.txt |
| `serp_analyzer.analyze_batch_deprecated` | POST `/api/v1/serp_analyzer/batches` (deprecated alias of `serp_analyzer.analyze_batch`) | No | — | https://app.surferseo.com/llms/serp-analyzer.txt |
| `serp_analyzer.list` | GET `/api/v1/exports/csv/serp_analyzer` (CSV; `Workspace-Id` header) | No | — | https://app.surferseo.com/llms/serp-analyzer.txt |
| `serp_analyzer.get_prominent_terms` | GET `/api/v1/exports/csv/serp_analyzer/{serp_analyzer_id}/prominent_terms` (CSV) | No | — | https://app.surferseo.com/llms/serp-analyzer.txt |
| `serp_analyzer.get_search_results` | GET `/api/v1/exports/csv/serp_analyzer/{serp_analyzer_id}/search_results` (CSV) | No | — | https://app.surferseo.com/llms/serp-analyzer.txt |

## AI Detector / Humanizer / Locations (v1)

| Capability ID | REST | WS | Async event | Live doc |
|---|---|---|---|---|
| `ai_detector.detect` | POST `/api/v1/ai_detector/detect` (synchronous; 60 req/min) | No | — | https://app.surferseo.com/llms/other.txt |
| `humanizer.humanize` | POST `/api/v1/humanizer/humanize` (synchronous; `Workspace-Id` header) | No | — | https://app.surferseo.com/llms/other.txt |
| `locations.list` | GET `/api/v1/locations` (**public — no API key**) | No | — | https://app.surferseo.com/llms/other.txt |
