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


def list_approved_closes(close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """Return a list of (period_label, metadata_dict, folder_path) for every
    snapshot under close_history_dir that has a readable metadata.json.
    Does NOT sort by folder name or mtime — sorting by recency is the
    caller's job (resolve_latest_approved_close), and it sorts by the
    approval_timestamp field inside metadata.json, not by anything
    filesystem-specific."""
    if not os.path.isdir(close_history_dir):
        return []
    out = []
    for entry in os.listdir(close_history_dir):
        folder = os.path.join(close_history_dir, entry)
        meta_path = os.path.join(folder, "metadata.json")
        if os.path.isdir(folder) and os.path.isfile(meta_path):
            try:
                with open(meta_path) as f:
                    meta = json.load(f)
                out.append((entry, meta, folder))
            except (json.JSONDecodeError, OSError):
                # A folder with a corrupt/unreadable metadata.json is not a
                # usable approved close; skip it rather than error the whole
                # resolution (evidence-based, doesn't assume a clean store).
                continue
    return out


def resolve_latest_approved_close(close_history_dir=DEFAULT_CLOSE_HISTORY_DIR):
    """Return a dict describing the latest APPROVED close, or None if
    Close History is empty / has no valid snapshots (the bootstrap case).

    'Latest' = max metadata['approval_timestamp'] across all valid
    snapshots — not folder name, not mtime, not directory listing order.
    """
    closes = list_approved_closes(close_history_dir)
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
    folder = os.path.join(close_history_dir, period_label)
    if os.path.isdir(folder):
        raise FileExistsError(
            f"Close History snapshot '{period_label}' already exists at {folder} — "
            "snapshots are immutable and must not be overwritten."
        )
    os.makedirs(folder, exist_ok=False)

    shutil.copyfile(raw_dataset_src, os.path.join(folder, "raw_dataset.xlsx"))
    shutil.copyfile(rollups_output_src, os.path.join(folder, "rollups_output.xlsx"))
    observations_df.to_csv(os.path.join(folder, "observations.csv"), index=False)
    with open(os.path.join(folder, "narrative.txt"), "w") as f:
        f.write(narrative_text)

    metadata = {
        "period_label": period_label,
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
