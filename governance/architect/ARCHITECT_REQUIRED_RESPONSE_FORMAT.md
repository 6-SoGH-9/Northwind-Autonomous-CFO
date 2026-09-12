# ARCHITECT REQUIRED RESPONSE FORMAT

## Mandatory Use

Use this format for every material scope, authorization, dependency, governance, or requirements-preservation question.

Do not provide an informal alternative response.

---

# 1. REQUIREMENT

State exactly what the Principal is asking for.

Separate:

- explicit requirement;
- implied requirement;
- assumptions.

Do not silently add assumptions to the requirement.

---

# 2. EXISTING AUTHORITY

Identify the authoritative source.

For each relevant requirement provide:

- document;
- section;
- decision/reference;
- exact relevant wording or precise summary.

Classify the authority:

- Principal decision;
- Handbook;
- Decision Log;
- Product Operability Charter;
- Builder Brief;
- other governance;
- historical/superseded.

---

# 3. CLASSIFICATION

Classify every material requirement:

- A — Already Authorized
- B — New Principal Decision
- C — Genuine Conflict
- D — Technical/Procedural Constraint
- E — Architect Recommendation

Explain each classification.

---

# 4. SUPERSEDED / DEFERRED DECISIONS

Identify any earlier decision that appears relevant.

For each:

- what was previously decided;
- whether it was deferred;
- whether the Principal has subsequently changed it;
- whether it remains authoritative.

A previous deferral is not permanent if the Principal subsequently makes a contrary decision.

---

# 5. GENUINE CONFLICTS

Identify only actual conflicts.

Do not manufacture a conflict from:

- missing Brief content;
- technical inconvenience;
- preferred architecture;
- future-proofing;
- rework avoidance.

If no genuine conflict exists, state:

> No genuine conflict identified.

---

# 6. GOVERNANCE CHANGES REQUIRED

Identify documentation changes required to accurately record the Principal's decision.

Separate:

### Documentation correction

Required because existing authorization was omitted or inaccurately represented.

### New authorization

Required because the Principal genuinely introduced new scope.

### Implementation work

Separate from governance synchronization.

---

# 7. ARCHITECTURE IMPACT

Describe architecture implications.

Clearly distinguish:

- required by authorized scope;
- technically necessary;
- recommended;
- future.

Do not turn recommendations into requirements.

---

# 8. IMPLEMENTATION IMPACT

Describe the smallest implementation necessary to satisfy the authorized requirement.

Do not write a full implementation specification unless that is explicitly the task.

Do not introduce unapproved schemas, storage models, redesigns, or new capabilities as mandatory scope.

---

# 9. TESTING IMPACT

State:

- what must be tested;
- what user operation must work;
- what persistence must be verified;
- what integration must be verified;
- what evidence proves completion.

Distinguish:

### Component test

A component works in isolation.

### Integration test

Components interact correctly.

### Product test

A real user can perform the intended operation.

---

# 10. DEPENDENCIES AND BLOCKING

For every claimed dependency:

1. State the dependency.
2. Explain why it exists.
3. Apply the Minimum-Scope Test.
4. Identify a workaround if one exists.
5. State whether the workaround satisfies existing requirements.
6. Explain whether the dependency is genuinely blocking.

Do not use "hard dependency" as a conclusion without evidence.

---

# 11. SEQUENCING RECOMMENDATION

Recommend implementation order.

Separate:

- required sequence;
- convenient sequence;
- optional bundling.

If two items can be implemented independently, do not present them as mandatory bundle.

---

# 12. READY FOR BUILDER BRIEF?

Choose exactly one:

### YES — READY

The scope is authorized, correctly translated, dependencies are understood, and the Builder Brief can accurately represent it.

### NO — GOVERNANCE CORRECTION REQUIRED

An existing authorized requirement is missing or incorrectly represented.

### NO — PRINCIPAL DECISION REQUIRED

A genuinely new decision or genuine conflict remains unresolved.

### NO — TECHNICAL BLOCKER

A demonstrated technical blocker prevents correct implementation and no compliant workaround exists.

### NO — EVIDENCE INSUFFICIENT

The Architect cannot establish the required facts from canonical evidence.

---

# ARCHITECT ATTESTATION

I confirm that:

- I reviewed the relevant canonical governance.
- I checked the canonical repository state.
- I classified the scope.
- I separated requirements from recommendations.
- I performed the Minimum-Scope Test where applicable.
- I did not silently expand or narrow Principal-authorized scope.
- I did not use a missing Builder Brief item as evidence that the requirement was unauthorized.
- I did not convert an Architect recommendation into mandatory scope.
- I have identified all remaining decisions or blockers.

Architect: __________________

Date: __________________
