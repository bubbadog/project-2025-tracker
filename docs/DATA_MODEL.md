# Data model

Everything the site shows comes from `data/`. One JSON file per document, pretty-printed with sorted keys, so a diff shows only real changes. `data/schema/item.schema.json` is the JSON Schema for a record; `scripts/validate.py` enforces the rules the schema cannot express (bands, label consistency, symmetric links, counts).

## `data/items/<id>.json`: one record per tracked recommendation

Ids are `cNN-SS`: chapter number (00 Foreword, 01 to 30) and a sequence number within the chapter. Ids are permanent; a record that is dropped keeps its file with `tracked: false`.

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | `cNN-SS` |
| `chapter` | string | `"00"` to `"30"` |
| `agency` | string | The department, agency or office the recommendation addresses |
| `title` | string | Up to 90 characters, neutral |
| `proposal` | string | Paraphrase of the recommendation. Never the document's text |
| `pages` | int[] | Printed page numbers in the document where the recommendation appears |
| `position` | string or null | Where the recommendation sits in the chapter (section heading), when useful |
| `mechanism` | enum | `executive_order`, `agency_rule`, `agency_action`, `legislation`, `appointment`, `litigation`, `mixed` |
| `requires_congress` | enum | `yes`, `no`, `partial` |
| `stage` | enum | `not_started`, `proposed`, `in_progress`, `implemented`, `completed`, `blocked`, `diverged`, `pending` |
| `progress` | int 0 to 100 | Inside the band for the stage (see METHOD.md) |
| `match` | enum | `direct`, `partial`, `parallel`: how closely the action matches the recommendation |
| `status_summary` | string | 2 to 4 sentences with dates, neutral voice |
| `timeline` | object[] | `{date, event, url, source, kind}`; `kind` is `primary`, `court`, `news` or `tracker`; sorted by date; may be empty only for `not_started` and `pending` |
| `remaining` | string[] | What would still have to happen for the recommendation to be complete |
| `blockers` | string[] | Court orders, statutory limits, failed votes, and the like |
| `est_completion` | object | `{window, basis}`; `window` is `done`, `YYYY-Qn`, `YYYY-Hn`, `YYYY`, `unlikely this term` or `unknown`; `basis` is always an inference and says so |
| `durability` | object | `{level: low, medium, high; why}` |
| `sources` | object[] | `{title, url, publisher, date, kind}`; https URLs only |
| `uncertainties` | string | What is not known; no raw URLs |
| `confidence` | int 0 to 100 | The reviewer's rating |
| `confidence_label` | enum | `high` (80+), `medium` (55 to 79), `low` (21 to 54), `unverified` (0 to 20); must agree with `confidence` |
| `confidence_reason` | string | Why, in one or two sentences |
| `review` | object | `{reviewer, model, reviewed_at, mandate_check, mandate_note, source_checks[], flags[]}`; `mandate_check` is `verified`, `partial` or `not_found` (did the cited pages say this); `source_checks` are `{url, result: supports, partial, does_not_support, unreachable; note}`; `flags` are the reviewer's open concerns. Optional `question` and `second_review` when a record went to a second independent review |
| `redteam` | object, optional | `{date, verdict: holds, weakened, changed; what_was_tested, evidence[], note}`: the refutation pass on in-effect records |
| `court_status` | object, optional | `{state: enjoined, stayed, vacated, upheld, dismissed, pending; date, url, basis}`, derived from the latest court event |
| `related_ids` | string[], optional | Cross-references; always symmetric (the validator checks) |
| `restates_ids` | string[], optional | Set on Foreword or chapter-introduction records that restate recommendations tracked elsewhere; such records are listed but never counted |
| `significance` | object | `{R, M, B, F, weight, F_estimated, raters, adjudicated, rationale, version, rater_scores[]}`; scores 1 to 3 per dimension (a value of 1.5 or 2.5 is the mean of two raters who differed by one); `weight` is the mean of the four; `rater_scores` holds `{rater: A, B or C; R, M, B, F}` per rater and is being filled in for every record |
| `self_confidence` | int, optional | The researching agent's own confidence before review (provenance only; the page shows the reviewer's) |
| `research_agent` | string, optional | Which research pass produced the record (provenance only) |
| `layer` | int | 1 or 2: original key objectives; 3: added in the fuller reading. Provenance only; does not affect counting |
| `headline` | bool, optional | Historical flag from before the single-headline decision of 2026-10-11; provenance only |
| `tracked` | bool | `false` means dropped; the record stays in the repository |
| `updated_at` | date | Last change to the record |
| `last_checked` | date | Last time a run looked for developments, whether or not anything changed |
| `history` | object[] | `{date, note}`; every change gets a note; notes name the source's host, never a raw URL |

### Counting rule

A record is counted in the headline when `tracked` is not `false`, `chapter` is not `"00"`, and `restates_ids` is absent or empty. "In effect" means `stage` is `implemented` or `completed`. `data/meta/state.json` carries `total`, `counts` (by stage) and `reviewed` for that counted set; the validator fails if they disagree with the records.

## `data/meta/state.json`

| Field | Meaning |
| --- | --- |
| `as_of` | Date of the latest research run reflected in the record |
| `built_at` | Date the published snapshot was last assembled |
| `total`, `counts`, `reviewed` | Headline figures for the counted set (see above) |
| `limits` | The Limits list shown on the Method tab |
| `trackers` | Related projects shown under the Method tab: `{name, url, note}` |
| `update_note` | The Updates paragraph on the Method tab |
| `chapter_summaries` | `{NN: {summary, basis_ids, as_of}}`: the 72 to 89 word narrative shown above each chapter, drawn only from the records in `basis_ids` |
| `significance` | Aggregates from the weekly recomputation: `weighted_share`, `unweighted_share`, `weighted_progress`, `unweighted_progress`, `band_5_95`, `kappa {R, M, B, F, composite}`, `exact_agreement`, `sensitivity`, `weight_distribution`, `top10`, `F_estimated_count`, `adjudicated`, `n`, `as_of`, `note` |
| `deepen_cursor`, `deepen_done` | Where the fuller enumeration stands (next chapter to read; whether the first pass is complete) |
| `show_layer3`, `show_no_ads`, `support_url`, `layer` | Page switches: kept for compatibility; the single headline made `show_layer3` moot |

## `data/meta/chapters.json`

The 31 chapters: `{num, title, authors, start, end}` with printed page ranges.

## `data/meta/sig_raters.json`

Per-rater blind significance scores for the first 219 records (`{as_of, count, note, scores: {id: {A: {R, M, B, F}, B: {...}, C: {...}}}}`), kept so the weekly task can write them into each record as `significance.rater_scores` and recompute the band. Newer records carry `rater_scores` directly.

## `data/runs/<id>.json`

One log per research run, id `YYYY-MM-DD-<kind>`: `{id, date, kind, title, summary, changes[]}` where each change is `{id, title, from, to, note, url}` for a record whose stage changed or that was added. The Changes tab is built from these. Run kinds so far: `baseline`, `validation`, `deepening`, `update` (Tuesday and Thursday), `freshness` (Monday, Wednesday, Friday), `layer3` and `layer3-late` (nightly enumeration), `primary`, `lowconf`, `structure`, `headline`, `review`, `review2`.

## What is private and never in the repository

The research runs' working documents (`meta/backlog`, `meta/guidance`, `meta/leads`, `requests`) and the document text used for enumeration. The private identifier list the validator scans for lives in a repository secret, not in a file.
