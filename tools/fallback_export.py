#!/usr/bin/env python3
"""Fallback export: publish a review session's commits when the automation
account cannot push.

The normal export path is a pull request opened and squash-merged by the
automation account (MAINTAINING.md section 6). When that account cannot reach
GitHub (suspended, signed out, token refused), the review session finishes the
review, commits locally with the project identity and hands the maintainer a
git bundle. This tool is how the maintainer publishes that bundle without
putting a personal name on `main`:

  * the commits keep the project identity as author AND committer, so the
    history on `main` reads exactly as an automated export would;
  * the maintainer pushes them as a fast-forward of `main`, which the pull
    request ruleset allows only for the repository admin (bypass "always");
  * because that push skips the pull request checks, this tool runs the same
    checks locally first (`validate --strict` with the private identifier
    list, `build_snapshot`, the browser test) and refuses to push on any
    failure.

Usage (from a clean clone of the repository, on any branch; the tool works on
the repository of the current directory, wherever the file itself is):

  python3 tools/fallback_export.py review-2026-11-08.bundle            # dry run
  python3 tools/fallback_export.py review-2026-11-08.bundle --push     # publish

Options:
  --ref NAME      the bundle head to publish (default: the only head, or the
                  one starting with refs/heads/review/)
  --skip-ui       skip the browser test (only when Node or Chromium is not
                  available; check.yml runs it again on main after the push)
  --chrome PATH   Chromium or Chrome executable for the browser test
  --port N        port for the local test server (default 8765)
  --no-wait       after --push, do not wait for the checks and the deploy on main
  --wait-minutes N  how long to wait for them (default 25)

After --push the tool waits for the checks on the new main (validate, build
and ui from check.yml; build-site and deploy-site from deploy-pages) and exits
1 if any of them fails, so a red main is never left unnoticed.

Exit codes: 0 ready (dry run) or pushed with green checks, 1 a check failed
(before or after the push), 2 usage or git error. Nothing is pushed without --push, and nothing is ever force-pushed.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import json
import time
import urllib.request

PROJECT_NAME = "Project 2025 Tracker"
PROJECT_EMAIL = "349068206+bubbadog-claude@users.noreply.github.com"
DASHES = ("\u2014", "\u2013")  # em dash, en dash
# The repository is the one the tool is run from, so the first fallback can run
# a copy of this file taken from the bundle itself (see MAINTAINING.md section 6).
ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], text=True,
                      stdout=subprocess.PIPE).stdout.strip() or os.getcwd()


def run(cmd, check=True, capture=True, env=None):
    res = subprocess.run(cmd, cwd=ROOT, text=True, env=env,
                         stdout=subprocess.PIPE if capture else None,
                         stderr=subprocess.STDOUT if capture else None)
    if check and res.returncode != 0:
        out = (res.stdout or "").strip()
        raise SystemExit(f"ERROR: {' '.join(cmd)} failed ({res.returncode})\n{out}")
    return (res.stdout or "").strip() if capture else ""


def git(*args, check=True):
    return run(["git", *args], check=check)


def fail(msg):
    print(f"FAIL {msg}")
    return 1


def load_forbidden_env():
    """Pass the private identifier list to validate.py through the
    environment, so the check runs even though .private/ is gitignored."""
    env = dict(os.environ)
    if env.get("TRACKER_FORBIDDEN_WORDS"):
        return env, True
    local = os.path.join(ROOT, ".private", "forbidden_words.txt")
    if os.path.exists(local):
        terms = [t.strip() for t in open(local, encoding="utf-8") if t.strip() and not t.startswith("#")]
        env["TRACKER_FORBIDDEN_WORDS"] = ",".join(terms)
        return env, bool(terms)
    return env, False


def pick_ref(heads, wanted):
    names = [h.split()[1] for h in heads if h.strip()]
    if wanted:
        for n in names:
            if n == wanted or n.endswith("/" + wanted) or n == "refs/heads/" + wanted:
                return n
        raise SystemExit(f"ERROR: bundle has no head {wanted}; heads: {', '.join(names)}")
    if len(names) == 1:
        return names[0]
    review = [n for n in names if n.startswith("refs/heads/review/")]
    if len(review) == 1:
        return review[0]
    raise SystemExit(f"ERROR: bundle has several heads, pass --ref: {', '.join(names)}")


def check_commits(base, tip):
    """Every commit to publish must carry the project identity, the sign-off
    and the AI co-author line, and no dash characters in its message."""
    problems = []
    shas = git("rev-list", "--reverse", f"{base}..{tip}").split()
    for sha in shas:
        fmt = git("show", "-s", "--format=%an%x00%ae%x00%cn%x00%ce%x00%s%x00%B", sha)
        an, ae, cn, ce, subj, body = fmt.split("\x00", 5)
        short = sha[:9]
        if (an, ae) != (PROJECT_NAME, PROJECT_EMAIL):
            problems.append(f"{short}: author is {an} <{ae}>, expected the project identity")
        if (cn, ce) != (PROJECT_NAME, PROJECT_EMAIL):
            problems.append(f"{short}: committer is {cn} <{ce}>, expected the project identity")
        if f"Signed-off-by: {PROJECT_NAME} <{PROJECT_EMAIL}>" not in body:
            problems.append(f"{short}: no project sign-off")
        if "Co-Authored-By:" not in body:
            problems.append(f"{short}: no Co-Authored-By line")
        if any(d in body for d in DASHES):
            problems.append(f"{short}: dash character in the commit message")
        print(f"  commit {short} {subj}")
    return shas, problems


def check_diff(base, tip, env):
    """Added lines must carry no dash characters and no private identifier
    (validate.py covers records; this also covers MAINTAINING.md and docs)."""
    problems = []
    diff = git("diff", "--unified=0", f"{base}..{tip}")
    terms = [t.strip().lower() for t in env.get("TRACKER_FORBIDDEN_WORDS", "").split(",") if t.strip()]
    current = None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else line[4:]
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        text = line[1:]
        if any(d in text for d in DASHES):
            problems.append(f"{current}: added line with a dash character")
        low = text.lower()
        for t in terms:
            if re.search(r"(?<![a-z0-9])" + re.escape(t) + r"(?![a-z0-9])", low):
                problems.append(f"{current}: added line contains a private identifier (term not printed)")
                break
    return sorted(set(problems))


def ui_test(args):
    chrome = args.chrome or os.environ.get("UITEST_CHROME") or ""
    if not chrome:
        for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
            path = shutil.which(name)
            if path:
                chrome = path
                break
    env = dict(os.environ)
    if chrome:
        env["UITEST_CHROME"] = chrome
    env["UITEST_BASE"] = f"http://127.0.0.1:{args.port}/index.html"
    server = subprocess.Popen([sys.executable, "-m", "http.server", str(args.port), "--directory", "site"],
                              cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1.0)
        res = subprocess.run(["node", "scripts/uitest.js"], cwd=ROOT, text=True, env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    finally:
        server.terminate()
        server.wait(timeout=10)
    out = res.stdout or ""
    summary = [l for l in out.splitlines() if "links checked" in l or l.startswith("FAILURES")]
    for l in summary:
        print(f"  {l}")
    ok = res.returncode == 0 and "FAILURES (0)" in out
    if not ok:
        print(out[-3000:])
    return ok


REQUIRED_ON_MAIN = ("validate", "build", "ui", "build-site", "deploy-site")


def fetch_check_runs(repo, sha):
    """Check runs on a commit, from the public API (no token needed for a
    public repository; GITHUB_TOKEN is used when set, for the rate limit)."""
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/commits/{sha}/check-runs?per_page=100",
                                 headers={"Accept": "application/vnd.github+json",
                                          "User-Agent": "project-2025-tracker-fallback-export"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("check_runs", [])


def summarize(runs):
    """Latest run per required name: (done, failed, state by name)."""
    latest = {}
    for c in runs:
        n = c.get("name")
        if n in REQUIRED_ON_MAIN and (n not in latest or c.get("id", 0) > latest[n].get("id", 0)):
            latest[n] = c
    state = {n: (latest[n].get("conclusion") or latest[n].get("status")) if n in latest else "not started"
             for n in REQUIRED_ON_MAIN}
    done = all(n in latest and latest[n].get("status") == "completed" for n in REQUIRED_ON_MAIN)
    failed = [n for n in REQUIRED_ON_MAIN
              if n in latest and latest[n].get("status") == "completed" and latest[n].get("conclusion") != "success"]
    return done, failed, state


def wait_for_main(repo, sha, minutes, fetch=fetch_check_runs, sleep=time.sleep):
    """Poll the checks on the pushed main until all required ones conclude.
    Returns 0 when all succeeded, 1 on a failure or a timeout."""
    deadline = time.monotonic() + minutes * 60
    while True:
        try:
            done, failed, state = summarize(fetch(repo, sha))
        except Exception as e:  # network or rate limit: keep trying until the deadline
            done, failed, state = False, [], {"error": str(e)[:120]}
        line = ", ".join(f"{k} {v}" for k, v in state.items())
        print(f"  checks on main: {line}")
        if failed:
            print(f"FAIL checks on main failed: {', '.join(failed)}. Main is red: open a revert pull request "
                  f"or a fix now; the page may not have deployed.")
            return 1
        if done:
            print("  all checks on main succeeded and the page deployed")
            return 0
        if time.monotonic() > deadline:
            print(f"FAIL checks on main did not all conclude within {minutes} minutes; look at the Actions tab")
            return 1
        sleep(45)


def repo_slug():
    url = git("remote", "get-url", "origin")
    m = re.search(r"github\.com[:/]+([^/]+/[^/.]+?)(?:\.git)?/?$", url)
    return m.group(1) if m else "bubbadog/project-2025-tracker"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("bundle")
    ap.add_argument("--ref")
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--skip-ui", action="store_true")
    ap.add_argument("--chrome")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-wait", action="store_true")
    ap.add_argument("--wait-minutes", type=int, default=25)
    args = ap.parse_args()
    bundle = os.path.abspath(args.bundle)

    if git("status", "--porcelain", "--untracked-files=no"):
        raise SystemExit("ERROR: the working tree has uncommitted changes; commit or stash them first")
    start = git("rev-parse", "--abbrev-ref", "HEAD")
    if start == "HEAD":
        start = git("rev-parse", "HEAD")

    print("1. Fetch main and the bundle")
    git("fetch", "--quiet", "origin", "main")
    git("bundle", "verify", "--quiet", bundle)
    ref = pick_ref(git("bundle", "list-heads", bundle).splitlines(), args.ref)
    local = "refs/fallback/" + ref.split("/", 2)[-1]
    git("fetch", "--quiet", "--force", bundle, f"{ref}:{local}")
    tip = git("rev-parse", local)
    main_sha = git("rev-parse", "origin/main")
    print(f"  bundle head {ref} at {tip[:9]}; origin/main at {main_sha[:9]}")

    if subprocess.run(["git", "merge-base", "--is-ancestor", main_sha, tip], cwd=ROOT).returncode != 0:
        # main moved since the review session committed: replay the commits on
        # the current main, keeping the project identity as committer too.
        print("  main moved since the bundle was made; replaying the commits on origin/main")
        base = git("merge-base", main_sha, tip)
        env = dict(os.environ, GIT_COMMITTER_NAME=PROJECT_NAME, GIT_COMMITTER_EMAIL=PROJECT_EMAIL)
        git("checkout", "--quiet", "--detach", tip)
        res = subprocess.run(["git", "rebase", "--quiet", "--onto", main_sha, base], cwd=ROOT, env=env,
                             text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if res.returncode != 0:
            subprocess.run(["git", "rebase", "--abort"], cwd=ROOT)
            git("checkout", "--quiet", start)
            raise SystemExit("ERROR: the bundle's commits conflict with the current main; "
                             "ask the review session to re-run on the current main\n" + (res.stdout or ""))
        tip = git("rev-parse", "HEAD")
        git("update-ref", local, tip)
        git("checkout", "--quiet", start)

    print("2. Commit identity, sign-off and message checks")
    shas, problems = check_commits(main_sha, tip)
    if not shas:
        raise SystemExit("ERROR: nothing to publish; the bundle head is already on main")
    env, have_terms = load_forbidden_env()
    if not have_terms:
        problems.append("no private identifier list (TRACKER_FORBIDDEN_WORDS or .private/forbidden_words.txt); "
                        "the deploy job would catch a hit only after the push, so this tool requires it")
    problems += check_diff(main_sha, tip, env)

    print("3. validate --strict, build_snapshot and the browser test on the bundle's tree")
    rc = 0
    git("checkout", "--quiet", "--detach", tip)
    try:
        v = subprocess.run([sys.executable, "scripts/validate.py", "--strict"], cwd=ROOT, env=env, text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        last = [l for l in v.stdout.splitlines() if l.startswith("records ")]
        print("  " + (last[-1] if last else v.stdout.strip()[-400:]))
        if v.returncode != 0 or not last or not re.search(r"errors 0, warnings 0", last[-1]):
            problems.append("validate --strict did not report 0 errors and 0 warnings")
        b = subprocess.run([sys.executable, "scripts/build_snapshot.py"], cwd=ROOT, text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if b.returncode != 0:
            problems.append("build_snapshot.py failed: " + b.stdout.strip()[-400:])
        elif args.skip_ui:
            print("  browser test skipped (--skip-ui); check.yml runs it on main after the push")
        elif not shutil.which("node"):
            problems.append("node not found for the browser test (install Node and run npm ci, or pass --skip-ui)")
        elif not ui_test(args):
            problems.append("browser test did not report FAILURES (0)")
    finally:
        git("checkout", "--quiet", start)

    if problems:
        for p in problems:
            rc = fail(p)
        print(f"\nNot published: {len(problems)} problem(s). Nothing was pushed.")
        return rc

    print(f"\nReady: {len(shas)} commit(s), tip {tip[:9]}, fast-forward of main {main_sha[:9]}.")
    if not args.push:
        print("Dry run: re-run with --push to publish.")
        return 0

    print("4. Push (fast-forward of main; uses the admin bypass of the pull request ruleset)")
    git("push", "origin", f"{tip}:refs/heads/main")
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "origin/main") != tip:
        raise SystemExit("ERROR: origin/main is not the pushed tip after the push; check the repository")
    print(f"  pushed: main is now {tip}")
    print("\nAfter the push:\n"
          "  * close the review pull request for these commits, if one is open, as superseded by the push;\n"
          "  * write any dump corrections the digest lists back to the database, pinned to the versions it names.")
    if args.no_wait:
        print("Not waiting for the checks on main (--no-wait); the next review session checks main's health.")
        return 0
    print("5. Wait for the checks and the deploy on main")
    return wait_for_main(repo_slug(), tip, args.wait_minutes)


if __name__ == "__main__":
    sys.exit(main())
