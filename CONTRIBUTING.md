# Contributing

Corrections are the most useful contribution. A wrong status, a dead link, a missing primary source, a recommendation in the document that is not tracked yet: each of those makes the record better for everyone who reads it, whatever their politics.

## Ways to contribute

1. **Report an error** (no git needed): open an issue with the [Report an error](../../issues/new?template=report-error.yml) form. Give the record id (for example `c14-07`, shown on every record), what is wrong, and a link to the source that shows it. The maintainer or the next research run checks the source and corrects the record with a dated note in its history.
2. **Suggest a recommendation** that is in the document but not tracked: the [Suggest a recommendation](../../issues/new?template=suggest-objective.yml) form. Give the chapter and the printed page numbers.
3. **Open a pull request** that edits a record under `data/items/`, a chapter summary under `data/meta/`, the page under `site/`, or the scripts.

## House rules for the data

These are the rules every research run follows. Pull requests are held to the same ones; `scripts/validate.py` enforces the mechanical parts.

- **Primary sources decide status.** A status change needs a primary source in the record: the Federal Register, congress.gov, govinfo, a court docket or opinion, the White House, or the agency's own site. News reports support dates and context but do not carry a stage change on their own.
- **Every claim is linked.** Timeline events and sources carry an https URL and a date in `YYYY-MM-DD`. Dates are the date of the event in the document that carries it (the rule's publication date, the order's signing date, the court's judgment date), not the date a news story ran.
- **Inferences are labeled.** Estimated windows are inferences and say so in `est_completion.basis`. Uncertainties go in `uncertainties`, not in the status summary as if they were facts.
- **Stay within the rubric.** `progress` stays inside the band for the stage (see the README table). A record that rests on no action having been found stays at or below confidence 50 unless it carries the documented five-part systematic check in `review.source_checks`, and then at or below 70.
- **Neutral voice.** Describe what was recommended and what happened. No adjectives about whether a recommendation is good or bad, no characterizations of motives, no advocacy sources used as evidence. Advocacy sites may be cited for context only when labeled as such.
- **Log the change.** Add a dated note to the record's `history` saying what changed and why, naming the source's host (for example "per the Federal Register notice of 2026-09-30"), never pasting a raw URL into a note.
- **Cross-references are symmetric.** If you add `related_ids` on one record, add the reverse link on the other.
- **No em dashes** anywhere in data or text; use commas, colons, semicolons or parentheses. The validator and the build refuse them.
- **No document text.** The repository holds paraphrases and page citations, never passages from the document being tracked.
- **Privacy.** No names, handles or personal details of private people in records, issues, commit messages or pull requests. The project is published under its own name.

## Pull request flow

```bash
git clone https://github.com/bubbadog/project-2025-tracker.git
cd project-2025-tracker
git checkout -b fix/c14-07-title-x-source
# edit data/items/c14-07.json
python3 scripts/validate.py --strict
python3 scripts/build_snapshot.py && python3 -m http.server 8765 --directory site   # look at the record in the browser
git add data/items/c14-07.json
git commit -s -m "c14-07: add the 2026 Title X funding notice as a primary source"
git push -u origin fix/c14-07-title-x-source
```

Then open the pull request on GitHub and fill in the template. One record or one topic per pull request keeps review quick. The checks run automatically; `validate` and `build` must pass before merge. The maintainer re-reads the source behind any stage change before merging, and merges by squash, so your branch's commit history does not need to be tidy.

### Sign-off (DCO)

Commits are signed off (`git commit -s`), which adds a `Signed-off-by:` line. It states that you wrote the change or have the right to submit it under the project's licenses, per the [Developer Certificate of Origin](https://developercertificate.org/). You can sign off with the GitHub noreply address (`username@users.noreply.github.com`) if you prefer not to publish an email address.

By contributing you agree that code is licensed under Apache-2.0 and data and documentation under CC BY-NC-SA 4.0 (CC BY 4.0 for versions before 2026-10-26), as described in the README.

## Running the checks locally

```bash
python3 scripts/validate.py --strict      # the rules every record must pass
python3 scripts/build_snapshot.py         # assembles site/snapshot.json
npm install && npx playwright install chromium
python3 -m http.server 8765 --directory site &
node scripts/uitest.js                    # opens every record, checks every link and the phone layout
```

Optional pre-commit hooks (`pip install pre-commit && pre-commit install`) run the validator and a secret scan on every commit.

## What is not accepted

- Changes that argue a position, in either direction, in the record text.
- Status changes with no primary source, or with a source the maintainer cannot open.
- Edits that paste passages of the document being tracked.
- Changes to `review.*` fields that make a record look reviewed when it was not. If you change the facts of a record, leave the review block alone and say so in the pull request; the next run re-reviews it.

## Questions

Open a discussion issue, or comment on an existing issue. Security concerns go through [SECURITY.md](SECURITY.md).
