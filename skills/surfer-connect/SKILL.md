---
name: surfer-connect
description: >-
  Use when no Surfer transport is usable in this session, or when the user asks to connect, install,
  or set up Surfer. Triggers include "connect the Surfer MCP server", "add Surfer to this client",
  "install Surfer MCP", "set up my Surfer API key", and "how do I authenticate Surfer". It registers
  the remote Surfer MCP server in the current client, one URL plus an OAuth sign-in, or configures
  an API key for the surfer-api REST adapter, then verifies the connection and hands control back to
  the interrupted surfer-* workflow.
license: MIT
---

# Surfer: Connect a Transport

## Overview

Get a usable Surfer transport for this session. The `surfer-*` workflows hand off here when
transport resolution finds nothing usable. Two outcomes are possible: the Surfer MCP server
connected in the client, which is primary, or an API key configured for `surfer-api`, which is
secondary. Prefer MCP unless the user pins REST, the client cannot register MCP servers, or the MCP
path fails on plan or availability.

The MCP server is remote, served over streamable HTTP with OAuth 2.1. Connecting installs nothing:
the client registers one URL and the user completes a browser sign-in.

## Ground rules

- Follow the current client's normal connector flow. Show a manual config edit before making it;
  use the client's secure settings or CLI when available.
- Never write an API key into a file that could be committed. Prefer the client's secret storage or
  an environment variable.
- Use Surfer's documented MCP URL below. Never fabricate an API key or ask the user to paste one
  into chat; direct them to Surfer and their client's secret storage instead.
- OAuth happens in the user's browser. Do not proxy, script, or ask for the credentials behind it.

## MCP path (primary)

The documented connection URL is **https://mcp.surferseo.com/mcp**. See
[Surfer's MCP setup guide](https://docs.surferseo.com/en/articles/12944186-surfer-mcp) and
[developer quickstart](https://devs.surferseo.com/mcp/quickstart). Dispatch on the client actually
running this session; ask which client only if it cannot be detected. If the user's Surfer app
shows a different tenant-specific URL, use that URL after verifying it with the user.

The table is a starting point, not a spec. Client MCP surfaces change faster than this skill, so
before applying a row, verify it against the client's current documentation or the client's own
help — `claude mcp add --help`, `codex mcp --help`, the in-app connector settings — and prefer what
the client itself reports over this table. Handle a client the table does not list the same way:
look up how it registers a remote MCP server rather than declaring it unsupported.

| Client | Starting point |
|---|---|
| Claude Code | Run `claude mcp add --transport http --scope user surfer https://mcp.surferseo.com/mcp`, then have the user run `/mcp` and complete the sign-in. No restart needed. |
| Claude Desktop / claude.ai | Follow Surfer’s current Claude connector guide and add a custom connector with the URL. On Team and Enterprise plans this can require an org admin. Reload afterward. |
| ChatGPT | Follow Surfer’s current ChatGPT plugin guide, choose OAuth, and add the URL. Availability depends on the ChatGPT plan and workspace policy. |
| Codex | Run `codex mcp add surfer --url https://mcp.surferseo.com/mcp`, or add an `[mcp_servers.surfer]` entry with the URL to `~/.codex/config.toml`. |
| Cursor | Add `{"mcpServers": {"surfer": {"url": "<url>"}}}` to `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global). |
| VS Code | Add `{"servers": {"surfer": {"type": "http", "url": "<url>"}}}` to `.vscode/mcp.json`. |
| Anything else | Register a remote, streamable-HTTP MCP server named `surfer` with the URL in the client's MCP settings, then complete the OAuth prompt. |

Some clients load MCP servers only at startup. When that applies, say so, let the user restart, and
expect the task to be re-requested rather than promising to resume this session.

## Verify

Registration alone is not success. Confirm the session lists the Surfer tools, names like
`workspace__list` and `content_editor__create`, and optionally call `server__info` as a no-op
check. If tools are missing after a completed sign-in, re-check the URL and whether the client
needs a restart, and report exactly what is missing.

## API-key path (secondary)

1. Check that `surfer-api` is installed and that the account has REST API access. Surfer documents
   that REST access requires Peace of Mind or Enterprise; the account owner obtains the API key
   through Surfer support. See [Surfer API introduction](https://docs.surferseo.com/en/articles/5700335-surfer-api-introduction).
2. Have the user put the key in the client's secret storage or `SURFER_API_KEY` in their own local
   environment. Do not ask them to paste it into chat or write it into a repository or config file
   that may be committed.
3. Verify with `workspace__list` through `surfer-api`. If the adapter is absent, install it before
   making any REST request; do not improvise a direct HTTP call.
4. From here `surfer-api` owns REST mechanics.

## Plan and availability failures

- The MCP path can return two distinct 403s. A plan-entitlement 403 reads "not available on your
  current plan". A rollout 403 reads "MCP access is not yet enabled for this organization". Report
  to the user which one occurred. Offer REST only if the account already has REST API access.
- On the API-key path, a `401` means the key is missing or wrong; a `403` means the plan or
  permissions deny it. Report the difference rather than retrying in a loop.

## Hand back

Once a transport verifies, return to the workflow that was interrupted and continue from its
transport-resolution step. If the user only asked to connect, report what is now usable and stop.
