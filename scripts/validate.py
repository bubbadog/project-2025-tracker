#!/usr/bin/env python3
"""Validate every record and meta document under data/.

Runs in CI on every pull request. A failure here blocks the merge. The checks are
the same rules the research runs follow, so a hand-edited record is held to the
same standard as a machine-written one.

Exit code 0: all checks pass. 1: at least one error. Warnings never fail the build.

Usage: python3 scripts/validate.py [--strict]   (--strict turns warnings into errors)
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

STAGES = {
    "not_started": (0, 0),
    "proposed": (5, 20),
    "in_progress": (25, 60),
    "implemented": (65, 90),
    "completed": (100, 100),
    "blocked": (0, 90),
    "diverged": (0, 0),
    "pending": (0, 0),
}
LABELS = {"high", "medium", "low", "unverified"}
MECHANISMS = {"executive_order", "agency_rule", "agency_action", "legislation", "appointment", "litigation", "mixed"}
MATCHES = {"direct", "partial", "parallel"}
CONGRESS = {"yes", "no", "partial"}
EVENT_KINDS = {"primary", "court", "news", "tracker"}
COURT_STATES = {"enjoined", "stayed", "vacated", "upheld", "dismissed", "pending"}
REQUIRED = [
    "id", "chapter", "agency", "title", "proposal", "pages", "stage", "progress", "match",
    "status_summary", "timeline", "sources", "confidence", "confidence_label",
    "confidence_reason", "review", "updated_at", "last_checked", "history",
]
ID_RE = re.compile(r"^c\d\d-\d\d$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# Words that must never appear in public data: the project is published under
# its own name, not a person's. The list itself is private, so it never lives in
# this file. It is read from the environment variable TRACKER_FORBIDDEN_WORDS
# (comma-separated; in CI this is a repository secret, which GitHub masks in
# logs) or from the gitignored file .private/forbidden_words.txt (one term per
# line). Matches are reported by record and field only, never by the word.
DASHES = ("\u2014", "\u2013")  # em dash, en dash


def load_forbidden() -> "re.Pattern[str] | None":
    terms: list[str] = []
    env = os.environ.get("TRACKER_FORBIDDEN_WORDS", "")
    terms += [t.strip() for t in env.split(",") if t.strip()]
    local = os.path.join(ROOT, ".private", "forbidden_words.txt")
    if os.path.exists(local):
        with open(local, encoding="utf-8") as f:
            terms += [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    terms = sorted({t.lower() for t in terms})
    if not terms:
        return None
    return re.compile(r"\b(" + "|".join(re.escape(t) for t in terms) + r")\b", re.I)


FORBIDDEN_RE = load_forbidden()


def forbidden_hit(text: str) -> bool:
    return bool(FORBIDDEN_RE and FORBIDDEN_RE.search(text))


def label_for(conf: int) -> str:
    return "high" if conf >= 80 else "medium" if conf >= 55 else "low" if conf > 20 else "unverified"


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notices: list[str] = []  # informational; never fail the build, even with --strict

    def notice(self, msg: str) -> None:
        self.notices.append(msg)

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def check_url(u: object, where: str, rep: Report) -> None:
    if not isinstance(u, str) or not u.startswith("https://") or " " in u:
        rep.err(f"{where}: url must be https with no spaces, got {u!r}")


def check_date(d: object, where: str, rep: Report, today: str) -> None:
    if not isinstance(d, str) or not DATE_RE.match(d):
        rep.err(f"{where}: date must be YYYY-MM-DD, got {d!r}")
        return
    if d > today:
        rep.err(f"{where}: date {d} is in the future")


def validate_item(it: dict, fname: str, rep: Report, today: str, ids: set[str]) -> None:
    where = fname
    for k in REQUIRED:
        if k == "timeline" and it.get("stage") in ("not_started", "pending") and it.get(k) == []:
            continue  # a no-action record may legitimately have no dated action
        if k not in it or it[k] in (None, "", []):
            rep.err(f"{where}: missing {k}")
    i = str(it.get("id", ""))
    if not ID_RE.match(i):
        rep.err(f"{where}: bad id {i!r}")
    if fname != f"{i}.json":
        rep.err(f"{where}: file name does not match id {i}")
    if str(it.get("chapter", "")) != i[1:3]:
        rep.err(f"{where}: chapter {it.get('chapter')!r} does not match id")
    if len(str(it.get("title", ""))) > 90:
        rep.err(f"{where}: title longer than 90 characters")
    stage = it.get("stage")
    if stage not in STAGES:
        rep.err(f"{where}: unknown stage {stage!r}")
    else:
        lo, hi = STAGES[stage]
        try:
            p = int(it.get("progress", -1))
        except (TypeError, ValueError):
            p = -1
        if not (lo <= p <= hi):
            rep.err(f"{where}: progress {p} outside the {stage} band {lo} to {hi}")
    if it.get("mechanism") not in MECHANISMS:
        rep.warn(f"{where}: mechanism {it.get('mechanism')!r} not in the allowed set")
    if it.get("match") not in MATCHES:
        rep.err(f"{where}: match {it.get('match')!r} not in the allowed set")
    if it.get("requires_congress") not in CONGRESS:
        rep.warn(f"{where}: requires_congress {it.get('requires_congress')!r} not in the allowed set")
    conf = it.get("confidence")
    if not isinstance(conf, (int, float)) or not 0 <= conf <= 100:
        rep.err(f"{where}: confidence must be 0 to 100")
    else:
        if it.get("confidence_label") not in LABELS:
            rep.err(f"{where}: confidence_label {it.get('confidence_label')!r} not in the allowed set")
        elif it["confidence_label"] != label_for(int(conf)):
            rep.err(f"{where}: confidence_label {it['confidence_label']} does not match confidence {conf}")
        if stage == "not_started" and conf > 70:
            rep.err(f"{where}: a no-action record may not exceed confidence 70 (50 without a documented systematic check)")
        if stage == "not_started" and conf > 50:
            sc = (it.get("review") or {}).get("source_checks") or []
            if len(sc) < 4:
                rep.err(f"{where}: no-action confidence above 50 requires the documented systematic check in review.source_checks")
    for e in it.get("timeline") or []:
        if not isinstance(e, dict):
            rep.err(f"{where}: timeline entry is not an object")
            continue
        check_date(e.get("date"), f"{where} timeline", rep, today)
        check_url(e.get("url"), f"{where} timeline", rep)
        if e.get("kind") not in EVENT_KINDS:
            rep.warn(f"{where}: timeline kind {e.get('kind')!r} not in the allowed set")
        if not e.get("event"):
            rep.err(f"{where}: timeline entry without an event description")
    source_urls = {s.get("url") for s in (it.get("sources") or []) if isinstance(s, dict)}
    for e in it.get("timeline") or []:
        if isinstance(e, dict) and e.get("url") and e["url"] not in source_urls:
            rep.warn(f"{where}: timeline event {e.get('date')} cites a URL that is not listed in sources")
    cs = it.get("court_status")
    if isinstance(cs, dict) and cs.get("url") and cs["url"] not in source_urls:
        rep.warn(f"{where}: court_status cites a URL that is not listed in sources")
    # Query URLs recorded in red-team evidence or review.source_checks should be percent-encoded
    # (brackets, quotes and spaces); the page renders them as links. Informational only.
    for coll, entries in (("redteam.evidence", (it.get("redteam") or {}).get("evidence") or []),
                          ("review.source_checks", (it.get("review") or {}).get("source_checks") or [])):
        for ent in entries:
            u = ent.get("url") if isinstance(ent, dict) else None
            if isinstance(u, str) and any(ch in u for ch in "[]\" "):
                rep.notice(f"{where}: {coll} URL has unencoded brackets, quotes or spaces")
    for s in it.get("sources") or []:
        if not isinstance(s, dict):
            rep.err(f"{where}: source is not an object")
            continue
        check_url(s.get("url"), f"{where} sources", rep)
        if not s.get("title"):
            rep.warn(f"{where}: source without a title")
    if stage in ("implemented", "completed", "in_progress", "blocked") and not it.get("timeline"):
        rep.err(f"{where}: stage {stage} needs at least one dated, sourced event")
    unc = it.get("uncertainties", "")
    if unc is not None and not isinstance(unc, str):
        rep.err(f"{where}: uncertainties must be a string")
    if isinstance(unc, str) and "http" in unc:
        rep.err(f"{where}: uncertainties must not carry raw URLs (name the host instead)")
    for h in it.get("history") or []:
        if not isinstance(h, dict) or not DATE_RE.match(str(h.get("date", ""))) or not h.get("note"):
            rep.err(f"{where}: history entries need a date and a note")
        elif "http" in str(h.get("note")):
            rep.err(f"{where}: history notes must not carry raw URLs")
    rv = it.get("review") or {}
    if not isinstance(rv, dict) or not rv.get("reviewed_at"):
        rep.err(f"{where}: review block with reviewed_at is required (every record is independently reviewed)")
    else:
        check_date(rv.get("reviewed_at"), f"{where} review", rep, today)
        for c in rv.get("source_checks") or []:
            if isinstance(c, dict) and c.get("url"):
                check_url(c.get("url"), f"{where} review.source_checks", rep)
    cs = it.get("court_status")
    if cs is not None:
        if not isinstance(cs, dict) or cs.get("state") not in COURT_STATES:
            rep.err(f"{where}: court_status must be an object with a known state")
        elif cs.get("url"):
            check_url(cs.get("url"), f"{where} court_status", rep)
    g = it.get("significance")
    if g is not None:
        if not isinstance(g, dict) or not all(k in g for k in ("R", "M", "B", "F", "weight")):
            rep.err(f"{where}: significance needs R, M, B, F and weight")
        else:
            for k in ("R", "M", "B", "F"):
                if not (1 <= float(g[k]) <= 3):
                    rep.err(f"{where}: significance {k} outside 1 to 3")
            exp = round((float(g["R"]) + float(g["M"]) + float(g["B"]) + float(g["F"])) / 4, 3)
            if abs(exp - round(float(g["weight"]), 3)) > 0.01:
                rep.err(f"{where}: significance weight {g['weight']} is not the mean of the four scores ({exp})")
    for r in it.get("related_ids") or []:
        if r not in ids:
            rep.err(f"{where}: related_ids points to unknown record {r}")
    for r in it.get("restates_ids") or []:
        if r not in ids:
            rep.err(f"{where}: restates_ids points to unknown record {r}")
    for d in ("updated_at", "last_checked"):
        if it.get(d):
            check_date(it[d], f"{where} {d}", rep, today)
    text = json.dumps(it, ensure_ascii=False)
    if any(ch in text for ch in DASHES):
        rep.err(f"{where}: em or en dash found; use commas, colons, semicolons or parentheses")
    if forbidden_hit(text):
        rep.err(f"{where}: personal identifier found; the project is published anonymously")


def load_schema_validator():
    """data/schema/item.schema.json, checked when the jsonschema package is
    installed (CI installs it; locally it is optional)."""
    try:
        import jsonschema  # type: ignore
    except ImportError:
        print("NOTE jsonschema not installed; the JSON Schema check is skipped (pip install jsonschema)")
        return None
    with open(os.path.join(DATA, "schema", "item.schema.json"), encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--notices", action="store_true", help="list informational notices (never affect the exit status)")
    args = ap.parse_args()
    rep = Report()
    today = dt.date.today().isoformat()
    if FORBIDDEN_RE is None:
        print("NOTE no private identifier list loaded (TRACKER_FORBIDDEN_WORDS or .private/forbidden_words.txt); that check is skipped")
    items_dir = os.path.join(DATA, "items")
    files = sorted(f for f in os.listdir(items_dir) if f.endswith(".json"))
    items: dict[str, dict] = {}
    for fname in files:
        try:
            with open(os.path.join(items_dir, fname), encoding="utf-8") as f:
                it = json.load(f)
        except json.JSONDecodeError as e:
            rep.err(f"{fname}: invalid JSON ({e})")
            continue
        items[str(it.get("id"))] = it
    ids = set(items)
    schema_validator = load_schema_validator()
    for fname in files:
        it = items.get(fname[:-5])
        if it is not None:
            validate_item(it, fname, rep, today, ids)
            if schema_validator is not None:
                for e in schema_validator.iter_errors(it):
                    path = "/".join(str(p) for p in e.absolute_path) or "(root)"
                    rep.err(f"{fname}: schema: {path}: {e.message[:160]}")
    # symmetry of cross-references
    for i, it in items.items():
        for r in it.get("related_ids") or []:
            if r in items and i not in (items[r].get("related_ids") or []):
                rep.err(f"{i}: related_ids link to {r} is not mirrored on {r}")
    # headline counts in meta/state must match the records
    with open(os.path.join(DATA, "meta", "state.json"), encoding="utf-8") as f:
        state = json.load(f)
    counted = [it for it in items.values() if it.get("tracked") is not False and str(it.get("chapter")) != "00" and not it.get("restates_ids")]
    counts = collections.Counter(it.get("stage") for it in counted)
    if state.get("total") != len(counted):
        rep.err(f"meta/state.total is {state.get('total')} but {len(counted)} records are counted")
    if state.get("counts") != dict(counts):
        rep.err(f"meta/state.counts {state.get('counts')} differ from the records {dict(counts)}")
    for k in ("as_of", "built_at"):
        if state.get(k):
            check_date(state[k], f"meta/state.{k}", rep, today)
    stext = json.dumps(state, ensure_ascii=False)
    if any(ch in stext for ch in DASHES):
        rep.err("meta/state: em or en dash found")
    if forbidden_hit(stext):
        rep.err("meta/state: personal identifier found")
    # runs
    runs_dir = os.path.join(DATA, "runs")
    for fname in sorted(os.listdir(runs_dir)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(runs_dir, fname), encoding="utf-8") as f:
            run = json.load(f)
        if run.get("id") != fname[:-5]:
            rep.err(f"runs/{fname}: id does not match file name")
        check_date(run.get("date"), f"runs/{fname}", rep, today)
        for c in run.get("changes") or []:
            if c.get("id") not in ids:
                rep.err(f"runs/{fname}: change refers to unknown record {c.get('id')}")
            if c.get("url"):
                check_url(c.get("url"), f"runs/{fname} change {c.get('id')}", rep)
        rtext = json.dumps(run, ensure_ascii=False)
        if any(ch in rtext for ch in DASHES) or forbidden_hit(rtext):
            rep.err(f"runs/{fname}: dash or personal identifier found")

    if rep.notices:
        print(f"NOTICE {len(rep.notices)} evidence or source-check URL(s) with unencoded characters (informational; run with --notices to list)")
        if getattr(args, "notices", False):
            for n in rep.notices:
                print(f"NOTICE {n}")
    for w in rep.warnings:
        print(f"WARN {w}")
    for e in rep.errors:
        print(f"ERROR {e}")
    in_effect = sum(1 for it in counted if it.get("stage") in ("implemented", "completed"))
    print(f"records {len(items)}, counted {len(counted)}, in effect {in_effect}, errors {len(rep.errors)}, warnings {len(rep.warnings)}")
    if rep.errors or (args.strict and rep.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
