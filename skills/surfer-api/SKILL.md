---
name: surfer-api
description: >-
  Surfer's REST adapter. Use it to run a Surfer capability over the HTTP API, when a surfer-*
  workflow runs over REST, or when the user mentions the Surfer API, an API key, an endpoint or path,
  webhooks, or idempotency. Capability IDs are the Surfer MCP server's tool names; the MCP server is
  the primary transport, and this skill is the secondary, REST one. It binds each ID to a REST method
  and path and owns the REST async and poll mechanics in capability-map.md. It never implements
  the MCP-only capabilities: brand knowledge and site recommendations. An explicit transport pin
  such as /surfer-api always takes precedence.
license: MIT
---

# Surfer API (REST adapter)

## Overview

Surfer's REST adapter. It covers how to authenticate and call the API, the always-on REST
conventions every HTTP call obeys, and the capability map that binds each capability ID to a REST
method and path. The `surfer-*` workflow skills decide what to call and in what order. This skill is
how to make those calls over HTTP.

Capability IDs are the Surfer MCP server's tool names. This skill binds each ID to a REST method and
path, and it owns the REST async and poll semantics. Both live in `capability-map.md`. That
reference matters here because a REST caller has no tool descriptions in context. It cannot
otherwise tell which operations are asynchronous or which GET to poll.

## Transport selection

Two transports exist, and the workflows run unchanged over either.

- The Surfer MCP server is primary. When its tools are connected this session, call them directly.
  Its tool names are the capability IDs, and each tool carries its own description of inputs, async
  behavior, and poll target.
- This skill is the secondary, REST transport. It runs when the MCP server is not connected, or when
  the user pins it explicitly, such as with /surfer-api. A pin wins over the primary default.

If neither is usable, run `surfer-connect`: it registers the MCP server in the current client or
sets up an API key for this skill, then hands control back. Never fall back to hand-written HTTP
against guessed endpoints, and do not treat a missing credential as the blocker when the real gap is
a missing transport.

The active transport owns everything mechanical: authentication, workspace scoping on the wire,
idempotency, the async/poll or webhook mechanics, error taxonomy, rate limits, pagination, and any
schema lookup before a call. Workflows name capability IDs only and never restate those.

## Prerequisites

1. **Get an API key** from the Surfer app's organization API settings.
2. **Send `API-KEY: <key>`** on every request. All contract capabilities are authenticated. If no
   API key is configured, stop and ask the user for it before the first call; `surfer-connect`
   covers obtaining and storing one. Never fabricate one or fire a blind request. This credential
   gate is separate from transport resolution. Reach it only once a transport is resolved.
3. **Resolve a `workspace_id`.** Most v2 resources are workspace-scoped. List workspaces with
   `workspace__list` and use one whose `state` is `active`, since only active workspaces can manage
   resources. If exactly one is active, use it. If several are active, ask the caller for the
   `workspace_id` rather than guessing. If none are active, stop and report, because no resource
   operations are possible.

## REST conventions (always on)

These are the REST-specific mechanics every HTTP call to Surfer obeys. They are local to this
adapter. Which operations are async, and how to poll them, is in the *Async operations & polling*
section of `capability-map.md`. Workflow skills assume these mechanics and never restate them.

**Authentication.** Send `API-KEY: <key>` on every request. A missing or invalid key returns
`401 unauthorized`.

**Workspace scoping.** v2 resources live under `/api/v2/workspaces/{workspace_id}/...`, and the key
must own the workspace. Accessing another org's workspace returns `404 not_found` rather than `403`,
so existence is never leaked. Treat an unexpected 404 on a known-good ID as a scoping or ownership
problem. `content_editor__list` and `workspace__list` are org-wide reads that omit the workspace
path segment.

**Pagination.** List endpoints accept `page`, which is 1-indexed and defaults to `1`, and
`page_size`, which defaults to `25` and caps at `100`. Responses carry `meta` with `total`, `page`,
`page_size`, and `total_pages`, plus `filters` and `ordering` where supported. Page until
`page >= total_pages`.

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

**Rate limits.** Enforced per API key and per endpoint. Most v2 ops allow 10 requests per second.
Check the live doc for the exact limit. A `429` includes a `Retry-After` header, also surfaced as
`details[].retry_after`. Back off that many seconds, then retry. v2 also returns
`x-ratelimit-limit`, `x-ratelimit-remaining`, and `x-ratelimit-reset`, in Unix seconds. Throttle
proactively as `remaining` nears 0.

**Idempotency.** v2 create ops accept an `Idempotency-Key` header. Reusing the same key on the same
path returns the original response. Reusing it on a different path returns `422`. Keys expire after
24 hours. Generate one key per logical create up front and reuse it on every retry of that create,
including `429` and network retries, so you never double-spend. Apply an idempotency key only to a v2
create whose live doc advertises one. The Content Editor, custom-template, and custom-voice create
docs advertise one. For every other operation, inspect the live document rather than carrying a key
by assumption. A `quota_exceeded` (`422`) is not retryable. Stop and report.

**Async transport.** The per-ID table lives in the *Async operations & polling* section of
`capability-map.md`. It names which ops are async, which GET to poll, the field, and the verified
terminal values. A REST caller learns an async outcome one of two ways.

- *Polling.* An agent executing calls directly, with no webhook receiver of its own, polls. Poll the
  GET named in that section. Never assume the literal value `completed`, because terminal vocabulary
  differs by resource. Respect rate-limit headers, back off between polls using the interval in
  that section, and stop at a hard cap. On reaching the cap, report the job as indeterminate rather
  than looping.
- *Webhooks, optional, for integrators.* Setup is org-level. Expose an HTTPS endpoint that accepts
  POST and returns `200`, then have Surfer register it. Each delivery carries a `Verification-Key`
  header and a JSON body naming a `content_editor.*` event. The event families are `initialization`,
  `seo_score`, `ai_search_score`, `content_score`, `ai_article`, `auto_optimize`, `outline`, and
  `seo_guidelines.competitors.load_more`. Most families end in `.completed` or `.failed`. The
  `seo_score` and `ai_search_score` families end in `.calculated` on success or `.failed`. The
  `content_score` family fires only `.recalculated`. Some families also add `.cancelled` or
  `.waiting_for_user_input`. These event names are a REST-transport detail. Over MCP the same
  completions arrive as progress notifications.

**Stale-score trap.** After a `content__update`, a score read can return the prior `score` with
`status: calculating`. Trust `score` only when `status` is `ready` and `calculated_at` has advanced
past the pre-mutation value. Capture `calculated_at` before mutating so you can detect the new
calculation.

**Versioning.** Every contract capability is v2. The REST API also exposes legacy `v1` and other
endpoints: audit, SERP analyzer, AI detector, humanizer, locations, editor delete, and permalink
reset. Those are outside this contract. No capability ID binds to them, so do not call them from a
workflow.

## Capability map

The sibling `capability-map.md` binds all 37 contract capability IDs, each with its REST method and
path, workspace scoping, and Live-doc URL. It also holds the *Async operations & polling* reference
for the async ones. `content_score__get` has no single endpoint. It is a composite of the editor
total plus the SEO and AI Search score reads, as the map shows. The MCP-only IDs used by
`surfer-content-recommendations` never get a REST row. Report a capability ID with no row as
unsupported rather than guessing an endpoint. Workflow skills reference IDs, never raw paths.

## Standing rule: fetch the live doc before calling

The capability map gives the method, the path, and where the truth lives. It deliberately omits
request params and response shapes. Before invoking any capability, WebFetch its Live-doc URL,
`https://app.surferseo.com/llms/<resource>.txt`, for the exact params, headers, body schema, and
response shape. The index is `.../llms.txt` and the full reference is `.../llms-full.txt`. These docs
are OpenAPI-generated and authoritative. Never hard-code from memory. If your recollection disagrees
with the live doc, the live doc wins.

## On terminal failure

This transport skill never decides what to do next. It reports the terminal state up to the calling
`surfer-*` workflow skill.

- A `401`, `403`, `quota_exceeded` (`422`), or a `404` on a known-good ID is not retryable here. Stop
  and report it as an auth, billing, or scoping problem.
- A `429`, a `5xx`, or a transient network error gets a bounded retry, reusing the idempotency key on
  creates. Report it if it persists.
- A poll that reaches its hard cap is reported as indeterminate.

## Request shape

A v2 call is the workspace-scoped path plus the auth header. Everything else comes from the Live doc:
params, body, and response shape.

```bash
curl -sS -H "API-KEY: $SURFER_API_KEY" \
  "https://app.surferseo.com/api/v2/workspaces/{workspace_id}/content_editors/{id}"
```
