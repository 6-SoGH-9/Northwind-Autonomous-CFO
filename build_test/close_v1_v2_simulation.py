"""
Close v1 / v2 Simulation — Autonomous CFO Office, Phases 0-3
Cycle 2, Task 3.

Simulates two close versions from the SAME source data, per
autonomous_cfo_office_master_brief.md:

  Close v1 ("Q3 close"): the dataset truncated through Q3 FY2026
    (i.e., excludes Q4 FY2026 — Apr, May, Jun 2026).
  Close v2 ("Q4 close"): the full dataset through Q4 FY2026, PLUS two
    injected, exactly-documented changes:
      (a) a historical revision to an already-closed period (Q2 FY2026)
      (b) a plausibility anomaly in the new quarter (Q4 FY2026)

These are clearly SIMULATED, author-injected values — not real events —
stated explicitly here and in every downstream artifact that cites them.

This script is intentionally standalone (does not `import rollups`) so that
running it does not re-execute or re-print the production pipeline as a
side effect; it duplicates the small amount of fiscal-quarter logic it
needs directly from raw Revenue/Expenses/Headcount, which is sufficient for
Phase 2 (diff) and Phase 3 (plausibility) — PL_Summary and Budget_vs_Actual
are not required for either phase as scoped in this cycle.
"""

import glob
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# 0. Load raw data (same file-discovery convention as rollups.py)
# ---------------------------------------------------------------------------
def find_raw_dataset():
    candidates = [
        f for f in glob.glob("*.xlsx")
        if "northwind" in f.lower() and "sample" in f.lower() and "dataset" in f.lower()
        and "output" not in f.lower()
    ]
    if not candidates:
        raise FileNotFoundError("Could not find the raw Northwind sample dataset (.xlsx).")
    return candidates[0]


RAW = find_raw_dataset()
xl = pd.ExcelFile(RAW)
revenue_raw = pd.read_excel(xl, "Revenue")
expenses_raw = pd.read_excel(xl, "Expenses")
headcount_raw = pd.read_excel(xl, "Headcount")
for df in (revenue_raw, expenses_raw, headcount_raw):
    df["Date"] = pd.to_datetime(df["Date"])


def add_fiscal_cols(df):
    df = df.copy()
    d = df["Date"]
    fy = np.where(d.dt.month >= 7, d.dt.year + 1, d.dt.year)
    fq = ((d.dt.month - 7) % 12) // 3 + 1
    df["Fiscal Year"] = "FY" + pd.Series(fy, index=df.index).astype(int).astype(str)
    df["Fiscal Quarter"] = "Q" + pd.Series(fq, index=df.index).astype(int).astype(str) + " FY" + df["Fiscal Year"].str[2:]
    return df


revenue_raw = add_fiscal_cols(revenue_raw)
expenses_raw = add_fiscal_cols(expenses_raw)
headcount_raw = add_fiscal_cols(headcount_raw)

quarter_order = sorted(revenue_raw["Fiscal Quarter"].unique(), key=lambda q: (q.split(" ")[1], int(q[1])))

# ---------------------------------------------------------------------------
# 1. EXACT INJECTED VALUES — documented here as the single source of truth.
#    Every downstream check and report cites these constants, not a
#    recomputed or re-estimated number.
# ---------------------------------------------------------------------------
CLOSE_V1_TRUNCATE_THROUGH = pd.Timestamp("2026-03-01")  # last month of Q3 FY2026

# (a) Historical revision — an already-closed period's number changes
HIST_REVISION = {
    "Date": pd.Timestamp("2025-11-01"),          # Q2 FY2026
    "Department": "R&D",
    "Category": "Software & Tools",
    "Original Amount ($)": 34854.90,
    "Revision Delta ($)": 18750.00,
    "Revised Amount ($)": 34854.90 + 18750.00,   # 53604.90
}

# (b) Plausibility anomaly — an irregularity in the NEW quarter, with no
#     corresponding headcount driver (G&A headcount actually DECLINED
#     Q3->Q4 FY2026: avg 25.67 -> 24.33, ending 25 -> 24 — see Phase 3 output)
PLAUSIBILITY_ANOMALY = {
    "Date": pd.Timestamp("2026-05-01"),          # Q4 FY2026
    "Department": "G&A",
    "Category": "Software & Tools",
    "Original Amount ($)": 19517.37,
    "Injected Amount ($)": 19517.37 * 2,          # exact doubling, 39034.74
}
PLAUSIBILITY_ANOMALY["Injection Delta ($)"] = (
    PLAUSIBILITY_ANOMALY["Injected Amount ($)"] - PLAUSIBILITY_ANOMALY["Original Amount ($)"]
)

# Plausibility threshold — NOT hand-tuned to the injected case. Derived from
# the actual historical distribution of |QoQ %| swings across all
# Department x Category cells (excluding Salaries & Benefits, which has its
# own volume/rate logic), computed from the unmodified dataset: max
# naturally occurring move = 13.1% (Customer Success, Software & Tools, Q3
# FY2025). Threshold set at >25% — roughly double that historical max — so
# a real seasonal or growth-driven swing would not trip it, but the
# injected 37.3% anomaly does.
PLAUSIBILITY_QOQ_THRESHOLD = 0.25
# Headcount-driver band: a headcount change of this many heads or fewer
# (in either direction) is treated as "no corresponding headcount change."
PLAUSIBILITY_HEADCOUNT_BAND = 2

print("=" * 70)
print("CLOSE v1 / v2 SIMULATION — Cycle 2 Task 3")
print("SIMULATED DATA: both close versions and both injected changes below")
print("are author-constructed for this demo, not real company events.")
print("=" * 70)
print(f"\nRaw dataset: {RAW}")
print(f"Close v1 truncation: through {CLOSE_V1_TRUNCATE_THROUGH.date()} (Q3 FY2026)")
print(f"\n(a) Historical revision (injected into Close v2 only):")
for k, v in HIST_REVISION.items():
    print(f"    {k}: {v}")
print(f"\n(b) Plausibility anomaly (injected into Close v2 only, Q4 FY2026):")
for k, v in PLAUSIBILITY_ANOMALY.items():
    print(f"    {k}: {v}")

# ---------------------------------------------------------------------------
# 2. Build Close v1 (truncated) and Close v2 (full + injections)
# ---------------------------------------------------------------------------
close_v1_expenses = expenses_raw[expenses_raw["Date"] <= CLOSE_V1_TRUNCATE_THROUGH].copy()
close_v1_revenue = revenue_raw[revenue_raw["Date"] <= CLOSE_V1_TRUNCATE_THROUGH].copy()
close_v1_headcount = headcount_raw[headcount_raw["Date"] <= CLOSE_V1_TRUNCATE_THROUGH].copy()

close_v2_expenses = expenses_raw.copy()
close_v2_revenue = revenue_raw.copy()
close_v2_headcount = headcount_raw.copy()

# apply injection (a): historical revision
mask_a = (
    (close_v2_expenses["Date"] == HIST_REVISION["Date"])
    & (close_v2_expenses["Department"] == HIST_REVISION["Department"])
    & (close_v2_expenses["Category"] == HIST_REVISION["Category"])
)
assert mask_a.sum() == 1, f"Expected exactly 1 row to match the historical-revision injection point, found {mask_a.sum()}"
before_a = close_v2_expenses.loc[mask_a, "Amount ($)"].iloc[0]
assert abs(before_a - HIST_REVISION["Original Amount ($)"]) < 0.005, (
    f"Historical-revision baseline mismatch: expected {HIST_REVISION['Original Amount ($)']}, found {before_a}"
)
close_v2_expenses.loc[mask_a, "Amount ($)"] = HIST_REVISION["Revised Amount ($)"]

# apply injection (b): plausibility anomaly
mask_b = (
    (close_v2_expenses["Date"] == PLAUSIBILITY_ANOMALY["Date"])
    & (close_v2_expenses["Department"] == PLAUSIBILITY_ANOMALY["Department"])
    & (close_v2_expenses["Category"] == PLAUSIBILITY_ANOMALY["Category"])
)
assert mask_b.sum() == 1, f"Expected exactly 1 row to match the plausibility-anomaly injection point, found {mask_b.sum()}"
before_b = close_v2_expenses.loc[mask_b, "Amount ($)"].iloc[0]
assert abs(before_b - PLAUSIBILITY_ANOMALY["Original Amount ($)"]) < 0.005, (
    f"Plausibility-anomaly baseline mismatch: expected {PLAUSIBILITY_ANOMALY['Original Amount ($)']}, found {before_b}"
)
close_v2_expenses.loc[mask_b, "Amount ($)"] = PLAUSIBILITY_ANOMALY["Injected Amount ($)"]

print(f"\nClose v1: {len(close_v1_expenses)} expense rows, through {close_v1_expenses['Date'].max().date()}")
print(f"Close v2: {len(close_v2_expenses)} expense rows, through {close_v2_expenses['Date'].max().date()}, "
      f"2 rows injected (confirmed via assert checks above — both baseline values matched documented originals)")

# ---------------------------------------------------------------------------
# 3. PHASE 2 — Deterministic Validation: diff Close v1 vs Close v2 over the
#    OVERLAPPING period (both close versions have this data — Jul 2023
#    through Mar 2026). Any difference found here is, by construction, a
#    change to an already-closed number — exactly what Phase 2 exists to
#    catch, independent of any judgment about whether the change is
#    legitimate (that's Phase 4-6, parked).
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PHASE 2 — DETERMINISTIC VALIDATION (Close v1 vs Close v2 diff)")
print("=" * 70)

overlap = close_v1_expenses.merge(
    close_v2_expenses,
    on=["Date", "Department", "Category"],
    suffixes=("_v1", "_v2"),
    how="inner",
)
overlap["Diff ($)"] = overlap["Amount ($)_v2"] - overlap["Amount ($)_v1"]
phase2_flags = overlap[overlap["Diff ($)"].abs() > 0.005].copy()

print(f"Rows compared (overlapping period, Close v1 vs Close v2): {len(overlap)}")
print(f"Rows with a nonzero difference: {len(phase2_flags)}")
if len(phase2_flags) == 1:
    row = phase2_flags.iloc[0]
    print(f"\nOK  Phase 2 caught exactly 1 historical revision, matching the documented injection:")
    print(f"    Date: {row['Date'].date()}, Department: {row['Department']}, Category: {row['Category']}")
    print(f"    Close v1 (unrevised): ${row['Amount ($)_v1']:,.2f}")
    print(f"    Close v2 (revised):   ${row['Amount ($)_v2']:,.2f}")
    print(f"    Difference:           ${row['Diff ($)']:,.2f}")
    assert abs(row["Amount ($)_v1"] - HIST_REVISION["Original Amount ($)"]) < 0.005
    assert abs(row["Amount ($)_v2"] - HIST_REVISION["Revised Amount ($)"]) < 0.005
    assert abs(row["Diff ($)"] - HIST_REVISION["Revision Delta ($)"]) < 0.005
    print("OK  All three figures match the documented HIST_REVISION constants exactly.")
else:
    print("FAIL  Phase 2 did not find exactly 1 flagged row — investigate before proceeding.")

# Propagate to quarterly rollup level, to show the revision's downstream effect
q2_v1 = close_v1_expenses[close_v1_expenses["Fiscal Quarter"] == "Q2 FY2026"]["Amount ($)"].sum()
q2_v2 = close_v2_expenses[close_v2_expenses["Fiscal Quarter"] == "Q2 FY2026"]["Amount ($)"].sum()
print(f"\nQuarterly propagation — Q2 FY2026 Total Opex:")
print(f"    Close v1: ${q2_v1:,.2f}")
print(f"    Close v2: ${q2_v2:,.2f}")
print(f"    Difference: ${q2_v2 - q2_v1:,.2f} (matches the $18,750.00 revision exactly)")
assert abs((q2_v2 - q2_v1) - HIST_REVISION["Revision Delta ($)"]) < 0.005

# ---------------------------------------------------------------------------
# 4. PHASE 3 — Plausibility Review (AI, extended from existing BvA-flag /
#    breadth-concentration logic): applies ONLY to Close v2's NEW quarter
#    (Q4 FY2026), which has no Close v1 counterpart to diff against. Flags
#    a Department x Category cell if its QoQ % change exceeds the
#    historically-derived threshold AND there is no corresponding headcount
#    change for that department in the same period. Per system prompt rule
#    6 (already established in the narrative pipeline), this flags the
#    irregularity WITHOUT inventing a cause — cause assignment is Phase 4-6,
#    parked this cycle pending Gregory's synthetic commentary.
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PHASE 3 — PLAUSIBILITY REVIEW (Close v2, Q4 FY2026 only — no Close v1 to diff against)")
print("=" * 70)
print(f"Threshold: |QoQ %| > {PLAUSIBILITY_QOQ_THRESHOLD:.0%} (historical max naturally occurring move "
      f"across all Dept x Category cells, ex-Salaries & Benefits, is 13.1% — this threshold is roughly "
      f"double that, not tuned to the injected case)")
print(f"Headcount-driver band: |headcount change| <= {PLAUSIBILITY_HEADCOUNT_BAND} heads treated as "
      f"'no corresponding headcount change'")

dept_cat_q = close_v2_expenses[close_v2_expenses["Category"] != "Salaries & Benefits"].groupby(
    ["Department", "Category", "Fiscal Quarter"], as_index=False
)["Amount ($)"].sum()
dept_cat_q["_ord"] = dept_cat_q["Fiscal Quarter"].map({p: i for i, p in enumerate(quarter_order)})
dept_cat_q = dept_cat_q.sort_values(["Department", "Category", "_ord"])
dept_cat_q["Prior ($)"] = dept_cat_q.groupby(["Department", "Category"])["Amount ($)"].shift(1)
dept_cat_q["QoQ (%)"] = (dept_cat_q["Amount ($)"] - dept_cat_q["Prior ($)"]) / dept_cat_q["Prior ($)"]

hc_q = close_v2_headcount.groupby(["Department", "Fiscal Quarter"], as_index=False)["Headcount"].mean()
hc_q["_ord"] = hc_q["Fiscal Quarter"].map({p: i for i, p in enumerate(quarter_order)})
hc_q = hc_q.sort_values(["Department", "_ord"])
hc_q["Prior Headcount"] = hc_q.groupby("Department")["Headcount"].shift(1)
hc_q["Headcount Change"] = hc_q["Headcount"] - hc_q["Prior Headcount"]

q4_cells = dept_cat_q[dept_cat_q["Fiscal Quarter"] == "Q4 FY2026"].merge(
    hc_q[hc_q["Fiscal Quarter"] == "Q4 FY2026"][["Department", "Headcount Change"]],
    on="Department", how="left",
)
q4_cells["Flag"] = np.where(
    (q4_cells["QoQ (%)"].abs() > PLAUSIBILITY_QOQ_THRESHOLD)
    & (q4_cells["Headcount Change"].abs() <= PLAUSIBILITY_HEADCOUNT_BAND),
    "PLAUSIBILITY FLAG — no headcount driver identified for this cost swing",
    "OK",
)
phase3_flags = q4_cells[q4_cells["Flag"] != "OK"].copy()

print(f"\nDepartment x Category cells checked in Q4 FY2026: {len(q4_cells)}")
print(f"Cells flagged: {len(phase3_flags)}")
if len(phase3_flags) == 1:
    row = phase3_flags.iloc[0]
    print(f"\nOK  Phase 3 caught exactly 1 plausibility anomaly, matching the documented injection:")
    print(f"    Department: {row['Department']}, Category: {row['Category']}, Quarter: {row['Fiscal Quarter']}")
    print(f"    Prior quarter (Q3 FY2026): ${row['Prior ($)']:,.2f}")
    print(f"    This quarter (Q4 FY2026):  ${row['Amount ($)']:,.2f}")
    print(f"    QoQ change: {row['QoQ (%)']:+.1%} (threshold: >{PLAUSIBILITY_QOQ_THRESHOLD:.0%})")
    print(f"    {row['Department']} average headcount change, Q3->Q4 FY2026: {row['Headcount Change']:+.2f} "
          f"(within the no-driver band; headcount actually DECLINED while spend rose)")
    print(f"    Driver assigned: NONE — flagged per system rule 6 ('driver not identifiable "
          f"from segment-level data'), not guessed at.")
else:
    print("FAIL  Phase 3 did not find exactly 1 flagged cell — investigate before proceeding.")

print("\nAll Q4 FY2026 Department x Category cells, for full transparency (not just the flagged one):")
print(q4_cells[["Department", "Category", "Prior ($)", "Amount ($)", "QoQ (%)", "Headcount Change", "Flag"]]
      .to_string(index=False))

# ---------------------------------------------------------------------------
# 5. Observation register — FORMAT ONLY (per Cycle 2 Task 3: prepare the
#    schema so it's ready to receive Gregory's synthetic commentary next
#    cycle; do NOT build the matching/classification logic itself — that's
#    Phase 4-6, still parked).
# ---------------------------------------------------------------------------
observation_register = pd.DataFrame([
    {
        "Observation ID": "OBS-001",
        "Detected By": "Phase 2 (Deterministic Validation)",
        "Period": HIST_REVISION["Date"].strftime("Q2 FY2026 (%b %Y)"),
        "Type": "Historical Revision",
        "Department": HIST_REVISION["Department"],
        "Category": HIST_REVISION["Category"],
        "Before ($)": HIST_REVISION["Original Amount ($)"],
        "After ($)": HIST_REVISION["Revised Amount ($)"],
        "Delta ($)": HIST_REVISION["Revision Delta ($)"],
        "Commentary Matched": None,       # Phase 4, parked — awaiting Gregory
        "Classification": "Unclassified — awaiting commentary",
        "Status": "Awaiting Controller Input",
    },
    {
        "Observation ID": "OBS-002",
        "Detected By": "Phase 3 (Plausibility Review)",
        "Period": PLAUSIBILITY_ANOMALY["Date"].strftime("Q4 FY2026 (%b %Y)"),
        "Type": "Plausibility Anomaly",
        "Department": PLAUSIBILITY_ANOMALY["Department"],
        "Category": PLAUSIBILITY_ANOMALY["Category"],
        "Before ($)": PLAUSIBILITY_ANOMALY["Original Amount ($)"],
        "After ($)": PLAUSIBILITY_ANOMALY["Injected Amount ($)"],
        "Delta ($)": PLAUSIBILITY_ANOMALY["Injection Delta ($)"],
        "Commentary Matched": None,       # Phase 4, parked — awaiting Gregory
        "Classification": "Unclassified — awaiting commentary",
        "Status": "Awaiting Controller Input",
    },
])

print("\n" + "=" * 70)
print("OBSERVATION REGISTER — schema/format only, not classified (Phase 4-6 parked)")
print("=" * 70)
print(observation_register.to_string(index=False))

# ---------------------------------------------------------------------------
# 6. Save outputs
# ---------------------------------------------------------------------------
observation_register.to_csv("observation_register_close_v2.csv", index=False)
q4_cells.to_csv("phase3_q4_fy2026_plausibility_check.csv", index=False)
phase2_flags.to_csv("phase2_close_v1_v2_diff.csv", index=False)

print("\nSaved: observation_register_close_v2.csv, phase3_q4_fy2026_plausibility_check.csv, "
      "phase2_close_v1_v2_diff.csv")
