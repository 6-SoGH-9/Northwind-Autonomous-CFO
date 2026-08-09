# Builder Brief — Cost Structure: Department × Cost Type Investigation View

**Status:** Issued
**Issued by:** Architect
**Date:** 2026-08-09
**Precedence:** This Brief is authoritative for this task's scope and acceptance criteria (Source-of-Truth Precedence, Architect Permanent Instructions §2 / Handbook "Source of Truth"). Where anything here conflicts with the Project Handbook on current *product state*, the Handbook wins; this Brief does not alter Handbook state on its own.

**Provenance note:** Presence of the required files below in the canonical GitHub repository (`Northwind_Financial_Dashboard.py`, `rollups.py`, `close_validation.py`, `Northwind_Sample_Dataset.xlsx`, `requirements.txt`) is **Principal-confirmed, not independently Architect-verified** — the repository is private and no authenticated Architect-side access was available at time of issuance. Builder must work from the actual GitHub versions of these files, not a local copy of unconfirmed provenance.

---

## Objective

Give the Controller a visible **Department → Cost Type → Current vs Prior → Variance $ → Variance %** view on the existing Cost Structure page (Information Architecture #3), so a flagged cost variance can be investigated using information the product actually exposes — not internal validation-engine output the Controller cannot see today.

This task exists because the current Cost Structure page provides department-level opex totals, a S&B volume/rate bridge, breadth/concentration, and Opex/Employee — but no Department × Cost Type breakdown. Both of D11's real, Verified flagged items (Customer Success / Other Opex; Sales & Marketing / Other Opex) are category-level movements a Controller cannot currently see broken out. This gap was identified as blocking meaningful Phase 4–6 testing and is being closed first, per principal direction.

## Required Files (from canonical GitHub repository)

- `Northwind_Financial_Dashboard.py` — dashboard source, to be extended
- `rollups.py` — pipeline; confirm whether Department × Category grain is already computed internally
- `close_validation.py` — read-only reference, to confirm the new view uses the same Department/Category grain Phase 2/3 reads from
- `Northwind_Sample_Dataset.xlsx` (canonical, Q4 FY2026, repo root) — source data for tie-outs
- `requirements.txt` — pinned environment; install from this file only, never a bare `pip install`

Not required for this task: `close_history.py`, `close_orchestrator.py`, `close_v1_v2_simulation.py`, archived Q2/Q3 dataset files, `northwind_narrative_prompt.md`.

## In Scope

- New table/view on the existing Cost Structure page: rows = Department × Cost Type, columns = Current period, Prior period, Variance $, Variance %.
- Reuse existing rollup/data-access patterns wherever the required grain already exists.
- Add a new rollup function **only if** the required Department × Cost Type grain is not already computed — if so, this must be flagged explicitly in the Return Report as a dependency identified during implementation, not silently added.
- The new view must be computed from the same canonical dataset and same Department/Category grain that `close_validation.py` reads, so figures the Controller sees are traceable to the same numbers a Phase 2/3 flag would reference.

## Explicitly Out of Scope

- No redesign of the Cost Structure page's existing sections: S&B volume/rate bridge, breadth/concentration, Opex/Employee.
- No change to `close_validation.py`, `close_history.py`, or any D10/D11/D12 logic or behavior.
- No change to revenue views, other dashboard pages, or approved KPI definitions (Information Architecture, Handbook §3).
- No new architectural decision — this is an additive change within already-approved Information Architecture, not a redesign of it.
- Do not treat this as an opportunity to generally improve or restructure the dashboard.

## Acceptance Criteria

Each criterion requires actual evidence in the Return Report — real output, before/after numbers, actual delivered files — not a narrated or summarized claim.

1. Department-level totals in the new view reconcile exactly to existing Cost Structure page department totals (tie-out, $0.0000 diff).
2. Cost Type/Category breakdown within each department sums to that department's total (internal consistency check).
3. Current vs prior values match the same current/prior period definitions already used elsewhere in the pipeline — no new period logic invented.
4. Variance $ = Current − Prior, verified by direct calculation check, not assumed from a formula read.
5. Variance % = Variance $ / Prior, verified the same way; sign convention consistent with existing QoQ % elsewhere in the product.
6. The view is actually rendered and navigable on the Cost Structure page in a running dashboard session (AppTest or equivalent) — not just present in code.
7. **Regression — dashboard:** 8/8 tabs still render, 0 exceptions, using the same AppTest method established in Cycle 2 Task 4.
8. **Regression — pipeline:** 12/12 tie-outs still pass, $0.0000 diff.
9. **Regression — validation engine:** `close_validation.py` Phase 2/3 re-run against the canonical dataset reproduces D11's evidence exactly — Scenario 1: 0/0 flags; Scenario 2 (Customer Success/Other Opex): 1 Phase 2 flag; Scenario 3 (Sales & Marketing/Other Opex): 1 Phase 3 flag at QoQ +38.42%/headcount +1.0.
10. **Regression — existing Cost Structure sections:** the S&B bridge, breadth/concentration, and Opex/Employee sections continue to produce the same outputs and values as the pre-change baseline, with no functional regression. Byte-for-byte code identity is not required, since the underlying file will necessarily change.
11. Any dependency that forces a change outside this Brief's stated scope is identified and flagged explicitly in the Return Report before being treated as acceptable — never silently absorbed into the change.

## Evidence Required for Architect Review

- Before/after screenshots or AppTest output demonstrating the new view.
- Full tie-out logs (12/12).
- Phase 2/3 re-run output (Scenarios 1–3) against the canonical dataset.
- Explicit diff, or explicit confirmation of no diff, for the untouched Cost Structure sections versus the pre-change baseline.
- The actual changed/new files, not a description of the changes.

## Status Discipline

This Brief does not authorize Builder to mark any criterion, this task, or any Decision Log entry as Verified. Implementation Status changes only after the Architect independently reviews the actual Return Report and delivered files, and the principal gives final acceptance. Issuing this Brief does not itself update the Project Handbook.

**Not reopened by this task:** D10, D11, D12. Cycle 3 remains closed.
