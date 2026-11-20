#!/usr/bin/env python3
"""Render a lead magnet written in markdown into one standalone HTML page.

The page has no external requests: inline CSS, light and dark themes, print styles,
working checkboxes for checklists (state kept in the reader's browser), and
toggles as <details>. Host it anywhere static (GitHub Pages, Netlify, Cloudflare
Pages, your own site) or send it as a file.

Usage:
  python3 md_to_html.py magnet.md -o magnet.html
  python3 md_to_html.py magnet.md -o magnet.html --accent "#2f6f4f" --lang en

The markdown subset is in docs/markdown-conventions.md. Standard library only.
"""
import argparse
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mdlite import inline_spans, parse  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to a legacy code page

CSS = """
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#5d5d58;--card:#ffffff;--line:#e4e1da;--accent:ACCENT}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--fg:#ecebe6;--muted:#a3a29b;--card:#1e1e1c;--line:#33322f}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
main{max-width:720px;margin:0 auto;padding:32px 16px 64px}
h1{font-size:2rem;line-height:1.2;margin:0 0 12px}
h2{font-size:1.35rem;margin:40px 0 8px;padding-top:16px;border-top:1px solid var(--line)}
h3{font-size:1.1rem;margin:24px 0 6px}
p{margin:0 0 14px}
a{color:var(--accent)}
ul,ol{padding-left:22px;margin:0 0 14px}
li{margin:4px 0}
.todo{list-style:none;padding-left:0}
.todo label{display:flex;gap:10px;align-items:flex-start;cursor:pointer}
.todo input{margin-top:6px;width:18px;height:18px;accent-color:var(--accent)}
.callout{display:flex;gap:10px;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:8px;padding:12px 14px;margin:0 0 16px}
details{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px;margin:0 0 14px}
summary{cursor:pointer;font-weight:600}
details>*:nth-child(2){margin-top:10px}
pre{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;overflow-x:auto;white-space:pre-wrap;font-size:.9rem}
code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.92em}
hr{border:0;border-top:1px solid var(--line);margin:28px 0}
.copy{float:right;font-size:.8rem;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:6px;padding:2px 8px;cursor:pointer}
@media print{.copy{display:none}details{border:0;padding:0}details>summary{list-style:none}body{background:#fff;color:#000}}
"""

JS = """
document.querySelectorAll('.todo input').forEach(function(box,i){
  var key='lm-'+location.pathname+'-'+i;
  try{box.checked=localStorage.getItem(key)==='1';}catch(e){}
  box.addEventListener('change',function(){try{localStorage.setItem(key,box.checked?'1':'0');}catch(e){}});
});
document.querySelectorAll('pre').forEach(function(pre){
  var b=document.createElement('button');b.className='copy';b.textContent='Copy';
  b.addEventListener('click',function(){var t=pre.querySelector('code').innerText;
    if(navigator.clipboard){navigator.clipboard.writeText(t);b.textContent='Copied';setTimeout(function(){b.textContent='Copy'},1500);}});
  pre.prepend(b);
});
"""


def render_inline(text):
    out = []
    for s in inline_spans(text):
        t = html.escape(s["text"])
        if s.get("code"):
            t = "<code>%s</code>" % t
        if s.get("bold"):
            t = "<strong>%s</strong>" % t
        if s.get("italic"):
            t = "<em>%s</em>" % t
        if s.get("link"):
            href = s["link"]
            if not re.match(r"^(https?:|mailto:|#|/)", href):
                href = "#"
            t = '<a href="%s">%s</a>' % (html.escape(href, quote=True), t)
        out.append(t)
    return "".join(out)


def render(blocks):
    out, i = [], 0
    while i < len(blocks):
        b = blocks[i]
        t = b["type"]
        if t in ("bulleted_list_item", "numbered_list_item", "to_do"):
            tag = {"bulleted_list_item": "ul", "numbered_list_item": "ol", "to_do": "ul"}[t]
            cls = ' class="todo"' if t == "to_do" else ""
            items = []
            while i < len(blocks) and blocks[i]["type"] == t:
                x = blocks[i]
                if t == "to_do":
                    chk = " checked" if x.get("checked") else ""
                    items.append('<li><label><input type="checkbox"%s><span>%s</span></label></li>' % (chk, render_inline(x["text"])))
                else:
                    items.append("<li>%s</li>" % render_inline(x["text"]))
                i += 1
            out.append("<%s%s>%s</%s>" % (tag, cls, "".join(items), tag))
            continue
        if t.startswith("heading_"):
            n = t[-1]
            out.append("<h%s>%s</h%s>" % (n, render_inline(b["text"]), n))
        elif t == "paragraph":
            out.append("<p>%s</p>" % render_inline(b["text"]))
        elif t == "callout":
            icon = '<span aria-hidden="true">%s</span>' % html.escape(b["icon"]) if b.get("icon") else ""
            out.append('<div class="callout">%s<div>%s</div></div>' % (icon, render_inline(b["text"])))
        elif t == "code":
            out.append("<pre><code>%s</code></pre>" % html.escape(b["text"]))
        elif t == "divider":
            out.append("<hr>")
        elif t == "toggle":
            out.append("<details><summary>%s</summary>%s</details>" % (render_inline(b["text"]), render(b["children"])))
        i += 1
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="markdown file")
    ap.add_argument("-o", "--out", help="output .html (default: same name)")
    ap.add_argument("--accent", default="#2f6f4f", help="accent color, CSS value")
    ap.add_argument("--lang", default="en", help="html lang attribute")
    a = ap.parse_args()
    with open(a.src, encoding="utf-8") as f:
        blocks = parse(f.read())
    title = next((b["text"] for b in blocks if b["type"] == "heading_1"), os.path.splitext(os.path.basename(a.src))[0])
    title = re.sub(r"[*`]", "", title)
    if not re.match(r"^#[0-9a-fA-F]{3,8}$|^[a-z]+$", a.accent):
        sys.exit("--accent must be a hex color or a CSS color name")
    page = (
        '<!doctype html>\n<html lang="%s"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>%s</title><style>%s</style></head>\n<body><main>\n%s\n</main><script>%s</script></body></html>\n"
    ) % (html.escape(a.lang), html.escape(title), CSS.replace("ACCENT", a.accent), render(blocks), JS)
    out = a.out or os.path.splitext(a.src)[0] + ".html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote %s (%d blocks)" % (out, len(blocks)))


if __name__ == "__main__":
    main()
