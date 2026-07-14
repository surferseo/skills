---
name: surfer-capabilities
description: >-
  Use when you need to understand or execute a Surfer capability ID referenced by a surfer-*
  workflow — e.g. a content_editor.*, seo_guidelines.*, ai_article.*, auto_optimize.*,
  ai_search.*, recommendation.*, brand_knowledge.*, internal_link.*, wordpress.*, audit.*, or
  workspace.* id — and you need the shared, transport-neutral meaning of that id, or you are
  asking "which transport actually runs this capability". This skill defines the contract and
  vocabulary that capability IDs are drawn from: workspace-scoping, idempotency intent, and the
  async model, all phrased independently of any one transport. It does NOT make calls and names no
  endpoint, path, or tool — the active Surfer transport adapter (e.g. the REST adapter behind
  /surfer-api) executes capabilities and owns those details.
license: MIT
---

# Surfer Capabilities (transport-neutral contract)

## Overview

The shared vocabulary every `surfer-*` workflow draws from. It defines *what a capability ID
means* and the always-on semantics that hold no matter how the call is made. It is **not a
resolver and makes no calls** — execution belongs to whichever Surfer transport **adapter** is
active. Read `ports.md` for verified async/poll behavior and `content-workflows.md` for the
semantic setup, score, and extension contracts behind the content-workflow skills.

## 1. The contract rule

- Workflows name **capability IDs only** (e.g. `content_editor.create`, `seo_guidelines.get_score`,
  `ai_article.generate`) — never endpoints, paths, or tool names.
- Every ID is executed through whichever Surfer transport **adapter** is currently active.
- Transports are **interchangeable** and capability IDs are **transport-opaque**: the same ID
  means the same thing regardless of how it travels. Swapping the adapter must not change which
  ID a workflow asks for.

## 2. Transport-neutral always-on semantics

These hold for **all** transports. Workflows assume them and rarely restate them; the active
adapter implements the mechanism.

**Workspace scoping (concept).** Most Surfer resources act **within a workspace**. Before
operating on workspace-scoped resources, resolve an active `workspace_id` via `workspace.list`
and use one that is active. If exactly one is active, use it; if several are, the caller must
supply the `workspace_id` (do not guess); if none are, stop and report. *How* the scope is
carried on the wire is the adapter's concern.

**Idempotency (intent).** A create may be retried (transient failure, backoff, network blip).
Use **one logical idempotency key per logical create**, generated up front and reused on every
retry of that same create, so retries do not double-spend credits or duplicate resources. The
adapter implements the actual mechanism (header, token, dedup, etc.); the workflow's obligation
is only "one key per create, reused on retry".

**Async model (neutral).** Some operations return in a **non-terminal** state and finish later.
To learn the outcome, either await the operation's **named completion event** or **poll the
named GET capability** until it reaches a terminal state. Terminal vocabulary varies by
resource — never assume `completed`. Poll with bounded backoff and a hard cap; on cap, treat the
job as timed-out / indeterminate rather than looping forever.

## 3. Per-ID async/poll table

The mapping of each async capability ID to its named completion event and its poll-via GET
capability (plus the terminal field/value to check) lives in the sibling **`ports.md`**. Consult
it whenever an operation is non-terminal.

`content-workflows.md` registers the deliberately unbound extension IDs required for workspace
setup, recommendations, fresh outline generation, internal links, and WordPress publishing. An
extension is part of the contract but is **not executable** until an active adapter explicitly
reports it as supported and supplies its normalized operation contract. The REST adapter does not
bind those IDs today.

## 4. Normalized operation vocabulary

Adapters may expose native state names, but normalize them for workflows as `pending`, `running`,
`awaiting_input`, `succeeded`, `failed`, `cancelled`, or `indeterminate`. Preserve the resource or
operation id across every wait/retry. `awaiting_input` is not a timeout; surface the decision and
do not continue until it is supplied. `indeterminate` means the bounded observation window ended
without a verified terminal state.

## 5. Transport selection & override (stated once)

**First, determine which adapters are usable in *this session*.** An adapter is usable only if its
skill is activatable here (you can load it) and, where it relies on an external transport, that
transport is connected this session. Files merely present in a source checkout do **not** count as
installed. Apply the rules below only among adapters usable here.

- **No adapter usable** → **stop and ask** the user how Surfer should be run / which transport to
  install or activate (e.g. `/surfer-api`). Do **not** fall back to a default, do **not** hand-write
  HTTP, and do **not** treat a missing credential as the blocker when the real gap is a missing
  transport.
- **Exactly one usable** → use it; no choice to make.
- **Several usable, user has not pinned one** → use the **declared default adapter** (currently
  `surfer-api` — the only adapter today). Only ever select an adapter usable here. When more
  transports are added, set the default/precedence here.
- **Explicit user pin overrides** — e.g. the user activating a specific transport such as
  `/surfer-api`. An explicit pin always wins over the default.
- **Adapter installed but not yet connected** (its underlying transport isn't bound this session)
  → surface the single concrete connect step for *that* adapter and proceed once connected; do not
  present a transport choice and do not silently switch to another adapter.

The **chosen adapter owns** everything mechanical: authentication, error taxonomy, rate limits,
the idempotency mechanism, pagination, native-to-normalized status mapping, and any pre-call
documentation/schema lookup needed before a call. Workflows do not duplicate these.

## 6. Non-goal (explicit)

This skill names **no concrete endpoint, path, method, or tool**, and resolves no ID to one. For
anything concrete — how an ID maps to a call, request/response shapes, auth, errors — the
**active adapter is authoritative**. This file is vocabulary and contract; the adapter is the
mechanism.
