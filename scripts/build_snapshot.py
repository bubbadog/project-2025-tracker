#!/usr/bin/env python3
"""Assemble site/snapshot.json from the files under data/.

The site is static: index.html fetches snapshot.json next to it. The snapshot is
never committed; CI builds it from data/ on every push and deploy, so the data
files are the single source of truth.

Usage: python3 scripts/build_snapshot.py [--out site/snapshot.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def load_dir(path: str) -> list[dict]:
    out = []
    for name in sorted(os.listdir(path)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(path, name), encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def build() -> dict:
    with open(os.path.join(DATA, "meta", "state.json"), encoding="utf-8") as f:
        meta = json.load(f)
    with open(os.path.join(DATA, "meta", "chapters.json"), encoding="utf-8") as f:
        chapters = json.load(f)
    items = load_dir(os.path.join(DATA, "items"))
    runs = load_dir(os.path.join(DATA, "runs"))
    items.sort(key=lambda i: i["id"])
    runs.sort(key=lambda r: (r.get("date", ""), r.get("id", "")))
    return {"meta": meta, "chapters": chapters, "items": items, "runs": runs}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "site", "snapshot.json"))
    args = ap.parse_args()
    snap = build()
    text = json.dumps(snap, ensure_ascii=False, separators=(",", ":"))
    if "\u2014" in text or "\u2013" in text:
        print("em or en dash found in data; refusing to build", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"wrote {args.out}: {len(snap['items'])} items, {len(snap['runs'])} runs, {len(text.encode())} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
