"""
Builder regression fixture — Phase 4 Matching & Semantic Reconciliation
(phase4_semantic_reconciliation_brief_v2.md)

BUILD/TEST ONLY. Never Live. Per the Handbook's Validation Independence
Principle, this fixture is Builder-authored (both the synthetic observation
register and the commentary text) and proves NON-REGRESSION / control-flow
correctness of the Section 1-2-3-5a logic only. It is explicitly NOT cited
as evidence that semantic reconciliation (Section 3, the actual model call)
is generically correct -- that requires the principal-supplied, independently
authored UAT Cases B/C (Brief Section 8 / governing task Section 5), run
against a real ANTHROPIC_API_KEY, by a session other than Builder's own, per
the Validation Independence Principle. No ANTHROPIC_API_KEY is present in
this Builder's environment (confirmed below) -- Criterion 4's actual
semantic-match capability and the live-call half of Criterion 7 are NOT
exercised here; every semantic-layer call in this fixture is either (a) the
real no-key neutral-failure path (genuinely exercised, no key needed), or
(b) a monkeypatched/injected fake `anthropic` module used ONLY to test this
code's own response-parsing/validation/retry-discipline logic -- never
treated as evidence the real model behaves any particular way (per the
Builder onboarding prompt, Section 4).

This script uses different observations and different commentary text from
anything the v4/v5 fixture uses and from anything the principal's future
UAT package will supply -- written before that content exists.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

import commentary_workflow as CW

PASS, FAIL = [], []


def check(label, cond, detail=""):
    if cond:
        PASS.append(label)
        print(f"OK   {label}")
    else:
        FAIL.append(label)
        print(f"FAIL {label}  {detail}")


# ---------------------------------------------------------------------------
# Synthetic observation register -- 3 observations. OBS-GA-Q1/OBS-GA-Q2
# deliberately share Department+Category across two different periods (to
# exercise the period-narrowing defect fix); OBS-RD is the sole R&D/Other
# Opex observation (a clean single-candidate case for the exclusivity and
# no-unmatched-remain tests).
# ---------------------------------------------------------------------------
observation_register = pd.DataFrame([
    {
        "Observation ID": "OBS-GA-Q1", "Detected By": "Phase 3 (Plausibility Review)",
        "Period": "Q1 2026", "Type": "Plausibility Anomaly",
        "Department": "G&A", "Category": "Salaries & Benefits",
        "Before ($)": 200000.00, "After ($)": 260000.00, "Delta ($)": 60000.00,
        "Threshold Crossed": "|QoQ %| > 25%",
    },
    {
        "Observation ID": "OBS-GA-Q2", "Detected By": "Phase 3 (Plausibility Review)",
        "Period": "Q2 2026", "Type": "Plausibility Anomaly",
        "Department": "G&A", "Category": "Salaries & Benefits",
        "Before ($)": 260000.00, "After ($)": 300000.00, "Delta ($)": 40000.00,
        "Threshold Crossed": "|QoQ %| > 25%",
    },
    {
        "Observation ID": "OBS-RD", "Detected By": "Phase 3 (Plausibility Review)",
        "Period": "Q1 2026", "Type": "Plausibility Anomaly",
        "Department": "R&D", "Category": "Other Opex",
        "Before ($)": 15000.00, "After ($)": 9000.00, "Delta ($)": -6000.00,
        "Threshold Crossed": "|QoQ %| > 25%",
    },
], columns=CW.OBSERVATION_REGISTER_COLUMNS)


def counting_semantic_stub(*results):
    """Returns (fn, call_log). fn pops the next canned (id_or_None,
    reason_or_None) from `results` each call and appends the call's args to
    call_log -- used to both control the semantic layer's output AND assert
    exactly how many times / with what candidate set it was invoked
    (Criteria 5, 10)."""
    call_log = []
    remaining = list(results)

    def fn(entry_text, candidates_df):
        call_log.append({"text": entry_text, "candidate_ids": set(candidates_df["Observation ID"])})
        if remaining:
            return remaining.pop(0)
        return (None, "stub exhausted -- no confident match")

    return fn, call_log


# ===========================================================================
# Criterion 1 -- deterministic match (Dept+Cat+Value+Period all correct);
# zero semantic calls.
# ===========================================================================
c1_entry = CW.CommentaryEntry(
    commentary_id="C1",
    text="G&A Salaries & Benefits rose by $40,000 in Q2 2026 due to merit increases.",
)
stub_c1, log_c1 = counting_semantic_stub()
r1 = CW.resolve_commentary_matches([c1_entry], observation_register, {}, semantic_fn=stub_c1)[0]
check("Criterion 1: explicit Dept+Cat+Value+Period commentary matches OBS-GA-Q2 deterministically",
      r1.matched and r1.matched_observation_id == "OBS-GA-Q2" and r1.method == "deterministic",
      f"matched={r1.matched} oid={r1.matched_observation_id} method={r1.method} basis={r1.match_basis}")
check("Criterion 1: zero semantic calls for a resolved deterministic match (call-count assertion)",
      len(log_c1) == 0, f"call_log={log_c1}")

# ===========================================================================
# Criterion 2 -- corrected period-narrowing defect. OBS-RD is the ONLY
# R&D/Other Opex observation (Period=Q1 2026); commentary states "Q2 2026" --
# a period that DOES exist in the register (it's OBS-GA-Q2's period) but
# does NOT belong to the R&D/Other Opex candidate. This is the exact defect
# scenario the Brief describes ("a wrong-period single candidate"): the
# period is recognizable at all only because SOME observation in the
# register carries it -- an unrecognized period (one appearing nowhere in
# the register, e.g. "Q3 2026") is invisible to _find_period_terms()'s
# substring matcher and therefore can never trigger this narrowing path in
# the first place; that is a separate, pre-existing scope limit of the
# matcher, not what this Brief's defect fix addresses. Under the PRE-FIX
# defect, this case silently kept OBS-RD as an unnarrowed "single candidate"
# match; it must now be no confident match.
# ===========================================================================
c2_entry = CW.CommentaryEntry(commentary_id="C2", text="R&D Other Opex declined in Q2 2026.")
r2 = CW.match_commentary_entries([c2_entry], observation_register)[0]
check("Criterion 2: stated period (Q2 2026, real elsewhere in the register) not belonging to the "
      "sole R&D/Other Opex candidate (OBS-RD, Q1 2026) does NOT match it (corrected defect)",
      r2.matched is False, f"matched={r2.matched} oid={r2.matched_observation_id} basis={r2.match_basis}")
check("Criterion 2: rejection reason explicitly cites the stated period, not a generic ambiguity message",
      "Q2 2026" in r2.match_basis, r2.match_basis)

# Companion regression check: the SAME Department/Category reference with NO
# stated period, or with the CORRECT period, must still match OBS-RD --
# confirms the fix narrows correctly rather than over-rejecting.
c2b_entry = CW.CommentaryEntry(commentary_id="C2b", text="R&D Other Opex declined this quarter.")
r2b = CW.match_commentary_entries([c2b_entry], observation_register)[0]
check("Companion: same Dept/Cat with NO stated period still matches the sole candidate (no over-rejection)",
      r2b.matched and r2b.matched_observation_id == "OBS-RD", r2b.match_basis)

c2c_entry = CW.CommentaryEntry(commentary_id="C2c", text="R&D Other Opex declined in Q1 2026.")
r2c = CW.match_commentary_entries([c2c_entry], observation_register)[0]
check("Companion: same Dept/Cat with the CORRECT stated period still matches (fix narrows, not blocks)",
      r2c.matched and r2c.matched_observation_id == "OBS-RD", r2c.match_basis)

# Section 1's Value signal, explicit and testable: a stated $ figure that
# CONFLICTS with the only remaining Dept/Cat/Period candidate falls through
# to no confident match, rather than being silently ignored.
c2d_entry = CW.CommentaryEntry(
    commentary_id="C2d",
    text="R&D Other Opex declined in Q1 2026, a $999,000 drop versus last quarter.",
)
r2d = CW.match_commentary_entries([c2d_entry], observation_register)[0]
check("Value signal: a stated figure ($999,000) that conflicts with the sole candidate's actual "
      "Delta/Before/After (OBS-RD: Delta -$6,000) is NOT silently ignored -- falls through to no "
      "confident match (Section 1)",
      r2d.matched is False and "999,000" in r2d.match_basis, r2d.match_basis)

# ...and a stated figure that IS consistent is reflected in the match basis
# (evidence the check actually ran, not merely present in code).
c2e_entry = CW.CommentaryEntry(
    commentary_id="C2e",
    text="R&D Other Opex declined in Q1 2026, a $6,000 drop versus last quarter.",
)
r2e = CW.match_commentary_entries([c2e_entry], observation_register)[0]
check("Value signal: a stated figure ($6,000) consistent with the candidate's Delta is used as "
      "positive support and recorded in the match basis",
      r2e.matched and r2e.matched_observation_id == "OBS-RD" and "6,000.00 consistent" in r2e.match_basis,
      r2e.match_basis)

# ===========================================================================
# Criterion 3 -- exclusivity. Register used here is narrowed to the sole
# OBS-RD observation so that after the first entry claims it, ZERO
# observations remain unmatched -- this keeps the "occupied" distinguishing
# label visible in the final result (Section 3's gate then closes on
# condition 2, so no semantic call further overwrites it) and doubles as a
# partial demonstration of Criterion 5.
# ===========================================================================
solo_register = observation_register[observation_register["Observation ID"] == "OBS-RD"].reset_index(drop=True)
c3a = CW.CommentaryEntry(commentary_id="C3a", text="R&D Other Opex spend fell this quarter.")
c3b = CW.CommentaryEntry(commentary_id="C3b", text="R&D Other Opex costs also dropped this quarter.")
stub_c3, log_c3 = counting_semantic_stub()
results_c3 = CW.resolve_commentary_matches([c3a, c3b], solo_register, {}, semantic_fn=stub_c3)
by_id_c3 = {m.commentary_id: m for m in results_c3}
check("Criterion 3 (within-batch): first commentary (C3a) is attached to OBS-RD",
      by_id_c3["C3a"].matched and by_id_c3["C3a"].matched_observation_id == "OBS-RD",
      by_id_c3["C3a"].match_basis)
check("Criterion 3 (within-batch): second commentary (C3b), same only candidate, is reported "
      "unresolved/occupied -- never silently added as a second version",
      by_id_c3["C3b"].matched is False and by_id_c3["C3b"].match_basis.startswith(CW.OCCUPIED_BASIS_PREFIX),
      by_id_c3["C3b"].match_basis)
check("Criterion 3 (within-batch): zero semantic calls (only candidate is occupied after C3a)",
      len(log_c3) == 0, f"call_log={log_c3}")

# Same exclusivity rule, but the occupancy is EXTERNAL (an already-existing
# CommentaryRecord from a prior import), not within-batch.
existing_record = CW.CommentaryRecord(observation_id="OBS-RD")
existing_record.add_version("Prior commentary already on file for this observation.",
                             CW.SOURCE_ORIGINAL_IMPORT, "controller_import", validation_result=None)
c3c = CW.CommentaryEntry(commentary_id="C3c", text="R&D Other Opex spend moved again this quarter.")
stub_c3c, log_c3c = counting_semantic_stub()
r3c = CW.resolve_commentary_matches([c3c], solo_register, {"OBS-RD": existing_record}, semantic_fn=stub_c3c)[0]
check("Criterion 3 (externally occupied): a commentary deterministically matching an ALREADY-occupied "
      "observation (from a prior import) is reported unresolved/occupied, not attached",
      r3c.matched is False and r3c.match_basis.startswith(CW.OCCUPIED_BASIS_PREFIX), r3c.match_basis)
check("Criterion 3 (externally occupied): zero semantic calls (sole candidate already occupied)",
      len(log_c3c) == 0, f"call_log={log_c3c}")

# ===========================================================================
# Criterion 5 -- ALL observations occupied (full 3-row register this time);
# any remaining unresolved commentary stays Open/Unmatched with ZERO
# semantic calls, even for an entry with no Department/Category reference
# at all.
# ===========================================================================
all_occupied_records = {}
for oid in observation_register["Observation ID"]:
    rec = CW.CommentaryRecord(observation_id=oid)
    rec.add_version(f"Pre-existing commentary for {oid}.", CW.SOURCE_ORIGINAL_IMPORT, "controller_import", None)
    all_occupied_records[oid] = rec

c5_entry = CW.CommentaryEntry(commentary_id="C5", text="General cost increase across the business this quarter.")
stub_c5, log_c5 = counting_semantic_stub(("OBS-GA-Q1", None))  # would force a match if the gate were open
r5 = CW.resolve_commentary_matches([c5_entry], observation_register, all_occupied_records, semantic_fn=stub_c5)[0]
check("Criterion 5: with all observations occupied, remaining unresolved commentary stays Open/Unmatched",
      r5.matched is False and r5.method == "unresolved", f"matched={r5.matched} method={r5.method} basis={r5.match_basis}")
check("Criterion 5: ZERO semantic-reconciliation calls when no unmatched observations remain "
      "(call-count assertion -- even though the stub was primed to return a match if called)",
      len(log_c5) == 0, f"call_log={log_c5}")

# ===========================================================================
# Criterion 6 -- no-API-key path (REAL semantic_reconcile_commentary, no
# mock) and simulated API-failure path, both neutral, and confirmed to
# leave an already-resolved deterministic match in the SAME batch untouched.
# ===========================================================================
check("Precondition: ANTHROPIC_API_KEY is NOT set in this Builder environment "
      "(confirms the no-key path below is genuinely exercised, not skipped)",
      os.environ.get("ANTHROPIC_API_KEY") in (None, ""),
      f"ANTHROPIC_API_KEY={'<set, unexpectedly>' if os.environ.get('ANTHROPIC_API_KEY') else '<unset>'}")

c6_deterministic = CW.CommentaryEntry(commentary_id="C6-det",
                                       text="G&A Salaries & Benefits rose by $60,000 in Q1 2026.")
c6_needs_semantic = CW.CommentaryEntry(commentary_id="C6-sem",
                                        text="Support-side software spend eased off a bit this quarter.")
results_c6 = CW.resolve_commentary_matches(
    [c6_deterministic, c6_needs_semantic], observation_register, {},
    semantic_fn=CW.semantic_reconcile_commentary,  # the REAL function, no mock
)
by_id_c6 = {m.commentary_id: m for m in results_c6}
check("Criterion 6: no-API-key path -- unresolved commentary stays Open/Unmatched, no exception raised",
      by_id_c6["C6-sem"].matched is False and by_id_c6["C6-sem"].method == "unresolved",
      by_id_c6["C6-sem"].match_basis)
check("Criterion 6: no-API-key failure reason is neutral and identifies the missing key "
      "(distinguishable from 'ran and found no match')",
      "ANTHROPIC_API_KEY" in by_id_c6["C6-sem"].match_basis, by_id_c6["C6-sem"].match_basis)
check("Criterion 6: the no-key semantic-layer path has ZERO effect on an already-resolved "
      "deterministic match in the same batch",
      by_id_c6["C6-det"].matched and by_id_c6["C6-det"].matched_observation_id == "OBS-GA-Q1"
      and by_id_c6["C6-det"].method == "deterministic",
      f"{by_id_c6['C6-det'].matched}, {by_id_c6['C6-det'].matched_observation_id}, {by_id_c6['C6-det'].method}")

# Simulated API failure: inject a fake `anthropic` module whose client
# raises on `.messages.create` -- exercises the REAL try/except in
# semantic_reconcile_commentary (Section 5's "no retry on failure" path),
# not a mock of that function itself.
import types

fake_anthropic_fail = types.ModuleType("anthropic")


class _FailingMessages:
    def create(self, **kwargs):
        raise RuntimeError("simulated network failure")


class _FailingClient:
    def __init__(self, api_key=None):
        self.messages = _FailingMessages()


fake_anthropic_fail.Anthropic = _FailingClient

os.environ["ANTHROPIC_API_KEY"] = "sk-ant-FIXTURE-FAKE-DO-NOT-USE"  # fixture-only fake, never a real credential
sys.modules["anthropic"] = fake_anthropic_fail
try:
    fail_result, fail_reason = CW.semantic_reconcile_commentary(
        "Support-side software spend eased off a bit this quarter.",
        observation_register[observation_register["Observation ID"] != "OBS-GA-Q1"],
    )
    raised = False
except Exception:
    fail_result, fail_reason = None, None
    raised = True
finally:
    del os.environ["ANTHROPIC_API_KEY"]
    del sys.modules["anthropic"]

check("Criterion 6: simulated API failure -- semantic_reconcile_commentary does NOT raise "
      "(returns a neutral failure tuple instead)",
      raised is False, "an exception propagated out of semantic_reconcile_commentary")
check("Criterion 6: simulated API failure -- result is (None, reason), reason surfaces the failure neutrally",
      fail_result is None and fail_reason is not None and "API call failed" in fail_reason,
      f"result={fail_result} reason={fail_reason}")

# ===========================================================================
# Criterion 7 (logic half only -- response validation, no live model
# judgment claimed) -- malformed / out-of-set model response is treated as
# no confident match, never accepted at face value.
# ===========================================================================
def _fake_anthropic_returning(text):
    mod = types.ModuleType("anthropic")

    class _Block:
        type = "text"

    block = _Block()
    block.text = text

    class _Resp:
        content = [block]

    class _Messages:
        def create(self, **kwargs):
            return _Resp()

    class _Client:
        def __init__(self, api_key=None):
            self.messages = _Messages()

    mod.Anthropic = _Client
    return mod


def _run_fake_semantic(response_text, candidates_df):
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-FIXTURE-FAKE-DO-NOT-USE"
    sys.modules["anthropic"] = _fake_anthropic_returning(response_text)
    try:
        return CW.semantic_reconcile_commentary("irrelevant fixture text", candidates_df)
    finally:
        del os.environ["ANTHROPIC_API_KEY"]
        del sys.modules["anthropic"]


unmatched_for_c7 = observation_register[observation_register["Observation ID"] != "OBS-GA-Q1"]

r7a_id, r7a_reason = _run_fake_semantic("OBS-DOES-NOT-EXIST-0000", unmatched_for_c7)
check("Criterion 7: a response naming an Observation ID NOT in the current unmatched set is "
      "treated as no confident match, not accepted at face value",
      r7a_id is None and "unusable/invalid" in (r7a_reason or ""), f"id={r7a_id} reason={r7a_reason}")

r7b_id, r7b_reason = _run_fake_semantic("OBS-GA-Q1", unmatched_for_c7)  # occupied ID, excluded from this candidate set
check("Criterion 7: a response naming a real Observation ID that is NOT in the CURRENT candidate "
      "set (e.g. already occupied / not passed as a candidate) is rejected, never trusted blindly",
      r7b_id is None, f"id={r7b_id} reason={r7b_reason}")

r7c_id, r7c_reason = _run_fake_semantic("Sure, I think this refers to OBS-GA-Q2 probably.", unmatched_for_c7)
check("Criterion 7: malformed/chatty response (not exactly an ID or NO_MATCH on its own line) is "
      "rejected rather than fuzzily parsed",
      r7c_id is None, f"id={r7c_id} reason={r7c_reason}")

r7d_id, r7d_reason = _run_fake_semantic("NO_MATCH", unmatched_for_c7)
check("Criterion 7 (legal outcome): a clean NO_MATCH response is accepted as 'no confident match', "
      "distinct from a rejected/malformed response",
      r7d_id is None and "no confident match" in (r7d_reason or "").lower(), f"id={r7d_id} reason={r7d_reason}")

r7e_id, r7e_reason = _run_fake_semantic("OBS-GA-Q2", unmatched_for_c7)
check("Criterion 7 (legal outcome): a response naming a real, currently-unmatched candidate ID IS accepted",
      r7e_id == "OBS-GA-Q2" and r7e_reason is None, f"id={r7e_id} reason={r7e_reason}")

# ===========================================================================
# Criterion 9 -- credential-exposure sweep. Confirms no Anthropic API key
# appears hardcoded/committed anywhere Builder touched, and that this
# fixture's own fake keys are unambiguously fake (never a plausible real
# key shape) so this check has teeth.
# ===========================================================================
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SWEEP_FILES = ["commentary_workflow.py", "Northwind_Financial_Dashboard.py",
                os.path.join("build_test", "phase4_semantic_reconciliation_demo.py")]
REAL_KEY_SHAPE = re.compile(r"sk-ant-api03-[A-Za-z0-9_\-]{20,}")  # real Anthropic key shape
KEY_LITERAL_ASSIGN = re.compile(r"(api[_-]?key|anthropic[_-]?api[_-]?key)\s*=\s*[\"'][^\"']+[\"']", re.IGNORECASE)

sweep_hits = []
for relpath in SWEEP_FILES:
    full = os.path.join(REPO_ROOT, relpath)
    with open(full, "r", encoding="utf-8") as fh:
        text = fh.read()
    for lineno, line in enumerate(text.splitlines(), 1):
        if REAL_KEY_SHAPE.search(line):
            sweep_hits.append((relpath, lineno, "real-shaped key literal", line.strip()))
        for m in KEY_LITERAL_ASSIGN.finditer(line):
            literal = m.group(0)
            # The only allowed pattern is reading FROM the environment
            # (os.environ.get("ANTHROPIC_API_KEY")) -- a string literal
            # ASSIGNED to an api-key-like name is exactly what's disallowed.
            if "environ" not in line:
                sweep_hits.append((relpath, lineno, "string literal assigned to an api-key-like name", line.strip()))

print("--- Criterion 9 sweep output ---")
if sweep_hits:
    for f, ln, kind, line in sweep_hits:
        print(f"  {f}:{ln}: {kind}: {line}")
else:
    print("  (no hits -- swept for real-shaped key literals and api-key-like string-literal assignments "
          f"across {SWEEP_FILES}, only os.environ.get('ANTHROPIC_API_KEY') reads found)")
check("Criterion 9: full sweep of touched files finds NO hardcoded/committed Anthropic credential",
      len(sweep_hits) == 0, sweep_hits)

grep_env_pattern = "ANTHROPIC_API_KEY"
env_read_count = sum(
    open(os.path.join(REPO_ROOT, f), encoding="utf-8").read().count(f'os.environ.get("{grep_env_pattern}")')
    for f in ["commentary_workflow.py"]
)
check("Criterion 9: the only credential-access pattern in commentary_workflow.py is the standard "
      "os.environ.get('ANTHROPIC_API_KEY') runtime read (>=1 occurrence, matching rollups.py's model)",
      env_read_count >= 1, f"count={env_read_count}")

# ===========================================================================
# Criterion 10 -- no uncontrolled repeated invocation, across >=2 simulated
# dashboard reruns of the SAME session state.
# ===========================================================================
# (a) A resolved-and-failed commentary must not trigger a further semantic
# call on a subsequent rerun.
rerun_state = set()  # stands in for st.session_state["semantic_reconciliation_attempted"]
stub_rerun, log_rerun = counting_semantic_stub((None, "no confident match, run 1"))
rerun_entry = CW.CommentaryEntry(commentary_id="C10", text="Support-side software spend eased off a bit this quarter.")

# Rerun 1 -- script "reruns", same entry re-submitted, same persisted state.
_ = CW.resolve_commentary_matches([rerun_entry], observation_register, {}, semantic_attempted=rerun_state, semantic_fn=stub_rerun)
# Rerun 2 -- identical call again (mirrors Streamlit re-executing the script).
_ = CW.resolve_commentary_matches([rerun_entry], observation_register, {}, semantic_attempted=rerun_state, semantic_fn=stub_rerun)
# Rerun 3, for good measure.
_ = CW.resolve_commentary_matches([rerun_entry], observation_register, {}, semantic_attempted=rerun_state, semantic_fn=stub_rerun)
check("Criterion 10a: an already-attempted-and-failed commentary triggers exactly ONE semantic "
      "call total across 3 simulated reruns of the same session state (call-count assertion)",
      len(log_rerun) == 1, f"call_log length={len(log_rerun)}, expected 1")

# (b) API failure does not trigger an automatic retry -- confirmed directly
# via the real semantic_reconcile_commentary's try/except (single call
# attempt, no loop) by inspecting the function does not itself retry; the
# call-count evidence above (exactly 1 call across 3 resolve_commentary_
# matches invocations) already demonstrates the CALLER-level non-retry
# discipline (Section 5a bullet 3) for a failure outcome specifically, since
# stub_rerun's canned result was itself a failure ("no confident match").
check("Criterion 10b: the single semantic call recorded above was for a FAILURE outcome, "
      "confirming non-retry applies to the failure path specifically, not just the success path",
      len(log_rerun) == 1 and log_rerun[0]["text"] == rerun_entry.text, log_rerun)

# (c) Different commentary entries are NOT deduplicated against each other
# -- only the (already-attempted) SAME commentary_id is suppressed. Confirms
# 10a's suppression is per-entry, not a blanket "never call again" bug.
rerun_state_2 = set()
stub_rerun2, log_rerun2 = counting_semantic_stub(
    (None, "no match for C10a"), (None, "no match for C10b"),
)
entry_10a = CW.CommentaryEntry(commentary_id="C10a", text="Support-side software spend eased off a bit this quarter.")
entry_10b = CW.CommentaryEntry(commentary_id="C10b", text="Marketing tooling costs also softened this quarter, unclear why.")
_ = CW.resolve_commentary_matches([entry_10a], observation_register, {}, semantic_attempted=rerun_state_2, semantic_fn=stub_rerun2)
_ = CW.resolve_commentary_matches([entry_10a, entry_10b], observation_register, {}, semantic_attempted=rerun_state_2, semantic_fn=stub_rerun2)
check("Criterion 10c: suppression is per-commentary-id -- a NEW entry (C10b) introduced on a later "
      "rerun still gets exactly one semantic call, while the already-attempted C10a (re-submitted "
      "in the same rerun) gets zero additional calls",
      len(log_rerun2) == 2 and {c["text"] for c in log_rerun2} == {entry_10a.text, entry_10b.text},
      f"call_log={log_rerun2}")

# ===========================================================================
# Audit-trail addendum checks (builder_brief_audit_trail_narrative_sync.md,
# Section 5) -- match_method/match_basis on CommentaryRecord, set once at
# attachment time, for all three resolution paths, plus a round-trip check.
# These mirror the exact call pattern the dashboard uses at each of its
# three edit points (Section 2.2), not a new abstraction.
# ===========================================================================

# New check 1 -- deterministic match.
c_audit_det = CW.CommentaryEntry(commentary_id="C-AUDIT-DET",
                                  text="G&A Salaries & Benefits rose by $40,000 in Q2 2026 due to merit increases.")
stub_audit_det, _ = counting_semantic_stub()
r_audit_det = CW.resolve_commentary_matches([c_audit_det], observation_register, {}, semantic_fn=stub_audit_det)[0]
rec_audit_det = CW.CommentaryRecord(observation_id=r_audit_det.matched_observation_id)
rec_audit_det.match_method = r_audit_det.method
rec_audit_det.match_basis = r_audit_det.match_basis
rec_audit_det.add_version(c_audit_det.text, CW.SOURCE_ORIGINAL_IMPORT, "controller_import", None)
check("Audit trail: a deterministic match produces match_method == 'deterministic' on the resulting "
      "CommentaryRecord, set once at attachment (mirrors dashboard's automated-match edit point)",
      rec_audit_det.match_method == "deterministic", rec_audit_det.match_method)

# New check 2 -- semantic match (injectable semantic_fn test double, same
# pattern as the rest of this fixture -- not a real API call).
c_audit_sem = CW.CommentaryEntry(commentary_id="C-AUDIT-SEM",
                                  text="Support-side software spend eased off a bit this quarter.")
stub_audit_sem, _ = counting_semantic_stub(("OBS-RD", "semantic reconciliation: confident match"))
r_audit_sem = CW.resolve_commentary_matches([c_audit_sem], observation_register, {}, semantic_fn=stub_audit_sem)[0]
rec_audit_sem = CW.CommentaryRecord(observation_id=r_audit_sem.matched_observation_id)
rec_audit_sem.match_method = r_audit_sem.method
rec_audit_sem.match_basis = r_audit_sem.match_basis
rec_audit_sem.add_version(c_audit_sem.text, CW.SOURCE_ORIGINAL_IMPORT, "controller_import", None)
check("Audit trail: a semantic match (injected test double) produces match_method == 'semantic' on "
      "the resulting CommentaryRecord",
      r_audit_sem.matched and rec_audit_sem.match_method == "semantic",
      f"matched={r_audit_sem.matched} method={rec_audit_sem.match_method}")

# New check 3 -- manual match. Not a commentary_workflow.py function (the
# manual path lives entirely in the dashboard's confirm-button branch) --
# this mirrors that exact assignment sequence: record.match_method="manual",
# record.match_basis="manually reconciled via Commentary Review", set
# BEFORE add_version(), exactly as Northwind_Financial_Dashboard.py does.
rec_audit_manual = CW.CommentaryRecord(observation_id="OBS-RD")
rec_audit_manual.match_method = "manual"
rec_audit_manual.match_basis = "manually reconciled via Commentary Review"
rec_audit_manual.add_version("Manually reconciled commentary text.", CW.SOURCE_ORIGINAL_IMPORT, "controller_import", None)
check("Audit trail: a manual match produces match_method == 'manual' on the resulting CommentaryRecord",
      rec_audit_manual.match_method == "manual" and
      rec_audit_manual.match_basis == "manually reconciled via Commentary Review",
      rec_audit_manual.match_method)

# New check 4 -- to_dict() -> serialize_commentary_records() round trip.
serialized = CW.serialize_commentary_records({
    rec_audit_det.observation_id: rec_audit_det,
    "OBS-RD-MANUAL": rec_audit_manual,
})
check("Audit trail: match_method/match_basis survive a full to_dict() -> "
      "serialize_commentary_records() round trip unchanged (deterministic record)",
      serialized[rec_audit_det.observation_id]["match_method"] == "deterministic" and
      serialized[rec_audit_det.observation_id]["match_basis"] == rec_audit_det.match_basis,
      serialized[rec_audit_det.observation_id])
check("Audit trail: match_method/match_basis survive the same round trip unchanged (manual record)",
      serialized["OBS-RD-MANUAL"]["match_method"] == "manual" and
      serialized["OBS-RD-MANUAL"]["match_basis"] == "manually reconciled via Commentary Review",
      serialized["OBS-RD-MANUAL"])

# ===========================================================================
# Criterion 8 -- existing v4/v5 fixtures still pass. Run as a separate
# subprocess so this script's own import/monkeypatch state (fake `anthropic`
# module injections above) can never leak into that run.
# ===========================================================================
import subprocess

v4_result = subprocess.run(
    [sys.executable, os.path.join(REPO_ROOT, "build_test", "commentary_workflow_demo.py")],
    capture_output=True, text=True, cwd=REPO_ROOT,
)
v4_ok = "RESULT: 49 passed, 0 failed" in v4_result.stdout
check("Criterion 8: existing v4 Builder regression fixture (49 checks) still passes unmodified, "
      "run fresh in a clean subprocess",
      v4_ok, v4_result.stdout[-400:] if not v4_ok else "49/49")

print()
print("=" * 70)
print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
print("=" * 70)
if FAIL:
    sys.exit(1)
