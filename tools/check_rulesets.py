#!/usr/bin/env python3
"""Fail if .github/rulesets/*.json differ from the rulesets GitHub enforces.

Rule: a ruleset change and its file change travel in the same pull request.
Needs GH_TOKEN (the workflow's own read token is enough) and REPO (owner/name).
The public API omits bypass lists, so a change to who may bypass is invisible
here; review those by hand in Settings, Rules, Rulesets.
"""
from __future__ import annotations

import glob
import json
import os
import sys
import urllib.request

IGNORE = {"id", "node_id", "created_at", "updated_at", "_links", "current_user_can_bypass", "bypass_actors", "source", "source_type"}


def api(path: str) -> object:
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def strip(o: object) -> object:
    if isinstance(o, dict):
        return {k: strip(v) for k, v in sorted(o.items()) if k not in IGNORE}
    if isinstance(o, list):
        return [strip(x) for x in o]
    return o


def main() -> int:
    repo = os.environ["REPO"]
    live = {r["name"]: strip(api(f"/repos/{repo}/rulesets/{r['id']}")) for r in api(f"/repos/{repo}/rulesets")}
    files = {}
    for path in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", ".github", "rulesets", "*.json"))):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        files[d["name"]] = strip(d)
    bad = 0
    for name in sorted(set(live) | set(files)):
        if name not in live:
            print(f"MISSING on GitHub: {name}")
            bad += 1
        elif name not in files:
            print(f"MISSING in repo: {name}")
            bad += 1
        elif live[name] != files[name]:
            print(f"DIFFERS: {name}")
            print("  file:", json.dumps(files[name], sort_keys=True))
            print("  live:", json.dumps(live[name], sort_keys=True))
            bad += 1
        else:
            print(f"ok: {name}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
