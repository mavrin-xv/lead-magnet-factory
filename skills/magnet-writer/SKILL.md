---
name: magnet-writer
description: Writes the lead magnet itself from a concept card or raw input - a checklist, playbook, swipe file, template, mini-course or a five-part hub page - with a sourced hook fact, a quick win near the top, filled examples, one earned next step, then lints it and renders it as a standalone HTML page or Notion blocks (pushed through the Notion API with NOTION_TOKEN). Use when the user says "write the lead magnet", "make the checklist / playbook / swipe file", "build the freebie page", "put it in Notion", "turn this article into a guide", "make an HTML version", or after magnet-concept has produced a concept card.
---

# Magnet writer

A lead magnet is judged in the first screen and finished only if the first section pays off. This skill writes to that: the reader sees a fact that names their problem, gets a result within the first quarter of the page, and finds one honest next step at the end. A lint script checks the mechanical rules; the model checks the judgement rules.

## Inputs

- `magnets/<slug>/concept.md` from `magnet-concept`. If there is none and the user gave raw input, run the five-line brief from `magnet-concept` first (reader, pain, outcome, offer, bridge) and show it. Do not write without a reader and a next step.
- The source material: article, transcript, notes, survey outline.
- The CTA: the delivery keyword or the single link the magnet ends with.

## Procedure

1. **Pick the structure** for the format from [references/format-structures.md](references/format-structures.md). For a flagship page that covers all five angles, use the hub map in [references/hub.md](references/hub.md).
2. **Collect the facts** you will use, each with its source (a URL, "owner's own numbers", "from the survey, n=24"). The hook fact needs a source or the owner's first-hand data. No source, no number: write the claim without one.
3. **Write the draft** to `magnets/<slug>/magnet.md` using the markdown conventions in `docs/markdown-conventions.md` (callouts with `>`, toggles with `+++`, checkboxes with `- [ ]`). Order:
   1. `# Title` (from the concept card)
   2. One callout: who it is for and what they will have at the end.
   3. The hook: one fact that makes the reader feel the problem, with its source.
   4. `## Start here` (or `## Quick win`): the smallest piece that produces a result in under 15 minutes.
   5. The body in the format's structure.
   6. `## Mistakes to avoid`: the top 3 to 5, each one line plus the fix.
   7. `## Next step`: what they just got, what happens if they use it, one action (the keyword or one link).
4. **Apply the laws** in [references/laws.md](references/laws.md) while writing, not after.
5. **Lint:**
   ```
   python3 scripts/magnet_lint.py magnets/<slug>/magnet.md --format checklist --keyword DIALIN
   ```
   Fix every FAIL. Fix WARNs unless you can say why the rule does not apply here.
6. **Run the judgement half** of [references/quality-gate.md](references/quality-gate.md) yourself: the cold-reader pass, the swipe test, the AI-summary test. Rewrite what fails.
7. **Render** what the user asked for:
   ```
   python3 scripts/md_to_html.py magnets/<slug>/magnet.md -o magnets/<slug>/index.html --accent "#2f6f4f"
   python3 scripts/md_to_notion.py magnets/<slug>/magnet.md -o magnets/<slug>/notion.json      # dry run, inspect
   python3 scripts/md_to_notion.py magnets/<slug>/magnet.md --push --parent <PAGE_ID>        # needs NOTION_TOKEN
   ```
   Details, limits and setup for Notion: [references/notion-output.md](references/notion-output.md). Always run the dry run first and check the block count and title.
8. **Report** to the user: title, format, word count, lint result, where the files are, and anything marked `[NEEDS SOURCE]`.

## Hard rules

- One reader, one promise, one CTA. Never "subscribe, follow, book a call and reply".
- No paragraph over 3 sentences. Every action item is something the reader can copy or do without adapting it.
- Examples are complete. A filled example with a `[PLACEHOLDER]` left in it is a broken example.
- Numbers beat adjectives, and every number has a source or is the owner's own.
- Use the reader's plain words. For beginners, no jargon; an unavoidable term gets a one-line explanation the first time.
- Do not cut the magnet short to force the sale. It must work on its own; the offer solves the next problem.
- Never push to Notion without the user asking. Never print or store the token; it comes from `NOTION_TOKEN` only.
- Interactive magnets (quiz, calculator, AI audit) follow [references/interactive-formats.md](references/interactive-formats.md), including its security rules.

## Output

```
magnets/dial-in-checklist/
  magnet.md      source of truth, edit this
  index.html     standalone page: checkboxes remember their state, copy buttons on code blocks, dark mode, print styles
  notion.json    what would be sent to Notion (dry run)
Lint: OK, 0 fail(s), 1 warning(s): no source link in the opening (owner's own data, noted on page)
```

Worked example: `examples/acme-coffee/magnet.md` and the generated `examples/acme-coffee/magnet.html`.
