---
name: surfer-api
description: >-
  Surfer's REST adapter — today the default Surfer transport. Use to execute any Surfer capability
  over REST, when a surfer-* workflow needs to execute its calls, or when the user mentions the
  Surfer API, an API key, a workspace_id, a v1/v2 endpoint or path, webhooks, rate limits,
  idempotency, or pagination. Capability IDs and their neutral async/poll semantics live in
  surfer-capabilities; this skill is how those run over HTTP. An explicit transport pin (e.g.
  /surfer-api) always takes precedence.
license: MIT
---

# Surfer API (REST adapter)

## Overview

Surfer's pure REST adapter. It covers how to authenticate and call the API, the always-on
REST conventions every HTTP call obeys, and the **capability map** binding each shared
capability ID to its REST method+path. The `surfer-*` workflow skills decide *what* to call
and in what order; this skill is *how* over HTTP. REST is the **current default** Surfer
transport; per `surfer-capabilities` §4 an explicit transport pin always wins, and new
transport adapters can be added later without changing workflows.

Capability IDs and their neutral async/poll semantics are defined in
`surfer-capabilities/ports.md`; this skill binds each ID to its REST method+path in
`capability-map.md`. The transport-neutral contract (which ops are async, which webhook
events they emit, how to poll for terminal state) is owned by `surfer-capabilities`, not
here — this adapter restates only the REST-specific mechanics of executing those ops.

## Prerequisites

1. **Get an API key** from the Surfer app (organization API settings).
2. **Send `API-KEY: <key>`** on every authenticated request (some ops are public — see
   the map's notes, e.g. `locations.list`). **If no API key is configured, stop and ask the
   user for it before the first authenticated call — never fabricate one or fire a blind
   request.** (This is a credential gate, separate from transport resolution: only reach it
   once a transport is already resolved.)
3. **Resolve a workspace_id.** Most v2 resources are workspace-scoped. List with
   `workspace.list` (`GET /api/v2/workspaces`) and use one whose `state` is `active` (only
   active workspaces can manage resources). If exactly one is active, use it. If several
   are active, the caller must supply `workspace_id` — do not guess. If none are active,
   stop and report (no resource ops are possible).

## REST conventions (always on)

These are the REST-specific mechanics every HTTP call to Surfer obeys; they are local to this
adapter. (Transport-neutral semantics — async/webhook/poll — live in
`surfer-capabilities/ports.md`.) Workflow skills assume these and never restate them.

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

**Async transport (REST mechanics).** *Which* ops are async, the webhook events they emit,
and the poll-via target / field / verified terminal values are the transport-neutral
contract in `surfer-capabilities/ports.md` — cite it, do not restate it here. This adapter
covers only how those play out over HTTP:

- *Webhook setup (for integrators).* Setup is **org-level**: expose an HTTPS endpoint that
  accepts POST and returns `200`, then have Surfer register it. Each delivery carries a
  `Verification-Key` header and a JSON body naming the `content_editor.*` event (event set
  per `ports.md`).
- *Polling (for direct callers).* **If you are an agent executing calls directly (no
  persistent webhook receiver you control), polling is your path** — the webhook bullet
  above is for integrators. Poll the matching GET capability; resolve which GET, which
  field, and the verified terminal values from `ports.md` (never assume the literal value
  `completed` — terminal vocabulary differs by resource), then bind that GET to its
  method+path via `capability-map.md`.

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

All 69 capability IDs — grouped, with REST method+path, workspace-scoping, and Live-doc URL
— are bound in **capability-map.md** (sibling). That is the REST binding only; the neutral
async/poll semantics for each ID live in `surfer-capabilities/ports.md`. Workflow skills
reference IDs, never raw paths; read the map to resolve an ID to its endpoint.

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
