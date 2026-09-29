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

Set up a usable Surfer connection, verify it, and return to the interrupted workflow. Preserve
an explicit MCP or REST choice from the caller; prefer MCP when neither was selected.

## MCP setup

Use the [Surfer MCP overview](https://devs.surferseo.com/mcp/overview) and
[quickstart](https://devs.surferseo.com/mcp/quickstart) as the source of truth for requirements.
Detect the current client and read its guide before configuring it; ask which client only when
it cannot be determined. Follow that guide's current endpoint, sign-in, and verification steps.

| Client | Setup guide |
|---|---|
| Claude Code | https://devs.surferseo.com/mcp/connect/claude-code |
| Claude web or desktop | https://devs.surferseo.com/mcp/connect/claude |
| ChatGPT web | https://devs.surferseo.com/mcp/connect/chatgpt-web |
| ChatGPT desktop (Work) | https://devs.surferseo.com/mcp/connect/chatgpt-desktop |
| Codex CLI or IDE | https://devs.surferseo.com/mcp/connect/codex |
| Cursor | https://devs.surferseo.com/mcp/connect/cursor |
| VS Code | https://devs.surferseo.com/mcp/connect/vs-code |
| Other clients | https://devs.surferseo.com/mcp/connect/other |

Use the client's normal connector settings or CLI. Show a manual configuration edit before
applying it. The user completes OAuth in their browser; never request their sign-in credentials.

## REST setup

1. Ensure `surfer-api` is installed. Use the [Surfer API introduction](https://docs.surferseo.com/en/articles/5700335-surfer-api-introduction)
   for current account eligibility and how to obtain an API key.
2. Have the user configure the key in client secret storage or `SURFER_API_KEY` in their local
   environment. Never ask them to paste it into chat or write it into a repository.
3. Verify through `surfer-api` with `workspace__list`; leave request mechanics to that adapter.

## Verify and return

For MCP, confirm that Surfer tools are available and `workspace__list` succeeds. Registration
alone is not success; if a restart is required, report setup as pending until the tools are usable.
For REST, an authenticated `workspace__list` through `surfer-api` verifies the connection.

For MCP connection errors, follow [troubleshooting](https://devs.surferseo.com/mcp/troubleshooting);
for MCP access or quota issues, consult [credits and limits](https://devs.surferseo.com/mcp/credits-and-limits).
For REST, report a `401` as missing or invalid credentials and a `403` as an access problem.
Offer another transport only when available, and preserve an explicit user choice.

After verification, resume the interrupted workflow from transport resolution. If the user only
asked to connect, report what is usable and stop.
