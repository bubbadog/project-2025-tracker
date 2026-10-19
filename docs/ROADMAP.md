# Roadmap

Living document. Status as of 2026-10-19: one headline over 627 counted recommendations (648 records; Foreword items listed, not counted), 115 in effect (18 percent; weighted 18.1 percent); confidence 246 high, 387 medium, 15 low; all 30 chapters read in full and both enumeration passes complete (2026-10-16).

| # | Work | Status | What it changes |
| --- | --- | --- | --- |
| B5 | **Fuller enumeration.** Read every chapter in full, list every concrete and checkable recommendation, add the ones not yet tracked (up to 12 per chapter per pass), review and score each; then a second pass over the candidates left behind the cap | Done: first pass 2026-10-14, second pass 2026-10-16 (648 records, 627 counted); first pass through chapter 30 targeted for 2026-10-18 and the second pass for 2026-10-21 (about two weeks before the 2026-11-03 election) | Coverage becomes defensible as "the document", not "key objectives"; total checkable recommendations likely 450 to 700 (Estimate) |
| B3 | **Freshness.** Records whose latest dated event predates mid-2026 | Monday, Wednesday, Friday runs; backlog list of ids | Timelines catch up to summer and fall 2026 |
| B16 | **Primary-source lift.** Medium-confidence records in order of significance weight: read the stage-deciding official document and re-review | Reachable work done 2026-10-18: every medium or low record above not_started or diverged has a lift review; seven remain on hosts that refuse fetches (task P1) | High-confidence share (37 percent today, up from 23 percent on 2026-10-15) rises toward what the rubric allows, roughly 55 to 65 percent (Estimate) |
| B17 | **Systematic absence checks.** No-action and diverged records get the documented five-part check so they can be rated up to 70 | Done for every absence-based record below 70 as of 2026-10-19 (five documented checks, Unified Agenda included); low-confidence records fell from 88 to 15 | Removes the permanent low on records where nothing has happened |
| B12 | **Source archiving.** A Wayback capture per source against link rot | Blocked: no network path to archive.org from the research container; test from a scheduled run | Dead links stop silently eroding the record |
| F1 | **Fiscal anchors.** Source the 204 estimated fiscal scores from CBO, CRS and budget documents | Open | Tightens the significance band |
| P1 | **Blocked primary documents.** Six documents on sites that refuse automated retrieval (defense, DHS, State) | Open; needs a person with a browser | Those records move from "cited, not read" to read |

Done (Fact): primary-source pass on the first 219 (0 records without a primary or court source); red-team of every in-effect record; estimated windows on every record; event dates moved to the documents that carry them; cross-references symmetric; chapter summaries on all 31 chapters; structured court status; significance weighting with blind raters.

## B. Scheduled runs

| Run | Schedule (Pacific) | State |
| --- | --- | --- |
| Daily (requests and leads, news sweep, rotation of about 10 records with refutation checks, review) | Every day 4:47 am | Live from 2026-10-20; replaces the three runs below |
| Significance recompute (band, kappa, sensitivity) | Sunday 3:31 am | First run 2026-10-18 |
| Update (news sweep, 25 deep checks, review) | Tuesday and Thursday 6:54 am | 2026-10-08 to 2026-10-19; paused, folded into the daily run |
| Freshness (12 oldest records, watch items) | Monday, Wednesday, Friday 4:47 am | 2026-10-12 to 2026-10-19; paused, folded into the daily run |
| Enumeration, then primary-source lift and absence checks | Nightly 11:11 pm and 1:51 am | 2026-10-09 to 2026-10-19; paused, work complete |

Every run reads the standing guidance and the backlog first, does its mandate, writes with version-pinned writes, and (Phase 1 below) opens a pull request here. The schedule was consolidated into one daily run on 2026-10-19, once the full reading of the document, the primary-source lift and the systematic absence checks were complete; the primary-source lift (B16) and the absence checks (B17) continue as maintenance inside the daily run.

## C. Site features (ranked)

| # | Feature | Depends on |
| --- | --- | --- |
| D4 | Per-record share links with a preview card (title, status, confidence) | Phase 2 |
| D8 | RSS and JSON feed of changes | Phase 2 |
| D5 | Cumulative in-effect chart over time from run history | Six to eight weeks of runs (Estimate) |
| D6 | Subject tags across chapters (immigration, personnel, energy) with a filter | Tagging pass (scripted plus review) |
| D7 | Officeholder context line per chapter linking to the official leadership page | None |
| D9 | Spanish version of the page chrome, then of the record | Phase 2 |
| D10 | Record-grounded question-and-answer assistant with enforced citations | Phase 4; method questions first |

## D. Open source phases

See [OPEN_SOURCE_PLAN.md](OPEN_SOURCE_PLAN.md).

| Phase | Contents | State |
| --- | --- | --- |
| 1 | Repository public; checks on every pull request; Pages deploy on merge; rulesets; runs export by pull request | Done 2026-10-13: site live at https://bubbadog.github.io/project-2025-tracker/ ; run pull requests merge once the checks pass; contributor pull requests are merged by hand |
| 2 | Site: design pass, social preview, change feed, share stubs, downloads, custom domain | After Phase 1 |
| 3 | Contributors: labels, board, triage role, monthly note | From week 2 |
| 4 | Assistant: record-grounded Q&A first; Stage 1 to 5 questions before any architecture | After Phase 2 |
| 5 | Sustainability: service, not data, is what could be charged for; the record stays identical for everyone | Open |

## E. Operations

- After every run: diff live against baseline, confirm pinned writes, sources on every stage change, snapshot equals the database, identifier and dash scan, sibling rule on removed facts, research notes out of timelines (PIPELINE.md section 5).
- Monthly: link audit, browser test against the live site, five records spot-checked by hand against their sources.
- Quarterly: re-read METHOD.md against what the pipeline does; update the Limits list.

## F. Decisions log

- 2026-10-13: Repository and GitHub Pages site live; run pull requests merge automatically once `validate` and `build` pass, contributor pull requests by hand; public announcement targeted for 2026-10-21.
- 2026-10-13: Open source under Apache-2.0 (code) and CC BY 4.0 (data), DCO sign-off, pull requests for every change with the maintainer's admin bypass only; GitHub Pages as the canonical site; runs export by pull request. No election-week freeze: the headline changes as evidence changes and the page says so. Assistant: record-grounded Q&A first, after the method's Stage 1 to 5 questions.
- 2026-10-12: Enumeration deadline set (first pass 2026-10-18, second pass 2026-10-21). Per-rater significance scores stored on every record; weekly recomputation of the band. Confidence rubric addition: documented systematic absence checks lift the cap on no-action records to 70. Six judgment-call records sent to a second independent review; all held.
- 2026-10-11: One headline counts every tracked record except Foreword items and records that restate chapter objectives. Freshness run added Monday, Wednesday, Friday.
- 2026-10-09: Foreword and chapter-introduction records that restate tracked objectives carry `restates_ids` and are never counted, so one action is never counted twice.
- 2026-10-08: Reviewing model name kept in `review.model` as provenance; the page says "AI". Significance weighting published with its method. Mission framed as an apolitical scorecard usable by the right or the left. Advocacy sites removed from the data. Update schedule Tuesday and Thursday.
- 2026-10-07: Headline is the share of recommendations in effect, not the progress score; both are shown. Published anonymously under the project name.
