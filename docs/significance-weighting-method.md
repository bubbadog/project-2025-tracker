# Significance weighting: method

Status: in use since 2026-10-08; the band and agreement figures are recomputed weekly (see [PIPELINE.md](PIPELINE.md)). Labels: **Fact** is measured from the data; **Opinion** and **Inference** are judgment calls; standard references are named where a choice follows an established practice.

## 1. The problem it solves

A headline such as "30 percent of counted recommendations are in effect" counts a government-wide tax law and a single pilot program as one recommendation each. That is a fair criticism of any unweighted tally. A weighted figure answers it only if the weights are transparent, reproducible by a reader, independent of status, and shown with their uncertainty. The method follows the OECD and JRC Handbook on Constructing Composite Indicators (2008) for the aggregation and sensitivity steps, and standard inter-rater reliability practice (Cohen's kappa, Landis and Koch's interpretation bands) for the scoring step.

## 2. What "significance" means here

Significance is the expected consequence of the recommendation for people in the United States if it were fully carried out, judged from the recommendation itself, not from whether or how far it has been carried out. It has nothing to do with whether the recommendation is good or bad. Two recommendations on opposite sides of a question can both be highly significant.

## 3. The rubric (four dimensions, each scored 1, 2 or 3)

Ordinal scores with written anchors are used on purpose: they avoid false precision and can be checked by a reader without expertise (Opinion, following the Handbook's guidance on ordinal scales).

| Dimension | 1 | 2 | 3 |
| --- | --- | --- | --- |
| **R. Reach**: share of people in the US whose lives, money, rights or services the recommendation touches directly if fully carried out | A narrow group (one program's grantees, one profession, one small agency's staff), roughly under 1 percent of the population | A large group (a benefit population, an industry's customers, a region, federal employees), roughly 1 to 20 percent | Most people, the whole economy, or the structure of the federal government itself |
| **M. Magnitude**: size of the effect on those reached | Procedural or marginal: reporting, process, naming, internal organization with little outside effect | Material: a real change in money, eligibility, obligations, enforcement or services for those reached | Large: changes what is legal, who is eligible for a major program, or costs or benefits at a scale that changes behavior |
| **B. Breadth of government**: how much of the government the recommendation changes | One office, program or rule | One agency or one sector's regulatory scheme | Government-wide, multi-agency, or a change to the constitutional or statutory architecture (civil service, independent agencies, the budget process) |
| **F. Fiscal scale**: annual federal dollars moved, cut, raised or redirected, or the regulated economic activity at stake | Under roughly 1 billion dollars a year, or no identifiable fiscal effect | Roughly 1 to 50 billion dollars a year | Over roughly 50 billion dollars a year, or a structural change to taxes, entitlements or the budget |

Anchors for F use published figures where they exist (CBO, CRS, OMB, agency budgets). When no figure can be sourced, the rater scores F by the nearest anchor and marks it estimated (`F_estimated`), and the uncertainty band treats estimated F scores as uncertain (section 6).

## 4. From scores to a weight

Weight of recommendation i: w_i = (R_i + M_i + B_i + F_i) / 4, so w ranges from 1 to 3 and no recommendation can count more than three times another. Equal weights across dimensions is the Handbook's default when there is no empirical basis for anything else (Fact about the Handbook; Opinion that it applies here). The cap matters: without it a handful of recommendations would dominate, and the figure would reflect the rater's view of those few more than the record as a whole.

Alternative aggregation kept for the sensitivity analysis: the geometric mean (R·M·B·F)^(1/4), which penalizes a recommendation that scores high on one dimension and low on the others. If the two aggregations disagree on the headline by more than two percentage points, both are reported.

## 5. The weighted figures

- Weighted share in effect = Σ w_i · [recommendation i is implemented or completed] / Σ w_i.
- Weighted progress score = Σ w_i · progress_i / Σ w_i.

Both sit next to the unweighted figures, never in place of them. The unweighted share is the headline; the weighted share is the second number, with its band.

## 6. Reliability and uncertainty

**Blind scoring.** Two independent AI raters score every recommendation from the id, chapter, title, recommendation paraphrase and page citations only. They do not see the stage, progress, evidence, confidence or each other's scores. This removes the obvious circularity: a recommendation must not look more significant because it has been carried out. Each rater's own four scores are stored on the record (`significance.rater_scores`).

**Agreement.** For each dimension and for the composite, quadratic-weighted Cohen's kappa between the two raters. Target κ ≥ 0.6 (Landis and Koch: substantial). Any recommendation where the two composites differ by more than 0.5, or any dimension differs by 2 points, goes to a third rater, and the median of the three is used.

**Band on the weighted share.** A bootstrap over rater disagreement: for each of 1,000 draws, take each recommendation's weight from one of its raters at random (and, for F scores marked estimated, from the neighboring anchors as well), recompute the weighted share, and report the 5th to 95th percentile. If the band is wider than 10 points the weights are not telling the reader anything and the band is not published (it is still stored). Recomputed weekly from the stored per-rater scores.

**Sensitivity analysis (reported with the figure).** Leave-one-dimension-out (four recomputations), geometric versus arithmetic aggregation, and a cap of 2:1 instead of 3:1. The page shows the central figure and the band; `data/meta/state.json` under `significance` holds the full table.

## 7. Publication and neutrality

- The rubric, every recommendation's four scores, its weight, each rater's scores, the rater agreement and the sensitivity table are public (the Method tab and the data files), so any reader can recompute the figure or rescore a recommendation and see what changes.
- Scores are frozen per recommendation and versioned. They are rescored only when the recommendation text of the record changes (not when its status changes), and the change is logged in the record's history.
- Wording on the page: "Weighted by significance, where significance means how many people a recommendation would reach, how much it would change for them, how much of the government it touches, and how many dollars it moves. It says nothing about whether a recommendation is good or bad."

## 8. Results so far (Fact, from `data/meta/state.json`, as of 2026-10-11)

Over the 257 counted recommendations scored at that date: weighted share in effect 29.3 percent against 30.0 unweighted; weighted progress 41.2 against 41.6. Rater agreement on the first 219 (quadratic-weighted kappa): reach 0.80, magnitude 0.88, breadth 0.89, fiscal 0.89, composite 0.92; exact agreement 84 to 91 percent per dimension; four records adjudicated by a third rater. Sensitivity: geometric mean 29.1, cap 2:1 29.5, leave-one-dimension-out 28.8 to 29.8. Weight distribution: 115 records at 1.0 to 1.5, 117 at 1.75 to 2.25, 25 at 2.5 to 3.0. Fiscal anchors are estimated on 204 records (no published figure found); sourcing them from CBO, CRS and budget documents is the open improvement. The weighting barely moves the headline, which is itself a finding worth stating (Opinion): the in-effect share is not driven by small items.

The page recomputes the weighted share live from the scores on each record, so the figure shown is always for the current counted set; the band and kappa are refreshed by the weekly run.

## 9. Alternatives considered and why not (Opinion)

- **Budget-only weighting**: objective and sourced, but misses rights, eligibility and structure (a civil-service change has a small budget line and a large effect).
- **Press-coverage weighting** (how often a recommendation is written about): measures salience, not consequence, and imports media attention bias into a page that claims neutrality.
- **Expert elicitation**: the right tool in principle, but an anonymous project has no panel, and a hand-picked one would be the first thing critics attack.
- **A single 1 to 5 "importance" score**: faster, but hides the reasoning; four anchored dimensions make the disagreement visible and fixable.

## 10. What this does not do

It does not weight by likelihood of completion, by legal durability, or by direction of effect. Durability is already a field on every record. Direction is deliberately excluded: weighting by whether an outcome is good or bad would make the tracker an argument.
