# Builder Brief D17-BB-001 — Movement-Concentration Narrative Component Detail (Net-Variance Basis)

**Governing Decision Log entry:** D17
**Authority:** Principal (authorized 2026-09-17)
**Architect:** Claude
**Status:** RELEASED TO BUILDER — Scope Authorization Gate completed 2026-09-17
**Independent from:** D15 Item 2, D16 (no file overlap, no shared logic)

---

## 0. Read this section first — what already existed and required NO new approval

Builder should not re-derive or second-guess the following; they are existing, already-Verified canonical behavior and are listed here only so this Brief is self-contained and Builder doesn't waste time treating them as open questions:

- **`Total Variance ($)` is already the net, signed sum of segment variances** (`sub["Variance ($)"].sum()`) — unchanged by this Brief.
- **`CONCENTRATION_THRESHOLD = 0.60`** is an existing, already-governed constant in `rollups.py` — unchanged value, unchanged name.
- **Data sources** `Rev_by_Region_Q`, `Rev_by_Product_Q`, `Exp_by_Dept_Cat_Q` (and their `_Y` equivalents) already exist in canonical `rollups_output.xlsx` — confirmed present by direct inspection, nothing to build here.
- **Sheet name `Breadth_Concentration_Q` / `Breadth_Concentration_Y` is retained as-is.** A rename was considered and explicitly deferred (see Section 6) — do not rename.
- **Column name `"Breadth/Concentration Flag"` is retained as-is** for the same reason.
- **The four observation types, their fixed segment lists, and their `Rev_by_Region_Q`/`Rev_by_Product_Q`/`Exp_by_Dept_Cat_Q` sourcing** were authorized under D17 already and are not re-litigated here.
- **`period_lifecycle.py`, `close_history.py`, `close_validation.py`** are out of scope — do not touch, per D17's original exclusion, reconfirmed.

What follows is only what actually changed or is newly authorized.

---

## 1. Objective

Two things, delivered together (they must ship together — see Section 5, Dependencies):

1. **Fix `build_breadth_concentration()` in `rollups.py`** so its concentration determination is based on **net variance**, preserves **sign**, and distinguishes a segment **driving** the net movement from one **offsetting** it — replacing the current gross-variance-based, sign-blind, magnitude-only logic.
2. **Add per-segment component-breakdown detail to Phase 7 narrative output** (`commentary_workflow.py` / `northwind_narrative_prompt.md`) for all four observation types, using the same net-variance, signed convention as (1), so the two never contradict each other.

---

## 2. Why (1) is in scope, not just (2)

The original D17 package assumed the existing `build_breadth_concentration()` output ("Broad-based across 3 of 4 segments…") was correct and only needed a new per-segment detail line added underneath it. Architect review found the existing function's concentration test uses **gross** variance (`sub["Variance ($)"].abs().sum()`) as its denominator, and picks a "top contributor" by raw magnitude regardless of sign. Both are now Principal-rejected as the analytical basis (this session). Since this logic already drives the sentence in every close's narrative today, shipping only a new net-based detail line underneath an old gross-based summary sentence would let the two disagree in the same narrative block. Confirmed dependency, not Architect preference — see Minimum-Scope note in the Scope Authorization Gate.

---

## 3. Required change — `rollups.py`, `build_breadth_concentration()`

Replace the function body with:

```python
CONCENTRATION_THRESHOLD = 0.60          # unchanged — existing governed constant
OFFSET_MATERIALITY_THRESHOLD = 0.20     # NEW — default, Architect-set, not yet Principal-confirmed (adjustable)


def build_breadth_concentration(df, dim_col, period_col, period_order, line_item_label,
                                 threshold=CONCENTRATION_THRESHOLD):
    rows = []
    for period in period_order:
        sub = df[df[period_col] == period].dropna(subset=["Variance ($)"])
        if sub.empty:
            continue
        total_var = sub["Variance ($)"].sum()          # net, signed — UNCHANGED
        gross_var = sub["Variance ($)"].abs().sum()     # kept, now supplementary only
        n_segments = sub[dim_col].nunique()

        if total_var == 0:
            rows.append({
                period_col: period, "Line Item": line_item_label,
                "Total Variance ($)": 0, "Gross Variance ($)": gross_var,
                "Top Driver": None, "Top Driver Share of Net Variance": np.nan,
                "Top Offsetting Segment": None, "Top Offsetting Share of Net Variance": np.nan,
                "Breadth/Concentration Flag": "No net movement (flat period-over-period)",
            })
            continue

        net_sign = 1 if total_var > 0 else -1
        drivers = sub[np.sign(sub["Variance ($)"]) == net_sign]
        offsetters = sub[np.sign(sub["Variance ($)"]) == -net_sign]
        n_drivers = len(drivers)

        top_driver_row = drivers.loc[drivers["Variance ($)"].abs().idxmax()] if not drivers.empty else None
        top_offset_row = offsetters.loc[offsetters["Variance ($)"].abs().idxmax()] if not offsetters.empty else None

        top_driver = top_driver_row[dim_col] if top_driver_row is not None else None
        top_driver_share = (top_driver_row["Variance ($)"] / abs(total_var)) if top_driver_row is not None else np.nan
        top_offset = top_offset_row[dim_col] if top_offset_row is not None else None
        top_offset_share = (top_offset_row["Variance ($)"] / abs(total_var)) if top_offset_row is not None else np.nan

        if top_driver_row is not None and top_driver_share >= threshold:
            flag = (f"Concentrated in {top_driver} ({top_driver_share:+.0%} of net variance, "
                     f"threshold {threshold:.0%}), driving the net movement")
        else:
            flag = f"Broad-based across {n_drivers} of {n_segments} segments driving the net movement"

        if top_offset_row is not None and abs(top_offset_share) >= OFFSET_MATERIALITY_THRESHOLD:
            flag += f"; substantially offset by {top_offset} ({top_offset_share:+.0%} of net variance)"

        rows.append({
            period_col: period, "Line Item": line_item_label,
            "Total Variance ($)": total_var, "Gross Variance ($)": gross_var,
            "Top Driver": top_driver, "Top Driver Share of Net Variance": top_driver_share,
            "Top Offsetting Segment": top_offset, "Top Offsetting Share of Net Variance": top_offset_share,
            "Breadth/Concentration Flag": flag,
        })
    return pd.DataFrame(rows)
```

**Column changes:** `"Top Contributor"` / `"Top Contributor Share"` are replaced by the four new columns above (`Top Driver`, `Top Driver Share of Net Variance`, `Top Offsetting Segment`, `Top Offsetting Share of Net Variance`). This is a schema change to `breadth_all_q` / `breadth_all_y`, not additive-only — flag this explicitly in the Return Report, do not describe it as additive.

**Required companion edit — `Northwind_Financial_Dashboard.py`, line ~116:** the formatting dict keyed on `"Top Contributor Share"` will silently stop applying formatting once that column no longer exists. Update to format the four new column names instead (percentage formatting on the two `Share of Net Variance` columns; leave `Top Driver` / `Top Offsetting Segment` as plain text). This is required, not optional — it is a direct consequence of the schema change above, not new scope.

---

## 4. Required change — Phase 7 narrative component detail (D17's original scope, formula corrected)

Per-segment line, same file/module boundaries as the original D17 package (`commentary_workflow.py`, `northwind_narrative_prompt.md`; read-only: `rollups.py` beyond the change in Section 3):

```python
share = row["Variance ($)"] / abs(total_var)     # signed, net-based — matches Section 3 exactly
line = f"  {segment_name}: {fmt_money(row['Variance ($)'])}  | {share:+.0%}"
```

Assessment line: reuse the `"Breadth/Concentration Flag"` string produced by Section 3's corrected function, verbatim. Do not compute a second, separate threshold check in `commentary_workflow.py` — this was the specific inconsistency risk flagged and corrected earlier in Architect review; the two must derive from one calculation, not two.

Format, unchanged from prior sign-off:
```
Revenue (by Region) — Q4 2026
Total Variance: $121,919

Component Breakdown:
  North America: ($16,511)  | -14%
  EMEA:           $68,622   | +56%
  APAC:           $36,390   | +30%
  LATAM:          $33,417   | +27%

Assessment: Concentrated in EMEA (+56% of net variance, threshold 60%)... [or Broad-based, per Section 3 logic — reused verbatim]
```

Apply identically to all four observation types (Revenue by Region, Revenue by Product Line, Software & Tools by Department, Other Opex by Department), all periods, no conditional logic — per original D17 authorization.

---

## 5. Dependencies — explicit, not assumed

Section 3 and Section 4 **must ship in the same Builder submission.** Shipping Section 4 (new per-segment line) against the *old* Section 3 logic (gross-based) would recreate the exact narrative self-contradiction this Brief exists to prevent. This is a demonstrated dependency (see Section 2), not a scheduling convenience — do not split across separate Builder sessions.

No dependency on D15 (`period_lifecycle.py`, `close_history.py`) or D16. Both may proceed in parallel, independently.

---

## 6. Explicitly deferred — do NOT implement without separate authorization

- **Renaming `Breadth_Concentration_Q`/`_Y` or the generic "Concentration" terminology.** Considered, and deferred: it would require updating `governance/architect_reports/architect_alignment_report_period_lifecycle_reopen_correction.md` and `governance/builder_briefs/period_lifecycle_reopen_correction_brief.md`, both of which name this sheet explicitly as part of D15's architecture. Renaming it is not necessary to satisfy the Principal's net-variance/signed/driver-vs-offsetting requirement — only the calculation and the two flagged column/dict updates above are. Do not rename anything as part of this Brief.
- **Auto-generated "favorable" / "unfavorable" wording.** Not authorized. Signed `$` and `%` are sufficient; adding an English favorable/unfavorable judgment would require a revenue-vs-expense directionality rule that does not currently exist, and risks an invented interpretive claim under the Phase 7 no-invention boundary (Handbook Section 2a). Do not add this wording anywhere in the narrative output.

---

## 7. Defaults set by the Architect — not blocking, but flagged for Principal awareness

- `OFFSET_MATERIALITY_THRESHOLD = 0.20` — the offsetting-segment clause only appears in the flag when the top offsetter's share of net variance is ≥20%. Ship with this default; revisit if the Principal wants a different number after seeing real output.

---

## 8. Files — scope of changes

**Will be modified:**
- `rollups.py` — `build_breadth_concentration()` (Section 3)
- `commentary_workflow.py` — Phase 7 component-detail generation (Section 4)
- `northwind_narrative_prompt.md` — prompt instruction for component detail
- `Northwind_Financial_Dashboard.py` — one line, formatting-dict key update only (Section 3, required companion edit)

**Will be read, not modified:**
- `Rev_by_Region_Q`, `Rev_by_Product_Q`, `Exp_by_Dept_Cat_Q` sheet structures (unchanged)

**Do NOT modify:**
- `period_lifecycle.py`, `close_history.py`, `close_validation.py` — no D15/D16 overlap
- Anything under `governance/` — no D15 governance doc touch (rename deferred, Section 6)

---

## 9. Regression requirement — this is not purely additive

`build_breadth_concentration()` feeds the existing, already-Verified pipeline (Cycle 1–3 tie-outs; `rollups.py`'s own internal check at `breadth_total_check` against `pl_rev_var_check`). Because Section 3 changes this function's output schema and values, **the existing tie-out/regression suite must be re-run and reconfirmed clean**, not just a new fixture added for the new columns. Treat this the same as any other change to already-Verified pipeline output — per this project's standing Regression Discipline.

---

## 10. Acceptance Criteria

**Functional:**
- ✅ `Total Variance ($)` unchanged (still net, signed) — regression-confirmed identical to pre-change values
- ✅ `Top Driver` / `Top Offsetting Segment` correctly split by sign relative to net variance, not by magnitude alone — test with a case where the largest-magnitude segment is an offsetter, confirm it is NOT reported as "Concentrated in"
- ✅ Shares are signed; a negative-contributing segment never displays a positive percentage
- ✅ Flag string reused verbatim between `rollups.py` output and the Phase 7 narrative Assessment line — byte-identical, not independently regenerated
- ✅ All four observation types show component detail, every close, no conditionals
- ✅ Dashboard renders without exception with the new column set (formatting-dict fix confirmed live, not just code-reviewed)
- ✅ Existing tie-out/regression suite passes against the new logic

**Evidence required (Return Report):**
1. Before/after output for at least one period with a genuine offsetting segment (not just all-same-direction), demonstrating the driver/offset distinction working correctly
2. Full existing regression suite re-run against the new function, results included
3. Confirmation that `breadth_all_q`/`breadth_all_y`'s schema change is disclosed explicitly, not described as additive
4. Narrative sample showing Assessment line matches the `rollups.py`-computed flag string exactly (not independently derived)

---

## 11. Effort / Sequencing

No dependency on D15 or D16 — may proceed immediately, in parallel with either. Sections 3 and 4 ship together (Section 5).

---

**Prepared by:** Architect
**Principal Authorization:** Confirmed 2026-09-17 ("I, the principal, authorize")
**Ready for Builder:** YES
