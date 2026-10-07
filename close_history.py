"""
Close History — Cycle 3, Task 1 (D10)

Implements the minimal version of "the canonical object of the Live system
is the Approved Financial Close, not a single active dataset" (D10):
- A storage-neutral way to resolve the LATEST approved close.
- A storage-neutral way to archive a newly-approved close as an immutable
  snapshot.

Storage convention for THIS challenge (GitHub-hosted folder tree):

    close_history/
        <PERIOD_LABEL>/
            raw_dataset.xlsx
            rollups_output.xlsx
            observations.csv
            narrative.txt
            metadata.json

This file intentionally does NOT hardcode any dataset filename, and does
NOT rely on filesystem-specific ordering (folder mtime, alphabetical sort,
directory-listing order) to determine "latest" — "latest approved close" is
resolved from the `approval_timestamp` field written into each snapshot's
own metadata.json. Swapping the storage backend (S3, SharePoint, a DB) only
requires re-implementing the small set of functions below (list snapshots,
read a snapshot's metadata, write a snapshot) — the resolution *logic*
(pick the metadata with the max approval_timestamp) does not change.

This module contains NO tie-out, allocation, or narrative calculation
logic. It only resolves what data feeds the pipeline and archives what the
pipeline (and the plausibility/diff phases) produced.
"""

import os
import glob
import json
import shutil
import stat
import subprocess
from datetime import datetime, timezone

DEFAULT_CLOSE_HISTORY_DIR = "close_history"

REQUIRED_SNAPSHOT_FILES = [
    "raw_dataset.xlsx",
    "rollups_output.xlsx",
    "observations.csv",
    "narrative.txt",
    "metadata.json",
]


class BootstrapRequired(Exception):
    """Raised by callers that want an explicit signal (rather than a bare
    None) that Close History is empty and the bootstrap path must run."""
    pass


def get_git_commit_hash(repo_dir="."):
    """The commit hash of the pipeline code that produced a given close.
    Storage-neutral: this is metadata about the CODE, not about the close
    storage backend, and is computed the same way regardless of where
    close_history itself lives."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_dir, capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return "unknown (git not available or repo not initialized)"


def _is_legacy_unversioned_snapshot(folder):
    """A pre-D15 snapshot folder is close_history/<period_label>/ directly
    containing metadata.json (no v{n}/ subfolder level). D15 (Section 5.A)
    requires zero migration of these — every pre-D15 snapshot is treated as
    an *implicit v1* by every function below, without rewriting any file on
    disk."""
    return os.path.isfile(os.path.join(folder, "metadata.json"))


def _version_folders(period_folder):
    """Return sorted (version_int, folder_path) pairs for every vN/
    subfolder under a period folder that has a readable metadata.json.
    Does not include a legacy unversioned snapshot (callers that need to
    treat a legacy snapshot as v1 do so explicitly via
    _is_legacy_unversioned_snapshot, per Section 5.A: 'no migration of
    existing files, no rewriting of existing snapshot data')."""
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


def list_approved_closes(close_history_dir=DEFAULT_CLOSE_HISTORY_DIR, latest_version_only=True):
    """Return a list of (period_label, metadata_dict, folder_path) for every
    approved snapshot under close_history_dir.

    D15 (Section 5.A) extension: a period_label folder may now contain
    either (a) a legacy pre-D15 unversioned snapshot (metadata.json
    directly inside it — treated as implicit v1), or (b) one or more
    v{n}/ subfolders. latest_version_only (default True, matching every
    pre-D15 caller's existing behavior with ZERO code change required of
    them) returns only the highest version per period; False returns every
    version of every period, each still keyed by its own period_label so
    existing single-result-per-period callers are unaffected by default.

    Does NOT sort by folder name or mtime — sorting by recency is the
    caller's job (resolve_latest_approved_close), and it sorts by the
    approval_timestamp field inside metadata.json, not by anything
    filesystem-specific."""
    if not os.path.isdir(close_history_dir):
        return []
    out = []
    for entry in os.listdir(close_history_dir):
        folder = os.path.join(close_history_dir, entry)
        if not os.path.isdir(folder):
            continue

        versions = _version_folders(folder)
        if _is_legacy_unversioned_snapshot(folder):
            # Legacy pre-D15 snapshot: implicit v1, read from the period
            # folder itself, never migrated.
            try:
                with open(os.path.join(folder, "metadata.json")) as f:
                    meta = json.load(f)
                versions = [(1, folder)] + versions
            except (json.JSONDecodeError, OSError):
                pass

        if not versions:
            continue

        if latest_version_only:
            v, vfolder = versions[-1]
            try:
                with open(os.path.join(vfolder, "metadata.json")) as f:
                    meta = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue
            out.append((entry, meta, vfolder))
        else:
            for v, vfolder in versions:
                try:
                    with open(os.path.join(vfolder, "metadata.json")) as f:
                        meta = json.load(f)
                except (json.JSONDecodeError, OSError):
                    continue
                out.append((entry, meta, vfolder))
    return out


def resolve_version(period_label, version, close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """Return the specific (period_label, version) snapshot, or an explicit
    not-found result — NEVER silently falls back to latest (Section 5.A).

    Returns a dict identical in shape to resolve_latest_approved_close()'s
    return value (plus a 'version' key), or None if that exact version does
    not exist for that period."""
    folder = os.path.join(close_history_dir, period_label)
    if not os.path.isdir(folder):
        return None

    target_folder = None
    if version == 1 and _is_legacy_unversioned_snapshot(folder):
        target_folder = folder
    vfolder_candidate = os.path.join(folder, f"v{version}")
    if os.path.isdir(vfolder_candidate) and os.path.isfile(os.path.join(vfolder_candidate, "metadata.json")):
        target_folder = vfolder_candidate

    if target_folder is None:
        return None

    try:
        with open(os.path.join(target_folder, "metadata.json")) as f:
            meta = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    return {
        "period_label": period_label,
        "version": version,
        "folder": target_folder,
        "metadata": meta,
        "raw_dataset_path": os.path.join(target_folder, "raw_dataset.xlsx"),
        "rollups_output_path": os.path.join(target_folder, "rollups_output.xlsx"),
        "observations_path": os.path.join(target_folder, "observations.csv"),
        "narrative_path": os.path.join(target_folder, "narrative.txt"),
    }


def next_version_for_period(period_label, close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """D15 Item 2, correction 1: the version a NEW archive_close() call
    should use for period_label -- one more than the highest existing
    version for THAT period (a legacy pre-D15 unversioned snapshot counts
    as v1), or 1 if the period has no approved snapshot at all. Never
    hardcoded by a caller -- this is the single place that decision is
    made, so two independent callers can never disagree about what the
    "next" version is."""
    existing_versions = [
        meta.get("version", 1)
        for (label, meta, folder) in list_approved_closes(close_history_dir, latest_version_only=False)
        if label == period_label
    ]
    return (max(existing_versions) + 1) if existing_versions else 1


def resolve_latest_approved_close_for_period(period_label, close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """D15 Item 2, correction 3: return period_label's OWN latest-version
    approved close, or None if that period has no approved snapshot at
    all -- never comparing approval_timestamp across DIFFERENT periods.

    This exists specifically because resolve_latest_approved_close()
    ranks candidates by approval_timestamp GLOBALLY, across every period
    in Close History. That is the correct question for callers that
    genuinely want "the single most recently approved close, of any
    period" (e.g. rollups.py's find_raw_dataset() bootstrap resolution,
    which needs exactly that to pick a default dataset when nothing else
    tells it which period to load). It is the WRONG question for a caller
    that wants to know whether one SPECIFIC period's own close is durably
    archived -- e.g. the dashboard's "Executive Ready" status strip for
    `target_period`. Once D15 makes it possible to approve a close for a
    historical period (a reopen/correction) with a timestamp newer than
    another, unrelated period's own most recent approval,
    resolve_latest_approved_close() would return that OTHER period's
    snapshot to a caller asking about `target_period` -- silently
    changing `target_period`'s own Executive Ready status because of an
    action taken against a completely different period. Callers that need
    "is THIS period's own latest version durably archived" must use this
    function instead.

    resolve_latest_approved_close() itself is intentionally left
    UNCHANGED -- its existing global-latest-by-timestamp semantics remain
    correct for the callers that actually need them."""
    for (label, meta, folder) in list_approved_closes(close_history_dir, latest_version_only=True):
        if label == period_label:
            return {
                "period_label": label,
                "version": meta.get("version", 1),
                "folder": folder,
                "metadata": meta,
                "raw_dataset_path": os.path.join(folder, "raw_dataset.xlsx"),
                "rollups_output_path": os.path.join(folder, "rollups_output.xlsx"),
                "observations_path": os.path.join(folder, "observations.csv"),
                "narrative_path": os.path.join(folder, "narrative.txt"),
            }
    return None


def resolve_canonical_dataset_path():
    """Principal-directed extension (two-tier per-period data sourcing,
    live-testing session): the one fixed, canonical raw dataset -- the
    original seed workbook, never written to or perturbed by any close,
    reopen, or correction activity. Single source of truth for two
    call sites that both need the exact same file:
      1. rollups.py's own bootstrap fallback (Close History empty --
         nothing approved yet to resolve).
      2. period_lifecycle.assemble_governed_dataset() and
         enforce_period_scoped_correction()'s fallback for any period
         that has never been closed -- such a period's value must never
         come from a correction upload for some OTHER period (even one
         that happens to include out-of-period rows mentioning it), only
         from this canonical file, until it is itself closed for the
         first time.
    Previously this glob search lived only inside rollups.py's own
    find_raw_dataset(), duplicated here would have meant two
    independently-maintained definitions of "canonical" that could
    silently drift apart -- this is the one definition both now use.
    """
    candidates = [
        f for f in glob.glob("*.xlsx")
        if "northwind" in f.lower() and "sample" in f.lower() and "dataset" in f.lower()
        and "output" not in f.lower()
    ]
    if not candidates:
        raise FileNotFoundError(
            "Could not resolve the canonical raw dataset: expected a file with 'Northwind', "
            "'Sample', and 'Dataset' in the name, e.g. 'Northwind_Sample_Dataset.xlsx', in the "
            "current directory."
        )
    if len(candidates) > 1:
        raise FileNotFoundError(
            f"Found multiple candidate canonical dataset files, ambiguous which to use: {candidates}. "
            "Keep only one in this directory, or rename the others."
        )
    return candidates[0]


def resolve_latest_approved_close(close_history_dir=DEFAULT_CLOSE_HISTORY_DIR, latest_version_only=True):
    """Return a dict describing the latest APPROVED close, or None if
    Close History is empty / has no valid snapshots (the bootstrap case).

    'Latest' = max metadata['approval_timestamp'] across all valid
    snapshots — not folder name, not mtime, not directory listing order.

    D15 (Section 5.A): latest_version_only (default True — existing callers
    unaffected with zero code change) restricts candidates to each period's
    highest version before ranking by approval_timestamp. This parameter
    exists for signature symmetry with list_approved_closes(); with the
    default True it has no behavioral effect versus pre-D15 canonical,
    since each period previously had exactly one snapshot."""
    closes = list_approved_closes(close_history_dir, latest_version_only=latest_version_only)
    if not closes:
        return None

    def _ts(item):
        _, meta, _ = item
        ts = meta.get("approval_timestamp")
        try:
            return datetime.fromisoformat(ts)
        except (TypeError, ValueError):
            # A snapshot missing/with a malformed timestamp can't be ranked;
            # treat as earliest so it never wins "latest" by accident.
            return datetime.min.replace(tzinfo=timezone.utc)

    period_label, meta, folder = max(closes, key=_ts)
    return {
        "period_label": period_label,
        "version": meta.get("version", 1),
        "folder": folder,
        "metadata": meta,
        "raw_dataset_path": os.path.join(folder, "raw_dataset.xlsx"),
        "rollups_output_path": os.path.join(folder, "rollups_output.xlsx"),
        "observations_path": os.path.join(folder, "observations.csv"),
        "narrative_path": os.path.join(folder, "narrative.txt"),
    }


def archive_close(
    period_label,
    raw_dataset_src,
    rollups_output_src,
    observations_df,
    narrative_text,
    phase2_flag_count,
    phase3_flag_count,
    workflow_state,
    prior_close_period_label,
    close_history_dir=DEFAULT_CLOSE_HISTORY_DIR,
    repo_dir=".",
    extra_metadata=None,
    commentary_record=None,
    version=1,
):
    """Write one immutable snapshot folder under close_history_dir.

    raw_dataset_src / rollups_output_src: paths to the already-built files
    to copy in (this function does not build them — no calc logic here).
    observations_df: a DataFrame written to observations.csv (may be empty).
    narrative_text: written to narrative.txt as-is. Per the Brief, this
    reflects ACTUAL behavior (AI-generated narrative text, or the rendered
    prompt if no API key was available) rather than assuming a live-API
    path always ran.
    commentary_record: JSON-serializable dict of the COMPLETE Commentary
    Record (Phase 4-6 Brief v4, Section F) — original imported version,
    every subsequent complete revision, each version's stored validation
    result, and the accepted_version_number, for every observation that had
    commentary this close. Produced by
    commentary_workflow.serialize_commentary_records(). Explicitly
    present-and-{} rather than silently absent when no commentary workflow
    ran this close (e.g. Cycle 3 Task 1's D10 snapshots, produced before
    Phase 4-6 existed), so the metadata record is honest about what phase
    of the product produced a given snapshot. No intermediate commentary
    version is discarded — this is stored as supplied, verbatim.
    """
    period_folder = os.path.join(close_history_dir, period_label)
    # D15, Section 5.A: new archives always use the versioned layout
    # close_history/{period_label}/v{n}/, regardless of the 'version' value
    # passed (including version=1). Pre-D15 snapshots (metadata.json
    # directly under period_folder) are NEVER migrated or rewritten — they
    # remain readable as implicit v1 via list_approved_closes()/
    # resolve_version(), but a *new* v1 archive for that same period_label
    # is a distinct write path and must not silently coexist with an
    # unversioned legacy v1: that would be two things both claiming to be
    # v1, breaking the "one immutable record per version" guarantee.
    if version == 1 and _is_legacy_unversioned_snapshot(period_folder):
        raise FileExistsError(
            f"Close History snapshot '{_display_label(period_label)}' already exists (as a legacy, "
            f"pre-D15 unversioned v1) at {period_folder} — snapshots are immutable "
            "and must not be overwritten. Use resolve_version(period_label, 1) to "
            "read it, or archive_close(..., version=2) to record a correction."
        )
    folder = os.path.join(period_folder, f"v{version}")
    if os.path.isdir(folder):
        raise FileExistsError(
            f"Close History snapshot '{_display_label(period_label)}' version {version} already exists at "
            f"{folder} — snapshots are immutable and must not be overwritten."
        )
    os.makedirs(folder, exist_ok=False)

    shutil.copyfile(raw_dataset_src, os.path.join(folder, "raw_dataset.xlsx"))
    shutil.copyfile(rollups_output_src, os.path.join(folder, "rollups_output.xlsx"))
    observations_df.to_csv(os.path.join(folder, "observations.csv"), index=False)
    with open(os.path.join(folder, "narrative.txt"), "w") as f:
        f.write(narrative_text)

    metadata = {
        "period_label": period_label,
        "version": version,
        "approval_timestamp": datetime.now(timezone.utc).isoformat(),
        "workflow_state": workflow_state,
        "phase2_flag_count": phase2_flag_count,
        "phase3_flag_count": phase3_flag_count,
        "prior_close_period_label": prior_close_period_label,  # None for the bootstrap snapshot
        "pipeline_git_commit_hash": get_git_commit_hash(repo_dir),
        # Explicitly present-and-null rather than silently absent, per the
        # Brief's out-of-scope note: these artifacts are not built this
        # cycle, and that must be visible in the record, not just implied
        # by a missing key.
        "dashboard_html": None,
        "board_deck_pptx": None,
        # Phase 4-6 Brief v4, Section F: complete Commentary Record captured
        # at close approval. {} (not None) when no commentary workflow ran
        # this close, so "ran and found nothing" stays distinguishable from
        # "this field didn't exist yet" only by the pipeline_git_commit_hash
        # / snapshot date, not by a silently-different value shape.
        "commentary_record": commentary_record if commentary_record is not None else {},
    }
    if extra_metadata:
        metadata.update(extra_metadata)

    with open(os.path.join(folder, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    return folder, metadata


# -----------------------------------------------------------------------
# D15 Items 3 & 4 — Chronological Close-Order Enforcement & Reopen-
# Propagation Blocking (Principal-confirmed 2026-09-28). Two small sidecar
# files, deliberately NOT new close-history versions or a schema change to
# the existing snapshot format: both live ALONGSIDE, never inside, the
# versioned snapshot folders, so resolve_latest_approved_close_for_period()/
# resolve_latest_approved_close() and Executive Ready logic never see them
# and cannot be affected by them.
# -----------------------------------------------------------------------

BASELINE_FILENAME = "_baseline.json"
PENDING_REPROCESSING_FILENAME = "pending_reprocessing.json"


class ControlFileError(Exception):
    """A close-order control file (_baseline.json or a period's
    pending_reprocessing.json) exists but cannot be trusted: unreadable,
    truncated, not valid JSON, or missing its required key. Deliberately
    NOT treated as "file absent": an absent file means "rule not started /
    period not flagged", whereas a damaged one means the rule state is
    unknown, so callers must fail safe (block) rather than fail open."""


def _read_control_json(path, required_key):
    """None if the file does not exist; the parsed dict if it is valid;
    ControlFileError if it exists but is damaged."""
    if not os.path.isfile(path):
        return None
    try:
        with open(path) as f:
            rec = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        raise ControlFileError(f"{path} exists but cannot be read ({type(exc).__name__}: {exc}).")
    if not isinstance(rec, dict) or required_key not in rec:
        raise ControlFileError(f"{path} exists but is missing its required field '{required_key}'.")
    return rec


def _write_json_atomic(path, record):
    """Write via a temp file in the same folder, then os.replace(), so a
    crash mid-write can never leave a truncated control file behind."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(record, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def read_close_order_baseline(close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """Returns the write-once bootstrap-baseline record
    {"baseline_period": <label>, "established_at": <iso ts>}, or None if
    no period has ever closed under this rule yet (close-order enforcement
    has not started). Raises ControlFileError if the file exists but is
    damaged (never silently treated as absent)."""
    return _read_control_json(os.path.join(close_history_dir, BASELINE_FILENAME), "baseline_period")


def establish_close_order_baseline_if_absent(period_label, close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """Write close_history/_baseline.json exactly once — the first time
    any period closes under this rule — recording period_label as the
    permanent baseline. A no-op returning the EXISTING record, unchanged,
    if a baseline already exists: never overwritten, recomputed, or moved
    afterward, per the confirmed bootstrap rule. A DAMAGED existing
    baseline raises ControlFileError and is never overwritten. This
    function only writes the record; it is the caller's responsibility to
    call it only on a close attempt's own success, never speculatively."""
    existing = read_close_order_baseline(close_history_dir)
    if existing is not None:
        return existing
    record = {
        "baseline_period": period_label,
        "established_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_json_atomic(os.path.join(close_history_dir, BASELINE_FILENAME), record)
    return record


# -----------------------------------------------------------------------
# Fix K ("No flag, no approval", brief v2.3): attempt record on marks.
# A mark written during a reopen-and-correct approval attempt carries four
# OPTIONAL fields (attempt_id, reopened_period, expected_version,
# prior_state). Marks without attempt_id (old files, post-save resolved
# marks) behave exactly as before.
# -----------------------------------------------------------------------

def _display_label(period):
    """Display-only 'Q3 FY2026' -> 'Q3 2026' (mirror of rollups.fmt_period_label,
    which this module does not import). v2.4 A3: messages never show a
    'Q# FY####' label; folder paths are unaffected."""
    import re
    m = re.match(r"^(Q[1-4]) FY(\d{4})$", period) if isinstance(period, str) else None
    return f"{m.group(1)} {m.group(2)}" if m else period


ATTEMPT_FIELDS = ("attempt_id", "reopened_period", "expected_version", "prior_state", "attempt_at")

# D6 (Principal-approved): how long an unmatched mark is treated as "in
# doubt" (the attempt may still be running) before M7 may release it. The
# time is NOT the evidence of abandonment; the missing save is.
PENDING_GRACE_SECONDS = 15 * 60


def _utcnow():
    """Single clock for M7 so tests can inject time."""
    return datetime.now(timezone.utc)


def _pending_reprocessing_path(period_label, close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    return os.path.join(close_history_dir, period_label, PENDING_REPROCESSING_FILENAME)


def read_pending_mark_raw(period_label, close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """The mark file exactly as stored (no M7 evaluation). None if absent;
    ControlFileError if damaged. Used for read-back verification and by the
    evaluation itself."""
    return _read_control_json(
        _pending_reprocessing_path(period_label, close_history_dir), "predecessor_period_label"
    )


def _scan_for_matching_save(reopened_period, attempt_id, close_history_dir):
    """"saved" if a COMPLETE version folder (readable metadata.json) of
    reopened_period carries attempt_id; "none" if the folder was listed and
    read cleanly and no such save exists; "unknown" if anything could not be
    listed or read (caller must fail safe). A version folder with no
    metadata.json is an incomplete save and is ignored (same as every
    existing reader)."""
    period_folder = os.path.join(close_history_dir, reopened_period)
    try:
        entries = os.listdir(period_folder)
    except OSError:
        return "unknown"
    unknown = False
    for entry in entries:
        if not entry.startswith("v"):
            continue
        try:
            int(entry[1:])
        except ValueError:
            continue  # e.g. "v2.incomplete-<ts>" (moved aside) or unrelated
        vfolder = os.path.join(period_folder, entry)
        try:
            if not stat.S_ISDIR(os.stat(vfolder).st_mode):
                continue  # a plain file cannot hold a save
        except OSError:
            unknown = True
            continue
        try:
            with open(os.path.join(vfolder, "metadata.json")) as f:
                meta = json.load(f)
        except FileNotFoundError:
            continue  # incomplete version folder: no save
        except (OSError, ValueError, UnicodeDecodeError):
            unknown = True
            continue
        if isinstance(meta, dict) and meta.get("attempt_id") == attempt_id:
            return "saved"
    return "unknown" if unknown else "none"


def _evaluate_mark(rec, close_history_dir):
    """M7 rule. Returns (effective_record_or_None, status) where status is
    one of: "legacy" (no attempt_id: returned unchanged), "saved",
    "in_doubt", "released" (no save established; effective record is the
    prior state), "flagged_prior_damaged" (no save established but the
    prior file was damaged: stays flagged, fail-safe).

    PRODUCTION-STORAGE NOTE (Principal footnote, Fix K Addendum
    2026-10-01): this rule assumes a write either fully completes or fully
    fails with no partial-visibility window, as on the Codespace file
    system. It MUST be explicitly revisited if the project moves to
    different storage (network or object storage with delayed visibility),
    which could release a mark too early or leave a quarter stuck.

    Pure read: never deletes or rewrites anything."""
    attempt_id = rec.get("attempt_id")
    if not attempt_id:
        return rec, "legacy"
    reopened = rec.get("reopened_period") or rec.get("predecessor_period_label")
    scan = _scan_for_matching_save(reopened, attempt_id, close_history_dir) if reopened else "unknown"
    # 1. matching complete save -> the save happened, forever.
    if scan == "saved":
        return rec, "saved"
    # 2. younger than the grace period -> in doubt. v2.4 A2: the grace is
    # measured from attempt_at; flagged_at is used only when attempt_at is
    # absent (a mark written without it).
    try:
        started = datetime.fromisoformat(rec["attempt_at"] if rec.get("attempt_at") else rec.get("flagged_at"))
        if started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        age = (_utcnow() - started).total_seconds()
    except (TypeError, ValueError):
        return rec, "in_doubt"
    if age < PENDING_GRACE_SECONDS:
        return rec, "in_doubt"
    # 3. folder could not be listed/read -> in doubt (fail safe).
    if scan != "none":
        return rec, "in_doubt"
    # 4. established: no save occurred. Return the prior state.
    prior = rec.get("prior_state")
    if isinstance(prior, dict) and prior.get("kind") == "none":
        return None, "released"
    if isinstance(prior, dict) and prior.get("kind") == "mark" and isinstance(prior.get("record"), dict):
        return prior["record"], "released"
    return rec, "flagged_prior_damaged"


def read_pending_reprocessing(period_label, close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """Returns period_label's sidecar dict, or None if it has never been
    flagged as reopen-affected. Raises ControlFileError if the file exists
    but is damaged. Does NOT itself apply the Definitions "resolved" test
    (design note §3) — a returned dict may carry resolved: true; callers
    deciding blocking status should treat resolved: true the same as no
    record at all.

    Fix K (M7): a mark carrying an attempt_id is evaluated here, at the one
    place every reader goes through. If it is established that the attempt's
    correction was never saved, the mark's prior state is returned as if the
    attempt never happened. Marks without attempt_id are returned exactly as
    stored."""
    rec = read_pending_mark_raw(period_label, close_history_dir)
    if rec is None:
        return None
    effective, _status = _evaluate_mark(rec, close_history_dir)
    return effective


def released_pending_marks(period_order, close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """M11 / D8: the marks currently evaluated as released (no save
    established), oldest period first, as
    [{"period", "reopened_period", "attempt_id"}]. A damaged file or an
    in-doubt/saved mark is never listed."""
    out = []
    for p in period_order:
        try:
            rec = read_pending_mark_raw(p, close_history_dir)
        except ControlFileError:
            continue
        if rec is None:
            continue
        _eff, status = _evaluate_mark(rec, close_history_dir)
        if status == "released":
            out.append({
                "period": p,
                "reopened_period": rec.get("reopened_period") or rec.get("predecessor_period_label"),
                "attempt_id": rec.get("attempt_id"),
            })
    return out


def capture_pending_state(period_label, close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """Snapshot of period_label's mark file before an attempt touches it:
    {"kind": "none"|"mark"|"damaged", "record": dict|None, "raw": bytes|None}.
    "raw" is the exact file content (for byte-for-byte undo); kind/record
    are what goes into the mark's prior_state. If the existing file is an
    attempt mark that is not (yet) a proven save (in doubt or released),
    the capture takes ITS prior_state, ignoring that attempt."""
    path = _pending_reprocessing_path(period_label, close_history_dir)
    if not os.path.lexists(path):
        return {"kind": "none", "record": None, "raw": None}
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except OSError:
        return {"kind": "damaged", "record": None, "raw": None}
    try:
        rec = read_pending_mark_raw(period_label, close_history_dir)
    except ControlFileError:
        return {"kind": "damaged", "record": None, "raw": raw}
    if rec is None:
        return {"kind": "none", "record": None, "raw": raw}
    if rec.get("attempt_id"):
        _eff, status = _evaluate_mark(rec, close_history_dir)
        if status != "saved":
            prior = rec.get("prior_state")
            if isinstance(prior, dict) and prior.get("kind") == "none":
                return {"kind": "none", "record": None, "raw": raw}
            if isinstance(prior, dict) and prior.get("kind") == "mark" and isinstance(prior.get("record"), dict):
                return {"kind": "mark", "record": prior["record"], "raw": raw}
            return {"kind": "damaged", "record": None, "raw": raw}
    return {"kind": "mark", "record": rec, "raw": raw}


def _attempt_block(attempt, prior_state):
    if not attempt:
        return {}
    ps = {"kind": "none"}
    if prior_state is not None:
        ps = {"kind": prior_state["kind"]}
        if prior_state.get("record") is not None:
            ps["record"] = prior_state["record"]
    return {
        "attempt_id": attempt["attempt_id"],
        "reopened_period": attempt["reopened_period"],
        "expected_version": attempt["expected_version"],
        "prior_state": ps,
        # v2.4 A2: the attempt's own time (grace period starts here, so
        # flagged_at can stay the mark's original value on a Fix F clear).
        "attempt_at": attempt.get("attempt_at") or _utcnow().isoformat(),
    }


def write_pending_reprocessing(period_label, predecessor_period_label, close_history_dir=DEFAULT_CLOSE_HISTORY_DIR,
                               attempt=None, prior_state=None):
    """5.G propagation-writing step: mark period_label as affected by an
    upstream reopen and not yet resolved, naming the reopened predecessor
    that caused it. Overwrites any existing (e.g. already-resolved or
    damaged) record for period_label — a period can be re-flagged by a
    later, independent reopen after a prior flag was resolved.

    Fix K: optional attempt = {"attempt_id", "reopened_period",
    "expected_version"} plus prior_state (from capture_pending_state) add the
    attempt record. Without them the record is exactly as before."""
    record = {
        "period_label": period_label,
        "predecessor_period_label": predecessor_period_label,
        "flagged_at": _utcnow().isoformat(),
        "resolved": False,
    }
    record.update(_attempt_block(attempt, prior_state))
    _write_json_atomic(_pending_reprocessing_path(period_label, close_history_dir), record)
    return record


def write_attempt_resolved_pending_reprocessing(period_label, current_record, attempt, prior_state,
                                                close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """Fix F clear performed as part of a Fix K attempt: the same resolved
    state resolve_pending_reprocessing() would write, but carrying the
    attempt record so it is restorable (M3/M5)."""
    rec = {k: v for k, v in current_record.items() if k not in ATTEMPT_FIELDS}
    rec["resolved"] = True
    rec["resolved_at"] = _utcnow().isoformat()
    # v2.4 A2: flagged_at is left exactly as the mark had it (as 691e8f4's
    # resolve does); the attempt's time is in attempt_at.
    rec.update(_attempt_block(attempt, prior_state))
    _write_json_atomic(_pending_reprocessing_path(period_label, close_history_dir), rec)
    return rec


def restore_pending_state(period_label, snapshot, close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """M5 undo for one quarter: put the file back exactly as captured
    (delete it if there was none), then compare. Returns None on success or
    an error string. A DAMAGED prior file is deliberately NOT restored: the
    attempt's own mark is left in place, so the quarter stays flagged
    (fail-safe). Never raises."""
    path = _pending_reprocessing_path(period_label, close_history_dir)
    try:
        if snapshot["kind"] == "damaged":
            return None
        # Already exactly the prior state (e.g. the attempt's write failed
        # before changing anything): nothing to undo.
        if snapshot["raw"] is None and not os.path.lexists(path):
            return None
        if snapshot["raw"] is not None and os.path.isfile(path):
            with open(path, "rb") as f:
                if f.read() == snapshot["raw"]:
                    return None
        if snapshot["raw"] is None:
            if os.path.lexists(path):
                os.remove(path)
            if os.path.lexists(path):
                return "file still present after undo"
            return None
        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(snapshot["raw"])
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        with open(path, "rb") as f:
            if f.read() != snapshot["raw"]:
                return "restored file does not match its prior content"
        return None
    except Exception as exc:  # noqa: BLE001 - undo must never raise (M5)
        return f"{type(exc).__name__}: {exc}"


def move_aside_incomplete_version(period_label, version, close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """M6 (D7): rename -- never delete -- an incomplete version folder so a
    retry can create it. Only a DIRECTORY named v<version> that has no
    metadata.json. Returns the new path, or None if nothing was moved."""
    folder = os.path.join(close_history_dir, period_label, f"v{version}")
    if not os.path.isdir(folder) or os.path.lexists(os.path.join(folder, "metadata.json")):
        return None
    stamp = _utcnow().strftime("%Y%m%dT%H%M%S%fZ")
    target = f"{folder}.incomplete-{stamp}"
    os.rename(folder, target)
    return target


def resolve_pending_reprocessing(period_label, close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """Mark period_label's pending_reprocessing.json resolved: true —
    called when that period is itself reopened and re-closed, or when a
    later re-close shows it is no longer affected. A no-op (returns None)
    if no such record exists for period_label.

    Fix K: attempt fields are dropped from the resolved record (it becomes
    a plain resolved mark, exactly the pre-Fix-K shape). A mark that M7
    evaluates as released is also given this plain resolved record, so the
    orphaned file is replaced (never deleted) and the D8 notice stops."""
    raw = read_pending_mark_raw(period_label, close_history_dir)
    if raw is None:
        return None
    effective, _status = _evaluate_mark(raw, close_history_dir)
    base = effective if effective is not None else raw
    rec = {k: v for k, v in base.items() if k not in ATTEMPT_FIELDS}
    rec["resolved"] = True
    rec["resolved_at"] = _utcnow().isoformat()
    _write_json_atomic(_pending_reprocessing_path(period_label, close_history_dir), rec)
    return rec


def reprocessing_state_by_period(period_order, close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """The dict shape period_lifecycle.find_blocking_predecessor() (5.H)
    expects: {period_label -> {"reprocessing_required": bool, "resolved": bool}}.
    Derived purely by checking each period in period_order for this
    sidecar file's presence — not a new complex data model, per the
    Brief's Implementation section."""
    out = {}
    for p in period_order:
        rec = read_pending_reprocessing(p, close_history_dir)
        if rec is None:
            continue
        out[p] = {
            "reprocessing_required": True,
            "resolved": bool(rec.get("resolved", False)),
        }
    return out
