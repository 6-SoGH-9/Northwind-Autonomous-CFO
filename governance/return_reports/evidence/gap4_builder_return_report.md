# Gap 4 Builder Return Report

**Brief:** `governance/builder_briefs/builder_brief_operability_gap4_close_durability.md`
**Repository:** fresh clone of `6-SoGH-9/Northwind-Autonomous-CFO`, `main`, resolved this session to HEAD `ac6180f65db03cc98a60c604ec288bb72a96a12f` (not the Brief's stated baseline `575bab6...` — the repo has moved on since that Brief was drafted; noted as an Architect item below, not something I resolved unilaterally).
**Diff scope:** exactly one file changed — `Northwind_Financial_Dashboard.py` (83 insertions, 1 deletion). `close_history.py`, `close_validation.py`, `commentary_workflow.py` confirmed **byte-identical** (`git status` shows no diff against any of them).
**No push performed:** this environment has no GitHub write credentials — consistent with the project's own documented standing constraint. Nothing here is canonical-synced.

---

## Environment honesty note (read first)

This is a sandboxed CLI environment: no browser, no way to run two independent live Streamlit server processes and interact with widgets across them. Where the Brief's acceptance criteria require genuine live-UI, cross-session evidence, I used **Streamlit's `AppTest` harness** (drives the real `Northwind_Financial_Dashboard.py` file, executes real button click handlers, real session reruns, real disk I/O) as the closest available approximation, and a **separate, unrelated Python process** for the closest available approximation of session independence. Neither is represented as live-browser/cross-session evidence below.

---

## Item 1 — Approve Close → Durable Archive

**Implemented:** `Approve close` button handler now calls `close_history.archive_close()` with all fields specified in Section 1b (period_label from `period_order[-1]`, `R.RAW`, `rollups_output.xlsx`, the real `observation_register`, `phase2_flag_count`/`phase3_flag_count` from the real result objects, `workflow_state="Executive Ready"`, `prior_close_period_label` from `resolve_latest_approved_close()`, and `commentary_record` via `CWF.serialize_commentary_records()`), inside a `try/except FileExistsError` (Item 1d). Fires once, inside the button's own `if st.button(...)` block, before `st.rerun()` — never as a side effect of a later rerun.

## Item 2 — Period-Target Documentation

**Implemented (in-app only):** added a caption at the top of the Close Validation Status tab stating the tab always targets `period_order[-1]`, names the actual current terminal quarter, and states the sidebar selector has no effect on it.

**Not implemented (Handbook):** the Brief also asks for this in `project_handbook.md`. Per this project's own established convention, the Handbook is Architect/PM-maintained and edited under strict versioning discipline ("edited in place... Handbook version bumped by the Architect after a reviewed Return Report") — I did not bump/edit that 208KB governance file myself. Flagged below as an Architect follow-up item, not silently skipped.

## Item 3 — State-Strip Accuracy

**Implemented:** `executive_ready` (the "Executive Ready" row in the workflow-state strip) now requires `close_approval_status == "approved"` **and** `resolve_latest_approved_close()` returns a snapshot whose `period_label == period_order[-1]`, not just the session flag. `_gate_approved` (the actual Phase 7 structural guard) was **not touched** — this only fixes the informational strip.

---

## Acceptance Criteria — evidence and honest status

**Criterion 1 (archive on approve produces all 5 files + correct metadata) — SCRIPT-APPROXIMATED (AppTest).**

Drove the real `approve_close_btn` via `AppTest`. Result: `close_history/Q4 FY2026/` created with `raw_dataset.xlsx`, `rollups_output.xlsx`, `observations.csv`, `narrative.txt`, `metadata.json`. `metadata.json` verified:

```json
{"period_label": "Q4 FY2026", "approval_timestamp": "2026-09-14T07:10:05...+00:00",
 "workflow_state": "Executive Ready", "phase2_flag_count": 0, "phase3_flag_count": 0,
 "prior_close_period_label": null, "pipeline_git_commit_hash": "ac6180f65db03cc98a60c604ec288bb72a96a12f",
 "dashboard_html": null, "board_deck_pptx": null, "commentary_record": {}}
```

`pipeline_git_commit_hash` correctly matches the actual HEAD. `narrative.txt` is a genuine **empty file, not a placeholder** — see the finding below.

**Criterion 2 (session-independence: terminate approving session, retrieve from a new one) — SCRIPT-APPROXIMATED, explicitly not LIVE-VERIFIED.**

I ran the approval in one Python/AppTest process, then read the result back with `resolve_latest_approved_close()` / `list_approved_closes()` from a **separate, freshly-started Python interpreter process with no shared state** — confirmed retrieval, correct `period_label`, count 1. This is a process-boundary approximation, not "close the browser tab" — I am not marking this LIVE-VERIFIED. Genuine browser cross-session testing cannot be performed in this environment.

**Criterion 3 (archived label = true latest period regardless of sidebar) — SCRIPT-APPROXIMATED (AppTest).**

Set the sidebar's period selector to its earliest option via AppTest, then clicked Approve: archived `period_label` was still `Q4 FY2026` (the true latest quarter), not the sidebar's selection.

**Criterion 4 (repeat approval against already-archived period) — SCRIPT-APPROXIMATED (AppTest).**

Second approve-click against the same already-archived period: no unhandled exception (`at.exception` empty), `last_archive_error` set and surfaced via `st.error(...)`, and the original snapshot's `raw_dataset.xlsx`/`metadata.json` confirmed **byte-identical** (md5 match) before and after the second attempt.

**Criterion 5 (regression) — PARTIAL / MIXED.**

- `rollups.py` tie-outs: ran clean, all `OK` lines, no assertion failures.
- `commentary_workflow_demo.py` (Builder's own v4 fixture): **49/49 passed**, unaffected (this file was never touched).
- `close_history.py`/`close_validation.py`: confirmed byte-identical to canonical via `git status`/`git diff` (zero diff).
- Human Approval Gate approve/reject session-state logic and the Phase 7 `_gate_approved` structural guard: **confirmed byte-identical by diff** (SCRIPT-APPROXIMATED evidence, i.e. diff-based, not a live re-run of the Gate's own 8 UAT cases — I did not reconstruct the Case-5 real-data fixture or re-run the full independent UAT set; that would be re-litigating an already-Verified Brief and was out of this Brief's scope). I did smoke-test that Approve/Reject buttons still function without exception via AppTest.
- **`build_test/close_orchestrator.py` — CANNOT-DEMONSTRATE, and this is a pre-existing defect, not caused by this change.** It fails with `AttributeError: module 'close_v1_v2_simulation' has no attribute 'PLAUSIBILITY_QOQ_THRESHOLD'` (it references the old unprefixed constant name; `close_validation.py` only defines `DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD`/`DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND`). I did not touch `close_orchestrator.py`, `close_validation.py`, or `close_v1_v2_simulation.py`. Flagged as an out-of-scope defect per standing instructions rather than fixed opportunistically. Note: this script also unconditionally deletes `close_history/` — I restored my test snapshot afterward from a backup I'd taken first.

**Criterion 6 (consumable by Gap 2, or by `list_approved_closes()` if Gap 2 isn't built) — SCRIPT-APPROXIMATED.**

Confirmed no "Review a prior close" control exists yet in the dashboard (Gap 2's UI is not built, matching the Handbook). Fallback applies: `list_approved_closes()` returns the new snapshot with a well-formed `metadata.json` (confirmed above).

---

## Genuine finding to flag (not silently resolved)

**`narrative_text` is structurally empty at archive time under the current single-version, immutable-on-first-write model.** Phase 7's "Generate narrative" action is gated behind `close_approval_status == "approved"`, and per Item 1c, `archive_close()` must fire *on the same click* that sets `close_approval_status = "approved"` — before Phase 7 has ever run. So on a first (and, under D10 immutability, only) approval, no narrative or prompt-download text can exist yet to capture. I implemented Item 1b exactly as specified ("reflect actual behavior; do not assume the live-API path always ran" — captures `st.session_state.get("phase7_narrative_text", "")`, currently always `""`), but I did not invent a workaround (e.g., moving the archive call, or archiving twice) since that would be a scope decision beyond this Brief and would collide with D10's immutability and with D15's not-yet-implemented versioning. **Recommend Architect review**: is an empty `narrative.txt` on the archived snapshot acceptable as designed, or does this need its own follow-up item?

## Other Architect review items

1. **Item 2's Handbook-text requirement not implemented by Builder** — see above; in-app caption is done, Handbook edit needs an Architect pass.
2. **Baseline commit mismatch** — this Brief's other sibling document (the D15 Brief) states a baseline of `575bab6...`; the repo's actual current `main` HEAD is `ac6180f...`, four commits later. I implemented against actual current `main` per the authority hierarchy (repository state governs over a stale baseline citation), but flagging the drift for the record.
3. **`close_orchestrator.py`'s pre-existing constant-name defect** (above) — blocks that specific regression script; unrelated to this Brief.
4. **One-time anomaly during testing**: an early AppTest run appeared to show a double-execution artifact (archive succeeded, then immediately hit `FileExistsError`, within what looked like one click). I instrumented and reproduced cleanly afterward — confirmed the handler fires exactly once per click under normal conditions — and believe the earlier anomaly was test-harness/process state from a prior command in the same shell, not a defect in the shipped code. Noting it rather than hiding it, since I couldn't fully root-cause it and it didn't recur.

## Blockers

None preventing Gap 4 code delivery. The items above are review/follow-up items, not blockers to producing this Return Report.

---

**Per the Sequential Implementation Instruction: stopping here. D15 is not started.** Waiting for Architect review of this Return Report and confirmation of canonical synchronization (which requires a push — outside this environment's credentials) before any D15 work begins.
