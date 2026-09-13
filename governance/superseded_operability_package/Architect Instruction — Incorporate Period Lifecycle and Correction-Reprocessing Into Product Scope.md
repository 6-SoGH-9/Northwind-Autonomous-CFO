# Architect Instruction — Incorporate Period Lifecycle and Correction/Reprocessing Into Product Scope

## 1. Principal Scope Decision

The Principal has decided that the following capability is part of the intended product scope.

Do **not** treat this as merely an optional future idea, exploratory requirement, or deferred capability.

The product must support a complete, user-operable, versioned close lifecycle in which the Principal can:

- explicitly select the period to be closed;
- close that selected period;
- reopen a previously closed period through a controlled two-step validation process;
- cancel the reopen process at either step without changing the persistent close state;
- abandon the session before final reopen confirmation without reopening the period;
- correct/reload data for the reopened period;
- provide new commentary for the corrected version;
- create a new version of the close rather than overwrite the previous close;
- preserve the original close and its complete historical lineage;
- propagate the correction/dependency to subsequent closed periods;
- require affected subsequent periods to be reprocessed in chronological order;
- block a later affected period while an earlier affected period remains unresolved;
- require downstream reprocessing even where the downstream numbers ultimately do not change;
- distinguish dependency/reprocessing impact from actual numerical impact;
- make the resulting dependency, blocking, correction and reprocessing state visible in Close Validation Status.

This is now a **Principal-approved product requirement**.

The Architect must therefore not reject this requirement solely because an earlier Builder Brief classified reopen/correction/reprocessing as deferred.

If an earlier document or Brief conflicts with this new Principal decision, identify the conflict explicitly and recommend the necessary governance/document amendment.

---

# 2. Required Architect Action Before Builder Brief

Do **not** immediately write the Builder Brief.

First perform an authorization and governance reconciliation.

Determine:

1. Which existing requirements already authorize this capability.
2. Which existing requirements were previously deferred and are now superseded by the Principal's decision.
3. Which governance documents, Decision Log entries, Handbook sections, architecture documents, or other canonical project records need to be updated.
4. Whether any existing active Builder Brief must be formally amended, superseded, or replaced.
5. Whether any part of the requested capability still requires a separate explicit Principal decision.
6. Exactly what changes the Principal must make in the repository before implementation can be authorized.

Do not use the absence of a requirement from an existing Builder Brief as evidence that the Principal has not decided it.

The Principal has now explicitly decided that this capability belongs in the product scope.

---

# 3. Decision 1 — Approval Must Create a Durable Historical Close

The existing product requirement is that a successful close approval becomes a durable historical close.

Therefore the live workflow must ultimately provide:

**Approve Close**
→ durable approval state
→ archive the approved close
→ immutable Close History snapshot
→ historical close becomes selectable
→ persisted observations/commentary/analytical-definition metadata can be reviewed.

The Architect must determine the safest implementation and governance amendment required to connect the existing Human Approval Gate to the existing `archive_close()` mechanism.

The current existence of `archive_close()` is not sufficient.

The acceptance criterion is the actual user journey through the live application.

A direct test-script invocation of `archive_close()` must not be treated as equivalent to live approval-to-archive integration.

---

# 4. Explicit Period Selection

The product must allow the user to explicitly select the period that they intend to close.

The selected period must be authoritative for the close workflow, including:

- validation;
- observations;
- commentary;
- approval;
- versioning;
- archival;
- Close History;
- downstream dependency tracking.

The Architect must verify that no independent “latest period” resolution silently overrides the user's selected period.

The Architect must identify and resolve any existing architecture where the sidebar period selector is merely an explorer while Phase 3 independently selects `period_order[-1]`.

---

# 5. Closed Periods Cannot Simply Be Closed Again

Once a period has been successfully closed, the user must not simply run the ordinary close process against that period as though it were still open.

A previously closed period requires the controlled **reopen/correction lifecycle**.

The original close must remain intact.

---

# 6. Two-Step Reopen Validation

Reopening a closed period requires two explicit validation/confirmation steps.

### Step 1 — Reopen Request / Consequence Review

The system must clearly show:

- which period is being reopened;
- why the period is being reopened;
- that the existing close will remain preserved;
- that reopening will create a new version;
- which downstream periods may become affected;
- the consequences of proceeding.

The user must be able to:

**Cancel** or **Continue**.

If Cancel is selected:

- no persistent state changes;
- the period remains Closed;
- the original close remains untouched.

### Step 2 — Final Reopen Confirmation

The system must again show the consequences, including:

- downstream periods affected;
- required reprocessing sequence;
- any blocking consequences;
- preservation of the original version;
- creation of a new version.

The user must be able to:

**Cancel** or **Confirm Reopen**.

If Cancel is selected:

- no persistent reopen occurs;
- the period remains Closed;
- the original close remains untouched.

If the user leaves the session before final confirmation:

- the period remains Closed;
- the reopen has not occurred;
- no partial persistent reopen state may exist.

The Architect must treat this as a transactional boundary.

---

# 7. Versioning

When a closed period is reopened and corrected, the system must create a new version.

Example:

**Q3 2025 v1 — Closed**

becomes:

**Q3 2025 v1 — preserved historical version**

and:

**Q3 2025 v2 — corrected/reprocessed close**

The system must never overwrite v1.

The new version must have its own:

- data;
- observations;
- commentary;
- validation results;
- approval;
- analytical-definition attribution;
- archival metadata;
- lineage to the previous version;
- correction/reopen provenance.

The Architect must define the minimum durable lineage required to make this auditable.

---

# 8. Downstream Propagation

A correction to a historical closed period propagates a dependency to subsequent periods.

Example:

**Q3 2025 v1 → Q4 2025 v1 → Q1 2026 v1**

If Q3 is corrected:

**Q3 2025 v2**

then:

**Q4 2025 v1 → Reprocessing Required**

and subsequently:

**Q1 2026 v1 → Blocked / Reprocessing Required**

The downstream requirement exists even if the later period's numerical results ultimately do not change.

Therefore the system must distinguish:

1. **Correction source**
   - e.g. Q3 2025

2. **Dependency / reprocessing impact**
   - e.g. Q4 2025 requires reprocessing

3. **Numerical impact**
   - e.g. Q4 2025 numerical impact = None

A period can therefore legitimately be:

**Reprocessed = Yes**  
**New Version = Yes**  
**Numerical Impact = None**

These are different concepts and must not be collapsed into one anomaly/impact flag.

---

# 9. Chronological Reprocessing and Blocking

Downstream affected periods must be reprocessed in chronological order.

For example:

Q3 correction  
↓  
Q4 reprocessing required  
↓  
Q1 blocked until Q4 is resolved.

The user must not be able to close Q1 while Q4 remains unresolved.

After Q4 is successfully reprocessed and closed:

Q1 becomes eligible for reprocessing.

The Architect must determine how this dependency state is persisted and enforced.

This must not be merely a visual warning.

The workflow must actually prevent an invalid downstream close.

---

# 10. Close Validation Status

The dependency state must be visible in the product.

For example:

**Q3 2025**
- Correction / reclose in progress

**Q4 2025**
- Reprocessing required — affected by Q3 2025 correction

**Q1 2026**
- Blocked — Q4 2025 must be reprocessed first

The exact UI design is for the Architect/Builder to determine, but the business meaning must remain explicit.

The user must not have to inspect source code or filesystem state to understand:

- which period was corrected;
- which periods are affected;
- which period must be processed next;
- why a period is blocked;
- whether numerical impact exists;
- which version is currently active.

---

# 11. Close History and Lineage

Close History must support the resulting versioned lifecycle.

A historical review must allow the user to distinguish:

- period;
- version;
- original close;
- corrected close;
- correction source;
- reprocessing status;
- numerical impact;
- approval state;
- archival state.

The original close must remain reviewable.

The new version must be separately reviewable.

The lineage between versions must be inspectable.

---

# 12. Product-Operability Requirement

The Architect must evaluate the complete capability as a real user workflow.

The required chain is:

**Select Period**
→ **Validate**
→ **Generate Observations**
→ **Enter/Review Commentary**
→ **Approve**
→ **Archive**
→ **Close History**

and, when correction is required:

**Select Closed Period**
→ **Step 1 Reopen Validation**
→ **Cancel or Continue**
→ **Step 2 Final Confirmation**
→ **Cancel or Confirm**
→ **New Version**
→ **Correct Data**
→ **New Commentary**
→ **Reprocess**
→ **Approve**
→ **Archive**
→ **Propagate Dependency**
→ **Block Later Periods Until Predecessor Is Resolved**

The Architect must not consider the capability complete merely because individual functions exist.

The complete user journey must work through the live application with durable state.

---

# 13. Required Architect Deliverable

Before producing an updated Builder Brief, return a reconciliation covering:

### A. Principal authorization

Confirm that the above requirements are now treated as Principal-approved product scope.

### B. Existing governance

Identify every existing requirement that:

- already supports this;
- conflicts with it;
- previously deferred it;
- needs amendment;
- needs supersession.

### C. Required repository updates

Tell the Principal exactly which canonical documents must be updated before implementation begins.

Do not ask the Principal to guess what needs changing.

### D. Architecture

Explain the proposed durable state model for:

- periods;
- close versions;
- reopen state;
- approval;
- archival;
- dependency propagation;
- reprocessing;
- blocking;
- numerical impact;
- lineage.

### E. Integration

Identify every required integration between:

- period selection;
- validation;
- observations;
- commentary;
- approval;
- archive;
- Close History;
- correction;
- versioning;
- downstream dependency handling;
- Close Validation Status.

### F. Testability

Define the end-to-end test scenarios required to prove the capability.

At minimum include:

1. normal close of a selected period;
2. approval creates durable Close History;
3. review of a prior close;
4. reopen Step 1 → Cancel;
5. reopen Step 2 → Cancel;
6. abandon session before final confirmation;
7. confirmed reopen;
8. correction creates v2 without modifying v1;
9. new commentary belongs to v2;
10. downstream period becomes reprocessing-required;
11. downstream period is reprocessed even with no numerical change;
12. later period remains blocked while predecessor is unresolved;
13. chronological dependency is enforced;
14. Close Validation Status displays the dependency chain;
15. historical versions remain reviewable.

---

# 14. Builder Brief

Only after the above reconciliation is complete and the necessary Principal/governance updates have been identified and recorded should the Architect produce the updated Builder Brief.

The Builder Brief must then implement the **entire authorized product capability**, not merely isolated mechanisms.

The Architect must not silently reduce the scope to:

- “period selector” only;
- “reopen button” only;
- “archive function” only;
- “version field” only;
- “dependency flag” only.

Those are implementation components.

The authorized scope is the complete operational lifecycle.

---

# 15. Final Architect Question

Before declaring the work ready for Builder implementation, answer:

> If the Principal opens the canonical application as an ordinary user, can the Principal select a specific period, close it, approve it, see it durably archived, later reopen it through the two-step confirmation process, cancel safely at either stage, create a corrected new version without destroying the original, provide new commentary, propagate the correction to downstream periods, force chronological reprocessing, block later periods until earlier affected periods are resolved, distinguish reprocessing impact from numerical impact, and see all of this clearly in Close Validation Status and Close History?

If the answer is **No**, identify the exact missing capability and the exact governance or implementation step required to make it **Yes**.

Do not declare the product ready for Principal testing until the complete user journey is demonstrably implemented and independently verified.