#!/usr/bin/env python3
"""Convert a lead magnet in markdown into Notion API blocks, and optionally push it.

Default (dry run): writes a JSON file with the page title and the blocks split into
batches, so you can inspect exactly what would be sent.

  python3 md_to_notion.py magnet.md -o notion-blocks.json

Push (needs an internal integration token, shared with the parent page):

  export NOTION_TOKEN="secret_..."          # or ntn_...
  python3 md_to_notion.py magnet.md --push --parent <PARENT_PAGE_ID>
  python3 md_to_notion.py magnet.md --push --parent <DATABASE_ID> --database --title-prop Name

What it handles (see docs/markdown-conventions.md):
  # ## ###       -> heading_1/2/3 (an H1 becomes the page title, not a block)
  - item / 1.    -> bulleted / numbered list items
  - [ ] item     -> to_do
  > emoji text   -> callout with that emoji as icon (default icon: a light bulb)
  +++ Label      -> toggle; everything until a bare +++ goes inside it
  ``` code ```   -> code block
  ---            -> divider
  **b** *i* `c` [t](url) -> rich text annotations and links

Notion limits respected: 2000 characters per rich text item (split), at most
--batch blocks per append call (default 40, the API max is 100), nested children
only one level deep (toggles). Markdown tables are not supported by this script:
write them as bullet lists. Standard library only.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mdlite import inline_spans, parse  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to a legacy code page

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"
MAX_TEXT = 2000
LANGS = {"", "bash", "javascript", "json", "markdown", "python", "shell", "plain text", "typescript", "html", "css", "yaml", "sql"}


def rich(text):
    items = []
    for s in inline_spans(text):
        chunk = s["text"]
        while chunk:
            part, chunk = chunk[:MAX_TEXT], chunk[MAX_TEXT:]
            item = {"type": "text", "text": {"content": part}}
            if s.get("link") and s["link"].startswith(("http://", "https://")):
                item["text"]["link"] = {"url": s["link"]}
            ann = {k: True for k in ("bold", "italic", "code") if s.get(k)}
            if ann:
                item["annotations"] = ann
            items.append(item)
    return items


def to_notion(b, depth=0):
    t = b["type"]
    if t == "divider":
        return {"object": "block", "type": "divider", "divider": {}}
    if t == "code":
        lang = b.get("lang", "").lower() or "plain text"
        if lang not in LANGS:
            lang = "plain text"
        body = []
        text = b["text"]
        while text:
            body.append({"type": "text", "text": {"content": text[:MAX_TEXT]}})
            text = text[MAX_TEXT:]
        return {"object": "block", "type": "code", "code": {"rich_text": body, "language": lang}}
    if t == "callout":
        icon = b.get("icon") or "\U0001F4A1"
        return {"object": "block", "type": "callout", "callout": {"rich_text": rich(b["text"]), "icon": {"type": "emoji", "emoji": icon}}}
    if t == "to_do":
        return {"object": "block", "type": "to_do", "to_do": {"rich_text": rich(b["text"]), "checked": bool(b.get("checked"))}}
    if t == "toggle":
        kids = [to_notion(c, depth + 1) for c in b["children"] if c["type"] != "toggle" or depth == 0]
        if depth >= 1:
            kids = [k for k in kids if k["type"] != "toggle"]
        blk = {"object": "block", "type": "toggle", "toggle": {"rich_text": rich(b["text"])}}
        if kids:
            blk["toggle"]["children"] = kids[:100]
        return blk
    return {"object": "block", "type": t, t: {"rich_text": rich(b["text"])}}


def convert(md):
    blocks = parse(md)
    title = None
    out = []
    for b in blocks:
        if b["type"] == "heading_1" and title is None:
            title = "".join(s["text"] for s in inline_spans(b["text"]))
            continue
        out.append(to_notion(b))
    return title or "Untitled lead magnet", out


def call(method, path, token, body):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode("utf-8"))
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Notion-Version", VERSION)
    req.add_header("Content-Type", "application/json")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            if e.code == 429 and attempt < 2:
                time.sleep(float(e.headers.get("Retry-After", "2")))
                continue
            sys.exit("Notion API %s %s failed: HTTP %s %s" % (method, path, e.code, detail))
        except urllib.error.URLError as e:
            sys.exit("Notion API unreachable: %s" % e.reason)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="markdown file")
    ap.add_argument("-o", "--out", help="write the blocks JSON here (dry run output)")
    ap.add_argument("--batch", type=int, default=40, help="blocks per append call, 1-100 (default 40)")
    ap.add_argument("--push", action="store_true", help="create the page in Notion (needs NOTION_TOKEN)")
    ap.add_argument("--parent", help="parent page id, or database id with --database")
    ap.add_argument("--database", action="store_true", help="--parent is a database; the page becomes a row")
    ap.add_argument("--title-prop", default="Name", help="title property name in the database (default Name)")
    ap.add_argument("--icon", default="", help="page icon emoji")
    a = ap.parse_args()
    if not 1 <= a.batch <= 100:
        sys.exit("--batch must be 1-100")
    with open(a.src, encoding="utf-8") as f:
        title, blocks = convert(f.read())
    batches = [blocks[i:i + a.batch] for i in range(0, len(blocks), a.batch)]
    if a.out or not a.push:
        out = a.out or os.path.splitext(a.src)[0] + ".notion.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"title": title, "block_count": len(blocks), "batches": batches}, f, indent=1, ensure_ascii=False)
        print("wrote %s: %d blocks in %d batch(es), title %r" % (out, len(blocks), len(batches), title))
    if not a.push:
        return
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        sys.exit("NOTION_TOKEN is not set")
    if not a.parent:
        sys.exit("--push needs --parent")
    if a.database:
        page = {"parent": {"database_id": a.parent}, "properties": {a.title_prop: {"title": [{"type": "text", "text": {"content": title}}]}}}
    else:
        page = {"parent": {"page_id": a.parent}, "properties": {"title": {"title": [{"type": "text", "text": {"content": title}}]}}}
    if a.icon:
        page["icon"] = {"type": "emoji", "emoji": a.icon}
    created = call("POST", "/pages", token, page)
    pid = created["id"]
    for n, batch in enumerate(batches, 1):
        call("PATCH", "/blocks/%s/children" % pid, token, {"children": batch})
        print("appended batch %d/%d (%d blocks)" % (n, len(batches), len(batch)))
    print("page: %s" % created.get("url", pid))


if __name__ == "__main__":
    main()
