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

import io
import os
import shutil
import importlib
import numpy as np
import pandas as pd
import streamlit as st

import rollups as R  # noqa: the import itself runs sections 1-14 (all data building)
import close_history
import close_validation as CV  # production Phase 2/3 service — Cycle 3 Task 2
import commentary_workflow as CWF  # Phase 4-6 (D13 scope) — Brief v4
import period_lifecycle as PL  # D15 — period lifecycle, reopen, correction/reprocessing


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


def _close_approval_status_for(period_label):
    """Addendum 3, Item J. Per-period read of the live (non-reopen)
    Human Approval Gate's in-session decision. Replaces the old,
    un-scoped single `close_approval_status` string, which reflected
    whichever period's Approve/Reject button was clicked LAST, for
    whoever it was clicked for -- switching the period selector
    afterward kept showing that stale decision as if it applied to the
    newly-selected period too. Defaults to "not_yet_decided" for a
    period with no in-session action yet, same default as before."""
    return st.session_state.get("close_approval_status_by_period", {}).get(period_label, "not_yet_decided")


def _set_close_approval_status_for(period_label, status):
    """Addendum 3, Item J. Per-period write, paired with
    _close_approval_status_for() above."""
    st.session_state.setdefault("close_approval_status_by_period", {})[period_label] = status


def _fmt_close_order_block_message(blocker, target_period):
    """D15 Items 3 & 4 — renders PL.find_close_order_blocker()'s raw
    result into the exact wording the Brief specifies (Message Wording
    section), applying R.fmt_period_label to every placeholder. The one
    and only place this module builds these two message templates, so
    all three call sites (the 5.B selection early warning and both
    Approve handlers' hard blocks) render identical text for the same
    underlying block."""
    target = R.fmt_period_label(target_period)
    if blocker["reason"] == "control_file_damaged":
        return (
            f"Closing {target} is blocked: a close-order control file in Close History is damaged or "
            f"unreadable, so the close-order state cannot be verified. Repair or restore it, then retry. "
            f"Detail: {blocker.get('detail', 'unknown')}"
        )
    blocking = R.fmt_period_label(blocker["blocking_period"])
    if blocker["reason"] == "never_closed":
        return f"{blocking} is still open. Close it before closing {target}."
    predecessor = R.fmt_period_label(blocker["predecessor"])
    return (
        f"Reopen and close {blocking} before closing {target}. "
        f"Reopening {predecessor} affected {blocking} QoQ."
    )


def _fixk_released_notice_text(released):
    """M11 / D8: the release notice for one released mark
    ({"period", "reopened_period", ...} from close_history.released_pending_marks)."""
    return (
        f"An earlier approval of {R.fmt_period_label(released['reopened_period'])} did not complete; "
        f"no correction was saved and {R.fmt_period_label(released['period'])} is no longer marked."
    )


def _fmt_scope_violation_line(v):
    """One line of the correction-scope violation list (pre-existing text;
    v2.4 A3: the period is shown as 'Q3 2026', never 'Q3 FY2026')."""
    return (
        f"- **{v['sheet']} / {R.fmt_period_label(v['period'])}** {v['key']}"
        + (f" — field `{v.get('field')}`: currently approved = {v.get('approved_value')}, "
           f"uploaded = {v.get('uploaded_value')}"
           if "field" in v else f" — {v['issue']}")
    )


def _fixk_clear_failure_notices(attempt):
    """W3 (brief v2.4, Message Wording; D4): one notice per quarter whose
    outdated flag could not be cleared. Exact approved text, no prefix."""
    out = []
    for c in attempt.get("clear_failures", []):
        q3 = R.fmt_period_label(c["period"])
        out.append({"exact": (
            f"An outdated flag on {q3} could not be cleared ({c['error']}). "
            f"{q3} stays blocked until it is reopened and re-closed."
        )})
    return out


def _fixk_render_notice(notice):
    """A notice is a plain string (shown with the existing 'Close-order
    notice:' prefix) or {"exact": text} (an approved message, shown as is)."""
    if isinstance(notice, dict):
        st.warning(notice["exact"])
    else:
        st.warning(f"Close-order notice: {notice}")


def _fixk_render_failure(reopened_period, attempt):
    """Fix K (M8): render a refused or failed approval. The texts are the
    Principal-approved W1, W2, W4 and W5 of brief v2.4 (Message Wording,
    authoritative); W3 is rendered by _fixk_clear_failure_notices."""
    q2 = R.fmt_period_label(reopened_period)
    if attempt["outcome"] == "refused_marks":
        fails = attempt["failures"]
        if len(fails) == 1:
            # W1 (one quarter).
            st.error(
                f"{q2} was NOT saved. {R.fmt_period_label(fails[0]['period'])} could not be marked as "
                f"outdated ({fails[0]['error']}), so the correction was refused. Fix the cause shown "
                "above (for example folder permissions or disk space) and approve again."
            )
        else:
            # W2 (several quarters, list, oldest first).
            items = "\n".join(f"- {R.fmt_period_label(f['period'])} ({f['error']})" for f in fails)
            st.error(
                f"{q2} was NOT saved. The correction was refused because these quarters could not be "
                f"marked as outdated:\n{items}\n\nFix the cause shown above (for example folder "
                "permissions or disk space) and approve again. The oldest quarter is listed first."
            )
    elif attempt["outcome"] == "save_failed":
        # W4: one message, no claim about flags.
        st.error(
            f"{q2} was NOT saved. The save failed ({attempt['save_error']}). Fix the cause shown above "
            "(for example folder permissions or disk space) and approve again."
        )
    for u in attempt.get("undo_failures", []):
        # W5, once per affected quarter, below W4 when the save failed.
        q3 = R.fmt_period_label(u["period"])
        st.error(
            f"The approval of {q2} did not complete, but a flag for {q3} from this attempt could not be "
            f"undone ({u['detail']}). {q3} stays blocked for narrative and later closes until a later "
            f"approval of {q2} completes, the storage problem is fixed and the mark is released, or "
            f"{q3} is reopened and re-closed. Other tabs still show {q3} figures without any warning."
        )
    for n in _fixk_clear_failure_notices(attempt):
        _fixk_render_notice(n)
    for n in attempt.get("notices", []):
        _fixk_render_notice(n)


def _fixk_list_text(labels):
    """'A', 'A and B', 'A, B and C' (no serial comma), in the order given."""
    if len(labels) <= 1:
        return "".join(labels)
    return ", ".join(labels[:-1]) + " and " + labels[-1]


def _fixk_fallback_notice_text(reopened_period, outcomes):
    """N1 (brief v2.5, Message Wording): the post-save fallback notice.
    Plain text; the display code adds the 'Close-order notice: ' prefix."""
    q2 = R.fmt_period_label(reopened_period)
    marked = [R.fmt_period_label(o["period"]) for o in outcomes if o["outcome"] == "flagged"]
    nosave = [R.fmt_period_label(o["period"]) for o in outcomes if o["outcome"] == "no saved close"]
    if not outcomes:
        return f"{q2} was saved. No later quarter exists, so nothing was marked."
    parts = []
    if marked:
        many = len(marked) > 1
        parts.append(
            f'As a precaution, {_fixk_list_text(marked)} {"are" if many else "is"} marked "may be outdated". '
            f'Reopen and re-close {"them" if many else "it"}{" in that order" if many else ""}.'
        )
    if nosave:
        parts.append(f'{_fixk_list_text(nosave)} {"have" if len(nosave) > 1 else "has"} no saved close, '
                     "so nothing was marked.")
    return f"{q2} was saved. " + " ".join(parts)


def _fixk_bookkeeping_notice_text(reopened_period, failure):
    """N2: one notice per failed follow-up step after a saved approval."""
    q2 = R.fmt_period_label(reopened_period)
    what = ("recording the close order" if failure["step"] == "baseline"
            else f'clearing the "may be outdated" mark on {q2} itself')
    return (f"{q2} was saved. A follow-up step failed: {what} ({failure['error']}). "
            "The saved version is complete.")


def _fixk_success_notices(reopened_period, attempt):
    """Fix K: notices to show after a SAVED approval (failed clears under
    D4 = W3, comparison / check notices N3 and N5 and N4, the fallback
    notice N1, and failed follow-up steps N2 under M9)."""
    out = _fixk_clear_failure_notices(attempt) + list(attempt.get("notices", []))
    fb = attempt.get("fallback_outcomes")
    if fb is not None:
        out.append(_fixk_fallback_notice_text(reopened_period, fb))
    for failure in attempt.get("post_save_failures", []):
        out.append(_fixk_bookkeeping_notice_text(reopened_period, failure))
    return out


def _find_unresolved_reopen_period():
    """Principal-directed extension (post-D15-Items-3&4 delivery, live-
    testing finding): a reopen that has been requested and/or confirmed
    (Step 1/2/3) but neither Approved nor abandoned via "Start over" must
    block Approve-close attempts on any OTHER period, and must block a
    second reopen from being started, until it is resolved.

    The dashboard tracks at most one in-progress reopen at a time -- a
    single session-state slot (`reopen_step` / `reopen_target_period`),
    not one per period -- so at most one period can ever be "still
    reopened" at once under the current design; this can never return
    more than one period, and "the oldest of multiple" is therefore
    moot as long as that remains true. Returns the pending period's
    label, or None if no reopen is currently in progress.
    """
    if st.session_state.get("reopen_step", 0) in (1, 2, 3):
        return st.session_state.get("reopen_target_period")
    return None


def _commentary_record_from_dict(d):
    """Inverse of CommentaryRecord.to_dict() (the writer used by
    CWF.serialize_commentary_records() when a close is archived). Rebuilds the
    complete record -- every version, its validation result, the accepted-version
    marker and the match audit fields -- from a Close History snapshot."""
    rec = CWF.CommentaryRecord(
        observation_id=d["observation_id"],
        accepted_version_number=d.get("accepted_version_number"),
        match_method=d.get("match_method"),
        match_basis=d.get("match_basis"),
    )
    for v in d.get("versions", []):
        vr = v.get("validation_result")
        rec.versions.append(CWF.CommentaryVersion(
            version_number=v["version_number"], text=v["text"], source=v["source"],
            submitted_by=v["submitted_by"], timestamp=v["timestamp"],
            validation_result=CWF.Phase6Result(**vr) if vr is not None else None,
        ))
    return rec


def _archived_commentary_for_period(period_label):
    """Read-back of a CLOSED quarter's observation register and Commentary Record
    from its latest approved Close History snapshot (D10: the immutable record of
    what was approved). Returns (register_df, records_by_observation_id,
    commentary_file_supplied) or None when the period has no saved close.
    Raises if a saved snapshot exists but cannot be read -- the caller reports
    that; it is never silently treated as 'no commentary'.

    commentary_file_supplied is derived from the snapshot itself: a non-empty
    Commentary Record means a commentary file was supplied and matched at least
    one observation. (A file supplied but matched to nothing leaves no record, so
    it cannot be told apart from no file at all -- see Return Report.)"""
    close = close_history.resolve_latest_approved_close_for_period(period_label)
    if close is None:
        return None
    register = pd.read_csv(close["observations_path"])
    raw_records = close["metadata"].get("commentary_record") or {}
    records = {oid: _commentary_record_from_dict(d) for oid, d in raw_records.items()}
    return register, records, bool(records)


def _narrative_gate_block(scope_quarters):
    """AI Narrative tab gate (Principal-directed). Returns None if narrative
    generation / prompt download may be offered for the period(s) in
    `scope_quarters` (the sidebar quarter, or every quarter of the selected
    fiscal year under Annual cadence), otherwise the message to show. In
    priority order a period is blocked when:
      1. a reopen of it is still in progress (started, not approved or
         cancelled): the archived version is about to be superseded;
      2. it is closed but was affected by a later reopen of an earlier
         period and has not itself been reopened and re-closed (its saved
         figures are outdated);
      3. it has no saved close (not approved);
      4. a close-order control file is damaged (state cannot be verified).
    Reads Close History and the reopen session slot only; sets nothing."""
    in_progress = _find_unresolved_reopen_period()
    if in_progress is not None and in_progress in scope_quarters:
        return f"{R.fmt_period_label(in_progress)} Reopen closed period is still in progress."
    damaged = getattr(close_history, "ControlFileError", ())
    for q in scope_quarters:
        try:
            pending = close_history.read_pending_reprocessing(q)
        except damaged as exc:
            return (
                "A close-order control file in Close History is damaged or unreadable, so this "
                f"period's status cannot be verified. Repair or restore it, then retry. Detail: {exc}"
            )
        if pending is not None and not pending.get("resolved", False):
            return (
                f"Reopen and close {R.fmt_period_label(q)}. "
                f"Reopening {R.fmt_period_label(pending['predecessor_period_label'])} "
                f"affected {R.fmt_period_label(q)} QoQ."
            )
    if not scope_quarters or any(
        close_history.resolve_latest_approved_close_for_period(q) is None for q in scope_quarters
    ):
        return (
            "**This close has not been approved.** Executive narrative generation and the prompt "
            "download are unavailable until a human approves this close via the Close Approval "
            "control on the Close Validation Status tab. This applies regardless of Phase 6 "
            "validation results — an adverse or absent assessment does not block approval, and a "
            "favorable one does not substitute for it (D13, Human Approval Gate)."
        )
    return None


def _fmt_unresolved_reopen_block_message(pending_period, action_period, action_verb="closing"):
    """Companion to _fmt_close_order_block_message() above, for the
    separate (non-D15-Brief-scope) unresolved-reopen block. Kept as its
    own message/template rather than folded into
    PL.find_close_order_blocker(), since this check is session-state
    (in-progress UI state), not Close History state -- it has nothing to
    do with period_lifecycle.py's pure, close-history-only logic.
    `action_verb` covers both call shapes: blocking an Approve-close
    attempt ("closing") and blocking a second reopen from starting
    ("reopening")."""
    pending = R.fmt_period_label(pending_period)
    action = R.fmt_period_label(action_period)
    return (
        f"{pending} is still reopened — its reopen has not yet been approved or cancelled. "
        f"Resolve it (approve the candidate close, or \"Start over\") before {action_verb} {action}."
    )


def render_phase2_flagged_table(flagged_rows):
    """Item D (D15-Item2-Corrections Brief): the exact Phase 2 flagged-row
    rendering already used by the Close Validation Status tab's own
    Phase 2 section (Date, Department, Category, Prior Close ($),
    Current Close ($), Diff ($)) -- factored out so the correction-intake
    candidate view can reuse it verbatim rather than a second, divergent
    implementation. No new computation; `flagged_rows` is whatever
    Phase2Result.flagged_rows already is.
    """
    display = flagged_rows[["Date", "Department", "Category", "Amount ($)_prior", "Amount ($)_current", "Diff ($)"]].rename(
        columns={"Amount ($)_prior": "Prior Close ($)", "Amount ($)_current": "Current Close ($)"}
    )
    st.dataframe(display.style.format({"Prior Close ($)": "${:,.2f}", "Current Close ($)": "${:,.2f}", "Diff ($)": "${:,.2f}"}),
                 use_container_width=True)


# Principal-directed fix ("budget should also be integrated"): Phase 2
# (Deterministic Validation) previously only ever checked the Expenses
# sheet. This generalizes it to Revenue, Headcount, and Budget_vs_Actual
# too, reusing close_validation.run_phase2_deterministic_validation()
# unchanged (it is already fully generic over key_cols/value_col -- no
# change to close_validation.py was needed). Kept ADDITIVE to, and
# separate from, the existing Expenses-based `phase2_result` used
# throughout the rest of this tab (Gap 4 flag count, archive_close's
# phase2_flag_count, the reopen candidate pipeline, and
# commentary_workflow.build_observation_register(), which is Expenses-
# schema-specific and Verified/not being reopened here -- see its own
# docstring). These extended results are surfaced as their own dedicated
# section below and folded additively into "any_flags_found" / the
# Workflow State strip, but are NOT (yet) matched against Controller
# commentary the way Phase 2/3's existing Expenses/Headcount/Revenue-QoQ
# flags are -- flagged as an Architect review item in the Return Report,
# not silently decided here.
_EXTENDED_PHASE2_SHEET_SPECS = [
    ("Revenue", ("Date", "Region", "Product Line"), "Revenue ($)"),
    ("Headcount", ("Date", "Department"), "Headcount"),
    ("Budget_vs_Actual (Budget $)", ("Date", "Line Item"), "Budget ($)"),
    ("Budget_vs_Actual (Actual $)", ("Date", "Line Item"), "Actual ($)"),
]


def _run_extended_phase2_coverage(current_revenue, prior_revenue, current_headcount, prior_headcount,
                                   current_bva, prior_bva):
    """Runs CV.run_phase2_deterministic_validation() for Revenue, Headcount,
    and Budget_vs_Actual (both its Budget ($) and Actual ($) value columns),
    against the SAME per-period prior-approved-close baseline the caller
    already resolved for Expenses. Returns an ordered dict of
    {label: Phase2Result}, in the order _EXTENDED_PHASE2_SHEET_SPECS
    defines, so rendering is deterministic.
    """
    current_by_sheet = {
        "Revenue": current_revenue,
        "Headcount": current_headcount,
        "Budget_vs_Actual (Budget $)": current_bva,
        "Budget_vs_Actual (Actual $)": current_bva,
    }
    prior_by_sheet = {
        "Revenue": prior_revenue,
        "Headcount": prior_headcount,
        "Budget_vs_Actual (Budget $)": prior_bva,
        "Budget_vs_Actual (Actual $)": prior_bva,
    }
    results = {}
    for label, key_cols, value_col in _EXTENDED_PHASE2_SHEET_SPECS:
        results[label] = CV.run_phase2_deterministic_validation(
            current_data=current_by_sheet[label],
            prior_data=prior_by_sheet[label],
            key_cols=key_cols,
            value_col=value_col,
        )
    return results


def _render_extended_phase2_coverage(extended_results):
    """Renders _run_extended_phase2_coverage()'s results as one small table
    per sheet, mirroring render_phase2_flagged_table()'s style but generic
    over whatever key_cols that sheet used (Revenue/Headcount/
    Budget_vs_Actual each have a different key shape than Expenses).
    """
    any_ran = any(r.status == CV.STATUS_OK for r in extended_results.values())
    if not any_ran:
        st.info(
            "**Not applicable** — no prior approved close exists yet for this period to diff any of "
            "Revenue, Headcount, or Budget vs Actual against."
        )
        return
    for label, result in extended_results.items():
        if result.status != CV.STATUS_OK:
            continue
        if len(result.flagged_rows) == 0:
            continue
        st.markdown(f"**{label}** — {len(result.flagged_rows)} row(s) changed vs. this period's latest approved close")
        value_col = [c for c in result.flagged_rows.columns if c.endswith("_current")][0][: -len("_current")]
        display_cols = [c for c in result.flagged_rows.columns if c not in (f"{value_col}_prior", f"{value_col}_current", "Diff ($)")]
        display = result.flagged_rows[display_cols + [f"{value_col}_prior", f"{value_col}_current", "Diff ($)"]].rename(
            columns={f"{value_col}_prior": "Prior Close", f"{value_col}_current": "Current Close"}
        )
        st.dataframe(
            display.style.format({"Prior Close": "${:,.2f}", "Current Close": "${:,.2f}", "Diff ($)": "${:,.2f}"}),
            use_container_width=True,
        )
    if all(r.status == CV.STATUS_OK and len(r.flagged_rows) == 0 for r in extended_results.values() if r.status == CV.STATUS_OK):
        st.success("No differences found against the latest approved close for Revenue, Headcount, or Budget vs Actual.")


def _render_commentary_review_records(commentary_records, observation_register, target_period,
                                       validate_new_text=None, close_approval_getter=None,
                                       close_approval_setter=None, read_only=False):
    """Bug/Change 2 fix. The READ display of already-captured commentary --
    observation summary, current commentary text, "Matched via", Phase 6
    result header/reason/cited-evidence-field, and Version History -- shared
    between the not-yet-closed Commentary Review section (read_only=False,
    with Edit/Submit/Accept controls) and the closed-period, read-only
    Commentary Review section (read_only=True: no edit, no accept, and
    critically no import/upload UI at all, since that lives only in the
    not-yet-closed caller).

    Per the reported fix:
      1. No file uploader/import UI here at all -- that remains exclusive
         to the not-yet-closed branch, above this function's only caller
         there.
      2. No "Manually associate with observation" control anywhere --
         removed at its own call site (the Unmatched expander), not
         reproduced here.
      3. The four-metric block (Specific claim? / Checkable? / Supported? /
         Specific enough?) is never rendered here. Version History and
         everything else the expander showed before remains.
    """
    # Principal-directed fix (live-testing session): this "open observation(s)
    # have no matching commentary yet" notice is the ONLY thing in this
    # dashboard that tells the user "something needs your attention" for an
    # observation nobody has commented on yet -- e.g. a reopen-candidate's
    # newly-flagged observation that appeared only after a correction, with
    # zero commentary imported for THIS candidate yet. It must render
    # whenever there are open observations, independent of whether
    # commentary_records happens to be empty.
    #
    # Previously, an early `if not commentary_records: ...; return` sat
    # ABOVE this notice's computation, so it never ran at all whenever
    # commentary_records was completely empty -- which is exactly the state
    # of a freshly-built reopen candidate before any commentary has been
    # uploaded for it. Confirmed live: a corrected Q2 2026 candidate with a
    # genuinely new Phase 3 flag (R&D/Software & Tools) showed only "No
    # commentary imported yet this session" -- no indication a new
    # observation existed at all -- and the close was approved with that
    # observation never offered a chance for commentary. The open-
    # uncommented notice only appeared afterward, on the closed/read-only
    # view, forcing a second reopen just to add the commentary that should
    # have been offered the first time.
    commented_ids = set(commentary_records.keys())
    open_uncommented = (
        observation_register[~observation_register["Observation ID"].isin(commented_ids)]
        if not observation_register.empty else observation_register
    )
    if not open_uncommented.empty:
        st.info(f"{len(open_uncommented)} open observation(s) have no matching commentary yet.")
        _display_open_uncommented = open_uncommented.copy()
        _display_open_uncommented["Period"] = _display_open_uncommented["Period"].apply(R.fmt_period_label)
        # Fix: same $-formatting as every other currency table (was raw floats,
        # e.g. 133623.893); fmt_display_df is the existing shared formatter.
        st.dataframe(fmt_display_df(_display_open_uncommented), use_container_width=True)

    if not commentary_records:
        if open_uncommented.empty:
            # Nothing flagged this period (or -- read-only historical view --
            # every observation that WAS flagged already has commentary
            # recorded elsewhere) and nothing imported: genuinely nothing to
            # review, not a state that needs a "no commentary" caption.
            st.caption("No commentary imported yet this session.")
        return

    for oid, record in commentary_records.items():
        obs_matches = observation_register[observation_register["Observation ID"] == oid]
        if obs_matches.empty or not record.versions:
            continue
        obs_row = obs_matches.iloc[0]
        latest = record.versions[-1]
        status_label = latest.validation_result.assessment if latest.validation_result else "unvalidated"
        with st.expander(
            f"{obs_row['Department']} / {obs_row['Category']} ({R.fmt_period_label(obs_row['Period'])}) — {status_label}",
            expanded=(record.accepted_version_number is None),
        ):
            st.markdown(
                f"**Observation:** {obs_row['Detected By']}, "
                f"${obs_row['Before ($)']:,.2f} → ${obs_row['After ($)']:,.2f} "
                f"(Δ ${obs_row['Delta ($)']:,.2f})"
            )
            st.markdown(f"**Current commentary — version {latest.version_number} ({latest.source}):**")
            st.write(latest.text)
            if record.match_method:
                st.caption(f"Matched via: {record.match_method}")

            if latest.validation_result is not None:
                vr = latest.validation_result
                st.markdown(f"**Phase 6 result: {vr.assessment}**")
                st.caption(vr.reason)
                if vr.cited_field:
                    st.caption(f"Cited evidence field: {vr.cited_field} = {vr.cited_value}")
                # Bug/Change 2, point 3 (corrected): this block is a live-
                # review aid, needed WHILE the period is still open, before
                # closing -- it is suppressed only in the read-only, closed-
                # period view (read_only=True), not in the live one. Point 3,
                # read against its own heading ("Once validated... it must
                # still be displayed with the following change"), is about
                # what the CLOSED view should omit, not the live one.
                if not read_only:
                    tc = st.columns(4)
                    tc[0].metric("1. Specific claim?", "Yes" if vr.check1_specific_claim else "No")
                    tc[1].metric("2. Checkable?", "—" if vr.check2_checkable is None else ("Yes" if vr.check2_checkable else "No"))
                    tc[2].metric("3. Supported?", "—" if vr.check3_supported is None else ("Yes" if vr.check3_supported else "No"))
                    tc[3].metric("4. Specific enough?", "—" if vr.check4_sufficiently_specific is None else ("Yes" if vr.check4_sufficiently_specific else "No"))
                if (not read_only) and vr.assessment == CWF.INSUFFICIENT:
                    st.info(f"For your reference: {CWF.draft_finance_note(phase6_result=vr)}")

            if not read_only:
                revised_text = st.text_area("Edit complete commentary text", value=latest.text, key=f"edit_text_{oid}")
                if st.button("Submit revision & revalidate", key=f"submit_{oid}"):
                    if revised_text.strip() and revised_text.strip() != latest.text.strip():
                        new_result = validate_new_text(revised_text.strip(), obs_row)
                        record.add_version(revised_text.strip(), CWF.SOURCE_USER_REVISION, "finance_cfo_user", new_result)
                        # Human Approval Gate, Section B.6: revising
                        # commentary after this close was already approved
                        # invalidates that approval -- the human approved a
                        # specific set of explanations, and that set just
                        # changed. Reset to not-yet-decided so Phase 7 is
                        # blocked again until the close is re-approved.
                        # No-op if the close wasn't already approved.
                        if close_approval_getter(target_period) == "approved":
                            close_approval_setter(target_period, "not_yet_decided")
                        st.rerun()
                    else:
                        st.warning("No change detected — edit the text before submitting.")

            st.markdown("**Version history**")
            hist_df = pd.DataFrame([{
                "Version": v.version_number, "Source": v.source, "Submitted": v.timestamp,
                "Assessment": v.validation_result.assessment if v.validation_result else "—",
                "Accepted": "✅" if record.accepted_version_number == v.version_number else "",
            } for v in record.versions])
            st.dataframe(hist_df, use_container_width=True)

            if not read_only:
                accept_choice = st.selectbox(
                    "Mark version as Accepted", [v.version_number for v in record.versions],
                    index=len(record.versions) - 1, key=f"accept_select_{oid}",
                )
                if st.button("Mark Accepted", key=f"accept_btn_{oid}"):
                    record.mark_accepted(accept_choice)
                    st.success(f"Version {accept_choice} marked Accepted for this observation.")
                    st.rerun()

    accepted_lines_preview = CWF.accepted_commentary_prompt_lines(
        commentary_records, observation_register, fmt_period_label=R.fmt_period_label
    )
    if accepted_lines_preview:
        st.divider()
        st.caption("Accepted commentary that will flow into the executive narrative (Phase 7, Section G handoff):")
        for line in accepted_lines_preview:
            st.write(line)


def _render_commentary_intake_and_review(commentary_records, observation_register, target_period,
                                         hc_current_df, hc_prior_df, exp_by_dept_cat_df, headcount_band,
                                         uploader_key, semantic_attempted,
                                         close_approval_getter, close_approval_setter,
                                         uploader_label="Commentary.xlsx (optional)",
                                         on_file_supplied=None, carried_file=None):
    """Bug/Change 4. The Commentary Review (Phase 4-6) import + review
    experience, factored out of the not-yet-closed close workflow so the
    reopen-a-closed-period candidate runs EXACTLY the same code, not a
    parallel re-implementation: file upload -> deterministic match ->
    exclusivity -> gated semantic reconciliation -> Phase 6 validation of
    every matched commentary -> Phase 5 finance note for unmatched entries
    -> manual reconciliation -> edit/revalidate -> Accept -> version
    history -> accepted-commentary preview.

    The two callers differ ONLY in the data they hand in:
      * live close: R.hc_dept_q / R.exp_by_dept_cat_q (the loaded dataset)
        and the live period's own Phase 3 headcount band;
      * reopen candidate: the candidate's OWN rollups output and Phase 3
        result, so Phase 6 evidence is checked against the corrected
        numbers, not the previously approved ones.
    `on_file_supplied` is called each render an upload is attached (the
    live close uses it for its Section G "was a file supplied" flag).
    """
    def _dept_category_breakdown_for(obs_row):
        # ALL categories for this department this period (D14), not just the
        # flagged one -- category_reallocation claims (Phase 6) name a
        # DIFFERENT category as the true driver, so checking that requires
        # the full department breakdown, not a single filtered row.
        matches = exp_by_dept_cat_df[
            (exp_by_dept_cat_df["Department"] == obs_row["Department"])
            & (exp_by_dept_cat_df["Fiscal Quarter"] == target_period)
        ]
        return matches if not matches.empty else None

    def _validate_new_text(text, obs_row):
        evidence = CWF.build_evidence_package(
            obs_row, hc_current_df, hc_prior_df,
            dept_category_breakdown=_dept_category_breakdown_for(obs_row),
            headcount_band=headcount_band,
        )
        return CWF.validate_commentary(text, evidence)

    uploaded = st.file_uploader(uploader_label, type=["xlsx"], key=uploader_key)
    # Fix (commentary had to be uploaded twice): `carried_file` is (name, bytes)
    # of a commentary file that was attached when "Run correction intake" reset
    # the uploader. It is processed through the identical pipeline below, so the
    # commentary is re-matched against the rebuilt candidate instead of lost.
    # A file attached in the uploader always takes precedence.
    if uploaded is None and carried_file is not None:
        uploaded = io.BytesIO(carried_file[1])
    if uploaded is not None:
        if on_file_supplied is not None:
            on_file_supplied()
        try:
            commentary_entries = CWF.load_commentary_workbook(uploaded)
        except CWF.CommentaryFileError as e:
            commentary_entries = []
            st.error(f"Commentary file rejected: {e}")

        if commentary_entries and observation_register.empty:
            st.info("Commentary file imported, but there are no open observations this period to match against.")
        elif commentary_entries:
            # Brief v2 Sections 1-3: deterministic pass -> exclusivity ->
            # gated semantic reconciliation, all in one pipeline call.
            #
            # Bug fix (Addendum 4, Item M): this block re-runs on every
            # Streamlit rerun while the uploaded file stays attached to
            # the widget, not just once on the upload itself -- and it
            # always resubmitted the FULL commentary_entries list,
            # unfiltered, to the matcher on every one of those reruns.
            # An entry already resolved this session -- whether
            # auto-matched by CWF.resolve_commentary_matches() itself,
            # or manually associated via the "Confirm manual match"
            # control further below -- was therefore re-evaluated by
            # the matcher again on every subsequent rerun regardless.
            # A manually-resolved entry is the sharper case: it was
            # never confidently auto-matchable in the first place --
            # that is exactly why manual reconciliation was needed --
            # so re-running it through the matcher on every rerun
            # reliably comes back matched=False again, landing it in
            # `unmatched` (rendered below as "Unmatched: ...") even
            # though its resolved version is already sitting in
            # commentary_records, rendering as Supported/Contradicted/
            # Insufficient in the Commentary Review list further down
            # -- the same commentary shown as both at once, regardless
            # of whether it was resolved automatically or manually.
            # Fix: never resubmit an entry that is already resolved --
            # filtered by exact text against every version already
            # stored in commentary_records (not just entries THIS
            # upload produced, and not just entries this pipeline call
            # itself matched: a manually-confirmed entry's text is
            # stored the identical way, via the identical add_version()
            # call, a few lines below the manual-match button -- so
            # this one check covers both resolution paths with no
            # special-casing between them).
            _already_resolved_texts = {
                v.text for rec in commentary_records.values() for v in rec.versions
            }
            _entries_to_resolve = [
                e for e in commentary_entries if e.text not in _already_resolved_texts
            ]
            match_results = (
                CWF.resolve_commentary_matches(
                    _entries_to_resolve, observation_register, commentary_records,
                    semantic_attempted=semantic_attempted,
                )
                if _entries_to_resolve else []
            )
            unmatched = [m for m in match_results if not m.matched]

            for m in match_results:
                if not m.matched:
                    continue
                oid = m.matched_observation_id
                record = commentary_records.get(oid) or CWF.CommentaryRecord(observation_id=oid)
                # Idempotent across reruns: only add the original-import
                # version once per (observation, exact text) pair — a rerun
                # must never duplicate it.
                if not any(v.source == CWF.SOURCE_ORIGINAL_IMPORT and v.text == m.text for v in record.versions):
                    obs_row = observation_register[observation_register["Observation ID"] == oid].iloc[0]
                    result = _validate_new_text(m.text, obs_row)
                    # Audit-trail addendum: record how this commentary was
                    # resolved ("deterministic" or "semantic"), set once at
                    # attachment time, before the first add_version() call.
                    record.match_method = m.method
                    record.match_basis = m.match_basis
                    record.add_version(m.text, CWF.SOURCE_ORIGINAL_IMPORT, "controller_import", result)
                commentary_records[oid] = record

            if unmatched:
                st.warning(
                    f"{len(unmatched)} commentary entr{'y' if len(unmatched) == 1 else 'ies'} could not be "
                    "confidently matched — manual reconciliation below (a dashboard action, not routed to "
                    "the Controller)."
                )
                for m in unmatched:
                    with st.expander(f"Unmatched: {m.commentary_id}"):
                        st.write(m.text)
                        if m.match_basis.startswith(CWF.OCCUPIED_BASIS_PREFIX):
                            st.info(m.match_basis)
                        else:
                            st.caption(CWF.draft_finance_note(no_match_reason=m.match_basis))
                        # Bug/Change 2, point 2 (corrected): the manual
                        # "associate with observation" control stays here
                        # in the LIVE (not-yet-closed) view -- it is the
                        # only way to ever reconcile an entry that
                        # deterministic AND semantic matching both missed
                        # (e.g. no ANTHROPIC_API_KEY configured, so
                        # semantic reconciliation is unavailable).
                        # Point 2 is about the CLOSED, read-only
                        # Commentary Review view, where this control
                        # never rendered in the first place: an
                        # "Unmatched" entry only exists as a byproduct of
                        # processing a freshly-uploaded file THIS
                        # session, inside this same not-yet-closed
                        # upload-handling block -- the closed-period
                        # branch's read display
                        # (_render_commentary_review_records, read_only=
                        # True) only ever iterates already-matched
                        # commentary_records, so an unmatched entry (and
                        # this control) was already absent there, with
                        # zero code change needed for that requirement.
                        # Exclusivity (Brief v2 Section 2): an already-
                        # occupied observation is never offered as a manual
                        # target either -- the manual path is the same
                        # "point where a match is about to be recorded" the
                        # Brief names, so it must enforce the same rule as
                        # the automated paths.
                        _occupied_ids = {o for o, rec in commentary_records.items() if rec.versions}
                        _available_obs = [
                            o for o in observation_register["Observation ID"].tolist()
                            if o not in _occupied_ids
                        ]
                        manual_obs = st.selectbox(
                            "Manually associate with observation (already-commented observations are not offered)",
                            ["(select)"] + _available_obs,
                            key=f"manual_{m.commentary_id}",
                        )
                        if manual_obs != "(select)" and st.button("Confirm manual match", key=f"confirm_{m.commentary_id}"):
                            if manual_obs in _occupied_ids:
                                st.error(
                                    "This observation already has a commentary — consolidate into the "
                                    "existing entry instead of creating a second one."
                                )
                            else:
                                record = commentary_records.get(manual_obs) or CWF.CommentaryRecord(observation_id=manual_obs)
                                obs_row = observation_register[observation_register["Observation ID"] == manual_obs].iloc[0]
                                result = _validate_new_text(m.text, obs_row)
                                # Audit-trail addendum: manual reconciliation
                                # gets its own explicit method label.
                                record.match_method = "manual"
                                record.match_basis = "manually reconciled via Commentary Review"
                                record.add_version(m.text, CWF.SOURCE_ORIGINAL_IMPORT, "controller_import", result)
                                commentary_records[manual_obs] = record
                                st.rerun()

    _render_commentary_review_records(
        commentary_records, observation_register, target_period,
        validate_new_text=_validate_new_text,
        close_approval_getter=close_approval_getter,
        close_approval_setter=close_approval_setter,
        read_only=False,
    )


def _mark_live_commentary_file_supplied():
    """Brief v5 Section G flag for the live close (see its own comment in
    the close workflow): once an upload has been attached this session it
    stays True."""
    st.session_state["commentary_file_supplied"] = True


def _candidate_approval_status_for(_period_label):
    """Bug/Change 4. Reopen-candidate counterpart of
    _close_approval_status_for(), so the shared Commentary Review's Human
    Approval Gate B.6 reset (revising commentary after an approval
    invalidates it) acts on the candidate's own gate."""
    return st.session_state.get("reopen_candidate_approval_status", "not_yet_decided")


def _set_candidate_approval_status_for(_period_label, status):
    st.session_state["reopen_candidate_approval_status"] = status


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
        # D17-BB-001, Section 3 required companion edit: "Top Contributor
        # Share" no longer exists (schema change, not additive -- see
        # Return Report) -- replaced by these two signed-percentage columns.
        # "Gross Variance ($)" is removed entirely (Principal correction,
        # this session) -- net (signed) variance only, no gross column.
        "Top Driver Share of Net Variance": fmt_pct_half,
        "Top Offsetting Share of Net Variance": fmt_pct_half,
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
    # D17-BB-001, Section 4: per-segment source frames matching breadth_df's
    # cadence, for the Phase 7 movement-concentration component detail.
    movement_component_sources = R.MOVEMENT_COMPONENT_SOURCES_Q
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
    movement_component_sources = R.MOVEMENT_COMPONENT_SOURCES_Y
    hc_dept_df, company_rev_df, bva_df = R.hc_dept_y, R.company_rev_per_hc_y, R.bva_y
    opex_per_emp_df = R.opex_per_employee_y
    exp_dept_cat_df = R.exp_by_dept_cat_y
    exp_cat_df = R.exp_by_cat_y

# periods with a prior period available (skip the very first, nothing to compare)
selectable_periods = [p for p in period_order if period_order.index(p) > 0]
current_period = st.sidebar.selectbox(
    "Current period", selectable_periods, index=len(selectable_periods) - 1,
    format_func=R.fmt_period_label,
)
prior_period = period_order[period_order.index(current_period) - 1]
st.sidebar.markdown(f"**Comparison basis:** vs. {R.fmt_period_label(prior_period)}")

# st.line_chart() renders its x-axis as a nominal (string) category and sorts
# it alphabetically, ignoring the DataFrame's row order. That's harmless for
# "Q# FY####" labels (alphabetical == chronological there), but once the
# label is reformatted to "Q# YYYY" for display, alphabetical order breaks
# the year grouping (Q1 2024, Q1 2025, Q1 2026, Q2 2024, ...). Setting the
# index to an ordered Categorical over the true chronological label sequence
# makes the axis ordinal instead of nominal, so it's plotted in that order.
_chrono_labels = [R.fmt_period_label(p) for p in period_order]


def _chrono_index(obj):
    """Reassign obj's index to an ordered Categorical matching period_order's
    chronological sequence, so full-trend st.line_chart() calls plot left-to-
    right in true chronological order instead of alphabetical order."""
    obj.index = pd.Categorical(obj.index, categories=_chrono_labels, ordered=True)
    return obj

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
# Prior-period comparison figures for the four KPI cards: derived from the
# current period's own (closed-at-the-time, frozen) row, so a period that was
# never reopened keeps comparing against its predecessor AS IT WAS when this
# period closed, even if that predecessor was reopened and corrected since
# (see rollups.pl_prior_values).
_pl_prior = R.pl_prior_values(pl_df, period_col, current_period, prior_period)

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
prior_rev = _pl_prior["revenue"] if _pl_prior is not None else None
prior_opex = _pl_prior["opex"] if _pl_prior is not None else None
prior_profit = _pl_prior["op_profit"] if _pl_prior is not None else None
prior_margin = _pl_prior["margin"] if _pl_prior is not None else None

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
        if cadence == "Quarterly":
            pivot = pivot.rename(index=R.fmt_period_label)
        st.line_chart(_chrono_index(pivot))
    with col2:
        st.subheader("Revenue by Product Line — full trend")
        chart_df2 = R.revenue.groupby(["Product Line", period_col if cadence == "Quarterly" else "Fiscal Year"], as_index=False)["Revenue ($)"].sum()
        pivot2 = chart_df2.pivot(index=period_col if cadence == "Quarterly" else "Fiscal Year", columns="Product Line", values="Revenue ($)")
        pivot2 = pivot2.reindex(period_order)
        if cadence == "Quarterly":
            pivot2 = pivot2.rename(index=R.fmt_period_label)
        st.line_chart(_chrono_index(pivot2))

    st.subheader(f"Revenue Mix (%) — {R.fmt_period_label(current_period)}")
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

    st.subheader(f"Revenue detail — {R.fmt_period_label(current_period)} vs {R.fmt_period_label(prior_period)}")
    rev_var_cols = ["QoQ/YoY Variance ($)", "QoQ/YoY Variance (%)", "YoY Variance ($)", "YoY Variance (%)"]
    rev_region_display = rev_region_df[rev_region_df[period_col] == current_period].copy()
    rev_product_display = rev_product_df[rev_product_df[period_col] == current_period].copy()
    if cadence == "Quarterly":
        rev_region_display[period_col] = rev_region_display[period_col].map(R.fmt_period_label)
        rev_product_display[period_col] = rev_product_display[period_col].map(R.fmt_period_label)
    st.dataframe(style_variance_df(rev_region_display,
                                    higher_is_good_cols=rev_var_cols), use_container_width=True)
    st.dataframe(style_variance_df(rev_product_display,
                                    higher_is_good_cols=rev_var_cols), use_container_width=True)

with tab_exp:
    st.subheader("Expenses by Department — full trend")
    exp_chart = R.expenses.groupby(["Department", period_col], as_index=False)["Amount ($)"].sum()
    pivot3 = exp_chart.pivot(index=period_col, columns="Department", values="Amount ($)").reindex(period_order)
    if cadence == "Quarterly":
        pivot3 = pivot3.rename(index=R.fmt_period_label)
    st.bar_chart(_chrono_index(pivot3))

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
    st.subheader(f"Department × Cost Type — Investigation View ({R.fmt_period_label(current_period)} vs {R.fmt_period_label(prior_period)})")
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
    st.subheader(f"Cost Category — Company-Wide View ({R.fmt_period_label(current_period)} vs {R.fmt_period_label(prior_period)})")
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

    st.subheader(f"Salaries & Benefits Volume/Rate Bridge — {R.fmt_period_label(current_period)}")
    sb_cost_cols = ["Headcount Change", "Cost-per-Head Change ($)", "Volume Effect ($)",
                    "Rate Effect ($)", "Bridge Total ($)", "Actual Variance ($)"]
    sb_display = sb_df[sb_df[period_col] == current_period].copy()
    if cadence == "Quarterly":
        sb_display[period_col] = sb_display[period_col].map(R.fmt_period_label)
    st.dataframe(style_variance_df(sb_display,
                                    higher_is_bad_cols=sb_cost_cols), use_container_width=True)
    st.caption("Volume effect = change in headcount x prior period cost-per-head. Rate effect = new headcount x change in cost-per-head. Volume + Rate = Actual Variance exactly.")

    st.subheader(f"Breadth / Concentration — {R.fmt_period_label(current_period)}")
    breadth_display = breadth_df[breadth_df[period_col] == current_period].copy()
    if cadence == "Quarterly":
        breadth_display[period_col] = breadth_display[period_col].map(R.fmt_period_label)
    st.dataframe(style_breadth_df(breadth_display), use_container_width=True)
    st.caption(
        "Threshold: for Revenue rows, a single segment driving >=60% of net (signed) variance is flagged "
        "Concentrated; for Expenses rows (Total / Category / Department, all sharing Total Expenses' own "
        "net variance as denominator and sign reference), the threshold is >=17%. An opposing segment "
        "carrying >=20% of net variance is flagged as substantially offsetting, for both. No gross-variance "
        "figure is used anywhere in this table (Principal correction, D17-BB-001)."
    )

    st.subheader(f"Opex per Employee by Department — {R.fmt_period_label(current_period)}")
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
    if cadence == "Quarterly":
        pivot4 = pivot4.rename(index=R.fmt_period_label)
    st.line_chart(_chrono_index(pivot4))

    st.subheader(f"Headcount by Department — {R.fmt_period_label(current_period)} vs {R.fmt_period_label(prior_period)}")
    hc_dept_display = hc_dept_df[hc_dept_df[period_col] == current_period].copy()
    if cadence == "Quarterly":
        hc_dept_display[period_col] = hc_dept_display[period_col].map(R.fmt_period_label)
    st.dataframe(fmt_display_df(hc_dept_display), use_container_width=True)

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
    if cadence == "Quarterly":
        trend = trend.rename(index=R.fmt_period_label)
    st.line_chart(_chrono_index(trend))

with tab_bva:
    st.subheader(f"Budget vs Actual — {R.fmt_period_label(current_period)}")
    bva_current = bva_df[bva_df[period_col] == current_period]
    bva_display = bva_current.copy()
    if cadence == "Quarterly":
        bva_display[period_col] = bva_display[period_col].map(R.fmt_period_label)

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

    bva_styler = bva_display.style.format(_base_format_map(bva_display), na_rep="").apply(_bva_row_color, axis=1)
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

    # -------------------------------------------------------------------
    # D15, Section 5.B — Authoritative period selection (absorbs Gap 1).
    #
    # This is the SOLE source of `target_period` for the close workflow —
    # a distinct control from the sidebar/explorer period selector above,
    # which remains display-only for the other eight IA pages and must
    # never independently determine the close target. No downstream
    # component in this tab may re-derive the period from period_order[-1],
    # the sidebar's current_period, or any other alternate path — every
    # existing internal derivation this tab previously used
    # (Phase 3's target_period default, the evidence package's
    # current_period/prior_period, archive_close()'s period_label) now
    # reads target_period, defined here, once.
    # -------------------------------------------------------------------
    _close_selectable_periods = [p for p in R.quarter_order if R.quarter_order.index(p) > 0]
    # Item K: single merged control, replacing the two separate dropdowns
    # ("Select period to close" / "Previously closed period to reopen").
    # Offers the same period universe as before (index 0 excluded -- no
    # "prior" period exists for it to validate/compare against, same
    # restriction the close workflow always had; unchanged by this item).
    target_period = st.selectbox(
        "Select period",
        _close_selectable_periods,
        index=len(_close_selectable_periods) - 1,
        format_func=R.fmt_period_label,
        key="target_period_to_close",
        help=(
            "Drives Phase 2/3 validation, the observation register, Phase 6 evidence, and which "
            "period is archived on approval — independent of the sidebar's 'Current period' "
            "selector above, which only changes the comparison basis shown on the other dashboard "
            "pages. An already-closed period shows the reopen workflow instead (Item K)."
        ),
    )
    _target_period_idx = R.quarter_order.index(target_period)
    target_prior_period = R.quarter_order[_target_period_idx - 1] if _target_period_idx > 0 else None

    # Addendum 3, Item K/J shared check: is this period already
    # durably closed? Drives Item K's top-level branching (close
    # workflow vs. reopen-only) and is reused, unmodified, by Item J's
    # own internal Gate check below.
    _target_period_closed_info = close_history.resolve_latest_approved_close_for_period(target_period)

    # D15 Items 3 & 4 -- early warning only (informational; the
    # authoritative, hard-blocking re-check runs again inside both Approve
    # handlers below, immediately before archive_close(), since the two
    # checks can observe different Close History states if time passes
    # between selection and Approve). Procedural only: never sets, clears,
    # or implies Workflow State, Executive Ready, or any other Human
    # Approval Gate (D13) criterion -- this is a caption, nothing else.
    for _notice in st.session_state.get("close_order_notices", []):
        _fixk_render_notice(_notice)
    # Fix K (M11 / D8, Principal decision): a mark released because its
    # approval never saved is NOT silent. Shown here until the Controller
    # dismisses it; dismissal is per browser session only (it changes no
    # mark, no file and no other reader).
    _dismissed_released = st.session_state.setdefault("released_mark_notices_dismissed", set())
    _visible_released = [
        _r for _r in close_history.released_pending_marks(R.quarter_order)
        if (_r["period"], _r["attempt_id"]) not in _dismissed_released
    ]
    for _r in _visible_released:
        st.warning(_fixk_released_notice_text(_r))
    if _visible_released and st.button("Dismiss", key="dismiss_released_mark_notices_btn"):
        _dismissed_released.update((_r["period"], _r["attempt_id"]) for _r in _visible_released)
        st.rerun()
    _close_order_blocker = PL.find_close_order_blocker(target_period, R.quarter_order, close_history)
    if _close_order_blocker is not None:
        st.warning(_fmt_close_order_block_message(_close_order_blocker, target_period))

    st.caption(
        f"This tab validates, generates observations for, and (on approval) archives "
        f"**{R.fmt_period_label(target_period)}** — the period selected above, not the sidebar's "
        "'Current period' selector, which only changes the current/prior comparison basis for the "
        "other dashboard pages (Revenue Performance, Cost Structure, Regional/Product Investment, "
        "Headcount & Efficiency, Budget vs Actual). It has no effect on Phase 2/3, the observation "
        "register, Commentary Review, or which period gets archived here."
    )

    # --- Resolve the TARGET PERIOD's own latest approved close from real
    # Close History, and run close_validation.py's production Phase 2/3
    # functions against it. This is the module swap for Cycle 3 Task 2: no
    # import of, and no data from, close_v1_v2_simulation.py anywhere in
    # this tab. Phase 2 compares the currently-loaded close (R.expenses)
    # against the prior approved state (None if this period has never been
    # closed before -- the real Live state today, per Handbook Section 7:
    # "Live's own Close History starts empty"). Phase 3 evaluates the
    # currently-loaded close's own quarterly history and needs no prior
    # approved close to run.
    #
    # Principal-directed fix (aligned in session: "the intake must only
    # affect the period which is reopened" / two-tier sourcing): this call
    # previously used close_history.resolve_latest_approved_close() -- the
    # GLOBAL latest approved close by approval timestamp across every
    # period in Close History, not this period's own prior state. That is
    # the exact same defect class already fixed for Executive Ready above
    # (see the D15 Item 2 correction 3 comment) and for the reopen
    # candidate's own Phase 2 call (_run_candidate_pipeline, "this period's
    # OWN prior approved close, never the global latest") -- it was simply
    # never applied to this call site. Using the global latest meant
    # approving an unrelated period's close (or a reopened HISTORICAL
    # period's v2) could silently swap in the wrong baseline here,
    # producing a Phase 2 diff against a period that has nothing to do with
    # target_period. resolve_latest_approved_close_for_period(target_period)
    # is the correct, already-established fix for this shape of bug.
    resolved_prior_close = close_history.resolve_latest_approved_close_for_period(target_period)
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

    # Extended Phase 2 coverage (Principal-directed: "budget should also be
    # integrated"), additive only -- Revenue, Headcount, and
    # Budget_vs_Actual, using the SAME per-period baseline
    # (resolved_prior_close, now correctly period-scoped above) instead of
    # the Expenses-only check that previously existed. Kept entirely
    # separate from `phase2_result` (which stays Expenses-only, unchanged
    # in shape) rather than merged into it, because build_observation_register()
    # and every existing consumer of phase2_result (Gap 4 flag count,
    # archive_close's phase2_flag_count, the reopen candidate pipeline) are
    # written against Expenses' own column shape (Department/Category) --
    # Revenue (Region/Product Line) and Budget_vs_Actual (Line Item) don't
    # fit that shape, and build_observation_register's Phase 2 branch is a
    # Verified, already-investigated piece of the system (see its own
    # "Observation Register Period Semantics" docstring) not being reopened
    # here. See _run_extended_phase2_coverage() below and its own docstring
    # for the full rationale and what is/isn't wired into Commentary Review.
    prior_revenue_df = prior_headcount_df = prior_bva_df = None
    if resolved_prior_close is not None:
        prior_revenue_df = pd.read_excel(resolved_prior_close["raw_dataset_path"], "Revenue")
        prior_revenue_df["Date"] = pd.to_datetime(prior_revenue_df["Date"])
        prior_headcount_df = pd.read_excel(resolved_prior_close["raw_dataset_path"], "Headcount")
        prior_headcount_df["Date"] = pd.to_datetime(prior_headcount_df["Date"])
        prior_bva_df = pd.read_excel(resolved_prior_close["raw_dataset_path"], "Budget_vs_Actual")
        prior_bva_df["Date"] = pd.to_datetime(prior_bva_df["Date"])

    extended_phase2_results = _run_extended_phase2_coverage(
        current_revenue=R.revenue, prior_revenue=prior_revenue_df,
        current_headcount=R.headcount, prior_headcount=prior_headcount_df,
        current_bva=R.bva, prior_bva=prior_bva_df,
    )
    phase3_result = CV.run_phase3_plausibility_review(
        expenses=R.expenses,
        headcount=R.headcount,
        # OI-10 (D15-Item2-Corrections Brief, Item C): Phase 3 now also
        # covers Revenue QoQ variance (Total, Region, Product Line), at
        # the same 25% threshold already governing Expenses.
        revenue=R.revenue,
        period_col="Fiscal Quarter",
        period_order=R.quarter_order,
        # D15, Section 5.B: explicit target_period from the single
        # "Select period to close" control above — no longer defaulting to
        # period_order[-1] implicitly, and never re-derived from the
        # sidebar's current_period.
        target_period=target_period,
    )

    if resolved_prior_close is not None:
        close_status_caption = (
            f"Autonomous CFO Office, Phases 0-3, run by close_validation.py against the currently-loaded close "
            f"vs. the latest APPROVED close in Close History ('{R.fmt_period_label(resolved_prior_close['period_label'])}'). "
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
    any_extended_phase2_flags = any(
        r.status == CV.STATUS_OK and len(r.flagged_rows) > 0 for r in extended_phase2_results.values()
    )
    # Principal directive (2026-09-29): Phase 2 findings -- both the base
    # Expenses check above and the extended Revenue/Headcount/Budget vs
    # Actual coverage -- no longer generate Observation IDs or enter the
    # Commentary Review register (see build_observation_register()'s
    # docstring). A Phase 2 row is a raw-data diff against the prior
    # approved close, not something a Controller can narrate. "Awaiting
    # Controller Input" must track only what the Commentary Review section
    # can actually act on, so no Phase 2 flag count (base or extended)
    # feeds it here; phase2_ran/phase2_result.flagged_rows and
    # extended_phase2_results remain fully reported elsewhere (Workflow
    # state's "Data Validated" caption and the dedicated Phase 2 sections
    # below) unchanged.
    any_flags_found = phase3_result.status == CV.STATUS_OK and len(phase3_result.flagged_rows) > 0

    # Human Approval Gate (Brief human_approval_gate_brief_v1.md), Section
    # B.4: the two rows below must reflect real computed state, not the
    # hardcoded False that previously sat here unconditionally. Both
    # booleans are computed here, ahead of the Commentary Review section's
    # own build of the same observation register further down this tab, so
    # the strip reflects the CURRENT rerun's state rather than a stale
    # value. build_observation_register() is a pure function of
    # phase2_result/phase3_result (already computed above) with no side
    # effects, so recomputing it here is safe and does not duplicate any
    # stateful logic -- see the Commentary Review section for the
    # authoritative build used for matching/display.
    _status_strip_observation_register = CWF.build_observation_register(
        phase2_result, phase3_result, R.fmt_period_label, CV.STATUS_OK
    )
    _status_strip_commentary_records = st.session_state.get("commentary_records", {})
    if _status_strip_observation_register.empty:
        # Nothing was ever flagged this close -- Phase 6 has nothing to do,
        # so "Explanations Validated" is trivially satisfied.
        explanations_validated = True
    else:
        _commented_ids = set(_status_strip_commentary_records.keys())
        _open_uncommented_ids = set(_status_strip_observation_register["Observation ID"]) - _commented_ids
        explanations_validated = (
            len(_open_uncommented_ids) == 0
            and all(
                rec.versions and rec.versions[-1].validation_result is not None
                for rec in _status_strip_commentary_records.values()
            )
        )
    # Human Approval Gate, Section B.1/D: the close's approval status is a
    # distinct, explicit human action (approve/reject buttons, Commentary
    # Review section) -- never inferred from Phase 6 assessment outcomes.
    # "Executive Ready" is real only once that explicit action has set this
    # to "approved". Addendum 3, Item J: per-period via
    # _close_approval_status_for()/_set_close_approval_status_for() --
    # see their own docstrings for why the un-scoped single flag this
    # replaced was a real defect.
    # Gap 4, Item 3: "Executive Ready" must reflect that the approval was
    # made DURABLE (archive_close() succeeded and the close is retrievable
    # from Close History) -- not merely that the in-session flag was set.
    # If Item 1's archive call errored (1d) or simply hasn't fired yet on
    # this rerun, the strip must not claim the close is durably complete.
    #
    # D15 Item 2, correction 3: uses resolve_latest_approved_close_FOR_PERIOD
    # (target_period), never resolve_latest_approved_close() -- the latter
    # ranks by approval_timestamp GLOBALLY across every period in Close
    # History, so approving a reopened HISTORICAL period's v2 (Item 2)
    # would otherwise become "the latest approved close" by timestamp and
    # silently flip this unrelated target_period's own Executive Ready
    # status to False. See close_history.resolve_latest_approved_close_for_period()
    # for the full rationale.
    _gap4_durable_close = close_history.resolve_latest_approved_close_for_period(target_period)
    executive_ready = (
        _close_approval_status_for(target_period) == "approved"
        and _gap4_durable_close is not None
        and _gap4_durable_close["period_label"] == target_period
    )

    states = [
        ("Close Received", "Phase 0", True),
        ("Data Validated", "Phase 2 complete" if phase2_ran else "Phase 2 not applicable (no prior close)", True),
        ("Observations Generated", "Phase 3 complete", phase3_result.status == CV.STATUS_OK),
        ("Awaiting Controller Input", "unexplained items exist" if any_flags_found else "no items awaiting explanation", any_flags_found),
        ("Explanations Validated", "Phase 6 complete", explanations_validated),
        ("Executive Ready", "human approval gate passed", executive_ready),
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
        render_phase2_flagged_table(phase2_result.flagged_rows)
        if len(phase2_result.flagged_rows) == 0:
            st.success("No differences found against the latest approved close.")
        else:
            st.warning(f"{len(phase2_result.flagged_rows)} row(s) changed vs. the latest approved close — see table above.")

    st.markdown("**Phase 2 — extended coverage: Revenue / Headcount / Budget vs Actual**")
    st.caption(
        "Same deterministic diff as above, extended to Revenue, Headcount, and Budget vs Actual "
        "(Principal-directed: previously Expenses-only). Compared against this same period's own prior "
        "approved close. Not yet matched against Controller commentary in the observation register below "
        "(Architect review item — see Return Report); shown here for visibility."
    )
    _render_extended_phase2_coverage(extended_phase2_results)

    st.divider()
    st.subheader(f"Phase 3 — Plausibility Review (current close, {R.fmt_period_label(phase3_result.target_period) or 'latest period'} only)")
    st.caption(
        f"{R.fmt_period_label(phase3_result.target_period) or 'The latest period'} has no prior-approved-close counterpart to diff against under "
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
    st.subheader("Observation register")
    st.caption(
        "Built here in the dashboard from close_validation.py's returned structured results — the production "
        "module itself never writes an observation register or any other artifact; that's caller-side, same as "
        "any CSV/report output. 'Observation ID' is a stable, deterministic key "
        "(commentary_workflow.make_observation_id) that Phase 4 commentary matching resolves against — "
        "re-running Phase 2/3 against the same close does not change it."
    )
    observation_register = CWF.build_observation_register(phase2_result, phase3_result, R.fmt_period_label, CV.STATUS_OK)
    if observation_register.empty:
        st.success("No observations this run — register is empty.")
    else:
        # Phase 7 period-display addendum (addendum to
        # phase6_headcount_direction_fix_brief_v1.md): apply R.fmt_period_label
        # at this render point, on a display-only copy. Under current
        # canonical build_observation_register() behavior the register's
        # Period field is already fmt_period_label() output, so this is a
        # safe no-op today (fmt_period_label is documented idempotent on
        # already-formatted strings) -- it hardens this render point against
        # any future change to what the register stores, without changing
        # today's displayed values. The underlying observation_register
        # variable used for matching/keying below is never mutated.
        _display_register = observation_register.copy()
        _display_register["Period"] = _display_register["Period"].apply(R.fmt_period_label)
        st.dataframe(fmt_display_df(_display_register), use_container_width=True)

    # Bug/Change 2 fix: commentary_records must be visible to BOTH branches
    # below. The Commentary Review READ display (observation -> commentary
    # -> Matched via -> Phase 6 result -> Version History) is no longer
    # gated behind "not yet closed" -- it keeps rendering, read-only, once
    # the period is durably closed too (see the `else` branch further
    # down). Only the import/matching UI (the uploader, and everything
    # that depends on a freshly-uploaded file) remains exclusive to the
    # not-yet-closed branch immediately below.
    if "commentary_records" not in st.session_state:
        st.session_state["commentary_records"] = {}  # observation_id -> CWF.CommentaryRecord
    commentary_records = st.session_state["commentary_records"]

    if _target_period_closed_info is None:
        # -----------------------------------------------------------------------
        # Commentary Review — Phase 4 (Commentary Matching), Phase 5 (Finance
        # Collaboration, reinterpreted as a self-reference draft for the
        # finance/CFO user), Phase 6 (Explanation Validation). Governed by
        # governance/builder_briefs/phase4_6_commentary_validation_brief_v4.md.
        # Additive: does not touch any D10/D11/D12/D14 logic above.
        #
        # Session-scoped state only — the Commentary Record (Brief Section F) is
        # working-state data before close approval; it is copied into the
        # immutable D10 Close History snapshot at close approval via
        # close_history.archive_close(commentary_record=...), demonstrated in
        # build_test/commentary_workflow_demo.py. The live Human Approval Gate
        # control (an actual "approve this close" st.button) remains
        # separately-scoped open technical debt (Handbook Section 10) — this
        # section does not add one, per the Brief's explicit out-of-scope list.
        # -----------------------------------------------------------------------
        st.divider()
        st.subheader("Commentary Review (Phase 4-6)")
        st.caption(
            "Import the Controller's Commentary.xlsx (sheet 'Commentary', columns Commentary_ID + "
            "Commentary_Text only — no observation ID, status, or AI field in the input file). The Controller "
            "never operates this dashboard; only the finance/CFO user reviews, edits, and accepts commentary here. "
            "This file is OPTIONAL (Brief v5) — the dashboard, financial analysis, and executive narrative all "
            "work correctly with no commentary file at all; flagged observations are simply reported as "
            "identified-but-unexplained in that case (see the AI Narrative tab)."
        )

        # Brief v5, Section A/B/K: Commentary.xlsx is now OPTIONAL. Whether a
        # file was ever supplied this close is tracked independently of the
        # file_uploader widget's current value, because Streamlit's uploader can
        # report None on a later rerun (e.g. widget state edge cases) even after
        # a file was genuinely supplied earlier this session -- Section G's
        # three-way narrative handoff needs a durable "was one supplied at all"
        # answer for this close, not just "is one attached to the widget right
        # now." Once True for this session, it stays True (a close doesn't un-
        # supply a commentary file mid-review).
        if "commentary_file_supplied" not in st.session_state:
            st.session_state["commentary_file_supplied"] = False

        # D15, Section 5.B (absorbs Gap 1's evidence-package period-sourcing
        # defect): these are keyed to target_period — the period this tab is
        # actually validating and will archive — never to the sidebar's
        # current_period/prior_period. R.hc_dept_q / R.exp_by_dept_cat_q are
        # used explicitly (quarterly grain) rather than the cadence-toggled
        # hc_dept_df/exp_dept_cat_df, because Phase 3 (and therefore this
        # tab's observation register) always operates at quarterly grain
        # regardless of the sidebar's Quarterly/Annual cadence radio — using
        # the cadence-toggled frames here would silently break whenever the
        # radio is set to Annual, independent of the sidebar period issue.
        hc_current_df = R.hc_dept_q[R.hc_dept_q["Fiscal Quarter"] == target_period][["Department", "Ending Headcount"]]
        hc_prior_df = (
            R.hc_dept_q[R.hc_dept_q["Fiscal Quarter"] == target_prior_period][["Department", "Ending Headcount"]]
            if target_prior_period is not None
            else R.hc_dept_q.iloc[0:0][["Department", "Ending Headcount"]]
        )

        # Brief v2 (phase4_semantic_reconciliation_brief_v2.md) Section 5a /
        # Criterion 10a: a set of commentary_id values already attempted for
        # semantic reconciliation THIS session (matched, or already tried and
        # failed). Backed by st.session_state so a Streamlit rerun -- which
        # re-executes this whole script -- never triggers a second semantic
        # call for the same commentary just because the script reran.
        if "semantic_reconciliation_attempted" not in st.session_state:
            st.session_state["semantic_reconciliation_attempted"] = set()
        semantic_attempted = st.session_state["semantic_reconciliation_attempted"]

        # Addendum 3, Item G (extended to the live uploader): a separate
        # generation counter, incremented once on a successful live "Approve
        # close" (see the Gate handler below), so this uploader resets to
        # empty rather than continuing to show the already-processed file
        # after a close is approved. Independent of the reopen flow's own
        # `reopen_uploader_generation` counter -- these are two different
        # flows and resetting one must not touch the other.
        _live_commentary_uploader_gen = st.session_state.get("live_commentary_uploader_generation", 0)
        # Bug/Change 4: the whole upload -> match -> validate -> review flow
        # (formerly inline here) now lives in
        # _render_commentary_intake_and_review(), shared verbatim with the
        # reopen-a-closed-period candidate.
        _render_commentary_intake_and_review(
            commentary_records, observation_register, target_period,
            hc_current_df=hc_current_df, hc_prior_df=hc_prior_df,
            exp_by_dept_cat_df=R.exp_by_dept_cat_q,
            headcount_band=phase3_result.headcount_band,
            uploader_key=f"commentary_uploader_{_live_commentary_uploader_gen}",
            semantic_attempted=semantic_attempted,
            close_approval_getter=_close_approval_status_for,
            close_approval_setter=_set_close_approval_status_for,
            on_file_supplied=_mark_live_commentary_file_supplied,
        )

        # ---------------------------------------------------------------------
        # Human Approval Gate (Brief human_approval_gate_brief_v1.md), Section
        # B.2/B.5/B.7. Two distinct, explicit human actions -- approve and
        # reject/return. Per D13 ("Machine Recommends, Human Decides") and
        # Section B.5, the approve control's availability must NOT depend on
        # any Phase 6 assessment (Supported/Contradicted/Insufficient) or on
        # whether commentary exists at all -- an adverse or missing assessment
        # is a flag for the human, never a block on the human's own
        # discretion. This is why these two buttons sit outside the
        # `if not commentary_records:` branch above (which only gates the
        # display of commentary review content, not this gate) and are always
        # rendered, every rerun, at the end of Commentary Review section.
        # ---------------------------------------------------------------------
        st.divider()
        st.subheader("Close Approval — Human Approval Gate")
        # Addendum 3, Item J: derive this period's TRUE state from Close
        # History directly, every render, rather than trusting the raw
        # in-session flag alone -- reuses the exact call already correct for
        # the "Executive Ready" row above. A durably closed period is shown
        # as such, with no live Approve/Reject offered for it (requirement
        # 1) -- this becomes practically unreachable in the UI once Item K
        # lands (its own top-level conditional keeps a closed period from
        # reaching this whole close-workflow branch at all), but is kept
        # here because Item J is independently specified and acceptance-
        # tested (J2/J3) on its own terms, and it is the exact check Item
        # K's branching relies on.
        _gate_durable_close = close_history.resolve_latest_approved_close_for_period(target_period)
        if _gate_durable_close is not None:
            st.info(
                f"**{R.fmt_period_label(target_period)} is already closed** — archived as "
                f"v{_gate_durable_close['metadata'].get('version', 1)} on "
                f"{_gate_durable_close['metadata'].get('approval_timestamp', 'an earlier date')}. "
                "See the historical-close view (Gap 2) to review it. To correct it, use "
                "\"Reopen closed period\" below."
            )
        else:
            _approval_status = _close_approval_status_for(target_period)
            _status_display = {
                "not_yet_decided": "⬜ Not yet decided",
                "approved": "✅ Approved",
                "rejected": "❌ Rejected / returned",
            }[_approval_status]
            st.markdown(f"**Current status:** {_status_display}")
            # Addendum 3, Item J, requirement 3: an equality check against
            # target_period, not mere truthiness -- a caption left over from
            # a DIFFERENT period's most recent action can never be shown
            # while target_period is selected.
            if st.session_state.get("last_archive_error") == target_period:
                st.error(
                    f"This period ('{R.fmt_period_label(target_period)}') is "
                    "already archived in Close History — approval status is set, but no new snapshot was "
                    "written. See the historical-close view (Gap 2) to review the existing archived record."
                )
            elif st.session_state.get("last_archived_close_period") == target_period and _approval_status == "approved":
                st.caption(
                    f"Archived to Close History as '{R.fmt_period_label(target_period)}' "
                    "this session."
                )
            st.caption(
                "This action is independent of Phase 6's assessment of any individual commentary item. "
                "An Insufficient or Contradicted result (or no commentary at all) is a flag for you to "
                "review, not a block on your discretion to approve, reject, or request further "
                "clarification (D13)."
            )
            gate_cols = st.columns(2)
            with gate_cols[0]:
                if st.button("Approve close", key="approve_close_btn"):
                    # Section D: available in every state, including re-affirming
                    # an already-approved close. The "approved" status itself is
                    # recorded further down, only AFTER both blocking checks
                    # (close-order, unresolved reopen) have passed -- a blocked
                    # attempt must leave the approval status untouched.
                    # ---------------------------------------------------------
                    # Gap 4 (builder_brief_operability_gap4_close_durability.md),
                    # Item 1: make this approval durable by calling
                    # close_history.archive_close() -- previously this button did
                    # nothing but flip a session-state flag, so no approved close
                    # was ever recorded outside the current browser session. This
                    # fires exactly once per genuine "Approve close" click (never
                    # as a side effect of an unrelated rerun where the flag
                    # already happens to be "approved") and targets the single
                    # authoritative `target_period` set by the "Select period to
                    # close" control above (D15, Section 5.B — absorbs Gap 1 and
                    # Gap 4's Item 2 into one flow) -- never period_order[-1]
                    # (which is cadence-dependent and not necessarily a quarter
                    # when the sidebar cadence is Annual) and never the sidebar's
                    # `current_period`.
                    #
                    # This button always archives at version=1 -- it is a normal,
                    # first-time close of target_period, not a reopen/correction.
                    # D15's versioned-correction path (Sections 5.C-5.D, a
                    # two-step reopen producing v2+) is separate, not-yet-built
                    # scope; this handler must not invent an uncontrolled
                    # alternate way to reach version 2, so a period already
                    # archived at v1 still surfaces Item 1d's message below,
                    # exactly as before this control existed.
                    # ---------------------------------------------------------
                    _gap4_period_label = target_period
                    _gap4_commentary_records = st.session_state.get("commentary_records", {})
                    _gap4_phase2_flag_count = (
                        len(phase2_result.flagged_rows) if phase2_result.status == CV.STATUS_OK else 0
                    )
                    _gap4_phase3_flag_count = (
                        len(phase3_result.flagged_rows) if phase3_result.status == CV.STATUS_OK else 0
                    )
                    _gap4_prior_close = close_history.resolve_latest_approved_close()
                    # D15 Items 3 & 4 -- hard, authoritative close-order /
                    # reopen-propagation check, immediately before
                    # archive_close() runs (the 5.B selection control above
                    # is only an early warning; this is the re-check the
                    # Brief requires at Approve time). Procedural only -- this
                    # check runs BEFORE _set_close_approval_status_for(...,
                    # "approved") below, so a blocked attempt never sets,
                    # clears, or implies any Human Approval Gate (D13)
                    # criterion (acceptance criterion 7).
                    _close_order_blocker = PL.find_close_order_blocker(_gap4_period_label, R.quarter_order, close_history)
                    if _close_order_blocker is not None:
                        st.error(_fmt_close_order_block_message(_close_order_blocker, _gap4_period_label))
                        st.stop()
                    # Principal-directed extension: an unresolved reopen (Step
                    # 1/2/3, not yet Approved or Started over) anywhere blocks
                    # Approve-close everywhere else, until it's resolved --
                    # checked here, hard, immediately before archive_close(),
                    # same as the close-order check above. Independent of
                    # _close_order_blocker: this is session in-progress-UI
                    # state, not Close History state.
                    _unresolved_reopen = _find_unresolved_reopen_period()
                    if _unresolved_reopen is not None:
                        st.error(_fmt_unresolved_reopen_block_message(_unresolved_reopen, _gap4_period_label))
                        st.stop()
                    # Both blocking checks passed: only now record the
                    # explicit human approval (same value, same per-period
                    # setter as before -- merely moved after the checks).
                    _set_close_approval_status_for(target_period, "approved")
                    try:
                        close_history.archive_close(
                            period_label=_gap4_period_label,
                            raw_dataset_src=R.RAW,
                            rollups_output_src="rollups_output.xlsx",
                            observations_df=observation_register,
                            # Phase 7 narrative generation is gated behind this
                            # same approval and happens as a separate, later user
                            # action (it cannot have run yet at the moment this
                            # click fires) -- reflect that honestly rather than
                            # inventing narrative text. If a narrative or a
                            # downloaded-prompt fallback was produced earlier in
                            # this session for any reason, use it; otherwise this
                            # is legitimately empty, and archive_close() writes
                            # narrative.txt as an empty file, not a placeholder.
                            narrative_text=st.session_state.get("phase7_narrative_text", ""),
                            phase2_flag_count=_gap4_phase2_flag_count,
                            phase3_flag_count=_gap4_phase3_flag_count,
                            workflow_state="Executive Ready",
                            prior_close_period_label=(
                                _gap4_prior_close["period_label"] if _gap4_prior_close is not None else None
                            ),
                            commentary_record=CWF.serialize_commentary_records(_gap4_commentary_records),
                        )
                        st.session_state["last_archived_close_period"] = _gap4_period_label
                        st.session_state["last_archive_error"] = None
                        # D15 Items 3 & 4 -- bootstrap rule: a no-op unless
                        # this is genuinely the very first close ever under
                        # this rule (close_history/_baseline.json absent),
                        # in which case this close's own period becomes the
                        # permanent baseline, written exactly once.
                        close_history.establish_close_order_baseline_if_absent(_gap4_period_label)
                        # Item B (D15-Item2-Corrections Brief, OI-9/OI-12): force
                        # rollups.py to re-resolve before the next render, so
                        # Close Validation Status/Phase 2/3 and every other tab
                        # reflect the just-archived close without a manual
                        # restart. Module-level state otherwise loads once at
                        # Streamlit startup and is never refreshed by st.rerun()
                        # alone.
                        importlib.reload(R)
                        # Item G (Addendum 3, G7): reset the live Commentary
                        # Review uploader on a successful approve.
                        st.session_state["live_commentary_uploader_generation"] = (
                            st.session_state.get("live_commentary_uploader_generation", 0) + 1
                        )
                    except FileExistsError:
                        # Item 1d: this exact period is already archived (this
                        # session or a prior one). Do not overwrite, version, or
                        # silently no-op -- surface a clear, specific message.
                        # D10's immutability is preserved exactly as-is.
                        st.session_state["last_archive_error"] = _gap4_period_label
                    st.rerun()
            with gate_cols[1]:
                if st.button("Reject / return close", key="reject_close_btn"):
                    # Section B.7: no reason required. No-op in substance if
                    # already rejected (still explicitly sets rejected, per
                    # Section D's table) or not-yet-decided. The existing Phase 6
                    # revision loop (commentary edit + resubmit, above) is the
                    # path back toward re-approval -- this Brief does not add a
                    # separate return-reason mechanism.
                    _set_close_approval_status_for(target_period, "rejected")
                    st.rerun()

    # -------------------------------------------------------------------
    # Addendum 3, Item K: the merged "Select period" control above
    # (formerly two separate dropdowns -- "Select period to close" and
    # "Previously closed period to reopen") branches here on the same
    # durable-close check Item J introduced. Not yet closed -> the close
    # workflow above (Phase 2/3, Commentary Review, Close Approval Gate).
    # Already closed -> ONLY the reopen section below; none of the close
    # workflow renders for an already-closed period.
    # -------------------------------------------------------------------
    else:
        # ---------------------------------------------------------------
        # Bug/Change 2 fix: Commentary Review must NOT disappear once the
        # period is durably closed -- it continues to render here,
        # read-only:
        #   1. No import/upload UI (no new commentary can be imported
        #      against an archived, immutable close).
        #   2. No "manually associate with observation" control anywhere
        #      (that control was removed entirely at its call site, above,
        #      not merely hidden here).
        #   3. No four-metric block (Specific claim? / Checkable? /
        #      Supported? / Specific enough?) -- Version History and
        #      everything else the expander showed for the live period
        #      is retained.
        # Uses the same session-scoped commentary_records this session
        # captured before approval; it does not read back the archived
        # snapshot's own persisted Commentary Record (that is Gap 2's
        # separate, read-only historical-navigation scope).
        # ---------------------------------------------------------------
        st.divider()
        st.subheader("Commentary Review (Phase 4-6)")
        st.caption(
            f"**{R.fmt_period_label(target_period)} is closed.** Showing the commentary captured before "
            "approval, read-only — no new commentary can be imported for an archived close."
        )
        _render_commentary_review_records(
            commentary_records, observation_register, target_period,
            read_only=True,
        )

        # -------------------------------------------------------------------
        # D15, Section 5.C — Reopen a previously closed period (two-step,
        # cancel/abandon-safe transactional boundary).
        #
        # Scope note: this section implements 5.C (the reopen transaction
        # itself) only. 5.D (correction intake: accepting new/corrected source
        # data and new commentary, producing a candidate version) is NOT YET
        # IMPLEMENTED -- see the message shown after Step 2 confirmation below.
        # Per the Brief, NEITHER screen writes to close_history/ under any
        # circumstance; only a future 5.D implementation would produce a
        # persisted (still not-yet-approved) candidate version, and even that
        # is never written until Human Approval Gate sign-off (5.J, unchanged).
        # -------------------------------------------------------------------
        st.divider()
        # Item K, requirement: header renamed exactly as specified.
        st.subheader("Reopen closed period")

        # Item K: target_period IS the period to reopen -- the merged
        # dropdown above already guarantees, by construction (the branch
        # condition), that it's an already-closed period. No separate
        # "Previously closed period to reopen" selectbox needed anymore.
        if "reopen_step" not in st.session_state:
            st.session_state["reopen_step"] = 0  # 0 = not started, 1 = Step 1 shown, 2 = confirmed
        if "reopen_target_period" not in st.session_state:
            st.session_state["reopen_target_period"] = None

        # Principal-directed extension: the state machine below
        # (reopen_step / reopen_target_period) is a single, global slot --
        # not one per period. Before this guard, switching the "Select
        # period" control to a DIFFERENT already-closed period while a
        # reopen was still in progress (Step 1/2/3, not yet Approved or
        # Started over) kept rendering that OTHER, unrelated period's
        # Step 1/2/3 content here -- because the branches below key
        # entirely off reopen_target_period, never off target_period. This
        # guard makes the in-progress period authoritative for what
        # renders: any other closed period shows a block notice (and
        # cannot start its own reopen) instead of stale/mismatched Step
        # 1/2/3 content, until the in-progress one is resolved.
        _reopen_pending_elsewhere = (
            st.session_state["reopen_step"] in (1, 2, 3)
            and st.session_state["reopen_target_period"] is not None
            and st.session_state["reopen_target_period"] != target_period
        )

        if _reopen_pending_elsewhere:
            st.error(
                _fmt_unresolved_reopen_block_message(
                    st.session_state["reopen_target_period"], target_period, action_verb="reopening"
                )
            )

        elif st.session_state["reopen_step"] == 0:
            if st.button("Request reopen", key="reopen_request_btn"):
                st.session_state["reopen_step"] = 1
                st.session_state["reopen_target_period"] = target_period
                st.rerun()

        elif st.session_state["reopen_step"] == 1:
            _rp = st.session_state["reopen_target_period"]
            _latest = close_history.resolve_latest_approved_close()
            _idx = R.quarter_order.index(_rp) if _rp in R.quarter_order else -1
            _downstream = R.quarter_order[_idx + 1:] if _idx >= 0 else []
            st.warning(
                f"**Step 1 — Consequence review for {R.fmt_period_label(_rp)}**\n\n"
                f"- Current approved version: v{_latest['metadata'].get('version', 1) if _latest else '?'}\n"
                f"- Reopening will involve new/corrected data and/or commentary (the dataset saved in "
                f"Close History is kept if no new one is imported), re-validation, and "
                f"re-approval through the Human Approval Gate before anything is archived.\n"
                f"- Chronologically downstream periods that could be affected if this correction "
                f"changes {R.fmt_period_label(_rp)}'s canonical state: "
                f"{', '.join(R.fmt_period_label(p) for p in _downstream) if _downstream else '(none — terminal period)'}\n"
                f"- **Nothing is written to Close History at this step.** No persistent state change "
                "occurs until Step 2 is explicitly confirmed."
            )
            _c1, _c2 = st.columns(2)
            with _c1:
                if st.button("Cancel", key="reopen_step1_cancel_btn"):
                    st.session_state["reopen_step"] = 0
                    st.session_state["reopen_target_period"] = None
                    st.rerun()
            with _c2:
                if st.button("Continue to final confirmation", key="reopen_step1_continue_btn"):
                    st.session_state["reopen_step"] = 2
                    st.rerun()

        elif st.session_state["reopen_step"] == 2:
            _rp = st.session_state["reopen_target_period"]
            st.error(
                f"**Step 2 — Final confirmation**\n\n"
                f"Confirming will begin correction intake for {R.fmt_period_label(_rp)}. The prior "
                "approved version remains untouched and immutable (D10) regardless of what happens "
                "next."
            )
            _c1, _c2 = st.columns(2)
            with _c1:
                if st.button("Cancel", key="reopen_step2_cancel_btn"):
                    st.session_state["reopen_step"] = 0
                    st.session_state["reopen_target_period"] = None
                    st.rerun()
            with _c2:
                if st.button("Confirm reopen", key="reopen_step2_confirm_btn"):
                    # 5.C ends here. Confirming records ONLY session state
                    # (no close_history/ write of any kind) and hands off to
                    # 5.D (correction intake) below.
                    st.session_state["reopen_step"] = 3
                    # Bug/Change 3: step 3 below builds the candidate straight
                    # away from the dataset saved in this period's own Close
                    # History entry (state-driven, see `_auto_build_now`).
                    # Clear any build error left by an earlier attempt so
                    # this confirmed reopen gets a fresh attempt.
                    st.session_state["reopen_candidate_build_error"] = None
                    st.rerun()

        elif st.session_state["reopen_step"] == 3:
            _rp = st.session_state["reopen_target_period"]
            st.info(
                f"Reopen confirmed for {R.fmt_period_label(_rp)} (session state only — no Close "
                "History write has occurred yet)."
            )

            # -----------------------------------------------------------
            # D15, Section 5.D — Correction intake and reprocessing.
            #
            # Accepts a corrected raw dataset for the reopened period, runs
            # it through the REAL rollups.py pipeline in an isolated
            # scratch directory (never touching the live session's data or
            # production files -- see period_lifecycle.compute_candidate_rollups_output),
            # re-runs Phase 2/3 against the corrected data for target
            # period `_rp`, and performs the Section 5.E numerical-impact
            # comparison of the candidate's six canonical outputs against
            # THIS PERIOD'S OWN previously-approved version (D15 Item 2
            # fix, below -- not the global latest approved close, which
            # would compare against an unrelated period whenever one
            # exists).
            #
            # Explicitly NOT covered by this pass: candidate Commentary
            # intake through Phase 4-6, and 5.G's live downstream
            # propagation walk (period_lifecycle.run_propagation_chain is
            # implemented and independently unit-tested, but is not yet
            # driven from this UI across multiple periods in one click).
            # -----------------------------------------------------------
            import tempfile as _tempfile

            def _run_candidate_pipeline(_scoped_raw_path, _violations, _cleanup_dirs, source_file_id=None):
                """Shared by both the no-conflict-immediate path and the
                post-Continue path (Addendum 1, Item A) so the candidate-
                build logic exists in exactly one place. `_violations` is
                Item A's audit trail (possibly empty); `_cleanup_dirs` is
                every scratch directory this call is responsible for
                removing once done, regardless of outcome.

                Addendum 3, Item H: this function COMPUTES and STORES the
                candidate's results into st.session_state["reopen_candidate"]
                only -- it renders NOTHING itself. A separate, unconditional
                block (after the uploaders, below) reads that stored state
                and renders the summary/diff every rerun, not just the one
                triggered by this button click. Previously the summary was
                rendered here directly, inside a button-click branch that
                only evaluates True on the exact rerun of the click itself
                -- and since this function also calls st.rerun() at the end
                (Item G), that summary was in practice being discarded
                before ever reaching the user, the same rerun that was
                supposed to show it also replacing it. Item H fixes the
                root cause, not just the symptom.
                """
                _candidate_scratch = None
                try:
                    _candidate_path, _candidate_log, _candidate_scratch = PL.compute_candidate_rollups_output(
                        _scoped_raw_path, repo_dir=os.path.dirname(os.path.abspath(__file__))
                    )

                    # D15 Item 2 fix: this period's OWN prior approved
                    # close, never the global latest -- same rationale as
                    # the Executive Ready fix above
                    # (close_history.resolve_latest_approved_close_for_period).
                    _prior_close = close_history.resolve_latest_approved_close_for_period(_rp)
                    _prior_expenses_for_candidate = None
                    if _prior_close is not None:
                        _prior_expenses_for_candidate = pd.read_excel(
                            _prior_close["raw_dataset_path"], "Expenses"
                        )
                        _prior_expenses_for_candidate["Date"] = pd.to_datetime(
                            _prior_expenses_for_candidate["Date"]
                        )

                    _cand_phase2, _cand_phase3 = PL.revalidate_period_from_raw(
                        _scoped_raw_path, _rp, R.quarter_order, R, CV,
                        prior_expenses=_prior_expenses_for_candidate,
                    )

                    if _prior_close is None:
                        st.session_state["reopen_candidate_build_error"] = (
                            f"No previously-approved close exists for {R.fmt_period_label(_rp)} "
                            "itself to compare the candidate against -- 5.E's numerical-impact "
                            "comparison requires this period's own prior approved snapshot."
                        )
                        return

                    _numerical_impact, _comparison = PL.compare_period_outputs(
                        _rp, _prior_close["rollups_output_path"], _candidate_path
                    )

                    # Item E (D15-Item2-Corrections Addendum 1): the
                    # candidate's own observation register, built now so
                    # the commentary-entry step below can match against
                    # it -- the SAME inputs (and therefore the same
                    # register) archive_close() will rebuild at approval
                    # time.
                    _candidate_obs_register = CWF.build_observation_register(
                        _cand_phase2, _cand_phase3, R.fmt_period_label, CV.STATUS_OK
                    )

                    # D15 Item 2: persist the corrected dataset and the
                    # candidate's rollups_output.xlsx in a session-scoped
                    # temp location that survives past this rerun --
                    # referenced from st.session_state["reopen_candidate"],
                    # cleaned up only once the candidate is resolved
                    # (approved or reset), never here.
                    _persist_dir = _tempfile.mkdtemp(prefix="d15_candidate_persist_")
                    _persisted_raw_path = os.path.join(_persist_dir, "corrected_dataset.xlsx")
                    shutil.copyfile(_scoped_raw_path, _persisted_raw_path)
                    _persisted_rollups_path = os.path.join(_persist_dir, "rollups_output.xlsx")
                    shutil.copyfile(_candidate_path, _persisted_rollups_path)

                    # Addendum 3, Item I: preserve previously-captured
                    # candidate commentary across a re-run of "Run
                    # correction intake" for the SAME reopened period
                    # (e.g. re-running after adjusting the corrected
                    # dataset). Only starts fresh ({}) when there is no
                    # prior candidate in session state, or the prior
                    # candidate was for a DIFFERENT period -- switching
                    # which period you're reopening must never carry
                    # commentary across.
                    _existing_cand = st.session_state.get("reopen_candidate")
                    if _existing_cand is not None and _existing_cand.get("period") == _rp:
                        _carried_commentary_records = _existing_cand.get("commentary_records", {})
                        _carried_semantic_attempted = _existing_cand.get("semantic_attempted", set())
                        # The old persist_dir's on-disk files are no longer
                        # referenced by the new candidate about to replace
                        # it -- clean it up now rather than leaking it
                        # (mirrors the cleanup already done on Approve).
                        if _existing_cand.get("persist_dir"):
                            shutil.rmtree(_existing_cand["persist_dir"], ignore_errors=True)
                    else:
                        _carried_commentary_records = {}
                        _carried_semantic_attempted = set()

                    # Fix: keep a commentary file that is attached at the moment
                    # of intake. The uploader is cleared by this very click
                    # (Addendum 2 G1) and a file attached BEFORE intake was only
                    # ever matched against the OLD candidate -- often one with
                    # no observations -- so it was silently lost. A file carried
                    # by the prior candidate for the same period is kept too.
                    _attached_commentary = st.session_state.get(
                        f"candidate_commentary_uploader_{st.session_state.get('reopen_uploader_generation', 0)}"
                    )
                    if _attached_commentary is not None:
                        _carried_commentary_file = (_attached_commentary.name, _attached_commentary.getvalue())
                    elif _existing_cand is not None and _existing_cand.get("period") == _rp:
                        _carried_commentary_file = _existing_cand.get("carried_commentary_file")
                    else:
                        _carried_commentary_file = None

                    st.session_state["reopen_candidate"] = {
                        "period": _rp,
                        "numerical_impact": _numerical_impact,
                        "comparison": _comparison,
                        "phase2_result": _cand_phase2,
                        "phase3_result": _cand_phase3,
                        "observation_register": _candidate_obs_register,
                        "raw_dataset_path": _persisted_raw_path,
                        "rollups_output_path": _persisted_rollups_path,
                        "persist_dir": _persist_dir,
                        # Item A audit trail (Addendum 1): the rows
                        # excluded at intake, if any -- persisted into
                        # archive_close()'s extra_metadata on approval,
                        # not just shown once and discarded.
                        "excluded_out_of_period_rows": _violations,
                        # Item E (Addendum 1) / Item I (Addendum 3):
                        # {observation_id -> CWF.CommentaryRecord}.
                        # Carried forward from the prior candidate for
                        # this same period (Item I) or fresh ({}) for a
                        # new period / first build.
                        "commentary_records": _carried_commentary_records,
                        # Bug/Change 4: same per-close "already attempted"
                        # set the live Commentary Review keeps in session
                        # state, so a rerun never re-calls semantic
                        # reconciliation for a commentary already tried.
                        "semantic_attempted": _carried_semantic_attempted,
                        "carried_commentary_file": _carried_commentary_file,
                        # Principal-directed fix (live-testing session):
                        # (name, size) of the uploaded file this candidate
                        # was actually built from, or None when it was
                        # built from the saved/approved dataset (no file
                        # attached at build time, or a commentary-only
                        # correction). Compared against whatever file
                        # currently sits in the uploader by the Approve
                        # handler below, so an unprocessed or since-
                        # replaced attachment can never be silently
                        # approved as if it were this candidate.
                        "source_file_id": source_file_id,
                    }
                    # A newly (re)computed candidate always starts
                    # undecided -- never inherits a stale
                    # approved/rejected status from a prior candidate for
                    # this same period.
                    st.session_state["reopen_candidate_approval_status"] = "not_yet_decided"
                    st.session_state["reopen_candidate_build_error"] = None

                    # Item G (Addendum 2/3): both reopen uploaders reset
                    # after a successful intake (immediate path AND the
                    # post-Continue path both route through here, so one
                    # bump covers both reset points at once). Safe now
                    # that Item I preserves commentary independently of
                    # the commentary uploader staying attached.
                    st.session_state["reopen_uploader_generation"] = (
                        st.session_state.get("reopen_uploader_generation", 0) + 1
                    )
                    st.rerun()
                except RuntimeError as _err:
                    st.session_state["reopen_candidate_build_error"] = str(_err)
                finally:
                    for _d in _cleanup_dirs + [_candidate_scratch]:
                        if _d:
                            shutil.rmtree(_d, ignore_errors=True)

            # Addendum 3, Item H: unconditional rendering of the most
            # recently built candidate's own build-time messaging
            # (success/violation-excluded note) or build error, read from
            # session state rather than rendered transiently inside the
            # button handler above. The per-output impact summary and
            # full line-item diff (also Item H) are rendered further
            # below, inside the persistent "if reopen_candidate in
            # session_state" block, alongside Item E's commentary section
            # -- one persistent block, not two.
            if st.session_state.get("reopen_candidate_build_error"):
                # Bug/Change 6: never dump the raw pipeline log at the user.
                # The plain-language sentence is shown; the subprocess
                # stdout/stderr (if any) is kept for support in an expander.
                _be_head, _be_sep, _be_tail = st.session_state["reopen_candidate_build_error"].partition("--- stdout")
                st.error(_be_head.strip())
                if _be_sep:
                    with st.expander("Technical details"):
                        st.code(_be_sep + _be_tail)

            # Item G (D15-Item2-Corrections Addendum 2): a single shared
            # generation counter, incremented at each of the five reset
            # points (successful intake, Cancel, successful Approve,
            # Reject, Start over) -- both reopen file_uploaders derive
            # their widget key from it, so bumping the counter is
            # Streamlit's standard way to force a fresh, empty uploader
            # rather than leaving the previous file attached.
            _uploader_gen = st.session_state.get("reopen_uploader_generation", 0)

            _corrected_file = st.file_uploader(
                "Corrected raw dataset (.xlsx, same shape as the canonical dataset) — optional; if none is "
                "attached, the dataset saved in this period's Close History entry is kept",
                type=["xlsx"],
                key=f"reopen_corrected_dataset_upload_{_uploader_gen}",
            )
            # Principal-directed fix (live-testing session), identity of
            # whatever file currently sits in the uploader -- used below
            # both to build the candidate (when "Run correction intake" is
            # actually clicked) and, separately, to detect a STALE
            # candidate that does not reflect this file (see the Approve
            # handler's own guard further down). (name, size) is a cheap,
            # good-enough fingerprint -- this only needs to distinguish
            # "same attachment as when the candidate was built" from
            # "something has changed since," not cryptographically
            # verify content.
            _current_upload_id = (
                (_corrected_file.name, _corrected_file.size) if _corrected_file is not None else None
            )

            # Addendum 1, Item A (REVISED): a pending out-of-period
            # conflict, surfaced but not yet resolved by the user via
            # Continue/Cancel. Scoped to THIS reopened period only --
            # switching target periods mid-flow does not carry a stale
            # pending conflict from a different period forward.
            _scope_pending = st.session_state.get("correction_scope_pending")
            _scope_pending_here = _scope_pending is not None and _scope_pending.get("period") == _rp

            # Bug/Change 6: the moment a file is attached it is reviewed for
            # compatibility -- (1) is it a dataset file, (2) are all the
            # dataset's categories (sheets) there, (3) is there data for the
            # period being reopened -- and the first failure is explained
            # right here, under the uploader, while the file is still
            # attached. "Run correction intake" is only offered for a file
            # that passed, so a wrong or corrupted file can never reach the
            # candidate pipeline and produce its technical traceback.
            _upload_check = None
            if _corrected_file is not None:
                _upload_check = PL.validate_correction_upload(_corrected_file.getvalue(), _rp, R)
                if not _upload_check.ok:
                    st.error(_upload_check.message)

            # Addendum 3, Item L, as changed by Bug/Change 3: the dataset
            # upload is optional, and no longer gates the Candidate
            # commentary step. Whenever this reopen is active and no
            # candidate exists yet for it (and no earlier attempt has
            # failed, and no scope conflict is awaiting Continue/Cancel),
            # intake runs automatically against the reopened period's
            # own currently-approved dataset, kept exactly as saved in
            # Close History -- derived from session state on every render
            # rather than a one-shot click flag, so it cannot be missed
            # (e.g. a reopen already in progress when the app reloaded)
            # and never repeats once a candidate exists or a build has
            # failed (the failure is shown; Start over retries). Item A's existing
            # scoping/reconstruction logic already handles a fully-
            # identical workbook correctly (zero violations, zero
            # in-period diff), so this reuses that path rather than
            # adding a second one. The candidate, and with it the
            # Candidate commentary section, therefore exists straight
            # away, so a commentary-only correction can proceed to
            # Approve without ever touching the dataset -- Item F's guard
            # still requires a genuine change (numeric or commentary)
            # before allowing a new version. "Run correction intake" is
            # offered only once a replacement dataset is attached, so it
            # can never silently revert a previously-applied corrected
            # dataset back to the saved one (Start over does that,
            # explicitly).
            _existing_cand_for_build = st.session_state.get("reopen_candidate")
            # Principal-directed fix (live-testing session): a file
            # currently attached in the uploader must NEVER be silently
            # skipped by the auto-build below. Before this fix,
            # _auto_build_now fired the moment no candidate existed yet
            # for this period -- including on the very rerun that
            # attaching a file itself triggers, before the user has had
            # any chance to click "Run correction intake." Auto-build
            # always sources the SAVED/approved dataset, never the
            # uploader's contents, so that race silently built a candidate
            # from the unchanged saved data, discarding the just-attached
            # file -- with only a build-summary banner
            # ("numerical_impact = False") as a hint, easy to miss. If the
            # user then clicked "Approve candidate close," the pre-existing
            # zero-net-change guard (Item F) saw no genuine change and
            # auto-cancelled the whole reopen -- so the file was discarded
            # and the reopen abandoned, with nothing in the UI clearly
            # explaining either. Requiring `_corrected_file is None` here
            # means: with a file attached, no candidate is auto-built at
            # all -- the user must explicitly click "Run correction
            # intake" (already shown right below, unconditionally, once a
            # file is attached) before any candidate -- and therefore
            # before "Approve candidate close" -- can appear. Removing the
            # attached file (uploader's own "X") restores the prior
            # auto-build-from-saved-data behavior for a commentary-only
            # correction, unchanged.
            _auto_build_now = (
                not _scope_pending_here
                and _corrected_file is None
                and (_existing_cand_for_build is None or _existing_cand_for_build.get("period") != _rp)
                and not st.session_state.get("reopen_candidate_build_error")
            )
            _run_intake_clicked = False
            if not _scope_pending_here and _corrected_file is not None and _upload_check.ok:
                # Principal-directed fix, paired with the _auto_build_now
                # change above: make explicit, every render a file sits
                # here unprocessed, that nothing has been done with it
                # yet -- rather than leaving the button as the only signal.
                st.info(
                    f"**{_corrected_file.name}** is attached but has not been applied yet. Click "
                    "**Run correction intake** below to build the candidate from it -- until then, "
                    "no candidate exists for this reopen and nothing can be approved."
                )
                _run_intake_clicked = st.button("Run correction intake", key="reopen_run_correction_btn")
            # The auto-build never reads the uploader: it always uses the
            # saved dataset. A click always uses the attached file.
            _intake_file = _corrected_file if _run_intake_clicked else None
            if not _scope_pending_here:
                if _auto_build_now or _run_intake_clicked:
                    with st.spinner("Checking correction scope against currently-approved data..."):
                        _tmp_dir = _tempfile.mkdtemp(prefix="d15_upload_")
                        _tmp_raw_path = os.path.join(_tmp_dir, "corrected_dataset.xlsx")
                        if _intake_file is not None:
                            with open(_tmp_raw_path, "wb") as _f:
                                _f.write(_intake_file.getvalue())
                        else:
                            # Bug/Change 3 (was Item L): no new dataset --
                            # source the reopened period's own currently-
                            # approved raw dataset, as saved in its Close
                            # History entry, as the intake input. Every
                            # row is, by definition, identical to itself,
                            # so enforce_period_scoped_correction() below
                            # reports zero violations and the in-period
                            # comparison naturally shows numerical_impact
                            # = False.
                            _own_approved_close = close_history.resolve_latest_approved_close_for_period(_rp)
                            if _own_approved_close is None:
                                st.session_state["reopen_candidate_build_error"] = (
                                    f"No currently-approved data exists for {R.fmt_period_label(_rp)} to "
                                    "keep as the saved dataset for this correction."
                                )
                                shutil.rmtree(_tmp_dir, ignore_errors=True)
                                _tmp_raw_path = None
                                st.rerun()
                            else:
                                shutil.copyfile(_own_approved_close["raw_dataset_path"], _tmp_raw_path)

                        if _tmp_raw_path is not None:
                            try:
                                # Item A (D15-Item2-Corrections Brief, OI-8;
                                # REVISED by Addendum 1 to warn-and-exclude):
                                # detection runs unconditionally, before any
                                # candidate is built. It never raises -- it
                                # always returns the scoped/reconstructed
                                # workbook AND the list of detected
                                # violations (possibly empty). A non-empty
                                # list means at least one out-of-period row
                                # differs from that period's own approved
                                # value; per Addendum 1 this is now shown to
                                # the user as a warning with an explicit
                                # Continue/Cancel choice (5.C's own pattern)
                                # rather than an automatic rejection --
                                # applies regardless of whether the reopened
                                # period itself has any genuine change (Item
                                # A-R3).
                                _scoped_raw_path, _scope_out_dir, _violations = PL.enforce_period_scoped_correction(
                                    _tmp_raw_path, _rp, R, close_history,
                                )
                            except RuntimeError as _err:
                                st.session_state["reopen_candidate_build_error"] = str(_err)
                                shutil.rmtree(_tmp_dir, ignore_errors=True)
                                st.rerun()
                            else:
                                if _violations:
                                    st.session_state["correction_scope_pending"] = {
                                        "period": _rp,
                                        "scoped_raw_path": _scoped_raw_path,
                                        "scope_out_dir": _scope_out_dir,
                                        "tmp_dir": _tmp_dir,
                                        "violations": _violations,
                                        # Principal-directed fix: captured now,
                                        # at detection time, rather than
                                        # re-derived from the uploader when
                                        # "Continue" is eventually clicked --
                                        # this out-of-period-violation path is
                                        # only ever reached via an uploaded
                                        # file (the saved-dataset-copy path is
                                        # trivially identical to itself, so it
                                        # can never produce a violation), so
                                        # this is always non-None here.
                                        "source_file_id": _current_upload_id,
                                    }
                                    st.rerun()
                                else:
                                    with st.spinner("Regenerating candidate outputs against the corrected dataset..."):
                                        _run_candidate_pipeline(
                                            _scoped_raw_path, [], [_tmp_dir, _scope_out_dir],
                                            source_file_id=(_current_upload_id if _run_intake_clicked else None),
                                        )
                                    # A failed build stores its error and returns without
                                    # a rerun; rerun so the error is actually shown.
                                    if st.session_state.get("reopen_candidate_build_error"):
                                        st.rerun()

            if _scope_pending_here:
                _pv = st.session_state["correction_scope_pending"]
                _violation_lines = "\n".join(_fmt_scope_violation_line(v) for v in _pv["violations"])
                st.warning(
                    f"These values fall outside {R.fmt_period_label(_rp)} and will not be captured in "
                    f"this close:\n\n{_violation_lines}"
                )
                _sc1, _sc2 = st.columns(2)
                with _sc1:
                    if st.button("Continue", key="correction_scope_continue_btn"):
                        with st.spinner("Regenerating candidate outputs against the corrected dataset..."):
                            _run_candidate_pipeline(
                                _pv["scoped_raw_path"], _pv["violations"],
                                [_pv["tmp_dir"], _pv["scope_out_dir"]],
                                source_file_id=_pv.get("source_file_id"),
                            )
                        st.session_state.pop("correction_scope_pending", None)
                with _sc2:
                    if st.button("Cancel", key="correction_scope_cancel_btn"):
                        # Original Item A's reject-outright behavior,
                        # preserved exactly for this choice: no candidate
                        # created, nothing archived, scratch cleaned up.
                        shutil.rmtree(_pv["tmp_dir"], ignore_errors=True)
                        shutil.rmtree(_pv["scope_out_dir"], ignore_errors=True)
                        st.session_state.pop("correction_scope_pending", None)
                        # Item G (Addendum 2): reset the dataset uploader.
                        st.session_state["reopen_uploader_generation"] = (
                            st.session_state.get("reopen_uploader_generation", 0) + 1
                        )
                        st.rerun()

            # -----------------------------------------------------------
            # D15 Item 2 — candidate-scoped Human Approval Gate + v2
            # archival. This is a SEPARATE session-state key
            # ("reopen_candidate_approval_status") from the live current
            # close's "close_approval_status" -- it must never read or
            # write that key, so approving/rejecting a candidate can never
            # affect the live target_period's own Gate state, and vice
            # versa. Exactly one archive_close() call exists for the
            # candidate, inside the Approve handler below; Reject is a
            # status change only, with no archive call and no other side
            # effect; Cancel/abandonment (Steps 1-2 above, and simply
            # never running correction intake here) leave close_history/
            # untouched by construction, since nothing else in this
            # section calls archive_close().
            # -----------------------------------------------------------
            if "reopen_candidate" in st.session_state and st.session_state["reopen_candidate"]["period"] == _rp:
                _cand = st.session_state["reopen_candidate"]

                # -----------------------------------------------------
                # Addendum 3, Item H — persistent candidate build summary.
                # Rendered unconditionally, every rerun, from stored state
                # only (never from a transient local variable) -- stays
                # visible across attaching a commentary file, an unrelated
                # widget interaction, etc. Disappears only when
                # "reopen_candidate" itself is cleared (Approve, Reject,
                # Start over) or the reopened period changes -- both
                # already handled by this same `if` condition.
                # -----------------------------------------------------
                st.success(
                    f"Candidate built for {R.fmt_period_label(_rp)}. "
                    f"**numerical_impact = {_cand['numerical_impact']}** "
                    f"(reprocessing_required for this explicitly-reopened period is `True` "
                    "unconditionally per 5.F, regardless of this value)."
                )
                # Principal-directed fix (live-testing session): a file
                # currently sitting in the uploader that this candidate
                # was NOT built from -- either because it was attached
                # after this candidate was built (including the very
                # first, automatic no-op build that fires the moment a
                # reopen is confirmed, before the user has attached
                # anything) or because it has since been replaced with a
                # different file. Without this, "Approve candidate close"
                # below could silently approve a candidate that does not
                # reflect the file the user can see sitting in the
                # uploader -- which is exactly the live-testing finding
                # this fixes (reported: uploading a correction, then
                # clicking Approve directly, silently closed against the
                # unchanged saved data and cancelled the reopen instead of
                # applying the upload). The Approve handler below hard-
                # blocks on this same condition; this banner is what
                # explains why, before the click.
                _candidate_is_stale = (
                    _corrected_file is not None and _current_upload_id != _cand.get("source_file_id")
                )
                if _candidate_is_stale:
                    st.warning(
                        f"**{_corrected_file.name}** is attached but this candidate was not built from it "
                        "(shown above) — approving now would NOT apply this file. Click **Run correction "
                        "intake** above to rebuild the candidate from it, or remove the file to proceed with "
                        "the candidate as already built."
                    )
                if _cand.get("excluded_out_of_period_rows"):
                    st.info(
                        f"{len(_cand['excluded_out_of_period_rows'])} out-of-period row(s) were excluded from "
                        "this candidate (reset to their currently-approved value) -- persisted into the "
                        "archived record's audit trail on approval."
                    )
                st.markdown("**Per-output impact summary (5.E)**")
                for _out_name, _res in _cand["comparison"].items():
                    _badge = "🔶 impact" if _res.impact else "no impact"
                    st.write(f"- **{_out_name}** — {_badge} ({len(_res.diffs_df)} differing row(s))")
                    if _res.impact and len(_res.diffs_df) > 0:
                        st.dataframe(fmt_display_df(_res.diffs_df), use_container_width=True)

                # Item D (D15-Item2-Corrections Brief): the candidate's own
                # full line-item Phase 2 diff (Date/Department/Category/
                # Prior/Current/Diff) -- reuses the exact Close Validation
                # Status Phase 2 table rendering, no new computation.
                # Reflects Item A's fix by construction: _cand["phase2_result"]
                # was computed from the scoped/reconstructed workbook, so it
                # can never contain a row that was excluded (whether via
                # identical-passthrough or via a confirmed Continue).
                st.markdown("**Full line-item diff (Phase 2, raw) — reopened period's own Expenses only**")
                _cand_phase2_display = _cand["phase2_result"]
                if _cand_phase2_display.status == CV.STATUS_NOT_APPLICABLE:
                    st.info(
                        "Not applicable — no prior approved close exists for "
                        f"{R.fmt_period_label(_rp)} to diff the candidate's Expenses against."
                    )
                elif len(_cand_phase2_display.flagged_rows) == 0:
                    st.success("No line-item differences found against this period's own prior approved close.")
                else:
                    render_phase2_flagged_table(_cand_phase2_display.flagged_rows)

                # -----------------------------------------------------
                # Bug/Change 4 (supersedes Item E's matching-only scope):
                # uploading a commentary file while a closed period is
                # reopened must behave EXACTLY like Commentary Review
                # (Phase 4-6) for a period that is not closed -- so this
                # calls the very same function the live close uses,
                # _render_commentary_intake_and_review(): deterministic
                # match, exclusivity, gated semantic reconciliation,
                # Phase 5 finance note for unmatched entries, manual
                # reconciliation, Phase 6 validation of every matched
                # commentary, edit/revalidate, Accept, version history.
                # The only differences are the inputs: Phase 6 evidence
                # is built from the CANDIDATE's own rollups output and
                # Phase 3 result (the corrected numbers), and approval
                # resets act on the candidate's own gate.
                # -----------------------------------------------------
                st.divider()
                st.subheader("Commentary Review (Phase 4-6)")
                st.caption(
                    "Import the Controller's Commentary.xlsx (sheet 'Commentary', columns Commentary_ID + "
                    "Commentary_Text only — no observation ID, status, or AI field in the input file). The Controller "
                    "never operates this dashboard; only the finance/CFO user reviews, edits, and accepts commentary here. "
                    f"This is the corrected candidate for {R.fmt_period_label(_rp)}: commentary is matched and validated "
                    "against the candidate's own observations and numbers. The file is OPTIONAL."
                )
                _cand_rollups_xl = pd.ExcelFile(_cand["rollups_output_path"])
                _cand_hc_q = pd.read_excel(_cand_rollups_xl, "Headcount_Q")
                _cand_exp_dept_cat_q = pd.read_excel(_cand_rollups_xl, "Exp_by_Dept_Cat_Q")
                _cand_rp_idx = R.quarter_order.index(_rp)
                _cand_rp_prior = R.quarter_order[_cand_rp_idx - 1] if _cand_rp_idx > 0 else None
                _cand_hc_current = _cand_hc_q[_cand_hc_q["Fiscal Quarter"] == _rp][["Department", "Ending Headcount"]]
                _cand_hc_prior = (
                    _cand_hc_q[_cand_hc_q["Fiscal Quarter"] == _cand_rp_prior][["Department", "Ending Headcount"]]
                    if _cand_rp_prior is not None
                    else _cand_hc_q.iloc[0:0][["Department", "Ending Headcount"]]
                )
                _render_commentary_intake_and_review(
                    _cand["commentary_records"], _cand["observation_register"], _rp,
                    hc_current_df=_cand_hc_current, hc_prior_df=_cand_hc_prior,
                    exp_by_dept_cat_df=_cand_exp_dept_cat_q,
                    headcount_band=_cand["phase3_result"].headcount_band,
                    uploader_key=f"candidate_commentary_uploader_{_uploader_gen}",
                    semantic_attempted=_cand.setdefault("semantic_attempted", set()),
                    close_approval_getter=_candidate_approval_status_for,
                    close_approval_setter=_set_candidate_approval_status_for,
                    uploader_label="Commentary.xlsx for this candidate (optional)",
                    carried_file=_cand.get("carried_commentary_file"),
                )

                st.divider()
                st.subheader("Candidate approval")
                if "reopen_candidate_approval_status" not in st.session_state:
                    st.session_state["reopen_candidate_approval_status"] = "not_yet_decided"
                st.write(f"Candidate status: **{st.session_state['reopen_candidate_approval_status']}**")

                _gate_c1, _gate_c2 = st.columns(2)
                with _gate_c1:
                    if st.button("Approve candidate close", key="approve_candidate_close_btn"):
                        # Principal-directed fix (live-testing session):
                        # hard, authoritative re-check of the same
                        # staleness condition the banner above already
                        # warns about -- same pattern as the close-order
                        # and unresolved-reopen hard checks elsewhere in
                        # this handler (an early warning is not enough by
                        # itself; the click itself must also be stopped).
                        # Re-reads _corrected_file/_current_upload_id
                        # fresh rather than trusting a value computed
                        # earlier in this same render, for the same reason
                        # those other checks do.
                        if _corrected_file is not None and _current_upload_id != _cand.get("source_file_id"):
                            st.error(
                                f"**{_corrected_file.name}** is attached but this candidate was not built from "
                                "it. Click **Run correction intake** to rebuild the candidate from this file, "
                                "or remove it before approving."
                            )
                            st.stop()
                        _fixk_refused = False
                        try:
                            # Item F (D15-Item2-Corrections Addendum 1) --
                            # zero-net-change guard. Blocks BEFORE any
                            # version is computed or archived if neither
                            # axis (numerical, reusing 5.E's already-
                            # computed _cand["numerical_impact"]; or
                            # commentary, Item E's matched records vs. the
                            # prior version's own stored commentary_record)
                            # shows a genuine change. Because
                            # _cand["numerical_impact"] was computed from
                            # the SCOPED/reconstructed workbook (Item A),
                            # an out-of-period row excluded via Continue
                            # never counts toward it by construction --
                            # this is exactly how Items A and F compose
                            # (F4).
                            _guard_prior_close = close_history.resolve_latest_approved_close_for_period(_rp)
                            _guard_prior_commentary = (
                                _guard_prior_close["metadata"].get("commentary_record", {})
                                if _guard_prior_close is not None else {}
                            )
                            _guard_commentary_changed, _guard_commentary_detail = PL.commentary_changed(
                                _guard_prior_commentary, _cand.get("commentary_records", {})
                            )
                            if not _cand["numerical_impact"] and not _guard_commentary_changed:
                                # Live-testing finding (Principal-directed,
                                # same session as the unresolved-reopen
                                # block above): this used to show the
                                # warning and call st.stop() -- but since
                                # st.stop() is inside this button's click
                                # handler, it halted the ENTIRE script for
                                # this render, so nothing below it (the
                                # "Reject candidate" button in the other
                                # column, and "Start over" further down)
                                # rendered either -- leaving no visible way
                                # off this screen. Nothing was ever written
                                # to Close History for this candidate
                                # (5.C/5.D never persists before Approve
                                # succeeds), so there is nothing to undo --
                                # resolving it automatically, exactly as
                                # "Start over" below does, is both the fix
                                # for that and the more sensible behavior:
                                # there is nothing left to correct, so
                                # nothing is gained by leaving it open for
                                # a second, manual "Start over" click.
                                if _cand.get("persist_dir"):
                                    shutil.rmtree(_cand["persist_dir"], ignore_errors=True)
                                st.session_state["reopen_step"] = 0
                                st.session_state["reopen_target_period"] = None
                                st.session_state.pop("reopen_candidate", None)
                                st.session_state.pop("reopen_candidate_approval_status", None)
                                st.session_state["reopen_candidate_build_error"] = None
                                st.session_state["reopen_uploader_generation"] = (
                                    st.session_state.get("reopen_uploader_generation", 0) + 1
                                )
                                st.toast(
                                    f"No change detected in {R.fmt_period_label(_rp)} — nothing to correct. "
                                    "Reopen cancelled.",
                                    icon="ℹ️",
                                )
                                st.rerun()

                            # D15 Items 3 & 4 -- hard, authoritative
                            # close-order / reopen-propagation check,
                            # immediately before archive_close() runs (same
                            # design as the live single-period Approve
                            # handler). Checks _rp -- the period actually
                            # being reopened and re-closed here -- against
                            # ITS predecessors, never against itself.
                            # Procedural only: nothing above or below this
                            # sets, clears, or implies any Human Approval
                            # Gate (D13) criterion.
                            _close_order_blocker = PL.find_close_order_blocker(_rp, R.quarter_order, close_history)
                            if _close_order_blocker is not None:
                                st.error(_fmt_close_order_block_message(_close_order_blocker, _rp))
                                st.stop()

                            # Correction 1: version computed dynamically,
                            # never hardcoded.
                            _candidate_version = close_history.next_version_for_period(_rp)
                            # Correction 2: chronological predecessor,
                            # never resolve_latest_approved_close().
                            _rp_idx = R.quarter_order.index(_rp)
                            _candidate_prior_period_label = (
                                R.quarter_order[_rp_idx - 1] if _rp_idx > 0 else None
                            )
                            # Correction 4: existing, unmodified
                            # build_observation_register(), fed the
                            # candidate's own Phase 2/3 results.
                            _candidate_obs_df = CWF.build_observation_register(
                                _cand["phase2_result"], _cand["phase3_result"], R.fmt_period_label, CV.STATUS_OK
                            )

                            # Fix K (brief v2.3, 'No flag, no approval'): marks are written and
                            # verified BEFORE the correction is saved. If a required mark cannot
                            # be saved and read back, nothing is saved and this attempt's marks
                            # are undone. Comparison reads the CANDIDATE's own rollups file
                            # (nothing is archived yet; archive_close copies it byte for byte).
                            _candidate_rollups_path = _cand["rollups_output_path"]

                            def _d15_propagation_compare_fn(downstream_period, predecessor_descriptor):
                                _prior_close = close_history.resolve_latest_approved_close_for_period(downstream_period)
                                if _prior_close is None:
                                    # Nothing archived yet for this downstream
                                    # period to compare against -- not affected.
                                    return False, predecessor_descriptor
                                _impact, _ = PL.compare_period_outputs(
                                    downstream_period, _prior_close["rollups_output_path"], _candidate_rollups_path
                                )
                                return _impact, predecessor_descriptor

                            # The ONE archive_close() call site for this
                            # candidate. Correction 5, UPDATED by Addendum
                            # 1 Item E: commentary_record is now whatever
                            # was actually matched during this candidate's
                            # own commentary-entry step above -- serialized
                            # via the same, unmodified
                            # serialize_commentary_records() the live path
                            # uses -- rather than always None. Still
                            # honestly {} (not fabricated) when nothing was
                            # entered this session.
                            def _fixk_archive(_attempt_id):
                                return close_history.archive_close(
                                    period_label=_rp,
                                    raw_dataset_src=_cand["raw_dataset_path"],
                                    rollups_output_src=_cand["rollups_output_path"],
                                    observations_df=_candidate_obs_df,
                                    narrative_text="",
                                    phase2_flag_count=len(_cand["phase2_result"].flagged_rows),
                                    phase3_flag_count=len(_cand["phase3_result"].flagged_rows),
                                    workflow_state="Executive Ready",
                                    prior_close_period_label=_candidate_prior_period_label,
                                    commentary_record=CWF.serialize_commentary_records(_cand.get("commentary_records", {})),
                                    version=_candidate_version,
                                    extra_metadata=dict(attempt_id=_attempt_id, **PL.build_lineage_metadata(
                                        trigger=PL.TRIGGER_EXPLICIT_REOPEN,
                                        comparison_result=_cand["comparison"],
                                        # Item A audit trail (Addendum 1):
                                        # persisted into the archived record,
                                        # not only shown once in the UI.
                                        excluded_out_of_period_rows=_cand.get("excluded_out_of_period_rows"),
                                    )),
                                )

                            _attempt = PL.run_reopen_approval_attempt(
                                _rp, R.quarter_order, close_history, _d15_propagation_compare_fn, _fixk_archive,
                                _candidate_version,
                            )
                            _fixk_refused = _attempt["outcome"] != "saved"
                            if _fixk_refused:
                                _fixk_render_failure(_rp, _attempt)
                            else:
                                _archived_folder, _archived_meta = _attempt["archived"]
                                st.session_state["reopen_candidate_approval_status"] = "approved"

                                # Principal-directed fix (live-testing session):
                                # the reopen candidate keeps its OWN commentary_
                                # records dict (_cand["commentary_records"]),
                                # entirely separate from the top-level
                                # st.session_state["commentary_records"] that the
                                # workflow-state strip (Explanations Validated),
                                # the closed-period read-only Commentary Review
                                # view, and the Narrative tab all read from.
                                # Nothing ever copied the candidate's dict back
                                # into the top-level one -- it was archived
                                # correctly to Close History (via
                                # serialize_commentary_records just above) and
                                # then discarded a few lines below when
                                # "reopen_candidate" is popped from session
                                # state, so a correction's accepted commentary
                                # durably existed on disk but was invisible
                                # everywhere else in this session: the narrative
                                # reported it as "commentary process attempted
                                # but no accepted explanation currently exists",
                                # and "Explanations Validated" stayed unchecked,
                                # even though the Controller had already written
                                # and accepted it. Confirmed live (both by
                                # reproducing it directly and independently by
                                # you hitting the identical symptom).
                                #
                                # A plain dict.update() is sufficient and safe: a
                                # stale key from a superseded observation (e.g. a
                                # prior version's flag that the correction
                                # resolved and which no longer appears in the
                                # current observation register) is never looked
                                # up by ID against anything but the CURRENT
                                # register everywhere it's consumed
                                # (_render_commentary_review_records skips a
                                # non-matching oid; the workflow-state strip's
                                # open-uncommented count is a set difference
                                # against the current register's own IDs;
                                # build_narrative_commentary_section iterates the
                                # current register's flagged rows, never the
                                # commentary dict's keys) -- so it becomes
                                # harmlessly inert rather than wrong.
                                st.session_state["commentary_records"].update(
                                    _cand.get("commentary_records", {})
                                )

                                # Fix K step 7 results: reported, never hidden (M9).
                                st.session_state["close_order_notices"] = _fixk_success_notices(_rp, _attempt)


                                # Temp files are cleaned up only now that the
                                # candidate is RESOLVED (approved) -- never
                                # earlier.
                                if _cand.get("persist_dir"):
                                    shutil.rmtree(_cand["persist_dir"], ignore_errors=True)
                                # Item B (D15-Item2-Corrections Brief, OI-9/
                                # OI-12): same fix as the live single-period
                                # Approve handler -- force rollups.py to
                                # re-resolve so Close Validation Status
                                # correctly reflects this candidate's
                                # correction without a manual restart.
                                importlib.reload(R)
                                _archived_version_msg = (
                                    f"✅ Archived {R.fmt_period_label(_rp)} as v{_candidate_version} at {_archived_folder}."
                                )
                                # Item G (Addendum 2/3): reset both reopen
                                # uploaders on a successful approve.
                                st.session_state["reopen_uploader_generation"] = (
                                    st.session_state.get("reopen_uploader_generation", 0) + 1
                                )
                                # Live-testing bug fix: previously the candidate
                                # (st.session_state["reopen_candidate"]) was left
                                # in place after a successful approve, so the
                                # persistent Item H summary block kept rendering
                                # the SAME "Candidate built for..." banner it
                                # showed before this click -- nothing on the page
                                # visibly changed, since the one-time "Archived
                                # as vN" confirmation below is rendered on this
                                # same pass and then discarded by st.rerun() a
                                # few lines down, exactly the flash Item H was
                                # built to fix for the build summary, but this
                                # success message was never given the same
                                # treatment. Clearing the candidate here lets
                                # Item K's own top-level check correctly show
                                # this period as "already closed" on the very
                                # next render -- the natural, unambiguous
                                # confirmation that this succeeded, no separate
                                # message channel needed. st.toast() (unlike
                                # st.success()) is specifically designed to
                                # survive exactly one st.rerun(), so the
                                # confirmation itself is not lost either.
                                st.session_state.pop("reopen_candidate", None)
                                st.session_state["reopen_step"] = 0
                                st.session_state["reopen_target_period"] = None
                                st.session_state.pop("reopen_candidate_approval_status", None)
                                st.toast(_archived_version_msg, icon="✅")
                        except FileExistsError as _err:
                            st.error(str(_err))
                        if not _fixk_refused:
                                st.rerun()
                with _gate_c2:
                    if st.button("Reject candidate", key="reject_candidate_close_btn"):
                        # Status change only. No archive call. No other
                        # side effect -- per the Architect's constraint,
                        # temp-file cleanup for a rejected candidate is
                        # deliberately left to "Start over" below, not
                        # folded in here.
                        st.session_state["reopen_candidate_approval_status"] = "rejected"
                        _rejected_cand = st.session_state.get("reopen_candidate")
                        if _rejected_cand is not None:
                            _rejected_cand["carried_commentary_file"] = None
                        # Item G (Addendum 2): reset both reopen uploaders.
                        st.session_state["reopen_uploader_generation"] = (
                            st.session_state.get("reopen_uploader_generation", 0) + 1
                        )
                        st.rerun()

            if st.button("Start over", key="reopen_reset_btn"):
                _existing_candidate = st.session_state.get("reopen_candidate")
                if _existing_candidate and _existing_candidate.get("persist_dir"):
                    shutil.rmtree(_existing_candidate["persist_dir"], ignore_errors=True)
                st.session_state["reopen_step"] = 0
                st.session_state["reopen_target_period"] = None
                st.session_state.pop("reopen_candidate", None)
                st.session_state.pop("reopen_candidate_approval_status", None)
                st.session_state["reopen_candidate_build_error"] = None
                # Item G (Addendum 2): reset both reopen uploaders.
                st.session_state["reopen_uploader_generation"] = (
                    st.session_state.get("reopen_uploader_generation", 0) + 1
                )
                st.rerun()

with tab_region_invest:
    st.title("Regional Revenue & Go-to-Market Investment")
    st.caption(
        "Shows whether go-to-market investment is growing in proportion to revenue by region — "
        "not a full profitability measure."
    )

    st.subheader(f"Revenue, Allocated GTM Cost, and Net of GTM Cost — {R.fmt_period_label(current_period)}")
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
    if cadence == "Quarterly":
        region_trend = region_trend.rename(index=R.fmt_period_label)
    st.line_chart(_chrono_index(region_trend))

with tab_product_invest:
    st.title("Product Line Revenue & R&D Investment")
    st.caption(
        "Shows whether R&D investment is growing in proportion to revenue by product line — "
        "not a full profitability measure."
    )

    st.subheader(f"Revenue, Allocated R&D Cost, and Net of R&D Cost — {R.fmt_period_label(current_period)}")
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
    if cadence == "Quarterly":
        product_trend = product_trend.rename(index=R.fmt_period_label)
    st.line_chart(_chrono_index(product_trend))

with tab_narr:
    st.subheader(f"AI-Generated Narrative — {R.fmt_period_label(current_period)} vs {R.fmt_period_label(prior_period)}")
    st.caption("Uses the exact system + user prompt from northwind_narrative_prompt.md, populated from the tables in the other tabs.")

    # Section G handoff (Brief v5, rewritten this revision): three required
    # states, not two -- no flags / flags+file-supplied (accepted+unresolved)
    # / flags+no-file-supplied (unexplained, no cause invented). Determined
    # here from (a) observation_register (built earlier in the tab_close
    # block above -- Streamlit executes every tab's body every rerun
    # regardless of which tab is visually active, so it's always defined by
    # this point) and (b) commentary_file_supplied, tracked durably across
    # this session (see Commentary Review section above). Byte-identical to
    # pre-Phase-4-6 behavior whenever observation_register is empty,
    # regardless of commentary-file presence (Brief Section G, Criterion 1).
    #
    # Phase 7 period-display addendum (addendum to
    # phase6_headcount_direction_fix_brief_v1.md): this tab's narrative/
    # prompt text is CFO/Board-facing (IA #9) and must use the same D14
    # display-format convention as every other user-facing surface. Reuses
    # the existing R.fmt_period_label formatter -- no second implementation.
    # Fix (commentary lost before/without download): for a CLOSED quarter the
    # register and the Commentary Record are read back from that period's own
    # latest approved Close History snapshot, not from session memory -- so the
    # narrative prompt is identical whether it is viewed right after approval,
    # after a page refresh, or days later in a new session. Unclosed periods,
    # and Annual cadence, keep the existing session-based path unchanged.
    _narr_register = observation_register
    _narr_records = st.session_state.get("commentary_records", {})
    _narr_file_supplied = st.session_state.get("commentary_file_supplied", False)
    if cadence == "Quarterly":
        try:
            _archived_commentary = _archived_commentary_for_period(current_period)
        except Exception as _archive_read_exc:
            _archived_commentary = None
            st.warning(
                f"The archived commentary for {R.fmt_period_label(current_period)} could not be read "
                f"({type(_archive_read_exc).__name__}: {_archive_read_exc}). The prompt below is built from "
                f"this session only and may be missing commentary."
            )
        if _archived_commentary is not None:
            _narr_register, _narr_records, _narr_file_supplied = _archived_commentary
    # Fix (cross-period leak): when the register comes from this session, it is
    # the one built for the Close Validation tab's own period selector, which can
    # differ from the sidebar period this prompt is about. Keep only observations
    # belonging to the period(s) the prompt covers, so a flag from another
    # period is never attributed to this narrative.
    if _narr_register is observation_register and not observation_register.empty:
        _narr_scope_labels = {
            R.fmt_period_label(_q)
            for _q in (
                [current_period] if cadence == "Quarterly"
                else [q for q in R.quarter_order if q.endswith(" " + str(current_period))]
            )
        }
        _narr_register = observation_register[observation_register["Period"].isin(_narr_scope_labels)]
    _commentary_block = CWF.build_narrative_commentary_section(
        _narr_register,
        _narr_records,
        _narr_file_supplied,
        fmt_period_label=R.fmt_period_label,
    )
    user_prompt = R.build_user_prompt(
        period_col, period_order, current_period, prior_period, prior_period,
        pl_df, rev_region_df, rev_product_df, region_cm_df, product_cm_df,
        exp_dept_df, sb_df, breadth_df, hc_dept_df, company_rev_df, bva_df,
        commentary_narrative_block=_commentary_block,
        movement_component_sources=movement_component_sources,
    )

    with st.expander("View rendered prompt (data sent to the model)"):
        st.text(user_prompt)

    # ---------------------------------------------------------------------
    # Human Approval Gate (Brief human_approval_gate_brief_v1.md), Section
    # A/E, Criteria 1-3. STRUCTURAL gate, not cosmetic: when the close is
    # not approved, the code paths that call R.call_claude_narrative() and
    # that build the download button simply do not execute at all -- they
    # sit inside the `if _gate_approved:` branch below.
    #
    # Principal-directed fix (live-testing session): this gate previously
    # read the Close Validation Status tab's own `target_period` selector
    # and the in-session approval flag, so it ignored the sidebar period
    # this tab's narrative is actually about. It now keys on the sidebar
    # `current_period` and on Close History (a saved close), with no new
    # selector on this tab:
    #   Quarterly: current_period has a saved close in Close History
    #     (also true for a period closed in an earlier session).
    #   Annual: every quarter of the selected fiscal year has a saved close.
    # It is additionally blocked while a reopen of that period is in
    # progress, and while that period is flagged as affected by a reopen of
    # an earlier period (see _narrative_gate_block).
    # A saved close only ever exists after the explicit Approve action
    # passed the close-order checks, so per D13 no Phase 6 outcome sets or
    # implies it.
    # ---------------------------------------------------------------------
    _narrative_scope = (
        [q for q in R.quarter_order if q.endswith(" " + str(current_period))]
        if cadence == "Annual" else [current_period]
    )
    _narrative_block = _narrative_gate_block(_narrative_scope)
    _gate_approved = _narrative_block is None

    if not _gate_approved:
        st.warning(_narrative_block)
    else:
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
            safe_current = R.fmt_period_label(current_period).replace(" ", "_")
            safe_prior = R.fmt_period_label(prior_period).replace(" ", "_")
            filename = f"prompt_{safe_current}_vs_{safe_prior}.txt"
            st.download_button(
                label="Download prompt for this period",
                data=user_prompt,
                file_name=filename,
                mime="text/plain",
                type="primary",
            )
