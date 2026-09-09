---
name: surfer-content-recommendations
description: >-
  Use when the user wants to act on Surfer's site recommendations. Triggers include "what should I
  optimize next", "turn my Surfer recommendations into articles", "find a content opportunity and
  act on it", and "run the write or optimize workflow from my workspace". It selects
  recommendation-led Optimize or Write work and delegates drafting and optimization to the focused
  Surfer skills.
---

# Surfer: Act on Content Recommendations

## Overview

Turn a chosen, site-level recommendation into one Content Editor workflow without creating the same
work twice.

## Prerequisites

- Resolve the transport: with the Surfer MCP server connected, call its tools directly; otherwise
  run over REST with `surfer-api`; with neither, connect one via `surfer-connect`. REST is usable
  when an API key is set in the `SURFER_API_KEY` environment variable or the client's secret
  storage. Check for that key before concluding that no transport exists. If no transport can run a
  required capability, name it and stop. Do not improvise raw HTTP or assume an endpoint.

## Playbook

1. **Establish scope.** Resolve an active `workspace_id` with `workspace__list`; recommendations
   are read per workspace. If several workspaces are active, ask the caller which one to use rather
   than guessing. If none is active, stop and report. Offer a brand review before optimizing:
   editors opened by `recommendation__optimize` always apply the workspace's brand profile, with no
   per-editor toggle, so read it with `brand__get` and write it with `brand__update` only with an
   approved replacement. Write recommendations are also generated from that profile, so an update
   shapes future generation runs, not the current list. Do not confuse "enabled for this editor"
   with inspecting the profile.

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

4. **Report the lifecycle.** Return the recommendation selected, the workspace and editor ids, the
   baseline and final score snapshot, and the changes made. An optimize item's progress also shows
   in the product: its `optimization_status` and the linked draft's `content_score` update on
   `recommendation__list`.
