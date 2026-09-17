"""
D15 Sections 5.E/5.F/5.G/5.H — Builder regression fixture.

Per the Validation Independence Principle, this is Builder-authored
regression/demonstration evidence only: it proves period_lifecycle.py's
logic behaves as Builder intended against a fixture Builder itself
constructed, not that the requirement is generically correct against
arbitrary independent data. Independent Test evidence is still required
before D15's 5.E-5.H can move to Verified (Brief Section 8).

Run: PYTHONPATH=. python3 build_test/d15_5e_5g_5h_demo.py
"""
import os
import sys
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl
import period_lifecycle as PL

PASS = 0
FAIL = 0


def check(label, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"OK   {label}")
    else:
        FAIL += 1
        print(f"FAIL {label}")


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_XLSX = os.path.join(REPO_ROOT, "rollups_output.xlsx")
if not os.path.isfile(SOURCE_XLSX):
    print(f"SKIPPED: {SOURCE_XLSX} not found -- run rollups.py first to produce it.")
    sys.exit(0)

scratch = tempfile.mkdtemp(prefix="d15_5e_")
before_path = os.path.join(scratch, "before.xlsx")
after_path = os.path.join(scratch, "after.xlsx")
shutil.copyfile(SOURCE_XLSX, before_path)
shutil.copyfile(SOURCE_XLSX, after_path)

TARGET_PERIOD = "Q4 FY2026"

# =========================================================================
# 5.E — offsetting Department/Category change, per the Brief's worked
# example (X moves +$100k, Y moves -$100k, department total unchanged).
# Using Department "R&D", Category "Software & Tools" (X) / "Other Opex"
# (Y) at TARGET_PERIOD -- real values already present in the canonical
# workbook (see the "All Q4 FY2026 Department x Category cells" sample in
# close_orchestrator.py's own output for these two rows' real base
# values), shifted by a fully-specified, deterministic +/-$100,000.00.
# =========================================================================
wb = openpyxl.load_workbook(after_path)
ws = wb["Exp_by_Dept_Cat_Q"]
header = [c.value for c in ws[1]]
dept_col = header.index("Department") + 1
cat_col = header.index("Category") + 1
period_col = header.index("Fiscal Quarter") + 1
amount_col = header.index("Amount ($)") + 1

changed_x = changed_y = False
for row in ws.iter_rows(min_row=2):
    dept = row[dept_col - 1].value
    cat = row[cat_col - 1].value
    period = row[period_col - 1].value
    if dept == "R&D" and period == TARGET_PERIOD and cat == "Software & Tools":
        row[amount_col - 1].value = row[amount_col - 1].value + 100000.0
        changed_x = True
    if dept == "R&D" and period == TARGET_PERIOD and cat == "Other Opex":
        row[amount_col - 1].value = row[amount_col - 1].value - 100000.0
        changed_y = True
wb.save(after_path)
check("Fixture construction: found and modified BOTH R&D/Software & Tools (X) and R&D/Other Opex (Y) rows", changed_x and changed_y)

numerical_impact, results = PL.compare_period_outputs(TARGET_PERIOD, before_path, after_path)

check("compare_period_outputs(): numerical_impact = True overall (the offsetting change IS detected)", numerical_impact is True)
check(
    "Exp_by_Dept_Cat_Q shows impact at the offsetting change's own grain",
    results["Exp_by_Dept_Cat_Q"].impact is True and len(results["Exp_by_Dept_Cat_Q"].diffs_df) == 2,
)
check(
    "PL_Quarterly (company-level total) shows NO impact -- confirming the company-level check ALONE would have missed this",
    results["PL_Quarterly"].impact is False,
)
check("Rev_by_Region_Q unaffected by an expense-only change", results["Rev_by_Region_Q"].impact is False)
check("Rev_by_Product_Q unaffected by an expense-only change", results["Rev_by_Product_Q"].impact is False)
check("Headcount_Q unaffected by an expense-only change", results["Headcount_Q"].impact is False)
check("BvA_Q unaffected by an expense-only change (BvA compares vs. Budget, not vs. this before-workbook)", results["BvA_Q"].impact is False)

# --- No-change control: comparing the untouched workbook against itself -
numerical_impact_clean, results_clean = PL.compare_period_outputs(TARGET_PERIOD, before_path, before_path)
check("Zero false positives: comparing an unmodified workbook against itself shows numerical_impact = False", numerical_impact_clean is False)
check(
    "Zero false positives, per-output: all six outputs show no impact on a clean no-op comparison",
    all(not r.impact for r in results_clean.values()),
)

# =========================================================================
# 5.F — the three-way distinction test matrix (four combinations).
# =========================================================================
check(
    "5.F Row 1: explicit reopen source, numerical_impact=False -> reprocessing_required=True (recorded, not caused)",
    PL.reprocessing_required_for_explicit_reopen_source() is True,
)
check(
    "5.F Row 2: explicit reopen source, numerical_impact=True -> reprocessing_required=True",
    PL.reprocessing_required_for_explicit_reopen_source() is True,
)
check(
    "5.F Row 3: downstream, numerical_impact=False -> reprocessing_required=False (never True by regeneration alone)",
    PL.reprocessing_required_for_downstream(False) is False,
)
check(
    "5.F Row 4: downstream, numerical_impact=True -> reprocessing_required=True",
    PL.reprocessing_required_for_downstream(True) is True,
)

# =========================================================================
# 5.G — propagation and stopping rule, including the affected-then-
# unaffected two-hop case and the terminal-period no-op case.
# =========================================================================
period_order = ["Q1 FY2026", "Q2 FY2026", "Q3 FY2026", "Q4 FY2026"]

# Case: P1 reopened, P2 affected, P3 UNAFFECTED -> P4 never examined.
scripted_impact = {"Q2 FY2026": True, "Q3 FY2026": False, "Q4 FY2026": True}


def stub_compare_fn(period_label, predecessor_descriptor):
    return scripted_impact[period_label], f"{period_label}/v2"


steps = PL.run_propagation_chain("Q1 FY2026", period_order, stub_compare_fn)
check("5.G: propagation chain has exactly 3 steps (source P1, then P2, then P3 -- P4 never reached)", len(steps) == 3)
check("5.G: step 0 is the explicit-reopen source with trigger 'explicit reopen'", steps[0].trigger == PL.TRIGGER_EXPLICIT_REOPEN)
check("5.G: step 0's reprocessing_required is True unconditionally", steps[0].reprocessing_required is True)
check("5.G: step 1 (P2) is affected, reprocessing_required=True, trigger propagated from P1", steps[1].period_label == "Q2 FY2026" and steps[1].reprocessing_required is True and steps[1].trigger.startswith(PL.TRIGGER_PROPAGATED))
check("5.G: step 2 (P3) is examined (affected P2 did not stop propagation prematurely)", steps[2].period_label == "Q3 FY2026")
check("5.G: step 2 (P3) is unaffected, reprocessing_required=False, and propagation STOPS here", steps[2].reprocessing_required is False)
check("5.G: P4 is never examined at all (propagation correctly stopped at P3)", all(s.period_label != "Q4 FY2026" for s in steps))

# Case: immediately-unaffected downstream (P2 unaffected) -> stop at P2, P3/P4 never touched.
scripted_impact2 = {"Q2 FY2026": False}
steps2 = PL.run_propagation_chain("Q1 FY2026", period_order, lambda p, pred: (scripted_impact2[p], f"{p}/v2"))
check("5.G: immediately-unaffected P2 stops propagation after exactly 2 steps (source + P2)", len(steps2) == 2)

# Case: immediately-affected P2, P3, P4 all affected -> full chain examined.
scripted_impact3 = {"Q2 FY2026": True, "Q3 FY2026": True, "Q4 FY2026": True}
steps3 = PL.run_propagation_chain("Q1 FY2026", period_order, lambda p, pred: (scripted_impact3[p], f"{p}/v2"))
check("5.G: all-affected chain examines every downstream period (4 steps total)", len(steps3) == 4)

# Case: terminal-period reopen (no downstream periods) -> degrades to a no-op, no error.
steps_terminal = PL.run_propagation_chain("Q4 FY2026", period_order, stub_compare_fn)
check("5.G: terminal-period reopen produces exactly 1 step (source only), no error", len(steps_terminal) == 1)

# =========================================================================
# 5.H — chronological blocking.
# =========================================================================
state_blocked = {
    "Q1 FY2026": {"reprocessing_required": False, "resolved": True},
    "Q2 FY2026": {"reprocessing_required": True, "resolved": False},
}
blocker = PL.find_blocking_predecessor("Q3 FY2026", period_order, state_blocked)
check("5.H: P3 is blocked by unresolved P2, specific blocking predecessor identified", blocker == "Q2 FY2026")

state_unblocked = {
    "Q1 FY2026": {"reprocessing_required": False, "resolved": True},
    "Q2 FY2026": {"reprocessing_required": True, "resolved": True},  # re-approved
}
blocker2 = PL.find_blocking_predecessor("Q3 FY2026", period_order, state_unblocked)
check("5.H: once P2 is re-approved (resolved=True), P3 is no longer blocked", blocker2 is None)

state_never_affected = {
    "Q1 FY2026": {"reprocessing_required": False, "resolved": True},
    "Q2 FY2026": {"reprocessing_required": False, "resolved": True},
}
blocker3 = PL.find_blocking_predecessor("Q3 FY2026", period_order, state_never_affected)
check("5.H: a period that was never affected (reprocessing_required=False) is never a blocker", blocker3 is None)

# =========================================================================
# 5.I — lineage metadata shape.
# =========================================================================
meta_explicit = PL.build_lineage_metadata(trigger=PL.TRIGGER_EXPLICIT_REOPEN, comparison_result=results)
check("5.I: lineage metadata for an explicit reopen carries trigger='explicit reopen'", meta_explicit["trigger"] == "explicit reopen")
check("5.I: lineage metadata carries numerical_impact computed from the comparison result", meta_explicit["numerical_impact"] is True)
check("5.I: lineage metadata records the epsilon actually used, for audit", meta_explicit["epsilon_used"] == PL.PROPOSED_EPSILON)

meta_propagated = PL.build_lineage_metadata(trigger=f"{PL.TRIGGER_PROPAGATED} from Q1 FY2026/v2", predecessor="Q1 FY2026/v2")
check("5.I: propagated trigger correctly distinguishable from explicit reopen", meta_propagated["trigger"] != PL.TRIGGER_EXPLICIT_REOPEN and "Q1 FY2026/v2" in meta_propagated["trigger"])

shutil.rmtree(scratch, ignore_errors=True)

print()
print("=" * 70)
print(f"RESULT: {PASS} passed, {FAIL} failed")
print("=" * 70)
if FAIL:
    sys.exit(1)
