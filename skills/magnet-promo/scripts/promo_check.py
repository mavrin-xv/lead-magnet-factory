#!/usr/bin/env python3
"""Check promo posts for a lead magnet before they go out.

  python3 promo_check.py promo.md --keyword DIALIN
  python3 promo_check.py promo.md --keyword DIALIN --json

promo.md has one section per post: '## <platform>: <label>', e.g.
'## instagram: carousel caption', '## x: post', '## telegram: channel post'.
Text inside ``` fences is ignored (use them for notes to yourself).

Per post it checks:
  FAIL  over the platform's character limit
  FAIL  keyword missing, or the keyword plus a link (two calls to action)
  FAIL  a link in an Instagram or TikTok caption (not clickable there; use the keyword)
  FAIL  newsletter / email sections: not exactly one link (they deliver by link)
  WARN  keyword not in the last 3 lines (people look for the ask at the end)
  WARN  keyword written in different cases across posts
  WARN  more than 5 hashtags; hype words; em or en dashes
  WARN  no concrete item from the magnet given away (no digit and no colon list)
Platforms and limits: x 280, threads 500, bluesky 300, linkedin 3000,
instagram 2200, tiktok 2200, facebook 5000, telegram 4096, newsletter none.
Standard library only.
"""
import argparse
import json
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to a legacy code page

LIMITS = {"x": 280, "twitter": 280, "threads": 500, "bluesky": 300, "linkedin": 3000, "instagram": 2200,
          "tiktok": 2200, "facebook": 5000, "telegram": 4096, "newsletter": None, "email": None, "youtube": 5000}
NO_LINK = {"instagram", "tiktok"}
HYPE = ["unlock", "seamless", "game-changer", "game changer", "supercharge", "revolutionize", "effortless",
        "in today's world", "skyrocket", "don't miss out", "secret sauce", "next level"]
LINK_DELIVERY = {"newsletter", "email"}


def posts(md):
    md = re.sub(r"```.*?```", "", md, flags=re.S)
    out, cur = [], None
    for line in md.splitlines():
        m = re.match(r"^##\s+([A-Za-z]+)\s*:?\s*(.*)$", line)
        if m:
            cur = {"platform": m.group(1).lower(), "label": m.group(2).strip(), "lines": []}
            out.append(cur)
        elif cur is not None:
            cur["lines"].append(line)
    for p in out:
        p["text"] = "\n".join(p["lines"]).strip()
    return out


def check(md, keyword):
    kw = re.compile(r"\b%s\b" % re.escape(keyword), re.I)
    R = []
    seen_cases = set()
    for p in posts(md):
        name = "%s: %s" % (p["platform"], p["label"]) if p["label"] else p["platform"]
        t = p["text"]
        lim = LIMITS.get(p["platform"], "unknown")
        if lim == "unknown":
            R.append(("WARN", name, "unknown platform, no length check"))
        elif lim and len(t) > lim:
            R.append(("FAIL", name, "%d chars, limit %d" % (len(t), lim)))
        else:
            R.append(("PASS", name, "%d chars" % len(t)))
        links = re.findall(r"https?://\S+", t)
        if p["platform"] in LINK_DELIVERY:
            if len(links) != 1:
                R.append(("FAIL", name, "link-delivery post needs exactly one link, has %d" % len(links)))
        else:
            hits = kw.findall(t)
            if not hits:
                R.append(("FAIL", name, "keyword %s missing" % keyword))
            else:
                seen_cases.update(hits)
                last = "\n".join([x for x in t.splitlines() if x.strip()][-3:])
                if not kw.search(last):
                    R.append(("WARN", name, "keyword not in the last 3 lines"))
            if links and p["platform"] in NO_LINK:
                R.append(("FAIL", name, "link in a %s caption is not clickable; use the keyword" % p["platform"]))
            elif links:
                R.append(("FAIL", name, "keyword and a link in one post: two calls to action, keep the keyword"))
        tags = re.findall(r"(?<!\w)#\w+", t)
        if len(tags) > 5:
            R.append(("WARN", name, "%d hashtags, keep 5 or fewer" % len(tags)))
        low = t.lower()
        hy = [w for w in HYPE if w in low]
        if hy:
            R.append(("WARN", name, "hype words: " + ", ".join(hy)))
        if "—" in t or "–" in t:
            R.append(("WARN", name, "em/en dash"))
        if not re.search(r"\d", t) and not re.search(r":\s*\n\s*[-*\d]", t):
            R.append(("WARN", name, "no concrete item given away (no number, no list)"))
    if len(seen_cases) > 1:
        R.append(("WARN", "all", "keyword written as %s; pick one spelling" % ", ".join(sorted(seen_cases))))
    if not R:
        R.append(("FAIL", "all", "no '## platform: label' sections found"))
    return R


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="promo markdown file")
    ap.add_argument("--keyword", required=True, help="the delivery keyword, e.g. DIALIN")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with open(a.src, encoding="utf-8") as f:
        R = check(f.read(), a.keyword)
    fails = sum(1 for r in R if r[0] == "FAIL")
    if a.json:
        print(json.dumps({"fails": fails, "results": [{"level": l, "post": p, "msg": m} for l, p, m in R]}, indent=1))
    else:
        for l, p, m in R:
            print("%-4s [%s] %s" % (l, p, m))
        print("\n%s: %d fail(s)" % ("BLOCKED" if fails else "OK", fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
