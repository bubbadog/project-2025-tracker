# Open source and site plan

Written 2026-10-13. Labels: **Fact** is checked; **Decision** is settled; **Opinion** and **Estimate** are the maintainer's judgment and may change. Status of each phase is tracked in [ROADMAP.md](ROADMAP.md).

## Goal

A public repository that is the single source of truth for the record, where anyone can report an error or propose a change, where every change passes the same checks the research runs follow, and where an accepted change publishes itself. On top of that, a site worth sharing, and later an assistant that answers questions from the record with citations.

## Principles (Decision)

1. **Data is the product; the repository is the record.** One JSON file per recommendation, diffs readable by a person, history never rewritten.
2. **Same rules for machines and people.** The validator holds a run's output and a contributor's pull request to identical rules. If a rule only lives in a prompt, it is not a rule.
3. **Primary sources decide status; the maintainer decides merges.** Nothing reaches `main` without a pull request, except the maintainer in an emergency (admin bypass, logged).
4. **Anonymous by construction.** No private person is named anywhere in the record, the site, the issues or the commits. The private identifier list lives in a secret, never in a file.
5. **Neutral by construction.** The record describes alignment, never causation or merit. Contributions that argue are declined whichever way they argue.
6. **Disclosed automation.** AI does the research and review and the site says so; a person owns the method and the merges.
7. **Changes in real time, called out.** The headline moves whenever evidence moves, including in election week. There is no freeze; every change is dated and visible.

## Phase 1: the repository (this week)

Fact, done locally on 2026-10-13: data exported (389 records, 19 run logs), validator and schema, snapshot build, site page, three workflows (checks, Pages deploy, ruleset drift), Dependabot, three ruleset files, issue forms, pull request template, CODEOWNERS, licenses, code of conduct, README, CONTRIBUTING, SECURITY, MAINTAINING, docs.

To do, in order:

1. Install the GitHub App that lets sessions push; push `main`.
2. Let `check.yml` run once on `main`; then apply the three rulesets (required checks `validate` and `build`; admin bypass on the pull-request ruleset only).
3. Repository settings per MAINTAINING.md section 2; the `TRACKER_FORBIDDEN_WORDS` secret; Pages source set to GitHub Actions; About box.
4. First deploy; verify the Pages address shows the current `as_of`; put the address in the README and the About box.
5. Connect the runs: add the export step (PIPELINE.md section 2) to the four run prompts; first run pull request merged by hand; then enable auto-merge for run pull requests.
6. Make the repository public on the day of the public announcement (it is public and empty today; it can be made private until then, which on a Free personal account only costs the rulesets, which are not needed while it is private).

## Phase 2: the site (weeks 2 to 4)

The current page is one static file that already does the job: headline, chapter view, list view, record sheets with evidence, Changes and Method tabs, phone layout, deep links per record (`#cNN-SS`). The plan keeps that architecture (one file, no build step, no framework) because it is what lets anyone run the site from a clone and what keeps the deploy trivial, and improves what a visitor sees:

- Visual design pass: typography, spacing, a headline block that reads at a glance, consistent status colors with text labels (never color alone), print stylesheet.
- Social preview: an image generated at build time from the headline figures (`scripts/build_og.py`), `og:image` and Twitter card tags, so a shared link shows the number and the date.
- A change feed: `site/changes.xml` (RSS) and `site/changes.json` built from `data/runs/`, so readers and other sites can subscribe.
- A per-record share card: a static `site/r/cNN-SS.html` stub per record with title, status and confidence in the meta tags, redirecting to the deep link (search engines and chat apps read the stub).
- Downloads: `snapshot.json` and a CSV of the counted set, linked from the Method tab.
- Cumulative in-effect chart from run history once there are six to eight weeks of runs (Estimate).
- A custom domain when the maintainer chooses one (DNS record, domain saved in Pages, HTTPS enforced after the certificate issues, domain verified on the account).

Opinion: a framework rewrite (React, Next) buys nothing a reader can see and costs a build step, a dependency tree for Dependabot to chase, and a harder contribution path. If a designer joins, the design lives in a Design artifact and is implemented in the single file.

## Phase 3: contributors (ongoing from week 2)

- Labels: `needs-source`, `accepted`, `declined`, `postponed`, `archived`, `good first issue`, `run`.
- A public project board fed by the issue forms.
- Discussions enabled only for method questions; no editorializing threads (the code of conduct covers this).
- Helpers: a `triage` role (label and ask for sources) before anyone gets write access; write access only through a pull request history. The admin bypass stays with the maintainer alone.
- Monthly contributor note in Discussions: what changed, what needs sources.

## Phase 4: the assistant (not before Phase 2 is live)

Decision 2026-10-13: a record-grounded question-and-answer assistant first; current-events research with analysis second, if the first one proves useful.

The maintainer's AI project method applies: no architecture is chosen before the Stage 1 to 5 questions are answered (who asks, what they ask, what a wrong answer costs, what a right one is worth, what the assistant must never do), and a Gate 1 decision is recorded. The questions are in the roadmap; the answers decide whether the assistant is a page feature, a separate service, or not built.

Constraints already known (Decision): every answer cites record ids and source URLs; inferences are labeled as such in the answer; the assistant refuses to characterize merit or motive; the document text is never in the assistant's context (paraphrases and citations only); it runs outside GitHub Pages (which is static) on a small service with a spend cap.

## Phase 5: sustainability

The licenses are chosen so that nothing here closes a door later (not legal advice):

- Code under Apache-2.0 and data under CC BY 4.0 let anyone, including the maintainer, use the work commercially with attribution. Changed 2026-10-26: data and documentation versions from that date are under CC BY-NC-SA 4.0, so a copy of the tracker must credit the project, stay non-commercial and share alike, and other uses go through a "Request a data license" issue; the earlier versions stay under CC BY 4.0, which cannot be withdrawn. There is no download gate: the page loads the whole dataset in the browser and the records are in this repository, so a gate would only inconvenience honest users. The maintainer can also offer the same work under other terms (dual licensing) for code the maintainer wrote; contributions arrive under the same licenses with a sign-off, so the project can always be redistributed as it is.
- What can be charged for is service, not the data: an API with uptime and support, the assistant, a newsletter, sponsorship, donations. The record itself stays free, which is also what makes it credible.
- Any paid tier must not change the record. The headline and the data are identical for paying and non-paying readers.

Donations: a button appears when `meta.support_url` is set; the link stays off community posts.

## Risks and how they are handled

| Risk | Handling |
| --- | --- |
| A contributor pushes advocacy into the record | Validator (neutral vocabulary is not machine-checkable, so this is a review rule); CONTRIBUTING states it; declined without argument |
| A run writes something private | Identifier scan in every run, in the validator (secret list), and in the deploy job; private vulnerability reporting for anything that slips |
| Two runs collide on `main` | Branch per run, strict status checks, rebase before opening |
| The checks pass but the site is wrong | `ui` job opens every record; monthly manual spot check of five records |
| A dependency or action is compromised | SHA pins, Dependabot grouped updates, Actions allow-list of GitHub and verified creators only |
| The maintainer is unavailable | Everything needed to run the project is in the repository (prompts, scripts, method); a second admin can be added without anything else changing |
| Heritage Foundation copyright or trademark complaint | Paraphrases and page numbers only; no document text; the name is used to identify the document; non-affiliation stated |
| Defamation or accuracy complaint | Every claim sourced and dated; corrections by issue with a public history; the project describes actions, never motives |
