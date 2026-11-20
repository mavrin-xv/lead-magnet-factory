# Measuring the flow

Each step has one job, so each gets its own rate. A low overall number tells you nothing; a low step rate tells you which message to rewrite.

| Step | Rate | If it is low, fix |
|---|---|---|
| Post reach to keyword comments | comments with keyword / reach | The promo post: the hook or the give-away (see `magnet-promo`) |
| Comment to DM delivered | DMs delivered / keyword comments | The tool: trigger spelling, post not attached, account limits |
| DM to tap | taps / DMs delivered | The first DM: shorter, name the magnet, clearer button |
| Tap to link open | opens / taps | The link DM: link on its own line, page loads on a phone without login |
| Open to next step | next-step actions / opens | The magnet's quick win and its Next step section |
| Replies answered | replies answered within a day / replies | The human path: someone has to read the inbox |

## How to count

- **Per placement.** `flow_builder.py` tags each link with `utm_content=<placement>`, so your page analytics split opens by post.
- **Telegram:** count `/start <payload>` per payload in the bot.
- **Comments and DMs:** most DM tools show triggers, sent and button clicks per automation.

## Watch also

- **Unsubscribes and blocks after the follow-up.** A follow-up that raises them costs more than it brings.
- **Replies that are questions.** They are the next magnet, or a gap in this one.
- **Time to first reply by a person.** If people who write back wait days, the automation saved the start and lost the end.

## Rules for changes

Change one message at a time and give it a week or a few hundred deliveries before judging. Write the change and the date in `flow.md` so you can tell later which version produced which numbers.
