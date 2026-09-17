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
import json
import shutil
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
            f"Close History snapshot '{period_label}' already exists (as a legacy, "
            f"pre-D15 unversioned v1) at {period_folder} — snapshots are immutable "
            "and must not be overwritten. Use resolve_version(period_label, 1) to "
            "read it, or archive_close(..., version=2) to record a correction."
        )
    folder = os.path.join(period_folder, f"v{version}")
    if os.path.isdir(folder):
        raise FileExistsError(
            f"Close History snapshot '{period_label}' version {version} already exists at "
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
