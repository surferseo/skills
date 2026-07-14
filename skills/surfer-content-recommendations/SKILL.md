---
name: surfer-content-recommendations
description: >-
  Use when the user wants to act on Surfer's site recommendations or run the full content loop —
  e.g. "what should I optimize next", "turn my Surfer recommendations into articles", "find a
  content opportunity, optimize it, link it, and publish", or "run the write/optimize workflow
  from my workspace". Selects recommendation-led Optimize or Write work, delegates drafting and
  optimization to the focused Surfer skills, and safely gates optional internal-link and WordPress
  actions. Requires an adapter that supports the recommendation and publishing extension
  capabilities; REST alone cannot perform those stages.
---

# Surfer: Act on Content Recommendations

## Overview

Turn a chosen, site-level recommendation into one Content Editor workflow without accidentally
creating it twice or publishing an unreviewed change.

## Capability boundary

The following capability IDs are registered in `surfer-capabilities` as adapter extensions:

| Stage | Capability IDs |
|---|---|
| Create and brand a workspace | `workspace.create`, `brand_knowledge.get`, `brand_knowledge.update` |
| Select and launch work | `recommendation.list`, `recommendation.execute` |
| Finalize content | `internal_link.suggest`, `internal_link.apply`, `wordpress.list_destinations`, `wordpress.publish` |

Before every extension stage, ask the active adapter whether it supports the exact capability. If
it does not, report the unavailable stage and either stop or continue with the user-approved
callable subset. Do not treat `surfer-api` as an implementation of these extension IDs.

## Playbook

1. **Establish scope.** Resolve an existing active workspace with `workspace.list`. Create a new
   workspace only when the user asked for one or none is suitable. If brand knowledge must be
   reviewed or changed, use `brand_knowledge.get` first and `brand_knowledge.update` only with an
   approved replacement; do not confuse "enabled for this editor" with inspecting the profile.

2. **List, explain, and select a recommendation.** Call `recommendation.list` filtered to
   `optimize` or `write`. Present the relevant URL or keyword, rationale, priority, and expected
   action. Let the user choose; only auto-select when the user states a clear rule such as
   "highest priority Optimize recommendation."

3. **Execute once.** Call `recommendation.execute` for the chosen recommendation. It must return
   the accepted action and, when it creates a Content Editor, its `content_editor_id` and
   workspace. Treat that editor as the workflow resource; do not call `content_editor.create`
   again for the same recommendation. If no editor is returned, ask before creating one because
   it may consume a second credit.

4. **Run the focused workflow.** For an Optimize recommendation, hand the returned editor and URL
   context to `surfer-optimize-content`. For a Write recommendation, hand the editor and keyword
   context to `surfer-write-article`. Preserve chosen brand, template, instructions, and
   competitor decisions; do not force a second setup wizard.

5. **Propose internal links before changing content.** Use `internal_link.suggest`, show the
   proposed source pages, anchor text, and target placement, then apply only the links the user
   approves through `internal_link.apply`. Require a connected site/GSC context and explain if it
   is absent.

6. **Publish safely.** Fetch the canonical content with `content_editor.get_content`; discover
   connected targets through `wordpress.list_destinations`. Default `wordpress.publish` to a new
   draft. Require a final explicit confirmation to update an existing published post/page or to
   make any post/page live, even if the overall workflow was requested.

7. **Report the lifecycle.** Return the recommendation selected, workspace/editor ids, baseline
   and final score snapshot, changes made, accepted internal links, WordPress destination/status,
   and every stage skipped because its capability was unsupported.
