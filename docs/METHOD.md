# Method

This is the method as published on the site's Method tab, kept here so it can be read, cited and corrected by pull request. The site renders the live counts; this file states the rules.

## Mission

The tracker is apolitical. It is a scorecard, nothing more: it shows how closely the goals set out in the 2023 *Mandate for Leadership* align with this presidency's objectives and outcomes, recommendation by recommendation, with the evidence attached. It can be used by the right or the left. It takes no position on whether any recommendation is good or bad policy, and it does not claim the document caused any action.

The aim is a factual, current and checkable record. Every status rests on cited public sources with clickable links, every record carries a confidence rating from an independent review, and every change is logged.

The research and review are automated with AI models and are disclosed as such. The record is refreshed on a published schedule.

## What is tracked

A record of the recommendations in *Mandate for Leadership: The Conservative Promise* (Heritage Foundation, 2023), set against federal actions since January 20, 2025. It tracks whether actions align with what the document recommends.

The record began as a selection of key objectives, the concrete and checkable recommendations that carry each chapter, and is being extended chapter by chapter into a fuller enumeration by reading each chapter in full. The headline counts every recommendation tracked so far. Until every chapter has been read in full, chapters read in full contribute more recommendations than chapters still limited to their key objectives, and the figure moves as more are added; the page says so.

Foreword records (chapter 00) and records that restate a recommendation tracked elsewhere (`restates_ids`) are listed for completeness and left out of the count, so that one action is never counted twice.

The document text used is the 920-page PDF preserved at the Internet Archive (`archive.org/details/2025_MandateForLeadership_FULL`); the publisher's original download links now redirect to a book sales page, so page links open the archived scan. The repository holds paraphrases and page citations only, never passages of the text.

## How status is assigned

| Status | Meaning | Progress band |
| --- | --- | --- |
| Completed | Done as the document specified and in effect | 100 |
| Implemented | Operative in substance through executive or agency action, but reversible or short of the full recommendation | 65 to 90 |
| In progress | Formally underway and partly operative | 25 to 60 |
| Proposed | Announced, proposed, or introduced, with nothing operative yet | 5 to 20 |
| Blocked | Enjoined, vacated, or stalled; keeps the progress reached before the block | 0 to 90 |
| Diverged | The administration did something materially different from the recommendation | 0 |
| No action found | No qualifying government action found | 0 |

"In effect" means implemented or completed. The headline is the share of counted recommendations in effect; the unweighted progress score (mean of `progress`) and the significance-weighted share are shown next to it, never in its place.

Each record also carries a match type (direct, partial or parallel), the route it needs (executive action alone, Congress, or both), and a durability note: an executive order or guidance can be undone quickly by a later administration, a final rule or completed reorganization is harder to undo, and a statute or Supreme Court holding is hardest.

Court events set `court_status` (enjoined, stayed, vacated, upheld, dismissed, pending) from the latest court event in the timeline; list rows show a tag for enjoined, stayed and vacated.

## Confidence

Research and review are done by AI models, and every claim is linked to its source so that a person can check it. One model researches each recommendation. A different model then reviews it without having seen the research being produced: it re-reads the cited pages of the document, opens the sources that decide the status, corrects errors, re-derives the status from the rubric, and scores how confident a reader should be that the status is right.

- **High** (80 to 100): the document text and a primary source were both checked.
- **Medium** (55 to 79): the text was checked and a reputable secondary source or part of the primary record supports the status.

What counts as the primary source opened (decided 2026-10-22 to 2026-10-26): the document on its official host; a copy of it retrieved from that host and supplied to the project, or an Internet Archive snapshot of the official address, with the record saying how the copy was obtained; an official agency page that itself states the deciding fact (an agency page stating that a memorandum was rescinded, for example); a court filing or an agency document filed as a court exhibit, read on the court's site or on CourtListener; and the U.S. Code as reproduced by Cornell's Legal Information Institute. A copy posted only by an advocacy group, a union, a litigant or its counsel, a newsletter or an aggregator keeps the rating at 79 or below until the document is read on one of those hosts. Research institutions, including university litigation trackers, are sources, except a page on which the institution is itself a party or amicus.
- **Low** (21 to 54): the status rests on sources the reviewer could not open, on a single secondary source, or on finding no evidence in a limited search.
- **Unverified** (0 to 20): not yet reviewed.

**Absence of evidence.** A status that rests on no action having been found (no action found, diverged, and some proposed or in-progress calls) is capped at 50 unless the record carries a documented systematic check: a Federal Register search on the recommendation and its agency since January 20, 2025, the agency's current Unified Agenda entry, a congress.gov search of the 119th Congress, the agency's own press and policy pages, and one major news search, each listed with its date under `review.source_checks`. With that check recorded, the reviewer may rate the status up to 70, and the record says when the check was made. A qualifying action found later by any run resets the status in the ordinary way. This rule was added on 2026-10-12; records are being brought under it in order of significance.

**Red team.** Recommendations counted as in effect also get a red-team pass: a separate agent searches for reversals, injunctions and effective dates that would make that status wrong. The verdict (holds, weakened, changed) is shown on each record under `redteam`.

## Significance weighting

Significance is the expected consequence of a recommendation for people in the United States if it were fully carried out, judged from the recommendation itself and not from whether it has been carried out. It says nothing about whether a recommendation is good or bad. The weighted share reweights the same recommendations by this score, so that a government-wide law and a single pilot program no longer count the same.

Two independent AI raters score every record blind, from the recommendation text and page citations only, with no sight of its status or of each other, on four dimensions with written anchors (reach, magnitude, breadth of government, fiscal scale), each 1, 2 or 3. The weight is the mean of the four. Where the raters differ by more than half a point on the weight, or by two points on any dimension, a third rater scores it and the median is used. Where no published fiscal figure could be sourced, the fiscal score is marked estimated. Per-rater scores are stored on each record; a weekly task recomputes the 5th to 95th percentile band over rater disagreement, the rater agreement (quadratic-weighted kappa) and a sensitivity table. Scores are frozen per record and rescored only when the recommendation text changes, never when its status changes. Full procedure: [significance-weighting-method.md](significance-weighting-method.md).

## Estimated timeframes

Every estimated window is an inference, not a fact, and the record says so in `est_completion.basis`. It reasons from the route a recommendation needs: rulemaking usually takes one to two years, legislation needs 60 Senate votes or a budget reconciliation bill, litigation follows court calendars, and the presidential term ends January 20, 2029.

## Headlines change

The record is updated as new information comes in, on the schedule in [PIPELINE.md](PIPELINE.md), and the headline moves with it, including in the weeks around an election. There is no freeze. Every change is dated in the Changes tab and in each record's history, so a reader who sees a different figure from one visit to the next can see exactly what moved and why.

## Limits

The current list is kept in `data/meta/state.json` under `limits` and shown on the Method tab. Standing limits: the enumeration is not yet complete; some primary documents sit behind sites that refuse automated retrieval and are cited by URL without having been read (those records say so); confidence is a reviewer's judgment, not a measurement; significance scores are ordinal judgments with stated anchors, and most fiscal anchors are estimated.

## Related trackers

Other projects count different sets of recommendations with different rules, so their percentages are not comparable with the figures here. Links to outside commentary are given for context and are labeled where the source takes an advocacy stance; nothing from them is used as evidence for a status.
