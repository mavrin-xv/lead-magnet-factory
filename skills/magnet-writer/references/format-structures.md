# Format structures

Every format shares the same frame: `# Title`, a who-it-is-for callout, the hook fact, `## Start here`, the body below, `## Mistakes to avoid`, `## Next step`. Ready-to-fill skeletons are in the repo's `templates/` folder (`templates/checklist.md`, `templates/playbook.md`, `templates/swipe-file.md`, `templates/template.md`, `templates/mini-course.md`).

## Checklist (20 to 25 items)

Group items under 3 to 5 `##` headings (before, during, after; or by area). Each item:

```
- [ ] **Grinder burrs cleaned this week.** Why: old grounds go stale and taste bitter. Check: run a finger along the burr chamber, no oily residue.
```

Bold the check, then `Why:` (one clause), then `Check:` (how the reader knows it is done). Put the 3 to 5 items with the biggest effect under `## Start here`.

## Playbook (5 to 7 steps)

```
## Step 1: <verb + result>
Context: why this step matters, what goes wrong without it (1 to 2 sentences).
Action: exactly what to do: the words, the settings, the order.
+++ Example
The step done for a real or realistic case, complete.
+++
Don't: the common wrong version, and what it costs.
```

Steps are numbered `## Step N:` so the lint can count them. Each step ends with something the reader has produced.

## Swipe file (15 to 20 entries)

```
### 7. The "we missed you" email (lapsed regulars)
> 💬 Subject: Your usual is on us this week
> Body text in full, ready to paste.
When: 30+ days since the last visit. Why it works: names the habit, removes the cost of coming back.
```

Group entries under `##` headings by situation. Never shorten an entry to "something like...". The full text is the value.

## Template

```
## How to use this template
3 to 5 numbered steps.

## Template
The blank, with [PLACEHOLDERS] in capitals.

## Filled example
The same template filled in for one realistic case. No placeholders left.
```

## Mini-course (3 to 5 lessons)

```
## Lesson 1: <the misunderstanding, fixed>
Problem: what happens without this knowledge.
Solution: the concept, 150 to 300 words, with one example.
Action: one thing to do today.
Self-check: one question; the answer is in a toggle.
```

For an email course, each lesson is one email and the last one carries the next step.

## Hub

All five angles on one page. See [hub.md](hub.md) for the map that keeps them from repeating each other.
