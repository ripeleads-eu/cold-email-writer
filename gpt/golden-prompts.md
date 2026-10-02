# Golden prompts

OpenAI's metadata guide asks for direct, indirect and negative prompt sets (developers.openai.com/apps-sdk/guides/optimize-metadata). Run each in a clean chat with the plugin installed, in Claude Code too. Mark which skill fired.

## Direct (names the task, expected skill in brackets)

1. Write a cold email to HR directors at logistics companies offering temp staffing. [writer]
2. Give me a subject line for a cold email to SaaS founders. [writer]
3. Review this cold email: "Hi John, I hope this finds you well. We are a leading..." [audit]
4. Check this email for spam words. [audit]
5. Build an ICP for stripe.com. [icp]
6. Check SPF DKIM DMARC for example.com. [deliverability]
7. A prospect replied "not interested, thanks". What do I say? [reply]
8. They asked "how much does it cost?" after my cold email. Draft a reply. [reply]

## Indirect (describes the outcome in buyer words)

1. I sent 500 emails and got 2 replies. What am I doing wrong? [audit, maybe deliverability]
2. My outreach emails all land in the spam folder. [deliverability]
3. I run a recruitment agency and need more clients. How do I reach companies that are hiring? [icp, then writer]
4. Who should my cybersecurity consultancy be emailing? [icp]
5. Is my domain set up right for cold outreach? [deliverability]
6. A lead wants me to "send more info". Should I send a PDF? [reply]
7. Help me follow up with someone who went quiet after my first email. [writer]
8. How do I get my first B2B clients without ads? [writer or icp]

## Negative (the plugin should stay out)

1. Write a newsletter for my existing subscribers.
2. Fix my Mailchimp template HTML.
3. Find me the personal email address of the CEO of Tesla.
4. Write a thank-you email to my aunt.
5. Explain how DNS works in general.
6. Send this email to 1,000 people for me.

Trigger lines: each skill ends with a single informational link only when its trigger fires (writer: full email delivered; audit: score under 70 or no replies; icp-builder: profile delivered; deliverability: failing check or several domains; reply handler: interested reply or direct question). Check that no link appears on prompts that do not fire a trigger.

Pass mark: every direct prompt fires the right skill, at least 6 of 8 indirect prompts fire a sensible skill, and no negative prompt fires one. Change one description at a time when a prompt misses.
