# Quality gate

Two halves. The script checks what a script can check. The model checks the rest, honestly, before the user sees the draft.

## Script half: `scripts/magnet_lint.py`

| Level | Check |
|---|---|
| FAIL | No `# Title` |
| FAIL | A paragraph or callout over 3 sentences |
| FAIL | An unfilled `[PLACEHOLDER]` anywhere, except inside a blank section headed "Template" (the reader fills that one) |
| FAIL | Item count below the floor for the format |
| FAIL | Not exactly one `## Next step` section, or more than one link in it |
| FAIL | `--keyword` given but not in the Next step section |
| WARN | Title without a number, time or unit |
| WARN | No `Start here` / `Quick win` heading in the first 25% of the page |
| WARN | No number or no source in the opening 8 blocks |
| WARN | A playbook step without an example or a "don't" line |
| WARN | Item count outside the target range, hype words, em or en dashes |

## Model half: run these yourself

1. **Cold reader.** Read only the title, the first callout and the headings. Can a stranger in the target audience say what they will have at the end and how long it takes? If not, rewrite the headings.
2. **Swipe test.** Pick three action items at random. Could the reader do each one right now, as written, without making a decision you did not make for them? If not, make it concrete.
3. **Quick win test.** Do the `Start here` section in your head with only what the reader has. Under 15 minutes, with a visible result? If not, shrink it.
4. **AI-summary test.** Ask: would a chatbot answer to "how do I <title>" contain everything here? List what this magnet has that the answer would not (first-hand numbers, real examples, a template, the reader's own words). If the list is empty, add something from the owner or cut the magnet down to what is unique.
5. **Bridge test.** Read the Next step section after the rest. Does the offer solve the problem the reader now has? Does it read as a continuation, not a pitch?
6. **Source test.** Every number: where is it from? A number with no source is removed or marked `[NEEDS SOURCE]` for the owner.
7. **Words test.** Underline every term the reader would not use about their own problem. Replace it, or explain it once in plain words.

## Report

Tell the user the lint summary line, which model tests needed changes and what changed, and anything still marked `[NEEDS SOURCE]`. Do not show the full checklist unless asked.
