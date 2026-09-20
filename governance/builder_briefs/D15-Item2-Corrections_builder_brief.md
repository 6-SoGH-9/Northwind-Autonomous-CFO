# D15 Item 2 Corrections — Builder Brief (RELEASED)

**Governs:** corrections to `governance/builder_briefs/period_lifecycle_reopen_correction_brief.md` (v2) Item 2 scope, as delivered at canonical commit `eca6b1c2e3f2792ae7f6c2ae135abf607184db09`.
**Authority:** `d15-item2-critical-findings-principal-approved.md` (Principal-approved 2026-09-17), OI-8/OI-9/OI-10/OI-12 — Category A (already-authorized, implementation defect). Plus one Category B item, Principal-authorized (line-item audit diff).
**Excluded from this Brief:** OI-11 (narrative component breakdown) — governed separately by `D17-BB-001`. D15 Items 1/3/4/5 (candidate Commentary intake, live 5.G/5.H/5.I dashboard wiring) — untouched, out of scope.
**Status:** **RELEASED — ACTIVE.** Scope Authorization Gate closed this session. This is the sole governing document for this scope; the earlier `d15_item2_design_note.md` governed a separate, already-completed piece of work (the original v1→v2 archival mechanics) and does not apply to Items A–D below.

---

## Canonical state at release (fresh clone, this session)

```
Repository: 6-SoGH-9/Northwind-Autonomous-CFO
Branch: main
HEAD: 6c00f29450aee6ffb8fbceccdb87be81c1818f94
```

Independently confirmed by direct inspection of the actual files at this HEAD — not narration, not the prior Advisor-sourced compliance note:

- **Item A:** not present. The "Run correction intake" handler in `Northwind_Financial_Dashboard.py` passes the uploaded workbook to `compute_candidate_rollups_output()` / `revalidate_period_from_raw()` with no period-boundary filtering or rejection logic anywhere in the path.
- **Item B:** not present. Zero occurrences of `importlib` in `Northwind_Financial_Dashboard.py`, `rollups.py`, `close_validation.py`, `close_history.py`.
- **Item C:** not present. `run_phase3_plausibility_review()`'s signature carries no `revenue` parameter; zero revenue references anywhere in `close_validation.py`.
- **Item D:** not present. The candidate's `_cand_phase2.flagged_rows` is computed and stored but only reduced to a count at archive time; never rendered in the correction-intake display.

All four items are therefore confirmed live requirements against the current codebase, not stale findings against superseded code.

**Note, not part of this Brief's scope:** current HEAD is 7 commits past `eca6b1c...` (`29691e7`, `ca8f8ef`, `6bfedc0`, `6b63397`, `5b4502b`, `e92d1d0`, `6c00f29`), all but the last via "Add files via upload" with no descriptive commit messages, and HEAD's own message ("Update print statement from 'Hello' to 'Goodbye'") is not meaningful. This does not block release of this Brief, but it means the Handbook's evidence chain should be re-walked against this HEAD before D17 or any other item is next described as canonical-synced — flagged for a future session, not actioned here.

---

## Item A — Period-scoped correction intake (OI-8)

### Root cause (independently verified, not narration)

`Northwind_Financial_Dashboard.py`'s reopen/correction-intake handler accepts the uploaded workbook whole and archives it, unfiltered, as the reopened period's `raw_dataset_path`. No code anywhere in the intake path restricts the upload to the reopened period's own months. `period_lifecycle.run_propagation_chain()` exists but is never called from the live dashboard — OI-8 is **not** a propagation-logic defect.

### Scenario — confirmed intended (Principal, this session)

Reopening one period and uploading a corrected file that also carries a genuine, differing change to another period's months is the intended test case. **Required outcome: that upload must be rejected outright, not captured into history.** Current behavior violates this — confirmed KO.

### Required behavior

1. From the uploaded workbook, determine which rows fall within the reopened period's own fiscal months and which do not.
2. Rows within the reopened period: accepted as the correction, proceed through the existing 5.D/5.E flow unchanged.
3. Rows outside the reopened period: compared against the currently-approved value for that row (from that other period's own last-approved snapshot). If identical, silently ignored (normal — a full-history re-upload always carries unrelated, unchanged rows). If **different**, the intake must be **rejected outright** — no candidate created, no archive call made — with an explicit error identifying the offending row(s) and the period they actually belong to.
4. Only the reopened period's own filtered rows are ever written into that period's `raw_dataset_path` on archive — never the full uploaded workbook.

### Acceptance criteria

- A1. Reopening a period and uploading a file with only in-period changes: unaffected, behaves exactly as today.
- A2. Reopening a period and uploading a file with an out-of-period value that differs from that other period's currently-approved value: intake rejected, clear error naming the offending row(s) and period, no candidate created, no archive call made.
- A3. Reopening a period and uploading a file with out-of-period rows identical to the currently-approved value: intake proceeds normally.
- A4. Reproduce the Principal's exact scenario end to end and confirm rejection.
- A5. Regression: existing correctly-scoped reopen flows still produce the expected single-period-only new versions.

---

## Item B — Stale dataset cache affecting Phase 2 and dashboard refresh (OI-9 + OI-12, same root cause)

### Root cause (independently verified)

Neither the Close Validation Status tab's Phase 2 check nor the persistent dashboard tabs reload the module-level `R` (`rollups.py`) after a correction is archived. Module-level state loads once at Streamlit startup and is never refreshed by `st.rerun()`. No `importlib.reload` exists anywhere in the codebase. This is the same defect Gap 4/OI-12 identified for the live single-period approve button; it was never extended to D15 Item 2's candidate path, and the Close Validation Status tab's own Phase 2 section was never covered by Gap 4's fix at all.

### Required behavior

After any `archive_close()` call succeeds — live single-period Approve, or D15 Item 2's candidate-approval path — force `rollups.py` to re-resolve before the next render:

```python
import importlib
importlib.reload(R)
```

placed before `st.rerun()` at every call site that can change Close History.

### Acceptance criteria

- B1. Approve a live single-period close; Close Validation Status Phase 2/dashboard figures reflect it without a manual restart.
- B2. Approve a D15 Item 2 candidate correction; Close Validation Status Phase 2 correctly flags the change without a manual restart.
- B3. Regression: confirm reload doesn't break any dashboard state holding a stale direct reference to a pre-reload DataFrame — explicit check required, not assumed safe.
- B4. No change to `run_phase2_deterministic_validation()`'s or `run_phase3_plausibility_review()`'s own logic — caching/refresh fix only.

---

## Item C — Phase 3 revenue coverage (OI-10)

### Root cause (independently verified)

`run_phase3_plausibility_review(expenses, headcount, ...)` has no `revenue` parameter and no revenue code path at all, at any dimension.

### Threshold — confirmed (Principal, this session)

**25% — reuse the existing `DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD` unchanged, same value already governing Expenses.** No revenue-specific value.

### Required behavior

Extend Phase 3 to flag QoQ variance on Revenue, at minimum at Total and at `Rev_by_Region_Q` / `Rev_by_Product_Q` (D15's existing canonical outputs — no new grain invented), at the 25% threshold.

### Acceptance criteria

- C1. A revenue variance exceeding 25% is flagged, with flag text stating metric, variance, and threshold — same shape as existing Expense flags.
- C2. A normal revenue swing (single-digit-to-low-teens % QoQ) is not flagged.
- C3. Regression: existing Expense/Headcount Phase 3 checks unaffected — additive only.

---

## Item D — Surface the candidate's line-item diff (Category B, Principal-authorized)

### Current state

`revalidate_period_from_raw()` already computes a full line-item Phase 2 diff for every correction intake (`_cand_phase2`), stored in `st.session_state["reopen_candidate"]["phase2_result"]`. Never rendered — only reduced to a flag count at archive time.

### Required behavior

In the correction-intake display, render `_cand_phase2.flagged_rows` as a table — reusing the exact rendering already built for the Close Validation Status tab's own Phase 2 section (same columns: Date, Department, Category, Prior Close, Current Close, Diff). No new computation.

### Acceptance criteria

- D1. Running correction intake on a file with genuine changes shows both the existing per-output impact summary (5.E) and the new full line-item table (raw Phase 2).
- D2. The line-item table correctly reflects Item A's fix once both land together — never shows a row Item A would have rejected.

---

# SCOPE AUTHORIZATION GATE

| Item | Classification | Confirmed how |
|---|---|---|
| A — period-scoped intake (OI-8) | Category A, already-authorized defect | Direct code read + Principal confirmation of intended scenario, this session |
| B — stale cache (OI-9 + OI-12) | Category A, already-authorized defect | Direct code read, fresh clone this session |
| C — Phase 3 revenue coverage (OI-10) | Category A, already-authorized defect | Direct function-signature read, fresh clone this session |
| D — line-item diff surfacing | Category B, new scope | Explicit Principal authorization |

**Explicit exclusions:** OI-11 (governed by `D17-BB-001`). D15 Items 1/3/4/5. Any wiring of `run_propagation_chain()` into the live UI — out of scope; OI-8's fix is intake-rejection, not propagation.

**Minimum-scope check:** each item's fix is confined to the function/call-site actually responsible — no schema change, no new state model, no redesign of D15's versioning. A = filter/reject step in one handler. B = one reload call at two existing call sites. C = one parameter, one code path, one existing function. D = one rendering block reusing existing display code.

**Decisions closed this session:**
- ☑ Item C threshold: 25%, confirmed by Principal.
- ☑ OI-8 scenario: confirmed intended by Principal; acceptance criteria A1–A5 unchanged.

**Minimum-Scope Verification:**
☑ Minimum implementation identified
☑ Claimed dependencies tested (none found — items are independently implementable)
☑ Workarounds considered
☑ Optional architecture separated (none proposed)
☑ No unnecessary bundling introduced

**Architect Attestation:**
☑ Reviewed relevant Handbook and Decision Log
☑ Reviewed canonical repository state — fresh clone, this session, HEAD `6c00f29450aee6ffb8fbceccdb87be81c1818f94`
☑ Classified all material scope
☑ Applied the Required Response Format
☑ Applied the Minimum-Scope Test
☑ Did not bundle scope without authorization
☑ Did not use technical preference as product authority
☑ Did not silently narrow or expand Principal scope
☑ This Brief accurately represents the authorized scope

**PRINCIPAL APPROVAL GATE:**
☑ This Brief includes all requirements the Principal has decided (Items A–D)
☑ This Brief includes no product scope the Principal did not authorize
☑ Exclusions accurately represent deferred/out-of-scope decisions (OI-11, D15 Items 1/3/4/5, propagation UI wiring)
☑ Item C threshold and OI-8 scenario explicitly confirmed by Principal
☑ Architect recommendations clearly separated from mandatory scope (none proposed beyond the four items)
☑ Builder implements ONLY the authorized scope in this Brief

**RELEASE RULE SATISFIED.** This Brief is released to Builder as of this session.
