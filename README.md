# Project 2025: Mandate for Leadership Tracker

An apolitical, source-linked scorecard of how closely the recommendations in the Heritage Foundation's 2023 *Mandate for Leadership: The Conservative Promise* align with federal government actions since January 20, 2025. Every tracked recommendation carries a status, the dated evidence behind it with links, what would still have to happen, an estimated timeframe (labeled as an inference), a significance weight, and a confidence rating from an independent review.

It takes no position on whether any recommendation is good or bad policy, and it does not claim the document caused any action. It can be read from the right or the left.

**Live site:** https://claude.ai/artifact/G1M6Gd5HPzWMXXMXBgqC2X (the GitHub Pages address is listed in the repository's About box once the first deploy has run)

Status: **beta**. The fuller enumeration of the document is being completed chapter by chapter; the headline count grows as chapters are read in full, and the page says so. Corrections are welcome and are the most useful help.

## What is in this repository

| Path | What it holds |
| --- | --- |
| `data/items/*.json` | One file per tracked recommendation (the record). The single source of truth. |
| `data/meta/state.json` | Headline counts, chapter summaries, significance aggregates, limits, update note. |
| `data/meta/chapters.json` | The 31 chapters with authors and printed page ranges. |
| `data/meta/sig_raters.json` | Per-rater blind significance scores for the first 219 records. |
| `data/runs/*.json` | One log per research run: what changed and why, with source links. |
| `data/schema/item.schema.json` | JSON Schema for a record. `scripts/validate.py` enforces more than the schema can express. |
| `site/index.html` | The whole site: one static page that reads `snapshot.json`. |
| `scripts/build_snapshot.py` | Assembles `site/snapshot.json` from `data/` (never committed; CI builds it). |
| `scripts/validate.py` | The rules every record must pass. Runs on every pull request. |
| `scripts/uitest.js` | Browser test: opens every record, checks every link, contrast, phone layout. |
| `docs/` | The method, the data model, the significance weighting procedure, the pipeline, the roadmap. |

## How the record is built

1. **Research.** AI research agents read each chapter of the document in full, list the concrete and checkable recommendations, and research what the federal government has done on each since January 20, 2025, primary sources first (Federal Register, congress.gov, govinfo, courts, agency sites).
2. **Independent review.** A different AI model that did not see the research re-reads the cited pages, opens the sources that decide the status, corrects errors, re-derives the status from the rubric, and sets the confidence rating.
3. **Blind significance scoring.** Two raters who see only the recommendation text score reach, magnitude, breadth of government and fiscal scale; a third rater adjudicates disagreements.
4. **Scheduled runs** keep the record current: a news sweep and deep-check rotation on Tuesdays and Thursdays, a freshness pass on Mondays, Wednesdays and Fridays, a nightly enumeration pass, and a weekly significance recomputation. Every run writes a log under `data/runs/` and a dated note in each changed record's `history`.
5. **Validation.** `scripts/validate.py` holds every record to the same rules, machine-written or hand-edited.

Full detail: [docs/METHOD.md](docs/METHOD.md), [docs/DATA_MODEL.md](docs/DATA_MODEL.md), [docs/PIPELINE.md](docs/PIPELINE.md).

## Status rubric (short form)

| Status | Meaning | Progress band |
| --- | --- | --- |
| Completed | Done as the document specified and in effect | 100 |
| Implemented | Operative in substance through executive or agency action, but reversible or short of the full recommendation | 65 to 90 |
| In progress | Formally underway and partly operative | 25 to 60 |
| Proposed | Announced, proposed, or introduced, with nothing operative yet | 5 to 20 |
| Blocked | Enjoined, vacated, or stalled; keeps the progress reached before the block | 0 to 90 |
| Diverged | The administration did something materially different from the recommendation | 0 |
| No action found | No qualifying government action found | 0 |

The headline counts every tracked recommendation except Foreword items (chapter 00) and records that restate recommendations tracked elsewhere, so that one action is never counted twice.

## Run it locally

```bash
python3 scripts/validate.py --strict      # every record passes the rules
python3 scripts/build_snapshot.py         # writes site/snapshot.json
python3 -m http.server 8765 --directory site
# open http://127.0.0.1:8765/
```

The browser test needs Node 22 and Playwright: `npm install playwright@1.55.0 && npx playwright install chromium && node scripts/uitest.js` with the local server running.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). The short version: report an error or suggest a recommendation through the issue forms, or open a pull request that edits a record. A status change needs a primary source in the record and a dated note in its `history`. Every pull request runs the validator; the maintainer (and the next research run) re-reviews the evidence before merge. Commits are signed off under the Developer Certificate of Origin.

## Licenses

- Code (`scripts/`, `site/`, `tools/`, workflows): [Apache License 2.0](LICENSE).
- Data and documentation (`data/`, `docs/`): [Creative Commons Attribution 4.0 International](LICENSE-DATA). Attribute as "Project 2025: Mandate for Leadership Tracker" with a link to this repository.
- The document being tracked is the Heritage Foundation's. This repository holds paraphrases and page citations, never the document text. Page links open the scan preserved at the Internet Archive.

Not affiliated with the Heritage Foundation or any campaign, party, or government body. "Project 2025" and "Mandate for Leadership" are used to identify the document being tracked.
