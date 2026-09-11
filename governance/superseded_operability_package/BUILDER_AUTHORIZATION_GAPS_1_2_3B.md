# SUPERSEDED — PROVENANCE COPY

**PROVENANCE — NOT AUTHORITATIVE.** Principal/Advisor-authored document, briefly and incorrectly placed in `governance/builder_briefs/` (added then removed from canonical `main` — commits visible in repository history). Never Architect-authored; per this project's governance model, Builder Briefs are Architect-owned. Gap 1's content here is consistent with, and was folded into, the authoritative Brief. Gap 2's "previous-period visibility" framing and Gap 3's registry description were both scope inputs, not verified architecture, at the time this was written — both have since been explicitly principal-authorized at this document's full scope and are now governed by `governance/builder_briefs/builder_brief_operability_gaps_1_2_3.md`, which is the sole authoritative version. Retained for provenance only.

---

# Builder Authorization Package
## Operability and Auditability Work — Gaps 1, 2, 3B

**To:** Builder  
**From:** Principal (Authorization)  
**Subject:** Approved scope for operability and auditability improvements  
**Status:** AUTHORIZED — Proceed with work  
**Scope:** Three distinct work items (Gaps 1, 2, 3B) tied to E2E Product Demonstration  
**Deferral:** Baseline/trend analysis NOT authorized (deferred to Phase 10 evaluation)

---

## Authorization Context

**What has been approved:**
- Principal has reviewed Product Operability Gap Review
- Architect has provided clarifications on four gaps
- Principal has made decisions on Gaps 1, 2, 3 Option B
- Principal has approved "consolidate now, evolve later" roadmap for analytical engine
- Baseline/trend analysis is explicitly deferred to Phase 10

**What Builder is authorized to do:**
- Fix Gap 1: Phase 6 evidence-package defect
- Improve Gap 2: Previous-period visibility for Phase 4-6 results
- Implement Gap 3 Option B: Capture and display analytical definition versions for auditability

**What Builder is NOT authorized to do:**
- Implement baseline/trend analysis
- Make analytical definitions user-configurable
- Change Phase 3 detection thresholds or logic
- Introduce new analytical rules beyond capturing/versioning existing ones

---

## Gap 1: Phase 6 Evidence-Package Defect Fix

### What to Fix

**Problem:** Phase 6 evidence-package construction pulls headcount data from **sidebar period**, not from **observation register period**.

**Consequence:** 
- If user navigates sidebar to Q3, Phase 6 validates Q4 observations against Q3 headcount data
- Silent correctness defect (system produces wrong validation results without warning)

**Example:**
```
Sidebar shows: Q3 FY2026 (user navigated here)
Observation register shows: Q4 FY2026 observations (what's being reviewed)
Phase 6 pulls headcount from: Q3 (sidebar) — WRONG
Phase 6 should pull from: Q4 (observation register) — CORRECT
Result: Validation is against wrong period's data
```

### Work Scope: Gap 1

**Objective:** Wire Phase 6 evidence-package to use observation register's period, not sidebar period.

**Files involved:**
- `commentary_workflow.py` — `_validate_*_claim()` functions
- Likely: wherever headcount data is retrieved for validation
- `Northwind_Financial_Dashboard.py` — data passing to Phase 6

**What to change:**
1. Identify where Phase 6 retrieves headcount data for validation
2. Change data source from sidebar period to observation register's actual period
3. Ensure all Phase 6 validation uses the correct period's data

**What to test:**
- Select Q3 observation
- Navigate sidebar to Q2
- Validate commentary
- Confirm Phase 6 uses Q3 data (observation period), not Q2 data (sidebar period)

**Acceptance criteria:**
- ✅ Phase 6 evidence-package always uses observation register's period
- ✅ Sidebar navigation does not affect Phase 6 validation accuracy
- ✅ All validation results are correct for the observation's actual period
- ✅ No silent data mismatches

**Priority:** HIGH — This is a correctness defect affecting validation results

**Complexity:** Low — Scoped, localized fix

---

## Gap 2: Previous-Period Visibility for Phase 4-6 Results

### What to Fix

**Problem:** Users can view Phase 4-6 results (observation→commentary→match→validation detail) for latest period only.

**Cannot see:** Historical close's Phase 4-6 results from prior quarters.

**Consequence:**
- Controllers cannot audit/review how prior quarters' observations were explained and validated
- Auditors cannot trace back through historical closes
- Governance visibility is limited to current period only

**Example:**
```
Current period: Q4 FY2026 (observations visible)
User wants to review: Q3 FY2026 observations and their validation
Current state: Cannot navigate to Q3 Phase 4-6 results
Required: Enable navigation to view Q3 Phase 4-6 results
```

### Work Scope: Gap 2

**Objective:** Enable users to navigate to and view Phase 4-6 results (observation→commentary→match→validation detail) for previous periods.

**Files involved:**
- `Northwind_Financial_Dashboard.py` — Period navigation, Close Validation Status tab, Commentary Review section
- Likely: Data retrieval from Close History for prior periods

**What to change:**
1. Identify where Close Validation Status tab retrieves observations for display
2. Make period selector enable viewing **prior periods' results** (not just current period)
3. Ensure Phase 4-6 data (matches, validation results) is retrievable for prior periods
4. Display previous period results with full detail (observation→commentary→match→validation chain)

**What to test:**
- Navigate period selector to Q3 FY2026
- Go to Commentary Review section
- Confirm observations for Q3 are displayed with full Phase 4-6 detail
- Confirm "Matched via" labels are visible
- Confirm validation results are shown

**Acceptance criteria:**
- ✅ Users can select any prior period and view its Phase 4-6 results
- ✅ Observation→commentary→match→validation chain is complete for prior periods
- ✅ Historical results are retrievable from Close History
- ✅ No data loss or unavailability for prior quarters

**Priority:** HIGH — Enables audit trail and historical review; required for governance

**Complexity:** Medium — Requires filtering/retrieval logic for Close History

---

## Gap 3 Option B: Analytical Definition Versioning and Auditability

### What to Implement

**Problem:** Analytical definitions (25% QoQ threshold, ±2 headcount band, excluded categories) are not versioned, not visible, and not captured with approved closes.

**Consequence:**
- Auditor in 2027 cannot answer: "Which analytical definitions were active when Q3 2026 was closed?"
- Observations don't explain which rule triggered them
- Governance auditability is implicit (in code), not explicit (in records)

**Approval:** Principal has chosen Option B — "Visible, versioned, auditable"

**This is not configurability.** Definitions remain centrally governed, non-configurable. This is governance visibility.

### Work Scope: Gap 3 Option B — Three Components

#### Component 3A: Analytical Definition Registry

**Objective:** Create a versioned registry of analytical definitions.

**What to create:**
1. **Analytical Definition metadata structure** (can be config file, code constants with metadata, or database table)
   ```
   Definition ID: PLAUSIBILITY_QOQ_THRESHOLD
   Version: v1.0
   Effective date: 2026-01-01
   Value: 0.25 (25%)
   Description: "QoQ variance >25% indicates anomalous movement"
   Category: Analytical Definition (not configurable)
   Applied to: All revenue/expense/headcount metrics
   
   Definition ID: PLAUSIBILITY_HEADCOUNT_BAND
   Version: v1.0
   Effective date: 2026-01-01
   Value: 2
   Description: "Headcount changes ±2 or fewer treated as normal variation"
   Category: Analytical Definition (not configurable)
   
   Definition ID: PLAUSIBILITY_EXCLUDED_CATEGORIES
   Version: v1.0
   Effective date: 2026-01-01
   Value: ["Salaries & Benefits"]
   Description: "S&B costs excluded from Phase 3 QoQ threshold (handled separately)"
   Category: Analytical Definition (not configurable)
   ```

2. **Definition versioning** — If definitions ever change (Phase 11+), create v1.1, v2.0, etc. with effective dates

3. **Definition retrieval** — Ability to query "What definitions were active on date X?"

**Acceptance criteria:**
- ✅ All analytical definitions are registered with metadata
- ✅ Each definition has a stable version identifier
- ✅ Effective dates are recorded
- ✅ Definitions can be queried by version/date
- ✅ Definitions are immutable once published (no editing after effective date)

**Priority:** HIGH — Foundation for auditability

**Complexity:** Low — Primarily data structure and versioning logic

---

#### Component 3B: Observation Attribution

**Objective:** Each generated observation records which analytical definition triggered it.

**Current state:**
```
Observation: "QoQ revenue variance +28.0% detected"
[No explanation of which rule triggered it]
```

**Desired state:**
```
Observation: "QoQ revenue variance +28.0% detected"
Analytical definition triggered: PLAUSIBILITY_QOQ_THRESHOLD v1.0
Rule: QoQ movement >25%
Threshold value: 25%
Definition version: v1.0
Effective date: 2026-01-01
Result: Flagged as anomalous
```

**What to change:**
1. When Phase 3 generates an observation, capture **which definition triggered it**
2. Store definition ID + version in observation record
3. When displaying observation, show:
   - The definition name (business-readable)
   - The threshold/rule (what the definition is)
   - The version (for reproducibility)

**Files involved:**
- `close_validation.py` — Phase 3 observation generation
- `Northwind_Financial_Dashboard.py` — Observation register display
- Data model for observations

**Acceptance criteria:**
- ✅ Each observation records which definition triggered it
- ✅ Definition ID, version, and rule are captured
- ✅ Observation register displays definition attribution (business-readable form)
- ✅ Users can see **why** each observation was generated (which rule)
- ✅ Historical observations retain attribution (traceable to v1.0)

**Priority:** HIGH — Explainability and auditability

**Complexity:** Medium — Requires observation data model changes and display updates

---

#### Component 3C: Close Record Audit Capture

**Objective:** When a close is approved and archived, capture the exact analytical definition versions that were active.

**What to capture:**
```
Close record (Q3 FY2026):
{
  period: "Q3 FY2026",
  approval_date: "2026-10-15",
  approval_status: "Approved",
  
  --- NEW: Analytical definition audit trail ---
  analytical_definitions_active: {
    PLAUSIBILITY_QOQ_THRESHOLD: "v1.0",
    PLAUSIBILITY_HEADCOUNT_BAND: "v1.0",
    PLAUSIBILITY_EXCLUDED_CATEGORIES: "v1.0"
  },
  definition_snapshot_date: "2026-10-15",
  
  observations: [
    {
      observation_id: "OBS-Q3-REV-001",
      definition_triggered: "PLAUSIBILITY_QOQ_THRESHOLD v1.0",
      ...
    }
  ]
}
```

**What to change:**
1. When close is approved (Human Approval Gate), capture active definition versions
2. Archive this metadata with the close record
3. Store in Close History for later retrieval

**Files involved:**
- `close_history.py` — Close archival
- Human Approval Gate logic

**Acceptance criteria:**
- ✅ Approved close records capture analytical definition versions
- ✅ Definition versions are archived with close
- ✅ Can later query: "Which definitions were active for Q3 2026?"
- ✅ Historical closes remain reproducible even if definitions change

**Priority:** HIGH — Auditability foundation

**Complexity:** Low-Medium — Data capture at approval point

---

### Gap 3 Option B: Full Scope Summary

| Component | Purpose | Priority | Complexity |
|-----------|---------|----------|-----------|
| **3A: Definition Registry** | Version and register all analytical definitions | HIGH | Low |
| **3B: Observation Attribution** | Each observation shows which definition triggered it | HIGH | Medium |
| **3C: Close Record Capture** | Archive definition versions with approved closes | HIGH | Low-Medium |

**Acceptance criteria (all components):**
- ✅ All three components complete
- ✅ End-to-end auditability: Can trace observation → definition version → close record
- ✅ Governance visibility: Users see which rules are active
- ✅ Reproducibility: Same definitions always produce same results
- ✅ No user configuration (definitions remain centrally governed)

---

## What NOT to Do

**Builder must NOT:**
- ❌ Make analytical definitions user-configurable
- ❌ Implement baseline/trend analysis
- ❌ Change Phase 3 detection thresholds
- ❌ Add new analytical rules (only version existing ones)
- ❌ Modify the 25% or ±2 values (lock these in)
- ❌ Build UI for rule configuration

**Baseline/trend analysis is explicitly deferred.** Do not include it in any of this work.

---

## Builder's Verification Requirements

**Gap 1 (Phase 6 defect):**
- Regression test: All existing Phase 6 validations still work correctly
- New test: Phase 6 validation uses observation period when sidebar shows different period
- Test case: Sidebar Q2, observation Q4, validate headcount claims — should use Q4 data

**Gap 2 (Previous-period visibility):**
- Navigation test: Can select any prior period and view Phase 4-6 results
- Data test: Q3 FY2026 results are complete and correct
- Regression test: Current period (Q4) results remain unchanged

**Gap 3B (Observation attribution):**
- Each Phase 3 observation includes definition attribution
- Observation register displays definition information
- Users can see "Flagged because QoQ movement >25% (v1.0)"

**Gap 3C (Close record capture):**
- Approved close includes analytical definition version snapshot
- Can retrieve: "Which definitions were active for Q3 2026?"

---

## Independent Test Verification

**Independent Test will verify:**
1. **Gap 1:** Phase 6 evidence-package uses correct period's data
2. **Gap 2:** Previous-period results are complete and accurate
3. **Gap 3A-C:** Analytical definitions are versioned, captured, and traceable

**These verifications are preconditions for:**
- D13 (Phase 4-6 verification) — cannot complete without Gap 1 and 2
- E2E Product Demonstration — cannot demonstrate governance/auditability without Gap 3B-C

---

## Scope Boundaries

### Included (Authorized):
- Fix Phase 6 period-data defect
- Enable previous-period Phase 4-6 visibility
- Version and display analytical definitions
- Capture definitions with approved closes
- Improve observation attribution for explainability

### Deferred (NOT authorized):
- Baseline/trend analysis (Phase 10+)
- User-configurable rules (never)
- New analytical definitions (future decision)
- Rule optimization (Phase 10+ evaluation)

---

## Timeline and Dependencies

**Critical path for E2E demonstration:**
1. **Gap 1 fix** — Unblock D13 (Phase 4-6 verification)
2. **Gap 2 improvement** — Support historical review
3. **Gap 3B attribution** — Demonstrate governance/explainability
4. **Gap 3C capture** — Complete auditability architecture

**All three gaps must complete before:**
- D13 independent verification (Phase 4-6)
- E2E Product Demonstration
- Principal sign-off on governance architecture

---

## Builder Authority and Autonomy

**Builder has authority over:**
- Implementation approach (how to wire Phase 6 period reference, how to structure definition registry, etc.)
- Technical design decisions within approved scope
- Regression testing strategy
- Code organization

**Builder does NOT have authority over:**
- Scope (do not expand to baseline/trend analysis)
- Analytical definitions (lock in 25%, ±2, S&B exclusion)
- Configurability (definitions remain code-governed)
- Timeline (E2E demonstration is the gate)

**If Builder identifies technical blockers**, escalate to Architect immediately. Do not wait.

---

## Summary

**Builder is authorized to proceed with:**
- Gap 1: Phase 6 defect fix (small, high-priority)
- Gap 2: Previous-period navigation improvement (medium, high-priority)
- Gap 3B-C: Analytical definition versioning and auditability (medium-priority, high-value)

**Builder is explicitly NOT authorized to:**
- Implement baseline/trend analysis (deferred to Phase 10)
- Make definitions configurable (never)
- Change analytical thresholds (locked in)

**This work enables:**
- Complete Phase 4-6 verification (D13)
- Governance/auditability demonstration (E2E)
- Audit trail for Principal sign-off

**Proceed with Builder authorization as specified above.**

