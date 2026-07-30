---
name: surfer-content-recommendations
description: >-
  Use when the user wants to act on Surfer's site recommendations or run the full content loop.
  Triggers include "what should I optimize next", "turn my Surfer recommendations into articles",
  "find a content opportunity, optimize it, link it, and publish", and "run the write or optimize
  workflow from my workspace". It selects recommendation-led Optimize or Write work, delegates
  drafting and optimization to the focused Surfer skills, and gates the optional internal-linking
  and WordPress actions. Its stages run on MCP-only tools: REST never runs them, and any stage the
  connected server does not expose yet is reported as unavailable.
---

# Surfer: Act on Content Recommendations

## Overview

Turn a chosen, site-level recommendation into one Content Editor workflow, without accidentally
creating it twice or publishing an unreviewed change.

## MCP-only stages

The workspace-setup, brand, recommendation, internal-linking, and WordPress stages run on MCP-only
tools: the REST API does not expose them, no capability-map row ever binds them, and `surfer-api`
never runs them. With no Surfer MCP server connected, report those stages as unavailable rather
than substituting a REST endpoint or a guessed call. The delegated `surfer-optimize-content` and
`surfer-write-article` runs use either transport as usual.

The workspace tools (`workspace__create`, `workspace__get`, `workspace__activate`), the brand tools
(`brand__get`, `brand__update`), and the recommendation tools (`recommendation__list`,
`recommendation__optimize`) are live on the MCP server and carry their own contracts. The
internal-linking and WordPress tools below are planned and may not be exposed yet. Before each of
those stages, check whether the connected server exposes the exact tool. If it does not, report the
unavailable stage, then either stop or continue with the subset the user approved.

| Capability ID | Contract | Safety requirement |
|---|---|---|
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

2. **List, explain, and select a recommendation.** Call `recommendation__list`, filtered with
   `type` when the user already chose `optimize` or `write` work. Present each candidate's page URL
   or keyword and its `score`. Scores order items within one type and are not comparable across
   types; the default ordering lists optimize items before write items, each block score-descending.
   An item whose `content_editor_id` is set is already being worked on, so offer to continue it
   rather than start over. An empty list may mean no source is configured:
   `meta.content_audit_configured` and `meta.topical_maps_configured` name which of Content Audit
   or Topical Maps is missing, so report that rather than a bare "no recommendations". Let the user
   choose. Auto-select only when the user states a clear rule, such as "highest-score optimize
   recommendation", and rank within one type only.

3. **Run the focused workflow.** The recommendation carries everything needed to act, and its
   `content_editor_id` marks the editor already covering it — never create a second editor for a
   covered item.
   - For an *optimize* item, hand its editor to `surfer-optimize-content`, skipping that skill's
     create step. Use `content_editor_id` when set. Otherwise confirm the spend, then call
     `recommendation__optimize` — the product's Optimize button. It opens the page's own Content
     Editor, connected to Content Audit so optimization progress tracks in the product, charges one
     Content Editor credit unless the page's editor was already paid for, and returns the refreshed
     item with `content_editor_id` set. Never import the page URL into a fresh editor instead; that
     disconnects the tracking. A conflict means the editor is already open, so re-list and use its
     id. A retryable failure means the editor is still being prepared, so wait and retry, bounded.
   - For a *write* item, continue in the `content_editor_id` editor when set. Otherwise hand its
     `main_keyword` and `location` to `surfer-write-article`, which creates the editor itself.

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
   tool. An optimize item's progress also shows in the product: its `optimization_status` and the
   linked draft's `content_score` update on `recommendation__list`.
