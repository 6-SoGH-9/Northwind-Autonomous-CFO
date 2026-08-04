# Builder Brief — Cycle 3, Task 3
**Status:** Active
**Depends on:** Cycle 3, Task 2 (`close_validation.py`) for the integration check in AC4 — can be built in parallel, but that check can't run until Task 2 delivers.

---

## Objective

Build the missing link: a raw dataset, plus a requested period cutoff, in → a validation-ready Close Object out, matching the input contract `close_validation.py` already expects (Task 2).

## Item 1 — `close_construction.py`

One function: takes the raw dataset and a requested fiscal cutoff (e.g. "through FY2026 Q3"), returns a Close Object — cumulative through that cutoff, not just the newest period.

**This is the one place fiscal-calendar logic belongs.** Unlike `close_validation.py`, which must stay period-agnostic, this module's entire job is period boundaries — apply D1 (fiscal year Jul-Jun) to slice the raw data correctly.

**Output shape**, per Task 2's contract:
- Expense data: `(Period, Department, Category, Amount)` rows, all periods up to and including the cutoff. `Period` labels assigned here become the opaque labels `close_validation.py` consumes downstream.
- Headcount data: `(Period, Department, Headcount)` rows, same range.

**Pure function, no side effects** — same discipline as `close_validation.py`: no file writes, no printing, no calls to `archive_close()`. Construction produces an in-memory object; approval and archival are separate steps this module does not perform.

## Acceptance Criteria

| # | Criterion |
|---|---|
| 1 | `close_construction.py` produces a Close Object for a given cutoff; no side effects (grep-checkable, same standard as Task 2) |
| 2 | Cumulative through cutoff confirmed — e.g. a "through Q3" object contains Q1-Q3 data, not just Q3 |
| 3 | Output shape matches `close_validation.py`'s documented input contract exactly (same column names, same `Period` label convention) |
| 4 | **Integration check** (once Task 2 available): a constructed close, fed into `close_validation.py` against a prior constructed close, reproduces the same clean result as Test's Scenario 1 (zero false positives on real, unmodified data) |
| 5 | 12/12 tie-outs unaffected — this module doesn't touch `rollups.py` |

Report with actual output — constructed data, actual grep results, actual integration-check output.
