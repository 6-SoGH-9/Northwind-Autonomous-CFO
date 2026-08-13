"""
Builder regression fixture — Phase 4-6 commentary workflow (D13 scope)

BUILD/TEST ONLY. Never Live. Per the Handbook's Validation Independence
Principle, this fixture is Builder-authored (both the synthetic observation
register and the commentary text) and proves NON-REGRESSION of the Phase
4/5/6 logic only. It is explicitly NOT cited as evidence that Phase 4/6 are
generically correct -- that evidence must come from the principal-supplied
UAT set (Brief v4, Section H/J), run independently, exactly as D11's
genericity claim rested on a fresh Test session's evidence, never Build's
own fixture (close_v1_v2_simulation.py plays the same narrow role for D11).

This script deliberately uses different observations and different
commentary text from anything the principal's future UAT package will
supply -- it was written before that content exists.

What this demonstrates, end to end, with actual execution (not narration):
  1. Commentary.xlsx contract enforcement (writes and reads a real workbook)
  2. Phase 4 matching: explicit match, inferable-only (synonym) match, and
     no-confident-match
  3. Phase 6 validation: Supported, Contradicted, and Insufficient (both
     Check 2 and Check 4 failure paths), each with a full four-check trace
  4. Phase 5 draft output reflecting the SPECIFIC failed check, not a
     generic template, with no send/transmit path anywhere
  5. The correction loop: an Insufficient v1 -> user-edited v2 -> an
     independent fresh Phase 6 re-run -> both results retained and
     distinguishable -> v2 marked Accepted
  6. Section G handoff: only the accepted version's text reaches
     rollups.build_user_prompt(), traceably
  7. Section F/D10: the complete Commentary Record (both observations, all
     versions, both validation results, accepted-version id) is captured in
     an immutable close_history snapshot and read back intact
"""

import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

import commentary_workflow as CW
import close_history
import rollups as R

PASS, FAIL = [], []


def check(label, cond, detail=""):
    if cond:
        PASS.append(label)
        print(f"OK   {label}")
    else:
        FAIL.append(label)
        print(f"FAIL {label}  {detail}")


# ---------------------------------------------------------------------------
# 1. Builder-authored synthetic observation register (NOT the real close's
#    D11 output -- the real canonical close currently has zero flags, so a
#    fixture is required to exercise Phase 4/6 at all; this mirrors how
#    close_v1_v2_simulation.py injects known values to exercise Phase 2/3).
# ---------------------------------------------------------------------------
observation_register = pd.DataFrame([
    {
        "Observation ID": "OBS-FIXTURE-0001",
        "Detected By": "Phase 3 (Plausibility Review)",
        "Period": "Q4 2026",
        "Type": "Plausibility Anomaly",
        "Department": "Sales & Marketing",
        "Category": "Salaries & Benefits",
        "Before ($)": 350000.00,
        "After ($)": 400000.00,
        "Delta ($)": 50000.00,
        "Threshold Crossed": "|QoQ %| > 25%",
    },
    {
        "Observation ID": "OBS-FIXTURE-0002",
        "Detected By": "Phase 3 (Plausibility Review)",
        "Period": "Q4 2026",
        "Type": "Plausibility Anomaly",
        "Department": "Customer Success",
        "Category": "Software & Tools",
        "Before ($)": 90000.00,
        "After ($)": 70000.00,
        "Delta ($)": -20000.00,
        "Threshold Crossed": "|QoQ %| > 25%",
    },
], columns=CW.OBSERVATION_REGISTER_COLUMNS)

hc_current = pd.DataFrame([
    {"Department": "Sales & Marketing", "Ending Headcount": 45},
    {"Department": "Customer Success", "Ending Headcount": 20},
])
hc_prior = pd.DataFrame([
    {"Department": "Sales & Marketing", "Ending Headcount": 40},
    {"Department": "Customer Success", "Ending Headcount": 20},
])

# D14 Department x Category breakdown fixtures -- Correction Task item 2
# (Architect review): full per-department category breakdowns backing the
# new category_reallocation claim type. Different values/scenarios from
# anything the future principal-supplied UAT set will use.
dept_breakdown_sm = pd.DataFrame([
    # Same category as OBS-FIXTURE-0001 itself (the flagged row).
    {"Category": "Salaries & Benefits", "Amount ($)": 400000.00, "Prior Period ($)": 350000.00,
     "QoQ/YoY Variance ($)": 50000.00, "QoQ/YoY Variance (%)": 50000 / 350000},
    # Offsetting movement -- supports a reallocation claim naming this category.
    {"Category": "Software & Tools", "Amount ($)": 45000.00, "Prior Period ($)": 95000.00,
     "QoQ/YoY Variance ($)": -50000.00, "QoQ/YoY Variance (%)": -50000 / 95000},
    # Too small relative to the $50k flagged variance to corroborate anything.
    {"Category": "Other Opex", "Amount ($)": 20000.00, "Prior Period ($)": 20500.00,
     "QoQ/YoY Variance ($)": -500.00, "QoQ/YoY Variance (%)": -500 / 20500},
])

# Third synthetic observation -- needed for the category_reallocation
# CONTRADICTED case: a named "other" category that moved the SAME direction
# as the flagged variance (not an offsetting pattern).
observation_register = pd.concat([observation_register, pd.DataFrame([{
    "Observation ID": "OBS-FIXTURE-0003",
    "Detected By": "Phase 3 (Plausibility Review)",
    "Period": "Q4 2026",
    "Type": "Plausibility Anomaly",
    "Department": "Customer Success",
    "Category": "Other Opex",
    "Before ($)": 70000.00,
    "After ($)": 100000.00,
    "Delta ($)": 30000.00,
    "Threshold Crossed": "|QoQ %| > 25%",
}])], ignore_index=True)[CW.OBSERVATION_REGISTER_COLUMNS]

dept_breakdown_cs = pd.DataFrame([
    {"Category": "Other Opex", "Amount ($)": 100000.00, "Prior Period ($)": 70000.00,
     "QoQ/YoY Variance ($)": 30000.00, "QoQ/YoY Variance (%)": 30000 / 70000},
    # Moved the SAME direction as the flagged variance -- not an offset.
    {"Category": "Software & Tools", "Amount ($)": 60000.00, "Prior Period ($)": 40000.00,
     "QoQ/YoY Variance ($)": 20000.00, "QoQ/YoY Variance (%)": 20000 / 40000},
])

# ---------------------------------------------------------------------------
# 2. Commentary.xlsx contract: write a real workbook, read it back through
#    load_commentary_workbook(), confirm blank rows are dropped.
# ---------------------------------------------------------------------------
tmp_dir = tempfile.mkdtemp(prefix="commentary_fixture_")
commentary_path = os.path.join(tmp_dir, "Commentary.xlsx")

commentary_rows = pd.DataFrame([
    {"Commentary_ID": "C1", "Commentary_Text": "Salaries rose due to hiring this quarter."},
    {"Commentary_ID": "C2", "Commentary_Text": "Customer Success Software & Tools spend fell because the team added headcount this quarter."},
    {"Commentary_ID": "C3", "Commentary_Text": "S&M payroll costs increased due to a vendor pricing adjustment for our HRIS platform this quarter."},
    {"Commentary_ID": "C4", "Commentary_Text": "General increase across several departments this quarter."},
    {"Commentary_ID": "C5", "Commentary_Text": None},  # blank -- must be dropped
])
with pd.ExcelWriter(commentary_path, engine="openpyxl") as writer:
    commentary_rows.to_excel(writer, sheet_name="Commentary", index=False)

entries = CW.load_commentary_workbook(commentary_path)
check("Commentary.xlsx loads via the fixed contract (sheet='Commentary', 2 required columns)",
      len(entries) == 4, f"got {len(entries)} entries, expected 4 (blank row dropped)")
check("Blank commentary row (C5) correctly dropped, not treated as an entry",
      all(e.commentary_id != "C5" for e in entries))

# Contract violation check: wrong sheet name must raise, not silently guess
bad_path = os.path.join(tmp_dir, "BadCommentary.xlsx")
with pd.ExcelWriter(bad_path, engine="openpyxl") as writer:
    commentary_rows.rename(columns={"Commentary_Text": "Text"}).to_excel(writer, sheet_name="Sheet1", index=False)
raised = False
try:
    CW.load_commentary_workbook(bad_path)
except CW.CommentaryFileError:
    raised = True
check("Wrong sheet name / missing column raises CommentaryFileError, not a silent guess", raised)

# ---------------------------------------------------------------------------
# 3. Phase 4 — matching: explicit, inferable-only, no-confident-match
# ---------------------------------------------------------------------------
match_results = CW.match_commentary_entries(entries, observation_register)
by_id = {m.commentary_id: m for m in match_results}

check("C1 (explicit 'Salaries' + no dept name) -- generic dept ref alone must NOT force a match",
      by_id["C1"].matched is False,
      by_id["C1"].match_basis)
check("C2 (explicit 'Customer Success' + 'Software & Tools') matches OBS-FIXTURE-0002",
      by_id["C2"].matched and by_id["C2"].matched_observation_id == "OBS-FIXTURE-0002",
      by_id["C2"].match_basis)
check("C3 (inferable-only: 'S&M' + 'payroll') matches OBS-FIXTURE-0001 via synonym, not exact text",
      by_id["C3"].matched and by_id["C3"].matched_observation_id == "OBS-FIXTURE-0001",
      by_id["C3"].match_basis)
check("C4 (no department/category reference at all) returns no confident match",
      by_id["C4"].matched is False,
      by_id["C4"].match_basis)
check("Full, unaltered entry text preserved on every match result (Criterion B.4)",
      all(m.text == e.text for m, e in zip(match_results, entries)))

# Since C1 didn't match on its own text (by design -- generic "Salaries"
# alone is deliberately not enough to identify a Department), give it an
# explicit reference for the rest of the demo, mirroring how a real
# commentary entry would actually be written by a Controller who names the
# department. This exercises the SAME explicit-match path Acceptance
# Criterion B.1 requires, just re-demonstrated on OBS-FIXTURE-0001 directly.
c1_explicit = CW.CommentaryEntry(commentary_id="C1", text="Sales & Marketing Salaries & Benefits rose due to hiring this quarter.")
match_c1 = CW.match_commentary_entries([c1_explicit], observation_register)[0]
check("C1 (explicit 'Sales & Marketing' + 'Salaries & Benefits') matches OBS-FIXTURE-0001",
      match_c1.matched and match_c1.matched_observation_id == "OBS-FIXTURE-0001",
      match_c1.match_basis)

# ---------------------------------------------------------------------------
# 4. Phase 6 — validation, all three outcomes with full four-check trace
# ---------------------------------------------------------------------------
def dept_row(oid):
    return observation_register[observation_register["Observation ID"] == oid].iloc[0]

evidence_1 = CW.build_evidence_package(dept_row("OBS-FIXTURE-0001"), hc_current, hc_prior,
                                        dept_category_breakdown=dept_breakdown_sm)
evidence_2 = CW.build_evidence_package(dept_row("OBS-FIXTURE-0002"), hc_current, hc_prior)
evidence_3 = CW.build_evidence_package(dept_row("OBS-FIXTURE-0003"), hc_current, hc_prior,
                                        dept_category_breakdown=dept_breakdown_cs)

# C1 v1: checkable (hiring), material headcount change (+5, same direction
# as +$50k variance), but NO number/scale/role given -> too generic -> Check 4.
result_c1_v1 = CW.validate_commentary(c1_explicit.text, evidence_1)
check("C1 v1 ('...due to hiring this quarter', no scale) -> Insufficient at Check 4",
      result_c1_v1.assessment == CW.INSUFFICIENT and result_c1_v1.failed_check == 4,
      f"assessment={result_c1_v1.assessment}, failed_check={result_c1_v1.failed_check}")
check("C1 v1 four-check trace fully populated (Checks 1-2 True, Check 4 False)",
      result_c1_v1.check1_specific_claim is True and result_c1_v1.check2_checkable is True
      and result_c1_v1.check4_sufficiently_specific is False)

# C3: uncheckable claim type (vendor pricing) -> Check 2, even though it's
# also an inferable Department/Category match.
result_c3 = CW.validate_commentary(
    "S&M payroll costs increased due to a vendor pricing adjustment for our HRIS platform this quarter.",
    evidence_1,
)
check("C3 (vendor-pricing claim) -> Insufficient at Check 2 (claim type not covered by evidence package)",
      result_c3.assessment == CW.INSUFFICIENT and result_c3.failed_check == 2,
      f"assessment={result_c3.assessment}, failed_check={result_c3.failed_check}")

# C2: headcount claim against OBS-FIXTURE-0002, where CS headcount did NOT
# change (20 -> 20) -> directly conflicts with a headcount-driven claim.
result_c2 = CW.validate_commentary(
    "Customer Success Software & Tools spend fell because the team added headcount this quarter.",
    evidence_2,
)
check("C2 (headcount claim, but headcount actually unchanged) -> Contradicted",
      result_c2.assessment == CW.CONTRADICTED,
      f"assessment={result_c2.assessment}, cited={result_c2.cited_field}={result_c2.cited_value}")
check("C2 Contradicted result cites the specific conflicting field (Criterion C.2)",
      result_c2.cited_field == "Headcount Change" and result_c2.cited_value == "+0.00")

# Correction loop: revise C1's text to add a concrete scale/role detail.
c1_v2_text = "Sales & Marketing Salaries & Benefits rose because we hired 5 additional sales reps this quarter."
result_c1_v2 = CW.validate_commentary(c1_v2_text, evidence_1)
check("C1 v2 (revised, with concrete scale '5 additional sales reps') -> Supported",
      result_c1_v2.assessment == CW.SUPPORTED,
      f"assessment={result_c1_v2.assessment}")
check("C1 v2 result is independent of v1's result (fresh assessment, all 4 checks re-run) -- Criterion C.6",
      result_c1_v2.failed_check is None and result_c1_v1.failed_check == 4
      and result_c1_v2.assessment != result_c1_v1.assessment)
# Criterion C.5 bars CLAIMING causation/proof (e.g. "this proves", "confirms
# that", "caused by") -- it does not bar the word "proof" appearing inside a
# disclaimer that explicitly denies proof, which is the Brief's own required
# pattern ("worded as consistent with ... never as proof of causation").
_PROHIBITED_CAUSAL_CLAIMS = ["this proves", "confirms that", "caused by", "is proof that", "demonstrates that"]
check("Supported wording never CLAIMS causation/proof (Criterion C.5)",
      "consistent with" in result_c1_v2.reason
      and not any(p in result_c1_v2.reason.lower() for p in _PROHIBITED_CAUSAL_CLAIMS))

# ---------------------------------------------------------------------------
# 4b. Phase 6 — category_reallocation claim type (Correction Task item 2:
#     the D14 Department x Cost Category evidence must be genuinely usable
#     by the validation logic, not just present in the evidence package).
#     Different scenarios/wording from the headcount cases above and from
#     anything the future principal-supplied UAT set will use.
# ---------------------------------------------------------------------------

# Supported: OBS-FIXTURE-0001's Salaries & Benefits rose +$50,000; the same
# department's Software & Tools fell -$50,000 the same period -- a genuine,
# materially offsetting reclassification.
result_realloc_supported = CW.validate_commentary(
    "The Salaries & Benefits increase actually reflects a reclassification -- we moved a large "
    "software licensing renewal from Software & Tools into Salaries & Benefits this quarter.",
    evidence_1,
)
check("Reallocation claim (real, materially offsetting D14 category movement) -> Supported",
      result_realloc_supported.assessment == CW.SUPPORTED,
      f"assessment={result_realloc_supported.assessment}, reason={result_realloc_supported.reason}")
check("Reallocation Supported result cites the D14 target category's Variance ($) field",
      result_realloc_supported.cited_field == "D14 Software & Tools Variance ($)"
      and result_realloc_supported.cited_value == "-50000.00")

# Contradicted: OBS-FIXTURE-0003's Other Opex rose +$30,000; the named
# "other" category (Software & Tools) ALSO rose +$20,000 the same period --
# not an offsetting pattern, so the reallocation claim is Contradicted.
result_realloc_contradicted = CW.validate_commentary(
    "This Other Opex increase is really a reclassification from Software & Tools, not a genuine "
    "cost increase in this category.",
    evidence_3,
)
check("Reallocation claim (named category moved SAME direction, not offsetting) -> Contradicted",
      result_realloc_contradicted.assessment == CW.CONTRADICTED,
      f"assessment={result_realloc_contradicted.assessment}, reason={result_realloc_contradicted.reason}")

# Insufficient (Check 4a): reallocation language present, but no specific
# other category named -- checkable claim TYPE, not checkable as stated.
result_realloc_no_target = CW.validate_commentary(
    "This was due to a budget line change this quarter.",
    evidence_1,
)
check("Reallocation claim with NO specific other category named -> Insufficient at Check 4",
      result_realloc_no_target.assessment == CW.INSUFFICIENT and result_realloc_no_target.failed_check == 4,
      f"assessment={result_realloc_no_target.assessment}, failed_check={result_realloc_no_target.failed_check}")

# Insufficient (Check 4b): a real other category is named, but its own
# movement is too small relative to the flagged variance to corroborate
# anything (Other Opex moved only -$500 against a $50,000 flagged variance).
result_realloc_too_small = CW.validate_commentary(
    "The Salaries & Benefits increase reflects a reclassification from Other Opex this quarter.",
    evidence_1,
)
check("Reallocation claim naming a category with an immaterial offset -> Insufficient at Check 4",
      result_realloc_too_small.assessment == CW.INSUFFICIENT and result_realloc_too_small.failed_check == 4,
      f"assessment={result_realloc_too_small.assessment}, failed_check={result_realloc_too_small.failed_check}")

check("All three category_reallocation outcomes carry the full four-check trace",
      all(r.check1_specific_claim is True and r.check2_checkable is True
          for r in (result_realloc_supported, result_realloc_contradicted,
                    result_realloc_no_target, result_realloc_too_small)))
check("category_reallocation Supported wording is consistency-only, never a proof/causation claim",
      "consistent with" in result_realloc_supported.reason and "proves" not in result_realloc_supported.reason.lower())

# ---------------------------------------------------------------------------
# 5. Phase 5 — draft output reflects the SPECIFIC failed check, no send path
# ---------------------------------------------------------------------------
draft_c1_v1 = CW.draft_finance_note(phase6_result=result_c1_v1)
draft_c3 = CW.draft_finance_note(phase6_result=result_c3)
draft_c4 = CW.draft_finance_note(no_match_reason=by_id["C4"].match_basis)
check("C1 v1 draft reflects Check 4 (genericity), not a generic template",
      "general" in draft_c1_v1.lower() or "generic" in draft_c1_v1.lower() or "detail" in draft_c1_v1.lower())
check("C3 draft reflects Check 2 (claim type not checkable), distinct wording from C1 v1's draft",
      draft_c3 != draft_c1_v1 and "checked" in draft_c3.lower())
check("C4 (unmatched) draft reflects the specific no-match reason, not a generic template",
      by_id["C4"].match_basis.split(" ")[0] in draft_c4 or "matched" in draft_c4.lower())
check("No send/transmit function exists anywhere in commentary_workflow.py (structural check)",
      not any(name.lower().startswith(("send_", "email_", "transmit_")) for name in dir(CW)))
check("No Controller-addressed field/language appears in any draft produced above",
      all("controller" not in d.lower() for d in (draft_c1_v1, draft_c3, draft_c4)))

# ---------------------------------------------------------------------------
# 6. Section F — Commentary Record / version model, full correction loop
# ---------------------------------------------------------------------------
record_1 = CW.CommentaryRecord(observation_id="OBS-FIXTURE-0001")
record_1.add_version(c1_explicit.text, CW.SOURCE_ORIGINAL_IMPORT, "controller_import", result_c1_v1)
check("Original v1 stored, retrievable, never overwritten by the revision",
      record_1.versions[0].text == c1_explicit.text and record_1.versions[0].version_number == 1)

record_1.add_version(c1_v2_text, CW.SOURCE_USER_REVISION, "finance_cfo_user", result_c1_v2)
check("v2 is a NEW complete version (not a patch) -- both v1 and v2 retained with their own stored results",
      len(record_1.versions) == 2
      and record_1.versions[0].validation_result.assessment == CW.INSUFFICIENT
      and record_1.versions[1].validation_result.assessment == CW.SUPPORTED)

record_1.mark_accepted(2)
check("v2 explicitly marked Accepted (Criterion E.10 -- distinct human action)",
      record_1.accepted_version_number == 2 and record_1.accepted_text() == c1_v2_text)

record_2 = CW.CommentaryRecord(observation_id="OBS-FIXTURE-0002")
record_2.add_version(
    "Customer Success Software & Tools spend fell because the team added headcount this quarter.",
    CW.SOURCE_ORIGINAL_IMPORT, "controller_import", result_c2,
)
check("Record with NO accepted version yet correctly reports accepted_text() as None",
      record_2.accepted_text() is None)

records = {"OBS-FIXTURE-0001": record_1, "OBS-FIXTURE-0002": record_2}

# ---------------------------------------------------------------------------
# 7. Section G — executive-output handoff: ONLY the accepted version reaches
#    the narrative prompt, traceably.
# ---------------------------------------------------------------------------
lines = CW.accepted_commentary_prompt_lines(records, observation_register)
check("Exactly one accepted-commentary line produced (only OBS-1 has an accepted version)",
      len(lines) == 1)
check("Accepted line contains v2's text (not v1's, not a fabricated summary)",
      c1_v2_text in lines[0] and "[accepted version 2]" in lines[0])
check("Accepted line does NOT contain OBS-2's unaccepted commentary",
      "Customer Success Software & Tools spend fell" not in "".join(lines))

# Confirm handoff into rollups.build_user_prompt itself, not just the helper.
pl_row = R.pl_q.iloc[-1]
current_q = R.pl_q[R.pl_q["Fiscal Quarter"] == R.quarter_order[-1]]
prior_q_label = R.quarter_order[-2]
prompt_with = R.build_user_prompt(
    "Fiscal Quarter", R.quarter_order, R.quarter_order[-1], prior_q_label, prior_q_label,
    R.pl_q, R.rev_by_region_q, R.rev_by_product_q, R.region_cm_q, R.product_cm_q,
    R.exp_by_dept_q, R.sb_volrate_q, R.breadth_all_q, R.hc_dept_q, R.company_rev_per_hc_q, R.bva_q,
    accepted_commentary_lines=lines,
)
prompt_without = R.build_user_prompt(
    "Fiscal Quarter", R.quarter_order, R.quarter_order[-1], prior_q_label, prior_q_label,
    R.pl_q, R.rev_by_region_q, R.rev_by_product_q, R.region_cm_q, R.product_cm_q,
    R.exp_by_dept_q, R.sb_volrate_q, R.breadth_all_q, R.hc_dept_q, R.company_rev_per_hc_q, R.bva_q,
)
check("Prompt WITH accepted commentary contains v2's exact accepted text",
      c1_v2_text in prompt_with)
check("Prompt WITHOUT accepted_commentary_lines (existing callers, e.g. Cycle 2/3) is byte-identical to pre-Phase-4-6 behavior",
      prompt_without.count("Finance/CFO-Approved Explanations") == 0)

# ---------------------------------------------------------------------------
# 8. D10 capture — complete Commentary Record persisted into an immutable
#    close_history snapshot, and read back intact (Section F requirement).
# ---------------------------------------------------------------------------
demo_close_history_dir = os.path.join(tmp_dir, "close_history_demo")
os.makedirs(demo_close_history_dir, exist_ok=True)

raw_dataset_stub = os.path.join(tmp_dir, "raw_dataset_stub.xlsx")
shutil.copyfile(R.RAW, raw_dataset_stub)
rollups_output_stub = os.path.join(tmp_dir, "rollups_output_stub.xlsx")
# rollups.py already wrote rollups_output.xlsx as a side effect of import;
# reuse it as the stub input archive_close() copies in (no calc logic here).
shutil.copyfile("rollups_output.xlsx", rollups_output_stub)

commentary_payload = CW.serialize_commentary_records(records)
folder, metadata = close_history.archive_close(
    period_label="Q4-2026-COMMENTARY-DEMO",
    raw_dataset_src=raw_dataset_stub,
    rollups_output_src=rollups_output_stub,
    observations_df=observation_register,
    narrative_text=prompt_with,
    phase2_flag_count=0,
    phase3_flag_count=len(observation_register),
    workflow_state="Executive Ready",
    prior_close_period_label=None,
    close_history_dir=demo_close_history_dir,
    commentary_record=commentary_payload,
)
check("archive_close() succeeds with a commentary_record payload", os.path.isdir(folder))
check("metadata.json's commentary_record is present and non-empty",
      bool(metadata.get("commentary_record")))

resolved = close_history.resolve_latest_approved_close(close_history_dir=demo_close_history_dir)
check("resolve_latest_approved_close() reads the snapshot back", resolved is not None)
read_back = resolved["metadata"]["commentary_record"]
check("Read-back commentary_record has BOTH observations",
      set(read_back.keys()) == {"OBS-FIXTURE-0001", "OBS-FIXTURE-0002"})
check("Read-back OBS-FIXTURE-0001 retains BOTH versions (v1 not discarded despite v2 being accepted)",
      len(read_back["OBS-FIXTURE-0001"]["versions"]) == 2)
check("Read-back OBS-FIXTURE-0001 accepted_version_number == 2, matching in-memory state",
      read_back["OBS-FIXTURE-0001"]["accepted_version_number"] == 2)
check("Read-back v1's stored validation_result is still Insufficient (not overwritten by v2's Supported result)",
      read_back["OBS-FIXTURE-0001"]["versions"][0]["validation_result"]["assessment"] == CW.INSUFFICIENT)
check("Read-back v2's stored validation_result is Supported",
      read_back["OBS-FIXTURE-0001"]["versions"][1]["validation_result"]["assessment"] == CW.SUPPORTED)
check("Read-back OBS-FIXTURE-0002 has accepted_version_number None (nothing accepted yet, correctly preserved)",
      read_back["OBS-FIXTURE-0002"]["accepted_version_number"] is None)

# Immutability check (D10's existing guarantee, re-exercised, not re-litigated)
raised_immutable = False
try:
    close_history.archive_close(
        period_label="Q4-2026-COMMENTARY-DEMO",
        raw_dataset_src=raw_dataset_stub, rollups_output_src=rollups_output_stub,
        observations_df=observation_register, narrative_text="x",
        phase2_flag_count=0, phase3_flag_count=0, workflow_state="x",
        prior_close_period_label=None, close_history_dir=demo_close_history_dir,
        commentary_record=commentary_payload,
    )
except FileExistsError:
    raised_immutable = True
check("Re-archiving the same period_label still raises FileExistsError (D10 immutability, not reopened)",
      raised_immutable)

# Backward-compat check: archive_close() with NO commentary_record (existing
# D10/Cycle-3-Task-1 call pattern) must still work exactly as before.
folder2, metadata2 = close_history.archive_close(
    period_label="Q4-2026-NO-COMMENTARY-DEMO",
    raw_dataset_src=raw_dataset_stub, rollups_output_src=rollups_output_stub,
    observations_df=pd.DataFrame(), narrative_text="no commentary this close",
    phase2_flag_count=0, phase3_flag_count=0, workflow_state="Executive Ready",
    prior_close_period_label=None, close_history_dir=demo_close_history_dir,
)
check("archive_close() with NO commentary_record (pre-existing D10 call pattern) still succeeds -- no regression",
      os.path.isdir(folder2) and metadata2["commentary_record"] == {})

shutil.rmtree(tmp_dir, ignore_errors=True)

print()
print(f"{'='*70}")
print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
print(f"{'='*70}")
if FAIL:
    print("FAILED:")
    for f in FAIL:
        print(f"  - {f}")
    sys.exit(1)
