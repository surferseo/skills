# Claude plugin package

This repository root is the Claude plugin folder. Anthropic's directory reads a committed GitHub folder, so the source for a submission is `surferseo/skills` with the plugin path left empty. The `.claude-plugin/plugin.json` manifest supplies the plugin identity; `.mcp.json` registers Surfer's [documented remote MCP endpoint](https://docs.surferseo.com/en/articles/12944186-surfer-mcp). The root `README.md` and `LICENSE` are part of the folder the directory reads. The plugin has no local server, executable hook, package install, or bundled credential.

Claude automatically loads every skill under the root `skills/` directory. That currently means six content workflows (`surfer-write-article`, `surfer-optimize-content`, `surfer-create-outline`, `surfer-create-content-brief`, `surfer-manage-content-templates`, and `surfer-content-recommendations`) plus the developer-oriented `surfer-connect` and `surfer-api` skills. The latter two remain in the canonical skill collection for CLI users; Claude's manifest `skills` paths add to the default `skills/` scan and cannot exclude individual root skills. A six-skill-only directory package would require a separately committed plugin folder or a source-layout change. Do not describe this root package as containing only six skills.

## Local install and connection

From a checkout of this repository, validate and load the plugin in Claude Code:

```bash
claude plugin validate --strict .
claude --plugin-dir .
```

Inside Claude Code, open `/mcp`, select `surfer`, and authenticate in the browser with a Surfer account. The OAuth connection is handled by Claude and Surfer; it does not require an API key or store OAuth tokens in this package. A Surfer plan or trial with MCP access is required. Confirm the connection with “List my Surfer workspaces”, then try a bounded workflow such as “Create a Surfer outline for [keyword] in [workspace].” Creating a Content Editor or running generation and optimization can consume Surfer plan credits, so review the proposed operation and scope first. [Surfer's MCP guide](https://docs.surferseo.com/en/articles/12944186-surfer-mcp) documents availability and sign-in.

The plugin's packaged MCP server is the primary transport. The `surfer-api` skill is a separate REST fallback for developers who deliberately configure an API key; it is not needed for OAuth sign-in. Because this skill is present in the root package, its environment-key instructions need review under Anthropic's [credential guidance](https://claude.com/docs/plugins/pre-submission-checklist) before directory submission. The MCP server also serves its own dynamic skills; keep those and these committed workflow snapshots compatible when either changes.

## Directory preparation

This file records preparation steps; no directory submission or publication is implied.

1. Use `claude plugin validate --strict .` on the exact commit to be submitted. Run a clean-account sign-in and bounded workflow smoke test in Claude Code, then test the other surfaces the listing will advertise. Local validation checks structure, not directory policy or runtime behavior.
2. In the [Claude developer portal](https://claude.com/docs/plugins/submit), submit this repository as a **Plugin bundle**, using the repository root as the plugin path and an explicit branch or tag. A private repository can be validated and submitted when the connected GitHub account has the required access; it must be public before the listing goes live. Revalidate after each pushed change.
3. Submit Surfer's remote MCP server separately as an **MCP connector** if that connector has not already been submitted. The plugin submission does not replace connector review.
4. Supply verified publisher access, a working reviewer account with sample data, at least three tested use cases, support and privacy links, and accurate data-handling answers. Confirm the final listing text, credential behavior, and credit disclosures against the submitted commit. These organization and server facts cannot be established from this repository alone.
5. Raise the manifest `version` for each release, test the exact new commit, and publish only after the portal's validation, security scan, and review succeed. A passing local `claude plugin validate` result is not directory approval.

No logo is bundled here because no licensed official asset has been verified for redistribution. The plugin uses the established Surfer name and website without inventing a support contact or visual mark.
