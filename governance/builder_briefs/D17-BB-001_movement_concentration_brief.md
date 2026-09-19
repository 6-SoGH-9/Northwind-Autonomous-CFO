# Builder Brief D17-BB-001 — Movement-Concentration Narrative Component Detail (Net-Variance, Signed, Hierarchical Basis) — v2

**Governing Decision Log entry:** D17
**Supersedes:** v1 in full (text below). v1 is retained as historical record — see "What changed from v1," not struck through, per this project's standing addendum discipline.
**Authority:** Principal — original authorization 2026-09-17 (v1); corrections below authorized directly by Principal in Builder session 2026-09-19 ("Round 2"), plus a Builder-identified and Builder-fixed environment defect ("Round 3"), both confirmed against the Principal's own worked numbers and the Principal's own D15 test environment. This is a governance-synchronization rewrite, not new Architect-decided scope.
**Architect:** Claude
**Status:** Reflects Principal-tested, Builder-regression-tested design (per Builder Return Report, Round 3, HEAD `29691e7f94db58385f3aa5850a8f607e38992294`). **Architect independent verification (fresh clone, diff, regression re-run) is not yet performed this session** — pending before this can be described as canonical-synced. This Brief documents the corrected governing specification; it is not itself a canonical-promotion attestation.
**Independent from:** D15 Item 2, D16 (no file overlap, no shared logic — see Section 3a for the one *runtime* interaction, which is a compatibility accommodation, not a scope overlap).

---

## What changed from v1 (read this first)

1. **Gross variance removed entirely.** v1 kept `Gross Variance ($)` as a supplementary column. It is now gone — no gross-based calculation anywhere in Breadth/Concentration, Revenue or Expenses.
2. **Expenses restructured into a three-level hierarchy sharing one denominator** (Total Expenses → Category → Department), replacing v1's flat, category-siloed treatment. **Salaries & Benefits is added as a third Expenses category** (previously absent).
3. **Threshold split.** v1 had one `CONCENTRATION_THRESHOLD = 0.60` for everything. Expenses (all three hierarchy levels) now use **17%**; Revenue keeps **60%**. `OFFSET_MATERIALITY_THRESHOLD = 0.20` stays a single shared, independent constant across both domains — now Principal-confirmed, not an Architect default awaiting confirmation.
4. **Sign-bug fix.** v1's driver-check (`top_driver_share >= threshold`) is corrected to `abs(top_driver_share) >= threshold` in both domains — required once Expenses subtotals can be negative under the shared-denominator model, and applies to Revenue too per Principal instruction.
5. **New: module-boundary safety fix (Section 3a).** Not part of v1. A genuine environment defect — `rollups.py` failing to import standalone inside D15's isolated candidate-pipeline sandbox — was found and fixed. See Section 3a.
6. All of 1–4 were **Principal-directed in the Builder session**, confirmed against the Principal's own worked Q2 FY2025 numbers (row-by-row match, see Section 10) and Principal's own live testing. They are recorded here as authorized corrections to v1's Section 3/4/7, not Builder-initiated or Architect-initiated scope changes.

---

## 0. Read this section first — what already existed and required NO new approval

Unchanged from v1, plus one addition:

- `Total Variance ($)` is already the net, signed sum of segment variances (`sub["Variance ($)"].sum()`) — unchanged by this Brief, at every hierarchy level.
- Data sources `Rev_by_Region_Q`, `Rev_by_Product_Q`, `Exp_by_Dept_Cat_Q` (and `_Y` equivalents) already exist in canonical `rollups_output.xlsx` — nothing to build here.
- Sheet name `Breadth_Concentration_Q` / `Breadth_Concentration_Y` is retained as-is. Still deferred, not authorized — see Section 6.
- Column name `"Breadth/Concentration Flag"` is retained as-is.
- `period_lifecycle.py`, `close_history.py`, `close_validation.py` are out of scope — do not touch. **Confirmed unmodified in Round 3** (Return Report Section 4 — byte-identical to canonical throughout).
- **New this revision:** the four observation types' fixed segment lists are unchanged, but Expenses now has a fourth, higher level ("Total Expenses") sitting above them, sharing their denominator — this is not a fifth observation type, it's a new row in the existing Expenses hierarchy. Do not treat it as a new observation category requiring separate authorization.

---

## 1. Objective

Three things, delivered together (Sections 3 and 4 must ship together — unchanged rule, see Section 5; Section 3a ships with them because it lives in the same file and was required to make the others runnable in D15's environment):

1. Fix `build_breadth_concentration()` in `rollups.py` so concentration is based on **net, signed variance**, distinguishes a segment **driving** the net movement from one **offsetting** it, and — for Expenses specifically — evaluates every level (Total / Category / Department) against **Total Expenses' own net variance**, never a Category subtotal.
2. Add per-segment component-breakdown detail to Phase 7 narrative output (`commentary_workflow.py` / `northwind_narrative_prompt.md`) for all four observation types plus the new Expenses hierarchy levels, using the identical signed convention and identical denominator as (1), so the two never contradict each other.
3. Make `rollups.py`'s import of `commentary_workflow` fail **safely** rather than fatally when run outside the full dashboard checkout (D15's isolated candidate-pipeline sandbox), since that sandbox has no use for narrative generation and should not be broken by a Brief that never touches it.

---

## 2. Why (1) and (3) are in scope, not just (2)

**(1):** unchanged from v1 — the pre-existing function used gross variance and magnitude-only "top contributor" selection, both Principal-rejected as the analytical basis. Round 2 additionally established that a **flat, category-siloed** Expenses treatment was itself wrong: your own worked example (Software & Tools' negative category subtotal, with G&A still correctly reported as the "driver") only resolves correctly if every level shares Total Expenses' own denominator and sign reference. This is not an Architect elaboration — it's the specific mechanism your worked numbers require, confirmed row-by-row (Section 10).

**(3):** confirmed by direct reproduction of a real failure in your own D15 test environment (`ModuleNotFoundError: No module named 'commentary_workflow'`, raised from `/tmp/d15_candidate_<id>/rollups.py`). D15's architecture already depends on `rollups.py` being safely standalone-importable — that's not new information this Brief introduces, it's an existing constraint this Brief's Section 4 wiring violated by adding a hard top-level import. Leaving it unfixed would mean this Brief, though independent of D15 in scope, silently breaks a D15 workflow at runtime. Fixing it is the minimum necessary to make Sections 3–4 actually deployable, not new functionality.

---

## 3. Required change — `rollups.py`, `build_breadth_concentration()`

**Behavioral specification** (Builder's actual implementation is the artifact of record; this documents the confirmed, Principal-tested design — Architect has not yet independently diffed the pushed code against this spec):

- `CONCENTRATION_THRESHOLD` splits into two: **Revenue = 0.60** (unchanged value/name where it already applied), **Expenses (all three levels) = 0.17** (new).
- `OFFSET_MATERIALITY_THRESHOLD = 0.20` remains a single constant shared by both domains, independent of either concentration threshold.
- `Gross Variance ($)` is removed from the function's output entirely — not computed, not displayed, at any level.
- The function gains one new optional parameter, `grand_total_by_period` (a `{period: total}` dict). When supplied:
  - it overrides the **% share denominator** and the **sign reference** used to classify a row as driver vs. offsetter;
  - it does **not** override the row's own **displayed `Total Variance ($)`**, which always remains that row's own subtotal.
  - When omitted (Revenue calls, and the "Expenses" Total row itself), the function behaves exactly as before — own subtotal is both the displayed total and the denominator.
- Driver/offsetter classification: `abs(top_driver_share) >= threshold` (both domains — the sign-bug fix; **not** `top_driver_share >= threshold` as in v1's draft).
- Expenses is computed as three tiers against one shared source of truth:
  1. **Total Expenses** ("Expenses" line item) — own subtotal = denominator (no `grand_total_by_period` needed; segments already sum to it by construction).
  2. **Category** (Salaries & Benefits — new; Software & Tools; Other Opex) — `grand_total_by_period` = the Total Expenses row's own computed total, read directly off that row's output (not recomputed independently), keyed by period.
  3. **Department**, nested under each Category — same `grand_total_by_period` as its parent Category (i.e., Total Expenses' total, not the Category's own subtotal).
- Revenue is unchanged in structure: own total, own denominator, 60% threshold, no `grand_total_by_period`.
- New internal tie-out check required: the "Expenses" Total row's own net variance must independently tie to `pl_q`'s `Total Opex QoQ/YoY Var ($)` — same pattern as the existing Revenue-by-Region tie-out. This becomes the project's 19th internal tie-out (was 18).

**Companion edit — `Northwind_Financial_Dashboard.py`:** the formatting dict must drop the `Gross Variance ($)` entry (no longer produced) and the Cost Structure caption must state both thresholds separately (60% Revenue / 17% Expenses) rather than a single shared number. Required, not optional — direct consequence of the schema/threshold change.

**Column changes (still non-additive — say so explicitly in any Return Report, per v1's standing instruction, now doubly true):** `"Top Contributor"` / `"Top Contributor Share"` are replaced by `Top Driver`, `Top Driver Share of Net Variance`, `Top Offsetting Segment`, `Top Offsetting Share of Net Variance` — unchanged from v1. `Gross Variance ($)` is now removed, not merely de-emphasized.

---

## 3a. Required change — `rollups.py`, module-boundary safety (new, Round 3)

**Problem:** `rollups.py`'s top-level `import commentary_workflow` (added to wire Section 4) breaks when `rollups.py` is executed standalone in D15's isolated candidate-pipeline sandbox, which stages only `rollups.py` (plus dataset/close-history files) without `commentary_workflow.py` co-located. That sandbox never calls narrative generation — it only needs Phase 2/3 deterministic tie-out logic — so it should not fail to import at all.

**Required behavior:**
- Guard the import: `try: import commentary_workflow; COMMENTARY_WORKFLOW = commentary_workflow; except ImportError: COMMENTARY_WORKFLOW = None`.
- `build_user_prompt()`'s component-detail wiring must check `COMMENTARY_WORKFLOW is not None` before calling into it.
- When `None`: every line item falls back to the pre-Section-4, one-line summary (i.e., the behavior that existed before this Brief) — not a partial failure, not a crash, not a silently empty section.
- This is confined to `rollups.py`. **Do not touch `period_lifecycle.py`** — it is not the source of the defect and remains out of scope per Section 0.

**Evidence required (already produced once by Builder, needs Architect independent reproduction before canonical promotion):**
- A standalone sandbox (only `rollups.py` + `close_history.py` + dataset — matching the real traceback's file layout) imports cleanly, all 19 tie-outs still run and pass, `COMMENTARY_WORKFLOW is None` confirmed, and `python3 rollups.py`'s `__main__` narrative-demo path exits 0 with no exceptions.
- The normal full-checkout environment (both files present) still resolves `COMMENTARY_WORKFLOW is not None` and passes the full regression suite unchanged (19/19 + 49/49 + 0 AppTest exceptions).

---

## 4. Required change — Phase 7 narrative component detail

Same file/module boundaries as v1 (`commentary_workflow.py`, `northwind_narrative_prompt.md`; `rollups.py` read-only beyond Sections 3/3a). Two changes from v1:

- `build_movement_component_detail()` (or equivalent) now takes **two** separate values where v1 had one: `total_var` (the row's own subtotal — used for the header line) and `share_reference_total` (the applicable `grand_total_by_period` value, or `None` — used only for the per-segment `%` calculation). These must not be collapsed back into one parameter; Category/Department rows genuinely need a different value for each.
- Whatever internal source-mapping structure drives this (e.g. `MOVEMENT_COMPONENT_SOURCES_Q`/`_Y`) must carry a third element per entry — the applicable `share_reference_total` dict, or `None` for Revenue and the Expenses Total row.
- Assessment line: reused **verbatim** from Section 3's `"Breadth/Concentration Flag"` output — unchanged rule from v1. Do not compute a second, independent threshold check in `commentary_workflow.py`.
- Apply to all four original observation types **plus** the three new Expenses hierarchy levels (Total, Category, Department) — same signed, net-based, shared-denominator convention throughout, no conditional logic per line item.

---

## 5. Dependencies — explicit, not assumed

Unchanged core rule: **Sections 3, 3a, and 4 ship together.** Shipping narrative detail (Section 4) against pre-fix concentration logic (Section 3), or shipping either without the import guard (Section 3a), reproduces exactly the failure modes this Brief exists to prevent — narrative/summary disagreement in the first case, a hard environment crash in the second.

**No dependency on D15 (`period_lifecycle.py`, `close_history.py`) or D16** in the sense of shared logic or file overlap — that remains true. Section 3a is a **runtime compatibility accommodation** for D15's existing, already-authorized sandboxed-execution design, not new coupling this Brief is introducing into D15 itself. D15's own files are not modified.

---

## 6. Explicitly deferred — do NOT implement without separate authorization

Unchanged from v1, plus one addition:

- Renaming `Breadth_Concentration_Q`/`_Y` or the generic "Concentration" terminology. Still deferred — still touches D15's governance documents, still not necessary to satisfy the Principal's requirements.
- Auto-generated "favorable"/"unfavorable" wording. Still not authorized — still risks an invented interpretive claim under the Phase 7 no-invention boundary (Handbook Section 2a).
- **New — the long-term shape of the `rollups.py` → `commentary_workflow.py` coupling.** Section 3a's guarded import makes the *current* shape safe. It does not settle whether that's the *right* long-term shape (e.g., moving the wiring elsewhere so `rollups.py` never needs to know about `commentary_workflow` at all). This is flagged as a **Decision Needed** item for the Principal/Architect, not resolved by this Brief, and not something Builder should redesign unilaterally.

---

## 7. Defaults and thresholds — Principal-confirmed this revision

- `CONCENTRATION_THRESHOLD` (Revenue) = **0.60** — unchanged.
- `CONCENTRATION_THRESHOLD` (Expenses, all three levels) = **0.17** — new, Principal-set (not an Architect default).
- `OFFSET_MATERIALITY_THRESHOLD` = **0.20** — Principal-confirmed as a single constant shared across both domains, independent of either concentration threshold. (v1 listed this as an Architect default awaiting confirmation; that confirmation has now happened.)

---

## 8. Files — scope of changes

**Will be modified:**
- `rollups.py` — `build_breadth_concentration()` (Section 3), import guard (Section 3a)
- `commentary_workflow.py` — Phase 7 component-detail generation (Section 4)
- `northwind_narrative_prompt.md` — prompt instruction, updated for the hierarchy and threshold split
- `Northwind_Financial_Dashboard.py` — formatting-dict update (Section 3), caption update for dual thresholds

**Will be read, not modified:** `Rev_by_Region_Q`, `Rev_by_Product_Q`, `Exp_by_Dept_Cat_Q` sheet structures.

**Do NOT modify:** `period_lifecycle.py`, `close_history.py`, `close_validation.py`; anything under `governance/`.

---

## 9. Regression requirement — this is not purely additive

Unchanged principle from v1, updated count: the internal tie-out suite must be re-run and reconfirmed clean at **19/19** (was 18 — the new Expenses-total-vs-`pl_q` check is the 19th), not merely a new fixture appended for the new columns. `build_test/commentary_workflow_demo.py` must remain clean at 49/49. Both the isolated-sandbox and full-checkout environments must be exercised per Section 3a.

---

## 10. Acceptance Criteria

**Functional:**
- ✅ `Total Variance ($)` at every hierarchy level unchanged (still each row's own net, signed subtotal)
- ✅ `Gross Variance ($)` is absent from output entirely — not present, not zeroed, not hidden
- ✅ Expenses Category/Department rows' `%` shares and driver/offsetter classification are computed against **Total Expenses' own net variance**, confirmed by a case where a Category's own subtotal is negative but a Department within it is still correctly reported as the driver (the Software & Tools / G&A case)
- ✅ Self-consistency check: each Category's own Department shares sum to that Category's own share of Total Expenses (not to 100%) — reproduced for all three Categories
- ✅ Revenue and the Expenses Total row use `abs(top_driver_share) >= threshold`; Expenses Category/Department rows use the 17% threshold, Revenue uses 60%
- ✅ `OFFSET_MATERIALITY_THRESHOLD` (0.20) applied identically and independently of either concentration threshold
- ✅ Flag string reused verbatim between `rollups.py` output and the Phase 7 narrative Assessment line for every row, including the new hierarchy levels
- ✅ New 19th tie-out (Expenses Total net variance vs. `pl_q`'s Total Opex Var) passes
- ✅ Dashboard renders without exception under the new column set and dual-threshold caption
- ✅ Standalone D15-sandbox import of `rollups.py` succeeds with `COMMENTARY_WORKFLOW is None`, all 19 tie-outs pass, narrative demo path exits 0
- ✅ Full-checkout import resolves `COMMENTARY_WORKFLOW is not None`, full regression (19/19 + 49/49 + 0 AppTest exceptions) passes

**Evidence required (Return Report):**
- Worked-number reproduction against at least one full Principal-supplied table, row-by-row
- Live narrative output (AppTest) for at least one period showing the full Expenses hierarchy (Total + 3 Categories, at least one Department expansion)
- Self-consistency arithmetic shown explicitly (Category share = sum of its Department shares)
- Full regression suite results, both environments (sandbox and full-checkout)
- Explicit disclosure that this is a schema change, not additive, and that `Gross Variance ($)` is removed (not merely unused)
- Confirmation `period_lifecycle.py` and everything under `governance/` remain byte-identical to canonical

---

## 11. Effort / Sequencing

Unchanged: no dependency on D15 or D16: proceeds independently. Sections 3, 3a, and 4 ship together (Section 5).

---

**Architect note (not part of the Brief's authorization text):** this rewrite records Principal-directed design already implemented and tested by you and Builder. It is not, on its own, a canonical-promotion verdict — independent fresh-clone/diff/regression verification by the Architect is still owed before this reaches "Verified/canonical-synced" status in Handbook terms. Separately flag the Handbook/D17 provenance gap (no D15/D16/D17 entries in canonical `project_handbook.md` v2.19) as a housekeeping item that should close alongside that verification, not before it.
