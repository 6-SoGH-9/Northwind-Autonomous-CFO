# D15 Item 2 Corrections — Addendum 3 (RELEASED)

**Supersedes:** `D15-Item2-Corrections_ADDENDUM2_RELEASED.md`, which is withdrawn in full and replaced by this document. Item G and the Item E exclusivity fix are carried forward unchanged; everything else here is new, driven by live-testing findings this session.
**Status:** RELEASED — ACTIVE.
**Sequencing:** Items H and I must land together (both touch the candidate's state model). Item G depends on Item I (auto-clear is only safe once commentary survives a re-run without needing the file to stay attached). Item K depends on Item J (reuses its per-period close-state check). Item L depends on H/I's persistent candidate model. Order: **H+I → J → K → L → G → Item E fix** (E fix is independent and can land any time).

---

## Item H — NEW: persistent intake-output display

### Root cause (confirmed by direct code trace, not narration)

The "Per-output impact summary (5.E)" and "Full line-item diff" blocks are written as `st.success`/`st.markdown`/`st.write` calls *inside* `_run_candidate_pipeline()`, which is only ever called from within `if st.button("Run correction intake"):` (and the equivalent post-Continue branch). Streamlit reruns the entire script on every interaction; `st.button(...)` only evaluates `True` on the exact rerun triggered by that click. On every subsequent rerun — including the one triggered by attaching a commentary file — the button condition is `False` again, so the function never runs, and none of that output redraws, even though the underlying candidate data is untouched in session state the whole time.

### Required behavior

`_run_candidate_pipeline()` must **compute and store** its results into `st.session_state["reopen_candidate"]` (numerical_impact, the 5.E comparison dict, the Phase 2 diff result, violations) and must not render anything itself. A **separate, unconditional rendering block**, placed after the file uploaders and executed on every rerun as long as `"reopen_candidate" in st.session_state` for the current `_rp`, reads that stored data and renders the summary/diff/violations exactly as today. This block must **not** be nested inside any `if st.button(...)` condition.

### Acceptance criteria

- H1. After a successful "Run correction intake," the summary and diff remain visible across any subsequent rerun (attaching a commentary file, an unrelated widget interaction, etc.) without needing to click the button again.
- H2. The display only disappears when the candidate itself is cleared — Approve success, Reject, Start over, or switching the reopened period.
- H3. Regression: content and values shown are identical to today's — this is a rendering-location change, not a computation change.

---

## Item I — NEW: preserve candidate commentary across an intake re-run

### Required behavior

Resolves both open questions from the withdrawn Addendum 2. `_run_candidate_pipeline()` must **not** reset `commentary_records` to `{}` unconditionally. Instead: if a candidate already exists in session state **for the same reopened period**, carry its `commentary_records` forward into the newly (re)computed candidate. Reset to `{}` only when there is no prior candidate for this period, or the period being reopened has changed.

### Acceptance criteria

- I1. Run intake once, upload commentary, run intake again (e.g., after adjusting the corrected dataset): the previously-captured commentary is still present afterward, without needing the file to still be attached to the uploader.
- I2. Switching to a different period to reopen starts commentary fresh — no carryover across periods.
- I3. Regression: Item F's zero-net-change guard still reads the correct, current `commentary_records` — unaffected by this change since it reads from the same session-state location.

---

## Item J — NEW: Close Approval Gate must reflect the selected period's true state, not a global session flag

### Root cause (confirmed by direct code trace)

`close_approval_status`, `last_archived_close_period`, and `last_archive_error` are single, un-scoped session variables. They are set once by whichever Approve/Reject action last ran, for whichever period was selected *at that moment*, and are never reset or re-derived when `target_period` changes afterward. The Gate's status line, its caption, and its Approve/Reject buttons all read these raw flags directly, with no check against the currently selected period or against actual Close History state.

This produces exactly what was observed live: switching the period selector away from a just-approved period still shows that period's "Approved / Archived as X" message; and an already-closed period can show "Not yet decided" with Approve/Reject still offered, because the flag simply reflects whatever happened last, for whoever it happened to.

### Required behavior

On every render, derive the period's true state from `close_history.resolve_latest_approved_close_for_period(target_period)` — the same call already used correctly for the "Executive Ready" workflow-state row (line ~707) — rather than trusting the raw session flag alone:

1. If a durable approved close already exists for `target_period`: the Gate section shows that fact plainly (e.g. "Already closed — see Close History" with the archived version/date), and does **not** offer live Approve/Reject buttons for it. (This becomes moot once Item K lands, since the close-workflow section — including the Gate — will only render at all for periods that aren't yet closed; Item J is the underlying check Item K's conditional relies on, so it must land first.)
2. If no durable close exists: the Gate shows the in-session decision status for `target_period` specifically — and that status must not leak from a different period's earlier action in the same session.
3. The "Archived to Close History as 'X' this session" caption only ever names `target_period` itself, never a different, previously-archived period.

### Acceptance criteria

- J1. Approve period A, then switch to not-yet-closed period B: Gate shows B's own (not-yet-decided) status, no reference to A.
- J2. Switch to an already-closed period: Gate shows "already closed," Approve/Reject are not offered as live actions.
- J3. Reject is never clickable for the same reason.
- J4. Regression: the existing "Executive Ready" workflow-state row (already correctly period-scoped) is unaffected.

---

## Item K — NEW: merge the two period dropdowns; conditional close vs. reopen workflow

### Required behavior

Replace "Select period to close" and "Previously closed period to reopen" with a single control, labeled **"Select period"**. On every render, resolve the selected period's state via the same check Item J introduced (`close_history.resolve_latest_approved_close_for_period()`):

- **Not yet closed:** render the normal close workflow — Phase 2/3, Commentary Review, Close Approval Gate — exactly as today. The reopen section does not render at all.
- **Already closed:** render only the reopen section, header renamed from "Reopen a previously closed period" to **"Reopen closed period"**, with its "Request reopen" entry point. Phase 2/3, Commentary Review, and the Gate do not render at all for this period.

### Acceptance criteria

- K1. One dropdown only; selecting a not-yet-closed period shows the close workflow, nothing reopen-related.
- K2. Selecting an already-closed period shows only "Reopen closed period," nothing from the close workflow.
- K3. Header text confirmed renamed exactly as specified.
- K4. Regression: within each branch, all existing behavior (Phase 2/3 content, Gate behavior per Item J, reopen flow per Items A/E/F/H/I) is unchanged — this item only changes which branch renders, not what's inside either one.

---

## Item L — NEW: corrected dataset optional on reopen (commentary-only correction)

### Required behavior

The "Corrected raw dataset" upload becomes optional. If no file is attached, "Run correction intake" runs against the reopened period's own current approved data unchanged (zero in-period numeric difference by construction — Item A's existing scoping logic already handles a fully-identical dataset correctly, so this reuses that path rather than adding new logic). This allows reaching the "Candidate commentary" section, and ultimately Approve, purely to update commentary — Item F's guard still requires a genuine commentary change (or genuine numeric change) before it will allow a new version, so a commentary-only correction with no actual content change is still correctly blocked.

### Acceptance criteria

- L1. Reopen a period, attach no dataset file, upload commentary only, run correction intake: candidate is built, numerical_impact is False, commentary is captured.
- L2. Approve with a genuine commentary change and no dataset change: version created (Item F's F2 case).
- L3. Approve with no dataset change and no commentary change: blocked, "nothing to correct" (Item F's F3 case) — confirms this composes correctly with the existing guard.
- L4. Regression: attaching a dataset file still works exactly as today — this only removes the requirement to attach one.

---

## Item G — auto-clear uploaders (carried forward, now safe)

Unchanged from the withdrawn Addendum 2, with its scope extended to also cover the **live, first-close** Commentary Review uploader (`Northwind_Financial_Dashboard.py`'s Phase 4-6 section), which was found still holding its file after "Approve close" — Addendum 2's Item G only covered the two reopen-flow uploaders and missed this one.

### Acceptance criteria (extends the original G1–G6)

- G7. After a successful live "Approve close," the live Commentary Review uploader is empty.
- G8. Auto-clearing a candidate's commentary uploader (on a successful terminal action) does not cause data loss on a subsequent action, now that Item I preserves `commentary_records` independently of the file staying attached.

---

## Item E exclusivity fix — carried forward unchanged

`resolve_commentary_matches()` with a disabled `semantic_fn` stub, replacing the raw `match_commentary_entries()` call, exactly as specified in the withdrawn Addendum 2. No change to that specification.

---

# SCOPE AUTHORIZATION GATE

| Item | Classification | Confirmed how |
|---|---|---|
| H — persistent display | Category A, defect against the already-established requirement that candidate state be reliably visible until a terminal action | Root cause traced directly in code this session |
| I — preserve commentary across re-run | Category B, resolves two previously-open design questions, now decided by this session's findings | Principal-driven, grounded in reproduced live behavior |
| J — Gate period-scoping | Category A, critical defect — Human Approval Gate must reflect true state of the selected period | Root cause traced directly in code, reproduced via Principal's own screenshots |
| K — merged dropdown / conditional workflow | Category B, new UX scope | Principal-specified this session |
| L — optional dataset upload | Category B, new scope | Principal-specified this session |
| G — auto-clear (extended) | Category B, carried forward + one scope addition (live uploader) | Principal-confirmed prior session, extended this session |
| E-fix — exclusivity | Category A, carried forward unchanged | Reproduced prior session |

**Minimum-scope check:** H and I both touch only `_run_candidate_pipeline()`'s internals and add one unconditional rendering block — no new state model. J reuses the exact existing per-period resolution call already proven correct elsewhere in the file. K is a conditional wrapper around two already-correct branches, not a rewrite of either. L reuses Item A's existing identical-dataset passthrough path.

**Priority note:** Item J is flagged highest-severity — an approval gate that can show the wrong state, or offer Approve/Reject for an already-decided period, is a trust-critical defect in the one control this entire project's governance is built around (D13). Recommend Builder treats H+I+J as the first slice, with K/L/G/E-fix following.

**PRINCIPAL APPROVAL GATE:** ☑ All items in this addendum trace directly to decisions or findings made in this session. Released to Builder as of this session, superseding Addendum 2 in full.
