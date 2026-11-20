# Platform rules for keyword delivery

Rules change. Check the platform's current developer docs before launch; what follows is what the flow is built around and what `flow_builder.py` enforces.

## Instagram and Facebook (Meta)

- Automated DMs must go through Meta's messaging API, directly or through an approved tool. Tools built on it handle the comment trigger.
- **Private reply to a comment:** a business can send one private reply to a person who commented, within 7 days of the comment. That is the first DM.
- **The 24-hour window:** after the person messages you or taps a button in your message, you can send messages for 24 hours. The link DM and the follow-up go out inside that window. After it closes, you cannot message them again until they do.
- That is why the flow asks for a tap before sending the link: the tap opens the 24-hour window and shows the person wants the message.
- Public replies to comments are ordinary comments. Rotate several, keep them short, no links.
- Hide or limit automation on posts that do not carry the keyword, so a stray comment does not trigger it.

## TikTok, LinkedIn

- Comment-to-DM automation support is narrower and changes often. Check what the platform's API and approved tools allow for your account type today.
- When DM automation is not available, use the keyword for a manual reply, or point to a link in the profile with the keyword as the tracking tag.

## Telegram

- Bots can only message people who started the bot. The entry point is a deep link: `https://t.me/<bot_username>?start=<payload>`.
- The payload is up to 64 characters of `A-Z a-z 0-9 _ -`. The bot receives `/start <payload>` and knows which post sent the person.
- Use a different payload per placement to track sources (`dialin_reel`, `dialin_bio`).
- Messaging rate limits apply to bots. A big launch with thousands of starts per minute needs a queue in the bot.

## Form and email (any platform)

- The keyword can still work: "comment DIALIN and I will reply with the link" done by hand, or the link in the profile.
- Show the magnet on the thank-you page right away. Do not make people wait for the email.
- Use double opt-in where the law or your email tool requires it.

## Keyword rules (all platforms)

- One word, 3 to 15 letters or digits. Not a word people write anyway (yes, link, info, guide, free, interested).
- Tied to the magnet, so you can run two magnets at once (`DIALIN`, `WHOLESALE`).
- Matching ignores case and position: "dialin please" triggers it.
- Same spelling in the video, the caption, the pinned comment and the image text.
