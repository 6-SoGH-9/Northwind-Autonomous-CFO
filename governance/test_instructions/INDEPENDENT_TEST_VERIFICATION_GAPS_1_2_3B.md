> **SUPERSEDED.** This document is retained for provenance/procedural detail only (Sections not restated in the successor — see below). The authoritative, Architect-issued Test Instructions for this scope are `test_instructions_operability_gaps_1_2_3.md`, in this same directory. Where the two disagree, the successor document governs.

# Independent Test Verification Package
## Gaps 1, 2, 3B — Operability and Auditability Verification

**To:** Independent Test / UAT  
**From:** Principal (Verification Requirements)  
**Subject:** Verification scope for operability and auditability improvements  
**Status:** Verification requirements — Ready for test planning  
**Trigger:** After Builder completes Gaps 1, 2, 3B implementation  

---

## Verification Context

**What has been authorized:**
- Gap 1: Phase 6 evidence-package defect fix (period data wiring)
- Gap 2: Previous-period visibility for Phase 4-6 results
- Gap 3B: Analytical definition versioning and observation attribution
- Gap 3C: Close record capture of definition versions

**What needs independent verification:**
- Each gap works as intended
- No regressions in existing functionality
- Auditability and governance requirements are met
- Product is ready for E2E demonstration

---

## Gap 1: Phase 6 Evidence-Package Verification

### What to Verify

**Correctness requirement:** Phase 6 validation must use the **observation register's period**, not the **sidebar period**.

### Test Scenario 1A: Default Behavior (Correct Path)

**Setup:**
- Close Q4 FY2026 (latest period)
- Sidebar shows Q4 (default)
- Commentary is submitted
- Phase 6 validation runs

**Expected:**
- Phase 6 retrieves Q4 headcount data
- Validation results are correct for Q4
- "Matched via" and validation results show in Commentary Review

**Verify:**
- ✅ Headcount-claim validation uses Q4 data (observation period)
- ✅ Validation result is correct for Q4 context
- ✅ No data mismatch between observation period and validation data

---

### Test Scenario 1B: Period Navigation Defect Exposure

**Setup:**
- Close Q4 FY2026
- **Sidebar navigate to Q3**
- Commentary Review tab shows Q4 observations
- Validation has already been completed

**Expected (after fix):**
- Phase 6 validation used Q4 data (not Q3)
- Result is correct for Q4 observations

**Verify:**
- ✅ Validation results remain correct even though sidebar shows Q3
- ✅ Phase 6 pull headcount from Q4, not Q3
- ✅ Sidebar navigation does NOT change validation results retroactively

**Test approach:**
- Run validation with sidebar at Q4 → capture validation result
- Navigate sidebar to Q3 → verify validation result unchanged
- Navigate back to Q4 → verify result consistent

---

### Test Scenario 1C: Historical Validation Accuracy

**Setup:**
- Use Q3 FY2026 observations
- Submit Q3 commentary
- Validate Q3 claims

**Expected:**
- Phase 6 uses Q3 headcount data
- Q3 validation results are correct

**Verify:**
- ✅ Historical period validation uses correct period's data
- ✅ Headcount claims validated against correct period
- ✅ Results are reproducible (same every time)

---

### Acceptance Criteria for Gap 1

- ✅ Phase 6 always uses observation register's period for data retrieval
- ✅ Sidebar period does NOT affect Phase 6 validation
- ✅ All three test scenarios pass
- ✅ No regressions in Phase 4-6 logic
- ✅ Validation results are correct and reproducible

---

## Gap 2: Previous-Period Visibility Verification

### What to Verify

**Navigation requirement:** Users can navigate to and view Phase 4-6 results for previous periods.

**Data requirement:** Phase 4-6 results (observations, matches, validation) must be retrievable from Close History for prior quarters.

### Test Scenario 2A: Navigate to Prior Period

**Setup:**
- Current dashboard shows Q4 FY2026 (latest)
- Close History exists for Q1-Q4 FY2025 and Q1-Q3 FY2026
- Period selector allows navigation

**Expected:**
- User can select Q3 FY2026 from period selector
- Dashboard switches to Q3 context
- Observation register shows Q3 observations

**Verify:**
- ✅ Period selector includes all prior periods
- ✅ Q3 can be selected and dashboard updates
- ✅ Observations displayed are for Q3 (not Q4 bleeding through)

---

### Test Scenario 2B: Previous-Period Phase 4-6 Results

**Setup:**
- Navigate to Q3 FY2026
- Go to Commentary Review section
- Look for Phase 4-6 data (observations, matches, validation)

**Expected:**
- Full Observation→Commentary→Match→Validation detail is visible
- "Matched via" label shows which observation matched
- Validation results (Supported / Contradicted / Insufficient) are displayed

**Verify:**
- ✅ Commentary Review section renders Q3 phase 4-6 results
- ✅ Observations linked to commentary (matched via)
- ✅ Validation results are shown
- ✅ All details are complete and correct for Q3

---

### Test Scenario 2C: Data Completeness for Multiple Periods

**Setup:**
- Navigate through several periods (Q4, Q3, Q2, Q1)
- For each, check Phase 4-6 results

**Expected:**
- Each period's results are complete and correct
- No data missing or corrupted
- Results are retrievable from Close History

**Verify:**
- ✅ Q4 results: Complete
- ✅ Q3 results: Complete
- ✅ Q2 results: Complete
- ✅ Q1 results: Complete
- ✅ No data loss across periods
- ✅ Results are consistent when period is revisited

---

### Test Scenario 2D: Current Period Behavior Unchanged

**Setup:**
- Navigate to Q4 (latest/current)
- Verify all Phase 4-6 results are displayed

**Expected:**
- Q4 (current period) behavior is unchanged from before
- All Phase 4-6 data visible
- No regression

**Verify:**
- ✅ Current period functionality unchanged
- ✅ All Phase 4-6 results visible
- ✅ No performance degradation
- ✅ No UI regressions

---

### Acceptance Criteria for Gap 2

- ✅ Users can navigate to any prior period in Close History
- ✅ Phase 4-6 results (observations, matches, validation) are retrievable for prior periods
- ✅ Results are complete and accurate for each period
- ✅ Current period behavior is unchanged
- ✅ No data loss or corruption
- ✅ All four test scenarios pass

---

## Gap 3B: Analytical Definition Versioning and Observation Attribution

### What to Verify

**Versioning requirement:** Each analytical definition is registered, versioned, and retrievable.

**Attribution requirement:** Each generated observation records which definition triggered it.

**Display requirement:** Observation register shows definition attribution in business-readable form.

### Test Scenario 3B-1: Definition Registry and Versioning

**Setup:**
- System has analytical definition registry (v1.0)
- Three definitions registered:
  - PLAUSIBILITY_QOQ_THRESHOLD: 25% (v1.0)
  - PLAUSIBILITY_HEADCOUNT_BAND: ±2 (v1.0)
  - PLAUSIBILITY_EXCLUDED_CATEGORIES: S&B (v1.0)
- Each definition has metadata (ID, version, effective date, description)

**Expected:**
- Definitions are registered and accessible
- Version information is present
- Effective dates are recorded

**Verify:**
- ✅ Definition registry contains all three definitions
- ✅ Each definition has ID, version, description
- ✅ Effective date is recorded (2026-01-01 or current date)
- ✅ Definitions are immutable (cannot be edited)
- ✅ Version v1.0 is locked in (no changes to 25%, ±2, S&B)

---

### Test Scenario 3B-2: Observation Attribution

**Setup:**
- Phase 3 generates observations for Q4 FY2026
- Observations include: revenue +28% QoQ, other metrics

**Expected:**
- Revenue observation shows:
  - Metric: "QoQ revenue variance +28.0%"
  - Definition triggered: "PLAUSIBILITY_QOQ_THRESHOLD"
  - Rule: "QoQ movement >25%"
  - Version: v1.0
  - Result: Flagged as anomalous

**Verify:**
- ✅ Each observation records definition ID
- ✅ Definition version is captured
- ✅ Rule description is present (human-readable)
- ✅ Threshold value is shown (25%)
- ✅ Observation register displays this attribution

---

### Test Scenario 3B-3: Display in Observation Register

**Setup:**
- Open Close Validation Status tab
- Look at observation register
- Examine a flagged observation (e.g., revenue variance)

**Expected:**
- Observation shows:
  ```
  Metric: QoQ Revenue Variance
  Value: +28.0%
  Analytical definition triggered: QoQ movement >25% (PLAUSIBILITY_QOQ_THRESHOLD v1.0)
  Result: Flagged as anomalous
  ```

**Verify:**
- ✅ Definition name is visible (business-readable)
- ✅ Rule is explained (">25%")
- ✅ Version is shown (v1.0)
- ✅ User can understand why observation was generated
- ✅ Attribution is clear without exposing code

---

### Test Scenario 3B-4: Previous Period Attribution

**Setup:**
- Navigate to Q3 FY2026
- Look at Q3 observations and their attribution

**Expected:**
- Q3 observations show definition attribution
- Definitions are the same version (v1.0) as they were when Q3 was processed
- Attribution is consistent

**Verify:**
- ✅ Historical observations include definition attribution
- ✅ Definitions shown are v1.0 (versions used at the time)
- ✅ Attribution is traceable/auditable

---

## Gap 3C: Close Record Audit Capture Verification

### What to Verify

**Capture requirement:** When a close is approved, the exact analytical definition versions are archived.

**Retrievability requirement:** Can later query which definitions were active for a specific close.

### Test Scenario 3C-1: Definition Capture at Approval

**Setup:**
- Commentary is validated
- Human Approval Gate: User clicks Approve
- Close is archived

**Expected:**
- Close record captures:
  - `analytical_definitions_active.PLAUSIBILITY_QOQ_THRESHOLD: v1.0`
  - `analytical_definitions_active.PLAUSIBILITY_HEADCOUNT_BAND: v1.0`
  - `analytical_definitions_active.PLAUSIBILITY_EXCLUDED_CATEGORIES: v1.0`
  - `definition_snapshot_date: [approval date]`

**Verify:**
- ✅ Definition versions are captured at approval time
- ✅ All three definitions are recorded
- ✅ Snapshot date is recorded
- ✅ Data is persisted to Close History

---

### Test Scenario 3C-2: Close Record Retrievability

**Setup:**
- Q3 FY2026 close has been approved and archived
- User (or auditor) wants to know: "Which definitions were active for Q3 2026?"

**Expected:**
- Can retrieve close record for Q3
- Close record includes definition versions
- Can answer: "Q3 2026 was processed with v1.0 definitions"

**Verify:**
- ✅ Close record is retrievable from Close History
- ✅ Definition versions are present in record
- ✅ Can determine which definitions were active
- ✅ Historical reproducibility is enabled

---

### Test Scenario 3C-3: Observation-to-Definition Traceability

**Setup:**
- Review Q3 approved close
- Look at an observation (e.g., revenue variance)
- Trace from observation → definition → close record

**Expected:**
- Observation shows: Definition PLAUSIBILITY_QOQ_THRESHOLD v1.0
- Close record shows: Definition PLAUSIBILITY_QOQ_THRESHOLD v1.0
- Versions match (consistent)

**Verify:**
- ✅ Observation attribution matches close record
- ✅ Definition versions are consistent end-to-end
- ✅ Auditability chain is complete (observation → definition → close)

---

### Acceptance Criteria for Gap 3B-C

- ✅ Analytical definitions are versioned (v1.0)
- ✅ Each observation records which definition triggered it
- ✅ Observation register displays definition attribution (business-readable)
- ✅ Approved close records capture definition versions
- ✅ Definition versions can be retrieved from close records
- ✅ Auditability chain is complete (observation → definition version → close record)
- ✅ Historical reproducibility is enabled
- ✅ All test scenarios pass

---

## Regression Testing

**Independent Test must verify NO REGRESSIONS:**

| Area | Regression Test |
|------|-----------------|
| **Phase 2 (Historical Diff)** | Verify Phase 2 still works; no changes from Gaps 1-3 |
| **Phase 3 (Plausibility)** | Verify Phase 3 still generates correct observations |
| **Phase 4 (Reconciliation)** | Verify commentary matching still works |
| **Phase 6 (Validation)** | Verify validation logic unchanged (only period-data wiring changed) |
| **Human Approval Gate** | Verify approval/rejection logic unchanged |
| **Close History** | Verify archive/retrieval still works |
| **Dashboard UI** | Verify no UI breakage; all tabs render correctly |

**Acceptance:** All regression tests pass; no existing functionality broken.

---

## Test Data Requirements

**Independent Test will need:**
- Q1-Q4 FY2025 historical data
- Q1-Q3 FY2026 data
- Observations for each period
- Commentary for at least Q3 and Q4
- Phase 6 validation results for prior periods

**Use the same canonical dataset (Handbook D11/D14 baseline)** to ensure consistency with prior verification.

---

## Test Execution Timeline

| Phase | Activity |
|-------|----------|
| **Phase 1: Test Planning** | Architect test scenarios, set up test data, prepare expected results |
| **Phase 2: Gap 1 Testing** | Verify Phase 6 period-data defect fix |
| **Phase 3: Gap 2 Testing** | Verify previous-period visibility |
| **Phase 4: Gap 3B-C Testing** | Verify definition versioning and attribution |
| **Phase 5: Regression Testing** | Verify no breakage to existing functionality |
| **Phase 6: Integration Testing** | Verify all three gaps work together in E2E context |
| **Phase 7: Sign-off** | Independent Test confirms all requirements met |

---

## Pass/Fail Criteria

**PASS if:**
- ✅ All test scenarios (1A-C, 2A-D, 3B-1 through 3C-3) pass
- ✅ All regression tests pass
- ✅ All acceptance criteria are met
- ✅ No unexpected defects found
- ✅ Governance/auditability requirements are satisfied

**FAIL if:**
- ❌ Any scenario fails
- ❌ Regression defects found
- ✅ New defects that block governance/auditability
- ❌ Data loss or corruption
- ❌ Acceptance criteria not met

**CONDITIONAL PASS if:**
- Minor defects found that do not affect Gaps 1-3 core functionality
- Document as Known Limitations; can be addressed in Phase 9

---

## Escalation Path

**If Independent Test finds issues:**
1. **Minor defect** (doesn't block E2E) — Log and document; proceed conditionally
2. **Major defect** (blocks E2E) — Escalate to Architect/Builder; block until fixed
3. **Governance defect** (auditability broken) — STOP; requires Principal decision

---

## Independent Test Authority

**Independent Test has authority over:**
- Test methodology and scenarios
- Test data generation
- Acceptance of or challenge to Builder's work
- Decision to pass or fail

**Independent Test does NOT have authority over:**
- Scope (scope is locked in by Principal)
- Definitions (locked in at 25%, ±2, S&B)
- Timeline (E2E demonstration deadline applies)

**If Independent Test identifies scope issues**, escalate immediately. Do not wait.

---

## Sign-Off

**Independent Test will issue:**
- **Verification Report** — All scenarios tested, results documented
- **Pass/Fail Assessment** — Whether Gaps 1-3 are verified
- **Known Limitations** (if any) — Issues found but not blocking
- **Recommendation** — Ready for E2E demonstration or blockers identified

**This sign-off is required before E2E Product Demonstration can proceed.**

