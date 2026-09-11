# Builder Brief — Product Operability & Auditability (Gaps 1, 2, 3)

**Status:** **ACTIVE.** Authorized by the principal (Gap 1 authorized at initial Architect review; Gap 2 and Gap 3 explicitly authorized by the principal after reviewing the Architect's narrower Gap-2/Gap-3 recommendation and electing the fuller scope below). No Builder Return Report exists yet against this Brief.
**Supersedes:** `BUILDER_AUTHORIZATION_GAPS_1_2_3B.md` (never canonical, held only briefly in `governance/builder_briefs/` and removed — see Section 5, Superseded Documents, in the accompanying reconciliation report). This is the first and only authoritative Builder Brief for this scope.
**Author:** Architect
**Basis:** Fresh clone of canonical `main`, HEAD `b745d48f72bbb030e337802043d80cffaa889f52`, confirmed by direct execution/inspection, not narration. Findings below reconcile and, where they conflict, supersede `Architect_Documentation___Alignment_Report___Product_Operability_Gaps__Gaps_1_4_.txt` (retained separately — see Section 6) on scope only: that report's Gap 2/Gap 3 scope recommendations were narrower than what the principal has now explicitly authorized; its underlying code findings (what currently exists) are unchanged and are relied on directly below.
**Constrained by:** D13 (Machine Recommends, Human Decides) — not reopened by this Brief. D10 (Approved Financial Close / immutable Close History) — not reopened; Gap 2 is built as a read path over existing immutable snapshots, never a mutation path. The Validation Independence Principle — `DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD`, `DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND`, `DEFAULT_EXCLUDED_CATEGORIES` remain load-bearing, non-configurable constants; this Brief adds visibility and attribution, never a way to change their values from the UI.
**Does not reopen:** D10, D11, D12, D14, the Human Approval Gate, Phase 4's matching logic, Phase 6's bounded evidence model, commentary versioning, the accepted-version concept, Phase 7/8, or final human approval authority.
**Precedence:** Project Handbook > this Brief (Active) > `phase4_semantic_reconciliation_brief_v2.md` (separate, unaffected scope) > archived Briefs.

---

## 0. What NOT to do (applies to all three gaps)

Builder must **not**:
- make `DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD`, `DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND`, or `DEFAULT_EXCLUDED_CATEGORIES` user-editable, anywhere, in any form;
- change any of their current values (`0.25`, `2`, `("Salaries & Benefits",)`);
- add new analytical rules beyond registering/attributing the three that already exist;
- implement baseline/trend analysis (explicitly deferred, out of scope);
- build any period-reopen/correction/reprocess capability (Gap 4 — confirmed out of scope, no material gap found, remains Phase-9-adjacent and deferred);
- weaken Close History's immutable-snapshot model (`archive_close()` must continue to raise on an existing period label).

---

## 1. Gap 1 — Phase 6 Evidence-Package Period Defect

### 1.1 Verified current behavior (Architect inspection, this HEAD)

`Northwind_Financial_Dashboard.py` lines 772–789: `hc_current_df`, `hc_prior_df`, and `_dept_category_breakdown_for()` — the inputs to Phase 6's evidence package — are all built by filtering on `current_period` (the sidebar's `st.sidebar.selectbox`, line 205), **not** on the period of the observation actually being validated (`obs_row['Period']`). When the sidebar is at its default (latest period, `Q4 FY2026`), this is invisible because the two happen to coincide. When a user navigates the sidebar to any other period — which the UI freely permits — Phase 6 silently validates the observation register's (always-latest) observations against a different period's headcount/category-breakdown data.

This is the same underlying mechanism as the existing Known Technical Debt entry ("sidebar period selector does not affect the Close Validation Status page"), sharpened to the specific line-level defect. It is a genuine correctness defect, not a UX issue.

### 1.2 Required fix

Evidence-package construction (`hc_current_df`, `hc_prior_df`, `_dept_category_breakdown_for()`, and any other Phase 6 input keyed by period) must derive its period from the observation register's own `Period` field for the observation under validation — never from the sidebar's `current_period`. The corresponding prior-period comparison must derive from that same observation's period's immediate predecessor in `period_order`, not from the sidebar's `prior_period`.

### 1.3 Acceptance criteria

1. Phase 6 evidence-package construction reads period from `obs_row['Period']`, confirmed by code inspection (no remaining reference to sidebar `current_period`/`prior_period` inside the evidence-package-building code path).
2. Sidebar navigation to any period other than the observation's own period does not change Phase 6's validation result for that observation (regression case).
3. Existing default-path behavior (sidebar at latest, which is today's only tested path) is unchanged — v4/v5/headcount-direction-fix regression fixtures (49/49, 23/23, 23/23) still pass unmodified.
4. `close_validation.py` and `close_history.py` remain byte-identical to canonical (no scope creep beyond `Northwind_Financial_Dashboard.py` for this item).

### 1.4 D13 sequencing requirement (binding on Test, not Builder)

The Section H/J independent UAT for D13 must run against the **post-Gap-1** implementation, not before it, and must record the sidebar's period state at the time of each test case. This is now recorded explicitly in the Handbook (Section 13) and in the reconciled test instructions (Section 2 below) — it is not new scope for Builder, but Builder's fix is a precondition for that UAT being trustworthy.

---

## 2. Gap 2 — Historical Phase 4–6 Navigation (Principal-authorized, full scope)

### 2.1 What already exists (do not rebuild)

- `close_history.list_approved_closes()` already enumerates every archived close snapshot.
- Per the v4 Brief (Section F), the **complete** Commentary Record — every version, every Phase 6 result, the accepted-version identifier — is already captured into each close's immutable snapshot at approval time via `archive_close()`.
- The current-period Commentary Review rendering (observation → commentary → "Matched via" → Phase 6 result → evidence → sub-checks → version history → accepted preview) already exists and works for the live, not-yet-archived period (`Northwind_Financial_Dashboard.py`, ~lines 703–983). This is confirmed working and must not be rebuilt or altered by this item.

Gap 2 is therefore a **read path**, not new data capture: the data Gap 2 needs to display is already being persisted; what's missing is retrieval and rendering of a prior, archived close's persisted Commentary Record alongside its observation register.

### 2.2 Required capability

1. A period-scoped **"Review a prior close"** control, distinct from the general dashboard sidebar (which drives the other eight IA pages and must not be repurposed for this), on the Close Validation Status tab. Default: the live/current close (today's behavior, unchanged). Selecting a prior period loads that period's archived snapshot via `list_approved_closes()`.
2. When a prior period is selected, render that snapshot's persisted observation register and persisted Commentary Record chain (observation → commentary → match method → Phase 6 result → evidence → version history → accepted marker) using the **same rendering components** already used for the live period — not a second, divergent implementation.
3. This view is **read-only**. No revision, no re-validation, no re-approval of an archived close — consistent with D10's immutability guarantee. Any UI element that implies mutation (submit revision, approve/reject) must be absent or disabled when viewing an archived snapshot.
4. Returning to the live/current close must restore exactly today's live-editing behavior, unaffected.

### 2.3 Acceptance criteria

1. Every period present in Close History (`list_approved_closes()`) is selectable from the new control.
2. Selecting a prior period renders that period's actual persisted observation register and Commentary Record chain — not the current period's data, and not a placeholder.
3. All fields visible for the live period (Matched via, Phase 6 result, evidence, sub-checks, version history, accepted marker) are also visible for a selected prior period, sourced from the archived snapshot.
4. No write action (revision submission, approve/reject) is reachable while viewing an archived snapshot.
5. Live/current-period behavior is byte-for-byte unchanged when the new control is left at its default.
6. Regression: v4/v5/headcount-direction-fix fixtures unaffected; this is additive.

---

## 3. Gap 3 — Analytical Definition Registry (Principal-authorized, full scope)

### 3.1 Verified current state

`close_validation.py` lines 88–94 define `DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD = 0.25`, `DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND = 2`, `DEFAULT_EXCLUDED_CATEGORIES = ("Salaries & Benefits",)` as plain module constants — confirmed as read-only, never overridden anywhere in the call chain, and never exposed in any UI (direct grep). `archive_close()` (`close_history.py` line ~188) captures `pipeline_git_commit_hash` only — an indirect, code-level version pointer — not the explicit threshold values used to produce a given snapshot's flags. First canonical introduction of these exact constants: commit `9cfe4ca1a5fe41747110832d9445328c69563f78` (2026-08-05).

### 3.2 Required capability

**3A — Definition Registry.** A versioned registry (new module or a clearly separated section of `close_validation.py`) holding, per definition: `definition_id`, `version`, `effective_date`, `value`, `description`, `category` (fixed as `"analytical_definition"`), `applies_to`. Register the three existing constants as version `v1.0` each, with `effective_date` set to the constant's actual first-canonical-commit date (`2026-08-05`, per 3.1) — **derived from git history, not invented**. Entries must be structurally immutable (e.g. a frozen dataclass/namedtuple) — a code change to a value requires a new version record with its own `effective_date`, never an in-place edit. Provide a lookup function returning the applicable version(s) as of a given date.

**3B — Observation Attribution.** Each Phase 3-generated observation (`close_validation.py` flagging logic) records which registry definition (`definition_id` + `version`) triggered it. The observation register display (`Northwind_Financial_Dashboard.py`) shows this attribution in business-readable form (e.g. "Flagged because QoQ movement >25% (PLAUSIBILITY_QOQ_THRESHOLD v1.0)") alongside the existing observation detail. Historical observations retain their attribution unchanged when re-displayed.

**3C — Close Record Capture.** At close approval (`archive_close()`), capture the full set of applicable definition versions (as of the approval date, via the 3A lookup function) into the snapshot's `metadata.json`, alongside a `definition_snapshot_date`. This must be additive to the existing metadata structure — `pipeline_git_commit_hash` and all other existing fields are unchanged.

### 3.3 Acceptance criteria

1. All three definitions are registered with complete metadata; each has a stable `version` identifier and a git-history-derived `effective_date`.
2. Definitions are structurally immutable once published (attempting to mutate a published entry in place must fail or be structurally impossible — Builder's choice of mechanism, but it must be demonstrated, not merely asserted).
3. A lookup-by-date function exists and is independently callable (not just used internally).
4. Every Phase-3-generated observation, current and historical, carries `definition_id` + `version` attribution; the observation register displays it.
5. `archive_close()`'s `metadata.json` captures `analytical_definitions_active` (id → version) and `definition_snapshot_date` for every close archived after this change; existing archived closes (pre-change) are unaffected and not retroactively rewritten.
6. End-to-end traceability demonstrated: a specific observation's attribution matches its close record's captured definition version, for at least one archived close.
7. No UI path exists anywhere to edit a definition's value. `0.25`, `2`, and `("Salaries & Benefits",)` are unchanged.
8. Regression: D11's Phase 2/3 behavior is bit-for-bit unchanged (this is metadata/attribution only, never a change to flagging logic itself).

---

## 4. Files in scope

- `Northwind_Financial_Dashboard.py` — Gap 1 (evidence-package wiring), Gap 2 (prior-close navigation/rendering), Gap 3B (observation-register display).
- `close_validation.py` — Gap 3A (registry), Gap 3B (attribution at generation time).
- `close_history.py` — Gap 3C (`archive_close()` metadata capture); Gap 2 relies on `list_approved_closes()` unchanged.
- No changes in scope for `rollups.py`, `commentary_workflow.py`, `northwind_narrative_prompt.md`, or the Phase 4 semantic-reconciliation Brief's scope (`phase4_semantic_reconciliation_brief_v2.md` is unaffected and proceeds independently).

## 5. Required evidence (all three gaps)

Builder regression evidence (existing fixtures reproduced unmodified, plus new fixtures for each gap) **and** independent Test evidence per `governance/test_instructions/test_instructions_operability_gaps_1_2_3.md` (Section 2 of the accompanying reconciliation) are both required before any of Gap 1/2/3 can move from Built to Verified — Builder's own regression evidence is not sufficient on its own (Validation Independence Principle).

## 6. Provenance note

`BUILDER_AUTHORIZATION_GAPS_1_2_3B.md` contains materially useful problem statements and was a legitimate input, but was not Architect-authored and its Gap 3 scope (in its original form) was narrower on process than what's recorded here (it lacked the git-history-derived effective-date requirement and the explicit immutability/read-only constraints tied to D10). This Brief is the sole authoritative version; that document is superseded and retained for provenance only (see the reconciliation report, Section 5).
