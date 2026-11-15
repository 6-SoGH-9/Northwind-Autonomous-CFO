"""
Builder INTEGRATION tests for D22 Release 1, WP1, run against the real, modified
Northwind_Financial_Dashboard.py through Streamlit's AppTest (no browser).

STATUS: Builder-authored component/integration evidence. NOT independent
validation and NOT calibration. Data is the canonical SYNTHETIC sample dataset
plus Close History snapshots written by the repository's own archive_close()
into a TEMPORARY copy of the code (the repository's close_history/ is never
touched). Observations and commentary text are invented by the Builder.
Offline: no API call is made (ANTHROPIC_API_KEY is removed for the run).

Requires the pinned environment (streamlit). Skipped, with a stated reason, if
streamlit is not importable.

Run from the repository root:  python -m unittest build_test.test_narrative_integration -v
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    from streamlit.testing.v1 import AppTest
    HAVE_ST = True
except Exception:  # pragma: no cover
    HAVE_ST = False

FORBIDDEN_WORDS = ("hard", "soft", "audit trail", "login", "authenticated", "signed in", "reopen")
Q4, Q3, Q2, Q1 = "Q4 FY2026", "Q3 FY2026", "Q2 FY2026", "Q1 FY2026"
SNAP_MARK = "ZZ-SNAPSHOT-COMMENTARY"
SESSION_MARK = "ZZ-SESSION-COMMENTARY"


def _obs_row(period_display, n):
    return {"Observation ID": f"OBS-{period_display.replace(' ', '')}-{n}", "Detected By": "P3",
            "Period": period_display, "Type": "T", "Department": "R&D", "Category": "Other Opex",
            "Before ($)": 100, "After ($)": 200, "Delta ($)": 100, "Threshold Crossed": "x"}


@unittest.skipUnless(HAVE_ST, "streamlit is not importable in this interpreter (use the pinned environment)")
class TestNarrativeTabWP1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._old_key = os.environ.pop("ANTHROPIC_API_KEY", None)
        cls._cwd = os.getcwd()
        cls.tmp = tempfile.mkdtemp(prefix="wp1_integration_")
        cls.base = os.path.join(cls.tmp, "base")
        os.makedirs(cls.base)
        for name in os.listdir(ROOT):
            p = os.path.join(ROOT, name)
            if os.path.isfile(p) and name.endswith((".py", ".xlsx", ".md", ".txt")):
                shutil.copy(p, cls.base)
        # the real rollups_output.xlsx, produced by the repository's own rollups.py in the temp copy
        import subprocess
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        out = subprocess.run([sys.executable, "rollups.py"], cwd=cls.base, env=env, capture_output=True, timeout=300)
        assert out.returncode == 0, out.stderr[-500:]

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._cwd)
        shutil.rmtree(cls.tmp, ignore_errors=True)
        if cls._old_key is not None:
            os.environ["ANTHROPIC_API_KEY"] = cls._old_key

    # -- helpers -----------------------------------------------------------
    def fresh_app(self):
        d = tempfile.mkdtemp(prefix="app_", dir=self.tmp)
        for name in os.listdir(self.base):
            if os.path.isfile(os.path.join(self.base, name)):
                shutil.copy(os.path.join(self.base, name), d)
        return d

    def close(self, app, period, *, display, with_commentary, text=SNAP_MARK):
        """Archive one quarter through the repository's own archive_close()."""
        sys.path.insert(0, app)
        try:
            import importlib
            for m in ("close_history", "commentary_workflow"):
                sys.modules.pop(m, None)
            CH = importlib.import_module("close_history")
            CWF = importlib.import_module("commentary_workflow")
        finally:
            sys.path.pop(0)
        import pandas as pd
        row = _obs_row(display, 1)
        rec_dict = None
        if with_commentary:
            rec = CWF.CommentaryRecord(observation_id=row["Observation ID"])
            rec.add_version(f"{text} for {display}.", CWF.SOURCE_ORIGINAL_IMPORT, "x", None)
            rec.mark_accepted(1)
            rec_dict = {row["Observation ID"]: rec.to_dict()}
        CH.archive_close(
            period, os.path.join(app, "Northwind_Sample_Dataset.xlsx"), os.path.join(app, "rollups_output.xlsx"),
            pd.DataFrame([row]), "narrative", 0, 0, {}, None,
            close_history_dir=os.path.join(app, "close_history"), repo_dir=app, commentary_record=rec_dict,
        )

    def meta_path(self, app, period):
        return os.path.join(app, "close_history", period, "v1", "metadata.json")

    def run_app(self, app, annual=False, session=None):
        os.chdir(app)
        sys.path.insert(0, app)
        try:
            at = AppTest.from_file(os.path.join(app, "Northwind_Financial_Dashboard.py"), default_timeout=300)
            for k, v in (session or {}).items():
                at.session_state[k] = v
            at.run()
            if annual:
                at.radio[0].set_value("Annual").run()
                # the Annual period selector holds fiscal years; 2026 is the one with FY2026 quarters
            return at
        finally:
            sys.path.remove(app)
            os.chdir(self._cwd)

    @staticmethod
    def warnings(at):
        return [w.value for w in at.warning]

    @staticmethod
    def prompt_text(at):
        return "\n".join(e.value for ex in at.expander if "rendered prompt" in ex.label for e in ex.text)

    @staticmethod
    def has_expander(at):
        return any("rendered prompt" in ex.label for ex in at.expander)

    def assert_damaged_message(self, at, label):
        msgs = [m for m in self.warnings(at) if "damaged or incomplete" in m]
        self.assertEqual(len(msgs), 1, self.warnings(at))
        self.assertIn(label, msgs[0])
        low = msgs[0].lower()
        for w in FORBIDDEN_WORDS:
            self.assertNotIn(w, low, w)
        self.assertEqual([e.value for e in at.exception], [])
        self.assertFalse(self.has_expander(at), "no rendered prompt may be built for a damaged period")
        self.assertEqual([b for b in at.get("download_button")], [], "no prompt download may be offered")

    # -- WP1-1 / WP1-3: Quarterly ------------------------------------------
    def test_quarterly_healthy_reads_the_snapshot_and_never_session_state(self):
        app = self.fresh_app()
        self.close(app, Q4, display="Q4 2026", with_commentary=True)
        session = {"commentary_records": {"OBS-Q42026-1": self.session_record(app)},
                   "commentary_file_supplied": True}
        at = self.run_app(app, session=session)
        self.assertEqual([e.value for e in at.exception], [])
        self.assertTrue(self.has_expander(at))
        prompt = self.prompt_text(at)
        self.assertIn(SNAP_MARK, prompt)
        self.assertNotIn(SESSION_MARK, prompt, "session-state commentary must not reach the prompt of a closed period")
        self.assertEqual([m for m in self.warnings(at) if "damaged" in m], [])
        self.assertEqual(len(at.get("download_button")), 1)

    def session_record(self, app):
        sys.path.insert(0, app)
        try:
            import importlib
            CWF = importlib.import_module("commentary_workflow")
        finally:
            sys.path.pop(0)
        rec = CWF.CommentaryRecord(observation_id="OBS-Q42026-1")
        rec.add_version(f"{SESSION_MARK}.", CWF.SOURCE_ORIGINAL_IMPORT, "x", None)
        rec.mark_accepted(1)
        return rec

    def test_quarterly_damaged_unparsable_metadata_gives_the_damaged_message_and_builds_nothing(self):
        app = self.fresh_app()
        self.close(app, Q4, display="Q4 2026", with_commentary=True)
        with open(self.meta_path(app, Q4), "w") as f:
            f.write("{broken")
        # session state holds commentary that WOULD have produced a prompt before WP1: it must not be used
        at = self.run_app(app, session={"commentary_file_supplied": True})
        self.assert_damaged_message(at, "Q4 2026")

    def test_quarterly_damaged_other_ways(self):
        cases = {
            # NOT here: metadata that parses to a JSON list. The app cannot reach the tab at all: close_history.
            # resolve_latest_approved_close() raises AttributeError while rollups.py is imported (pre-existing
            # defect in a protected file, reported, not fixed). The classifier's own handling of it is covered
            # in build_test/test_snapshot_classifier.py.
            "metadata is empty": lambda a: open(self.meta_path(a, Q4), "w").write(""),
            "observations.csv missing": lambda a: os.remove(os.path.join(a, "close_history", Q4, "v1", "observations.csv")),
            "commentary_record not an object": lambda a: self._patch_meta(a, Q4, {"commentary_record": ["x"]}),
            "commentary_record entry unrebuildable": lambda a: self._patch_meta(a, Q4, {"commentary_record": {"OBS-1": {"nope": 1}}}),
        }
        for name, damage in cases.items():
            with self.subTest(damage=name):
                app = self.fresh_app()
                self.close(app, Q4, display="Q4 2026", with_commentary=True)
                damage(app)
                self.assert_damaged_message(self.run_app(app), "Q4 2026")

    def _patch_meta(self, app, period, changes):
        p = self.meta_path(app, period)
        with open(p) as f:
            m = json.load(f)
        m.update(changes)
        with open(p, "w") as f:
            json.dump(m, f)

    def test_the_latest_version_decides_an_older_healthy_version_is_not_a_fallback(self):
        app = self.fresh_app()
        self.close(app, Q4, display="Q4 2026", with_commentary=True)
        v2 = os.path.join(app, "close_history", Q4, "v2")
        shutil.copytree(os.path.join(app, "close_history", Q4, "v1"), v2)
        with open(os.path.join(v2, "metadata.json"), "w") as f:
            f.write("{broken")
        self.assert_damaged_message(self.run_app(app), "Q4 2026")

    # -- WP1-3: NOT CLOSED keeps today's behaviour ---------------------------
    def test_not_closed_period_keeps_the_existing_not_approved_message(self):
        app = self.fresh_app()         # no close_history at all
        at = self.run_app(app)
        self.assertEqual([e.value for e in at.exception], [])
        msgs = self.warnings(at)
        self.assertEqual([m for m in msgs if "damaged or incomplete" in m], [])
        self.assertTrue(any("approved" in m.lower() for m in msgs), msgs)
        self.assertEqual(len(at.get("download_button")), 0)

    # -- WP1-2: Annual ------------------------------------------------------
    def annual_app(self, damage_quarter=None):
        app = self.fresh_app()
        for q in (Q1, Q2, Q3, Q4):
            disp = q.replace(" FY", " ")
            self.close(app, q, display=disp, with_commentary=True, text=f"{SNAP_MARK}-{q[:2]}")
        if damage_quarter:
            with open(self.meta_path(app, damage_quarter), "w") as f:
                f.write("{broken")
        return app

    def test_annual_with_one_damaged_quarter_is_blocked_and_names_it(self):
        app = self.annual_app(damage_quarter=Q3)
        at = self.run_app(app, annual=True, session={"commentary_file_supplied": True})
        self.assert_damaged_message(at, "Q3 2026")
        msg = [m for m in self.warnings(at) if "damaged or incomplete" in m][0]
        for healthy in ("Q1 2026", "Q2 2026", "Q4 2026"):
            self.assertNotIn(healthy, msg)

    def test_annual_with_four_healthy_quarters_reads_the_snapshots(self):
        app = self.annual_app()
        at = self.run_app(app, annual=True, session={"commentary_records": {}, "commentary_file_supplied": False})
        self.assertEqual([e.value for e in at.exception], [])
        self.assertEqual([m for m in self.warnings(at) if "damaged" in m], [])
        prompt = self.prompt_text(at)
        for q in ("Q1", "Q2", "Q3", "Q4"):
            self.assertIn(f"{SNAP_MARK}-{q}", prompt, q)
        self.assertEqual(len(at.get("download_button")), 1)

    def test_annual_two_damaged_quarters_names_both(self):
        app = self.annual_app(damage_quarter=Q3)
        with open(self.meta_path(app, Q1), "w") as f:
            f.write("{broken")
        at = self.run_app(app, annual=True)
        msg = [m for m in self.warnings(at) if "damaged or incomplete" in m]
        self.assertEqual(len(msg), 1)
        self.assertIn("Q1 2026", msg[0])
        self.assertIn("Q3 2026", msg[0])
        self.assertFalse(self.has_expander(at))


if __name__ == "__main__":
    unittest.main()
