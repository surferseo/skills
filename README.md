# Surfer Skills

[Agent Skills](https://agentskills.io) for working with [Surfer](https://surferseo.com) — content workflows built on top of the Surfer REST API.

Install with the [`skills`](https://skills.sh) CLI:

```bash
# everything
npx skills add surferseo/skills

# or pick specific skills
npx skills add surferseo/skills --skill surfer-write-article --skill surfer-api
```

## How it's organized

Two layers. **Workflow skills are the entrypoints** — start there. They each encode a playbook for a real Surfer job and delegate the actual API calls to a **transport skill**.

### Workflow skills — *what you want to do*

| Skill | Use it to… |
|---|---|
| `surfer-write-article` | Turn a keyword/topic into an SEO-optimized draft, end to end |
| `surfer-optimize-content` | Improve existing content toward a target SEO score |
| `surfer-serp-research` | Analyze the SERP / keywords and plan content |
| `surfer-ai-search` | Optimize content for AI-search / LLM visibility (AIO) |
| `surfer-detect-humanize` | Detect AI-written text and humanize it |

### Transport skills — *how the calls are made*

| Skill | What it is |
|---|---|
| `surfer-api` | The Surfer REST API: auth, conventions, and a capability → endpoint map. Fetches live docs for exact request/response shapes. |

> An MCP transport (`surfer-mcp`) is planned. Workflow skills are transport-agnostic and will work with it unchanged.

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
