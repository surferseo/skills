---
name: surfer-detect-humanize
description: >-
  Use when the user wants to check whether text is AI-written or make it read as human — e.g. "is
  this AI-generated", "detect AI content", "check the AI probability", "humanize this text", "make
  this sound less robotic". Uses Surfer's AI detector and humanizer.
license: MIT
---

# Surfer Detect & Humanize

## Overview
Score how likely text is AI-generated, then paraphrase it to read human and re-score to confirm. Use for a probability check, a rewrite, or both.

## Prerequisites
- Plain text input. If the user points at a URL, file, or Content Editor, extract the text first — both ops take raw text, not an editor id.
- Both are **v1**, **synchronous** (no webhook/poll), and require a `model`: `surfer-ai-detector-v1` for detect, `surfer-humanizer-v1` for humanize.
- `ai_detector.detect` is not workspace-scoped; `humanizer.humanize` is. Pass its `Workspace-Id` only when the user names a workspace or a quota error suggests another has allowance (resolve via `workspace.list`).

## Playbook

1. **Detect** — `ai_detector.detect`. Returns overall `ai_probability` (0–1) plus a per-chunk `ai_probability` over `chunks[].text`. Use the overall value as the headline and per-chunk values to locate the most AI-like passages.

2. **Decide.** If the user only asked to detect, report and stop. Otherwise continue, naming the explicit probability threshold you'll humanize above.

3. **Humanize flagged chunks** — `humanizer.humanize`. For each chunk above the threshold, send its `text`; it returns one rewritten `text`. Substitute that back in document order, leave un-flagged chunks verbatim, then concatenate to rebuild the document. Use `stream` only for incremental output.

4. **Re-detect** — run `ai_detector.detect` on the rebuilt document; compare to the original `ai_probability`.

5. **Iterate then report.** Re-humanize at most twice. Stop early on a plateau (no meaningful drop between iterations) — hand still-flagged chunks back with suggestions instead of looping. Otherwise stop below the step-2 threshold or when the user is satisfied. Report original-vs-final probability, the humanized text, and the passages that changed most. Scores are probabilistic, not proof.

## Gotchas
- A quota-or-access error on either op means the allowance is spent or the plan lacks the feature — surface it and stop; never retry in a loop.
- Route SEO scoring to **surfer-optimize-content** and AI-search visibility to **surfer-ai-search**; neither belongs here.

## Calling Surfer
Execute every call through **surfer-api**. Fetch the live doc it points to for `ai_detector.detect` and `humanizer.humanize` before calling.
