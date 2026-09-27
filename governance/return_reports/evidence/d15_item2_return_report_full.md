# Builder Return Report: D15 Item 2 Corrections, Complete Implementation

**Author:** Builder
**Date:** 2026-09-27
**Starting point:** the repository, at commit `9ecf530759c6da60da425b7f4cedd16e0c155483` (`main` of `6-SoGH-9/Northwind-Autonomous-CFO`)
**Deliverable:** `d15_item2_implementation.diff` (complete, against the base commit above) plus the four updated `.py` files
**Status:** Builder completion for Bug/Changes 3, 4, 6, the reopen "stuck" fix, and the PL_Summary source-of-truth fix. Not independently validated, not committed, not pushed, not canonically synchronized. Bug/Change 5 is not implemented (parked at the Principal's instruction, see Section 10).

---

## 1. Scope and authority

| Item | Source | Outcome |
|---|---|---|
| Bug/Change 3: reopen must show Candidate commentary directly, dataset optional, saved dataset kept | Principal, this engagement | Implemented |
| Bug/Change 4: commentary upload on a reopened period must behave exactly like Commentary Review (Phase 4 to 6) on a not-yet-closed period | Principal, this engagement | Implemented |
| Follow-up to 3: reopen "stuck" without a candidate | Principal report ("cannot directly submit a commentary file") | Implemented |
| Bug/Change 6: upload-time compatibility review of a corrected dataset | Principal, this engagement | Implemented (three requested checks plus three additions, Section 3.4) |
| PL_Summary source-of-truth fix: `Total Revenue ($)` / `Total Opex ($)` computed from Revenue/Expenses instead of the unverified `PL_Summary` sheet | Principal, this engagement (Category A defect, released standalone) | Implemented |
| Bug/Change 5: replaced dataset ignored after a close exists | Principal, this engagement | Reproduced and root-caused only. Parked by the Principal. No code written. |

Working method: repository inspected directly at the base commit above; Handbook, Addendum 3 and the relevant briefs read; every change built on the actual repository, not on assumption.

---

## 2. Baseline

The base commit is `9ecf530759c6da60da425b7f4cedd16e0c155483`. Everything in `d15_item2_implementation.diff` and in this report is Builder work on top of that commit, verified by `git apply --check` against a fresh checkout of it and by comparing the resulting blob hashes to the working repository (Section 5).

---

## 3. Implemented

### 3.1 Bug/Change 3: Candidate commentary shown directly; saved dataset kept

Problem reproduced first (unmodified base commit): after "Confirm reopen", no Candidate commentary section existed until a dataset was attached and "Run correction intake" was clicked.

Now:
- On a reopened period the candidate is built automatically from the dataset saved in that period's own Close History entry, through the existing Item A path (`enforce_period_scoped_correction` then `_run_candidate_pipeline`). No second code path was added.
- The auto-build is state-driven (Section 3.3), not tied to one click.
- The corrected-dataset uploader remains, as an optional replacement. "Run correction intake" is offered only once a replacement file is attached and has passed the upload review, so it can never silently revert an applied correction to the saved dataset. "Start over" is the explicit way to revert.
- Step 1 warning text and the uploader label reworded, since they said data was required.
- Item F's zero-net-change guard is unchanged: a reopen with no dataset change and no commentary change is still blocked with "nothing to correct".

### 3.2 Bug/Change 4: reopen commentary behaves exactly like Commentary Review (Phase 4 to 6)

Approach: the live upload, matching, validation and review logic was moved verbatim (same lines, dedented) out of the not-yet-closed close workflow into one shared function, `_render_commentary_intake_and_review()`. The live close and the reopen candidate now call the same function. The two callers differ only in the data they pass:

| Input | Live close | Reopen candidate |
|---|---|---|
| Headcount and expense evidence | `R.hc_dept_q`, `R.exp_by_dept_cat_q` | The candidate's own `rollups_output.xlsx` (`Headcount_Q`, `Exp_by_Dept_Cat_Q`), so Phase 6 evidence reflects the corrected numbers |
| Headcount band | live Phase 3 result | candidate Phase 3 result |
| Semantic "already attempted" set | session-level set | held in the candidate and carried across intake re-runs with the commentary (Item I) |
| Approval reset on a revision (Gate B.6) | live per-period status | candidate approval status (`_candidate_approval_status_for` and its setter) |
| Uploader key and label | `commentary_uploader_<n>` | `candidate_commentary_uploader_<n>`, label "Commentary.xlsx for this candidate (optional)" |

Result on a reopened period: deterministic matching, exclusivity, gated semantic reconciliation, Phase 6 validation of every matched commentary, the four-metric block, Phase 5 note for unmatched entries, manual reconciliation, edit and revalidate, Mark Accepted, version history, accepted-commentary preview. On approve, the archived `commentary_record` carries the validation results and accepted version, with the same structure as a live close.

Related changes:
- `period_lifecycle._commentary_snapshot_by_oid` (Item F): the candidate side now resolves "current" as the accepted version, else the last entered, exactly as the prior side already did. Previously it always read the last entered version, which was only correct while a candidate had no Accept step.
- `_disabled_semantic_fn` (Addendum 2 stub) removed, since nothing calls it any more.
- The "matching only, no Phase 5/6" heading and caption replaced by the standard Commentary Review heading and caption.

### 3.3 Reopen "stuck" fix (follow-up to Bug/Change 3)

Defect introduced by 3.1: the auto-build fired only on the single "Confirm reopen" click (a one-shot flag). A reopen already at the intake step when the app reloaded, or any failed build, left no candidate, no Commentary Review and only "Start over".

Now:
- The build runs whenever a reopen is active and no candidate exists for that period, no earlier attempt has failed, and no out-of-period conflict is awaiting Continue or Cancel. Derived from session state on every render.
- A failed build stores its error, the error is displayed (a rerun is forced so it is not lost), and it is not retried in a loop. "Start over" and "Confirm reopen" clear the error, so a retry is possible.
- The residual "no approved data" and scope-check failures now go through the same stored, displayed error path.

### 3.4 Bug/Change 6: upload-time compatibility review of a corrected dataset

Problem reproduced from the Principal's report: a wrong or corrupted file was only examined when "Run correction intake" was clicked, surfacing the raw pipeline traceback (`Worksheet named 'Expenses' not found`), and in some cases the message was not visible until the file was removed.

New pure function `period_lifecycle.validate_correction_upload(file_bytes, target_period, R_module)`, called by the dashboard every time a file is attached. The first failing check is shown under the uploader while the file is still attached. "Run correction intake" is not offered for a file that fails.

Checks, in order (as amended by the PL_Summary fix, Section 3.5):

| # | Check | User-facing message |
|---|---|---|
| 1 | Is it a dataset file? (opens as .xlsx and contains at least one dataset sheet) | You have not uploaded a dataset file. |
| 2 | Are all dataset sheets present? (Revenue, Expenses, Headcount, Budget_vs_Actual; `PL_Summary` no longer required, Section 3.5) | The categories are missing in the dataset you have uploaded: <sheets>. |
| 2b | Do present sheets have the columns the pipeline needs? (addition) | The categories in the dataset you have uploaded do not have the expected columns: <sheet (column)>. |
| 3 | Are values valid? Text in numeric columns, invalid dates, blank dates (additions, found by testing, Section 8) | The dataset you have uploaded contains values that are not valid: <sheet (column: n non-numeric values / n blank or invalid dates)>. These columns must contain only numbers (and valid dates). |
| 4 | Is there data for the reopened period in every category? | There is no data in the dataset you have uploaded for the categories (<sheets>) matching the period you are reopening (<period>). |

Also:
- Any residual pipeline failure is shown as its plain first sentence; the subprocess log is kept in a "Technical details" expander.
- Fully empty rows are ignored (pandas drops them). Blank numeric cells are not flagged (Section 9).

### 3.5 PL_Summary source-of-truth fix

**Problem.** `PL_Summary` is a hardcoded, unverified sheet supplied by Controlling for reference only. `rollups.py`'s `build_pl_rollup()` sourced the P&L headline figures (`Total Revenue ($)`, `Total Opex ($)`, and the `Operating Profit`/`Operating Margin` derived from them) directly from it, with no independent verification. These figures feed every KPI card on the dashboard and the AI narrative.

**Required behavior implemented, exactly as released:**

1. `build_pl_rollup()` now computes `Total Revenue ($)` and `Total Opex ($)` from the `revenue` and `expenses` DataFrames, using the identical `groupby(period_col)[...].sum()` already used elsewhere in the file for the equivalent tie-out. `Operating Profit ($)` and `Operating Margin (%)` are derived exactly as before, no change to that arithmetic.
2. The three checks that tied `pl_q`/`pl_y` out against `PL_Summary` (revenue quarterly, opex quarterly, revenue annual) were removed entirely, not converted to a hard rejection. Once `pl_q` is itself sourced from Revenue/Expenses, comparing it to `PL_Summary` would only compare it to something independent of it again, which is the point, but the instruction was explicit: delete, don't reject.
3. `period_lifecycle.py`'s upload review (Section 3.4): `PL_Summary` removed from `DATASET_REQUIRED_SHEETS`, `DATASET_REQUIRED_COLUMNS`, and `DATASET_NUMERIC_COLUMNS`. A corrected dataset missing, or with a malformed, `PL_Summary` sheet is now accepted.
4. The `PL_Summary` load itself was not removed, per instruction. It was, however, wrapped in a `try/except ValueError`, and this is the one finding flagged rather than silently decided (see below).

**Concrete finding, flagged not decided.** Confirmed by direct execution that the unguarded `pd.read_excel(xl, "PL_Summary")` crashes the entire pipeline (`ValueError: Worksheet named 'PL_Summary' not found`) the moment a dataset lacks that sheet, which item 3 above now permits at upload. Since nothing downstream reads `pl_summary` any more, the load was wrapped in `try/except` so a missing sheet degrades to an empty frame instead of halting the pipeline. This was the smallest change consistent with "do not remove the load" while still meeting the brief's own acceptance criterion that a `PL_Summary`-less upload "produces correct candidate figures." Flagged in Section 10, item 8.

**A live-testing episode worth recording as evidence.** The Principal tested the standalone `pl_summary_source_of_truth_fix.diff` against a real uploaded dataset and saw KPI cards of $141,797,186 revenue, -487.0% operating margin. Diagnosis (Section 6) showed this was not a defect in the fix: the diff applied had not included the `build_pl_rollup()` change (a separate, older diff was applied instead), so the dashboard was still reading `PL_Summary` directly, and this particular test file's `PL_Summary` sheet turned out to genuinely disagree with its own Revenue/Expenses sheets by exactly the reported tie-out gap ($137,780,280.00 revenue, $829,960,298.91 opex). This is direct, real-world confirmation of the defect this fix exists to close: a dashboard sourced from `PL_Summary` can silently show numbers that disagree with the underlying transactional data by orders of magnitude. Once the complete, combined diff (this document's `d15_item2_implementation.diff`) was applied, the Principal validated the fix.

---

## 4. Files changed

Base commit `9ecf530`. "Delta" is what changed against that base commit; this is exactly what `d15_item2_implementation.diff` contains.

| File | Final lines | Final blob | Delta vs base |
|---|---|---|---|
| `Northwind_Financial_Dashboard.py` | 2419 | `ecf2605410e0` | +1269 / -527 |
| `close_validation.py` | 519 | `f9301f038c51` | +86 / -0 |
| `period_lifecycle.py` | 874 | `3cdd5eec1ad8` | +428 / -1 |
| `rollups.py` | 1621 | `7f852ea0afcf` | +61 / -39 |
| **Whole diff** | | | **4 files, +1844 / -567** |

Of `period_lifecycle.py`'s total delta, +14 / -15 is the PL_Summary fix specifically (on top of the Bug 3/4/6 delta already in the file); `rollups.py`'s entire +61 / -39 is the PL_Summary fix, since that file was untouched by Bug 3/4/6.

New or moved definitions:

- `Northwind_Financial_Dashboard.py`: `_render_commentary_intake_and_review`, `_mark_live_commentary_file_supplied`, `_candidate_approval_status_for`, `_set_candidate_approval_status_for` (new); live Commentary Review block replaced by a call to the shared function; reopen candidate block rewritten to call it; state-driven auto-build; upload validation wiring; friendly error display; `_disabled_semantic_fn` removed.
- `period_lifecycle.py`: `validate_correction_upload`, `CorrectionUploadCheck`, `CheckResultNotDataset`, `DATASET_REQUIRED_SHEETS`, `DATASET_REQUIRED_COLUMNS`, `DATASET_NUMERIC_COLUMNS`, `CHECK_*` constants (new); `_commentary_snapshot_by_oid` candidate branch (changed); `PL_Summary` removed from the three `DATASET_*` constants and from the invalid-values loop's dead special case.
- `rollups.py`: `build_pl_rollup()` rewritten to source from `revenue`/`expenses`; the `PL_Summary` load wrapped in `try/except`; the three `PL_Summary` tie-out checks (8a, 8c, 8d) removed; comments referencing `PL_Summary` as a tie-out target corrected in three other places (module docstring, section 11 header, criterion 13 comment).

Delivered artifacts:

| Artifact | Purpose |
|---|---|
| `d15_item2_implementation.diff` | Complete diff against `9ecf530`, all four files. Applies cleanly to a fresh checkout; resulting blobs equal the working repo's (Section 5). |
| `Northwind_Financial_Dashboard.py`, `close_validation.py`, `period_lifecycle.py`, `rollups.py` | The four updated files, complete |
| `builder_test_scripts.zip` | Test drivers and fixture generators used for Section 5 |
| `bug6_test_files.zip` and `bug6_test_files_README.md` | 40 upload fixtures with expected results (synthetic) |

No other repository file was modified. Nothing was committed or pushed.

---

## 5. Verification (what was actually executed)

**Environment.** Python 3.11.15 in an isolated venv (system environment untouched). `pandas==2.2.3`, `openpyxl==3.1.5`, `streamlit==1.60.0` as pinned. **`numpy==2.4.6` instead of the pinned `2.5.1`**: 2.5.1 is not available on the package index reachable from this sandbox (newest available is 2.4.6). Streamlit `AppTest` was used to run the real dashboard script headlessly. Tests ran in scratch copies of the repo so the repo, `rollups_output.xlsx` and `close_history/` were never polluted.

**Method.** Full user flows against the actual app: approve a close, request reopen, both confirmations, attach files, run intake, edit commentary, accept, approve candidate, inspect what Close History actually contains (versions, saved datasets, `commentary_record`). For the PL_Summary fix specifically: direct execution of `rollups.py` (not just import/inspection) against the canonical dataset and against constructed fixtures, plus the full `AppTest` suite.

**Test-harness stand-in.** `AppTest` cannot drive real file uploads. The uploader widget was replaced by a stand-in that returns real `.xlsx` bytes; all application code downstream of the widget ran unmodified. Separate runs with the real widget (`t8`) confirmed the correct uploaders render in the correct states.

**Diff integrity.** `git apply --check` and `git apply` of the final combined diff onto a fresh checkout of `9ecf530`, then blob comparison against the working repo:

| File | Applied blob | Working repo blob |
|---|---|---|
| `Northwind_Financial_Dashboard.py` | `ecf2605410` | `ecf2605410` |
| `close_validation.py` | `f9301f038c` | `f9301f038c` |
| `period_lifecycle.py` | `3cdd5eec1a` | `3cdd5eec1a` |
| `rollups.py` | `7f852ea0af` | `7f852ea0af` |

Compile check passed on all four.

**PL_Summary fix, specific verification:**

| Check | Method | Result |
|---|---|---|
| Canonical dataset: all remaining tie-out checks | Direct execution of `rollups.py` | All checks pass, max diff $0.0000 on every remaining check |
| Canonical dataset: KPI figures unchanged | Compared `PL_Quarterly`/`PL_Annual` output, base run vs modified run | Total Revenue/Opex identical to the cent; Operating Profit/Margin/variance columns differ by ~1e-10 (floating-point summation-order noise, not a data change). Q4 FY2026 Operating Margin: 0.382023 both before and after |
| Dataset missing `PL_Summary` entirely | Upload review (`validate_correction_upload`) + full pipeline run | Upload accepted; pipeline exits 0; all 16 remaining checks pass; KPI figures identical to the canonical run |
| Dataset with a malformed value in `PL_Summary` | Same | Upload accepted; pipeline exits 0; all checks pass |
| `AppTest` suites written for the old (`PL_Summary`-required) behavior | Three stale assertions (in `t11`, `t13`, `t16`) updated to the new intended behavior and rerun | 49 checks, 0 failures |
| Full repository regression suite | All ten `AppTest` suites rerun after the fix | 0 failures across the board |

**Scenario suites executed (final code, all passing):**

| Suite | Covers | Checks |
|---|---|---|
| `t1`, `t4`, `t5` | Bug 3: direct display, saved dataset kept, commentary-only correction to v2, unchanged input blocked, dataset replacement with commentary carry-over, one-shot behaviour, Start over, Reject, out-of-period Continue/Cancel | 32 (t1 prints 4 observations; t4 16; t5 16) |
| `t6` | Bug 4: live versus reopen signature equality, Phase 6 on reopen, unmatched and manual reconciliation, revision, accept, v2 record shape, Item F semantics, evidence from candidate data | 17 |
| `t7`, `t8` | Live close regression, closed-period read-only view, real-widget checks | 9 |
| `t9` | Stuck reopen fix: mid-reopen state, failing build, no retry loop, recovery | 6 |
| `t11`, `t13`, `t16` | Bug 6 plus PL_Summary fix: every check, every sheet, values, dates | 49 |
| **Total** | | **113 checks, 0 failures** (plus t1's 4 printed observations) |

**Repository regression scripts** (`build_test/*.py`, each run on a clean copy of the base tree and of the fully modified tree, exit code captured correctly):

| Script | Base | Modified |
|---|---|---|
| `close_orchestrator.py` | exit 1 | exit 1 (identical failure, byte-identical traceback, see Section 10) |
| `close_v1_v2_simulation.py` | exit 1 | exit 1 (identical failure, byte-identical traceback, see Section 10) |
| `commentary_workflow_demo.py` | 0 | 0 |
| `d15_5a_versioning_demo.py` | 0 | 0 |
| `d15_5e_5g_5h_demo.py` | 0 | 0 |
| `phase4_semantic_reconciliation_demo.py` | 0 | 0 |

---

## 6. Results (actual observed values)

**Bug 3.** Baseline: after Confirm reopen, buttons `reopen_run_correction_btn, reopen_reset_btn`, no Candidate commentary, no candidate. After change: candidate present, `numerical_impact = False`, Candidate commentary shown, no intake button. Candidate workbook content equals the saved v1 dataset on all six sheets (bytes differ because the workbook is rewritten; content compared). Commentary-only correction: v2 archived, v2 dataset equals v1 content, commentary recorded, v1 untouched. Same commentary and data again: blocked, no v3.

**Bug 4.** Same commentary file through the live review and through the reopen flow: identical assessment ("Insufficient / Requires Clarification"), identical controls, metric block, warnings and archived record keys. Phase 6 evidence check: after replacing the dataset so that Sales & Marketing Other Opex moved, the reopen validation cited **-18,517.18**, the candidate's own variance, and not **+2,184.34**, the approved one.

**Stuck fix.** With the reopen forced to the intake step and no candidate: candidate built automatically and commentary submitted directly and validated. With the build forced to fail: error displayed, exactly one attempt across repeated reruns, recovery after Start over.

**Bug 6.** Principal's own file (`Kopie`, letter "A" typed over numbers) before the values check: accepted at upload, then pipeline `TypeError: unsupported operand type(s) for +: 'float' and 'str'`. After: refused at upload with `Revenue (Revenue ($): 441 non-numeric values); Expenses (Amount ($): 420 non-numeric values); Headcount (Headcount: 129 non-numeric values)`. Date matrix (5 sheets by 4 cases: one letter, many letters, blank, malformed): before the blank-date fix all four letter and format cases were refused but blank dates in every sheet were accepted and crashed the pipeline (`IntCastingNaNError`); after, all 20 refused with plain text, no technical text, no intake button, existing candidate untouched.

**PL_Summary fix.** Canonical dataset: Q4 FY2026 Total Revenue $4,016,905.92, Total Opex $2,462,355.83, Operating Margin 38.2% (identical before and after, see Section 5 table). Dataset with `PL_Summary` deleted entirely: pipeline runs clean, identical KPI figures. Real-world confirmation via the Principal's own test: a dataset whose `PL_Summary` sheet disagreed with its own Revenue/Expenses by $137,780,280.00 (revenue) and $829,960,298.91 (opex) produced a dashboard showing $141,797,186 revenue and -487.0% operating margin **when the fix was not actually applied** ($4,016,905.92 + $137,780,280.00 = $141,797,185.92, and $2,462,355.83 + $829,960,298.91 = $832,422,654.74, both matching the displayed cards to the dollar). This confirms both the defect (an unverified `PL_Summary` sheet can silently drive dashboard figures far from the transactional data) and, once the complete diff was applied, that the fix closes it; the Principal validated the corrected behavior.

---

## 7. Regression

Checked and unchanged: live close (upload, match, Phase 6, four-metric block, approve archives v1 with commentary, reruns idempotent, Section G "file supplied" flag); closed-period read-only Commentary Review from Bug/Change 2 (no live uploader, no edit or accept controls, no metric block, version history retained); Items A (scope warning, Continue and Cancel), F (guard), G (uploader reset), H (persistent summary), I (commentary carry-over), J, K; approval gate per period; every other `rollups.py` tie-out not touched by the PL_Summary fix (Region/Product Net-of-cost, Breadth/Concentration, S&B volume/rate bridge, Cost Structure Investigation View, Cost Category-only view: all re-executed, all still pass at $0.0000 max diff); the six repository scripts above.

---

## 8. Defects found and fixed during this work (Builder-caused or Builder-missed)

1. **Reopen stuck without a candidate** (introduced by Bug/Change 3, Section 3.3). Fixed.
2. **Upload review missed non-numeric values.** First version of Bug/Change 6 checked file type, sheets, columns and period rows but not values; the Principal's file passed and crashed the pipeline. Fixed (check 3).
3. **Upload review missed blank dates.** Found by testing dates across all sheets when asked. Fixed.
4. **`PL_Summary` load, unguarded, crashes the pipeline once `PL_Summary` is optional at upload.** Found by direct execution before delivering the PL_Summary fix, not reported by the Principal. Fixed by wrapping the load in `try/except` (Section 3.5), flagged rather than decided silently.
5. **Three `AppTest` assertions hardcoded the old, superseded `PL_Summary`-required behavior.** Found while re-running the full suite after the PL_Summary fix. These are Builder's own regression fixtures (not independent UAT), so they were updated to the new intended behavior rather than left failing. Listed here for transparency, not hidden as a clean pass.
6. Test-side mistakes corrected along the way in earlier sessions (wrong expected counts, a harness module cache, an exit-code capture bug that briefly reported all scripts as passing). None affected the product; each was caught and the results re-derived correctly before reporting.

---

## 9. Assumptions and limitations

- **Semantic reconciliation has never run against a live model.** No `ANTHROPIC_API_KEY` exists in this environment. Both flows show the identical "unavailable" message. This is the same open gap the project already tracks (Handbook Section 13). The reopen flow now reaches that code path; it is unexercised live in both places.
- **Real file uploads** were not driven (stand-in described above).
- **numpy 2.4.6 instead of the pinned 2.5.1.**
- **Synthetic fixtures.** All test data is Builder-created regression material derived from the canonical sample dataset. It is suitable only for Builder regression. It is not evidence about real or historical data and it is not independent UAT.
- **Blank numeric cells are accepted silently.** They do not crash the pipeline (executed), but the P&L then treats them as missing. Not flagged, to stay within the requested scope.
- **A numeric-looking text cell such as "12345" is accepted**, because pandas (and `rollups.py`, which reads the same way) reads it as a number.
- **Upload review is tuned to the reopened period's label** and the four required dataset sheets. It does not validate cross-sheet consistency (Section 10, item 5).
- **Bug/Change 4 evidence source:** candidate Phase 6 uses the candidate's own rollups output (a design choice made to avoid validating against uncorrected numbers).
- **`PL_Summary` is still loaded and parsed** (Section 3.5, item 4) even though nothing reads it downstream any more. It was kept per instruction rather than removed outright.
- The Handbook, briefs and READMEs were **not** updated (Architect and PM maintained); this report is submitted for that purpose.
- Nothing is committed, pushed or canonically synchronized. The working clone lives only in this session.

---

## 10. Architect review items

1. **Addendum 3, Item L, criterion L1 superseded.** L1 said "attach no dataset, run correction intake, candidate is built". The candidate is now built automatically and the intake button appears only with a replacement file attached. L2 to L4 still hold (all exercised).
2. **Addendum 1, Item E scope superseded.** Item E specified candidate commentary as matching only, no Phase 5 or 6. Bug/Change 4 requires the full Phase 4 to 6 experience.
3. **Item F candidate-side "current version"** now honours the accepted version (Section 3.2). Confirm this is the intended equivalence.
4. **Refactor of the live Commentary Review block** into a shared function (moved verbatim). Behaviour verified equal (Section 6), but it touches previously accepted code.
5. **Pre-existing, not introduced by this work: cross-sheet consistency of an uploaded dataset is not enforced anywhere.** The PL_Summary fix removes the one check that would have caught an internally inconsistent dataset (Expenses changed, `PL_Summary` not); no other check replaces it, because `PL_Summary` is now correctly treated as non-authoritative rather than as a verification target. There is no remaining mechanism that would catch, say, an uploaded `Revenue` sheet whose total disagrees with an uploaded `Budget_vs_Actual` sheet's stated Revenue actuals. Decision needed on whether cross-sheet consistency should be enforced some other way, or is out of scope.
6. **Pre-existing: `build_test/close_orchestrator.py` and `build_test/close_v1_v2_simulation.py` fail on the untouched base commit**, both with a `ModuleNotFoundError` (`close_history`, `close_validation` respectively): a script-location/`sys.path` issue, not a code defect. Identical failure, byte-identical traceback, on the fully modified tree. Unrelated to this work; flagged again here since this report supersedes the prior one, which described a different pre-existing failure in this same script (an `AttributeError` from an earlier repository state); the two are not the same defect, and the current one should be tracked instead.
7. **Bug/Change 5 (parked), decision needed before implementation.** Reproduced: after a close exists, `rollups.find_raw_dataset()` resolves the latest approved close's archived dataset ahead of any loose dataset file, so replacing `Northwind_Sample_Dataset.xlsx` has no effect. Recommended rule if resumed: treat a loose dataset as "incoming" only if its content matches no dataset archived in Close History, so the seed file and corrected versions stay "known" and the reload-after-approve behaviour is preserved. Open questions: scope (whole app or Close Validation only) and behaviour for an already-closed period.
8. **`PL_Summary`'s load is now dead code protected by a try/except, not removed.** (Section 3.5, item 4, Section 9.) Confirm whether the Architect wants it removed outright in a future pass, given nothing reads it, or kept as-is for provenance/possible future use.
9. **`PL_Summary` no longer has any required columns in the upload review** (Section 3.4, superseding item 8 of the prior report, which said it gained two required columns; that was reversed by this fix). Confirm this matches the intended dataset contract going forward.

---

## 11. Blockers

None for the delivered scope. Outstanding: Principal/Architect decisions in Section 10 (items 5, 7, 8), and the promotion step (commit, review, canonical sync), which remains with the Principal.

---

## 12. What was implemented, executed, demonstrated, untested, unverified

| | |
|---|---|
| **Implemented** | Bug/Changes 3, 4, 6, the stuck-reopen fix, and the PL_Summary source-of-truth fix, as in Section 3 |
| **Executed** | Real-app flows via Streamlit `AppTest` (113 checks), six repository scripts on base and modified trees, diff apply and blob comparison, direct `rollups.py` execution against the canonical dataset and constructed PL_Summary-absent/malformed fixtures |
| **Demonstrated** | Every reported symptom reproduced before the change and gone after (Section 6); behaviour equality between live and reopen commentary review; the PL_Summary defect and its fix, confirmed against real Principal-supplied test data (Section 3.5, Section 6) |
| **Could not be tested** | Live semantic reconciliation (no API key); real browser file uploads; the pinned numpy 2.5.1 |
| **Remains unverified** | Independent validation; behaviour on the Principal's own real Close History beyond the files supplied; canonical synchronization; cross-sheet consistency of an uploaded dataset (Section 10, item 5) |

Builder completion is not final acceptance.

---

## 13. Reproduction

`builder_test_scripts.zip` contains `flow_helpers.py` and the suites (`t1`, `t4`, `t5`, `t6`, `t7`, `t8`, `t9`, `t11`, `t13`, `t16`), the fixture generators, and the probe scripts for the parked Bug/Change 5 reproduction and the date and value investigations. Each suite is run as `python <suite>.py` with the pinned venv; `flow_helpers.py` builds a fresh scratch copy of the repository for every scenario and expects the repository at the path set in its `fresh_ws()` default. Each prints `PASS` or `FAIL <name>` lines and, for most suites, a `SUMMARY` line.

For the PL_Summary fix specifically, `rollups.py` can be run directly against any dataset:

```bash
NORTHWIND_RAW_DATASET_PATH="/path/to/dataset.xlsx" python3 rollups.py
```
