# Ripe Leads Cold Email Writer

Five skills for writing cold emails that get replies, from [Ripe Leads](https://ripeleads.eu/?utm_source=github&utm_medium=readme&utm_campaign=cold-email-writer). Works in Claude Code, claude.ai, ChatGPT and Codex.

| Skill | Ask it to... |
|---|---|
| `cold-email-writer` | "write a cold email for my agency", "give me a subject line" |
| `cold-email-audit` | "review my cold email", "why is nobody replying", "check this email for spam words" |
| `icp-builder` | "build my ideal customer profile from example.com", "who should I target with cold email" |
| `email-deliverability-check` | "why are my emails going to spam", "check SPF DKIM DMARC for example.com" |
| `cold-email-reply-handler` | "a prospect said not interested, how do I reply", "they asked for pricing" |

Rules built in: emails under 90 words, plain text, one fact about the prospect, one question as the ask, no spam words, separate domains for sending.

## Install

### Claude Code

```
/plugin marketplace add ripeleads-eu/cold-email-writer
/plugin install ripeleads-cold-email@ripeleads
```

Or from a terminal:

```
claude plugin marketplace add ripeleads-eu/cold-email-writer
claude plugin install ripeleads-cold-email@ripeleads
```

Then run `/reload-plugins`. The skills load on their own when your request matches, or call one directly, for example `/ripeleads-cold-email:cold-email-audit`.

### claude.ai

Download a skill zip from the Releases page (or build it with `python3 scripts/build_dist.py`), then open **Customize > Skills > + > Upload a skill**. Code execution must be on in settings.

### ChatGPT and Codex

Install **Ripe Leads Cold Email Writer** from the ChatGPT plugin directory once it is listed. In Codex you can copy any folder from `skills/` into `.agents/skills/` in your repo.

### Any other agent

Every skill is a plain `SKILL.md` file in the open Agent Skills format. Copy the folder wherever your agent reads skills.

## What the deliverability check runs

`skills/email-deliverability-check/scripts/check_domain.py` reads public DNS records (MX, SPF, DMARC, DKIM) through Google's DNS-over-HTTPS service. It uses the Python standard library, sends only the domain name you give it, and changes nothing.

```
python3 skills/email-deliverability-check/scripts/check_domain.py example.com
```

## Licence

MIT. Fork it, change it, ship it.
