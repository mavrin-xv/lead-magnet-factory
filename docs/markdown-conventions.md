# Markdown conventions

`magnet.md` is the source of truth for a magnet. Three scripts read it: `md_to_html.py` (standalone page), `md_to_notion.py` (Notion blocks) and `magnet_lint.py` (the quality gate). They share one small parser, so write only the syntax below. Anything else is passed through as plain text.

## Blocks

| Write | You get | HTML | Notion |
|---|---|---|---|
| `# Title` | The page title. Exactly one. | `<h1>` | Page title (not a block) |
| `## Section`, `### Item` | Headings | `<h2>`, `<h3>` | heading_2, heading_3 |
| A plain paragraph | Paragraph. Lines next to each other join into one. | `<p>` | paragraph |
| `- item` or `* item` | Bullet | `<ul>` | bulleted_list_item |
| `1. item` | Numbered item | `<ol>` | numbered_list_item |
| `- [ ] item` / `- [x] item` | Checkbox | Checkbox the reader can tick, saved in their browser | to_do |
| `> ☕ text` | Callout. A first character that is an emoji becomes the icon. | Shaded box | callout with icon |
| `+++ Label` ... `+++` | Toggle: the label shows, the body opens on click | `<details>` | toggle with children |
| A fenced code block | Copyable text, for scripts, prompts and templates | `<pre>` with a Copy button | code |
| `---` on its own line | Divider | `<hr>` | divider |

Inside a line: `**bold**`, `*italic*`, `` `code` ``, `[text](https://link)`.

## Limits

- No tables in `magnet.md`. Readers open magnets on phones, where tables break. Use a list with bold labels instead.
- No nested lists. A nested item is flattened to one level.
- No images. Add them by hand in Notion, or with `<img>` in the HTML after export.
- Notion caps one text run at 2000 characters. `md_to_notion.py` splits longer paragraphs for you.

## Conventions the lint relies on

- `## Start here` (or "Quick win", "Do this first") near the top holds the quick win.
- `## Step N: ...` for playbook steps, `## Lesson N: ...` for course lessons, `### ...` for swipe entries.
- `## Template` holds the blank (placeholders allowed there only). `## Filled example` holds the same template filled in.
- Exactly one `## Next step` at the end, with at most one link, and the keyword if the flow uses one.
- Placeholders are written `[IN CAPITALS]`. The lint fails on any left outside the blank template.

## Check what the parser sees

```
python3 skills/magnet-writer/scripts/mdlite.py magnets/<slug>/magnet.md
```

This prints the block tree as JSON. If a block shows up as the wrong type, the HTML and Notion versions will be wrong too.
