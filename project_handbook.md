# Northwind — Autonomous CFO Office — Project Handbook

**Status:** Living document. Contains only stable, approved information — not work in progress.
**Maintained by:** Architect/PM (Claude), updated after each reviewed Builder Return Report.
**Handbook version:** 1.5
**Last updated:** Cycle 3, Task 2 briefed (Validation Independence Principle adopted; Task 2 itself not yet complete).

---

## Current Release

| Field | Value |
|---|---|
| Product target version | v1.0 (Information Architecture frozen per Section 3) |
| Environment | **Live** |
| Current cycle | Cycle 3 — Task 1 complete |
| Current task | None open — Cycle 3, Task 2 not yet briefed |
| Current Builder Brief | None active (`builder_brief_cycle3_task1.md` closed out) |
| Current status | Cycle 2 (Tasks 1–4) and Cycle 3 (Task 1) **complete, passed, promoted to Live.** Canonical object of the Live system is now the Approved Financial Close (D10), with a minimal Close History resolution/archival layer verified end-to-end (bootstrap path + normal path, both independently exercised). HTML story/deck still carved out, still blocked on file delivery. |
| Last approved milestone | Cycle 3, Task 1 — Close History bootstrap + normal-path resolution, verified against actual files |
| Next milestone | Write-up document (highest-priority open gap, zero remaining technical blocker); HTML story/deck once current files are supplied |

*A new Builder session should be able to read this table alone and know exactly where the project stands before opening anything else.*

## Source of Truth

When any two documents disagree, precedence resolves the conflict in this order:

1. **Project Handbook** (this document)
2. **Current Builder Brief**
3. **Current project code and documentation** (`rollups.py`, dashboard, `assumptions_and_limitations.md`, `northwind_narrative_prompt.md`)
4. **Archived Builder Briefs**
5. **Archived Builder Return Reports**

Archived documents (4, 5) exist for traceability only and must never override the current Handbook. If a discrepancy is found — e.g., code that doesn't match what the Handbook records, or a brief that references a superseded decision — the correct response is to flag it and update the Handbook (or correct the code, if the Handbook is right and the code drifted), never to silently defer to the lower-precedence source. This is the same discipline that caught the narrative-prompt drift in Cycle 2, Task 1 — applied now as a standing rule instead of something rediscovered each time.

**Configuration Integrity Check (standing procedure, added after the Cycle 2 Task 3 drift discovery):** A task is not accepted as Pass on code correctness alone. Every review must also confirm the active project's files are actually synchronized with what's being claimed as current, specifically:
- A case-insensitive (not case-sensitive) terminology resweep across every file the task touches or references, every time — not just after a rename task, and not assumed clean because a prior sweep passed.
- Where a `.md` template mirrors a code-embedded string (e.g., `northwind_narrative_prompt.md` vs. `rollups.py`'s `SYSTEM_PROMPT`), the review confirms **content correspondence** between the two directly — a clean grep on each file separately is not sufficient, since both files can independently pass a banned-terms sweep while still saying different things.
- When a discrepancy is found between an "accepted" state and the file currently in the project, the default recovery path is to **regenerate the drifted file from the verified-correct source already in the project** (usually the code), not to source a fix from an external archive of unconfirmed provenance — an unverified archived copy carries the same risk it's meant to resolve.
- This check does not depend on anyone's memory of which file was uploaded when — it's evidence-based, run fresh, every review.
- **Canonical Sync Verification (added after Cycle 2, Task 4):** A Return Report may only record a fix as "Pass" once the fix is confirmed present in a freshly-pulled copy of the canonical file set that feeds promotion — not merely verified in the session's working copy. A fix that only exists in-session is not yet a fix, regardless of how it was tested. This closes the specific failure mode found in Cycle 2 Task 4: a terminology correction was reviewed and accepted as Pass in Task 3/Item 3, but never propagated to the canonical store, so Test re-encountered the original defect.

**Self-healing boundary (added after Cycle 2, Task 3, Item 3):** if a review's own verification step (e.g., "resweep must show zero matches across all four files") reveals that a file has regressed from a *previously-approved, specific* fix, the Builder may reproduce that exact previously-approved content without waiting for a new brief — provided the fix is reported prominently, not silently absorbed into a "clean" claim. This is narrow: it covers restoring already-agreed content only. Any new label, threshold, structural change, or judgment call is not covered by this exception and still stops and flags rather than proceeds.

**Validation Independence Principle (added Cycle 3, Task 2):** The Builder may not be the sole author of both a piece of validation/detection logic and the test data used to prove that logic works. Doing so creates an unavoidable conflict of interest — logic can trivially "pass" a test whose specific values its own author already knew in advance, without that being evidence the logic is actually generic. This applies wherever Build produces a rule, threshold, or check meant to operate on arbitrary future data (e.g. Phase 2/3 plausibility and deterministic-diff logic). Consequences for roles:
- Builder's responsibility is limited to the generic logic itself and documenting the business rules it implements (thresholds, rationale).
- Builder does not author, extend, or tune test data, injected anomalies, or fixtures meant to prove that logic's correctness going forward.
- Data used to validate genericity must come from outside Builder's authorship — either genuine approved closes from Close History, or a dataset independently constructed by Test/Architect.
- Pre-existing Builder-authored fixtures (e.g. `close_v1_v2_simulation.py`) may still serve a **narrower** purpose — regression continuity, confirming a refactor didn't change behavior versus an already-established baseline — but must not be cited as proof of genericity. The two claims ("didn't regress" vs. "works generically") must be kept explicitly distinct in Return Reports and Handbook records.

This mirrors, at the role level, the same discipline Canonical Sync Verification already applies at the file level: evidence must come from somewhere the claim-maker doesn't fully control.

---

## 1. Project Vision

An AI-powered quarterly close workflow for a submission to the AI in Finance Challenge (deadline August 18). The differentiator is **not** any single KPI or dashboard page — it is the automation of the analyst-judgment step of financial reporting: validating numbers, flagging anomalies without inventing causes, matching real explanations to flagged items, and only then generating executive-ready narrative and deliverables, with a human approval gate before anything publishes.

The graded deliverable is a **single written document** (problem, workflow, impact). The dashboard, workbook, deck, and HTML story are supporting evidence for that document, not the product being judged in themselves.

**The canonical object this system manages is the Approved Financial Close** (see D10). The dashboard, executive narrative, and board deliverables are outputs generated from an approved close — evidence of what the workflow produced — not independent products in their own right. This distinction is architectural, not cosmetic: it's why the workflow diffs against a prior approved close (Phase 2), uses historical context for plausibility (Phase 3), and retains rather than overwrites each close (Workflow State Model, ending in Archived).

## 2. Product Principles

1. **Every number traces to a real calculation.** Nothing invented, nothing asserted without a corresponding figure in the data.
2. **Don't manufacture a metric the dataset can't support.** If a calculation requires more caveats to use safely than it delivers in insight, the calculation is wrong for the product, not just poorly labeled. (See Decision Log, Cycle 2.)
3. **Name metrics after the business question they answer, not the mechanics of how they're computed.** A CFO should understand a page title without opening it.
4. **Structural prevention over disclaimed caveats.** If a UI layout invites a wrong reading (e.g., a side-by-side % comparison), fix the layout — don't add a warning box next to the wrong reading.
5. **Every dashboard page answers exactly one business question**, has a defined primary audience, and does not overlap another page's job.
6. **Settled architectural decisions stay settled** unless a genuine defect is found — not a preference, not a stylistic reopening.
7. **Evidence over claims.** "Done" and "passed" require the actual output shown, not a status word.
8. **The Handbook is an index and a record of decisions, not a container for evidence.** It records what was decided and why, and points to where the proof lives (a Return Report, a tie-out log) — it does not reproduce that proof. This keeps the Handbook small and durable while keeping every claim in it checkable.
9. **A review checks configuration state, not just code correctness.** A task isn't verified merely because the logic is right — the active project's files must also be checked for drift against what was previously accepted as done. "Passed before, assumed synced since" is not evidence; a review that skips this can approve a project that quietly regressed to an earlier state.

## 3. Information Architecture (v1.0, frozen)

| # | Page | Business Question | Audience | Primary KPIs | Flagship / Supporting | Status |
|---|---|---|---|---|---|---|
| 1 | Executive Summary (KPI strip) | How did we do this period, at a glance? | CFO, Board | Revenue, Opex, Op. Profit, Op. Margin vs prior | Flagship | Built |
| 2 | Revenue Performance | Where is revenue growing/shrinking, broad-based or concentrated? | CFO, FP&A | Revenue by region/product, QoQ/YoY %, breadth/concentration, revenue mix % | Flagship | Built (Cycle 2 Task 2 added mix %) |
| 3 | Cost Structure | Which departments drive opex change, and why? | CFO, FP&A | Opex by dept, QoQ/YoY %, S&B volume/rate bridge, breadth/concentration; **Opex per Employee by dept** | Flagship | Built (Cycle 2 Task 2 added Opex/Employee) |
| 4 | Regional Revenue & Go-to-Market Investment | Is GTM spend proportionate to where revenue comes from, and is that shifting? | FP&A (primary), CFO (secondary) | Region Revenue ($), Allocated GTM cost ($), Net of GTM Cost ($); single-region % trend only | Supporting (demoted from flagship in Cycle 2) | Redesigned, built |
| 5 | Product Line Revenue & R&D Investment | Is R&D investment proportionate to revenue by product, and is that shifting? | FP&A (primary), CFO (secondary) | Product Revenue ($), Allocated R&D cost ($), Net of R&D Cost ($); single-product % trend only | Supporting (demoted from flagship in Cycle 2) | Redesigned, built |
| 6 | Headcount & Efficiency | Is headcount growth tracking ahead of, in line with, or behind revenue growth? | CFO, Board | Company-wide Revenue per Employee (trend), headcount growth % vs revenue growth %, headcount by dept (trend) | Flagship | Corrected (Cycle 2 Task 2 — removed dept-level Revenue/Employee) |
| 7 | Budget vs Actual / Variance Review | Which variances against plan need explanation, which are recurring? | CFO, Controller | Largest fav/unfav variances, Major Miss/Watch flags, consecutive-Watch streaks | Flagship | Built |
| 8 | Close Validation Status | Has this close been reconciled, are anomalies investigated, is it safe to publish? | Controller, FP&A | Close state (Workflow State Model), Explained/Partial/Unexplained counts, diff + plausibility flags | Flagship (differentiator) | **Not built — Cycle 2 Task 3, in progress** |
| 9 | AI Executive Narrative | What's the board-ready explanation of this period? | CFO | Prose, 6 sections (Section 4 = "Investment Alignment," $-only) | Flagship | Built, regenerated Q4 FY2026 vs Q3 FY2026 |
| 10 | Executive Deliverables (HTML story, PPTX deck) | What do I hand to the Board? | Board | No new calc — presentation only | Flagship | **Pending — needs current file upload, Cycle 2 item 12 blocked** |

**Explicitly rejected metric:** department-level Revenue-per-Employee (attributes company-wide revenue to a single department's headcount — same structural fallacy as the original Contribution Margin design; see Decision Log).

## 4. Workflow Specification

Reused unchanged from `autonomous_cfo_office_master_brief.md`. Ten phases (0-9), modular, each consuming only the prior phase's defined output:

| Phase | Name | Status |
|---|---|---|
| 0 | Close Trigger | Simulated only (folder/naming convention) |
| 1 | Data Intake & Version Control | Simulated (Close v1/v2), in progress |
| 2 | Deterministic Validation | Reused (`rollups.py` tie-outs), extended to Close v1/v2 diff — in progress |
| 3 | Plausibility Review (AI) | Extended from breadth/concentration logic — in progress |
| 4 | Commentary Matching | Not started — depends on Gregory's synthetic commentary |
| 5 | Finance Collaboration (draft email) | Not started |
| 6 | Explanation Validation | Not started |
| — | **Human Approval Gate** | Between Phase 6 and 7 — no executive output publishes without sign-off on the validated observation register |
| 7 | Executive Insight Engine | Reused (`northwind_narrative_prompt.md`) |
| 8 | Executive Deliverables | Reused (HTML story, deck) — pending file delivery |
| 9 | Knowledge Archive | Not started — single log entry only, explicitly framed as future architecture, not a learning system |

**Workflow State Model** (per close version): Close Received → Data Validated → Observations Generated → Awaiting Controller Input → Explanations Validated → Executive Ready → Published → Archived.

**Simulated close versions:** Close v1 = dataset truncated through Q3 FY2026. Close v2 = full dataset through Q4 FY2026 + two injected, exactly-documented changes (a historical revision to a closed period, a Q4 plausibility anomaly). Both clearly labeled as simulated, not real events, in the write-up.

## 5. Product Decisions — Decision Log

**Convention (added Cycle 3):** Decision Log entries are approved architectural direction, effective immediately upon being agreed — not contingent on implementation. Each entry carries an **Implementation Status**: `Planned` / `In Progress` / `Verified`. A decision's own text describes the decision only, never an implementation claim — "Verified" requires a reviewed Return Report with actual evidence, same bar as everywhere else in this Handbook.

| # | Decision | Rationale | Cycle | Implementation Status |
|---|---|---|---|---|
| D1 | Fiscal year = Jul-Jun, labeled by ending calendar year | Dataset's 36 months split into exactly 3 clean fiscal years on this convention | Pre-Cycle 1 | Verified |
| D2 | "Operating Profit/Margin," never "Gross Profit/Margin" | No COGS line in dataset | Pre-Cycle 1 | Verified |
| D3 | Segment allocation: S&M+CS → Region, R&D → Product, by revenue share; G&A excluded from both | No finer driver available (no rep count, no engineer count, no time-tracking) | Cycle 1 | Verified |
| D4 | Professional Services excluded from R&D allocation base | Real allocation error, not a labeling issue — Professional Services is a services line, not something R&D builds | Cycle 1, retained through Cycle 2 | Verified |
| D5 | BvA flag thresholds: Watch >4%, Major Miss >8% | Reverse-engineered from organizer's reference workbook, 100% match | Pre-Cycle 1 | Verified |
| D6 | **Region/Product allocation views redesigned from "margin" to "investment proportionality"** | Any proportional allocation key makes CM% mathematically identical across all segments in a period — not a labeling problem, a structural one. The metric required 5 simultaneous caveats to read safely and invited the one comparison (cross-segment %) that the math forbids. Renamed, cross-segment % removed entirely, replaced with $-only comparison + single-segment % trend. Demoted from flagship to supporting. | **Cycle 2** | Verified |
| D7 | Department-level Revenue-per-Employee rejected; company-wide Revenue/Employee and department-level Opex/Employee kept instead | Attributing company-wide revenue to one department's headcount reproduces the same attribution fallacy just removed in D6 — revenue isn't produced by a single department. Opex/Employee has no such problem (department's own cost over its own headcount). | Cycle 2 | Verified |
| D8 | Revenue Mix (%) added to Revenue Performance page | Independently varying (reflects real mix shift over time), not a ratio constructed from proportional allocation — does not reduce to D6's mathematical-identity problem | Cycle 2 Task 2 | Verified |
| D9 | `rename_instruction_contribution_margin.md` fully superseded | Superseded by D6; do not apply that file's renaming table in any future session | Cycle 2 | Verified |
| D10 | **Canonical object of the Live system is the Approved Financial Close, not a single active dataset. Live maintains an immutable Close History (one snapshot per approved close). The dashboard, executive narrative, and future board deliverables are outputs generated from an approved close, not independent products.** | The workflow already assumed this: Phase 2 diffs against a previous approved close, Phase 3 uses historical context, the Workflow State Model terminates in Archived (retained, not overwritten), Phase 9 was already framed as a Knowledge Archive. Storage mechanism (GitHub, for this challenge) is an implementation choice, not part of the decision. | Cycle 3 | **Verified — Cycle 3, Task 1.** Minimal folder-based Close History (resolution + archival) confirmed: bootstrap path and normal path both independently exercised (not hand-placed), dynamic resolution with zero hardcoded filenames, Phase 2/3 catches reproduced exactly against archived snapshots, no regression (12/12 tie-outs). Full retention/query/lifecycle management remains deferred to Phase 9, per scope. |

## 6. Assumptions & Limitations (current, approved)

- Headcount is a stock: rollups report **average** (mean of monthly values) and **ending** (last month's snapshot) headcount, never a sum. Starting company-wide headcount (Jul 2023) = 135; ending (Jun 2026) = 167.
- Region/Product "Net of Allocated Cost" views are **two separate, partial views, not a full segment P&L.** Region view nets S&M+CS only; Product view nets R&D only. Neither is directed at a profitability claim — both are investment-proportionality views by design (D6).
- The mathematical-identity property (any proportional allocation key forces % to be identical across segments in a period) is documented as the reason cross-segment % was removed entirely, not disclaimed alongside it.
- No true volume/rate split exists for revenue or non-headcount expense categories (no unit/customer count in the data) — breadth/concentration measure used instead, named for what it is.
- Department-level Revenue-per-Employee is deliberately not built — see D7.
- Real historical closes: only two simulated versions (Close v1/v2) demonstrated, not a long history — stated explicitly as a limitation, not hidden.
- Finance replies are drafted, never sent — Phase 6 validation runs against Gregory's synthetic commentary, not a live reply thread.
- Cross-close learning: Phase 9 is a single log entry, described as designed architecture, not a mature capability.
- `assumptions_and_limitations.md`'s worked-example dollar figures (e.g. Core Platform Net of R&D Cost) are rounded to the nearest dollar for readability; exact pipeline output carries cents (verified match: $1,638,011 documented vs. $1,638,011.09 computed).
- **Open item:** narrative generation's behavior when `ANTHROPIC_API_KEY` is not present (falls back to a "download prompt" button rather than generating text) has been observed in Test but is not yet formally decided as intended Live behavior vs. a gap — see Section 10.

## 7. Current Build Status

| Component | Status |
|---|---|
| Rollups (Revenue, Expenses, Headcount, BvA), QoQ/YoY | Done, verified, 12/12 tie-outs passing |
| Region/Product Investment views (redesigned) | Done — Cycle 2 Task 1 |
| Headcount & Efficiency correction | Done — Cycle 2 Task 2 |
| Opex per Employee (Cost Structure) | Done — Cycle 2 Task 2 |
| Revenue Mix (%) | Done — Cycle 2 Task 2 |
| Narrative prompt — `SYSTEM_PROMPT`/`build_user_prompt` in `rollups.py` and `northwind_narrative_prompt.md` template | **Done — both confirmed byte-identical in substance (rule 2c, Section 4, data block), Cycle 2 Task 3 Item 3** |
| Dashboard tab structure matching IA names | Done — Cycle 2 Task 1 |
| Close v1/v2 simulation + Close Validation Status page | **Done — Cycle 2 Task 3, verified: exact injected values, Phase 2/3 catch confirmed** |
| Dashboard dependency pin / Styler API | **Done — Cycle 2 Task 4.** `.applymap` → `.map`, `requirements.txt` added (pandas 2.2.3, numpy 2.5.1, openpyxl 3.1.5, streamlit 1.60.0), confirmed clean under fresh install via script-executing test (8/8 tabs, 0 exceptions) |
| Terminology sync (dashboard + rollups.py) | **Done — Cycle 2 Task 4.** Zero case-insensitive matches across all four files, confirmed against canonical store, not just session copy |
| Broken `.md` reference (lines 410/450) | **Done — Cycle 2 Task 4** |
| Close History resolution + archival (D10) | **Done — Cycle 3 Task 1, verified.** `close_history.py` (storage-neutral resolve/archive) + `rollups.py`'s `find_raw_dataset()` extended with dynamic resolution (env override → Close History lookup → bootstrap fallback). Bootstrap and normal paths both independently exercised via `close_orchestrator.py` (Build/Test only, not Live). Live's own Close History starts empty — the Cycle 3 Task 1 demo snapshots are verification artifacts, not seed data for production. |
| HTML story, PPTX deck | **Blocked — current files not yet supplied to Builder** |
| Write-up document (the actual graded submission) | **Not started — highest-priority open gap** |
| Phases 4-6, 9 (commentary matching, email, validation, archive log) | Parked — depends on Gregory's synthetic commentary |

## 8. Builder Brief History

| Brief | Scope | Status |
|---|---|---|
| Cycle 1 | Rename/allocation fix (Professional Services exclusion), Close v1/v2 planning, decline orchestrator/learning-claims scope | Complete |
| Cycle 2 | Redesign Region/Product views (D6), Headcount correction (D7), Close v1/v2 simulation + Close Validation page | **Complete** — Tasks 1-3 and all follow-ups (line 163 caption, headcount-band rationale, narrative prompt sync) passed. HTML story/deck carved out, remains blocked. |

*(Full brief text archived externally by PM, not retained in Project once superseded.)*

## 9. Review & Acceptance History

| Task | Criteria checked | Result | Evidence |
|---|---|---|---|
| Cycle 2, Task 1 | 1, 3, 4 | **Pass** | 12/12 tie-outs, zero diffs; grep swept twice (3 comment-only matches found and fixed, then zero); tab renames applied and confirmed via `st.tabs()` grep |
| Cycle 2, Task 2 | 5, 6 | **Pass** | 12/12 tie-outs, zero diffs; structural verification that dept-level Revenue-per-Employee is unconstructable (no revenue column in dept table, no Department column in company-wide table), not just absent from a text search |
| Cycle 2, Task 3 core | 7 (Close v1/v2 injected values, Phase 2/3 catch) | **Pass, accepted** | Exact injected values verified against CSVs; Phase 2 caught the 1 historical revision exactly; Phase 3 caught the 1 plausibility anomaly exactly, no cause guessed; dashboard state display honest (no Phase 4-9 overclaim) |
| Cycle 2, Task 3 follow-up, Items 1-2 | 4 (terminology), documentation | **Pass** | Line 163 before/after clean; assumptions-log entry quoted in full; 12/12 tie-outs, no regression |
| Cycle 2, Task 3 follow-up, Item 3 | 4 (terminology consistency, content correspondence) | **Pass, but scope-limited — see Task 4.** The fix was correctly made and verified in-session; it did not reach the canonical file store, so Test (Cycle 2 batch run) re-encountered the original defect. Not a false Pass on the work done — a gap in the promotion pipeline itself. Resolved by Cycle 2 Task 4 and the new Canonical Sync Verification procedure (Section 0). | Zero matches, case-insensitive, all four files; rule 2c/Section 4/data-block confirmed byte-identical to code, not just absent of banned terms; 12/12 tie-outs, no regression |
| Cycle 2, Task 4 | Dependency pinning, terminology sync (canonical), broken reference, no regression | **Pass** | 8/8 tabs render, 0 exceptions (AppTest, fresh install); 6→0 terminology matches across all 4 files, verified against canonical store; 12/12 tie-outs + both Close v1/v2 injections exact under pinned env; `.md`→`.py` references corrected; root cause of Task 3/Item 3's non-propagation identified and distinguished from the Section 10 pattern |
| Cycle 2 — Test Verification | Full Section 6 criteria, fresh env | **Pass** | 12/12 tie-outs $0.0000; 8/8 tabs, 0 exceptions (AppTest); pinned deps confirmed active; Phase 2/3 catches exact; terminology zero matches (independently re-swept); batch hashes recorded for traceability |
| Cycle 3, Task 1 | D10 — Close History resolution + archival, bootstrap and normal path, no regression | **Pass** | Bootstrap path forced via hard assertion (Close v1 could not be hand-placed); dynamic resolution confirmed zero hardcoded filenames (independent grep); Phase 2/3 catches reproduced exactly against archived snapshots; `metadata.json` includes real git commit hash per snapshot; 12/12 tie-outs, no regression; dashboard re-verified 8/8 tabs clean with Close History populated; `close_orchestrator.py` correctly excluded from Live scope and documented as Build/Test-only, confirmed via re-run after doc addition |

**Cycle 2 close-out: all 9 Section 6 criteria met** for every artifact that currently exists (pipeline, dashboard, narrative prompt, close simulation, assumptions doc). Criteria 3-4 have no finding against the HTML story or PPTX deck because those artifacts don't exist yet — carved out of this promotion, not a failure of it.

**Cycle 3, Task 1 close-out:** D10 implementation status moved to Verified. Live's canonical data model is now the Approved Financial Close, with a minimal, storage-neutral resolution/archival layer in place. Full retention, querying across many closes, and lifecycle management remain deferred to Phase 9, per the task's explicit scope.

**Status: promoted to Live.** Batch = `rollups.py`, `Northwind Financial_Dashboard.py`, `northwind_narrative_prompt.md`, `assumptions_and_limitations.md`, `requirements.txt`, `close_history.py`. **Excluded from Live** (Build/Test verification tools only): `close_v1_v2_simulation.py`, `close_orchestrator.py`. HTML story and PPTX deck remain blocked on file delivery, carved out of this promotion.

## 10. Known Technical Debt

- **Narrative prompt drift — resolved, Cycle 2 Task 3 Item 3.** `northwind_narrative_prompt.md` confirmed byte-identical in substance to `rollups.py`'s `SYSTEM_PROMPT`/`build_user_prompt` for rule 2c, Section 4, and the data block. Root cause was a project synchronization gap (the `.md` never received Task 1's edit in the copy carried forward across project restarts), not a pipeline defect. Recovery followed the Configuration Integrity Check procedure: regenerated from the verified-correct code, not from an unverified archive.
- **Promotion-pipeline sync gap — resolved, Cycle 2 Task 4.** A previously-accepted fix (Task 3/Item 3 terminology correction) was verified in a Builder session but never written to the canonical file store, so it did not appear in the batch Test actually received. Distinct from the earlier narrative-prompt drift (stale copy carried across restarts) — this was a fix that simply never left the session it was made in. Addressed structurally via the new Canonical Sync Verification procedure, not by re-fixing this instance alone.
- **Trivial, non-blocking:** `rollups.py` lines 710 and 745 still say "segment margin" (not "contribution margin," so outside Criterion 4's literal scope, but inconsistent with D6's broader spirit of moving away from margin framing). Comments/print text only, no functional or criterion impact. Left as opportunistic cleanup, not worth a dedicated brief.
- **Deck/HTML story staleness:** `Northwind_Quarterly_AI_Deck.pptx` and `Northwind_Quarterly_AI_Story.html` are not in current Builder files (only a PDF version of the deck exists in Project). Do not reconstruct from the PDF — risks propagating stale content. Needs current files supplied before Task 1 item 12 can close.
- **Write-up document not started** — flagged repeatedly as the actual graded deliverable; everything else is supporting evidence.
- **Narrative-generation fallback behavior undecided.** With no `ANTHROPIC_API_KEY` present, the dashboard falls back to a "download prompt" button rather than generating narrative text. Observed in Test, not yet formally decided as intended Live behavior (consistent with the Human Approval Gate — a human reviews before anything narrative-facing publishes) vs. an unaddressed gap. Needs an explicit decision before Cycle 3 continues into narrative-touching work.

## 11. Roadmap / Future Ideas

- Cycle 2 Task 3: Close v1/v2 simulation, Phase 2/3 execution, Close Validation Status page.
- Cycle 3 (parked): Phases 4-6 (commentary matching, drafted email, explanation validation) and Phase 9 log entry — blocked on Gregory's synthetic commentary.
- Deck + HTML story regeneration once current files are supplied.
- Write-up document — can and should start in parallel now; problem statement, workflow architecture (leading with the close-workflow story per D6's demotion of the margin narrative), and phase explanations don't depend on Task 3's output. Implementation-details section should wait for Task 3's real Phase 2/3 evidence.
- Optional: video walkthrough, if time allows before Aug 18.

## 12. Active File Manifest

What should sit in the active Build Project vs. external archive, and why. Re-evaluate this table whenever the file set changes — see the accompanying PM recommendation for full reasoning.

| File | Category | Why |
|---|---|---|
| Project Handbook | Required every session | The index and source of truth; nothing else makes sense without it |
| Current Builder Brief | Required every session | Defines the active task and acceptance criteria; moves to archive the moment it's superseded |
| `rollups.py` | Required every session | The single pipeline; nearly every task touches or depends on it, and its own tie-out checks are the primary verification mechanism |
| `assumptions_and_limitations.md` | Required every session | Small; must be checked/updated whenever a decision or limitation is touched, so its absence risks silent contradiction |
| `Northwind Financial_Dashboard.py` | Required only for dashboard/UI-related tasks | Large file; needed when a task touches layout, tabs, or charts, not for pure pipeline or write-up work |
| `northwind_narrative_prompt.md` | Required only for narrative/prompt-related tasks | Needed when a task touches narrative generation or prompt wording, not for pipeline-only or dashboard-layout-only work |
| `requirements.txt` | Required every session | Pins pandas/numpy/openpyxl/streamlit to the versions confirmed clean (Cycle 2 Task 4); a fresh unpinned install reproduces the pandas 3.0 `Styler.applymap` crash |
| `close_history.py` | Required every session | Storage-neutral Close History resolve/archive logic (D10); imported by `rollups.py`'s dataset resolution path |
| `Northwind_Sample_Dataset.xlsx` | Required every session | Raw data source `rollups.py` reads via its dataset resolution path; not generated by the pipeline, must be supplied |
| `close_v1_v2_simulation.py` | Build/Test only — never Live | Verification tool for Phase 2/3 logic; imported by `close_orchestrator.py`. Not part of the Live batch — Live's Close History starts from real data, not simulation output. **Frozen as of Cycle 3, Task 2** — regression-only fixture, not evidence of generic correctness (see Validation Independence Principle). Not extended or modified by Build going forward. |
| `close_orchestrator.py` | Build/Test only — never Live | Same category as `close_v1_v2_simulation.py`: verifies Close History bootstrap + normal-path resolution logic. Unconditionally deletes any pre-existing `close_history/` on every run, by design, to prove the bootstrap path for real — must never run against a populated production Close History. |
| Archived Builder Briefs | Archive only | Traceability; content already distilled into the Decision Log and Section 8 |
| Archived Builder Return Reports | Archive only | Traceability; content already distilled into the Review & Acceptance History |
| `rollups_output.xlsx` | Regenerate while in progress; kept once archived | While a close is in progress: fully reproduced by running `rollups.py`, no architectural knowledge, don't keep. Once a close is approved: copied into that close's Close History snapshot as part of the permanent audit trail (D10) — same file, different rule depending on state. |

---

*Handbook conventions: this file is edited in place, not appended to. Superseded content is removed, not struck through. The Decision Log and Review & Acceptance History are the only sections that grow purely by addition; everything else reflects only the current state.*
