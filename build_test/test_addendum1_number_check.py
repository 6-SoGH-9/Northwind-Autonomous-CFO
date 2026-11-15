"""
Builder component tests for D22 Number Check Amendment, Addendum 1 (revision 5,
signed 2026-11-13; governance/builder_briefs/D22_Narrative_versioning_builder_brief_addendum_1.md)
and the Principal's rulings of 2026-11-15:
  ruling 1  A-3 applies literally, also when the block has no Budget lines: a
            budget-word sentence is then checked against an empty Budget pool,
            flagged, and clearable by a pick (A-5b). A-6(c) holds for sentences
            without a budget word; A-6(d) is unchanged.
  ruling 2  The rules are built as written; the one Release 1 test whose expected
            result A-3 changes is updated (build_test/test_number_check.py,
            test_a_correct_figure_with_two_named_lines_carrying_it_is_flagged_not_guessed).
  ruling 3  A B-6 flag (two direction words that disagree) carries no direction_word
            and no direction (both None).

STATUS: Builder-authored COMPONENT tests. NOT calibration and NOT independent
validation: Set A and Set B belong to Independent Test and are not here.
The sentences under "Architect illustrations" are copied from the addendum's
acceptance illustrations; every other sentence is invented by the Builder.
Part A and Part B have separate test classes, so their evidence is separate.

Data: the real DATA block of build_test/fixtures/rendered_prompt_q4_fy2026_demo.txt
(canonical SYNTHETIC sample dataset). Blocks "without Budget lines" are made from
it in memory by renaming the heading or replacing the one Budget line with the
"(none flagged ...)" line, exactly as rollups.py prints it. One small synthetic
block (SYNTH) is used for printed zeros and mixed-sign equal figures, which the
fixture does not contain. The Release 1 reference for A-6(c) is
build_test/fixtures/narrative_number_check_release1.py, a byte-exact copy of the
Release 1 module on main (SHA-256 checked below).

Run from the repository root:  python -m unittest discover -s build_test -v
"""
import hashlib
import importlib.util
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import narrative_number_check as N  # noqa: E402

FIXTURES = os.path.join(ROOT, "build_test", "fixtures")
FIXTURE = os.path.join(FIXTURES, "rendered_prompt_q4_fy2026_demo.txt")
RELEASE1_COPY = os.path.join(FIXTURES, "narrative_number_check_release1.py")
RELEASE1_SHA256 = "6960899c48aa0f15bdb6cb6fbe9d1383fb53072fed7a8d77f149023b2ce1016c"

with open(FIXTURE, encoding="utf-8") as _f:
    DATA = N.extract_data_block(_f.read())
BLOCK = N.parse_data_block(DATA)

BUDGET_LINE_TEXT = "  - Revenue: Budget $4,294,336, Actual $4,016,906, Variance -6.5% — Watch"
NONE_FLAGGED_DATA = DATA.replace(BUDGET_LINE_TEXT, "  (none flagged Watch or Major Miss this period)")
NO_HEADING_DATA = DATA.replace(N.BUDGET_SECTION_HEADING, "Budget vs Actual (heading renamed)")

SYNTH = (
    "Synthetic Section:\n"
    "  - Alpha: +5.0% vs -5.0%\n"
    "  - Beta: 0.0% vs 0.0%\n"
    "  - Gamma: -3.0%\n"
)


def check(text, block=BLOCK, **kw):
    return N.check_numbers(text, block, **kw)


def one(text, block=BLOCK, **kw):
    r = check(text, block, **kw)
    assert len(r.numbers) == 1, [c.number.raw for c in r.numbers]
    return r.numbers[0]


def lid(label, section_contains, block=BLOCK):
    hits = [ln for ln in block.lines if ln.label == label and section_contains in ln.section]
    assert len(hits) == 1, (label, section_contains, len(hits))
    return hits[0].line_id


PL_REVENUE = lid("Revenue", "Consolidated")
BUDGET_REVENUE = lid("Revenue", "Budget vs Actual")


def load_release1():
    spec = importlib.util.spec_from_file_location("narrative_number_check_release1", RELEASE1_COPY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ref(r):
    """A LineRef as plain values (the two modules have distinct LineRef classes)."""
    return None if r is None else (r.line_id, r.section, r.label, tuple(r.figures))


def summary(result):
    """Everything Release 1 puts in a result, for an exact comparison."""
    out = []
    for c in result.numbers:
        f = c.flag
        out.append((c.number.raw, c.number.occurrence, c.status, c.line_id, None if f is None else (
            f.ordinal, f.kind, f.kind_words, f.reason, f.placed, _ref(f.line), f.line_has_figure_of_kind,
            tuple(x.line_id for x in f.candidate_lines), tuple(x.line_id for x in f.lines_of_kind),
            f.picked_line_id, f.sentence_start, f.sentence_end,
            None if f.accepted is None else (f.accepted.number, f.accepted.line_id))))
    return tuple(out)


# =============================================================================
# PART A: Budget lines
# =============================================================================
class TestPartA_Section(unittest.TestCase):
    """A-1, A-6 (heading pin)."""

    def test_A6a_heading_literals_are_in_rollups_source_and_equal_the_parser_constants(self):
        with open(os.path.join(ROOT, "rollups.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertEqual(N.BUDGET_SECTION_HEADING, "Budget vs Actual — flagged items only")
        self.assertEqual(N.BUDGET_SECTION_END, "(Flag thresholds")
        self.assertIn("\n" + N.BUDGET_SECTION_HEADING, src)
        self.assertIn("\n" + N.BUDGET_SECTION_END, src)
        self.assertIn('"  (none flagged Watch or Major Miss this period)"', src)

    def test_A6b_fixture_has_exactly_one_budget_line_revenue(self):
        lines = BLOCK.budget_lines
        self.assertEqual(len(lines), 1)
        ln = lines[0]
        self.assertEqual(ln.label, "Revenue")
        self.assertEqual(tuple(f.raw for f in ln.figures), ("$4,294,336", "$4,016,906", "-6.5%"))
        self.assertEqual(ln.line_id, BUDGET_REVENUE)

    def test_A1_thresholds_line_and_the_heading_are_not_budget_lines(self):
        thresholds = [ln for ln in BLOCK.lines if ln.text.startswith(N.BUDGET_SECTION_END)]
        self.assertEqual(len(thresholds), 1)
        self.assertFalse(thresholds[0].is_budget)
        self.assertFalse(any(ln.text.startswith(N.BUDGET_SECTION_HEADING) for ln in BLOCK.lines))
        self.assertEqual(sum(1 for ln in BLOCK.lines if not ln.is_budget), len(BLOCK.lines) - 1)

    def test_A6c_block_without_the_heading_has_no_budget_lines(self):
        b = N.parse_data_block(NO_HEADING_DATA)
        self.assertEqual(b.budget_lines, ())
        self.assertEqual(len(b.lines), len(BLOCK.lines))

    def test_A6d_none_flagged_line_gives_no_budget_lines_and_no_error(self):
        self.assertNotEqual(NONE_FLAGGED_DATA, DATA)
        b = N.parse_data_block(NONE_FLAGGED_DATA)
        self.assertEqual(b.budget_lines, ())
        self.assertEqual(len(b.lines), len(BLOCK.lines) - 1)
        self.assertEqual(one("Operating Margin was 38.2%.", b).status, "matched")

    def test_line_ids_are_unchanged_by_the_amendment(self):
        r1 = load_release1()
        old = r1.parse_data_block(DATA)
        self.assertEqual([ln.line_id for ln in old.lines], [ln.line_id for ln in BLOCK.lines])


class TestPartA_BudgetWords(unittest.TestCase):
    """A-2, E-1, E-9."""

    def test_the_four_words_case_insensitive(self):
        for w in ("budget", "budgets", "budgeted", "plan", "BUDGET", "Budgeted", "Plan"):
            with self.subTest(w=w):
                self.assertTrue(N._has_budget_word(f"Revenue against {w} was fine"))

    def test_apostrophe_and_hyphen_split_words(self):
        self.assertTrue(N._has_budget_word("the budget's line"))
        self.assertTrue(N._has_budget_word("an over-budget quarter"))

    def test_status_words_case_sensitive(self):
        self.assertTrue(N._has_budget_word("Revenue flagged Watch"))
        self.assertTrue(N._has_budget_word("a Major Miss this period"))
        for t in ("one to watch", "a major miss", "a Major miss", "major Miss", "Watchful eyes", "WATCH"):
            with self.subTest(t=t):
                self.assertFalse(N._has_budget_word(t))

    def test_not_budget_words(self):
        for t in ("planned hiring", "the company plans to hire", "Revenue's variance", "target", "forecast",
                  "guidance", "goal", "short of", "shortfall"):
            with self.subTest(t=t):
                self.assertFalse(N._has_budget_word(t))


class TestPartA_Pools(unittest.TestCase):
    """A-2b, A-3, A-4, A-5, A-5b, ruling 1."""

    def test_A3_no_budget_word_uses_actual_lines_only(self):
        c = one("Revenue was $4,016,906.")
        self.assertEqual((c.status, c.line_id), ("matched", PL_REVENUE))
        c = one("Revenue was $4,294,336.")                    # the Budget figure, without a budget word
        self.assertEqual(c.status, "flagged")
        self.assertEqual(c.flag.reason, N.REASON_NO_EQUAL_FIGURE)

    def test_A3_budget_word_uses_budget_lines_only_including_the_actual_figure(self):
        for t in ("Revenue was $4,294,336 against budget.", "Revenue was $4,016,906 against budget.",
                  "Against plan, Revenue was $4,016,906."):
            with self.subTest(t=t):
                c = one(t)
                self.assertEqual((c.status, c.line_id), ("matched", BUDGET_REVENUE))

    def test_A3_budget_word_names_come_from_budget_lines_only(self):
        c = one("Operating Margin was 38.2% against budget.")   # an actual line, in a budget sentence
        self.assertEqual(c.status, "flagged")
        self.assertEqual(c.flag.reason, N.REASON_NO_NAME)

    def test_A2b_number_sentence_after_the_number_counts(self):
        c = one("Revenue fell 6.5% below budget.")
        self.assertEqual(c.line_id, BUDGET_REVENUE)
        self.assertEqual(c.status, "matched")

    def test_A2b_previous_sentence_counts_only_when_the_own_sentence_has_no_name(self):
        c = one("Revenue missed budget. It was 6.5% short.")
        self.assertEqual((c.status, c.line_id), ("matched", BUDGET_REVENUE))
        c = one("Revenue missed budget. APAC grew 12%.")
        self.assertEqual(c.status, "flagged")
        self.assertEqual(c.flag.reason, N.REASON_NAME_DOES_NOT_CARRY_IT)   # APAC is an actual-line name
        self.assertFalse(N._uses_budget_pool(N.find_numbers("Revenue missed budget. APAC grew 12%.")[0],
                                             "Revenue missed budget. APAC grew 12%.",
                                             N._sentence_spans("Revenue missed budget. APAC grew 12%."), BLOCK))

    def test_A2b_any_line_name_blocks_the_previous_sentence(self):
        text = "Revenue missed budget. Operating Margin was 6.5%."
        n = N.find_numbers(text)[0]
        self.assertFalse(N._uses_budget_pool(n, text, N._sentence_spans(text), BLOCK))

    def test_A4_known_false_flags_are_expected_results(self):
        """Accepted false flags (A-4); each is clearable by a pick (A-5b) or by editing the sentence."""
        cases = [
            "Revenue missed budget. It grew 6.4% on the year.",   # budget sentence, then a nameless actual sentence
            "Following the plan, Revenue grew 6.4%.",             # 'plan' in another sense
            "Revenue came in 6.5% short of target.",              # other names for the budget
            "Revenue showed a 6.5% shortfall against target.",
            "Revenue missed. It was 6.5% short.",
            "Revenue's variance was 6.5%.",                       # 'variance' alone
        ]
        for t in cases:
            with self.subTest(t=t):
                self.assertEqual(one(t).status, "flagged")

    def test_A4_each_known_false_flag_clears_by_picking_the_right_line(self):
        for t, line in (("Revenue came in 6.5% short of target.", BUDGET_REVENUE),
                        ("Revenue's variance was 6.5%.", BUDGET_REVENUE),
                        ("Revenue missed budget. It grew 6.4% on the year.", PL_REVENUE)):
            with self.subTest(t=t):
                n = N.find_numbers(t)[0]
                c = one(t, picks={(n.raw, 0): line})
                self.assertEqual((c.status, c.line_id), ("matched_by_pick", line))

    def test_A5b_candidate_lines_and_lines_of_kind_list_both_pools(self):
        f = one("Revenue came in 6.5% short of target.").flag
        self.assertIn(BUDGET_REVENUE, [x.line_id for x in f.candidate_lines])
        f = one("We saw $4,294,336 somewhere.").flag
        self.assertFalse(f.placed)
        self.assertIn(BUDGET_REVENUE, [x.line_id for x in f.lines_of_kind])
        self.assertIn(BUDGET_REVENUE, [x.line_id for x in f.candidate_lines])

    def test_A5b_pick_of_a_budget_line_is_checked_against_its_own_figures(self):
        c = one("Revenue was $4,294,336.", picks={("$4,294,336", 0): BUDGET_REVENUE})
        self.assertEqual(c.status, "matched_by_pick")
        c = one("Revenue was $1,000.", picks={("$1,000", 0): BUDGET_REVENUE})
        self.assertEqual(c.flag.reason, N.REASON_PICK_MISMATCH)

    def test_A5_acceptance_key_unchanged_and_budget_line_is_a_different_line(self):
        self.assertNotEqual(PL_REVENUE, BUDGET_REVENUE)
        f = one("Revenue came in 6.5% short of target.").flag
        self.assertEqual(f.acceptance_key, ("6.5%", PL_REVENUE))
        a = N.Acceptance("6.5%", PL_REVENUE, "A. Controller", "2026-11-15T09:00:00+00:00")
        self.assertEqual(a.key, ("6.5%", PL_REVENUE))
        self.assertEqual(check("Revenue came in 6.5% short of target.", acceptances=[a]).open_count, 0)
        b = N.Acceptance("6.5%", BUDGET_REVENUE, "A. Controller", "2026-11-15T09:00:00+00:00")
        self.assertEqual(check("Revenue came in 6.5% short of target.", acceptances=[b]).open_count, 1)

    def test_ruling1_budget_word_sentence_in_a_block_with_no_budget_lines_is_flagged_and_clears_by_pick(self):
        """Principal ruling 1 (2026-11-15). Both ways a block can have no Budget lines."""
        text = "Revenue grew 6.4% and stayed within budget."
        for label, data in (("none flagged", NONE_FLAGGED_DATA), ("no heading", NO_HEADING_DATA)):
            with self.subTest(block=label):
                b = N.parse_data_block(data)
                self.assertEqual(b.budget_lines, ())
                c = one(text, b)
                self.assertEqual(c.status, "flagged")
                self.assertEqual(c.flag.flag_class, N.FLAG_CLASS_NUMBER)
                pl = lid("Revenue", "Consolidated", b)
                self.assertIn(pl, [x.line_id for x in c.flag.candidate_lines])
                c = one(text, b, picks={("6.4%", 0): pl})
                self.assertEqual((c.status, c.line_id), ("matched_by_pick", pl))

    def test_ruling1_the_same_sentence_without_the_budget_word_matches_as_in_release1(self):
        for data in (NONE_FLAGGED_DATA, NO_HEADING_DATA):
            b = N.parse_data_block(data)
            self.assertEqual(one("Revenue grew 6.4%.", b).status, "matched")


class TestPartA_Release1Regression(unittest.TestCase):
    """A-6(c), ruling 1: a block without Budget lines behaves as Release 1 for every
    sentence without a budget word (and, so that Part B is not involved, without an
    attached direction word). Compared field by field with the Release 1 module."""

    CORPUS = [
        "Revenue was $4,016,906.", "Revenue was $4.0M.", "Revenue was 6.5%.", "Revenue was $4,294,336.",
        "Operating Margin was 38.2%, up from 35.0%.", "R&D spend was $902,208.", "Operating Profit was $1.5M.",
        "Total Opex was $4,016,906.", "The figure of $4,016,906 stands.", "In APAC: $669,939.",
        "We saw $12,345 somewhere.", "Operating Margin improved. It reached 38.2%.", "38.2% was the Operating Margin.",
        "Operating Margin and Operating Profit: $1.5M.", "Sales and Marketing spend was $754,316.",
        "SALES & MARKETING spend was $754,316.", "Add-on: Forecasting grew +11.5%.", "EMEA's growth was +10.0%.",
        "Operating Margin was 40.0%.", "Operating Margin was $5.", "Total Opex was 9.9%.",
        "Revenue plus Total Opex came to $6.5M.", "G&A total variance was $10,751.",
        "Professional Services added 10.0%.", "Operating Margin rose to 35.0% this quarter.",
        "Expenses were concentrated in G&A at +39%.", "Software & Tools total variance was $3,846.",
        "Software & Tools total variance was +$3,846.", "Headcount: 167 people, 29 in Customer Success.",
        "Revenue missed. It was 6.5% short.", "Revenue came in 6.5% short of target.", "",
        "1. Headline\n2) Revenue Drivers\nRevenue was $4.0M in Q4 2026 (October 26, 2026).",
    ]

    @classmethod
    def setUpClass(cls):
        cls.R1 = load_release1()

    def test_release1_reference_copy_is_byte_exact(self):
        with open(RELEASE1_COPY, "rb") as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), RELEASE1_SHA256)

    def test_corpus_has_no_budget_word(self):
        for t in self.CORPUS:
            self.assertFalse(N._has_budget_word(t), t)

    def test_blocks_without_budget_lines_give_release1_results(self):
        for label, data in (("no heading", NO_HEADING_DATA), ("none flagged", NONE_FLAGGED_DATA)):
            new_b, old_b = N.parse_data_block(data), self.R1.parse_data_block(data)
            for t in self.CORPUS:
                with self.subTest(block=label, t=t):
                    self.assertEqual(summary(N.check_numbers(t, new_b)), summary(self.R1.check_numbers(t, old_b)))

    def test_picks_and_acceptances_give_release1_results(self):
        new_b, old_b = N.parse_data_block(NO_HEADING_DATA), self.R1.parse_data_block(NO_HEADING_DATA)
        pl = lid("Revenue", "Consolidated", new_b)
        rd = [ln.line_id for ln in new_b.lines if ln.label == "R&D"][0]
        runs = [
            ("The figure of $4,016,906 stands.", {("$4,016,906", 0): pl}, []),
            ("The figure of $4,016,906 stands.", {("$4,016,906", 0): rd}, []),
            ("The figure of $4,016,906 stands.", {("$4,016,906", 0): "deadbeef00"}, []),
            ("Operating Margin was 40.0%.", {}, [("40.0%", lid("Operating Margin", "Consolidated", new_b))]),
            ("We saw $12,345 somewhere.", {}, [("$12,345", None)]),
        ]
        for t, picks, acc in runs:
            with self.subTest(t=t, picks=picks):
                new_acc = [N.Acceptance(n, l, "x", "t") for n, l in acc]
                old_acc = [self.R1.Acceptance(n, l, "x", "t") for n, l in acc]
                self.assertEqual(summary(N.check_numbers(t, new_b, picks=picks, acceptances=new_acc)),
                                 summary(self.R1.check_numbers(t, old_b, picks=picks, acceptances=old_acc)))

    def test_with_budget_lines_only_revenue_and_budget_sentences_change(self):
        """On the real block, Release 1 results change only where the Budget line is involved."""
        old_b = self.R1.parse_data_block(DATA)
        changed = [t for t in self.CORPUS
                   if summary(N.check_numbers(t, BLOCK)) != summary(self.R1.check_numbers(t, old_b))]
        self.assertEqual(sorted(changed), sorted([
            "Revenue was $4,016,906.", "Revenue was $4.0M.", "Revenue was 6.5%.", "Revenue was $4,294,336.",
            "Revenue missed. It was 6.5% short.", "Revenue came in 6.5% short of target.",
            "1. Headline\n2) Revenue Drivers\nRevenue was $4.0M in Q4 2026 (October 26, 2026).",
        ]))


# =============================================================================
# PART B: Direction
# =============================================================================
class TestPartB_WhenItApplies(unittest.TestCase):
    """B-1."""

    def test_explicit_sign_is_not_direction_checked(self):
        c = one("Revenue fell +6.4%.")
        self.assertEqual(c.status, "matched")
        c = one("Revenue rose −6.4%.")                         # R3 rejects the sign; a number flag, not a direction flag
        self.assertEqual(c.flag.flag_class, N.FLAG_CLASS_NUMBER)

    def test_flagged_number_is_not_direction_checked(self):
        c = one("Revenue fell 7%.")
        self.assertEqual(c.flag.flag_class, N.FLAG_CLASS_NUMBER)
        self.assertIsNone(c.flag.direction_word)

    def test_resolved_by_pick_is_direction_checked(self):
        t = "The total fell 6.4%."
        self.assertEqual(one(t).flag.reason, N.REASON_NO_NAME)
        c = one(t, picks={("6.4%", 0): PL_REVENUE})
        self.assertEqual(c.status, "flagged")
        self.assertEqual((c.flag.flag_class, c.flag.reason, c.flag.picked_line_id),
                         (N.FLAG_CLASS_DIRECTION, N.REASON_DIRECTION, PL_REVENUE))

    def test_accepted_only_is_not_a_match_and_is_not_direction_checked(self):
        a = N.Acceptance("6.4%", None, "A. Controller", "2026-11-15T09:00:00+00:00")
        r = check("The total fell 6.4%.", acceptances=[a])
        self.assertEqual([(f.flag_class, f.reason, f.is_open) for f in r.flags],
                         [(N.FLAG_CLASS_NUMBER, N.REASON_NO_NAME, False)])


class TestPartB_Words(unittest.TestCase):
    """B-2, E-2, E-8. The consolidated Revenue line prints +6.4%; the Budget line prints -6.5%."""

    def test_every_word_before_the_number(self):
        for w, d in N.DIRECTION_WORDS_BEFORE.items():
            with self.subTest(w=w):
                c = one(f"Revenue {w} 6.4%.")
                if d == N.UP:
                    self.assertEqual(c.status, "matched")
                else:
                    self.assertEqual((c.flag.reason, c.flag.direction_word, c.flag.direction),
                                     (N.REASON_DIRECTION, w, N.DOWN))

    def test_every_word_after_the_number(self):
        for w, d in N.DIRECTION_WORDS_AFTER.items():
            with self.subTest(w=w):
                c = one(f"Revenue was 6.4% {w}.")
                self.assertEqual(c.status, "matched" if d == N.UP else "flagged")

    def test_below_above_under_over_need_a_budget_word(self):
        for w, d in N.DIRECTION_WORDS_AFTER_WITH_BUDGET.items():
            for tail in ("budget", "the budget", "its plan", "our budget", "Watch"):
                with self.subTest(w=w, tail=tail):
                    c = one(f"Revenue was 6.5% {w} {tail}.")
                    self.assertEqual(c.line_id, BUDGET_REVENUE)
                    self.assertEqual(c.status, "matched" if d == N.DOWN else "flagged")
        for t in ("Revenue fell 6% over the year.", "Revenue grew 6.4% over last quarter."):
            with self.subTest(t=t):
                c = one(t)
                self.assertNotIn("over", (c.flag.direction_word,) if c.flag else ())

    def test_words_not_on_the_list_are_not_checked(self):
        for t in ("Revenue improved 6.4%.", "Revenue worsened 6.4%.", "Revenue was 6.4% more.",
                  "Revenue was 6.4% less.", "Revenue rising 6.4%.", "Revenue's favourable 6.4%."):
            with self.subTest(t=t):
                self.assertEqual(one(t).status, "matched")
        self.assertEqual(one("Revenue was 6.5% behind budget.").status, "matched")


class TestPartB_Attachment(unittest.TestCase):
    """B-3, E-3."""

    def test_fillers(self):
        for f in sorted(N.DIRECTION_FILLERS):
            with self.subTest(filler=f):
                self.assertEqual(one(f"Revenue fell {f} 6.4%.").flag.reason, N.REASON_DIRECTION)
        self.assertEqual(one("Revenue fell by about 6.4%.").flag.reason, N.REASON_DIRECTION)

    def test_punctuation_or_another_word_between_breaks_attachment(self):
        for t in ("Revenue fell, 6.4% in all.", "Revenue fell sharply 6.4%.", "Revenue fell (6.4%).",
                  "Revenue was 6.4%, lower."):
            with self.subTest(t=t):
                self.assertEqual(one(t).status, "matched")

    def test_to_or_from_makes_a_level(self):
        r = check("Revenue rose by 6.4% to $4.0M.")
        self.assertEqual([c.status for c in r.numbers], ["matched", "matched"])
        self.assertEqual(one("Revenue fell to $4.0M.").status, "matched")
        self.assertEqual(one("Revenue was 6.4% down from last quarter.").status, "matched")
        self.assertEqual(one("Revenue was 6.4% down by about to nothing.").status, "matched")

    def test_unattached_words_are_ignored(self):
        self.assertEqual(one("Revenue fell short of hopes, but it was 6.4% in total.").status, "matched")


class TestPartB_Negation(unittest.TestCase):
    """B-4, E-4."""

    def test_negations_within_three_words(self):
        for t in ("Revenue has not fallen 6.4%.", "Revenue hasn't dropped 6.4%.", "Revenue never declined 6.4%.",
                  "Revenue isn’t down 6.4%.", "There was no decline; Revenue was not 6.4% lower.",
                  "Revenue, without doubt, down 6.4%."):
            with self.subTest(t=t):
                self.assertEqual(one(t).status, "matched")

    def test_negation_four_words_away_does_not_count(self):
        c = one("Not that Revenue really honestly fell 6.4%.")
        self.assertEqual(c.flag.reason, N.REASON_DIRECTION)

    def test_negation_in_the_previous_sentence_does_not_count(self):
        c = one("It was not bad. Revenue fell 6.4%.")
        self.assertEqual(c.flag.reason, N.REASON_DIRECTION)


class TestPartB_Verdict(unittest.TestCase):
    """B-5, B-6, E-5, E-6, ruling 3."""

    SB = N.parse_data_block(SYNTH)

    def test_disagreeing_sign_flags_with_the_line(self):
        c = one("Revenue fell 6.4%.")
        f = c.flag
        self.assertEqual((c.status, c.line_id), ("flagged", PL_REVENUE))
        self.assertEqual((f.flag_class, f.reason, f.direction_word, f.direction, f.placed),
                         (N.FLAG_CLASS_DIRECTION, N.REASON_DIRECTION, "fell", N.DOWN, True))
        self.assertEqual(f.line.line_id, PL_REVENUE)
        self.assertIn("+6.4%", f.line.figures)
        self.assertEqual(f.kind, N.PERCENT)                    # Flag.kind is still the number's kind

    def test_E6_mixed_sign_equal_figures_agree_if_any_agrees(self):
        self.assertEqual(one("Alpha fell 5.0%.", self.SB).status, "matched")
        self.assertEqual(one("Alpha rose 5.0%.", self.SB).status, "matched")
        self.assertEqual(one("Gamma rose 3.0%.", self.SB).flag.reason, N.REASON_DIRECTION)

    def test_printed_zero_is_not_checked(self):
        self.assertEqual(one("Beta fell 0.0%.", self.SB).status, "matched")
        self.assertEqual(one("Beta rose 0.0%.", self.SB).status, "matched")

    def test_B6_two_words_that_disagree_ruling3_fields_empty(self):
        for t in ("Revenue rose 6.4% lower.", "Revenue fell 6.4% higher.", "Revenue was up 6.5% below budget."):
            with self.subTest(t=t):
                f = one(t).flag
                self.assertEqual((f.flag_class, f.reason), (N.FLAG_CLASS_DIRECTION, N.REASON_DIRECTION_WORDS_DISAGREE))
                self.assertIsNone(f.direction_word)
                self.assertIsNone(f.direction)

    def test_two_agreeing_words(self):
        self.assertEqual(one("Revenue rose 6.4% higher.").status, "matched")
        f = one("Revenue fell 6.4% lower.").flag
        self.assertEqual((f.reason, f.direction_word, f.direction), (N.REASON_DIRECTION, "fell", N.DOWN))

    def test_known_miss_ii_is_narrowed_and_otherwise_kept(self):
        self.assertEqual(one("Operating Profit grew by $1,534,550.").status, "matched")   # Release 1 miss (ii) kept
        self.assertEqual(one("Operating Profit fell by $1,534,550.").flag.reason, N.REASON_DIRECTION)

    def test_known_misses_i_and_iii_unchanged(self):
        self.assertEqual(one("Operating Margin rose to 35.0% this quarter.").status, "matched")
        self.assertEqual(one("Revenue was led by EMEA, and Professional Services added 10.0%.").status, "matched")


class TestPartB_Acceptance(unittest.TestCase):
    """B-7, B-7a."""

    def test_classes_and_new_fields(self):
        self.assertEqual((N.FLAG_CLASS_NUMBER, N.FLAG_CLASS_DIRECTION), ("number", "direction"))
        fields = set(N.Flag.__dataclass_fields__)
        self.assertTrue({"flag_class", "direction_word", "direction", "kind"} <= fields)
        self.assertEqual(N.Acceptance("1%", None, "x", "t").flag_class, N.FLAG_CLASS_NUMBER)
        self.assertEqual(one("Revenue was up 7%.").flag.flag_class, N.FLAG_CLASS_NUMBER)

    def test_keys(self):
        f = one("Revenue fell 6.4%.").flag
        self.assertEqual(f.acceptance_key, ("6.4%", PL_REVENUE, "direction"))
        self.assertEqual(N.Acceptance("6.4%", PL_REVENUE, "x", "t", N.FLAG_CLASS_DIRECTION).key,
                         ("6.4%", PL_REVENUE, "direction"))
        self.assertEqual(N.Acceptance("6.4%", PL_REVENUE, "x", "t").key, ("6.4%", PL_REVENUE))
        self.assertEqual(one("Operating Margin was 40.0%.").flag.acceptance_key[2:], ())

    def test_an_ordinary_acceptance_does_not_cover_a_direction_flag(self):
        ordinary = N.Acceptance("6.4%", PL_REVENUE, "A. Controller", "2026-11-15T09:00:00+00:00")
        self.assertEqual(check("Revenue fell 6.4%.", acceptances=[ordinary]).open_count, 1)
        direction = N.Acceptance("6.4%", PL_REVENUE, "A. Controller", "2026-11-15T09:00:00+00:00",
                                 N.FLAG_CLASS_DIRECTION)
        r = check("Revenue fell 6.4%.", acceptances=[direction])
        self.assertEqual((r.open_count, r.flags[0].accepted), (0, direction))
        self.assertEqual(check("Operating Margin was 40.0%.",
                               acceptances=[N.Acceptance("40.0%", lid("Operating Margin", "Consolidated"), "x", "t",
                                                         N.FLAG_CLASS_DIRECTION)]).open_count, 1)

    def test_pick_then_ordinary_acceptance_does_not_hide_a_direction_mismatch(self):
        t = "The total fell 6.4%."
        ordinary = N.Acceptance("6.4%", PL_REVENUE, "x", "t")
        r = check(t, picks={("6.4%", 0): PL_REVENUE}, acceptances=[ordinary])
        self.assertEqual([(f.flag_class, f.is_open) for f in r.flags], [(N.FLAG_CLASS_DIRECTION, True)])

    def test_reason_constants(self):
        self.assertEqual(N.REASON_DIRECTION, "the direction word disagrees with the sign printed on the line")
        self.assertEqual(N.REASON_DIRECTION_WORDS_DISAGREE, "the two direction words disagree")
        reasons = [N.REASON_NO_NAME, N.REASON_AMBIGUOUS, N.REASON_NAME_DOES_NOT_CARRY_IT, N.REASON_NO_EQUAL_FIGURE,
                   N.REASON_PICK_MISMATCH, N.REASON_DIRECTION, N.REASON_DIRECTION_WORDS_DISAGREE]
        self.assertEqual(len(set(reasons)), 7)
        for s in (N.REASON_DIRECTION, N.REASON_DIRECTION_WORDS_DISAGREE):
            for word in ("hard", "soft", "none"):
                self.assertNotIn(word, s.lower().split())

    def test_one_flag_per_number_at_most(self):
        r = check("Revenue fell 6.4%. The total fell 6.4%. Revenue was up 7%.")
        self.assertEqual(len(r.flags), len([c for c in r.numbers if c.status == "flagged"]))


# =============================================================================
# The addendum's acceptance illustrations (copied; Architect-authored, read from the data, not run)
# =============================================================================
class TestArchitectIllustrations(unittest.TestCase):

    def test_illustrations(self):
        D, NUM = N.FLAG_CLASS_DIRECTION, N.FLAG_CLASS_NUMBER
        cases = [
            ("Revenue was $4.0M.", "matched", PL_REVENUE, None),
            ("Revenue was up 7%.", "flagged", None, NUM),
            ("Revenue was up 6.5% against budget.", "flagged", BUDGET_REVENUE, D),
            ("Revenue missed budget by 6.5%.", "matched", BUDGET_REVENUE, None),
            ("Revenue missed budget. It was 6.5% short.", "matched", BUDGET_REVENUE, None),
            ("Revenue was 6.5% below budget.", "matched", BUDGET_REVENUE, None),
            ("Revenue was 6.5% above budget.", "flagged", BUDGET_REVENUE, D),
            ("Revenue came in below the budgeted $4.3M.", "matched", BUDGET_REVENUE, None),
            ("Revenue fell 6% over the year.", "flagged", PL_REVENUE, D),
            ("Revenue flagged Watch at −6.5%.", "matched", BUDGET_REVENUE, None),
            ("Revenue came in 6.5% short of target.", "flagged", None, NUM),
            ("Revenue fell 6%.", "flagged", PL_REVENUE, D),
        ]
        for t, status, line, cls in cases:
            with self.subTest(t=t):
                c = one(t)
                self.assertEqual(c.status, status)
                if line is not None:
                    self.assertEqual(c.line_id, line)
                if cls is not None:
                    self.assertEqual(c.flag.flag_class, cls)
        c = one("Revenue fell 6% over the year.")
        self.assertEqual(c.flag.direction_word, "fell")
        self.assertEqual(one("Revenue fell to $3.9M.").flag.flag_class, NUM)   # not direction-checked
        c = one("Revenue missed budget. APAC grew 12%.")
        self.assertEqual(c.flag.flag_class, NUM)
        self.assertFalse(N._uses_budget_pool(N.find_numbers("Revenue missed budget. APAC grew 12%.")[0],
                                             "Revenue missed budget. APAC grew 12%.",
                                             N._sentence_spans("Revenue missed budget. APAC grew 12%."), BLOCK))
        for t in ("Revenue flagged Watch at −6.5%.", "Revenue came in 6.5% short of target."):
            n = N.find_numbers(t)[0]
            c = one(t, picks={(n.raw, 0): BUDGET_REVENUE})
            self.assertEqual((c.status, c.line_id), ("matched_by_pick", BUDGET_REVENUE))


class TestDeterminism(unittest.TestCase):
    TEXT = ("Revenue fell 6.4%. Revenue was 6.5% above budget. Revenue missed budget. It was 6.5% short. "
            "Revenue rose 6.4% lower. The total fell 6.4%. Revenue came in 6.5% short of target.")

    def test_same_input_same_output(self):
        a = check(self.TEXT, picks={("6.4%", 3): PL_REVENUE})
        b = check(self.TEXT, picks={("6.4%", 3): PL_REVENUE})
        self.assertEqual(a, b)
        self.assertEqual(N.check_numbers(self.TEXT, DATA), check(self.TEXT))


if __name__ == "__main__":
    unittest.main()
