# Return Report — D15 Items 3 & 4 (Chronological Close-Order Enforcement & Reopen-Propagation Blocking) and Subsequent Extensions

The point of origin for this whole batch is one Builder Brief: **D15 Items 3 & 4 — Chronological Close-Order Enforcement & Reopen-Propagation Blocking**, implemented directly by commit `b974176`. The other nine commits were not separately briefed — they arose during live testing of that delivery and of each other, and are Principal-directed corrections and extensions that went beyond what the Brief originally specified. Local HEAD is 10 commits ahead of canonical `6-SoGH-9/northwind-autonomous-cfo`, `main`. Nothing has been pushed or promoted — all 10 exist only in this working repo, awaiting Architect review and Principal promotion. Base commit for canonical: current `origin/main` tip at time of writing.

| # | Commit | Change | Scope |
| --- | --- | --- | --- |
| 1 | `b974176` | D15 Items 3 & 4: Chronological Close-Order Enforcement & Reopen-Propagation Blocking | **In scope — this is the Brief** |
| 2 | `f73fadb` | Block Approve-close and second reopen while a reopen is unresolved | Beyond Brief — live-testing finding |
| 3 | `7a8f3bd` | Auto-resolve the zero-net-change reopen guard instead of freezing the page | Beyond Brief — live-testing finding |
| 4 | `a273c52` | Reword the reopen-propagation close-order block message | Beyond Brief — Principal wording correction |
| 5 | `ff9de8e` | Two-tier per-period data sourcing (stop cross-period leakage) | Beyond Brief — Principal-directed architecture fix |
| 6 | `c9e9a1b` | Block silently-approved reopen candidates without a matching correction file | Beyond Brief — live-testing finding |
| 7 | `d43116b` | Freeze closed periods' derived/rollup tables | Beyond Brief — live-testing finding (consequence of #5) |
| 8 | `93ef3f0` | Show open-uncommented-observation notice even with zero commentary imported | Beyond Brief — live-testing finding |
| 9 | `11b3366` | Stop Phase 2 findings from generating Observation IDs / gating commentary | Beyond Brief — Principal directive |
| 10 | `48f0ab8` | Reopen-candidate commentary never merged into live session state | Beyond Brief — live-testing finding |

## Principal-approved scope beyond the D15 Items 3 & 4 Brief

As Principal, Gregory Harter reviewed each of commits #2–10 (table above) as it was found during live testing of the D15 Items 3 & 4 deliverable, and explicitly directed and approved implementing it — in every case going beyond what that Brief originally specified. None of these were unilateral Builder decisions: each is either (a) a defect the Brief's own text got wrong (e.g. the Edge Cases call reversed by commit `f73fadb`), (b) a live-testing finding the Principal directed be fixed on the spot (the majority), or (c) a wording/architecture correction the Principal specified directly (commits `a273c52`, `ff9de8e`). Where a change reopens or extends settled D15 architecture, that was done on explicit Principal instruction, not Builder initiative — consistent with the "no silent decisions" discipline this project runs under.

## Changes, oldest to newest

Each entry: what changed, why, files touched, how it was verified, and canonical status (all: **not yet promoted**).

### 1. `b974176` — D15 Items 3 & 4: Chronological Close-Order Enforcement & Reopen-Propagation Blocking

**Scope:** In scope — this commit *is* the D15 Items 3 & 4 Brief.

Implements `find_close_order_blocker()` and two persistence sidecars (`_baseline.json`, `pending_reprocessing.json`), wired into period selection (early warning) and both Approve handlers (hard block). Extends `CANONICAL_COMPARISON_SET` with each output's own QoQ variance field, Principal-confirmed 2026-09-28, so a pure QoQ-only effect from a reopen is detectable.

- **Files:** `Northwind_Financial_Dashboard.py`, `period_lifecycle.py`, `close_history.py`, `rollups.py`, new `build_test/d15_items_3_4_close_order_demo.py`
- **Verification:** existing suites unchanged (49/49, 18/18, 31/31, rollups' 16 tie-outs); new suite 25/25 covering the Brief's required unit cases plus the QoQ-detection acceptance criterion.
- **Regression:** `close_history.py` versioned-snapshot format, D10 archival/immutability, D13 Human Approval Gate criteria all confirmed unaffected.

### 2. `f73fadb` — Block Approve-close and second reopen while a reopen is unresolved

**Scope:** Beyond Brief scope — live-testing finding on the Brief's own delivery; reverses the Brief's Edge Cases text, per Principal direction.

Live-testing finding: an unresolved reopen on one period did not block Approve-close on a *different* period, silently archiving it while the original reopen sat dangling. **This explicitly reverses the D15 Items 3 & 4 Brief's own Edge Cases text** on this scenario, per Principal direction this session.

- **Files:** `Northwind_Financial_Dashboard.py`
- **Verification:** live Streamlit `AppTest` reproducing the exact reported repro; confirmed `archive_close()` does not run while blocked; confirmed "Start over" correctly unblocks.
- **Regression:** all 5 suites, 160 checks, unchanged.

### 3. `7a8f3bd` — Auto-resolve the zero-net-change reopen guard instead of freezing the page

**Scope:** Beyond Brief scope — live-testing finding on a rendering defect the Brief did not anticipate; Principal-directed fix.

Reported symptom: "I reopen a period, changed absolutely nothing, and I cannot do start over or cancel." The zero-net-change guard's `st.stop()` froze the entire render, hiding the Reject/Start-over controls. Fixed per the Principal's own proposed approach ("can't we just do it like clicking on start over").

- **Files:** `Northwind_Financial_Dashboard.py`
- **Verification:** live `AppTest`; confirmed state clears to step 0 exactly as Start Over does, nothing spurious written to Close History, a subsequent Approve-close on another period succeeds.
- **Regression:** 160/160 unchanged.

### 4. `a273c52` — Reword the reopen-propagation close-order block message

**Scope:** Beyond Brief scope — Principal-directed correction to the Brief's own Message Wording template.

Principal correction to the Brief's own Message Wording template: lead with the instruction, then the reason, phrased as the QoQ effect rather than "affected its figures." Single string change.

- **Files:** `Northwind_Financial_Dashboard.py`
- **Verification:** direct extraction and execution of the formatting function against the real blocker shape; output matched the requested wording exactly.
- **Regression:** 160/160 unchanged (no suite asserts on this string).

### 5. `ff9de8e` — Two-tier per-period data sourcing: stop cross-period leakage through reopen corrections and Phase 2's global baseline

**Scope:** Beyond Brief scope — Principal-directed architecture fix, based on the Principal's own Test 1/Test 2 live-testing findings.

Based on the Principal's own Test 1/Test 2 findings: a correction upload for one period could leak into another, never-closed period's figures. New `resolve_canonical_dataset_path()` and `assemble_governed_dataset()` (`period_lifecycle.py`) enforce: closed periods always source from their own approved snapshot; never-closed periods always source from the canonical dataset — never from another period's correction upload. `rollups.py`'s `find_raw_dataset()` now builds this governed composite. The dashboard's own Phase 2 call is fixed to use the same per-period resolution already applied elsewhere (Executive Ready, the reopen candidate pipeline). Phase 2 coverage extended from Expenses-only to Revenue, Headcount, and Budget vs Actual (budget integration), as an additive section, not reshaping the existing Verified observation register.

- **Files:** `Northwind_Financial_Dashboard.py`, `close_history.py`, `period_lifecycle.py`, `rollups.py`
- **Verification:** 160/160 existing suite; a targeted repro of the Principal's own Test 2 scenario (Q4 2024 no longer perturbed by an out-of-period Q2 correction); live `AppTest` confirming Q3 2024 (never closed) correctly reports Not Applicable instead of a spurious diff.

### 6. `c9e9a1b` — Block silently-approved reopen candidates that don't reflect an attached, unprocessed correction file

**Scope:** Beyond Brief scope — live-testing finding; Principal-directed fix.

Reported symptom: attaching a corrected dataset and clicking "Approve candidate close" directly (skipping "Run correction intake") appeared to silently close, but actually discarded the attached file. Fix: every candidate now fingerprints the file it was built from; Approve hard-blocks (with a banner warning beforehand) if the uploader currently holds a file the stored candidate doesn't match.

- **Files:** `Northwind_Financial_Dashboard.py`
- **Verification:** live `AppTest` reproducing the exact sequence; direct Approve-without-intake now blocks with a clear message; the legitimate intake→Approve path still succeeds.
- **Regression:** 160/160 unchanged.

### 7. `d43116b` — Freeze closed periods' derived/rollup tables, not just raw values

**Scope:** Beyond Brief scope — live-testing finding surfaced as a consequence of item 5's fix; Principal-directed.

The two-tier sourcing fix (#5) froze raw values correctly, but every cross-period *derived* metric (QoQ/YoY, PL rollups, margin/breadth/concentration, volume-rate bridges) still recomputed fresh — so a closed period's own QoQ could silently drift when a neighboring period was later corrected. Confirmed live: Q3 FY2026's QoQ moved from -5.12% (as approved) to -24.2% purely because Q2 was corrected — a change nobody reviewed or approved. New `period_lifecycle.freeze_closed_period_tables()` covers all \~34 period-indexed rollup tables.

- **Files:** `period_lifecycle.py`, `rollups.py`
- **Verification:** direct re-import confirming Q3's frozen row matches its originally-approved figures, Q2's own row reflects its correction, Q4 (never closed) stays fully live; reopen-candidate "what-if" preview independently re-confirmed to stay unfrozen (by design — it runs as a subprocess without `period_lifecycle.py` available).

### 8. `93ef3f0` — Show the open-uncommented-observation notice even with zero commentary imported

**Scope:** Beyond Brief scope — live-testing finding; Principal-directed fix.

Reported symptom: a correction produced a genuinely new Phase 3 observation, but Commentary Review showed only "No commentary imported yet this session" — no indication anything needed attention, discovered only after approval. Root cause: an early return in `_render_commentary_review_records()` skipped the open-observation notice whenever `commentary_records` was completely empty — exactly the state of a freshly-built reopen candidate.

- **Files:** `Northwind_Financial_Dashboard.py`
- **Verification:** live `AppTest`, three cases (the exact repro; nothing flagged; an already-commented observation) — all correct, no false positives, no regression to existing rendering.

### 9. `11b3366` — Stop Phase 2 findings from generating Observation IDs or gating Controller commentary

**Scope:** Beyond Brief scope — Principal directive on Controller-commentary workflow design, found during live testing.

Principal directive: a Phase 2 (raw-data diff against the prior approved close) row is not something a Controller can meaningfully narrate. Requiring commentary against it left the Controller with nothing to say and no way to satisfy the gate. Confirmed live: 6 real Phase 2 differences were showing as 6 "Historical Revision" entries demanding commentary. Fix: `build_observation_register()`'s Phase 2 branch removed — only Phase 3 rows receive Observation IDs; Phase 2 stays fully visible on its own dedicated section, untouched.

- **Files:** `Northwind_Financial_Dashboard.py`, `commentary_workflow.py`
- **Verification:** reproduced the real 6-row Phase 2 diff from this session's Q2 2026 test dataset — register now returns 0 rows for those 6, exactly 1 for the genuine Phase 3 anomaly. Full app confirmed via `AppTest`, zero exceptions.

### 10. `48f0ab8` — Fix: reopen-candidate commentary never merged into live session state

**Scope:** Beyond Brief scope — live-testing finding; Principal-directed fix.

After a correction candidate was approved, its accepted Controller commentary lived only in the candidate's own dict, never merged into the session-wide dict the workflow-state strip, closed-period Commentary Review, and Narrative tab all read from. It was archived correctly to Close History, but within the same session "Explanations Validated" stayed unchecked and the Narrative reported the accepted item as "UNRESOLVED (commentary process incomplete, not absent)" — reproduced live and independently confirmed by the Principal hitting the identical symptom.

- **Files:** `Northwind_Financial_Dashboard.py`
- **Verification:** full same-session `AppTest` walkthrough (close → reopen → correct → comment → approve) confirming "Explanations Validated" turns ✅ immediately and the Narrative correctly shows the accepted commentary under "Finance/CFO-Approved Explanations," with no "Unresolved" text remaining; regression-checked against the plain (never-reopened) close path, unaffected.

## Cumulative diff vs. canonical `main`

```
Northwind_Financial_Dashboard.py             | 611 ++++++++++++++++++++++++++-
build_test/d15_items_3_4_close_order_demo.py | 236 +++++++++++
close_history.py                             | 161 +++++++
commentary_workflow.py                       |  30 +-
period_lifecycle.py                          | 376 ++++++++++++++++-
rollups.py                                   | 274 ++++++++++--
6 files changed, 1619 insertions(+), 69 deletions(-)
```

No other files differ from canonical. Nothing has been pushed; all 10 commits sit locally, ready for Architect review and Principal-directed promotion.

## Setup Windows — planned future work (not yet implemented)

The Principal wants to add a **Setup Window**: a guided onboarding/configuration flow run once (or reopenable from settings) that walks a new user through configuring the app before first use — rather than requiring them to already understand `NORTHWIND_RAW_DATASET_PATH`, Close History bootstrap state, and canonical-dataset resolution up front.

This is a stated future direction only. No design, Builder Brief, or code exists for it yet. Flagging it here so it's on record ahead of a future Brief:

- **Likely scope:** a first-run (or Settings-triggered) screen collecting the choices `find_raw_dataset()` currently resolves silently — which canonical dataset to seed from, confirming Close History location, and any org-specific defaults — before the main dashboard is shown.
- **Dependency:** should be scoped against the two-tier sourcing architecture already in place (`assemble_governed_dataset()`, item 5 above) rather than introduce a second, competing configuration path.
- **Status:** idea only, pending a Principal-authored or Principal-approved Builder Brief before implementation begins.

## Architect review items (flagged, not resolved)

- **`CANONICAL_COMPARISON_SET` QoQ fields vs. D15 Brief Section 5.E:** the Brief's own raw-only comparison table does not list the QoQ fields added in commit `b974176`. Principal confirmed the QoQ additions live (2026-09-28), but the Brief text itself was never formally amended to match. Flagging so the Handbook/Brief record is reconciled, not silently left inconsistent.
- **Bug/Change 5** (replaced dataset ignored once Close History exists, root-caused to `find_raw_dataset()` prioritizing Close History): reproduced and parked at Principal instruction. Still open, not part of this batch.
- **Test-harness limitation, not a product defect:** Streamlit `AppTest`'s widget-state harvesting throws a `KeyError` on a stale `edit_text_{observation_id}` key once that widget has rendered and later stopped rendering in the same test session. Confirmed to occur identically against pre-fix code; worked around during verification (reading `at.session_state` directly rather than re-driving further UI widgets) rather than fixed, since it isn't product code.

## Regression status summary

All five existing regression suites (160 checks total) pass unchanged as of the last commit in this batch (`48f0ab8`). No suite assertion was modified to accommodate any of the 10 changes above.
