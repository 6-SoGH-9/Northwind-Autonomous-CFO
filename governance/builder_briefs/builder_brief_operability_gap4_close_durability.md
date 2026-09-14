# Builder Brief — Product Operability, Gap 4: Live Close Durability (Approve → Archive → Persist)

**Status:** **ACTIVE — APPROVED FOR BUILDER.** Principal-authorized in full (this exact Brief, no scope changes) following Architect reconciliation of the reopened Gap 4 question.
**Supersedes, on Gap 4 only:** the prior Gap 4 finding recorded in `governance/architect_reports/architect_alignment_report_operability_gaps_1_4.md` ("no material gap, correctly deferred") and the corresponding line in `governance/builder_briefs/builder_brief_operability_gaps_1_2_3.md` ("build any period-reopen/correction/reprocess capability — confirmed out of scope"). That line concerned reopen/correction only and remains correct for that narrower question — see Section 5, Deferred Capability, below. It did not cover, and is not overridden with respect to, anything else in the Gaps 1-3 Brief, which remains untouched and on its own track.
**Author:** Architect
**Basis:** Fresh clone of canonical `main`, HEAD `575bab645810084a42fd36ed3c278d2741fd397e`, direct inspection of `close_history.py`, `close_validation.py`, `Northwind_Financial_Dashboard.py` — not narration. Repository identity per Project Handbook, Source of Truth section (`6-SoGH-9/Northwind-Autonomous-CFO`, branch `main`).
**Constrained by:** D10 (Approved Financial Close / immutable Close History) — `archive_close()`'s unconditional immutability (`FileExistsError` on any existing `period_label`) is preserved exactly as-is; this Brief adds a caller, never a new write path. D13 (Machine Recommends, Human Decides) — the human decision itself (`Approve close` / `Reject`) is untouched; this Brief only makes an already-made human decision durable. The Human Approval Gate's eight already-verified acceptance criteria are not reopened or retested for their own logic — only regression-confirmed.
**Does not reopen:** D10, D11, D12, D14, D13, the Human Approval Gate's approval/rejection logic or its independence from Phase 6 outcome, Phase 4's matching logic, Commentary Record versioning, Phase 7/8, or `builder_brief_operability_gaps_1_2_3.md`'s Gaps 1-3 (separate, unaffected, non-overlapping scope — both Briefs are simultaneously active).
**Precedence:** Project Handbook > this Brief (Active, Gap 4) > `builder_brief_operability_gaps_1_2_3.md` (Active, Gaps 1-3, separate scope) > `phase4_semantic_reconciliation_brief_v2.md` (separate scope) > archived Briefs.

---

## 0. What NOT to do

Builder must **not**:
- build any reopen, correction, versioning (v1/v2), lineage, cross-period dependency, or chronological-blocking capability — that is a separate, explicitly deferred future capability (Section 5), not part of this Brief, regardless of anything in the source instruction document that originally reopened this question;
- change which periods are selectable in the sidebar, or introduce a user-selectable "period being closed" — the close workflow continues to target `period_order[-1]` unconditionally;
- weaken or bypass `archive_close()`'s immutability — a repeat approval against an already-archived `period_label` must still fail to overwrite; this Brief only requires that failure be surfaced legibly (Section 1, Item 1d) instead of as a raw exception;
- alter the Human Approval Gate's existing approve/reject session-state logic, or its independence from Phase 6's Supported/Contradicted/Insufficient outcome;
- alter `commentary_workflow.py`'s matching, validation, or versioning logic;
- expand scope during implementation for any reason. If something discovered during implementation appears to require scope beyond what's written here, **stop and return to the Architect** rather than resolving it unilaterally — per explicit Principal instruction, this Brief's scope is closed.

---

## 1. Item 1 — Approve Close → Durable Archive

### 1a. Finding (why this is required)

Direct inspection confirms `close_history.archive_close()` is called **only** from `build_test/close_orchestrator.py` and `build_test/commentary_workflow_demo.py` — both explicitly Build/Test-only. In the live dashboard, the **"Approve close"** button (`Northwind_Financial_Dashboard.py`, `st.button("Approve close", key="approve_close_btn")`) does exactly one thing: sets `st.session_state["close_approval_status"] = "approved"`. It never calls `archive_close()`. No durable record of an approved close is ever written by the live product. This was previously out-of-scope by explicit design note in the v4 Commentary Workflow Brief ("the live Human Approval Gate control... remains separately-scoped open technical debt") and was never subsequently picked up — the Human Approval Gate Brief's own UAT tested the approve/reject flag and the Phase 7 structural guard, not whether approval persists anything.

### 1b. Required behavior

On a genuine new approval (see 1d for the already-archived case), call `close_history.archive_close()` with:
- `period_label`: the period the close workflow actually processed — `period_order[-1]` at the moment of approval (the dataset's true latest quarter) — **never** the sidebar's `current_period` (see Item 2).
- `raw_dataset_src`: the resolved path from `rollups.find_raw_dataset()` (already computed earlier in the dashboard's load sequence).
- `rollups_output_src`: the on-disk `rollups_output.xlsx` (already written as a module-level side effect of importing `rollups.py`).
- `observations_df`: the observation register already built via `commentary_workflow.build_observation_register(...)` for this render.
- `narrative_text`: whatever Phase 7 actually produced this session — the live-generated narrative if `ANTHROPIC_API_KEY` was present and a call was made, or the rendered prompt text if the download-fallback path was used. Reflect actual behavior; do not assume the live-API path always ran.
- `phase2_flag_count` / `phase3_flag_count`: from the already-computed `phase2_result` / `phase3_result`.
- `workflow_state`: the current, real workflow-state value (see Item 3).
- `prior_close_period_label`: from `close_history.resolve_latest_approved_close()`, or `None` if Close History is currently empty (bootstrap case — do not special-case this beyond what `archive_close()` already handles).
- `commentary_record`: `commentary_workflow.serialize_commentary_records(records_by_observation_id)` for whatever commentary state exists this session (may legitimately be `{}` if no commentary was ever supplied — `archive_close()` already handles this correctly).

### 1c. Trigger point

Fire on the `Approve close` button handler, immediately after `close_approval_status` is set to `"approved"`, before `st.rerun()`. Do not fire on `Reject / return close`, and do not fire merely because `close_approval_status` happens to already equal `"approved"` on a later rerun (e.g., from an unrelated widget interaction) — this must be an explicit, one-time action per genuine approval click, not a side effect of every rerun where the flag is set.

### 1d. Already-archived period

If `archive_close()` raises `FileExistsError` (i.e., this exact `period_label` was already archived — including in a prior session), catch it and surface a clear, specific message to the user (e.g., "This period is already archived in Close History — see [Gap 2's historical view] to review it.") rather than an unhandled exception or a silent no-op. Do not attempt to overwrite, version, or work around the immutability — that is explicitly out of scope (Section 5).

---

## 2. Item 2 — Period-Target Documentation

No code change to period-selection logic. Document the following, verbatim in substance, in **both** the Project Handbook and an in-app caption on the Close Validation Status tab:

- **What period the close workflow targets:** always the dataset's newest available quarter (`period_order[-1]`), unconditionally.
- **How that's determined:** `close_validation.py`'s `_resolve_target_period()` default — triggered because Phase 2/3 are called from the dashboard with no explicit `target_period` argument.
- **What the sidebar "Current period" selector does:** changes the current/prior comparison basis for the other dashboard pages (Revenue Performance, Cost Structure, Regional/Product Investment, Headcount & Efficiency, Budget vs Actual) only.
- **What it does NOT do:** it has no effect on Phase 2, Phase 3, the observation register, Commentary Review, or which period gets archived on approval, regardless of what value it is set to.
- **Why this is acceptable for the current milestone:** the architecture supports exactly one canonical current close at a time (D10); there is no approved product concept of processing an arbitrary historical period as a live close, and neither End-to-End Demonstration scenario requires one. Multi-period-in-flight selection is explicitly deferred (Section 5) and not required here.

This is a documentation/labeling correction, not a UI redesign — it must not introduce a second, competing period-selection control.

---

## 3. Item 3 — State-Strip Accuracy

The dashboard's workflow-state display (the "Executive Ready" / close-status strip) must reflect that `archive_close()` genuinely succeeded and the close is retrievable via `close_history.resolve_latest_approved_close()` — not merely that `st.session_state["close_approval_status"] == "approved"`. If Item 1's archive call has not yet succeeded this session (e.g., it errored per 1d, or hasn't fired yet on this rerun), the strip must not claim the close is durably complete.

---

## 4. Acceptance Criteria (live evidence required — not isolated function calls)

1. From a running dashboard session: load data, reach Commentary Review, click **Approve close** → a new folder appears under `close_history/<period_label>/` containing all five required files (`raw_dataset.xlsx`, `rollups_output.xlsx`, `observations.csv`, `narrative.txt`, `metadata.json`), with `metadata.json` correctly populated (`period_label`, `approval_timestamp`, `phase2_flag_count`, `phase3_flag_count`, `commentary_record`, `pipeline_git_commit_hash`).
2. **Session-independence (the Principal's specific test — do not treat as satisfied by same-session evidence alone):** after the archive in Criterion 1, **terminate the approving session entirely** — close the browser tab/process, or launch a genuinely new, unrelated Streamlit session — and confirm the approved close is independently retrievable via `close_history.resolve_latest_approved_close()` / `list_approved_closes()` from that new session, with no dependency on the original session's state. A folder appearing on disk during the approving session is not, by itself, sufficient evidence for this criterion — the test is retrieval from a session that never performed the approval.
3. The archived `period_label` equals `period_order[-1]` at the time of approval, confirmed by deliberately setting the sidebar's "Current period" to an earlier period before clicking Approve, and confirming the archived label is still the true latest quarter, not the sidebar's selection.
4. A second live "Approve close" attempt against an already-archived period surfaces the Item 1d message, not a stack trace, and the original snapshot's files are confirmed byte-unchanged afterward.
5. Regression, unaffected: `close_orchestrator.py`'s existing bootstrap/normal-path exercises still pass; the Human Approval Gate's existing eight acceptance criteria (approve/reject session-state behavior, structural Phase 7 guard, revision-after-approval reset) still pass unchanged.
6. Once Criteria 1-2 pass, confirm the record is consumable by Gap 2's historical-navigation feature (`builder_brief_operability_gaps_1_2_3.md`) if that work is present at test time — if not yet built, confirm instead that `list_approved_closes()` returns the new snapshot with a well-formed `metadata.json`, i.e., that nothing about this Brief's output would be unreadable by that feature once it exists.

---

## 5. Deferred — Future Capability (recorded, not authorized)

**Period Reopen / Correction / Reprocessing**, per `governance/superseded_operability_package/Architect Instruction — Incorporate Period Lifecycle and Correction-Reprocessing Into Product Scope.md` (Principal-confirmed provenance): two-step reopen/cancel/abandon transaction; non-destructive `v1`/`v2` versioning; cross-period dependency propagation; chronological reprocessing and blocking; dependency-impact vs. numerical-impact distinction; multi-version Close History lineage.

**Status:** acknowledged as a genuine, Principal-intended future product capability. **Explicitly not evidence that the current close lifecycle is complete without it**, and **explicitly not a reason to delay or dilute this Brief's scope**. Not required by either End-to-End Demonstration scenario (Handbook Section 4). No implementation or design work is authorized by this Brief. Requires its own dedicated Builder Brief and its own Scope Authorization Gate when the Principal takes it up.

---

## 6. Required Evidence for Return Report

- Live screen-recording or step-by-step console/log evidence of Criteria 1-4, including the deliberate cross-session step for Criterion 2.
- Diff scope confined to: the `Approve close` button handler, the new error-handling for `FileExistsError`, the workflow-state display logic, and the two documentation locations in Item 2. No other file should show a diff.
- Confirmation that `close_history.py`, `close_validation.py`, `commentary_workflow.py`'s matching/validation logic, and the Human Approval Gate's approve/reject/guard code are byte-identical to canonical pre-change, except for the new call site itself in the dashboard.
