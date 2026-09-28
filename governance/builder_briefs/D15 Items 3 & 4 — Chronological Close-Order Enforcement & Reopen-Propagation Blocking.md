# D15 Items 3 & 4 — Chronological Close-Order Enforcement & Reopen-Propagation Blocking

## Builder Brief — periods close in chronological order (bootstrap-safe, no historical backfill), and a reopen that changes a downstream period's numbers forces that period to be reopened and re-closed before a later period can close.

**Status: DESIGN RESOLVED, awaiting Principal's own confirmation of the Approval Gate below.** Repo `6-SoGH-9/northwind-autonomous-cfo`, HEAD `242b518f9b9d139fa730c9386b928708acb133e2`. Both halves proceed: chronological close-order enforcement (bootstrap-safe: enforcement starts from whichever period is closed first, established once and never retroactively moved — see Implementation) and reopen-propagation blocking (persistence design resolved — see Implementation). The `numerical_impact` comparison set is being extended to detect QoQ effects (Principal-confirmed 2026-09-28), enforcement applies at both period-selection and Approve time (Principal-confirmed), and the OI-8/9/10/12 Corrections Brief lands first (Principal-confirmed). Full design rationale: project doc `architect_reviews/d15_items_3_4_design_note.md`. This revision resolves the Advisor's second-review blockers; the Advisor Review and Architect Verification history has been moved out of this Brief into project docs (see Governance Record, near the end) so this document stays internally consistent.

## Objective

Wire both chronological close-order enforcement and reopen-propagation blocking into the live close/approve flow in `Northwind_Financial_Dashboard.py`. Today a period can be closed regardless of whether prior periods are still open, and regardless of whether an earlier reopen changed a downstream period's numbers without that downstream period being reopened and re-closed itself. This Brief closes both gaps, with close-order enforcement anchored to a confirmed bootstrap rule (below) rather than requiring a historical backfill.

## Scope In

**Category A — already authorized, reused unmodified (read-side logic only — see Category B for the write-side gap this uncovered)**

| Requirement | Source |
| --- | --- |
| Reopen-caused downstream QoQ impact requires reopen+close of that period before a later target can close | D15 architecture (Final); `reprocessing_required_for_downstream()` |
| Oldest-affected-period-first reporting when multiple periods were reopened | `run_propagation_chain()` / `find_blocking_predecessor()` |
| Commentary-only reopen never triggers downstream reprocessing | `reprocessing_required_for_downstream(numerical_impact)` |

All three read/compare functions above (`reprocessing_required_for_downstream`, `run_propagation_chain`, `find_blocking_predecessor` in `period_lifecycle.py`) require no code changes. What does not exist yet: anything that *writes* the lineage state these functions read, and the `numerical_impact` comparison scope is too narrow to detect a pure QoQ effect — both covered in Category B and the Implementation section, per the Architect design note.

**Category B — new Principal decisions**

| Requirement | Authorization |
| --- | --- |
| Chronological close-order enforcement, built now | Principal, confirmed 2026-09-28 |
| Bootstrap baseline rule: established once, the first time any period closes; never retroactively moves | Principal, confirmed 2026-09-28; precise mechanism (write-once record, not a recomputed rule) is the Architect's technical translation, see design note §1 |
| Enforcement applies at both period-selection (early warning) and Approve time (hard block) | Principal, confirmed 2026-09-28 |
| Extend `CANONICAL_COMPARISON_SET` to include sequential/QoQ variance fields, so a reopen's downstream QoQ effect is actually detectable | Principal, confirmed 2026-09-28; changes D15's "Final" architecture, needs a Decision Log addendum, see design note §5 |
| OI-8/9/10/12 Corrections Brief lands before this Brief | Principal, confirmed 2026-09-28 |
| Exact message wording, both cases, incl. Q1→Q2 correction | Principal, 2026-09-27–28 |

Chronological close-order enforcement is new logic, not covered by existing blocking checks: `find_blocking_predecessor()` only fires on a period flagged `reprocessing_required`, not on a period that was simply never closed. The bootstrap rule above (first close = baseline, nothing retroactive) is what makes this buildable without forcing a historical backfill through the dataset's full quarter range.

## Message Wording

Evaluated fresh on every close/selection attempt, against current Close History, not cached from a prior check. Both cases below apply. Period labels display via `fmt_period_label` ("Q# YYYY"), the settled D14 convention — no further decision needed.

**Case (a) template — prior period since the baseline never closed:**

```
{period} is still open. Close it before closing {target}.
```

Example: attempting to close Q4 2026 while Q1 2026 (the first period closed under this rule) has never been closed returns "Q1 2026 is still open. Close it before closing Q4 2026." A second example from the same sequence, once Q1 2026 is closed and Q2 2026/Q3 2026 remain unclosed: attempting Q4 2026 returns "Q2 2026 is still open. Close it before closing Q4 2026." No period predating whichever one is closed first under this rule is ever named as a blocker.

**Message template — reopen caused unresolved downstream impact:**

```
{period} is still open. Reopening {predecessor} affected its figures. Reopen and close {period} before closing {target}.
```

Corrected example, replacing the earlier incoherent one flagged by the Advisor (the original step 3 scenario blocked on periods that were never closed, which is case (a), not a reopen-caused case): close Q1 2026, Q2 2026 and Q3 2026 in order. Reopen Q1 2026 and re-close it, causing a QoQ impact on Q2 2026. Attempt to close Q4 2026. The system returns "Q2 2026 is still open. Reopening Q1 2026 affected its figures. Reopen and close Q2 2026 before closing Q4 2026." Reopen and close Q2 2026. Re-attempt Q4 2026. The system re-evaluates whether Q3 2026 is also affected, per the propagation-stops-at-first-unaffected rule.

**Open point, not yet decided:** exact display convention for {period}/{target} ("Q4 2026" confirmed; whether the predecessor's own period label or a date range is used needs one line of confirmation, not a redesign).

## Scope Out

Surfacing the full propagation chain (every affected period at once) as an informational aside in the Close Validation Status tab. Not requested by the Principal. Not authorized. Not included in this Brief.

Only the single oldest blocker is reported per close attempt, as specified above. The Builder is not to add a queue or chain display.

## Deferred / Future Scope (corrected 2026-09-28)

**Only the configurable Setup window is deferred, not close-order enforcement itself** (an earlier revision of this Brief mistakenly deferred the whole rule — corrected once the Principal clarified: "the normal behaviour" that should be built now IS chronological close-order enforcement, just without a forced historical backfill; see the confirmed bootstrap rule above).

What's deferred: a dedicated Setup button opening a separate window/panel where the bootstrap-baseline rule and other close-order parameters could be explicitly configured (e.g. an explicit cutoff period, or switching to stricter full-history enforcement), rather than the fixed "first close = baseline" default this Brief hardcodes. This is not authorized as buildable scope today: it has no acceptance criteria, no defined parameter set, and no Category A/B classification yet. It requires its own Required-Response-Format pass once the Principal is ready to scope it, per `ARCHITECT_SCOPE_REFUSAL_RULES.md` Rule 2 (a deferral is not a permanent veto) — logged here only so the decision trail is not lost.

## Implementation

**New function:** `find_close_order_blocker()` in `period_lifecycle.py`, called for `target_period` at two points — an early warning when the period is selected (D15 Section 5.B control), and a hard, authoritative re-check inside the Approve handler (both the live single-period "Approve close" handler and the reopen-candidate "Approve candidate close" handler) immediately before `archive_close()` runs, since the two checks can observe different states if time passes between selection and Approve:

1. Reads `close_history/_baseline.json`. Absent → this is the first close ever under this rule: never blocked by the close-order check, and on success this close's own period becomes the baseline (written once, never recomputed or moved afterward — design note §1). Present → the close-order check applies only to periods at or after `baseline_period` in `period_order`.
2. For every period between the baseline and `target_period` (using `period_order` position, not close timestamps), checks whether it is closed (`close_history.resolve_latest_approved_close_for_period()` returns non-`None`).
3. For each such period that IS closed, additionally checks `pending_reprocessing.json` (design note §2) via `find_blocking_predecessor()`'s existing logic, to catch the reopen-caused case.
4. Returns the single oldest blocking reason (never closed, or reopened/closed but caused unresolved downstream impact), in the wording specified above.

**New propagation-writing step and sidecar state (design note §2):** on a successful `archive_close()` for an explicit reopen (either Approve handler), `run_propagation_chain()` walks forward and writes `close_history/<PERIOD_LABEL>/pending_reprocessing.json` for each downstream period where `numerical_impact=True`, stopping at the first unaffected period per the existing 5.G contract. This is a new small sidecar file, structurally separate from versioned close snapshots (see design note §2 for why this cannot corrupt D10 immutability or Executive Ready). `reprocessing_state_by_period` (the dict `find_blocking_predecessor()` expects) is derived by checking each period for this file's presence, not a new complex data model.

**Call sites, verified against canonical code (Architect Verification, project doc):** the D15 5.B "Select period" control (`Northwind_Financial_Dashboard.py` \~line 942) is where the early warning renders. The live single-period close path's Approve handler is `st.button("Approve close", key="approve_close_btn")` (\~line 1370); the reopen-candidate path's is `st.button("Approve candidate close", key="approve_candidate_close_btn")` (\~line 2103). `find_close_order_blocker()` runs at selection (informational) and again inside both Approve handlers (authoritative, before `archive_close()`), and considers predecessors of the target only — never the target period itself, so a period's own approval can succeed even while it was itself the blocker on an earlier attempt. The check is procedural only: it never sets, clears, or implies Workflow State, Executive Ready, or any of the Human Approval Gate's eight criteria (D13) — see Testing for the required regression check.

**Persistence (consistent with Implementation above, design note §1–§2):** the close-order case needs one write-once sidecar (`close_history/_baseline.json`), written exactly once, the first time any period closes under this rule — never edited or recomputed afterward, so it cannot retroactively move as later periods close out of order. The reopen-caused case needs a per-period sidecar (`close_history/<PERIOD_LABEL>/pending_reprocessing.json`), written by the new propagation-writing step above and cleared when that period is itself reopened and re-closed. Neither sidecar is a new close-history *version* or schema change to the existing snapshot format — both live alongside, not inside, the versioned snapshot folders, so `resolve_latest_approved_close_for_period()` and Executive Ready logic never see them. `numerical_impact` itself is also being extended (Category B) to include sequential/QoQ variance fields, without which the reopen-caused case could never actually fire — see the design note §5 for exactly which fields and which outputs still need Builder confirmation.

**Definitions (non-timestamp-based, design note §3):** a period is **closed** iff `resolve_latest_approved_close_for_period(period)` returns non-`None`. A period is **resolved** (reprocessing sense) iff it has no `pending_reprocessing.json`, or that file is marked `resolved: true`. Neither uses `approval_timestamp`, consistent with avoiding the Item 2 cross-period timestamp-contamination defect.

**Edge cases (design note §4), explicitly resolved, not left implicit:**

- A downstream period already closed before an upstream reopen later affects it: this Brief does not retroactively invalidate its closed status. Out of scope whether its *content* should be reconsidered stale (that's OI-8/9/10/12 territory).
- Closing a period earlier than the last-closed one, and re-closing an already-closed period: both remain undefined/out of scope for this Brief, not silently permitted or blocked.
- A pending, unconfirmed reopen candidate: nothing persists until Approve succeeds; the period being reopened still reads as closed at its last approved version until then.

## Testing

**Unit:** `find_close_order_blocker()` tested in isolation with constructed `period_order` / Close History fixtures covering: no prior close at all, i.e. the very first close under this rule (must NOT block — confirmed bootstrap rule); one gap after the baseline; multiple gaps after the baseline; a resolved vs. unresolved reprocessing-required predecessor; a commentary-only downstream version (must not block).

**Integration:** live dashboard — the D15 5.B period-selection control (early warning) and both Approve handlers (`approve_close_btn`, `approve_candidate_close_btn`; hard block before `archive_close()`) correctly call `find_close_order_blocker()` and correctly suppress or enable the close workflow. Builder-run. Must include a regression check that none of the Human Approval Gate's eight criteria (D13) — Workflow State, Executive Ready, or any other approval-status field — are set, cleared, or implied by this check; the block is procedural only.

**Product test, end-to-end in the live app, on a clean Close History, run under Independent Test per the Validation Independence Principle, not Builder-verified:**

1. On a clean Close History, close Q1 2026 first (D15 Section 5.B "Select period" control) — confirm this is never blocked, since it is the baseline under the confirmed bootstrap rule.
2. With Q1 2026 closed, attempt Q4 2026 while Q2 2026/Q3 2026 remain unclosed. Blocked by Q2 2026, not Q1 2026 (Q1 is already closed and cannot be the blocker).
3. Continuing from step 1 (Q1 2026 already closed — do not reopen it here), close Q2 2026 and Q3 2026 in order. Then reopen Q1 2026 and re-close it, causing a QoQ impact on Q2 2026. Attempt to close Q4 2026 again. Blocked by Q2 2026 as the affected period, with the message naming Q1 2026 as the reopen that caused it. Both possible outcomes for the next step (Q3 2026 affected, and Q3 2026 unaffected) must be fixed in advance by Independent Test's fixtures, not decided by the Builder.
4. Reopen and close Q2 2026. Re-attempt the Q4 2026 close. Confirm the system correctly re-evaluates whether Q3 2026 is now also affected, per the propagation-stops-at-first-unaffected rule already built.

Can the intended user perform the complete close-order and reopen-propagation workflow in the actual canonical application without developer intervention? This Brief is not complete until all four product-test steps above pass in the live app under Independent Test, not merely until unit tests pass.

## Builder Package

**Acceptance criteria (mapped to test):**

1. First-ever close under this rule is never blocked (Unit; Product test step 1).
2. A period at or after the baseline that was never closed blocks a later target, naming the oldest such period (Unit; Product test step 2).
3. A period at or after the baseline that is closed but has an unresolved `pending_reprocessing.json` blocks a later target, naming the affected period and the reopen that caused it (Unit; Product test step 3).
4. Once the affected period is reopened and re-closed, the block clears and propagation re-evaluates the next period (Unit; Product test step 4).
5. A commentary-only reopen never sets `pending_reprocessing.json` and never blocks (Unit).
6. The check runs at both period-selection (informational) and inside both Approve handlers (authoritative, before `archive_close()`) (Integration).
7. The block never sets, clears, or implies any of the Human Approval Gate's eight criteria (D13) (Integration regression).
8. `numerical_impact`/`CANONICAL_COMPARISON_SET` correctly detects the QoQ effects specified in the design note §5, for the fields and outputs confirmed there (Unit).

**Files in scope:** `period_lifecycle.py` (new `find_close_order_blocker()`; new propagation-writing step using existing `run_propagation_chain()`); `Northwind_Financial_Dashboard.py` (both Approve handlers and the 5.B selection control — call sites only, per Implementation); `close_history.py` (new sidecar read/write helpers for `_baseline.json` and `pending_reprocessing.json`); the `CANONICAL_COMPARISON_SET` definition (Category B QoQ-field extension, design note §5).

**Files that must not change:** `close_history.py`'s existing versioned-snapshot format and `resolve_latest_approved_close_for_period()`/`resolve_latest_approved_close()` logic; D10 archival/immutability behavior; D13 Human Approval Gate criteria and their storage; any Executive Ready logic.

**Regression fixtures required:** the existing 49/49, 18/18, 31/31 and 32/32 fixture suites, plus `rollups.py` tie-outs, all passing unchanged; the Human Approval Gate's eight criteria unaffected (see acceptance criterion 7).

**Return Report:** Builder returns the fixture results above, the new unit-test results, and confirmation of which product-test steps were exercised in the Test Codespace — not as a substitute for the Independent Test product run required above, per `ARCHITECT_GITHUB_AND_EVIDENCE_RULES.md` §3 and §10 (Test Codespace/patches are not canonical; Builder narration is not verification).

## Dependencies

The OI-8 (out-of-period propagation, Critical) / OI-9 / OI-10 / OI-12 (stale dashboard after approval) Corrections Brief lands and is verified on canonical `main` before this Brief's product test is run (Principal-confirmed 2026-09-28, design note §6). Both defects touch the same Approve handlers this Brief modifies; sequencing first avoids a merge conflict and avoids a corrupted or stale product-test result being misread as this Brief's own failure.

## Governance Record

The full first-round Advisor Review, second-round Advisor Review, and Architect Verification against canonical `main` have been moved out of this Brief to keep it internally consistent, per the Advisor's explicit recommendation. Full text: project docs `architect_reviews/advisor_review_d15_items_3_4_builder_brief.md`, `architect_reviews/d15_items_3_4_architect_verification.md`, and `architect_reviews/d15_items_3_4_design_note.md` (which also records the second-round Advisor findings and their resolution).

## Scope Authorization Gate

**Brief Title:** D15 Items 3 & 4 — Chronological Close-Order Enforcement & Reopen-Propagation Blocking

**Status:** APPROVED — released to Builder. Principal Approval Gate confirmed by Gregory Harter, 2026-09-28 (explicit chat instruction: "So I approve everything. Give me the final builder brief. I will make it canonical and send it to the builder.").

### Category A — Already Authorized

| Requirement | Authoritative Source | Incorporated? |
| --- | --- | --- |
| Reopen-caused downstream QoQ impact requires reopen+close of that period before a later close | D15 architecture (Final), Handbook Items 3/4 | ☑ |
| Oldest-affected-period-first reporting | `run_propagation_chain()`/`find_blocking_predecessor()`, already built | ☑ |
| Commentary-only change never triggers downstream reprocessing | `reprocessing_required_for_downstream()`, already built and correct | ☑ |

### Category B — New Principal Decisions

| Requirement | Authorization Reference | Incorporated? |
| --- | --- | --- |
| Chronological close-order enforcement, built now | Principal, 2026-09-27; confirmed to build now, 2026-09-28 (chat) | ☑ |
| Bootstrap baseline rule: first close = baseline, no historical backfill, order enforced forward from there | Principal, confirmed 2026-09-28 via explicit question-and-answer | ☑ |
| Exact message wording, both cases, incl. Q1→Q2 correction | Principal, 2026-09-27–28 | ☑ |

### Category C — Genuine Conflicts

> No genuine conflict identified.

### Category D — Technical / Procedural Constraints

**Category D — technical/procedural constraints:** the `reprocessing_state_by_period` derivation does not exist yet and is genuine new implementation work, not a trivial wiring step. See Implementation above.

See table below: blocking for the reopen-caused case only — the close-order case is independent and unaffected by this constraint.

| Constraint | Workaround | Blocking? |
| --- | --- | --- |
| No live code path writes lineage metadata for a downstream period never itself explicitly reopened (Architect Verification, Blocker 3) | Wire the propagation walk (already-authorized D15 Item 3) as a genuine prerequisite for the reopen-caused case only | Blocking for the reopen-caused case; does not block the close-order case, which is independent |

### Category E — Architect Recommendations

| Recommendation | Reason | Principal Authorization |
| --- | --- | --- |
| Surface the full propagation queue, not just the single oldest blocker, in Close Validation Status | Usability — lets the user see the whole chain up front | ☐ Not authorized |

### Explicit Exclusions

| Exclusion | Reason | Authority |
| --- | --- | --- |
| Propagation-queue display (Category E above) | Not requested by the Principal | Principal, 2026-09-27 |
| Configurable Setup window for close-order parameters | Not yet scoped — no acceptance criteria or parameter set exists | Principal, 2026-09-28; see Deferred / Future Scope |

### Minimum-Scope Verification

☑ Minimum implementation identified (one function, split into a close-order check and a reopen-impact check, each independently testable) ☑ Claimed dependencies tested (existing propagation/blocking functions confirmed correct and reusable unmodified; Architect Verification against canonical `main`) ☑ Workarounds considered (bootstrap rule avoids historical-backfill workaround entirely; no new persistence needed for the close-order case) ☑ Optional architecture separated (propagation-queue display and Setup window both kept out, Categories E and Deferred/Future Scope) ☑ No unnecessary bundling introduced (close-order and reopen-propagation checks are independently buildable and testable, per Category D)

### Principal Approval Gate

Confirmed directly by the Principal, in chat, 2026-09-28 (not pre-ticked by the Architect — see Governance Record for the earlier, corrected error on this point):

☑ This Brief includes ALL requirements I have decided. ☑ This Brief includes NO product scope I did not authorize. ☑ The exclusions accurately represent my deferred/out-of-scope decisions. ☑ The Architect has not silently narrowed my authorized scope. ☑ The Architect has not silently expanded my authorized scope. ☑ Architect recommendations are clearly separated from mandatory scope. ☑ I understand that Builder implements ONLY the authorized scope in this Brief. ☑ If the Brief is incomplete, I will request clarification before issuing it.

**Approved by Principal:** Gregory Harter, explicit chat confirmation, 2026-09-28 **Date:** 2026-09-28

### Architect Attestation

☑ I reviewed the relevant Handbook and Decision Log. ☑ I reviewed the relevant canonical repository state (fresh clone, HEAD `242b518f9b9d139fa730c9386b928708acb133e2`, matches `origin/main`, clean tree). ☑ I classified all material scope. ☑ I applied the Required Response Format. ☑ I applied the Minimum-Scope Test where applicable. ☑ I did not bundle scope without authorization. ☑ I did not use technical preference as product authority. ☑ I did not silently narrow or expand Principal scope (an earlier same-day draft did narrow it in error — caught and corrected within this session before release; see the project doc recording that correction). ☑ This Brief accurately represents the authorized scope.

**Architect:** Claude (Architect role, this session) **Date:** 2026-09-28

---

**Release Rule:** per `ARCHITECT_SCOPE_AUTHORIZATION_GATE.md`, this Builder Brief is released only once the Principal Approval Gate above is explicitly confirmed by the Principal. That confirmation is recorded above. This Brief is RELEASED to Builder, subject to the Dependencies section above (Corrections Brief lands and is verified first).
