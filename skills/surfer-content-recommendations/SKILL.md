---
name: surfer-content-recommendations
description: >-
  Use when the user wants to act on Surfer's site recommendations or run the full content loop.
  Triggers include "what should I optimize next", "turn my Surfer recommendations into articles",
  "find a content opportunity, optimize it, link it, and publish", and "run the write or optimize
  workflow from my workspace". It selects recommendation-led Optimize or Write work, delegates
  drafting and optimization to the focused Surfer skills, and gates the optional internal-link and
  WordPress actions. It requires a transport that supports the recommendation and publishing
  extension capabilities. REST alone cannot run those stages.
---

# Surfer: Act on Content Recommendations

## Overview

Turn a chosen, site-level recommendation into one Content Editor workflow, without accidentally
creating it twice or publishing an unreviewed change.

## Extension capabilities

This workflow runs on capabilities that are not MCP tools or REST endpoints yet, so no transport
binds them today. This skill owns their contract. Before every extension stage, ask the active
transport whether it supports the exact capability. If it does not, report the unavailable stage.
Then either stop or continue with the subset the user approved. Do not treat `surfer-api` as an
implementation of these IDs.

| Capability ID | Contract | Safety requirement |
|---|---|---|
| `workspace__create` | Create a branded workspace from a name, site or GSC context, location, language, and members. Return its active `workspace_id`. | Require the user to choose the organization and site context. |
| `brand_knowledge__get` | Return the single brand profile for a workspace and whether it is usable. | Read-only. Do not infer its text from `use_brand_knowledge`. |
| `brand_knowledge__update` | Replace or patch the approved profile. Return the effective version. | Show the material change before writing it. |
| `recommendation__list` | Return actionable site recommendations filtered by `optimize` or `write`, each with a stable id, rationale, priority, and URL or keyword context. | Read-only. Do not silently select one. |
| `recommendation__execute` | Start the chosen recommendation. Return its accepted action, plus a `content_editor_id` when one was created. | Treat it as credit-spending if it creates an editor. Never create a duplicate editor. |
| `internal_link__suggest` | Return candidate internal links with source page, target, anchor, location, and rationale. | Require connected site or GSC context. Make no content change. |
| `internal_link__apply` | Apply only selected link suggestions to a named Content Editor. | Present the exact changes and require approval immediately before applying. |
| `wordpress__list_destinations` | Return connected WordPress sites and writable post or page destinations. | Read-only. Do not expose or inspect credentials. |
| `wordpress__publish` | Export a named editor's canonical content to a WordPress draft, an existing item, or a live item. Return its URL and status. | Default to a new draft. Require final explicit confirmation before a live publish or before updating an existing published item. |

## Playbook

1. **Establish scope.** Resolve an existing active workspace with `workspace__list`. Create a new
   workspace only when the user asked for one or none is suitable. If brand knowledge must be
   reviewed or changed, use `brand_knowledge__get` first, and use `brand_knowledge__update` only with
   an approved replacement. Do not confuse "enabled for this editor" with inspecting the profile.

2. **List, explain, and select a recommendation.** Call `recommendation__list` filtered to `optimize`
   or `write`. Present the relevant URL or keyword, the rationale, the priority, and the expected
   action. Let the user choose. Auto-select only when the user states a clear rule, such as "highest
   priority Optimize recommendation."

3. **Execute once.** Call `recommendation__execute` for the chosen recommendation. It must return the
   accepted action, and when it creates a Content Editor, its `content_editor_id` and workspace.
   Treat that editor as the workflow resource. Do not call `content_editor__create` again for the
   same recommendation. If no editor is returned, ask before creating one, because it may consume a
   second credit.

4. **Run the focused workflow.** For an Optimize recommendation, hand the returned editor and URL
   context to `surfer-optimize-content`. For a Write recommendation, hand the editor and keyword
   context to `surfer-write-article`. Preserve the chosen brand, template, instructions, and
   competitor decisions. Do not force a second setup wizard.

5. **Propose internal links before changing content.** Use `internal_link__suggest`, show the
   proposed source pages, anchor text, and target placement, then apply only the links the user
   approves with `internal_link__apply`. Require a connected site or GSC context, and explain if it
   is absent.

6. **Publish safely.** Fetch the canonical content with `content__get`. Discover connected targets
   with `wordpress__list_destinations`. Default `wordpress__publish` to a new draft. Require a final
   explicit confirmation before updating an existing published post or page, or before making any
   post or page live, even when the overall workflow was requested.

7. **Report the lifecycle.** Return the recommendation selected, the workspace and editor ids, the
   baseline and final score snapshot, the changes made, the accepted internal links, the WordPress
   destination and status, and every stage skipped because its capability was unsupported.
