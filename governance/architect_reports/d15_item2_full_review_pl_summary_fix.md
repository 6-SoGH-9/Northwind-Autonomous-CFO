# Architect Review: D15 Item 2 Corrections — Full Implementation, including PL_Summary Source-of-Truth Fix

**Author:** Architect
**Date:** 2026-09-27
**Reviewing:** `d15_item2_return_report_full.md` (Builder, 2026-09-27), against `Northwind_Financial_Dashboard.py`, `close_validation.py`, `period_lifecycle.py`, `rollups.py` as supplied in this session.
**Principal statement relied on:** all four `.py` files are committed to `main`.

---

## 1. Verification method and its limits

I read all four `.py` files in full, not the Return Report's narration of them. Where the Return Report makes a factual claim about the code (a check removed, a sheet no longer required, a function's new source), I checked it against the actual file content rather than accepting the claim.

What I could **not** verify myself in this session, and am relying on the Principal's statement for:
- That these are in fact the current contents of canonical `main`. I have not queried GitHub directly in this session to confirm HEAD.
- Blob hashes, diff-apply results, and the 113/49/etc. test-suite pass counts in Section 5 of the Return Report — this describes execution I did not witness. Treated as Builder's report of its own testing, not independent evidence, per this project's Validation Independence Principle.
- The real-world confirmation episode in Section 6 (Principal's own test with the wrong diff applied) — internally consistent arithmetically ($4,016,905.92 + $137,780,280.00 = $141,797,185.92), but not independently reproduced by me.

## 2. PL_Summary fix — verified directly against the code

Confirmed by direct reading of `rollups.py` and `period_lifecycle.py`:

- `build_pl_rollup()` computes `Total Revenue ($)` and `Total Opex ($)` from `revenue.groupby(period_col)["Revenue ($)"].sum()` and `expenses.groupby(period_col)["Amount ($)"].sum()` — not from `pl_summary`. `Operating Profit ($)`/`Operating Margin (%)` arithmetic is unchanged.
- The three former tie-out checks against `PL_Summary` are gone from the verification block; replaced with comments explaining why, not converted to a rejection — matches the instruction ("drop, don't reject") exactly.
- `pl_summary` is still loaded, now inside `try/except ValueError`, degrading to an empty frame on a missing sheet. Confirmed no other reference to `pl_summary` remains anywhere in `rollups.py` outside the load block.
- `period_lifecycle.py`: `PL_Summary` removed from `DATASET_REQUIRED_SHEETS`, `DATASET_REQUIRED_COLUMNS`, and `DATASET_NUMERIC_COLUMNS`. The old `PL_Summary`-specific "Total / Avg" footer-row exception in the upload-validation loop is gone along with it — no dead reference left behind.
- `CORRECTION_SCOPE_SHEETS` is unchanged: `PL_Summary` still passes through `enforce_period_scoped_correction()` unfiltered, but this is now inert since nothing reads the sheet downstream.

**This resolves my prior open finding (the cross-period `PL_Summary` leakage into the archived P&L), not merely narrows it.** Nothing reads `PL_Summary` any more, so a tampered value in it has no effect on anything computed, displayed, or archived. Closed.

## 3. Regression check

Read every remaining tie-out in `rollups.py`'s verification block and every other file for anything that could have silently broken:

- Every remaining tie-out (Region/Product-cut agreement, Region/Product Net-of-cost sums, S&B volume/rate bridge, Breadth/Concentration vs. `pl_q`'s own QoQ variance, Department×Category vs. Department-level, Category-only vs. Department×Category) reads from `pl_q`/`pl_y`, `expenses`, `revenue`, or each other — none read `pl_summary`. None needed to change and none did.
- `Northwind_Financial_Dashboard.py` never referenced `pl_summary` directly (only via `R.pl_q`/`R.pl_y`, already sourced correctly), so it required no change and I found none beyond what the fix touches.

No regression found from this fix.

## 4. Status of earlier-open items (Bug 3/4/6, from prior review) — unchanged, not silently resolved

1. **Cancel silently building a candidate anyway** (contradicts Addendum 1 A-R2) — still present.
2. **Carried-over commentary not revalidated on dataset replacement** — still present.
3. **Bug 4's live-model-call consequence** — still unresolved/unexercised live.
4. **Bug 5 / new-period intake** — still parked, as intended.

None of these were claimed fixed by this Return Report; I found nothing suggesting otherwise.

## 5. New items raised by this Return Report's Section 10 — carried forward, not decided here

- **Cross-sheet consistency of an uploaded dataset is no longer checked at all**, now that `PL_Summary` is correctly non-authoritative (e.g. an uploaded `Revenue` sheet's total is never checked against an uploaded `Budget_vs_Actual` sheet's stated Revenue actuals). Distinct risk from the closed PL_Summary finding. Recommend leaving open as a separate future decision, not folded into this fix.
- **Bug 5 (parked)** — unchanged, still needs a decision, tied to "how does a new period's data get in."
- **`PL_Summary` load now dead code behind try/except, not removed** — recommend "no further action"; removing it is cosmetic with no functional benefit and risks re-touching a closed fix. Recommendation only, not a decision.
- **`PL_Summary` has no required columns at upload any more** — confirmed correct and intended, matches the "drop it completely" instruction exactly.

## 6. Required final question

**Can the intended user perform the complete intended operation — trusting the resulting P&L figures after closing or correcting a period — in the canonical application without developer intervention, for the PL_Summary defect specifically?**

**Yes, for the specific defect this fix targets.** Direct code read confirms the P&L headline figures are now computed from Revenue/Expenses on both the live-close and reopen-candidate paths (both consume `pl_q`). Regression check found no other tie-out affected. The Principal's own real-dataset test, taken at face value, is stronger evidence than a synthetic fixture.

**Not established:** the complete end-to-end chain remains open on other axes — the pre-existing gaps in Section 4 above were never in scope for this fix and are unresolved.

## 7. Sign-off

| Check | Status |
|---|---|
| PL_Summary fix matches the instruction given | Confirmed by direct code read |
| No regression in `rollups.py`'s other tie-outs | Confirmed by direct code read |
| No regression in `period_lifecycle.py`'s upload review or correction scoping | Confirmed by direct code read |
| Prior open findings (Cancel, stale commentary, Bug 4 live-model consequence, Bug 5) | Unchanged, correctly not claimed resolved |
| Independent execution of Builder's test suites, blob hashes, diff application, canonical `main` HEAD | Not independently verified this session — resting on Builder's report and Principal's confirmation of commit status |

No Builder Brief is required for this fix; it is complete as delivered. Outstanding decisions: cross-sheet consistency (new), Bug 5 (parked), PL_Summary dead-load cleanup (recommendation only).
