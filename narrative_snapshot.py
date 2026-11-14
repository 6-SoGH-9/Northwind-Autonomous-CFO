"""
narrative_snapshot.py -- D22 Builder Brief v3, Release 1, WP1.

Read-only classification of a period's approved Close History snapshot for the
AI Narrative tab, and the read-back of the commentary the narrative prompt is
built from. It exists because the public functions of close_history.py cannot
tell a DAMAGED close from a period that was NEVER CLOSED: list_approved_closes()
silently skips a period whose latest metadata.json cannot be parsed, so
resolve_latest_approved_close_for_period() returns None for both (one of the two
defects logged in Handbook Section 10, deliberately NOT fixed here, WP1-5).

This module:
  * never writes, renames or deletes anything;
  * does not import-modify or patch close_history.py (it only reads the
    DEFAULT_CLOSE_HISTORY_DIR constant);
  * never falls back to session state or to an older healthy version (WP1-1,
    WP1-3: damage is judged on the latest version only).

States (WP1-3, Handbook D22-C (5), D22-D (7)):
  NOT CLOSED  the period has no folder in Close History, or no version folder
              (or legacy root) holds a metadata.json file.
  DAMAGED     the latest version's metadata.json exists but cannot be parsed
              or is not a JSON object; and, for narrative generation
              (read_narrative_snapshot), also when its commentary_record cannot
              be rebuilt or its observations.csv cannot be read.
  READABLE    otherwise.
A version folder with no metadata.json is an interrupted save and is ignored,
exactly as close_history.py ignores it.

COPIED LOGIC (named for the Return Report, Brief "File discipline"):
  _is_legacy_unversioned_snapshot()  <- close_history._is_legacy_unversioned_snapshot
  _version_folders()                 <- close_history._version_folders
  _candidate_versions()              <- the legacy-first ordering used in
                                        close_history.list_approved_closes()
                                        (legacy root counts as implicit v1 and
                                        precedes the vN/ folders; the LAST
                                        candidate is the latest version).
tests/test_snapshot_classifier.py has a parity test that, on healthy stores,
compares the folder chosen here with
close_history.resolve_latest_approved_close_for_period(), so drift is detected.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence

import pandas as pd

from close_history import DEFAULT_CLOSE_HISTORY_DIR

NOT_CLOSED = "NOT CLOSED"
DAMAGED = "DAMAGED"
READABLE = "READABLE"


# ---------------------------------------------------------------------------
# Copied "latest version" logic (see module docstring)
# ---------------------------------------------------------------------------
def _is_legacy_unversioned_snapshot(folder):
    """Copy of close_history._is_legacy_unversioned_snapshot: a pre-D15 period
    folder that directly contains metadata.json (implicit v1)."""
    return os.path.isfile(os.path.join(folder, "metadata.json"))


def _version_folders(period_folder):
    """Copy of close_history._version_folders: sorted (version_int, path) for
    every vN/ subfolder of the period folder that has a metadata.json FILE.
    Whether that file parses is NOT decided here."""
    out = []
    if not os.path.isdir(period_folder):
        return out
    for entry in os.listdir(period_folder):
        if not entry.startswith("v"):
            continue
        try:
            v = int(entry[1:])
        except ValueError:
            continue
        vfolder = os.path.join(period_folder, entry)
        meta_path = os.path.join(vfolder, "metadata.json")
        if os.path.isdir(vfolder) and os.path.isfile(meta_path):
            out.append((v, vfolder))
    out.sort(key=lambda x: x[0])
    return out


def _candidate_versions(period_folder):
    """Legacy root (implicit v1) first, then the vN/ folders, as
    close_history.list_approved_closes() orders them. The last item is the
    latest version. Unlike list_approved_closes() this does not drop a
    candidate whose metadata.json fails to parse -- that is exactly the case
    this module must be able to see."""
    candidates = []
    if _is_legacy_unversioned_snapshot(period_folder):
        candidates.append((1, period_folder))
    candidates.extend(_version_folders(period_folder))
    return candidates


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------
@dataclass
class PeriodSnapshot:
    """Result of classifying one period. `detail` carries a technical reason
    for tests and logs; it is deliberately NOT shown on screen (the message
    must say 'damaged or incomplete' and assert no cause, WP1-3)."""
    period_label: str
    state: str
    folder: Optional[str] = None
    version: Optional[int] = None
    metadata: Optional[dict] = None
    detail: Optional[str] = None


def classify_period(period_label, close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """Structural classification of the LATEST version of period_label."""
    period_folder = os.path.join(close_history_dir, period_label)
    if not os.path.isdir(period_folder):
        return PeriodSnapshot(period_label, NOT_CLOSED, detail="no period folder in Close History")

    candidates = _candidate_versions(period_folder)
    if not candidates:
        return PeriodSnapshot(period_label, NOT_CLOSED, detail="no version folder holds a metadata.json")

    version, folder = candidates[-1]  # latest; no fall-back to an older version
    meta_path = os.path.join(folder, "metadata.json")
    try:
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError, ValueError, RecursionError) as exc:
        return PeriodSnapshot(
            period_label, DAMAGED, folder=folder, version=version,
            detail=f"metadata.json cannot be parsed ({type(exc).__name__}: {exc})",
        )
    if not isinstance(meta, dict):
        return PeriodSnapshot(
            period_label, DAMAGED, folder=folder, version=version,
            detail=f"metadata.json is not a JSON object ({type(meta).__name__})",
        )
    return PeriodSnapshot(period_label, READABLE, folder=folder, version=version, metadata=meta)


# ---------------------------------------------------------------------------
# Narrative read-back (adds the two narrative-only DAMAGED conditions)
# ---------------------------------------------------------------------------
@dataclass
class NarrativeSnapshot:
    """What the narrative prompt needs from one period's approved snapshot.
    register / records / commentary_file_supplied are None unless state is
    READABLE. Same meaning as the tuple the dashboard's
    _archived_commentary_for_period() returned: commentary_file_supplied is
    True iff the snapshot's Commentary Record is non-empty."""
    status: PeriodSnapshot
    register: Optional[pd.DataFrame] = None
    records: Optional[Dict[str, Any]] = None
    commentary_file_supplied: Optional[bool] = None

    @property
    def state(self):
        return self.status.state

    @property
    def period_label(self):
        return self.status.period_label


def read_narrative_snapshot(period_label, record_from_dict: Callable[[dict], Any],
                            close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """Classify period_label for NARRATIVE generation and, when READABLE, read
    back its observation register and Commentary Record.

    record_from_dict is the rebuild function for one commentary_record entry
    (the dashboard passes its existing _commentary_record_from_dict, so the
    rebuild is not implemented twice). Any exception it raises, any malformed
    commentary_record, and any failure to read observations.csv make the
    period DAMAGED (WP1-3)."""
    status = classify_period(period_label, close_history_dir)
    if status.state != READABLE:
        return NarrativeSnapshot(status)

    obs_path = os.path.join(status.folder, "observations.csv")
    try:
        register = pd.read_csv(obs_path)
    except Exception as exc:  # missing, empty, undecodable or malformed CSV
        return NarrativeSnapshot(_damaged_from(status, f"observations.csv cannot be read ({type(exc).__name__}: {exc})"))

    raw_records = status.metadata.get("commentary_record") or {}
    if not isinstance(raw_records, dict):
        return NarrativeSnapshot(_damaged_from(status, f"commentary_record is not an object ({type(raw_records).__name__})"))
    try:
        records = {oid: record_from_dict(d) for oid, d in raw_records.items()}
    except Exception as exc:
        return NarrativeSnapshot(_damaged_from(status, f"commentary_record cannot be rebuilt ({type(exc).__name__}: {exc})"))

    return NarrativeSnapshot(status, register=register, records=records, commentary_file_supplied=bool(records))


def _damaged_from(status, detail):
    return PeriodSnapshot(
        status.period_label, DAMAGED, folder=status.folder, version=status.version,
        metadata=status.metadata, detail=detail,
    )


# ---------------------------------------------------------------------------
# Annual: combining four approved quarters into commentary inputs (WP1-2)
# ---------------------------------------------------------------------------
@dataclass
class CommentaryInput:
    """One call's worth of arguments for
    commentary_workflow.build_narrative_commentary_section()."""
    register: pd.DataFrame
    records: Dict[str, Any]
    commentary_file_supplied: bool


def commentary_inputs_for_quarters(snapshots: Sequence[NarrativeSnapshot]) -> List[CommentaryInput]:
    """Turn READABLE quarter snapshots (chronological order) into the minimum
    number of build_narrative_commentary_section() inputs that keeps every
    quarter's three-way state truthful.

    build_narrative_commentary_section() takes ONE commentary_file_supplied
    flag. If the quarters that have observations all agree on that flag, their
    registers and records are combined into a single input (one block, the same
    shape Annual produced before). If they disagree (one quarter had a
    commentary file, another had none), a single flag would mislabel one of
    them ('unresolved' when no commentary process ever ran, or the reverse), so
    each such quarter is given its own input and the blocks are concatenated by
    the caller. A quarter with no observations contributes nothing and never
    decides the flag. Observation IDs include the period, so merging the
    records of different quarters cannot collide."""
    for s in snapshots:
        if s.state != READABLE:
            raise ValueError(f"{s.period_label} is {s.state}; only READABLE snapshots can supply commentary")
    with_obs = [s for s in snapshots if s.register is not None and not s.register.empty]
    if not with_obs:
        return []
    flags = {s.commentary_file_supplied for s in with_obs}
    if len(flags) == 1:
        register = pd.concat([s.register for s in with_obs], ignore_index=True)
        records: Dict[str, Any] = {}
        for s in with_obs:
            records.update(s.records)
        return [CommentaryInput(register, records, flags.pop())]
    return [CommentaryInput(s.register, dict(s.records), s.commentary_file_supplied) for s in with_obs]


# ---------------------------------------------------------------------------
# Message (WP1-1, WP1-2, WP1-4). Says "damaged or incomplete", names the
# period(s), says the close needs restoring, asserts no cause and does not
# tell the user to reopen.
# ---------------------------------------------------------------------------
def damaged_snapshot_message(display_labels: Sequence[str]) -> str:
    labels = list(display_labels)
    if not labels:
        raise ValueError("at least one period label is required")
    if len(labels) == 1:
        head = f"The approved close for {labels[0]} is damaged or incomplete and needs restoring."
        tail = "until the saved close is restored"
    else:
        head = f"The approved closes for {', '.join(labels)} are damaged or incomplete and need restoring."
        tail = "until the saved closes are restored"
    return (
        f"**{head}** Executive narrative generation and the prompt download are unavailable "
        f"{tail}."
    )
