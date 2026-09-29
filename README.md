# Surfer Skills

Skills for using [Surfer](https://surferseo.com) in your AI assistant: write and optimize articles, create outlines and briefs, manage templates, and act on content recommendations. Connect through [Surfer MCP](https://devs.surferseo.com/mcp/overview).

## Install

Use the [skills CLI](https://skills.sh) in your project:

```bash
# All skills, including connection setup
npx skills add surferseo/skills --skill '*' -y

# One workflow, when Surfer is already connected
npx skills add surferseo/skills --skill surfer-create-outline -y
```

## Connect

Ask your assistant to use [`surfer-connect`](skills/surfer-connect/SKILL.md) for account setup, client-specific instructions, and connection problems. If you installed only a workflow, add `surfer-connect` when you need setup help.

You need a Surfer account with MCP access. Content creation and optimization may consume Surfer credits.

## Skills

| Skill | Use it to |
|---|---|
| `surfer-write-article` | Generate an article from a keyword or topic |
| `surfer-optimize-content` | Improve existing content for SEO, AI Search, or both |
| `surfer-create-outline` | Create a SERP-informed outline |
| `surfer-create-content-brief` | Prepare a writer-ready content brief |
| `surfer-manage-content-templates` | Manage reusable content templates |
| `surfer-content-recommendations` | Act on site recommendations |
| `surfer-connect` | Set up and verify your connection |

Try: “Create a Surfer outline for best trail running shoes. Stop after the outline.”

For account help, visit the [Surfer help center](https://docs.surferseo.com/). MIT licensed; see [LICENSE](LICENSE).
