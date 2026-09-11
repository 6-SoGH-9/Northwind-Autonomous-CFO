# SUPERSEDED — PROVENANCE COPY

**PROVENANCE — NOT AUTHORITATIVE.** PM/Project Advisor decision-request package addressed to the Architect. Superseded by the Architect's actual response (`governance/architect_reports/architect_alignment_report_operability_gaps_1_4.md`) and by the authoritative Builder Brief (`governance/builder_briefs/builder_brief_operability_gaps_1_2_3.md`). Retained for provenance/context only — the questions this document poses were answered in the Architect report; do not treat this document's framing as settled.

---

# Architect Package

## Product Operability Gaps — Architectural Clarification and Decision Request

**To:** Architect
**From:** PM / Project Advisor
**Subject:** Four product operability gaps requiring architectural interpretation
**Status:** Architectural clarification required — **no implementation authorization**

---

# 1. Purpose

The PM has identified four areas where the current product evidence does not yet establish a sufficiently clear, operable end-to-end product workflow.

The purpose of this package is **not** to create four Builder tasks.

The purpose is to ask the Architect to determine:

* what the intended product capability actually is;
* what the current architecture and implementation already support;
* whether an actual capability gap exists;
* how the gap should be classified;
* what architectural consequences or dependencies exist;
* what existing architecture must be preserved;
* what, if anything, requires a product or Principal decision;
* whether implementation is actually necessary;
* and whether the issue belongs in the current E2E milestone or should legitimately be deferred.

The PM will subsequently challenge the Architect's interpretation against the intended product journey and roadmap before any implementation is authorized.

---

# 2. Scope and Decision Boundary

This document is a **clarification and decision package only**.

Identification of a gap does **not** by itself imply:

* a new screen;
* a new configuration mechanism;
* a new architectural component;
* a change to an established data model;
* a new Builder task;
* reopening of an established architectural decision;
* or inclusion in the current milestone.

The Architect is explicitly asked to classify each issue rather than assume that implementation is required.

Possible classifications include:

* Product requirement
* Architectural requirement
* Implementation gap
* Workflow gap
* Data/integration gap
* Testing/verification gap
* Documentation issue
* Governance issue
* Product decision required
* Roadmap decision required
* Legitimately deferred
* No material gap identified

No implementation scope is authorized by this package.

---

# 3. Operating Context

The current strategic objective is to establish a coherent, demonstrable CFO workflow from product setup through final executive output.

The intended product journey includes, among other stages:

1. Company/workspace setup
2. Dataset intake and storage
3. Period lifecycle
4. Analytical rules and thresholds
5. Observation generation
6. Controller commentary
7. Commentary reconciliation
8. Evidence/validation
9. Finance/CFO review
10. Human approval
11. HTML output
12. Board deck/PPTX output
13. Period closure/archival
14. Re-running/correcting a period
15. Navigation, status, errors and discoverability
16. Demonstration/play-with-product experience

The PM's concern is not whether individual technical components exist.

The concern is whether the components form an **operable product workflow that a Controller can understand and use**.

---

# 4. Preservation Principle

The identification of these gaps must not automatically reopen established architectural decisions.

Where the existing architecture already supports the intended capability, the expectation is to **preserve that architecture and identify the minimum necessary change**.

An established architectural decision should only be reconsidered where the Architect identifies a genuine:

* conflict;
* missing capability;
* lifecycle consequence;
* data-model consequence;
* integration consequence;
* governance requirement;
* or other material architectural issue.

The objective is to close genuine product gaps, **not to redesign the system because the review has identified something that is not yet sufficiently visible or operable**.

---

# 5. Gap Summary

| # | Area                           | Current observation                                                                                                                                                          | Initial PM assessment              | Decision required                                                            |
| - | ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- | ---------------------------------------------------------------------------- |
| 1 | Workflow / Operating Model     | The latest available period is not currently selectable for the observed workflow                                                                                            | Potential E2E issue                | Determine intended period operating model                                    |
| 2 | Workflow / Integration         | Phase 4–6 results exist but are not sufficiently visible in the current user workflow                                                                                        | Potential E2E / verification issue | Define canonical information and workflow contract                           |
| 3 | Configuration / Governance     | Rules and thresholds are currently represented as code-level constants without an identified user-facing configuration or clearly established product-level governance model | Product/governance question        | Classify what should be policy, analytical definition, or technical constant |
| 4 | Lifecycle / Product Capability | Operational reopen/correct/reprocess workflow for closed periods is not currently available                                                                                  | Product completeness issue         | Determine scope and roadmap timing                                           |

These four items are intentionally **not treated as equivalent implementation tasks**.

---

# 6. Gap 1 — Latest Available Period and Processing Workflow

## 6.1 Observed issue

During product demonstration, the latest available period, Q3 FY2026, was not available for selection in the sidebar for the observed processing workflow.

The current evidence indicates that period ordering/filtering logic affects which periods are selectable.

The PM does **not** want to infer from this observation alone that the implementation is technically incorrect.

The relevant question is first:

> **What is the intended product operating model for the latest available period?**

## 6.2 Questions for Architect

Please determine:

### A. Actual current behaviour

* What exact logic determines which periods are selectable?
* Is the latest available period intentionally excluded?
* If so, why?
* Are there dependencies between the period selector and Phase 2 / Phase 3 processing?
* Are there prerequisites that require another period to exist or be completed first?

### B. Intended operating model

Please interpret the intended workflow:

* Should the latest available period normally be selectable for processing?
* Is there a deliberate distinction between an "available" period and a "processable" period?
* Does the product require a previous period to establish a comparison baseline?
* Is the observed behaviour a workflow constraint, a technical implementation issue, or an intentional lifecycle rule?

The term **"terminal period" should not be assumed as an established product concept**. If such a concept is useful, please define it.

### C. E2E impact

Please determine whether the current behaviour:

* actually blocks the intended E2E demonstration;
* merely changes the demonstration scenario;
* or exposes a genuine product/workflow gap.

## 6.3 Required Architect response

Please return:

1. Product interpretation
2. Actual current behaviour
3. Actual gap, if any
4. Gap classification
5. Relevant period/lifecycle dependencies
6. Existing architecture to preserve
7. Architectural implications
8. Options/trade-offs
9. Architect recommendation
10. Current E2E impact
11. Whether implementation is required
12. If implementation is required, what must first be defined
13. If implementation is not required, recommended deferral/recording

---

# 7. Gap 2 — Phase 4–6 Results and User Workflow

## 7.1 Observed issue

The implementation contains Phase 4–6 logic for:

* commentary/observation matching;
* reconciliation;
* validation.

The current product workflow, however, does not yet make the complete result sufficiently visible to the user.

In particular, the current dashboard experience does not clearly expose the full relationship between:

**Observation → Commentary → Reconciliation → Validation outcome**

including outcomes such as:

* Supported
* Contradicted
* Insufficient

The current evidence indicates that the underlying functionality exists, but independent verification of the complete live workflow remains outstanding.

## 7.2 Important qualification

The PM does **not** want to assume that "results are not visible in the UI" automatically means a new UI is required.

The architectural question comes first:

> **What is the canonical product information and workflow contract for Phase 4–6?**

Only after that should implementation or presentation mechanisms be considered.

## 7.3 Questions for Architect

Please determine:

### A. Canonical workflow

What is the intended product flow between:

1. observation generation;
2. Controller commentary;
3. deterministic/semantic matching;
4. reconciliation;
5. evidence validation;
6. finance/CFO review;
7. human approval?

### B. Data contract

What information must persist across those stages?

For example:

* observation identity;
* commentary identity;
* match relationship;
* reconciliation result;
* validation status;
* evidence;
* period;
* dataset/data version;
* timestamps;
* user/action information;
* downstream approval state.

Please distinguish what is already architecturally established from what remains undefined.

### C. User visibility

What information must a Controller be able to understand in order for the workflow to be operational?

This should be expressed as **product information requirements**, not a prescribed screen design.

### D. Verification

Please determine whether the current lack of visible end-to-end results:

* blocks the intended E2E demonstration;
* affects D13 independent verification;
* affects only observability;
* or indicates a deeper workflow/data-persistence gap.

The PM deliberately does **not** assert that UI visibility is necessarily a prerequisite for D13 verification. Please determine the relationship.

## 7.4 Required Architect response

Please return:

1. Canonical product workflow
2. Required information/data contract
3. Current architectural support
4. Actual gap
5. Gap classification
6. Existing architecture to preserve
7. Architectural implications
8. Dependencies
9. User-visibility requirements
10. E2E impact
11. D13 verification implications
12. Options/trade-offs
13. Architect recommendation
14. Whether implementation is required
15. If implementation is required, what must first be defined

---

# 8. Gap 3 — Analytical Rules, Thresholds and Governance

## 8.1 Observed issue

The current implementation contains code-level constants including:

* `DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD = 0.25`
* `DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND = 2`
* `DEFAULT_EXCLUDED_CATEGORIES = ("Salaries & Benefits",)`

Phase 3 accepts threshold parameters.

However, the current product evidence does not identify a user-facing configuration mechanism or a clearly established product-level governance model for these values.

The PM does **not** conclude that this is necessarily a missing settings screen.

The question is first one of product definition and governance.

## 8.2 Required distinction

Please classify relevant values according to:

### A. Business policy

Values that represent organisational policy and may legitimately require controlled configuration.

### B. Analytical definition

Values or rules that define how the analytical methodology itself works and therefore should remain centrally governed.

### C. Technical implementation constant

Values that are implementation details and should remain developer-controlled.

The PM specifically does not want every hardcoded value converted into user configuration.

## 8.3 Questions for Architect

Please determine:

1. Which current constants belong to which category?
2. Which rules are part of the analytical definition?
3. Which, if any, represent business policy?
4. Does the product need an operational mechanism to change or govern any of them?
5. If configuration is required, who should control it?
6. Does configuration require versioning?
7. Should a period retain the rule version used when it was processed?
8. What auditability is required?
9. What happens when analytical definitions change?
10. What should a Controller/CFO be able to understand about why an observation was generated?
11. Is user-facing visibility required even where user configuration is not?
12. Does any of this affect current E2E demonstration?
13. What belongs in the current milestone versus a later product capability?

## 8.4 Required Architect response

Please return:

1. Classification of relevant values
2. Product interpretation
3. Governance interpretation
4. Current architectural support
5. Actual gap
6. Gap classification
7. Existing architecture to preserve
8. Versioning/audit implications
9. Workflow implications
10. E2E impact
11. Options/trade-offs
12. Architect recommendation
13. Whether implementation is required
14. Whether user-facing configuration is actually required
15. If deferred, recommended roadmap placement

---

# 9. Gap 4 — Closed Period Correction / Reopen / Reprocess

## 9.1 Observed issue

The current product supports archival/immutability behaviour, but the operational workflow for:

**Closed → Reopened → Corrected/Replaced → Reprocessed → Reviewed → Approved → Closed**

is not currently available as an operational product workflow.

The Handbook identifies this capability but places it later in the roadmap.

The PM therefore does **not** assume this is a current implementation blocker.

## 9.2 Questions for Architect

Please determine:

### A. Product capability

Is reopen/correction/reprocessing an intended product capability?

If yes:

* what is the intended lifecycle;
* who may reopen;
* under what conditions;
* what happens to the original data;
* what happens to observations;
* what happens to commentary;
* what happens to validation;
* what happens to approvals;
* what happens to generated outputs?

### B. Data/version lifecycle

Please determine whether correction requires:

* immutable historical versions;
* replacement datasets;
* processing/version identifiers;
* observation regeneration;
* commentary invalidation or reconciliation;
* approval invalidation;
* output supersession;
* audit history.

### C. Current milestone

Please determine:

* whether this capability is required for the current E2E product demonstration;
* whether its absence creates a genuine current product blocker;
* whether the existing roadmap deferral remains architecturally sound.

## 9.3 Required Architect response

Please return:

1. Product interpretation
2. Intended lifecycle
3. Current architectural support
4. Actual gap
5. Gap classification
6. Existing architecture to preserve
7. Data/version implications
8. State-transition implications
9. Downstream observation/commentary/approval/output implications
10. E2E impact
11. Options/trade-offs
12. Architect recommendation
13. Whether current implementation is required
14. If deferred, recommended roadmap position
15. Any architectural decision that must be made now to avoid future rework

---

# 10. Cross-Cutting Architectural Questions

Across all four gaps, please identify any common architectural concern.

In particular:

## 10.1 Product state

Does the current product have a sufficiently explicit state model connecting:

**Dataset → Imported → Validated → Associated with Period → Processed → Reviewed → Approved → Closed → Archived**

and, where applicable:

**Closed → Reopened → Corrected/Replaced → Reprocessed → Reviewed → Approved → Closed**

?

If not, identify precisely what is missing.

## 10.2 Data versioning

Where processing, commentary, validation or outputs depend on a particular dataset/rule version, is that relationship preserved?

## 10.3 Observations

Does the current architecture support observations at the required business granularity without assuming that every analytical problem is naturally represented as Department × Category?

## 10.4 Configuration

Does the architecture distinguish:

* business policy;
* analytical definition;
* technical implementation?

## 10.5 Outputs

Are HTML and PPTX outputs treated as product artefacts with:

* period association;
* version;
* storage;
* current/superseded state;
* rerun behaviour;
* history?

## 10.6 Auditability

Where a user or system action changes financial workflow state, is the necessary history preserved?

---

# 11. Required Architect Decision Format

Please respond to each gap using the following structure.

## Gap [N] — [Name]

### 1. Product interpretation

What should the product actually do?

### 2. Current capability

What does the existing architecture and implementation already support?

### 3. Actual gap

What is genuinely missing or unclear?

### 4. Gap classification

Classify the issue.

### 5. Existing architecture to preserve

What should not be changed?

### 6. Architectural implications

What architecture, data, workflow or lifecycle consequences exist?

### 7. Dependencies

What other product capabilities or decisions depend on this?

### 8. Options and trade-offs

What reasonable approaches exist?

### 9. Architect recommendation

What does the Architect recommend?

### 10. E2E impact

Does this affect the current E2E product demonstration? If yes, how?

### 11. Verification impact

Does this affect independent verification or D13? If yes, explain precisely.

### 12. Implementation requirement

Is Builder implementation actually required?

### 13. If implementation is required

What must be defined before the Builder receives a task?

### 14. If implementation is not required

Should the issue be:

* accepted as-is;
* documented;
* deferred;
* converted into a future roadmap item;
* or escalated for Principal decision?

---

# 12. Decision Sequence

The intended sequence is:

**1. Architect review**

Architect provides:

* interpretation;
* classification;
* architectural consequences;
* options;
* recommendation;
* dependencies;
* what requires Principal approval;
* what can legitimately be deferred.

**2. PM challenge**

The PM challenges the interpretation against:

* intended Controller workflow;
* product journey;
* roadmap;
* E2E milestone;
* operability;
* evidence;
* risk of unnecessary implementation.

**3. Principal decision**

Where a product, scope or strategic decision is required, the Principal decides.

**4. Builder authorization**

Only after the above steps does the PM prepare a Builder package.

Builder receives:

* precise scope;
* acceptance criteria;
* dependencies;
* evidence requirements;
* explicit exclusions;
* regression expectations.

**5. Independent validation**

Implementation is independently tested against the intended capability.

**6. PM reconciliation**

The PM determines whether the resulting capability actually closes the product gap and updates:

* roadmap;
* status;
* risks;
* governance/process lessons;
* next milestone.

---

# 13. Explicit Non-Goals

This package does **not** authorize:

* creation of a settings screen;
* creation of a period-management screen;
* redesign of the dashboard;
* redesign of Phase 4–6;
* changes to the observation model;
* changes to established analytical definitions;
* implementation of reopen/correction;
* changes to established architecture;
* creation of Builder tasks without further approval.

These may become appropriate outcomes of the Architect's analysis, but they must not be assumed in advance.

---

# 14. Evidence Standard

Please distinguish clearly between:

* capability demonstrated in the canonical product;
* architecture/documentation describing intended capability;
* implementation evidence;
* regression tests;
* independent verification;
* live product demonstration;
* PM inference.

In particular:

* Builder tests are not automatically independent verification.
* Test doubles are not evidence of live AI behaviour.
* Code existence is not evidence of product operability.
* Documentation describing intended behaviour is not evidence that the workflow is operational.
* One mechanism proving one part of a workflow does not prove the complete workflow.

---

# 15. Expected Outcome

The desired outcome of this review is **not four new Builder tasks**.

The desired outcome is a clear decision map:

| Gap                         | What is actually wrong? | What is already supported? | Decision needed?      | Current milestone?                           | Implementation?        |
| --------------------------- | ----------------------- | -------------------------- | --------------------- | -------------------------------------------- | ---------------------- |
| 1. Latest period            | Architect to determine  | Architect to determine     | Architect to identify | Architect to assess                          | Architect to determine |
| 2. Phase 4–6 visibility     | Architect to determine  | Architect to determine     | Architect to identify | Architect to assess                          | Architect to determine |
| 3. Rules/thresholds         | Architect to classify   | Architect to determine     | Potentially           | Architect to assess                          | Architect to determine |
| 4. Closed-period correction | Architect to determine  | Architect to determine     | Scope/roadmap         | Likely future unless evidence says otherwise | Architect to determine |

The PM will then use this decision map to establish the next product milestone.

---

# 16. Final Instruction to Architect

Please treat this package as an **architectural clarification request**, not an implementation brief.

For each issue:

> **Interpret first. Classify second. Identify architectural consequences third. Recommend fourth. Implement only if the resulting decision requires it.**

The objective is to make the product more coherent and operable while preserving sound existing architecture and avoiding implementation driven solely by the discovery of a gap.

The central question is:

> **What must be true for the CFO product to provide a coherent, understandable and verifiable workflow from setup through executive output?**

The answer—not the existence of a missing file, screen or code path—should determine the next Builder task.
