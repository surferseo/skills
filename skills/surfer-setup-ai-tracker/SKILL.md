---
name: surfer-setup-ai-tracker
description: >-
  Use when the user wants to start tracking a brand in AI search with Surfer's AI Tracker. Triggers
  include "set up AI Tracker for my site", "start tracking my brand in ChatGPT and Perplexity",
  "create a workspace for example.com and track it in AI search", and "turn on AI Tracker for this
  workspace". It creates or picks a branded workspace, waits for Surfer's prompt suggestions, has
  the user choose and edit the prompts within the prompt quota, and creates the AI Tracker project.
license: MIT
---

# Surfer: Set Up AI Tracker

## Overview

Set up the AI Tracker project of a branded workspace (it holds exactly one) the way the Surfer app's
setup form does: wait for the suggested prompts, let the user choose and edit them within the quota,
then start tracking. The user decides the prompt list; never create the project from an unreviewed
list.

## Prerequisites

- Require connected Surfer MCP tools. For setup or connection failures, use `surfer-connect`;
  ask to install it if missing. If a required tool is unavailable, name it and stop.

## Playbook

1. **Get a branded workspace.** For a new site, ask for the workspace name, site URL, and location
   if the user did not give them, then call `workspace__create`. Poll `workspace__get` until
   `state` is `ready_for_activation` and call `workspace__activate`; activation starts the prompt
   suggestions. On `failed`, report it and stop. For an existing workspace, resolve it with
   `workspace__list`: it must be `branded` and `active`, and `ai_tracker__list` must return no
   project. A playground workspace cannot be set up here; offer to create a branded one. A
   workspace that already has a project is set up; offer its reports instead.

2. **Wait for the suggestions.** Call `ai_tracker__get_setup_suggestions`. While `status` is
   `pending` or `running`, generation takes several minutes: if you can wait in this conversation,
   check again about once a minute for up to ten minutes; otherwise tell the user it is still
   running and ask them to tell you to check again. Never promise to come back on your own unless
   you will. On `completed`, use the topics. On `failed` or `none`, no suggestions will come: tell
   the user and write the prompts with them in step 4 instead. Never ask Surfer to generate them
   again; no tool does that.

3. **Read the limit.** Call `ai_tracker__get_prompt_quota`. The project can track at most the
   smaller of `available` and `max_per_project`. If that is 0, explain that the organization's AI
   Tracker prompts are used up across its projects and stop; the user frees prompts in the Surfer
   app or upgrades the plan.

4. **Review the prompts with the user.** Aim for a review as easy as the Surfer app's setup form:
   the user sees the suggestions, keeps the good ones, fixes or drops the rest, and adds their own,
   without being flooded.
   - Go topic by topic. Never put all of the suggestions in one message.
   - For each topic, show all of its prompts, numbered and in their original language, with the
     `preselected` ones selected.
   - Use the best interface your client has: an interactive form per topic, with checkboxes,
     editable prompts, an editable topic name, and ways to add a prompt or drop the topic. Without
     one, use a numbered text list, not a table, with the selected prompts marked, and ask whether
     to keep, drop, or edit the topic.
   - Whatever the form or list shows, also tell the user in one line that they can type changes,
     for example "drop this topic", "remove 1 and 3", "change 2 to ...", or "add ...".
   - After any change, show the topic again with the updated selection. After the last topic,
     offer a topic of the user's own.
   - Present the suggestions as they are: do not replace, rewrite, or add prompts unless the user
     asks, and do not push a selection of your own. Call the default selection simply selected,
     not Surfer's choice.
   - When you show a prompt, add its source after it as the Surfer app does: "[source: Reddit]"
     for `origin` `reddit`, "[source: Quora]" for `quora`, and "[source: Google]" for `serp`.
     Show no source for any other origin, and never show `type`, `intent`, or `locale`.

   Show the count against the limit and keep it up to date. Keep prompts brand-neutral: a
   prompt that names the user's own brand tells AI Tracker nothing. Drop prompts that differ only
   in case or spacing. Prompts and topic names are at most 255 characters.

5. **Confirm, then create.** Show the final list without topics that have no selected prompts, the
   prompt count, and that creating the project spends that many prompts of the organization's quota.
   Create only after the user explicitly confirms. Call `ai_tracker__create` with the list grouped
   by topic. For every kept suggestion, including a reworded one, pass its `type`, `intent`,
   `origin`, and `locale` unchanged, even when its locale differs from the workspace's. For a
   prompt the user or you wrote, send only `text`, written in the language of the workspace's
   locale. The brand name and the project's locale come from the workspace. On `409`, the
   workspace already has a project: find it with `ai_tracker__list` instead of retrying. On a
   quota error, re-read the limit and trim with the user.

6. **Report.** Return the workspace and project ids, the number of prompts tracked, and that the
   first report is running and refreshes daily. Its progress is on `ai_tracker__get`
   (`latest_run_status`); results appear in the AI Tracker report tools once it completes.
