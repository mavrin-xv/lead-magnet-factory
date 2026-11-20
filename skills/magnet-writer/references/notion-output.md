# Notion output

`scripts/md_to_notion.py` turns `magnet.md` into Notion blocks. The dry run writes JSON you can read; `--push` sends it through the official API.

## Setup (once)

1. In Notion, open Settings, Connections, then "Develop or manage integrations", and create an internal integration. Copy its secret.
2. Put it in the environment, never in a file in the repo:
   ```
   export NOTION_TOKEN="<your integration secret>"
   ```
3. Open the parent page (or database) in Notion, use the page menu to add a connection, and pick your integration. Without this step the API answers 404 even with a valid token.
4. The parent id is the 32-character hex string at the end of the page URL.

## Run

```
python3 scripts/md_to_notion.py magnet.md -o notion.json                       # dry run
python3 scripts/md_to_notion.py magnet.md --push --parent <PAGE_ID> --icon "☕"
python3 scripts/md_to_notion.py magnet.md --push --parent <DATABASE_ID> --database --title-prop Name
```

The page is created first with the H1 as its title, then the blocks are appended in batches (`--batch`, default 40). A failed call stops the run and prints the API's error. The page may then exist with some blocks missing: delete it in Notion and run again.

## What maps to what

| Markdown | Notion block |
|---|---|
| First `# H1` | Page title (not a block) |
| `##`, `###`, later `#` | heading_2, heading_3, heading_1 |
| `- item`, `1. item` | bulleted / numbered list item |
| `- [ ] item`, `- [x] item` | to_do |
| `> 💡 text` | callout with that emoji (default 💡) |
| `+++ Label` ... `+++` | toggle with the lines inside as children |
| fenced code | code block (unknown languages become plain text) |
| `---` | divider |
| `**b**`, `*i*`, `` `c` ``, `[t](url)` | bold, italic, code, link |

## Limits and choices

- Rich text is split every 2000 characters (the API limit per item).
- At most 100 blocks per append call (the API limit); 40 is the default to stay well under request size limits.
- Children nest one level: a toggle inside a toggle is dropped. Keep toggles flat.
- Markdown tables are not converted. Write them as lists, or as a list per row.
- Images are not uploaded. Link to them or add them in Notion after the push.

## Making the page public

Use Share, then Publish in Notion and copy the public link. That link is what the delivery flow sends. Check it in a private browser window: if it asks for a login, it is not published.
