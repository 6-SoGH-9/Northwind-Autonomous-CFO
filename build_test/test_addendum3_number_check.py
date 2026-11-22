"""
Builder component tests for D22 Addendum 3 (revision 3, signed 2026-11-22;
governance/builder_briefs/D22_Narrative_versioning_builder_brief_addendum_3.md):
the list-numbering fix. A token that carries a unit is not list numbering
(B-1, and B-1a: every unit the scanner already recognises). A bare integer
still is (B-2).

STATUS: Builder-authored COMPONENT tests. Builder evidence ONLY: NOT calibration
and NOT independent validation. Independent Test writes and owns the cases and
expected results (Addendum 3 section 5). Every sentence here is invented by the
Builder; the short forms quoted in the addendum's section 1 table are reused as
probe inputs. No Independent Test case or result was looked for or used.

Data: the real DATA block of build_test/fixtures/rendered_prompt_q4_fy2026_demo.txt
(canonical SYNTHETIC sample dataset) for the percent case, and small SYNTHETIC
one-line blocks for the other units, which the fixture does not print as
integers.

What each unit test shows (section 3.2): the figure at the start of a line is
now scanned, and its result (status, line, reason, flag class, kind) is exactly
the result the same figure gets in the middle of a line, for a right value and
for a wrong value.

Run from the repository root:  python -m unittest discover -s build_test -v
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import narrative_number_check as N  # noqa: E402

FIXTURE = os.path.join(ROOT, "build_test", "fixtures", "rendered_prompt_q4_fy2026_demo.txt")
with open(FIXTURE, encoding="utf-8") as _f:
    REAL_BLOCK = N.parse_data_block(N.extract_data_block(_f.read()))


def synth_block(figure):
    """A SYNTHETIC DATA block with one named line, 'EMEA', carrying the figure as printed."""
    return N.parse_data_block(f"Regional summary:\n  - EMEA: {figure}\n")


def raws(text):
    return [n.raw for n in N.find_numbers(text)]


def summary(result):
    """A result as plain values: one tuple per number found."""
    return [
        (c.number.raw, c.number.kind, c.status, c.line_id,
         c.flag.reason if c.flag else None, c.flag.flag_class if c.flag else None)
        for c in result.numbers
    ]


# Each unit the signed B-1 and B-1a cover: (written form, printed figure, a wrong written form).
# B-1: percent, K, M, B.  B-1a: "5 %", lowercase "k", "MM"/"mm", "bn", "mn", "x".
# Also "pp" and "pt": units the scanner already reads as percent (_PCT_TAIL), so inside
# B-1a's "every unit the scanner already recognises"; not listed in the addendum's section 1
# (see the Return Report, Architect review items).
B1_UNITS = [
    ("5K", "5K", "6K"),
    ("5M", "5M", "6M"),
    ("5B", "5B", "6B"),
]
B1A_UNITS = [
    ("5 %", "5%", "6 %"),
    ("5k", "5K", "6k"),
    ("5MM", "5M", "6MM"),
    ("5mm", "5M", "6mm"),
    ("5bn", "5B", "6bn"),
    ("5mn", "5M", "6mn"),
    ("5x", "5x", "6x"),
]
SCANNER_PCT_UNITS = [
    ("5pp", "5pp", "6pp"),
    ("5pt", "5pt", "6pt"),
]

# Line-start forms (previous line holds the name) and the mid-line form, per the addendum's table.
LINE_START_TEMPLATES = (
    "EMEA grew\n{}.",
    "EMEA grew\n{})",
    "EMEA grew\n{}. Then it held.",
    "EMEA grew\n* {}.",
    "EMEA grew\n- {}.",
    "EMEA grew\n> {}.",
    "EMEA grew\n** {}.",
    "EMEA grew\n({}).",
)
MID_LINE_TEMPLATE = "EMEA grew {}."


class _UnitCase(unittest.TestCase):
    def assert_line_start_equals_mid_line(self, written, block):
        mid = summary(N.check_numbers(MID_LINE_TEMPLATE.format(written), block))
        self.assertEqual(len(mid), 1, mid)
        for tmpl in LINE_START_TEMPLATES:
            text = tmpl.format(written)
            with self.subTest(text=text):
                self.assertEqual(raws(text), [written])          # scanned now
                self.assertEqual(summary(N.check_numbers(text, block)), mid)
        return mid[0]

    def check_unit(self, written, printed, wrong):
        block = synth_block(printed)
        right = self.assert_line_start_equals_mid_line(written, block)
        self.assertEqual(right[2], "matched", right)
        bad = self.assert_line_start_equals_mid_line(wrong, block)
        self.assertEqual(bad[2], "flagged", bad)
        self.assertEqual(bad[4], N.REASON_NO_EQUAL_FIGURE, bad)


class TestB1Units(_UnitCase):
    """Section 3.2, B-1: percent, K, M, B."""

    def test_percent_on_the_real_block(self):
        # "EMEA: $109,448 | +45%" is printed in the real fixture; "99%." is the addendum's own form.
        self.assertEqual(raws("EMEA grew\n99%."), ["99%"])
        self.assertEqual(raws("* 99%. EMEA grew."), ["99%"])
        right = self.assert_line_start_equals_mid_line("45%", REAL_BLOCK)
        self.assertEqual(right[1], N.PERCENT)
        self.assertEqual(right[2], "matched", right)
        bad = self.assert_line_start_equals_mid_line("99%", REAL_BLOCK)
        self.assertEqual(bad[2], "flagged", bad)

    def test_percent_on_a_synthetic_block(self):
        self.check_unit("99%", "99%", "98%")

    def test_K(self):
        self.check_unit(*B1_UNITS[0])

    def test_M(self):
        self.check_unit(*B1_UNITS[1])

    def test_B(self):
        self.check_unit(*B1_UNITS[2])


class TestB1aUnits(_UnitCase):
    """Section 3.2, B-1a (ticked): one test for each further form in section 1's last paragraph."""

    def test_space_percent(self):
        self.check_unit(*B1A_UNITS[0])

    def test_lowercase_k(self):
        self.check_unit(*B1A_UNITS[1])

    def test_MM(self):
        self.check_unit(*B1A_UNITS[2])

    def test_mm(self):
        self.check_unit(*B1A_UNITS[3])

    def test_bn(self):
        self.check_unit(*B1A_UNITS[4])

    def test_mn(self):
        self.check_unit(*B1A_UNITS[5])

    def test_x(self):
        self.check_unit(*B1A_UNITS[6])


class TestOtherScannerUnits(_UnitCase):
    """B-1a covers every unit the scanner already recognises: "pp" and "pt" are such units
    (read as percent) with the same defect on 52bb5c5. Not listed in the addendum's section 1."""

    def test_pp(self):
        self.check_unit(*SCANNER_PCT_UNITS[0])

    def test_pt(self):
        self.check_unit(*SCANNER_PCT_UNITS[1])


class TestUnchanged(unittest.TestCase):
    """Section 3.3: behaviour that must not change."""

    def test_bare_integer_is_still_list_numbering(self):
        # B-2: the accepted residual miss.
        for text in ("3. EMEA grew.", "3) EMEA grew", "12. Headcount rose.",
                     "EMEA grew\n12. Headcount rose.", "* 3. EMEA grew.", "EMEA grew\n5.", "EMEA grew\n5)"):
            with self.subTest(text=text):
                self.assertEqual(raws(text), [])

    def test_decimals_at_line_start(self):
        for written, printed in (("6.4%", "6.4%"), ("5.5K", "5.5K")):
            block = synth_block(printed)
            line_start = summary(N.check_numbers(f"EMEA grew\n{written}.", block))
            self.assertEqual(line_start, summary(N.check_numbers(f"EMEA grew {written}.", block)))
            self.assertEqual(line_start[0][2], "matched")

    def test_dollar_at_line_start(self):
        block = synth_block("$5M")
        line_start = summary(N.check_numbers("EMEA grew\n$5M.", block))
        self.assertEqual(line_start, summary(N.check_numbers("EMEA grew $5M.", block)))
        self.assertEqual(line_start[0][1:3], (N.DOLLAR, "matched"))

    def test_words_at_line_start(self):
        for written, printed in (("5 percent", "5%"), ("5 million", "5M")):
            block = synth_block(printed)
            line_start = summary(N.check_numbers(f"EMEA grew\n{written}.", block))
            self.assertEqual(raws(f"EMEA grew\n{written}."), [written])
            self.assertEqual(line_start, summary(N.check_numbers(f"EMEA grew {written}.", block)))
            self.assertEqual(line_start[0][2], "matched")

    def test_mid_line_figures(self):
        for written in ("99%", "5K", "5M", "5B", "3", "12"):
            with self.subTest(written=written):
                self.assertEqual(raws(f"EMEA grew {written}."), [written])

    def test_dates_ordinals_and_years(self):
        for text in ("EMEA grew\n2025.", "EMEA grew\n2026)", "EMEA grew\n3rd.", "EMEA grew\n21st)",
                     "EMEA grew\nMarch 5, 2026.", "EMEA grew\n2026-03-31.", "EMEA grew\n12/31/2025.",
                     "EMEA grew\nQ4.", "EMEA grew\nFY2026."):
            with self.subTest(text=text):
                self.assertEqual(raws(text), [])

    def test_lowercase_m_and_b_without_dollar_still_not_scanned(self):
        for text in ("EMEA grew\n5m.", "EMEA grew\n5b.", "EMEA grew\n5m)", "EMEA grew 5m.", "EMEA grew 5b."):
            with self.subTest(text=text):
                self.assertEqual(raws(text), [])
        for text in ("EMEA grew\n$5m.", "EMEA grew\n$5b."):
            with self.subTest(text=text):
                self.assertEqual(len(raws(text)), 1)

    def test_printed_mode_is_unaffected(self):
        # The list rule applies only to the narrative ("written"); DATA-block scanning is unchanged.
        block = N.parse_data_block("Regional summary:\n  - EMEA: 5M.\n  - APAC: 3.\n")
        self.assertEqual([[f.raw for f in ln.figures] for ln in block.lines], [["5M"], ["3"]])

    def test_deterministic(self):
        text = "EMEA grew\n99%.\nEMEA grew\n5M.\n3. EMEA grew 5K."
        self.assertEqual(summary(N.check_numbers(text, REAL_BLOCK)),
                         summary(N.check_numbers(text, REAL_BLOCK)))
        self.assertEqual(raws(text), ["99%", "5M", "5K"])


if __name__ == "__main__":
    unittest.main()
