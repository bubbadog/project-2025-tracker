#!/usr/bin/env python3
"""Red-team review of a run's output before it is exported to the repository.

The daily run writes to the working database; a coordinating session exports it
here. This script compares the exported dump with the committed record and applies
the review rules the maintainers use (see MAINTAINING.md):

  BLOCKING (exit 1; do not export until fixed in the database or by hand):
    - a stage or progress change without an independent review dated the run day
    - a field present in the committed record that the new record drops
    - a source on a lead-only host (encyclopedia, newsletter, advocacy group, aggregator)
      unless its title marks it as a hosted copy of an official document
    - a timeline event or court_status URL that is not in the record's sources
    - a dash (em or en) or a personal identifier in public text
    - a model or tool name in public text (review.model is provenance and is allowed)
  FIXABLE (exit 2 without --fix; fixed in place with --fix, then exit 0):
    - a changed record with no history note dated the run day (a note is composed from
      the run log's own change note for that record)
  INFORMATIONAL (printed, never affects the exit status):
    - query URLs in red-team evidence or source checks with unencoded brackets
    - confidence label moves, so the digest can list them

Usage:
  python3 scripts/review_run.py DUMP_DIR --date YYYY-MM-DD [--fix] [--json OUT]

DUMP_DIR has the layout the export produces: items/*.json, runs/*.json, meta/*.json.
The committed record is read from data/ next to this script. Nothing is written to
data/ by this script; --fix edits the dump so that import_dump.py carries the fix.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

PUBLIC_EXCLUDE = {"review", "history", "redteam"}
MINOR = {"history", "related_ids", "updated_at", "last_checked"}
DASHES = ("—", "–")
MODEL_WORDS = ("Claude", "Opus", "Sonnet", "Fable", "Muse ", "ChatGPT", "Perplexity")
# Retrieval-method wording (owner decision 2026-10-28): public text says what was read and where
# (host, kind of copy, date), never how (tools, browsers, proxies, tool errors). Narrow phrases only,
# so records about browsers, proxy voting or tunnels are not caught.
METHOD_RE = re.compile(
    r"\b(browser retrieval|owner browser|in a browser|automated fetch\w*|automated access|fetch tools?|"
    r"page fetch tool|research tools?|refuses? (?:automated|fetch)\w*|refused fetch\w*|blocked to automated|"
    r"client[_ ]error|proxy (?:refused|error|returned)|tunnel failure)\b",
    re.I,
)
# Hosts that are leads, never sources (owner decision 2026-10-23). Research institutions,
# think tanks, trade press and law firms are not on this list on purpose.
LEAD_HOSTS = (
    "wikipedia.org", "substack.com", "ballotpedia.org", "citizen.org", "aclu.org", "acludc.org",
    "democracyforward.org", "lawyerscommittee.org", "nwlc.org", "naacpldf.org", "splcenter.org",
    "afge.org", "aflcio.org", "afscme.org", "nteu.org", "youthlaw.org", "immpolicytracking.org",
    "fwd.us", "edgi.org", "nrdc.org", "sierraclub.org", "earthjustice.org", "heritage.org",
    "americanprogress.org", "fedtools.com", "mondaq.com", "lexblog.com", "jdsupra.com",
    "nga.org", "nafsa.org", "acenet.edu", "naicu.edu", "aera.net", "afsa.org", "csba.org",
)
COPY_RE = re.compile(r"copy hosted|copy posted|hosted copy|copy of|\(copy|filed copy", re.I)


def load_dir(path: str) -> dict[str, dict]:
    out = {}
    for f in glob.glob(os.path.join(path, "*.json")):
        with open(f, encoding="utf-8") as fh:
            out[os.path.basename(f)[:-5]] = json.load(fh)
    return out


def forbidden_words() -> list[str]:
    words = []
    env = os.environ.get("TRACKER_FORBIDDEN_WORDS", "")
    words += [w.strip() for w in env.split(",") if w.strip()]
    priv = os.path.join(ROOT, ".private", "forbidden_words.txt")
    if os.path.exists(priv):
        with open(priv, encoding="utf-8") as fh:
            words += [l.strip() for l in fh if l.strip() and not l.startswith("#")]
    return words


def public_text(rec: dict) -> str:
    return json.dumps({k: v for k, v in rec.items() if k not in PUBLIC_EXCLUDE}, ensure_ascii=False)


def host(u: str) -> str:
    return urlparse(u).netloc.lower().removeprefix("www.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dump")
    ap.add_argument("--date", required=True)
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--json")
    args = ap.parse_args()

    new_items = load_dir(os.path.join(args.dump, "items"))
    runs = load_dir(os.path.join(args.dump, "runs"))
    old_items = {}
    for k in new_items:
        p = os.path.join(DATA, "items", f"{k}.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                old_items[k] = json.load(fh)
    run_notes: dict[str, str] = {}
    for r in runs.values():
        for c in r.get("changes") or []:
            run_notes.setdefault(c.get("id", ""), c.get("note", ""))

    blocking: list[str] = []
    fixable: list[str] = []
    info: list[str] = []
    fixed: list[str] = []
    words = forbidden_words()
    stage_changes = []
    label_moves = []
    changed = 0

    for k, n in sorted(new_items.items()):
        o = old_items.get(k)
        pub = public_text(n)
        for d in DASHES:
            if d in pub:
                blocking.append(f"{k}: dash in public text")
                break
        if words and re.search(r"\b(" + "|".join(re.escape(w.lower()) for w in words) + r")\b", pub, re.I):
            # same matcher as validate.py: whole words, any case ("adjusting" is not a hit)
            blocking.append(f"{k}: personal identifier in public text")
        m = METHOD_RE.search(pub)
        if m:
            blocking.append(f"{k}: retrieval-method wording in public text ('{m.group(0)}')")
        for w in MODEL_WORDS:
            if re.search(r"\b" + re.escape(w.strip()) + r"\b", pub):
                blocking.append(f"{k}: model or tool name '{w.strip()}' in public text")
        src_urls = {s.get("url") for s in n.get("sources") or []}
        for s in n.get("sources") or []:
            h = host(s.get("url") or "")
            if any(h == lh or h.endswith("." + lh) for lh in LEAD_HOSTS) and not COPY_RE.search(
                (s.get("title") or "") + " " + (s.get("publisher") or "")
            ):
                blocking.append(f"{k}: source on lead-only host {h}: {s.get('title','')[:60]}")
        for t in n.get("timeline") or []:
            if t.get("url") and t["url"] not in src_urls:
                blocking.append(f"{k}: event {t.get('date')} cites a URL not in sources")
        cs = n.get("court_status")
        if isinstance(cs, dict) and cs.get("url") and cs["url"] not in src_urls:
            blocking.append(f"{k}: court_status cites a URL not in sources")
        for coll, entries in (("redteam.evidence", (n.get("redteam") or {}).get("evidence") or []),
                              ("review.source_checks", (n.get("review") or {}).get("source_checks") or [])):
            for e in entries:
                u = e.get("url") if isinstance(e, dict) else None
                if isinstance(u, str):
                    if any(ch in u for ch in ' "'):
                        blocking.append(f"{k}: {coll} URL has a space or quote")
                    elif any(ch in u for ch in "[]"):
                        info.append(f"{k}: {coll} URL has unencoded brackets")
        if o is None:
            info.append(f"{k}: new record")
            rv = (n.get("review") or {}).get("reviewed_at")
            if rv != args.date:
                blocking.append(f"{k}: new record without a review dated {args.date}")
            continue
        if json.dumps(o, sort_keys=True) == json.dumps(n, sort_keys=True):
            continue
        changed += 1
        lost = [f for f in o if f not in n]
        if lost:
            blocking.append(f"{k}: fields lost {lost}")
        diff = {f for f in set(o) | set(n) if o.get(f) != n.get(f)}
        rv = (n.get("review") or {}).get("reviewed_at")
        if o.get("stage") != n.get("stage") or o.get("progress") != n.get("progress"):
            stage_changes.append((k, o.get("stage"), o.get("progress"), n.get("stage"), n.get("progress"), n.get("confidence")))
            if rv != args.date:
                blocking.append(f"{k}: stage or progress changed without a review dated {args.date}")
        if o.get("confidence_label") != n.get("confidence_label"):
            label_moves.append((k, o.get("confidence_label"), n.get("confidence_label"), o.get("confidence"), n.get("confidence")))
        substantive = diff - MINOR - {"significance"}
        if substantive and not any(h.get("date") == args.date for h in n.get("history") or [] if isinstance(h, dict)):
            if args.fix:
                note = run_notes.get(k) or "Checked by the daily run with no new action found; public fields updated."
                note = note.replace("Watch item: ", "Watch item check: ").rstrip(".") + ". No change of stage or confidence." if o.get("stage") == n.get("stage") else note
                if any(d in note for d in DASHES) or "http" in note:
                    blocking.append(f"{k}: cannot compose a history note from the run log (dash or URL)")
                else:
                    n.setdefault("history", []).append({"date": args.date, "note": note})
                    n["updated_at"] = args.date
                    with open(os.path.join(args.dump, "items", f"{k}.json"), "w", encoding="utf-8") as fh:
                        json.dump(n, fh, ensure_ascii=False, indent=2, sort_keys=True)
                    fixed.append(k)
            else:
                fixable.append(f"{k}: changed fields {sorted(substantive)} without a history note dated {args.date}")

    for rid, r in runs.items():
        rtext = json.dumps(r, ensure_ascii=False)
        if any(d in rtext for d in DASHES):
            blocking.append(f"runs/{rid}: dash")
        for w in words:
            if w and w in rtext:
                blocking.append(f"runs/{rid}: personal identifier")
        for w in MODEL_WORDS:
            if re.search(r"\b" + re.escape(w.strip()) + r"\b", rtext):
                blocking.append(f"runs/{rid}: model or tool name in the run log")
        listed = {c.get("id") for c in r.get("changes") or []}
        missing = [k for k, n in new_items.items() if k in old_items and k not in listed
                   and (set(old_items[k]) | set(n)) and any(old_items[k].get(f) != n.get(f) for f in set(old_items[k]) | set(n) if f not in MINOR | {"significance", "uncertainties"})]
        if missing and r.get("kind") == "daily":
            info.append(f"runs/{rid}: changed records not listed in changes: {sorted(missing)}")

    report = {
        "date": args.date, "records_in_dump": len(new_items), "changed": changed,
        "stage_changes": stage_changes, "confidence_label_moves": label_moves,
        "blocking": blocking, "fixable": fixable, "fixed": fixed, "info": info,
        "runs": sorted(runs),
    }
    print(f"review {args.date}: {len(new_items)} records in dump, {changed} changed, "
          f"{len(stage_changes)} stage changes, {len(label_moves)} confidence label moves")
    for s in stage_changes:
        print(f"  STAGE {s[0]}: {s[1]}/{s[2]} -> {s[3]}/{s[4]} (confidence {s[5]})")
    for m in label_moves:
        print(f"  LABEL {m[0]}: {m[1]} -> {m[2]} ({m[3]} -> {m[4]})")
    for b in blocking:
        print(f"  BLOCKING {b}")
    for f in fixable:
        print(f"  FIXABLE {f}")
    for f in fixed:
        print(f"  FIXED {f}: history note added from the run log")
    for i in info:
        print(f"  INFO {i}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
    if blocking:
        return 1
    if fixable:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
