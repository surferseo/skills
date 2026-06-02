---
name: surfer-api
description: >-
  Use when calling the Surfer SEO REST API directly, when a surfer-* workflow skill needs to
  execute its API calls, or when the user mentions the Surfer API, an API key, a workspace_id, a
  v1/v2 endpoint or path, webhooks, rate limits, idempotency, or pagination.
license: MIT
---

# Surfer API (transport)

## Overview

The REST transport for Surfer SEO: how to authenticate and call the API, the always-on
conventions every call obeys, and the **capability map** binding each shared capability ID
to its REST method+path. The `surfer-*` workflow skills decide *what* to call and in what
order; this skill is *how*, and is the single source for the conventions below.

## Prerequisites

1. **Get an API key** from the Surfer app (organization API settings).
2. **Send `API-KEY: <key>`** on every authenticated request (some ops are public — see
   the map's notes, e.g. `locations.list`).
3. **Resolve a workspace_id.** Most v2 resources are workspace-scoped. List with
   `workspace.list` (`GET /api/v2/workspaces`) and use one whose `state` is `active` (only
   active workspaces can manage resources). If exactly one is active, use it. If several
   are active, the caller must supply `workspace_id` — do not guess. If none are active,
   stop and report (no resource ops are possible).

## Conventions (always on — single source)

Hold for every Surfer call. Workflow skills assume these and never restate them.

**Authentication.** Send `API-KEY: <key>` unless the op is explicitly public. Missing or
invalid key -> `401 unauthorized`.

**Workspace scoping.** v2 resources live under `/api/v2/workspaces/{workspace_id}/...`;
the key must own the workspace. Accessing another org's workspace returns
**`404 not_found`, not `403`** (existence is not leaked) — treat an unexpected 404 on a
known-good ID as a scoping/ownership problem. Some v1 ops select the workspace via a
`Workspace-Id` header, falling back to the oldest active workspace when omitted (noted in
the map).

**Pagination.** List endpoints accept `page` (default `1`, 1-indexed) and `page_size`
(default `25`, max `100`). Responses carry `meta` `{ total, page, page_size, total_pages }`
(plus `filters`/`ordering` where supported). Page until `page >= total_pages`.

**Errors.** v2 uses the envelope `{ "error": { "reason", "message", "details": [] } }`.

| HTTP | reason | Meaning |
|------|--------|---------|
| 400 | `validation_error` | Invalid request parameters |
| 401 | `unauthorized` | Missing or invalid API key |
| 403 | `permission_denied` | Valid key but no access (incl. plan/billing) |
| 404 | `not_found` | Resource does not exist (also cross-org access) |
| 406 | `not_acceptable` | Requested response format unavailable |
| 409 | `conflict` | Idempotency-key conflict / state conflict |
| 413 | `content_too_large` | Request body too large |
| 415 | `unsupported_media_type` | Unsupported request content type |
| 422 | `unprocessable_entity` | Understood but cannot be processed |
| 422 | `quota_exceeded` | Feature enabled but credit/quota limit reached |
| 429 | `rate_limit_exceeded` | Too many requests |
| 500 | `internal_error` | Unexpected server error |

**Rate limits.** Enforced per API key, per endpoint (most v2 ops 10 req/sec; some v1 ops
differ — check the live doc). `429` includes a `Retry-After` header (also surfaced as
`details[].retry_after`); back off that many seconds, then retry. v2 also returns
`x-ratelimit-limit` / `x-ratelimit-remaining` / `x-ratelimit-reset` (Unix seconds) —
throttle proactively as `remaining` nears 0.

**Idempotency.** v2 create ops accept an `Idempotency-Key` header. Reusing the same key on
the same path returns the original response; reusing it on a different path -> `422`. Keys
expire after 24h. Generate **one key per logical create up front and reuse it on every
retry** of that same create (including `429` and network retries) to avoid double-spending.
Credit-spending creates: `content_editor.create`, `ai_article.generate`, `auto_optimize.run`,
`outline.regenerate`, `serp_analyzer.*`, `audit.create`. `quota_exceeded` (`422`) is **not
retryable** — stop and report.

**Async model (webhooks vs polling).** Async ops (Content Editor init, AI article
generation, auto-optimize, SEO/AI-search scoring, outline regeneration, load-more
competitors) return immediately in a non-terminal state and finish later.

- *Webhooks (for integrators).* Setup is **org-level**: expose an HTTPS endpoint that
  accepts POST and returns `200`, then have Surfer register it. Each delivery carries a
  `Verification-Key` header and a JSON body naming a `content_editor.*` event. The
  authoritative event set:
  - `content_editor.initialization.completed` / `.failed`
  - `content_editor.ai_article.completed` / `.waiting_for_user_input` / `.failed`
  - `content_editor.seo_score.calculated` / `.failed`
  - `content_editor.ai_search_score.calculated` / `.failed`
  - `content_editor.content_score.recalculated`
  - `content_editor.auto_optimize.completed` / `.failed` / `.cancelled`
  - `content_editor.outline.completed` / `.failed`
  - `content_editor.seo_guidelines.competitors.load_more.completed` / `.failed`
- *Polling.* **If you are an agent executing calls directly (no persistent webhook
  receiver you control), polling is your path** — the webhook bullet above is for
  integrators. Poll the matching GET (see capability-map.md "Poll-via targets").

**Terminal vocabulary differs by resource — never assume `completed`.** Confirm the field
and success/failure values from the Live doc, but the verified mapping is:

| Poll via | Field | Success | Notes |
|---|---|---|---|
| `content_editor.get` | `state` | `completed` | **No `failed` in the body** — init failure is only delivered via webhook; without one, a timeout is your only failure detector. |
| `ai_article.get` | `state` | `completed` | Failure value `failed`; `waiting_for_user_input` pauses for outline review. |
| `auto_optimize.get` | `state` (+`result`) | `completed` | `result` = `optimized` / `nothing_to_optimize`. |
| `seo_guidelines.get_score` / `ai_search.get_score` | `status` | `ready` | Terminal-success is `ready` (not `completed`); `calculating` means keep polling. |

**Bounded poll.** The API documents no timeout or interval. Start at 2-5s, back off
exponentially capped at ~30-60s, and stop at a hard cap (max elapsed or max attempts);
on cap, report the job as **timed-out / indeterminate** rather than looping. Respect
rate-limit headers throughout.

**Stale-score trap.** After mutating content (`content_editor.update_content`), a score
read can return the **prior** `score` with `status: calculating`. Do not trust `score`
unless `status == ready` **and** `calculated_at` has advanced past the pre-mutation value —
capture `calculated_at` before mutating so you can detect the new calculation.

**Versioning.** Prefer v2. v1 is legacy/deprecated, kept only for older clients or where
no v2 equivalent exists yet (Audit, SERP Analyzer, AI Detector, Humanizer, Locations).

## Capability map

All 69 capability IDs — grouped, with REST method+path, workspace-scoping, async events,
poll-via targets, and live doc — live in **capability-map.md** (sibling). Workflow skills
reference these IDs, never raw paths; read it to resolve an ID to its endpoint.

## Standing rule: fetch the live doc before calling

The capability map gives method, path, and where the truth lives — not request params or
response shapes, on purpose. **Before invoking any capability, WebFetch its Live doc URL**
(`https://app.surferseo.com/llms/<resource>.txt`) for the exact params, headers, body
schema, and response shape (index: `.../llms.txt`; full: `.../llms-full.txt`). These are
OpenAPI-generated and authoritative — **never hard-code from memory**; if recollection
disagrees with the live doc, the live doc wins.

## On terminal failure

This transport skill never decides what to do next — it reports the terminal state up to
the calling `surfer-*` workflow skill.

- `401` / `403` / `quota_exceeded` (`422`) / `404` on a known-good ID -> **not retryable
  here**; stop and report (auth, billing/plan, or scoping problem).
- `429` / `5xx` / transient network -> bounded retry (reuse the idempotency key on
  creates), then report if it persists.
- Poll timeout (hard cap reached) -> report **indeterminate**.

## Request shape

A v2 call is just the workspace-scoped path plus the auth header; everything else (params,
body, response shape) comes from the Live doc:

```bash
curl -sS -H "API-KEY: $SURFER_API_KEY" \
  "https://app.surferseo.com/api/v2/workspaces/{workspace_id}/content_editors/{id}"
```
