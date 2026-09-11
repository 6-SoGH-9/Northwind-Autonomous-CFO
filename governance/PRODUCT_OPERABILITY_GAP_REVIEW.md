# SUPERSEDED — PROVENANCE COPY

**PROVENANCE — NOT AUTHORITATIVE.** PM/Project Advisor input document (September 5, 2026), superseded on findings by `governance/architect_reports/architect_alignment_report_operability_gaps_1_4.md`.

Specific corrections on record: Gap 1's "cannot select the terminal period" framing is factually incorrect (Q4 FY2026 is selectable and is the default) — the real Gap 1 defect is narrower (Phase 6 evidence-package period-sourcing, see the authoritative Brief). The claim "Phase 4-6 results are not displayed" (Critical Gap #4, Step 7/8/9) is not supported by direct code inspection — the Commentary Review section already renders this chain for the current period. Gap 4 (period reopen/correction) is confirmed already-deferred, not a new finding. Retained for provenance only; do not cite this document's gap classifications as current architectural truth.

---

# Product Operability & User Journey Gap Review
## Northwind Autonomous CFO Office

**Review Date:** September 5, 2026  
**Methodology:** Direct code inspection + user experience evidence  
**Status:** CRITICAL OPERABILITY GAPS IDENTIFIED — Implementation exists but is not operable

---

## Executive Summary

The Northwind CFO Office has built most of the technical machinery (Phases 0-8), but **the product cannot be operated by a real user without developer involvement**. Configuration is hardcoded. Files are auto-discovered. Rules are inaccessible. Data correction workflows don't exist in the UI.

This is not a UI polish issue. This is a **product scope gap**: the application assumes a developer is standing next to the user, not that users operate it independently.

---

## 16-Step Operability Review

### **STEP 1: Company / Workspace Setup**

| Aspect | Intended | Implemented | Operable | Gap Type |
|--------|----------|-------------|----------|----------|
| Company selection | User selects company/workspace | None | ❌ No | **Capability Gap** |
| Company configuration | Set company name, fiscal calendar, regions | None | ❌ No | **Capability Gap** |
| Initial setup wizard | First-time user guide through setup | None | ❌ No | **Operability Gap** |
| Setup persistence | Save configuration for reuse | None | ❌ No | **Capability Gap** |

**Finding:** The application hardcodes the company as "Northwind Financial Co." (dashboard.py line 163). Users cannot create a new company, configure calendar, or change core settings.

**Evidence:**
- Dashboard.py line 163: `st.title("Northwind Financial Co. — FP&A Dashboard")`
- No company selector widget
- No settings/admin area

**User Impact:** A real CFO/Controller cannot use this product without modifying the code.

**Rework Risk:** HIGH — This is foundational. Configuration architecture must be decided before building application depth.

---

### **STEP 2: Dataset Intake & Storage**

| Aspect | Intended | Implemented | Operable | Gap Type |
|--------|----------|-------------|----------|----------|
| Dataset upload | User can upload their dataset | UI uploader visible in Phase 4 only | ⚠️ Partial | **Workflow Gap** |
| Dataset selection | Choose which dataset to load | Automatic via glob + Close History | ❌ No | **Capability Gap** |
| File location specification | Define where files come from/go | Hardcoded to current directory | ❌ No | **Configuration Gap** |
| Expected file format | Clear documentation on structure | Documented in rollups.py comments only | ❌ Hidden | **Documentation Gap** |
| Dataset validation | Confirm structure before use | Implicit (will error if missing sheets) | ⚠️ Implicit | **Operability Gap** |

**Finding:** The application uses `find_raw_dataset()` (rollups.py lines 25-80) which:
- Checks env variable `NORTHWIND_RAW_DATASET_PATH` (developer-only)
- Falls back to Close History (production path)
- Falls back to glob for `*.xlsx` with "northwind", "sample", "dataset" in name

**Evidence:**
```python
# rollups.py lines 63-66
candidates = [
    f for f in glob.glob("*.xlsx")
    if "northwind" in f.lower() and "sample" in f.lower() and "dataset" in f.lower()
]
```

**User Impact:** 
- ✅ Initial bootstrap works if file is named correctly and in current directory
- ❌ User cannot specify their own file location
- ❌ User cannot upload a different dataset without developer help
- ❌ User cannot understand what datasets are available or which one is active

**Rework Risk:** HIGH — Once the product goes live, users will have multiple datasets (quarters) and no way to navigate them.

---

### **STEP 3: Period Lifecycle**

| Aspect | Intended | Implemented | Operable | Gap Type |
|--------|----------|-------------|----------|----------|
| View available periods | See list of periods | Sidebar selectbox exists | ✅ Yes | None |
| Select a period | Choose which period to work on | Sidebar selectbox with constraint | ⚠️ Partial | **Workflow Gap** |
| Understand period state | Know if period is open/processing/reviewed/approved/closed | No UI display of state | ❌ No | **Capability Gap** |
| Period state transitions | Open → Reviewed → Approved → Closed | No UI controls | ❌ No | **Capability Gap** |
| Reopen a closed period | Correct/reprocess a period | No "Reopen" button or workflow | ❌ No | **Capability Gap** |
| Correct/replace data | Fix errors in an already-processed period | No correction workflow | ❌ No | **Capability Gap** |
| Data versioning | Understand which version of data is active | No version indicator | ❌ No | **Information Gap** |

**Finding:** Period selection exists but is constrained:
- Dashboard.py lines 203-210: Only periods with a prior period are selectable
- Line 204: `selectable_periods = [p for p in period_order if period_order.index(p) > 0]`

**Evidence:**
```python
# Dashboard.py lines 205-208
current_period = st.sidebar.selectbox(
    "Current period", selectable_periods, index=len(selectable_periods) - 1,
    format_func=R.fmt_period_label,
)
```

**User Impact:**
- ✅ User can see available periods in a dropdown
- ❌ User cannot select the very first period (intentional, but undocumented)
- ❌ **User cannot reopen a closed period** ← THIS IS YOUR Q3 2026 PROBLEM
- ❌ User cannot see the state of each period (is it reviewed? approved? closed?)
- ❌ No workflow to correct data once a close is archived

**Your Specific Problem:** You tried to submit Q3 2026, but Q3 2026 is the latest period in the dataset. The dashboard only allows selecting periods with a prior period, so Q3 2026 cannot be selected because there's no Q4 2026 in the dataset yet. The system is treating it as "already closed" implicitly because it's the terminal period.

**Rework Risk:** CRITICAL — This blocks the entire "period correction" workflow which is essential for a real close process.

---

### **STEP 4: Analytical Rules & Thresholds**

| Aspect | Intended | Implemented | Operable | Gap Type |
|--------|----------|-------------|----------|----------|
| View active rules | See what rules are enabled | Hardcoded in code only | ❌ No | **Capability Gap** |
| Understand thresholds | Know why something was flagged | No explanation in UI | ❌ No | **Information Gap** |
| Change thresholds | Adjust materiality, QoQ %, bands | Hardcoded constants only | ❌ No | **Capability Gap** |
| Configure rules | Enable/disable risk checks | No configuration UI | ❌ No | **Capability Gap** |
| Rule explanation | Understand the business logic | Documented in comments only | ❌ Hidden | **Documentation Gap** |

**Finding:** Thresholds are defined as module-level constants in close_validation.py:

**Evidence:**
```python
# close_validation.py lines 88-94
DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD = 0.25  # ← THE 25% YOU MENTIONED
DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND = 2
DEFAULT_EXCLUDED_CATEGORIES = ("Salaries & Benefits",)
```

These constants are:
- ✅ Well-documented in code comments
- ✅ Passed as parameters to Phase 3 function
- ❌ **Not exposed in any UI**
- ❌ **Users cannot see, understand, or modify them**
- ❌ **Rationale (lines 66-86) is in code comments, not in a user-facing help screen**

**User Impact:**
- ❌ **User cannot discover the 25% rule exists**
- ❌ **User cannot understand why Q3 2026 Sales & Marketing / Other Opex was flagged (or wasn't)**
- ❌ **User cannot adjust thresholds for business policy changes** (e.g., "this quarter we accept up to 30% because market is volatile")
- ❌ **User cannot see why Salaries & Benefits is excluded from Phase 3** (it's hardcoded, not configurable)
- ❌ When a threshold is breached, the observation register just shows a flag with no explanation of which rule triggered it

**YOUR SPECIFIC PROBLEM:** The 25% threshold **is never breached in the dataset** (your data shows max 13% QoQ variance). So no observations are flagged by Phase 3. The product runs silently without raising anything to investigate. This is exactly what you experienced: "the thresholds flag will never show up, and it doesn't help identify potential risk."

**Rework Risk:** CRITICAL — This is the core risk-detection mechanism. Without configuration UI, the product cannot adapt to different business needs.

---

### **STEP 5: Observation Generation & Display**

| Aspect | Intended | Implemented | Operable | Gap Type |
|--------|----------|-------------|----------|----------|
| Display observations | Show what was flagged | Observation register exists | ✅ Yes | None |
| Understand why flagged | Explain the anomaly | Only shows "Phase 2" or "Phase 3" | ⚠️ Minimal | **Information Gap** |
| Observation details | Department, Category, Period, variance | All present in table | ✅ Yes | None |
| Filter observations | Find flags for a specific area | No filter controls | ❌ No | **Operability Gap** |
| Historical context | See prior periods for comparison | Charts show trend separately | ⚠️ Disconnected | **Workflow Gap** |

**Finding:** Dashboard tab "Close Validation Status" (dashboard.py tab_close) displays the observation register, but:
- No explanation of which rule triggered each flag
- No way to filter by department or category
- Phase 4-6 reconciliation results not yet displayed (pending D13 verification)

**User Impact:**
- ✅ User can see what was flagged
- ❌ User cannot easily filter or search
- ❌ User does not see **which rule** triggered the flag (25%? Headcount-band? Historical revision?)
- ❌ User cannot see the recommended action

**Rework Risk:** MEDIUM — This is UI/UX polish, but it's critical for usability.

---

### **STEP 6: Controller Commentary**

| Aspect | Intended | Implemented | Operable | Gap Type |
|--------|----------|-------------|----------|----------|
| Provide commentary | Submit explanation for observation | Commentary.xlsx uploader exists | ✅ Yes | None |
| Create commentary | Write explanation in-app | No in-app text editor | ❌ No | **Workflow Gap** |
| Edit commentary | Revise explanation | Revision loop exists but clunky | ⚠️ Partial | **Operability Gap** |
| Save commentary | Store explanation durably | Persisted in session state | ⚠️ Temporary | **Information Gap** |
| View submitted commentary | See what was submitted | Commentary Review section exists | ✅ Yes | None |

**Finding:** Commentary workflow requires external file:
- Dashboard.py lines 859-890: File uploader for `Commentary.xlsx`
- Phase 4-6 (commentary_workflow.py) accepts the file and processes it
- No in-app text editor—Controller must submit a spreadsheet

**User Impact:**
- ⚠️ Controller must work outside the dashboard (open Excel, edit sheet, save, re-upload)
- ❌ No ability to type directly in the app
- ⚠️ Session-based storage means commentary is lost if browser refreshes
- ✅ Can revise and resubmit multiple times

**Rework Risk:** MEDIUM — This is a workflow gap, not a blocker. Could be improved with an in-app editor later.

---

### **STEP 7: Commentary Reconciliation (Phase 4)**

| Aspect | Intended | Implemented | Operable | Gap Type |
|--------|----------|-------------|----------|----------|
| Match commentary to observation | Determine which observation each comment refers to | Implemented in commentary_workflow.py | ✅ Built | **Verification Gap** |
| Display reconciliation result | Show matched observation | No UI display yet | ⚠️ Pending | **Workflow Gap** |
| Handle unmatched commentary | Indicate no match found | Logic exists but not displayed | ❌ Hidden | **Information Gap** |
| Multiple revisions | Allow Controller to resubmit | Revision loop exists | ✅ Yes | None |
| Understand matching logic | Know how commentary is interpreted | Not documented in UI | ❌ Hidden | **Documentation Gap** |

**Finding:** Phase 4 implementation exists (commentary_workflow.py) but results are not integrated into the observation register display yet (dashboard.py shows observation register, but Phase 4-6 outcomes are not rendered there — per Handbook Section 10).

**User Impact:**
- ❌ User cannot see which observation their commentary matched to
- ❌ If commentary didn't match, user doesn't know why
- ❌ No feedback loop showing reconciliation result

**Rework Risk:** HIGH — This is a display integration issue, not missing logic. Needs UI work before Phase 4-6 can be verified.

---

### **STEP 8: Evidence Validation (Phase 6)**

| Aspect | Intended | Implemented | Operable | Gap Type |
|--------|----------|-------------|----------|----------|
| Validate explanation | Check if explanation is supported | Implemented in commentary_workflow.py | ✅ Built | **Verification Gap** |
| Display validation result | Show Supported / Contradicted / Insufficient | No UI display yet | ⚠️ Pending | **Workflow Gap** |
| Explain validation reasoning | Show which evidence supports/contradicts | Not displayed | ❌ Hidden | **Information Gap** |
| Handle revisions | Allow resubmission if validation fails | Revision loop exists | ✅ Yes | None |

**Finding:** Same as Phase 4 — logic exists but not integrated into dashboard display.

**User Impact:**
- ❌ User cannot see validation result
- ❌ No feedback on whether explanation was sufficient

**Rework Risk:** HIGH — Same as Phase 4.

---

### **STEP 9: CFO/Finance Review**

| Aspect | Intended | Implemented | Operable | Gap Type |
|--------|----------|-------------|----------|----------|
| Finance user sees accumulated observations | Display all flagged items for period | Observation register visible | ✅ Yes | None |
| Finance user sees Controller commentary | View explanations provided | Commentary Review section visible | ✅ Yes | None |
| Finance user sees validation results | Check if explanations are supported | Results not displayed yet | ❌ No | **Workflow Gap** |
| Finance user reviews for approval | Manual review step | Exists (Finance/CFO review stage) | ✅ Exists | None |
| Finance user can edit commentary | Refine or add explanations | Can submit revision via the revision loop | ✅ Yes | None |

**Finding:** Workflow exists conceptually but is incomplete because Phase 4-6 results aren't displayed.

**User Impact:**
- ⚠️ Finance user can see observations but cannot see reconciliation/validation results
- ❌ Cannot make an informed approval/rejection decision without all evidence

**Rework Risk:** HIGH — Blocks decision-making.

---

### **STEP 10: Human Approval Gate**

| Aspect | Intended | Implemented | Operable | Gap Type |
|--------|----------|-------------|----------|----------|
| Explicit Approve button | User clicks to approve | Implemented in dashboard.py line 1015 | ✅ Yes | None |
| Explicit Reject button | User clicks to reject | Implemented in dashboard.py line 1020 | ✅ Yes | None |
| Block executive output without approval | Prevent narrative/deck if not approved | Structural guard at line 1150 | ✅ Yes | None |
| Approval state persistence | Remember approval across sessions | Session state only (lost on refresh) | ⚠️ Temporary | **Persistence Gap** |
| Audit trail | Record who approved and when | Not persisted to Close History yet | ❌ No | **Capability Gap** |

**Finding:** Human Approval Gate is implemented and independently verified (Handbook Section 10). It works correctly.

**User Impact:**
- ✅ Gate functions as intended
- ⚠️ Approval state is lost if browser refreshes (session state only)
- ❌ No audit trail of approvals

**Rework Risk:** LOW for the gate itself; MEDIUM for audit trail persistence.

---

### **STEP 11: Executive Narrative Generation (Phase 7)**

| Aspect | Intended | Implemented | Operable | Gap Type |
|--------|----------|-------------|----------|----------|
| Generate narrative | Create CFO/Board-ready narrative | Implemented with live API call OR download fallback | ✅ Yes | **Verification Gap** |
| API key requirement | Use Anthropic API if key present | Falls back to download if key absent | ✅ Yes | None |
| Manual fallback | Download prompt to use elsewhere | Download button exists | ✅ Yes | None |
| Narrative accuracy | Ensure no invented facts/causes | Prompt guards exist in code | ✅ Yes | **Verification Gap** |
| Narrative sources | Trace narrative back to observations | Currently not demonstrated end-to-end | ⚠️ Pending | **Demonstration Gap** |

**Finding:** Phase 7 is built but hasn't been verified end-to-end with real data.

**User Impact:**
- ⚠️ Live API call works IF `ANTHROPIC_API_KEY` is set
- ✅ Fallback download works if API key not available
- ❌ No live-semantic verification yet (per Handbook D13)

**Rework Risk:** LOW for the mechanism; HIGH for verification.

---

### **STEP 12: HTML Output**

| Aspect | Intended | Implemented | Operable | Gap Type |
|--------|----------|-------------|----------|----------|
| Generate HTML story | Create HTML output of narrative | Code exists in rollups.py | ✅ Built | **Not Yet Delivered** |
| Store HTML file | Save for retrieval | Path exists but files not provided for E2E scenarios | ⚠️ Incomplete | **Demonstration Gap** |
| Retrieve HTML | Access previously generated outputs | Close History can store metadata | ✅ Designed | **Not Yet Implemented** |
| HTML versioning | Track HTML versions per close | Close History architecture supports it | ✅ Designed | **Not Yet Implemented** |

**Finding:** HTML generation code exists but is not produced/delivered for the current E2E demonstration scenarios (per Handbook Section 10, "Current source files not yet supplied").

**User Impact:**
- ❌ Cannot see the HTML story output (hasn't been generated for E2E scenarios yet)
- ⚠️ Infrastructure exists but not operationalized

**Rework Risk:** LOW — Infrastructure is in place.

---

### **STEP 13: PPTX / Board Deck**

| Aspect | Intended | Implemented | Operable | Gap Type |
|--------|----------|-------------|----------|----------|
| Generate PPTX deck | Create Board-ready presentation | Code exists in rollups.py | ✅ Built | **Not Yet Delivered** |
| Store PPTX file | Save for retrieval | Path exists but files not provided for E2E scenarios | ⚠️ Incomplete | **Demonstration Gap** |
| Deck versioning | Track versions per close | Close History architecture supports it | ✅ Designed | **Not Yet Implemented** |

**Finding:** Same as HTML.

**User Impact:**
- ❌ Cannot see the PPTX output yet
- ⚠️ Infrastructure exists

**Rework Risk:** LOW.

---

### **STEP 14: Period Closure & Correction**

| Aspect | Intended | Implemented | Operable | Gap Type |
|--------|----------|-------------|----------|----------|
| Archive approved close | Save permanent snapshot | close_history.py implements this | ✅ Yes | None |
| Retrieve archived close | Access prior approved closes | Designed in D10, not yet operationalized | ⚠️ Designed | **Capability Gap** |
| Reopen closed period | Correct and reprocess | No UI workflow | ❌ No | **CRITICAL GAP** |
| Correct data mid-close | Fix errors before approval | No mechanism for this | ❌ No | **CRITICAL GAP** |
| Period immutability | Prevent accidental changes | Enforced via Close History | ✅ Yes | None |

**Finding:** Archive works; retrieval and correction workflows are missing.

**User Impact:**
- ✅ Approved closes are archived safely
- ❌ **User cannot reopen a closed period to fix errors** ← THIS IS A BLOCKER
- ❌ User cannot correct data once started
- ❌ If wrong data is uploaded, must start over (no recovery)

**Rework Risk:** CRITICAL — This is essential for any real close workflow.

---

### **STEP 15: Navigation, Status, Error Handling & Discoverability**

| Aspect | Intended | Implemented | Operable | Gap Type |
|--------|----------|-------------|----------|----------|
| Clear navigation | Understand how to move through workflow | Tab structure exists | ✅ Partial | **Information Gap** |
| Status displays | Know current position in workflow | Workflow state strip exists but incomplete | ⚠️ Partial | **Information Gap** |
| Error messages | Understand what went wrong | Errors are Streamlit defaults (generic) | ❌ Cryptic | **UX Gap** |
| Help/guidance | Learn how to use features | No in-app help or tooltips | ❌ No | **Documentation Gap** |
| Discoverability | Find features you need | Must explore tabs blind | ❌ No | **UX Gap** |

**Finding:** Basic navigation exists but lacks guidance.

**User Impact:**
- ⚠️ Tabs are clearly labeled but their purpose isn't obvious
- ❌ First-time user has no guidance
- ❌ Errors are cryptic (generic Streamlit errors)
- ❌ No tooltips explaining configuration or workflow

**Rework Risk:** MEDIUM — UX improvement, not blocking.

---

### **STEP 16: Demo / "Play With the Product" Experience**

| Aspect | Intended | Implemented | Operable | Gap Type |
|--------|----------|-------------|----------|----------|
| Launch and see dashboard | Open the app | ✅ `streamlit run Northwind_Financial_Dashboard.py` | ✅ Yes | None |
| Explore without setup | Click around to understand | ✅ Can see data immediately | ✅ Yes | None |
| Change periods | Switch between Q3/Q4/etc | ✅ Sidebar selector works | ✅ Yes | None |
| Change assumptions | Adjust materiality/thresholds | ❌ Cannot find configuration | ❌ No | **CRITICAL** |
| Submit commentary | Try the workflow | ❌ Must provide Excel file externally | ⚠️ Clunky | **Operability Gap** |
| See results | Watch system respond | ⚠️ Partial (Phase 4-6 results not displayed yet) | ⚠️ Incomplete | **Integration Gap** |
| Generate output | See the Board deck | ❌ Not delivered for demo scenarios | ❌ No | **Demonstration Gap** |

**Finding:** The product can be launched and explored, but demonstrates incomplete workflows.

**User Impact:**
- ✅ Can see the data and understand the structure
- ❌ Cannot operate key features (configuration, correction, rules)
- ❌ Feels like a demo, not a product

**Rework Risk:** CRITICAL for demonstration; blocks E2E product proof.

---

## Summary of Gap Classification

### **CRITICAL GAPS** (Block E2E demonstration or product operation)
1. **Configuration UI is completely missing** — thresholds, rules, all hardcoded
2. **Period correction workflow does not exist** — cannot reopen a closed period
3. **File/dataset location is hardcoded** — users cannot specify their own directory
4. **Phase 4-6 results are not displayed** — reconciliation/validation outcomes are hidden
5. **Period selection is constrained** — cannot select terminal period (your Q3 2026 problem)
6. **Company setup is missing** — application hardcoded to "Northwind"

### **HIGH GAPS** (Severely limit usability)
7. Data versioning / period lifecycle not exposed
8. No audit trail for approvals
9. No error explanations (generic Streamlit errors)
10. Commentary requires external Excel file (not in-app editor)
11. Observation flagging logic not explained to users

### **MEDIUM GAPS** (Usability issues, not blockers)
12. No filtering/search on observations
13. No in-app help or tooltips
14. HTML/PPTX not yet delivered for E2E scenarios
15. Workflow state display incomplete

---

## What This Means for Your Next Steps

### **You cannot run an E2E demonstration yet because:**
1. ✅ Phase 4-6 logic is built and regression-verified
2. ✅ Human Approval Gate is built and independently verified
3. ❌ **Phase 4-6 results are not displayed in the observation register** — users cannot see what matched, what validated, what's Supported/Contradicted
4. ❌ **Period selection cannot handle terminal period** — you tried Q3 2026 (latest), which cannot be selected
5. ❌ **Configuration is missing** — users cannot see, understand, or change the 25% rule or other thresholds

### **Before E2E demonstration can work, you must:**
1. **Integrate Phase 4-6 results into the dashboard display** — show reconciliation and validation outcomes in the observation register or a new section
2. **Fix period selection to allow terminal period** — modify line 204 in dashboard.py to allow the latest period to be selected, OR define the "period complete" state explicitly
3. **Create a configuration UI** — even if minimal (a Setup tab with toggle-able rules and threshold sliders)

### **What the code review found about your specific problems:**

#### **Problem 1: "I cannot submit Q3 2026"**
**Root cause:** Q3 2026 is the latest (terminal) period in your dataset. Line 204 of dashboard.py explicitly excludes the first period and implicitly treats the terminal period as "no next period to compare to."
```python
selectable_periods = [p for p in period_order if period_order.index(p) > 0]
# This allows Q1, Q2, Q3 (but not terminal Q4 if it existed as a Q4)
# Your Q3 is terminal, so it would NOT be selectable
```
**Fix:** Either (a) add Q4 2026 to your dataset, (b) change the logic to allow terminal period, or (c) explicitly define when a period is "ready to close" vs. "waiting for next quarter's data."

#### **Problem 2: "The 25% threshold is hardcoded somewhere"**
**Root cause:** `DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD = 0.25` in close_validation.py line 88. It's not exposed in any UI.
```python
# close_validation.py line 88
DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD = 0.25  # Never breached in your data (max 13%)
```
**Impact:** Your data never triggers this threshold, so no observations are raised. The system runs silently. This is correct behavior, but the user has no way to know:
- That a 25% threshold exists
- Why nothing was flagged
- How to change the threshold for different business conditions

**Fix:** Create a Configuration UI to expose and explain thresholds.

#### **Problem 3: "The other rule is also not accessible"**
**Root cause:** `DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND = 2` in close_validation.py line 89. Also not exposed.
```python
# close_validation.py line 89
DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND = 2
# Headcount changes of ±2 or fewer are treated as "noise," not a driver
```
**Fix:** Same as Problem 2.

#### **Problem 4: "I cannot define where my files should be located"**
**Root cause:** `find_raw_dataset()` in rollups.py lines 25-80 uses glob patterns and Close History. No UI to specify file paths.
```python
# rollups.py lines 63-66
candidates = [
    f for f in glob.glob("*.xlsx")
    if "northwind" in f.lower() and "sample" in f.lower() and "dataset" in f.lower()
]
```
**Fix:** Create a Data Configuration UI where users can (a) upload a dataset, (b) specify a directory, or (c) select from available closes in Close History.

---

## Priority for Next Milestone

**Do NOT continue with Phase 4-6 verification or E2E demonstration until:**

1. **Display Phase 4-6 results in the dashboard** — integrate reconciliation and validation outcomes into a visible section of the observation register or Create Review tab

2. **Fix period selection logic** — decide whether terminal periods should be allowed, and implement accordingly

3. **Create minimal Configuration UI** — even just a toggle or settings panel where users can see the 25% threshold and understand why items are/aren't flagged

These are not new Builder tasks. These are **product-definition clarifications** that must be resolved before implementation can proceed.

---

## Recommendation

**Next milestone should be:**

**Product Operability Review Closure**

Before declaring anything "complete," ensure:
- ✅ Workflow coherence (Step 1-16 all connected)
- ✅ Configuration visibility (users can see rules, thresholds, settings)
- ✅ Data lifecycle clarity (users can select periods, reopen if needed, understand state)
- ✅ Result display (Phase 4-6 outcomes visible in the UI)
- ✅ Error clarity (users understand what went wrong and why)

**NOT "E2E demonstration" OR "LLM enhancement."**

The product must be operable first. Everything else is secondary.
