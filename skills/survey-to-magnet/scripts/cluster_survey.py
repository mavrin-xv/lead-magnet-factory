#!/usr/bin/env python3
"""Group free-text survey answers into pain themes and rank them for a lead magnet.

  python3 cluster_survey.py responses.csv -o outline.md
  python3 cluster_survey.py responses.csv --column "biggest challenge" --themes 4 --json themes.json
  python3 cluster_survey.py answers.json --column answer

Input: CSV (header row) or JSON (a list of objects, or a list of strings).
The answer column is auto-detected from its name (challenge, problem, struggle,
frustration, question, hardest...) or, failing that, the text column with the
longest average answer. Pass --column to choose it yourself. Pass --segment to
name a multiple-choice column (role, stage) whose values are counted per theme.

Method (deterministic, standard library only):
  1. Tokenise, drop stopwords, fold simple plurals, add two-word phrases.
  2. Greedy theme picking: the term in the most unassigned answers becomes a
     theme; every unassigned answer containing it joins; repeat. Terms found in
     more than 60% of answers are too generic to be themes.
  3. Score each theme: size (share of answers), depth (average words per answer:
     long, specific answers mark the people who feel the pain most) and intent
     (answers mentioning money, time lost, tries that failed, wanting help).
  4. Pick verbatim quotes: the deepest answers with intent words, trimmed.
  5. Suggest a format from the words people used (how/steps -> checklist or
     playbook; write/send/say -> swipe file; plan/set up -> template;
     cost/price/numbers -> calculator; why/understand -> mini-course).

The output is an outline for a human and the magnet-concept skill, not a
finished magnet. Fewer than 15 answers: themes are a hint, not a finding.
"""
import argparse
import csv
import json
import re
import sys
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to a legacy code page

STOP = set("""
a about above after again against all also am an and any are aren as at be because been before being below
between both but by can cannot could did do does doing don down during each even ever every few for from
further get gets getting got had has have having he her here hers him his how i if in into is isn it its
itself just keep know let like lot lots make makes many me more most much my myself need needs no nor not
now of off on once one only or other our ours out over own really right same say she should so some still
such than that the their them then there these they thing things think this those through to too try under
until up us very want wants was way we well were what when where which while who whom why will with
without would yes yet you your yours im ive dont cant doesnt didnt isnt thats theres whats biggest main
problem problems challenge challenges hard hardest difficult issue issues struggle struggling right now
always never often sometimes actually probably maybe kind sort enough around time times us able
""".split())

COLUMN_HINT = re.compile(r"challeng|problem|struggl|frustrat|pain|hardest|difficult|question|obstacle|blocker|worry|stuck|wish", re.I)
INTENT = re.compile(r"\b(pay|paid|paying|cost|costs|price|budget|spend|spent|money|waste|wasted|wasting|lose|losing|lost|"
                    r"hours?|every (day|week|month)|tried|try|hire|hired|help|course|tool|fix|afford|refund|cancel|late|behind)\b", re.I)
FORMATS = [
    ("calculator", r"\b(cost|price|pricing|budget|margin|numbers?|how much|roi|profit|forecast)\b"),
    ("swipe file", r"\b(write|writing|say|send|reply|message|email|script|words|caption|pitch)\b"),
    ("template", r"\b(plan|planning|set ?up|organi[sz]e|track|tracking|schedule|system|document)\b"),
    ("checklist", r"\b(steps?|process|launch|start|routine|forget|miss|check|consistent|every time)\b"),
    ("mini-course", r"\b(why|understand|learn|confus\w*|basics|know where|overwhelm\w*)\b"),
    ("playbook", r"\b(how|grow|get more|find|scale|build|first)\b"),
]


def tokens(text):
    words = [w for w in re.findall(r"[^\W\d_]+(?:'[^\W\d_]+)?", text.lower()) if len(w) > 2]
    words = [w.replace("'", "") for w in words]
    out = []
    for w in words:
        if w in STOP:
            continue
        if len(w) > 4 and w.endswith("ies"):
            w = w[:-3] + "y"
        elif len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.append(w)
    terms = set(out)
    terms.update("%s %s" % (a, b) for a, b in zip(out, out[1:]))
    return terms


def load(path, column):
    if path.lower().endswith(".json"):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if data and isinstance(data[0], str):
            return [{"answer": x} for x in data], "answer"
        rows = data
    else:
        rows = None
        for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                with open(path, encoding=enc, newline="") as f:
                    rows = list(csv.DictReader(f))
                break
            except UnicodeDecodeError:
                continue
        if rows is None:
            sys.exit("could not read %s" % path)
    if not rows:
        sys.exit("no rows in %s" % path)
    cols = list(rows[0].keys())
    if column:
        match = [c for c in cols if c.lower() == column.lower()] or [c for c in cols if column.lower() in c.lower()]
        if not match:
            sys.exit("column %r not found; columns: %s" % (column, ", ".join(cols)))
        return rows, match[0]
    hinted = [c for c in cols if COLUMN_HINT.search(c)]
    if hinted:
        return rows, hinted[0]

    def avg(c):
        vals = [str(r.get(c) or "") for r in rows]
        return sum(len(v) for v in vals) / max(1, len(vals))
    return rows, max(cols, key=avg)


def cluster(answers, max_themes, min_size):
    toks = [tokens(a) for a in answers]
    n = len(answers)
    df = Counter(t for ts in toks for t in ts)
    generic = {t for t, c in df.items() if c > 0.6 * n and n >= 5}
    unassigned = set(range(n))
    themes = []
    while len(themes) < max_themes and unassigned:
        counts = Counter(t for i in unassigned for t in toks[i] if t not in generic)
        if not counts:
            break
        # prefer phrases on ties, then alphabetical for determinism
        term, c = sorted(counts.items(), key=lambda kv: (-kv[1], -len(kv[0].split()), kv[0]))[0]
        if c < min_size:
            break
        members = sorted(i for i in unassigned if term in toks[i])
        co = Counter(t for i in members for t in toks[i] if t != term and t not in generic and t not in term.split())
        label_terms = [term] + [t for t, k in co.most_common(3) if k >= 2 and " " not in t][:2]
        themes.append({"term": term, "label": " / ".join(label_terms), "members": members})
        unassigned -= set(members)
    return themes, sorted(unassigned)


def score(themes, answers, n):
    depths = []
    for th in themes:
        texts = [answers[i] for i in th["members"]]
        th["count"] = len(texts)
        th["share"] = round(100.0 * len(texts) / n, 1)
        th["depth"] = round(sum(len(t.split()) for t in texts) / len(texts), 1)
        th["intent"] = round(100.0 * sum(1 for t in texts if INTENT.search(t)) / len(texts), 1)
        depths.append(th["depth"])
    max_share = max([t["share"] for t in themes] or [1])
    max_depth = max(depths or [1])
    for th in themes:
        th["score"] = round(50 * th["share"] / max_share + 30 * th["depth"] / max_depth + 20 * th["intent"] / 100, 1)
        texts = [answers[i] for i in th["members"]]
        ranked = sorted(texts, key=lambda t: (bool(INTENT.search(t)), len(t.split())), reverse=True)
        th["quotes"] = [q if len(q) <= 240 else q[:237].rsplit(" ", 1)[0] + "..." for q in ranked[:3]]
        joined = " ".join(texts).lower()
        hits = [(len(re.findall(rx, joined)), name) for name, rx in FORMATS]
        best = max(hits)
        th["format"] = best[1] if best[0] else "playbook"
    themes.sort(key=lambda t: -t["score"])
    return themes


def segments(rows, col, seg_col, themes, idx):
    if not seg_col:
        return
    for th in themes:
        c = Counter(str(rows[idx[i]].get(seg_col) or "unknown").strip() or "unknown" for i in th["members"])
        th["segments"] = dict(c.most_common())


def hook_line(quotes):
    """First sentence of 6+ words from the quotes, else the first quote."""
    for q in quotes:
        for sent in re.split(r"(?<=[.!?])\s+", q):
            if len(sent.split()) >= 6:
                return sent.rstrip(".!?")
    return quotes[0].rstrip(".!?")


def outline(themes, other, n, col, source):
    L = ["# Survey themes: %s" % source, "",
         "%d answers from column %r. %d theme(s), %d answer(s) unthemed." % (n, col, len(themes), len(other)), ""]
    if n < 15:
        L += ["> Fewer than 15 answers. Treat these themes as hints and read every answer yourself.", ""]
    L += ["| # | Theme | Answers | Share | Avg words | Intent | Score | Suggested format |",
          "|---|---|---|---|---|---|---|---|"]
    for k, th in enumerate(themes, 1):
        L.append("| %d | %s | %d | %s%% | %s | %s%% | %s | %s |" % (k, th["label"], th["count"], th["share"], th["depth"], th["intent"], th["score"], th["format"]))
    L.append("")
    for k, th in enumerate(themes, 1):
        L += ["## %d. %s" % (k, th["label"]), ""]
        if th.get("segments"):
            L.append("Who: " + ", ".join("%s %d" % kv for kv in th["segments"].items()))
            L.append("")
        L.append("In their words:")
        L.append("")
        for q in th["quotes"]:
            L.append('- "%s"' % q.replace("\n", " "))
        L += ["", "Draft hook (rewrite before use): \"%s.\" Here is what fixes it." % hook_line(th["quotes"]), "",
              "Suggested format: %s. Next: run magnet-concept with this theme and these quotes." % th["format"], ""]
    if themes:
        top = themes[0]
        L += ["## Pick", "", "Start with theme 1, **%s**: %d answers (%s%%), %s words on average, %s%% mention money, time or failed tries." % (
            top["label"], top["count"], top["share"], top["depth"], top["intent"]), ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="CSV or JSON file with survey answers")
    ap.add_argument("--column", help="answer column (default: auto-detect)")
    ap.add_argument("--segment", help="multiple-choice column to break each theme down by")
    ap.add_argument("--themes", type=int, default=5, help="max themes (default 5)")
    ap.add_argument("--min-size", type=int, default=2, help="min answers per theme (default 2)")
    ap.add_argument("-o", "--out", help="write the markdown outline here (default: stdout)")
    ap.add_argument("--json", help="also write themes as JSON here")
    a = ap.parse_args()
    rows, col = load(a.src, a.column)
    idx, answers = [], []
    for i, r in enumerate(rows):
        v = str(r.get(col) or "").strip()
        if len(v.split()) >= 2:
            idx.append(i)
            answers.append(v)
    if not answers:
        sys.exit("column %r has no answers of 2+ words" % col)
    themes, other = cluster(answers, a.themes, a.min_size)
    themes = score(themes, answers, len(answers))
    segments(rows, col, a.segment, themes, idx)
    md = outline(themes, other, len(answers), col, a.src.replace("\\", "/").split("/")[-1])
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(md + "\n")
        print("wrote %s: %d themes from %d answers" % (a.out, len(themes), len(answers)))
    else:
        print(md)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"column": col, "answers": len(answers), "unthemed": [answers[i] for i in other],
                       "themes": [{k: v for k, v in t.items() if k != "members"} for t in themes]}, f, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
