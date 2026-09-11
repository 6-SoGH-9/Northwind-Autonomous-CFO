# Test Instructions — Product Operability & Auditability (Gaps 1, 2, 3)

**Status:** ACTIVE — governing Test Instructions for `builder_brief_operability_gaps_1_2_3.md`.
**Supersedes:** `INDEPENDENT_TEST_VERIFICATION_GAPS_1_2_3B.md` (retained for provenance — see the reconciliation report, Section 5). That document's test scenarios (1A–1C, 2A–2D, 3B-1 through 3C-3) were reviewed against the authoritative Brief above and found to already assume the full Gap 2/Gap 3 scope the principal has now authorized — they are preserved below essentially unchanged, with corrections noted in Section 0.
**Issued by:** Architect, reconciled against the authoritative Builder Brief. Per the Validation Independence Principle, actual test data/expected values for execution must still be constructed independently of Builder's own fixtures at execution time — this document defines required scenarios and acceptance criteria, not Builder-authored expected answers.
**Trigger:** After Builder completes and regression-verifies Gap 1, 2, and 3 against `builder_brief_operability_gaps_1_2_3.md`.

---

## Section 0 — Corrections made during reconciliation

1. Framing corrected from "From: Principal (Verification Requirements)" to Architect-issued, referencing the authoritative Brief rather than the superseded `BUILDER_AUTHORIZATION_GAPS_1_2_3B.md`.
2. Gap 1 acceptance criteria reworded to match the Brief's precise fix (period sourced from `obs_row['Period']`, not "observation period" as a loose phrase) — no scenario content changed.
3. Gap 3B-1's "effective date (2026-01-01 or current date)" is corrected: the effective date must be the git-history-derived date established in the Brief (`2026-08-05`, first canonical commit of the constants), not an arbitrary placeholder.
4. Added Section 5 (D13 sequencing cross-reference), not present in the superseded document.
5. All other scenarios (1A–1C, 2A–2D, 3B-2 through 3C-3), the regression table, test data requirements, execution timeline, pass/fail criteria, escalation path, and sign-off requirements are preserved unchanged from the superseded document — they were already scoped to the full Gap 2/Gap 3 interpretation now authorized.

---

## 1. Gap 1 — Phase 6 Evidence-Package Verification

**Correctness requirement:** Phase 6 validation must use the observation's own `Period` (from the observation register), never the sidebar's `current_period`.

### Test Scenario 1A — Default Behavior
Setup: Close Q4 FY2026 (latest). Sidebar at default (Q4). Commentary submitted, Phase 6 runs.
Verify: Phase 6 retrieves Q4 headcount/category data; validation result correct for Q4; no data mismatch.

### Test Scenario 1B — Period Navigation Defect Exposure
Setup: Close Q4 FY2026. Sidebar navigated to Q3. Commentary Review shows Q4 observations, already validated.
Verify: Validation result is unchanged and correct for Q4 regardless of sidebar position. Navigating sidebar to Q3 then back to Q4 does not alter the result.

### Test Scenario 1C — Historical Validation Accuracy
Setup: Q3 FY2026 observations, Q3 commentary submitted and validated (sidebar at Q3, matching the observation's own period).
Verify: Phase 6 uses Q3 data; result is correct and reproducible.

**Acceptance criteria:** all three scenarios pass; sidebar position never affects Phase 6's result for a given observation; no regression to Phase 4-6 logic (49/49, 23/23, 23/23 existing fixtures reproduced).

---

## 2. Gap 2 — Historical Phase 4–6 Navigation Verification

**Requirement:** users can navigate to and view the full, persisted Phase 4-6 chain (observation → commentary → match method → Phase 6 result → evidence → version history → accepted marker) for any prior close in Close History, read-only.

### Test Scenario 2A — Navigate to Prior Period
Verify: the new prior-close control lists every period present in `list_approved_closes()`; selecting one switches the Close Validation Status tab into that snapshot's context without altering the general sidebar's own period (they are distinct controls).

### Test Scenario 2B — Previous-Period Phase 4-6 Results
Verify: for a selected prior period, the full chain (Matched via, Phase 6 result, evidence, sub-checks, version history, accepted marker) renders from the archived snapshot's persisted data — not from the current live observation register.

### Test Scenario 2C — Data Completeness Across Multiple Periods
Verify: results are complete and correct across at least three distinct archived periods; no data missing, no cross-period bleed-through.

### Test Scenario 2D — Current Period Behavior Unchanged
Verify: with the new control at its default (live/current close), behavior is byte-for-byte identical to pre-Gap-2 behavior.

### Test Scenario 2E — Read-only enforcement (new, required by the Brief's Section 2.2.3)
Setup: a prior archived period is selected.
Verify: no revision-submission, approve, or reject control is reachable or active while viewing the archived snapshot.

**Acceptance criteria:** all five scenarios pass; no write path reachable on an archived close; live-period behavior unaffected.

---

## 3. Gap 3 — Analytical Definition Registry Verification

### 3B-1 — Definition Registry and Versioning
Verify: all three definitions (`PLAUSIBILITY_QOQ_THRESHOLD` 0.25, `PLAUSIBILITY_HEADCOUNT_BAND` 2, `PLAUSIBILITY_EXCLUDED_CATEGORIES` S&B) are registered as `v1.0`, with `effective_date = 2026-08-05` (git-history-derived, per Section 0.3), each with ID, description, and immutability confirmed by direct attempt (a mutation attempt must fail or be structurally impossible).

### 3B-2 — Observation Attribution
Verify: a Phase 3-generated observation (e.g. a QoQ revenue variance flag) records `definition_id`/`version`, human-readable rule text, and threshold value.

### 3B-3 — Display in Observation Register
Verify: the observation register renders the attribution in business-readable form (e.g. "QoQ movement >25% (PLAUSIBILITY_QOQ_THRESHOLD v1.0)").

### 3B-4 — Previous-Period Attribution
Verify: historical observations (viewed via Gap 2's prior-close navigation) retain their original attribution unchanged.

### 3C-1 — Definition Capture at Approval
Verify: on close approval, `metadata.json` captures `analytical_definitions_active` (all three, with versions) and `definition_snapshot_date`.

### 3C-2 — Close Record Retrievability
Verify: for an approved, archived close, the captured definition versions are retrievable and answer "which definitions were active for this close."

### 3C-3 — Observation-to-Definition Traceability
Verify: a specific observation's attributed definition/version matches its close record's captured version for the same close.

**Acceptance criteria:** all seven scenarios pass; auditability chain (observation → definition version → close record) is complete and consistent; no definition value is editable anywhere; D11's Phase 2/3 flagging output is bit-for-bit unchanged (attribution is additive metadata only).

---

## 4. Regression Testing

| Area | Requirement |
|---|---|
| Phase 2 (historical diff) | Unchanged — no diff |
| Phase 3 (plausibility) | Flagging output unchanged; only attribution metadata added |
| Phase 4 (reconciliation) | Unaffected by this Brief (separate Brief governs Phase 4) |
| Phase 6 (validation) | Only period-sourcing changed (Gap 1); validation logic itself unchanged |
| Human Approval Gate | Unaffected |
| Close History | `archive_close()` additive only; existing archived closes not rewritten; immutability (`FileExistsError` on duplicate period) still enforced |
| Dashboard UI | No tab breakage; 8/8 (or current count) tabs render, 0 exceptions |

---

## 5. D13 sequencing cross-reference (new in this reconciliation)

The Section H/J independent UAT for D13 (Handbook Section 13) must be run against the **post-Gap-1** implementation and must record the sidebar's period state for each test case, per the Brief's Section 1.4. This Test Instructions document does not itself supply Section H/J content (that remains principal-supplied, per standing Validation Independence Principle) — it only records the sequencing dependency so Section H/J execution isn't scheduled ahead of Gap 1's fix landing.

---

## 6. Test Data, Timeline, Pass/Fail, Escalation, Sign-off

Unchanged from the superseded document (`INDEPENDENT_TEST_VERIFICATION_GAPS_1_2_3B.md`): canonical Q1 FY2025–Q4 FY2026 dataset baseline (D11/D14), the seven-phase execution timeline (planning → Gap 1 → Gap 2 → Gap 3 → regression → integration → sign-off), the PASS/FAIL/CONDITIONAL-PASS criteria, the three-tier escalation path (minor/major/governance defect), and the required sign-off artifacts (Verification Report, Pass/Fail Assessment, Known Limitations, Recommendation). Reproduced in full in the superseded document; not restated here to avoid two divergent copies of the same procedural text — see that document (Section 5 of the reconciliation report) for the exact wording, which remains authoritative for these procedural sections only.
