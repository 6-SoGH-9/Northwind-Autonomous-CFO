# Test Instructions — Close Validation Engine, Real-Data Sequential Methodology
**Status:** Standing methodology, adopted Cycle 3 (supersedes reliance on `close_v1_v2_simulation.py` as evidence of correctness)
**Applies to:** Any Test verification of `close_validation.py` (Phase 2/3 logic), starting with Cycle 3, Task 2
**Governing principle:** Validation Independence — see Handbook, Configuration Integrity Check section

---

## Why this exists

`close_v1_v2_simulation.py` was authored by Build and contains Build-chosen injected values. It remains useful as a **regression fixture** — confirming future code changes don't silently alter previously-verified behavior — but it cannot serve as evidence the validation engine is *generically correct*, since the same party who wrote the detection logic also wrote the only data it's ever been shown to catch. This methodology closes that gap using the real dataset, modified independently by Test, with Build never informed of what was changed or where.

## Input contract Test must prepare (per the Brief's scope boundary)

`close_validation.py` does not construct closes from raw data or interpret fiscal periods — that preparation is Test's responsibility for this methodology. Before running any scenario, Test must produce, for each close (A, B, C and their modified variants): expense data as `(Period, Department, Category, Amount)` rows and headcount data as `(Period, Department, Headcount)` rows, with `Period` as a plain label (e.g. `"FY2026-Q2"`) — the engine will never parse or validate it. When calling Phase 3, Test must explicitly identify which period is "current" and which is "prior"; the engine does not infer succession from the labels themselves.

## Precondition

`close_history.py`'s `archive_close()` is immutable by design — re-archiving a period label raises an error. The three scenarios below **must run in three completely separate `close_history/` directories**, never the same one, and never Live's. Collisions on period labels or cross-contamination of "latest approved close" resolution between unrelated scenarios would invalidate the results.

---

## Scenario 1 — Clean sequential run (false-positive check)

**Sandbox:** fresh, empty `close_history/` (Sandbox 1).

1. Archive Close A — real, unmodified dataset through Q2 FY2026. (Bootstrap path.)
2. Archive Close B — real, unmodified dataset through Q3 FY2026, validated against Close A. (Normal path.)
3. Archive Close C — real, unmodified dataset through Q4 FY2026, validated against Close B. (Normal path.)

**Expected result, at every step:** Phase 2 — zero flags. Phase 3 — zero flags.

**Proves:** the engine does not manufacture false positives on genuine, unmodified business data — a property no synthetic scenario alone can demonstrate.

---

## Scenario 2 — Historical revision detection (Phase 2)

**Sandbox:** fresh, empty `close_history/` (Sandbox 2, independent of Sandbox 1).

1. Archive clean Close A (same as Scenario 1, through Q2 FY2026, unmodified).
2. On a **copy** of the source dataset, modify exactly one value in **Q2 FY2026** (the only quarter overlapping the A→B transition) — a department/category combination different from the frozen fixture's (avoid R&D/Software & Tools). Keep the original value recorded before editing.
3. Archive Close B built from this modified dataset (through Q3 FY2026), validated against clean Close A.

**Expected result:** Phase 2 — exactly 1 flag, matching the exact value/department/category/date Test recorded before running. Phase 3 — zero flags.

**Proves:** historical-revision detection works on data the engine's author never saw or specified.

---

## Scenario 3 — Plausibility anomaly detection (Phase 3)

**Sandbox:** fresh, empty `close_history/` (Sandbox 3, independent of Sandboxes 1 and 2).

1. Archive clean Close A (unmodified, through Q2 FY2026).
2. Archive clean Close B (unmodified, through Q3 FY2026), validated against clean Close A.
3. On a **copy** of the source dataset, modify exactly one value in **Q4 FY2026** — a department/category combination different from the frozen fixture's (avoid G&A/Software & Tools) — sized to clearly exceed the documented plausibility threshold, with no corresponding headcount change in the approved band. Record the exact modification before running.
4. Archive Close C built from this modified dataset (through Q4 FY2026), validated against clean Close B.

**Expected result:** Phase 2 — zero flags (Q4 is new, not overlapping — nothing to diff). Phase 3 — exactly 1 flag, matching the exact value/department/category Test recorded before running.

**Proves:** plausibility detection works on an anomaly the engine's author never saw or specified.

---

## What Test must record before running each scenario (not after)

For Scenarios 2 and 3: the exact department, category, date, original value, new value, and expected flag — written down **before** execution. The Return Report should show the actual engine output checked against this prediction, not a post-hoc judgment of whether the output "looks right."

## What Test must never share with Build

The specific values, departments, categories, or dates used in Scenarios 2 and 3, at any point — before, during, or after the test. Build's role is limited to the generic engine and documented thresholds; knowledge of the specific test cases would undermine the independence this methodology exists to establish, for this and any future validation task.

## Status of `close_v1_v2_simulation.py` going forward

Retained as a **regression-only** fixture (per the Validation Independence Principle) — confirms code changes don't alter previously-verified behavior. Not cited as evidence of correctness in any Return Report or Handbook entry from this point forward; Scenarios 1-3 above are that evidence.
