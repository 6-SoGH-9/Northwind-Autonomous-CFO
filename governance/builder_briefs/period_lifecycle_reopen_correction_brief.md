# Builder Brief — Period Lifecycle, Reopen, and Correction/Reprocessing (D15)

**Version:** v2 — Builder-ready. **Supersedes `period_lifecycle_reopen_correction_brief_v1.md` in full.** v1 is retained for provenance only; v2 is the sole governing document for D15 implementation from this point forward. No Return Report exists against v1 (no implementation began), so this is a pre-implementation revision, not a mid-implementation scope change.
**Status:** Active
**Governs:** Decision Log D15 (Handbook v2.17)
**Governing authority, in order:** (1) Principal authorization, `architect_alignment_report_period_lifecycle_reopen_correction.md` Section A; (2) Final architecture, same report, Sections D.A–D.H; (3) Project Handbook v2.17; (4) this Brief.
**Repository identity:** per `project_handbook.md`'s "Repository Identity (standing context)" subsection — not restated here.
**Baseline commit this Brief was drafted against:** `575bab645810084a42fd36ed3c278d2741fd397e` (fresh clone, confirmed clean working tree).
**Concurrently active, non-overlapping Briefs:** `phase4_semantic_reconciliation_brief_v2.md`. `builder_brief_operability_gaps_1_2_3.md` remains active for **Gaps 2 and 3 only** — see Section 4 below for the explicit Gap 1 disposition.

**Purpose of this revision:** v1 left several coordination points as statements of intent rather than fixed requirements, and several open architectural questions without an explicit classification of who may resolve them. v2 corrects both. No Principal requirement, Final architecture decision, or Handbook v2.17 scope statement is changed, narrowed, or expanded by this revision — only precision and completeness.

**Post-review correction (same v2, Project Advisor review):** four wording-only fixes applied after Advisor review, no scope/architecture change: (1) Scenario 3's HTML/PPTX requirement corrected to remain intact per the Handbook's milestone-expansion decision, rather than reading as waived pending the open reuse-vs-own-output question (Section 7); (2) epsilon/tolerance classified precisely as "Builder proposes, Architect confirms" rather than "Builder implementation detail" (Section 4); (3) the independent-comparison rationale reworded to name `PL_Quarterly`/`BvA_Q` — the actual canonical comparison targets — rather than the raw `PL_Summary`/`Budget_vs_Actual` sheets, so Builder cannot read the raw sheets as separate comparison targets (Section 4, 5.E); (4) Section 12 item 15's self-certification softened from an absolute completeness claim to a checked-consistency claim.

---

## 1. Objective

Implement the complete, user-operable, versioned close lifecycle authorized as D15, such that after this Brief, Builder can implement without making any material product, lifecycle, integration, or scope decision on its own. Every ambiguity in v1 is resolved here or explicitly routed to the party who must resolve it.

## 2. Business Purpose

A Controller/CFO must be able to correct a previously closed period without destroying its audit history, without silently reopening unaffected downstream periods, and without the product misrepresenting a purely technical recalculation as a business-significant event.

---

## 3. Requirement-Preservation Matrix

| Principal requirement | Final architecture section | Builder Brief section | User-visible behavior | Persistence/state | Acceptance evidence |
|---|---|---|---|---|---|
| Authoritative period selection | D.B | 5.B | Explicit "Select period to close" control drives the entire close operation | `target_period` session value, consumed by every downstream call | 5.B acceptance: non-terminal period selection reflected end-to-end |
| Versioned close identity | D.A | 5.A | Close History shows v1, v2, ... per period | `close_history/{period_label}/v{n}/` | 5.A acceptance: `resolve_version()` round-trip |
| Two-step reopen, cancel/abandon-safe | D.C | 5.C | Step 1/Step 2 screens, Cancel at either, session abandonment | Zero persistent write until Step 2 confirmed | 5.C acceptance: `close_history/` untouched after cancel/abandon, live UI |
| Correction/reprocessing pipeline | Source instruction §7–9 | 5.D | New data + new commentary intake for reopened period | New candidate version, not yet approved | 5.D acceptance: candidate created, v1 untouched |
| Numerical-impact determination | D.D | 5.E | Evidence shown to Gate reviewer | `numerical_impact` bool, minimum-comparison-set values in `extra_metadata` | 5.E acceptance: offsetting-change fixture |
| Technical regeneration vs. business reprocessing | D.E | 5.F | Unaffected downstream periods show no affected status anywhere | `reprocessing_required` per D.E causation rule | 5.F acceptance: three-way distinction test matrix |
| Downstream propagation + stopping rule | D.F | 5.G | P1→P4 chain behaves per explicit contract | Propagation halts at first unaffected period | 5.G acceptance: P1–P4 explicit scenarios |
| Chronological blocking | D.F | 5.H | Later period cannot close while predecessor unresolved | Read-time check against Close History | 5.H acceptance: block, then unblock after predecessor re-approval |
| Lineage / audit trail | D.G | 5.I | Close Validation Status / Close History show trigger type | `trigger = "explicit reopen"` / `"propagated from <period/version>"` | 5.I acceptance: both trigger types visibly distinguishable |
| Human Approval Gate unchanged | D.G | 5.J | Every new version still requires explicit human approval | `_gate_approved`, `close_approval_status` unchanged | 5.J acceptance: byte-diff confirms Gate logic untouched |
| Gap 1 absorption | Report §B | 4, 5.B | One authoritative period flow, not two | — | 5.B acceptance covers Gap 1's defect exactly |
| Gap 2 compatibility | Report §B | Section 6 | Historical navigation shows version, not just period | — | Compatibility statement, Section 6 |
| Scenario 3 full journey | Handbook §"Current Milestone" | Section 7 | Complete user-operable journey, HTML/PPTX form excluded | — | Section 7 acceptance list |

---

## 4. Classification of Every Open Item (resolves Critical Correction 2)

| Item | Classification | Resolution / routing |
|---|---|---|
| **Gap 1's period-selection defect vs. D15's period-selection requirement** | (1) Already decided by Final architecture (Report §B: "generalized, not duplicated") | **Gap 1, as a distinct implementation item inside `builder_brief_operability_gaps_1_2_3.md`, is superseded by this Brief's Section 5.B.** Builder must not implement a separate Gap 1 fix. When `builder_brief_operability_gaps_1_2_3.md` is next worked, its Gap 1 item should be marked "Satisfied by D15, Section 5.B" with a cross-reference to this Brief — not independently implemented, not silently dropped. |
| **Numerical comparison epsilon/tolerance value** | (3) Builder proposes; Architect confirms before acceptance — not a value Builder may finalize unilaterally | Builder proposes a specific epsilon consistent with this project's existing tie-out convention (`close_validation.py`/`rollups.py`'s own tolerance patterns) and states it explicitly in the Return Report. Builder may write code using the proposed value, but 5.E is not accepted as Pass until the Architect confirms it. This is a joint category — Builder initiates, Architect settles — not a pure Builder implementation detail Builder can finalize and move past. |
| **`PL_Quarterly` / `BvA_Q` independent comparison, due to `PL_Summary` / `Budget_vs_Actual` raw-source provenance** | (2) Already decided by Final architecture (D.D table: `PL_Quarterly` and `BvA_Q` — the canonical outputs — are compared independently; D.H item 1 explains why) | **Not open.** The fixed comparison table (Section 5.E) targets `PL_Quarterly`'s `Total Revenue ($)`/`Total Opex ($)` and `BvA_Q`'s `Budget ($)`/`Actual ($)` — these are the canonical comparison outputs, not the raw `PL_Summary`/`Budget_vs_Actual` sheets themselves. They are compared independently (not assumed derivable from `Expenses`/`Revenue`) specifically because their *underlying raw sources* — the `PL_Summary` and `Budget_vs_Actual` sheets — have independent provenance from `Expenses`/`Revenue`/`Headcount` (D.H item 1). Builder must not interpret this as licensing `PL_Summary` or `Budget_vs_Actual` themselves as separate, additional comparison targets — the comparison scope remains exactly the six canonical outputs in Section 5.E's table, no more. |
| **Whether `Budget ($)` is immutable across versions** | (6) Explicitly deferred, outside this Builder task | Builder implements `Budget ($)` as part of the compared set (per D.D — it is compared, immutable or not) **without assuming immutability**. If Builder's implementation would behave differently depending on the answer, Builder must not choose — flag the specific fork in the Return Report as a Principal/Architect decision needed, and implement the code path that treats `Budget ($)` as potentially variable (the safer, non-assuming default) pending that decision. |
| **Scenario 3's executive-output form (own HTML/PPTX pair vs. reused-with-lineage-view)** | (5) Principal decision required before Phase 7/8 work on Scenario 3, not before D15's lifecycle implementation | **Not a Builder decision, not resolved by this Brief.** Section 7 states exactly what is required regardless of this outcome, and what is explicitly excluded pending it. |
| **Exact UI placement/design of Step 1/Step 2 screens, Close Validation Status lineage display, Close History version list** | (3) Legitimate Builder implementation detail | Builder proposes concrete UI in the Return Report; the *information content* required (what must be shown) is fixed in Sections 5.C, 5.I, and 6 — the visual layout is Builder's to design. |

**No item above is left for Builder to decide silently.** Every row is either fixed by this Brief, routed to an explicit Architect confirmation step, or explicitly named as a Principal-level dependency Builder must not resolve.

---

## 0. Prerequisite — Gap 4 (operationally explicit, resolves Critical Correction 9)

D15 implementation (Sections 5.A onward) **does not begin** until all four of the following are true for `outputs/builder_brief_operability_gap4_close_durability.md`:

1. Implementation exists (Approve-close → `archive_close()` wiring, live).
2. A Builder Return Report has been produced against it.
3. The Architect has reviewed that Return Report and recorded a Pass.
4. The implementation is confirmed canonical-synced via fresh clone.

**Builder must not implement any part of the Gap 4 fix inside this Brief.** D15's 5.A extends `archive_close()` with a `version` parameter on top of the *already-working* single-version call path Gap 4 establishes; it does not create that call path. If Builder finds, on starting D15 work, that Gap 4 is not yet satisfied per the four conditions above, **stop and escalate to the Architect** rather than implementing Gap 4's fix as an undocumented side effect of D15.

---

## 5. Required Behavior — implemented in this order, each independently acceptance-tested

### 5.A — Close identity and versioning (architecture D.A)

- `close_history.archive_close()` gains a `version` integer parameter, default `1`.
- Folder layout: `close_history/{period_label}/v{n}/`. Every pre-D15 snapshot is implicit v1 — **no migration of existing files, no rewriting of existing snapshot data.**
- `list_approved_closes()` / `resolve_latest_approved_close()` gain `latest_version_only`, default `true` (existing callers unaffected with zero code changes).
- New function `resolve_version(period_label, version)`: returns the specific version or an explicit not-found result — **never silently falls back to latest.**

**Acceptance (live, connected):** archive a period at v1, then archive a correction at v2; confirm via live Close History UI that both are independently retrievable, v1's stored data is byte-identical before and after v2's creation, and `resolve_latest_approved_close()` without `latest_version_only=False` returns v2 while `resolve_version(period, 1)` still returns v1.

### 5.B — Authoritative period selection (architecture D.B; **absorbs Gap 1 — see Section 4**)

**This is one authoritative period-selection flow, not two separate fixes.** Gap 1's evidence-package period-sourcing defect and D15's Phase 2/3 period-selection defect are the same underlying problem: no single authoritative `target_period` exists anywhere in the current implementation.

- A single explicit **"Select period to close"** control is the sole source of `target_period` for the close workflow. It is a distinct control from the existing sidebar/explorer period selector.
- **The sidebar/explorer selector remains display-only and must never independently determine the close target**, directly or indirectly.
- The **exact same** `target_period` value — not a re-derived or re-resolved copy — must reach, from the same user selection, in this session:
  - Phase 2 validation
  - Phase 3 observation generation
  - Phase 6 evidence-package construction
  - the commentary/reconciliation workflow, wherever period is consumed
  - the approval/close lifecycle
  - `archive_close()`
- **No downstream component may independently infer the period** from: the dataset's terminal period, `period_order[-1]`, the currently-displayed sidebar period, whole-dataset processing without period filtering, or any separately-derived period variable. Every existing internal period-derivation path found during implementation must be replaced with a read of the single `target_period` value, not left in place as a redundant/inconsistent alternate path.

**Acceptance (live, connected — not a function-signature check):** With a multi-period dataset loaded, select a **non-terminal** period via the new control and run the complete close operation through to archival. Confirm, via direct inspection of the live application's actual output (not a direct call to any individual function): (a) Phase 2/3 validation results correspond to the selected period's data, not the terminal period's; (b) the Phase 6 evidence package's dates/values correspond to the selected period; (c) the archived Close History snapshot is keyed to the selected period, not the terminal period. All three must be demonstrated in one continuous live session, not as three isolated tests against three isolated functions.

### 5.C — Reopen transactional boundary (architecture D.C)

- Step 1 (Reopen Request / Consequence Review) and Step 2 (Final Confirmation) are pure session-state screens. **Neither writes to `close_history/` under any circumstance.**
- Cancel at Step 1 or Step 2: session state clears; period remains Closed at its current version; zero persistent change.
- Session abandonment before Step 2 confirmation: identical outcome to Cancel — achieved automatically because nothing was persisted. **No explicit rollback/cleanup code should exist**, because there is nothing to roll back; writing such code would itself indicate a persistence leak earlier in the flow and should be treated as a defect, not a feature.
- Only confirmed Step 2 triggers 5.D onward.

**Acceptance (live):** for each of Cancel-at-Step-1, Cancel-at-Step-2, and session-abandonment-before-Step-2, inspect `close_history/` directly before and after the sequence and confirm byte-for-byte identical contents. This is source-instruction Section 13-F test cases 4, 5, 6.

### 5.D — Correction intake and reprocessing pipeline

- A confirmed Step 2 reopen accepts new/corrected source data and new commentary for the reopened period only.
- This produces a **candidate version** (not yet persisted to Close History, not yet approved) — data validated, observations regenerated, commentary reconciled, against the same Phase 2–6 logic already governing a normal close, targeted at the reopened period via the same `target_period` mechanism from 5.B.
- v1 (and any prior version) of the period is untouched throughout.

**Acceptance:** source-instruction Section 13-F test case 8 (correction creates v2 without modifying v1) and case 9 (new commentary belongs to v2), both confirmed via live UI execution and direct inspection of stored data for both versions.

### 5.E — Canonical output comparison / numerical-impact determination (architecture D.D — fixed, not open)

Comparison operates on **exactly** this minimum independent-comparison set. This table is not a starting point for Builder judgment — it is the complete, fixed comparison scope:

| Output | Grain | Fields compared |
|---|---|---|
| `PL_Quarterly` | Fiscal Quarter (company-wide) | `Total Revenue ($)`, `Total Opex ($)` |
| `Rev_by_Region_Q` | Region × Fiscal Quarter | `Revenue ($)` |
| `Rev_by_Product_Q` | Product Line × Fiscal Quarter | `Revenue ($)` |
| `Exp_by_Dept_Cat_Q` | Department × Category × Fiscal Quarter | `Amount ($)` |
| `Headcount_Q` | Department × Fiscal Quarter | `Avg Headcount`, `Ending Headcount` |
| `BvA_Q` | Line Item × Fiscal Quarter | `Budget ($)`, `Actual ($)` |

All other named canonical outputs (`Exp_by_Dept_Q`, `Exp_by_Cat_Q`, `RegionNetGTMCost_Q`, `ProductNetRDCost_Q`, `RegionGTMPctTrend_Q`, `ProductRDPctTrend_Q`, `GA_Unallocated_Q`, `SB_VolRate_Q`, `Breadth_Concentration_Q`) are **regenerated, never independently compared** — they are formulas over the six above.

`PL_Quarterly`'s and `BvA_Q`'s values (the canonical outputs, not the raw sheets that feed them) are compared independently — this is fixed per D.D/D.H item 1, not a Builder choice; see Section 4 for the precise wording distinguishing the canonical outputs from their raw sources.

**Tolerance:** per Section 4's classification, Builder proposes a specific epsilon in the Return Report, consistent with existing tie-out conventions in `close_validation.py`/`rollups.py`; this section is not accepted as Pass until the Architect confirms the proposed value.

**Acceptance (fixture, Validation-Independence-compliant):** a constructed fixture with a known Department A / Category X↔Y offsetting change (per the Principal's worked example: X moves €500k→€600k, Y moves €300k→€200k, Department total unchanged at €800k) must be detected as `numerical_impact = true` at the `Exp_by_Dept_Cat_Q` grain — confirming the company-level `PL_Quarterly` check alone would have missed it. Per the Validation Independence Principle, this fixture may be Builder-authored for demonstrating implementation behavior, but genericity is not claimed from it alone — independent Test evidence is required before D15 reaches Verified (Section 8).

### 5.F — Technical regeneration / numerical impact / business-level reprocessing (architecture D.E — protected against the incorrect interpretation)

**The following interpretation is explicitly incorrect and must not be implementable:** *"a downstream period was technically regenerated, therefore `reprocessing_required = true` for it."* Acceptance testing must actively try to falsify this by regenerating an unaffected downstream period and confirming its state stays exactly as before.

The correct model, fixed exactly as follows:

- **Correction-source period** (explicitly reopened): `reprocessing_required = true` unconditionally — this is a *record* of the explicit reopen event, not caused by any comparison. New version, review, and re-approval proceed regardless of that period's own `numerical_impact` value.
- **Downstream period** (never explicitly reopened): technical regeneration is automatic whenever an upstream period changes — this is an internal computation only, never itself business-facing. `numerical_impact` for that period is computed per 5.E. **`reprocessing_required` for a downstream period equals `numerical_impact` for that period, exactly — it is never independently set, and it is never set to `true` by regeneration alone.**
- A downstream period with `numerical_impact = false`: no new version, no re-approval request, no affected/unresolved status anywhere in the product (Close Validation Status, Close History, or any other surface). Its existing approved version remains current and unchanged.

**Acceptance — three-way distinction test matrix (all four combinations must be independently demonstrable):**

| Period role | `numerical_impact` | Expected `reprocessing_required` | Expected user-visible state |
|---|---|---|---|
| Explicit reopen source | `false` | `true` (recorded, not caused) | New version created, requires re-approval, shows `trigger = "explicit reopen"` |
| Explicit reopen source | `true` | `true` | New version created, requires re-approval, shows `trigger = "explicit reopen"` |
| Downstream | `false` | `false` | No new version, no re-approval, no affected status, existing version unchanged |
| Downstream | `true` | `true` | New version created, requires re-approval, shows `trigger = "propagated from <period/version>"` |

All four rows must be independently demonstrated live, not inferred from code inspection alone.

### 5.G — Downstream propagation and stopping rule (architecture D.F — fully explicit)

For chronological periods P1 → P2 → P3 → P4, with P1 explicitly reopened and corrected:

1. Regenerate P2 (technical regeneration, automatic).
2. Compare P2's own state (5.E) against P2's own previously approved state.
3. **If P2 is unaffected:** stop. P3 and P4 are never examined, never regenerated, never touched in any way. P2 remains at its existing approved version.
4. **If P2 is affected:** P2 is versioned, reviewed, and re-approved via the Human Approval Gate. Only once P2 is re-approved does it become the **propagated source** for checking P3 (trigger recorded as `"propagated from P2/v<n>"`, not `"explicit reopen"`). Repeat steps 1–4 for P3, then P4, chronologically — never out of order, never skipping ahead.

**Required acceptance scenarios (all independently tested):**
- Terminal-period reopen (no downstream periods exist at all) — degrades to a no-op for propagation, no error.
- Immediately-affected downstream period (P2 affected).
- Immediately-unaffected downstream period (P2 unaffected, propagation stops).
- **Affected P2 followed by unaffected P3** — confirms propagation continues correctly past an affected period and can still stop at the next one, exercising the full chain logic rather than only single-hop cases.
- Chronological blocking: P3 cannot be closed while P2's `reprocessing_required = true` remains unresolved (unapproved).
- Blocking removal: once P2 is re-approved, P3 becomes eligible.

This is source-instruction Section 13-F cases 10–13, plus the terminal-period case, plus the two-hop affected-then-unaffected case added by this Brief.

### 5.H — Chronological blocking (architecture D.F)

- Blocking is a **read-time check** against Close History's dependency metadata, evaluated at close-attempt time — not a separately persisted lock. A period is blocked from closing only while a chronologically-prior period has `reprocessing_required = true` and is not yet re-approved at its new version.
- A period that was never in an affected state (5.F, `numerical_impact = false`) is never a blocker to anything downstream of it.

**Acceptance:** attempt to close P3 while P2 is unresolved — confirmed blocked, with the specific blocking predecessor identified in the UI (not a generic "blocked" message). Re-approve P2; confirm P3 becomes closeable without any other state change.

### 5.I — Lineage and audit evidence (architecture D.G)

- Comparison evidence — per-output, per-dimension before/after values, the `numerical_impact` boolean, and a `trigger` field (`"explicit reopen"` or `"propagated from <predecessor period/version>"`) — is stored in `archive_close()`'s existing `extra_metadata` hook. No signature change beyond 5.A's `version` parameter.
- Close Validation Status and Close History must both visibly distinguish, for any version beyond v1: which trigger type produced it, and (for a propagated version) its causal predecessor period/version.

**Acceptance:** for a chain including both an explicit-reopen version and a propagated version, confirm both trigger types are visibly and correctly distinguished in the live Close Validation Status/Close History UI — not just present in stored metadata.

### 5.J — Human Approval Gate boundary (architecture D.G — unchanged authority)

- D15 may generate evidence and lifecycle state. D15 may mechanically determine `numerical_impact`. D15 may mechanically determine whether a downstream period is affected, per 5.F/5.G.
- **D15 must not automatically approve any close version, under any condition, including `numerical_impact = false`.** Every new version requiring approval — the explicit-reopen source and every affected downstream version — passes through the existing Human Approval Gate unchanged.
- `_gate_approved`, `close_approval_status`'s existing transitions, and the Phase 7 structural guard are **not modified** by this Brief.

**Acceptance:** direct code diff confirms `_gate_approved` and the Phase 7 structural guard are byte-identical to pre-D15 canonical outside of newly-available evidence being displayed to the reviewer. Live confirmation that a new version (both explicit-reopen and propagated cases) sits at "awaiting approval" until the existing Approve/Reject controls are used — no code path advances it automatically.

---

## 6. Gap 2 Compatibility Requirement (does not change Gap 2's scope)

`builder_brief_operability_gaps_1_2_3.md`'s Gap 2 (read-only historical navigation of archived Phase 4-6 results) is **not modified, narrowed, or expanded** by this Brief. However, because the architecture identifies Gap 2 as a direct dependency of D15 (Report, Section B), D15's implementation must be compatible with it:

- Gap 2's navigation UI, whenever implemented, must be able to display **version**, not just period — its design must not assume one-snapshot-per-period.
- D15's `list_approved_closes(latest_version_only=False)` (5.A) is the function Gap 2's implementation should call to enumerate all versions of a period, once Gap 2 is built.
- Builder implementing this D15 Brief does **not** implement Gap 2's UI. This section exists only so that when Gap 2 is later built, it is built against a data model that already supports what it needs, rather than discovering a gap and requiring D15 rework.

---

## 7. Scenario 3 — Complete User-Operable Journey (resolves Critical Correction 3)

Scenario 3 (Handbook v2.17, Current Milestone) is not a backend lifecycle test. It requires the **complete, user-operable journey**, live, in the actual application:

1. Selecting the intended period (5.B's control).
2. Identifying the previously closed version to reopen.
3. Requesting reopen (Step 1).
4. Consequence review (Step 1's display).
5. Final confirmation (Step 2).
6. Correction intake (5.D).
7. Reprocessing (5.D/5.F automatic regeneration).
8. Numerical-impact determination (5.E).
9. Downstream propagation where applicable (5.G).
10. Blocking where applicable (5.H).
11. Human review/approval (5.J, unchanged Gate).
12. Creation of the new version (5.A).
13. Preservation of the old version (5.A).
14. Close Validation Status visibility (5.I).
15. Close History visibility (5.A, 5.I).
16. Lineage showing explicit-reopen vs. propagated-impact origin (5.I).

Items 1–16 are **required** for this Brief and for Scenario 3 to be demonstrable, regardless of how the open executive-output question below resolves.

**Scenario 3's D15 lifecycle implementation does not include independent Phase 7/8 output generation under this Brief.** However, Scenario 3 as a milestone requires the same HTML/PPTX final-output stage established by the Principal's milestone-expansion decision (Handbook v2.17, "Current Milestone"; architecture report Section G) — that requirement is not waived or narrowed by this Brief. The exact reuse-vs-own-output implementation decision (own HTML/PPTX pair vs. reusing Scenario 1/2's outputs with an added lineage view) remains a **Principal decision** and must be resolved before the Scenario 3 demonstration reaches that stage — it is not eliminated, only sequenced after the lifecycle work this Brief governs. Builder does not implement Phase 7/8 output generation for Scenario 3 under this Brief; that work is scoped once the Principal decision above is made, via an Architect/Builder Brief addendum. Builder should not infer or default an answer, and must not treat the absence of that decision as evidence the output requirement itself doesn't apply.

---

## 8. Required Evidence

- **Implementation evidence:** direct code review against each of 5.A–5.J's specific acceptance criteria, individually — not a single composite claim.
- **Builder regression evidence:** existing tie-out suites (`rollups.py`, `close_validation.py`) show zero regression. A new Builder-authored regression fixture covering 5.A–5.J proves non-regression only — not genericity (Validation Independence Principle).
- **Canonical synchronization:** fresh-clone confirmation at promotion, per this project's standing Canonical Sync Verification procedure.
- **Independent Test evidence:** source-instruction Section 13-F scenarios 1–16 (15 original + terminal-period case), plus the 5.F three-way distinction matrix and the 5.G affected-then-unaffected two-hop case, run independently of Builder per the Validation Independence Principle.
- **Live/connected evidence requirement (applies throughout):** no acceptance criterion in Section 5 is satisfied by function existence, a passing unit test, or a Return Report claim alone — each requires the user-action → live-behavior → state-transition → persistence → downstream-effect chain demonstrated in the running application, as specified per subsection.

## 9. Explicit Exclusions

- No change to any regenerated-only output's own comparison logic (5.E) — never independently compared.
- No migration of existing `close_history/` snapshot files.
- No change to the Human Approval Gate's approval/rejection logic (5.J).
- No change to `phase4_semantic_reconciliation_brief_v2.md` scope.
- No implementation of Gap 2's or Gap 3's UI/scope under this Brief (Section 6).
- No implementation of Gap 1's fix as a separate item — absorbed into 5.B (Section 4).
- No Phase 7/8 executive-output implementation for Scenario 3 (Section 7).
- No resolution of the `Budget ($)` immutability question — implemented per Section 4's routing (treat as potentially variable, flag the fork).

## 10. Constraints

- Validation Independence Principle: the 5.E offsetting-change fixture and any other Builder-constructed fixture prove implementation behavior only, never genericity.
- Dataset Provenance Discipline applies to any dataset used in testing.
- No live API/credential dependency — D15 has no AI/LLM component.

## 11. Regression Expectations

Zero effect on: D10/D11/D12/D14 (Verified, not reopened), D13's Section H/J UAT requirement (unchanged, independent of this Brief), the Human Approval Gate's eight existing acceptance criteria (5.J), Phase 4-6 commentary matching/validation, Phase 7 period-display formatting. Every close prior to this Brief's implementation continues to function identically as implicit v1.

---

## 12. Architect Builder-Readiness Self-Review (Critical Correction 12)

1. **No Principal requirement narrowed** — Section 3's matrix traces every requirement from the source instruction/Section A through to an acceptance criterion; none dropped.
2. **No Final architecture decision reopened** — D.A–D.H reproduced exactly (comparison set, causation model, propagation rule); zero redesign.
3. **No material product decision left for Builder to invent** — Section 4 classifies every open item; categories 4/5 items are explicitly routed, not left silent.
4. **Gap 1 coordination explicit and non-duplicative** — Section 4 + 5.B: one flow, Gap 1 marked superseded-by-cross-reference, not separately implemented.
5. **Gap 2 compatibility explicit** — Section 6, scope not touched, data-model compatibility stated.
6. **Gap 4 prerequisite explicit** — Section 0, four concrete conditions, explicit stop-and-escalate instruction if not met.
7. **Human Approval Gate semantics unchanged** — 5.J, byte-diff acceptance criterion.
8. **Scenario 3 fully connected** — Section 7, 16-item live journey, executive-output question explicitly excluded and routed.
9. **Version history immutable and testable** — 5.A acceptance requires byte-identical v1 after v2 creation.
10. **Technical regeneration / numerical impact / reprocessing remain distinct** — 5.F's explicit-incorrect-interpretation warning plus the four-row test matrix.
11. **Propagation and stopping rules testable** — 5.G's numbered P1–P4 contract plus six required scenarios, including the two-hop case.
12. **Acceptance criteria test live connected behavior** — every subsection in Section 5 states "(live, connected)" or equivalent and specifies the actual application behavior required, not isolated function checks.
13. **Every unresolved item classified** — Section 4's table, all five non-"already decided" categories used correctly, none silently resolved.
14. **Required evidence specified** — Section 8.
15. **No contradiction identified within the Brief; consistency with the governing architecture and Handbook was checked** — Section 3's matrix, Section 4's classifications, and Section 5's detailed requirements checked against each other and against the architecture report and Handbook v2.17. (This revision corrects a governance inconsistency the Project Advisor identified between Section 7's original wording and the Handbook's milestone-expansion decision — see the revision note at the top of this document. That correction is itself evidence this self-review is a check performed in good faith, not a guarantee of prior completeness; it is not asserted as exhaustive beyond what was actually checked.)
16. **No duplication or silent modification of another active Brief** — `phase4_semantic_reconciliation_brief_v2.md` untouched; `builder_brief_operability_gaps_1_2_3.md` touched only by the explicit, narrow Gap-1-superseded cross-reference in Section 4, which is itself already-decided architecture (not new scope), not a modification of Gaps 2/3.
17. **No new scope introduced without Principal authorization** — every requirement in this Brief traces to Section A's authorization or the Final architecture; nothing added.

---

*This Brief implements `governance/architect_reports/architect_alignment_report_period_lifecycle_reopen_correction.md`, Section D, exactly as finalized through Principal review. Any implementation choice not resolved by that architecture or this Brief is a Return Report item for Architect review — see Section 4 for the explicit routing of every currently-known open item.*
