# Surfer Skills

Use Surfer from an AI assistant to create outlines and briefs, write or optimize articles, manage templates, and act on site recommendations. Connect your Surfer account through [Surfer MCP](https://docs.surferseo.com/en/articles/12944186-surfer-mcp) using browser sign-in.

## Before you start

- Have a Surfer account and an AI assistant that supports remote MCP. Surfer documents MCP access for Pro, Peace of Mind, Enterprise, AI Search Analytics, and trial accounts; your plan limits still apply. Check [Surfer's current MCP requirements](https://docs.surferseo.com/en/articles/12944186-surfer-mcp) for changes.
- For the optional REST route, you need `surfer-api`, an API key, and REST API access. [Surfer's API introduction](https://docs.surferseo.com/en/articles/5700335-surfer-api-introduction) documents Peace of Mind or Enterprise access and explains how the account owner obtains a key. An API key alone does not install the adapter.
- Installing skills does not connect an account. Connect once in your assistant, then verify with a read request.

## Install the skills

Run the [skills CLI](https://skills.sh) in the project where your assistant will use Surfer. It detects your installed assistants; use `--agent` to select a specific one.

```bash
# All eight skills, including setup and REST support
npx skills add surferseo/skills --skill '*' -y

# One workflow is enough when Surfer MCP is already connected
npx skills add surferseo/skills --skill surfer-create-outline -y

# A writing workflow with setup and optional REST fallback
npx skills add surferseo/skills \
  --skill surfer-write-article --skill surfer-connect --skill surfer-api -y
```

You can also [follow the Surfer MCP setup guide](https://docs.surferseo.com/en/articles/12944186-surfer-mcp) without installing this repository's playbooks. Surfer's MCP server supplies its own six workflow skills. Check which version your client invokes if both server supplied and locally installed copies are present.

With MCP connected, you can install any workflow on its own. Add `surfer-connect` if you need help connecting your account. For REST access, also install `surfer-api`. Content recommendations require MCP.

## Connect and verify with OAuth

The documented remote MCP endpoint is **`https://mcp.surferseo.com/mcp`**. Register it in your assistant, then sign in to Surfer in the browser. Use the current [Surfer client setup guide](https://docs.surferseo.com/en/articles/12944186-surfer-mcp) or [developer quickstart](https://devs.surferseo.com/mcp/quickstart) for your client. For example:

```bash
# Claude Code: user-wide connection
claude mcp add --transport http --scope user surfer https://mcp.surferseo.com/mcp
# Then run /mcp in Claude Code and authenticate.

# Codex CLI
codex mcp add surfer --url https://mcp.surferseo.com/mcp
# If needed, run: codex mcp login surfer
```

In Claude, ChatGPT, Cursor, and other MCP clients, add a remote HTTP connector named Surfer using that URL and choose OAuth. Complete sign-in in the browser and select the right Surfer organization. Connection controls and plan availability vary by client; follow Surfer's current guide for its exact interface.

Start a fresh chat with **“List my Surfer workspaces.”** Seeing your workspaces confirms the connection without creating content or spending a Content Editor credit. If the tools are absent, check that the connector is enabled in this chat and whether your client needs a restart. If sign-in is refused, check the Surfer account, organization, and plan in the [setup guide](https://docs.surferseo.com/en/articles/12944186-surfer-mcp).

## Try a workflow

- “Create a Surfer outline for *best trail running shoes* in the United States. Stop after the outline.”
- “Make a writer-ready brief for *how to choose a standing desk*. Include source-attributed AI Search facts.”
- “Optimize my existing article for SEO and report its starting and final Content Score.”
- “Show my Surfer content recommendations, then let me choose one.” This needs MCP.

A read such as listing workspaces does not use a Content Editor credit. Creating an editor, generating an AI article, and optimization can consume plan limits or credits. A score measures Surfer's coverage criteria; it does not guarantee search rankings or AI citations. See [MCP limits](https://devs.surferseo.com/mcp/credits-and-limits) and [Surfer pricing](https://surferseo.com/pricing/) for current terms.

## Optional REST route

If you explicitly request REST or invoke `/surfer-api`, that choice takes precedence even when MCP is connected. Install both the workflow and `surfer-api`. Configure `SURFER_API_KEY` in your own local environment or the client's secret storage; never paste a key into a chat, a repository, or a file that may be committed. The `surfer-connect` skill can guide setup. Ask the assistant to list your workspaces to verify the connection. REST cannot run site recommendations or brand knowledge calls; use MCP for those.

See [`surfer-api`](skills/surfer-api/SKILL.md) for supported REST operations and setup details.

## Skills in this repository

| Skill | Job |
|---|---|
| `surfer-write-article` | Generate an AI article from a keyword or topic |
| `surfer-optimize-content` | Improve existing content for SEO, AI Search, or both |
| `surfer-create-outline` | Produce a SERP informed outline without a draft |
| `surfer-create-content-brief` | Assemble a writer brief with SEO and AI Search guidance |
| `surfer-manage-content-templates` | Manage reusable content templates |
| `surfer-content-recommendations` | Act on site recommendations; MCP required for discovery |
| `surfer-connect` | Set up and verify MCP or REST access |
| `surfer-api` | REST adapter and capability map |

## Help, privacy, and license

For Surfer account, plan, or connection issues, use the [Surfer help center](https://docs.surferseo.com/) or the support contact in the [MCP guide](https://docs.surferseo.com/en/articles/12944186-surfer-mcp). Read the [Surfer customer privacy policy](https://surferseo.com/legal/privacy-policy-customers/) before submitting account content. Repository issues can be filed in [GitHub Issues](https://github.com/surferseo/skills/issues).

MIT licensed. See [LICENSE](LICENSE).
