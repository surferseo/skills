# Surfer API capability map

REST binding for the IDs in `surfer-capabilities/ports.md`; cite ports.md for async/poll
semantics. Referenced by surfer-api as a sibling, never by a workflow.

This file is the REST half of the capability map: it binds each capability ID to its HTTP
method+path, flags workspace scoping, and points at the per-resource Live doc. It carries
**no** transport-neutral async detail (async?/webhook event/poll-via/field/terminal value);
those live in `surfer-capabilities/ports.md`. Columns:

- **Capability ID** — the neutral ID defined in `surfer-capabilities/ports.md`.
- **REST method+path** — HTTP verb + path. `{workspace_id}`-scoped paths are flagged under
  **Workspace-scoped?**.
- **Workspace-scoped?** — under `/api/v2/workspaces/{workspace_id}/...`? `Yes` / `No`.
- **Live-doc URL** — per-resource doc to fetch before calling (see SKILL.md standing rule):
  `https://app.surferseo.com/llms/<resource>.txt`.

All 69 capability IDs are listed. Prefer v2; v1/`_v1` rows are legacy/deprecated, kept only
where no v2 equivalent exists.

## Workspaces

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `workspace.list` | GET `/api/v2/workspaces` | No | https://app.surferseo.com/llms/workspaces.txt |
| `workspace.list_v1` | GET `/api/v1/workspaces` (legacy) | No | https://app.surferseo.com/llms/other.txt |

## Content Editors

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `content_editor.list_all` | GET `/api/v2/content_editors` (org-wide) | No | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.list` | GET `/api/v2/workspaces/{workspace_id}/content_editors` | Yes | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.create` | POST `/api/v2/workspaces/{workspace_id}/content_editors` | Yes | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{id}` | Yes | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.update` | PATCH `/api/v2/workspaces/{workspace_id}/content_editors/{id}` | Yes | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.delete` | DELETE `/api/v2/workspaces/{workspace_id}/content_editors/{id}` | Yes | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.get_content` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/content` | Yes | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.update_content` | PUT `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/content` | Yes | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.list_v1` | GET `/api/v1/content_editors` (legacy; `Workspace-Id` header) | No | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.create_v1` | POST `/api/v1/content_editors` (legacy; `Workspace-Id` header) | No | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.get_v1` | GET `/api/v1/content_editors/{id}` (legacy) | No | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.update_v1` | PATCH `/api/v1/content_editors/{id}` (legacy) | No | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.get_content_v1` | GET `/api/v1/content_editors/{id}/content` (legacy) | No | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.get_content_score_v1` | GET `/api/v1/content_editors/{id}/content_score` (legacy) | No | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.get_structural_guidelines_v1` | GET `/api/v1/content_editors/{id}/structural_guidelines` (legacy) | No | https://app.surferseo.com/llms/content-editors.txt |
| `content_editor.get_terms_v1` | GET `/api/v1/content_editors/{id}/terms` (legacy) | No | https://app.surferseo.com/llms/content-editors.txt |

## AI Articles

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `ai_article.list` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_articles` | Yes | https://app.surferseo.com/llms/ai-articles.txt |
| `ai_article.generate` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_articles` | Yes | https://app.surferseo.com/llms/ai-articles.txt |
| `ai_article.get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_articles/{article_id}` | Yes | https://app.surferseo.com/llms/ai-articles.txt |
| `ai_article.get_outline` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_articles/outline` | Yes | https://app.surferseo.com/llms/ai-articles.txt |
| `ai_article.submit_outline` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_articles/outline` | Yes | https://app.surferseo.com/llms/ai-articles.txt |

## Auto-Optimize

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `auto_optimize.get_latest` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/auto_optimize` | Yes | https://app.surferseo.com/llms/auto-optimize.txt |
| `auto_optimize.run` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/auto_optimize` | Yes | https://app.surferseo.com/llms/auto-optimize.txt |
| `auto_optimize.get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/auto_optimize/{job_id}` | Yes | https://app.surferseo.com/llms/auto-optimize.txt |
| `auto_optimize.run_v1` | POST `/api/v1/content_editors/{id}/auto_optimize` (legacy) | No | https://app.surferseo.com/llms/content-editors.txt |

## SEO Guidelines

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `seo_guidelines.get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.get_status` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/status` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.get_score` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/score` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.get_structure` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/structure` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.update_structure` | PATCH `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/structure` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.get_terms` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/terms` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.update_terms` | PATCH `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/terms` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.get_topics_and_questions` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/topics_and_questions` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.update_topics_and_questions` | PATCH `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/topics_and_questions` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.get_competitors` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/competitors` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.update_competitors` | PATCH `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/competitors` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |
| `seo_guidelines.load_more_competitors` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/seo_guidelines/competitors/load_more` | Yes | https://app.surferseo.com/llms/seo-guidelines.txt |

## AI Search

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `ai_search.get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_search_guidelines` | Yes | https://app.surferseo.com/llms/ai-search.txt |
| `ai_search.get_facts` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_search_guidelines/facts` | Yes | https://app.surferseo.com/llms/ai-search.txt |
| `ai_search.get_score` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/ai_search_guidelines/score` | Yes | https://app.surferseo.com/llms/ai-search.txt |

## Outline

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `outline.get` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/outline` | Yes | https://app.surferseo.com/llms/outline.txt |
| `outline.regenerate` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/outline/regenerate` | Yes | https://app.surferseo.com/llms/outline.txt |

## Permalinks

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `permalink.list` | GET `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/permalinks` | Yes | https://app.surferseo.com/llms/permalinks.txt |
| `permalink.reset` | POST `/api/v2/workspaces/{workspace_id}/content_editors/{content_editor_id}/permalinks/reset` | Yes | https://app.surferseo.com/llms/permalinks.txt |

## Content Templates

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `content_template.list` | GET `/api/v2/workspaces/{workspace_id}/content_templates` | Yes | https://app.surferseo.com/llms/content-templates.txt |
| `content_template.create` | POST `/api/v2/workspaces/{workspace_id}/content_templates` | Yes | https://app.surferseo.com/llms/content-templates.txt |
| `content_template.get` | GET `/api/v2/workspaces/{workspace_id}/content_templates/{id}` | Yes | https://app.surferseo.com/llms/content-templates.txt |
| `content_template.update` | PATCH or PUT `/api/v2/workspaces/{workspace_id}/content_templates/{id}` | Yes | https://app.surferseo.com/llms/content-templates.txt |
| `content_template.delete` | DELETE `/api/v2/workspaces/{workspace_id}/content_templates/{id}` | Yes | https://app.surferseo.com/llms/content-templates.txt |

## Custom Voices

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `custom_voice.list` | GET `/api/v2/workspaces/{workspace_id}/custom_voices` | Yes | https://app.surferseo.com/llms/custom-voices.txt |
| `custom_voice.create` | POST `/api/v2/workspaces/{workspace_id}/custom_voices` | Yes | https://app.surferseo.com/llms/custom-voices.txt |
| `custom_voice.get` | GET `/api/v2/workspaces/{workspace_id}/custom_voices/{id}` | Yes | https://app.surferseo.com/llms/custom-voices.txt |
| `custom_voice.update` | PATCH or PUT `/api/v2/workspaces/{workspace_id}/custom_voices/{id}` | Yes | https://app.surferseo.com/llms/custom-voices.txt |
| `custom_voice.delete` | DELETE `/api/v2/workspaces/{workspace_id}/custom_voices/{id}` | Yes | https://app.surferseo.com/llms/custom-voices.txt |

## Surfer Content Templates

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `surfer_content_template.list` | GET `/api/v2/surfer_content_templates` | No | https://app.surferseo.com/llms/surfer-content-templates.txt |

## Audit (v1)

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `audit.create` | POST `/api/v1/audits` (`Workspace-Id` header) | No | https://app.surferseo.com/llms/audit.txt |
| `audit.get` | GET `/api/v1/audits/{id}` | No | https://app.surferseo.com/llms/audit.txt |

## SERP Analyzer (v1)

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `serp_analyzer.analyze` | POST `/api/v1/serp_analyzers` (`Workspace-Id` header) | No | https://app.surferseo.com/llms/serp-analyzer.txt |
| `serp_analyzer.analyze_batch` | POST `/api/v1/serp_analyzers/batch` (10 req/min) | No | https://app.surferseo.com/llms/serp-analyzer.txt |
| `serp_analyzer.analyze_deprecated` | POST `/api/v1/serp_analyzer` (deprecated alias of `serp_analyzer.analyze`) | No | https://app.surferseo.com/llms/serp-analyzer.txt |
| `serp_analyzer.analyze_batch_deprecated` | POST `/api/v1/serp_analyzer/batches` (deprecated alias of `serp_analyzer.analyze_batch`) | No | https://app.surferseo.com/llms/serp-analyzer.txt |
| `serp_analyzer.list` | GET `/api/v1/exports/csv/serp_analyzer` (CSV; `Workspace-Id` header) | No | https://app.surferseo.com/llms/serp-analyzer.txt |
| `serp_analyzer.get_prominent_terms` | GET `/api/v1/exports/csv/serp_analyzer/{serp_analyzer_id}/prominent_terms` (CSV) | No | https://app.surferseo.com/llms/serp-analyzer.txt |
| `serp_analyzer.get_search_results` | GET `/api/v1/exports/csv/serp_analyzer/{serp_analyzer_id}/search_results` (CSV) | No | https://app.surferseo.com/llms/serp-analyzer.txt |

## AI Detector / Humanizer / Locations (v1)

| Capability ID | REST method+path | Workspace-scoped? | Live-doc URL |
|---|---|---|---|
| `ai_detector.detect` | POST `/api/v1/ai_detector/detect` (60 req/min) | No | https://app.surferseo.com/llms/other.txt |
| `humanizer.humanize` | POST `/api/v1/humanizer/humanize` (`Workspace-Id` header) | No | https://app.surferseo.com/llms/other.txt |
| `locations.list` | GET `/api/v1/locations` (**public — no API key**) | No | https://app.surferseo.com/llms/other.txt |
