"""Tiny markdown parser shared by md_to_html.py, md_to_notion.py and magnet_lint.py.

Supports the subset described in docs/markdown-conventions.md:
headings (#, ##, ###), paragraphs, bullet lists (- or *), numbered lists (1.),
checkboxes (- [ ] / - [x]), callouts (> text, first line may start with an emoji),
toggles (+++ Label ... +++), fenced code (```), dividers (---), and inline
**bold**, *italic*, `code`, [text](url).

Not a full CommonMark parser. Nested lists are flattened to one level.
Run `python3 mdlite.py FILE` to print the parsed block tree as JSON.
"""
import json
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to a legacy code page

INLINE = re.compile(r"(\*\*(.+?)\*\*|`([^`]+)`|\[([^\]]+)\]\(([^)\s]+)\)|(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*]))")


def inline_spans(text):
    """Split text into spans: list of dicts {text, bold, italic, code, link}."""
    spans, pos = [], 0
    for m in INLINE.finditer(text):
        if m.start() > pos:
            spans.append({"text": text[pos:m.start()]})
        if m.group(2) is not None:
            spans.append({"text": m.group(2), "bold": True})
        elif m.group(3) is not None:
            spans.append({"text": m.group(3), "code": True})
        elif m.group(4) is not None:
            spans.append({"text": m.group(4), "link": m.group(5)})
        elif m.group(6) is not None:
            spans.append({"text": m.group(6), "italic": True})
        pos = m.end()
    if pos < len(text):
        spans.append({"text": text[pos:]})
    return [s for s in spans if s["text"]]


def parse(md):
    """Return a list of blocks: {type, text, ...}. Toggles carry 'children'."""
    lines = md.replace("\r\n", "\n").split("\n")
    blocks, stack = [], []

    def out():
        return stack[-1]["children"] if stack else blocks

    i, para = 0, []

    def flush():
        if para:
            out().append({"type": "paragraph", "text": " ".join(p.strip() for p in para)})
            para.clear()

    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s.startswith("```"):
            flush()
            lang = s[3:].strip()
            code, i = [], i + 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            out().append({"type": "code", "text": "\n".join(code), "lang": lang})
            i += 1
            continue
        if s.startswith("+++"):
            flush()
            label = s[3:].strip()
            if label:
                tog = {"type": "toggle", "text": label, "children": []}
                out().append(tog)
                stack.append(tog)
            elif stack:
                stack.pop()
            i += 1
            continue
        if not s:
            flush()
            i += 1
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", s)
        if m:
            flush()
            out().append({"type": "heading_%d" % len(m.group(1)), "text": m.group(2).strip()})
            i += 1
            continue
        if re.match(r"^(-{3,}|\*{3,})$", s):
            flush()
            out().append({"type": "divider", "text": ""})
            i += 1
            continue
        m = re.match(r"^[-*]\s+\[([ xX])\]\s+(.*)$", s)
        if m:
            flush()
            out().append({"type": "to_do", "text": m.group(2), "checked": m.group(1) != " "})
            i += 1
            continue
        m = re.match(r"^[-*]\s+(.*)$", s)
        if m:
            flush()
            out().append({"type": "bulleted_list_item", "text": m.group(1)})
            i += 1
            continue
        m = re.match(r"^\d+[.)]\s+(.*)$", s)
        if m:
            flush()
            out().append({"type": "numbered_list_item", "text": m.group(1)})
            i += 1
            continue
        if s.startswith(">"):
            flush()
            q = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q.append(lines[i].strip()[1:].strip())
                i += 1
            text = " ".join(x for x in q if x)
            icon = ""
            m2 = re.match(r"^([^\w\s\[\]*`(]{1,2})\s+(.*)$", text)
            if m2:
                icon, text = m2.group(1), m2.group(2)
            out().append({"type": "callout", "text": text, "icon": icon})
            continue
        para.append(line)
        i += 1
    flush()
    return blocks


def walk(blocks):
    """Yield every block, toggles' children included."""
    for b in blocks:
        yield b
        for c in b.get("children", []):
            yield from walk([c])


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    with open(sys.argv[1], encoding="utf-8") as f:
        print(json.dumps(parse(f.read()), indent=2, ensure_ascii=False))
