"""
period_lifecycle.py — D15 (Period Lifecycle, Reopen, and Correction/Reprocessing)

Implements the FIXED (not Builder-judgment) architecture in
governance/builder_briefs/period_lifecycle_reopen_correction_brief.md,
Sections 5.E-5.I:

  - 5.E: numerical-impact comparison over the minimum independent-
    comparison set (six canonical outputs, quarterly grain).
  - 5.F: the three-way distinction between technical regeneration
    (never itself business-facing), numerical_impact (machine-determined
    per period), and business-level reprocessing_required.
  - 5.G: per-period chronological propagation with a first-unaffected-
    period stopping rule.
  - 5.H: chronological blocking, a read-time check against Close
    History's dependency metadata.
  - 5.I: lineage/audit evidence shape (trigger + predecessor), meant to
    be passed into close_history.archive_close()'s existing
    extra_metadata hook -- no new persistence mechanism invented here.

This module contains NO Streamlit/UI code and NO session-state handling
-- it is pure comparison/classification logic, independently callable
and independently testable, per the Brief's "live, connected" evidence
requirement being about the *product*, not about every helper function
needing a UI. The interactive reopen flow (Sections 5.B-5.D: the
"Select period to close" control, the two-step reopen transactional
boundary, and correction/data-intake handling) lives in the dashboard
and session state, and calls into this module rather than duplicating
its logic.

Per Section 4 of the Brief: the numerical-equality tolerance below is a
BUILDER PROPOSAL requiring explicit Architect confirmation before 5.E is
accepted as Pass -- see PROPOSED_EPSILON's docstring. Everything else in
this module implements the Brief's already-fixed architecture verbatim;
no other value here is a Builder judgment call.
"""

import os
import subprocess
import sys
import shutil
import tempfile

import pandas as pd



# -----------------------------------------------------------------------
# 5.E — the minimum independent-comparison set (Brief Section 5.E table).
# This dict is NOT a starting point for Builder judgment -- it is the
# complete, fixed comparison scope, transcribed verbatim from the Brief.
# All other named canonical outputs are regenerated, never independently
# compared (Brief Section 5.E, "All other named canonical outputs...").
# -----------------------------------------------------------------------
CANONICAL_COMPARISON_SET = {
    "PL_Quarterly": {
        "grain": ["Fiscal Quarter"],
        "fields": ["Total Revenue ($)", "Total Opex ($)"],
    },
    "Rev_by_Region_Q": {
        "grain": ["Region", "Fiscal Quarter"],
        "fields": ["Revenue ($)"],
    },
    "Rev_by_Product_Q": {
        "grain": ["Product Line", "Fiscal Quarter"],
        "fields": ["Revenue ($)"],
    },
    "Exp_by_Dept_Cat_Q": {
        "grain": ["Department", "Category", "Fiscal Quarter"],
        "fields": ["Amount ($)"],
    },
    "Headcount_Q": {
        "grain": ["Department", "Fiscal Quarter"],
        "fields": ["Avg Headcount", "Ending Headcount"],
    },
    "BvA_Q": {
        "grain": ["Line Item", "Fiscal Quarter"],
        "fields": ["Budget ($)", "Actual ($)"],
    },
}

PERIOD_COL = "Fiscal Quarter"

# --- Builder proposal, per Brief Section 4: "Builder proposes a specific
# epsilon consistent with existing tie-out conventions...; this section is
# not accepted as Pass until the Architect confirms the proposed value."
#
# Proposed value: 0.005 (half a cent), matching close_validation.py's own
# Phase 2 tolerance default (run_phase2_deterministic_validation's
# `tolerance=0.005` parameter) -- the only existing numeric-equality
# tolerance convention in this codebase, guarding against floating-point
# noise from the Excel round-trip (xlsx read/write), not a business
# materiality threshold. NOT YET ARCHITECT-CONFIRMED. Callers should treat
# this constant as provisional and override it explicitly if/when the
# Architect specifies a different value.
PROPOSED_EPSILON = 0.005


class ComparisonOutputResult:
    """Result of comparing one canonical output at one period between two
    states (before/after)."""

    def __init__(self, output_name, period_label, diffs_df, impact):
        self.output_name = output_name
        self.period_label = period_label
        self.diffs_df = diffs_df  # rows with a difference beyond epsilon, or an added/removed row
        self.impact = impact  # bool: True if diffs_df is non-empty

    def to_dict(self):
        return {
            "output_name": self.output_name,
            "period_label": self.period_label,
            "impact": self.impact,
            "diff_row_count": 0 if self.diffs_df is None else len(self.diffs_df),
            "diffs": [] if self.diffs_df is None else self.diffs_df.to_dict(orient="records"),
        }


def _read_sheet_for_period(xlsx_path, sheet_name, period_label, grain, fields):
    df = pd.read_excel(xlsx_path, sheet_name=sheet_name)
    missing = [c for c in grain + fields if c not in df.columns]
    if missing:
        raise ValueError(f"Sheet '{sheet_name}' in {xlsx_path} is missing expected columns: {missing}")
    return df[df[PERIOD_COL] == period_label][grain + fields].reset_index(drop=True)


def compare_one_output(output_name, period_label, before_xlsx_path, after_xlsx_path, epsilon=PROPOSED_EPSILON):
    """Compare a single canonical output, at period_label's grain rows only,
    between two rollups_output.xlsx-shaped workbooks. Returns a
    ComparisonOutputResult. A row present in one side and absent in the
    other (e.g. a Department/Category combination that newly appears or
    disappears) is itself treated as a difference, not silently ignored."""
    spec = CANONICAL_COMPARISON_SET[output_name]
    grain, fields = spec["grain"], spec["fields"]

    before = _read_sheet_for_period(before_xlsx_path, output_name, period_label, grain, fields)
    after = _read_sheet_for_period(after_xlsx_path, output_name, period_label, grain, fields)

    merged = before.merge(after, on=grain, how="outer", suffixes=("_before", "_after"), indicator=True)

    diff_mask = pd.Series(False, index=merged.index)
    # Rows that exist on only one side are always a difference.
    diff_mask |= merged["_merge"] != "both"
    for f in fields:
        b_col, a_col = f"{f}_before", f"{f}_after"
        # For outer-merge rows missing one side, the field column is NaN;
        # treat NaN-vs-value as already covered by the _merge != "both"
        # check above, and only apply the numeric epsilon test where both
        # sides are present.
        both_present = merged["_merge"] == "both"
        field_diff = (merged[b_col] - merged[a_col]).abs() > epsilon
        diff_mask |= (both_present & field_diff.fillna(False))

    diffs = merged[diff_mask].copy()
    diffs["Fiscal Quarter"] = period_label
    return ComparisonOutputResult(output_name, period_label, diffs, impact=len(diffs) > 0)


def compare_period_outputs(period_label, before_xlsx_path, after_xlsx_path, epsilon=PROPOSED_EPSILON):
    """5.E — compare ALL six canonical outputs for one period between a
    before-state and an after-state rollups_output.xlsx. Returns
    (numerical_impact: bool, results: dict[output_name -> ComparisonOutputResult]).

    numerical_impact is True iff ANY of the six outputs shows a difference
    at this period's grain -- this is what makes the fixture in the Brief's
    acceptance criterion work: an offsetting Department/Category change
    that nets to zero at company-level PL_Quarterly is still caught here,
    because Exp_by_Dept_Cat_Q is compared independently, not derived from
    PL_Quarterly."""
    results = {}
    any_impact = False
    for output_name in CANONICAL_COMPARISON_SET:
        r = compare_one_output(output_name, period_label, before_xlsx_path, after_xlsx_path, epsilon=epsilon)
        results[output_name] = r
        any_impact = any_impact or r.impact
    return any_impact, results


# -----------------------------------------------------------------------
# Item A (D15-Item2-Corrections Brief, OI-8) -- period-scoped correction
# intake. Runs BEFORE compute_candidate_rollups_output/revalidate_period_
# from_raw: a correction upload for one reopened period must never be
# allowed to silently carry a *different* value for some other period's
# months into that period's eventual archived snapshot. See the Brief's
# Item A for the required behavior; the reconciliation strategy chosen
# here (documented in CorrectionScopeViolation's own docstring below) is
# a Builder judgment call flagged for Architect confirmation, not a
# literal-text-only implementation -- see the Return Report.
# -----------------------------------------------------------------------

# Sheet -> (key columns, value columns) for every raw workbook sheet that
# is period-keyed (carries a Date column mapping to a Fiscal Quarter) and
# is a genuine transactional input (not a derived/tie-out sheet). This is
# NOT every sheet in the raw workbook -- PL_Summary and README are
# intentionally excluded; see the Return Report's Assumptions section for
# why, and why that is an acceptable minimum-scope choice rather than a
# silent gap.
CORRECTION_SCOPE_SHEETS = {
    "Revenue":          {"key_cols": ["Date", "Region", "Product Line"], "value_cols": ["Revenue ($)"]},
    "Expenses":         {"key_cols": ["Date", "Department", "Category"], "value_cols": ["Amount ($)"]},
    "Headcount":        {"key_cols": ["Date", "Department"], "value_cols": ["Headcount"]},
    "Budget_vs_Actual": {"key_cols": ["Date", "Line Item"], "value_cols": ["Budget ($)", "Actual ($)"]},
}


class CorrectionScopeViolation(Exception):
    """Retained for structural/back-compat reasons only -- as of Addendum
    1, enforce_period_scoped_correction() no longer raises this. Item A
    was revised from reject-outright to warn-and-exclude: the function
    now always returns its detected violations (possibly empty) rather
    than raising on them, so the caller can present them to the user and
    let the user choose Continue/Cancel (see the function's own
    docstring below)."""
    def __init__(self, message, violations):
        super().__init__(message)
        self.violations = violations


def enforce_period_scoped_correction(raw_dataset_path, target_period, R_module, close_history_module, tolerance=PROPOSED_EPSILON):
    """Item A (OI-8), REVISED by D15-Item2-Corrections Addendum 1:
    warn-and-exclude replaces reject-outright. Detection logic is
    unchanged from the original Item A. Read the uploaded correction
    workbook and, for every sheet in CORRECTION_SCOPE_SHEETS, split its
    rows into the reopened period's (`target_period`) own fiscal months
    vs. every other period's.

    For each OTHER period actually present in the upload:
      - No approved snapshot exists for that period yet (per
        close_history_module.resolve_latest_approved_close_for_period) --
        nothing established to violate; those rows are accepted as
        supplied, unchanged.
      - An approved snapshot exists -- every uploaded row for that period
        is checked (within `tolerance`) against that period's own
        last-approved value for the same key columns. Any added row,
        removed row, or changed value is recorded as a violation.

    UNLIKE the original Item A, this function NEVER raises on a detected
    violation. It always returns (scoped_path, scratch_dir, violations):
    violations is a list (possibly empty) of the same detail dicts the
    original CorrectionScopeViolation carried (sheet, period, key, and
    either an added/removed `issue` or a `field`/`approved_value`/
    `uploaded_value` triple). The caller is responsible for Addendum 1's
    warn-and-exclude UI: surface `violations` to the user with an
    explicit Continue/Cancel choice BEFORE treating the returned
    scoped_path as usable -- Cancel must discard it and create nothing,
    exactly like the original reject-outright behavior; Continue proceeds
    using it as-is. This function does the substitution work for
    "Continue" unconditionally as part of building scoped_path (see
    below), so the caller does not need to re-derive it -- only decide
    whether to proceed.

    Returns (scoped_path, scratch_dir, violations) -- scoped_path is a
    newly-written .xlsx, same sheet set as the upload, where:
      - CORRECTION_SCOPE_SHEETS sheets contain the reopened period's own
        rows exactly as uploaded, plus -- for every OTHER period that HAS
        an approved snapshot -- that period's own currently-approved rows
        (sourced from the approved snapshot itself, never the upload, so
        an excluded/conflicting out-of-period row is silently replaced by
        its approved value in the output regardless of whether it was a
        violation or already identical) -- plus, for periods with no
        approved snapshot, the upload's own rows for that period (nothing
        to reconcile against).
      - PL_Summary and README (and any other sheet outside
        CORRECTION_SCOPE_SHEETS) are passed through from the upload
        unfiltered. PL_Summary source-of-truth fix (this session):
        rollups.py no longer ties PL_Summary out against anything, or
        sources any figure from it -- PL_Summary is a hardcoded,
        unverified reference sheet, not a computed source -- so this is
        pure passthrough with no backstop check on it any longer.

    Rationale for reconstructing a FULL multi-period workbook here rather
    than writing a file containing ONLY the reopened period's rows:
    rollups.py structurally requires full multi-period history to run at
    all (sequential QoQ/YoY variance, quarter_order, its own internal tie-
    outs), and close_history.py's existing convention -- unchanged by
    this Brief, exercised by every close before and after this fix -- is
    that an archived raw_dataset.xlsx is always a full workbook, because
    rollups.py's own find_raw_dataset() bootstrap path resolves the
    GLOBAL-latest-by-timestamp approved close and re-runs the full
    pipeline against ITS raw_dataset_path. A period-only-filtered archive
    would silently break that resolver -- and therefore the live app's
    own startup/reload path -- the moment such a snapshot became global-
    latest. Reconstructing a full, per-row-verified workbook achieves the
    same protection (no unauthorized cross-period value can ever reach
    the archive, once the user has confirmed Continue) without that
    regression. Flagged for Architect confirmation in the Return Report.
    """
    xl = pd.ExcelFile(raw_dataset_path)
    sheet_names = xl.sheet_names
    all_sheets = {name: pd.read_excel(xl, name) for name in sheet_names}

    violations = []
    reconstructed = {}
    _approved_cache = {}

    def _approved_sheet_with_fq(other_period, sheet_name):
        if other_period not in _approved_cache:
            _approved_cache[other_period] = close_history_module.resolve_latest_approved_close_for_period(other_period)
        approved = _approved_cache[other_period]
        if approved is None:
            return None
        approved_xl = pd.ExcelFile(approved["raw_dataset_path"])
        if sheet_name not in approved_xl.sheet_names:
            return None
        adf = pd.read_excel(approved_xl, sheet_name)
        adf["Date"] = pd.to_datetime(adf["Date"])
        return R_module.add_fiscal_cols(adf)

    for sheet_name, spec in CORRECTION_SCOPE_SHEETS.items():
        if sheet_name not in all_sheets:
            continue
        key_cols, value_cols = spec["key_cols"], spec["value_cols"]
        df = all_sheets[sheet_name].copy()
        df["Date"] = pd.to_datetime(df["Date"])
        df_fq = R_module.add_fiscal_cols(df)

        in_period_rows = df_fq[df_fq["Fiscal Quarter"] == target_period].copy()
        out_of_period_rows = df_fq[df_fq["Fiscal Quarter"] != target_period].copy()

        kept_frames = [in_period_rows]

        if not out_of_period_rows.empty:
            for other_period, group in out_of_period_rows.groupby("Fiscal Quarter"):
                approved_fq = _approved_sheet_with_fq(other_period, sheet_name)
                if approved_fq is None:
                    kept_frames.append(group)
                    continue
                approved_period_rows = approved_fq[approved_fq["Fiscal Quarter"] == other_period]

                merged = approved_period_rows[key_cols + value_cols].merge(
                    group[key_cols + value_cols], on=key_cols, how="outer",
                    suffixes=("_approved", "_uploaded"), indicator=True,
                )
                for _, row in merged.iterrows():
                    if row["_merge"] != "both":
                        violations.append({
                            "sheet": sheet_name, "period": other_period,
                            "key": {k: row[k] for k in key_cols},
                            "issue": "row present only in " + ("upload" if row["_merge"] == "right_only" else "the approved snapshot"),
                        })
                        continue
                    for vc in value_cols:
                        a, u = row.get(f"{vc}_approved"), row.get(f"{vc}_uploaded")
                        if pd.notna(a) and pd.notna(u) and abs(float(a) - float(u)) > tolerance:
                            violations.append({
                                "sheet": sheet_name, "period": other_period,
                                "key": {k: row[k] for k in key_cols}, "field": vc,
                                "approved_value": float(a), "uploaded_value": float(u),
                            })
                # Addendum 1: the approved snapshot's own rows are used
                # for this other period UNCONDITIONALLY -- whether or not
                # a violation was found above -- since "Continue" means
                # every excluded row is silently reset to its approved
                # value, and the identical-row case (no violation) always
                # resolved to the approved copy already, pre-Addendum.
                kept_frames.append(approved_period_rows[df_fq.columns])

        reconstructed[sheet_name] = pd.concat(kept_frames, ignore_index=True) if kept_frames else in_period_rows

    out_dir = tempfile.mkdtemp(prefix="d15_scoped_correction_")
    out_path = os.path.join(out_dir, "scoped_corrected_dataset.xlsx")
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for sheet_name in sheet_names:
            df_out = reconstructed.get(sheet_name)
            if df_out is None:
                df_out = all_sheets[sheet_name]
            else:
                df_out = df_out.drop(columns=["Fiscal Year", "Fiscal Quarter"], errors="ignore")
            df_out.to_excel(writer, sheet_name=sheet_name, index=False)
    return out_path, out_dir, violations


# -----------------------------------------------------------------------
# Bug/Change 6 -- upload-time compatibility review of a corrected dataset.
# Runs the moment a file is attached on the reopen screen (not when "Run
# correction intake" is clicked), so a wrong/corrupted file is explained in
# plain language instead of surfacing rollups.py's raw traceback.
# -----------------------------------------------------------------------

# The transactional sheets the pipeline requires (README is not read).
# PL_Summary removed this session (PL_Summary source-of-truth fix):
# rollups.py's build_pl_rollup() no longer sums PL_Summary at all, so it is
# no longer required, or checked, at upload -- a corrected dataset missing
# or with a malformed PL_Summary sheet is now accepted.
DATASET_REQUIRED_SHEETS = ["Revenue", "Expenses", "Headcount", "Budget_vs_Actual"]

# Columns each required sheet must carry for the pipeline (key + value
# columns for the four transactional sheets).
DATASET_REQUIRED_COLUMNS = {
    name: spec["key_cols"] + spec["value_cols"] for name, spec in CORRECTION_SCOPE_SHEETS.items()
}

# Bug/Change 6 (follow-up): columns that must hold numbers. Text in any of
# them (e.g. a letter typed over a value) breaks rollups.py's sums with a
# raw "TypeError: unsupported operand type(s)", so it is caught at upload.
DATASET_NUMERIC_COLUMNS = {
    "Revenue": ["Revenue ($)"],
    "Expenses": ["Amount ($)"],
    "Headcount": ["Headcount"],
    "Budget_vs_Actual": ["Budget ($)", "Actual ($)"],
}

CHECK_OK = "ok"
CHECK_NOT_A_DATASET = "not_a_dataset"
CHECK_MISSING_SHEETS = "missing_sheets"
CHECK_MISSING_COLUMNS = "missing_columns"
CHECK_NO_PERIOD_DATA = "no_period_data"
CHECK_INVALID_VALUES = "invalid_values"


class CorrectionUploadCheck:
    """Result of validate_correction_upload(). `ok` is True only when every
    check passed; otherwise `stage` names the first check that failed and
    `message` is the user-facing sentence to display. `names` lists the
    sheets/categories the message refers to."""
    def __init__(self, ok, stage, message="", names=None):
        self.ok, self.stage, self.message, self.names = ok, stage, message, list(names or [])


def validate_correction_upload(file_bytes, target_period, R_module):
    """Review an uploaded corrected dataset for compatibility, in this order,
    returning at the FIRST failure:

      1. Is it a dataset file at all? (must open as an .xlsx workbook AND
         contain at least one of the dataset's sheets -- e.g. a Commentary
         workbook or a renamed non-Excel file is not a dataset.)
      2. Are all the dataset's sheets there? (and, per present sheet, the
         columns the pipeline needs)
      3. Are the values valid? (numbers in the numeric columns, real dates
         in Date -- e.g. a letter typed over a figure is refused here)
      4. Is there data for the period being reopened, in every category?

    Pure function of the file's bytes -- reads nothing else, writes nothing.
    """
    import io
    try:
        xl = pd.ExcelFile(io.BytesIO(file_bytes))
        present = list(xl.sheet_names)
    except Exception:
        return CheckResultNotDataset()

    if not any(name in present for name in DATASET_REQUIRED_SHEETS):
        return CheckResultNotDataset()

    missing = [n for n in DATASET_REQUIRED_SHEETS if n not in present]
    if missing:
        return CorrectionUploadCheck(
            False, CHECK_MISSING_SHEETS,
            "The categories are missing in the dataset you have uploaded: " + ", ".join(missing) + ".",
            missing,
        )

    frames, bad_cols = {}, []
    for name in DATASET_REQUIRED_SHEETS:
        try:
            df = pd.read_excel(xl, name)
        except Exception:
            return CheckResultNotDataset()
        lacking = [c for c in DATASET_REQUIRED_COLUMNS[name] if c not in df.columns]
        if lacking:
            bad_cols.append(f"{name} ({', '.join(lacking)})")
        frames[name] = df
    if bad_cols:
        return CorrectionUploadCheck(
            False, CHECK_MISSING_COLUMNS,
            "The categories in the dataset you have uploaded do not have the expected columns: "
            + "; ".join(bad_cols) + ".",
            [b.split(" (")[0] for b in bad_cols],
        )

    # Values must be numbers (numeric columns) and dates (Date column).
    invalid = []
    for name in DATASET_REQUIRED_SHEETS:
        df = frames[name]
        for col in DATASET_NUMERIC_COLUMNS[name]:
            # Any text cell that pandas could not read as a number counts.
            # (A numeric-looking text cell such as "123" is read as a
            # number by pandas -- and by rollups.py, which reads the file
            # the same way -- so it is correctly not flagged.)
            is_text = df[col].map(lambda v: isinstance(v, str))
            n_bad = int((df[col].notna() & (is_text | pd.to_numeric(df[col], errors="coerce").isna())).sum())
            if n_bad:
                invalid.append(f"{name} ({col}: {n_bad} non-numeric value{'s' if n_bad != 1 else ''})")
        # A blank Date is as fatal as a bad one: rollups.py cannot derive a
        # fiscal quarter from it and crashes (IntCastingNaNError). Rows that
        # are entirely empty are not a problem -- pandas drops them on read.
        df = df.dropna(how="all")
        n_bad = int((df["Date"].isna() | pd.to_datetime(df["Date"], errors="coerce").isna()).sum())
        if n_bad:
            invalid.append(f"{name} (Date: {n_bad} blank or invalid date{'s' if n_bad != 1 else ''})")
    if invalid:
        return CorrectionUploadCheck(
            False, CHECK_INVALID_VALUES,
            "The dataset you have uploaded contains values that are not valid: " + "; ".join(invalid)
            + ". These columns must contain only numbers (and valid dates).",
            sorted({i.split(" (")[0] for i in invalid}),
        )

    empty = []
    for name in DATASET_REQUIRED_SHEETS:
        df = frames[name].copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")   # a blank/invalid Date -> NaT
        df = df.dropna(subset=["Date"])
        if df.empty or not (R_module.add_fiscal_cols(df)["Fiscal Quarter"] == target_period).any():
            empty.append(name)
    if empty:
        return CorrectionUploadCheck(
            False, CHECK_NO_PERIOD_DATA,
            "There is no data in the dataset you have uploaded for the categories (" + ", ".join(empty)
            + f") matching the period you are reopening ({R_module.fmt_period_label(target_period)}).",
            empty,
        )
    return CorrectionUploadCheck(True, CHECK_OK)


def CheckResultNotDataset():
    return CorrectionUploadCheck(False, CHECK_NOT_A_DATASET, "You have not uploaded a dataset file.")


def _commentary_snapshot_by_oid(commentary_record_dict):
    """Item F helper. Reduce a commentary-record collection to
    {observation_id: current_text} for the added/edited/removed
    comparison. Accepts EITHER shape:

    - The JSON dict archive_close() reads back (CommentaryRecord.to_dict()'s
      shape: {"accepted_version_number": ..., "versions": [{"version_number":
      ..., "text": ...}]}) -- this is always the PRIOR (already-archived)
      side. "Current" here is the version actually marked Accepted
      (accepted_version_number), looked up by version_number in `versions`
      -- NOT necessarily the last version entered. The live UI's "Mark
      version as Accepted" control allows accepting any version, not only
      the latest, so a later, never-accepted draft can and does exist
      alongside an earlier accepted version (Architect Review 2, Item F
      defect: reading versions[-1] here misreads that case in both
      directions -- a false "changed" when the candidate's re-entry
      matches the accepted text but not an abandoned later draft, and a
      false "unchanged" the other way around). Falls back to the last
      version only if accepted_version_number is None -- a record with
      zero acceptances, which normal flow shouldn't produce, but the
      fallback avoids raising on it rather than silently mis-resolving.
    - The candidate's own live dict of CommentaryRecord objects -- ALWAYS
      the CANDIDATE side. Bug/Change 4: the candidate now runs the same
      Commentary Review as a not-yet-closed period, including "Mark
      Accepted", so "current" is resolved exactly as on the prior side --
      the version marked Accepted, else (no acceptance recorded) the last
      version entered. Before Bug/Change 4 the candidate had no accept
      step and always read the last version."""
    out = {}
    for oid, rec in (commentary_record_dict or {}).items():
        if isinstance(rec, dict):
            versions = rec.get("versions") or []
            if not versions:
                continue
            accepted_num = rec.get("accepted_version_number")
            accepted = next((v for v in versions if v.get("version_number") == accepted_num), None) \
                if accepted_num is not None else None
            out[oid] = accepted["text"] if accepted is not None else versions[-1]["text"]
        else:
            if rec.versions:
                accepted_num = rec.accepted_version_number
                accepted = next((v for v in rec.versions if v.version_number == accepted_num), None) \
                    if accepted_num is not None else None
                out[oid] = (accepted if accepted is not None else rec.versions[-1]).text
    return out


def commentary_changed(prior_commentary_record, candidate_commentary_records):
    """Item F. True if the candidate's matched commentary (Item E) differs
    from the prior approved version's stored commentary_record for the
    same period, by observation -- an observation newly commented
    (added), an existing observation's text differing (edited), or a
    previously-commented observation no longer commented (removed) all
    count, per Principal confirmation. Returns (changed: bool, detail:
    dict with "added"/"removed"/"edited" observation-id lists) so the
    caller can show specifics, not just a boolean.

    prior_commentary_record: the prior version's metadata["commentary_record"]
    dict (JSON shape, {} if none) -- "current" per observation there is
    the version actually marked Accepted, not necessarily the last one
    entered (see _commentary_snapshot_by_oid). candidate_commentary_records:
    the candidate's own {observation_id: CommentaryRecord} dict (Item E,
    {} if none entered this session) -- "current" there is the latest
    entered version, since Item E has no accept step."""
    prior_snapshot = _commentary_snapshot_by_oid(prior_commentary_record)
    candidate_snapshot = _commentary_snapshot_by_oid(candidate_commentary_records)
    added = set(candidate_snapshot) - set(prior_snapshot)
    removed = set(prior_snapshot) - set(candidate_snapshot)
    edited = {oid for oid in (set(prior_snapshot) & set(candidate_snapshot))
              if prior_snapshot[oid] != candidate_snapshot[oid]}
    changed = bool(added or removed or edited)
    return changed, {"added": sorted(added), "removed": sorted(removed), "edited": sorted(edited)}


def compute_candidate_rollups_output(raw_dataset_path, repo_dir, timeout=180):
    """5.D — correction intake, the regeneration leg.

    Runs the REAL, unmodified rollups.py pipeline against a corrected raw
    dataset (raw_dataset_path), entirely inside an ISOLATED scratch
    directory -- never repo_dir/the live session's working directory --
    so the production rollups_output.xlsx and close_history/ are never
    touched, and the dashboard's already-imported `R` module (and
    whatever period the live session currently has open) is completely
    unaffected. This is "technical regeneration" per 5.F: an internal
    computation, not itself business-facing.

    Does not reimplement rollups.py's logic -- runs the actual file, so
    corrected data goes through the exact same allocation/rollup/tie-out
    logic as any other close, including rollups.py's own internal tie-out
    assertions. A corrected dataset that fails those tie-outs raises
    RuntimeError here rather than silently producing unreliable candidate
    output.

    Returns (candidate_rollups_output_path, stdout_log, scratch_dir).
    Caller is responsible for cleaning up scratch_dir when done with it.
    """
    scratch = tempfile.mkdtemp(prefix="d15_candidate_")
    # rollups.py imports close_history (for dynamic dataset resolution) --
    # copy both so the subprocess can import cleanly with cwd=scratch,
    # writing its own rollups_output.xlsx there, never at repo_dir's path.
    shutil.copyfile(os.path.join(repo_dir, "rollups.py"), os.path.join(scratch, "rollups.py"))
    shutil.copyfile(os.path.join(repo_dir, "close_history.py"), os.path.join(scratch, "close_history.py"))

    env = dict(os.environ)
    env["NORTHWIND_RAW_DATASET_PATH"] = os.path.abspath(raw_dataset_path)

    proc = subprocess.run(
        [sys.executable, "rollups.py"],
        cwd=scratch,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    output_path = os.path.join(scratch, "rollups_output.xlsx")
    if proc.returncode != 0 or not os.path.isfile(output_path):
        raise RuntimeError(
            "Candidate pipeline run failed -- corrected data was not accepted. This is either "
            "a real tie-out failure in the corrected dataset or an execution error; see the log "
            f"below.\n--- stdout (tail) ---\n{proc.stdout[-4000:]}\n--- stderr (tail) ---\n{proc.stderr[-2000:]}"
        )
    return output_path, proc.stdout, scratch


def revalidate_period_from_raw(raw_dataset_path, target_period, quarter_order, R_module, CV_module, prior_expenses=None):
    """5.D — the validation leg (Phase 2/3 re-run against corrected data for
    the reopened period), without going through the full candidate
    rollups.py subprocess run (which is for 5.E's canonical-output
    comparison specifically). Uses R_module.add_fiscal_cols -- the same,
    already-imported, real pipeline function the live dashboard uses --
    rather than reimplementing fiscal-column derivation.

    prior_expenses: the PRIOR APPROVED close's Expenses data (same source
    the live dashboard's own Phase 2 call uses -- the last approved
    close's raw_dataset_path, not the live/current in-session dataset),
    or None (Phase 2's own NOT_APPLICABLE bootstrap case). Passed in by
    the caller rather than defaulted here, so this function never silently
    substitutes the wrong "prior" state.

    Returns (phase2_result, phase3_result).
    """
    xl = pd.ExcelFile(raw_dataset_path)
    corrected_expenses = R_module.add_fiscal_cols(pd.read_excel(xl, "Expenses"))
    corrected_headcount = R_module.add_fiscal_cols(pd.read_excel(xl, "Headcount"))
    corrected_revenue = R_module.add_fiscal_cols(pd.read_excel(xl, "Revenue"))

    phase2_result = CV_module.run_phase2_deterministic_validation(
        current_data=corrected_expenses,
        prior_data=prior_expenses,
    )
    phase3_result = CV_module.run_phase3_plausibility_review(
        expenses=corrected_expenses,
        headcount=corrected_headcount,
        revenue=corrected_revenue,
        period_col="Fiscal Quarter",
        period_order=quarter_order,
        target_period=target_period,
    )
    return phase2_result, phase3_result


# -----------------------------------------------------------------------
# 5.F — technical regeneration / numerical_impact / business-level
# reprocessing_required, kept as three distinct concepts.
#
# The following interpretation is explicitly incorrect per the Brief and
# must never be implementable: "a downstream period was technically
# regenerated, therefore reprocessing_required = true for it." The
# functions below enforce the correct model:
#   - explicit reopen source period: reprocessing_required = True
#     UNCONDITIONALLY (a record of the reopen event, not caused by
#     numerical_impact).
#   - downstream period: reprocessing_required = numerical_impact for
#     that period, EXACTLY -- never independently set, never True merely
#     because regeneration happened.
# -----------------------------------------------------------------------

TRIGGER_EXPLICIT_REOPEN = "explicit reopen"
TRIGGER_PROPAGATED = "propagated"


def reprocessing_required_for_explicit_reopen_source():
    """5.F: always True for the period a user explicitly reopened,
    regardless of that period's own numerical_impact value -- it is a
    lifecycle record of the reopen event itself, not caused by the
    comparison."""
    return True


def reprocessing_required_for_downstream(numerical_impact):
    """5.F: for a downstream (never explicitly reopened) period,
    reprocessing_required is numerical_impact, exactly -- no independent
    setting, no True-by-regeneration-alone."""
    return bool(numerical_impact)


# -----------------------------------------------------------------------
# 5.G — downstream propagation and stopping rule.
# -----------------------------------------------------------------------

class PropagationStep:
    def __init__(self, period_label, numerical_impact, reprocessing_required, trigger, predecessor=None):
        self.period_label = period_label
        self.numerical_impact = numerical_impact
        self.reprocessing_required = reprocessing_required
        self.trigger = trigger  # "explicit reopen" or "propagated from <predecessor period/version>"
        self.predecessor = predecessor

    def to_dict(self):
        return {
            "period_label": self.period_label,
            "numerical_impact": self.numerical_impact,
            "reprocessing_required": self.reprocessing_required,
            "trigger": self.trigger,
            "predecessor": self.predecessor,
        }


def run_propagation_chain(reopened_period, period_order, compare_fn):
    """5.G: for chronological periods P1 (reopened_period) -> P2 -> P3 ->
    P4 ..., walk period_order strictly in order starting immediately after
    reopened_period. At each step, call compare_fn(period_label) ->
    (numerical_impact: bool, predecessor_descriptor: str) for that
    period's own state vs. its own previously-approved state. STOP at the
    first period with numerical_impact=False -- every period after that
    point is never examined, never regenerated (in the business-facing
    sense), never touched. This is exactly the 5.G contract, including the
    terminal-period degrade-to-no-op case (reopened_period is last in
    period_order -> returns just the source step, no propagation attempted)
    and the affected-then-unaffected multi-hop case (propagation must
    continue correctly past an affected period and still be able to stop
    at the next one).

    compare_fn is injected (rather than this function calling
    compare_period_outputs directly) so this function has zero I/O/xlsx
    coupling and is trivially unit-testable with a stub, per this
    project's standing "clean interface, zero I/O" discipline for
    comparison/classification logic (see close_validation.py's own
    documented rationale for the same choice).

    Returns a list[PropagationStep]: index 0 is always the explicit-reopen
    source period itself (reprocessing_required=True unconditionally,
    trigger="explicit reopen"); subsequent entries are downstream periods
    actually examined before the chain stopped.
    """
    steps = [
        PropagationStep(
            period_label=reopened_period,
            numerical_impact=None,  # 5.F: the source's own numerical_impact does not drive its reprocessing_required
            reprocessing_required=reprocessing_required_for_explicit_reopen_source(),
            trigger=TRIGGER_EXPLICIT_REOPEN,
            predecessor=None,
        )
    ]

    idx = period_order.index(reopened_period)
    predecessor_descriptor = reopened_period  # updated to "<period>/v<n>" by the caller's compare_fn as it re-approves

    for downstream in period_order[idx + 1:]:
        numerical_impact, next_predecessor_descriptor = compare_fn(downstream, predecessor_descriptor)
        reprocessing_required = reprocessing_required_for_downstream(numerical_impact)
        steps.append(
            PropagationStep(
                period_label=downstream,
                numerical_impact=numerical_impact,
                reprocessing_required=reprocessing_required,
                trigger=f"{TRIGGER_PROPAGATED} from {predecessor_descriptor}",
                predecessor=predecessor_descriptor,
            )
        )
        if not numerical_impact:
            # 5.G, Step 3: stop. Every subsequent period is never examined.
            break
        # 5.G, Step 4: only once re-approved does this period become the
        # propagated source for the next hop. compare_fn is expected to
        # return the descriptor reflecting that (e.g. "<period>/v2") once
        # its caller has actually driven that period through re-approval;
        # a pure/offline caller (e.g. a regression fixture) may simply
        # return the same downstream label.
        predecessor_descriptor = next_predecessor_descriptor

    return steps


# -----------------------------------------------------------------------
# 5.H — chronological blocking: a read-time check, not a persisted lock.
# -----------------------------------------------------------------------

def find_blocking_predecessor(period_label, period_order, reprocessing_state_by_period):
    """5.H: a period is blocked from closing only while a chronologically
    PRIOR period has reprocessing_required=True and is not yet resolved
    (re-approved at its new version). reprocessing_state_by_period is a
    dict[period_label -> {"reprocessing_required": bool, "resolved": bool}]
    -- the caller supplies this from Close History's actual dependency
    metadata (this function does no I/O itself, same rationale as
    run_propagation_chain).

    Returns the specific blocking predecessor's period_label, or None if
    not blocked. A period that was never in an affected state
    (numerical_impact=False, hence reprocessing_required=False) is never a
    blocker to anything downstream of it -- callers get that for free here
    since such a period's reprocessing_required is already False."""
    if period_label not in period_order:
        return None
    idx = period_order.index(period_label)
    for predecessor in period_order[:idx]:
        state = reprocessing_state_by_period.get(predecessor)
        if not state:
            continue
        if state.get("reprocessing_required") and not state.get("resolved"):
            return predecessor
    return None


# -----------------------------------------------------------------------
# 5.I — lineage/audit evidence shape, passed into
# close_history.archive_close()'s existing extra_metadata hook. No new
# persistence mechanism is introduced -- this only shapes the dict.
# -----------------------------------------------------------------------

def build_lineage_metadata(trigger, predecessor=None, comparison_result=None, proposed_epsilon=PROPOSED_EPSILON, excluded_out_of_period_rows=None):
    """Build the extra_metadata payload D15 adds to a close's snapshot,
    on top of (never replacing) the existing metadata fields Gap 4 already
    writes (pipeline_git_commit_hash, etc.) -- passed as archive_close()'s
    extra_metadata argument, which already merges additively into the
    existing metadata dict (close_history.py: `if extra_metadata:
    metadata.update(extra_metadata)`), so this requires zero signature
    change to archive_close() beyond 5.A's `version` parameter.

    comparison_result: optional dict[output_name -> ComparisonOutputResult]
    from compare_period_outputs(), serialized to per-output before/after
    evidence for the Gate reviewer and for Close Validation Status/Close
    History lineage display (5.I).

    excluded_out_of_period_rows: Addendum 1, Item A's audit-trail
    requirement. Optional list of violation dicts (from
    enforce_period_scoped_correction()'s returned `violations`) -- rows
    the user chose to exclude (Continue) at correction intake. Only
    written when non-empty/non-None, additive, so a candidate with no
    excluded rows produces byte-identical metadata to before this field
    existed.
    """
    payload = {
        "trigger": trigger,  # "explicit reopen" or "propagated from <predecessor period/version>"
        "predecessor": predecessor,
        "epsilon_used": proposed_epsilon,
    }
    if comparison_result is not None:
        payload["numerical_impact_by_output"] = {
            name: r.to_dict() for name, r in comparison_result.items()
        }
        payload["numerical_impact"] = any(r.impact for r in comparison_result.values())
    if excluded_out_of_period_rows:
        payload["excluded_out_of_period_rows"] = excluded_out_of_period_rows
    return payload
