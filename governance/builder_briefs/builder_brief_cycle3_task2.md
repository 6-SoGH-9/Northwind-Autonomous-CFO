# Builder Brief — Cycle 3, Task 2
**Status:** Active
**Precedence reminder:** Handbook > this Brief > code/docs > archived briefs > archived reports.
**Depends on:** Cycle 3, Task 1 (Close History resolution/archival) — Verified.

---

## Context

Per D10, the dashboard's Close Validation Status page (IA #8, the flagship differentiator) currently depends on `close_v1_v2_simulation.py` — a script built to prove Phase 2/3 catch two specific, pre-known injected anomalies. It was never built to run on an arbitrary real close against an arbitrary prior approved close. This task separates the two roles: a production validation engine, and a Build/Test fixture that verifies it.

**Explicitly not in scope:**
- No changes to `rollups.py`'s tie-out/allocation calculation logic.
- No changes to `close_history.py`'s resolve/archive functions (already correct, Task 1).
- No dashboard layout/UI changes beyond swapping the import source.
- No narrative-generation work (API-key decision remains deferred).

---

## Item 1 — Production module: `close_validation.py` as a reusable service, not a script

Create a module containing **only generic, reusable logic** — no hardcoded fiscal period labels (e.g. "Q4 FY2026"), no company-specific injected dollar amounts, no assumption about which department/category will be flagged. It must operate correctly on **any** current close compared against **any** prior approved close, including the case where there is no prior close at all.

**Interface requirement:** this module is a service, not a script.
- Expose functions with a clean interface — accept the current close's data and the latest approved close's data (or the resolved-close object from `close_history.resolve_latest_approved_close()`), return **structured results** (e.g. a dataclass, dict, or DataFrame of flagged rows).
- **No printing, no file writes, no CSV export, no dashboard/Streamlit calls, no filesystem side effects of any kind inside this module.** If a caller wants a CSV or a printed report, that's the caller's job, consuming this module's return value — not something the module produces itself.
- No demo-specific assumptions or injected constants — this was already required; the interface requirement makes it structurally harder to violate, since a pure function returning data has nowhere to hide a hardcoded print statement referencing a specific period.
- Designed to be callable identically from: the dashboard, the close-processing workflow, a future API, and any CLI utility. If any of those need different *output* (a rendered table, a CSV, an HTTP response), that formatting happens in the caller, not here.

**Phase 2 (deterministic diff):** compare a current close's raw data against the close returned by `close_history.resolve_latest_approved_close()`. Return flagged rows (overlapping periods with a nonzero difference) as structured data. If no prior approved close exists (bootstrap case), return a result that clearly represents "not applicable — no prior close to compare," not an error and not an empty result indistinguishable from "compared and found nothing."

**Phase 3 (plausibility review):** return flagged QoQ swings by Department × Category exceeding the approved threshold, where no explainable headcount driver exists within the approved band, as structured data. Per system rule 6, never assign a cause — the returned result states "driver not identifiable from segment-level data" when the threshold is crossed without a corresponding headcount change; this is data on the result object, not printed text.

**Input contract (must be explicit, not assumed):** `close_validation.py` validates two **already-prepared** close datasets — it does not construct a close from a raw dataset, and contains no fiscal-cutoff, quarter-boundary, or period-derivation logic of any kind. Constructing "a close through Q2/Q3/Q4" from the raw Northwind file is explicitly **out of scope for this task** — it's the responsibility of whatever calls this module (Test, for validation purposes now; a future workflow capability eventually — see "Flagged for future work" below).

Expected shape, both phases, both closes:
- **Expense data:** tabular, columns `Period` (an opaque label the caller assigns — the engine never parses it as a date, never derives "which quarter comes next," never validates it against a calendar), `Department`, `Category`, `Amount`.
- **Headcount data** (for Phase 3's driver check): same shape — `Period`, `Department`, `Headcount`.

**Phase 2** diffs rows where `(Period, Department, Category)` exists in both the current and prior close's expense data — "overlapping" means set intersection on those keys, nothing calendar-based.

**Phase 3** compares a "current period" against a "prior period" — the caller must explicitly identify which rows are which (e.g. two clearly separated inputs, or an explicit `prior_period_label` parameter) when calling the module. The engine performs arithmetic on two already-identified periods; it never decides for itself what "prior" means. This is the same principle as Phase 2's scope boundary, applied to comparison instead of construction — if the engine had to figure out fiscal succession itself, it would be back to owning period-boundary logic under a different name.

**Flagged for future work, not this task:** constructing "an approved close through a given cutoff" from the raw dataset doesn't currently exist as a capability anywhere in the project — Task 1 archives whatever it's handed, this task validates whatever it's handed, but nothing yet *builds* a close from raw data. Worth tracking as a Cycle 3, Task 3 candidate once the validation engine itself is done and verified.

**Document the actual threshold values in this module** (currently only living as comments inside the demo script): QoQ threshold and headcount-driver band, with their existing rationale (threshold set well above the historical max naturally-occurring move, not tuned to any specific case). State these as parameters with defaults, not literals buried in logic — flag in your Return Report whether these should be formally added to the Decision Log (D11) now that they're production policy rather than demo-only.

## Item 2 — Dashboard consumes the production module's structured results

The Close Validation Status page must call `close_validation.py`'s Phase 2/3 functions against real Close History data (via `close_history.resolve_latest_approved_close()`) and render the returned structured results itself — not import anything from `close_v1_v2_simulation.py`, and not expect the module to hand it pre-formatted display strings or files.

## Item 3 — `close_v1_v2_simulation.py` reclassified as a frozen regression fixture (Builder does not extend it)

**Governance change, effective this task:** the Builder's responsibility ends at the generic validation logic and documenting the business rules it implements. **The Builder does not author, extend, or modify test data or injected anomalies going forward.** This eliminates a real conflict of interest: the same author designing both an anomaly and the logic that detects it cannot demonstrate the logic is genuinely generic — at best it demonstrates the logic catches what its own author already knew was there.

Concretely for this task:
- `close_v1_v2_simulation.py`'s existing injected constants (HIST_REVISION, PLAUSIBILITY_ANOMALY) are **frozen as-is** — do not add, adjust, or tune anything in them, even if it would make a check pass more cleanly.
- Its only remaining purpose is **regression continuity**: confirming that extracting Phase 2/3 into `close_validation.py` didn't change behavior versus the baseline already established and reviewed back in Cycle 2, Task 3. This is a narrower claim than "the engine works correctly" — state it as regression-only in your Return Report, not as proof of genericity.
- Refactor it only to the extent needed to call the production module instead of owning the logic itself (as before), asserting against the same frozen constants (quarter-grain, per Item 4).

**Independent validation of genericity is explicitly out of this task's scope** — it happens at Test, using a dataset Test constructs independently (different department, category, and injected values than anything in this Brief or `close_v1_v2_simulation.py`), specifically so the engine is checked against an anomaly its own author never saw. Do not attempt to pre-empt this by adding your own additional test cases beyond the frozen regression fixture.

## Item 4 — Resolve the `observations.csv` grain discrepancy flagged in Task 1

Task 1's Return Report noted `close_v1_v2_simulation.py`'s hardcoded `observation_register` reports the injected anomaly at month-grain (privileged knowledge of the exact injection), while a real Phase 3 run reports it at quarter-grain (what the logic actually detects). Once Phase 3 lives in `close_validation.py`, the fixture's expected-output assertions must check against the **quarter-grain** result — the real thing the module produces — not the month-grain figure that only existed because the demo script knew its own injection in advance.

## Item 5 — `observations.csv` remains a caller-side artifact

Consistent with Item 1's interface requirement: `observations.csv` (produced when a close is archived, per Task 1's `close_history.archive_close()`) is built by whatever calls `close_validation.py` and archives the result — never written by the validation module itself. No separate design decision needed here; it's a direct consequence of the module having zero file-write side effects.

---

## Required before this task closes — independent validation at Test (not Builder's job)

Per the new Validation Independence principle: this task's own fixture (Item 3) only proves regression continuity, not genericity, because the same party (Builder) would otherwise be judging its own work against data it also controls. **Before Cycle 3, Task 2 can be marked Verified**, Test must construct its own close data independently — different department, category, and injected dollar swing than anything in this Brief or `close_v1_v2_simulation.py` — and confirm `close_validation.py` correctly flags it using only the documented generic thresholds, with zero code changes. This step is tracked separately in the Test instructions, not as an acceptance criterion the Builder self-certifies.

---

## Acceptance Criteria

| # | Criterion |
|---|---|
| 1 | `close_validation.py` exists; grep confirms zero fiscal-period-label or injected-dollar-amount literals in it |
| 1a | Grep confirms zero date-parsing, quarter-derivation, or calendar logic anywhere in the module — engine treats `Period` purely as an opaque caller-supplied label |
| 1b | `close_validation.py` contains zero `print(`, zero file-write calls (`open(...,'w')`, `.to_csv(`, etc.), and zero Streamlit/dashboard calls anywhere in the module — grep-checkable |
| 1c | Both Phase 2 and Phase 3 functions return structured data (not None, not printed text) — demonstrated by calling them directly and inspecting the return value, independent of the dashboard or the fixture |
| 2 | Dashboard's Close Validation Status page imports and calls `close_validation.py`, not `close_v1_v2_simulation.py`, and does its own rendering of the returned structured results |
| 3 | `close_v1_v2_simulation.py` contains no duplicated comparison/plausibility logic — calls the production module and asserts against known constants (quarter-grain, per Item 4) |
| 4 | Bootstrap case (no prior approved close) handled cleanly by Phase 2 — no error, explicit "not applicable" result, distinguishable from an empty comparison |
| 5 | Frozen fixture reproduces the exact same catches already verified (1 historical revision, 1 plausibility anomaly, matching documented constants) — confirms **regression continuity only** (extraction didn't change behavior vs. the Cycle 2 Task 3 baseline). This is not evidence the engine is generic — see Item 3 and the separate Test-stage requirement below. |
| 6 | 12/12 tie-outs still pass — no regression |
| 7 | Dashboard still renders 8/8 tabs, 0 exceptions (AppTest), now sourcing Close Validation Status from the production module |
| 8 | Threshold values (QoQ %, headcount-driver band) documented in the module with rationale; Return Report flags whether these warrant a formal Decision Log entry |

Report with actual grep output, actual test output, actual tie-out output — not status claims. Include the changed/new files alongside the report, not just a narrated account.
