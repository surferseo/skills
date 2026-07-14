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

- Edit a client config file only with the user's approval, and show the exact change first.
- Never write an API key into a file that could be committed. Prefer the client's secret storage or
  an environment variable.
- Never fabricate a server URL or an API key. When a step needs a value only Surfer or the user can
  provide, ask for that one value.
- OAuth happens in the user's browser. Do not proxy, script, or ask for the credentials behind it.

## MCP path (primary)

The connection URL comes from Surfer's MCP documentation or the Surfer app's MCP settings. If it is
not known in this session, ask the user for it rather than guessing. Then dispatch on the client
actually running this session, and ask which client is in use if it cannot be detected.

The table is a starting point, not a spec. Client MCP surfaces change faster than this skill, so
before applying a row, verify it against the client's current documentation or the client's own
help — `claude mcp add --help`, `codex mcp --help`, the in-app connector settings — and prefer what
the client itself reports over this table. Handle a client the table does not list the same way:
look up how it registers a remote MCP server rather than declaring it unsupported.

| Client | Starting point |
|---|---|
| Claude Code | Run `claude mcp add --transport http surfer <url>`, then have the user run `/mcp` and complete the sign-in. No restart needed. |
| Claude Desktop / claude.ai | Settings → Connectors → add a custom connector with the URL. On Team and Enterprise plans this can require an org admin. Reload afterward. |
| ChatGPT | Settings → Connectors → add a custom connector with the URL. Custom MCP connectors may require enabling developer mode under the connector settings, and availability is plan-dependent. |
| Codex | Run `codex mcp add surfer --url <url>`, or add an `[mcp_servers.surfer]` entry with the URL to `~/.codex/config.toml`. |
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

1. The user creates or copies an API key in the Surfer app, under the organization's API settings.
2. Store it where the session can read it, such as a `SURFER_API_KEY` environment variable or the
   client's secret storage, with approval and never in a committed file.
3. Verify with one call through `surfer-api`: `workspace__list` should return the organization's
   workspaces.
4. From here `surfer-api` owns the REST mechanics.

## Plan and availability failures

- An OAuth or consent failure that names the plan means the organization's plan does not include the
  MCP server. Say so and offer the API-key path instead.
- On the API-key path, a `401` means the key is missing or wrong; a `403` means the plan or
  permissions deny it. Report the difference rather than retrying in a loop.

## Hand back

Once a transport verifies, return to the workflow that was interrupted and continue from its
transport-resolution step. If the user only asked to connect, report what is now usable and stop.
