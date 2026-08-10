# Builder Brief — Cost Structure: Department × Cost Category and Company-Wide Cost Category Views

**Status:** FINAL — v2, AUTHORITATIVE. Supersedes the v1 Brief issued 2026-08-09.
**Issued by:** Architect
**Date:** 2026-08-09 (final revision)
**Precedence:** This Brief is the single source of truth for this task's scope and acceptance criteria. Do not work from v1 or from any prior chat summary of scope — this document fully incorporates and replaces both. Where anything here conflicts with the Project Handbook on current *product state*, the Handbook wins; this Brief does not alter Handbook state on its own.

**Provenance note:** Presence of the required files below in the canonical GitHub repository is **Principal-confirmed, not independently Architect-verified** (private repository, no authenticated Architect-side access available). Builder must work from the actual GitHub versions of these files.

**What changed from the draft v2:** terminology standardized to "Cost Category" throughout (the underlying dataset/code field remains `Category` where technically appropriate — e.g. in code snippets and DataFrame column references); the Objective now accurately describes three analytical cuts rather than "two directions"; the dangling in-document reference to a Handbook/Governance note has been removed — that assessment is handled separately by the Architect, outside this Brief.

**What changed from v1 (for reference):** added a third analytical view (Cost by Cost Category, company-wide, no Department dimension) as new in-scope work; integrated previously-outstanding evidence requirements directly into this Brief's evidence section; Criterion 9 (Phase 2/3 D11 reproduction) is unchanged pending a separate, explicit decision on archived-file availability — not silently weakened.

---

## Objective

Give the Controller three complementary, visible cost-investigation views on the existing Cost Structure page (Information Architecture #3):

1. **Cost by Department** — already existing.
2. **Cost by Department × Cost Category** — this task's original scope.
3. **Cost by Cost Category, company-wide (no Department dimension)** — new in this revision.

Together these give a Controller three complementary analytical cuts to investigate a flagged cost variance: the overall department trend (view 1), which department and cost-category combination is driving it (view 2), and whether a cost category is moving broadly across the business or is concentrated within a single department (view 3) — using only information the product actually exposes, not internal validation-engine output.

## Required Files (from canonical GitHub repository)

- `Northwind_Financial_Dashboard.py` — dashboard source, to be extended
- `rollups.py` — pipeline; Department × Cost Category grain already extended under v1 scope; Cost Category-only grain to be added under this revision
- `close_validation.py` — read-only reference, to confirm both new views use the same Department/Category grain Phase 2/3 reads from
- `Northwind_Sample_Dataset.xlsx` (canonical, Q4 FY2026, repo root) — source data for tie-outs
- `requirements.txt` — pinned environment; install from this file only

**Open question, not yet resolved (see "Outstanding: Criterion 9" below):** whether the archived Q2/Q3 FY2026 vintage dataset files should be added to this list. Not added yet — pending an explicit principal decision on whether they can be supplied to Builder.

Not required for this task: `close_history.py` and `close_v1_v2_simulation.py` are **not implementation dependencies** of this task (this task does not touch close resolution), but `close_history.py` **is** required as an evidence artifact — see "Outstanding Evidence Requirements" below, item 3.

## In Scope

**Carried over from v1 (Department × Cost Category view):**
- Table/view on the Cost Structure page: rows = Department × Cost Category, columns = Current period, Prior period, Variance $, Variance %.
- Reuse existing rollup/data-access patterns wherever the required grain already exists; flag explicitly if a new rollup function is needed.
- Computed from the same canonical dataset and same Department/Category grain `close_validation.py` reads.

**New in this revision (Cost Category-only view):**
- A second new table/view on the Cost Structure page: rows = Cost Category only (no Department dimension), columns = Current period, Prior period, Variance $, Variance %, company-wide.
- Reuse the same generic rollup mechanism already established and verified for the Department-only and Department × Cost Category cuts (expected: `build_expense_rollup(["Category"], period_col, period_order)` — same function, same period logic, same `prior_shift`; confirm via inspection before treating this as a given).
- Rendered on the Cost Structure page, positioned near the Department × Cost Category view.
- Cost Category-only totals must reconcile exactly to the corresponding cost category totals summed across all departments in the Department × Cost Category view.
- Cost Category-only grand total (summed across all cost categories) must reconcile exactly to the existing Department-level expense total.

## Explicitly Out of Scope

- No redesign of the Cost Structure page's pre-existing sections: S&B volume/rate bridge, breadth/concentration, Opex/Employee.
- No change to `close_validation.py`, `close_history.py`, or any D10/D11/D12 logic or behavior.
- No change to revenue views, other dashboard pages, or approved KPI definitions.
- No new architectural decision is made or recorded by this Brief itself. Any Decision Log entry is handled separately by the Architect and requires principal approval before it is added to the Project Handbook.
- **The Cost Category-only view is dashboard-only for this task.** Do not extend Phase 2/3 flagging, plausibility checks, or Phase 4 matching/investigation logic to cost-category-level totals. This is a presentation-layer addition, not a validation-engine change.
- Do not treat this Brief as an opportunity to generally improve or restructure the dashboard.

## Acceptance Criteria

Each criterion requires actual evidence in the Return Report — real output, before/after numbers, actual delivered files — not a narrated or summarized claim.

### Department × Cost Category view (carried over from v1, unchanged)

1. Department-level totals in the Department × Cost Category view reconcile exactly to existing Cost Structure page department totals ($0.0000 diff).
2. Cost Category breakdown within each department sums to that department's total.
3. Current vs prior values match the same current/prior period definitions already used elsewhere in the pipeline — no new period logic invented.
4. Variance $ = Current − Prior, verified by direct calculation check.
5. Variance % = Variance $ / Prior, verified the same way; sign convention consistent with existing QoQ % elsewhere in the product.
6. The Department × Cost Category view is rendered and navigable on the Cost Structure page in a running dashboard session (AppTest or equivalent) — not just present in code.
7. **Regression — dashboard:** 8/8 tabs still render, 0 exceptions.
8. **Regression — pipeline:** 12/12 tie-outs still pass, $0.0000 diff.
9. **Regression — validation engine:** `close_validation.py` Phase 2/3 re-run against the canonical dataset reproduces D11's evidence exactly — Scenario 1: 0/0 flags; Scenario 2 (Customer Success/Other Opex): 1 Phase 2 flag; Scenario 3 (Sales & Marketing/Other Opex): 1 Phase 3 flag at QoQ +38.42%/headcount +1.0. **Status: unresolved, unchanged in this revision — see "Outstanding: Criterion 9" below. Not weakened or reinterpreted here.**
10. **Regression — existing Cost Structure sections:** the S&B bridge, breadth/concentration, and Opex/Employee sections continue to produce the same outputs and values as the pre-change baseline, with no functional regression. Byte-for-byte code identity is not required.
11. Any dependency that forces a change outside this Brief's stated scope is identified and flagged explicitly in the Return Report before being treated as acceptable.

### Cost Category-only view (new in this revision)

12. Cost Category-only totals reconcile exactly to the sum of that cost category's values across all departments in the Department × Cost Category view (internal consistency check, $0.0000 diff).
13. Cost Category-only grand total (summed across all cost categories) reconciles exactly to the existing Department-level expense total already established under Criterion 1 ($0.0000 diff).
14. Current vs prior values follow the same period definitions already established and verified for the other two views — no new period logic invented.
15. Variance $ = Current − Prior for the Cost Category-only view, verified by direct calculation check.
16. Variance % = Variance $ / Prior for the Cost Category-only view, verified the same way, consistent sign convention.
17. The Cost Category-only view is rendered and navigable on the Cost Structure page in a running dashboard session (AppTest or equivalent), positioned alongside the Department × Cost Category view.
18. If a new rollup call is required (expected: reuse of `build_expense_rollup` with `dim_cols=["Category"]`), confirm via direct inspection that no existing consumer of cost-category-level data is altered by this addition.
19. **Extended regression:** adding the Cost Category-only view does not alter the values produced by the Department view or the Department × Cost Category view — direct before/after comparison required, not inferred from a clean diff alone.

## Outstanding Evidence Requirements (integrated from prior Architect review, not yet satisfied)

The following are required in the next Return Report, in addition to the criteria above:

1. **Actual AppTest/dashboard execution evidence** — real output showing 8/8 tabs render with 0 exceptions, and both new views (Department × Cost Category, Cost Category-only) actually present and populated in a running session. Code presence alone is not sufficient (Criteria 6, 7, 17).
2. **Actual execution output from `evidence_scenario1_harness.py`** — the script alone was previously delivered without its stdout. Captured run output is required, not just the script.
3. **Canonical/unchanged `close_history.py` evidence** — either the actual file, or an explicit diff confirming it is byte-identical to the canonical repository version, since the scenario harness depends on it and no such confirmation has yet been provided.
4. **Canonical/unchanged `close_validation.py` evidence** — same requirement as above; not yet provided.
5. **Direct before/after value evidence for Criterion 10 (and its extension, Criterion 19)** — an explicit output comparison for the untouched/pre-existing sections, not inferred solely from diff cleanliness.
6. **Outstanding: Criterion 9.** Do not change Criterion 9's wording or requirement in this Brief. Whether the archived Q2/Q3 FY2026 vintage files needed to genuinely reproduce D11's Scenario 2/3 evidence can be supplied to Builder is an open question requiring an explicit principal decision — addressed separately from this Brief, not resolved by silently narrowing this criterion.

## Status Discipline

This Brief does not authorize Builder to mark any criterion, view, or Decision Log entry as Verified. Implementation Status changes only after the Architect independently reviews the actual Return Report and delivered files, and the principal gives final acceptance. Issuing this Brief does not itself update the Project Handbook or Decision Log.

**Not reopened by this task:** D10, D11, D12. Cycle 3 remains closed.

**Superseded:** the v1 Brief (`builder_brief_cost_structure_investigation_view.md`, issued 2026-08-09) and the draft v2 Brief (`builder_brief_cost_structure_investigation_view_v2.md`, pre-correction) are both superseded by this document and should be archived, not worked from.
