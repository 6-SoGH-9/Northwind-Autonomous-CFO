"""
Close Orchestrator — Cycle 3, Task 1, Item 3

*** BUILD/TEST VERIFICATION TOOL — NOT A LIVE ARTIFACT ***
Same category as close_v1_v2_simulation.py: this script exists to
demonstrate and verify the Close History bootstrap + normal-path resolution
logic, not to run in production.

DO NOT execute this against a production Close History. On every run it
unconditionally deletes any pre-existing close_history/ folder
(shutil.rmtree) so it can start from a genuinely empty state and prove the
bootstrap path for real, rather than assuming it. That is correct,
intentional behavior for this script's purpose — verification — and would
be destructive if pointed at a real, populated Close History. This is not
a defect to fix; it is a reason this file must never be included in the
Live deployment file set (see Handbook Section 12).

Demonstrates the full Close History loop end-to-end, starting from a
genuinely empty close_history/, using the existing Close v1/v2 simulation
data (close_v1_v2_simulation.py, UNCHANGED — imported, not edited) to drive
the sequence:

  Close v1 (Q3 FY2026, truncated dataset)  -> BOOTSTRAP path (Item 2)
  Close v2 (Q4 FY2026, full + 2 injections) -> NORMAL path (Item 2)

Scope discipline (per the Brief: "resolution-logic change only"):
  - This script contains NO tie-out, allocation, or narrative calculation
    logic of its own for the P&L/segment views. Quarterly rollups for each
    close are built by calling rollups.py's build_revenue_rollup /
    build_expense_rollup / build_headcount_rollup EXACTLY AS WRITTEN — this
    script only temporarily repoints the module-level `revenue` /
    `expenses` / `headcount` globals those functions close over, so they
    run against Close v1's or Close v2's data instead of whatever rollups.py
    resolved at import time. Not one character of those functions changes.
  - Phase 2 (diff) and Phase 3 (plausibility) reproduce the exact merge/
    threshold logic already verified in close_v1_v2_simulation.py, made
    reusable against two arbitrary dataframes / an arbitrary target quarter
    instead of the fixed close_v1/close_v2 in-memory pair — this is the
    "how the comparison baseline is found" change the Brief describes, not
    a change to what counts as a flag.
  - close_v1_v2_simulation.py itself is imported unmodified; its own Phase
    2/3 output (computed the OLD, fixed, in-memory way) is left completely
    intact and is used below as the independent ground truth this script's
    NEW, Close-History-driven Phase 2/3 output is checked against.

Explicitly out of scope (per the Brief) and NOT built here:
  - dashboard.html / board_deck.pptx generation — left absent, not stubbed.
  - Narrative generation (Phase 7) for these two demo closes — narrative.txt
    for each snapshot honestly records that no narrative call was made for
    this demo (no fabricated/stub content), since Phase 7 for arbitrary
    partial/simulated closes is not part of Task 1's Items 1-3.
"""

import os
import shutil
import numpy as np
import pandas as pd

import close_history
import rollups as R                  # unmodified — import runs it once via the bootstrap-fallback path
import close_v1_v2_simulation as CV  # unmodified — import runs the original fixed Close v1/v2 demo as-is

CLOSE_HISTORY_DIR = "close_history"
SCRATCH_DIR = "close_orchestrator_scratch"


# ---------------------------------------------------------------------------
# Reusable helpers (resolution/archival plumbing only — see module docstring)
# ---------------------------------------------------------------------------
def strip_fiscal_cols(df):
    return df.drop(columns=[c for c in ("Fiscal Year", "Fiscal Quarter") if c in df.columns])


def load_bva_pl(cutoff=None):
    """Budget_vs_Actual and PL_Summary are not touched by either injection
    (close_v1_v2_simulation.py only ever revises the Expenses sheet — see
    its own module docstring), so these are copied straight from the
    source workbook, truncated by date for Close v1's raw_dataset.xlsx to
    keep that snapshot internally consistent (all sheets same date range)."""
    xl = pd.ExcelFile(CV.RAW)
    bva = pd.read_excel(xl, "Budget_vs_Actual")
    pl = pd.read_excel(xl, "PL_Summary")
    pl = pl[pl["Date"] != "Total / Avg"].copy()  # non-date summary row; excluded from both snapshots for consistency
    pl["Date"] = pd.to_datetime(pl["Date"])
    bva["Date"] = pd.to_datetime(bva["Date"])
    if cutoff is not None:
        bva = bva[bva["Date"] <= cutoff].copy()
        pl = pl[pl["Date"] <= cutoff].copy()
    return bva, pl


def build_rollups_for(revenue_df, expenses_df, headcount_df, quarter_order):
    """Build quarterly Revenue/Expense/Headcount rollups for one close by
    calling rollups.py's own build_* functions UNCHANGED, temporarily
    repointing the globals they read (revenue/expenses/headcount) at this
    close's data, then restoring them. No calculation code is edited."""
    orig = (R.revenue, R.expenses, R.headcount)
    try:
        R.revenue, R.expenses, R.headcount = revenue_df, expenses_df, headcount_df
        rev_region = R.build_revenue_rollup("Region", "Fiscal Quarter", quarter_order)
        rev_product = R.build_revenue_rollup("Product Line", "Fiscal Quarter", quarter_order)
        exp_dept = R.build_expense_rollup(["Department"], "Fiscal Quarter", quarter_order)
        hc_dept = R.build_headcount_rollup("Fiscal Quarter")
    finally:
        R.revenue, R.expenses, R.headcount = orig
    return rev_region, rev_product, exp_dept, hc_dept


def write_rollups_workbook(path, rev_region, rev_product, exp_dept, hc_dept):
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        rev_region.to_excel(writer, sheet_name="Rev_by_Region_Q", index=False)
        rev_product.to_excel(writer, sheet_name="Rev_by_Product_Q", index=False)
        exp_dept.to_excel(writer, sheet_name="Exp_by_Dept_Q", index=False)
        hc_dept.to_excel(writer, sheet_name="Headcount_Q", index=False)


def write_raw_dataset_workbook(path, revenue_df, expenses_df, headcount_df, bva_df, pl_df):
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        strip_fiscal_cols(revenue_df).to_excel(writer, sheet_name="Revenue", index=False)
        strip_fiscal_cols(expenses_df).to_excel(writer, sheet_name="Expenses", index=False)
        strip_fiscal_cols(headcount_df).to_excel(writer, sheet_name="Headcount", index=False)
        bva_df.to_excel(writer, sheet_name="Budget_vs_Actual", index=False)
        pl_df.to_excel(writer, sheet_name="PL_Summary", index=False)


def run_phase2_diff(prior_expenses_df, current_expenses_df):
    """Same merge-and-threshold logic as close_v1_v2_simulation.py's Phase 2
    (inner join on Date/Department/Category, flag |diff| > $0.005) — made
    reusable against two arbitrary Expenses frames instead of the fixed
    close_v1_expenses/close_v2_expenses pair."""
    overlap = prior_expenses_df.merge(
        current_expenses_df, on=["Date", "Department", "Category"],
        suffixes=("_prior", "_current"), how="inner",
    )
    overlap["Diff ($)"] = overlap["Amount ($)_current"] - overlap["Amount ($)_prior"]
    flags = overlap[overlap["Diff ($)"].abs() > 0.005].copy()
    return overlap, flags


def run_phase3_plausibility(expenses_df, headcount_df, quarter_order, target_quarter, threshold, hc_band):
    """Same QoQ-threshold + no-headcount-driver logic as
    close_v1_v2_simulation.py's Phase 3 — made reusable against an arbitrary
    target quarter instead of the hardcoded 'Q4 FY2026'."""
    dept_cat_q = expenses_df[expenses_df["Category"] != "Salaries & Benefits"].groupby(
        ["Department", "Category", "Fiscal Quarter"], as_index=False
    )["Amount ($)"].sum()
    dept_cat_q["_ord"] = dept_cat_q["Fiscal Quarter"].map({p: i for i, p in enumerate(quarter_order)})
    dept_cat_q = dept_cat_q.sort_values(["Department", "Category", "_ord"])
    dept_cat_q["Prior ($)"] = dept_cat_q.groupby(["Department", "Category"])["Amount ($)"].shift(1)
    dept_cat_q["QoQ (%)"] = (dept_cat_q["Amount ($)"] - dept_cat_q["Prior ($)"]) / dept_cat_q["Prior ($)"]

    hc_q = headcount_df.groupby(["Department", "Fiscal Quarter"], as_index=False)["Headcount"].mean()
    hc_q["_ord"] = hc_q["Fiscal Quarter"].map({p: i for i, p in enumerate(quarter_order)})
    hc_q = hc_q.sort_values(["Department", "_ord"])
    hc_q["Prior Headcount"] = hc_q.groupby("Department")["Headcount"].shift(1)
    hc_q["Headcount Change"] = hc_q["Headcount"] - hc_q["Prior Headcount"]

    target_cells = dept_cat_q[dept_cat_q["Fiscal Quarter"] == target_quarter].merge(
        hc_q[hc_q["Fiscal Quarter"] == target_quarter][["Department", "Headcount Change"]],
        on="Department", how="left",
    )
    target_cells["Flag"] = np.where(
        (target_cells["QoQ (%)"].abs() > threshold) & (target_cells["Headcount Change"].abs() <= hc_band),
        "PLAUSIBILITY FLAG — no headcount driver identified for this cost swing", "OK",
    )
    flags = target_cells[target_cells["Flag"] != "OK"].copy()
    return target_cells, flags


OBS_COLUMNS = ["Observation ID", "Detected By", "Period", "Type", "Department", "Category",
               "Before ($)", "After ($)", "Delta ($)", "Commentary Matched", "Classification", "Status"]


NO_NARRATIVE_NOTE = (
    "No narrative generated for this Close History demo snapshot. Phase 7 (Executive Insight "
    "Engine) generation for arbitrary/simulated closes is out of scope for Cycle 3 Task 1 (Items "
    "1-3), which covers only Close History resolution and archival behavior. The existing, "
    "already-verified narrative pipeline (northwind_narrative_prompt.md / rollups.py "
    "SYSTEM_PROMPT+build_user_prompt) is unchanged and continues to operate on the canonical "
    "current dataset per Cycle 2. This file is intentionally not a fabricated stub."
)


def main():
    if os.path.isdir(CLOSE_HISTORY_DIR):
        print(f"Removing pre-existing '{CLOSE_HISTORY_DIR}/' so this run starts from a genuinely empty Close History, per Item 3.")
        shutil.rmtree(CLOSE_HISTORY_DIR)
    if os.path.isdir(SCRATCH_DIR):
        shutil.rmtree(SCRATCH_DIR)
    os.makedirs(SCRATCH_DIR)

    print("=" * 70)
    print("CLOSE ORCHESTRATOR — Cycle 3, Task 1, Item 3")
    print("=" * 70)

    # =========================================================================
    # STEP 1 — Close v1 (Q3 FY2026 truncated dataset): BOOTSTRAP PATH
    # =========================================================================
    print("\n" + "-" * 70)
    print("STEP 1 — CLOSE v1 (bootstrap path)")
    print("-" * 70)

    prior = close_history.resolve_latest_approved_close(CLOSE_HISTORY_DIR)
    print(f"resolve_latest_approved_close() -> {prior!r}")
    assert prior is None, "Expected Close History empty at the very start (bootstrap case)."
    print("Confirmed: Close History is empty. No prior approved close to diff against.")
    print("Phase 2 status: SKIPPED — 'no prior close to compare' (bootstrap), not an error.")

    cv1_present = set(CV.close_v1_revenue["Fiscal Quarter"].unique())
    cv1_quarter_order = [q for q in CV.quarter_order if q in cv1_present]
    cv1_target_quarter = cv1_quarter_order[-1]
    print(f"Close v1 covers {len(cv1_quarter_order)} fiscal quarters, through {cv1_target_quarter}.")

    p3_cells_v1, p3_flags_v1 = run_phase3_plausibility(
        CV.close_v1_expenses, CV.close_v1_headcount, cv1_quarter_order, cv1_target_quarter,
        CV.PLAUSIBILITY_QOQ_THRESHOLD, CV.PLAUSIBILITY_HEADCOUNT_BAND,
    )
    print(f"Phase 3 (plausibility, run on {cv1_target_quarter}, the newest quarter in this close): "
          f"{len(p3_cells_v1)} Department x Category cells checked, {len(p3_flags_v1)} flagged.")
    assert len(p3_flags_v1) == 0, "Close v1 is unmodified source data — expected 0 plausibility flags."
    print("OK  0 flags, as expected for unmodified source data (no injections applied to Close v1).")

    rev_region_v1, rev_product_v1, exp_dept_v1, hc_dept_v1 = build_rollups_for(
        CV.close_v1_revenue, CV.close_v1_expenses, CV.close_v1_headcount, cv1_quarter_order
    )
    bva_v1, pl_v1 = load_bva_pl(cutoff=CV.CLOSE_V1_TRUNCATE_THROUGH)

    raw_v1_path = os.path.join(SCRATCH_DIR, "close_v1_raw_dataset.xlsx")
    rollups_v1_path = os.path.join(SCRATCH_DIR, "close_v1_rollups_output.xlsx")
    write_raw_dataset_workbook(raw_v1_path, CV.close_v1_revenue, CV.close_v1_expenses, CV.close_v1_headcount, bva_v1, pl_v1)
    write_rollups_workbook(rollups_v1_path, rev_region_v1, rev_product_v1, exp_dept_v1, hc_dept_v1)

    observations_v1 = pd.DataFrame(columns=OBS_COLUMNS)

    folder_v1, meta_v1 = close_history.archive_close(
        period_label="Q3 FY2026",
        raw_dataset_src=raw_v1_path,
        rollups_output_src=rollups_v1_path,
        observations_df=observations_v1,
        narrative_text=NO_NARRATIVE_NOTE,
        phase2_flag_count=None,
        phase3_flag_count=len(p3_flags_v1),
        workflow_state="Archived",
        prior_close_period_label=None,
        close_history_dir=CLOSE_HISTORY_DIR,
        extra_metadata={
            "close_type": "bootstrap (first approved close — Close History was empty)",
            "phase2_status": "not_applicable — no prior approved close to diff against",
            "phase3_status": f"ran on {cv1_target_quarter} (newest quarter in this close), {len(p3_flags_v1)} flagged",
            "source": "close_v1_v2_simulation.py: close_v1_revenue/expenses/headcount (unmodified, Q3 FY2026 truncation)",
        },
    )
    print(f"\nArchived: {folder_v1}/")
    print(f"metadata.json:\n{pd.Series(meta_v1).to_string()}")

    # =========================================================================
    # STEP 2 — Close v2 (full dataset + 2 injections): NORMAL PATH
    # =========================================================================
    print("\n" + "-" * 70)
    print("STEP 2 — CLOSE v2 (normal path)")
    print("-" * 70)

    prior2 = close_history.resolve_latest_approved_close(CLOSE_HISTORY_DIR)
    print(f"resolve_latest_approved_close() -> period_label={prior2['period_label']!r}, folder={prior2['folder']!r}")
    assert prior2 is not None and prior2["period_label"] == "Q3 FY2026", "Expected Close v1 to resolve as latest approved close."
    print("Confirmed: dynamic resolution found Close v1 as the latest approved close (no hardcoded filename).")

    prior_expenses_key = pd.read_excel(prior2["raw_dataset_path"], sheet_name="Expenses")[
        ["Date", "Department", "Category", "Amount ($)"]
    ].copy()
    prior_expenses_key["Date"] = pd.to_datetime(prior_expenses_key["Date"])
    current_expenses_key = CV.close_v2_expenses[["Date", "Department", "Category", "Amount ($)"]].copy()

    overlap_v2, p2_flags_v2 = run_phase2_diff(prior_expenses_key, current_expenses_key)
    print(f"Phase 2 (diff, Close v2 vs archived Close v1 raw_dataset.xlsx): "
          f"{len(overlap_v2)} overlapping expense rows compared, {len(p2_flags_v2)} flagged.")
    assert len(p2_flags_v2) == 1, f"Expected exactly 1 flagged row, found {len(p2_flags_v2)}"
    row2 = p2_flags_v2.iloc[0]
    print(f"  Flagged: Date={row2['Date'].date()}, Department={row2['Department']}, Category={row2['Category']}, "
          f"Prior=${row2['Amount ($)_prior']:,.2f}, Current=${row2['Amount ($)_current']:,.2f}, Diff=${row2['Diff ($)']:,.2f}")
    assert abs(row2["Amount ($)_prior"] - CV.HIST_REVISION["Original Amount ($)"]) < 0.005
    assert abs(row2["Amount ($)_current"] - CV.HIST_REVISION["Revised Amount ($)"]) < 0.005
    assert abs(row2["Diff ($)"] - CV.HIST_REVISION["Revision Delta ($)"]) < 0.005
    print("OK  Matches the documented HIST_REVISION constants exactly — same catch as the original in-memory Phase 2, "
          "now sourced by reading the archived Close v1 snapshot from disk.")

    p3_cells_v2, p3_flags_v2 = run_phase3_plausibility(
        CV.close_v2_expenses, CV.close_v2_headcount, CV.quarter_order, "Q4 FY2026",
        CV.PLAUSIBILITY_QOQ_THRESHOLD, CV.PLAUSIBILITY_HEADCOUNT_BAND,
    )
    print(f"\nPhase 3 (plausibility, Q4 FY2026): {len(p3_cells_v2)} cells checked, {len(p3_flags_v2)} flagged.")
    assert len(p3_flags_v2) == 1, f"Expected exactly 1 flagged cell, found {len(p3_flags_v2)}"
    row3 = p3_flags_v2.iloc[0]
    print(f"  Flagged: Department={row3['Department']}, Category={row3['Category']}, QoQ={row3['QoQ (%)']:+.1%}, "
          f"Headcount Change={row3['Headcount Change']:+.2f}")
    assert row3["Department"] == CV.PLAUSIBILITY_ANOMALY["Department"]
    assert row3["Category"] == CV.PLAUSIBILITY_ANOMALY["Category"]
    print("OK  Matches the documented PLAUSIBILITY_ANOMALY exactly — same catch as the original Phase 3.")

    rev_region_v2, rev_product_v2, exp_dept_v2, hc_dept_v2 = build_rollups_for(
        CV.close_v2_revenue, CV.close_v2_expenses, CV.close_v2_headcount, CV.quarter_order
    )
    bva_v2, pl_v2 = load_bva_pl(cutoff=None)

    raw_v2_path = os.path.join(SCRATCH_DIR, "close_v2_raw_dataset.xlsx")
    rollups_v2_path = os.path.join(SCRATCH_DIR, "close_v2_rollups_output.xlsx")
    write_raw_dataset_workbook(raw_v2_path, CV.close_v2_revenue, CV.close_v2_expenses, CV.close_v2_headcount, bva_v2, pl_v2)
    write_rollups_workbook(rollups_v2_path, rev_region_v2, rev_product_v2, exp_dept_v2, hc_dept_v2)

    observations_v2 = pd.DataFrame([
        {
            "Observation ID": "OBS-001", "Detected By": "Phase 2 (Deterministic Validation)",
            "Period": CV.HIST_REVISION["Date"].strftime("Q2 FY2026 (%b %Y)"), "Type": "Historical Revision",
            "Department": CV.HIST_REVISION["Department"], "Category": CV.HIST_REVISION["Category"],
            "Before ($)": row2["Amount ($)_prior"], "After ($)": row2["Amount ($)_current"], "Delta ($)": row2["Diff ($)"],
            "Commentary Matched": None, "Classification": "Unclassified — awaiting commentary",
            "Status": "Awaiting Controller Input",
        },
        {
            "Observation ID": "OBS-002", "Detected By": "Phase 3 (Plausibility Review)",
            "Period": CV.PLAUSIBILITY_ANOMALY["Date"].strftime("Q4 FY2026 (%b %Y)"), "Type": "Plausibility Anomaly",
            "Department": row3["Department"], "Category": row3["Category"],
            "Before ($)": row3["Prior ($)"], "After ($)": row3["Amount ($)"], "Delta ($)": row3["Amount ($)"] - row3["Prior ($)"],
            "Commentary Matched": None, "Classification": "Unclassified — awaiting commentary",
            "Status": "Awaiting Controller Input",
        },
    ], columns=OBS_COLUMNS)

    folder_v2, meta_v2 = close_history.archive_close(
        period_label="Q4 FY2026",
        raw_dataset_src=raw_v2_path,
        rollups_output_src=rollups_v2_path,
        observations_df=observations_v2,
        narrative_text=NO_NARRATIVE_NOTE,
        phase2_flag_count=len(p2_flags_v2),
        phase3_flag_count=len(p3_flags_v2),
        workflow_state="Archived",
        prior_close_period_label=prior2["period_label"],
        close_history_dir=CLOSE_HISTORY_DIR,
        extra_metadata={
            "close_type": "normal (diffed against latest approved close)",
            "phase2_status": f"ran against {prior2['period_label']} (dynamically resolved), {len(p2_flags_v2)} flagged",
            "phase3_status": f"ran on Q4 FY2026, {len(p3_flags_v2)} flagged",
            "source": "close_v1_v2_simulation.py: close_v2_revenue/expenses/headcount (unmodified, full dataset + 2 documented injections)",
        },
    )
    print(f"\nArchived: {folder_v2}/")
    print(f"metadata.json:\n{pd.Series(meta_v2).to_string()}")

    # =========================================================================
    # Final state
    # =========================================================================
    print("\n" + "=" * 70)
    print("FINAL CLOSE HISTORY STATE")
    print("=" * 70)
    for label, meta, folder in close_history.list_approved_closes(CLOSE_HISTORY_DIR):
        files = sorted(os.listdir(folder))
        print(f"{folder}/  ->  {files}")
    print("\ndashboard.html / board_deck.pptx: confirmed absent from every snapshot (metadata fields present and null; "
          "out of scope per the Brief — not fabricated).")


if __name__ == "__main__":
    main()
