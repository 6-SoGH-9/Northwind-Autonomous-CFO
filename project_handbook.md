# Northwind — Autonomous CFO Office — Project Handbook

**Status:** Living document. Contains only stable, approved information — not work in progress.
**Maintained by:** Architect/PM (Claude), updated after each reviewed Builder/Test Return Report.
**Handbook version:** 2.0
**Last updated:** D11 (Close Validation Engine) moved to Verified on fresh, independently-reproduced evidence. A fresh Test session — given only the governing methodology document, the canonical Q4 FY2026 dataset, `close_validation.py`, and `close_history.py`, with explicit instruction to disregard prior-conversation memory, prior Return Reports, prior test results, and prior datasets — executed Scenarios 1-3 and the immutability check against the real, unmodified Q2/Q3/Q4 FY2026 sequence with no substitution. The Architect independently re-executed the same harnesses against its own copy of the canonical dataset and reproduced every result exactly (Scenarios 1-3, immutability). The earlier v1/v2 rounds (dataset-short substitutions, and a since-corrected procedural claim Test sourced from memory rather than the governing document) are retained below as historical record only and are explicitly excluded from D11's evidence basis. Cycle 3 is closed; no open items remain.

---

## Current Release

| Field | Value |
|---|---|
| Product target version | v1.0 (Information Architecture frozen per Section 3) |
| Environment | **Live** |
| Current cycle | **Cycle 3 — complete and closed out.** Both tasks (D10 Close History, D11 Close Validation Engine) Verified, no open items. |
| Current task | **None active.** Cycle 3 is closed. Next work is the write-up document (Section 15 of the Architect's permanent instructions — a product deliverable, not governed by Builder/Test mechanics). |
| Current Builder Brief | None active. `builder_brief_cycle3_task2.md` archived. |
| Current status | Cycle 2 (Tasks 1–4), Cycle 3 Task 1, and Cycle 3 Task 2 **complete, passed, Verified, promoted to Live.** |
| Last approved milestone | Cycle 3, Task 2 — Close Validation Engine (Phase 2/3), Verified on the fresh, memory-independent Test session's evidence, independently reproduced by the Architect. |
| Next milestone | **Write-up document** — the actual graded deliverable. Zero remaining technical blocker. |

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

**Dataset Provenance Discipline (added Cycle 3, Task 2):** A dataset supplied to Test for a real-data validation methodology must be checked for actual coverage range before results are treated as satisfying the methodology's stated scenarios — the file's own contents govern, not its filename or an assumption about what it should contain. Consequences, standing:
- If a supplied dataset's coverage falls short of what a Test Instructions document specifies, Test flags this explicitly and either substitutes the closest genuine equivalent (clearly labeled as a substitution, never silently) or declines to proceed — fabricating synthetic "real" data to fill the gap is never acceptable under a real-data methodology.
- Silent substitution is prohibited. Transparent substitution, disclosed in the Return Report with an explicit mapping of what was asked for versus what was used, is acceptable interim protocol and does not itself constitute a failed test.
- Evidence produced against a substituted or short dataset is **provisional**, not Verified, until re-run against the canonical dataset the instructions actually specified.
- The Architect verifies dataset coverage directly (opening the actual file, checking min/max dates across every sheet the methodology touches) before accepting a Test Return Report's coverage claims as fact — this is the same "artifact overrides narration" discipline applied at the file-content level, not just the filename level.
- **Resolver hygiene corollary (added at Cycle 3 close-out):** once a canonical dataset is confirmed, any prior-round dataset files used only to build up to that confirmation (e.g. intermediate quarter-truncated versions used across a multi-round provenance sequence) must be kept outside the production resolver's search path — archived for evidence/traceability of the provenance chain, never left alongside the canonical file where a wildcard resolver could match more than one. This is a repository-hygiene rule, not a new architectural decision — it follows directly from `rollups.py`'s existing "exactly one match" resolution contract (Section 12).
- This round's sequence (Q2 dataset → flagged gap, substituted → Q3 dataset → flagged remaining gap → Q4 dataset → exact match, no substitution) is the discipline working as designed: Test independently rediscovering and flagging a provenance gap is a protocol success, not a defect to be smoothed over.

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
| 8 | Close Validation Status | Has this close been reconciled, are anomalies investigated, is it safe to publish? | Controller, FP&A | Close state (Workflow State Model), Explained/Partial/Unexplained counts, diff + plausibility flags | Flagship (differentiator) | **Built and Verified — Cycle 3, Task 2** |
| 9 | AI Executive Narrative | What's the board-ready explanation of this period? | CFO | Prose, 6 sections (Section 4 = "Investment Alignment," $-only) | Flagship | Built, regenerated Q4 FY2026 vs Q3 FY2026 |
| 10 | Executive Deliverables (HTML story, PPTX deck) | What do I hand to the Board? | Board | No new calc — presentation only | Flagship | **Pending — needs current file upload, Cycle 2 item 12 blocked** |

**Explicitly rejected metric:** department-level Revenue-per-Employee (attributes company-wide revenue to a single department's headcount — same structural fallacy as the original Contribution Margin design; see Decision Log).

## 4. Workflow Specification

Reused unchanged from `autonomous_cfo_office_master_brief.md`. Ten phases (0-9), modular, each consuming only the prior phase's defined output:

| Phase | Name | Status |
|---|---|---|
| 0 | Close Trigger | Simulated only (folder/naming convention) |
| 1 | Data Intake & Version Control | Simulated (Close v1/v2), in progress |
| 2 | Deterministic Validation | **Verified — Cycle 3, Task 2.** `close_validation.py` Phase 2 (historical-revision diff detection), independently tested against real data through Q4 FY2026 |
| 3 | Plausibility Review (AI) | **Verified — Cycle 3, Task 2.** `close_validation.py` Phase 3 (QoQ threshold + headcount-band plausibility), independently tested against real data through Q4 FY2026 |
| 4 | Commentary Matching | Not started — depends on Gregory's synthetic commentary |
| 5 | Finance Collaboration (draft email) | Not started |
| 6 | Explanation Validation | Not started |
| — | **Human Approval Gate** | Between Phase 6 and 7 — no executive output publishes without sign-off on the validated observation register |
| 7 | Executive Insight Engine | Reused (`northwind_narrative_prompt.md`) |
| 8 | Executive Deliverables | Reused (HTML story, deck) — pending file delivery |
| 9 | Knowledge Archive | Not started — single log entry only, explicitly framed as future architecture, not a learning system |

**Workflow State Model** (per close version): Close Received → Data Validated → Observations Generated → Awaiting Controller Input → Explanations Validated → Executive Ready → Published → Archived.

**Simulated close versions (Build/Test fixture only, regression use):** Close v1 = dataset truncated through Q3 FY2026. Close v2 = full dataset through Q4 FY2026 + two injected, exactly-documented changes (a historical revision to a closed period, a Q4 plausibility anomaly). Both clearly labeled as simulated, not real events, in the write-up. **Superseded, for genericity-proof purposes, by the Cycle 3 Task 2 real-data sequential methodology** — see Section 5's Validation Independence Principle and Section 9's Review & Acceptance History.

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
| D11 | **Close Validation Engine (`close_validation.py` Phase 2 historical-revision diff + Phase 3 plausibility/headcount-band check) is generically correct, not merely non-regressing against Build's own fixture.** | A fresh, memory-independent Test session — given only the governing methodology document, the canonical Q4 FY2026 dataset, `close_validation.py`, and `close_history.py` — ran Scenarios 1-3 and the immutability check against the real, unmodified Q2/Q3/Q4 FY2026 sequence with no substitution, using department/category/value combinations Test chose independently and never disclosed to Build. The Architect independently re-executed the same harnesses against its own copy of the canonical dataset and reproduced every result exactly. This satisfies the Validation Independence Principle's bar for a genericity claim. **Earlier v1/v2 rounds (dataset-short substitutions, and a procedural claim Test had sourced from prior-conversation memory rather than the governing document) are explicitly excluded from this evidence basis — see Section 9.** | Cycle 3, Task 2 | **Verified — Cycle 3, Task 2, on fresh-session evidence.** See Section 9 for full evidence chain. |
| D12 | **Canonical raw dataset is the Q4 FY2026 file (Jul 2023–Jun 2026), single file at repo root. The Q2 FY2026 and Q3 FY2026 intermediate files used during Task 2's provenance sequence are retained only as archived testing/provenance artifacts, outside the production resolver's search path.** | Principal confirmation, resolving the resolver-collision risk flagged at Task 2 close-out: `rollups.py`'s dataset resolver requires exactly one `*.xlsx` match; multiple dated dataset files at repo root would break it. The Q2/Q3 files have ongoing evidentiary value (they support the v1→v2→v3 evidence chain in Task 2's Return Reports) but no ongoing production role once Q4 superseded them. | Cycle 3 close-out | **Verified — principal-confirmed, resolver-hygiene action, not a code change.** |

## 6. Assumptions & Limitations (current, approved)

- Headcount is a stock: rollups report **average** (mean of monthly values) and **ending** (last month's snapshot) headcount, never a sum. Starting company-wide headcount (Jul 2023) = 135; ending (Jun 2026) = 167.
- Region/Product "Net of Allocated Cost" views are **two separate, partial views, not a full segment P&L.** Region view nets S&M+CS only; Product view nets R&D only. Neither is directed at a profitability claim — both are investment-proportionality views by design (D6).
- The mathematical-identity property (any proportional allocation key forces % to be identical across segments in a period) is documented as the reason cross-segment % was removed entirely, not disclaimed alongside it.
- No true volume/rate split exists for revenue or non-headcount expense categories (no unit/customer count in the data) — breadth/concentration measure used instead, named for what it is.
- Department-level Revenue-per-Employee is deliberately not built — see D7.
- Real historical closes: Close History is populated only from this project's own Cycle 3 activity to date — not a long production history — stated explicitly as a limitation, not hidden.
- Finance replies are drafted, never sent — Phase 6 validation runs against Gregory's synthetic commentary, not a live reply thread.
- Cross-close learning: Phase 9 is a single log entry, described as designed architecture, not a mature capability.
- `assumptions_and_limitations.md`'s worked-example dollar figures (e.g. Core Platform Net of R&D Cost) are rounded to the nearest dollar for readability; exact pipeline output carries cents (verified match: $1,638,011 documented vs. $1,638,011.09 computed).
- **Open item:** narrative generation's behavior when `ANTHROPIC_API_KEY` is not present (falls back to a "download prompt" button rather than generating text) has been observed in Test but is not yet formally decided as intended Live behavior vs. a gap — see Section 10.
- **Resolved:** the dataset-coverage gap that caused Task 2's Test evidence to be provisional through two prior rounds is closed — the canonical dataset now genuinely spans Jul 2023 through Jun 2026 (confirmed by direct inspection of all 5 sheets, not just the Expenses sheet the test scenarios exercised), and is the single file at repo root (D12).

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
| Close v1/v2 simulation + Close Validation Status page | **Done — Cycle 2 Task 3, verified: exact injected values, Phase 2/3 catch confirmed** (regression-only fixture as of Cycle 3 Task 2 — see Validation Independence Principle) |
| Dashboard dependency pin / Styler API | **Done — Cycle 2 Task 4.** `.applymap` → `.map`, `requirements.txt` added (pandas 2.2.3, numpy 2.5.1, openpyxl 3.1.5, streamlit 1.60.0), confirmed clean under fresh install via script-executing test (8/8 tabs, 0 exceptions) |
| Terminology sync (dashboard + rollups.py) | **Done — Cycle 2 Task 4.** Zero case-insensitive matches across all four files, confirmed against canonical store, not just session copy |
| Broken `.md` reference (lines 410/450) | **Done — Cycle 2 Task 4** |
| Close History resolution + archival (D10) | **Done — Cycle 3 Task 1, verified.** `close_history.py` (storage-neutral resolve/archive) + `rollups.py`'s `find_raw_dataset()` extended with dynamic resolution (env override → Close History lookup → bootstrap fallback). Bootstrap and normal paths both independently exercised via `close_orchestrator.py` (Build/Test only, not Live). Live's own Close History starts empty — the Cycle 3 Task 1 demo snapshots are verification artifacts, not seed data for production. |
| Close Validation Engine — Phase 2 (historical-revision diff) + Phase 3 (plausibility/headcount-band) (D11) | **Done — Cycle 3 Task 2, Verified on fresh-session evidence.** `close_validation.py` reviewed as clean interface (zero I/O, zero fiscal-calendar logic, zero injected literals). A fresh, memory-independent Test session ran 3 scenarios with predictions recorded in advance against the canonical Q4 FY2026 dataset, no substitution; the Architect independently reproduced every result. Zero false positives on clean data, both anomaly classes (historical revision, plausibility swing) caught exactly on cases Build did not construct. See Section 9 for why the earlier v1/v2/v3 rounds are excluded from this evidence basis. |
| Canonical dataset resolution (D12) | **Done — Cycle 3 close-out.** Single Q4 FY2026 file (Jul 2023–Jun 2026) at repo root; Q2/Q3 intermediate files archived outside the resolver's search path. Resolver-collision risk closed. |
| HTML story, PPTX deck | **Blocked — current files not yet supplied to Builder** |
| Write-up document (the actual graded submission) | **Not started — highest-priority open gap, now the only open gap** |
| Phases 4-6, 9 (commentary matching, email, validation, archive log) | Parked — depends on Gregory's synthetic commentary |

## 8. Builder Brief History

| Brief | Scope | Status |
|---|---|---|
| Cycle 1 | Rename/allocation fix (Professional Services exclusion), Close v1/v2 planning, decline orchestrator/learning-claims scope | Complete |
| Cycle 2 | Redesign Region/Product views (D6), Headcount correction (D7), Close v1/v2 simulation + Close Validation page | **Complete** — Tasks 1-3 and all follow-ups (line 163 caption, headcount-band rationale, narrative prompt sync) passed. HTML story/deck carved out, remains blocked. |
| Cycle 3 | Task 1 (Close History resolution/archival, D10); Task 2 (Close Validation Engine, Phase 2/3, D11); close-out (canonical dataset selection, D12) | **Complete.** All items Verified. Cycle formally closed. |

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
| Cycle 3, Task 2 | D11 — Close Validation Engine genericity, Validation Independence Principle, Dataset Provenance Discipline | **Pass — Verified, on fresh-session evidence.** | Implementation reviewed clean (zero I/O, zero fiscal-calendar logic, zero injected literals, independently re-verified by grep). **Historical record (v1/v2/v3, NOT part of D11's evidence basis):** an earlier Test session ran this methodology across three rounds as dataset coverage improved — v1 (dataset short, through Q2 FY2026 only) substituted the last 3 available real quarters and flagged the gap; v2 (dataset extended to Q3 FY2026) flagged the remaining gap; v3 (dataset extended to Q4 FY2026) ran the real, unmodified Q2/Q3/Q4 FY2026 window with no substitution and all three scenarios passed. Under direct questioning, that same session admitted its stated justification for the v1 substitution ("document gaps as an open item, don't fabricate data") had been asserted as if it were a rule written in `test_instructions_validation_methodology.md`, when it was in fact carried in from prior-conversation memory — the governing document contains no such contingency clause. This was a genuine procedural-independence failure, not a wording slip, and disqualifies v1 and v2 as authorized runs; it also means v3's own procedural claims (sandbox isolation, immutability, prediction timing) could not be trusted on that session's narration alone, even though v3 needed no substitution. **Fresh evidence actually underlying Verified status:** a new Test session, given only `test_instructions_validation_methodology.md`, the canonical Q4 FY2026 dataset, `close_validation.py`, and `close_history.py`, explicitly instructed to disregard all prior-conversation memory, prior Return Reports, prior test results, and prior datasets, independently re-derived and re-ran Scenarios 1-3 and the immutability check against the real, unmodified Q2/Q3/Q4 FY2026 sequence — predictions recorded before execution, department/category/value combinations chosen independently and never disclosed to Build, isolated sandboxes, full harness scripts and sandbox trees supplied as evidence. **The Architect independently re-executed the same harnesses against its own separately-obtained copy of the canonical dataset** (not the fresh session's sandbox copies) and reproduced every result exactly: Scenario 1 (0/0 flags at every step), Scenario 2 (Customer Success/Other Opex, $22,675.64→$27,675.64, 1 Phase 2 flag, 0 Phase 3 flags — exact match), Scenario 3 (Sales & Marketing/Other Opex, $47,857.52→$97,857.52, 0 Phase 2 flags, 1 Phase 3 flag at QoQ +38.42%/headcount change +1.0 — exact match), and immutability (`FileExistsError` on re-archiving an existing period label, triggered directly by the Architect, not just read from a report). The Architect also confirmed by direct code inspection that `archive_close()`'s `rollups_output_src` parameter is only copied to storage and never read by any Phase 2/3 logic, so the documented placeholder used for it has no bearing on the validation evidence. This — the fresh session's evidence plus the Architect's independent, code-level reproduction of it — is what D11's Verified status rests on, not the earlier v1/v2/v3 sequence. |
| Cycle 3 close-out | D12 — canonical dataset file selection, resolver-collision hygiene | **Pass — Verified.** | Principal confirmed the Q4 FY2026 file as sole canonical dataset at repo root; Q2/Q3 files to be retained only as archived provenance artifacts outside the resolver's search path. Not a code change — a repository-hygiene action within the principal's data-provenance authority (Section 8 of the Architect's instructions). |

**Cycle 2 close-out: all 9 Section 6 criteria met** for every artifact that currently exists (pipeline, dashboard, narrative prompt, close simulation, assumptions doc). Criteria 3-4 have no finding against the HTML story or PPTX deck because those artifacts don't exist yet — carved out of this promotion, not a failure of it.

**Cycle 3, Task 1 close-out:** D10 implementation status moved to Verified. Live's canonical data model is now the Approved Financial Close, with a minimal, storage-neutral resolution/archival layer in place. Full retention, querying across many closes, and lifecycle management remain deferred to Phase 9, per the task's explicit scope.

**Cycle 3, Task 2 close-out:** D11 implementation status moved to Verified. The Close Validation Engine (Phase 2 + Phase 3) is proven generically correct — not merely non-regressing — via a fresh, memory-independent Test session's evidence, independently reproduced by the Architect using the same code and harnesses against a separately-obtained copy of the canonical dataset. The Dataset Provenance Discipline this task's earlier v1/v2 rounds motivated adding to this Handbook remains standing procedure and is credited with surfacing the original coverage gap as a protocol success. Separately, the earlier session's admission that a stated justification for its v1 substitution had been sourced from prior-conversation memory rather than the governing document — not caught until directly challenged — is recorded as a genuine finding, not smoothed over: it is why v1/v2/v3 are retained here as historical record but excluded from D11's actual evidence basis, and why the fresh session was run under an explicit no-prior-memory instruction and then independently re-verified rather than accepted on its own narration.

**Cycle 3 close-out (full):** D12 implementation status moved to Verified. The resolver-collision risk flagged when the third dataset file arrived is resolved by principal decision: single canonical Q4 FY2026 file at repo root, Q2/Q3 files archived outside the resolver's search path. **Cycle 3 has no open items.** All three of its decisions (D10, D11, D12) are Verified.

**Status: promoted to Live.** Batch = `rollups.py`, `Northwind_Financial_Dashboard.py`, `northwind_narrative_prompt.md`, `assumptions_and_limitations.md`, `requirements.txt`, `close_history.py`, `close_validation.py`, `Northwind_Sample_Dataset.xlsx` (Q4 FY2026, single canonical file). **Excluded from Live** (Build/Test verification tools only): `close_v1_v2_simulation.py`, `close_orchestrator.py`, and the archived Q2/Q3 dataset provenance artifacts. HTML story and PPTX deck remain blocked on file delivery, carved out of this promotion.

## 10. Known Technical Debt

- **Documentation/implementation grain mismatch — open, non-blocking (identified during Cycle 3, Task 2 D11 review).** `test_instructions_validation_methodology.md`'s Input Contract describes `Period` with a quarter-grain example (`"FY2026-Q2"`), while `close_validation.py`'s own docstring names monthly-grain `Date` as "the expected production usage" for Phase 2. The methodology document itself states the engine never parses or validates the `Period`/key-column values, so this did not invalidate any test result — Phase 2's monthly-grain usage in both the disqualified v1/v2/v3 rounds and the fresh evidence run is directly supported by the code's own stated default and docstring, checked line-by-line. This is flagged as a documentation-alignment item (the Test Instructions' example should be updated to match the implementation's actual recommended grain), not a functional defect, and does not block D11.
- **Test procedural-independence finding — resolved via fresh session, Cycle 3 Task 2.** An earlier Test session, when directly challenged, admitted that its stated justification for substituting quarters in its first (v1) round — framed as "the document's own explicit principle" — had actually been carried in from a prior conversation's memory, not from the text of `test_instructions_validation_methodology.md` as supplied that session. The governing document contains no such contingency clause. This is recorded as a genuine procedural-independence failure: memory-derived assumptions were presented as document-mandated rules. It was not caught by the Architect's own review until specifically pressed on it, which is itself a gap in that review, not just Test's. Resolved for Task 2 by commissioning a fresh Test session under an explicit no-prior-memory instruction, whose results the Architect then independently reproduced end-to-end rather than accepting on narration (see Section 9). The three original Return Reports (v1/v2/v3) are retained as historical record but are explicitly excluded from D11's evidence basis. **Open question for future Test/Architect sessions on this project:** whether "fresh session, no prior-conversation memory, independently reproduced by the Architect" should become a standing requirement for any Return Report used to support a Verified/genericity claim, rather than a one-off recovery for this incident — not decided here, flagged for the principal.
- **Narrative prompt drift — resolved, Cycle 2 Task 3 Item 3.** `northwind_narrative_prompt.md` confirmed byte-identical in substance to `rollups.py`'s `SYSTEM_PROMPT`/`build_user_prompt` for rule 2c, Section 4, and the data block. Root cause was a project synchronization gap (the `.md` never received Task 1's edit in the copy carried forward across project restarts), not a pipeline defect. Recovery followed the Configuration Integrity Check procedure: regenerated from the verified-correct code, not from an unverified archive.
- **Promotion-pipeline sync gap — resolved, Cycle 2 Task 4.** A previously-accepted fix (Task 3/Item 3 terminology correction) was verified in a Builder session but never written to the canonical file store, so it did not appear in the batch Test actually received. Distinct from the earlier narrative-prompt drift (stale copy carried across restarts) — this was a fix that simply never left the session it was made in. Addressed structurally via the new Canonical Sync Verification procedure, not by re-fixing this instance alone.
- **Dataset provenance gap — resolved, Cycle 3 Task 2.** Test Instructions assumed a dataset through Q4 FY2026 while the file actually supplied initially only ran through Q2 FY2026. Resolved over three rounds by supplying progressively later canonical datasets (Q2 → Q3 → Q4 FY2026); Test transparently flagged the shortfall at each round rather than silently substituting or fabricating. New standing procedure added: Dataset Provenance Discipline (Section "Source of Truth").
- **Dataset resolver-collision risk — resolved, Cycle 3 close-out.** Three dataset files existed as candidates after Task 2's testing sequence, all matching `rollups.py`'s resolver filter. Principal confirmed the Q4 file as sole canonical file at repo root (D12); Q2/Q3 files archived outside the resolver's search path.
- **Trivial, non-blocking:** `rollups.py` lines 710 and 745 still say "segment margin" (not "contribution margin," so outside Criterion 4's literal scope, but inconsistent with D6's broader spirit of moving away from margin framing). Comments/print text only, no functional or criterion impact. Left as opportunistic cleanup, not worth a dedicated brief.
- **Deck/HTML story staleness:** `Northwind_Quarterly_AI_Deck.pptx` and `Northwind_Quarterly_AI_Story.html` are not in current Builder files (only a PDF version of the deck exists in Project). Do not reconstruct from the PDF — risks propagating stale content. Needs current files supplied before Task 1 item 12 can close.
- **Write-up document not started** — flagged repeatedly as the actual graded deliverable; everything else is supporting evidence. **Now the sole remaining open item in the entire project.**
- **Narrative-generation fallback behavior undecided.** With no `ANTHROPIC_API_KEY` present, the dashboard falls back to a "download prompt" button rather than generating narrative text. Observed in Test, not yet formally decided as intended Live behavior (consistent with the Human Approval Gate — a human reviews before anything narrative-facing publishes) vs. an unaddressed gap. Needs an explicit decision before Cycle 3 continues into narrative-touching work — though this no longer blocks the write-up, which can describe the fallback as designed behavior consistent with the Human Approval Gate unless/until decided otherwise.

## 11. Roadmap / Future Ideas

- **Write-up document — the only remaining work.** Problem statement, workflow architecture (leading with the close-workflow story per D6's demotion of the margin narrative), and phase explanations. Task 2's real Phase 2/3 evidence (Verified, D11) and Task 1's Close History evidence (Verified, D10) are both available to cite directly, with no caveats remaining.
- Deck + HTML story regeneration once current files are supplied (not a blocker for the write-up; the write-up is the graded artifact, these are supporting evidence — Section 15 of the Architect's instructions).
- Cycle 4 (parked, likely post-deadline or opportunistic): Phases 4-6 (commentary matching, drafted email, explanation validation) and Phase 9 log entry — blocked on Gregory's synthetic commentary.
- Optional: video walkthrough, if time allows before Aug 18.

## 12. Active File Manifest

What should sit in the active Build Project vs. external archive, and why. Re-evaluate this table whenever the file set changes — see the accompanying PM recommendation for full reasoning.

| File | Category | Why |
|---|---|---|
| Project Handbook | Required every session | The index and source of truth; nothing else makes sense without it |
| Current Builder Brief | Not applicable — none active | Cycle 3 closed; no open Brief until a new task is scoped |
| `rollups.py` | Required every session | The single pipeline; nearly every task touches or depends on it, and its own tie-out checks are the primary verification mechanism |
| `assumptions_and_limitations.md` | Required every session | Small; must be checked/updated whenever a decision or limitation is touched, so its absence risks silent contradiction |
| `Northwind_Financial_Dashboard.py` | Required only for dashboard/UI-related tasks | Large file; needed when a task touches layout, tabs, or charts, not for pure pipeline or write-up work |
| `northwind_narrative_prompt.md` | Required only for narrative/prompt-related tasks | Needed when a task touches narrative generation or prompt wording, not for pipeline-only or dashboard-layout-only work |
| `requirements.txt` | Required every session | Pins pandas/numpy/openpyxl/streamlit to the versions confirmed clean (Cycle 2 Task 4); a fresh unpinned install reproduces the pandas 3.0 `Styler.applymap` crash |
| `close_history.py` | Required every session | Storage-neutral Close History resolve/archive logic (D10); imported by `rollups.py`'s dataset resolution path |
| `close_validation.py` | Required every session | Phase 2 (historical-revision diff) + Phase 3 (plausibility/headcount-band) logic (D11); Verified Cycle 3 Task 2 |
| `Northwind_Sample_Dataset.xlsx` (canonical, single file — the Q4 FY2026 version) | Required every session | Raw data source `rollups.py` reads via its dataset resolution path; not generated by the pipeline, must be supplied. **Resolved (D12): this is now the only dataset file at repo root.** |
| `close_v1_v2_simulation.py` | Build/Test only — never Live | Verification tool for Phase 2/3 logic; imported by `close_orchestrator.py`. Not part of the Live batch — Live's Close History starts from real data, not simulation output. **Frozen as of Cycle 3, Task 2** — regression-only fixture, not evidence of generic correctness (see Validation Independence Principle). Not extended or modified by Build going forward. |
| `close_orchestrator.py` | Build/Test only — never Live | Same category as `close_v1_v2_simulation.py`: verifies Close History bootstrap + normal-path resolution logic. Unconditionally deletes any pre-existing `close_history/` on every run, by design, to prove the bootstrap path for real — must never run against a populated production Close History. |
| `Northwind__Sample_Dataset_-_Q2_26.xlsx`, `...Q3_26.xlsx` | Archive only — testing/provenance artifacts, outside resolver's search path | Retained for traceability of Task 2's v1→v2→v3 evidence chain (D12); must not sit at repo root alongside the canonical Q4 file or the resolver's "exactly one match" contract breaks |
| Archived Builder Briefs | Archive only | Traceability; content already distilled into the Decision Log and Section 8 |

**Dataset location (decided Cycle 3, Task 2 — Option B, confirmed by direct implementation inspection):** the bootstrap dataset lives at **repo root**, alongside the application files — not in a `data/` subdirectory. This matches the implementation exactly as built: `rollups.py` and `close_v1_v2_simulation.py` both resolve it via `glob.glob("*.xlsx")` in the current working directory, filtering for filenames containing `northwind`, `sample`, and `dataset` (case-insensitive) while excluding `output` — not an exact filename match. Exactly one match must exist, or the code raises an error rather than guessing. `NORTHWIND_RAW_DATASET_PATH` is the built-in override for any deployment that needs a different location. A `data/` subdirectory was considered and explicitly rejected for now — it would require a code change that doesn't exist yet; adopting it as documented "architecture" ahead of the implementation would recreate the exact Handbook/code mismatch this project has repeatedly had to resolve. Revisit only alongside an actual code change, not as a documentation update in isolation.

**Canonical dataset file selection (D12, resolved at Cycle 3 close-out):** the Q4 FY2026 file (Jul 2023–Jun 2026) is the single canonical dataset at repo root. The Q2 FY2026 and Q3 FY2026 files used during Task 2's provenance sequence are retained only as archived testing/provenance artifacts supporting the v1→v2→v3 evidence chain in the Task 2 Return Reports — they must not be committed at repo root alongside the canonical file, since the resolver's glob-based filter would then match more than one file and raise an error rather than resolving cleanly. This closes the open item flagged at the end of Task 2's review.

**Filename resolution precedent (Cycle 3, Task 2):** `Northwind_Financial_Dashboard.py` (underscore) was confirmed canonical by direct inspection of the actual file on disk, which contradicted its own internal docstring (which incorrectly claimed a space-variant run command) and contradicted this Handbook's prior text. The real artifact overrode both the code's own stale comment and the Handbook — evidence from the artifact itself outranks any other source, including this document, when they disagree. This Handbook has been corrected to match; if this file is ever renamed in the future, update here deliberately, not by inference.

| Archived Builder Return Reports | Archive only | Traceability; content already distilled into the Review & Acceptance History |
| `rollups_output.xlsx` | Regenerate while in progress; kept once archived | While a close is in progress: fully reproduced by running `rollups.py`, no architectural knowledge, don't keep. Once a close is approved: copied into that close's Close History snapshot as part of the permanent audit trail (D10) — same file, different rule depending on state. |

---

*Handbook conventions: this file is edited in place, not appended to. Superseded content is removed, not struck through. The Decision Log and Review & Acceptance History are the only sections that grow purely by addition; everything else reflects only the current state.*
SYNC TEST — 2026-08-08 — refresh verification
