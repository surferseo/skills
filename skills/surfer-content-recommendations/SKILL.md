---
name: surfer-content-recommendations
description: >-
  Use when the user wants to act on Surfer's site recommendations or run the full content loop.
  Triggers include "what should I optimize next", "turn my Surfer recommendations into articles",
  "find a content opportunity, optimize it, link it, and publish", and "run the write or optimize
  workflow from my workspace". It selects recommendation-led Optimize or Write work, delegates
  drafting and optimization to the focused Surfer skills, and gates the optional internal-linking
  and WordPress actions. Its extension capabilities are MCP-only: REST never runs those stages, and
  any stage the connected server does not expose yet is reported as unavailable.
---

# Surfer: Act on Content Recommendations

## Overview

Turn a chosen, site-level recommendation into one Content Editor workflow, without accidentally
creating it twice or publishing an unreviewed change.

## Extension capabilities

The stages below run on tools planned for the Surfer MCP server that the connected server may not
expose yet, and they are MCP-only by design: the REST transport never binds them. Before every
extension stage, check whether the connected server exposes the exact tool. If it does not, report
the unavailable stage, then either stop or continue with the subset the user approved. Do not
substitute a REST endpoint or a guessed call.

| Capability ID | Contract | Safety requirement |
|---|---|---|
| `workspace__create` | Create a branded workspace from a site URL context. Async: returns the workspace in `processing`; poll `workspace__get` until it leaves that state. | Require the user to choose the organization and site context. |
| `workspace__get` | Read one workspace in any state. | Read-only. |
| `workspace__activate` | Explicitly activate a workspace. Only active workspaces can manage resources. | Activate only a workspace the user chose. |
| `brand__get` | Return the workspace's brand profile, its name and knowledge, and whether it is usable. | Read-only. Do not infer its text from `use_brand_knowledge`. |
| `brand__update` | Replace or patch the approved profile. Return the effective version. | Show the material change before writing it. |
| `recommendation__list` | Return actionable site recommendations filtered by `optimize` or `write`, each with a stable id, priority, and the context needed to act: page URL and keyword for optimize, main keyword and location for write. | Read-only. Do not silently select one. Priorities compare only within one type, not across types. |
| `internal_linking__run` | Start an internal-link suggestion run for a Content Editor against a GSC site context. Async trigger; poll `internal_linking__get`. | Needs a configured Content Audit project. Report its absence instead of guessing a site URL. Makes no content change. |
| `internal_linking__get` | Poll a run: its status, the suggested links with source, target, and anchor, and the updated content once links are inserted. | Read-only. |
| `internal_linking__insert` | Insert the selected suggestions into the run's content. Async; spends an internal-links credit. | Present the exact links and require approval immediately before inserting. |
| `internal_linking__review` | Record the accept-or-reject decision on the inserted result. Accepting persists the linked content into the editor; rejecting writes nothing. | Accepting is the write that changes the document. Confirm before accepting. |
| `wordpress__list_sites` | Return the organization's connected WordPress sites. | Read-only. Never expose credentials or tokens. |
| `wordpress__publish` | Export a completed editor's canonical content to WordPress, as a new post or an update to a given post id, with status `draft` or `publish`. Synchronous, no idempotency key. | Default to a new draft. Require final explicit confirmation before a live publish or before updating an existing post. On a timeout, verify in WordPress before any retry, because a blind retry can double-publish. |

## Playbook

1. **Establish scope.** Resolve an existing active workspace with `workspace__list`. Create one only
   when the user asked for it or none is suitable: call `workspace__create`, poll `workspace__get`
   until the state leaves `processing`, then call `workspace__activate` for the workspace the user
   confirmed. If brand knowledge must be reviewed or changed, read it with `brand__get` first, and
   write it with `brand__update` only with an approved replacement. Do not confuse "enabled for this
   editor" with inspecting the profile.

2. **List, explain, and select a recommendation.** Call `recommendation__list` filtered to
   `optimize` or `write`. Present the relevant URL or keyword, the priority, and the expected
   action. An empty list may mean no source is configured; report which of Content Audit or Topical
   Maps is missing rather than a bare "no recommendations". Let the user choose. Auto-select only
   when the user states a clear rule, such as "highest priority Optimize recommendation", and rank
   within one type only.

3. **Run the focused workflow.** There is no execute step; the recommendation carries everything
   needed to act. For an Optimize recommendation, hand its page URL as the import URL, plus the
   keyword and location, to `surfer-optimize-content`. For a Write recommendation, hand its main
   keyword and location to `surfer-write-article`. Before any create, check `content_editor__list`
   for an editor already covering that page or keyword and reuse it; a create spends a credit, so
   create once with one logical idempotency key.

4. **Propose internal links before changing content.** Start `internal_linking__run` for the editor,
   poll `internal_linking__get` until the suggestions are ready, and show the proposed source pages,
   anchors, and targets. With the user's approval, and only for the links they selected, call
   `internal_linking__insert`, poll until inserted, then present the updated content and record the
   decision with `internal_linking__review`. Accepting the review is what persists the linked
   content into the editor; re-read `content__get` afterward. Rejecting leaves the editor unchanged.

5. **Publish safely.** Fetch the canonical content with `content__get`. Discover connected sites
   with `wordpress__list_sites`. Default `wordpress__publish` to a new draft. Require a final
   explicit confirmation before updating an existing post or page, or before publishing live, even
   when the overall workflow was requested. The call is synchronous with no idempotency key, so on a
   timeout verify the result in WordPress before retrying.

6. **Report the lifecycle.** Return the recommendation selected, the workspace and editor ids, the
   baseline and final score snapshot, the changes made, the inserted links, the WordPress
   destination and status, and every stage skipped because the connected server does not expose its
   tool.
