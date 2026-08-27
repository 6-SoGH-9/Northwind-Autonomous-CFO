"""
Commentary Workflow — Phases 4-6 (D13 scope)

Implements:
  - Phase 4: Commentary Matching        (Brief Section B)
  - Phase 5: Finance Collaboration       (Brief Section D — reinterpreted:
             draft is for the finance/CFO user's own reference, never sent)
  - Phase 6: Explanation Validation      (Brief Section C)
  - Commentary Record / version model    (Brief Section F)
  - Executive-output handoff helper      (Brief Section G)

Governs: governance/builder_briefs/phase4_6_commentary_validation_brief_v5.md
  (v5 supersedes v4; v4's Sections C, D, F, H, J are unchanged and v4's
  implementation of them is not reopened or redone here — see v5 Revision
  Note. v5 adds: Commentary.xlsx becomes optional (Section A/B), and Section
  G's Phase 7 handoff is rewritten from a binary framing into the three
  required states below.)
Constrained by: D13 (Machine Recommends, Human Decides) — Planned. This
module never sets, implies, or influences close approval/rejection status.

WHAT THIS MODULE IS
--------------------
Mostly a pure service, in the same spirit as close_validation.py: matching
and validation are pure functions over already-loaded data structures, with
zero Streamlit/dashboard calls and zero cause-invention beyond what the
bounded evidence package supports. The one I/O function is
load_commentary_workbook(), which reads the fixed Commentary.xlsx contract
(Brief Section B) — analogous to close_history.py doing I/O while
close_validation.py stays pure; this module follows the same split.

WHAT THIS MODULE IS NOT
------------------------
- Not a redesign of D10/D11/D12/D14. It consumes close_validation.py's
  already-Verified Phase2Result/Phase3Result and D14's Department x Category
  breakdown as read-only inputs.
- Not an approval mechanism. Phase 6's assessments (Supported / Contradicted
  / Insufficient) are recommendations for a human to read, never a close
  status. Phase 5 never creates, addresses, or sends anything to the
  Controller — there is no send/transmit path anywhere in this module.
- Not an LLM-backed validator. Given that every other production decision
  engine in this project (Phase 2, Phase 3) is deterministic and testable
  without any external API dependency, and that narrative generation
  (Phase 7, the one place this project *does* call an LLM) already has an
  explicitly-flagged, still-undecided fallback behavior when no API key is
  present (Handbook Section 10), Phase 6 here is implemented as a
  deterministic, keyword/rule-based classifier over the bounded evidence
  package. This is a design choice, not dictated by the Brief, and is
  flagged as an Architect review item in the Return Report: an LLM-backed
  Phase 6 (e.g. reusing rollups.call_claude_narrative's API pattern) is a
  plausible alternative implementation, deferred rather than decided here,
  to avoid making the finance/CFO review path hard-depend on
  ANTHROPIC_API_KEY being present.
"""

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

import pandas as pd

# ---------------------------------------------------------------------------
# Section B — fixed commentary-file contract
# ---------------------------------------------------------------------------
COMMENTARY_SHEET_NAME = "Commentary"
COMMENTARY_REQUIRED_COLUMNS = ("Commentary_ID", "Commentary_Text")

# Section C — assessment labels (structured, not free text, so callers can
# branch on them without string-matching a human-readable message — same
# convention close_validation.py uses for STATUS_OK / STATUS_NOT_APPLICABLE).
SUPPORTED = "Supported"
CONTRADICTED = "Contradicted"
INSUFFICIENT = "Insufficient / Requires Clarification"

# Version-model source tags (Section F)
SOURCE_ORIGINAL_IMPORT = "original_import"
SOURCE_USER_REVISION = "user_revision"


class CommentaryFileError(ValueError):
    """Raised when the imported workbook does not match the fixed
    Commentary.xlsx contract (Brief Section B). Builder must not invent an
    alternate accepted shape — this is intentionally strict."""


# ---------------------------------------------------------------------------
# Commentary intake (I/O — Section B)
# ---------------------------------------------------------------------------
@dataclass
class CommentaryEntry:
    commentary_id: str
    text: str


def load_commentary_workbook(path_or_buffer):
    """Load Commentary.xlsx per the fixed contract: one sheet named
    'Commentary', with 'Commentary_ID' and 'Commentary_Text' columns.
    Blank commentary rows are dropped — the Brief states they 'are not
    valid input entries and must not be treated as commentary.'

    Raises CommentaryFileError on any contract violation (wrong sheet name,
    missing column, unreadable file) rather than guessing at an alternate
    shape. `path_or_buffer` may be a filesystem path or a file-like object
    (e.g. Streamlit's UploadedFile), since pandas.ExcelFile accepts both.
    """
    try:
        xl = pd.ExcelFile(path_or_buffer)
    except Exception as e:
        raise CommentaryFileError(f"Could not open commentary workbook: {e}")

    if COMMENTARY_SHEET_NAME not in xl.sheet_names:
        raise CommentaryFileError(
            f"Commentary workbook must contain a sheet named '{COMMENTARY_SHEET_NAME}'; "
            f"found sheets: {xl.sheet_names}"
        )

    df = xl.parse(COMMENTARY_SHEET_NAME)
    missing = [c for c in COMMENTARY_REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise CommentaryFileError(
            f"Commentary sheet missing required column(s): {missing}. "
            f"Required: {list(COMMENTARY_REQUIRED_COLUMNS)}"
        )

    entries = []
    for _, row in df.iterrows():
        cid, text = row["Commentary_ID"], row["Commentary_Text"]
        if pd.isna(cid) or pd.isna(text) or str(text).strip() == "":
            continue
        entries.append(CommentaryEntry(commentary_id=str(cid).strip(), text=str(text).strip()))
    return entries


# ---------------------------------------------------------------------------
# Observation register + stable IDs
#
# close_validation.py's Phase2Result/Phase3Result carry no persistent ID —
# the dashboard has, until now, rebuilt an unkeyed register purely for
# display (Handbook IA #8: "format only — Phase 4-6 not built this cycle").
# Phase 4 needs a STABLE key to match commentary against and a Commentary
# Record to be keyed by. This wrapper adds that ID without touching any D11
# detection logic — Phase2Result/Phase3Result themselves are unmodified.
# ---------------------------------------------------------------------------
def make_observation_id(detected_by, period, department, category):
    """Deterministic: identical (detected_by, period, department, category)
    always yields the same ID, so re-running Phase 2/3 against the same
    close doesn't shuffle IDs a Commentary Record is keyed against."""
    basis = f"{detected_by}|{period}|{department}|{category}"
    return "OBS-" + hashlib.sha1(basis.encode("utf-8")).hexdigest()[:10]


OBSERVATION_REGISTER_COLUMNS = [
    "Observation ID", "Detected By", "Period", "Type", "Department", "Category",
    "Before ($)", "After ($)", "Delta ($)", "Threshold Crossed",
]


def build_observation_register(phase2_result, phase3_result, fmt_period_label, cv_status_ok):
    """Same register content the dashboard already renders (Handbook IA #8),
    plus a stable 'Observation ID' column. Purely a presentation/keying
    wrapper around close_validation.py's already-Verified results — no D11
    logic is reimplemented or changed here.

    cv_status_ok: close_validation.STATUS_OK, passed in by the caller so
    this module has zero import-time coupling to close_validation.py
    (keeps this module trivially unit-testable, same rationale
    close_validation.py itself documents for its own interface choices).
    """
    rows = []
    if phase2_result.status == cv_status_ok:
        for _, r in phase2_result.flagged_rows.iterrows():
            period_label = r["Date"].strftime("%b %Y") if pd.notna(r["Date"]) else ""
            obs_id = make_observation_id("Phase 2", period_label, r["Department"], r["Category"])
            rows.append({
                "Observation ID": obs_id,
                "Detected By": "Phase 2 (Deterministic Validation)",
                "Period": period_label,
                "Type": "Historical Revision",
                "Department": r["Department"], "Category": r["Category"],
                "Before ($)": r["Amount ($)_prior"], "After ($)": r["Amount ($)_current"],
                "Delta ($)": r["Diff ($)"],
                "Threshold Crossed": None,
            })
    if phase3_result.status == cv_status_ok:
        for _, r in phase3_result.flagged_rows.iterrows():
            # Period representation (investigated per builder_task_final,
            # "Observation Register Period Semantics" independent
            # investigation): this line intentionally applies
            # fmt_period_label() to the raw "Fiscal Quarter" value BEFORE
            # storing it as this register's canonical "Period" field and
            # passing it into make_observation_id().
            #
            # This is CORRECT, not a defect, and must not be "fixed" to
            # store the raw value instead without a fresh investigation
            # reaching a different evidence-based conclusion than the one
            # already on record. Evidence (see build_test/
            # period_semantics_investigation.py and the governing Return
            # Report):
            #   1. The source dataset (Northwind_Sample_Dataset.xlsx)
            #      contains no "Fiscal Quarter" value at all -- only
            #      monthly Date columns. "Fiscal Quarter" and its "Q# FY####"
            #      shape are entirely derived (rollups.py's add_fiscal_cols),
            #      not a source-of-truth format.
            #   2. project_handbook.md's D14 close-out (Verified) already
            #      settled the product-wide convention: rendered labels are
            #      "Q4 2026", not "Q4 FY2026" -- this line's use of
            #      fmt_period_label() keeps the register consistent with
            #      that already-settled, Verified convention.
            #   3. _find_period_terms() (below) is a plain, format-agnostic
            #      substring matcher -- it matches whatever the register's
            #      own Period column currently contains, whatever format
            #      that is. Commentary written in the D14 display
            #      convention ("Q2 2025") matches correctly against this
            #      register today; commentary written in the older, raw
            #      "Q# FY####" convention does not, and correctly falls
            #      back to "ambiguous, no period reference to disambiguate"
            #      rather than a silent wrong match.
            #   4. A prior, informal, unpromoted local change that stored
            #      the raw Fiscal Quarter value instead was found, on
            #      independent re-investigation, to have been based on an
            #      incorrect premise (assuming commentary using the OLDER
            #      "FY"-inclusive wording was the thing that needed to
            #      match, rather than recognizing that wording predates
            #      the settled D14 convention). That change is NOT applied
            #      here. If commentary text still uses the older
            #      "Q# FY####" wording, the correct fix is to update that
            #      commentary text to the current convention -- not to
            #      move this register away from a Verified, product-wide
            #      display standard.
            period_label = fmt_period_label(r["Fiscal Quarter"])
            obs_id = make_observation_id("Phase 3", period_label, r["Department"], r["Category"])
            rows.append({
                "Observation ID": obs_id,
                "Detected By": "Phase 3 (Plausibility Review)",
                "Period": period_label,
                "Type": "Plausibility Anomaly",
                "Department": r["Department"], "Category": r["Category"],
                "Before ($)": r["Prior ($)"], "After ($)": r["Amount ($)"],
                "Delta ($)": r["Amount ($)"] - r["Prior ($)"],
                "Threshold Crossed": f"|QoQ %| > {phase3_result.threshold:.0%}",
            })
    return pd.DataFrame(rows, columns=OBSERVATION_REGISTER_COLUMNS)


# ---------------------------------------------------------------------------
# Phase 4 — Commentary Matching (Section B; deterministic-pass corrections
# and Value signal added by phase4_semantic_reconciliation_brief_v2.md
# Section 1; exclusivity added Section 2; semantic reconciliation added
# Section 3, all below)
# ---------------------------------------------------------------------------
@dataclass
class MatchResult:
    commentary_id: str
    text: str
    matched_observation_id: Optional[str]
    matched: bool
    match_basis: str
    # Added Brief v2 -- which resolution path produced this result:
    # "deterministic" | "semantic" | "unresolved". Defaulted so every
    # existing positional/keyword construction site (all inside this
    # module) and every external reader (build_test/commentary_workflow_
    # demo.py, the dashboard) that only reads matched/matched_observation_id/
    # match_basis by name keeps working unmodified.
    method: str = "deterministic"


# Generic synonym/abbreviation vocabulary for THIS dataset's fixed
# Department/Category values (Customer Success, G&A, R&D, Sales & Marketing;
# Other Opex, Salaries & Benefits, Software & Tools). Not tuned to any
# specific commentary wording — these are common real-world ways an analyst
# would refer to these same four departments / three categories, independent
# of what any particular UAT case says (Validation Independence: this
# vocabulary was written before seeing the principal's UAT commentary set).
DEPARTMENT_SYNONYMS = {
    "sales and marketing": "Sales & Marketing", "sales & marketing": "Sales & Marketing",
    "s&m": "Sales & Marketing", "snm": "Sales & Marketing", "marketing": "Sales & Marketing",
    "customer success": "Customer Success", "cs team": "Customer Success", "support team": "Customer Success",
    "general and administrative": "G&A", "general & administrative": "G&A", "g and a": "G&A",
    "research and development": "R&D", "research & development": "R&D", "engineering": "R&D",
    "r and d": "R&D",
}
CATEGORY_SYNONYMS = {
    "salaries and benefits": "Salaries & Benefits", "salaries & benefits": "Salaries & Benefits",
    "payroll": "Salaries & Benefits", "compensation": "Salaries & Benefits", "salaries": "Salaries & Benefits",
    # Deliberately EXCLUDES "headcount"/"hiring" -- those describe a possible
    # CAUSE of a Salaries & Benefits movement (and are also Phase 6 claim-
    # type vocabulary, see CHECKABLE_CLAIM_TYPES below), not a reference to
    # the category itself. A commentary can discuss headcount/hiring in
    # connection with Software & Tools or Other Opex too (e.g. new-hire
    # equipment/licenses), so treating those words as Salaries & Benefits
    # synonyms produced false-positive category ambiguity.
    "software and tools": "Software & Tools", "software & tools": "Software & Tools",
    "software": "Software & Tools", "saas": "Software & Tools", "licenses": "Software & Tools",
    "subscriptions": "Software & Tools", "tooling": "Software & Tools",
    "other opex": "Other Opex", "travel": "Other Opex", "miscellaneous": "Other Opex", "misc": "Other Opex",
}


def _find_canonical_terms(text, synonym_map, canonical_values):
    """Return the set of canonical values (real Department/Category names)
    that `text` refers to — explicitly (the exact name appears) or via a
    known synonym/abbreviation. Longer synonym phrases are checked first so
    e.g. 'sales and marketing' isn't lost to a shorter false match."""
    lower = text.lower()
    found = set()
    for canon in canonical_values:
        if canon.lower() in lower:
            found.add(canon)
    for phrase in sorted(synonym_map, key=len, reverse=True):
        if phrase in lower:
            found.add(synonym_map[phrase])
    return found


def _find_period_terms(text, period_labels):
    lower = text.lower()
    return {label for label in period_labels if label and label.lower() in lower}


# Recognizes a single stated monetary figure, e.g. "$45,000", "$45,000.00",
# "-$12,000". Deliberately conservative (Brief v2 Section 1: "Builder's
# implementation discretion on parsing, not on whether the check happens") --
# this does not attempt to parse "forty five thousand dollars" or bare
# numbers with no "$", since an unmarked number is too likely to be
# something else (a date, a headcount, a percentage) to treat as a stated
# financial value.
_VALUE_PATTERN = re.compile(r"(-)?\$\s?([\d,]+(?:\.\d+)?)")


def _parse_stated_value(text):
    """Return the first $-marked figure in `text` as a float, or None if no
    such figure is present. Sign is taken from a leading '-' immediately
    before the '$' (e.g. '-$12,000'); dollar amounts are otherwise
    magnitude-only, since commentary text describes both increases and
    decreases in plain language ('fell by $12,000') rather than always
    signing the figure itself -- magnitude comparison against the
    observation's Delta/Before/After is handled in `_value_consistent`."""
    m = _VALUE_PATTERN.search(text)
    if not m:
        return None
    digits = m.group(2).replace(",", "")
    if not digits:
        return None
    try:
        value = float(digits)
    except ValueError:
        return None
    return -value if m.group(1) else value


def _value_consistent(stated_value, obs_row, tolerance=1.0):
    """Brief v2 Section 1, "Value as a matching signal". Compares the
    commentary's stated figure against whichever of the candidate
    observation's Delta ($) / Before ($) / After ($) it most plausibly
    refers to.

    Returns:
      - None  if stated_value is None (no figure was stated -- no
        comparison possible, and the caller must not treat this as either
        support or conflict).
      - True  if stated_value's magnitude is within `tolerance` of at least
        one of Delta/Before/After's magnitude.
      - False if a figure was stated and it matches none of the three --
        this is "evidence against th[e] match, not proof of a different
        one" (Brief v2 Section 1); the caller decides what to do with it.

    Magnitude-only comparison (abs() on both sides): commentary states
    figures in plain language ("costs rose by $50,000") without necessarily
    matching this dataset's Delta ($) sign convention, so a magnitude match
    is the correct check here -- direction is not part of what Section 1
    asks this signal to verify.
    """
    if stated_value is None:
        return None
    candidates = []
    for field_name in ("Delta ($)", "Before ($)", "After ($)"):
        v = obs_row.get(field_name)
        if v is not None and pd.notna(v):
            candidates.append(v)
    if not candidates:
        return None
    return any(abs(abs(stated_value) - abs(c)) <= tolerance for c in candidates)


def match_commentary_entries(entries, observation_register):
    """Phase 4 — deterministic pass (Brief v2 Section 1). For each
    CommentaryEntry, resolve the single best-supported observation, or
    return 'no confident match'.

    Scoring is deliberately conservative: a match requires an unambiguous
    Department reference AND an unambiguous Category reference (explicit
    name or known synonym). Department or Category alone is never
    sufficient — a forced match with weak support is a defect, not a
    feature. A stated Value, when present, is checked against the
    candidate's Delta/Before/After (Section 1) -- a conflicting value falls
    through to no confident match rather than being silently ignored.

    Period handling (Section 1, corrected defect): when the commentary
    explicitly states a period, the candidate set is ALWAYS narrowed to that
    period -- including to zero -- never left as an unnarrowed, wrong-period
    candidate. A stated period matching none of the Department/Category
    candidates is therefore no confident match, full stop.

    This function performs ONLY the deterministic pass. Exclusivity
    (Section 2) and gated semantic reconciliation (Section 3) are applied
    afterward by resolve_commentary_matches(), which wraps this function --
    call that, not this one, for the full Phase 4 pipeline.
    """
    if observation_register.empty:
        departments, categories, periods = [], [], []
    else:
        departments = sorted(observation_register["Department"].unique())
        categories = sorted(observation_register["Category"].unique())
        periods = sorted(observation_register["Period"].unique())

    results = []
    for entry in entries:
        dept_hits = _find_canonical_terms(entry.text, DEPARTMENT_SYNONYMS, departments)
        cat_hits = _find_canonical_terms(entry.text, CATEGORY_SYNONYMS, categories)
        period_hits = _find_period_terms(entry.text, periods)
        stated_value = _parse_stated_value(entry.text)

        if not dept_hits or not cat_hits or len(dept_hits) > 1 or len(cat_hits) > 1:
            reason = ("no department/category reference found" if not (dept_hits or cat_hits)
                       else "ambiguous department/category reference (more than one candidate named)")
            results.append(MatchResult(entry.commentary_id, entry.text, None, False, reason))
            continue

        dept, cat = next(iter(dept_hits)), next(iter(cat_hits))
        candidates = observation_register[
            (observation_register["Department"] == dept) & (observation_register["Category"] == cat)
        ]
        if period_hits:
            # CORRECTED DEFECT (Brief v2 Section 1): always narrow, even to
            # empty -- never fall back to an unnarrowed, wrong-period
            # candidate just because narrowing produced zero rows.
            candidates = candidates[candidates["Period"].isin(period_hits)]

        if len(candidates) == 0:
            period_clause = f", Period in {sorted(period_hits)}" if period_hits else ""
            results.append(MatchResult(
                entry.commentary_id, entry.text, None, False,
                f"referenced {dept} / {cat}{period_clause} but no open observation exists for that combination",
            ))
        elif len(candidates) == 1:
            obs_row = candidates.iloc[0]
            value_check = _value_consistent(stated_value, obs_row)
            if value_check is False:
                results.append(MatchResult(
                    entry.commentary_id, entry.text, None, False,
                    f"referenced {dept} / {cat} but stated value (${stated_value:,.2f}) does not match this "
                    f"observation's Delta/Before/After (${obs_row['Delta ($)']:,.2f} / ${obs_row['Before ($)']:,.2f} "
                    f"/ ${obs_row['After ($)']:,.2f}) — no confident match",
                ))
                continue
            basis = f"matched on Department={dept}, Category={cat}"
            basis += f", Period in {sorted(period_hits)}" if period_hits else " (single open observation for this Department/Category)"
            if value_check is True:
                basis += f", Value ${stated_value:,.2f} consistent"
            results.append(MatchResult(
                entry.commentary_id, entry.text, obs_row["Observation ID"], True, basis,
            ))
        else:
            # Multiple candidates remain after Department/Category(/Period)
            # narrowing. A stated Value may still disambiguate them (Section
            # 1: Value is a matching signal, not limited to the
            # single-candidate case) -- but only if it points to EXACTLY one
            # of the remaining candidates; anything else stays ambiguous.
            if stated_value is not None:
                value_hits = [
                    idx for idx, row in candidates.iterrows()
                    if _value_consistent(stated_value, row) is True
                ]
                if len(value_hits) == 1:
                    obs_row = candidates.loc[value_hits[0]]
                    results.append(MatchResult(
                        entry.commentary_id, entry.text, obs_row["Observation ID"], True,
                        f"matched on Department={dept}, Category={cat}, disambiguated by stated Value "
                        f"(${stated_value:,.2f} consistent with only one of {len(candidates)} candidates)",
                    ))
                    continue
            results.append(MatchResult(
                entry.commentary_id, entry.text, None, False,
                f"{dept} / {cat} matches {len(candidates)} open observations across different periods; "
                "no period reference (or stated Value) in the commentary to disambiguate",
            ))
    return results


# ---------------------------------------------------------------------------
# Phase 4 v2 — Exclusivity (Brief v2 Section 2) and gated semantic
# reconciliation (Sections 3-5, 5a)
# ---------------------------------------------------------------------------
OCCUPIED_BASIS_PREFIX = "observation already has a commentary — consolidate into the existing entry"

# Section 4: the semantic layer's ENTIRE job is "which of these candidates,
# if any, does this commentary mean" -- no financial calculation, no
# evidence validation, no fact invention. The system prompt states this
# boundary directly so it's enforced at the request level, not only in
# Builder's post-hoc validation of the response.
SEMANTIC_RECONCILIATION_SYSTEM_PROMPT = """You are assisting a financial close review. You will be given a list of currently-unmatched financial observations and a piece of Controller commentary. Your ONLY job is to decide whether the commentary's meaning refers to exactly one of the listed observations.

Rules:
- You may select an observation ONLY by its exact Observation ID from the list provided. Never invent an ID.
- If the commentary does not clearly and confidently refer to exactly one observation in the list, respond NO_MATCH. On ambiguity between two or more candidates, respond NO_MATCH.
- Do not perform financial calculation. Do not judge whether the commentary is a correct or supported explanation. Do not invent facts, causes, or figures. Your only task is identifying which observation (if any) the commentary is ABOUT.
- Respond with EXACTLY one line and nothing else: either the Observation ID, or the literal text NO_MATCH."""


def _build_semantic_prompt(entry_text, candidate_observations):
    lines = ["Currently-unmatched candidate observations:"]
    for _, row in candidate_observations.iterrows():
        lines.append(
            f"- {row['Observation ID']}: {row['Department']} / {row['Category']}, "
            f"{row['Period']}, Delta ${row['Delta ($)']:,.2f} "
            f"(${row['Before ($)']:,.2f} -> ${row['After ($)']:,.2f})"
        )
    lines.append("")
    lines.append('Controller commentary:\n"""')
    lines.append(entry_text)
    lines.append('"""')
    lines.append("")
    lines.append("Which candidate Observation ID (if any) does this commentary refer to?")
    return "\n".join(lines)


def semantic_reconcile_commentary(entry_text, candidate_observations, model="claude-sonnet-4-6", max_tokens=50):
    """Semantic reconciliation, Brief v2 Sections 3-5. Pure function: given
    one unresolved commentary's text and the DataFrame of currently-
    unmatched/unoccupied observations, returns (matched_observation_id, None)
    on a confident, validated match, or (None, reason) in every other case
    -- never raises. Mirrors rollups.call_claude_narrative()'s exact
    failure-mode shape (Section 5's "return a tuple, never raise" pattern).

    Failure modes, all neutral (Section 5):
      - No ANTHROPIC_API_KEY -> (None, reason), no exception, no forced
        match, no call attempted.
      - No candidates supplied -> (None, reason), no call attempted (this
        is the Section 3 condition-2 gate; also enforced by the caller,
        resolve_commentary_matches, but checked again here defensively).
      - API/network failure -> (None, reason), no retry (Section 5a).
      - Model response is not exactly "NO_MATCH" or a real member of
        candidate_observations' actual Observation ID set -> treated as no
        confident match (Section 4: "never trust a returned observation ID
        without checking it against real data"; Criterion 7).

    This function makes NO gating decision (Section 3's two-condition
    invocation gate is the caller's responsibility, in
    resolve_commentary_matches) and NO idempotency decision (Section 5a's
    rerun-deduplication is also the caller's responsibility) -- it is the
    gated action itself, always calling the API when invoked with a key
    present and a non-empty candidate set. Injected as `semantic_fn` in
    resolve_commentary_matches for testing without a real API call.
    """
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None, "No ANTHROPIC_API_KEY found in environment — semantic reconciliation unavailable this session."
    if candidate_observations is None or candidate_observations.empty:
        return None, "No unmatched observations remain — semantic reconciliation not invoked."

    valid_ids = set(candidate_observations["Observation ID"])
    prompt = _build_semantic_prompt(entry_text, candidate_observations)
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=0.0,
            system=SEMANTIC_RECONCILIATION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = "".join(block.text for block in resp.content if block.type == "text").strip()
    except Exception as e:
        return None, f"API call failed: {e}"

    candidate_id = raw.splitlines()[0].strip() if raw else ""
    if candidate_id == "NO_MATCH":
        return None, "Semantic reconciliation found no confident match."
    if candidate_id in valid_ids:
        return candidate_id, None
    # Malformed, out-of-set, or otherwise unusable -- never trusted at face
    # value (Section 4 / Criterion 7).
    return None, f"Semantic reconciliation returned an unusable/invalid response ({raw[:120]!r}); treated as no confident match."


def resolve_commentary_matches(entries, observation_register, commentary_records, semantic_attempted=None, semantic_fn=None):
    """Full Phase 4 resolution pipeline (Brief v2): deterministic pass
    (Section 1, match_commentary_entries) -> exclusivity enforcement
    (Section 2) -> gated semantic reconciliation (Section 3). This is the
    function callers (the dashboard) should use for the complete pipeline;
    match_commentary_entries() alone only covers Section 1.

    entries: list[CommentaryEntry] to resolve this call.
    observation_register: the current full observation register (as built
      by build_observation_register()).
    commentary_records: dict[observation_id -> CommentaryRecord] --
      TODAY's actual state, read but not mutated by this function (the
      caller decides how/when to call record.add_version(), same as
      before). An observation_id present here with >=1 version is
      OCCUPIED (Section 2) and is excluded from BOTH deterministic
      acceptance and the semantic candidate set.
    semantic_attempted: optional mutable set[str] of commentary_id values
      already attempted this session (matched, or already tried and
      failed) -- the caller (dashboard) should back this with
      st.session_state so a Streamlit rerun does not re-invoke the API for
      the same commentary twice (Section 5a / Criterion 10a). A fresh set
      is used if omitted -- correct for a one-shot call, not sufficient for
      a caller that re-invokes this function every rerun without
      persisting the set itself.
    semantic_fn: injectable for testing (defaults to
      semantic_reconcile_commentary); must return (id_or_None, reason_or_None).

    Returns list[MatchResult], one per input entry, each carrying `method`
    in {"deterministic", "semantic", "unresolved"}.
    """
    if semantic_attempted is None:
        semantic_attempted = set()
    if semantic_fn is None:
        semantic_fn = semantic_reconcile_commentary

    def _occupied(oid):
        rec = commentary_records.get(oid)
        return bool(rec and rec.versions)

    deterministic = match_commentary_entries(entries, observation_register)

    results = []
    unresolved = []  # list of MatchResult still needing the semantic gate
    claimed_this_batch = set()  # observation IDs already attached EARLIER in
    # this same call's entries list -- needed because match_commentary_
    # entries() resolves every entry independently and has no knowledge of
    # exclusivity, so two entries in one batch can both deterministically
    # resolve to the same still-unoccupied observation. Processed in input
    # order: the first claims it, later ones are treated exactly like an
    # externally-occupied conflict (Criterion 3: "the first is attached; the
    # second is reported unresolved/occupied, never silently added as a
    # second version").
    for m in deterministic:
        m.method = "deterministic"
        if m.matched and (_occupied(m.matched_observation_id) or m.matched_observation_id in claimed_this_batch):
            if m.matched_observation_id in claimed_this_batch and not _occupied(m.matched_observation_id):
                conflict_note = "already claimed by an earlier entry in this same import batch"
            else:
                conflict_note = f"deterministic candidate occupied: {m.match_basis}"
            m.match_basis = f"{OCCUPIED_BASIS_PREFIX} ({conflict_note})"
            m.matched = False
            m.matched_observation_id = None
            unresolved.append(m)
        elif m.matched:
            claimed_this_batch.add(m.matched_observation_id)
            results.append(m)
        else:
            unresolved.append(m)

    for m in unresolved:
        was_occupied_conflict = m.match_basis.startswith(OCCUPIED_BASIS_PREFIX)

        occupied_ids = {oid for oid, rec in commentary_records.items() if rec.versions}
        # Also exclude observations already claimed earlier IN THIS SAME
        # batch (deterministic matches processed above), so two entries in
        # one import batch can't both deterministically or semantically
        # claim the same observation before commentary_records itself is
        # updated by the caller.
        occupied_ids |= {r.matched_observation_id for r in results if r.matched}
        unmatched_obs = (
            observation_register[~observation_register["Observation ID"].isin(occupied_ids)]
            if not observation_register.empty else observation_register
        )

        if unmatched_obs.empty:
            # Section 3 condition 2 fails: gate closed, zero semantic calls.
            if not was_occupied_conflict:
                m.match_basis += " (no unmatched observations remain — semantic reconciliation not invoked)"
            m.method = "unresolved"
            results.append(m)
            continue

        if m.commentary_id in semantic_attempted:
            # Section 5a / Criterion 10a: already attempted this session --
            # a rerun must not call again.
            m.match_basis = (
                m.match_basis if was_occupied_conflict
                else "semantic reconciliation already attempted this session — not called again"
            )
            m.method = "unresolved"
            results.append(m)
            continue

        semantic_attempted.add(m.commentary_id)
        matched_oid, reason = semantic_fn(m.text, unmatched_obs)
        if matched_oid:
            m.matched = True
            m.matched_observation_id = matched_oid
            m.match_basis = "semantic reconciliation: confident match, validated against current unmatched set"
            m.method = "semantic"
        else:
            m.match_basis = reason or "semantic reconciliation: no confident match"
            m.method = "unresolved"
        results.append(m)

    return results


# ---------------------------------------------------------------------------
# Phase 6 — Explanation Validation (Section C)
# ---------------------------------------------------------------------------
@dataclass
class Phase6Result:
    assessment: str
    check1_specific_claim: bool
    check2_checkable: Optional[bool]
    check3_supported: Optional[bool]          # True=Supported, False=Contradicted, None=not reached
    check4_sufficiently_specific: Optional[bool]
    failed_check: Optional[int]               # 1, 2, or 4 -- which check produced Insufficient
    cited_field: Optional[str]
    cited_value: Optional[str]
    reason: str


# Claim-type vocabularies. CHECKABLE types name a driver this project's
# bounded evidence package (build_evidence_package) actually has a field
# for -- every entry here must be backed by real validation logic in
# validate_commentary() and a real evidence source, not just a name.
# UNCHECKABLE types are named directly by the Brief's own example (vendor
# pricing, invoice timing) plus adjacent categories the evidence package
# likewise has no field for.
#
#   "headcount"            -> evidence["headcount_change"] (department
#                              headcount current vs. prior, per Brief
#                              Section C's evidence package list)
#   "category_reallocation" -> evidence["dept_category_breakdown"] (the D14
#                              Department x Cost Category breakdown for
#                              every category in this department, per Brief
#                              Section C: "the corresponding D14 Department
#                              x Cost Category breakdown row, where
#                              relevant"). A reallocation/reclassification
#                              claim names a SPECIFIC other category within
#                              the same department as the true driver (e.g.
#                              "this is really a software licensing cost,
#                              not payroll") -- checkable against whether
#                              that named category shows a materially
#                              offsetting movement in the same department
#                              and period.
CHECKABLE_CLAIM_TYPES = {
    "headcount": [
        "headcount", "hire", "hiring", "hired", "new hire", "new hires", "staff", "staffed",
        "team grew", "team growth", "reduction in force", "layoff", "layoffs", "attrition", "backfill",
    ],
    "category_reallocation": [
        "reclassif", "reallocat", "recateg", "moved from", "shifted from", "shifted to",
        "now booked under", "now classified as", "budget line change", "category change",
        "moved to a different", "reassigned to", "was actually",
    ],
}
UNCHECKABLE_CLAIM_TYPES = {
    "vendor pricing": ["vendor price", "vendor pricing", "price increase from", "renewal price", "list price"],
    "invoice timing": ["invoice timing", "invoice was late", "invoice delay", "billing timing", "billed early", "billed late"],
    "contract terms": ["contract terms", "renegotiat", "new contract", "contract change"],
    "market conditions": ["market rate", "market conditions", "fx rate", "exchange rate", "currency fluctuation"],
}

# A genuine reclassification should show up as a materially offsetting
# movement in the named other category -- not just any nonzero change.
# Policy constant, same spirit as close_validation.py's documented
# DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND: the named category's variance must be
# at least this fraction of the flagged observation's own variance to count
# as a meaningful corroborating (or contradicting) offset.
CATEGORY_REALLOCATION_MATERIALITY_RATIO = 0.20

_CAUSAL_MARKERS = [
    "because", "due to", "driven by", "as a result of", "owing to", "caused by",
    "attributable to", "resulted from", "reflects", "explained by",
]
_NUMBER_RE = re.compile(r"\d+(\.\d+)?")


def _has_specific_claim(text):
    """Check 1: is there an explanation at all, vs. no claim / pure
    restatement of the number itself?"""
    t = text.strip()
    if len(t) < 15:
        return False
    lower = t.lower()
    if any(m in lower for m in _CAUSAL_MARKERS):
        return True
    all_keywords = [kw for kws in CHECKABLE_CLAIM_TYPES.values() for kw in kws] + \
                   [kw for kws in UNCHECKABLE_CLAIM_TYPES.values() for kw in kws]
    return any(kw in lower for kw in all_keywords)


def _classify_claim_type(text):
    """Check 2 input: what kind of claim is this, and does the evidence
    package have a field for it at all? Uncheckable types are matched first
    -- a claim can name both a checkable and uncheckable phrase, and the
    Brief's own bar for Check 2 is whether the evidence package HAS a field,
    not whether some field is more relevant."""
    lower = text.lower()
    for ctype, kws in UNCHECKABLE_CLAIM_TYPES.items():
        if any(kw in lower for kw in kws):
            return ctype, False
    for ctype, kws in CHECKABLE_CLAIM_TYPES.items():
        if any(kw in lower for kw in kws):
            return ctype, True
    return None, False


# ---------------------------------------------------------------------------
# Headcount claim DIRECTION parsing (Brief:
# phase6_headcount_direction_fix_brief_v1.md, Section C1).
#
# Business rule: a headcount-type claim asserts one of four things about
# the direction of the department's own headcount movement -- "increase",
# "decrease", "no change", or nothing discernible ("unspecified"). Prior to
# this fix, _validate_headcount_claim() never parsed this at all; it only
# checked whether the movement was material and, if so, compared the
# ACTUAL headcount-change sign against the ACTUAL variance sign -- never
# against what the commentary claimed. That meant a claim of "increase" and
# a claim of "no change" against the same evidence produced byte-identical
# results. This function is the fix: it parses the commentary text only,
# independent of any evidence figure, and returns the asserted direction so
# the caller can compare it against the actual headcount_change value.
#
# "backfill" is deliberately NOT decrease-only: replacing a departure is
# direction-neutral on its own (net headcount may be flat). It only counts
# as a decrease assertion if the SAME claim also contains an unambiguous
# decrease term elsewhere in the text.
_HEADCOUNT_INCREASE_TERMS = [
    "increase", "hire", "hiring", "hired", "grew", "grow", "added", "expand", "expanded", "expansion",
]
_HEADCOUNT_DECREASE_TERMS = [
    "decrease", "layoff", "layoffs", "reduction", "reduced", "reduce", "attrition",
]
_HEADCOUNT_NO_CHANGE_TERMS = [
    "no change", "unchanged", "flat", "stayed the same", "did not change", "hasn't changed", "has not changed",
]


def _parse_headcount_direction(text):
    """Section C1. Returns one of "increase", "decrease", "no_change", or
    "unspecified". Evaluated independent of whether the text contains a
    number -- direction and materiality are separate questions (Section C3
    keeps them separate on purpose)."""
    lower = text.lower()

    if any(term in lower for term in _HEADCOUNT_NO_CHANGE_TERMS):
        return "no_change"

    has_increase = any(term in lower for term in _HEADCOUNT_INCREASE_TERMS)
    has_decrease = any(term in lower for term in _HEADCOUNT_DECREASE_TERMS)

    if has_increase and not has_decrease:
        return "increase"
    if has_decrease and not has_increase:
        return "decrease"
    if has_increase and has_decrease:
        # Both an explicit increase and an explicit decrease term present --
        # genuinely ambiguous within the claim itself, not a case this Brief
        # is asked to disambiguate further. Falls through to "backfill"
        # check below (moot, since has_decrease is already True here) and
        # then to unspecified.
        return "unspecified"

    if "backfill" in lower:
        # Backfill alone is direction-neutral (Section C1) -- it only
        # resolves to "decrease" if paired with an unambiguous decrease
        # term, which would already have set has_decrease above. Reaching
        # here means "backfill" is the only signal present, so unspecified.
        return "unspecified"

    return "unspecified"


def _validate_headcount_claim(text, evidence):
    """Check 3/4 for claim_type == 'headcount', backed by
    evidence['headcount_change'] / evidence['variance_pct'].

    Business rule (Brief phase6_headcount_direction_fix_brief_v1.md,
    Section C3), applied in this order:
      1. Parse the ASSERTED direction from the commentary text alone
         (increase / decrease / no_change / unspecified) -- see
         _parse_headcount_direction() above.
      2. If unspecified: route to the existing genericity check (Check 4)
         -> Insufficient. This does NOT fall through to a variance-sign
         default -- that was the pre-fix defect.
      3. If "no_change": immaterial actual movement (|change| <= band) is
         CONSISTENT with the claim -> Supported. A material actual movement
         directly contradicts the claim's own premise -> Contradicted.
      4. If "increase" or "decrease": an immaterial actual movement fails
         the materiality gate regardless of asserted direction ->
         Contradicted, reason text explicitly names this a materiality-gate
         result (not a direction mismatch -- none exists to report yet,
         since the movement isn't even large enough to have a meaningful
         direction). A material movement is then compared: matching sign ->
         Supported; opposite sign -> Contradicted, reason text explicitly
         names this a direction mismatch.
    The materiality band itself (default 2, same value and role as
    close_validation.py's DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND) is
    unchanged by this fix -- only what the movement is compared against
    (asserted claim direction, not actual variance direction) has changed.
    """
    hc_change = evidence.get("headcount_change")
    variance_pct = evidence.get("variance_pct")
    if hc_change is None or variance_pct is None:
        return Phase6Result(
            INSUFFICIENT, True, False, None, None, 2, None, None,
            "The claim type is checkable in principle, but this observation's evidence package does not "
            "include a usable headcount-change or variance figure.",
        )

    headcount_band = evidence.get("headcount_band", 2)
    material_hc_change = abs(hc_change) > headcount_band
    has_number = bool(_NUMBER_RE.search(text))
    generic_only = (not has_number) and (len(text.split()) <= 12)
    direction = _parse_headcount_direction(text)

    if direction == "unspecified":
        # Route through the existing genericity check (Check 4), never
        # through the old (removed) variance-direction default. A claim
        # that is merely topically about headcount but asserts no
        # discernible direction is exactly the "too generic to compare
        # meaningfully" case Check 4 already exists to catch.
        return Phase6Result(
            INSUFFICIENT, True, True, None, False, 4, "Headcount Change", f"{hc_change:+.2f}",
            "The claim is checkable (headcount is a recognized driver type) and a headcount change exists "
            "in the evidence, but the commentary does not assert a discernible direction (increase, "
            "decrease, or no change) for that headcount movement -- too generic to compare meaningfully "
            "against the evidence.",
        )

    if generic_only and direction != "no_change":
        # Preserve the pre-existing genericity behavior for very short,
        # numberless claims -- a parsed direction doesn't by itself make a
        # near-empty claim ("hired.") sufficiently specific. A "no_change"
        # assertion is exempt: "no change" / "unchanged" is itself a
        # complete, checkable claim regardless of length.
        return Phase6Result(
            INSUFFICIENT, True, True, None, False, 4, "Headcount Change", f"{hc_change:+.2f}",
            "The claim is checkable and a headcount change exists in the evidence, but the commentary "
            "gives no scale, role, or timing detail beyond a bare direction word -- too generic to "
            "compare meaningfully against the evidence.",
        )

    if direction == "no_change":
        if not material_hc_change:
            return Phase6Result(
                SUPPORTED, True, True, True, True, None, "Headcount Change", f"{hc_change:+.2f}",
                f"The commentary claims no material change in headcount; the evidence package shows a "
                f"headcount change of {hc_change:+.2f} for this department, within the +/-{headcount_band} "
                f"band -- consistent with (not proof of) the claimed 'no change'.",
            )
        return Phase6Result(
            CONTRADICTED, True, True, False, True, None, "Headcount Change", f"{hc_change:+.2f}",
            f"The commentary claims no change in headcount, but the evidence package shows a headcount "
            f"change of {hc_change:+.2f} for this department, outside the +/-{headcount_band} band -- "
            f"directly contradicting the claim's own premise.",
        )

    # direction is "increase" or "decrease" from here on.
    if not material_hc_change:
        return Phase6Result(
            CONTRADICTED, True, True, False, True, None, "Headcount Change", f"{hc_change:+.2f}",
            f"MATERIALITY GATE: the commentary attributes the movement to a headcount {direction}, but "
            f"the evidence package shows a headcount change of {hc_change:+.2f} for this department -- "
            f"within the +/-{headcount_band} band treated as no material headcount driver, regardless of "
            f"which direction was claimed.",
        )

    asserted_sign_positive = (direction == "increase")
    actual_sign_positive = hc_change > 0
    direction_matches = asserted_sign_positive == actual_sign_positive

    if direction_matches:
        return Phase6Result(
            SUPPORTED, True, True, True, True, None, "Headcount Change", f"{hc_change:+.2f}",
            f"Headcount changed {hc_change:+.2f}, matching the claimed {direction} -- consistent with "
            f"(not proof of) the claimed driver.",
        )
    return Phase6Result(
        CONTRADICTED, True, True, False, True, None, "Headcount Change", f"{hc_change:+.2f}",
        f"DIRECTION MISMATCH: the commentary attributes the movement to a headcount {direction}, but "
        f"headcount actually moved {hc_change:+.2f} for this department -- the opposite of the claimed "
        f"direction.",
    )


def _validate_category_reallocation_claim(text, evidence):
    """Check 3/4 for claim_type == 'category_reallocation', backed by
    evidence['dept_category_breakdown'] -- the D14 Department x Cost
    Category breakdown for every category in this observation's department
    (Brief Section C: 'the corresponding D14 Department x Cost Category
    breakdown row, where relevant'). A reallocation claim names a SPECIFIC
    other category as the true driver; that is only checkable if (a) the
    text names one, (b) the breakdown has data for it, and (c) that
    category's own movement is materially large enough to plausibly be an
    offsetting reclassification, not noise."""
    own_category = evidence.get("category")
    breakdown = evidence.get("dept_category_breakdown")
    obs_delta = evidence.get("variance_dollars")

    if breakdown is None or breakdown.empty or obs_delta is None:
        return Phase6Result(
            INSUFFICIENT, True, False, None, None, 2, None, None,
            "The claim type is checkable in principle, but no Department x Cost Category breakdown is "
            "available for this observation to check a reallocation claim against.",
        )

    canonical_categories = sorted(c for c in breakdown["Category"].unique() if c != own_category)
    named_targets = _find_canonical_terms(text, CATEGORY_SYNONYMS, canonical_categories)
    # A reallocation claim naming its OWN flagged category isn't a
    # cross-category claim at all -- exclude it explicitly so e.g. "software
    # costs were reclassified within software" doesn't pass as a target.
    named_targets = {c for c in named_targets if c != own_category}

    if not named_targets or len(named_targets) > 1:
        return Phase6Result(
            INSUFFICIENT, True, True, None, False, 4,
            None, None,
            "The claim is checkable in principle (a category reallocation is a real, checkable driver "
            "type), but the commentary does not name exactly one specific OTHER category to check the "
            "reallocation against -- too generic to compare meaningfully.",
        )

    target_category = next(iter(named_targets))
    target_rows = breakdown[breakdown["Category"] == target_category]
    if target_rows.empty:
        return Phase6Result(
            INSUFFICIENT, True, False, None, None, 2, None, None,
            f"The commentary names '{target_category}' as the reallocation source, but the evidence "
            f"package has no breakdown data for that category in this department.",
        )

    target_variance = float(target_rows.iloc[0]["QoQ/YoY Variance ($)"])
    field_label = f"D14 {target_category} Variance ($)"
    cited_value = f"{target_variance:+.2f}"

    threshold = CATEGORY_REALLOCATION_MATERIALITY_RATIO * abs(obs_delta) if obs_delta else 0
    material = abs(target_variance) >= threshold and threshold > 0
    opposite_sign = (target_variance > 0 and obs_delta < 0) or (target_variance < 0 and obs_delta > 0)

    if not material:
        return Phase6Result(
            INSUFFICIENT, True, True, None, False, 4, field_label, cited_value,
            f"The claim is checkable and names a specific category ('{target_category}'), but that "
            f"category's own movement ({target_variance:+.2f}) is too small relative to the flagged "
            f"variance ({obs_delta:+.2f}) to meaningfully corroborate a reallocation claim.",
        )

    if opposite_sign:
        return Phase6Result(
            SUPPORTED, True, True, True, True, None, field_label, cited_value,
            f"'{target_category}' moved {target_variance:+.2f} in this department the same period -- an "
            f"offsetting movement consistent with (not proof of) a reallocation between categories.",
        )
    return Phase6Result(
        CONTRADICTED, True, True, False, True, None, field_label, cited_value,
        f"The commentary attributes the movement to a reallocation from/to '{target_category}', but that "
        f"category moved {target_variance:+.2f} in the SAME direction as the flagged variance "
        f"({obs_delta:+.2f}) this period -- not the offsetting pattern a reallocation would produce.",
    )


_CLAIM_TYPE_VALIDATORS = {
    "headcount": _validate_headcount_claim,
    "category_reallocation": _validate_category_reallocation_claim,
}


def validate_commentary(text, evidence):
    """Phase 6. Runs the four checks in Brief Section C, in order, stopping
    at the first failure. `evidence` is the bounded evidence package (see
    build_evidence_package) -- this function reads only what's in that dict;
    it never reaches back to the raw dataset, other observations, or other
    periods. Never invents a cause the evidence package cannot establish;
    Supported is always worded as consistency, never proof/causation.

    Check 3/4 logic is dispatched per claim type (_CLAIM_TYPE_VALIDATORS) --
    every entry in CHECKABLE_CLAIM_TYPES must have a corresponding
    validator backed by a real evidence-package field; there is no
    claim type that is merely named without validation logic behind it."""
    text = (text or "").strip()

    # --- Check 1: specific claim present? ---------------------------------
    if not _has_specific_claim(text):
        return Phase6Result(
            INSUFFICIENT, False, None, None, None, 1, None, None,
            "No specific explanation was found in the commentary text -- it does not name a driver "
            "beyond the number itself.",
        )

    # --- Check 2: checkable against available evidence? -------------------
    claim_type, checkable = _classify_claim_type(text)
    if not checkable:
        detail = f"claim type '{claim_type}'" if claim_type else "no recognizable claim type"
        return Phase6Result(
            INSUFFICIENT, True, False, None, None, 2, None, None,
            f"The commentary makes a specific claim ({detail}), but the evidence package has no field "
            "capable of corroborating or contradicting this claim type.",
        )

    # --- Checks 3 & 4: dispatched to the claim type's own validator --------
    validator = _CLAIM_TYPE_VALIDATORS[claim_type]
    return validator(text, evidence)


def build_evidence_package(observation_row, hc_current_df, hc_prior_df, dept_category_breakdown=None, headcount_band=2):
    """The bounded set of financial data Phase 6 is allowed to check a claim
    against (Brief Section C). Computes nothing new -- reuses D11 output
    (the observation row, already produced by close_validation.py) and,
    when supplied, D14's Department x Category breakdown. Never the raw
    dataset, other observations, or other periods.

    hc_current_df / hc_prior_df: department-level headcount rollups for the
    observation's current/prior period (e.g. rollups.py's hc_dept_q/_y,
    filtered to the relevant period rows by the caller), each with
    ['Department', 'Ending Headcount'].

    dept_category_breakdown: the D14 Department x Cost Category breakdown
    for EVERY category in this observation's department, for the current
    period (e.g. rollups.py's exp_by_dept_cat_q/_y filtered to this
    department + current period, with columns ['Category', 'Amount ($)',
    'Prior Period ($)', 'QoQ/YoY Variance ($)', 'QoQ/YoY Variance (%)']).
    Deliberately the FULL set of the department's categories, not just the
    one that was flagged -- a category_reallocation claim (Phase 6) names a
    DIFFERENT category as the true driver, so checking it requires more
    than the flagged category's own row.
    """
    dept = observation_row["Department"]
    before, after, delta = observation_row["Before ($)"], observation_row["After ($)"], observation_row["Delta ($)"]
    variance_pct = (delta / before) if before else None

    hc_cur = hc_current_df.loc[hc_current_df["Department"] == dept, "Ending Headcount"]
    hc_pri = hc_prior_df.loc[hc_prior_df["Department"] == dept, "Ending Headcount"]
    hc_cur_val = float(hc_cur.iloc[0]) if len(hc_cur) else None
    hc_pri_val = float(hc_pri.iloc[0]) if len(hc_pri) else None
    hc_change = (hc_cur_val - hc_pri_val) if (hc_cur_val is not None and hc_pri_val is not None) else None

    return {
        "department": dept,
        "category": observation_row["Category"],
        "period": observation_row["Period"],
        "detected_by": observation_row["Detected By"],
        "threshold_crossed": observation_row["Threshold Crossed"],
        "prior_value": before,
        "current_value": after,
        "variance_dollars": delta,
        "variance_pct": variance_pct,
        "headcount_current": hc_cur_val,
        "headcount_prior": hc_pri_val,
        "headcount_change": hc_change,
        "headcount_band": headcount_band,
        "dept_category_breakdown": dept_category_breakdown,
    }


# ---------------------------------------------------------------------------
# Phase 5 — Finance Collaboration, reinterpreted (Section D)
# ---------------------------------------------------------------------------
def draft_finance_note(phase6_result=None, no_match_reason=None):
    """Phase 5. Formats Phase 6's (or Phase 4's) OWN stated reason into a
    short, plain-language note for the finance/CFO user's own reference.
    No independent judgment logic. Never addressed to, formatted for, or
    sendable to the Controller -- there is no send/transmit path anywhere
    in this module."""
    if no_match_reason is not None:
        return (
            f"This commentary entry could not be confidently matched to an open observation "
            f"({no_match_reason}). Manual reconciliation is needed to associate it with the correct "
            f"observation."
        )
    if phase6_result is None:
        return "Nothing to draft -- no Phase 6 result or unmatched-commentary reason was supplied."
    if phase6_result.assessment != INSUFFICIENT:
        return "No draft needed -- this commentary was not assessed Insufficient."
    if phase6_result.failed_check == 1:
        return "No specific driver was identified for this movement -- the commentary does not name a cause."
    if phase6_result.failed_check == 2:
        return "The claimed driver type cannot be checked against the fields available in this observation's evidence package."
    if phase6_result.failed_check == 4:
        return "The explanation given is too general to compare meaningfully against the evidence -- more scale, role, or timing detail would help."
    return "The commentary could not be validated for an unspecified reason."


# ---------------------------------------------------------------------------
# Section F — Commentary Record / version model
# ---------------------------------------------------------------------------
@dataclass
class CommentaryVersion:
    version_number: int
    text: str
    source: str
    submitted_by: str
    timestamp: str
    validation_result: Optional[Phase6Result]


@dataclass
class CommentaryRecord:
    observation_id: str
    versions: List[CommentaryVersion] = field(default_factory=list)
    accepted_version_number: Optional[int] = None

    def add_version(self, text, source, submitted_by, validation_result):
        """Each revision is a new, complete version -- never a patch applied
        to a prior version, and the original is never overwritten (Brief
        Section F)."""
        if source not in (SOURCE_ORIGINAL_IMPORT, SOURCE_USER_REVISION):
            raise ValueError(f"Unknown version source: {source!r}")
        vnum = len(self.versions) + 1
        v = CommentaryVersion(
            version_number=vnum, text=text, source=source, submitted_by=submitted_by,
            timestamp=datetime.now(timezone.utc).isoformat(), validation_result=validation_result,
        )
        self.versions.append(v)
        return v

    def mark_accepted(self, version_number):
        """Exactly one version may be Accepted at a time; accepting a new
        version does not delete history."""
        if version_number not in [v.version_number for v in self.versions]:
            raise ValueError(f"No such version {version_number} for observation {self.observation_id}")
        self.accepted_version_number = version_number

    def accepted_text(self):
        if self.accepted_version_number is None:
            return None
        for v in self.versions:
            if v.version_number == self.accepted_version_number:
                return v.text
        return None

    def to_dict(self):
        """JSON-serializable form -- what gets copied into the immutable
        D10 Close History snapshot at close approval (Brief Section F)."""
        def _vres(r):
            if r is None:
                return None
            return {
                "assessment": r.assessment,
                "check1_specific_claim": r.check1_specific_claim,
                "check2_checkable": r.check2_checkable,
                "check3_supported": r.check3_supported,
                "check4_sufficiently_specific": r.check4_sufficiently_specific,
                "failed_check": r.failed_check,
                "cited_field": r.cited_field,
                "cited_value": r.cited_value,
                "reason": r.reason,
            }
        return {
            "observation_id": self.observation_id,
            "accepted_version_number": self.accepted_version_number,
            "versions": [
                {
                    "version_number": v.version_number, "text": v.text, "source": v.source,
                    "submitted_by": v.submitted_by, "timestamp": v.timestamp,
                    "validation_result": _vres(v.validation_result),
                }
                for v in self.versions
            ],
        }


def serialize_commentary_records(records_by_observation_id):
    """records_by_observation_id: dict[observation_id -> CommentaryRecord].
    Returns the JSON-serializable payload for close_history.archive_close()'s
    commentary_record parameter -- the COMPLETE Commentary Record (original
    import, every revision, every version's validation result, and the
    accepted-version identifier), per Brief Section F. No intermediate
    version is discarded."""
    return {oid: rec.to_dict() for oid, rec in records_by_observation_id.items()}


# ---------------------------------------------------------------------------
# Section G — Executive-output handoff
# ---------------------------------------------------------------------------
def accepted_commentary_prompt_lines(records_by_observation_id, observation_register, fmt_period_label=None):
    """v4-era helper, unchanged behavior, still used by the dashboard's own
    'accepted commentary preview' panel (Section E display only). Phase 7
    reads ONLY the text of the version marked accepted_version_number --
    never an unaccepted, superseded, or AI-generated substitute (Brief
    Section G). Returns formatted lines, each traceable to a specific
    accepted commentary version.

    fmt_period_label: optional display formatter (e.g. R.fmt_period_label),
    added by the Phase 7 period-display addendum (addendum to
    phase6_headcount_direction_fix_brief_v1.md). Called from two places:
    the dashboard's own display-only preview panel, and
    build_narrative_commentary_section() (Phase 7's Section G handoff,
    CFO/Board-facing per IA #9). Both now pass a formatter. Defaults to no
    formatting (identity) when omitted, so any caller that predates this
    parameter keeps its exact pre-existing behavior.

    NOT used directly for the narrative prompt as of v5 -- see
    build_narrative_commentary_section() below, which wraps this same
    "accepted only" rule inside the required three-way Section G logic."""
    lines = []
    for oid, rec in records_by_observation_id.items():
        text = rec.accepted_text()
        if text is None:
            continue
        obs_rows = observation_register[observation_register["Observation ID"] == oid]
        if obs_rows.empty:
            continue
        obs = obs_rows.iloc[0]
        display_period = fmt_period_label(obs["Period"]) if fmt_period_label else obs["Period"]
        lines.append(
            f"  - {obs['Department']} / {obs['Category']} ({display_period}, {obs['Type']}): "
            f"{text} [accepted version {rec.accepted_version_number}]"
        )
    return lines


# ---------------------------------------------------------------------------
# Section G — Executive-output handoff, THREE-WAY (Brief v5, rewritten)
# ---------------------------------------------------------------------------
def _obs_label(obs_row, fmt_period_label=None):
    display_period = fmt_period_label(obs_row["Period"]) if fmt_period_label else obs_row["Period"]
    return f"{obs_row['Department']} / {obs_row['Category']} ({display_period}, {obs_row['Type']})"


def build_narrative_commentary_section(
    observation_register, records_by_observation_id, commentary_file_supplied, fmt_period_label=None
):
    """Brief v5, Section G. Determines which of the three required states
    applies and returns a single formatted block ready to insert into
    rollups.build_user_prompt()'s prompt (empty string if nothing to add).

    fmt_period_label: display formatter (e.g. R.fmt_period_label), added by
    the Phase 7 period-display addendum (addendum to
    phase6_headcount_direction_fix_brief_v1.md). Phase 7's narrative/prompt
    text is CFO/Board-facing (IA #9) and must use the same D14 display
    convention as every other user-facing surface (e.g. "Q3 2026"), so this
    function threads the formatter through to every place it renders a
    period into text: the Case 2 "unresolved" lines, the Case 3
    "unexplained" lines (both via _obs_label() above), and the Case 2
    "accepted" lines (via accepted_commentary_prompt_lines(), which already
    supports this same optional-formatter pattern). Defaults to no
    formatting (identity) when omitted, so any caller that doesn't pass
    this argument keeps this function's pre-addendum behavior exactly.
    Note: under current canonical build_observation_register() behavior,
    observation_register['Period'] is ALREADY the fmt_period_label()
    output (see that function's Phase 3 branch) — fmt_period_label() is
    documented idempotent on already-formatted strings (returns unchanged
    if the input doesn't match the raw "Q# FY####" shape), so applying it
    again here is a safe no-op today and only becomes load-bearing if the
    register's storage format ever changes upstream. This keeps the
    "apply display formatting only at the point of rendering to a user"
    principle honored at this call site regardless of what the register
    currently stores.

    Three states, in order, first match wins:

      1. No flags at all (observation_register is empty). Commentary-file
         presence is irrelevant. Returns "" -- byte-identical to
         pre-Phase-4-6 behavior for this case (Brief Section G, Criterion 1).

      2. Flags exist AND a commentary file was supplied this close.
         - Each flagged observation with an ACCEPTED version: reported via
           the existing v4 "Finance/CFO-Approved Explanations" block
           (accepted_commentary_prompt_lines(), unchanged).
         - Each flagged observation with NO accepted version (never matched,
           matched but never resubmitted past Insufficient/Contradicted, or
           simply never reviewed): reported as UNRESOLVED -- a commentary
           process was attempted for this close but did not conclude.

      3. Flags exist AND no commentary file was supplied at all. Every
         flagged observation is reported as UNEXPLAINED -- identified by
         Phase 2/3, no Controller commentary was ever supplied this close.
         No cause is invented to fill the gap.

    Case 2's "unresolved" wording and Case 3's "unexplained, no commentary
    supplied" wording are deliberately distinct strings (Brief Section G,
    Criterion 4) so a reader -- human or the narrative-generation model --
    can tell which situation produced an unexplained item.
    """
    # Case 1 — no flags at all. Commentary-file presence is irrelevant.
    if observation_register is None or observation_register.empty:
        return ""

    # Case 3 — flags exist, no commentary file was ever supplied this close.
    if not commentary_file_supplied:
        lines = [
            f"  - {_obs_label(obs, fmt_period_label)}: identified by Phase 2/3 validation; no Controller commentary "
            f"was supplied for this close; UNEXPLAINED (no commentary process occurred for this item)."
            for _, obs in observation_register.iterrows()
        ]
        return (
            "\nFlagged Observations — No Commentary Supplied This Close:\n"
            + "\n".join(lines)
            + "\n(No Commentary.xlsx was provided for this close. These items were identified by automated "
              "validation only and have no Controller explanation of any kind. Do not infer, guess, or invent "
              "a cause for any item in this list -- state plainly that it is unexplained.)"
        )

    # Case 2 — flags exist, a commentary file WAS supplied this close.
    accepted_lines = accepted_commentary_prompt_lines(records_by_observation_id, observation_register, fmt_period_label)
    unresolved_lines = []
    for _, obs in observation_register.iterrows():
        oid = obs["Observation ID"]
        rec = records_by_observation_id.get(oid)
        if rec is not None and rec.accepted_text() is not None:
            continue  # already covered by accepted_lines
        unresolved_lines.append(
            f"  - {_obs_label(obs, fmt_period_label)}: identified by Phase 2/3 validation; a commentary process was "
            f"attempted for this close but no accepted explanation currently exists; UNRESOLVED "
            f"(commentary process incomplete, not absent)."
        )

    blocks = []
    if accepted_lines:
        blocks.append(
            "\nFinance/CFO-Approved Explanations (accepted commentary, human-reviewed):\n"
            + "\n".join(accepted_lines)
            + "\n(These are human-approved explanations for flagged items this period -- treat them as "
              "established context, not something to re-derive or second-guess.)"
        )
    if unresolved_lines:
        blocks.append(
            "\nFlagged Observations — Unresolved (commentary process incomplete):\n"
            + "\n".join(unresolved_lines)
            + "\n(A commentary file was supplied for this close, but these items do not yet have an "
              "accepted explanation. Do not infer, guess, or invent a cause for any item in this list -- "
              "state plainly that it remains unresolved.)"
        )
    return "".join(blocks)
