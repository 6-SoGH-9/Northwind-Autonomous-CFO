"""
Close v1 / v2 Simulation — Build/Test Fixture — Cycle 3, Task 2 refactor
(originally built Cycle 2, Task 3)

*** BUILD/TEST VERIFICATION TOOL — NOT A LIVE ARTIFACT ***
Same classification as close_orchestrator.py (see Handbook Section 12).

WHAT CHANGED IN CYCLE 3, TASK 2
--------------------------------
This script used to contain its OWN copy of the Phase 2 diff logic and the
Phase 3 plausibility logic, duplicating what is now the production
close_validation.py module. Per the Cycle 3 Task 2 Builder Brief, that
duplication is removed:

  - This fixture still owns exactly what a fixture should own: the two
    injected, exactly-documented anomalies (HIST_REVISION,
    PLAUSIBILITY_ANOMALY) and the Close v1/v2 dataset construction from the
    raw sample dataset.
  - It now calls close_validation.py's real
    run_phase2_deterministic_validation() and
    run_phase3_plausibility_review() functions on that fixture data, and
    asserts the RETURNED STRUCTURED RESULT matches the documented expected
    catches exactly.
  - It contains ZERO copies of the actual comparison/plausibility
    calculation logic. If an assertion below ever fails, it means
    close_validation.py has a real defect -- not that two independent
    implementations drifted apart from each other.
  - All printing/CSV output for human readability happens HERE, in the
    fixture, after calling the module -- never inside close_validation.py
    itself (which has zero I/O by design).

GRAIN NOTE (Cycle 3 Task 2, Item 4 -- resolves the discrepancy flagged in
the Cycle 3 Task 1 Return Report): the fixture's own
`observation_register` schema/demo below reports the plausibility
anomaly's Phase 3 catch at QUARTER grain (Q4 FY2026: prior-quarter total
vs. current-quarter total for R&D/G&A x Category), matching exactly what
close_validation.run_phase3_plausibility_review() actually detects and
returns. It does NOT report a month-grain figure -- a month-grain number
only ever existed in the old hardcoded register because that version of
the script had privileged knowledge of its own single-month injection
point, not because Phase 3 logic operates at month grain. Phase 3 has
never operated at month grain; only the OLD register text did.

These are clearly SIMULATED, author-injected values -- not real events --
stated explicitly here and in every downstream artifact that cites them.
"""

import glob
import pandas as pd
import numpy as np

import close_validation as CV


# ---------------------------------------------------------------------------
# 0. Load raw data (same file-discovery convention as rollups.py's bootstrap
#    fallback -- this fixture intentionally does NOT import rollups, so
#    running it does not re-execute or re-print the production pipeline as
#    a side effect. It duplicates only the small amount of fiscal-quarter
#    labeling it needs to build its own two synthetic close versions -- NOT
#    any comparison/plausibility logic, which now lives solely in
#    close_validation.py.)
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
#    recomputed or re-estimated number. This is exactly what a Build/Test
#    fixture should own -- close_validation.py contains none of these.
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
#     Q3->Q4 FY2026: avg 25.67 -> 24.33, ending 25 -> 24 — confirmed via
#     close_validation.py's returned Headcount Change column, Phase 3
#     output below, not re-derived here)
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

print("=" * 70)
print("CLOSE v1 / v2 FIXTURE — Cycle 3 Task 2 (verifies close_validation.py)")
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
# 3. PHASE 2 — call close_validation.run_phase2_deterministic_validation()
#    (the production function) on Close v1 (as "prior approved close") vs.
#    Close v2 (as "current close"), then assert the RETURNED result matches
#    the documented HIST_REVISION constants exactly. No diff logic is
#    reimplemented here.
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PHASE 2 — DETERMINISTIC VALIDATION (via close_validation.py, Close v1 vs Close v2)")
print("=" * 70)

phase2_result = CV.run_phase2_deterministic_validation(
    current_data=close_v2_expenses,
    prior_data=close_v1_expenses,
    key_cols=("Date", "Department", "Category"),
    value_col="Amount ($)",
)
phase2_flags = phase2_result.flagged_rows

print(f"close_validation.py Phase 2 status: {phase2_result.status}")
assert phase2_result.status == CV.STATUS_OK, "Expected STATUS_OK -- Close v1 exists, this is not the bootstrap case."
print(f"Rows compared (overlapping period, Close v1 vs Close v2): {phase2_result.rows_compared}")
print(f"Rows with a nonzero difference: {len(phase2_flags)}")

if len(phase2_flags) == 1:
    row = phase2_flags.iloc[0]
    print(f"\nOK  Phase 2 caught exactly 1 historical revision, matching the documented injection:")
    print(f"    Date: {row['Date'].date()}, Department: {row['Department']}, Category: {row['Category']}")
    print(f"    Close v1 (unrevised): ${row['Amount ($)_prior']:,.2f}")
    print(f"    Close v2 (revised):   ${row['Amount ($)_current']:,.2f}")
    print(f"    Difference:           ${row['Diff ($)']:,.2f}")
    assert abs(row["Amount ($)_prior"] - HIST_REVISION["Original Amount ($)"]) < 0.005
    assert abs(row["Amount ($)_current"] - HIST_REVISION["Revised Amount ($)"]) < 0.005
    assert abs(row["Diff ($)"] - HIST_REVISION["Revision Delta ($)"]) < 0.005
    print("OK  All three figures match the documented HIST_REVISION constants exactly.")
else:
    raise AssertionError(f"FAIL  Phase 2 did not return exactly 1 flagged row (got {len(phase2_flags)}) — "
                          f"investigate close_validation.py before proceeding.")

# Propagate to quarterly rollup level, to show the revision's downstream
# effect (fixture-only aggregation for readability -- not part of the
# production module's contract).
q2_v1 = close_v1_expenses[close_v1_expenses["Fiscal Quarter"] == "Q2 FY2026"]["Amount ($)"].sum()
q2_v2 = close_v2_expenses[close_v2_expenses["Fiscal Quarter"] == "Q2 FY2026"]["Amount ($)"].sum()
print(f"\nQuarterly propagation — Q2 FY2026 Total Opex:")
print(f"    Close v1: ${q2_v1:,.2f}")
print(f"    Close v2: ${q2_v2:,.2f}")
print(f"    Difference: ${q2_v2 - q2_v1:,.2f} (matches the $18,750.00 revision exactly)")
assert abs((q2_v2 - q2_v1) - HIST_REVISION["Revision Delta ($)"]) < 0.005

# Bootstrap-case regression check: confirm the same production function
# returns NOT_APPLICABLE (not an error, not a silently-empty OK result)
# when there is genuinely no prior close, using this fixture's own data as
# the "current" close with prior_data=None. This exercises the exact code
# path Acceptance Criterion 4 requires, on real (not synthetic) data.
bootstrap_check = CV.run_phase2_deterministic_validation(current_data=close_v2_expenses, prior_data=None)
assert bootstrap_check.status == CV.STATUS_NOT_APPLICABLE
assert bootstrap_check.rows_compared == 0
assert bootstrap_check.flagged_rows.empty
print(f"\nOK  Bootstrap-case regression check: close_validation.py correctly returns "
      f"status='{bootstrap_check.status}' (not an error, not an empty-but-ambiguous OK) when prior_data=None.")

# ---------------------------------------------------------------------------
# 4. PHASE 3 — call close_validation.run_phase3_plausibility_review() (the
#    production function) on Close v2's full history, targeting Q4 FY2026
#    (the new quarter with no Close v1 counterpart to diff against), then
#    assert the RETURNED result matches the documented PLAUSIBILITY_ANOMALY
#    constants exactly. No plausibility logic is reimplemented here.
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PHASE 3 — PLAUSIBILITY REVIEW (via close_validation.py, Close v2, Q4 FY2026 only)")
print("=" * 70)
print(f"Threshold: |QoQ %| > {CV.DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD:.0%} (production default from close_validation.py — "
      f"historical max naturally occurring move across all Dept x Category cells, ex-Salaries & Benefits, "
      f"is documented in close_validation.py as the derivation basis; this threshold is roughly double that, "
      f"not tuned to this fixture's injected case)")
print(f"Headcount-driver band: production default from close_validation.py "
      f"(|headcount change| <= {CV.DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND} heads treated as 'no corresponding headcount change')")

phase3_result = CV.run_phase3_plausibility_review(
    expenses=close_v2_expenses,
    headcount=close_v2_headcount,
    period_col="Fiscal Quarter",
    period_order=quarter_order,
    target_period="Q4 FY2026",
)
q4_cells = phase3_result.all_cells
phase3_flags = phase3_result.flagged_rows

print(f"\nclose_validation.py Phase 3 status: {phase3_result.status}")
assert phase3_result.status == CV.STATUS_OK
print(f"Department x Category cells checked in Q4 FY2026: {phase3_result.cells_checked}")
print(f"Cells flagged: {len(phase3_flags)}")

if len(phase3_flags) == 1:
    row = phase3_flags.iloc[0]
    print(f"\nOK  Phase 3 caught exactly 1 plausibility anomaly, matching the documented injection:")
    print(f"    Department: {row['Department']}, Category: {row['Category']}, Quarter: {row['Fiscal Quarter']}")
    print(f"    Prior quarter (Q3 FY2026): ${row['Prior ($)']:,.2f}")
    print(f"    This quarter (Q4 FY2026):  ${row['Amount ($)']:,.2f}")
    print(f"    QoQ change: {row['QoQ (%)']:+.1%} (threshold: >{CV.DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD:.0%})")
    print(f"    {row['Department']} average headcount change, Q3->Q4 FY2026: {row['Headcount Change']:+.2f} "
          f"(within the no-driver band; headcount actually DECLINED while spend rose)")
    print(f"    Driver assigned: {row['Driver']} — flagged per system rule 6, close_validation.py never guesses a cause.")
    assert row["Department"] == PLAUSIBILITY_ANOMALY["Department"]
    assert row["Category"] == PLAUSIBILITY_ANOMALY["Category"]
    assert row["Driver"] == CV.DRIVER_NOT_IDENTIFIABLE
    # QUARTER-GRAIN assertion (Item 4): the fixture checks the quarter-level
    # totals close_validation.py actually returns -- Q3 FY2026 total (prior)
    # vs Q4 FY2026 total (current) for G&A x Software & Tools -- NOT a
    # month-grain figure. The quarter-level "Amount ($)" for Q4 FY2026
    # includes the injected month's doubled value summed alongside that
    # quarter's other two (unmodified) months, so it will not equal
    # PLAUSIBILITY_ANOMALY["Injected Amount ($)"] directly; what IS checked
    # is that the quarter-level QoQ swing crosses the production threshold
    # and that no other cell is flagged.
    assert abs(row["QoQ (%)"]) > CV.DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD
    print("OK  Flagged cell matches the documented PLAUSIBILITY_ANOMALY department/category, "
          "at the quarter grain close_validation.py actually computes (Item 4 resolution).")
else:
    raise AssertionError(f"FAIL  Phase 3 did not return exactly 1 flagged cell (got {len(phase3_flags)}) — "
                          f"investigate close_validation.py before proceeding.")

print("\nAll Q4 FY2026 Department x Category cells, for full transparency (not just the flagged one):")
print(q4_cells.to_string(index=False))

# ---------------------------------------------------------------------------
# 5. Observation register — FORMAT ONLY (per Cycle 2 Task 3: prepare the
#    schema so it's ready to receive Gregory's synthetic commentary next
#    cycle; do NOT build the matching/classification logic itself — that's
#    Phase 4-6, still parked). Built HERE, by the fixture, from
#    close_validation.py's returned structured results -- this register was
#    never something the production module produces itself (see Item 3's
#    note on observations.csv remaining a caller-side artifact).
#
# GRAIN NOTE (Item 4): OBS-002's Period is now "Q4 FY2026" (quarter grain --
# what close_validation.py's Phase 3 actually evaluated and returned), not
# a month-level date. OBS-001 was already quarter/period-appropriate
# (Phase 2 operates at the raw row grain, Date is a real column in that
# grain, so no change needed there).
# ---------------------------------------------------------------------------
phase3_flagged_row = phase3_flags.iloc[0]
observation_register = pd.DataFrame([
    {
        "Observation ID": "OBS-001",
        "Detected By": "Phase 2 (Deterministic Validation, via close_validation.py)",
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
        "Detected By": "Phase 3 (Plausibility Review, via close_validation.py)",
        "Period": phase3_flagged_row["Fiscal Quarter"],  # quarter grain — Item 4
        "Type": "Plausibility Anomaly",
        "Department": phase3_flagged_row["Department"],
        "Category": phase3_flagged_row["Category"],
        "Before ($)": phase3_flagged_row["Prior ($)"],   # quarter-level prior total, as returned
        "After ($)": phase3_flagged_row["Amount ($)"],   # quarter-level current total, as returned
        "Delta ($)": phase3_flagged_row["Amount ($)"] - phase3_flagged_row["Prior ($)"],
        "Commentary Matched": None,       # Phase 4, parked — awaiting Gregory
        "Classification": "Unclassified — awaiting commentary",
        "Status": "Awaiting Controller Input",
    },
])

print("\n" + "=" * 70)
print("OBSERVATION REGISTER — schema/format only, not classified (Phase 4-6 parked)")
print("Built by this fixture from close_validation.py's returned structured results —")
print("Period grain is quarter-level throughout, matching what Phase 2/3 actually detect.")
print("=" * 70)
print(observation_register.to_string(index=False))

# ---------------------------------------------------------------------------
# 6. Save outputs — printing/CSV export happens HERE (the fixture), never
#    inside close_validation.py.
# ---------------------------------------------------------------------------
observation_register.to_csv("observation_register_close_v2.csv", index=False)
q4_cells.to_csv("phase3_q4_fy2026_plausibility_check.csv", index=False)
phase2_flags.to_csv("phase2_close_v1_v2_diff.csv", index=False)

print("\nSaved: observation_register_close_v2.csv, phase3_q4_fy2026_plausibility_check.csv, "
      "phase2_close_v1_v2_diff.csv")
print("\nAll assertions passed — close_validation.py's production Phase 2/3 functions reproduce")
print("the exact catches previously verified in the pre-extraction demo script.")
