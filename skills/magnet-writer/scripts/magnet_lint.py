#!/usr/bin/env python3
"""Check a lead magnet draft against the quality gate before anyone sees it.

  python3 magnet_lint.py magnet.md --format playbook
  python3 magnet_lint.py magnet.md --format checklist --keyword DIALIN --json

Formats: checklist, playbook, swipe, template, course, hub.
Exit code 1 if any FAIL, 0 if only PASS and WARN.

What it checks (the judgement checks stay with the model, see
references/quality-gate.md):
  FAIL  no H1 title
  FAIL  a paragraph longer than 3 sentences
  FAIL  an unfilled [PLACEHOLDER] anywhere except a blank "Template" section
  FAIL  item count out of range for the format (e.g. playbook steps 5-7)
  FAIL  not exactly one "Next step" section, or more than one link in it
  FAIL  --keyword given but missing from the Next step section
  WARN  title has no number, time or concrete unit
  WARN  no "Quick win" / "Start here" section in the first 25% of the page
  WARN  no number in the opening, or no source link in the opening
  WARN  playbook step without an example or a "don't" line
  WARN  hype words, em or en dashes
Standard library only.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mdlite import parse, walk  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to a legacy code page

HYPE = ["unlock", "seamless", "game-changer", "game changer", "supercharge", "revolutionize", "revolutionise",
        "effortless", "in today's world", "skyrocket", "ultimate guide", "secret sauce", "next level", "10x your"]
TITLE_UNIT = re.compile(r"\d|\b(minute|minutes|hour|hours|day|days|week|weeks|month|months|step|steps)\b", re.I)
PLACEHOLDER = re.compile(r"\[[A-Z][A-Z0-9 _/'.,+:-]{2,}\]|(?i:\[insert[^\]]*\]|\[your [^\]]*\])")
BLANK = re.compile(r"^(the |blank |your )?template$|blank", re.I)
NEXT = re.compile(r"^(next step|next steps|what next|what to do next|your next step)\b", re.I)
SENT = re.compile(r"[^.!?]+[.!?]+(\s|$)")

RANGES = {  # format: (what is counted, min, max, hard floor)
    "checklist": ("checkbox items", 20, 25, 10),
    "playbook": ("'## Step' sections", 5, 7, 3),
    "swipe": ("'###' entries", 15, 20, 8),
    "course": ("'## Lesson' sections", 3, 5, 2),
}


def sentences(text):
    t = re.sub(r"\b(e\.g|i\.e|vs|etc|approx|min|max|no)\.", r"\1", text)
    t = re.sub(r"\d\.\d", "0", t)
    t = re.sub(r"\([^)]*\)", "", t)
    return len(SENT.findall(t + (" " if t.rstrip()[-1:] in ".!?" else ". ")))


def plain(text):
    return re.sub(r"[*`]|\[([^\]]+)\]\([^)]+\)", r"\1", text)


def lint(md, fmt, keyword=None):
    res = []
    add = lambda level, msg: res.append((level, msg))  # noqa: E731
    blocks = parse(md)
    flat = list(walk(blocks))
    h1 = [b for b in blocks if b["type"] == "heading_1"]
    if not h1:
        add("FAIL", "no '# Title' line")
    else:
        title = plain(h1[0]["text"])
        if not TITLE_UNIT.search(title):
            add("WARN", "title has no number, time or unit: %r" % title)
        else:
            add("PASS", "title: %r" % title)

    # paragraphs
    long_p = [b for b in flat if b["type"] in ("paragraph", "callout") and sentences(plain(b["text"])) > 3]
    for b in long_p:
        add("FAIL", "paragraph over 3 sentences: %r" % (plain(b["text"])[:70] + "..."))
    if not long_p:
        add("PASS", "every paragraph is 3 sentences or fewer")

    # placeholders inside filled examples
    ctx, bad = "", []

    def scan(items, context):
        for b in items:
            c = context
            if b["type"].startswith("heading_"):
                c = b["text"]
            if b["type"] == "toggle":
                inner = b["text"] if re.search(r"example|filled", b["text"], re.I) else c
                scan(b["children"], inner)
                continue
            if re.search(r"example|filled", c, re.I) and not re.search(r"anti-example|blank", c, re.I):
                if PLACEHOLDER.search(b.get("text", "")):
                    bad.append((c, PLACEHOLDER.search(b["text"]).group(0)))
            context = c if b["type"].startswith("heading_") else context

    for b in blocks:
        if b["type"].startswith("heading_"):
            ctx = b["text"]
        if b["type"] == "toggle":
            scan(b["children"], b["text"] if re.search(r"example|filled", b["text"], re.I) else ctx)
        elif re.search(r"example|filled", ctx, re.I) and not re.search(r"anti-example|blank", ctx, re.I):
            m = PLACEHOLDER.search(b.get("text", ""))
            if m:
                bad.append((ctx, m.group(0)))
    # placeholders anywhere else (a blank template section may keep its fields)
    seen = set(p for _, p in bad)
    ctx = ""
    for b in walk(blocks):
        if b["type"].startswith("heading_"):
            ctx = b["text"]
        if BLANK.search(ctx) and not b["type"].startswith("heading_"):
            continue
        for p in PLACEHOLDER.findall(b.get("text", "")):
            if p not in seen:
                seen.add(p)
                bad.append((ctx or "title", p))
    for c, p in bad:
        add("FAIL", "unfilled placeholder %s in %r" % (p, c[:50]))
    if not bad:
        add("PASS", "no unfilled placeholders")

    # format counts
    h2 = [b for b in blocks if b["type"] == "heading_2"]
    if fmt in RANGES:
        what, lo, hi, floor = RANGES[fmt]
        if fmt == "checklist":
            n = sum(1 for b in flat if b["type"] == "to_do")
        elif fmt == "playbook":
            n = sum(1 for b in h2 if re.match(r"step\s*\d", plain(b["text"]), re.I))
        elif fmt == "swipe":
            n = sum(1 for b in blocks if b["type"] == "heading_3")
        else:
            n = sum(1 for b in h2 if re.match(r"lesson\s*\d", plain(b["text"]), re.I))
        if n < floor:
            add("FAIL", "%d %s, need %d-%d" % (n, what, lo, hi))
        elif n < lo or n > hi:
            add("WARN", "%d %s, target %d-%d" % (n, what, lo, hi))
        else:
            add("PASS", "%d %s" % (n, what))
    elif fmt == "template":
        names = " | ".join(plain(b["text"]).lower() for b in h2)
        for need in ("template", "filled example"):
            add("PASS" if need in names else "FAIL", "section '%s' %s" % (need, "present" if need in names else "missing"))
    elif fmt == "hub":
        names = " | ".join(plain(b["text"]).lower() for b in h2)
        for need in ("playbook", "checklist", "swipe", "template", "course"):
            add("PASS" if need in names else "FAIL", "hub section '%s' %s" % (need, "present" if need in names else "missing"))

    # playbook step anatomy
    if fmt in ("playbook", "hub"):
        cur, body = None, []
        steps = []
        for b in blocks:
            if b["type"] == "heading_2":
                if cur:
                    steps.append((cur, body))
                cur, body = (plain(b["text"]) if re.match(r"step\s*\d", plain(b["text"]), re.I) else None), []
            elif cur:
                body.extend(x.get("text", "") for x in walk([b]))
        if cur:
            steps.append((cur, body))
        for name, body in steps:
            txt = " ".join(body).lower()
            if "example" not in txt and not any(re.search("example", x, re.I) for x in body):
                add("WARN", "%r has no example" % name[:40])
            if not re.search(r"don't|do not|avoid|mistake|anti-example", txt):
                add("WARN", "%r has no 'don't' line" % name[:40])

    # quick win early
    n_blocks = max(1, len(blocks))
    qw = [i for i, b in enumerate(blocks) if b["type"].startswith("heading_") and re.search(r"quick win|start here|do this first|first 15|first 10", b["text"], re.I)]
    if qw and qw[0] <= n_blocks * 0.25:
        add("PASS", "quick win section near the top")
    else:
        add("WARN", "no 'Quick win' / 'Start here' section in the first 25% of the page")

    # hook stat and source in the opening
    opening = blocks[:8]
    otext = " ".join(b.get("text", "") for b in opening)
    if not re.search(r"\d", re.sub(r"^#.*$", "", plain(otext))):
        add("WARN", "no number in the opening (hook fact)")
    if not re.search(r"\]\(https?://|source:", otext, re.I):
        add("WARN", "no source link in the opening; cite the hook fact or mark it as your own experience")

    # next step
    nxt = [i for i, b in enumerate(blocks) if b["type"] == "heading_2" and NEXT.match(plain(b["text"]))]
    if len(nxt) != 1:
        add("FAIL", "need exactly one '## Next step' section, found %d" % len(nxt))
    else:
        i = nxt[0] + 1
        sec = []
        while i < len(blocks) and blocks[i]["type"] not in ("heading_1", "heading_2"):
            sec.extend(walk([blocks[i]]))
            i += 1
        stext = " ".join(b.get("text", "") for b in sec)
        links = len(re.findall(r"\]\(https?://", stext))
        add("FAIL" if links > 1 else "PASS", "Next step has %d link(s)" % links)
        if keyword:
            ok = re.search(r"\b%s\b" % re.escape(keyword), stext, re.I) is not None
            add("PASS" if ok else "FAIL", "keyword %s %s in Next step" % (keyword, "found" if ok else "missing"))

    # words
    low = md.lower()
    hits = [w for w in HYPE if w in low]
    if hits:
        add("WARN", "hype words: %s" % ", ".join(hits))
    dashes = md.count("—") + md.count("–")
    if dashes:
        add("WARN", "%d em/en dash(es); use commas, colons or periods" % dashes)
    words = len(re.findall(r"\w+", plain(md)))
    add("INFO", "%d words, %d blocks" % (words, len(flat)))
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="markdown file")
    ap.add_argument("--format", required=True, choices=["checklist", "playbook", "swipe", "template", "course", "hub"])
    ap.add_argument("--keyword", help="the CTA keyword that must appear in the Next step section")
    ap.add_argument("--json", action="store_true", help="print JSON")
    a = ap.parse_args()
    with open(a.src, encoding="utf-8") as f:
        res = lint(f.read(), a.format, a.keyword)
    fails = sum(1 for r in res if r[0] == "FAIL")
    if a.json:
        print(json.dumps({"fails": fails, "results": [{"level": l, "msg": m} for l, m in res]}, indent=1))
    else:
        for level, msg in res:
            print("%-4s %s" % (level, msg))
        print("\n%s: %d fail(s), %d warning(s)" % ("BLOCKED" if fails else "OK", fails, sum(1 for r in res if r[0] == "WARN")))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
