# Surfer Skills

[Agent Skills](https://agentskills.io) for working with [Surfer](https://surferseo.com) — transport-agnostic content workflows backed by a capability contract and pluggable transport adapters (REST today; the structure is ready for additional transports).

Install with the [`skills`](https://skills.sh) CLI:

```bash
# everything
npx skills add surferseo/skills

# or a workflow + the contract + at least one adapter
npx skills add surferseo/skills --skill surfer-write-article --skill surfer-capabilities --skill surfer-api
```

A workflow on its own can't do anything — it needs the **capability contract** (`surfer-capabilities`) plus **at least one transport adapter** (e.g. `surfer-api`). The skills spec has no hard dependency mechanism, so this co-install is a **convention**, not something enforced for you. `npx skills add surferseo/skills` (no `--skill`) sidesteps it by installing everything.

## How it's organized

Three layers:

1. **Workflow skills** — the entrypoints. Each is a transport-agnostic playbook for a real Surfer job. Start here.
2. **`surfer-capabilities`** — the transport-neutral capability **contract** every workflow draws from: stable capability IDs plus the async/poll semantics that govern them.
3. **Transport adapters** — bind capability IDs to a concrete transport: `surfer-api` (REST) today. New transports plug in as additional adapters without touching workflows.

Workflows reference **capability IDs only** — never a transport, endpoint, or URL. Whichever adapter is installed and active executes those IDs. Add or swap a transport adapter and the workflows run unchanged.

### Workflow skills — *what you want to do*

| Skill | Use it to… |
|---|---|
| `surfer-write-article` | Turn a keyword/topic into an SEO-optimized draft, end to end |
| `surfer-optimize-content` | Improve existing content toward a target SEO score |
| `surfer-serp-research` | Analyze the SERP / keywords and plan content |
| `surfer-ai-search` | Optimize content for AI-search / LLM visibility (AIO) |
| `surfer-detect-humanize` | Detect AI-written text and humanize it |

### Capability contract — *what can be done*

| Skill | What it is |
|---|---|
| `surfer-capabilities` | The transport-neutral contract: capability IDs and their async/poll semantics. Every workflow targets these IDs; every adapter implements them. |

### Transport adapters — *how the calls are made*

| Skill | What it is |
|---|---|
| `surfer-api` | REST adapter. Maps capability IDs to the Surfer REST API: auth, conventions, endpoints. Fetches live docs for exact request/response shapes. |

> New transports plug in here as additional adapters — each implements the same capability contract, so workflows (and the contract) work with them unchanged.

## Always up to date

`surfer-api` does **not** hard-code endpoint details. Surfer's docs are generated from its OpenAPI spec and published at:

- `https://app.surferseo.com/llms.txt` — index
- `https://app.surferseo.com/llms/<resource>.txt` — per resource
- `https://app.surferseo.com/llms-full.txt` — full reference

The skill fetches these at runtime, so it tracks the live API with no vendoring or sync step.

## Authentication

Surfer API requests use an `API-KEY` header. v2 resources are scoped to a workspace (`/api/v2/workspaces/{workspace_id}/...`). See `surfer-api` for details; use `GET /api/v2/workspaces` to find your workspace id.

## License

MIT — see [LICENSE](./LICENSE).
