# Surfer Skills

Use Surfer from an AI assistant to create outlines and briefs, write or optimize articles, manage templates, and act on site recommendations. Each skill is a playbook; it needs a connected Surfer transport to read or change your account. The recommended transport is [Surfer MCP](https://docs.surferseo.com/en/articles/12944186-surfer-mcp), with browser based OAuth sign-in.

## Before you start

- Have a Surfer account and an AI assistant that supports remote MCP. Surfer documents MCP access for Pro, Peace of Mind, Enterprise, AI Search Analytics, and trial accounts; your plan limits still apply. Check [Surfer's current MCP requirements](https://docs.surferseo.com/en/articles/12944186-surfer-mcp) for changes.
- For the optional REST route, you need `surfer-api`, an API key, and REST API access. [Surfer's API introduction](https://docs.surferseo.com/en/articles/5700335-surfer-api-introduction) documents Peace of Mind or Enterprise access and explains how the account owner obtains a key. An API key alone does not install the adapter.
- Installing skills does not connect an account. Connect once in your assistant, then verify with a read request.

## Install the skills

Run the [skills CLI](https://skills.sh) in the project where your assistant will use Surfer. The pinned CLI version below makes the commands reproducible. The CLI detects the target agent by default; pass `--agent` when you need to choose one.

```bash
# All eight skills, including setup and REST support
npx skills@1.7.0 add surferseo/skills --skill '*' -y

# One workflow is enough when Surfer MCP is already connected
npx skills@1.7.0 add surferseo/skills --skill surfer-create-outline -y

# A writing workflow with setup and optional REST fallback
npx skills@1.7.0 add surferseo/skills \
  --skill surfer-write-article --skill surfer-connect --skill surfer-api -y
```

You can also [follow the Surfer MCP setup guide](https://docs.surferseo.com/en/articles/12944186-surfer-mcp) without installing this repository's playbooks. Surfer's MCP server supplies its own six workflow skills. Check which version your client invokes if both server supplied and locally installed copies are present.

A single installed workflow contains its essential input defaults and connection guidance. The `surfer-connect` helper and `surfer-api` adapter are separate skills; a workflow installed alone cannot assume either is present. The recommendations skill needs MCP for recommendation and brand calls because REST does not expose them.

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

Start a fresh chat with **“List my Surfer workspaces.”** A list from `workspace__list` confirms the connection without creating content or spending a Content Editor credit. If the tools are absent, check that the connector is enabled in this chat and whether your client needs a restart. If sign-in is refused, check the Surfer account, organization, and plan in the [setup guide](https://docs.surferseo.com/en/articles/12944186-surfer-mcp).

## Try a workflow

- “Create a Surfer outline for *best trail running shoes* in the United States. Stop after the outline.”
- “Make a writer-ready brief for *how to choose a standing desk*. Include source-attributed AI Search facts.”
- “Optimize my existing article for SEO and report its starting and final Content Score.”
- “Show my Surfer content recommendations, then let me choose one.” This needs MCP.

A read such as listing workspaces does not use a Content Editor credit. Creating an editor, generating an AI article, and optimization can consume plan limits or credits. The assistant should disclose the planned operations and wait for user direction where a workflow requires it. A score measures Surfer's coverage criteria; it does not guarantee search rankings or AI citations. See [MCP limits](https://devs.surferseo.com/mcp/credits-and-limits) and [Surfer pricing](https://surferseo.com/pricing/) for current terms.

## Optional REST route

If you explicitly request REST or invoke `/surfer-api`, that choice takes precedence even when MCP is connected. Install both the workflow and `surfer-api`. Configure `SURFER_API_KEY` in your own local environment or the client's secret storage; never paste a key into a chat, a repository, or a file that may be committed. The `surfer-connect` skill can guide setup. Use `workspace__list` through the adapter as a read-only verification call. REST cannot run site recommendations or brand knowledge calls; use MCP for those.

The workflows name Surfer MCP capability IDs. With MCP, the connected tools execute them. With REST, [`surfer-api`](skills/surfer-api/SKILL.md) maps supported IDs to documented methods and paths in its [capability map](skills/surfer-api/capability-map.md). The adapter checks Surfer's live [API documentation index](https://app.surferseo.com/llms.txt) for request and response detail. Its capability map and workflow assumptions are maintained in this repository and may need updates when Surfer changes the API. Run the repository checks before a release; live schema lookup is not an automatic compatibility guarantee.

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

The skills are MIT licensed. The [root license](LICENSE) is copied into each skill folder so an individually installed skill carries its notice.
