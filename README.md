# Surfer Skills

[Agent Skills](https://agentskills.io) for working with [Surfer](https://surferseo.com). These are transport-agnostic content workflows whose capability IDs are the **Surfer MCP server's tool names**. Run them over the MCP server, which is primary, or over the REST API through the `surfer-api` adapter, which is secondary.

Install with the [`skills`](https://skills.sh) CLI:

```bash
# everything
npx skills add surferseo/skills

# or a workflow plus the REST adapter
npx skills add surferseo/skills --skill surfer-write-article --skill surfer-api
```

A workflow on its own can't do anything. It needs a **transport** to run against. The primary transport is the connected **Surfer MCP server**, whose tools are the capability IDs, so no extra skill is required. The secondary transport is the **`surfer-api`** adapter over REST. The skills spec has no hard dependency mechanism, so co-installing `surfer-api` with a workflow is a convention rather than an enforced rule. Running `npx skills add surferseo/skills` with no `--skill` installs everything.

## How it's organized

Two layers:

1. **Workflow skills** are the entrypoints. Each is a transport-agnostic playbook for a real Surfer job. Start here.
2. **Transports** are where a capability ID becomes a real call. The **Surfer MCP server** is primary. Its tools are the IDs and carry their own descriptions. **`surfer-api`** is secondary. It maps each ID to a REST method and path and owns the REST async and poll mechanics.

Workflows reference **capability IDs only** — the MCP server's tool names — never a transport, endpoint, or URL. Whichever transport is connected executes those IDs, and the workflows run unchanged over either.

### Workflow skills — *what you want to do*

| Skill | Use it to… |
|---|---|
| `surfer-write-article` | Turn a keyword or topic into a Surfer AI draft with SEO and AI Search analysis |
| `surfer-optimize-content` | Improve existing content for SEO, AI Search, or both |
| `surfer-create-outline` | Build a Surfer-derived, SERP-informed article outline |
| `surfer-create-content-brief` | Build a writer-ready SEO and AI Search content brief |
| `surfer-manage-content-templates` | Create and manage reusable content templates |

### Transports — *how the calls are made*

The **primary** transport is the **Surfer MCP server**. Connect it, and its tools are the capability
IDs. Each tool carries its own description of inputs, async behavior, and poll target, so no adapter
skill is needed. The **secondary** transport is the REST API, reached through one adapter skill:

| Skill | What it is |
|---|---|
| `surfer-api` | REST adapter. Maps each capability ID to a Surfer REST method and path and owns the REST async and poll mechanics: auth, conventions, endpoints, and polling. Fetches live docs for the exact request and response shapes. |

## Always up to date

`surfer-api` does **not** hard-code endpoint details. Surfer's docs are generated from its OpenAPI spec and published at these URLs:

- the index: `https://app.surferseo.com/llms.txt`
- a per-resource doc: `https://app.surferseo.com/llms/<resource>.txt`
- the full reference: `https://app.surferseo.com/llms-full.txt`

The skill fetches these at runtime, so it tracks the live API with no vendoring or sync step.

## Authentication

Surfer API requests use an `API-KEY` header. v2 resources are scoped to a workspace under `/api/v2/workspaces/{workspace_id}/...`. See `surfer-api` for details, and use `GET /api/v2/workspaces` to find your workspace id.

## License

MIT. See [LICENSE](./LICENSE).
