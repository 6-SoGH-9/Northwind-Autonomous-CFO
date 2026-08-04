"""
Northwind AI in Finance Challenge — Step 1: Data Layer
Builds quarter and year rollups from the raw monthly tables (Revenue, Expenses,
Headcount, Budget_vs_Actual), with QoQ and YoY variance, and verifies tie-out
against PL_Summary and Budget_vs_Actual.

Fiscal year convention: FY runs July-June (matches the dataset's Jul 2023-Jun 2026
span exactly = 3 complete fiscal years, no partial year). FY label = the calendar
year the fiscal year ENDS in, e.g. FY2024 = Jul 2023-Jun 2024. This matches the
example labels in northwind_narrative_prompt.md ("FY2025 Full Year").

Headcount is a stock, not a flow: quarter/year headcount = the value in the LAST
month of the period (end-of-period snapshot), not a sum or average. This is stated
explicitly wherever headcount rollups are produced.
"""

import glob
import os
import pandas as pd
import numpy as np

import close_history


def find_raw_dataset():
    """Resolve which raw dataset file this run of the pipeline should build
    rollups from. Cycle 3 (D10): the canonical object is the Approved
    Financial Close, not a single hardcoded/glob-matched dataset filename.
    Resolution order (no hardcoded filename anywhere in this order):

      1. NORTHWIND_RAW_DATASET_PATH env var — an explicit override used by
         the Close Orchestrator to point the pipeline at the specific
         incoming dataset for the close currently being processed (which,
         by definition, is not yet an *approved* close, so it can't be
         found in Close History). Takes precedence when set.
      2. The latest APPROVED close in Close History (close_history/), found
         dynamically via close_history.resolve_latest_approved_close() —
         i.e., whichever snapshot has the max approval_timestamp in its own
         metadata.json, not whichever file happens to glob-match a naming
         pattern.
      3. Bootstrap fallback: if Close History does not exist yet or is
         empty (a real, expected first-run state), fall back to the same
         filename-pattern search used before Cycle 3, so a fresh
         environment with no Close History yet still finds the initial
         dataset to seed the first approved close from. This preserves
         pre-Cycle-3 behavior exactly when Close History hasn't been
         created yet.
    """
    override = os.environ.get("NORTHWIND_RAW_DATASET_PATH")
    if override:
        if not os.path.isfile(override):
            raise FileNotFoundError(
                f"NORTHWIND_RAW_DATASET_PATH is set to '{override}' but that file does not exist."
            )
        return override

    resolved = close_history.resolve_latest_approved_close()
    if resolved is not None:
        return resolved["raw_dataset_path"]

    # Bootstrap fallback — unchanged from pre-Cycle-3 glob logic, used only
    # when Close History has no approved closes yet.
    candidates = [
        f for f in glob.glob("*.xlsx")
        if "northwind" in f.lower() and "sample" in f.lower() and "dataset" in f.lower()
        and "output" not in f.lower()
    ]
    if not candidates:
        raise FileNotFoundError(
            "Could not resolve a raw dataset: no approved close exists in Close History "
            "(bootstrap case) and no loose dataset file was found in the current directory "
            "either. Expected a file with 'Northwind', 'Sample', and 'Dataset' in the name, "
            "e.g. 'Northwind__Sample_Dataset.xlsx', to seed the first approved close."
        )
    if len(candidates) > 1:
        raise FileNotFoundError(
            f"Found multiple candidate raw dataset files, ambiguous which to use: {candidates}. "
            "Keep only one in this directory, or rename the others."
        )
    return candidates[0]


RAW = find_raw_dataset()
print(f"Using raw dataset file: {RAW}")

# ---------------------------------------------------------------------------
# 1. Load raw monthly tables
# ---------------------------------------------------------------------------
xl = pd.ExcelFile(RAW)
revenue = pd.read_excel(xl, "Revenue")
expenses = pd.read_excel(xl, "Expenses")
headcount = pd.read_excel(xl, "Headcount")
bva = pd.read_excel(xl, "Budget_vs_Actual")
pl_summary = pd.read_excel(xl, "PL_Summary")
pl_summary = pl_summary[pl_summary["Date"] != "Total / Avg"].copy()
pl_summary["Date"] = pd.to_datetime(pl_summary["Date"])


def add_fiscal_cols(df, date_col="Date"):
    """Add Fiscal Quarter (e.g. 'Q1 FY2024') and Fiscal Year (e.g. 'FY2024') columns.
    FY = Jul-Jun, labeled by the calendar year it ends in."""
    df = df.copy()
    d = pd.to_datetime(df[date_col])
    fy = pd.Series(
        np.where(d.dt.month >= 7, d.dt.year + 1, d.dt.year), index=df.index
    ).astype(int)
    fq = pd.Series(
        ((d.dt.month - 7) % 12) // 3 + 1, index=df.index
    ).astype(int)
    df["Fiscal Year"] = "FY" + fy.astype(str)
    df["Fiscal Quarter"] = "Q" + fq.astype(str) + " FY" + fy.astype(str)
    return df


revenue = add_fiscal_cols(revenue)
expenses = add_fiscal_cols(expenses)
headcount = add_fiscal_cols(headcount)
bva = add_fiscal_cols(bva)
pl_summary = add_fiscal_cols(pl_summary)


# ---------------------------------------------------------------------------
# 2. QoQ / YoY variance helper
# ---------------------------------------------------------------------------
def add_variance(df, group_cols, value_col, period_col, period_order, prior_shift):
    """Sort by period within each group, add prior-period value and variance %.
    prior_shift=1 for QoQ (immediately preceding period in period_order).
    For YoY, prior_shift is handled separately via same-quarter-prior-year join."""
    df = df.copy()
    df["_ord"] = df[period_col].map({p: i for i, p in enumerate(period_order)})
    df = df.sort_values(group_cols + ["_ord"])
    df["Prior"] = df.groupby(group_cols)[value_col].shift(prior_shift)
    df["Variance $"] = df[value_col] - df["Prior"]
    df["Variance %"] = np.where(
        df["Prior"].notna() & (df["Prior"] != 0),
        df["Variance $"] / df["Prior"],
        np.nan,
    )
    return df.drop(columns="_ord")


quarter_order = sorted(
    revenue["Fiscal Quarter"].unique(),
    key=lambda q: (q.split(" ")[1], int(q[1])),
)
year_order = sorted(revenue["Fiscal Year"].unique())

# ---------------------------------------------------------------------------
# 3. Revenue rollups (by Region, by Product Line) — quarter and year, w/ QoQ & YoY
# ---------------------------------------------------------------------------
def build_revenue_rollup(dim_col, period_col, period_order):
    g = (
        revenue.groupby([dim_col, period_col], as_index=False)["Revenue ($)"]
        .sum()
    )
    # Revenue Mix (%) — this segment's share of TOTAL revenue in the same
    # period (across all segments of this dim_col). Unlike the Region/Product
    # Net-of-cost %, this is NOT a proportional-allocation artifact — it's a
    # direct ratio of real revenue figures, so it varies meaningfully across
    # segments and IS a valid cross-segment comparison. Added per Cycle 2
    # Task 2 item 4 (Revenue Performance page).
    period_totals = g.groupby(period_col)["Revenue ($)"].transform("sum")
    g["Revenue Mix (%)"] = g["Revenue ($)"] / period_totals
    # QoQ / prior-period-of-same-cadence variance
    g = add_variance(g, [dim_col], "Revenue ($)", period_col, period_order, 1)
    g = g.rename(columns={"Prior": "Prior Period ($)", "Variance $": "QoQ/YoY Variance ($)",
                           "Variance %": "QoQ/YoY Variance (%)"})
    return g


rev_by_region_q = build_revenue_rollup("Region", "Fiscal Quarter", quarter_order)
rev_by_product_q = build_revenue_rollup("Product Line", "Fiscal Quarter", quarter_order)
rev_by_region_y = build_revenue_rollup("Region", "Fiscal Year", year_order)
rev_by_product_y = build_revenue_rollup("Product Line", "Fiscal Year", year_order)

# YoY on the quarterly cut (same quarter, prior year) — separate from sequential QoQ
def add_yoy_on_quarters(df, dim_col):
    df = df.copy()
    df["_fy"] = df["Fiscal Quarter"].str.split(" FY").str[1].astype(int)
    df["_q"] = df["Fiscal Quarter"].str[1].astype(int)
    lookup = df.set_index([dim_col, "_q", "_fy"])["Revenue ($)"] if "Revenue ($)" in df.columns else None
    val_col = "Revenue ($)" if "Revenue ($)" in df.columns else "Amount ($)"
    lookup = df.set_index([dim_col, "_q", "_fy"])[val_col]
    def get_prior_year(row):
        key = (row[dim_col], row["_q"], row["_fy"] - 1)
        return lookup.get(key, np.nan)
    df["YoY Prior-Year Same-Qtr ($)"] = df.apply(get_prior_year, axis=1)
    df["YoY Variance ($)"] = df[val_col] - df["YoY Prior-Year Same-Qtr ($)"]
    df["YoY Variance (%)"] = np.where(
        df["YoY Prior-Year Same-Qtr ($)"].notna() & (df["YoY Prior-Year Same-Qtr ($)"] != 0),
        df["YoY Variance ($)"] / df["YoY Prior-Year Same-Qtr ($)"],
        np.nan,
    )
    return df.drop(columns=["_fy", "_q"])


rev_by_region_q = add_yoy_on_quarters(rev_by_region_q, "Region")
rev_by_product_q = add_yoy_on_quarters(rev_by_product_q, "Product Line")

# ---------------------------------------------------------------------------
# 4. Expense rollups (by Department, by Category) — quarter and year
# ---------------------------------------------------------------------------
def build_expense_rollup(dim_cols, period_col, period_order):
    g = expenses.groupby(dim_cols + [period_col], as_index=False)["Amount ($)"].sum()
    group_only = dim_cols
    g = add_variance(g, group_only, "Amount ($)", period_col, period_order, 1)
    g = g.rename(columns={"Prior": "Prior Period ($)", "Variance $": "QoQ/YoY Variance ($)",
                           "Variance %": "QoQ/YoY Variance (%)"})
    return g


exp_by_dept_q = build_expense_rollup(["Department"], "Fiscal Quarter", quarter_order)
exp_by_dept_y = build_expense_rollup(["Department"], "Fiscal Year", year_order)
exp_by_dept_cat_q = expenses.groupby(["Department", "Category", "Fiscal Quarter"], as_index=False)["Amount ($)"].sum()
exp_by_dept_cat_y = expenses.groupby(["Department", "Category", "Fiscal Year"], as_index=False)["Amount ($)"].sum()

exp_by_dept_q = add_yoy_on_quarters(exp_by_dept_q, "Department")

# ---------------------------------------------------------------------------
# 5. Headcount rollups — both AVERAGE (mean of the monthly values in the period)
#    and ENDING (last month's snapshot) headcount. Headcount is a stock, not a
#    flow, so "rollup" here means these two different snapshots, not a sum.
# ---------------------------------------------------------------------------
def build_headcount_rollup(period_col):
    avg = (
        headcount.groupby(["Department", period_col], as_index=False)["Headcount"]
        .mean()
        .rename(columns={"Headcount": "Avg Headcount"})
    )
    last_month = headcount.groupby(["Department", period_col])["Date"].transform("max")
    snap = headcount[headcount["Date"] == last_month][["Department", period_col, "Headcount"]]
    snap = snap.rename(columns={"Headcount": "Ending Headcount"})
    out = avg.merge(snap, on=["Department", period_col])
    return out.sort_values(["Department", period_col]).reset_index(drop=True)


hc_by_dept_q = build_headcount_rollup("Fiscal Quarter")
hc_by_dept_y = build_headcount_rollup("Fiscal Year")

# ---------------------------------------------------------------------------
# 6. Budget vs Actual rollups — sum Budget & Actual, recompute variance
# ---------------------------------------------------------------------------
def build_bva_rollup(period_col):
    g = bva.groupby(["Line Item", period_col], as_index=False)[["Budget ($)", "Actual ($)"]].sum()
    g["Variance ($)"] = g["Actual ($)"] - g["Budget ($)"]
    g["Variance (%)"] = np.where(g["Budget ($)"] != 0, g["Variance ($)"] / g["Budget ($)"], np.nan)
    return g


bva_q = build_bva_rollup("Fiscal Quarter")
bva_y = build_bva_rollup("Fiscal Year")

# ---------------------------------------------------------------------------
# 7. PL rollups (Revenue, Opex, Operating Profit, Operating Margin)
#    Renamed from PL_Summary's "Gross Profit/Margin" per project convention:
#    no COGS line in this dataset, so use Operating Profit / Operating Margin.
# ---------------------------------------------------------------------------
pl_summary = pl_summary.rename(columns={
    "Gross Profit ($)": "Operating Profit ($)",
    "Gross Margin (%)": "Operating Margin (%)",
})

def build_pl_rollup(period_col):
    g = pl_summary.groupby(period_col, as_index=False)[["Total Revenue ($)", "Total Opex ($)"]].sum()
    g["Operating Profit ($)"] = g["Total Revenue ($)"] - g["Total Opex ($)"]
    g["Operating Margin (%)"] = g["Operating Profit ($)"] / g["Total Revenue ($)"]
    return g


pl_q = build_pl_rollup("Fiscal Quarter")
pl_y = build_pl_rollup("Fiscal Year")
pl_q = add_variance(pl_q, [], "Total Revenue ($)", "Fiscal Quarter", quarter_order, 1) if False else pl_q  # placeholder, sequential variance added below

def add_sequential_variance(df, period_col, period_order, value_cols):
    df = df.copy()
    df["_ord"] = df[period_col].map({p: i for i, p in enumerate(period_order)})
    df = df.sort_values("_ord").drop(columns="_ord")
    for vc in value_cols:
        prior = df[vc].shift(1)
        df[f"{vc.replace(' ($)','')} QoQ/YoY Var ($)"] = df[vc] - prior
        df[f"{vc.replace(' ($)','')} QoQ/YoY Var (%)"] = np.where(prior.notna() & (prior != 0), (df[vc]-prior)/prior, np.nan)
    return df


pl_q = add_sequential_variance(pl_q, "Fiscal Quarter", quarter_order, ["Total Revenue ($)", "Total Opex ($)", "Operating Profit ($)"])
pl_y = add_sequential_variance(pl_y, "Fiscal Year", year_order, ["Total Revenue ($)", "Total Opex ($)", "Operating Profit ($)"])

# ---------------------------------------------------------------------------
# 8. STEP 2 — Regional Revenue & Go-to-Market Investment / Product Line
#    Revenue & R&D Investment (driver-based allocation, approved)
#
# CYCLE 2 REFRAME (supersedes Cycle 1's rename_instruction_contribution_
# margin.md in full — that file is no longer applied): two earlier margin-
# style labels for this same data (a standard-margin term, then an "adjusted"
# variant of it — see git history / the superseded rename doc for the exact
# prior wording) both still implied a per-segment PROFITABILITY reading. The
# underlying defect: under a proportional revenue-share allocation key, the
# resulting % is mathematically identical across every segment sharing an
# allocation base in the same period (see assumptions_and_limitations.md) —
# no wording fix removes that, only a data-shape change does. So as of this
# cycle: NO cross-segment % table exists anywhere in these outputs. Only $
# figures are shown side-by-side across segments (Revenue, Allocated cost,
# Net-of-allocated-cost — these ARE valid to compare, since $ differences
# reflect real revenue/segment size). The % is retained ONLY as a per-segment
# trend series (this segment's own % over time), built as a separate
# long-format table never merged back into the cross-segment $ table, so a
# UI built on top of this data structurally cannot place two segments' %
# side by side.
#
# ALLOCATION METHOD — UNCHANGED FROM CYCLE 1 (math not touched, only the
# framing/presentation changed):
#   Region cut:   Sales & Marketing + Customer Success opex allocated to region
#                 by that region's share of total revenue in the period.
#                 Region Net of GTM Cost = Region Revenue - Region-allocated (S&M + CS)
#   Product cut:  R&D opex allocated to product line by that product line's
#                 share of revenue AMONG THE R&D-ALLOCATION-BASE LINES ONLY,
#                 excluding Professional Services (see fix below, RETAINED
#                 from Cycle 1 — this was a math fix, not a framing fix).
#                 Product Net of R&D Cost = Product Revenue - Product-allocated R&D
#   G&A is EXCLUDED from both cuts (corporate overhead, no plausible tie to a
#   region or product) and reported separately as unallocated overhead.
#
#   FIX (retained from Cycle 1, real correction, not a label change):
#   Professional Services is a services line, not something R&D builds, so it
#   must not receive an R&D allocation. R&D opex is split only across Core
#   Platform, Add-on: Forecasting, and Add-on: Reporting, by their relative
#   revenue share among those three product lines only. Professional
#   Services' Allocated R&D Opex ($) = 0, so its Net of R&D Cost ($) equals
#   its own revenue exactly (and its own % trend is a fixed 100% every
#   period, by construction).
#
#   THESE ARE TWO SEPARATE, PARTIAL VIEWS, NOT A FULL SEGMENT P&L, AND NOT A
#   PROFITABILITY MEASURE:
#   - Region Net of GTM Cost is net of go-to-market cost (S&M + CS) ONLY.
#     R&D and G&A are not included.
#   - Product Net of R&D Cost is net of R&D cost ONLY (and, for Professional
#     Services, net of nothing at all). S&M, CS, and G&A are not included.
#   - Summing all four regions' Net of GTM Cost $ equals Total Revenue -
#     (S&M + CS), not Operating Profit. Same logic for product lines vs R&D.
#     This is checked explicitly in the verification section below.
#   - Region and Product views are NOT comparable to each other, since they
#     subtract different cost bases by design; segments are only comparable
#     to other segments within the same cut, and only on $.
#
#   Revenue share is the allocation key because the dataset has no finer
#   driver (no rep count by region, no engineer count by product line, no
#   time-tracking). Additionally, the split of R&D between Core Platform and
#   the Add-on lines should be read with low confidence: Core Platform
#   likely carries foundational engineering cost that benefits all product
#   lines, and this dataset has no way to separate platform-maintenance
#   spend from feature-specific spend.
# ---------------------------------------------------------------------------
GTM_DEPTS = ["Sales & Marketing", "Customer Success"]
RD_DEPT = "R&D"
RD_ALLOCATION_BASE_PRODUCT_LINES = ["Core Platform", "Add-on: Forecasting", "Add-on: Reporting"]
PROFESSIONAL_SERVICES_LABEL = "Professional Services"

RCM_LABEL = "Region Net of Go-to-Market Cost (net of Sales & Marketing + Customer Success ONLY — excludes R&D and G&A; not a profitability measure, shows go-to-market investment relative to revenue)"
PCM_LABEL = "Product Net of R&D Cost (net of R&D ONLY, and Professional Services excluded from the R&D allocation base entirely — excludes Sales & Marketing, Customer Success, and G&A; not a profitability measure, shows R&D investment relative to revenue)"


def build_region_contribution_margin(period_col, rev_df, total_rev_df, exp_dept_df):
    """Region Revenue - (Region Revenue / Total Revenue) x (S&M + CS opex), per period.
    NO % column — cross-segment % is structurally excluded per Cycle 2 Task 1. A
    single-segment % trend is built separately by build_pct_trend()."""
    gtm_total = (
        exp_dept_df[exp_dept_df["Department"].isin(GTM_DEPTS)]
        .groupby(period_col, as_index=False)["Amount ($)"]
        .sum()
        .rename(columns={"Amount ($)": "S&M + CS Opex ($)"})
    )
    tot_rev = total_rev_df[[period_col, "Total Revenue ($)"]]
    base = rev_df[["Region", period_col, "Revenue ($)"]].rename(columns={"Revenue ($)": "Region Revenue ($)"})
    out = base.merge(tot_rev, on=period_col).merge(gtm_total, on=period_col)
    out["Revenue Share"] = out["Region Revenue ($)"] / out["Total Revenue ($)"]
    out["Allocated S&M + CS Opex ($)"] = out["Revenue Share"] * out["S&M + CS Opex ($)"]
    out["Region Net of GTM Cost ($)"] = out["Region Revenue ($)"] - out["Allocated S&M + CS Opex ($)"]
    out["View"] = RCM_LABEL
    cols = [period_col, "Region", "Region Revenue ($)", "Revenue Share", "Allocated S&M + CS Opex ($)",
            "Region Net of GTM Cost ($)", "View"]
    return out[cols].sort_values(["Region", period_col]).reset_index(drop=True)


def build_product_contribution_margin(period_col, rev_df, total_rev_df, exp_dept_df):
    """Product Line Revenue - (Product Revenue / R&D-allocation-base Revenue) x R&D opex, per period.
    Professional Services is excluded from the R&D allocation base entirely (fix retained from
    Cycle 1) — it receives Allocated R&D Opex ($) = 0, so its Net of R&D Cost ($) equals its own
    revenue. R&D is split only across Core Platform, Add-on: Forecasting, and Add-on: Reporting,
    by their relative revenue share among those three. NO % column — cross-segment % is
    structurally excluded per Cycle 2 Task 1. A single-segment % trend is built separately by
    build_pct_trend()."""
    rd_total = (
        exp_dept_df[exp_dept_df["Department"] == RD_DEPT]
        .groupby(period_col, as_index=False)["Amount ($)"]
        .sum()
        .rename(columns={"Amount ($)": "R&D Opex ($)"})
    )
    base = rev_df[["Product Line", period_col, "Revenue ($)"]].rename(columns={"Revenue ($)": "Product Revenue ($)"})

    # Revenue base for the allocation SHARE excludes Professional Services —
    # the share denominator is "revenue among the three R&D-allocation-base
    # product lines", not total company revenue.
    rd_base_rev = (
        base[base["Product Line"].isin(RD_ALLOCATION_BASE_PRODUCT_LINES)]
        .groupby(period_col, as_index=False)["Product Revenue ($)"]
        .sum()
        .rename(columns={"Product Revenue ($)": "R&D-Allocation-Base Revenue ($)"})
    )

    out = base.merge(rd_total, on=period_col).merge(rd_base_rev, on=period_col)
    out["Revenue Share"] = np.where(
        out["Product Line"].isin(RD_ALLOCATION_BASE_PRODUCT_LINES),
        out["Product Revenue ($)"] / out["R&D-Allocation-Base Revenue ($)"],
        0.0,
    )
    out["Allocated R&D Opex ($)"] = out["Revenue Share"] * out["R&D Opex ($)"]
    out["Product Net of R&D Cost ($)"] = out["Product Revenue ($)"] - out["Allocated R&D Opex ($)"]
    out["View"] = PCM_LABEL
    cols = [period_col, "Product Line", "Product Revenue ($)", "Revenue Share", "Allocated R&D Opex ($)",
            "Product Net of R&D Cost ($)", "View"]
    return out[cols].sort_values(["Product Line", period_col]).reset_index(drop=True)


def build_pct_trend(cm_df, period_col, segment_col, revenue_col, net_col, pct_col_name):
    """Long-format, SINGLE-SEGMENT-ONLY % series (segment, period, %). Deliberately kept as a
    separate table from the cross-segment $ table above — this % must only ever be displayed for
    one segment at a time (a trend over its own history), never placed next to another segment's %
    in the same table/chart, per Cycle 2 Task 1 items 2-3. A UI reading only this table has no
    columns available to build a cross-segment % comparison even by mistake."""
    out = cm_df[[period_col, segment_col, revenue_col, net_col]].copy()
    out[pct_col_name] = out[net_col] / out[revenue_col]
    return out[[period_col, segment_col, pct_col_name]].sort_values([segment_col, period_col]).reset_index(drop=True)


region_cm_q = build_region_contribution_margin("Fiscal Quarter", rev_by_region_q, pl_q, expenses)
region_cm_y = build_region_contribution_margin("Fiscal Year", rev_by_region_y, pl_y, expenses)
product_cm_q = build_product_contribution_margin("Fiscal Quarter", rev_by_product_q, pl_q, expenses)
product_cm_y = build_product_contribution_margin("Fiscal Year", rev_by_product_y, pl_y, expenses)

region_gtm_pct_q = build_pct_trend(region_cm_q, "Fiscal Quarter", "Region", "Region Revenue ($)",
                                    "Region Net of GTM Cost ($)", "Region Net of GTM Cost (%)")
region_gtm_pct_y = build_pct_trend(region_cm_y, "Fiscal Year", "Region", "Region Revenue ($)",
                                    "Region Net of GTM Cost ($)", "Region Net of GTM Cost (%)")
product_rd_pct_q = build_pct_trend(product_cm_q, "Fiscal Quarter", "Product Line", "Product Revenue ($)",
                                    "Product Net of R&D Cost ($)", "Product Net of R&D Cost (%)")
product_rd_pct_y = build_pct_trend(product_cm_y, "Fiscal Year", "Product Line", "Product Revenue ($)",
                                    "Product Net of R&D Cost ($)", "Product Net of R&D Cost (%)")


# G&A reported separately — unallocated corporate overhead, not folded into either cut
ga_overhead_q = expenses[expenses["Department"] == "G&A"].groupby("Fiscal Quarter", as_index=False)["Amount ($)"].sum()
ga_overhead_q = ga_overhead_q.rename(columns={"Amount ($)": "G&A Unallocated Overhead ($)"})
ga_overhead_y = expenses[expenses["Department"] == "G&A"].groupby("Fiscal Year", as_index=False)["Amount ($)"].sum()
ga_overhead_y = ga_overhead_y.rename(columns={"Amount ($)": "G&A Unallocated Overhead ($)"})

# ---------------------------------------------------------------------------
# 10. STEP 3 — Decomposition
#
# (a) Salaries & Benefits: TRUE volume/rate bridge, since a real unit count
#     (headcount) exists. Uses AVERAGE headcount for the period (not ending),
#     because S&B cost accrues over the period, not at a point in time.
#     Volume effect = change in headcount x prior period cost-per-head.
#     Rate effect    = new headcount x change in cost-per-head.
#     By construction, Volume + Rate = Actual variance exactly — checked below.
#
# (b) Revenue and all other expense categories (Software & Tools, Other
#     Opex): NO unit count exists for these, so a volume/rate split would be
#     invented, not calculated. Instead: breadth/concentration — whether a
#     period's variance is spread across most segments or driven by one or
#     two. THRESHOLD USED (stated per system-prompt rule 7): a single
#     segment accounting for >=60% of GROSS variance (sum of |segment
#     variances|, not the net total — net total can be near zero when
#     segments offset, which would make a share-of-net-total figure
#     meaningless or >100%) is flagged "Concentrated"; otherwise "Broad-based".
# ---------------------------------------------------------------------------

# --- (a) Salaries & Benefits volume/rate bridge -----------------------------
def build_salaries_volume_rate(period_col, period_order, hc_df):
    sb = (
        expenses[expenses["Category"] == "Salaries & Benefits"]
        .groupby(["Department", period_col], as_index=False)["Amount ($)"]
        .sum()
        .rename(columns={"Amount ($)": "S&B Amount ($)"})
    )
    sb = sb.merge(hc_df[["Department", period_col, "Avg Headcount"]], on=["Department", period_col])
    sb["Cost per Head ($)"] = sb["S&B Amount ($)"] / sb["Avg Headcount"]

    sb["_ord"] = sb[period_col].map({p: i for i, p in enumerate(period_order)})
    sb = sb.sort_values(["Department", "_ord"]).drop(columns="_ord")

    g = sb.groupby("Department")
    sb["Prior Avg Headcount"] = g["Avg Headcount"].shift(1)
    sb["Prior Cost per Head ($)"] = g["Cost per Head ($)"].shift(1)
    sb["Prior S&B Amount ($)"] = g["S&B Amount ($)"].shift(1)

    sb["Headcount Change"] = sb["Avg Headcount"] - sb["Prior Avg Headcount"]
    sb["Cost-per-Head Change ($)"] = sb["Cost per Head ($)"] - sb["Prior Cost per Head ($)"]
    sb["Volume Effect ($)"] = sb["Headcount Change"] * sb["Prior Cost per Head ($)"]
    sb["Rate Effect ($)"] = sb["Avg Headcount"] * sb["Cost-per-Head Change ($)"]
    sb["Bridge Total ($)"] = sb["Volume Effect ($)"] + sb["Rate Effect ($)"]
    sb["Actual Variance ($)"] = sb["S&B Amount ($)"] - sb["Prior S&B Amount ($)"]

    cols = [period_col, "Department", "Avg Headcount", "Cost per Head ($)", "S&B Amount ($)",
            "Headcount Change", "Cost-per-Head Change ($)", "Volume Effect ($)", "Rate Effect ($)",
            "Bridge Total ($)", "Actual Variance ($)"]
    return sb[cols].reset_index(drop=True)


sb_volrate_q = build_salaries_volume_rate("Fiscal Quarter", quarter_order, hc_by_dept_q)
sb_volrate_y = build_salaries_volume_rate("Fiscal Year", year_order, hc_by_dept_y)

# --- (b) Breadth/concentration for Revenue and other expense categories -----
CONCENTRATION_THRESHOLD = 0.60  # >=60% of gross variance from one segment = "Concentrated"


def add_qoq_variance_generic(df, group_cols, value_col, period_col, period_order):
    df = df.copy()
    df["_ord"] = df[period_col].map({p: i for i, p in enumerate(period_order)})
    df = df.sort_values(group_cols + ["_ord"])
    df["Variance ($)"] = df.groupby(group_cols)[value_col].diff()
    return df.drop(columns="_ord")


def build_breadth_concentration(df, dim_col, period_col, period_order, line_item_label,
                                 threshold=CONCENTRATION_THRESHOLD):
    rows = []
    for period in period_order:
        sub = df[df[period_col] == period].dropna(subset=["Variance ($)"])
        if sub.empty:
            continue
        total_var = sub["Variance ($)"].sum()
        gross_var = sub["Variance ($)"].abs().sum()
        n_segments = sub[dim_col].nunique()
        if total_var > 0:
            n_same_direction = int((sub["Variance ($)"] > 0).sum())
        elif total_var < 0:
            n_same_direction = int((sub["Variance ($)"] < 0).sum())
        else:
            n_same_direction = 0
        if gross_var == 0:
            top_segment, top_share = None, np.nan
            flag = "No variance (flat period-over-period)"
        else:
            top_row = sub.loc[sub["Variance ($)"].abs().idxmax()]
            top_segment = top_row[dim_col]
            top_share = abs(top_row["Variance ($)"]) / gross_var
            if top_share >= threshold:
                flag = f"Concentrated in {top_segment} ({top_share:.0%} of gross variance, threshold {threshold:.0%})"
            else:
                flag = f"Broad-based across {n_same_direction} of {n_segments} segments moving the same direction"
        rows.append({
            period_col: period,
            "Line Item": line_item_label,
            "Total Variance ($)": total_var,
            "Gross Variance ($)": gross_var,
            "Segments Moving Same Direction": n_same_direction,
            "Total Segments": n_segments,
            "Top Contributor": top_segment,
            "Top Contributor Share": top_share,
            "Breadth/Concentration Flag": flag,
        })
    return pd.DataFrame(rows)


# Revenue breadth — by region and by product line (two cuts of the same total)
rev_region_var_q = add_qoq_variance_generic(revenue.groupby(["Region", "Fiscal Quarter"], as_index=False)["Revenue ($)"].sum(),
                                             ["Region"], "Revenue ($)", "Fiscal Quarter", quarter_order)
rev_product_var_q = add_qoq_variance_generic(revenue.groupby(["Product Line", "Fiscal Quarter"], as_index=False)["Revenue ($)"].sum(),
                                              ["Product Line"], "Revenue ($)", "Fiscal Quarter", quarter_order)
rev_region_var_y = add_qoq_variance_generic(revenue.groupby(["Region", "Fiscal Year"], as_index=False)["Revenue ($)"].sum(),
                                             ["Region"], "Revenue ($)", "Fiscal Year", year_order)
rev_product_var_y = add_qoq_variance_generic(revenue.groupby(["Product Line", "Fiscal Year"], as_index=False)["Revenue ($)"].sum(),
                                              ["Product Line"], "Revenue ($)", "Fiscal Year", year_order)

breadth_rev_region_q = build_breadth_concentration(rev_region_var_q, "Region", "Fiscal Quarter", quarter_order, "Revenue (by Region)")
breadth_rev_product_q = build_breadth_concentration(rev_product_var_q, "Product Line", "Fiscal Quarter", quarter_order, "Revenue (by Product Line)")
breadth_rev_region_y = build_breadth_concentration(rev_region_var_y, "Region", "Fiscal Year", year_order, "Revenue (by Region)")
breadth_rev_product_y = build_breadth_concentration(rev_product_var_y, "Product Line", "Fiscal Year", year_order, "Revenue (by Product Line)")

# Expense category breadth — Software & Tools and Other Opex, by department
breadth_exp_frames_q = []
breadth_exp_frames_y = []
for cat in ["Software & Tools", "Other Opex"]:
    cat_df_q = expenses[expenses["Category"] == cat].groupby(["Department", "Fiscal Quarter"], as_index=False)["Amount ($)"].sum()
    cat_df_q = add_qoq_variance_generic(cat_df_q, ["Department"], "Amount ($)", "Fiscal Quarter", quarter_order)
    breadth_exp_frames_q.append(build_breadth_concentration(cat_df_q, "Department", "Fiscal Quarter", quarter_order, f"{cat} (by Department)"))

    cat_df_y = expenses[expenses["Category"] == cat].groupby(["Department", "Fiscal Year"], as_index=False)["Amount ($)"].sum()
    cat_df_y = add_qoq_variance_generic(cat_df_y, ["Department"], "Amount ($)", "Fiscal Year", year_order)
    breadth_exp_frames_y.append(build_breadth_concentration(cat_df_y, "Department", "Fiscal Year", year_order, f"{cat} (by Department)"))

breadth_all_q = pd.concat(
    [breadth_rev_region_q, breadth_rev_product_q] + breadth_exp_frames_q, ignore_index=True
)
breadth_all_y = pd.concat(
    [breadth_rev_region_y, breadth_rev_product_y] + breadth_exp_frames_y, ignore_index=True
)

# ---------------------------------------------------------------------------
# 11. VERIFY: rollups must tie out exactly to PL_Summary / raw totals
# ---------------------------------------------------------------------------
print("=" * 70)
print("VERIFICATION")
print("=" * 70)

errors = []

# 8a. Revenue rollup totals vs PL_Summary Total Revenue, by quarter
rev_q_total = revenue.groupby("Fiscal Quarter")["Revenue ($)"].sum()
pl_rev_q = pl_q.set_index("Fiscal Quarter")["Total Revenue ($)"]
diff = (rev_q_total - pl_rev_q).abs()
if diff.max() > 0.01:
    errors.append(f"Revenue quarterly rollup vs PL_Summary mismatch: max diff {diff.max():.2f}")
else:
    print(f"OK  Revenue (by region/product, summed) ties to PL_Summary Total Revenue by quarter (max diff ${diff.max():.4f})")

# 8b. Region rollup sums to same total as product-line rollup, per quarter
region_q_total = rev_by_region_q.groupby("Fiscal Quarter")["Revenue ($)"].sum()
product_q_total = rev_by_product_q.groupby("Fiscal Quarter")["Revenue ($)"].sum()
diff2 = (region_q_total - product_q_total).abs()
if diff2.max() > 0.01:
    errors.append(f"Region-cut vs Product-cut revenue mismatch: max diff {diff2.max():.2f}")
else:
    print(f"OK  Revenue by Region and by Product Line tie to each other, per quarter (max diff ${diff2.max():.4f})")

# 8c. Expense rollup totals vs PL_Summary Total Opex, by quarter
exp_q_total = expenses.groupby("Fiscal Quarter")["Amount ($)"].sum()
pl_opex_q = pl_q.set_index("Fiscal Quarter")["Total Opex ($)"]
diff3 = (exp_q_total - pl_opex_q).abs()
if diff3.max() > 0.01:
    errors.append(f"Expense quarterly rollup vs PL_Summary mismatch: max diff {diff3.max():.2f}")
else:
    print(f"OK  Expenses (by department, summed) tie to PL_Summary Total Opex by quarter (max diff ${diff3.max():.4f})")

# 8d. Annual rollups tie to sum of their own quarters
rev_y_check = revenue.groupby("Fiscal Year")["Revenue ($)"].sum()
pl_rev_y = pl_y.set_index("Fiscal Year")["Total Revenue ($)"]
diff4 = (rev_y_check - pl_rev_y).abs()
if diff4.max() > 0.01:
    errors.append(f"Revenue annual rollup vs PL_Summary mismatch: max diff {diff4.max():.2f}")
else:
    print(f"OK  Revenue annual rollup ties to PL_Summary Total Revenue by fiscal year (max diff ${diff4.max():.4f})")

# 8e. BvA rollup Actual vs raw Revenue actuals, per quarter (Line Item == 'Revenue')
bva_rev_q = bva_q[bva_q["Line Item"] == "Revenue"].set_index("Fiscal Quarter")["Actual ($)"]
diff5 = (bva_rev_q - rev_q_total).abs()
if diff5.max() > 0.01:
    errors.append(f"BvA Revenue actuals vs raw Revenue rollup mismatch: max diff {diff5.max():.2f}")
else:
    print(f"OK  Budget_vs_Actual Revenue actuals tie to raw Revenue rollup by quarter (max diff ${diff5.max():.4f})")

# 8f. Headcount snapshot count check: 4 departments x N quarters/years, no missing
exp_hc_rows_q = 4 * len(quarter_order)
if len(hc_by_dept_q) != exp_hc_rows_q:
    errors.append(f"Headcount quarterly snapshot row count off: got {len(hc_by_dept_q)}, expected {exp_hc_rows_q}")
else:
    print(f"OK  Headcount quarterly snapshot has complete coverage ({len(hc_by_dept_q)} rows = 4 depts x {len(quarter_order)} quarters)")

# 8g. Checkpoint: starting headcount (first raw month, Jul 2023) = 135,
# ending headcount (last raw month, Jun 2026) = 167 (company-wide totals,
# per project brief). NOTE: this is the first/last MONTH, not "ending
# headcount of the first quarter" — headcount already moved within Q1
# (135 in Jul 2023 -> 138 by Sep 2023, the last month of Q1 FY2024).
start_hc = headcount[headcount["Date"] == headcount["Date"].min()]["Headcount"].sum()
end_hc = headcount[headcount["Date"] == headcount["Date"].max()]["Headcount"].sum()
if start_hc != 135:
    errors.append(f"Starting headcount checkpoint failed: got {start_hc}, expected 135")
else:
    print(f"OK  Starting headcount (first month, {headcount['Date'].min().date()}) = 135, matches checkpoint")
if end_hc != 167:
    errors.append(f"Ending headcount checkpoint failed: got {end_hc}, expected 167")
else:
    print(f"OK  Ending headcount (last month, {headcount['Date'].max().date()}) = 167, matches checkpoint")

if errors:
    print("\nFAILURES SO FAR:")
    for e in errors:
        print(" -", e)
else:
    print(f"All checks passed so far. {len(quarter_order)} fiscal quarters, {len(year_order)} fiscal years covered.")

# 9h. STEP 2 tie-out: sum of Region CM $ across all 4 regions, per quarter,
# must equal Total Revenue - S&M - CS for that quarter (NOT Operating Profit —
# this view excludes R&D and G&A by design).
region_cm_sum_q = region_cm_q.groupby("Fiscal Quarter")["Region Net of GTM Cost ($)"].sum()
sm_cs_q = (
    expenses[expenses["Department"].isin(GTM_DEPTS)]
    .groupby("Fiscal Quarter")["Amount ($)"].sum()
)
total_rev_q_series = pl_q.set_index("Fiscal Quarter")["Total Revenue ($)"]
expected_q = total_rev_q_series - sm_cs_q
diff6 = (region_cm_sum_q - expected_q).abs()
if diff6.max() > 0.01:
    errors.append(f"Region CM sum vs (Total Revenue - S&M - CS) mismatch: max diff {diff6.max():.2f}")
else:
    print(f"OK  Region Net of GTM Cost sums to Total Revenue - S&M - CS, every quarter (max diff ${diff6.max():.4f})")

# 9i. STEP 2 tie-out: sum of Product CM $ across all 4 product lines, per quarter,
# must equal Total Revenue - R&D for that quarter.
product_cm_sum_q = product_cm_q.groupby("Fiscal Quarter")["Product Net of R&D Cost ($)"].sum()
rd_q = expenses[expenses["Department"] == RD_DEPT].groupby("Fiscal Quarter")["Amount ($)"].sum()
expected_q2 = total_rev_q_series - rd_q
diff7 = (product_cm_sum_q - expected_q2).abs()
if diff7.max() > 0.01:
    errors.append(f"Product CM sum vs (Total Revenue - R&D) mismatch: max diff {diff7.max():.2f}")
else:
    print(f"OK  Product Net of R&D Cost sums to Total Revenue - R&D, every quarter, even with Professional Services excluded from the allocation base (max diff ${diff7.max():.4f})")

print()
if errors:
    print("ALL FAILURES:")
    for e in errors:
        print(" -", e)
else:
    print("All checks passed, including both Step 2 segment investment-view tie-outs.")

# 11j. STEP 3 tie-out: Volume Effect + Rate Effect = Actual Variance exactly, for every
# department/period where a prior period exists (Salaries & Benefits bridge).
bridge_check = sb_volrate_q.dropna(subset=["Actual Variance ($)"])
diff8 = (bridge_check["Bridge Total ($)"] - bridge_check["Actual Variance ($)"]).abs()
if diff8.max() > 0.01:
    errors.append(f"S&B volume/rate bridge does not sum to actual variance: max diff {diff8.max():.4f}")
else:
    print(f"OK  Salaries & Benefits Volume Effect + Rate Effect = Actual Variance exactly, every department/quarter (max diff ${diff8.max():.6f})")

# 11k. STEP 3 sanity: breadth/concentration total variance ties to the raw QoQ variance
# it was built from, for revenue by region (spot-check one cut).
breadth_total_check = breadth_rev_region_q.set_index("Fiscal Quarter")["Total Variance ($)"]
pl_rev_var_check = pl_q.set_index("Fiscal Quarter")["Total Revenue QoQ/YoY Var ($)"]
common_idx = breadth_total_check.index.intersection(pl_rev_var_check.dropna().index)
diff9 = (breadth_total_check.loc[common_idx] - pl_rev_var_check.loc[common_idx]).abs()
if diff9.max() > 0.01:
    errors.append(f"Breadth total variance (Revenue by Region) vs PL Total Revenue variance mismatch: max diff {diff9.max():.2f}")
else:
    print(f"OK  Breadth/concentration total variance (Revenue by Region) ties to PL_Quarterly's Total Revenue QoQ variance (max diff ${diff9.max():.4f})")

print()
if errors:
    print("ALL FAILURES (final):")
    for e in errors:
        print(" -", e)
else:
    print("All checks passed, including Step 2 segment margin tie-outs and Step 3 decomposition tie-outs.")

# ---------------------------------------------------------------------------
# 9. Save rollups for the next step (segment investment views + AI narrative)
# ---------------------------------------------------------------------------
with pd.ExcelWriter("rollups_output.xlsx", engine="openpyxl") as writer:
    pl_q.to_excel(writer, sheet_name="PL_Quarterly", index=False)
    pl_y.to_excel(writer, sheet_name="PL_Annual", index=False)
    rev_by_region_q.to_excel(writer, sheet_name="Rev_by_Region_Q", index=False)
    rev_by_region_y.to_excel(writer, sheet_name="Rev_by_Region_Y", index=False)
    rev_by_product_q.to_excel(writer, sheet_name="Rev_by_Product_Q", index=False)
    rev_by_product_y.to_excel(writer, sheet_name="Rev_by_Product_Y", index=False)
    exp_by_dept_q.to_excel(writer, sheet_name="Exp_by_Dept_Q", index=False)
    exp_by_dept_y.to_excel(writer, sheet_name="Exp_by_Dept_Y", index=False)
    exp_by_dept_cat_q.to_excel(writer, sheet_name="Exp_by_Dept_Cat_Q", index=False)
    exp_by_dept_cat_y.to_excel(writer, sheet_name="Exp_by_Dept_Cat_Y", index=False)
    hc_by_dept_q.to_excel(writer, sheet_name="Headcount_Q", index=False)
    hc_by_dept_y.to_excel(writer, sheet_name="Headcount_Y", index=False)
    bva_q.to_excel(writer, sheet_name="BvA_Q", index=False)
    bva_y.to_excel(writer, sheet_name="BvA_Y", index=False)
    region_cm_q.to_excel(writer, sheet_name="RegionNetGTMCost_Q", index=False)
    region_cm_y.to_excel(writer, sheet_name="RegionNetGTMCost_Y", index=False)
    product_cm_q.to_excel(writer, sheet_name="ProductNetRDCost_Q", index=False)
    product_cm_y.to_excel(writer, sheet_name="ProductNetRDCost_Y", index=False)
    region_gtm_pct_q.to_excel(writer, sheet_name="RegionGTMPctTrend_Q", index=False)
    region_gtm_pct_y.to_excel(writer, sheet_name="RegionGTMPctTrend_Y", index=False)
    product_rd_pct_q.to_excel(writer, sheet_name="ProductRDPctTrend_Q", index=False)
    product_rd_pct_y.to_excel(writer, sheet_name="ProductRDPctTrend_Y", index=False)
    ga_overhead_q.to_excel(writer, sheet_name="GA_Unallocated_Q", index=False)
    ga_overhead_y.to_excel(writer, sheet_name="GA_Unallocated_Y", index=False)
    sb_volrate_q.to_excel(writer, sheet_name="SB_VolRate_Q", index=False)
    sb_volrate_y.to_excel(writer, sheet_name="SB_VolRate_Y", index=False)
    breadth_all_q.to_excel(writer, sheet_name="Breadth_Concentration_Q", index=False)
    breadth_all_y.to_excel(writer, sheet_name="Breadth_Concentration_Y", index=False)

print("\nSaved rollups_output.xlsx (all rollup + segment margin tables, one sheet each).")
print("\nSample — Region Net of GTM Cost (Q1 FY2024, $ only — no cross-segment %):")
print(region_cm_q[region_cm_q["Fiscal Quarter"] == "Q1 FY2024"].to_string(index=False))
print("\nSample — Product Net of R&D Cost (Q1 FY2024, $ only, Professional Services excluded from the allocation base):")
print(product_cm_q[product_cm_q["Fiscal Quarter"] == "Q1 FY2024"].to_string(index=False))
print("\nSample — Region Net of GTM Cost (%) single-segment trend, North America only (all quarters — never shown alongside another region's %):")
print(region_gtm_pct_q[region_gtm_pct_q["Region"] == "North America"].to_string(index=False))
print("\nSample — Salaries & Benefits Volume/Rate Bridge (Q2 FY2024, first quarter with a prior period):")
print(sb_volrate_q[sb_volrate_q["Fiscal Quarter"] == "Q2 FY2024"].to_string(index=False))
print("\nSample — Breadth/Concentration, Revenue by Region (all quarters):")
print(breadth_rev_region_q[["Fiscal Quarter", "Total Variance ($)", "Top Contributor", "Top Contributor Share", "Breadth/Concentration Flag"]].to_string(index=False))

# ---------------------------------------------------------------------------
# 12. STEP 4a — Budget vs Actual flags + recurrence tracking
#
# Thresholds reverse-engineered from the organizer's own reference workbook
# (Northwind_PL_and_BvA_Workbook.xlsx, Budget_vs_Actual tab) and confirmed to
# reproduce its flags on the monthly data with a 100% match (excluding blank
# trailing rows): |Variance %| > 8% = Major Miss, > 4% = Watch, else On Track.
# Applied here to the QUARTERLY and ANNUAL aggregated variance %, not
# re-derived from monthly flags, since the narrative operates at whatever
# period grain is selected.
# ---------------------------------------------------------------------------
def classify_bva_flag(v):
    if pd.isna(v):
        return None
    v = abs(v)
    if v > 0.08:
        return "Major Miss"
    if v > 0.04:
        return "Watch"
    return "On Track"


def add_bva_flags_and_streak(df, period_col, period_order):
    df = df.copy()
    df["Flag"] = df["Variance (%)"].apply(classify_bva_flag)
    df["_ord"] = df[period_col].map({p: i for i, p in enumerate(period_order)})
    df = df.sort_values(["Line Item", "_ord"])

    def streak(flags):
        out, run = [], 0
        for f in flags:
            run = run + 1 if f == "Watch" else 0
            out.append(run)
        return out

    df["Consecutive Watch Periods (ending here)"] = df.groupby("Line Item")["Flag"].transform(
        lambda s: pd.Series(streak(s.tolist()), index=s.index)
    )
    return df.drop(columns="_ord").reset_index(drop=True)


bva_q = add_bva_flags_and_streak(bva_q, "Fiscal Quarter", quarter_order)
bva_y = add_bva_flags_and_streak(bva_y, "Fiscal Year", year_order)

# ---------------------------------------------------------------------------
# 13. STEP 4b — Headcount, Revenue per Headcount, and Opex per Employee
#
# CYCLE 2 TASK 2 CORRECTION: the prior build attached a single COMPANY-WIDE
# Revenue-per-Headcount figure to every department row in one combined table
# "for convenience." Even though that figure was never actually computed per
# department (it was the same company-wide number repeated), the shape
# invited exactly the misreading the Region/Product pages were just fixed
# for — a company-wide ratio sitting in a department-indexed row looks
# department-level even when it isn't. Fixed by splitting into three
# STRUCTURALLY separate tables, each incapable of producing the wrong
# reading because the disallowed dimension doesn't exist in that table:
#
#   1. build_headcount_department_trend — Department, Ending Headcount,
#      Prior Ending Headcount. Headcount ONLY, no revenue or opex column
#      exists in this table at all.
#   2. build_company_revenue_per_headcount — Total Revenue, Company Ending
#      Headcount, Revenue per Headcount ($, company-wide). NO Department
#      column exists in this table — it cannot be mistaken for a
#      department-level metric because there is no department dimension to
#      misread it against. Lives on the Headcount & Efficiency page.
#   3. build_opex_per_employee — Department, Opex ($), Ending Headcount,
#      Opex per Employee ($). This IS a valid department-level ratio (opex
#      and headcount both genuinely belong to the department), unlike
#      Revenue per Headcount — but it's a COST-DISCIPLINE metric (is this
#      department's spend per head rising or falling), not a
#      workforce-efficiency metric, so it lives on the Cost Structure page,
#      not Headcount & Efficiency.
#
# No department-level Revenue-per-Employee metric is computed or displayed
# anywhere in this project as of this cycle.
# ---------------------------------------------------------------------------
def build_headcount_department_trend(period_col, period_order, hc_df):
    """Department Ending Headcount, current vs prior period. Headcount ONLY —
    no revenue or opex column in this table, by design."""
    hc = hc_df.copy()
    hc["_ord"] = hc[period_col].map({p: i for i, p in enumerate(period_order)})
    hc = hc.sort_values(["Department", "_ord"])
    hc["Prior Ending Headcount"] = hc.groupby("Department")["Ending Headcount"].shift(1)
    hc = hc.drop(columns="_ord")
    cols = [period_col, "Department", "Ending Headcount", "Prior Ending Headcount"]
    return hc[cols].reset_index(drop=True)


def build_company_revenue_per_headcount(period_col, period_order, hc_df, pl_df):
    """COMPANY-WIDE Revenue per Headcount trend. NO Department column exists in
    this table — Total Revenue / Total Ending Headcount, per period, current
    vs prior."""
    company_hc = hc_df.groupby(period_col, as_index=False)["Ending Headcount"].sum().rename(
        columns={"Ending Headcount": "Company Ending Headcount"}
    )
    company_hc["_ord"] = company_hc[period_col].map({p: i for i, p in enumerate(period_order)})
    company_hc = company_hc.sort_values("_ord").drop(columns="_ord")

    out = pl_df[[period_col, "Total Revenue ($)"]].merge(company_hc, on=period_col)
    out["_ord"] = out[period_col].map({p: i for i, p in enumerate(period_order)})
    out = out.sort_values("_ord")
    out["Prior Total Revenue ($)"] = out["Total Revenue ($)"].shift(1)
    out["Prior Company Ending Headcount"] = out["Company Ending Headcount"].shift(1)
    out = out.drop(columns="_ord")

    out["Revenue per Headcount ($, company-wide)"] = out["Total Revenue ($)"] / out["Company Ending Headcount"]
    out["Prior Revenue per Headcount ($, company-wide)"] = (
        out["Prior Total Revenue ($)"] / out["Prior Company Ending Headcount"]
    )
    cols = [period_col, "Total Revenue ($)", "Company Ending Headcount",
            "Revenue per Headcount ($, company-wide)", "Prior Revenue per Headcount ($, company-wide)"]
    return out[cols].reset_index(drop=True)


def build_opex_per_employee(period_col, exp_dept_df, hc_dept_df):
    """Department Opex ($) / Department Ending Headcount, per period — a
    COST-DISCIPLINE metric for the Cost Structure page, not a
    workforce-efficiency metric. Unlike Revenue per Headcount, this ratio IS
    department-level in a defensible sense (both the numerator and
    denominator genuinely belong to the department)."""
    opex = exp_dept_df[[period_col, "Department", "Amount ($)"]].copy()
    hc = hc_dept_df[[period_col, "Department", "Ending Headcount"]].copy()
    out = opex.merge(hc, on=[period_col, "Department"])
    out["Opex per Employee ($)"] = out["Amount ($)"] / out["Ending Headcount"]
    return out.sort_values(["Department", period_col]).reset_index(drop=True)


hc_dept_q = build_headcount_department_trend("Fiscal Quarter", quarter_order, hc_by_dept_q)
hc_dept_y = build_headcount_department_trend("Fiscal Year", year_order, hc_by_dept_y)
company_rev_per_hc_q = build_company_revenue_per_headcount("Fiscal Quarter", quarter_order, hc_by_dept_q, pl_q)
company_rev_per_hc_y = build_company_revenue_per_headcount("Fiscal Year", year_order, hc_by_dept_y, pl_y)
opex_per_employee_q = build_opex_per_employee("Fiscal Quarter", exp_by_dept_q, hc_by_dept_q)
opex_per_employee_y = build_opex_per_employee("Fiscal Year", exp_by_dept_y, hc_by_dept_y)

# ---------------------------------------------------------------------------
# 14. STEP 4c — Narrative generation pipeline (prompt population + API call)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a senior FP&A analyst producing board-ready commentary for Northwind Financial Co., a B2B SaaS company. You write the analysis section of an investor/board update: the numbers are already calculated and provided to you as structured data. Your job is to explain what happened and why, not to recompute or restate the numbers.

Rules:
1. Every claim must be traceable to a number in the input data. Never invent a figure, a cause, or a trend not supported by the data provided.
2. The volume/rate decomposition (for Salaries & Benefits) and the breadth/concentration measure (for revenue and other expense categories) are provided to you pre-calculated in the input data. Narrate these finished figures — do not attempt to calculate or infer a volume/rate split yourself from raw totals. If the input data doesn't include a decomposition for a given line, say so rather than guessing at one.
2b. Never use "Gross Profit" or "Gross Margin" — this dataset has no COGS line. Use "Operating Profit" and "Operating Margin" throughout.
2c. The region view ("Net of GTM Cost") and product line view ("Net of R&D Cost") are investment-proportionality measures, not profitability or margin measures — they show whether go-to-market spend (region) or R&D spend (product line) is growing in proportion to revenue, nothing more. The input data provides these as $ figures only (Revenue, Allocated cost, Net-of-allocated-cost) per segment for the current period, plus a separate single-segment % trend series when one is given to you. NEVER state or imply a profitability or efficiency ranking between segments from either the $ figures or the % trend — a larger Net-of-cost $ figure reflects a larger segment, not better unit economics, and the % trend for one segment says nothing about any other segment's %, because no other segment's % is ever provided to you in the same context. If you are given a % trend for a single segment, narrate it only as that segment's own investment-proportionality trend over time (e.g. "North America's go-to-market cost has held at approximately X% of its own revenue for three consecutive quarters"). The Region cut and the Product cut are NEVER comparable to each other (different cost bases subtracted by design) — do not compare a region's figures to a product line's figures.
3. Lead with the most material item first, not chronologically or alphabetically. Materiality = largest absolute dollar variance or largest percentage swing, whichever a board member would ask about first.
4. One sentence per material finding. No hedging language ("it appears," "seems to suggest," "could potentially"). State the finding, then the evidence, in the same sentence or the next.
5. No filler, no motivational framing, no phrases like "exciting growth" or "strong momentum" unless the data specifically supports the magnitude of that claim.
6. If a number is ambiguous or the input data doesn't support a clean explanation (e.g. a variance with no obvious driver in the segment breakdown), say so directly: "Driver not identifiable from segment-level data" rather than guessing.
7. Where you flag something as a risk or a positive, state the threshold you're using (e.g. ">5% variance," "two consecutive quarters of decline") so a reader can apply the same lens to future periods.
8. Output in plain prose, organized under the section headers given in the user prompt. No bullet points unless a header explicitly asks for a list. No markdown headers in your output — the sections will be inserted into a formatted document separately.
9. Length: 2-4 sentences per section. This is a first draft for an analyst to review and tighten, not a finished investor letter."""


def fmt_money(x):
    if pd.isna(x):
        return "N/A"
    return f"${x:,.0f}"


def fmt_pct(x):
    if pd.isna(x):
        return "N/A"
    return f"{x:+.1%}"


def build_user_prompt(period_col, period_order, current_period, prior_period, comparison_label,
                       pl_df, rev_region_df, rev_product_df, region_cm_df, product_cm_df,
                       exp_dept_df, sb_df, breadth_df, hc_dept_df, company_rev_df, bva_df):
    pl_row = pl_df[pl_df[period_col] == current_period].iloc[0]
    pl_prior_row = pl_df[pl_df[period_col] == prior_period].iloc[0] if prior_period in pl_df[period_col].values else None

    revenue_current = pl_row["Total Revenue ($)"]
    opex_current = pl_row["Total Opex ($)"]
    op_profit_current = pl_row["Operating Profit ($)"]
    margin_current = pl_row["Operating Margin (%)"]
    if pl_prior_row is not None:
        revenue_prior = pl_prior_row["Total Revenue ($)"]
        opex_prior = pl_prior_row["Total Opex ($)"]
        op_profit_prior = pl_prior_row["Operating Profit ($)"]
        margin_prior = pl_prior_row["Operating Margin (%)"]
        rev_var_pct = (revenue_current - revenue_prior) / revenue_prior
        opex_var_pct = (opex_current - opex_prior) / opex_prior
    else:
        revenue_prior = opex_prior = op_profit_prior = margin_prior = np.nan
        rev_var_pct = opex_var_pct = np.nan

    region_lines = []
    for _, r in rev_region_df[rev_region_df[period_col] == current_period].iterrows():
        prior_val = rev_region_df[(rev_region_df[period_col] == prior_period) & (rev_region_df["Region"] == r["Region"])]
        prior_val = prior_val["Revenue ($)"].iloc[0] if not prior_val.empty else np.nan
        var_pct = (r["Revenue ($)"] - prior_val) / prior_val if pd.notna(prior_val) and prior_val != 0 else np.nan
        region_lines.append(f"  - {r['Region']}: {fmt_money(r['Revenue ($)'])} vs {fmt_money(prior_val)} ({fmt_pct(var_pct)})")

    product_lines = []
    for _, r in rev_product_df[rev_product_df[period_col] == current_period].iterrows():
        prior_val = rev_product_df[(rev_product_df[period_col] == prior_period) & (rev_product_df["Product Line"] == r["Product Line"])]
        prior_val = prior_val["Revenue ($)"].iloc[0] if not prior_val.empty else np.nan
        var_pct = (r["Revenue ($)"] - prior_val) / prior_val if pd.notna(prior_val) and prior_val != 0 else np.nan
        product_lines.append(f"  - {r['Product Line']}: {fmt_money(r['Revenue ($)'])} vs {fmt_money(prior_val)} ({fmt_pct(var_pct)})")

    region_cm_lines = []
    for _, r in region_cm_df[region_cm_df[period_col] == current_period].iterrows():
        region_cm_lines.append(
            f"  - {r['Region']}: Revenue {fmt_money(r['Region Revenue ($)'])}, Allocated S&M+CS Opex {fmt_money(r['Allocated S&M + CS Opex ($)'])}, "
            f"Net of GTM Cost {fmt_money(r['Region Net of GTM Cost ($)'])}"
        )
    product_cm_lines = []
    for _, r in product_cm_df[product_cm_df[period_col] == current_period].iterrows():
        product_cm_lines.append(
            f"  - {r['Product Line']}: Revenue {fmt_money(r['Product Revenue ($)'])}, Allocated R&D Opex {fmt_money(r['Allocated R&D Opex ($)'])}, "
            f"Net of R&D Cost {fmt_money(r['Product Net of R&D Cost ($)'])}"
        )
    cm_caveat = ("  NOTE: these are investment-proportionality figures ($only) — Net of GTM Cost (region) and Net of "
                 "R&D Cost (product) — not a margin or profitability measure, and not comparable to each other "
                 "(different cost bases). No cross-segment % is provided anywhere in this data by design (Professional "
                 "Services carries zero allocated R&D, so its Net of R&D Cost equals its own revenue). Use the $ "
                 "figures only to discuss relative segment size or which segment carries the largest/smallest "
                 "allocated cost — never infer or state a %.")

    dept_lines = []
    for _, r in exp_dept_df[exp_dept_df[period_col] == current_period].iterrows():
        prior_val = r.get("Prior Period ($)", np.nan)
        var_pct = r.get("QoQ/YoY Variance (%)", np.nan)
        dept_lines.append(f"  - {r['Department']}: {fmt_money(r['Amount ($)'])} vs {fmt_money(prior_val)} ({fmt_pct(var_pct)})")

    sb_lines = []
    for _, r in sb_df[sb_df[period_col] == current_period].iterrows():
        sb_lines.append(
            f"  - {r['Department']}: headcount change {r['Headcount Change']:+.1f}, cost-per-head change {fmt_money(r['Cost-per-Head Change ($)'])}, "
            f"Volume effect {fmt_money(r['Volume Effect ($)'])}, Rate effect {fmt_money(r['Rate Effect ($)'])}, total variance {fmt_money(r['Actual Variance ($)'])}"
        )

    breadth_lines = []
    for _, r in breadth_df[breadth_df[period_col] == current_period].iterrows():
        breadth_lines.append(f"  - {r['Line Item']}: total variance {fmt_money(r['Total Variance ($)'])} — {r['Breadth/Concentration Flag']}")

    hc_lines = []
    for _, r in hc_dept_df[hc_dept_df[period_col] == current_period].iterrows():
        hc_lines.append(f"  - {r['Department']}: {r['Ending Headcount']:.0f} vs {r['Prior Ending Headcount']}")
    rev_per_hc_row = company_rev_df[company_rev_df[period_col] == current_period]
    rev_per_hc_row = rev_per_hc_row.iloc[0] if not rev_per_hc_row.empty else None
    rev_per_hc_line = ""
    if rev_per_hc_row is not None:
        rev_per_hc_line = (f"  Company-wide Revenue per Headcount: {fmt_money(rev_per_hc_row['Revenue per Headcount ($, company-wide)'])} "
                            f"vs {fmt_money(rev_per_hc_row['Prior Revenue per Headcount ($, company-wide)'])}")

    bva_current = bva_df[bva_df[period_col] == current_period]
    flagged = bva_current[bva_current["Flag"].isin(["Watch", "Major Miss"])]
    bva_lines = []
    for _, r in flagged.iterrows():
        recurring = f", recurring for {r['Consecutive Watch Periods (ending here)']} consecutive periods" if r["Flag"] == "Watch" and r["Consecutive Watch Periods (ending here)"] >= 2 else ""
        bva_lines.append(f"  - {r['Line Item']}: Budget {fmt_money(r['Budget ($)'])}, Actual {fmt_money(r['Actual ($)'])}, Variance {fmt_pct(r['Variance (%)'])} — {r['Flag']}{recurring}")
    if not bva_lines:
        bva_lines = ["  (none flagged Watch or Major Miss this period)"]

    prompt = f"""Period: {current_period}
Comparison basis: vs. {comparison_label}

DATA:

Consolidated P&L:
- Revenue: {fmt_money(revenue_current)} vs {fmt_money(revenue_prior)} ({fmt_pct(rev_var_pct)})
- Total Opex: {fmt_money(opex_current)} vs {fmt_money(opex_prior)} ({fmt_pct(opex_var_pct)})
- Operating Profit: {fmt_money(op_profit_current)} vs {fmt_money(op_profit_prior)}
- Operating Margin: {margin_current:.1%} vs {(f"{margin_prior:.1%}" if pd.notna(margin_prior) else "N/A")}

Revenue by Region ({current_period}):
{chr(10).join(region_lines)}

Revenue by Product Line ({current_period}):
{chr(10).join(product_lines)}

Regional Go-to-Market Investment / Product Line R&D Investment ({current_period}) — $ only, no cross-segment % (see note below):
Region cut (net of Sales & Marketing + Customer Success only):
{chr(10).join(region_cm_lines)}
Product Line cut (net of R&D only):
{chr(10).join(product_cm_lines)}
{cm_caveat}

Expenses by Department:
{chr(10).join(dept_lines)}

Salaries & Benefits — Volume/Rate Decomposition (pre-calculated, per department):
{chr(10).join(sb_lines)}
(Volume effect = change in headcount x prior period cost-per-head. Rate effect = new headcount x change in cost-per-head. Calculated upstream — narrate, do not recompute.)

Revenue and Other Expense Categories — Breadth/Concentration (pre-calculated):
{chr(10).join(breadth_lines)}
(Not a volume/rate split — measures whether a variance is systemic or localized. Threshold: a single segment carrying >=60% of gross variance is "Concentrated"; otherwise "Broad-based".)

Headcount:
{chr(10).join(hc_lines)}
{rev_per_hc_line}

Budget vs Actual — flagged items only (Watch or Major Miss):
{chr(10).join(bva_lines)}
(Flag thresholds: |Variance %| > 8% = Major Miss, > 4% = Watch, else On Track.)

TASK:
Write commentary under these section headers, in this order:

1. Headline (1-2 sentences: the single most important story this period, tying revenue, margin, and the biggest flagged variance together)
2. Revenue Drivers (which region/product line drove the change, using the breadth/concentration figures — broad-based vs. localized, not volume vs rate)
3. Margin and Cost Structure (what happened to operating margin and why, referencing department-level spend and the Salaries & Benefits volume/rate decomposition where applicable)
4. Investment Alignment (brief, $ only: which region/product line carries the largest and smallest allocated cost this period, and any notable shift in Net-of-cost $ vs. prior period for a segment. No % language anywhere in this section — do not state, imply, or compute a percentage for any segment.)
5. Budget Variance Flags (walk through each Major Miss by name, plus any Watch item that's now recurring for 2+ consecutive periods if that data is available)
6. Headcount and Efficiency (revenue-per-headcount trend, whether headcount growth is tracking ahead of or behind revenue growth)"""
    return prompt


def call_claude_narrative(user_prompt, model="claude-sonnet-4-6", max_tokens=1500):
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None, "No ANTHROPIC_API_KEY found in environment — prompt built and printed below, but not sent."
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=0.2,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = "".join(block.text for block in resp.content if block.type == "text")
        return text, None
    except Exception as e:
        return None, f"API call failed: {e}"


# ---------------------------------------------------------------------------
# 15. RUN — generate narrative for Q4 FY2026 vs Q3 FY2026 (most recent
# complete quarter). NOT run at annual grain: annual BvA variance never
# exceeds 4% for any line item in any of the 3 fiscal years (Budget's
# month-level noise cancels out over 12 months), so an annual demo period
# would leave the Budget Variance Flags section with nothing to narrate.
# Quarterly grain is where flagged items actually exist to demonstrate.
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# 15. RUN — generate narrative for Q4 FY2026 vs Q3 FY2026 (most recent
# complete quarter). NOT run at annual grain: annual BvA variance never
# exceeds 4% for any line item in any of the 3 fiscal years (Budget's
# month-level noise cancels out over 12 months), so an annual demo period
# would leave the Budget Variance Flags section with nothing to narrate.
# Quarterly grain is where flagged items actually exist to demonstrate.
#
# Guarded behind __name__ == "__main__" so that app.py (Streamlit) can
# `import rollups` to reuse every dataframe and function built above —
# without firing a live API call or rewriting the workbook every time the
# app process starts or a page reruns.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    DEMO_PERIOD_COL = "Fiscal Quarter"
    DEMO_CURRENT = "Q4 FY2026"
    DEMO_PRIOR = "Q3 FY2026"

    demo_prompt = build_user_prompt(
        DEMO_PERIOD_COL, quarter_order, DEMO_CURRENT, DEMO_PRIOR, DEMO_PRIOR,
        pl_q, rev_by_region_q, rev_by_product_q, region_cm_q, product_cm_q,
        exp_by_dept_q, sb_volrate_q, breadth_all_q, hc_dept_q, company_rev_per_hc_q, bva_q,
    )

    print("\n" + "=" * 70)
    print(f"STEP 4 — RENDERED USER PROMPT ({DEMO_CURRENT} vs {DEMO_PRIOR})")
    print("=" * 70)
    print(demo_prompt)

    narrative, error = call_claude_narrative(demo_prompt)
    print("\n" + "=" * 70)
    print("STEP 4 — GENERATED NARRATIVE" if narrative else "STEP 4 — API CALL STATUS")
    print("=" * 70)
    if narrative:
        print(narrative)
        with open("generated_narrative_Q4FY2026_vs_Q3FY2026.txt", "w") as f:
            f.write(narrative)
        print("\nSaved generated_narrative_Q4FY2026_vs_Q3FY2026.txt")
    else:
        print(error)

    # -----------------------------------------------------------------------
    # 16. Re-export sheets that changed after the original workbook write:
    #     BvA_Q/BvA_Y now have Flag + streak columns, and headcount efficiency
    #     is a new table. Written with mode="a" + replace so the earlier BvA
    #     sheets (without flags) don't linger stale in the workbook.
    # -----------------------------------------------------------------------
    with pd.ExcelWriter("rollups_output.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        bva_q.to_excel(writer, sheet_name="BvA_Q", index=False)
        bva_y.to_excel(writer, sheet_name="BvA_Y", index=False)
        hc_dept_q.to_excel(writer, sheet_name="Headcount_Dept_Q", index=False)
        hc_dept_y.to_excel(writer, sheet_name="Headcount_Dept_Y", index=False)
        company_rev_per_hc_q.to_excel(writer, sheet_name="CompanyRevPerHC_Q", index=False)
        company_rev_per_hc_y.to_excel(writer, sheet_name="CompanyRevPerHC_Y", index=False)
        opex_per_employee_q.to_excel(writer, sheet_name="OpexPerEmployee_Q", index=False)
        opex_per_employee_y.to_excel(writer, sheet_name="OpexPerEmployee_Y", index=False)

    print("\nRe-saved BvA_Q/BvA_Y with flags, added Headcount_Dept_Q/Y, CompanyRevPerHC_Q/Y, and OpexPerEmployee_Q/Y sheets.")

print("\nQuarterly BvA flagged items (Watch or Major Miss), all periods:")
flagged_all = bva_q[bva_q["Flag"].isin(["Watch", "Major Miss"])]
print(flagged_all[["Fiscal Quarter", "Line Item", "Variance (%)", "Flag", "Consecutive Watch Periods (ending here)"]].to_string(index=False))
print("\nAnnual BvA flags, all periods:")
print(bva_y[["Fiscal Year", "Line Item", "Variance (%)", "Flag"]].to_string(index=False))

