# Survey design

## The core question

Ask one open question about the reader's biggest challenge:

> When it comes to <topic>, what is the single biggest challenge you are facing right now?

Why this shape (it follows Ryan Levesque's "single most important question"):

- **Open, not multiple choice.** Choices give you your own words back. Free text gives you theirs, which you need for titles and hooks.
- **"Single biggest"** forces a priority. Without it you get a list of everything.
- **"Right now"** gets current pain, not old history.
- **No "why" or "how would you like us to help".** People are poor at designing solutions; they are good at describing problems.

## Depth beats count

Answers vary in length a lot. The long, specific ones (often 3 to 5 times the median) come from the people who feel the pain most and are most likely to buy. `cluster_survey.py` weights depth (average words) at 30% of a theme's score for this reason. Read those answers first.

## The optional segment question

At most one multiple-choice question, before or after the open one, to split themes by who said them:

> Which best describes you? (a) thinking about opening a cafe (b) running one, under 2 years (c) running one, 2+ years (d) other

Pass it with `--segment`. A theme that is all (a) leads to a different offer than one that is all (c).

## The bucket question (before an opt-in)

A different use of the same idea: one multiple-choice question before the opt-in that sends each reader to a different magnet or a different version of it ("Which is closer to you?"). Use it only after the survey has shown you the 2 to 4 groups. Each bucket gets its own next step.

## Where to run it

| Channel | How |
|---|---|
| Email list | One email, one question, "reply to this email". Paste replies into a CSV |
| Social post or story | The question as the post; collect comments or story replies |
| Community or chat | Pinned message; export or copy replies |
| Form tool | Any free form tool; export CSV |
| Existing data | Support tickets, sales call notes, DMs, reviews: the questions people already asked count |

## How many

- Under 15: hints. Read every answer by hand.
- 15 to 50: themes are usable for one magnet.
- 50 or more: themes are reliable enough to rank several magnets.

## Privacy

Tell people how answers will be used ("to decide what guide to write next"). Quote only without names. Do not collect emails in the survey unless you will use them and they agree.
