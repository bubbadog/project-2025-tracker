# Maintaining

For the maintainer. Contributors need only [CONTRIBUTING.md](CONTRIBUTING.md).

## 1. What the repository is

`data/` is the record. `site/index.html` reads `site/snapshot.json`, which `scripts/build_snapshot.py` assembles from `data/` and which is never committed. A merge to `main` runs `deploy-pages.yml`, which validates, builds the snapshot and publishes `site/` to GitHub Pages. There is no other deploy path, so the published site always equals `main`.

The research runs are scheduled AI sessions (see [docs/PIPELINE.md](docs/PIPELINE.md)). They write to a working database and, at the end of each run, export the changed records into this repository on a branch `run/<date>-<kind>` and open a pull request. See section 6 for the merge policy for those pull requests.

## 2. Repository settings (the target state)

Each line says what the setting prevents. Status is kept current in section 9.

| Setting | Target | Why |
| --- | --- | --- |
| Visibility | Public | The point of the project. Goes public on the day of the first public announcement. |
| Wikis, Projects | Off | Unused surfaces are unmoderated surfaces. |
| Issues | On, blank issues off | Every issue comes through a form that asks for a record id and a source. |
| Pull requests | Squash only; merge commits and rebase off; delete head branches on merge | One commit per change on `main`, readable history, no stale branches. |
| Actions permissions | Allow bubbadog actions and reusable workflows, plus actions created by GitHub and verified creators | A workflow can only run actions from trusted publishers, and each is pinned to a commit SHA in the workflow file. |
| Fork pull request workflows | Require approval for first-time contributors | A stranger's first pull request cannot run CI until a maintainer looks at it. |
| Workflow permissions | Read repository contents; "create and approve pull requests" off | A compromised step cannot push, publish or approve. The deploy job raises `pages: write` and `id-token: write` for itself only. |
| Dependabot | Alerts and security updates on; version updates from `.github/dependabot.yml` | Pinned action SHAs and Playwright get updated by pull request, grouped weekly. |
| Private vulnerability reporting | On | A security report reaches the maintainer privately (see SECURITY.md). |
| Secret scanning and push protection | On (free on public repos) | A pushed token is blocked before it lands in history. |
| Code scanning | CodeQL default setup, if offered for Python and JavaScript | Free on public repositories; catches the obvious. |
| Pages | Source: GitHub Actions; Enforce HTTPS on | The deploy workflow is the only publisher. |
| About box | Description, website (the Pages URL), topics | So the repository explains itself from the listing. |
| Rulesets | The three files in `.github/rulesets/` (section 3) | Enforced by GitHub; the files are the versioned copy. |
| Repository secret `TRACKER_FORBIDDEN_WORDS` | Set; comma-separated | The private identifier list the validator scans for (section 7). |

## 3. Rulesets

Three rulesets, defined in `.github/rulesets/*.json` and applied through the API or the Rulesets UI. GitHub does not read them from the repository, so the weekly `rulesets.yml` workflow (and any pull request touching the files) compares the files with the live rulesets and fails on any difference. A ruleset change and its file change travel in the same pull request. The public API omits bypass lists, so the drift check cannot see a bypass change; review those by hand in Settings, Rules.

| Ruleset | Rules | Bypass |
| --- | --- | --- |
| `main: no force push, no delete` | Deletion and non-fast-forward blocked on the default branch | None. Nobody rewrites `main`, including the maintainer. |
| `main: changes arrive by pull request` | Pull request required (0 approvals, stale reviews dismissed, review threads resolved, squash only); required status checks `validate` and `build`, strict (branch up to date) | Repository admin, always. The maintainer can push directly in an emergency; everyone else, AI runs included, opens a pull request. A merge queue is not offered on a repository owned by a personal account (checked in the ruleset editor 2026-10-13); the strict up-to-date requirement gives contributors the same guarantee one pull request at a time. |
| `tags: releases are permanent` | Tags `v*` cannot be deleted, moved or updated | None. |

The required checks can only be attached after each check has run at least once on the repository, so the order is: push the files, let `check.yml` run on `main`, then create the pull request ruleset.

## 4. Checks

`check.yml` runs on every push to `main` and every pull request: `validate` (every record against `scripts/validate.py --strict`), then `build` (snapshot assembled, page parsed), then `ui` (Playwright opens every record and checks every link; advisory until it has run clean for a week, then make it required by adding `ui` to the pull request ruleset and to the file).

`rulesets.yml` runs weekly on Mondays, on demand, and on any pull request that touches `.github/rulesets/` or the checker.

`deploy-pages.yml` runs on every push to `main`: validate, build, upload, deploy. If validation fails there, nothing is published and `main` is wrong; fix forward with a pull request (history is never rewritten).

## 5. Releases

Tag a release when the record reaches a milestone (a chapter pass completed, a method change, a monthly snapshot): `git tag -s v2026.10.21 && git push origin v2026.10.21`, then create the release on GitHub with notes drawn from `data/runs/`. Calendar version numbers (`vYYYY.MM.DD`) fit a record that changes daily. Tags are permanent under the tag ruleset. A release workflow that attaches `snapshot.json` and a CSV is on the roadmap.

## 6. Pull requests from the research runs

Each run opens one pull request from `run/<date>-<kind>` with the records it changed, its run log under `data/runs/`, and `data/meta/state.json`. Policy (decided 2026-10-13): auto-merge on run pull requests opened by the maintainer or the maintainer's sessions, so they merge as soon as `validate` and `build` pass, with the run's private digest as the review; revert by pull request if a run was wrong. Pull requests from other contributors are merged by hand after reading the source behind any stage change, one at a time against an up-to-date branch (the ruleset enforces this; a merge queue would automate the rebasing but is only offered to organization-owned repositories). The export step is in every run prompt (docs/prompts/); a run waits for `validate` and `build` and merges its own pull request by squash from the session, which is the auto-merge behaviour, since GitHub's auto-merge toggle is only reachable through GraphQL, which sessions lack.

Two runs can fire within hours of each other. Each exports against current `main`, so their branches can conflict on `data/meta/state.json`; the second one rebases before opening its pull request (the export script does this), and the strict status check forces an up-to-date branch before merge.

## 7. Secrets

The repository holds one secret, `TRACKER_FORBIDDEN_WORDS`: the comma-separated private list of identifiers (names, places, handles) that must never appear in public data. `scripts/validate.py` reads it from the environment, or locally from the gitignored `.private/forbidden_words.txt`, and reports a hit by record and field only. GitHub masks the secret in logs. It is not available to pull requests from forks, so for those the check runs with the list on merge to `main` and in the deploy job; a hit there fails the deploy, and the fix is a follow-up pull request that removes the text, then a history rewrite only if the text reached a public commit (rotate the concern, then clean).

No other secrets. The deploy job authenticates to Pages with the job's OIDC token. The ruleset drift check uses the job's own read token.

## 8. Routine

- Weekly: merge Dependabot's grouped pull request after the checks pass; read the `rulesets.yml` result.
- After each run: read the digest; spot-check one changed record against its source; confirm the Pages site shows the new `as_of` date.
- Monthly: run `node scripts/uitest.js` locally against the live Pages address (`UITEST_BASE`), and the link audit; re-read SECURITY.md and this file against what is actually configured (section 9).
- Quarterly: re-read docs/METHOD.md against what the pipeline does.

## 9. Status log

| Date | What | Evidence |
| --- | --- | --- |
| 2026-10-13 | Repository created on GitHub, public, empty. Files prepared locally and validated (389 records, 0 errors). | `gh api repos/bubbadog/project-2025-tracker`: size 0, no rulesets |
| 2026-10-13 | `main` pushed; `check` green on `main`. Applied in the owner's browser: Pages source GitHub Actions with HTTPS enforced; Actions limited to bubbadog plus GitHub and verified creators, pinned SHAs required, read-only workflow token, approval for first-time contributors; Wikis and Projects off; squash only, auto-merge on, head branches deleted, sign-off required on web commits; private vulnerability reporting, dependency graph, Dependabot alerts and security updates, CodeQL default setup, secret scanning and push protection on; secret `TRACKER_FORBIDDEN_WORDS` set. Three rulesets imported from the files and active (ids 25031452, 25031477, 25031553); `tools/check_rulesets.py` passes. | API reads of the rulesets by id; settings pages read back after saving |

Update this table whenever a setting is applied, with the API read or screenshot that proves it.
