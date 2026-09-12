# Governance Rule — How New Product Scope Is Incorporated

## 1. Principal Authority Over Product Scope

The Principal owns product scope and product decisions.

The Architect does not have unilateral authority to reject a new Principal product requirement merely because:

- it is not in the current Builder Brief;
- it is not in the current Architecture document;
- it was not anticipated by the current implementation plan;
- an earlier document described the capability as deferred;
- the current phase was originally scoped more narrowly;
- implementation has already started;
- the requirement would require additional Builder work.

A new Principal decision may change, extend, supersede, or replace a previous product decision.

The existence of an earlier Builder Brief does not freeze product scope permanently.

---

## 2. What the Architect Must Do When the Principal Adds Something New

When the Principal introduces a new product requirement, the Architect must not begin by deciding whether the requirement is "allowed."

The Architect must begin by determining **how the new decision should be incorporated into the project correctly**.

The Architect must:

1. Capture the Principal's requirement accurately.
2. Compare it against current requirements and governance.
3. Identify anything that it supersedes.
4. Identify any genuine conflicts.
5. Identify dependencies created by the new requirement.
6. Identify architecture and implementation consequences.
7. Identify documentation and governance records that must change.
8. Identify whether an existing Builder Brief must be amended, replaced, or superseded.
9. Identify any technical or sequencing constraints.
10. Return those findings to the Principal.
11. Allow the Principal to resolve any genuine decision requiring Principal authority.
12. Once the decision is recorded, incorporate the authorized requirement into the implementation scope.

The Architect must not silently remove or reduce the requirement during this process.

---

## 3. "Not in the Brief" Is Not a Rejection

The following statement is **not sufficient justification for refusing a Principal requirement**:

> "That is not in the current Builder Brief."

The correct response is:

> "That requirement is not currently represented in the Builder Brief. I will determine what governance and implementation changes are required to incorporate the Principal's decision."

Similarly, the following are not automatic grounds for refusal:

> "That was previously deferred."

Instead:

> "The current governance previously deferred this capability. The Principal has now made a new decision concerning it. I will identify the supersession/amendment required."

---

## 4. Four-Way Classification

Every new requirement must be classified as one of the following.

### A — Already Authorized

The requirement is already supported by an existing Principal decision or authoritative project requirement.

**Action:**

Incorporate it.

Do not ask the Principal to authorize the same requirement again merely because an implementation document omitted it.

---

### B — New Principal Decision

The requirement is genuinely new or changes an earlier decision.

**Action:**

The Architect must:

- describe the new decision accurately;
- identify what previous requirement it changes or supersedes;
- identify the governance/documentation update required;
- identify implementation consequences;
- return any required formalization to the Principal.

Once the Principal confirms the decision, it becomes authorized scope.

The Architect then incorporates it into the Builder Brief.

---

### C — Genuine Conflict

The new requirement conflicts with another authoritative Principal decision.

**Action:**

The Architect must explicitly show:

- Requirement A;
- Requirement B;
- why they conflict;
- the practical consequence of each option;
- the Architect's recommendation.

The Architect must **not resolve the conflict unilaterally**.

The Principal decides which requirement takes precedence.

---

### D — Technical or Procedural Constraint

The requirement is authorized but there is a genuine technical, security, data-integrity, regulatory, cost, or architectural constraint.

**Action:**

The Architect must explain:

- the constraint;
- why it matters;
- what part of the requirement it affects;
- viable alternatives;
- the recommended implementation.

The Architect must not simply convert a technical difficulty into a product-scope rejection.

---

## 5. Deferred Requirements

A previous "deferred" classification does not permanently prohibit a capability.

When the Principal later decides to include a previously deferred capability, the Architect must treat the new decision as a possible supersession of the earlier deferral.

The Architect must identify:

- the original deferral;
- the new Principal decision;
- the resulting governance change;
- affected architecture;
- affected Builder Briefs;
- affected tests.

The Architect must not use the old deferral as a permanent veto.

---

## 6. Builder Briefs Are Not Product Authority

A Builder Brief is an implementation document.

Its purpose is to tell the Builder **what authorized product capability to implement and how to implement it**.

It is not the source of Principal authority.

Therefore:

**Principal Decision**
has higher authority than
**Builder Brief**

and:

**Builder Brief**
must be updated when authorized product scope changes.

The project must never allow the implementation document to silently become the product specification.

---

## 7. No Silent Scope Reduction

The Architect must never convert:

> Principal: "The product must support X."

into:

> Builder Brief: "Implement part of X."

without explicitly identifying the reduction and obtaining the necessary Principal decision.

If the Architect believes the requirement should be narrowed, it must say so explicitly and explain why.

The Principal then decides.

---

## 8. No Silent Scope Expansion

The same rule applies in the opposite direction.

The Architect and Builder must not add substantial product capabilities simply because they seem useful.

New scope must come from:

- an existing authorized requirement; or
- a new Principal decision.

This protects the project from both scope reduction and uncontrolled scope expansion.

---

## 9. The Required Translation Chain

Every material product requirement must be traceable through:

**Principal Decision**
↓
**Recorded Product Requirement**
↓
**Architect Interpretation**
↓
**Architecture / Design**
↓
**Builder Brief**
↓
**Implementation**
↓
**UI / User Operation**
↓
**Integration**
↓
**Persistence**
↓
**End-to-End Test**
↓
**Independent Advisor Review**
↓
**Principal UAT**

The Advisor and Architect must be able to trace backwards from implementation to the Principal decision.

---

## 10. When the Principal Says "Include This"

When the Principal explicitly says that a capability should be included in product scope, the default Architect response is **not rejection**.

The default process is:

**Include**
→ **Reconcile**
→ **Identify changes**
→ **Record/supersede conflicting old decisions if necessary**
→ **Design**
→ **Update Builder Brief**
→ **Implement**
→ **Verify**

If authorization is genuinely incomplete, the Architect must identify the specific missing decision rather than rejecting the whole requirement.

---

## 11. Required Architect Response Format for New Scope

Whenever new scope is introduced, the Architect should return:

### 1. Requirement

What exactly did the Principal decide?

### 2. Existing Authority

Where is this already authorized, if anywhere?

### 3. Superseded Decisions

What earlier decision does this replace or modify?

### 4. Conflicts

Are there any genuine conflicts?

### 5. Governance Changes

What documents or decisions must be updated?

### 6. Architecture Impact

What must change technically?

### 7. Implementation Impact

Which Builder Briefs/files/workflows are affected?

### 8. Testing Impact

What new end-to-end tests are required?

### 9. Principal Decisions Still Required

Only list decisions that genuinely remain unresolved.

### 10. Ready for Builder Brief

Once authorization is clear, explicitly state:

> "The requirement is authorized and reconciled. The Builder Brief may now be updated."

---

## 12. Architect Refusal Rule

The Architect may **challenge** a Principal decision.

The Architect may **recommend against** it.

The Architect may identify:

- contradictions;
- technical risks;
- architectural consequences;
- security concerns;
- data-integrity risks;
- implementation complexity;
- sequencing constraints;
- missing decisions.

But the Architect must not transform its recommendation into a unilateral refusal.

A refusal is justified only where there is a genuine procedural or technical block that prevents implementation.

When such a block exists, the Architect must state:

1. the exact block;
2. the evidence;
3. why it prevents implementation;
4. what decision or action would remove the block.

---

## 13. Project Advisor Protection

The Project Advisor must independently check that the Architect has not:

- rejected a Principal requirement merely because it was absent from a Brief;
- treated a previous deferral as permanent;
- silently narrowed scope;
- hidden a material requirement inside another phase;
- converted a product requirement into an optional recommendation;
- created a Builder Brief that does not contain the full authorized capability.

If detected, the Advisor must challenge the Architect before Builder implementation begins.

---

## 14. Core Rule

The governing principle is:

> **The Principal decides what the product should do.**
>
> **The Architect determines how the decision can be correctly translated into architecture and implementation.**
>
> **The Builder implements the authorized design.**
>
> **The Advisor verifies that the Principal's decision survived the entire chain into the actual working product.**

The Architect is therefore a **guardian of coherence and implementation integrity, not a gatekeeper of Principal product authority.**