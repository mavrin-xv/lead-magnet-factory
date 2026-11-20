---
name: magnet-concept
description: Picks what a lead magnet should be before anything is written - reads the raw input (article, voice note transcript, research dump, survey themes, a topic), names the reader, their pain and the paid offer it should lead to, drafts 3 to 5 concepts across magnet types and formats, scores each on five tests and returns one concept card with a title, a quick win and the bridge to the offer. Use when the user says "lead magnet idea", "what should I give away", "freebie for my list", "opt-in idea", "turn this into a lead magnet", "which magnet should I make", or before the magnet-writer skill when no concept card exists yet.
---

# Magnet concept

Most lead magnets fail before the first word: they solve a problem the buyer does not have, they are too big to finish, or they lead nowhere near the thing being sold. Writing quality cannot fix that. This skill decides **what** to give away, so `magnet-writer` only decides **how**.

## Inputs

Accept any of these. Do not ask for a template or a database.

| Input | What to pull from it |
|---|---|
| Article, blog post, URL | The one claim the reader would act on, the steps, any numbers with sources |
| Voice note transcript, call notes | The owner's own method, stories, mistakes they keep seeing |
| Research dump, notes, links | Facts with sources, the pattern across them |
| Survey themes (from `survey-to-magnet`) | The top theme, verbatim quotes, the format it suggests |
| A bare topic | Ask one question: "Who is it for, and what do you sell them next?" |

If the input does not say what is sold after the magnet, ask that **one** question and stop. A magnet with no next step is content, not a lead magnet.

## Procedure

1. **Write the brief in five lines** (show it to the user):
   - Reader: role + situation, as specific as the input allows ("owner of one independent cafe, 1 to 3 staff, buys beans retail").
   - Pain in their words: a phrase they would say, not a category ("my shots taste different every morning").
   - Outcome they want: a result they can see, with a number or a time if the input gives one.
   - Paid offer: what is sold next, and the problem it solves.
   - Bridge: the problem the magnet solves that makes the offer the obvious next step.
2. **Draft 3 to 5 concepts.** Spread them across the three magnet types and at least two formats (see [references/formats.md](references/formats.md)):
   - *Reveal a problem*: a quiz, audit, or checklist that shows the reader a problem they did not see. The offer fixes it.
   - *Sample*: a real piece of the paid thing (one chapter, one recipe, one week of the plan).
   - *One step*: the first step of a multi-step process, done completely.
   Each concept gets: name, hook line, type, format, quick win (what the reader has in under 30 minutes), bridge sentence.
3. **Score each concept on the five tests**, 1 to 5 each, using [references/five-tests.md](references/five-tests.md): Specific, Bridge, Quick win, Value, AI-proof. Write the scores into `concepts.json` (shape in [templates/concepts.example.json](templates/concepts.example.json)) and run:
   ```
   python3 scripts/score_concepts.py concepts.json
   ```
   Any test below 3 rejects the concept. Bridge and Value count double (maximum 35). The ranking is advice: on a tie or a near tie, prefer the concept that covers the bigger pain and ships sooner, and say why. Fix a rejected concept once if the fix is obvious, otherwise drop it.
4. **Write the title** of the winner with the outcome formula in [references/title-formula.md](references/title-formula.md): number or time + the outcome + who it is for. Write 3 options, keep the most specific.
5. **Pick the delivery mechanism**: page (Notion or HTML), downloadable file, short email course, or interactive tool. Default to a page: it opens on a phone, needs no login and can be updated after launch.
6. **Write the concept card** from [templates/concept-card.md](templates/concept-card.md) to `magnets/<slug>/concept.md`. Show the user the card and the ranking table, not the full scoring notes.

## Hard rules

- One reader, one pain, one promise. Two audiences means two magnets.
- The quick win must be reachable in under 30 minutes with what the reader already has.
- The bridge must be honest: the magnet works on its own, and the offer is the next problem, not the missing half of this one. A magnet that deliberately breaks off to force a purchase loses trust and unsubscribes.
- No numbers that are not in the input or a cited source. If the hook needs a number and there is none, mark it `[NEEDS SOURCE]` on the card.
- Use the reader's plain words. A beginner audience gets no jargon in the title or the hook; if a term is unavoidable, the magnet explains it in one line.
- If the input supports nothing specific, say so and ask for an example, a story or a number instead of inventing one.

## Output

```
Concepts for: independent cafe owners -> wholesale bean subscription

PICK   29/35  Weekly bean order calculator            one-step, calculator
ok     29/35  15-minute dial-in checklist             reveal-problem, checklist
REJECT 20/35  Barista training routine                sample, playbook
         - bridge 2 < 3
         - quick win takes 45 min (> 30)

Tie at 29. Picked the checklist: bigger survey theme (10 of 24), ships today
as a page; the calculator needs a small build and becomes magnet 2.

Title options:
1. Dial in your espresso in 15 minutes: a 22-point checklist for small cafes   <- picked
2. ...
Card: magnets/dial-in-checklist/concept.md
Next: magnet-writer
```

A worked example is in `examples/acme-coffee/` (input, `concepts.json`, `concept.md`).
