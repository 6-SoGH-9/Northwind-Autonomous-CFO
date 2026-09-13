# Architect Documentation & Alignment Report — Period Lifecycle, Reopen, Correction/Reprocessing

**Status:** Governance reconciliation only. No Builder Brief is authorized by this document.
**Trigger:** Principal decision (this session) supersedes the Gap 4 deferral recorded in Handbook v2.16 / `architect_alignment_report_operability_gaps_1_4.md`.
**Canonical baseline checked:** fresh clone, `main` HEAD `575bab645810084a42fd36ed3c278d2741fd397e`, working tree clean.
**Source instruction:** `governance/superseded_operability_package/Architect Instruction — Incorporate Period Lifecycle and Correction-Reprocessing Into Product Scope.md` (still carries no provenance banner — this is noted as a standing documentation defect to fix, not as a reason to question the Principal's direct, dated confirmation in this session, which is the actual authorizing act).

---

## A. Principal Authorization (recorded, not re-litigated)

Per the Principal's explicit statement this session: the full capability described in the instruction document — explicit period selection as authoritative; two-step reopen with cancel-safe/abandon-safe semantics; versioned closes (v1 preserved, v2+ created, never overwritten); downstream dependency propagation; chronological reprocessing; blocking of later periods until predecessors resolve; distinguishing reprocessing-impact from numerical-impact; visibility in Close Validation Status and Close History — **is authorized product scope, effective this session, superseding the prior Gap 4 deferral.**

This is recorded here as a dated decision. It supersedes, specifically:
- Handbook v2.16, Known Technical Debt: "a fourth, closed-period reopen/correction, was confirmed to have no material gap beyond the existing Phase-9 deferral and remains out of scope, unchanged."
- The corresponding line in `architect_alignment_report_operability_gaps_1_4.md`.

Nothing else in that prior review is disturbed (Gaps 1–3 dispositions stand unchanged).

---

## B. Existing Governance — What Already Supports, Conflicts, or Must Be Amended

| Item | Relationship to new scope |
|---|---|
| D10 (Approved Financial Close is the canonical object; Close History is immutable, one snapshot per approved close) | **Partially supports, but its current implementation must be extended, not replaced.** D10's principle (approved close = canonical object, retained not overwritten) is fully consistent with versioning. Its *implementation* (`close_history.archive_close()`, keyed by `period_label` alone, `FileExistsError` on any re-archive of the same label) does **not** currently support a second version of the same period — this is the concrete architectural gap, not a conflict of principle. |
| D13 (Machine Recommends, Human Decides; Human Approval Gate) | Fully compatible, unaffected. Reopen/versioning does not touch approval authority — each new version still requires its own Human Approval Gate pass before archival. |
| Gap 1 (Product Operability Brief, active) — Phase 6 evidence-package period-sourcing defect | **Same root cause family as this new scope's Section 4 requirement** (explicit period selection must be authoritative). Gap 1 fixes evidence-package sourcing specifically; this new scope requires the *same* fix generalized to Phase 2/3's target-period resolution (`_resolve_target_period()` / the unconditional `period_order[-1]`/whole-dataset behavior confirmed below). These should be sequenced together, not duplicated as two separate fixes to the same underlying selector problem.
| Gap 2 (read-only historical navigation of archived Phase 4-6 results, principal-authorized, active) | **Direct dependency.** Gap 2's read path over `close_history.list_approved_closes()` was designed against a one-snapshot-per-period model. Once versioning lands, Gap 2's navigation UI must display version, not just period, or it will silently show only one version per period with no way to know a v2 exists. This is a required-changes item for Gap 2, not new scope for Gap 2 itself.
| Gap 3 (Analytical Definition Registry — versioning, attribution, close-record capture, principal-authorized, active) | **No conflict, but must be reconciled at the data-model level.** Gap 3 already introduces a version-with-effective-date concept for analytical *definitions*. This new scope introduces a version concept for *closes*. These are two independent version axes (definition version vs. close version) that will co-exist in the same snapshot metadata (`archive_close()`'s `extra_metadata`). The Gap 3 Brief and this capability's eventual Brief must agree on non-colliding field names before either is implemented, to avoid a second "two documents each assuming they own the same field" defect.
| `governance/builder_briefs/builder_brief_operability_gaps_1_2_3.md` | **Must be amended or explicitly scoped around.** It currently governs Gaps 1–3 only. This new capability should **not** be silently folded into it (that Brief is close to Builder-ready and already principal-approved at its current scope) — see Section E (sequencing) below for the recommendation to keep it a separate, later Brief rather than bundling.
| The already-approved, not-yet-pushed Gap 4 Brief (`outputs/builder_brief_operability_gap4_close_durability.md` — narrow scope: wire `archive_close()` to the live "Approve close" button; document period-target behavior; make workflow-state display honest) | **Prerequisite, not superseded.** This narrow brief fixes the mechanical connection (`Approve close` → `archive_close()`) that the full lifecycle depends on. It should proceed first/unchanged — the new capability needs a *working* single-version archive-on-approve path before it can add versioning on top of it. |
| Section 2a (AI Role Boundaries) | No interaction. Not touched by this scope. |
| Cycle 3 (D10/D11/D12), D14 | Not reopened by this decision. |

**Conclusion:** no genuine remaining conflict once A is accepted as authoritative. The prior "no material gap" finding is superseded; the Gap 1/2/3 items are not superseded but must be sequenced/reconciled with this new work as noted.

---

## C. Required Repository/Documentation Synchronization

**These are governance-synchronization items, not a procedural block.** Per `ARCHITECT_SCOPE_REFUSAL_RULES.md`'s documentation-synchronization rule, the fact that these artifacts have not yet been updated does not prevent, delay, or gate the authorized architecture (Section D) or any authorized implementation work built on it — Section A's authorization is already effective. These updates keep the governance record accurate; they are not a precondition for proceeding.

In order, these are the artifacts that must be synchronized:

1. **`project_handbook.md` → v2.17.**
   - New Decision Log entry (**D15**, next available number): "Period Lifecycle, Reopen, and Correction/Reprocessing is authorized product scope. Implementation Status: Planned." Rationale line records this session's supersession of the Gap 4 deferral, with an explicit pointer to this report.
   - Known Technical Debt: remove/strike the "Gap 4 ... remains out of scope, unchanged" line; replace with a pointer to D15 and this report.
   - Section 10 (Known Technical Debt) and Section 8 (Builder Brief History): add a row noting this report exists and that a Builder Brief is pending the reconciliation in Sections D–F below.
   - **Section 4 (Workflow Specification) / Section 9 (End-to-End Product Demonstration milestone):** ~~flag that Scenario 1/2 as currently defined assume a single-version close~~ — **resolved by the Principal's later decision, recorded in Section G below: the milestone is expanded to three scenarios, with Scenario 3 covering the reopen/correction/reprocessing/re-approval/archival/lineage journey.** Section 4/9 must be updated to add Scenario 3's definition per Section G, not left posing this as an open question.
2. **`architect_alignment_report_operability_gaps_1_4.md`** — add an addendum (not a silent rewrite) noting Gap 4's disposition was superseded by Principal decision on this date, pointing to this report. Per Handbook convention (Section 27 of your standing instructions: "do not silently rewrite history"), the original text stays; the addendum is what changes the live disposition.
3. **The source instruction document itself** (`governance/superseded_operability_package/Architect Instruction — Incorporate Period Lifecycle...md`) — move it out of `superseded_operability_package/` (that folder is specifically for documents whose classification is "superseded," which this no longer is) into `governance/architect_reports/` or a new `governance/principal_instructions/` location, **with a provenance banner added** recording: date authorized, this report as the reconciling document, and the fact that it now governs active (not superseded) scope. This closes the standing "no provenance banner" defect on this specific file rather than leaving it permanently flagged.
4. **A new Builder Brief** — not yet drafted, and not created by this report. Section D architecture is now Final/confirmed; drafting the Brief is the next step after this documentation-synchronization task, not part of it.
5. **`builder_brief_operability_gaps_1_2_3.md`** gets a short cross-reference note (not a scope change) pointing to D15, specifically at the point where Gap 2's read-only navigation UI is specified, flagging that its design should not assume one-snapshot-per-period once D15 lands (see B above). This is a documentation cross-reference, not new scope for that Brief.

None of these are implementation work. All are governance-correction/synchronization, consistent with `ARCHITECT_SCOPE_REFUSAL_RULES.md` Rule 5 (documentation sync is not a procedural block, and must not be used to delay an authorized decision) — I'm listing them so the record stays internally consistent, not as a precondition that blocks starting architecture work in parallel.

---

## D. Architecture — Durable State Model

**Status: Final, as revised through this session's exchanges.** Checked against actual canonical code, not assumed. Verification basis (fresh clone, `main` HEAD `575bab645810084a42fd36ed3c278d2741fd397e`): `close_history.py` (`archive_close`, `list_approved_closes`, `resolve_latest_approved_close`), `Northwind_Financial_Dashboard.py` (lines ~205, ~539–548, ~1014–1017), `rollups.py` (`build_revenue_rollup`, `build_expense_rollup`, `build_headcount_rollup`, `build_bva_rollup`, `build_pl_rollup`, `build_region_contribution_margin`, `build_product_contribution_margin`, `build_pct_trend`, `build_salaries_volume_rate`, `build_breadth_concentration`, `add_variance` at line 164, and the five raw source sheets — `Revenue`, `Expenses`, `Headcount`, `Budget_vs_Actual`, `PL_Summary` — loaded at lines 84–91).

### D.A — Close identity and versioning

Confirmed defect: `close_history.archive_close(period_label, ...)` (`close_history.py:131`) keys each snapshot folder by `period_label` alone; a second call with the same label raises `FileExistsError`. There is no version concept today.

**Model:** close identity becomes the pair `(period_label, version)`. `archive_close()` gains a `version` integer parameter (default `1`, preserving every existing D10/Gap-4 snapshot as an implicit v1 with zero migration needed). Folder layout: `close_history/{period_label}/v{n}/`. `list_approved_closes()` and `resolve_latest_approved_close()` are extended, not replaced: both gain an explicit `latest_version_only` behavior (default true, preserving current callers' behavior unchanged) and a new `resolve_version(period_label, version)` lookup for a specific historical version. Any caller that needs to show lineage or prior versions — e.g. Gap 2's historical-navigation UI (Section B) — must explicitly request the version-inclusive listing (`latest_version_only=False`); the default view remains latest-version-only so existing callers see no behavior change.

### D.B — Authoritative period selection

Confirmed defect: Phase 2/3 (`Northwind_Financial_Dashboard.py:539–548`) run against `R.expenses`/`R.headcount` — the entire currently-loaded dataset — never against the sidebar's `current_period` variable (line 205). The sidebar selector drives *display* filtering throughout the dashboard (dozens of `== current_period` comparisons) but never reaches the close-validation call. This is the same root cause as Gap 1's evidence-package period-sourcing defect, generalized.

**Model:** a single `target_period` value, set only by an explicit "Select period to close" control (not the sidebar explorer selector, which remains a separate, display-only control), becomes the one input threaded into Phase 2/3, the evidence package, the commentary workflow, and `archive_close()`. No function anywhere derives its own period independently of this value.

### D.C — Reopen transactional boundary

Step 1 and Step 2 (source instruction, Section 6) write nothing to `close_history/`. Both are pure session-state confirmation screens. Only a confirmed Step 2 triggers the actual correction-intake → reprocess → new-version pipeline. Cancel or session-abandon at either step requires no rollback logic, because no persistent write has occurred yet — there is nothing to undo. The "Approve close" button (`Northwind_Financial_Dashboard.py:1014`) currently only sets `st.session_state["close_approval_status"] = "approved"` — no call to `archive_close()` exists on that path today (confirmed, not narrated); the Gap 4 Brief (separate, already-approved, prerequisite) fixes this for the single-version case, which D.A then extends to versions.

### D.D — Canonical output comparison / numerical-impact determination

Every one of the 14 named canonical outputs is a `pandas.groupby(...).sum()`/`.mean()` aggregation (or a further arithmetic/ratio transform of one) over exactly five raw sheets: `Revenue`, `Expenses`, `Headcount`, `Budget_vs_Actual`, `PL_Summary`. Several of the 14 are fully derivable from others already in the list. The comparison compares at the **finest independent grain actually present**; everything derivable from that grain is regenerated, not independently re-checked.

| Existing canonical output | Dimensional grain | Underlying numerical fields compared | Derived fields regenerated rather than independently triggering impact? | Downstream-triggering impact? |
|---|---|---|---|---|
| `PL_Quarterly` | Fiscal Quarter (company-wide) | `Total Revenue ($)`, `Total Opex ($)` — sourced from raw `PL_Summary`, **not** internally recomputed by `rollups.py` from `Expenses`/`Revenue` (see D.H item 1) | `Operating Profit ($)`, `Operating Margin (%)`, all `*_QoQ/YoY_Var` columns | **Yes, but not sufficient alone** — must be paired with the dimensional grains below, never used as a substitute for them |
| `Rev_by_Region_Q` | Region × Fiscal Quarter | `Revenue ($)` (sum from `Revenue` sheet) | `Revenue Mix (%)`, `Prior Period ($)`, `QoQ/YoY Variance ($/%)`, `YoY Prior-Year Same-Qtr ($)` | Yes |
| `Rev_by_Product_Q` | Product Line × Fiscal Quarter | `Revenue ($)` (sum from `Revenue` sheet) | Same set as above | Yes |
| `Exp_by_Dept_Q` | Department × Fiscal Quarter | `Amount ($)` — fully derivable as `Exp_by_Dept_Cat_Q` summed over Category | `Prior Period ($)`, `QoQ/YoY Variance ($/%)`, `YoY Variance ($/%)` | No — redundant with `Exp_by_Dept_Cat_Q`; retained as an internal cross-check, not an independent trigger |
| `Exp_by_Dept_Cat_Q` | **Department × Category × Fiscal Quarter** | `Amount ($)` (sum from `Expenses` sheet) — **the finest expense grain the pipeline produces** | `Prior Period ($)`, `QoQ/YoY Variance ($/%)` | **Yes — the primary expense trigger grain** |
| `Exp_by_Cat_Q` | Category × Fiscal Quarter (company-wide) | `Amount ($)` — fully derivable as `Exp_by_Dept_Cat_Q` summed over Department | `Prior Period ($)`, `QoQ/YoY Variance ($/%)` | No — redundant with `Exp_by_Dept_Cat_Q` |
| `Headcount_Q` | Department × Fiscal Quarter | `Avg Headcount`, `Ending Headcount` (direct measures, not ratios) | *(none)* | Yes |
| `BvA_Q` | Line Item × Fiscal Quarter | `Budget ($)`, `Actual ($)` — sourced from raw `Budget_vs_Actual` sheet, independent provenance (see D.H item 1) | `Variance ($)`, `Variance (%)`, `Flag`, streak count | Yes |
| `RegionNetGTMCost_Q` | Region × Fiscal Quarter | *(none — allocation formula over `Rev_by_Region_Q` + `Exp_by_Dept_Q`(GTM depts), both already covered)* | `Revenue Share`, `Allocated S&M + CS Opex ($)`, `Region Net of GTM Cost ($)` | No |
| `ProductNetRDCost_Q` | Product Line × Fiscal Quarter | *(none — same reasoning)* | `Revenue Share`, `Allocated R&D Opex ($)`, `Product Net of R&D Cost ($)` | No |
| `RegionGTMPctTrend_Q` | Region × Fiscal Quarter | *(none)* | `Region Net of GTM Cost (%)` — pure ratio | No |
| `ProductRDPctTrend_Q` | Product Line × Fiscal Quarter | *(none)* | `Product Net of R&D Cost (%)` — pure ratio | No |
| `GA_Unallocated_Q` | Fiscal Quarter (company-wide) | `G&A Unallocated Overhead ($)` — fully derivable as `Exp_by_Dept_Cat_Q` filtered to G&A, summed | *(none beyond the sum)* | No — redundant with `Exp_by_Dept_Cat_Q` |
| `SB_VolRate_Q` | Department × Fiscal Quarter | `S&B Amount ($)` and `Avg Headcount` — both already covered | `Cost per Head ($)`, all `Prior *`, `*Change`, `Volume/Rate/Bridge Effect ($)`, `Actual Variance ($)` | No — every field is a formula over already-covered inputs |
| `Breadth_Concentration_Q` | Region / Product Line / Department (by category subset) × Fiscal Quarter | *(none)* | Entire sheet — computed from `Rev_by_Region_Q`/`Rev_by_Product_Q`/`Exp_by_Dept_Cat_Q`, already covered | No |

**Minimum independent-comparison set:** `PL_Quarterly` (`Total Revenue ($)`, `Total Opex ($)` — necessary but not sufficient alone), `Rev_by_Region_Q` (`Revenue ($)`), `Rev_by_Product_Q` (`Revenue ($)`), `Exp_by_Dept_Cat_Q` (`Amount ($)`), `Headcount_Q` (`Avg Headcount`, `Ending Headcount`), `BvA_Q` (`Budget ($)`, `Actual ($)`). Every other named output is a formula over these six and is regenerated automatically.

### D.E — Technical Regeneration, Numerical Impact, and Business-Level Reprocessing (three distinct concepts)

**1. Technical regeneration / dependency recalculation.** Whenever an upstream period (a correction source, or an already-affected downstream period) changes, every immediately-following period's rollups are recomputed — automatic and unconditional, because `add_variance`'s `Prior Period ($)`/`QoQ`/`YoY` columns (`rollups.py:164`) always read the immediately preceding period's row. This is a computational step only. It is not persisted as a business-facing state and does not, by itself, touch `close_approval_status` or require any human action — it exists purely to produce the inputs D.D's comparison needs.

**2. Numerical impact.** For any period being checked — the correction source itself, or a downstream period reached via propagation — `numerical_impact` is the automatic output of comparing that period's own D.D independent-comparison-set values (its regenerated candidate state) against its own previously-approved values. A change in `Prior Period ($)`/variance columns caused solely by a predecessor's change is never, by itself, `numerical_impact = true` for the period being checked — only a change in that period's own values in D.D's minimum set counts.

**3. Business-level `reprocessing_required`.** This flag means: *this period's own approved canonical state has been affected (or, for the source period, was explicitly reopened) and it requires a new version and re-approval.* Its cause differs by role:

- **Correction-source period** (the period the Principal explicitly reopens, per the source instruction's Section 6 two-step process): the **explicit reopen action itself** is what initiates correction, reprocessing, a new version, and re-approval. `reprocessing_required = true` for this period is a **record of that already-decided business-lifecycle event, not the mechanism that causes it** — the version transition happens because the Principal reopened the period, independent of and prior to any comparison result. It is set unconditionally, regardless of what `numerical_impact` for that same period turns out to be. This is exactly the state the source instruction required to be representable: `reprocessing_required = true` with `numerical_impact = false` for the source period itself is valid and expected.
- **Downstream period** reached via propagation: there is no explicit human reopen here. `reprocessing_required[P+1] = numerical_impact[P+1]`, exactly — the **comparison result is the trigger**, because no human explicitly reopened that period. If the downstream period's own D.D comparison set is unchanged, it never enters a reprocessing state at all: no new version, no re-approval, no "affected" status anywhere in the product.

The same field name therefore carries two different causal relationships depending on the period's role, and the audit trail (D.G) records which: a source period's record carries `reprocessing_required = true, trigger = "explicit reopen"`; a downstream period's record carries `reprocessing_required = true, trigger = "propagated from <predecessor period/version>"` only when `numerical_impact` made it true — otherwise no new record is created at all, and the existing approved version simply remains current.

### D.F — Downstream Dependency and Chronological Blocking

```
Correction source period P (e.g. Q3) — PRINCIPAL EXPLICITLY REOPENS IT (source instruction, Section 6).
  → The reopen action itself is what initiates correction, reprocessing, a new version, and re-approval for P.
  → reprocessing_required[P] = true — a RECORD of this explicit lifecycle event, not its cause.
  → numerical_impact[P] = compare(P's new state, P's prior approved state)   [D.D]
  → P is versioned (vN+1), reviewed, and re-approved via the Human Approval Gate,
      regardless of numerical_impact[P]'s value — the version transition was already
      caused by the reopen action, not conditioned on the comparison result.

For the next chronological period P+1 — NO explicit reopen occurs here:
  → technical regeneration: recompute P+1's rollups using P's new (approved) state
  → numerical_impact[P+1] = compare(P+1's own regenerated state, P+1's prior approved state)   [D.D]
  → reprocessing_required[P+1] = numerical_impact[P+1]
      (the comparison result IS the cause here — there is no other trigger available)

  IF numerical_impact[P+1] == false:
      reprocessing_required[P+1] = false.
      P+1's existing approved version remains valid, unchanged, current.
      No new version, no re-approval, no "affected" status anywhere in the UI.
      Propagation STOPS. P+2 is never examined.

  IF numerical_impact[P+1] == true:
      reprocessing_required[P+1] = true.
      A new candidate version is generated for P+1; it requires its own review/re-approval
      via the Human Approval Gate.
      Once P+1 is re-approved (versioned to vN+1):
          P+1 now becomes the source for checking P+2 — but this is a PROPAGATED source
          (trigger = numerical impact found), not an explicit reopen. The distinction in
          causation is preserved in P+1's own record even as it plays the "source" role
          for the next iteration.
```

**Blocking:** a later period is blocked from being closed only while an earlier period in its chronological chain currently has `reprocessing_required = true` **and is not yet re-approved at its new version** — i.e., blocking tracks *unresolved* affected periods, not every period that was ever technically regenerated. A period whose propagation check resolved `reprocessing_required = false` was never in a blocking state and never appears as a blocker downstream of it.

**Reconciling with source-instruction test scenario 11** — corrected terminology: **"downstream period is technically regenerated and confirmed unaffected"** (the instruction's own original phrasing, "downstream period is reprocessed even with no numerical change," predates this session's D.E/D.F causation clarification and must not be read as implying a business-level reprocessing state). This scenario exercises **technical regeneration only** — confirming the system actually recomputes the downstream period and correctly determines `numerical_impact = false` / `reprocessing_required = false`. The eventual Builder Brief's acceptance criteria for this case must use "regenerated and confirmed unaffected" language, not "reprocessing_required = true" or any phrasing implying the downstream period entered a reprocessing state.

### D.G — Evidence and Human Approval Gate

The comparison in D.D/D.E produces structured evidence (per-output, per-dimension before/after values, the resulting `numerical_impact` boolean, and — per D.E's causation distinction — the `trigger` field: `"explicit reopen"` or `"propagated from <period/version>"`) stored in `archive_close()`'s existing `extra_metadata` hook — no signature change needed beyond D.A's `version` parameter. This evidence is what the Human Approval Gate's reviewer sees before approving the new version: the machine determines and presents the comparison and its cause (D13: Machine Recommends/Calculates); the human still makes the actual approve/reject decision, unchanged from the existing Gate mechanics (`Northwind_Financial_Dashboard.py:1014` onward). Nothing about the Gate's existing structural blocking logic (`_gate_approved`) changes.

### D.H — Remaining architectural questions

1. **`PL_Summary` / `Budget_vs_Actual` independent-source ambiguity.** Both are raw sheets in the incoming workbook, not values `rollups.py` computes internally from `Expenses`/`Revenue`. The Handbook's "Fixture internal-consistency corollary" (Section 10) documents a real, previously-encountered case where `PL_Summary` drifted from `Expenses` in a test fixture, producing a genuine tie-out failure. A corrected dataset could similarly supply a `PL_Summary`/`Budget_vs_Actual` that disagrees with corrected `Expenses`/`Revenue`/`Headcount` — exactly what D.D's independent comparison is designed to catch, but only because `PL_Quarterly` and `BvA_Q` are treated as independently-compared in the table above rather than assumed derivable. Flagging because this is the one place in D.D where "compare independently" isn't obvious from the pipeline's own internal derivation logic, and rests instead on this project's own prior incident.
2. **Rounding/tolerance for equality.** D.D's comparisons are floating-point dollar/percentage values. Existing tie-out checks use explicit epsilon tolerances rather than exact equality; D.D assumes the same convention but the exact tolerance value isn't decided — a Builder-Brief-level parameter, not an architectural blocker.
3. **Whether `BvA_Q`'s `Budget ($)` is expected to ever change on a correction.** If Budget is architecturally guaranteed immutable across versions, only `Actual ($)` needs independent comparison there. No evidence either way in the current dataset/code (no correction has ever occurred yet, by definition); not assumed.

---

## E. Integration Points

Required integration, in dependency order:
1. Gap 4's already-approved narrow Brief (archive-on-approve wiring) — **prerequisite, unblocked, should proceed independently and first.**
2. Explicit period selection becomes authoritative for Phase 2/3 (closes the `_resolve_target_period()` gap) — **this is also literally Gap 1's fix, generalized**; recommend a single fix, not two.
3. Versioned `archive_close()` / Close History data model (Section D).
4. Reopen Step 1/Step 2 UI + transactional boundary.
5. Correction/reprocessing pipeline (new data + new commentary against the reopened period).
6. Downstream dependency propagation + chronological blocking.
7. Close Validation Status UI surfacing all of the above.
8. Close History UI surfacing version/lineage (depends on, and should be coordinated with, Gap 2's historical-navigation work — see B).

## F. Testability

The instruction's own Section 13-F scenario list (15 items) is complete and I have no changes to recommend to it — it correctly separates version creation, **technical regeneration confirmed unaffected** (scenario 11 — no business-level reprocessing state, per D.E/D.F), **business-level reprocessing following genuine own-state change**, chronological blocking, and cancel/abandon safety as distinct test cases rather than one composite "reopen works" case. I'd add one: **16. A reopen Step 1/Step 2 sequence run against a period with *no* downstream periods at all** (the terminal period), to confirm the propagation/blocking logic degrades correctly to a no-op rather than erroring on an empty downstream set.

---

## G. PM Decision — End-to-End Product Demonstration Milestone Expanded (this session)

**Decision recorded:** the End-to-End Product Demonstration milestone (Handbook Section 4/"Current Milestone") is expanded from two scenarios to three. The prior open question in this report is now resolved by that decision, not reopened.

- **Scenario 1** — wrong/changed data (unchanged).
- **Scenario 2** — correct data (unchanged).
- **Scenario 3 (new)** — the complete reopen → correction → reprocessing → re-approval → archival → lineage journey, run against a previously closed period, ending in the same HTML/PPTX executive-output requirement as Scenarios 1–2, plus visible Close Validation Status/Close History evidence of the version lineage and dependency-propagation state.

**Consequences, made explicit rather than left implicit:**

1. **D13's path to Verified is unaffected.** D13 (Human Approval Gate blocking behavior) still gates only on the Section H/J Phase 4-6 UAT set. D15 does not add a new precondition to D13 — they are independent decisions that both happen to feed the same milestone.
2. **The milestone itself now has two independent blockers instead of one:** (a) D13 reaching Verified (Section H/J UAT, unchanged, already tracked), and (b) D15 reaching an implementation+verification state sufficient to run Scenario 3. Previously the milestone's only gate was (a). This is a real scope/timeline consequence of the expansion, not a hidden cost — recording it here so it isn't discovered later as a surprise.
3. **The milestone's "explicit final outputs" section** (Handbook, Current Milestone) must be updated: Scenario 3 needs its own HTML/PPTX pair (or an explicit decision that Scenario 3 reuses Scenario 1/2's outputs with an added lineage view — that's a product decision for you, not one I'm making silently here).
4. **Sequencing changes:** D15's Builder Brief is no longer "separate product scope, timeline flexible." It is now a critical-path dependency of the graded milestone. This raised the priority of confirming the Section D architecture — **since resolved: Section D is now Final** (see Section D's status line and the updated sequencing recommendation below).
5. **Write-up document** (Section 4/11, deferred until the milestone completes) is now deferred behind Scenario 3 as well, not just Scenarios 1–2. Flagging given the project's stated deadline-driven context (Handbook Section 1) — this is a timeline fact for you to weigh, not a recommendation to descope.

**Governance artifacts this decision additionally touches (added to Section C's update list):**
- Handbook "Current Milestone: End-to-End Product Demonstration" section — add Scenario 3's definition, boundaries, and explicit outputs.
- Handbook "Current Release" table's `Next milestone` row — update to reflect the added blocker.
- Section 9 (Review & Acceptance History) — the existing "End-to-End Product Demonstration (full milestone)" row's "Not started" scope description needs the Scenario 3 addition reflected once v2.17 is drafted.

No part of this expands D15's own authorized capability (Section A) — Scenario 3 exercises exactly the capability already authorized; it does not add new capability requirements beyond what's in the source instruction (e.g., it does not imply the demonstration needs a *second* reopen or a *second* correction chain — one confirmed pass through the full journey satisfies "complete journey," per the instruction's own Section 13 test list, items 7–15, which this scenario is built from).

## Recommendation on sequencing (updated)

1. Push the already-approved Gap 4 narrow Brief now (unblocked, unrelated to this decision, and now higher-priority given G.4).
2. ~~Confirm/amend the Section D architecture proposal~~ — **Section D is now Final** (accepted, with D.E/D.F wording clarified through this session's exchanges). No longer a blocker.
3. I draft Handbook v2.17 in one pass, recording D15 (Section C) *and* the milestone expansion (Section G) together, so the Handbook doesn't go through two partial revisions describing the same decision session.
4. I draft the Builder Brief against the confirmed architecture, applying the Minimum-Scope Test per item.
