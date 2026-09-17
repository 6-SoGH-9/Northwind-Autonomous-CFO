# Builder Return Report — D15 Item 2: v2 Archival Through the Existing Human Approval Gate

**Governing Brief:** `governance/builder_briefs/period_lifecycle_reopen_correction_brief.md` (v2, Builder-ready)
**Governing design note:** `d15_item2_design_note.md` (this session, Architect review: PASS WITH CORRECTIONS)
**Baseline:** working clone built on the previously-reviewed 5.A–5.D patch, itself on canonical `main` HEAD `ef86eb2cb90675963618321a3dd6ab4900f79037`
**Scope:** Item 2 only, per instruction. Items 1, 3, 4, 5 from the wider D15 roadmap were not started.
**Revision note:** this report has been updated in place to fold in the post-review `fmt_display_df` display fix (Architect-validated) — see Section 1's last item, Section 3's last two rows, and Section 6. No other content changed from the version the Architect reviewed and passed.
**Not promoted to canonical.** Working clone only.

---

## 1. Implemented

All five required corrections and all architectural constraints from the Architect's review were applied:

### Correction 1 — dynamic version, never hardcoded
- New `close_history.next_version_for_period(period_label)`: returns `max(existing versions for that period) + 1`, or `1` if the period has no approved snapshot at all. A legacy pre-D15 unversioned snapshot counts as v1.
- The candidate approval handler calls this at the moment of archival — confirmed live: Q2 FY2025 (already at v1) archived its candidate as **v2**, computed dynamically.

### Correction 2 — chronological predecessor, not `resolve_latest_approved_close()`
- `prior_close_period_label` for the candidate archive is computed as `R.quarter_order[R.quarter_order.index(_rp) - 1]` — the reopened period's own immediate chronological predecessor.
- Confirmed live in the archived metadata: reopening **Q2 FY2025** while **Q4 FY2026** was the most-recently-approved close by wall-clock time produced `"prior_close_period_label": "Q1 FY2025"` — the correct chronological predecessor, not the incorrect global-latest value (`Q4 FY2026`) the old logic would have produced.

### Correction 3 — fixed the `resolve_latest_approved_close()` cross-period timestamp contamination
- New `close_history.resolve_latest_approved_close_for_period(period_label)`: filters `list_approved_closes(latest_version_only=True)` to the exact period, with **no cross-period timestamp comparison at all** (there is only ever one entry per period at `latest_version_only=True`, so no ranking step exists to go wrong).
- `resolve_latest_approved_close()` itself is **unchanged** — its existing global-latest-by-timestamp semantics are still correct for callers that genuinely need them (e.g. `rollups.py`'s bootstrap dataset resolution), so this was a targeted addition, not a redefinition of existing behavior.
- The dashboard's "Executive Ready" status strip now calls the period-scoped resolver for `target_period`, instead of the global one.
- The 5.D correction-intake handler's comparison baseline (`_prior_close`) was **also** switched to the period-scoped resolver — this was the same latent bug pattern present in the previously-reviewed 5.D code (comparing a candidate against the global-latest close rather than that period's own prior version), caught and fixed as part of applying this same correction consistently, not as separate new scope.

### Correction 4 — `observations_df` via the existing, unmodified `build_observation_register()`
- The candidate approval handler calls `CWF.build_observation_register(_cand["phase2_result"], _cand["phase3_result"], R.fmt_period_label, CV.STATUS_OK)` — the exact same function, same signature, same arguments shape as the live v1 path uses. `commentary_workflow.py` remains byte-identical to canonical (confirmed by diff, zero lines).

### Correction 5 — `commentary_record=None`, never fabricated
- The candidate `archive_close()` call passes `commentary_record=None` explicitly. `archive_close()`'s own existing `None → {}` coercion (unchanged, pre-existing behavior) applies. Confirmed in the archived metadata: `"commentary_record": {}`.

### Architectural constraints — all honored
- **Separate candidate-scoped session-state key:** `reopen_candidate_approval_status`, entirely distinct from `close_approval_status`. Grepped and confirmed: no code path in the candidate section reads or writes `close_approval_status`.
- **Exactly one new `archive_close()` call site for the candidate** — inside the `Approve candidate close` button handler, and nowhere else in the reopen section.
- **Reject candidate = status change only.** The handler sets `reopen_candidate_approval_status = "rejected"` and does nothing else — no archive call, no temp-file cleanup (see the one documented tradeoff below).
- **Cancellation/abandonment leaves `close_history/` untouched** — structurally guaranteed, since only the one Approve call site can write, and it requires a candidate to exist and the button to be explicitly clicked.
- **Corrected dataset and candidate `rollups_output.xlsx` persist in a session-scoped temp location**, referenced via `st.session_state["reopen_candidate"]["raw_dataset_path"]` / `["rollups_output_path"]` / `["persist_dir"]`, and are cleaned up only when the candidate is resolved (currently: on successful Approve, and on "Start over"). **Documented tradeoff:** per the literal constraint ("Reject candidate = status change only; no ... other side effects"), Reject does **not** clean up the persisted temp directory — it remains on disk until "Start over" is clicked. This is a deliberate, disclosed choice to honor the constraint's exact wording rather than a missed case; flagged for the Architect in case the intended reading was "eventually cleaned up," not "cleaned up only by Approve or explicit reset."

### Post-review fix — `fmt_display_df` on the comparison diff display (Architect-validated)
- Requested after initial Item 2 review, applied on top of the same reviewed implementation: line 1399, `st.dataframe(_res.diffs_df, ...)` → `st.dataframe(fmt_display_df(_res.diffs_df), ...)`.
- `fmt_display_df` (`Northwind_Financial_Dashboard.py`, line 77) is a pre-existing function already used throughout the app (Cost Structure, headcount tables, observation register, Region/Product Investment) — not introduced by this change. It applies `_base_format_map()`, which formats any numeric column whose name contains `($` as `"${:,.0f}"` — `$`-prefixed, comma-thousands, whole-dollar.
- **One open call, flagged rather than decided:** whether a reconciliation/audit-evidence table specifically for a Gate reviewer should instead use 2-decimal precision (to distinguish a genuine sub-dollar rounding artifact from a real difference) was not decided — the fix follows the existing app-wide whole-dollar standard rather than introducing a new, narrower convention for this table only.

---

## 2. Files changed (delta from the previously-reviewed 5.A–5.D patch)

| File | Change this session |
|---|---|
| `close_history.py` | +`next_version_for_period()`, +`resolve_latest_approved_close_for_period()` (58 new lines; `archive_close()`, `resolve_version()`, etc. from 5.A untouched) |
| `Northwind_Financial_Dashboard.py` | Executive Ready check now uses the period-scoped resolver; correction-intake handler now persists candidate materials to a durable temp dir and uses the period-scoped comparison baseline; new candidate-scoped Gate (Approve/Reject buttons) and the one new `archive_close()` call site; "Start over" now cleans up persisted temp materials; **post-review: comparison diff display now renders via `fmt_display_df()` (whole-dollar, `$`-formatted, consistent with the rest of the app)** |

**Confirmed byte-identical to canonical (zero diff), same as every prior session:** `close_validation.py`, `commentary_workflow.py`, `rollups.py`.

**Cumulative diff since baseline HEAD `ef86eb2`:** 5 files changed, 1,446 insertions / 34 deletions (`Northwind_Financial_Dashboard.py`, `close_history.py`, `period_lifecycle.py`, and the two `build_test/` fixtures). Full patch delivered separately as `d15_item2_implementation.patch`; verified to apply cleanly to a fresh checkout of `ef86eb2` and to compile in full afterward.

---

## 3. Verification

| Check | Method | Result |
|---|---|---|
| Compile | `python3 -m py_compile` on all changed/new files | Clean |
| Existing regression | `commentary_workflow_demo.py` | **49/49 passed** |
| 5.A regression | `d15_5a_versioning_demo.py` | **18/18 passed** |
| 5.E/5.F/5.G/5.H regression | `d15_5e_5g_5h_demo.py` | **31/31 passed** |
| **Required evidence — unrelated-period non-corruption** | Live `AppTest`, isolated scratch clone (see below) | **Confirmed** |
| Dynamic version | Live: archived Q2 FY2025's candidate | `version: 2` (period already had v1) |
| Chronological predecessor | Live: inspected archived `metadata.json` | `"prior_close_period_label": "Q1 FY2025"` (not the global-latest `Q4 FY2026`) |
| `commentary_record=None` not fabricated | Live: inspected archived `metadata.json` | `"commentary_record": {}` |
| `build_observation_register()` reused unmodified | Live: `observations.csv` in the archived snapshot | 2 real observations, correct columns, `commentary_workflow.py` zero-diff |
| Reject candidate = status only | Live `AppTest` | `close_history/` byte-identical (md5) before and after Reject |
| Start over after Reject | Live `AppTest` | `close_history/` still byte-identical after |
| **`fmt_display_df` fix — literal rendered output** | Direct Styler-HTML extraction against a real diff (R&D offsetting fixture) | `Amount ($)_before → $164,164`, `Amount ($)_after → $64,164`, etc. — `$`-prefixed, comma-thousands, whole-dollar, matching the app-wide convention exactly |
| **`fmt_display_df` fix — live, end-to-end** | Live `AppTest`: Approve → Reopen → correction intake (now via `fmt_display_df`) → Approve candidate close | 0 exceptions throughout; 16 `st.dataframe` elements rendered without error, including all three D15 comparison-diff tables; candidate still archived successfully (`"Archived Q4 2026 as v2 ..."`) |

### Required evidence — full sequence (isolated scratch clone)

1. Loaded dashboard. `target_period` at default (`Q4 FY2026`). Clicked **Approve close** → archived as v1. Confirmed `Executive Ready = True`.
2. Switched `target_period` to `Q2 FY2025`. Clicked **Approve close** → archived as v1 (a second, unrelated period).
3. Switched `target_period` back to `Q4 FY2026`. Confirmed `Executive Ready = True` — recorded as the **before** state, along with an md5 snapshot of `close_history/`.
4. Reopened **Q2 FY2025** (Request → Continue → Confirm) — 0 exceptions.
5. Uploaded a deliberately-constructed, internally-consistent corrected dataset for Q2 FY2025 (Customer Success/Other Opex +$50,000 for November 2024, with the matching static `PL_Summary` recomputation; independently confirmed to pass `rollups.py`'s own full tie-out suite before use). Ran correction intake → `numerical_impact = True`.
6. Clicked **Approve candidate close** → archived Q2 FY2025 as **v2**, with a wall-clock timestamp *newer* than Q4 FY2026's v1.
7. Switched `target_period` back to `Q4 FY2026` and re-checked Executive Ready.

**Result:**
```
Q4 FY2026 v1 approved. Executive Ready now: True
Q2 FY2025 v1 approved.
Q4 FY2026 Executive Ready BEFORE reopening Q2 FY2025: True
Reopen confirmed for Q2 FY2025.
Correction intake run — numerical_impact = True
Archived Q2 2025 as v2 at close_history/Q2 FY2025/v2.
Q4 FY2026 Executive Ready AFTER approving Q2 FY2025's candidate v2: True
close_history/Q4 FY2026 versions: ['v1']
close_history/Q2 FY2025 versions: ['v1', 'v2']
Q4 FY2026's own v1 files byte-identical (md5) throughout the entire Q2 FY2025 reopen/approve sequence: True
ALL ASSERTIONS PASSED
```

This is the exact scenario the un-fixed code would have gotten wrong: approving Q2 FY2025's v2 gives it the most recent `approval_timestamp` in the whole store, so the old `resolve_latest_approved_close()`-based Executive Ready check would have returned Q2 FY2025's snapshot when asked about `target_period = "Q4 FY2026"`, and — since `"Q2 FY2025" != "Q4 FY2026"` — silently flipped Q4 FY2026's Executive Ready to `False`. With the fix, it stays `True`, and Q4 FY2026's own v1 files are confirmed byte-identical throughout.

### `fmt_display_df` fix — methodological note

`AppTest`'s `Dataframe.value` reconstructs the underlying Arrow-serialized **numeric** data, not the Styler's formatted display strings (confirmed directly: a Styler-formatted `"${:,.0f}"` column returned as raw `1234.5678` via `.value`, not `"$1,235"`). So the live `AppTest` run confirms the call succeeds with no exception and the correct columns/table reach the widget; it cannot by itself confirm the literal rendered `$`-formatted text the way a browser screenshot would. The Styler-HTML extraction above (run directly against the same `fmt_display_df` function on real diff data) is the substitute evidence for that — it reflects exactly what Streamlit serializes to the frontend for display, since `st.dataframe()` was passed the same Styler object either way.

### Reject / cancellation evidence (separate isolated run)

- Approved Q2 FY2025 v1, reopened it, ran correction intake (candidate produced). `close_history/` confirmed byte-identical (md5) before and after correction intake (candidate is session-state only, as before).
- Clicked **Reject candidate** → `close_history/` confirmed **still byte-identical**. Status correctly shown as `rejected`.
- Clicked **Start over** → `close_history/` confirmed **still byte-identical**, 0 exceptions.

---

## 4. Regression

- `commentary_workflow_demo.py`: 49/49, unaffected.
- `d15_5a_versioning_demo.py`: 18/18, unaffected (Item 2 uses `close_history.py`'s 5.A primitives but adds two new, independent functions rather than modifying existing ones).
- `d15_5e_5g_5h_demo.py`: 31/31, unaffected.
- `close_validation.py`, `commentary_workflow.py`, `rollups.py`: confirmed byte-identical to canonical.
- `build_test/close_orchestrator.py`: still not runnable, for the same pre-existing, previously-reported reason (`AttributeError` in `close_v1_v2_simulation.py`, confirmed independent of this or any prior D15 work via `git stash` in an earlier session). Not re-investigated this session; not fixed, per standing Builder Instructions on out-of-scope defects.

---

## 5. Assumptions / limitations

- **Reject-candidate temp-file cleanup deferred to "Start over"** (documented above) — a deliberate reading of the "no other side effects" constraint, not an oversight. Flagged for Architect confirmation of intended behavior.
- The candidate's persisted temp directory (`persist_dir`) is not cleaned up if the browser session is abandoned entirely after a candidate is computed but before any of Approve/Reject/Start-over is clicked — this is an OS-level temp-file lifecycle question (the directory lives under the system temp path, not under `close_history/`), not a Close History correctness concern, and was not in scope of the three required design points.
- Item 2 archives the candidate with `narrative_text=""` (no narrative is generated for a candidate in this pass) and `workflow_state="Executive Ready"` — matching the same accepted-as-designed pattern already recorded for Gap 4's first-version archives (a narrative cannot exist yet at the same click that first makes a state approvable).
- As previously reported and still true: candidate Commentary intake through Phase 4–6, live multi-period 5.G propagation, and live 5.H blocking enforcement remain unimplemented. This report does not claim otherwise.

---

## 6. Architect review items

1. **Confirm intended behavior for Reject-candidate temp-file cleanup** (Section 1/5 above) — current implementation defers it to "Start over," per the literal constraint text.
2. **Confirm the comparison-diff table's whole-dollar (0-decimal) formatting is the intended precision**, or whether 2-decimal precision is wanted instead for this specific, Gate-facing reconciliation table — the fix applied follows the existing app-wide convention rather than deciding a new, narrower one for this table. *(Architect-validated as of this revision; retained here for the record.)*
3. Everything else in this report is either directly demonstrated live or a restatement of previously-flagged, unchanged remaining scope.

---

## 7. Blockers

None new this session.

*End of Return Report.*
