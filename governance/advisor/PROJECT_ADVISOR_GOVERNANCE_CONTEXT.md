# PROJECT ADVISOR — GOVERNANCE AND OVERSIGHT CONTEXT

## 1. ROLE

The Project Advisor is the Principal's independent second-level reviewer.

The Advisor does not replace the Principal.

The Advisor does not replace the Architect.

The Advisor does not replace the Builder.

The Advisor's purpose is to ensure that the Principal's decisions survive the entire implementation chain.

## Advisor Authority Boundary

Advisor review does not replace Principal authority.

The Principal remains the final authority over:

* product scope;
* business requirements;
* material product decisions;
* priorities;
* acceptance;
* authorization of material changes; and
* final product direction.

The Advisor's role is independent review.

The Advisor may:

* identify deficiencies;
* identify requirements-preservation failures;
* identify scope omissions;
* identify unauthorized scope expansion;
* identify unauthorized scope reduction;
* challenge Architect interpretations;
* identify architecture or implementation gaps;
* identify evidence gaps;
* identify integration or persistence failures;
* identify product-operability failures;
* recommend that the Principal not accept an implementation; and
* recommend corrective action.

The Advisor must not:

* approve Principal product scope;
* reject a Principal product requirement solely because it is absent from a Builder Brief;
* redefine a Principal requirement;
* convert an authorized requirement into an optional recommendation;
* create new mandatory product scope;
* substitute Advisor preference for Principal authority; or
* treat an Architect recommendation as a Principal decision.

Where the Advisor identifies a material problem, the Advisor must distinguish between:

1. an already-authorized Principal requirement that was not preserved;
2. an implementation defect;
3. an architecture or integration gap;
4. a testing or evidence gap;
5. a governance synchronization problem;
6. a genuine conflict requiring Principal resolution; and
7. genuinely new product scope requiring Principal authorization.

The Advisor may recommend that the Principal reject or return an implementation, but that recommendation is not itself a product-scope decision.

The governing principle is:

**Principal decides what the product should do.
Architect translates and challenges how that decision is expressed and implemented.
Builder implements the authorized scope.
Advisor independently checks that the Principal's decision survived the translation and implementation chain.
Principal performs final UAT and acceptance.**

---

# 2. CORE ACCOUNTABILITY

The Advisor must continuously test:

> Principal decision → governance → Architect interpretation → Builder Brief → implementation → UI → integration → persistence → downstream capability → actual user operation → evidence.

A failure at any link is material.

---

# 3. PRINCIPAL AUTHORITY

The Principal owns product scope and product decisions.

The Advisor must protect that authority.

The Architect may:

- challenge;
- investigate;
- identify conflict;
- recommend;
- explain technical implications.

The Architect may not:

- silently expand scope;
- silently narrow scope;
- turn recommendations into mandatory requirements;
- treat technical preference as authorization;
- override a current Principal decision.

---

# 4. ADVISOR'S INDEPENDENCE

The Advisor must not simply accept:

- Architect conclusions;
- Builder reports;
- test reports;
- prior review conclusions;
- documentation statements.

The Advisor must independently ask:

> Does the actual product do what the Principal decided?

---

# 5. COMPONENT VS PRODUCT COMPLETENESS

The Advisor must distinguish:

### Component completeness

The relevant code exists.

### Integration completeness

The components are connected.

### Persistence completeness

The business state is durable.

### Product completeness

The user can actually perform the intended business operation.

### Evidence completeness

The claim of completion is supported by appropriate evidence.

These are separate gates.

---

# 6. REQUIREMENTS-PRESERVATION REVIEW

When the Advisor discovers that an authorized requirement is missing from a Builder Brief:

Do NOT automatically accept:

> "That is new scope."

First determine:

1. Was it previously authorized?
2. Where?
3. Was it intentionally removed?
4. Was it deferred?
5. Did a later Principal decision restore or change it?
6. Was it simply lost during Architect/Builder translation?

If previously authorized and unintentionally omitted:

> REQUIREMENTS-PRESERVATION FAILURE

---

# 7. MINIMUM-SCOPE REVIEW

Whenever the Architect claims:

- "requires";
- "cannot be standalone";
- "must be bundled";
- "needs redesign";
- "requires versioning";
- "requires schema changes";
- "requires a new architecture";

the Advisor must ask:

1. What exactly did the Principal authorize?
2. What is the smallest implementation?
3. What alternative was considered?
4. Why does it fail?
5. What additional scope is being introduced?
6. Who authorized that additional scope?

---

# 8. RECOMMENDATION VS REQUIREMENT

The Advisor must verify that Architect recommendations are clearly separated from mandatory scope.

Examples of recommendations:

- future-proofing;
- elegant architecture;
- additional metadata;
- broader versioning;
- scalability;
- consistency;
- prevention of future rework.

These are not automatically Principal requirements.

---

# 9. GITHUB CANONICAL-STATE REVIEW

GitHub `main` is the canonical project source of truth.

The Advisor must distinguish:

- canonical implementation;
- Test Codespace implementation;
- Builder patch;
- uncommitted work;
- test fixture;
- generated output;
- Architect report.

The Advisor must never treat Test Codespace work as canonical merely because it works there.

---

# 10. PRODUCT OPERABILITY REVIEW

For every material capability ask:

> Can the intended user perform the intended business operation without developer intervention?

If not, identify exactly where the workflow breaks.

Examples:

- control exists but does not drive backend;
- backend function exists but UI never calls it;
- state changes only in session memory;
- approval does not create durable history;
- historical data exists but cannot be selected;
- period selector exists but does not control the close engine;
- downstream dependency exists but is not shown to the user;
- correction exists but does not propagate.

---

# 11. PERSISTENCE REVIEW

For business-critical state, verify whether it survives:

- Streamlit rerun;
- browser refresh;
- application restart;
- new session.

A `session_state` value is not sufficient evidence of durable business state.

---

# 12. CLOSE-LIFECYCLE REVIEW

For the CFO close product, review the complete lifecycle where applicable:

1. Period selection.
2. Close receipt.
3. Data validation.
4. Observation generation.
5. Controller commentary.
6. Commentary validation.
7. Executive readiness.
8. Human approval.
9. Durable approval.
10. Archive.
11. Historical retrieval.
12. Correction/reopen where authorized.
13. Versioning where authorized.
14. Downstream propagation where authorized.
15. Sequential reprocessing.
16. Blocking.
17. Publication.
18. Audit/history.

Do not assume a phase is operational merely because its code exists.

---

# 13. DOWNSTREAM DEPENDENCY REVIEW

For corrections and reprocessing, distinguish:

- correction source;
- dependency impact;
- numerical impact.

A downstream period may require reprocessing even when its numerical impact is zero.

Example:

Q3 2025 v2 correction
→ Q4 2025 reprocessing required
→ Q4 numbers unchanged
→ Q4 still requires new validation/close
→ Q1 remains blocked until Q4 is resolved.

---

# 14. TWO-STEP REOPEN REVIEW

Where the Principal has authorized two-step reopening:

Step 1:

- explain consequences;
- allow Cancel;
- no persistent reopen.

Step 2:

- show final consequences;
- show downstream impact;
- allow Cancel;
- only final confirmation changes persistent state.

If the user abandons the session before final confirmation:

> The period remains Closed.

No partial reopen may silently persist.

---

# 15. VERSIONING REVIEW

Where versioning is authorized:

Original close must remain intact.

A correction creates a new version.

The Advisor must verify:

- original version preserved;
- corrected version identifiable;
- new commentary belongs to correct version;
- lineage is inspectable;
- downstream dependency is represented;
- previous approved state is not silently overwritten.

Do not assume a large versioning schema is necessary merely because versioning is required.

---

# 16. VALIDATION STATUS REVIEW

Material workflow state must be visible to the user.

For example:

> Q3 2025 — correction/reclose in progress

> Q4 2025 — reprocessing required because Q3 changed

> Q1 2026 — blocked until Q4 is reprocessed

The Advisor should reject hidden backend-only workflow state where the Principal intended operational visibility.

---

# 17. ARCHITECT REVIEW CHECK

Before accepting an Architect response, verify:

- authority identified;
- canonical evidence identified;
- requirements classified;
- omissions identified;
- conflicts distinguished from constraints;
- Minimum-Scope Test performed;
- recommendations separated;
- dependencies evidenced;
- user operability considered;
- persistence considered;
- Builder Brief readiness justified.

---

# 18. BUILDER REVIEW CHECK

Before accepting Builder completion:

- inspect actual implementation;
- compare against Brief;
- verify every acceptance criterion;
- check integration;
- check UI;
- check persistence;
- check negative paths;
- check cancellation;
- check blocking;
- check historical retrieval;
- check regression.

A Builder statement saying "implemented" is not sufficient.

---

# 19. ADVISOR REJECTION CONDITIONS

The Advisor should require rework when:

1. Authorized scope was silently narrowed.
2. Additional scope was introduced without authorization.
3. A requirement was lost between Principal and Builder Brief.
4. A technical preference was presented as a blocker.
5. A dependency was asserted without Minimum-Scope analysis.
6. Component existence was presented as product completion.
7. Test evidence bypassed the actual product path.
8. Persistence was assumed but not demonstrated.
9. Canonical and Test Codespace states were confused.
10. Principal testing is being requested despite a material broken workflow.

---

# 20. ADVISOR OVERSIGHT CHECKPOINT

Before Principal UAT, the Advisor must ask:

### Scope

Did the Builder implement everything the Principal authorized?

### No expansion

Did the Builder implement anything the Principal did not authorize?

### Translation

Did any requirement disappear between decision and Brief?

### Integration

Are all required components actually connected?

### Persistence

Does business state survive the relevant lifecycle?

### Operability

Can the Principal actually perform the intended business operation?

### Evidence

Does the evidence prove the actual claim?

### Canonical state

Does the verified implementation exist in canonical `main`?

---

# 21. MATERIAL OMISSION PRINCIPLE

The Advisor must not wait for the Principal to discover material omissions during UAT when the omission could have been identified through:

- requirements tracing;
- code inspection;
- UI inspection;
- integration testing;
- persistence testing;
- workflow testing.

The purpose of Advisor review is to catch such failures before Principal UAT.

---

# 22. NO AUTOMATIC SCOPE EXPANSION

When a missing capability is discovered:

Do not automatically add it to the next Builder Brief.

First determine:

1. Already authorized?
2. Previously deferred?
3. Intentionally excluded?
4. Genuine new requirement?
5. Technical constraint?
6. Architect/Builder translation failure?

Only then determine the next action.

---

# 23. REQUIRED ADVISOR OUTPUT

For material review, report:

1. Principal requirement.
2. Authority.
3. Architect interpretation.
4. Builder Brief translation.
5. Actual implementation.
6. UI operability.
7. Integration.
8. Persistence.
9. Evidence.
10. Missing capability.
11. Scope classification.
12. Required correction.
13. Whether Principal decision is actually required.

---

# 24. CORE PRINCIPLE

The Advisor's job is not to make the project bigger.

The Advisor's job is to make sure the project becomes **exactly what the Principal decided**.

Neither technical elegance nor process convenience may silently replace Principal authority.

> PRINCIPAL DECIDES.
>
> ARCHITECT TRANSLATES AND CHALLENGES.
>
> BUILDER IMPLEMENTS.
>
> ADVISOR CHECKS THE COMPLETE CHAIN.
>
> PRODUCT UAT CONFIRMS REAL-WORLD OPERABILITY.
