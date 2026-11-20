---
name: keyword-delivery
description: Designs and checks the delivery flow for a lead magnet - comment a keyword, get a DM, tap, get the link - for Instagram, Facebook, TikTok, LinkedIn or a Telegram bot deep link, plus a plain form-and-email variant. Writes the keyword, rotating public replies, the first DM, the button, the link message with tagged links per post, the follow-up inside the platform's messaging window, the disclosure and the human fallback, then validates them with a script and outputs a setup sheet and a test plan for whichever DM tool runs it. Use when the user says "comment to DM", "keyword automation", "comment KEYWORD to get the guide", "set up ManyChat for my freebie", "how do I deliver the lead magnet", "Telegram bot start link", or "why are people not getting the DM".
---

# Keyword delivery

A good magnet with a broken delivery flow is a dead magnet. The usual failures: the keyword is a word people type anyway, the first DM is a wall of text, the link goes out before anyone taps, the follow-up arrives after the platform's window closed, and nobody tested from a second account. This skill writes the flow so those cannot happen, and leaves the button-pressing in your DM tool to you.

## Inputs

- The magnet's public link (`https://`), name and the channel the promo runs on.
- The posts or placements that will carry the keyword.
- Which tool runs it: a Meta-approved DM automation tool, a Telegram bot, or a form plus email tool.

## Procedure

1. **Start a config:**
   ```
   python3 scripts/flow_builder.py --init > magnets/<slug>/flow.json
   ```
2. **Pick the keyword.** One word, 3 to 15 letters or digits, tied to the magnet (`DIALIN`, not `GUIDE` or `YES`). Same spelling everywhere. Rules: [references/platform-rules.md](references/platform-rules.md).
3. **Write the messages** using [references/message-templates.md](references/message-templates.md):
   - 3 or more public replies, each 100 characters or fewer, no link, rotated so the thread does not look like a bot.
   - First DM: 2 sentences or fewer, no link, says what is coming, one button (label 20 characters or fewer). Under 120 characters gets more taps.
   - Link DM, sent after the tap: the link, the first thing to do with it, a line saying the reply was automated and a person reads replies.
   - Optional follow-up, only to people who tapped, inside the platform's window.
4. **Check and build the sheet:**
   ```
   python3 scripts/flow_builder.py magnets/<slug>/flow.json -o magnets/<slug>/flow.md
   ```
   Fix every FAIL. The sheet has the trigger, the messages in order, one tagged link per placement (`utm_content` = the placement) and the test plan.
5. **Set it up** in the DM tool from the sheet. For Telegram: create the bot with BotFather, use the `https://t.me/<bot>?start=<payload>` link from the sheet, and have the bot answer `/start <payload>` with the messages. For form plus email: the form's thank-you page shows the link right away and the email repeats it.
6. **Test before the post goes live**, from a second account, with the checklist in the sheet. Do not skip the near-miss and double-comment tests.
7. **Measure weekly** with [references/measurement.md](references/measurement.md): every step has its own rate, so you know which message to fix.

## Hard rules

- Use only the platform's official messaging API or a tool approved by the platform. No unofficial bots, no logging in as the account from a script.
- Send only in reply to the person's action (their comment, their tap, their message), inside the window the platform allows. No cold DMs to people who did not ask.
- Always say the DM is automated and how to reach a person. A reply to the bot must land in a human inbox.
- One button, one link, one next step per message.
- Never put the link in a public reply. It invites spam and the platform may hide the reply.
- Store nothing beyond what the tool needs to deliver the link and the follow-up.
- This skill writes and checks. It never posts, sends or logs in.

## Output

```
PASS keyword DIALIN
PASS 3 public replies to rotate
PASS button 'Send the checklist'
PASS automation disclosed
PASS human path present
PASS follow-up at 20h, inside the 24h window
wrote magnets/dial-in-checklist/flow.md
```

Worked example: `examples/acme-coffee/flow.json` and the generated `examples/acme-coffee/flow.md`.
