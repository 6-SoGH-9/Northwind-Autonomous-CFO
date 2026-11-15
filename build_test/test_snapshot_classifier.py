"""
Builder component tests for D22 WP1 (narrative_snapshot.py).

PROVENANCE / STATUS (read before citing these results):
  * Builder-authored, SYNTHETIC fixtures built in temporary directories at test
    time. Nothing here is the real or historical close data.
  * This is Builder regression/component evidence only. It is NOT independent
    validation or calibration (Independent Test owns that).
  * No network, no API key, no write outside a temp directory.

Run from the repository root:
    python -m unittest discover -s build_test -v
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pandas as pd  # noqa: E402

import close_history  # noqa: E402
import narrative_snapshot as NS  # noqa: E402


def _write(path, text="", mode="w", **kw):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, **kw) as f:
        f.write(text)


def _good_meta(version=1, commentary_record=None):
    return {"period_label": "Q4 FY2026", "version": version,
            "approval_timestamp": "2026-01-01T00:00:00+00:00",
            "commentary_record": {} if commentary_record is None else commentary_record}


def _make_version(folder, meta=None, obs_csv="Observation ID,Period\n", raw_meta=None):
    """Create a snapshot-shaped folder. raw_meta (str/bytes) overrides metadata.json
    content verbatim, so tests can write damaged files."""
    os.makedirs(folder, exist_ok=True)
    if raw_meta is None:
        _write(os.path.join(folder, "metadata.json"), json.dumps(meta if meta is not None else _good_meta()))
    elif isinstance(raw_meta, bytes):
        _write(os.path.join(folder, "metadata.json"), raw_meta, mode="wb")
    else:
        _write(os.path.join(folder, "metadata.json"), raw_meta)
    if obs_csv is not None:
        _write(os.path.join(folder, "observations.csv"), obs_csv)


def _tree_fingerprint(root):
    """(relative path, size, mtime_ns) for every file and directory below root."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        for n in sorted(dirnames + filenames):
            p = os.path.join(dirpath, n)
            st = os.stat(p)
            out.append((os.path.relpath(p, root), st.st_size, st.st_mtime_ns))
    return sorted(out)


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="wp1_snapshot_test_")
        self.ch = os.path.join(self.tmp, "close_history")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def period(self, label="Q4 FY2026"):
        return os.path.join(self.ch, label)

    def classify(self, label="Q4 FY2026"):
        return NS.classify_period(label, self.ch)


class TestClassifyStructure(_Base):
    # -- NOT CLOSED ----------------------------------------------------
    def test_no_close_history_dir_is_not_closed(self):
        self.assertEqual(self.classify().state, NS.NOT_CLOSED)

    def test_no_period_folder_is_not_closed(self):
        os.makedirs(self.ch)
        self.assertEqual(self.classify().state, NS.NOT_CLOSED)

    def test_empty_period_folder_is_not_closed(self):
        os.makedirs(self.period())
        self.assertEqual(self.classify().state, NS.NOT_CLOSED)

    def test_version_folder_without_metadata_is_interrupted_save_not_closed(self):
        _write(os.path.join(self.period(), "v1", "observations.csv"), "x\n")
        self.assertEqual(self.classify().state, NS.NOT_CLOSED)

    def test_period_entry_that_is_a_file_is_not_closed(self):
        _write(self.period(), "not a folder")
        self.assertEqual(self.classify().state, NS.NOT_CLOSED)

    def test_metadata_json_that_is_a_directory_is_ignored_like_close_history(self):
        os.makedirs(os.path.join(self.period(), "v1", "metadata.json"))
        self.assertEqual(self.classify().state, NS.NOT_CLOSED)

    # -- READABLE ------------------------------------------------------
    def test_healthy_v1(self):
        _make_version(os.path.join(self.period(), "v1"))
        s = self.classify()
        self.assertEqual((s.state, s.version), (NS.READABLE, 1))
        self.assertEqual(s.folder, os.path.join(self.period(), "v1"))
        self.assertIsInstance(s.metadata, dict)

    def test_healthy_legacy_unversioned_root_is_implicit_v1(self):
        _make_version(self.period())
        s = self.classify()
        self.assertEqual((s.state, s.version, s.folder), (NS.READABLE, 1, self.period()))

    def test_latest_of_several_versions_is_used(self):
        for v in (1, 2, 3):
            _make_version(os.path.join(self.period(), f"v{v}"), _good_meta(v))
        s = self.classify()
        self.assertEqual((s.state, s.version), (NS.READABLE, 3))

    def test_numeric_not_lexicographic_version_order(self):
        for v in (2, 10):
            _make_version(os.path.join(self.period(), f"v{v}"), _good_meta(v))
        self.assertEqual(self.classify().version, 10)

    def test_interrupted_newer_version_is_ignored_older_healthy_one_is_latest(self):
        _make_version(os.path.join(self.period(), "v1"))
        _write(os.path.join(self.period(), "v2", "observations.csv"), "x\n")  # no metadata.json
        s = self.classify()
        self.assertEqual((s.state, s.version), (NS.READABLE, 1))

    def test_other_folders_beside_versions_are_not_versions(self):
        _make_version(os.path.join(self.period(), "v1"))
        os.makedirs(os.path.join(self.period(), "narratives"))
        _write(os.path.join(self.period(), "narratives", "state.json"), "{}")
        self.assertEqual(self.classify().version, 1)

    # -- DAMAGED (structural) -------------------------------------------
    def test_truncated_json_is_damaged(self):
        _make_version(os.path.join(self.period(), "v1"), raw_meta='{"period_label": "Q4 FY20')
        s = self.classify()
        self.assertEqual(s.state, NS.DAMAGED)
        self.assertIsNone(s.metadata)

    def test_empty_file_is_damaged(self):
        _make_version(os.path.join(self.period(), "v1"), raw_meta="")
        self.assertEqual(self.classify().state, NS.DAMAGED)

    def test_undecodable_bytes_are_damaged(self):
        _make_version(os.path.join(self.period(), "v1"), raw_meta=b"\xff\xfe\x00{\x80")
        self.assertEqual(self.classify().state, NS.DAMAGED)

    def test_json_that_is_not_an_object_is_damaged(self):
        for payload in ("[]", "[1, 2]", '"text"', "42", "null", "true"):
            with self.subTest(payload=payload):
                shutil.rmtree(self.ch, ignore_errors=True)
                _make_version(os.path.join(self.period(), "v1"), raw_meta=payload)
                self.assertEqual(self.classify().state, NS.DAMAGED)

    def test_damage_is_judged_on_latest_version_no_fallback_to_older_healthy(self):
        _make_version(os.path.join(self.period(), "v1"))
        _make_version(os.path.join(self.period(), "v2"), raw_meta="{broken")
        s = self.classify()
        self.assertEqual((s.state, s.version), (NS.DAMAGED, 2))

    def test_corrupt_legacy_root_with_no_version_folders_is_damaged(self):
        _make_version(self.period(), raw_meta="{broken")
        s = self.classify()
        self.assertEqual((s.state, s.version, s.folder), (NS.DAMAGED, 1, self.period()))

    def test_corrupt_legacy_root_with_healthy_later_version_is_readable_on_that_version(self):
        _make_version(self.period(), raw_meta="{broken")
        _make_version(os.path.join(self.period(), "v2"), _good_meta(2))
        s = self.classify()
        self.assertEqual((s.state, s.version), (NS.READABLE, 2))

    def test_deep_nesting_does_not_crash_the_classifier(self):
        _make_version(os.path.join(self.period(), "v1"), raw_meta="[" * 200000)
        self.assertEqual(self.classify().state, NS.DAMAGED)

    # -- read-only guarantee -------------------------------------------
    def test_classifier_changes_nothing_on_disk(self):
        _make_version(os.path.join(self.period(), "v1"))
        _make_version(os.path.join(self.period(), "v2"), raw_meta="{broken")
        _make_version(self.period("Q3 FY2026"), _good_meta())
        before = _tree_fingerprint(self.tmp)
        for label in ("Q4 FY2026", "Q3 FY2026", "Q1 FY2026"):
            self.classify(label)
            NS.read_narrative_snapshot(label, lambda d: d, self.ch)
        self.assertEqual(before, _tree_fingerprint(self.tmp))


class TestParityWithCloseHistory(_Base):
    """The classifier copies close_history's latest-version logic. On healthy
    stores it must pick the same folder close_history picks; on a damaged
    latest version close_history reports None (the logged defect), which is
    exactly why a separate classifier exists."""

    def _archive(self, label, version):
        raw = os.path.join(self.tmp, "raw.xlsx")
        roll = os.path.join(self.tmp, "roll.xlsx")
        _write(raw, "raw", mode="w")
        _write(roll, "roll", mode="w")
        return close_history.archive_close(
            label, raw, roll, pd.DataFrame({"Observation ID": [], "Period": []}), "n", 0, 0,
            "approved", None, close_history_dir=self.ch, repo_dir=self.tmp, version=version,
        )

    def test_same_folder_as_close_history_for_healthy_versioned_store(self):
        for label in ("Q3 FY2026", "Q4 FY2026"):
            self._archive(label, 1)
        self._archive("Q4 FY2026", 2)
        for label in ("Q3 FY2026", "Q4 FY2026"):
            with self.subTest(label=label):
                ch = close_history.resolve_latest_approved_close_for_period(label, self.ch)
                s = self.classify(label)
                self.assertEqual(s.state, NS.READABLE)
                self.assertEqual(os.path.normpath(s.folder), os.path.normpath(ch["folder"]))
                self.assertEqual(s.version, ch["version"])

    def test_same_folder_as_close_history_for_legacy_snapshot(self):
        _make_version(self.period("Q2 FY2026"), _good_meta())
        ch = close_history.resolve_latest_approved_close_for_period("Q2 FY2026", self.ch)
        s = self.classify("Q2 FY2026")
        self.assertEqual(os.path.normpath(s.folder), os.path.normpath(ch["folder"]))

    def test_close_history_reports_none_for_damaged_but_classifier_says_damaged(self):
        self._archive("Q4 FY2026", 1)
        meta = os.path.join(self.period(), "v1", "metadata.json")
        with open(meta, "w") as f:
            f.write("{broken")
        self.assertIsNone(close_history.resolve_latest_approved_close_for_period("Q4 FY2026", self.ch))
        self.assertEqual(self.classify().state, NS.DAMAGED)
        # ... and a period that was never closed gives the same None from close_history:
        self.assertIsNone(close_history.resolve_latest_approved_close_for_period("Q1 FY2026", self.ch))
        self.assertEqual(self.classify("Q1 FY2026").state, NS.NOT_CLOSED)


class _FakeRecord:
    def __init__(self, d):
        self.d = d


def _rebuild(d):
    """Test stand-in for the dashboard's _commentary_record_from_dict: raises on a
    malformed entry the same way the real rebuild would (KeyError)."""
    return _FakeRecord({"id": d["observation_id"], "versions": [v["version_number"] for v in d.get("versions", [])]})


GOOD_RECORD = {"OBS-1": {"observation_id": "OBS-1", "accepted_version_number": 1,
                         "versions": [{"version_number": 1, "text": "t", "source": "original_import",
                                       "submitted_by": "x", "timestamp": "z", "validation_result": None}]}}


class TestNarrativeRead(_Base):
    def read(self, label="Q4 FY2026", fn=_rebuild):
        return NS.read_narrative_snapshot(label, fn, self.ch)

    def test_healthy_with_records(self):
        _make_version(os.path.join(self.period(), "v1"), _good_meta(commentary_record=GOOD_RECORD),
                      obs_csv="Observation ID,Period\nOBS-1,Q4 2026\n")
        r = self.read()
        self.assertEqual(r.state, NS.READABLE)
        self.assertTrue(r.commentary_file_supplied)
        self.assertEqual(list(r.records), ["OBS-1"])
        self.assertEqual(list(r.register["Observation ID"]), ["OBS-1"])

    def test_empty_commentary_record_means_no_file_supplied(self):
        _make_version(os.path.join(self.period(), "v1"))
        r = self.read()
        self.assertEqual((r.state, r.commentary_file_supplied, r.records), (NS.READABLE, False, {}))

    def test_absent_or_null_commentary_record_means_no_file_supplied(self):
        for meta in ({"version": 1}, {"version": 1, "commentary_record": None}):
            with self.subTest(meta=meta):
                shutil.rmtree(self.ch, ignore_errors=True)
                _make_version(os.path.join(self.period(), "v1"), meta)
                r = self.read()
                self.assertEqual((r.state, r.commentary_file_supplied), (NS.READABLE, False))

    def test_header_only_register_is_readable_and_empty(self):
        _make_version(os.path.join(self.period(), "v1"))
        r = self.read()
        self.assertTrue(r.register.empty)

    def test_missing_observations_csv_is_damaged(self):
        _make_version(os.path.join(self.period(), "v1"), obs_csv=None)
        self.assertEqual(self.read().state, NS.DAMAGED)

    def test_zero_byte_observations_csv_is_damaged(self):
        _make_version(os.path.join(self.period(), "v1"), obs_csv="")
        self.assertEqual(self.read().state, NS.DAMAGED)

    def test_undecodable_observations_csv_is_damaged(self):
        _make_version(os.path.join(self.period(), "v1"), obs_csv=None)
        _write(os.path.join(self.period(), "v1", "observations.csv"), b"\xff\xfe\x00\x80\x81", mode="wb")
        self.assertEqual(self.read().state, NS.DAMAGED)

    def test_commentary_record_not_an_object_is_damaged(self):
        for bad in ([], [1], "text", 7):
            with self.subTest(bad=bad):
                shutil.rmtree(self.ch, ignore_errors=True)
                _make_version(os.path.join(self.period(), "v1"), {"version": 1, "commentary_record": bad})
                if bad == []:
                    # [] is falsy -> treated like an absent record by the existing reader
                    # (`metadata.get("commentary_record") or {}`); same behaviour kept.
                    self.assertEqual(self.read().state, NS.READABLE)
                else:
                    self.assertEqual(self.read().state, NS.DAMAGED)

    def test_commentary_record_that_cannot_be_rebuilt_is_damaged(self):
        _make_version(os.path.join(self.period(), "v1"),
                      _good_meta(commentary_record={"OBS-1": {"accepted_version_number": 1}}))  # no observation_id
        r = self.read()
        self.assertEqual(r.state, NS.DAMAGED)
        self.assertIsNone(r.records)
        self.assertIn("commentary_record cannot be rebuilt", r.status.detail)

    def test_not_closed_and_structural_damage_pass_through_without_reading(self):
        self.assertEqual(self.read("Q1 FY2026").state, NS.NOT_CLOSED)
        _make_version(os.path.join(self.period(), "v1"), raw_meta="{broken")
        self.assertEqual(self.read().state, NS.DAMAGED)

    def test_damage_detail_is_kept_for_logs_but_not_in_the_message(self):
        _make_version(os.path.join(self.period(), "v1"), raw_meta="{broken")
        r = self.read()
        self.assertTrue(r.status.detail)
        self.assertNotIn(r.status.detail, NS.damaged_snapshot_message(["Q4 2026"]))


class TestAnnualCombination(_Base):
    def snap(self, label, rows, supplied):
        reg = pd.DataFrame({"Observation ID": [f"{label}-{i}" for i in range(rows)],
                            "Period": [label] * rows})
        recs = {f"{label}-0": _FakeRecord({})} if supplied and rows else {}
        st = NS.PeriodSnapshot(label, NS.READABLE)
        return NS.NarrativeSnapshot(st, register=reg, records=recs, commentary_file_supplied=bool(recs))

    def test_all_quarters_agree_gives_one_combined_input(self):
        out = NS.commentary_inputs_for_quarters([self.snap(q, 2, True) for q in ("Q1", "Q2", "Q3", "Q4")])
        self.assertEqual(len(out), 1)
        self.assertEqual(len(out[0].register), 8)
        self.assertTrue(out[0].commentary_file_supplied)
        self.assertEqual(len(out[0].records), 4)

    def test_quarters_without_observations_never_decide_the_flag(self):
        out = NS.commentary_inputs_for_quarters(
            [self.snap("Q1", 0, False), self.snap("Q2", 2, True), self.snap("Q3", 0, False), self.snap("Q4", 1, True)])
        self.assertEqual(len(out), 1)
        self.assertTrue(out[0].commentary_file_supplied)
        self.assertEqual(len(out[0].register), 3)

    def test_disagreeing_quarters_are_kept_separate_so_none_is_mislabelled(self):
        out = NS.commentary_inputs_for_quarters(
            [self.snap("Q1", 1, True), self.snap("Q2", 2, False), self.snap("Q3", 0, False), self.snap("Q4", 1, True)])
        self.assertEqual([len(i.register) for i in out], [1, 2, 1])
        self.assertEqual([i.commentary_file_supplied for i in out], [True, False, True])

    def test_no_observations_anywhere_gives_no_input(self):
        self.assertEqual(NS.commentary_inputs_for_quarters([self.snap("Q1", 0, False), self.snap("Q2", 0, False)]), [])

    def test_a_non_readable_snapshot_is_refused(self):
        bad = NS.NarrativeSnapshot(NS.PeriodSnapshot("Q2", NS.DAMAGED))
        with self.assertRaises(ValueError):
            NS.commentary_inputs_for_quarters([self.snap("Q1", 1, True), bad])


class TestMessage(unittest.TestCase):
    FORBIDDEN = ("reopen", "re-open", "hard", "soft", "audit trail", "login", "authenticated", "signed in")

    def test_wording_and_naming(self):
        m = NS.damaged_snapshot_message(["Q4 2026"])
        self.assertIn("damaged or incomplete", m)
        self.assertIn("Q4 2026", m)
        self.assertIn("restor", m)

    def test_plural_names_every_period(self):
        m = NS.damaged_snapshot_message(["Q1 2026", "Q3 2026"])
        self.assertIn("Q1 2026", m)
        self.assertIn("Q3 2026", m)
        self.assertIn("damaged or incomplete", m)

    def test_no_forbidden_or_causal_words(self):
        for labels in (["Q4 2026"], ["Q1 2026", "Q2 2026"]):
            low = NS.damaged_snapshot_message(labels).lower()
            for w in self.FORBIDDEN:
                self.assertNotIn(w, low, w)
            for cause in ("corrupt", "crash", "truncat", "deleted", "tamper"):
                self.assertNotIn(cause, low, cause)

    def test_empty_label_list_is_refused(self):
        with self.assertRaises(ValueError):
            NS.damaged_snapshot_message([])


if __name__ == "__main__":
    unittest.main()
