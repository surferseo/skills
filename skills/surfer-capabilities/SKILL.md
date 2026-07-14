---
name: surfer-capabilities
description: >-
  Use to resolve which Surfer transport runs a capability, or to understand a capability ID's
  shared, transport-neutral meaning. Capability IDs are the Surfer MCP server's tool names, such as
  content_editor__*, content__*, content_score__*, seo_guidelines__*, ai_search_guidelines__*,
  ai_article__*, outline__*, and workspace__*. This is the transport-neutral contract the surfer-*
  workflows draw from: it picks the transport (the MCP server, or the surfer-api REST adapter), fixes
  the capability IDs, and defines the normalized outcome vocabulary. It makes no calls; for what a
  specific capability does, read the MCP tool description or surfer-api. An explicit transport pin
  such as /surfer-api takes precedence.
license: MIT
---

# Surfer Capabilities (transport-neutral contract)

## Overview

The transport-neutral layer the `surfer-*` workflows sit on. It does three jobs: it fixes what a
capability ID is, it chooses the transport that runs it, and it defines the normalized outcome words
both transports report in. It makes no calls and states no per-ID mechanics. For what a specific
capability does (its inputs, async behavior, and status values), read the MCP tool's own description
over MCP, or `surfer-api`'s `capability-map.md` over REST.

## 1. Capability IDs

- Capability IDs are exactly the Surfer MCP server's tool names, such as `content_editor__create`
  and `content_score__get`.
- Workflows name capability IDs only. They never name a REST endpoint, path, or method.
- The same ID means the same thing on every transport. Over MCP it is the tool to call directly.
  Over REST the `surfer-api` adapter maps it to a method and path.
- Some capabilities the full workflow needs are not tools yet: workspace creation, brand-knowledge
  management, recommendations, internal links, and WordPress publishing. `surfer-content-recommendations`
  owns those extension capabilities and their safety gates. No transport binds them today.

## 2. Transport selection

Determine which Surfer transports are usable in *this session*. Two exist:

- The Surfer MCP server is primary. It is usable when its tools are connected this session, and its
  tool names are the capability IDs, called directly.
- `surfer-api` is the secondary, REST transport. It is usable when the skill is loaded and an API key
  is available.

Files merely present in a source checkout do not count as connected or installed. Then:

- If both are usable and the user has not pinned one, use the MCP server.
- If exactly one is usable, use it.
- If neither is usable, stop and ask the user how Surfer should be run: connect the Surfer MCP
  server, or install and authenticate `/surfer-api`. Do not fall back to hand-written HTTP, and do
  not treat a missing credential as the blocker when the real gap is a missing transport.
- An explicit transport pin wins over the primary default. Pinning `/surfer-api` forces REST.
- If a transport is present but not connected, surface the one concrete connect step and proceed once
  it is connected. Do not present a transport choice and do not silently switch.

The chosen transport owns everything mechanical: authentication, workspace scoping on the wire,
idempotency, the async/poll or webhook mechanics, error taxonomy, rate limits, pagination, and any
schema lookup before a call. Workflows and this contract do not restate those.

## 3. Cross-transport rules

These hold on every transport, so workflows assume them.

**Workspace scoping.** Most resources act within a workspace. Resolve an active `workspace_id` with
`workspace__list` first. If exactly one workspace is active, use it. If several are active, ask the
caller which one rather than guessing. If none are active, stop and report.

**Waiting on async work.** An async operation returns non-terminal and finishes later. Poll the GET
the transport names, with bounded backoff and a hard cap. Never assume the terminal value is
`completed`; it varies by resource. On reaching the cap, report the job as `indeterminate` rather
than looping.

**Normalized outcomes.** A transport may expose native state names. Normalize them for workflows as
`pending`, `running`, `awaiting_input`, `succeeded`, `failed`, `cancelled`, or `indeterminate`.
Preserve the resource or operation id across every wait and retry. `awaiting_input` is not a timeout.
Surface the decision and wait for the user. `indeterminate` means the bounded window closed without a
verified terminal state.
