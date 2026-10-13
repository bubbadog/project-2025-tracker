#!/usr/bin/env python3
"""Import a dump of the working database into data/.

The research runs keep a working database with the collections items/{id},
meta/{state,...} and runs/{id}. A dump is a directory with one JSON file per
document under items/, meta/ and runs/ (the layout the runs' export produces).
This script writes those documents into data/ in the repository's canonical
form (pretty-printed, keys sorted, trailing newline), so that a diff shows only
real changes and a pull request can carry the run's output.

Only public documents are imported: items, meta/state, meta/chapters,
meta/sig_raters and runs. Private working documents (meta/backlog,
meta/guidance, meta/leads, requests) are skipped on purpose.

Usage:
  python3 scripts/import_dump.py DUMP_DIR [--prune]

--prune removes records under data/items/ that are absent from the dump
(records are normally never deleted; a dropped record keeps tracked: false).
Exit status is 1 if the dump contains no items, so an empty export cannot wipe
the record.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
PUBLIC_META = {"state", "chapters", "sig_raters"}


def dump_json(obj: object, path: str) -> bool:
    text = json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    old = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = f.read()
    if old == text:
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return True


def load_dir(path: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not os.path.isdir(path):
        return out
    for name in sorted(os.listdir(path)):
        if name.endswith(".json"):
            with open(os.path.join(path, name), encoding="utf-8") as f:
                out[name[:-5]] = json.load(f)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dump_dir")
    ap.add_argument("--prune", action="store_true")
    args = ap.parse_args()

    items = load_dir(os.path.join(args.dump_dir, "items"))
    if not items:
        print("dump has no items; refusing to import", file=sys.stderr)
        return 1
    changed = 0
    for key, it in items.items():
        if it.get("id") != key:
            print(f"items/{key}: id field is {it.get('id')!r}; skipped", file=sys.stderr)
            continue
        changed += dump_json(it, os.path.join(DATA, "items", f"{key}.json"))
    if args.prune:
        for name in os.listdir(os.path.join(DATA, "items")):
            if name.endswith(".json") and name[:-5] not in items:
                os.remove(os.path.join(DATA, "items", name))
                changed += 1
    meta = load_dir(os.path.join(args.dump_dir, "meta"))
    for key, doc in meta.items():
        if key in PUBLIC_META:
            changed += dump_json(doc, os.path.join(DATA, "meta", f"{key}.json"))
    runs = load_dir(os.path.join(args.dump_dir, "runs"))
    for key, run in runs.items():
        if run.get("id") != key:
            print(f"runs/{key}: id field is {run.get('id')!r}; skipped", file=sys.stderr)
            continue
        changed += dump_json(run, os.path.join(DATA, "runs", f"{key}.json"))
    print(f"imported {len(items)} items, {len([k for k in meta if k in PUBLIC_META])} meta documents, {len(runs)} runs; {changed} files changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
