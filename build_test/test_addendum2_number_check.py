"""
Builder component tests for D22 Number Check Amendment, Addendum 2 (revision 2,
signed 2026-11-13; governance/builder_briefs/D22_Narrative_versioning_builder_brief_addendum_2.md):
Part A (collapse duplicates) and Part D1 (leading qualifiers), plus the
addendum's N-4 reading of Addendum 1 after collapse.

STATUS: Builder-authored COMPONENT tests. NOT calibration and NOT independent
validation: Independent Test writes the cases and measures the false-flag rate
(addendum, Required evidence). The addendum itself contains no test sentence;
every sentence here is invented by the Builder. No Independent Test case or
result was looked for or used.

Data: the real DATA block of build_test/fixtures/rendered_prompt_q4_fy2026_demo.txt
(canonical SYNTHETIC sample dataset), in-memory variants of it with no Budget
lines, and small SYNTHETIC blocks for rules the fixture cannot show (different
values under one name, opposite signs, labels with qualifiers other than the
one in the fixture). The Addendum 1 reference is
build_test/fixtures/narrative_number_check_addendum1.py, a byte-exact copy of the
module on main at 43f9695 (SHA-256 checked below).

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
ADDENDUM1_COPY = os.path.join(FIXTURES, "narrative_number_check_addendum1.py")
ADDENDUM1_SHA256 = "c0a4150daf67be7a6fd454f51c3a8f5e30fe95cfa889433b1d3f48533438572b"

with open(FIXTURE, encoding="utf-8") as _f:
    DATA = N.extract_data_block(_f.read())
BLOCK = N.parse_data_block(DATA)
BUDGET_LINE_TEXT = "  - Revenue: Budget $4,294,336, Actual $4,016,906, Variance -6.5% — Watch"
NO_HEADING_DATA = DATA.replace(N.BUDGET_SECTION_HEADING, "Budget vs Actual (heading renamed)")
NONE_FLAGGED_DATA = DATA.replace(BUDGET_LINE_TEXT, "  (none flagged Watch or Major Miss this period)")


def synth(*sections):
    """A synthetic DATA block: each section is (title, [line texts])."""
    out = []
    for title, lines in sections:
        out.append(f"{title}:")
        out.extend(f"  - {ln}" for ln in lines)
    return N.parse_data_block("\n".join(out) + "\n")


def one(text, block=BLOCK, **kw):
    r = N.check_numbers(text, block, **kw)
    assert len(r.numbers) == 1, [c.number.raw for c in r.numbers]
    return r.numbers[0]


def ids_with(block, label, raw=None):
    return [ln.line_id for ln in block.lines if ln.label == label
            and (raw is None or any(f.raw == raw for f in ln.figures))]


def load_addendum1():
    spec = importlib.util.spec_from_file_location("narrative_number_check_addendum1", ADDENDUM1_COPY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ref(r):
    return None if r is None else (r.line_id, r.section, r.label, tuple(r.figures))


def summary(result):
    """Everything an Addendum 1 result holds, as plain values (the modules' classes differ)."""
    out = []
    for c in result.numbers:
        f = c.flag
        out.append((c.number.raw, c.number.occurrence, c.status, c.line_id, None if f is None else (
            f.ordinal, f.kind, f.kind_words, f.reason, f.placed, _ref(f.line), f.line_has_figure_of_kind,
            tuple(x.line_id for x in f.candidate_lines), tuple(x.line_id for x in f.lines_of_kind),
            f.picked_line_id, f.sentence_start, f.sentence_end, f.flag_class, f.direction_word, f.direction,
            None if f.accepted is None else (f.accepted.number, f.accepted.line_id))))
    return tuple(out)


APAC = ids_with(BLOCK, "APAC", "$669,939")
PL_REVENUE = [ln.line_id for ln in BLOCK.lines if ln.label == "Revenue" and "Consolidated" in ln.section][0]
RPH = ids_with(BLOCK, "Company-wide Revenue per Headcount")


# =============================================================================
# PART A: collapse duplicates
# =============================================================================
class TestPartA_Collapse(unittest.TestCase):

    def test_fixture_has_the_two_apac_lines(self):
        self.assertEqual(len(APAC), 2)
        self.assertNotEqual(BLOCK.by_id[APAC[0]].section, BLOCK.by_id[APAC[1]].section)

    def test_A1_same_value_on_two_named_lines_matches_first_in_block_order(self):
        c = one("In APAC: $669,939.")
        self.assertEqual((c.status, c.line_id, c.flag), ("matched", APAC[0], None))
        self.assertLess(BLOCK.by_id[APAC[0]].index, BLOCK.by_id[APAC[1]].index)

    def test_A1_precision_written_still_applies(self):
        for t in ("In APAC: $670K.", "In APAC: $0.7M.", "In APAC: $669,939."):
            with self.subTest(t=t):
                self.assertEqual(one(t).line_id, APAC[0])
        self.assertEqual(one("In APAC: $669,940.").status, "flagged")

    def test_A1_different_values_stay_ambiguous(self):
        b = synth(("Region A", ["Delta: 4.1%"]), ("Region B", ["Delta: 4.2%"]))
        c = one("Delta was 4%.", b)
        self.assertEqual((c.status, c.flag.reason, len(c.flag.candidate_lines)), ("flagged", N.REASON_AMBIGUOUS, 2))
        self.assertEqual(one("Delta was 4.1%.", b).status, "matched")    # only one line equals: one-line rule

    def test_EA1_same_magnitude_opposite_signs_are_not_the_same_value(self):
        b = synth(("Region A", ["Sigma: +5.0%"]), ("Region B", ["Sigma: -5.0%"]))
        c = one("Sigma was 5.0%.", b)
        self.assertEqual((c.status, c.flag.reason), ("flagged", N.REASON_AMBIGUOUS))
        c = one("Sigma was +5.0%.", b)                                    # explicit sign: one line equals
        self.assertEqual((c.status, c.line_id), ("matched", ids_with(b, "Sigma", "+5.0%")[0]))

    def test_EA1_same_value_printed_differently_is_the_same_value(self):
        b = synth(("Region A", ["Omega: $1,000"]), ("Region B", ["Omega: $1,000.00"]))
        self.assertEqual(one("Omega was $1,000.", b).status, "matched")

    def test_EA2_a_line_carrying_two_equal_values_keeps_it_a_flag(self):
        b = synth(("Region A", ["Echo: 4.1% vs 4.2%"]), ("Region B", ["Echo: 4.1%"]))
        self.assertEqual(one("Echo was 4%.", b).flag.reason, N.REASON_AMBIGUOUS)
        b = synth(("Region A", ["Echo: 4.1%"]), ("Region B", ["Echo: 4.1%"]), ("Region C", ["Echo: 4.1%"]))
        self.assertEqual(one("Echo was 4%.", b).line_id, ids_with(b, "Echo")[0])

    def test_A3_matched_line_follows_block_order(self):
        b1 = synth(("First", ["Kappa: $77"]), ("Second", ["Kappa: $77"]))
        b2 = synth(("Second", ["Kappa: $77"]), ("First", ["Kappa: $77"]))
        self.assertEqual(b1.by_id[one("Kappa was $77.", b1).line_id].section, "First")
        self.assertEqual(b2.by_id[one("Kappa was $77.", b2).line_id].section, "Second")

    def test_A2_no_fall_back_without_a_name(self):
        c = one("The figure of $669,939 stands.")
        self.assertEqual((c.status, c.flag.reason), ("flagged", N.REASON_NO_NAME))
        self.assertEqual([x.line_id for x in c.flag.candidate_lines], APAC)

    def test_A2_picks_unchanged(self):
        c = one("The figure of $669,939 stands.", picks={("$669,939", 0): APAC[1]})
        self.assertEqual((c.status, c.line_id), ("matched_by_pick", APAC[1]))
        c = one("In APAC: $669,939.", picks={("$669,939", 0): PL_REVENUE})
        self.assertEqual(c.flag.reason, N.REASON_PICK_MISMATCH)

    def test_A2_pools_unchanged_collapse_works_on_the_pool(self):
        c = one("Revenue was $4,016,906 against budget.")                 # budget pool: the one Budget line
        self.assertTrue(BLOCK.by_id[c.line_id].is_budget)
        c = one("Revenue was $4,016,906.")                                # actual pool: the one P&L line
        self.assertEqual(c.line_id, PL_REVENUE)
        nb = N.parse_data_block(NO_HEADING_DATA)                          # no Budget lines: both lines actual
        first = ids_with(nb, "Revenue", "$4,016,906")[0]
        self.assertEqual(one("Revenue was $4,016,906.", nb).line_id, first)

    def test_A2_acceptance_unchanged(self):
        b = synth(("Region A", ["Delta: 4.1%"]), ("Region B", ["Delta: 4.2%"]))
        a = N.Acceptance("4%", None, "A. Controller", "2026-11-16T09:00:00+00:00")
        r = N.check_numbers("Delta was 4%.", b, acceptances=[a])
        self.assertEqual((len(r.flags), r.open_count), (1, 0))

    def test_A4_known_miss_iv_is_an_expected_pass(self):
        """(iv): the number equals the shared value of two same-named lines but describes only one of them."""
        b = synth(("Revenue table", ["Alpha: $500"]), ("Margin table", ["Alpha: $500"]))
        self.assertEqual(one("Alpha margin was $500.", b).status, "matched")


# =============================================================================
# PART D1: leading qualifiers
# =============================================================================
class TestPartD1_Qualifiers(unittest.TestCase):

    def test_constants(self):
        self.assertEqual(N.IGNORABLE_QUALIFIERS, (("company", "wide"), ("total",)))
        self.assertEqual(N.MIN_TOKENS_AFTER_QUALIFIER, 2)

    def test_D13_fixture_gets_exactly_one_new_alias(self):
        old = load_addendum1().parse_data_block(DATA)
        added = {ln.line_id: set(ln.aliases) - set(o.aliases) for ln, o in zip(BLOCK.lines, old.lines)}
        added = {k: v for k, v in added.items() if v}
        self.assertEqual(added, {RPH[0]: {("revenue", "per", "headcount")}})
        for ln in BLOCK.lines:
            if ln.label in ("Total Opex", "Total Variance"):
                self.assertEqual(ln.aliases, (tuple(N._name_tokens(ln.label)),))

    def test_D11_name_without_the_qualifier_matches(self):
        label_line = BLOCK.by_id[RPH[0]]
        fig = label_line.figures[0].raw
        for t in (f"Revenue per Headcount was {fig}.", f"revenue per headcount was {fig}.",
                  f"Company-wide Revenue per Headcount was {fig}.", f"Company wide revenue per headcount: {fig}."):
            with self.subTest(t=t):
                c = one(t)
                self.assertEqual((c.status, c.line_id), ("matched", RPH[0]))

    def test_D13_guard_one_remaining_word_gives_no_alias(self):
        a1 = load_addendum1()
        old_b = a1.parse_data_block(DATA)
        for t in ("Opex was $2,482,356.", "Variance was $10,751.", "Total Opex was $2,482,356."):
            with self.subTest(t=t):
                self.assertEqual(summary(N.check_numbers(t, BLOCK)), summary(a1.check_numbers(t, old_b)))

    def test_D11_rules_on_synthetic_labels(self):
        b = synth(("S", ["Total Widget Sales: $10", "TOTAL Gadget Units: $11", "Company-wide Widgets: $3",
                         "Net Total Sales: $9", "Grand Total: $8", "Total Company-wide Sales Volume: $7",
                         "Gross Revenue Base: $6", "Totally New Thing: $5", "Companywide Sales Base: $4"]))
        aliases = {ln.label: ln.aliases for ln in b.lines}
        self.assertIn(("widget", "sales"), aliases["Total Widget Sales: $10".split(":")[0]])
        self.assertIn(("gadget", "units"), aliases["TOTAL Gadget Units"])             # case-insensitive
        self.assertEqual(len(aliases["Company-wide Widgets"]), 1)                     # guard: one token left
        self.assertEqual(len(aliases["Net Total Sales"]), 1)                          # start of the label only
        self.assertEqual(len(aliases["Grand Total"]), 1)
        self.assertIn(("company", "wide", "sales", "volume"), aliases["Total Company-wide Sales Volume"])
        self.assertNotIn(("sales", "volume"), aliases["Total Company-wide Sales Volume"])  # one qualifier only
        self.assertEqual(len(aliases["Gross Revenue Base"]), 1)                       # not in the list
        self.assertEqual(len(aliases["Totally New Thing"]), 1)                        # whole words
        self.assertEqual(len(aliases["Companywide Sales Base"]), 1)
        self.assertEqual(one("Widget Sales were $10.", b).status, "matched")
        self.assertEqual(one("Total Widget Sales were $10.", b).status, "matched")

    def test_D11_new_alias_is_shared_and_existing_rules_decide(self):
        same = synth(("A", ["Total Widget Sales: $10"]), ("B", ["Widget Sales: $10"]))
        self.assertEqual(one("Widget Sales were $10.", same).line_id, ids_with(same, "Total Widget Sales")[0])
        diff = synth(("A", ["Total Widget Sales: $10.4"]), ("B", ["Widget Sales: $9.6"]))
        self.assertEqual(one("Widget Sales were $10.", diff).flag.reason, N.REASON_AMBIGUOUS)
        self.assertEqual(one("Total Widget Sales were $10.", diff).status, "matched")  # full label: one line

    def test_D14_known_miss_v_is_an_expected_pass(self):
        """(v): a shortened name that equals the qualified line's figure, when the writer meant another entity."""
        b = synth(("A", ["Total Widget Sales: $10"]), ("B", ["EMEA: $12"]))
        self.assertEqual(one("Widget Sales were $10.", b).status, "matched")


# =============================================================================
# N-4: Addendum 1 after collapse
# =============================================================================
class TestN4_Addendum1AfterCollapse(unittest.TestCase):

    def test_direction_runs_on_a_collapsed_match_against_the_first_line(self):
        self.assertEqual(one("APAC grew by $669,939.").status, "matched")
        c = one("APAC fell by $669,939.")
        f = c.flag
        self.assertEqual((c.status, c.line_id, f.flag_class, f.reason), ("flagged", APAC[0], "direction",
                                                                          N.REASON_DIRECTION))
        self.assertEqual(f.line.line_id, APAC[0])
        self.assertEqual(f.acceptance_key, ("$669,939", APAC[0], "direction"))

    def test_direction_acceptance_key_carries_the_first_collapsed_line(self):
        first = N.Acceptance("$669,939", APAC[0], "x", "t", N.FLAG_CLASS_DIRECTION)
        second = N.Acceptance("$669,939", APAC[1], "x", "t", N.FLAG_CLASS_DIRECTION)
        self.assertEqual(N.check_numbers("APAC fell by $669,939.", BLOCK, acceptances=[first]).open_count, 0)
        self.assertEqual(N.check_numbers("APAC fell by $669,939.", BLOCK, acceptances=[second]).open_count, 1)

    def test_collapsed_lines_carry_one_sign(self):
        b = synth(("A", ["Theta: -2.0%"]), ("B", ["Theta: -2.0%"]))
        self.assertEqual(one("Theta fell 2.0%.", b).status, "matched")
        self.assertEqual(one("Theta rose 2.0%.", b).flag.reason, N.REASON_DIRECTION)


# =============================================================================
# Regression: unchanged where neither A nor D1 applies
# =============================================================================
class TestRegressionAgainstAddendum1(unittest.TestCase):
    """Acceptance criterion: "Release 1 behaviour is unchanged for names and numbers not touched by A or D1."
    Compared field by field with the byte-exact Addendum 1 module; every sentence that differs is named, and
    each is shown to differ only by the collapse (Release 1/Addendum 1: REASON_AMBIGUOUS, now matched) or by the
    one new D1 alias."""

    CORPUS = [
        "Revenue was $4,016,906.", "Revenue was $4.0M.", "Revenue was 6.5%.", "Revenue was $4,294,336.",
        "Operating Margin was 38.2%, up from 35.0%.", "R&D spend was $902,208.", "Operating Profit was $1.5M.",
        "Total Opex was $4,016,906.", "The figure of $4,016,906 stands.", "In APAC: $669,939.",
        "We saw $12,345 somewhere.", "Operating Margin improved. It reached 38.2%.", "38.2% was the Operating Margin.",
        "Sales and Marketing spend was $754,316.", "Add-on: Forecasting grew +11.5%.", "EMEA's growth was +10.0%.",
        "Operating Margin was 40.0%.", "Total Opex was 9.9%.", "G&A total variance was $10,751.",
        "Professional Services added 10.0%.", "Operating Margin rose to 35.0% this quarter.",
        "Revenue missed budget. It was 6.5% short.", "Revenue was 6.5% above budget.", "Revenue fell 6.4%.",
        "Revenue rose 6.4% lower.", "Revenue came in 6.5% short of target.", "APAC fell by $669,939.",
        "Revenue per Headcount was $24,053.", "Company-wide Revenue per Headcount was $24,053.",
        "Opex was $2,482,356.", "Variance was $10,751.", "Headcount was 167.", "",
    ]
    EXPECTED_CHANGED = {
        "real": {"In APAC: $669,939.", "APAC fell by $669,939.", "Revenue per Headcount was $24,053."},
        "no heading": {"In APAC: $669,939.", "APAC fell by $669,939.", "Revenue per Headcount was $24,053.",
                       "Revenue was $4,016,906.", "Revenue was $4.0M."},
        "none flagged": {"In APAC: $669,939.", "APAC fell by $669,939.", "Revenue per Headcount was $24,053."},
    }

    @classmethod
    def setUpClass(cls):
        cls.A1 = load_addendum1()

    def test_addendum1_reference_copy_is_byte_exact(self):
        with open(ADDENDUM1_COPY, "rb") as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), ADDENDUM1_SHA256)

    def test_only_the_named_sentences_change(self):
        for label, data in (("real", DATA), ("no heading", NO_HEADING_DATA), ("none flagged", NONE_FLAGGED_DATA)):
            new_b, old_b = N.parse_data_block(data), self.A1.parse_data_block(data)
            changed = {t for t in self.CORPUS
                       if summary(N.check_numbers(t, new_b)) != summary(self.A1.check_numbers(t, old_b))}
            with self.subTest(block=label):
                self.assertEqual(changed, self.EXPECTED_CHANGED[label])

    def test_each_change_is_the_collapse_or_the_new_alias(self):
        for label, data in (("real", DATA), ("no heading", NO_HEADING_DATA), ("none flagged", NONE_FLAGGED_DATA)):
            new_b, old_b = N.parse_data_block(data), self.A1.parse_data_block(data)
            for t in self.EXPECTED_CHANGED[label]:
                with self.subTest(block=label, t=t):
                    cn = N.check_numbers(t, new_b).numbers[0]
                    co = self.A1.check_numbers(t, old_b).numbers[0]
                    self.assertEqual(co.status, "flagged")
                    if "Revenue per Headcount" in t:                       # D1: the new alias names the line
                        self.assertEqual(co.flag.reason, self.A1.REASON_NAME_DOES_NOT_CARRY_IT)
                        self.assertEqual(new_b.by_id[cn.line_id].label, "Company-wide Revenue per Headcount")
                        self.assertEqual(cn.status, "matched")
                    else:                                                  # A: collapse
                        self.assertEqual(co.flag.reason, self.A1.REASON_AMBIGUOUS)
                        self.assertEqual(cn.line_id, co.flag.candidate_lines[0].line_id)
                        self.assertIn(cn.status, ("matched", "flagged"))
                        if cn.status == "flagged":                         # N-4: the direction check then runs
                            self.assertEqual(cn.flag.flag_class, N.FLAG_CLASS_DIRECTION)

    def test_line_ids_unchanged(self):
        old_b = self.A1.parse_data_block(DATA)
        self.assertEqual([ln.line_id for ln in old_b.lines], [ln.line_id for ln in BLOCK.lines])

    def test_deterministic(self):
        text = " ".join(self.CORPUS)
        self.assertEqual(N.check_numbers(text, BLOCK), N.check_numbers(text, BLOCK))
        self.assertEqual(N.check_numbers(text, DATA), N.check_numbers(text, BLOCK))


if __name__ == "__main__":
    unittest.main()
