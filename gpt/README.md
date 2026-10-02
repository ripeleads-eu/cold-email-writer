# ChatGPT and Codex path

Checked 2026-10-02 against developers.openai.com and help.openai.com. 

## Decision

- **Custom GPT / GPT Store: skip.** OpenAI is retiring custom GPTs and personal accounts (Free, Go, Plus, Pro) can no longer create or publish new ones (help.openai.com/en/articles/8554397).
- **ChatGPT plugin, skills only: use this.** OpenAI renamed "apps" to "plugins". A plugin can hold only skills, so it needs no server. OpenAI accepts a Claude Code plugin archive directly: `.claude-plugin/plugin.json` plus `skills/<name>/SKILL.md` (developers.openai.com/plugins/guides/submit-claude-plugin). Public plugins land in one directory shared by ChatGPT and Codex, where ChatGPT can suggest a plugin during a conversation.

## What to upload

`dist/openai-skills-only.zip`, built by `python3 scripts/build_dist.py`. It holds the portable root `plugin.json` (with `extensions.com.openai.interface` listing copy, logo, composer icon, support URL and up to 3 `defaultPrompt` entries of 128 chars or less), the five skills, a neutral README, the logo and icon, and LICENSE. It carries no Claude or Anthropic wording. Links in it carry `utm_source=chatgpt-plugin`. Build fails if `assets/logo.png` or `assets/icon.png` is missing.

## Submission steps

1. platform.openai.com: complete individual or business identity verification for the org that will own the plugin. The publisher name comes from this.
2. Get "Apps Management" write access in that org (org Owner has it).
3. Open https://platform.openai.com/plugins > **Create plugin** > **Skills only** > upload the zip.
4. Review the generated `.codex-plugin/plugin.json`, then fill the listing from `listing.md`.
5. Logo and composer icon are required (square PNGs, `assets/logo.png` and `assets/icon.png`, still to make). Screenshots are optional and not shown. Short description max 30 chars; support URL must be HTTPS.
6. Run the prompts in `golden-prompts.md` in a clean chat, fix any miss, resolve every scan finding, submit.
7. After approval, choose when to publish.

## Before submitting

- Guidelines: https://developers.openai.com/plugins/plugin-guidelines and https://developers.openai.com/plugins/deploy/submission.
- The privacy policy must cover data categories, purposes, recipients, retention and user controls.
- No fee and no review time are published.
