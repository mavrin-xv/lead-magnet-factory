#!/usr/bin/env python3
"""Build and check a comment-keyword -> DM -> link delivery flow from one JSON file.

  python3 flow_builder.py --init > flow.json        # starter config
  python3 flow_builder.py flow.json -o flow.md      # check + write the setup sheet
  python3 flow_builder.py flow.json --json          # machine-readable result

The output is a setup sheet you copy into whatever tool runs the flow
(ManyChat, another Meta-approved DM tool, a Telegram bot, a form + email tool):
the trigger, every message in order, the tagged link per placement, a test plan
and the numbers to watch. It does not talk to any platform.

Checks (FAIL blocks, WARN is advice):
  keyword: one word, 3-15 letters or digits, not a common word people type anyway
  public replies: 3+ distinct variants, each 100 characters or fewer, no link
  first DM: 2 sentences or fewer, no link, says what is coming; WARN over 120 chars
  button: exactly one, label 20 characters or fewer
  link DM: contains the magnet link
  disclosure: some message says the reply is automated
  human path: some message says how to reach a person
  follow-up: optional, and only sent inside the platform's reply window
  telegram: bot username and start payload valid (payload 1-64 chars of A-Z a-z 0-9 _ -)
Standard library only.
"""
import argparse
import json
import re
import sys
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to a legacy code page

COMMON = set("""yes no ok okay link info more send me please want need love wow nice cool great thanks thank
pdf guide free hi hello hey dm interested this that the and you for are was not but all can get got just here there what when how why who yeah sure nope lol omg top best""".split())

STARTER = {
    "platform": "instagram",
    "magnet_name": "The 15-minute espresso dial-in checklist",
    "magnet_url": "https://example.com/dial-in",
    "keyword": "DIALIN",
    "placements": ["reel-2026-03-04", "carousel-2026-03-06", "story-2026-03-07"],
    "utm": {"source": "instagram", "medium": "dm", "campaign": "dialin-checklist"},
    "public_replies": [
        "Sent, check your DMs.",
        "In your inbox now. Tell me which step you start with.",
        "Done. The checklist is in your DMs."
    ],
    "first_dm": "Here is the dial-in checklist you asked for. Tap below and I will send the link.",
    "button_label": "Send the checklist",
    "link_dm": "Here it is: {link} Start with step 1, it takes 5 minutes. (Automated reply. Write here any time and a person answers.)",
    "follow_up_dm": "Did the checklist open? Reply with your machine model if you want a starting recipe.",
    "follow_up_after_hours": 20,
    "telegram": {"bot_username": "", "start_payload": ""}
}

WINDOW = {  # hours a business may keep messaging after the person's last message
    "instagram": 24, "facebook": 24, "telegram": None, "tiktok": None, "linkedin": None, "email": None,
}


def tag(url, utm, placement):
    p = urlparse(url)
    q = dict(parse_qsl(p.query))
    q.update({"utm_source": utm.get("source", ""), "utm_medium": utm.get("medium", ""),
              "utm_campaign": utm.get("campaign", ""), "utm_content": placement})
    q = {k: v for k, v in q.items() if v}
    return urlunparse(p._replace(query=urlencode(q)))


def nsent(t):
    t = re.sub(r"\{link\}|https?://\S+", "LINK", t)
    return len([s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if s])


def check(cfg):
    R = []
    add = lambda lvl, msg: R.append((lvl, msg))  # noqa: E731
    plat = cfg.get("platform", "instagram").lower()
    kw = str(cfg.get("keyword", ""))
    if not re.fullmatch(r"[A-Za-z0-9]{3,15}", kw):
        add("FAIL", "keyword %r: use one word of 3-15 letters or digits" % kw)
    elif kw.lower() in COMMON:
        add("FAIL", "keyword %r is a word people type anyway; pick one tied to this magnet" % kw)
    else:
        add("PASS", "keyword %s" % kw.upper())
    url = cfg.get("magnet_url", "")
    if not re.match(r"^https://", url):
        add("FAIL", "magnet_url must be an https link")
    reps = cfg.get("public_replies", [])
    if plat in ("instagram", "facebook", "tiktok", "linkedin"):
        if len(set(reps)) < 3:
            add("FAIL", "need 3+ different public replies to rotate, have %d" % len(set(reps)))
        for r in reps:
            if len(r) > 100:
                add("FAIL", "public reply over 100 chars: %r" % r[:40])
            if re.search(r"https?://", r):
                add("FAIL", "public reply contains a link: %r" % r[:40])
        if len(set(reps)) >= 3 and all(len(r) <= 100 for r in reps):
            add("PASS", "%d public replies to rotate" % len(set(reps)))
    first = cfg.get("first_dm", "")
    if not first:
        add("FAIL", "first_dm is empty")
    else:
        if re.search(r"https?://|\{link\}", first):
            add("FAIL", "first DM contains the link; send it after the tap")
        if nsent(first) > 2:
            add("FAIL", "first DM has %d sentences, keep 2 or fewer" % nsent(first))
        if len(first) > 120:
            add("WARN", "first DM is %d chars; short openers get more taps, aim under 120" % len(first))
        if not re.search(re.escape(cfg.get("magnet_name", "")[:12]) or "x^", first, re.I) and not re.search(r"checklist|guide|playbook|template|swipe|course|calculator|quiz|audit|list|pack", first, re.I):
            add("WARN", "first DM does not name what is coming")
    btn = cfg.get("button_label", "")
    if isinstance(btn, list):
        add("FAIL", "use exactly one button, have %d" % len(btn))
    elif not btn:
        add("FAIL" if plat in ("instagram", "facebook") else "WARN", "no button label")
    elif len(btn) > 20:
        add("FAIL", "button label is %d chars, max 20" % len(btn))
    else:
        add("PASS", "button %r" % btn)
    link_dm = cfg.get("link_dm", "")
    if "{link}" not in link_dm and url not in link_dm:
        add("FAIL", "link_dm must contain {link} or the magnet URL")
    msgs = " ".join([first, link_dm, cfg.get("follow_up_dm", "")]).lower()
    if not re.search(r"automat|bot\b|auto-reply|auto reply", msgs):
        add("FAIL", "no message says the reply is automated")
    else:
        add("PASS", "automation disclosed")
    if not re.search(r"person|human|me directly|reply here|write here|answer", msgs):
        add("FAIL", "no message tells people how to reach a person")
    else:
        add("PASS", "human path present")
    fu = cfg.get("follow_up_dm")
    hrs = cfg.get("follow_up_after_hours")
    win = WINDOW.get(plat)
    if fu:
        if win and (hrs is None or hrs >= win):
            add("FAIL", "%s allows follow-ups only within %dh of the person's last message; set follow_up_after_hours below %d" % (plat, win, win))
        elif win:
            add("PASS", "follow-up at %sh, inside the %dh window (sent only to people who tapped or replied)" % (hrs, win))
    if plat == "telegram":
        tg = cfg.get("telegram", {})
        bot, pl = tg.get("bot_username", ""), tg.get("start_payload", "")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{3,31}bot", bot or "", re.I):
            add("FAIL", "telegram.bot_username must be a bot username ending in 'bot'")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", pl or ""):
            add("FAIL", "telegram.start_payload must be 1-64 chars of A-Z a-z 0-9 _ -")
    return R


def sheet(cfg, R):
    plat = cfg.get("platform", "instagram")
    utm = cfg.get("utm", {})
    placements = cfg.get("placements") or ["default"]
    L = ["# Delivery flow: %s" % cfg.get("magnet_name", ""), "",
         "Platform: %s. Keyword: **%s**. Magnet: %s" % (plat, str(cfg.get("keyword", "")).upper(), cfg.get("magnet_url", "")), ""]
    L += ["## Checks", ""] + ["- %s %s" % r for r in R] + [""]
    if plat == "telegram":
        tg = cfg.get("telegram", {})
        L += ["## Entry link", "", "`https://t.me/%s?start=%s`" % (tg.get("bot_username", ""), tg.get("start_payload", "")), "",
              "Put this link in your bio, posts and pinned comment. When someone opens it the bot receives `/start %s`; reply with the messages below." % tg.get("start_payload", ""), ""]
    else:
        L += ["## Trigger", "", "- Comment contains **%s** (any case, anywhere in the comment) on these posts only: %s" % (str(cfg.get("keyword", "")).upper(), ", ".join(placements)),
              "- One reply per person per post, even if they comment twice.", ""]
        L += ["## Public replies (rotate in order, post after the DM goes out)", ""] + ["%d. %s" % (i, r) for i, r in enumerate(cfg.get("public_replies", []), 1)] + [""]
    L += ["## Messages", "", "1. **First DM** (no link): %s" % cfg.get("first_dm", ""), "   Button: [%s]" % cfg.get("button_label", ""),
          "2. **After the tap** (link): %s" % cfg.get("link_dm", "").replace("{link}", "<tagged link for the placement>").replace("\n", "\n   ")]
    if cfg.get("follow_up_dm"):
        L.append("3. **Follow-up** at %sh, only to people who tapped but did not open the link: %s" % (cfg.get("follow_up_after_hours"), cfg["follow_up_dm"]))
    L += ["", "## Tagged links (one per placement)", ""]
    for p in placements:
        L.append("- %s: %s" % (p, tag(cfg.get("magnet_url", ""), utm, p)))
    L += ["", "## Test before going live", "",
          "- [ ] From a second account, comment the keyword in lower case inside a sentence. The DM arrives within a minute.",
          "- [ ] Comment a near miss (the keyword with a typo). Nothing is sent.",
          "- [ ] Tap the button. The link message arrives and the link opens on a phone without a login.",
          "- [ ] Reply to the DM with a question. It reaches a person's inbox, not a loop.",
          "- [ ] Comment twice. Only one DM is sent.",
          "- [ ] The public reply appears and does not repeat the previous one.",
          "", "## Watch weekly", "",
          "- Comments with the keyword, per placement",
          "- DMs delivered / comments (delivery failures show here first)",
          "- Taps / DMs delivered (the first DM's job)",
          "- Link opens / taps (use the utm_content per placement)",
          "- Next-step actions / link opens (signups, replies, calls)",
          "- Replies a person answered within a day", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config", nargs="?", help="flow JSON")
    ap.add_argument("--init", action="store_true", help="print a starter config and exit")
    ap.add_argument("-o", "--out", help="write the setup sheet (markdown) here")
    ap.add_argument("--json", action="store_true", help="print checks as JSON")
    a = ap.parse_args()
    if a.init:
        print(json.dumps(STARTER, indent=2))
        return
    if not a.config:
        ap.error("give a config file or --init")
    with open(a.config, encoding="utf-8") as f:
        cfg = json.load(f)
    R = check(cfg)
    fails = sum(1 for r in R if r[0] == "FAIL")
    if a.json:
        print(json.dumps({"fails": fails, "results": [{"level": l, "msg": m} for l, m in R]}, indent=1))
    else:
        for r in R:
            print("%-4s %s" % r)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(sheet(cfg, R))
        print("wrote %s" % a.out)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
