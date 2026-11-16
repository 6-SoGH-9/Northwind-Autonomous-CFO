"""
Builder component tests for D22 WP3 (narrative_number_check.py).

STATUS (read before citing these results):
  * These are Builder-authored COMPONENT tests. They are NOT calibration. Set A and
    Set B are authored by Independent Test, are kept from the Builder, and are not
    here (Brief, "Calibration"; hand-off note). Nothing below may be called
    independent validation, and the pass rule of D22-G (B2) is not applied here.
  * The DATA block is the real block rendered by the repository's own
    build_user_prompt() from the canonical SYNTHETIC sample dataset
    (build_test/fixtures/README.md). Sentences are invented by the Builder.
  * Each accepted known miss (i) to (iii) is recorded as an EXPECTED RESULT (it
    passes the check by design, WP3-5); none is "fixed".

Run from the repository root:  python -m unittest discover -s build_test -v
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import narrative_number_check as N  # noqa: E402

FIXTURE = os.path.join(ROOT, "build_test", "fixtures", "rendered_prompt_q4_fy2026_demo.txt")
with open(FIXTURE, encoding="utf-8") as _f:
    PROMPT = _f.read()
DATA = N.extract_data_block(PROMPT)
BLOCK = N.parse_data_block(DATA)


def check(text, **kw):
    return N.check_numbers(text, BLOCK, **kw)


def statuses(text, **kw):
    return [(c.number.raw, c.status) for c in check(text, **kw).numbers]


def line_id(label, nth=0, section_contains=None):
    """line_id of the nth line with this label (optionally within a section)."""
    hits = [ln for ln in BLOCK.lines if ln.label == label and (section_contains is None or section_contains in ln.section)]
    return hits[nth].line_id


def w(text):
    """The single written number in text."""
    nums = N.find_numbers(text)
    assert len(nums) == 1, nums
    return nums[0]


def printed(raw):
    return next(f for ln in BLOCK.lines for f in ln.figures if f.raw == raw)


# ---------------------------------------------------------------------------
class TestFixtureProvenance(unittest.TestCase):
    def test_fixture_matches_what_the_live_build_user_prompt_renders(self):
        """The fixture is the real rendered prompt, not a hand-edited one."""
        scratch = tempfile.mkdtemp(prefix="wp3_fixture_check_")
        self.addCleanup(shutil.rmtree, scratch, ignore_errors=True)
        for name in os.listdir(ROOT):
            if name.endswith(".py") or name.endswith(".xlsx") or name.endswith(".md"):
                if os.path.isfile(os.path.join(ROOT, name)):
                    shutil.copy(os.path.join(ROOT, name), scratch)
        code = (
            "import io, contextlib, sys\n"
            "with contextlib.redirect_stdout(io.StringIO()):\n"
            "    import rollups as R\n"
            "p = R.build_user_prompt('Fiscal Quarter', R.quarter_order, 'Q4 FY2026', 'Q3 FY2026', 'Q3 FY2026',\n"
            "    R.pl_q, R.rev_by_region_q, R.rev_by_product_q, R.region_cm_q, R.product_cm_q, R.exp_by_dept_q,\n"
            "    R.sb_volrate_q, R.breadth_all_q, R.hc_dept_q, R.company_rev_per_hc_q, R.bva_q,\n"
            "    movement_component_sources=R.MOVEMENT_COMPONENT_SOURCES_Q)\n"
            "sys.stdout.buffer.write(p.encode('utf-8'))\n"
        )
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        out = subprocess.run([sys.executable, "-c", code], cwd=scratch, env=env, capture_output=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr.decode("utf-8", "replace")[-800:])
        self.assertEqual(out.stdout.decode("utf-8"), PROMPT)

    def test_data_block_shape_agrees_with_the_architect_probe_counts(self):
        """Structural sanity only (observation (ad), 71 figure-carrying lines, 103 dollar figures)."""
        self.assertEqual(len(BLOCK.lines), 71)
        dollars = sum(1 for ln in BLOCK.lines for f in ln.figures if f.kind == N.DOLLAR)
        self.assertEqual(dollars, 103)

    def test_every_line_id_is_unique(self):
        ids = [ln.line_id for ln in BLOCK.lines]
        self.assertEqual(len(ids), len(set(ids)))


class TestExtractDataBlock(unittest.TestCase):
    def test_stops_before_task_and_excludes_headers_above_data(self):
        self.assertNotIn("TASK:", DATA)
        self.assertNotIn("Comparison basis", DATA)
        self.assertTrue(DATA.lstrip().startswith("Consolidated P&L:"))

    def test_commentary_blocks_are_not_part_of_the_data_block(self):
        import pandas as pd
        import commentary_workflow as CWF
        reg = pd.DataFrame([{"Observation ID": "OBS-1", "Detected By": "P3", "Period": "Q4 2026", "Type": "T",
                             "Department": "R&D", "Category": "Other Opex", "Before ($)": 1, "After ($)": 99999,
                             "Delta ($)": 99998, "Threshold Crossed": "x"}])
        # The three commentary blocks, exactly as the real function prints them.
        no_file = CWF.build_narrative_commentary_section(reg, {}, False)
        unresolved = CWF.build_narrative_commentary_section(reg, {}, True)
        rec = CWF.CommentaryRecord(observation_id="OBS-1")
        rec.add_version("Hiring of 77 contractors cost $88,888.", CWF.SOURCE_ORIGINAL_IMPORT, "x", None)
        rec.mark_accepted(1)
        accepted = CWF.build_narrative_commentary_section(reg, {"OBS-1": rec}, True)
        for label, blk in (("no file", no_file), ("unresolved", unresolved), ("accepted", accepted)):
            with self.subTest(block=label):
                self.assertTrue(blk.strip(), "block unexpectedly empty")
                prompt = PROMPT.replace("\n\nTASK:", blk + "\n\nTASK:", 1)
                self.assertNotEqual(prompt, PROMPT)
                self.assertEqual(N.extract_data_block(prompt), DATA)
        # a figure that exists only in a commentary block is therefore NOT a close figure
        prompt = PROMPT.replace("\n\nTASK:", accepted + "\n\nTASK:", 1)
        self.assertNotIn("88,888", N.extract_data_block(prompt))

    def test_end_markers_still_match_what_commentary_workflow_prints(self):
        import pandas as pd
        import commentary_workflow as CWF
        reg = pd.DataFrame([{"Observation ID": "OBS-1", "Detected By": "P3", "Period": "Q4 2026", "Type": "T",
                             "Department": "R&D", "Category": "Other Opex", "Before ($)": 1, "After ($)": 2,
                             "Delta ($)": 1, "Threshold Crossed": "x"}])
        rec = CWF.CommentaryRecord(observation_id="OBS-1")
        rec.add_version("x", CWF.SOURCE_ORIGINAL_IMPORT, "x", None)
        rec.mark_accepted(1)
        outs = [CWF.build_narrative_commentary_section(reg, {}, False),
                CWF.build_narrative_commentary_section(reg, {}, True),
                CWF.build_narrative_commentary_section(reg, {"OBS-1": rec}, True)]
        for marker, out in zip(N._DATA_END_MARKERS[:3][::-1], outs):
            self.assertIn(marker, out)

    def test_missing_data_section_is_an_error(self):
        with self.assertRaises(ValueError):
            N.extract_data_block("no data section here")


# ---------------------------------------------------------------------------
class TestWP3_1_WhatIsANumber(unittest.TestCase):
    def raws(self, text):
        return [n.raw for n in N.find_numbers(text)]

    def test_years_quarter_and_fy_labels_are_not_numbers(self):
        self.assertEqual(self.raws("In Q4 2026 and Q3 FY2026, FY2026 was strong; fiscal 2027 and H1 follow."), [])

    def test_dates_and_times_are_not_numbers(self):
        self.assertEqual(self.raws("Approved on October 26, 2026, 26 October 2026, 2026-10-26, 10/26/2026 at 11:47."), [])

    def test_ordinals_are_not_numbers(self):
        self.assertEqual(self.raws("This was the 1st, 2nd, 3rd and 4th quarter and the 11th review."), [])

    def test_list_numbering_is_not_a_number(self):
        text = "1. Headline\n2) Revenue Drivers\n(3) Margin\n**4. Cost Structure**\n  - 5. Investment\n## 6. Headcount"
        self.assertEqual(self.raws(text), [])

    def test_digits_glued_to_letters_are_not_numbers(self):
        self.assertEqual(self.raws("See D17-BB-001, rule 2c, a 4Q view and the S3 bucket."), [])

    def test_a_number_that_merely_starts_a_sentence_after_list_style_text_is_still_a_number(self):
        self.assertEqual(self.raws("Revenue: 29 people. About 12 were new"), ["29", "12"])
        self.assertEqual(self.raws("Revenue: 29 people.\n3. Margin"), ["29"])

    def test_dollar_percent_and_count_are_all_checked(self):
        nums = N.find_numbers("Revenue was $4.0M, up 6.4%, with 29 people.")
        self.assertEqual([(n.raw, n.kind) for n in nums], [("$4.0M", N.DOLLAR), ("6.4%", N.PERCENT), ("29", N.COUNT)])

    def test_percent_words_and_dollar_words(self):
        nums = N.find_numbers("Up 6.4 percent, 3 percentage points, 5 per cent and 12 dollars.")
        self.assertEqual([n.kind for n in nums], [N.PERCENT, N.PERCENT, N.PERCENT, N.DOLLAR])

    def test_spelled_out_numbers_are_not_scanned(self):
        self.assertEqual(self.raws("Revenue was four million dollars, up six percent, with twenty-nine people."), [])

    def test_signs_and_formats(self):
        nums = {n.raw: n for n in N.find_numbers("Moves of -6.5%, +1.3, -$3,846, $-139 and 4-5% and year-over-year.")}
        self.assertEqual(nums["-6.5%"].sign, -1)
        self.assertEqual(nums["+1.3"].sign, +1)
        self.assertEqual(nums["-$3,846"].sign, -1)
        self.assertEqual(nums["$-139"].sign, -1)
        self.assertIsNone(nums["5%"].sign, "a hyphen between digits is a range, not a sign")

    def test_the_check_applies_only_to_the_text_it_is_given(self):
        """WP3-1: user notes and the prompt are not part of the narrative; the caller passes only the narrative."""
        notes = "My own notes: remember the $9,999,999 target and 77% goal."
        self.assertEqual(check("Operating Margin was 38.2%.").flags, ())
        self.assertEqual(len(check("Operating Margin was 38.2%. " + notes).flags), 2)  # carried into the narrative -> checked


class TestWP3_2_ExactMatch(unittest.TestCase):
    def test_rounding_to_the_precision_written(self):
        p = printed("$4,016,906")
        cases = {"$4.0M": True, "$4M": True, "$4.02M": True, "$4.017M": True, "$4.1M": False, "$4.016M": False,
                 "$4,016,906": True, "$4,016,907": False, "$4,017K": True, "$4,016K": False, "$4.0 million": True,
                 "$4.0m": True, "$0.004B": True, "$0.005B": False, "$4.0B": False}
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(N.figure_matches(w(f"x {text} y"), p), expected)

    def test_half_up_rounding(self):
        p = printed("$24,053")                     # 24.053K
        self.assertTrue(N.figure_matches(w("$24.1K"), p))
        self.assertTrue(N.figure_matches(w("$24K"), p))
        p2 = printed("+6.4%")
        self.assertTrue(N.figure_matches(w("6%"), p2))
        self.assertFalse(N.figure_matches(w("6.43%"), p2), "a more precise figure than printed must not round up to a match")
        self.assertFalse(N.figure_matches(w("6.5%"), p2))

    def test_kinds_never_cross(self):
        self.assertFalse(N.figure_matches(w("$38.2"), printed("38.2%")))
        self.assertFalse(N.figure_matches(w("38.2%"), printed("$24,053")))
        self.assertFalse(N.figure_matches(w("38"), printed("38.2%")))

    def test_derived_figures_printed_in_the_data_block_count(self):
        # variances and shares are printed in the block; G&A total variance $10,751, share +39%
        # $10,751 is printed on two G&A lines (volume/rate table and variance table): a measured
        # literal consequence of "exactly one line" (Architect item), so it is a flag, not a match.
        r = check("G&A total variance was $10,751.")
        self.assertEqual([(c.number.raw, c.status) for c in r.numbers], [("$10,751", "flagged")])
        # (the nearest printed name before the figure is a label word such as "variance", not "G&A":
        # the "label words steal the nearest-name slot" consequence, also reported)
        self.assertEqual(len(r.flags[0].candidate_lines), 2)
        self.assertEqual(statuses("Expenses were concentrated in G&A at +39%."), [("+39%", "matched")])

    def test_a_figure_the_writer_computes_that_is_not_printed_is_flagged(self):
        r = check("Revenue plus Total Opex came to $6.5M.")
        self.assertEqual([(c.number.raw, c.status) for c in r.numbers], [("$6.5M", "flagged")])
        self.assertEqual(r.flags[0].reason, N.REASON_NO_EQUAL_FIGURE)

    def test_explicit_sign_must_agree_but_an_unsigned_number_matches_on_magnitude(self):
        # printed "$-3,846" (Software & Tools total variance)
        self.assertEqual(statuses("Software & Tools total variance was -$3,846."), [("-$3,846", "matched")])
        self.assertEqual(statuses("Software & Tools total variance was $-3,846."), [("$-3,846", "matched")])
        self.assertEqual(statuses("Software & Tools total variance was $3,846."), [("$3,846", "matched")])
        self.assertEqual(statuses("Software & Tools total variance was +$3,846."), [("+$3,846", "flagged")])


class TestWP3_3_LineLevel(unittest.TestCase):
    def test_matched_when_the_name_belongs_to_exactly_one_equal_line(self):
        self.assertEqual(statuses("Operating Margin was 38.2%."), [("38.2%", "matched")])
        self.assertEqual(statuses("R&D spend was $902,208."), [("$902,208", "matched")])

    def test_two_equal_lines_both_carry_the_name_collapse_to_a_match(self):
        """CHANGED BY ADDENDUM 2 A-1 (renamed from test_two_equal_lines_both_carry_the_name_is_a_flag).
        $669,939 is APAC's revenue on two lines (revenue table, regional-investment table).
        Release 1 / Addendum 1 expectation: "In APAC: $669,939." flagged REASON_AMBIGUOUS with 2 candidate lines.
        Addendum 2 expectation: both lines carry the same printed value, so the number matches (A-1), reported
        against the first of the two lines in block order (A-3)."""
        r = check("APAC revenue was $669,939.")
        c = r.numbers[0]
        # the nearest name here is 'revenue' (not APAC), which does not carry $669,939: unchanged, still a flag
        r2 = check("In APAC: $669,939.")
        apac = [ln.line_id for ln in BLOCK.lines if ln.label == "APAC"
                and any(f.raw == "$669,939" for f in ln.figures)]
        self.assertEqual(len(apac), 2)
        self.assertEqual((r2.numbers[0].status, r2.numbers[0].line_id), ("matched", apac[0]))
        self.assertEqual(r2.flags, ())
        self.assertIn(c.status, ("flagged",))

    def test_the_name_is_found_but_the_number_equals_a_different_lines_figure(self):
        r = check("Total Opex was $4,016,906.")           # that is Revenue's figure
        self.assertEqual(r.numbers[0].status, "flagged")
        self.assertEqual(r.flags[0].reason, N.REASON_NAME_DOES_NOT_CARRY_IT)

    def test_no_line_name_is_a_flag_even_when_the_figure_is_printed_elsewhere(self):
        """No fall-back to any printed figure (WP3-3)."""
        r = check("The figure of $4,016,906 stands.")
        self.assertEqual(r.numbers[0].status, "flagged")
        self.assertEqual(r.flags[0].reason, N.REASON_NO_NAME)
        self.assertGreater(len(r.flags[0].candidate_lines), 0, "the equal lines are listed ...")
        self.assertIsNone(r.numbers[0].line_id, "... but none is silently used to clear the flag")

    def test_previous_sentence_counts_two_sentences_back_does_not(self):
        self.assertEqual(statuses("Operating Margin improved. It reached 38.2%."), [("38.2%", "matched")])
        self.assertEqual(statuses("Operating Margin improved. Things went well. It reached 38.2%."), [("38.2%", "flagged")])

    def test_the_same_sentence_beats_the_previous_one(self):
        self.assertEqual(statuses("Operating Profit grew. Operating Margin was 38.2%."), [("38.2%", "matched")])
        self.assertEqual(statuses("Operating Margin held. Operating Profit was 38.2%."), [("38.2%", "flagged")])

    def test_a_name_after_the_number_does_not_count(self):
        self.assertEqual(statuses("38.2% was the Operating Margin."), [("38.2%", "flagged")])

    def test_nearest_preceding_name_decides(self):
        self.assertEqual(statuses("Operating Margin and Operating Profit: $1.5M."), [("$1.5M", "matched")])
        self.assertEqual(statuses("Operating Profit and Operating Margin: $1.5M."), [("$1.5M", "flagged")])

    def test_ampersand_and_case_are_equivalent(self):
        self.assertEqual(statuses("Sales and Marketing spend was $754,316."), [("$754,316", "matched")])
        self.assertEqual(statuses("SALES & MARKETING spend was $754,316."), [("$754,316", "matched")])
        self.assertEqual(statuses("g&a spend was $445,883."), [("$445,883", "matched")])

    def test_labels_with_a_colon_and_their_second_part(self):
        self.assertEqual(statuses("Add-on: Forecasting grew +11.5%."), [("+11.5%", "matched")])
        self.assertEqual(statuses("Add-on Forecasting grew +11.5%."), [("+11.5%", "matched")])

    def test_a_possessive_name_is_found(self):
        self.assertEqual(statuses("EMEA's growth was +10.0%."), [("+10.0%", "matched")])

    def test_a_name_that_belongs_to_many_lines_still_matches_when_only_one_carries_the_figure(self):
        # 'R&D' labels several lines; only one carries $902,208 as a figure
        self.assertGreater(sum(1 for ln in BLOCK.lines if ln.label == "R&D"), 3)
        self.assertEqual(statuses("R&D was $902,208."), [("$902,208", "matched")])

    def test_a_correct_figure_with_two_named_lines_carrying_it_is_flagged_not_guessed(self):
        """CHANGED BY ADDENDUM 1 A-3 (Principal ruling 2, 2026-11-15). In Release 1 this sentence was flagged as
        ambiguous: 'Revenue' labels the consolidated line and the Budget vs Actual line and both print $4,016,906
        (D22-G (B3), pass-rule clause (e)). Under A-3 a sentence with no budget word is matched against actual lines
        only, so the Budget line is neither a candidate nor a name, and the number matches the consolidated line.
        Both lines are still listed as equal-figure lines for a pick (A-5b).
        CHANGED AGAIN BY ADDENDUM 2 A-1, for the block without Budget lines only. Addendum 1 expectation there: flagged
        REASON_AMBIGUOUS with 2 candidate lines (the Release 1 outcome). Addendum 2 expectation: both Revenue lines are
        actual lines and carry the same printed value $4,016,906, so the number collapses to a match against the first
        in block order, the consolidated line (A-1, A-3). The Release 1 outcome itself is checked against the byte-exact
        Release 1 copy in build_test/test_addendum1_number_check.py."""
        r = check("Revenue was $4,016,906.")
        self.assertEqual(r.numbers[0].status, "matched")
        self.assertEqual(r.numbers[0].line_id, line_id("Revenue", 0, "Consolidated"))
        no_budget = N.parse_data_block(DATA.replace(N.BUDGET_SECTION_HEADING, "Budget vs Actual (heading renamed)"))
        self.assertEqual(no_budget.budget_lines, ())
        r1 = N.check_numbers("Revenue was $4,016,906.", no_budget)
        first = [ln.line_id for ln in no_budget.lines if ln.label == "Revenue"][0]
        self.assertEqual((r1.numbers[0].status, r1.numbers[0].line_id), ("matched", first))
        self.assertEqual(first, line_id("Revenue", 0, "Consolidated"))


class TestWP3_4_EveryNonExactNumberIsAFlag(unittest.TestCase):
    def test_near_misses_are_flags_there_is_no_tolerance(self):
        for text in ("Operating Profit was $1.6M.", "Operating Margin was 38.3%.",                      "Operating Margin was 38.1%.", "Total Opex was $2,482,357."):
            with self.subTest(text=text):
                self.assertEqual(check(text).numbers[0].status, "flagged")

    def test_a_correct_rounding_is_not_flagged(self):
        for text in ("Operating Profit was $1.5M.", "Operating Margin was 38%.", "Total Opex was $2.5M.",
                     "Total Opex was $2,482K.", "Operating Margin was 38.20%."):   # 38.20 == 38.2 at two decimals
            with self.subTest(text=text):
                self.assertEqual(check(text).numbers[0].status, "matched")

    def test_there_is_no_tier_or_severity_on_a_flag_and_no_internal_word_in_its_strings(self):
        r = check("Operating Margin was 40.0%.")
        names = set(N.Flag.__dataclass_fields__)
        self.assertFalse({"severity", "tier", "level", "soft", "hard"} & names)
        strings = [N.KIND_WORDS[k] for k in N.KIND_WORDS] + [
            N.REASON_NO_NAME, N.REASON_AMBIGUOUS, N.REASON_NAME_DOES_NOT_CARRY_IT, N.REASON_NO_EQUAL_FIGURE,
            N.REASON_PICK_MISMATCH, r.flags[0].kind_words, r.flags[0].reason]
        for s in strings:
            for word in ("hard", "soft", "none"):
                self.assertNotIn(word, s.lower().split(), (word, s))
                self.assertNotIn(f" {word} ", f" {s.lower()} ", (word, s))


class TestWP3_5_AcceptedKnownMisses(unittest.TestCase):
    """EXPECTED RESULTS: these pass the check by design (D22-F (1), D22-G (B1)). They must stay passing."""

    def test_miss_i_current_figure_written_where_the_prior_figure_of_the_same_line_belongs(self):
        # Operating Margin printed "38.2% vs 35.0%": 35.0% is the PRIOR figure, written as if it were current.
        r = check("Operating Margin rose to 35.0% this quarter.")
        self.assertEqual([c.status for c in r.numbers], ["matched"])
        self.assertEqual(r.flags, ())

    def test_miss_ii_a_wrong_number_that_is_the_right_figure_for_the_line_named(self):
        # $1,534,550 is Operating Profit, but it is not a growth figure.
        r = check("Operating Profit grew by $1,534,550.")
        self.assertEqual([c.status for c in r.numbers], ["matched"])
        self.assertEqual(r.flags, ())

    def test_miss_iii_a_number_after_the_name_of_a_different_line_where_it_equals_that_lines_figure(self):
        # Writer meant EMEA's +10.0% but typed it after Professional Services, whose printed
        # revenue-variance share is +10%: true of that line as written, so it passes.
        r = check("Revenue was led by EMEA, and Professional Services added 10.0%.")
        self.assertEqual([c.status for c in r.numbers], ["matched"])
        self.assertEqual(r.flags, ())

    def test_the_misses_are_not_fixed_by_an_unrelated_correct_sentence(self):
        r = check("Operating Margin rose to 35.0%. Operating Margin was 38.2%.")
        self.assertEqual([c.status for c in r.numbers], ["matched", "matched"])


class TestWP3_6_WhatAFlagCarries(unittest.TestCase):
    def test_line_known_shows_that_lines_same_kind_figures_only(self):
        f = check("Operating Margin was 40.0%.").flags[0]
        self.assertEqual(f.number.raw, "40.0%")                       # what was written
        self.assertTrue(f.placed)
        self.assertEqual((f.line.label, f.line.figures), ("Operating Margin", ("38.2%", "35.0%")))
        self.assertTrue(f.line_has_figure_of_kind)
        self.assertEqual(f.lines_of_kind, ())
        self.assertEqual(f.kind_words, "percentage")

    def test_dollars_with_dollars_percentages_with_percentages_counts_with_counts(self):
        f = check("Total Opex was $9,000,000.").flags[0]
        self.assertEqual(f.line.figures, ("$2,482,356", "$2,454,984"))     # not the +1.1%
        f = check("Total Opex was 9.9%.").flags[0]
        self.assertEqual(f.line.figures, ("+1.1%",))

    def test_line_known_but_no_figure_of_that_kind_gives_the_plain_wording_case(self):
        f = check("Operating Margin was $5.").flags[0]
        self.assertTrue(f.placed)
        self.assertEqual(f.line.figures, ())
        self.assertFalse(f.line_has_figure_of_kind)

    def test_line_cannot_be_placed_lists_every_line_with_a_figure_of_that_kind_each_with_its_figure(self):
        f = check("We saw $12,345 somewhere.").flags[0]
        self.assertFalse(f.placed)
        self.assertIsNone(f.line)
        expected = [ln for ln in BLOCK.lines if ln.figures_of_kind(N.DOLLAR)]
        self.assertEqual([r.line_id for r in f.lines_of_kind], [ln.line_id for ln in expected])
        for ref, ln in zip(f.lines_of_kind, expected):
            self.assertEqual(ref.figures, tuple(x.raw for x in ln.figures_of_kind(N.DOLLAR)))
            self.assertTrue(all(x.startswith(("$", "-$", "+$")) for x in ref.figures))
        f = check("We saw 9.9% somewhere.").flags[0]
        self.assertTrue(all("%" in x for r in f.lines_of_kind for x in r.figures))
        self.assertEqual(len(f.lines_of_kind), sum(1 for ln in BLOCK.lines if ln.figures_of_kind(N.PERCENT)))

    def test_candidate_lines_are_the_equal_figure_lines_and_may_be_empty(self):
        f = check("The figure of $669,939 stands.").flags[0]
        self.assertEqual(len(f.candidate_lines), 2)
        self.assertTrue(all("$669,939" in c.figures for c in f.candidate_lines))
        self.assertEqual(check("We saw $12,345 somewhere.").flags[0].candidate_lines, ())

    def test_flag_records_the_sentence_span_for_the_marker_link(self):
        text = "Revenue held up. We saw $12,345 somewhere. Done."
        f = check(text).flags[0]
        self.assertEqual(text[f.sentence_start:f.sentence_end].strip(), "We saw $12,345 somewhere.")


class TestWP3_7_PickingALine(unittest.TestCase):
    TEXT = "The figure of $4,016,906 stands."

    def test_picking_the_line_whose_figure_equals_the_number_clears_the_flag(self):
        lid = line_id("Revenue", 0, "Consolidated")
        r = check(self.TEXT, picks={("$4,016,906", 0): lid})
        self.assertEqual([(c.status, c.line_id) for c in r.numbers], [("matched_by_pick", lid)])
        self.assertEqual(r.flags, ())

    def test_picking_the_other_line_that_carries_it_also_clears(self):
        lid = line_id("Revenue", 0, "Budget vs Actual")
        self.assertEqual(check(self.TEXT, picks={("$4,016,906", 0): lid}).flags, ())

    def test_picking_a_line_whose_figure_differs_keeps_the_flag_open_and_shows_that_line(self):
        lid = line_id("R&D", 0, "Expenses by Department")
        r = check(self.TEXT, picks={("$4,016,906", 0): lid})
        f = r.flags[0]
        self.assertTrue(f.is_open)
        self.assertEqual(f.reason, N.REASON_PICK_MISMATCH)
        self.assertEqual((f.picked_line_id, f.line.line_id), (lid, lid))
        self.assertEqual(f.line.figures, ("$902,208", "$902,047"))
        self.assertTrue(f.placed)

    def test_the_pick_is_the_writers_statement_and_is_not_otherwise_verified(self):
        """The sentence names Total Opex, yet picking the Revenue line clears the flag."""
        lid = line_id("Revenue", 0, "Consolidated")
        r = check("Total Opex was $4,016,906.", picks={("$4,016,906", 0): lid})
        self.assertEqual(r.flags, ())

    def test_an_unknown_line_id_is_ignored(self):
        r = check(self.TEXT, picks={("$4,016,906", 0): "deadbeef00"})
        self.assertEqual(len(r.flags), 1)
        self.assertIsNone(r.flags[0].picked_line_id)

    def test_a_pick_applies_to_one_occurrence_only(self):
        text = "We saw $12,345 once. We saw $12,345 again."
        lid = line_id("R&D", 0, "Expenses by Department")
        r = check(text, picks={("$12,345", 1): lid})
        self.assertEqual([f.picked_line_id for f in r.flags], [None, lid])

    def test_a_pick_of_a_line_that_matches_works_even_when_the_name_would_not_place_it(self):
        lid = line_id("Operating Margin")
        r = check("Total Opex was 38.2%.", picks={("38.2%", 0): lid})
        self.assertEqual(r.flags, ())


class TestWP3_8_Acceptance(unittest.TestCase):
    def acc(self, number, line, name="A. Controller", time="2026-10-26T12:00:00+00:00"):
        return N.Acceptance(number=number, line_id=line, name=name, time=time)

    def test_an_acceptance_is_keyed_to_the_number_and_the_line(self):
        text = "Operating Margin was 40.0%."
        f = check(text).flags[0]
        key = f.acceptance_key
        self.assertEqual(key, ("40.0%", line_id("Operating Margin")))
        r = check(text, acceptances=[self.acc("40.0%", line_id("Operating Margin"))])
        self.assertIsNotNone(r.flags[0].accepted)
        self.assertEqual((r.flags[0].accepted.name, r.flags[0].accepted.time), ("A. Controller", "2026-10-26T12:00:00+00:00"))
        self.assertEqual(r.open_count, 0)

    def test_an_acceptance_for_another_line_or_another_number_does_not_cover_it(self):
        text = "Operating Margin was 40.0%."
        for a in (self.acc("40.0%", line_id("Operating Profit")), self.acc("41.0%", line_id("Operating Margin")),
                  self.acc("40.0%", None)):
            with self.subTest(a=a):
                self.assertEqual(check(text, acceptances=[a]).open_count, 1)

    def test_an_unplaced_flag_is_keyed_to_the_number_and_no_line(self):
        text = "We saw $12,345 somewhere."
        r = check(text, acceptances=[self.acc("$12,345", None)])
        self.assertEqual((r.open_count, len(r.flags)), (0, 1))

    def test_the_acceptance_survives_a_change_of_the_display_label(self):
        a = self.acc("40.0%", line_id("Operating Margin"))
        before = check("Operating Margin was 40.0%.", acceptances=[a])
        after = check("Revenue rose to 9.99%. Operating Margin was 40.0%.", acceptances=[a])   # a new flag now comes first
        self.assertEqual([f.ordinal for f in before.flags], [1])
        self.assertEqual([f.ordinal for f in after.flags], [1, 2])      # the label moved ...
        self.assertEqual([f.is_open for f in after.flags], [True, False])  # ... the acceptance did not

    def test_the_text_is_rechecked_when_it_changes_an_acceptance_holds_only_while_number_and_line_stand(self):
        a = self.acc("40.0%", line_id("Operating Margin"))
        self.assertEqual(check("Operating Margin was 40.0%.", acceptances=[a]).open_count, 0)
        # the number now sits after a different line's name: the key differs, so it is open again
        self.assertEqual(check("Total Opex was 40.0%.", acceptances=[a]).open_count, 1)
        # the number is gone: nothing to cover
        self.assertEqual(check("Operating Margin was 38.2%.", acceptances=[a]).flags, ())

    def test_an_accepted_flag_stays_in_the_result_but_is_not_open(self):
        a = self.acc("40.0%", line_id("Operating Margin"))
        r = check("Operating Margin was 40.0%.", acceptances=[a])
        self.assertEqual((len(r.flags), r.open_count), (1, 0))
        self.assertEqual(r.numbers[0].status, "flagged")

    def test_an_acceptance_for_a_picked_line(self):
        lid = line_id("R&D", 0, "Expenses by Department")
        r = check("The figure of $4,016,906 stands.", picks={("$4,016,906", 0): lid},
                  acceptances=[self.acc("$4,016,906", lid)])
        self.assertEqual((len(r.flags), r.open_count), (1, 0))


class TestWP3_9_HandWrittenNarrative(unittest.TestCase):
    def test_the_check_does_not_depend_on_how_the_text_was_produced_or_on_an_api_key(self):
        text = "Operating Margin was 38.2%. Operating Profit was $1.6M. We saw $12,345 somewhere."
        old = os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            without = check(text)
            os.environ["ANTHROPIC_API_KEY"] = "sk-test-not-a-real-key"
            with_key = check(text)
        finally:
            os.environ.pop("ANTHROPIC_API_KEY", None)
            if old is not None:
                os.environ["ANTHROPIC_API_KEY"] = old
        self.assertEqual(without, with_key)
        self.assertEqual(len(without.flags), 2)

    def test_the_module_has_no_screen_environment_clock_or_network_dependency(self):
        src = open(os.path.join(ROOT, "narrative_number_check.py"), encoding="utf-8").read()
        for needle in ("import streamlit", "session_state", "os.environ", "import os", "datetime", "import time",
                       "import random", "requests", "urllib", "socket"):
            self.assertFalse(needle in src, needle)
        import re as _re
        self.assertIsNone(_re.search(r"(?<![\w.])open\(", src), "the module opens no file")


class TestWP3_10_Deterministic(unittest.TestCase):
    TEXT = ("Revenue grew 6.4% to $4,016,906. Operating Margin was 38.3%, up from 35.0%. R&D spend was $902,208. "
            "We saw $12,345 somewhere. Professional Services revenue grew 10%. Sales & Marketing +8% of variance.")

    def test_same_input_same_output(self):
        self.assertEqual(check(self.TEXT), check(self.TEXT))
        self.assertEqual(N.check_numbers(self.TEXT, DATA), N.check_numbers(self.TEXT, BLOCK))

    def test_same_output_across_processes_and_hash_seeds(self):
        code = (
            "import sys, json\n"
            f"sys.path.insert(0, {ROOT!r})\n"
            "import narrative_number_check as N\n"
            f"d = N.extract_data_block(open({FIXTURE!r}, encoding='utf-8').read())\n"
            f"r = N.check_numbers({self.TEXT!r}, d)\n"
            "out = [(c.number.raw, c.status, c.line_id, None if c.flag is None else [c.flag.reason, c.flag.placed,\n"
            "        [x.line_id for x in c.flag.candidate_lines], [x.line_id for x in c.flag.lines_of_kind]]) for c in r.numbers]\n"
            "print(json.dumps(out))\n"
        )
        outs = set()
        for seed in ("0", "1", "42", "random"):
            env = {k: v for k, v in os.environ.items()}
            env["PYTHONHASHSEED"] = seed
            p = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=120)
            self.assertEqual(p.returncode, 0, p.stderr[-500:])
            outs.add(p.stdout)
        self.assertEqual(len(outs), 1)
        self.assertGreater(len(json.loads(outs.pop())), 5)


class TestRobustness(unittest.TestCase):
    def test_empty_and_numberless_text(self):
        for text in ("", "   ", "No numbers here.", "\n\n"):
            r = check(text)
            self.assertEqual((r.numbers, r.flags), ((), ()))

    def test_text_with_only_numbers(self):
        r = check("$1 2 3.5% $-4")
        self.assertEqual(len(r.numbers), 4)

    def test_very_long_text_and_odd_characters_do_not_crash(self):
        text = ("Revenue — “quoted” $4.0M and 6.4%… " * 400) + "\U0001F600 -−– \x00"
        self.assertEqual(len(check(text).numbers), 800)

    def test_data_block_with_no_figures_flags_everything_without_error(self):
        r = N.check_numbers("Revenue was $4.0M.", "Nothing numeric here:\n- just words")
        self.assertEqual(r.numbers[0].status, "flagged")
        self.assertEqual(r.flags[0].lines_of_kind, ())

    def test_parse_data_block_is_idempotent_and_accepts_a_parsed_block(self):
        self.assertEqual(N.parse_data_block(DATA), BLOCK)
        self.assertEqual(N.check_numbers("Operating Margin was 38.2%.", DATA), check("Operating Margin was 38.2%."))


if __name__ == "__main__":
    unittest.main()
