---
name: surfer-manage-content-templates
description: >-
  Use when the user wants to create, inspect, update, choose, or delete a reusable Surfer content
  template — e.g. "create a custom template", "turn this article into a Surfer template",
  "list our templates", "set a default template", or "update/delete a content template". Uses
  custom content-template capabilities; for a writing style or tone profile use custom voices,
  and for one article's direction use surfer-write-article custom instructions.
---

# Surfer: Manage Content Templates

## Overview

Manage reusable structural examples safely. A template is a reusable reference text for future
Content Editors; it is not a replacement for a voice profile or a one-off prompt.

## Boundaries

- **Template:** reusable organization, sections, formatting, and recurring document shape.
- **Custom voice:** reusable tone and style; manage it with `custom_voice.*` when that is the
  actual request.
- **Custom instructions:** one editor's editorial or factual direction; pass it through
  `content_editor.create` or `content_editor.update`.
- **Surfer template:** a read-only predefined template exposed through
  `surfer_content_template.list`; never try to update or delete it.

Resolve the workspace with `workspace.list` and the active transport under
`surfer-capabilities`. Do not create a template until the user supplies or approves its name and
reference text.

## Playbook

1. **Inspect before mutating.** Use `content_template.list` to find a similarly named custom
   template; use `content_template.get` before changing a specific template. List predefined
   options through `surfer_content_template.list` when the user wants to compare instead of
   creating a duplicate.

2. **Prepare a high-signal reference.** Keep stable structure, heading hierarchy, formatting,
   and representative phrasing. Remove stale facts, client secrets, and accidental product claims.
   Preserve only material the user is authorized to reuse. Do not bury changing campaign details
   in a shared template.

3. **Create safely.** Call `content_template.create` with `name`, `reference_text`, and
   `default: false` unless the user explicitly requests a workspace default. Reuse one logical
   idempotency key on retries, then read the created template to confirm its id and stored
   reference text.

4. **Update intentionally.** Read the target first, show the proposed name/reference/default
   changes, then call `content_template.update`. Treat changing the default as a workspace-wide
   behavior change and require explicit user confirmation immediately before it.

5. **Delete only with confirmation.** Identify the exact template by id and name, explain that
   deletion is destructive, and call `content_template.delete` only after the user confirms that
   exact target. Never infer a deletion from a request to "clean up templates."

6. **Make selection explicit.** Return the template id and workspace. To apply it to a new
   article, pass the chosen `custom_template_id` during `content_editor.create`; do not combine it
   with `surfer_template`, because the two are mutually exclusive.
