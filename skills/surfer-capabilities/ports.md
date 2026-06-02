# Surfer capability ports

Transport-neutral capability contract. Each transport adapter binds these IDs to its own
invocation (e.g. REST → surfer-api/capability-map.md). New transports bind the same IDs their own way.

This file is the transport-neutral half of the capability map: it states, per capability ID,
whether the operation is asynchronous, which `content_editor.*` webhook event(s) it can emit,
and — when an agent has no webhook receiver — how to poll for terminal state (which GET
capability to read, which field, and the verified success/failure values). It carries **no**
REST detail (no method, path, URL, header, or tool name); resolve those in the transport
adapter.

Terminal vocabulary differs by resource — never assume `completed`. The verified mappings:

- `content_editor.get` -> `state` -> success `completed`. Init **failure has no `failed`
  body value** and arrives only via webhook; without a webhook, a poll timeout is the only
  failure detector.
- `ai_article.get` -> `state` -> success `completed`, failure `failed`;
  `waiting_for_user_input` pauses for outline review.
- `auto_optimize.get` -> `state` (+`result`) -> success `completed`;
  `result` = `optimized` / `nothing_to_optimize`.
- `seo_guidelines.get_score` & `ai_search.get_score` -> `status` -> success `ready`
  (`calculating` means keep polling).

| Capability ID | Resource group | Async? | Webhook event(s) | Poll-via (capability ID) | Poll field | Success value | Failure value |
|---|---|---|---|---|---|---|---|
| `workspace.list` | Workspaces | no | — | — | — | — | — |
| `workspace.list_v1` | Workspaces | no | — | — | — | — | — |
| `content_editor.list_all` | Content Editors | no | — | — | — | — | — |
| `content_editor.list` | Content Editors | no | — | — | — | — | — |
| `content_editor.create` | Content Editors | yes | `content_editor.initialization.completed` / `.failed`; `content_editor.seo_score.calculated` / `.failed`; `content_editor.ai_search_score.calculated` / `.failed`; `content_editor.content_score.recalculated` | `content_editor.get` | `state` | `completed` | (none in body — webhook only) |
| `content_editor.get` | Content Editors | no | — | — | — | — | — |
| `content_editor.update` | Content Editors | no | — | — | — | — | — |
| `content_editor.delete` | Content Editors | no | — | — | — | — | — |
| `content_editor.get_content` | Content Editors | no | — | — | — | — | — |
| `content_editor.update_content` | Content Editors | yes | `content_editor.seo_score.calculated` / `.failed`; `content_editor.ai_search_score.calculated` / `.failed`; `content_editor.content_score.recalculated` | `seo_guidelines.get_score` + `ai_search.get_score` | `status` (each) | `ready` (each) | `.failed` event (no body failure value) |
| `content_editor.create_v1` | Content Editors | yes | `content_editor.initialization.completed` / `.failed`; `content_editor.content_score.recalculated`; `content_editor.ai_article.completed` / `.waiting_for_user_input` / `.failed` | `content_editor.get_v1` | `state` | `completed` | (none in body — webhook only) |
| `content_editor.get_v1` | Content Editors | no | — | — | — | — | — |
| `content_editor.update_v1` | Content Editors | yes | `content_editor.content_score.recalculated` | `content_editor.get_content_score_v1` | (content score) | (recalculated) | — |
| `content_editor.get_content_v1` | Content Editors | no | — | — | — | — | — |
| `content_editor.get_content_score_v1` | Content Editors | no | — | — | — | — | — |
| `content_editor.get_structural_guidelines_v1` | Content Editors | no | — | — | — | — | — |
| `content_editor.get_terms_v1` | Content Editors | no | — | — | — | — | — |
| `content_editor.list_v1` | Content Editors | no | — | — | — | — | — |
| `ai_article.list` | AI Articles | no | — | — | — | — | — |
| `ai_article.generate` | AI Articles | yes | `content_editor.ai_article.waiting_for_user_input` / `.completed` / `.failed` | `ai_article.get` | `state` | `completed` | `failed` |
| `ai_article.get` | AI Articles | no | — | — | — | — | — |
| `ai_article.get_outline` | AI Articles | no | — | — | — | — | — |
| `ai_article.submit_outline` | AI Articles | yes | — (resumes generation; completion webhooks belong to `ai_article.generate`) | `ai_article.get` | `state` | `completed` | `failed` |
| `auto_optimize.get_latest` | Auto-Optimize | no | — | — | — | — | — |
| `auto_optimize.run` | Auto-Optimize | yes | `content_editor.auto_optimize.completed` / `.failed` / `.cancelled` | `auto_optimize.get` | `state` (+`result`) | `completed` (`result` = `optimized` / `nothing_to_optimize`) | `failed` / `cancelled` |
| `auto_optimize.get` | Auto-Optimize | no | — | — | — | — | — |
| `auto_optimize.run_v1` | Auto-Optimize | yes | `content_editor.auto_optimize.completed` / `.failed` / `.cancelled` | `auto_optimize.get` | `state` (+`result`) | `completed` (`result` = `optimized` / `nothing_to_optimize`) | `failed` / `cancelled` |
| `seo_guidelines.get` | SEO Guidelines | no | `content_editor.seo_score.calculated` / `.failed` | — | — | — | — |
| `seo_guidelines.get_status` | SEO Guidelines | no | — | — | — | — | — |
| `seo_guidelines.get_score` | SEO Guidelines | yes | `content_editor.seo_score.calculated` / `.failed` | `seo_guidelines.get_score` | `status` | `ready` | `.failed` event (no body failure value) |
| `seo_guidelines.get_structure` | SEO Guidelines | no | — | — | — | — | — |
| `seo_guidelines.update_structure` | SEO Guidelines | no | — | — | — | — | — |
| `seo_guidelines.get_terms` | SEO Guidelines | no | — | — | — | — | — |
| `seo_guidelines.update_terms` | SEO Guidelines | no | — | — | — | — | — |
| `seo_guidelines.get_topics_and_questions` | SEO Guidelines | no | — | — | — | — | — |
| `seo_guidelines.update_topics_and_questions` | SEO Guidelines | no | — | — | — | — | — |
| `seo_guidelines.get_competitors` | SEO Guidelines | no | — | — | — | — | — |
| `seo_guidelines.update_competitors` | SEO Guidelines | no | — | — | — | — | — |
| `seo_guidelines.load_more_competitors` | SEO Guidelines | yes | `content_editor.seo_guidelines.competitors.load_more.completed` / `.failed` | `seo_guidelines.get` | `load_more_status` | `idle` | `.failed` event (no body failure value) |
| `ai_search.get` | AI Search | no | `content_editor.ai_search_score.calculated` / `.failed` | — | — | — | — |
| `ai_search.get_facts` | AI Search | no | — | — | — | — | — |
| `ai_search.get_score` | AI Search | yes | `content_editor.ai_search_score.calculated` / `.failed` | `ai_search.get_score` | `status` | `ready` | `.failed` event (no body failure value) |
| `outline.get` | Outline | no | — | — | — | — | — |
| `outline.regenerate` | Outline | yes | `content_editor.outline.completed` / `.failed` | `content_editor.get` | `outline.status` | (not `scheduled`/`executing`) | `.failed` event (no body failure value) |
| `permalink.list` | Permalinks | no | — | — | — | — | — |
| `permalink.reset` | Permalinks | no | — | — | — | — | — |
| `content_template.list` | Content Templates | no | — | — | — | — | — |
| `content_template.create` | Content Templates | no | — | — | — | — | — |
| `content_template.get` | Content Templates | no | — | — | — | — | — |
| `content_template.update` | Content Templates | no | — | — | — | — | — |
| `content_template.delete` | Content Templates | no | — | — | — | — | — |
| `custom_voice.list` | Custom Voices | no | — | — | — | — | — |
| `custom_voice.create` | Custom Voices | no | — | — | — | — | — |
| `custom_voice.get` | Custom Voices | no | — | — | — | — | — |
| `custom_voice.update` | Custom Voices | no | — | — | — | — | — |
| `custom_voice.delete` | Custom Voices | no | — | — | — | — | — |
| `surfer_content_template.list` | Surfer Content Templates | no | — | — | — | — | — |
| `audit.create` | Audit | yes | — | `audit.get` | `state` | (poll until terminal) | (per live doc) |
| `audit.get` | Audit | no | — | — | — | — | — |
| `serp_analyzer.analyze` | SERP Analyzer | yes | — | `serp_analyzer.list` | `state` | (poll until terminal) | (per live doc) |
| `serp_analyzer.analyze_batch` | SERP Analyzer | yes | — | `serp_analyzer.list` | `state` | (poll until terminal) | (per live doc) |
| `serp_analyzer.analyze_batch_deprecated` | SERP Analyzer | yes | — | `serp_analyzer.list` | `state` | (poll until terminal) | (per live doc) |
| `serp_analyzer.analyze_deprecated` | SERP Analyzer | yes | — | `serp_analyzer.list` | `state` | (poll until terminal) | (per live doc) |
| `serp_analyzer.get_prominent_terms` | SERP Analyzer | no | — | — | — | — | — |
| `serp_analyzer.get_search_results` | SERP Analyzer | no | — | — | — | — | — |
| `serp_analyzer.list` | SERP Analyzer | no | — | — | — | — | — |
| `ai_detector.detect` | AI Detector | no | — | — | — | — | — |
| `humanizer.humanize` | Humanizer | no | — | — | — | — | — |
| `locations.list` | Locations | no | — | — | — | — | — |

## Notes

- **Event vs. async.** A few read ops (`seo_guidelines.get`, `ai_search.get`) can have a
  `content_editor.*` score event delivered while they are read, but the read itself is
  synchronous; only the score-recalculation trigger is async. The async create/mutate ops
  that actually *kick off* that work are `content_editor.create`,
  `content_editor.update_content`, `seo_guidelines.get_score` / `ai_search.get_score`
  (after a content change), `ai_article.generate`, `auto_optimize.run`,
  `outline.regenerate`, and `seo_guidelines.load_more_competitors`.
- **No webhook path for v1 batch/analysis ops.** `audit.*` and `serp_analyzer.analyze*`
  are async but emit no `content_editor.*` webhook; an agent must poll the listed GET.
- **Stale-score trap.** A score read can return the prior value with `status: calculating`;
  trust `score` only when `status == ready` and `calculated_at` has advanced past the
  pre-mutation value.
- **Bounded poll.** No documented interval/timeout; start at 2-5s, back off exponentially
  capped at ~30-60s, stop at a hard cap, and report **timed-out / indeterminate** rather
  than looping.
