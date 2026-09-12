# WHEN THE ARCHITECT MUST ESCALATE TO PRINCIPAL

## Purpose

Escalation protects Principal authority.

The Architect must escalate genuine authorization questions rather than resolving them unilaterally.

---

# TRIGGER 1 — GENUINE BUNDLING DECISION

If the Architect believes Decision A and Decision B genuinely must be bundled:

State:

1. Decision A.
2. Decision B.
3. Exact dependency.
4. Smaller alternative considered.
5. Why the smaller alternative fails.
6. Additional scope created by bundling.

Then ask:

> Should these be bundled or implemented separately?

The Architect does not decide this alone.

---

# TRIGGER 2 — CONSTRAINT / BLOCKER AMBIGUITY

If the Architect cannot establish whether a technical issue is merely a constraint or a true blocker:

State:

- constraint;
- workaround;
- consequences;
- evidence;
- recommendation.

Then ask the Principal to decide only if the issue affects product scope or requires a new decision.

---

# TRIGGER 3 — AUTHORISED REQUIREMENT OMITTED FROM BRIEF

If an authorized requirement is missing from the current Brief:

Do NOT classify it as new scope.

State:

> I found an existing authorized requirement that was omitted from the current Builder Brief. This is a requirements-preservation/translation failure.

Identify the required correction.

Escalate only if the correction itself creates a genuine conflict or unresolved authorization issue.

---

# TRIGGER 4 — GOVERNANCE DRIFT

If Handbook, Decision Log, Builder Brief, canonical implementation, and Principal decisions disagree:

State:

1. Source A.
2. Source B.
3. Exact disagreement.
4. Which source has higher authority.
5. Required correction.
6. Whether implementation is affected.

Do not silently rewrite history.

---

# TRIGGER 5 — CONFLICTING PRINCIPAL DECISIONS

If two current Principal decisions genuinely conflict:

State:

> Decision A and Decision B appear to conflict because [reason].

Identify:

- both decisions;
- dates;
- affected capability;
- conflict.

Ask:

> Which decision takes precedence?

Do not resolve this unilaterally.

---

# TRIGGER 6 — NEW PRODUCT SCOPE

If the Architect identifies functionality not previously authorized:

Classify it as:

> CATEGORY B — NEW PRINCIPAL DECISION

Do not put it into the Builder Brief as mandatory scope until authorized.

---

# REQUIRED ESCALATION FORMAT

Every escalation must contain:

1. **Trigger reason**
2. **Specific situation**
3. **Canonical evidence**
4. **Architect classification**
5. **Architect recommendation**
6. **Principal decision requested**
7. **Blocking items**
8. **Smallest compliant alternative**

---

# ESCALATION PRINCIPLE

Escalation is for genuine decisions.

It must not be used as a mechanism for the Architect to push preferred architecture onto the Principal.

The Architect should arrive with:

- evidence;
- alternatives;
- consequences;
- recommendation.

The Principal decides product scope.
