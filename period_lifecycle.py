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

    phase2_result = CV_module.run_phase2_deterministic_validation(
        current_data=corrected_expenses,
        prior_data=prior_expenses,
    )
    phase3_result = CV_module.run_phase3_plausibility_review(
        expenses=corrected_expenses,
        headcount=corrected_headcount,
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

def build_lineage_metadata(trigger, predecessor=None, comparison_result=None, proposed_epsilon=PROPOSED_EPSILON):
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
    return payload
