---
name: surfer-explore-ai-tracker-answers
description: >-
  Use when the user asks what AI models (ChatGPT, Gemini, Perplexity, Google AI Overviews and AI
  Mode) say in the answers that Surfer's AI Tracker collects. Triggers include "what does ChatGPT
  say about us", "which answers mention competitor X", "how do models describe our pricing", "who
  gets recommended first for this topic", and "which sites back these answers". It reads the
  tracked answers and answers the question with quotes as evidence.
license: MIT
---

# Surfer: Explore AI Tracker Answers

## Overview

Answer questions about what AI models said in an AI Tracker project, using the answers themselves
as evidence: what each model said, which brands it mentioned and in what order, and which sources
it cited. Read the answers rather than guess from the metrics.

## Prerequisites

- Require connected Surfer MCP tools. For setup or connection failures, use `surfer-connect`;
  ask to install it if missing. If a required tool is unavailable, name it and stop.

## Playbook

1. **Find the project and narrow the question.** Resolve the project with `ai_tracker__list`. Get
   topic and prompt ids from `ai_tracker__list_prompts`. A brand filter matches a canonical name or
   a spelling variant that AI Tracker merges, ignoring case; a validation error means the project
   has no brand with that name, so take the name from `ai_tracker__list_brands`, or the project's
   own brand from `ai_tracker__get`. "My brand" is the project's `brand_name`. Its site is `url`
   from `brand__get` when that brand's `name` matches the project's `brand_name`; otherwise ask the
   user. Compare sites by host, and ask whether the brand has other sites. If the answers never
   mention the project's own brand, say so and offer to look at the competitors that are mentioned.

2. **Scan the answers.** Call `ai_tracker__list_responses` with the narrowest filters that fit the
   question: prompt, topic, brand, model, and range, with `limit` up to 20. Each row has the date,
   prompt, and model. Add `include` only when the question needs it: `brands` for who is mentioned,
   who comes first, and which answers leave a brand out; `source_domains` for which sites back the
   answers. Stop at a sample rather than paging through all 200. Only the 200 newest matching
   answers can be listed; to see others, narrow the filters or the range.

3. **Read what matters.** Call `ai_tracker__get_response` for the answers you need to quote or
   read closely. It returns the full text and every cited source. Read a few representative
   answers per model rather than all of them, unless the question needs all of them.

4. **Answer with evidence.**
   - Quote the answer text rather than paraphrase it, and say which model and date it came from.
   - One page is not the whole picture: say how many answers you looked at out of `meta.total`,
     and present counts from at most 200 answers as a sample.
   - Compare the models that appear in the rows before concluding what "AI" says in general.
   - A brand missing from `brands` was not detected, which does not prove it went unmentioned.
   - For trends, compare ranges, and use `ai_tracker__get_time_series` for the numbers.
   - For the sites behind a set of answers, count `source_domains` across the rows; for the sites
     cited most across the project, use `ai_tracker__list_sources`; for one answer's full URLs, use
     `ai_tracker__get_response`.
   - Do not invent answers or sources, and do not present your own opinion as what the models said.

5. **Offer the next step,** such as reading more answers, comparing another model or range, or
   looking at the sources behind a claim. Suggest an example question below when one fits.

## Example questions

- **What does ChatGPT say about my brand?** `ai_tracker__list_responses` with the brand and
  `model`, then quote two or three answers read with `ai_tracker__get_response`.
- **Who gets recommended first for this topic?** `ai_tracker__list_responses` with `topic_id`
  and `include` `brands`; compare the brands at position 1 per model.
- **On which prompts is my brand missing, and who wins there?** Prompts with a low
  `mention_rate` and their top brands from `ai_tracker__list_prompts`, then
  `ai_tracker__list_responses` with a `prompt_id` and `include` `brands` to read those answers.
- **How do the models differ on the same prompt?** One `ai_tracker__list_responses` call with
  `prompt_id` and `include` `brands`; group the rows by `model`.
- **Which sites back the answers that mention my brand or a competitor?** Count `source_domains`
  across the rows of `ai_tracker__list_responses` filtered by that brand, with `include`
  `source_domains`.
- **Is my own site cited when AI mentions my brand?** The share of those rows whose
  `source_domains` include the brand's site, per model.
- **How is my brand described: strengths, weaknesses, pricing?** Read the answers that mention
  it and quote their wording.
- **What changed recently?** Compare the 7d and 30d ranges; take the numbers from
  `ai_tracker__get_time_series`.
