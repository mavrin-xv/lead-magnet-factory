#!/usr/bin/env python3
"""Rank lead magnet concepts on the five tests and reject the weak ones.

  python3 score_concepts.py concepts.json
  python3 score_concepts.py concepts.json --min 3 --json

concepts.json is a list of objects. Required keys per concept:
  name, hook, type (reveal-problem | sample | one-step), format, bridge,
  scores: {specific, bridge, quick_win, value, ai_proof}   each 1-5
Optional: quick_win_minutes (number), notes.

Rules (from references/five-tests.md):
  - any single test below --min (default 3) rejects the concept
  - quick_win_minutes over 30 rejects it (the reader must get a result fast)
  - total = sum of the five scores; bridge and value count double, because a
    magnet that does not lead to the offer, or is not worth taking, fails the job
    however well it is written
  - ties: higher bridge wins, then shorter quick win
Prints a ranked table with the reason for every rejection. Standard library only.
"""
import argparse
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to a legacy code page

TESTS = ["specific", "bridge", "quick_win", "value", "ai_proof"]
WEIGHT = {"specific": 1, "bridge": 2, "quick_win": 1, "value": 2, "ai_proof": 1}
TYPES = {"reveal-problem", "sample", "one-step"}


def rank(concepts, minimum):
    out = []
    for c in concepts:
        s = c.get("scores", {})
        reasons = []
        for t in TESTS:
            v = s.get(t)
            if not isinstance(v, (int, float)) or not 1 <= v <= 5:
                reasons.append("%s score missing or not 1-5" % t)
            elif v < minimum:
                reasons.append("%s %s < %s" % (t, v, minimum))
        qw = c.get("quick_win_minutes")
        if isinstance(qw, (int, float)) and qw > 30:
            reasons.append("quick win takes %s min (> 30)" % qw)
        if c.get("type") not in TYPES:
            reasons.append("type must be one of %s" % ", ".join(sorted(TYPES)))
        total = sum(WEIGHT[t] * s.get(t, 0) for t in TESTS if isinstance(s.get(t), (int, float)))
        out.append({"name": c.get("name", "?"), "type": c.get("type"), "format": c.get("format"), "total": total,
                    "max": 5 * sum(WEIGHT.values()), "bridge": s.get("bridge", 0), "qw": qw if isinstance(qw, (int, float)) else 999,
                    "rejected": reasons})
    out.sort(key=lambda r: (bool(r["rejected"]), -r["total"], -r["bridge"], r["qw"]))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="concepts JSON")
    ap.add_argument("--min", type=float, default=3, help="minimum score per test (default 3)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with open(a.src, encoding="utf-8") as f:
        concepts = json.load(f)
    if not isinstance(concepts, list) or not concepts:
        sys.exit("expected a non-empty JSON list of concepts")
    res = rank(concepts, a.min)
    if a.json:
        print(json.dumps(res, indent=1))
    else:
        for i, r in enumerate(res, 1):
            mark = "REJECT" if r["rejected"] else ("PICK  " if i == 1 else "ok    ")
            print("%s %2d/%d  %-40s %s, %s" % (mark, r["total"], r["max"], r["name"][:40], r["type"], r["format"]))
            for why in r["rejected"]:
                print("         - %s" % why)
    sys.exit(0 if any(not r["rejected"] for r in res) else 1)


if __name__ == "__main__":
    main()
