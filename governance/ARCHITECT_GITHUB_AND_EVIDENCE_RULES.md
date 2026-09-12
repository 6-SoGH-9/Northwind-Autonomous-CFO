# ARCHITECT GITHUB AND EVIDENCE RULES

## 1. CANONICAL SOURCE OF TRUTH

For the Northwind Autonomous CFO project:

> GitHub `main` is the canonical source of truth for project state and implementation.

---

# 2. REQUIRED REPOSITORY IDENTIFICATION

Before material implementation or scope conclusions, identify:

- repository;
- branch;
- HEAD SHA;
- `origin/main` SHA;
- working-tree status.

If they differ, state the difference.

---

# 3. TEST CODESPACE IS NOT CANONICAL

The Test Codespace exists for implementation and testing.

It may contain:

- Builder changes;
- patches;
- temporary fixtures;
- datasets;
- generated files;
- experimental implementation.

None of these become project truth merely because they exist in the Test Codespace.

---

# 4. PATCHES ARE NOT IMPLEMENTATION

A patch demonstrates proposed or tested work.

It does not prove that the same work exists in canonical `main`.

Always distinguish:

> PATCHED / TESTED

from:

> CANONICAL / COMMITTED

---

# 5. BUILDER REPORTS ARE NOT EVIDENCE BY THEMSELVES

A Builder statement such as:

> "Implemented."

is not sufficient evidence.

The Architect must verify:

- actual files;
- actual code;
- actual integration;
- actual UI behavior where applicable;
- actual persistence;
- actual tests.

---

# 6. COMPONENT VS PRODUCT EVIDENCE

Evidence must be classified.

### Component evidence

A function/class/module works.

### Integration evidence

Components interact correctly.

### Persistence evidence

The state survives restart/session loss.

### UI evidence

A real user can invoke the capability.

### Product evidence

The complete intended business operation works end-to-end.

Do not describe component evidence as product evidence.

---

# 7. CURRENT EVIDENCE REQUIREMENT

Previous Architect conclusions do not constitute current verification.

When reviewing current implementation:

1. inspect current canonical `main`;
2. identify current commit;
3. inspect actual code;
4. inspect relevant tests;
5. test live behavior where necessary.

---

# 8. PRODUCT OPERABILITY REQUIREMENT

For a user-facing capability, the final question is:

> Can the intended user perform the intended business operation in the actual product without developer intervention?

If NO:

The capability is not product-complete.

---

# 9. STATE AND PERSISTENCE

Session state is not automatically durable state.

If a business decision is intended to survive:

- browser refresh;
- Streamlit rerun;
- application restart;
- new session;

the Architect must verify durable persistence.

---

# 10. END-TO-END CLAIM

The Architect may only use:

> VERIFIED

when evidence supports the exact claim being made.

For example:

> `archive_close()` exists

does NOT prove:

> Approve Close archives the close.

The second claim requires live integration evidence.

---

# 11. REQUIRED TRACE

For material product capability:

Principal decision
→ canonical governance
→ Builder Brief
→ code
→ UI
→ integration
→ state transition
→ persistence
→ downstream behavior
→ user verification.

Any broken link must be reported.

---

# 12. FINAL EVIDENCE RULE

When evidence conflicts with documentation:

Do not silently choose one.

Report:

> DOCUMENTATION / IMPLEMENTATION DRIFT IDENTIFIED

Then identify the appropriate authority and required correction.