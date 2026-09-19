# D15 Item 2 Corrections — Builder Brief

**Governs:** corrections to `governance/builder_briefs/period_lifecycle_reopen_correction_brief.md` (v2) Item 2 scope, as delivered at canonical commit `eca6b1c2e3f2792ae7f6c2ae135abf607184db09`.
**Authority:** `d15-item2-critical-findings-principal-approved.md` (Principal-approved 2026-09-17), OI-8/OI-9/OI-10/OI-12 — Category A (already-authorized, implementation defect). Plus one Category B item, Principal-authorized this session (line-item audit diff).
**Excluded from this Brief:** OI-11 (narrative component breakdown) — in a separate patch, already in Builder's hands. D15 Items 1/3/4/5 (candidate Commentary intake, live 5.G/5.H/5.I dashboard wiring) — untouched, out of scope.
**Status:** DRAFT — awaiting Scope Authorization Gate sign-off before release to Builder.

---

## Item A — Period-scoped correction intake (OI-8)

### Root cause (independently verified, not narration)

`Northwind_Financial_Dashboard.py`'s reopen/correction-intake handler (~line 1304) accepts the uploaded workbook whole and archives it, unfiltered, as the reopened period's `raw_dataset_path`. No code anywhere in the intake path restricts the upload to the reopened period's own months. `period_lifecycle.run_propagation_chain()` exists but is never called from the live dashboard (confirmed by repository-wide search — it appears only in a code comment) — OI-8 is **not** a propagation-logic defect.

**Reproduced exactly as Principal describes:** reopening Q3 FY2026 and uploading a file whose only genuine change vs. Q3's own approved state is a Jun-2026 (Q4 FY2026) row causes that change to be archived under Q3 and to surface in Q4's own figures. Confirmed by direct diff of the Principal-supplied files against the canonical dataset.

### Required behavior

When a period is reopened and a corrected dataset is uploaded:

1. The system must determine, from the uploaded workbook, which rows fall within the reopened period's own fiscal months and which do not.
2. Rows within the reopened period: accepted as the correction, proceed through the existing 5.D/5.E flow unchanged.
3. Rows outside the reopened period: compared against the currently-approved value for that row (from that other period's own last-approved snapshot). If identical, silently ignored (this is normal — a full-history upload will always carry unrelated, unchanged rows). If **different** from the currently-approved value for that other period, the intake must be **rejected outright** — not archived, not silently accepted — with an explicit error identifying the out-of-period row(s) and which period they actually belong to. This matches D15's existing immutability principle (Decision Log D15): a period's canonical state changes only through its own explicit reopen.
4. Only the reopened period's own filtered rows are ever written into that period's `raw_dataset_path` on archive — not the full uploaded workbook.

### Acceptance criteria

- A1. Reopening Q3 and uploading a file with only in-Q3 changes: unaffected, behaves exactly as today.
- A2. Reopening Q3 and uploading a file with an out-of-period (Q4-month) value that differs from Q4's currently-approved value: intake rejected, clear error naming the offending row(s) and period, no candidate created, no archive call made.
- A3. Reopening Q3 and uploading a file with out-of-period rows that are identical to the currently-approved value: intake proceeds normally (this is the common case — a full dataset re-upload).
- A4. Reproduce the Principal's exact scenario (reopen Q3, upload the Q4-labeled file with the +$1M Jun-2026 row) end to end and confirm rejection.
- A5. Regression: existing Q2/Q3/Q4 correctly-scoped reopen flows (the three files already supplied) still produce the expected single-period-only new versions.

---

## Item B — Stale dataset cache affecting Phase 2 and dashboard refresh (OI-9 + OI-12, same root cause)

### Root cause (independently verified — includes a live reproduction the Principal ran)

Neither the original Close Validation Status tab's Phase 2 check nor the persistent dashboard tabs reload the module-level `R` (`rollups.py`) after a correction is archived. `R.expenses` and related module state are loaded once at Streamlit startup and never refreshed by `st.rerun()`. No `importlib.reload` exists anywhere in `Northwind_Financial_Dashboard.py` (confirmed by repository-wide search).

**Live-confirmed by Principal, this session:** viewing Close Validation Status immediately after approving a correction, without restarting Streamlit, shows Phase 2 reporting "No differences found against the latest approved close" — the exact literal string at line 725 — even though a genuine change was just approved. Restarting Streamlit and reloading the same tab correctly flags it.

This is the same defect Gap 4/OI-12 already identified for the live single-period approve button; it was never extended to cover D15 Item 2's candidate archival path, and the Close Validation Status tab's own Phase 2 section was never covered by Gap 4's fix at all.

### Required behavior

After any `archive_close()` call succeeds — whether from the live single-period Approve button or from D15 Item 2's candidate-approval path — force `rollups.py` to re-resolve before the next render:

```python
import importlib
importlib.reload(R)
```

placed before `st.rerun()` at every call site that can change Close History (both approval paths).

### Acceptance criteria

- B1. Approve a live single-period close; Close Validation Status Phase 2/dashboard figures reflect it without a manual restart (this closes Gap 4's original recommendation, never actually applied).
- B2. Approve a D15 Item 2 candidate correction (reopen path); Close Validation Status Phase 2 correctly flags the change without a manual restart. Reproduce the Principal's own before/after-restart test as the acceptance evidence.
- B3. Regression: confirm reload doesn't break any dashboard state holding a stale direct reference to a pre-reload DataFrame — flagged as an open safety concern in the original OI-12 write-up; must be explicitly checked, not assumed safe.
- B4. No change to `run_phase2_deterministic_validation()`'s or `run_phase3_plausibility_review()`'s own logic — this item is a caching/refresh fix only.

---

## Item C — Phase 3 revenue coverage (OI-10)

### Root cause (independently verified)

`run_phase3_plausibility_review(expenses, headcount, ...)` — confirmed by direct signature read — has no `revenue` parameter and no revenue code path at all, at any dimension. This is a complete absence, not a threshold gap.

### Required behavior

Extend Phase 3 to also flag QoQ variance on Revenue, at minimum at Total and at the two dimensions D15 already established as canonical (`Rev_by_Region_Q`, `Rev_by_Product_Q` — reusing existing canonical outputs, not inventing new grain). Threshold: **Architect recommendation, not yet Principal-set** — proposing the same `DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD` (25%) already governing Expenses, flagged explicitly here for your confirmation or override before Builder implements, since this is a genuine business-policy choice (Gap 3's Analytical Definition Registry governs exactly this kind of value).

### Acceptance criteria

- C1. A revenue variance exceeding the threshold (e.g., the ~127% case from OI-10's original UAT) is flagged, with the flag text stating the metric, variance, and threshold — same shape as existing Expense flags.
- C2. A normal revenue swing (single-digit-to-low-teens % QoQ) is not flagged.
- C3. Regression: existing Expense/Headcount Phase 3 checks unaffected — this is additive.

---

## Item D — Surface the candidate's line-item diff (new, Category B, Principal-authorized this session)

Not an OI finding — added at Principal's request during Brief preparation, for audit-trail speed.

### Current state

`revalidate_period_from_raw()` already computes a full line-item Phase 2 diff for every correction intake (`_cand_phase2`), stored in `st.session_state["reopen_candidate"]["phase2_result"]`. It is never rendered — only reduced to a flag count at archive time.

### Required behavior

In the correction-intake display (alongside the existing 5.E per-output impact bullets), render `_cand_phase2.flagged_rows` as a table — reusing the exact rendering already built for the original Close Validation Status tab's Phase 2 section (same columns: Date, Department, Category, Prior Close, Current Close, Diff). No new computation.

### Acceptance criteria

- D1. Running correction intake on a file with genuine changes shows both the existing per-output impact summary (5.E) and the new full line-item table (raw Phase 2), side by side or in sequence.
- D2. The line-item table correctly reflects Item A's fix once both land together — i.e., it should never show a row this Brief's Item A would have rejected, since a rejected intake never reaches this display.

---

# SCOPE AUTHORIZATION GATE SUMMARY

| Item | Classification | Confirmed how |
|---|---|---|
| A — period-scoped intake (OI-8) | Category A, already-authorized defect | Direct code read + reproduced against Principal's actual files |
| B — stale cache (OI-9 + OI-12) | Category A, already-authorized defect | Direct code read + Principal's own live restart/no-restart test |
| C — Phase 3 revenue coverage (OI-10) | Category A, already-authorized defect | Direct function-signature read |
| D — line-item diff surfacing | Category B, new scope | Explicit Principal request and approval, this session |

**Explicit exclusions:** OI-11 (separate patch in progress). D15 Items 1/3/4/5. Any wiring of `run_propagation_chain()` into the live UI — confirmed out of scope for this Brief; OI-8's fix is intake-rejection, not propagation.

**Open decision requiring your confirmation before Builder starts:** Item C's variance threshold — reuse the existing 25% Expense threshold, or set something revenue-specific?

**Minimum-scope check:** each item's fix is confined to the function/call-site actually responsible — no schema change, no new state model, no redesign of D15's versioning. Item A adds a filter/reject step to one handler; Item B adds a reload call at two existing call sites; Item C adds one parameter and one code path to one existing function; Item D adds a rendering block reusing existing display code.

---

**Architect Attestation:** canonical repository state checked (HEAD `ca8f8ef...`, clean, consistent with governance docs); all four items independently confirmed by direct code inspection and/or live reproduction, not accepted on the Advisor's narration alone; Category A/B correctly separated; no unauthorized bundling — each item is independently implementable and independently testable.

**Principal Approval Gate:** not yet completed. Awaiting your sign-off (and the Item C threshold decision) before this releases to Builder.
