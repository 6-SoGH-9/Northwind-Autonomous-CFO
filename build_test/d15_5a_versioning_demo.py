"""
D15 Section 5.A — Close identity and versioning: Builder regression fixture.

Proves non-regression + new-behavior of close_history.py's versioning
extension in isolation, against a scratch close_history_dir (never the real
production close_history/). Per the Validation Independence Principle, this
is Builder-authored regression evidence only -- it proves the code behaves
as Builder intended, not that the requirement is generically satisfied;
independent Test evidence is still required before D15 reaches Verified.

Run: PYTHONPATH=. python3 build_test/d15_5a_versioning_demo.py
"""
import os
import sys
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import close_history as CH

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


scratch = tempfile.mkdtemp(prefix="d15_5a_")
close_dir = os.path.join(scratch, "close_history")

# Minimal stub source files archive_close() copies in.
raw_path = os.path.join(scratch, "raw.xlsx")
rollups_path = os.path.join(scratch, "rollups.xlsx")
pd.DataFrame({"x": [1]}).to_excel(raw_path, index=False)
pd.DataFrame({"x": [1]}).to_excel(rollups_path, index=False)
empty_obs = pd.DataFrame(columns=["Observation ID"])

# --- Archive v1 ---------------------------------------------------------
folder_v1, meta_v1 = CH.archive_close(
    period_label="Q4 FY2026",
    raw_dataset_src=raw_path,
    rollups_output_src=rollups_path,
    observations_df=empty_obs,
    narrative_text="v1 narrative",
    phase2_flag_count=0,
    phase3_flag_count=1,
    workflow_state="Archived",
    prior_close_period_label=None,
    close_history_dir=close_dir,
    version=1,
)
check("v1 archived successfully", os.path.isdir(folder_v1))
check("v1 metadata records version=1", meta_v1["version"] == 1)
check("v1 folder path uses versioned layout", folder_v1.endswith(os.path.join("Q4 FY2026", "v1")))

# --- Re-archiving v1 must fail (immutability, not reopened) ------------
raised = False
try:
    CH.archive_close(
        period_label="Q4 FY2026", raw_dataset_src=raw_path, rollups_output_src=rollups_path,
        observations_df=empty_obs, narrative_text="dup", phase2_flag_count=0, phase3_flag_count=1,
        workflow_state="Archived", prior_close_period_label=None, close_history_dir=close_dir, version=1,
    )
except FileExistsError:
    raised = True
check("Re-archiving v1 raises FileExistsError (D10 immutability preserved)", raised)

# --- Snapshot v1's stored bytes before v2 exists ------------------------
with open(os.path.join(folder_v1, "narrative.txt"), "rb") as f:
    v1_bytes_before = f.read()

# --- Archive v2 (a correction) ------------------------------------------
folder_v2, meta_v2 = CH.archive_close(
    period_label="Q4 FY2026",
    raw_dataset_src=raw_path,
    rollups_output_src=rollups_path,
    observations_df=empty_obs,
    narrative_text="v2 narrative (correction)",
    phase2_flag_count=0,
    phase3_flag_count=0,
    workflow_state="Archived",
    prior_close_period_label="Q3 FY2026",
    close_history_dir=close_dir,
    version=2,
)
check("v2 archived successfully", os.path.isdir(folder_v2))
check("v2 metadata records version=2", meta_v2["version"] == 2)
check("v1 and v2 are different folders", folder_v1 != folder_v2)

# --- v1 byte-identical after v2 creation --------------------------------
with open(os.path.join(folder_v1, "narrative.txt"), "rb") as f:
    v1_bytes_after = f.read()
check("v1's stored data is byte-identical before and after v2's creation", v1_bytes_before == v1_bytes_after)

# --- resolve_version() never silently falls back ------------------------
r1 = CH.resolve_version("Q4 FY2026", 1, close_history_dir=close_dir)
r2 = CH.resolve_version("Q4 FY2026", 2, close_history_dir=close_dir)
r3 = CH.resolve_version("Q4 FY2026", 3, close_history_dir=close_dir)
check("resolve_version(period, 1) returns v1", r1 is not None and r1["version"] == 1)
check("resolve_version(period, 2) returns v2", r2 is not None and r2["version"] == 2)
check("resolve_version(period, 3) (nonexistent) returns None, not a silent fallback to latest", r3 is None)

# --- resolve_latest_approved_close() default (latest_version_only=True) -
latest = CH.resolve_latest_approved_close(close_history_dir=close_dir)
check(
    "resolve_latest_approved_close() with default latest_version_only=True returns v2",
    latest is not None and latest["version"] == 2,
)

# --- list_approved_closes(latest_version_only=False) enumerates both ----
all_versions = CH.list_approved_closes(close_history_dir=close_dir, latest_version_only=False)
q4_versions = sorted(v for (label, meta, folder) in all_versions if label == "Q4 FY2026" for v in [meta["version"]])
check("list_approved_closes(latest_version_only=False) returns both v1 and v2 for the period", q4_versions == [1, 2])

default_list = CH.list_approved_closes(close_history_dir=close_dir)
check(
    "list_approved_closes() default (latest_version_only=True) returns exactly one entry for the period",
    len([1 for (label, meta, folder) in default_list if label == "Q4 FY2026"]) == 1,
)

# --- Legacy (pre-D15, unversioned) snapshot compatibility ---------------
legacy_folder = os.path.join(close_dir, "Q2 FY2026")
os.makedirs(legacy_folder)
shutil.copyfile(raw_path, os.path.join(legacy_folder, "raw_dataset.xlsx"))
shutil.copyfile(rollups_path, os.path.join(legacy_folder, "rollups_output.xlsx"))
empty_obs.to_csv(os.path.join(legacy_folder, "observations.csv"), index=False)
with open(os.path.join(legacy_folder, "narrative.txt"), "w") as f:
    f.write("legacy narrative")
import json
with open(os.path.join(legacy_folder, "metadata.json"), "w") as f:
    json.dump({
        "period_label": "Q2 FY2026", "approval_timestamp": "2026-05-01T00:00:00+00:00",
        "workflow_state": "Archived", "phase2_flag_count": 0, "phase3_flag_count": 0,
        "prior_close_period_label": None, "pipeline_git_commit_hash": "legacy",
        "commentary_record": {},
    }, f)

legacy_v1 = CH.resolve_version("Q2 FY2026", 1, close_history_dir=close_dir)
check("A pre-D15 unversioned snapshot resolves as implicit v1 via resolve_version()", legacy_v1 is not None)
check(
    "Legacy snapshot is read from its original (unmigrated) location, not a v1/ subfolder",
    legacy_v1 is not None and legacy_v1["folder"] == legacy_folder,
)
legacy_files_untouched = os.path.isfile(os.path.join(legacy_folder, "metadata.json")) and not os.path.isdir(
    os.path.join(legacy_folder, "v1")
)
check("Legacy snapshot's files were not migrated/rewritten (no new v1/ subfolder created)", legacy_files_untouched)

raised_legacy = False
try:
    CH.archive_close(
        period_label="Q2 FY2026", raw_dataset_src=raw_path, rollups_output_src=rollups_path,
        observations_df=empty_obs, narrative_text="dup", phase2_flag_count=0, phase3_flag_count=0,
        workflow_state="Archived", prior_close_period_label=None, close_history_dir=close_dir, version=1,
    )
except FileExistsError:
    raised_legacy = True
check(
    "Attempting a NEW v1 archive over an existing legacy v1 also raises FileExistsError (no dual-v1 state)",
    raised_legacy,
)

shutil.rmtree(scratch, ignore_errors=True)

print()
print("=" * 70)
print(f"RESULT: {PASS} passed, {FAIL} failed")
print("=" * 70)
if FAIL:
    sys.exit(1)
