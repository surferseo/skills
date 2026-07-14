---
name: surfer-capabilities
description: >-
  Use when a surfer-* workflow names a Surfer capability ID and you need its shared,
  transport-neutral meaning, or when you are choosing which transport runs a capability. Capability
  IDs are the Surfer MCP server's tool names, such as content_editor__*, content__*,
  content_score__*, seo_guidelines__*, ai_search_guidelines__*, ai_article__*, auto_optimize__*,
  outline__*, recommendation__*, brand_knowledge__*, internal_link__*, wordpress__*, and
  workspace__*. This skill defines the contract they are drawn from: workspace scoping, idempotency,
  the async model, and how a transport is chosen. It makes no calls and names no endpoint, path, or
  method. The active transport (for example the REST adapter behind /surfer-api) executes
  capabilities and owns those details.
license: MIT
---

# Surfer Capabilities (transport-neutral contract)

## Overview

Every `surfer-*` workflow draws its vocabulary from here. This skill defines the always-on
semantics that hold however a call is made, and the rules for choosing a transport. Capability IDs
are exactly the Surfer MCP server's tool names, such as `content_editor__create`. That curated tool
surface is the contract. The skill makes no calls. It also does not restate what each capability
does: for a capability's inputs, async behavior, and status values, the authoritative source is the
MCP tool's own description over MCP, or `surfer-api`'s `capability-map.md` over REST. Read
`content-workflows.md` for the shared setup vocabulary and the registry of extension capabilities
that are not yet tools.

## 1. The contract rule

- Workflows name capability IDs only, which are the MCP tool names such as `content_editor__create`,
  `content_score__get`, and `ai_article__generate`. They never name a REST endpoint, path, or method.
- Every ID runs through whichever Surfer transport is active. Over MCP the ID is the tool to call
  directly. Over REST the adapter maps it to a method and path.
- Transports are interchangeable. The same ID means the same thing over any transport, so swapping
  the transport must not change which ID a workflow asks for.

## 2. Transport-neutral always-on semantics

These hold for all transports. Workflows assume them and rarely restate them. The active transport
implements the mechanism.

**Workspace scoping.** Most Surfer resources act within a workspace. Before operating on one,
resolve an active `workspace_id` with `workspace__list`. If exactly one workspace is active, use it.
If several are active, ask the caller for the `workspace_id` rather than guessing. If none are
active, stop and report. How the scope travels on the wire is the transport's concern.

**Idempotency.** A create may be retried after a transient failure or network blip. Use one logical
idempotency key per logical create. Generate it up front and reuse it on every retry of that create,
so retries do not double-spend credits or duplicate resources. The transport implements the
mechanism. The workflow's only obligation is one key per create, reused on retry.

**Async model.** Some operations return in a non-terminal state and finish later. To learn the
outcome, poll the named GET capability until it reaches a terminal state. A transport may also push a
completion signal so a waiter need not poll. The MCP transport streams progress notifications while
it holds the call open for a progress-token client, and the REST transport posts webhooks to a
registered endpoint. That push channel is transport-specific, so polling is always valid. Terminal
vocabulary varies by resource, so never assume `completed`. Poll with bounded backoff and a hard cap.
On reaching the cap, report the job as timed out rather than looping forever.

## 3. Where per-ID semantics live

This contract carries no per-ID async/poll table, because that would duplicate the transport. When
an operation is non-terminal, read its poll target and terminal values from the active transport:

- Over the MCP server (primary), read the tool's own description. It states whether the tool is
  async, which tool to poll, and the terminal state.
- Over REST, read the *Async operations & polling* section of `surfer-api`'s `capability-map.md`.

`content-workflows.md` registers the extension IDs for the Notion "Future" full workflow: workspace
setup, brand-knowledge management, recommendations, internal links, and WordPress publishing. These
are not MCP tools yet, so nothing else documents them. An extension belongs to the contract. It is
not executable until an active transport reports it as supported and supplies its normalized
operation contract. Neither transport binds those IDs today.

## 4. Normalized operation vocabulary

A transport may expose native state names. Normalize them for workflows as `pending`, `running`,
`awaiting_input`, `succeeded`, `failed`, `cancelled`, or `indeterminate`. Preserve the resource or
operation id across every wait and retry. `awaiting_input` is not a timeout. Surface the decision
and wait until the user supplies it. `indeterminate` means the bounded observation window closed
without a verified terminal state.

## 5. Transport selection and override

First, determine which Surfer transports are usable in *this session*. Two exist:

- The Surfer MCP server is primary. It is usable when its tools are connected this session, and its
  tool names are the capability IDs, called directly.
- `surfer-api` is the secondary, REST transport. It is usable when the skill is loaded and an API key
  is available.

Files merely present in a source checkout do not count as connected or installed. Apply these rules
among the transports usable here:

- If both are usable and the user has not pinned one, use the MCP server.
- If exactly one is usable, use it.
- If neither is usable, stop and ask the user how Surfer should be run: connect the Surfer MCP
  server, or install and authenticate `/surfer-api`. Do not fall back to hand-written HTTP, and do
  not treat a missing credential as the blocker when the real gap is a missing transport.
- An explicit transport pin wins over the primary default. Pinning `/surfer-api` forces REST.
- If a transport is present but not connected, surface the one concrete connect step and proceed once
  it is connected. The MCP tools may be absent this session, or `surfer-api` may have no API key. Do
  not present a transport choice and do not silently switch.

The chosen transport owns everything mechanical: authentication, error taxonomy, rate limits, the
idempotency mechanism, pagination, native-to-normalized status mapping, and any documentation or
schema lookup needed before a call. Workflows do not duplicate these.

## 6. Non-goal

Capability IDs are the MCP tool names, but this skill resolves no ID to a concrete transport call. It
names no REST endpoint, path, method, or request and response shape. For anything concrete, such as
how an ID maps to a call, its request and response shapes, auth, or errors, the active transport is
authoritative. This file holds the vocabulary and the contract. The transport is the mechanism.
