# Pipeline

How the record is produced and kept current, and how it reaches this repository and the site.

## 1. The runs

Two scheduled AI sessions do the research (since 2026-10-19; before that, four) and a third, since 2026-10-26, reviews and exports. Each starts from nothing, reads the standing guidance and the work queue, does its mandate, writes to the working database with version-pinned writes, refreshes the published snapshot, and sends the maintainer a private digest. The full prompts are in [prompts/](prompts/), with only the maintainer's name removed; they are the specification of the process and change by pull request like everything else.

| Run | Schedule (Pacific) | Mandate | Prompt |
| --- | --- | --- | --- |
| Daily | Every day, 4:47 am | Owner requests and verified leads; a daily news sweep (about 40 searches plus Federal Register API queries for everything published since the last run) mapped to records; a rotation of about 10 records (about 6 with the oldest evidence, so that no record goes more than 90 days without a dated check, and about 4 refutation checks on records counted as in effect); independent review of everything that changed; a small backlog slice when budget remains, including a Sunday probe of hosts that refused earlier fetches; on Sundays the digest nominates the week's most consequential change for the maintainer to verify by hand on its primary source | [daily.txt](prompts/daily.txt) |
| Significance | Sunday, 3:31 am | Fills missing per-rater scores from the stored sheet or fresh blind raters; recomputes the weighted share, the bootstrap band, rater agreement and the sensitivity table | [significance-weekly.txt](prompts/significance-weekly.txt) |
| Review and export | Every day, about 8:03 am | Pulls what the daily run wrote, red-teams it against the committed record (`scripts/review_run.py`), fixes missing history notes from the run log, validates, builds, runs the UI test, writes the log row and pushes to this repository when the quality standards hold; sends the maintainer a digest of anything that blocked the export and every stage change, confidence label move and court-status change. Added 2026-10-26 | [review.txt](prompts/review.txt) |

From 2026-10-07 to 2026-10-19 the work ran in four sessions while the document was being read in full: an update run on Tuesday and Thursday mornings ([update-tuesday-thursday.txt](prompts/update-tuesday-thursday.txt)), a freshness pass on Monday, Wednesday and Friday mornings ([freshness-mon-wed-fri.txt](prompts/freshness-mon-wed-fri.txt)), two nightly firings that enumerated every chapter and then lifted records to their primary documents and ran the systematic absence checks ([nightly-enumeration.txt](prompts/nightly-enumeration.txt)), and the Sunday significance run. With the enumeration, the lift and the absence checks complete, the first three were consolidated into the daily run. Their prompts stay here as the record of how the existing records were produced.

Model routing inside a run: a coordinating agent plans and writes; research subagents (a smaller model) do the searching under an explicit search cap; an independent reviewer (a larger model that never sees the research being produced) re-derives every changed record from the rubric and sets confidence; blind raters score significance from the recommendation text alone. Each run's search budget is fixed (120 calls shared across the daily run's agents, at most three research subagents and one reviewer; the Federal Register API is free) so a run cannot drift into open-ended browsing.

Standing documents the runs read first, which are private and not in this repository: `meta/guidance` (standing notes and a dated feedback log, where lessons from each run are recorded so the process is refined run to run), `meta/backlog` (the work queue, mirrored in the roadmap), `meta/leads` (unverified leads; every URL is fetched before anything enters a record), and `requests` (the maintainer's add, recheck and remove requests).

## 2. From the database to this repository

The runs write to a working database (the artifact's database). The repository is the published, versioned copy, and `main` is what the site shows. Nothing moves from the database to the repository without a review. The path between them, since 2026-10-26:

1. The daily run finishes its writes, its run log and its mirror refresh. It does not push here.
2. The review session clones this repository, dumps the run log, every record the run touched and `meta/state` (and `meta/sig_raters` or `meta/chapters` when they changed) to a directory, and runs `python3 scripts/review_run.py DUMP_DIR --date DATE`. The script compares each record with the committed one and reports blocking findings (a stage or progress change without a same-day independent review, a lost field, a lead-only host used as a source, an event or court-status URL missing from the sources, a dash, a personal identifier or a model name in public text), fixable findings (a changed record without a dated history note, which `--fix` composes from the run log) and informational lines.
3. With no blocking finding, it runs `python3 scripts/import_dump.py DUMP_DIR` (public documents only, canonical form), `python3 scripts/validate.py --strict`, `python3 scripts/build_snapshot.py` and the UI test, adds the log row to MAINTAINING.md, commits with the project identity and pushes to `main` (the repository admin's bypass; the required checks still run and `deploy-pages.yml` publishes only when they pass). It then writes any fix it made back to the database with version-pinned writes, so the two copies match.
4. A blocking finding leaves the repository untouched; the finding goes to the maintainer in the digest, who decides it, corrects the database and exports by hand with the same scripts.
5. The maintainer's own pass later in the day reads the digest, spot-checks a changed record against its source and records the red-team result in MAINTAINING.md.

If a push to `main` is refused, the session pushes to `review/<date>` and opens a pull request instead; the pull-request ruleset's strict status checks refuse a merge from a stale branch, so a later export always includes an earlier one.

## 3. Checks on every change

Whether a change comes from a run or a person, the same checks run on the pull request (`.github/workflows/check.yml`):

- `validate`: every record against `scripts/validate.py` (required fields, stage bands, label consistency, no-action confidence caps, https URLs, no future dates, no raw URLs in notes, symmetric cross-references, headline counts in `meta/state` equal to the records, run logs pointing at real records, no em dashes, no private identifiers) and against the JSON Schema.
- `build`: the snapshot assembles; the page parses with one script block and no em dashes.
- `ui` (advisory until stable): Playwright opens every record on the built site, checks every link resolves, contrast, and the phone layout.

## 4. Publishing

A merge to `main` runs `.github/workflows/deploy-pages.yml`: validate again (with the private identifier list), build `site/snapshot.json`, upload `site/`, deploy to GitHub Pages. Nothing else can publish. The artifact page at claude.ai stays as a mirror of the same data while the GitHub Pages site becomes the canonical address; a later change will point one at the other.

## 5. Red-team procedure after each run

Run by the maintainer or a session after each scheduled run (find and fix, then record):

1. Pull every live record and the published snapshot; keep the previous local record as the baseline.
2. Diff live against baseline by id: which fields changed per record.
3. Confirm every write was version-pinned (the digest reports no stale-pin failure) and no document lost a field it had.
4. Confirm every stage change in the run log has a source URL and a review dated that day; progress stayed inside the stage band.
5. Confirm the published snapshot equals the database; `meta.as_of` moved; the Changes tab shows the run.
6. Scan everything written for private identifiers and em dashes; every new URL is https with no spaces; every new date is `YYYY-MM-DD` and not in the future.
7. For every fact a run removed as unsupported, check the sibling records in the same chapter; if a sibling cites a verified source for it, restore the fact with that source.
8. Research notes are not events: a timeline entry that describes a check rather than a government action moves to `uncertainties`.
9. For an enumeration run: every new record carries a review dated that day and a significance block with per-rater scores; every record that overlaps a tracked one carries `related_ids` with the reverse link present; `meta/state` counts match.
10. Fix what fails with pinned writes, add a history note on each corrected record, re-export, and record the check.

In the repository, steps 3, 4, 6 and 9 are what `scripts/validate.py` automates on the committed record, and `scripts/review_run.py` applies steps 2, 3, 4, 6 and the lead-only host and history-note rules to a dump before it is imported; steps 5, 7 and 8 still need a reader, which is why the maintainer's pass follows the automated one.

## 6. Limits of the pipeline (stated, not hidden)

- Some primary documents sit behind sites that refuse automated retrieval (war.gov, media.defense.gov, dhs.gov, state.gov, cadc.uscourts.gov, courtlistener.com docket pages, af.mil, congress.gov, ice.gov, fema.gov). Those records cite the URL and say the document was not opened and why, never that it was not found. Retrieval routes (decided 2026-10-26): automated fetching first, because it is cheaper; a live browser session as the backup when a fetch is refused, and as the first attempt only where it is the cheaper route for the task. Refusals are recorded as pending leads; the maintainer's browser retrieval (`docs/prompts/retrieval.txt` is the prompt template) returns the files to a shared folder with an index, the coordinating session verifies each file's text layer, and two independent reviewers rewrite the records before the gate, the database write and the push.
- The runs cannot archive sources (no network path to archive.org from the research container); link rot is caught by the monthly link audit, not prevented.
- A usage limit on the account can stop a run mid-way. Every write is pinned and atomic per document, so a stopped run leaves consistent records and an incomplete run log, and the digest says so.
