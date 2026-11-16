"""
narrative_number_check.py -- D22 Builder Brief v3, Release 1, WP3.

The narrative number check as a PURE FUNCTION: no Streamlit, no session state,
no file or network access, no clock, no randomness. The same narrative text and
the same DATA block always give the same result (WP3-10).

What it implements (Handbook D22-C (7), D22-D (2)(3), D22-E (1)(2), D22-F (1),
D22-G (B1)(B3), D22-H (3)):

  * Every number in the narrative text that is not an exact match is a flag.
    There is no tolerance and no soft tier (WP3-4). "Hard", "soft" and "none"
    are internal words and appear in no string meant for the screen.
  * Matching is at LINE level (Option 2 with Option 4). For each number the
    check lists the lines of the DATA block whose printed figure equals it, at
    the precision written, and counts it as matched ONLY IF the nearest
    preceding line name (same sentence, or the previous sentence) belongs to
    EXACTLY ONE of those lines. Otherwise it is a flag. There is NO fall-back
    to any printed figure (WP3-3).
  * The accepted known misses (i) to (iii) (WP3-5) are NOT fixed: a current
    figure written where the prior figure of the same line belongs passes; a
    wrong number that is the right figure for the line named passes; a number
    written after the name of a different line passes when it equals that
    line's figure. build_test/test_number_check.py records each as an expected result.
  * Picking a line (Option 4) re-runs the check against that line (WP3-7).
  * An acceptance is keyed to (number as written, line), never to the display
    label "Flag n" (WP3-8).

The caller passes ONLY the narrative text (not the user's own notes, not the
prompt: WP3-1) and the locked DATA block of the rendered prompt
(extract_data_block() cuts it out of a rendered prompt).

DESIGN READINGS made where the Handbook/Brief are silent. Each is a Builder
reading, listed in the Return Report for Architect review; none adds product
scope and each is a small, isolated function:
  R1  A "line" is one printed line of the DATA block that carries a figure. Its
      NAME is the label before the last colon preceding its first figure (e.g.
      "Revenue", "Add-on: Forecasting"; the part after a colon in a label is an
      extra alias). Only a labelled line can be named; unlabelled note lines can
      still be candidate lines.
  R2  Names are matched case-insensitively on word tokens ("&" reads as "and").
      The nearest preceding name is the closest occurrence that ends before the
      number; overlapping occurrences resolve to the longer one.
  R3  Sign: a written number with an EXPLICIT sign must agree with the printed
      sign; an unsigned written number matches on magnitude (the direction
      is carried by words the check does not read). Constant EXPLICIT_SIGN_MUST_AGREE.
  R4  Kinds: "$" or "dollars/USD" = dollar; "%", "percent", "percentage point(s)",
      "pp", "pts" = percent; everything else = count. A K/M/B/million/billion
      suffix scales the value but does not by itself make it a dollar amount.
  R5  What is not a number (WP3-1): years, quarter and FY labels (letters glued to
      digits), dates and times, ordinals, list numbering, digits glued to letters
      (e.g. "D17", "2c"), leading-zero strings ("001"). Spelled-out numbers are
      not scanned.

ADDENDUM 1 (governance/builder_briefs/D22_Narrative_versioning_builder_brief_addendum_1.md,
revision 5, signed 2026-11-13; Principal rulings of 2026-11-15 noted with "ruling"):
  Part A  Budget lines. Lines under the heading BUDGET_SECTION_HEADING, up to (not
          including) the line that begins BUDGET_SECTION_END, are Budget lines; all
          others are actual lines (A-1). A number whose sentence (or, under A-2b, the
          previous sentence) holds a budget word (A-2) is matched against Budget lines
          only, for the figure and for the name; otherwise against actual lines only
          (A-3). Ruling 1: this holds even when the block has no Budget lines, so such
          a number is then flagged and can be cleared by a pick. Picks, candidate_lines
          and lines_of_kind use all lines (A-5b).
  Part B  Direction. An unsigned number that matched exactly one line (by name or
          by pick) and has an attached direction word (B-2, B-3, B-4) is flagged with
          REASON_DIRECTION when every equal printed figure on that line has the
          opposite sign (B-5), or with REASON_DIRECTION_WORDS_DISAGREE when a word
          before and a word after it disagree (B-6). These flags have flag_class
          "direction" and their own acceptance key (B-7, B-7a). Ruling 3: a B-6 flag
          carries no direction_word and no direction (both None). R3 still applies to
          numbers with an explicit sign and to numbers with no direction word.
"""

import hashlib
import re
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union

DOLLAR = "dollar"
PERCENT = "percent"
COUNT = "count"
KIND_WORDS = {DOLLAR: "dollar amount", PERCENT: "percentage", COUNT: "count"}

# R3: explicit written sign must agree with the printed sign.
EXPLICIT_SIGN_MUST_AGREE = True

# Markers that end the locked DATA block inside a rendered prompt: the three
# commentary blocks printed by commentary_workflow.build_narrative_commentary_section()
# and the TASK section. build_test/test_number_check.py asserts these strings still
# appear in what that function produces.
_DATA_END_MARKERS = (
    "\nFinance/CFO-Approved Explanations (accepted commentary",
    "\nFlagged Observations — Unresolved",
    "\nFlagged Observations — No Commentary Supplied This Close",
    "\n\nTASK:",
)

_SIGN_CHARS = "+-−–"

# ---------------------------------------------------------------------------
# Addendum 1 constants (each list is copied from the signed addendum)
# ---------------------------------------------------------------------------
# A-1 / A-6: the Budget vs Actual section of the DATA block, as rollups.py prints it.
BUDGET_SECTION_HEADING = "Budget vs Actual — flagged items only"
BUDGET_SECTION_END = "(Flag thresholds"
# A-2: whole words, case-insensitive ...
BUDGET_WORDS = frozenset({"budget", "budgets", "budgeted", "plan"})
# ... and the status words, case-sensitive, exactly as printed (E-9, Gate decision 8).
BUDGET_STATUS_WORDS = (("Major", "Miss"), ("Watch",))

# B-7: flag classes.
FLAG_CLASS_NUMBER = "number"
FLAG_CLASS_DIRECTION = "direction"
UP = "up"
DOWN = "down"
# B-2: words before the number ...
DIRECTION_WORDS_BEFORE = {
    **{w: UP for w in ("up", "rose", "risen", "grew", "grown", "increased", "climbed", "gained", "jumped",
                       "surged", "expanded")},
    **{w: DOWN for w in ("down", "fell", "fallen", "dropped", "declined", "decreased", "slipped", "dipped",
                         "shrank", "shrunk", "contracted", "reduced")},
}
# ... words after the number ...
DIRECTION_WORDS_AFTER = {"higher": UP, "lower": DOWN, "up": UP, "down": DOWN}
# ... and words after the number only when a budget word follows directly (E-8, Gate decision 5),
# optionally after one of BUDGET_WORD_LEAD_INS.
DIRECTION_WORDS_AFTER_WITH_BUDGET = {"below": DOWN, "under": DOWN, "above": UP, "over": UP}
BUDGET_WORD_LEAD_INS = frozenset({"the", "its", "our"})
# B-3: fillers allowed between a word before the number and the number (E-3) ...
DIRECTION_FILLERS = frozenset({"by", "about", "around", "roughly", "approximately", "nearly", "almost", "just", "some"})
# ... and the words that make a direction word describe a level instead.
LEVEL_WORDS = frozenset({"to", "from"})
# B-4: negations within three words before the direction word (E-4); "n't" forms are matched by suffix.
NEGATION_WORDS = frozenset({"not", "no", "never", "without"})
NEGATION_WINDOW = 3


# ---------------------------------------------------------------------------
# Number scanning (shared by the DATA block and the narrative)
# ---------------------------------------------------------------------------
_CORE_RE = re.compile(
    r"(?<![A-Za-z0-9_.,])"
    r"(?P<s1>[+\-−–])?"
    r"(?P<usd>(?:US)?\$)?"
    r"(?P<s2>[+\-−–])?"
    r"(?P<num>(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\.\d+)"
)
_PCT_TAIL = re.compile(r"[ \t]?(?:%|percent(?:age)?(?:[ \t]+points?)?\b|per[ \t]?cent\b|ppts?\b|pp\b|pts?\b)", re.I)
_SCALE_WORD_TAIL = re.compile(r"[ \t](?:thousand|million|billion|trillion)\b", re.I)
_SCALE_LETTER_TAIL = re.compile(r"(?:MM|mm|bn|mn|K|k|M|B|m|b)(?![A-Za-z0-9])")
_DOLLAR_WORD_TAIL = re.compile(r"[ \t](?:dollars?|USD)\b", re.I)
_ORDINAL_TAIL = re.compile(r"(?:st|nd|rd|th)(?![A-Za-z0-9])", re.I)
_SCALES = {
    "k": Decimal(10) ** 3, "thousand": Decimal(10) ** 3,
    "m": Decimal(10) ** 6, "mm": Decimal(10) ** 6, "mn": Decimal(10) ** 6, "million": Decimal(10) ** 6,
    "b": Decimal(10) ** 9, "bn": Decimal(10) ** 9, "billion": Decimal(10) ** 9,
    "trillion": Decimal(10) ** 12,
}

_MONTHS = (r"(?:January|February|March|April|May|June|July|August|September|October|November|December|"
           r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)")
_DATE_RES = [
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"),
    re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b"),
    re.compile(rf"\b{_MONTHS}\b\.?\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?\b"),
    re.compile(rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+(?:of\s+)?{_MONTHS}\b\.?(?:,?\s+\d{{4}})?\b"),
    re.compile(rf"\b{_MONTHS}\b\.?,?\s+\d{{4}}\b"),
]


@dataclass(frozen=True)
class _Token:
    """One scanned number, before it is turned into a written or printed figure."""
    start: int
    end: int
    raw: str
    kind: str
    text_value: Decimal      # magnitude exactly as typed, in the unit typed (no scale applied)
    decimals: int            # digits after the decimal point as typed
    unit_scale: Decimal      # 1, 1e3, 1e6 ...
    sign: Optional[int]      # +1 / -1 when an explicit sign was typed, else None
    is_plain_integer: bool


def _date_spans(text):
    spans = []
    for rx in _DATE_RES:
        for m in rx.finditer(text):
            spans.append((m.start(), m.end()))
    return spans


def _in_spans(pos_start, pos_end, spans):
    return any(s <= pos_start and pos_end <= e for s, e in spans)


_LIST_PREFIX_RE = re.compile(r"[ \t]*(?:(?:[#>*_\-+][ \t]*)|\*\*|__)*\(?")


def _is_list_numbering(text, tok):
    if tok.sign is not None or "$" in tok.raw or not tok.is_plain_integer or len(tok.raw.strip("+-")) > 3:
        return False
    line_start = text.rfind("\n", 0, tok.start) + 1
    if not _LIST_PREFIX_RE.fullmatch(text[line_start:tok.start]):
        return False
    after = text[tok.end:tok.end + 2]
    return len(after) >= 1 and after[0] in ".)" and (len(after) == 1 or after[1] in " \t*_\n")


def _scan(text, mode):
    """Yield _Token for every number in text. mode is 'written' (narrative:
    drops list numbering) or 'printed' (DATA block)."""
    out = []
    dates = _date_spans(text)
    for m in _CORE_RE.finditer(text):
        s1, usd, s2, num = m.group("s1"), m.group("usd"), m.group("s2"), m.group("num")
        start, num_end = m.start(), m.end()
        if _in_spans(start, num_end, dates):
            continue
        digits_only = num.replace(",", "")
        if len(digits_only.split(".")[0]) > 1 and digits_only.split(".")[0].startswith("0") and "." not in digits_only:
            continue                                    # R5: "001"
        rest = text[num_end:]
        sign_ch = s1 or s2
        sign = None
        if sign_ch:
            sign = +1 if sign_ch == "+" else -1
        is_plain_integer = ("." not in num and "," not in num)

        kind, unit_scale, end = COUNT, Decimal(1), num_end
        pm = _PCT_TAIL.match(rest)
        if pm:
            kind, end = PERCENT, num_end + pm.end()
        elif _ORDINAL_TAIL.match(rest) and is_plain_integer and not usd:
            continue                                    # R5: ordinal
        else:
            wm = _SCALE_WORD_TAIL.match(rest)
            lm = None if wm else _SCALE_LETTER_TAIL.match(rest)
            if wm:
                unit_scale = _SCALES[wm.group().strip().lower()]
                end = num_end + wm.end()
            elif lm:
                tok = lm.group()
                if tok in ("m", "b") and not usd:       # lowercase single letters only in a $ context
                    lm = None
                else:
                    unit_scale = _SCALES[tok.lower()]
                    end = num_end + lm.end()
            if not wm and not lm:
                if rest[:1].isalpha():
                    if re.match(r"x(?![A-Za-z0-9])", rest):
                        end = num_end + 1               # "2.3x": a count with a unit
                    else:
                        continue                        # R5: digits glued to letters ("2c", "4Q")
            if usd:
                kind = DOLLAR
            else:
                dm = _DOLLAR_WORD_TAIL.match(text[end:])
                if dm:
                    kind, end = DOLLAR, end + dm.end()
        if usd and kind != PERCENT:
            kind = DOLLAR
        decimals = len(num.split(".")[1]) if "." in num else 0
        if (mode == "written" or mode == "printed") and kind == COUNT and unit_scale == 1 and is_plain_integer \
                and not usd and sign is None and end == num_end and len(digits_only) == 4 \
                and 1900 <= int(digits_only) <= 2100:
            continue                                    # R5: a bare year
        tok = _Token(
            start=start, end=end, raw=text[start:end], kind=kind,
            text_value=Decimal(digits_only), decimals=decimals, unit_scale=unit_scale,
            sign=sign, is_plain_integer=is_plain_integer,
        )
        if mode == "written" and _is_list_numbering(text, tok):
            continue                                    # R5: list numbering
        out.append(tok)
    return out


# ---------------------------------------------------------------------------
# Printed figures and lines of the DATA block
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PrintedFigure:
    kind: str
    abs_value: Decimal        # |value| in base units (unit scale applied)
    sign: int                 # -1, 0 (zero) or +1
    decimals: int
    raw: str


@dataclass(frozen=True)
class DataLine:
    line_id: str
    index: int
    section: str
    label: Optional[str]
    text: str
    aliases: Tuple[Tuple[str, ...], ...]
    figures: Tuple[PrintedFigure, ...]
    is_budget: bool = False   # Addendum 1 A-1: a line of the Budget vs Actual section

    def figures_of_kind(self, kind):
        return tuple(f for f in self.figures if f.kind == kind)


@dataclass(frozen=True)
class LineRef:
    """A line as a flag shows it: where it is, what it is called, and its
    figures of the one kind that matters (printed form, in printed order)."""
    line_id: str
    section: str
    label: Optional[str]
    figures: Tuple[str, ...]


@dataclass(frozen=True)
class DataBlock:
    lines: Tuple[DataLine, ...]
    by_id: Mapping[str, DataLine]
    alias_lines: Mapping[Tuple[str, ...], Tuple[str, ...]]   # alias tokens -> line ids (DATA order)
    max_alias_len: int
    # Addendum 1 A-3: the same index split by pool (Budget lines / actual lines).
    budget_alias_lines: Mapping[Tuple[str, ...], Tuple[str, ...]] = field(default_factory=dict)
    actual_alias_lines: Mapping[Tuple[str, ...], Tuple[str, ...]] = field(default_factory=dict)

    @property
    def budget_lines(self):
        return tuple(ln for ln in self.lines if ln.is_budget)

    def line_ref(self, line_id, kind):
        ln = self.by_id[line_id]
        return LineRef(ln.line_id, ln.section, ln.label, tuple(f.raw for f in ln.figures_of_kind(kind)))


def extract_data_block(rendered_prompt: str) -> str:
    """Cut the locked DATA block out of a rendered user prompt: everything after
    the line 'DATA:' up to the first commentary block or the TASK section. The
    commentary blocks are separate locked blocks and are not close figures."""
    marker = "\nDATA:\n"
    i = rendered_prompt.find(marker)
    if i < 0:
        raise ValueError("no 'DATA:' section in the rendered prompt")
    start = i + len(marker)
    ends = [j for j in (rendered_prompt.find(m, start) for m in _DATA_END_MARKERS) if j >= 0]
    end = min(ends) if ends else len(rendered_prompt)
    return rendered_prompt[start:end].rstrip()


_TOKEN_RE = re.compile(r"[A-Za-z0-9]+|&")


def _name_tokens(text):
    """Normalised word tokens of a name or a stretch of narrative: lower case,
    '&' read as 'and', punctuation dropped."""
    return [("and" if t == "&" else t.lower()) for t in _TOKEN_RE.findall(text)]


def _printed_figure(tok: _Token) -> PrintedFigure:
    value = tok.text_value * tok.unit_scale
    sign = 0 if value == 0 else (-1 if tok.sign == -1 else +1)
    return PrintedFigure(tok.kind, value, sign, tok.decimals, tok.raw)


def _label_of(stripped, first_fig_start):
    head = stripped[:first_fig_start]
    if ":" not in head:
        return None
    label = head[: head.rfind(":")].strip().lstrip("-").strip().lstrip("(").strip()
    if not label or len(label) > 80 or not _name_tokens(label):
        return None
    return label


def parse_data_block(data_block: str) -> DataBlock:
    """Parse the DATA block into lines (R1). A line is a non-blank printed line
    that carries at least one figure. A non-indented, non-bulleted line with no
    figure is a section heading."""
    lines: List[DataLine] = []
    section = ""
    seen: Dict[str, int] = {}
    in_budget = False                                  # Addendum 1 A-1
    for i, raw_line in enumerate(data_block.split("\n")):
        stripped = raw_line.strip()
        if not stripped:
            continue
        line_is_budget = in_budget
        if stripped.startswith(BUDGET_SECTION_HEADING):
            in_budget, line_is_budget = True, False    # lines UNDER the heading are Budget lines
        elif stripped.startswith(BUDGET_SECTION_END):
            in_budget = line_is_budget = False         # the thresholds line itself is not a Budget line (A-6(b))
        toks = _scan(raw_line, "printed")
        if not toks:
            indent = len(raw_line) - len(raw_line.lstrip(" "))
            if indent == 0 and not stripped.startswith(("-", "(")):
                section = stripped.rstrip(":").strip()
            continue
        lead = len(raw_line) - len(raw_line.lstrip())
        label = _label_of(stripped, toks[0].start - lead)
        aliases: List[Tuple[str, ...]] = []
        if label:
            full = tuple(_name_tokens(label))
            aliases.append(full)
            if ":" in label:
                tail = tuple(_name_tokens(label.rsplit(":", 1)[1]))
                if tail and tail != full:
                    aliases.append(tail)
        base = hashlib.sha1(f"{section}\n{stripped}".encode("utf-8")).hexdigest()[:10]
        n = seen.get(base, 0)
        seen[base] = n + 1
        line_id = base if n == 0 else f"{base}-{n}"
        lines.append(DataLine(
            line_id=line_id, index=i, section=section, label=label, text=stripped,
            aliases=tuple(aliases), figures=tuple(_printed_figure(t) for t in toks), is_budget=line_is_budget,
        ))
    alias_lines: Dict[Tuple[str, ...], List[str]] = {}
    budget_alias: Dict[Tuple[str, ...], List[str]] = {}
    actual_alias: Dict[Tuple[str, ...], List[str]] = {}
    for ln in lines:
        for a in ln.aliases:
            alias_lines.setdefault(a, []).append(ln.line_id)
            (budget_alias if ln.is_budget else actual_alias).setdefault(a, []).append(ln.line_id)
    return DataBlock(
        lines=tuple(lines),
        by_id={ln.line_id: ln for ln in lines},
        alias_lines={a: tuple(ids) for a, ids in alias_lines.items()},
        max_alias_len=max((len(a) for a in alias_lines), default=0),
        budget_alias_lines={a: tuple(ids) for a, ids in budget_alias.items()},
        actual_alias_lines={a: tuple(ids) for a, ids in actual_alias.items()},
    )


# ---------------------------------------------------------------------------
# Written numbers
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class WrittenNumber:
    raw: str                  # exactly as written, e.g. "$4.0M", "+6.4%"
    start: int
    end: int
    kind: str
    occurrence: int           # 0-based index among numbers with the same raw text
    text_value: Decimal
    decimals: int
    unit_scale: Decimal
    sign: Optional[int]


def find_numbers(text: str) -> List[WrittenNumber]:
    """The numbers of a narrative that the check applies to (WP3-1, R5)."""
    seen: Dict[str, int] = {}
    out = []
    for t in _scan(text, "written"):
        n = seen.get(t.raw, 0)
        seen[t.raw] = n + 1
        out.append(WrittenNumber(t.raw, t.start, t.end, t.kind, n, t.text_value, t.decimals, t.unit_scale, t.sign))
    return out


_Q = {}


def _quantum(decimals):
    q = _Q.get(decimals)
    if q is None:
        q = _Q[decimals] = Decimal(1).scaleb(-decimals)
    return q


def figure_matches(number: WrittenNumber, fig: PrintedFigure) -> bool:
    """A written figure matches a printed figure when it equals it rounded to the
    precision written (D22-D (2)), with the same kind and, when the writer typed
    an explicit sign, the same sign (R3)."""
    if number.kind != fig.kind:
        return False
    rounded = (fig.abs_value / number.unit_scale).quantize(_quantum(number.decimals), rounding=ROUND_HALF_UP)
    if rounded != number.text_value:
        return False
    if EXPLICIT_SIGN_MUST_AGREE and number.sign is not None and fig.sign != 0 and number.text_value != 0:
        return number.sign == fig.sign
    return True


# ---------------------------------------------------------------------------
# Sentences and names
# ---------------------------------------------------------------------------
_ABBREV = {"vs", "e.g", "i.e", "approx", "inc", "co", "no", "fig", "est", "u.s", "etc"}
_TERM_RE = re.compile(r"[.!?]+[\"'”’)\]*_]*[ \t]+(?=[\"'“‘(\[*_#$\-+0-9A-Z])")


def _sentence_spans(text):
    spans = []
    for lm in re.finditer(r"[^\n]+", text):
        line, base = lm.group(), lm.start()
        cut = 0
        for tm in _TERM_RE.finditer(line):
            word = re.search(r"([A-Za-z.]+)$", line[:tm.start()])
            if word and word.group(1).lower().rstrip(".") in _ABBREV:
                continue
            spans.append((base + cut, base + tm.end()))
            cut = tm.end()
        spans.append((base + cut, base + len(line)))
    return spans


def _name_occurrences(sentence_text, offset, block: DataBlock, alias_lines=None):
    """All name occurrences in a sentence as (char_start, char_end, tuple(line ids)),
    overlaps resolved to the longer occurrence (R2). alias_lines selects a pool
    (Addendum 1 A-3); None means every line, as in Release 1."""
    alias_lines = block.alias_lines if alias_lines is None else alias_lines
    toks = [(m.group(), m.start(), m.end()) for m in _TOKEN_RE.finditer(sentence_text)]
    norm = [("and" if t == "&" else t.lower()) for t, _, _ in toks]
    found = []
    for n in range(min(block.max_alias_len, len(norm)), 0, -1):
        for i in range(0, len(norm) - n + 1):
            alias = tuple(norm[i:i + n])
            ids = alias_lines.get(alias)
            if ids:
                found.append((n, i, i + n - 1, toks[i][1] + offset, toks[i + n - 1][2] + offset, ids))
    found.sort(key=lambda f: (-f[0], f[1]))
    taken = []
    used = set()
    for n, i, j, cs, ce, ids in found:
        if any(k in used for k in range(i, j + 1)):
            continue
        used.update(range(i, j + 1))
        taken.append((cs, ce, ids))
    taken.sort()
    return taken


def _nearest_preceding_name(number: WrittenNumber, text, sentences, block: DataBlock, alias_lines=None):
    """(char_start, char_end, line ids) of the nearest line name before the
    number, in the same sentence, else in the previous sentence; None if neither
    holds one. alias_lines selects a pool (Addendum 1 A-3); None = every line."""
    si = next((k for k, (s, e) in enumerate(sentences) if s <= number.start < e), None)
    if si is None:
        return None
    s, e = sentences[si]
    in_sentence = [o for o in _name_occurrences(text[s:number.start], s, block, alias_lines)]
    if in_sentence:
        return max(in_sentence, key=lambda o: o[1])
    if si > 0:
        ps, pe = sentences[si - 1]
        prev = _name_occurrences(text[ps:pe], ps, block, alias_lines)
        if prev:
            return max(prev, key=lambda o: o[1])
    return None


# ---------------------------------------------------------------------------
# Addendum 1 Part A: budget words and the pool a number is matched in
# ---------------------------------------------------------------------------
def _has_budget_word(text) -> bool:
    """A-2: a budget word, found with the same tokenizer as the name matching.
    BUDGET_WORDS case-insensitive; BUDGET_STATUS_WORDS case-sensitive, as printed."""
    raw = [t for t in _TOKEN_RE.findall(text) if t != "&"]
    for i, t in enumerate(raw):
        if t.lower() in BUDGET_WORDS:
            return True
        for phrase in BUDGET_STATUS_WORDS:
            if tuple(raw[i:i + len(phrase)]) == phrase:
                return True
    return False


def _sentence_index(number: WrittenNumber, sentences):
    return next((k for k, (s, e) in enumerate(sentences) if s <= number.start < e), None)


def _uses_budget_pool(number: WrittenNumber, text, sentences, block: DataBlock) -> bool:
    """A-2b, A-3: True when the number's own whole sentence holds a budget word,
    or when that sentence holds no line name (of any pool) before the number and
    the previous sentence holds a budget word."""
    si = _sentence_index(number, sentences)
    if si is None:
        return False
    s, e = sentences[si]
    if _has_budget_word(text[s:e]):
        return True
    if si > 0 and not _name_occurrences(text[s:number.start], s, block):
        ps, pe = sentences[si - 1]
        return _has_budget_word(text[ps:pe])
    return False


# ---------------------------------------------------------------------------
# Addendum 1 Part B: direction words
# ---------------------------------------------------------------------------
_WORD_RE = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)*")


def _words(text, offset=0):
    return [(m.group(), m.start() + offset, m.end() + offset) for m in _WORD_RE.finditer(text)]


def _is_negated(text, sentence_start, word_start) -> bool:
    """B-4: a negation within NEGATION_WINDOW words before the direction word, in
    the same sentence."""
    before = _words(text[sentence_start:word_start])[-NEGATION_WINDOW:]
    for w, _, _ in before:
        lw = w.lower().replace("’", "'")
        if lw in NEGATION_WORDS or lw.endswith("n't"):
            return True
    return False


def _gap_is_space(text, a, b) -> bool:
    return a <= b and text[a:b].strip(" \t") == "" and "\n" not in text[a:b]


def _word_before_number(number: WrittenNumber, text, s):
    """B-3: a word of DIRECTION_WORDS_BEFORE, then optional fillers, then the
    number, with nothing but spaces between. Returns (word, direction, start) or None."""
    words = _words(text[s:number.start], s)
    k = len(words) - 1
    if k < 0 or not _gap_is_space(text, words[k][2], number.start):
        return None
    while k >= 0 and words[k][0].lower() in DIRECTION_FILLERS:
        if k == 0 or not _gap_is_space(text, words[k - 1][2], words[k][1]):
            return None
        k -= 1
    w, ws, _ = words[k]
    d = DIRECTION_WORDS_BEFORE.get(w.lower())
    return (w, d, ws) if d else None


def _word_after_number(number: WrittenNumber, text, e):
    """B-3: the number with its unit, then a word of DIRECTION_WORDS_AFTER directly,
    not followed (after fillers) by "to" or "from"; or a word of
    DIRECTION_WORDS_AFTER_WITH_BUDGET followed directly (optionally after "the",
    "its" or "our") by a budget word (E-8). Returns (word, direction, start) or None."""
    words = _words(text[number.end:e], number.end)
    if not words or not _gap_is_space(text, number.end, words[0][1]):
        return None
    w, ws, we = words[0]
    lw = w.lower()
    rest = words[1:]

    def chained(seq, prev_end):
        out = []
        for t in seq:
            if not _gap_is_space(text, prev_end, t[1]):
                break
            out.append(t)
            prev_end = t[2]
        return out

    following = chained(rest, we)
    if lw in DIRECTION_WORDS_AFTER:
        k = 0
        while k < len(following) and following[k][0].lower() in DIRECTION_FILLERS:
            k += 1
        if k < len(following) and following[k][0].lower() in LEVEL_WORDS:
            return None
        return (w, DIRECTION_WORDS_AFTER[lw], ws)
    if lw in DIRECTION_WORDS_AFTER_WITH_BUDGET:
        k = 0
        if k < len(following) and following[k][0].lower() in BUDGET_WORD_LEAD_INS:
            k += 1
        if k < len(following):
            tail_start = following[k][1]
            tail_end = following[k + 1][2] if k + 1 < len(following) else following[k][2]
            if _starts_with_budget_word(text[tail_start:tail_end]):
                return (w, DIRECTION_WORDS_AFTER_WITH_BUDGET[lw], ws)
    return None


def _starts_with_budget_word(text) -> bool:
    raw = [t for t in _TOKEN_RE.findall(text) if t != "&"]
    if not raw:
        return False
    if raw[0].lower() in BUDGET_WORDS:
        return True
    return any(tuple(raw[:len(p)]) == p for p in BUDGET_STATUS_WORDS)


def _direction_verdict(number: WrittenNumber, text, sentences, line: DataLine):
    """B-1 to B-6 for a number that matched exactly one line. Returns None when
    there is nothing to flag, else (reason, direction_word, direction)."""
    if number.sign is not None:                                   # explicit sign: R3 only (B-1)
        return None
    si = _sentence_index(number, sentences)
    if si is None:
        return None
    s, e = sentences[si]
    attached = []
    for found in (_word_before_number(number, text, s), _word_after_number(number, text, e)):
        if found is not None and not _is_negated(text, s, found[2]):
            attached.append(found)
    if not attached:
        return None
    if len(attached) == 2 and attached[0][1] != attached[1][1]:   # B-6
        return (REASON_DIRECTION_WORDS_DISAGREE, None, None)    # ruling 3: no single word to carry
    word, direction = attached[0][0], attached[0][1]
    want = +1 if direction == UP else -1
    equal = [f for f in line.figures_of_kind(number.kind) if figure_matches(number, f) and f.sign != 0]
    if equal and all(f.sign == -want for f in equal):              # B-5, E-6
        return (REASON_DIRECTION, word, direction)
    return None


# ---------------------------------------------------------------------------
# The check
# ---------------------------------------------------------------------------
REASON_NO_NAME = "no line name before the number"
REASON_AMBIGUOUS = "the line named matches more than one line carrying this figure"
REASON_NAME_DOES_NOT_CARRY_IT = "the line named does not carry this figure"
REASON_NO_EQUAL_FIGURE = "no close figure equals this number"
REASON_PICK_MISMATCH = "the picked line does not carry this figure"
# Addendum 1 B-5, B-6, B-7a.
REASON_DIRECTION = "the direction word disagrees with the sign printed on the line"
REASON_DIRECTION_WORDS_DISAGREE = "the two direction words disagree"


@dataclass(frozen=True)
class Acceptance:
    """An acceptance as the store will hold it (WP3-8): who, when, the number as
    written and the line it was matched to or picked (None when the line could
    not be placed). Keyed by (number, line_id), never by the label 'Flag n'.
    Addendum 1 B-7: flag_class "direction" adds a third key element."""
    number: str
    line_id: Optional[str]
    name: str
    time: str
    flag_class: str = FLAG_CLASS_NUMBER

    @property
    def key(self):
        if self.flag_class == FLAG_CLASS_DIRECTION:
            return (self.number, self.line_id, FLAG_CLASS_DIRECTION)
        return (self.number, self.line_id)


@dataclass(frozen=True)
class Flag:
    """Everything a flag needs (WP3-6, WP3-7, WP3-8). Display text is the UI's
    job; this carries the data."""
    ordinal: int                          # 1-based position among all flags, for the label "Flag n" (display only)
    number: WrittenNumber
    kind: str
    kind_words: str                       # plain words for the figure kind
    reason: str                           # internal diagnosis, never shown as a tier
    placed: bool                          # False when the line could not be placed
    line: Optional[LineRef]               # the line when known (named uniquely, or picked)
    line_has_figure_of_kind: Optional[bool]  # False -> use plain wording instead of a figure
    candidate_lines: Tuple[LineRef, ...]  # lines whose printed figure equals the number
    lines_of_kind: Tuple[LineRef, ...]    # when not placed: every line carrying a figure of the kind
    picked_line_id: Optional[str]
    sentence_start: int                   # char span of the sentence, for the marker link
    sentence_end: int
    accepted: Optional[Acceptance]        # the acceptance that covers it, if any
    # Addendum 1 B-7, B-7a.
    flag_class: str = FLAG_CLASS_NUMBER   # "number" (Release 1 flags) or "direction"
    direction_word: Optional[str] = None  # the direction word as written (None for B-6, ruling 3)
    direction: Optional[str] = None       # "up" / "down" (None for B-6, ruling 3)

    @property
    def acceptance_key(self):
        """(number as written, line matched or picked or None): the key an
        acceptance must carry to cover this flag (WP3-8). A direction flag adds
        "direction" as a third element (Addendum 1 B-7)."""
        pair = (self.number.raw, self.line.line_id if self.line is not None else None)
        return pair + (FLAG_CLASS_DIRECTION,) if self.flag_class == FLAG_CLASS_DIRECTION else pair

    @property
    def is_open(self):
        return self.accepted is None


@dataclass(frozen=True)
class CheckedNumber:
    number: WrittenNumber
    status: str                           # "matched", "matched_by_pick" or "flagged"
    line_id: Optional[str]                # the line matched or picked, or the line the flag shows
    flag: Optional[Flag]


@dataclass(frozen=True)
class NumberCheckResult:
    numbers: Tuple[CheckedNumber, ...]
    flags: Tuple[Flag, ...]               # every flag, accepted or open, in text order

    @property
    def open_flags(self):
        return tuple(f for f in self.flags if f.is_open)

    @property
    def open_count(self):
        return len(self.open_flags)


PickKey = Tuple[str, int]   # (number as written, occurrence index among identical raw texts)


def check_numbers(
    narrative_text: str,
    data_block: Union[str, DataBlock],
    picks: Optional[Mapping[PickKey, str]] = None,
    acceptances: Optional[Iterable[Acceptance]] = None,
) -> NumberCheckResult:
    """Check every number of the narrative against the DATA block.

    picks: {(number as written, occurrence): line_id}. A pick re-runs the check
    against that line: equal clears the flag (status "matched_by_pick"), unequal
    leaves it open showing that line's figures (WP3-7). An unknown line_id is
    ignored. acceptances: Acceptance records; a flag is covered only when an
    acceptance carries the same (number as written, line) key (WP3-8). The check
    always runs on the text it is given, so an edit is re-checked in full and
    an acceptance holds only while its number and line stand."""
    block = data_block if isinstance(data_block, DataBlock) else parse_data_block(data_block)
    picks = dict(picks or {})
    accept_by_key: Dict[tuple, Acceptance] = {}
    for a in (acceptances or ()):
        accept_by_key.setdefault(a.key, a)

    sentences = _sentence_spans(narrative_text)
    checked: List[CheckedNumber] = []
    flags: List[Flag] = []

    for number in find_numbers(narrative_text):
        kind = number.kind
        # Every line whose figure equals the number: used by picks and listed as
        # candidates, whatever the pool (Addendum 1 A-5b).
        equal_ids = tuple(
            ln.line_id for ln in block.lines
            if any(figure_matches(number, f) for f in ln.figures_of_kind(kind))
        )
        pick_id = picks.get((number.raw, number.occurrence))
        if pick_id is not None and pick_id not in block.by_id:
            pick_id = None
        si = next((k for k, (s, e) in enumerate(sentences) if s <= number.start < e), 0)
        s_start, s_end = sentences[si] if sentences else (0, len(narrative_text))

        line: Optional[LineRef] = None
        placed = False
        matched_id: Optional[str] = None
        status = None

        if pick_id is not None:                                         # Option 4: re-run against the picked line
            if pick_id in equal_ids:
                matched_id, status = pick_id, "matched_by_pick"
            else:
                reason = REASON_PICK_MISMATCH
                line, placed = block.line_ref(pick_id, kind), True
        else:
            # Addendum 1 A-3: the automatic match uses one pool only, for the figure and the name.
            budget_pool = _uses_budget_pool(number, narrative_text, sentences, block)
            pool_alias = block.budget_alias_lines if budget_pool else block.actual_alias_lines
            equal_pool = tuple(i for i in equal_ids if block.by_id[i].is_budget == budget_pool)
            name = _nearest_preceding_name(number, narrative_text, sentences, block, pool_alias)
            name_ids = name[2] if name else ()
            overlap = [i for i in equal_pool if i in name_ids]
            if len(overlap) == 1:                                       # Option 2: matched
                matched_id, status = overlap[0], "matched"
            else:
                if name is None:
                    reason = REASON_NO_NAME
                elif len(overlap) > 1:
                    reason = REASON_AMBIGUOUS
                elif equal_pool:
                    reason = REASON_NAME_DOES_NOT_CARRY_IT
                else:
                    reason = REASON_NO_EQUAL_FIGURE
                # The line is "known" only when the name belongs to exactly one line.
                if name is not None and len(name_ids) == 1:
                    line, placed = block.line_ref(name_ids[0], kind), True

        flag_class, direction_word, direction = FLAG_CLASS_NUMBER, None, None
        if matched_id is not None:
            # Addendum 1 Part B: a matched number (by name or by pick) is direction-checked.
            verdict = _direction_verdict(number, narrative_text, sentences, block.by_id[matched_id])
            if verdict is None:
                checked.append(CheckedNumber(number, status, matched_id, None))
                continue
            reason, direction_word, direction = verdict
            flag_class = FLAG_CLASS_DIRECTION
            line, placed = block.line_ref(matched_id, kind), True

        has_fig = (len(line.figures) > 0) if line is not None else None
        candidates = tuple(block.line_ref(i, kind) for i in equal_ids)
        of_kind = ()
        if not placed:
            of_kind = tuple(
                block.line_ref(ln.line_id, kind) for ln in block.lines if ln.figures_of_kind(kind)
            )
        key = (number.raw, line.line_id if line is not None else None)
        if flag_class == FLAG_CLASS_DIRECTION:
            key = key + (FLAG_CLASS_DIRECTION,)
        flag = Flag(
            ordinal=len(flags) + 1, number=number, kind=kind, kind_words=KIND_WORDS[kind], reason=reason,
            placed=placed, line=line, line_has_figure_of_kind=has_fig, candidate_lines=candidates,
            lines_of_kind=of_kind, picked_line_id=pick_id, sentence_start=s_start, sentence_end=s_end,
            accepted=accept_by_key.get(key), flag_class=flag_class,
            direction_word=direction_word, direction=direction,
        )
        flags.append(flag)
        checked.append(CheckedNumber(number, "flagged", line.line_id if line is not None else None, flag))

    return NumberCheckResult(tuple(checked), tuple(flags))
