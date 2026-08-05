"""
Close Validation Service — Cycle 3, Task 2 (D10 continuation)

Extracts Phase 2 (Deterministic Validation) and Phase 3 (Plausibility
Review) out of the one-off close_v1_v2_simulation.py demo into a reusable,
generic production module, per the Cycle 3 Task 2 Builder Brief.

WHAT THIS MODULE IS
--------------------
A pure service: functions take structured input (pandas DataFrames already
loaded by the caller) and return structured output (dataclasses wrapping
pandas DataFrames). It contains NO fiscal-period-label literals, NO
company-specific injected dollar amounts, and makes NO assumption about
which department/category will be flagged. It operates
correctly on any current close compared against any prior approved close,
including the case where no prior close exists at all (the first approved
close in Close History).

INTERFACE DESIGN CHOICE (flagged for Architect confirmation; see Return
Report) — functions here accept already-loaded DataFrames, not file paths
and not the close_history.resolve_latest_approved_close() dict directly.
The Brief's wording ("accept ... the resolved-close object from
close_history.resolve_latest_approved_close()") could be read either way;
this module takes the stricter reading of "no filesystem side effects of
any kind" to mean no reads OR writes happen inside this module — the
caller resolves the latest approved close, loads whatever file(s) that
resolution points to (e.g. pd.read_excel(resolved['raw_dataset_path'],
'Expenses')), and hands the resulting DataFrame(s) in here. This keeps the
module trivially unit-testable with in-memory DataFrames and keeps the
"pure function, no side effects" property unambiguous rather than partial
(reads allowed, writes not). If the Architect prefers the module accept
the resolved-close dict and do the reads itself, that is a small, isolated
change to the two entry points below — flagged as an open question, not
decided unilaterally here.

WHAT THIS MODULE IS NOT
------------------------
- No console output, no file writes of any kind, no Streamlit/dashboard
  calls. If a caller wants a CSV, a rendered report, or a rendered table,
  that happens in the caller (dashboard, close_v1_v2_simulation.py
  fixture, future CLI/API), consuming the structured return value from
  here.
- No fiscal-calendar logic (that belongs to rollups.py's add_fiscal_cols).
  This module assumes the caller has already attached whatever period
  column it wants compared (Fiscal Quarter, Fiscal Year, or any other
  grain) and passes that column name in.
- No cause-assignment. Per system rule 6 (already established in the
  narrative pipeline), a plausibility flag never guesses at WHY a swing
  happened — it states that a driver was not identifiable from
  segment-level data, as a structured value, not free text a renderer
  would have to pattern-match.
"""

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Threshold values — PRODUCTION POLICY, not demo-only. Previously these lived
# only as comments inside close_v1_v2_simulation.py; per Cycle 3 Task 2 Item 1
# they are documented here as named parameters with defaults, not literals
# buried in logic.
#
# QoQ threshold rationale (unchanged from the Cycle 2 Task 3 derivation):
# derived from the historical distribution of |QoQ %| swings across all
# Department x Category cells in this dataset (excluding Salaries &
# Benefits, which has its own volume/rate logic — see
# rollups.py:build_salaries_volume_rate). The max naturally-occurring move
# found across the dataset's full history was 13.1%, in a single
# Department x Category x period cell. The threshold is set at roughly
# double that historical max, so a real
# seasonal or growth-driven swing should not trip it, while a materially
# larger, unexplained swing will.
#
# Headcount-driver band rationale: a headcount change of this many heads or
# fewer, in either direction, is treated as "no corresponding headcount
# change" for a department — i.e. within normal month-to-month headcount
# noise rather than a deliberate staffing shift that could plausibly drive
# a cost swing.
#
# Whether these two values should be promoted to a formal Decision Log
# entry (D11) now that they are production policy rather than demo-only is
# flagged in the Cycle 3 Task 2 Return Report for Architect decision — not
# decided in this module.
# ---------------------------------------------------------------------------
DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD = 0.25
DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND = 2

# Default categories excluded from Phase 3 (they have their own dedicated
# decomposition and would double-count / naturally trip a QoQ-based check
# for reasons Phase 3 doesn't model).
DEFAULT_EXCLUDED_CATEGORIES = ("Salaries & Benefits",)

# Structured status values (not free text) so callers can branch on them
# without string-matching a human-readable message.
STATUS_NOT_APPLICABLE = "NOT_APPLICABLE_NO_PRIOR_CLOSE"
STATUS_OK = "OK"

DRIVER_NOT_IDENTIFIABLE = "NOT_IDENTIFIABLE_FROM_SEGMENT_LEVEL_DATA"


@dataclass
class Phase2Result:
    """Structured result of a Phase 2 (Deterministic Validation) run.

    status:
        STATUS_NOT_APPLICABLE  -- there is no prior approved close to diff
                                   against (bootstrap case: this is the
                                   first approved close). flagged_rows is an
                                   empty, correctly-typed DataFrame in this
                                   case -- distinct from STATUS_OK with zero
                                   flagged rows, which means the comparison
                                   DID run and found no differences.
        STATUS_OK              -- the comparison ran. flagged_rows may still
                                   be empty (0 differences found).
    flagged_rows:
        DataFrame of key_cols + [f"{value_col}_prior", f"{value_col}_current",
        "Diff ($)"], one row per overlapping record whose value changed by
        more than `tolerance`.
    rows_compared:
        Count of overlapping records actually compared (0 when NOT_APPLICABLE).
    message:
        Human-readable summary for a caller that wants to log/display it.
        Not required reading -- status and flagged_rows carry the real signal.
    """
    status: str
    flagged_rows: pd.DataFrame
    rows_compared: int
    message: str


@dataclass
class Phase3Result:
    """Structured result of a Phase 3 (Plausibility Review) run.

    status:
        STATUS_OK is the only status Phase 3 returns when it has enough
        history to compute at least one QoQ comparison; if the target
        period has no prior period in the supplied data at all (e.g. the
        very first period in the dataset), status is STATUS_NOT_APPLICABLE
        and cells_checked is 0, since no QoQ swing can be computed with no
        prior period.
    flagged_rows:
        DataFrame of [Department, Category, period_col, "Prior ($)",
        "Amount ($)", "QoQ (%)", "Headcount Change", "Driver"] for every
        cell that crossed qoq_threshold with no corresponding headcount
        driver. "Driver" is always DRIVER_NOT_IDENTIFIABLE for flagged rows
        -- Phase 3 never assigns a cause (system rule 6).
    all_cells:
        DataFrame of every Department x Category cell checked in the target
        period (flagged or not), for callers that want full transparency,
        not just the flagged subset.
    target_period:
        The period this run actually evaluated (echoed back so a caller
        that didn't specify one explicitly can see what was inferred).
    cells_checked:
        Count of Department x Category cells evaluated.
    threshold / headcount_band:
        The actual threshold values used for this run (echoes the
        parameters, including any override), so a caller/report can state
        what was applied without re-deriving it.
    message:
        Human-readable summary. Not required reading.
    """
    status: str
    flagged_rows: pd.DataFrame
    all_cells: pd.DataFrame
    target_period: Optional[str]
    cells_checked: int
    threshold: float
    headcount_band: int
    message: str


def _empty_phase2_frame(key_cols, value_col):
    cols = list(key_cols) + [f"{value_col}_prior", f"{value_col}_current", "Diff ($)"]
    return pd.DataFrame(columns=cols)


def run_phase2_deterministic_validation(
    current_data,
    prior_data,
    key_cols=("Date", "Department", "Category"),
    value_col="Amount ($)",
    tolerance=0.005,
):
    """Diff a current close's data against a prior approved close's data on
    the overlapping key, flagging any nonzero difference. Generic over
    key_cols/value_col so it isn't tied to Expenses specifically, though
    Expenses (Date, Department, Category, Amount ($)) is the expected
    production usage per Close History's snapshot shape.

    Parameters
    ----------
    current_data : pd.DataFrame
        The current close's data (e.g. the Expenses sheet of the raw
        dataset currently being processed).
    prior_data : pd.DataFrame or None
        The latest approved close's equivalent data, already loaded by the
        caller (e.g. pd.read_excel(resolved['raw_dataset_path'],
        'Expenses')) -- or None / an empty DataFrame if
        close_history.resolve_latest_approved_close() returned None
        (bootstrap case: no prior approved close exists yet).
    key_cols : sequence of str
        Columns identifying a "same record" across the two closes.
    value_col : str
        The column being diffed.
    tolerance : float
        Absolute difference below which two values are treated as equal
        (guards against floating-point noise, not a business threshold).

    Returns
    -------
    Phase2Result
    """
    key_cols = list(key_cols)

    if prior_data is None or len(prior_data) == 0:
        return Phase2Result(
            status=STATUS_NOT_APPLICABLE,
            flagged_rows=_empty_phase2_frame(key_cols, value_col),
            rows_compared=0,
            message=(
                "No prior approved close to compare against (bootstrap case). "
                "Phase 2 does not apply to the first approved close in Close History."
            ),
        )

    missing_current = [c for c in key_cols + [value_col] if c not in current_data.columns]
    missing_prior = [c for c in key_cols + [value_col] if c not in prior_data.columns]
    if missing_current or missing_prior:
        raise ValueError(
            f"Phase 2 input missing required columns. "
            f"current_data missing: {missing_current}, prior_data missing: {missing_prior}"
        )

    overlap = prior_data[key_cols + [value_col]].merge(
        current_data[key_cols + [value_col]],
        on=key_cols,
        suffixes=("_prior", "_current"),
        how="inner",
    )
    overlap["Diff ($)"] = overlap[f"{value_col}_current"] - overlap[f"{value_col}_prior"]
    flagged = overlap[overlap["Diff ($)"].abs() > tolerance].copy().reset_index(drop=True)

    return Phase2Result(
        status=STATUS_OK,
        flagged_rows=flagged,
        rows_compared=len(overlap),
        message=(
            f"Compared {len(overlap)} overlapping records between the current close and the "
            f"latest approved close; {len(flagged)} flagged with a nonzero difference."
        ),
    )


def _resolve_target_period(period_col, period_order, target_period, data):
    if target_period is not None:
        return target_period
    if period_order:
        return period_order[-1]
    # No explicit order supplied: fall back to the max value present in the
    # data itself. This is a best-effort default for callers that don't
    # have a curated chronological order handy -- it is NOT a fiscal-aware
    # sort (this module has no fiscal-calendar knowledge by design), so
    # callers with period labels that don't sort correctly in plain string
    # order (e.g. single- vs double-digit period numbers within a year)
    # should always pass period_order explicitly.
    if period_col in data.columns and len(data) > 0:
        return sorted(data[period_col].unique())[-1]
    return None


def run_phase3_plausibility_review(
    expenses,
    headcount,
    period_col="Fiscal Quarter",
    period_order=None,
    target_period=None,
    exclude_categories=DEFAULT_EXCLUDED_CATEGORIES,
    qoq_threshold=DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD,
    headcount_band=DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND,
):
    """Flag Department x Category cells in the target period whose QoQ (or
    equivalent sequential-period) % change from the immediately preceding
    period exceeds `qoq_threshold`, AND where that department's headcount
    change over the same span falls within `headcount_band` (i.e. no
    corresponding headcount driver for the swing).

    Never assigns a cause (system rule 6): every flagged row's "Driver"
    value is the constant DRIVER_NOT_IDENTIFIABLE.

    Parameters
    ----------
    expenses : pd.DataFrame
        Must contain [Department, Category, period_col, "Amount ($)"] at
        whatever grain period_col represents. Not assumed to be
        fiscal-quarter-specific -- any period_col name/grain works as long
        as it's consistent with `headcount`.
    headcount : pd.DataFrame
        Must contain [Department, period_col, "Headcount"] (or a
        pre-aggregated average per period -- if raw monthly rows are
        passed, they are averaged per Department x period_col here).
    period_col : str
        Name of the period column shared by both inputs.
    period_order : sequence or None
        Chronological order of period labels. Required for a reliable
        "immediately preceding period" lookup unless the labels happen to
        sort correctly on their own (see _resolve_target_period). Strongly
        recommended to always pass this explicitly in production.
    target_period : str or None
        The period to evaluate. Defaults to the last entry in
        period_order, or (if period_order is not given) the max period
        label found in `expenses`.
    exclude_categories : sequence of str
        Categories skipped entirely (default: Salaries & Benefits, which
        has its own dedicated volume/rate decomposition elsewhere in the
        pipeline).
    qoq_threshold : float
        See module-level DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD for rationale.
    headcount_band : int
        See module-level DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND for rationale.

    Returns
    -------
    Phase3Result
    """
    required_exp_cols = {"Department", "Category", period_col, "Amount ($)"}
    missing_exp = required_exp_cols - set(expenses.columns)
    if missing_exp:
        raise ValueError(f"Phase 3 expenses input missing required columns: {sorted(missing_exp)}")
    required_hc_cols = {"Department", period_col, "Headcount"}
    missing_hc = required_hc_cols - set(headcount.columns)
    if missing_hc:
        raise ValueError(f"Phase 3 headcount input missing required columns: {sorted(missing_hc)}")

    resolved_target = _resolve_target_period(period_col, period_order, target_period, expenses)

    if period_order:
        order_map = {p: i for i, p in enumerate(period_order)}
    else:
        order_map = {p: i for i, p in enumerate(sorted(expenses[period_col].unique()))}

    if resolved_target is None or resolved_target not in order_map:
        return Phase3Result(
            status=STATUS_NOT_APPLICABLE,
            flagged_rows=pd.DataFrame(columns=["Department", "Category", period_col, "Prior ($)",
                                                "Amount ($)", "QoQ (%)", "Headcount Change", "Driver"]),
            all_cells=pd.DataFrame(),
            target_period=resolved_target,
            cells_checked=0,
            threshold=qoq_threshold,
            headcount_band=headcount_band,
            message="Could not resolve a target period to evaluate.",
        )

    target_ord = order_map[resolved_target]
    if target_ord == 0:
        # No prior period exists at all -- nothing to compute a QoQ swing
        # against. Expected for the very first period in a dataset, not an
        # error.
        return Phase3Result(
            status=STATUS_NOT_APPLICABLE,
            flagged_rows=pd.DataFrame(columns=["Department", "Category", period_col, "Prior ($)",
                                                "Amount ($)", "QoQ (%)", "Headcount Change", "Driver"]),
            all_cells=pd.DataFrame(),
            target_period=resolved_target,
            cells_checked=0,
            threshold=qoq_threshold,
            headcount_band=headcount_band,
            message=f"'{resolved_target}' has no preceding period in the supplied data -- Phase 3 needs at least one prior period.",
        )

    dept_cat = (
        expenses[~expenses["Category"].isin(exclude_categories)]
        .groupby(["Department", "Category", period_col], as_index=False)["Amount ($)"].sum()
    )
    dept_cat["_ord"] = dept_cat[period_col].map(order_map)
    dept_cat = dept_cat.sort_values(["Department", "Category", "_ord"])
    dept_cat["Prior ($)"] = dept_cat.groupby(["Department", "Category"])["Amount ($)"].shift(1)
    dept_cat["_prior_ord"] = dept_cat.groupby(["Department", "Category"])["_ord"].shift(1)

    # Average headcount per Department x period (averages if the caller
    # passed raw monthly rows; a no-op if already period-level).
    hc_period = headcount.groupby(["Department", period_col], as_index=False)["Headcount"].mean()
    hc_period["_ord"] = hc_period[period_col].map(order_map)
    hc_period = hc_period.sort_values(["Department", "_ord"])
    hc_period["Prior Headcount"] = hc_period.groupby("Department")["Headcount"].shift(1)
    hc_period["Headcount Change"] = hc_period["Headcount"] - hc_period["Prior Headcount"]

    target_cells = dept_cat[dept_cat["_ord"] == target_ord].copy()
    # Only keep cells whose "prior" row is genuinely the immediately
    # preceding period (guards against gaps in the data being silently
    # treated as adjacent).
    target_cells = target_cells[target_cells["_prior_ord"] == target_ord - 1]
    target_cells["QoQ (%)"] = np.where(
        target_cells["Prior ($)"].notna() & (target_cells["Prior ($)"] != 0),
        (target_cells["Amount ($)"] - target_cells["Prior ($)"]) / target_cells["Prior ($)"],
        np.nan,
    )

    target_hc = hc_period[hc_period["_ord"] == target_ord][["Department", "Headcount Change"]]
    merged = target_cells.merge(target_hc, on="Department", how="left")

    merged["Driver"] = ""
    flag_condition = (
        merged["QoQ (%)"].abs() > qoq_threshold
    ) & (
        merged["Headcount Change"].abs() <= headcount_band
    )
    merged.loc[flag_condition, "Driver"] = DRIVER_NOT_IDENTIFIABLE

    out_cols = ["Department", "Category", period_col, "Prior ($)", "Amount ($)",
                "QoQ (%)", "Headcount Change", "Driver"]
    all_cells = merged[out_cols].reset_index(drop=True)
    flagged = all_cells[all_cells["Driver"] == DRIVER_NOT_IDENTIFIABLE].reset_index(drop=True)

    return Phase3Result(
        status=STATUS_OK,
        flagged_rows=flagged,
        all_cells=all_cells,
        target_period=resolved_target,
        cells_checked=len(all_cells),
        threshold=qoq_threshold,
        headcount_band=headcount_band,
        message=(
            f"Checked {len(all_cells)} Department x Category cells in '{resolved_target}'; "
            f"{len(flagged)} flagged (|QoQ %| > {qoq_threshold:.0%}, headcount change within "
            f"+/-{headcount_band} heads)."
        ),
    )
