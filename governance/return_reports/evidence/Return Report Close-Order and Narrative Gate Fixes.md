# Return Report: Close-Order and Narrative Gate Fixes

Sep 30, 2026 · @yo

Nine post-review fixes to the D15 Items 3 and 4 release (`b47a088`) are complete at Builder level and now in the working repository; this report is for Architect review before Handbook v2.23. It is a Builder completion report, not final acceptance or independent validation.

## Implemented

A to F are the Principal's numbered review findings; G to I are the two narrative-gate bugs and the prior-value defect raised during testing (labels are the Builder's own).

| ID | Defect found | Fix | File |
| --- | --- | --- | --- |
| A | A blocked "Approve close" still saved the period as "approved" and unlocked its narrative | The approval status is now written only after the close-order and reopen-in-progress checks pass | Dashboard |
| B | AI Narrative tab followed the Close Validation selector, not the sidebar "Current period" | Narrative gate now uses the sidebar period. Approved means a saved close exists in Close History. Annual cadence requires every quarter of that year to be closed | Dashboard |
| C | Reopen-impact message did not match the Principal's wording | Now: "Reopen and close Q2 2026 before closing Q4 2026. Reopening Q1 2026 affected Q2 2026 QoQ." Used only for the reopen-caused case | Dashboard |
| D | A damaged `_baseline.json` or `pending_reprocessing.json` was read as "absent", so the rule failed open | New `ControlFileError`. A damaged file now blocks closing and the narrative. Writes are atomic (temp file, fsync, replace). A damaged baseline is never overwritten | Close history, lifecycle, dashboard |
| E | If a downstream comparison failed after a reopen was archived, the approval aborted half-way | Comparison wrapped by `make_safe_compare_fn`: a period that cannot be compared is treated as affected and a notice is shown. Last-resort fallback `flag_all_closed_downstream` | Lifecycle, dashboard |
| F | A leftover flag on a period no longer affected forced a pointless reopen | `apply_propagation_flags` clears an unresolved flag on any examined downstream period that again matches its own saved close | Lifecycle |
| G | A period flagged as affected by a reopen could still show an approved narrative | Narrative blocked with "Reopen and close Q3 2026. Reopening Q2 2026 affected Q3 2026 QoQ." | Dashboard |
| H | A period with a reopen in progress could still show a narrative | Narrative blocked with "Q3 2026 Reopen closed period is still in progress." This message takes precedence | Dashboard |
| I | After Q2 was corrected, a closed Q3's KPI cards and prompt compared against the corrected Q2, a comparison nobody approved | New `pl_prior_values()` derives the prior figures from the period's own frozen row. Q3 keeps comparing against the original Q2 until Q3 is reopened and re-closed. A never-closed Q3 uses the corrected Q2 | Rollups, dashboard |

Narrative-gate message precedence (`_narrative_gate_block`): reopen in progress, then damaged control file, then unresolved reopen flag, then not approved.

## Files changed

Baseline is `b47a088`. Total: 4 files, 345 insertions, 133 deletions.

| File | Lines before | Lines after | Change |
| --- | --- | --- | --- |
| `Northwind_Financial_Dashboard.py` | 2,990 | 3,060 | A, B, C, G, H, I; reopen-approve bookkeeping (E); notice display |
| `close_history.py` | 558 | 580 | D: `ControlFileError`, validated reads, atomic writes |
| `period_lifecycle.py` | 1,236 | 1,311 | D, E, F: blocker for damaged files, `make_safe_compare_fn`, `apply_propagation_flags`, `flag_all_closed_downstream` |
| `rollups.py` | 1,839 | 1,884 | I: `pl_prior_values()`, region and product priors read the current row first |
| `commentary_workflow.py` | unchanged | unchanged | Included in the Principal's upload; byte-identical to `b47a088` |

The Principal's five uploaded files are byte-identical to the branch tip, checked with `cmp`. Five local commits on `fix/approve-close-check-before-status` (none pushed; the session has no write access):

- `bcb9a2f` Run close-order checks before recording Approve close status (A)
- `1749c58` Reword reopen-impact close-order message (C)
- `1b9a3db` Narrative gate on sidebar period; fail-safe control files (B, D, E, F)
- `6b0508d` Narrative gate: block outdated and mid-reopen periods (G, H)
- `01f47c9` Compare a closed period against its predecessor as of its own close (I)

## Verification and results

All checks ran against the real modules and the running dashboard (Streamlit `AppTest`, `streamlit==1.60.0`, Python 3.12), in temporary copies of the repository. The test scripts are Builder-authored, live outside the repository, and are development evidence only.

**Principal testing (reported 2026-09-30):** the Principal tested fixes A, B, C, G, H and I in their own environment. Fixes D, E and F were not tested by the Principal and rest on the Builder tests below only (16 of 16 unit checks). The details of the Principal's tests are not recorded in this report, and this does not amount to sign-off or independent validation.

| Fix | What was run | Result |
| --- | --- | --- |
| A, C, D | Approve-close flow, wording and damaged-file scripts | Blocked approval no longer recorded as approved; exact C wording shown; damaged file blocks |
| D, E, F | Unit script on `close_history` and `period_lifecycle` | 16 of 16 checks passed |
| B | Gate scenarios script (sidebar period, Annual, unclosed quarters) | 6 of 6 checks passed |
| G, H | Two reproduction scripts for the Principal's scenarios | Both bugs reproduced on the earlier code; both messages correct after the fix |
| I | Corrected-Q2 scenarios on the running app (below) | Behaves as specified in both cases |
| I | Old lookup versus `pl_prior_values()` with no correction present | 52 of 52 comparisons identical, quarterly and annual |

### Fix I: figures observed

Q2 2026 original: opex $2,362,852, profit $1,616,701. Q2 corrected with the Principal's file `q2_2026_v2_correction.xlsx`: opex $2,393,688, profit $1,585,864. Revenue $3,979,552 in both.

| Q3 2026 case | Total Opex vs prior | Operating Profit vs prior | Margin vs prior |
| --- | --- | --- | --- |
| Q3 closed, Q2 corrected, Q3 not reopened (cards) | $2,454,984 vs $2,362,852 (+4.0%) | $1,320,647 vs $1,616,701 (-18.5%) | 35.0% vs 40.5% (-5.5 pts) |
| Same case, narrative prompt | vs $2,362,852 (+3.9%) | vs $1,616,701 | 35.0% vs 40.6% |
| Q3 never closed, Q2 corrected (cards) | vs $2,393,688 (+2.5%) | vs $1,585,864 (-16.5%) | 35.0% vs 40.0% (-5.0 pts) |
| Same case, narrative prompt | vs $2,393,688 (+2.6%) | vs $1,585,864 | 35.0% vs 39.9% |
| Q3 reopened and re-closed (cards) | vs $2,393,688 (+2.5%) | vs $1,585,864 (-16.5%) | 35.0% vs 40.0% (-5.0 pts) |

The Q2 cards show the corrected figures against Q1 (opex $2,393,688, +8.0%). The last three cases were rerun on 2026-09-30 for this report; the narrative prompt for the re-closed case was not rerun separately.

## Regression

- **Whole-app comparison:** every on-screen element of the dashboard was compared against `b47a088` across 8 scenarios. The only differences are the intended Narrative-tab changes (B, G, H).
- **Existing suites:** the four regression suites pass with 49/49, 18/18, 31/31 and 37/37 checks.
- **Fix tests rerun after the last change:** the A, C and D scripts, the 16-check unit script and the 6-check gate script pass again after fix I.
- **Render:** the dashboard renders with no exceptions in every scenario run.
- **Not covered:** see the next section.

## Assumptions and limitations

- **Correction upload not exercised through the UI.** `AppTest` cannot upload files, so "Approve candidate close" was reproduced in code with the same calls the handler makes. One manual upload of `q2_2026_v2_correction.xlsx` is still needed.
- **Human Approval Gate (D13) not re-tested.** Fix A changes when the approval status is written. The independent gate tests were not rerun; only Builder tests were.
- **Fixture provenance.** Closes for Q1 to Q3 were created in temporary directories from the canonical sample dataset, so they are synthetic Builder regression fixtures. The correction file is Principal-supplied and was used as a scenario input, not as an expected answer. None of these results describe the real historical dataset.
- **Other tabs not compared one by one against a corrected Q2.** They read stored prior columns from the frozen current row, which was reasoned from the code and covered only by the whole-app comparison.
- **Rounding difference between cards and prompt** (for example +2.5% versus +2.6% on opex). The prompt uses unrounded figures and the cards use stored ones. It predates these fixes and was left unchanged.
- **Fix I method.** Prior figures are derived as current level minus the stored QoQ or YoY variance from the period's own row, falling back to the prior period's row if the variance columns are missing.
- **Pre-existing, out of scope, not fixed.** `build_test/close_orchestrator.py` and `close_v1_v2_simulation.py` fail to import when run from the repository root.

## Architect review items

These behaviors are now in the canonical code but were decided in review sessions, not in a Builder Brief. Each needs a decision or a Handbook v2.23 entry.

1. **No governing Brief.** Fixes A to I follow Principal instructions given after the D15 Items 3 and 4 review. Please confirm they are accepted as post-release defect fixes.
2. **Definition of "approved" for the narrative (B).** A saved close in Close History, checked against the sidebar period. Annual cadence requires all four quarters of the year to be closed.
3. **Fail-safe rule (D).** A damaged control file blocks closing and the narrative rather than being read as absent. A damaged baseline is never overwritten.
4. **Uncomparable period treated as affected (E).** A downstream period whose comparison fails is flagged and blocks later closes until reopened and re-closed.
5. **Automatic flag clearing (F).** A re-close that shows a downstream period unaffected resolves its stale flag. This is new behavior and should be confirmed.
6. **Narrative-gate precedence (G, H).** Reopen in progress, damaged file, unresolved reopen flag, not approved, in that order. Wording is Principal-specified.
7. **Comparison policy for a closed period (I).** A closed period compares against its predecessor as of its own close, not the predecessor's current figures, until it is reopened and re-closed. This extends the existing two-tier data sourcing rule to the KPI cards and narrative prompt.
8. **D13 Human Approval Gate.** Fix A touches the point at which approval status is written. The independent gate tests should be rerun.
9. **Promotion and provenance.** The Principal promoted the four files by upload. The local branch hashes above will not match the canonical commit.

## Blockers

None for the fixes themselves. The Builder session cannot push to `6-SoGH-9/northwind-autonomous-cfo` (403 from the git proxy), so canonical state depends on the Principal's upload. Not verified by the Builder: that the repository's canonical files are byte-identical to the uploaded ones.
