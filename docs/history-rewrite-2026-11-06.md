# History rewrite of 2026-11-06

The default branch was rewritten once, on 2026-11-06, to replace a personal display name in commit metadata with the account handle `bubbadog`. Four squash-merge commits carried that name as author, and one Dependabot commit carried it in a `Co-authored-by` trailer. Nothing else changed: every rewritten commit has the same files (tree), dates, author and committer email addresses and message as before, apart from those names. The check compared the tree, dates and emails of all 85 commits on the default branch, old against new, and found no difference.

Because each commit's identifier depends on its parent, every commit after the first one changed received a new identifier. Old identifiers cited in earlier notes or links no longer resolve on this branch; use the table below. In MAINTAINING.md the short identifiers in the log were updated to the new ones in the same change.

How it was done: `git filter-branch` with an environment filter on the author and committer name and a message filter on the one trailer, run on a fresh full clone, followed by a single push with a lease on the old tip (`2ae9191171df`). Both default-branch rulesets were switched off by the maintainer for the push and switched back on afterwards.

Forks or clones made before 2026-11-06 should be re-cloned or reset to the new default branch.

| Old | New | What changed | Subject |
|---|---|---|---|
| `80f67c31e664` | `6a99f00e5aa8` | parent only | build(deps-dev): bump playwright to 1.64.0 (#1) |
| `e4e33ca53ddd` | `4ab720558481` | author name | run: 2026-10-13 review3 and leads (five stage changes, three blocked documents read) (#3) |
| `3adfbb28fc7c` | `c2f2d853425a` | author name | docs: Pages address, run merge policy, roadmap status (#4) |
| `0f7617e3b2b1` | `f1c48742c9e1` | parent only | ci: install Playwright from the lockfile so Dependabot bumps take effect |
| `0c65f9684692` | `ba31a3a99f62` | parent only | run: 2026-10-13 late and 2026-10-14 runs (84 records added, chapters 17 to 27 read in full) |
| `f3a7b0ad2bf6` | `3962ac002df8` | parent only | run: 2026-10-14 late, 2026-10-15 layer 3 and update runs (74 records added; first pass complete) |
| `ea192c3365ce` | `23c0e3eebb43` | parent only | data: impersonal register on 33 records, c28-01 decoded, two spot-checks |
| `19628535d02d` | `d5ea72f9fca0` | parent only | run: 2026-10-15 to 2026-10-18 runs (101 records added, enumeration complete, 288 primary-source lifts) |
| `de6915f25f8a` | `124ffadb630b` | parent only | site: headline note reflects the completed enumeration; schedule note current |
| `5c2d15f42665` | `d434b57030cf` | parent only | run: 2026-10-18 late and 2026-10-19 runs (9 stage changes, absence checks complete) |
| `41cdf08f4cac` | `4be173512935` | parent only | site: Method tab reflects the completed enumeration and absence checks |
| `818be266f9b2` | `3a0ac3031a11` | parent only | schedule: one daily run replaces the update, freshness and nightly runs |
| `7e3d02fce105` | `fa5eb5dfa154` | parent only | schedule: 90-day freshness window and a 6 to 4 rotation split in the daily run |
| `05adedd2f943` | `bc64bbf8d71f` | parent only | run: 2026-10-19 retrieval (16 records re-read against newly reachable copies, no stage change) |
| `7ec637ac50f3` | `75b2df3ac9a6` | parent only | docs: maintaining log for the 2026-10-19 retrieval pass |
| `c4605b68bd35` | `9e9fd4f6c4c0` | parent only | run: 2026-10-20 daily (news sweep, 6 freshness and 4 refutation checks, no stage change) |
| `4d9b24050a70` | `956b20e11005` | parent only | prompts: topic searches tied to watch items; Sunday spot-check nomination |
| `b9afe66610c0` | `6cf62881ddc5` | parent only | build(deps-dev): bump playwright (#5) |
| `2570b3524d66` | `5a20a649d153` | parent only | run: 2026-10-21 daily (no stage change; 4 freshness lifts, 4 refutation checks hold, 14 source-check relabels) |
| `8786f6daf6b1` | `ebb0d3685eda` | parent only | run: 2026-10-22 daily (no stage change; CBP postal rule, First Circuit remand on c15-03) |
| `0bf56fd8f26e` | `4fa900792336` | parent only | run: 2026-10-22 courts (12 records re-read against opened court orders; c05-24 to blocked) |
| `63d0ce48df1b` | `e44659a90d42` | parent only | site: Method text names no model; states the U.S. Code and court-copy rules |
| `5e1d4baa9365` | `289a8f148c01` | parent only | run: 2026-10-22 statutes (21 records re-read against U.S. Code, CRS and bill status files); fix page script |
| `b1512b70e062` | `847d2e7464cc` | parent only | ci: fail build and deploy when the page script does not parse |
| `f5314c97a6ed` | `33a179cb54a5` | parent only | ci: ui job no longer advisory; document the pending ruleset change |
| `01d486ea444d` | `65b66c4ab9a8` | parent only | rulesets: ui is a required check (file synced to the live ruleset) |
| `1e74ec0023ce` | `8b7e72d07b8c` | parent only | run: 2026-10-22 documents (15 records re-read against opened official documents) |
| `e9c83ee7f3d4` | `299648427645` | parent only | run: 2026-10-22 sources (lead-only hosts removed or replaced in 25 records) |
| `eb35277d2a0d` | `aa585e2f06ff` | parent only | run: 2026-10-23 daily (four official developments mapped, no stage change); lead-only host rule in the daily prompt |
| `df0782f96a2c` | `67cd086db543` | parent only | site: footer links the data file instead of the repository until the repository moves |
| `d9b632d10943` | `5e3ad0c54978` | parent only | run: 2026-10-23 leads (lead-only host rule applied to 109 records, no stage change) |
| `42c6238573fd` | `a7f3c5f8acd0` | parent only | run: 2026-10-23 backfill part 1 (61 source entries for already-cited documents, 10 lead-only event sources replaced) |
| `ad5d56359363` | `a29b31d23087` | parent only | run: 2026-10-24 daily (NRC reactor-design rule and USTR Section 301 suspension notice mapped; c05-16 weakened; no stage change) |
| `49cdcd0c8459` | `6deb10038888` | parent only | run: 2026-10-24 backfill part 2 (39 source entries for already-cited documents; advocacy-host sweep) |
| `fddc1fa77bc7` | `f4265ed6f426` | parent only | meta: state as of 2026-10-24 from the daily run |
| `351ce33b4592` | `42132ff2314d` | parent only | run: 2026-10-24 backfill part 3 (last 26 source entries; validator now requires every event URL in sources) |
| `e0f0e70ef24d` | `e689a6889757` | parent only | prompt: source-list, encoding and fetch rules; c03-02 First Circuit event re-sourced to the court's opinion |
| `43690bab7230` | `8a0e766b2876` | parent only | run: 2026-10-25 significance (per-rater scores stored on 80 more records; weights unchanged) |
| `77dce2c328a6` | `21d60e3b1f84` | parent only | run: 2026-10-25 daily (Treasury outbound investment and NHTSA FMVSS 108 proposals mapped; c18-12 and c20-16 weakened; no stage change) |
| `d055690b2eff` | `5ea77f0f891c` | parent only | validate: informational notice for unencoded query URLs; c18-01 court copy upgraded to RECAP; c07-06 amicus page made lead-only; c06-11 2026 confirmation |
| `b567134af6a3` | `649ed28c0da5` | parent only | run: 2026-10-26 daily (quiet sweep; six freshness and four refutation checks; no stage change) |
| `23b10da6dc02` | `6643985c75e5` | parent only | review: automated red-team gate and a scheduled review session |
| `f14feb3172d4` | `0bcdefbca46f` | parent only | review prompt: credential fallback before the push |
| `66ec7befa2a5` | `b10229a6ce1f` | parent only | run: 2026-10-26 calibration (40 in-effect records at medium confidence re-read against official documents; 8 to high, 1 down; no stage change) |
| `1f7f838d72a1` | `ca5ff04b9d66` | parent only | run: 2026-10-26 documents (four blocked-host official documents read; c04-04 and c05-08 to high; no stage change) |
| `c15601c6aef7` | `a9241f4e35f6` | parent only | license: data and documentation under CC BY-NC-SA 4.0 from 2026-10-26; data license request form |
| `c2d0d004cca4` | `e20606f2177b` | parent only | docs: qualifying-host rulings in the prompts and method; roadmap item P2 and decisions log |
| `8f2e6718646c` | `426ef9f6e6c7` | parent only | review: c14-59 implemented to in_progress 50 after stage review; host rulings adopted; in effect 115 to 114 |
| `5ba85429baba` | `f188c8b181e8` | parent only | documents pass 2: five retrievals read; c05-16 81, c04-15 80, c05-04 80 under host rulings; c06-11 and c07-06 corrected from the documents |
| `35130e3c4221` | `c6d712cd6d40` | parent only | maintaining: mirror page license wording added in the documents pass 2 row |
| `35e3d598ece9` | `69a6e1342efa` | parent only | c07-06 court status stayed; writing rule: official titles and exact names, never paraphrases |
| `1f9a85f3128e` | `1026b6c1c148` | parent only | leads check: China Coordinator on state.gov, LeBlanc argument date from the clerk's order, Make the Road docket read |
| `200facc284a8` | `3fb191450b8c` | parent only | license wording per CC marking guidance; c06-11 implemented to in_progress 60 after stage review; in effect 114 to 113 |
| `1d80bc0aa404` | `6f6c5ec353e1` | parent only | c05-04: terms of the 2026-07-31 clerk's order on the en banc petition; third retrieval batch reconciled |
| `9fcd8814297e` | `d8d31a7ba97c` | parent only | retrieval routes: automated first, live browser as backup; refusals are leads, never not-found; retrieval prompt template |
| `88a45d4a53d8` | `01f4ecc482c6` | parent only | run: 2026-10-27 daily (quiet sweep; six freshness and four refutation checks; no stage change) |
| `c1c3366382ef` | `983d1fbdba10` | parent only | maintaining: owner's same-day pass on the 2026-10-27 export |
| `07972c0c5d9a` | `b87b6875547c` | co-author trailer | build(deps): bump actions/setup-python (#6) |
| `94b04be29bbb` | `9ebfa843211c` | parent only | run: 2026-10-28 daily (news sweep, Foreword freshness and refutation checks; no stage change) |
| `2a72921b0fd1` | `cf868ef235bf` | parent only | gate: match identifiers as whole words in any case, as validate.py does |
| `d3a6cc08924f` | `47f269beec6e` | parent only | run: 2026-10-28 watch (court and agency documents read; 1 stage change) |
| `db4d42f97a54` | `5088ae7a01e8` | parent only | run: 2026-10-28 wording (retrieval wording replaced in 102 records and 17 run logs; no stage change) |
| `abc08b34374e` | `2bfe987b11af` | parent only | gate: treat state ACLU affiliate sites as lead-only hosts |
| `3da4cfd20a84` | `ac3a28ad1403` | parent only | run: 2026-10-28 batch-a (court and agency documents read; no stage change) |
| `ac0b14cca2ee` | `bc23855861be` | parent only | docs: automated exports push as the automation account and merge after checks (#7) |
| `8859ee5546cc` | `516ecc9e612c` | parent only | run: 2026-10-29 daily (Super Emitter rescission proposed, Supreme Court stay denial; no stage change) (#9) |
| `cd9106e137af` | `8ffcb5d3ebdf` | parent only | docs: owner pass on the 2026-10-29 export (#10) |
| `ef60c2c9de4b` | `202da623f3ed` | parent only | run: 2026-10-30 daily (Section 232 robotics proclamation, Canada Proclamation 11076 published; no stage change) (#11) |
| `3de6d4aa498b` | `0c36921f38a1` | parent only | fix: percent-encode a source-check query address (c17-15); owner pass 2026-10-30 (#12) |
| `041939e5f8b0` | `824e416e382e` | parent only | owner decisions: c13-03 court-status wording, Fed citation rule, c24-02 and c30-04 sources (#13) |
| `768e87cc1d8a` | `24e86792e101` | parent only | run: 2026-10-30 courts (Massachusetts v. Oz decided, Goe v. HHS hearing held; no stage change) (#14) |
| `4a7140f16243` | `068d1dd35282` | author name | run: 2026-10-31 daily (farm bill lapse, DOE bulk-power RFI, H-2A wage order, three court-status corrections; no stage change) (#15) |
| `15c266c7f8a4` | `fdaf220c8c76` | author name | fix: c17-10 court status through the 2026-09-01 order; owner pass 2026-10-31 (#16) |
| `e82ebba8665e` | `945165056b1c` | parent only | run: 2026-11-01 daily and significance (Title V scope rule in effect, rater scores on 80 records; no stage change) (#17) |
| `0be0d2db1367` | `33018e100ff0` | parent only | run: 2026-11-02 daily (Proclamation 11077 published, Medium Landing Ship award, MATS repeal added; no stage change) (#18) |
| `12b977a36b13` | `00705bff8c58` | parent only | fix: c04-19 publisher as the Navy page prints it; owner pass 2026-11-02 (#19) |
| `2b5dc518dcd5` | `f734353a20f4` | parent only | run: 2026-11-03 daily (NRC hearing rule, Arctic Refuge appeal dismissed as moot; no stage change) (#20) |
| `d4f3bb1168d5` | `3453c4a603f6` | parent only | run: 2026-11-04 daily (D.N.J. dismissal of a DOJ FACE Act suit, Proclamation 11045 aluminum onshoring incentive, General License 46 text; no stage change) (#22) |
| `2ae9191171df` | `5c632246347b` | parent only | Add secret scan (gitleaks, full history) (#23) |
