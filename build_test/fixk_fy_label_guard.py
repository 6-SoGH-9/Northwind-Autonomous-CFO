"""
Fix K (brief v2.4, A3) -- "no FY in user-visible messages" guard.

*** BUILD/TEST VERIFICATION TOOL -- NOT A LIVE ARTIFACT ***
Same category as the other scripts in build_test/: it verifies, it does not
run in production. It writes only to temporary directories (created and
removed by this script); the repository tree, including close_history/, is not written.

What it checks
  * Quarter periods are shown as "Q3 2026", never "Q3 FY2026" (A3).
  * The matching rule is the Brief's: "FY" only as its own token, never as a
    raw substring and never case-insensitively. Reference pattern
    \\bFY\\s?\\d{2,4}\\b. The only text that passes is a standalone annual
    label matching ^FY\\d{4}$ exactly (not part of a quarter label).
  * Exemptions (exactly three): (i) a file path; (ii) quoted operating-system
    error text, only inside the error-detail slot, recognised by removing the
    injected sentinel string (never by pattern); (iii) a standalone FY####
    annual label.
  * Messages are rendered by the real dashboard functions (extracted from
    Northwind_Financial_Dashboard.py without running the Streamlit app; `st`
    is a recording stub, `R` is the real rollups module) fed with results of
    the real period_lifecycle / close_history code and quarter-style inputs
    such as "Q3 FY2026".

Run from the repository root:  python build_test/fixk_fy_label_guard.py
Exit status 0 = all checks passed.
"""
import ast
import os
import shutil
import tempfile
import re
import shutil
import sys
import tempfile
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
# Importing rollups runs the pipeline and WRITES rollups_output.xlsx into the
# current directory, so import it from a throw-away working directory that
# holds a copy of the sample dataset; the repository tree is never written.
_WORK = tempfile.mkdtemp(prefix="fixk_fy_guard_cwd_")
shutil.copyfile(os.path.join(ROOT, "Northwind_Sample_Dataset.xlsx"), os.path.join(_WORK, "Northwind_Sample_Dataset.xlsx"))
os.chdir(_WORK)

PASS = FAIL = 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  OK   {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label} {detail}")


# ---------------------------------------------------------------- the rule
_FY_TOKEN = re.compile(r"\bFY\s?\d{2,4}\b")          # reference pattern from the Brief
_ANNUAL_OK = re.compile(r"^FY\d{4}$")                # the only passing form
_QUARTER_PREFIX = re.compile(r"Q[1-4]\s$")           # token is part of a quarter label


def fy_violations(text):
    """Fiscal-year tokens in text that are NOT a standalone annual label."""
    bad = []
    for m in _FY_TOKEN.finditer(text):
        tok = m.group(0)
        part_of_quarter = bool(_QUARTER_PREFIX.search(text[: m.start()]))
        if _ANNUAL_OK.match(tok) and not part_of_quarter:
            continue
        bad.append(text[max(0, m.start() - 3): m.end()])
    return bad


print("=== matching rule (explicit must-pass / must-fail cases) ===")
for ok in ("verify", "notify", "identify", "modify", "FYI", "FY2026", "Please verify and notify.", "fy2026"):
    check(f"must pass: {ok!r}", fy_violations(ok) == [])
for bad in ("Q3 FY2026", "FY 2026", "FY26", "Q3 FY2026 was marked", "see FY2026 and Q3 FY2026"):
    check(f"must fail: {bad!r}", fy_violations(bad) != [])


# --------------------------------------------- real modules and the dashboard
import rollups as R                    # noqa: E402  (real; runs the pipeline on the sample dataset, as the app does)
os.chdir(ROOT)
import close_history as CH             # noqa: E402
import period_lifecycle as PL          # noqa: E402

QO = list(R.quarter_order)
Q2, Q3, Q4 = "Q2 FY2026", "Q3 FY2026", "Q4 FY2026"
assert all(q in QO for q in (Q2, Q3, Q4)), QO


class _St:
    """Recording stand-in for streamlit: keeps the text of each message call."""
    def __init__(self):
        self.out = []

    def _rec(self, kind):
        return lambda body, *a, **k: self.out.append((kind, str(body)))

    def __getattr__(self, name):
        if name in ("error", "warning", "info", "success", "caption", "markdown", "write"):
            return self._rec(name)
        raise AttributeError(name)


WANTED = {
    "_fmt_close_order_block_message", "_fmt_unresolved_reopen_block_message", "_fixk_released_notice_text",
    "_fmt_scope_violation_line", "_fixk_clear_failure_notices", "_fixk_render_notice", "_fixk_render_failure",
    "_fixk_success_notices", "_fixk_list_text", "_fixk_fallback_notice_text", "_fixk_bookkeeping_notice_text",
}
_tree = ast.parse(open(os.path.join(ROOT, "Northwind_Financial_Dashboard.py"), encoding="utf-8").read())
_funcs = [n for n in _tree.body if isinstance(n, ast.FunctionDef) and n.name in WANTED]
check("all message functions found in the dashboard", {f.name for f in _funcs} == WANTED, {f.name for f in _funcs} ^ WANTED)
ST = _St()
NS = {"R": R, "st": ST, "PL": PL, "close_history": CH}
exec(compile(ast.Module(body=_funcs, type_ignores=[]), "dashboard_message_functions", "exec"), NS)


def rendered(fn, *a):
    ST.out.clear()
    fn(*a)
    return [t for _k, t in ST.out]


def scan(label, texts, strip=()):
    """Remove each exempt string (sentinel / error slot / paths) exactly, then scan."""
    for t in texts:
        rest = t
        for s in strip:
            rest = rest.replace(s, "")
        check(f"{label}: no FY token", fy_violations(rest) == [], fy_violations(rest))


_E = OSError(13, "Permission denied", "/data/close_history/Q2 FY2026/v2")
SENT = f"{type(_E).__name__}: {_E}"   # injected error-slot text, exactly as the code renders "<type>: <detail>"

# ------------------------------------------------ real results of the real code
tmp = tempfile.mkdtemp(prefix="fixk_fy_guard_")
try:
    def fresh():
        d = tempfile.mkdtemp(dir=tmp)
        for q in (Q2, Q3, Q4):
            os.makedirs(os.path.join(d, q))
        return d

    def run(d, compare, archive, expected=2):
        return PL.run_reopen_approval_attempt(Q2, QO, CH, compare, archive, expected, close_history_dir=d)

    def _real_archive_failure(_att):
        raise _E

    print("\n=== W1 refusal, one quarter (real IsADirectoryError from a real obstruction) ===")
    d = fresh(); os.makedirs(os.path.join(d, Q3, "pending_reprocessing.json.tmp"))
    r1 = run(d, lambda p, desc: (p == Q3, desc), lambda a: (_ for _ in ()).throw(AssertionError("must not save")))
    check("outcome refused_marks, one failure", r1["outcome"] == "refused_marks" and len(r1["failures"]) == 1, r1["outcome"])
    t = rendered(NS["_fixk_render_failure"], Q2, r1)
    check("W1 exact text", t[0] == (
        f"Q2 2026 was NOT saved. Q3 2026 could not be marked as outdated ({r1['failures'][0]['error']}), so the "
        "correction was refused. Fix the cause shown above (for example folder permissions or disk space) and approve again."), t[0])
    scan("W1", t, strip=(r1["failures"][0]["error"],))

    print("\n=== W2 refusal, several quarters ===")
    d = fresh()
    for q in (Q3, Q4):
        os.makedirs(os.path.join(d, q, "pending_reprocessing.json.tmp"))
    r2 = run(d, lambda p, desc: (p in (Q3, Q4), desc), lambda a: None)
    errs = [f["error"] for f in r2["failures"]]
    check("two failures, oldest first", [f["period"] for f in r2["failures"]] == [Q3, Q4], r2["failures"])
    t = rendered(NS["_fixk_render_failure"], Q2, r2)
    check("W2 exact text", t[0] == (
        "Q2 2026 was NOT saved. The correction was refused because these quarters could not be marked as outdated:\n"
        f"- Q3 2026 ({errs[0]})\n- Q4 2026 ({errs[1]})\n\n"
        "Fix the cause shown above (for example folder permissions or disk space) and approve again. "
        "The oldest quarter is listed first."), t[0])
    scan("W2", t, strip=tuple(errs))

    print("\n=== W3 failed-clear notice (D4) ===")
    d = fresh()
    CH.write_pending_reprocessing(Q4, Q2, d)                       # a stale unresolved mark that Fix F should clear
    os.makedirs(os.path.join(d, Q4, "pending_reprocessing.json.tmp"))
    r3 = run(d, lambda p, desc: (p == Q3, desc), lambda a: ("folder", {"attempt_id": a}))
    check("approval not refused; clear failure recorded", r3["outcome"] == "saved" and [c["period"] for c in r3["clear_failures"]] == [Q4], (r3["outcome"], r3["clear_failures"]))
    e3 = r3["clear_failures"][0]["error"]
    t_notice = [x for x in rendered(lambda a: [NS["_fixk_render_notice"](n) for n in NS["_fixk_clear_failure_notices"](a)], r3)]
    check("W3 exact text", t_notice == [
        f"An outdated flag on Q4 2026 could not be cleared ({e3}). Q4 2026 stays blocked until it is reopened and re-closed."], t_notice)
    scan("W3", t_notice, strip=(e3,))
    scan("success notices", [x if isinstance(x, str) else x["exact"] for x in NS["_fixk_success_notices"](Q2, r3)], strip=(e3,))

    print("\n=== W4 save failure + W5 undo failure ===")
    d = fresh()
    orig = CH.restore_pending_state
    CH.restore_pending_state = lambda *a, **k: SENT
    try:
        r4 = run(d, lambda p, desc: (p == Q3, desc), _real_archive_failure)
    finally:
        CH.restore_pending_state = orig
    check("save_failed with one undo failure", r4["outcome"] == "save_failed" and len(r4["undo_failures"]) == 1, (r4["outcome"], r4["undo_failures"]))
    t = rendered(NS["_fixk_render_failure"], Q2, r4)
    check("W4 exact text (one message, no claim about flags)", t[0] == (
        f"Q2 2026 was NOT saved. The save failed ({r4['save_error']}). Fix the cause shown above "
        "(for example folder permissions or disk space) and approve again."), t[0])
    check("W5 exact text, below W4", t[1] == (
        f"The approval of Q2 2026 did not complete, but a flag for Q3 2026 from this attempt could not be undone ({SENT}). "
        "Q3 2026 stays blocked for narrative and later closes until a later approval of Q2 2026 completes, the storage "
        "problem is fixed and the mark is released, or Q3 2026 is reopened and re-closed. Other tabs still show Q3 2026 "
        "figures without any warning."), t[1])
    scan("W4/W5", t, strip=(r4["save_error"], SENT))
    CH.restore_pending_state = orig

    print("\n=== pre-existing and other message paths with quarter-style inputs ===")
    notices = []
    safe = PL.make_safe_compare_fn(lambda p, desc: (_ for _ in ()).throw(_E), notices)
    safe(Q3, Q2)
    check("compare-failure notice names 'Q3 2026'", notices and notices[0].startswith("Q3 2026 could not be compared"), notices)
    scan("could-not-be-compared notice", notices, strip=(SENT,))
    scan("release notice", [NS["_fixk_released_notice_text"]({"period": Q3, "reopened_period": Q2})])
    check("release notice exact text", NS["_fixk_released_notice_text"]({"period": Q3, "reopened_period": Q2}) ==
          "An earlier approval of Q2 2026 did not complete; no correction was saved and Q3 2026 is no longer marked.")
    scan("scope violation line", [NS["_fmt_scope_violation_line"]({"sheet": "Revenue", "period": Q3, "key": {"k": 1}, "issue": "row present only in upload"}),
                                  NS["_fmt_scope_violation_line"]({"sheet": "Revenue", "period": Q3, "key": {"k": 1}, "field": "Revenue ($)", "approved_value": 1.0, "uploaded_value": 2.0})])
    for blocker in ({"reason": "never_closed", "blocking_period": Q3, "predecessor": None},
                    {"reason": "reopen_impact", "blocking_period": Q3, "predecessor": Q2},
                    {"reason": "control_file_damaged", "blocking_period": None, "predecessor": None, "detail": "x"}):
        scan(f"close-order block message ({blocker['reason']})", [NS["_fmt_close_order_block_message"](blocker, Q4)])
    scan("unresolved-reopen block message", [NS["_fmt_unresolved_reopen_block_message"](Q3, Q4), NS["_fmt_unresolved_reopen_block_message"](Q3, Q4, "reopening")])

    print("\n=== N1 to N5 (brief v2.5): exact text, 'Close-order notice: ' prefix, no FY outside the error slot ===")
    PFX = "Close-order notice: "
    F, N = "flagged", "no saved close"
    def outs(*pairs):
        return [{"period": p, "outcome": o, "error": None} for p, o in pairs]
    Q1b, Q2b, Q3b = "Q1 FY2027", "Q2 FY2027", "Q3 FY2027"
    n1_cases = [
        ("one marked", outs((Q3, F)), 'Q2 2026 was saved. As a precaution, Q3 2026 is marked "may be outdated". Reopen and re-close it.'),
        ("two marked", outs((Q3, F), (Q4, F)), 'Q2 2026 was saved. As a precaution, Q3 2026 and Q4 2026 are marked "may be outdated". Reopen and re-close them in that order.'),
        ("three marked", outs((Q3, F), (Q4, F), (Q1b, F)), 'Q2 2026 was saved. As a precaution, Q3 2026, Q4 2026 and Q1 2027 are marked "may be outdated". Reopen and re-close them in that order.'),
        ("no-saved-close, one", outs((Q4, N)), "Q2 2026 was saved. Q4 2026 has no saved close, so nothing was marked."),
        ("no-saved-close, two", outs((Q4, N), (Q1b, N)), "Q2 2026 was saved. Q4 2026 and Q1 2027 have no saved close, so nothing was marked."),
        ("no-saved-close, three", outs((Q4, N), (Q1b, N), (Q2b, N)), "Q2 2026 was saved. Q4 2026, Q1 2027 and Q2 2027 have no saved close, so nothing was marked."),
        ("both parts (one marked + one no-saved-close)", outs((Q3, F), (Q4, N)), 'Q2 2026 was saved. As a precaution, Q3 2026 is marked "may be outdated". Reopen and re-close it. Q4 2026 has no saved close, so nothing was marked.'),
        ("both parts (two marked + two no-saved-close)", outs((Q3, F), (Q4, F), (Q1b, N), (Q2b, N)), 'Q2 2026 was saved. As a precaution, Q3 2026 and Q4 2026 are marked "may be outdated". Reopen and re-close them in that order. Q1 2027 and Q2 2027 have no saved close, so nothing was marked.'),
        ("no later quarter exists", [], "Q2 2026 was saved. No later quarter exists, so nothing was marked."),
    ]
    for name, o, want in n1_cases:
        got = NS["_fixk_fallback_notice_text"](Q2, o)
        check(f"N1 exact ({name}) [render test]", got == want, got)
        shown = rendered(NS["_fixk_render_notice"], got)
        check(f"N1 shown with the prefix ({name})", shown == [PFX + want], shown)
        scan(f"N1 ({name})", shown)

    # N5 + N1 together, through the real code (render of real results): the check of later quarters fails.
    d = fresh()
    o_apply, o_resolve = PL.apply_propagation_flags, CH.resolve_latest_approved_close_for_period
    PL.apply_propagation_flags = lambda *a, **k: (_ for _ in ()).throw(_E)
    CH.resolve_latest_approved_close_for_period = lambda p, *a, **k: {"stub": p} if p in (Q3, Q4) else None
    try:
        r5 = run(d, lambda p, desc: (False, desc), lambda a: ("folder", {"attempt_id": a}))
    finally:
        PL.apply_propagation_flags, CH.resolve_latest_approved_close_for_period = o_apply, o_resolve
    check("fallback ran and approval saved [real code path]", r5["outcome"] == "saved" and [o["outcome"] for o in r5["fallback_outcomes"]] == ["flagged", "flagged"], (r5["outcome"], r5.get("fallback_outcomes")))
    n5 = f"The check of later quarters failed ({SENT}). Every later quarter with a saved close is treated as affected."
    n1 = 'Q2 2026 was saved. As a precaution, Q3 2026 and Q4 2026 are marked "may be outdated". Reopen and re-close them in that order.'
    shown = rendered(lambda a: [NS["_fixk_render_notice"](n) for n in NS["_fixk_success_notices"](Q2, a)], r5)
    check("N5 exact, then N1 [real code path, sentinel error]", shown == [PFX + n5, PFX + n1], shown)
    scan("N5 + N1", shown, strip=(SENT,))

    # N3 (real make_safe_compare_fn with the sentinel error) shown through the dashboard notice renderer.
    n3 = f"Q3 2026 could not be compared with the corrected figures ({SENT}). It is treated as affected."
    check("N3 exact text [real code path]", notices and notices[0] == n3, notices)
    shown = rendered(NS["_fixk_render_notice"], notices[0])
    check("N3 shown with the prefix", shown == [PFX + n3], shown)
    scan("N3", shown, strip=(SENT,))

    # N4 (real move-aside failure after a real save failure).
    d = fresh()
    o_move = CH.move_aside_incomplete_version
    CH.move_aside_incomplete_version = lambda *a, **k: (_ for _ in ()).throw(_E)
    try:
        r4b = run(d, lambda p, desc: (False, desc), _real_archive_failure)
    finally:
        CH.move_aside_incomplete_version = o_move
    n4 = f"The incomplete folder for Q2 2026 (v2) could not be moved aside ({SENT}). It is not a saved version."
    check("save_failed and N4 recorded [real code path]", r4b["outcome"] == "save_failed" and r4b["notices"] == [n4], (r4b["outcome"], r4b["notices"]))
    shown = rendered(NS["_fixk_render_failure"], Q2, r4b)
    check("N4 shown with the prefix, below W4", len(shown) == 2 and shown[1] == PFX + n4 and shown[0].startswith("Q2 2026 was NOT saved. The save failed"), shown)
    scan("N4", shown, strip=(SENT, r4b["save_error"]))

    # N2 (both follow-up steps), real code path with the sentinel error.
    for step, attr, what in (("baseline", "establish_close_order_baseline_if_absent", "recording the close order"),
                             ("own flag", "resolve_pending_reprocessing", 'clearing the "may be outdated" mark on Q2 2026 itself')):
        d = fresh()
        orig_fn = getattr(CH, attr)
        setattr(CH, attr, lambda *a, **k: (_ for _ in ()).throw(_E))
        try:
            r2 = run(d, lambda p, desc: (False, desc), lambda a: ("folder", {"attempt_id": a}))
        finally:
            setattr(CH, attr, orig_fn)
        n2 = f"Q2 2026 was saved. A follow-up step failed: {what} ({SENT}). The saved version is complete."
        check(f"N2 {step}: approval still saved, one failure recorded [real code path]", r2["outcome"] == "saved" and r2["post_save_failures"] == [{"step": step, "error": SENT}], (r2["outcome"], r2["post_save_failures"]))
        shown = rendered(lambda a: [NS["_fixk_render_notice"](n) for n in NS["_fixk_success_notices"](Q2, a)], r2)
        check(f"N2 {step} exact text with the prefix", shown == [PFX + n2], shown)
        scan(f"N2 {step}", shown, strip=(SENT,))

    # W3 has NO prefix.
    shown = rendered(lambda a: [NS["_fixk_render_notice"](n) for n in NS["_fixk_clear_failure_notices"](a)], r3)
    check("W3 has no 'Close-order notice: ' prefix", len(shown) == 1 and not shown[0].startswith(PFX), shown)

    print("\n=== archive_close error text (shown through st.error) ===")
    d = fresh()
    os.makedirs(os.path.join(d, Q3, "v1"))
    try:
        CH.archive_close(period_label=Q3, raw_dataset_src=__file__, rollups_output_src=__file__, observations_df=None,
                         narrative_text="", phase2_flag_count=0, phase3_flag_count=0, workflow_state="x",
                         prior_close_period_label=None, close_history_dir=d, repo_dir=ROOT, version=1)
        msg = ""
    except FileExistsError as exc:
        msg = str(exc)
    folder = os.path.join(d, Q3, "v1")
    check("raised FileExistsError for an existing version", "already exists" in msg, msg)
    scan("archive_close error", [msg], strip=(folder,))
    check("message names 'Q3 2026'", "'Q3 2026'" in msg, msg)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.rmtree(_WORK, ignore_errors=True)

print(f"\nTOTAL: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
