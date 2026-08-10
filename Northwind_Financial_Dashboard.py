"""
Northwind AI in Finance Challenge — Streamlit Dashboard (Step 5, optional wrapper)

Reuses every dataframe and function from rollups.py (imported as a module —
see the `if __name__ == "__main__":` guard in that file, added specifically
so importing here does not fire a live API call or rewrite the workbook).

Run with: streamlit run "Northwind_Financial_Dashboard.py"
Requires ANTHROPIC_API_KEY in the environment to actually generate narrative
text via the API; without it, the app shows a "Download prompt for this
period" button instead — download the .txt file and paste it into a Claude
chat to get the narrative manually.
"""

import os
import numpy as np
import pandas as pd
import streamlit as st

import rollups as R  # noqa: the import itself runs sections 1-14 (all data building)
import close_history
import close_validation as CV  # production Phase 2/3 service — Cycle 3 Task 2


GOOD = "#1e8e3e"   # green — favorable variance
BAD = "#d93025"    # red — unfavorable variance
NEUTRAL = "#5f6368"  # gray — zero / N/A

CARD_BG = "#FDEDEA"       # pale salmon tint (background)
CARD_BORDER = "#FA8072"   # true "salmon" (left border) — deliberately a
                          # different, more saturated shade than the fill


def fmt_num_half(x):
    """Plain-number formatting rounded to the nearest 0.5 (e.g. 1.333333 -> 1.5),
    for count-like columns that are neither currency nor percent."""
    if pd.isna(x):
        return ""
    rounded = round(x * 2) / 2
    return f"{rounded:.1f}"


def fmt_pct_half(x):
    """Percent formatting rounded to the nearest 0.5 point (e.g. 6.3% -> 6.5%,
    6.2% -> 6.0%) instead of an arbitrary decimal or a whole number that hides
    which side of the half-point a value actually falls on. x is a fraction
    (0.063), not already multiplied by 100."""
    if pd.isna(x):
        return ""
    rounded = round(x * 100 * 2) / 2
    return f"{rounded:.1f}%"


def _base_format_map(df):
    """Column -> Styler format string, based on naming convention (same
    convention previously used by fmt_display_df, now applied via Styler
    instead of pre-stringifying so colors can still be applied numerically)."""
    fmt_map = {}
    for col in df.columns:
        if df[col].dtype.kind not in "fi":
            continue
        lower = col.lower()
        if col.endswith("(%)") or "share" in lower:
            fmt_map[col] = fmt_pct_half
        elif "($" in col:
            fmt_map[col] = "${:,.0f}"
        elif "headcount" in lower and "change" not in lower:
            fmt_map[col] = "{:.0f}"
        elif "headcount" in lower and "change" in lower:
            fmt_map[col] = fmt_num_half
    return fmt_map


def fmt_display_df(df):
    """Plain formatting, no color — used where a column's direction can't be
    classified as favorable/unfavorable (e.g. snapshot-only CM tables)."""
    return df.style.format(_base_format_map(df), na_rep="")


def _color_good_up(v):
    if pd.isna(v) or v == 0:
        return f"color: {NEUTRAL}"
    return f"color: {GOOD}; font-weight: 600" if v > 0 else f"color: {BAD}; font-weight: 600"


def _color_bad_up(v):
    if pd.isna(v) or v == 0:
        return f"color: {NEUTRAL}"
    return f"color: {BAD}; font-weight: 600" if v > 0 else f"color: {GOOD}; font-weight: 600"


def style_variance_df(df, higher_is_good_cols=None, higher_is_bad_cols=None):
    """Format + color-code a dataframe for display. higher_is_good_cols: columns
    where a positive value is favorable (e.g. revenue variance). higher_is_bad_cols:
    columns where a positive value is unfavorable (e.g. cost/opex variance)."""
    styler = df.style.format(_base_format_map(df), na_rep="")
    for col in higher_is_good_cols or []:
        if col in df.columns:
            styler = styler.map(_color_good_up, subset=[col])
    for col in higher_is_bad_cols or []:
        if col in df.columns:
            styler = styler.map(_color_bad_up, subset=[col])
    return styler


def style_breadth_df(df):
    """Breadth/concentration table mixes revenue rows (higher=good) and expense
    rows (higher=bad) in the same 'Total Variance ($)' column, so direction is
    decided per row from the Line Item label rather than a fixed column rule."""
    fmt_map = {
        "Total Variance ($)": "${:,.0f}",
        "Gross Variance ($)": "${:,.0f}",
        "Top Contributor Share": fmt_pct_half,
    }
    styler = df.style.format(fmt_map, na_rep="")

    def row_color(row):
        v = row["Total Variance ($)"]
        is_revenue = str(row["Line Item"]).startswith("Revenue")
        if pd.isna(v) or v == 0:
            color = NEUTRAL
        elif is_revenue:
            color = GOOD if v > 0 else BAD
        else:
            color = BAD if v > 0 else GOOD
        style = f"color: {color}; font-weight: 600"
        return [style if c == "Total Variance ($)" else "" for c in row.index]

    return styler.apply(row_color, axis=1)


def kpi_card(label, value_str, comparison_str, delta_str, delta_color):
    """Salmon KPI card matching the reference screenshot layout: pale salmon
    fill, a more saturated salmon left border, uppercase label, large value,
    and a 'vs prior' line with a directionally colored delta."""
    st.markdown(
        f"""
        <div style="
            background:{CARD_BG};
            border-left:5px solid {CARD_BORDER};
            border-radius:10px;
            padding:16px 20px;
            margin-bottom:8px;
        ">
            <div style="font-size:12px;font-weight:600;letter-spacing:0.05em;
                        color:#8a5a4d;text-transform:uppercase;">{label}</div>
            <div style="font-size:28px;font-weight:700;color:#1a1a1a;margin-top:4px;">
                {value_str}
            </div>
            <div style="font-size:13px;color:#666;margin-top:4px;">
                vs {comparison_str}
                {f'&nbsp;<span style="color:{delta_color};font-weight:600;">{delta_str}</span>' if delta_str else ""}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="Northwind FP&A Dashboard", layout="wide")

st.title("Northwind Financial Co. — FP&A Dashboard")
st.caption(
    "Synthetic demo data for the AI in Finance Challenge. Same pipeline as rollups.py: "
    "quarter/year rollups → segment investment views (revenue/investment cuts, $ only) → decomposition → AI narrative."
)

# -----------------------------------------------------------------------
# Sidebar: cadence + period selection
# -----------------------------------------------------------------------
st.sidebar.header("Period Selection")
cadence = st.sidebar.radio("Cadence", ["Quarterly", "Annual"], index=0)

if cadence == "Quarterly":
    period_col = "Fiscal Quarter"
    period_order = R.quarter_order
    pl_df, rev_region_df, rev_product_df = R.pl_q, R.rev_by_region_q, R.rev_by_product_q
    region_cm_df, product_cm_df = R.region_cm_q, R.product_cm_q
    region_pct_df, product_pct_df = R.region_gtm_pct_q, R.product_rd_pct_q
    exp_dept_df, sb_df, breadth_df = R.exp_by_dept_q, R.sb_volrate_q, R.breadth_all_q
    hc_dept_df, company_rev_df, bva_df = R.hc_dept_q, R.company_rev_per_hc_q, R.bva_q
    opex_per_emp_df = R.opex_per_employee_q
    # Cost Structure Investigation View Brief (2026-08-09): Department x
    # Cost Type (Category) grain, current/prior/variance now carried on
    # exp_by_dept_cat_q/_y (see rollups.py Section 4 for the extension).
    exp_dept_cat_df = R.exp_by_dept_cat_q
    # Cost Structure Views Brief v2 (2026-08-09, final): Cost Category-only,
    # company-wide grain (no Department dimension) — see rollups.py.
    exp_cat_df = R.exp_by_cat_q
else:
    period_col = "Fiscal Year"
    period_order = R.year_order
    pl_df, rev_region_df, rev_product_df = R.pl_y, R.rev_by_region_y, R.rev_by_product_y
    region_cm_df, product_cm_df = R.region_cm_y, R.product_cm_y
    region_pct_df, product_pct_df = R.region_gtm_pct_y, R.product_rd_pct_y
    exp_dept_df, sb_df, breadth_df = R.exp_by_dept_y, R.sb_volrate_y, R.breadth_all_y
    hc_dept_df, company_rev_df, bva_df = R.hc_dept_y, R.company_rev_per_hc_y, R.bva_y
    opex_per_emp_df = R.opex_per_employee_y
    exp_dept_cat_df = R.exp_by_dept_cat_y
    exp_cat_df = R.exp_by_cat_y

# periods with a prior period available (skip the very first, nothing to compare)
selectable_periods = [p for p in period_order if period_order.index(p) > 0]
current_period = st.sidebar.selectbox("Current period", selectable_periods, index=len(selectable_periods) - 1)
prior_period = period_order[period_order.index(current_period) - 1]
st.sidebar.markdown(f"**Comparison basis:** vs. {prior_period}")

if cadence == "Annual":
    ann_flags = R.bva_y[(R.bva_y[period_col] == current_period) & (R.bva_y["Flag"] != "On Track")]
    if ann_flags.empty:
        st.sidebar.info(
            "Note: annual Budget vs Actual variance never exceeds 4% for any line item, "
            "in any fiscal year in this dataset — Budget's month-level noise cancels out "
            "over 12 months. Switch to Quarterly to see flagged items."
        )

# -----------------------------------------------------------------------
# Top-line P&L
# -----------------------------------------------------------------------
pl_row = pl_df[pl_df[period_col] == current_period].iloc[0]
pl_prior_row = pl_df[pl_df[period_col] == prior_period].iloc[0] if prior_period in pl_df[period_col].values else None

def _kpi_delta(current, prior, higher_is_good, as_points=False):
    """Return (comparison_str, delta_str, delta_color) for a kpi_card."""
    if prior is None:
        return "N/A", "", NEUTRAL
    if as_points:
        delta = (current - prior) * 100
        comp_str = fmt_pct_half(prior)
        delta_rounded = round(delta * 2) / 2
        delta_str = f"{delta_rounded:+.1f} pts"
    else:
        delta = (current - prior) / prior if prior else float("nan")
        comp_str = f"${prior:,.0f}"
        delta_rounded = round(delta * 100 * 2) / 2
        delta_str = f"{delta_rounded:+.1f}%"
    if pd.isna(delta) or delta == 0:
        color = NEUTRAL
    else:
        favorable = (delta > 0) if higher_is_good else (delta < 0)
        color = GOOD if favorable else BAD
    return comp_str, delta_str, color

c1, c2, c3, c4 = st.columns(4)
prior_rev = pl_prior_row["Total Revenue ($)"] if pl_prior_row is not None else None
prior_opex = pl_prior_row["Total Opex ($)"] if pl_prior_row is not None else None
prior_profit = pl_prior_row["Operating Profit ($)"] if pl_prior_row is not None else None
prior_margin = pl_prior_row["Operating Margin (%)"] if pl_prior_row is not None else None

with c1:
    comp, delta, color = _kpi_delta(pl_row["Total Revenue ($)"], prior_rev, higher_is_good=True)
    kpi_card("Revenue", f"${pl_row['Total Revenue ($)']:,.0f}", comp, delta, color)
with c2:
    comp, delta, color = _kpi_delta(pl_row["Total Opex ($)"], prior_opex, higher_is_good=False)
    kpi_card("Total Opex", f"${pl_row['Total Opex ($)']:,.0f}", comp, delta, color)
with c3:
    comp, delta, color = _kpi_delta(pl_row["Operating Profit ($)"], prior_profit, higher_is_good=True)
    kpi_card("Operating Profit", f"${pl_row['Operating Profit ($)']:,.0f}", comp, delta, color)
with c4:
    comp, delta, color = _kpi_delta(pl_row["Operating Margin (%)"], prior_margin, higher_is_good=True, as_points=True)
    kpi_card("Operating Margin", fmt_pct_half(pl_row['Operating Margin (%)']), comp, delta, color)

st.divider()

# -----------------------------------------------------------------------
# Tabs: Revenue Performance / Cost Structure / Headcount & Efficiency / Budget
# vs Actual / AI Narrative are the flagship analytical pages (renamed to the
# v1.0 IA names per Architect resolution on the flagship-naming open question
# — this was completing Task 1 item 6's placement instruction, not new scope).
# The Executive Summary KPI strip is the st.columns() block of KPI cards
# rendered ABOVE the tab bar (see kpi_card calls before this block) — it is
# not itself a tab, so "positioned after the flagship pages" means after this
# tab bar's flagship tabs, not literally after a tab named "Executive
# Summary." Regional Revenue & Go-to-Market Investment and Product Line
# Revenue & R&D Investment are SUPPORTING analysis pages per Cycle 2's v1.0
# Information Architecture — placed after the flagship pages, not among the
# first tabs a user sees.
# -----------------------------------------------------------------------
tab_rev, tab_exp, tab_hc, tab_bva, tab_close, tab_region_invest, tab_product_invest, tab_narr = st.tabs(
    ["Revenue Performance", "Cost Structure", "Headcount & Efficiency", "Budget vs Actual", "Close Validation Status",
     "Regional Revenue & Go-to-Market Investment", "Product Line Revenue & R&D Investment", "AI Narrative"]
)

with tab_rev:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Revenue by Region — full trend")
        chart_df = R.revenue.groupby(["Region", period_col if cadence == "Quarterly" else "Fiscal Year"], as_index=False)["Revenue ($)"].sum()
        pivot = chart_df.pivot(index=period_col if cadence == "Quarterly" else "Fiscal Year", columns="Region", values="Revenue ($)")
        pivot = pivot.reindex(period_order)
        st.line_chart(pivot)
    with col2:
        st.subheader("Revenue by Product Line — full trend")
        chart_df2 = R.revenue.groupby(["Product Line", period_col if cadence == "Quarterly" else "Fiscal Year"], as_index=False)["Revenue ($)"].sum()
        pivot2 = chart_df2.pivot(index=period_col if cadence == "Quarterly" else "Fiscal Year", columns="Product Line", values="Revenue ($)")
        pivot2 = pivot2.reindex(period_order)
        st.line_chart(pivot2)

    st.subheader(f"Revenue Mix (%) — {current_period}")
    st.caption(
        "Share of total revenue this period — a direct ratio of actual revenue, not a proportionally "
        "allocated cost, so (unlike the Region/Product Investment pages' cost ratios) this % genuinely "
        "varies by segment and is a valid cross-segment comparison."
    )
    mixcol1, mixcol2 = st.columns(2)
    with mixcol1:
        st.bar_chart(rev_region_df[rev_region_df[period_col] == current_period].set_index("Region")["Revenue Mix (%)"])
    with mixcol2:
        st.bar_chart(rev_product_df[rev_product_df[period_col] == current_period].set_index("Product Line")["Revenue Mix (%)"])

    st.subheader(f"Revenue detail — {current_period} vs {prior_period}")
    rev_var_cols = ["QoQ/YoY Variance ($)", "QoQ/YoY Variance (%)", "YoY Variance ($)", "YoY Variance (%)"]
    st.dataframe(style_variance_df(rev_region_df[rev_region_df[period_col] == current_period],
                                    higher_is_good_cols=rev_var_cols), use_container_width=True)
    st.dataframe(style_variance_df(rev_product_df[rev_product_df[period_col] == current_period],
                                    higher_is_good_cols=rev_var_cols), use_container_width=True)

with tab_exp:
    st.subheader("Expenses by Department — full trend")
    exp_chart = R.expenses.groupby(["Department", period_col], as_index=False)["Amount ($)"].sum()
    pivot3 = exp_chart.pivot(index=period_col, columns="Department", values="Amount ($)").reindex(period_order)
    st.bar_chart(pivot3)

    # -------------------------------------------------------------------
    # Cost Structure Investigation View — Builder Brief, 2026-08-09.
    # Department x Cost Type (Category), Current vs Prior, Variance $,
    # Variance %. Added so a flagged cost variance (e.g. a Close
    # Validation Status Phase 2/3 flag) can be investigated using
    # information the Controller can actually see on this page, at the
    # same Department/Category grain close_validation.py reads from.
    # ADDITIVE ONLY — existing sections below (S&B bridge, breadth/
    # concentration, Opex/Employee) are unchanged and unmoved.
    # -------------------------------------------------------------------
    st.subheader(f"Department × Cost Type — Investigation View ({current_period} vs {prior_period})")
    st.caption(
        "Department and Cost Type (Category) breakdown, current vs prior period — same "
        "Department/Category grain, current/prior period definitions, and Amount ($) values "
        "close_validation.py's Phase 2/3 checks read from, so a flagged item on the Close "
        "Validation Status page can be traced here without needing internal validation-engine "
        "output."
    )
    dept_cat_current = exp_dept_cat_df[exp_dept_cat_df[period_col] == current_period][
        ["Department", "Category", "Amount ($)", "Prior Period ($)", "QoQ/YoY Variance ($)", "QoQ/YoY Variance (%)"]
    ].rename(columns={"Amount ($)": "Current Period ($)"})
    dept_cat_current = dept_cat_current.sort_values(["Department", "Category"]).reset_index(drop=True)
    dept_cat_var_cols = ["QoQ/YoY Variance ($)", "QoQ/YoY Variance (%)"]
    st.dataframe(
        style_variance_df(dept_cat_current, higher_is_bad_cols=dept_cat_var_cols),
        use_container_width=True,
    )

    # -------------------------------------------------------------------
    # Cost Category-only (company-wide) view — Builder Brief v2, 2026-08-09.
    # No Department dimension. Positioned alongside the Department x Cost
    # Category view per the Brief, so a Controller can see whether a cost
    # category is moving broadly across the business or is concentrated
    # within a single department (that latter question is answered by the
    # view above; this view answers "is it broad or department-specific").
    # ADDITIVE ONLY — does not touch the Department x Cost Category view
    # above or any section below.
    # -------------------------------------------------------------------
    st.subheader(f"Cost Category — Company-Wide View ({current_period} vs {prior_period})")
    st.caption(
        "Cost Category totals, company-wide (summed across all departments), current vs prior "
        "period. Reconciles exactly to the Department × Cost Category view above, summed across "
        "departments, and its grand total reconciles to the Department-level Expense total on "
        "this page. Dashboard-only presentation — not used by Phase 2/3 validation or plausibility "
        "logic, which continue to operate at the Department × Category grain only."
    )
    cat_current = exp_cat_df[exp_cat_df[period_col] == current_period][
        ["Category", "Amount ($)", "Prior Period ($)", "QoQ/YoY Variance ($)", "QoQ/YoY Variance (%)"]
    ].rename(columns={"Amount ($)": "Current Period ($)"})
    cat_current = cat_current.sort_values(["Category"]).reset_index(drop=True)
    cat_var_cols = ["QoQ/YoY Variance ($)", "QoQ/YoY Variance (%)"]
    st.dataframe(
        style_variance_df(cat_current, higher_is_bad_cols=cat_var_cols),
        use_container_width=True,
    )

    st.subheader(f"Salaries & Benefits Volume/Rate Bridge — {current_period}")
    sb_cost_cols = ["Headcount Change", "Cost-per-Head Change ($)", "Volume Effect ($)",
                    "Rate Effect ($)", "Bridge Total ($)", "Actual Variance ($)"]
    st.dataframe(style_variance_df(sb_df[sb_df[period_col] == current_period],
                                    higher_is_bad_cols=sb_cost_cols), use_container_width=True)
    st.caption("Volume effect = change in headcount x prior period cost-per-head. Rate effect = new headcount x change in cost-per-head. Volume + Rate = Actual Variance exactly.")

    st.subheader(f"Breadth / Concentration — {current_period}")
    st.dataframe(style_breadth_df(breadth_df[breadth_df[period_col] == current_period]), use_container_width=True)
    st.caption("Threshold: a single segment carrying >=60% of gross variance is flagged Concentrated; otherwise Broad-based.")

    st.subheader(f"Opex per Employee by Department — {current_period}")
    st.caption(
        "A cost-discipline metric — is this department's spend per head rising or falling — not a "
        "workforce-efficiency metric, which is why it lives here rather than on the Headcount & "
        "Efficiency page. Unlike company-wide Revenue per Headcount, this ratio IS department-level "
        "in a defensible sense: both the opex and the headcount genuinely belong to the department."
    )
    st.bar_chart(opex_per_emp_df[opex_per_emp_df[period_col] == current_period].set_index("Department")["Opex per Employee ($)"])
    st.dataframe(fmt_display_df(opex_per_emp_df[opex_per_emp_df[period_col] == current_period][
        ["Department", "Amount ($)", "Ending Headcount", "Opex per Employee ($)"]
    ]), use_container_width=True)

with tab_hc:
    st.subheader("Headcount by Department — full trend (ending headcount)")
    hc_all = R.hc_by_dept_q if cadence == "Quarterly" else R.hc_by_dept_y
    pivot4 = hc_all.pivot(index=period_col, columns="Department", values="Ending Headcount").reindex(period_order)
    st.line_chart(pivot4)

    st.subheader(f"Headcount by Department — {current_period} vs {prior_period}")
    st.dataframe(fmt_display_df(hc_dept_df[hc_dept_df[period_col] == current_period]), use_container_width=True)

    st.divider()
    st.subheader("Company-wide Revenue per Headcount")
    st.caption(
        "COMPANY-WIDE only — Total Revenue / Total Ending Headcount. No department-level "
        "Revenue-per-Employee metric is computed or shown anywhere in this project: revenue has "
        "no real per-department attribution basis, the same reasoning that led to removing "
        "cross-segment % from the Region/Product Investment pages. If you're looking for a "
        "department-level cost-per-head figure, see Opex per Employee on the Cost Structure page."
    )
    company_rev_row = company_rev_df[company_rev_df[period_col] == current_period]
    if not company_rev_row.empty:
        row = company_rev_row.iloc[0]
        c1, c2 = st.columns(2)
        with c1:
            st.metric(
                "Revenue per Headcount (company-wide)",
                f"${row['Revenue per Headcount ($, company-wide)']:,.0f}",
                delta=(
                    f"{(row['Revenue per Headcount ($, company-wide)'] - row['Prior Revenue per Headcount ($, company-wide)']) / row['Prior Revenue per Headcount ($, company-wide)']:+.1%}"
                    if pd.notna(row['Prior Revenue per Headcount ($, company-wide)']) else None
                ),
            )
        with c2:
            st.metric("Company Ending Headcount", f"{row['Company Ending Headcount']:.0f}")
    trend = company_rev_df.set_index(period_col)["Revenue per Headcount ($, company-wide)"].reindex(period_order)
    st.line_chart(trend)

with tab_bva:
    st.subheader(f"Budget vs Actual — {current_period}")
    bva_current = bva_df[bva_df[period_col] == current_period]

    def _bva_row_color(row):
        v = row["Variance (%)"]
        is_revenue = str(row["Line Item"]).strip().lower() == "revenue"
        if pd.isna(v) or v == 0:
            color = NEUTRAL
        elif is_revenue:
            color = GOOD if v > 0 else BAD
        else:
            color = BAD if v > 0 else GOOD
        style = f"color: {color}; font-weight: 600"
        return [style if c in ("Variance ($)", "Variance (%)") else "" for c in row.index]

    bva_styler = bva_current.style.format(_base_format_map(bva_current), na_rep="").apply(_bva_row_color, axis=1)
    st.dataframe(bva_styler, use_container_width=True)

    flagged = bva_current[bva_current["Flag"].isin(["Watch", "Major Miss"])]
    if flagged.empty:
        st.success("No Watch or Major Miss items this period.")
    else:
        for _, r in flagged.iterrows():
            is_revenue = str(r["Line Item"]).strip().lower() == "revenue"
            favorable = (r["Variance (%)"] > 0) if is_revenue else (r["Variance (%)"] < 0)
            dot = "🟢" if favorable else "🔴"
            tag = "Favorable" if favorable else "Unfavorable"
            recurring = f" — recurring {r['Consecutive Watch Periods (ending here)']} consecutive periods" if r["Flag"] == "Watch" and r["Consecutive Watch Periods (ending here)"] >= 2 else ""
            st.warning(
                f"**{r['Line Item']}** ({r['Flag']}): Budget ${r['Budget ($)']:,.0f}, Actual ${r['Actual ($)']:,.0f}, "
                f"Variance {'+' if r['Variance (%)'] >= 0 else ''}{fmt_pct_half(r['Variance (%)'])} {dot} **{tag}**{recurring}"
            )

with tab_close:
    st.title("Close Validation Status")

    # --- Resolve the latest APPROVED close from real Close History, and run
    # close_validation.py's production Phase 2/3 functions against it. This
    # is the module swap for Cycle 3 Task 2: no import of, and no data from,
    # close_v1_v2_simulation.py anywhere in this tab. Phase 2 compares the
    # currently-loaded close (R.expenses) against the latest approved close
    # in Close History (None if Close History is empty — the real Live
    # state today, per Handbook Section 7: "Live's own Close History starts
    # empty"). Phase 3 evaluates the currently-loaded close's own quarterly
    # history and needs no prior approved close to run.
    resolved_prior_close = close_history.resolve_latest_approved_close()
    prior_expenses_df = None
    if resolved_prior_close is not None:
        prior_expenses_df = pd.read_excel(resolved_prior_close["raw_dataset_path"], "Expenses")
        prior_expenses_df["Date"] = pd.to_datetime(prior_expenses_df["Date"])

    phase2_result = CV.run_phase2_deterministic_validation(
        current_data=R.expenses,
        prior_data=prior_expenses_df,
        key_cols=("Date", "Department", "Category"),
        value_col="Amount ($)",
    )
    phase3_result = CV.run_phase3_plausibility_review(
        expenses=R.expenses,
        headcount=R.headcount,
        period_col="Fiscal Quarter",
        period_order=R.quarter_order,
        # target_period defaults to the latest quarter in R.quarter_order —
        # no hardcoded period label here, unlike the pre-Task-2 demo tab.
    )

    if resolved_prior_close is not None:
        close_status_caption = (
            f"Autonomous CFO Office, Phases 0-3, run by close_validation.py against the currently-loaded close "
            f"vs. the latest APPROVED close in Close History ('{resolved_prior_close['period_label']}'). "
            "Phases 4-6 and 9 are parked pending synthetic controller commentary and are not shown as complete below."
        )
    else:
        close_status_caption = (
            "Autonomous CFO Office, Phases 0-3, run by close_validation.py against real Close History. "
            "Close History currently has no approved closes yet (bootstrap state) — Phase 2 reports "
            "'not applicable' rather than a diff, since there is nothing yet to compare the current close "
            "against; Phase 3 still runs, since it only needs the current close's own quarterly history. "
            "Phases 4-6 and 9 are parked pending synthetic controller commentary and are not shown as complete below."
        )
    st.caption(close_status_caption)

    st.subheader("Workflow state")
    phase2_ran = phase2_result.status == CV.STATUS_OK
    any_flags_found = (phase2_ran and len(phase2_result.flagged_rows) > 0) or (
        phase3_result.status == CV.STATUS_OK and len(phase3_result.flagged_rows) > 0
    )
    states = [
        ("Close Received", "Phase 0", True),
        ("Data Validated", "Phase 2 complete" if phase2_ran else "Phase 2 not applicable (no prior close)", True),
        ("Observations Generated", "Phase 3 complete", phase3_result.status == CV.STATUS_OK),
        ("Awaiting Controller Input", "unexplained items exist" if any_flags_found else "no items awaiting explanation", any_flags_found),
        ("Explanations Validated", "Phase 6 complete", False),
        ("Executive Ready", "human approval gate passed", False),
        ("Published", "Phase 8 outputs delivered", False),
        ("Archived", "Phase 9 log entry written", False),
    ]
    state_cols = st.columns(len(states))
    for col, (name, desc, done) in zip(state_cols, states):
        with col:
            icon = "✅" if done else "⬜"
            st.markdown(f"{icon}  **{name}**")
            st.caption(desc)
    if any_flags_found:
        st.info(
            "Current state: **Awaiting Controller Input** — real findings below are unexplained pending "
            "Gregory's synthetic commentary, which has not yet been delivered this cycle."
        )
    else:
        st.success(
            "Current state: **Data Validated / Observations Generated** — no flagged items this run "
            "(Phase 2 not applicable or found no differences; Phase 3 found no plausibility anomalies)."
        )

    st.divider()
    st.subheader("Phase 2 — Deterministic Validation (current close vs. latest approved close)")
    if phase2_result.status == CV.STATUS_NOT_APPLICABLE:
        st.info(
            "**Not applicable** — no prior approved close exists in Close History yet. Phase 2 diffs the "
            "current close against the latest APPROVED close; with no predecessor, there is nothing to diff "
            "against. This is the expected state for the first approved close, not an error."
        )
    else:
        st.caption(
            f"Compared {phase2_result.rows_compared} overlapping expense rows between the current close and the "
            "latest approved close in Close History. Any nonzero difference is, by construction, a change to an "
            "already-closed number."
        )
        phase2_display = phase2_result.flagged_rows[["Date", "Department", "Category", "Amount ($)_prior", "Amount ($)_current", "Diff ($)"]].rename(
            columns={"Amount ($)_prior": "Prior Close ($)", "Amount ($)_current": "Current Close ($)"}
        )
        st.dataframe(phase2_display.style.format({"Prior Close ($)": "${:,.2f}", "Current Close ($)": "${:,.2f}", "Diff ($)": "${:,.2f}"}),
                     use_container_width=True)
        if len(phase2_result.flagged_rows) == 0:
            st.success("No differences found against the latest approved close.")
        else:
            st.warning(f"{len(phase2_result.flagged_rows)} row(s) changed vs. the latest approved close — see table above.")

    st.divider()
    st.subheader(f"Phase 3 — Plausibility Review (current close, {phase3_result.target_period or 'latest period'} only)")
    st.caption(
        f"{phase3_result.target_period or 'The latest period'} has no prior-approved-close counterpart to diff against under "
        "Phase 2, so Phase 3 covers that gap — flagging a Department x Category cell if its QoQ change exceeds "
        f"{phase3_result.threshold:.0%} (set well above the historical max naturally-occurring per-cell move in "
        "this dataset, ~13.1% — see assumptions_and_limitations.md — not tuned to any specific case) with no "
        f"offsetting headcount change (within +/-{phase3_result.headcount_band} heads) for that department."
    )
    if phase3_result.status != CV.STATUS_OK:
        st.info("Not applicable — the target period has no preceding period in the current close's data to compare against.")
    else:
        phase3_display = phase3_result.all_cells.copy()
        phase3_display["Flag"] = np.where(phase3_display["Driver"] == CV.DRIVER_NOT_IDENTIFIABLE,
                                           "PLAUSIBILITY FLAG — no headcount driver identified for this cost swing", "OK")
        phase3_display = phase3_display[["Department", "Category", "Prior ($)", "Amount ($)", "QoQ (%)", "Headcount Change", "Flag"]]
        def _flag_color(row):
            is_flag = row["Flag"] != "OK"
            style = "background-color: #FDEDEA; font-weight: 600" if is_flag else ""
            return [style] * len(row)
        st.dataframe(
            phase3_display.style.format({"Prior ($)": "${:,.2f}", "Amount ($)": "${:,.2f}", "QoQ (%)": "{:+.1%}", "Headcount Change": "{:+.2f}"})
            .apply(_flag_color, axis=1),
            use_container_width=True,
        )
        if len(phase3_result.flagged_rows) == 0:
            st.success("No plausibility anomalies found this period.")
        elif len(phase3_result.flagged_rows) == 1:
            row = phase3_result.flagged_rows.iloc[0]
            st.warning(
                f"1 plausibility anomaly flagged: {row['Department']} / {row['Category']}, "
                f"{row['QoQ (%)']:+.1%} QoQ with headcount change {row['Headcount Change']:+.2f} "
                "(no headcount driver identified, no cause guessed, per system rule 6)."
            )
        else:
            st.warning(f"{len(phase3_result.flagged_rows)} plausibility anomalies flagged — see table above.")

    st.divider()
    st.subheader("Observation register (format only — Phase 4-6 not built this cycle)")
    st.caption(
        "Schema Phase 4-6 will consume once Gregory's synthetic commentary is delivered. This register is built "
        "here in the dashboard from close_validation.py's returned structured results — the production module "
        "itself never writes an observation register or any other artifact; that's caller-side, same as any "
        "CSV/report output."
    )
    obs_rows = []
    if phase2_result.status == CV.STATUS_OK:
        for _, r in phase2_result.flagged_rows.iterrows():
            obs_rows.append({
                "Detected By": "Phase 2 (Deterministic Validation)",
                "Period": r["Date"].strftime("%b %Y") if pd.notna(r["Date"]) else "",
                "Type": "Historical Revision",
                "Department": r["Department"], "Category": r["Category"],
                "Before ($)": r["Amount ($)_prior"], "After ($)": r["Amount ($)_current"], "Delta ($)": r["Diff ($)"],
                "Commentary Matched": None, "Classification": "Unclassified — awaiting commentary",
                "Status": "Awaiting Controller Input",
            })
    if phase3_result.status == CV.STATUS_OK:
        for _, r in phase3_result.flagged_rows.iterrows():
            obs_rows.append({
                "Detected By": "Phase 3 (Plausibility Review)",
                "Period": r["Fiscal Quarter"],
                "Type": "Plausibility Anomaly",
                "Department": r["Department"], "Category": r["Category"],
                "Before ($)": r["Prior ($)"], "After ($)": r["Amount ($)"], "Delta ($)": r["Amount ($)"] - r["Prior ($)"],
                "Commentary Matched": None, "Classification": "Unclassified — awaiting commentary",
                "Status": "Awaiting Controller Input",
            })
    observation_register = pd.DataFrame(
        obs_rows,
        columns=["Detected By", "Period", "Type", "Department", "Category", "Before ($)", "After ($)",
                 "Delta ($)", "Commentary Matched", "Classification", "Status"],
    )
    if observation_register.empty:
        st.success("No observations this run — register is empty.")
    else:
        st.dataframe(observation_register, use_container_width=True)

with tab_region_invest:
    st.title("Regional Revenue & Go-to-Market Investment")
    st.caption(
        "Shows whether go-to-market investment is growing in proportion to revenue by region — "
        "not a full profitability measure."
    )

    st.subheader(f"Revenue, Allocated GTM Cost, and Net of GTM Cost — {current_period}")
    st.bar_chart(region_cm_df[region_cm_df[period_col] == current_period].set_index("Region")["Region Net of GTM Cost ($)"])
    st.dataframe(fmt_display_df(region_cm_df[region_cm_df[period_col] == current_period][
        ["Region", "Region Revenue ($)", "Allocated S&M + CS Opex ($)", "Region Net of GTM Cost ($)"]
    ]), use_container_width=True)

    st.divider()
    st.subheader("Single-segment trend — Net of GTM Cost (%) of that region's own revenue, over time")
    st.caption(
        "This % is never shown next to another region's % — select one region to see its own trend. "
        "Comparing this figure across regions would always show the same value in a given period by "
        "construction of the revenue-share allocation, which is why that comparison isn't offered here."
    )
    region_options = sorted(region_pct_df["Region"].unique())
    selected_region = st.selectbox("Region", region_options, key="region_pct_select")
    region_trend = (
        region_pct_df[region_pct_df["Region"] == selected_region]
        .set_index(period_col)["Region Net of GTM Cost (%)"]
        .reindex(period_order)
    )
    st.line_chart(region_trend)

with tab_product_invest:
    st.title("Product Line Revenue & R&D Investment")
    st.caption(
        "Shows whether R&D investment is growing in proportion to revenue by product line — "
        "not a full profitability measure."
    )

    st.subheader(f"Revenue, Allocated R&D Cost, and Net of R&D Cost — {current_period}")
    st.bar_chart(product_cm_df[product_cm_df[period_col] == current_period].set_index("Product Line")["Product Net of R&D Cost ($)"])
    st.dataframe(fmt_display_df(product_cm_df[product_cm_df[period_col] == current_period][
        ["Product Line", "Product Revenue ($)", "Allocated R&D Opex ($)", "Product Net of R&D Cost ($)"]
    ]), use_container_width=True)
    st.caption(
        "Professional Services is excluded from the R&D allocation base entirely (it's a services line, "
        "not something R&D builds) — its Allocated R&D Opex is always $0, so its Net of R&D Cost equals "
        "its own revenue exactly. R&D is split only across Core Platform, Add-on: Forecasting, and "
        "Add-on: Reporting, by their relative revenue share among those three."
    )

    st.divider()
    st.subheader("Single-segment trend — Net of R&D Cost (%) of that product line's own revenue, over time")
    st.caption(
        "This % is never shown next to another product line's % — select one product line to see its "
        "own trend. Comparing this figure across the three R&D-allocation-base product lines would "
        "always show the same value in a given period by construction, which is why that comparison "
        "isn't offered here. Professional Services sits outside that identity entirely at a fixed 100%, "
        "since it receives no R&D allocation at all."
    )
    product_options = sorted(product_pct_df["Product Line"].unique())
    selected_product = st.selectbox("Product Line", product_options, key="product_pct_select")
    product_trend = (
        product_pct_df[product_pct_df["Product Line"] == selected_product]
        .set_index(period_col)["Product Net of R&D Cost (%)"]
        .reindex(period_order)
    )
    st.line_chart(product_trend)

with tab_narr:
    st.subheader(f"AI-Generated Narrative — {current_period} vs {prior_period}")
    st.caption("Uses the exact system + user prompt from northwind_narrative_prompt.md, populated from the tables in the other tabs.")

    user_prompt = R.build_user_prompt(
        period_col, period_order, current_period, prior_period, prior_period,
        pl_df, rev_region_df, rev_product_df, region_cm_df, product_cm_df,
        exp_dept_df, sb_df, breadth_df, hc_dept_df, company_rev_df, bva_df,
    )

    with st.expander("View rendered prompt (data sent to the model)"):
        st.text(user_prompt)

    api_key_present = bool(os.environ.get("ANTHROPIC_API_KEY"))

    if api_key_present:
        if st.button("Generate narrative", type="primary"):
            with st.spinner("Calling Claude..."):
                narrative, error = R.call_claude_narrative(user_prompt)
            if narrative:
                st.markdown(narrative.replace("\n\n", "\n\n> ").replace("\n", "\n\n"))
            else:
                st.error(error)
    else:
        st.info(
            "No ANTHROPIC_API_KEY found in this environment. Download the rendered prompt "
            "below and paste it into a Claude chat to generate the narrative manually — same "
            "system prompt, same rules, same numbers, just a manual hand-off instead of a "
            "live API call."
        )
        safe_current = current_period.replace(" ", "_")
        safe_prior = prior_period.replace(" ", "_")
        filename = f"prompt_{safe_current}_vs_{safe_prior}.txt"
        st.download_button(
            label="Download prompt for this period",
            data=user_prompt,
            file_name=filename,
            mime="text/plain",
            type="primary",
        )
