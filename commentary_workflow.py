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
# Phase 4 — Commentary Matching (Section B)
# ---------------------------------------------------------------------------
@dataclass
class MatchResult:
    commentary_id: str
    text: str
    matched_observation_id: Optional[str]
    matched: bool
    match_basis: str


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


def match_commentary_entries(entries, observation_register):
    """Phase 4. For each CommentaryEntry, resolve the single best-supported
    observation, or return 'no confident match' (Acceptance Criteria B.1-4).

    Scoring is deliberately conservative: a match requires an unambiguous
    Department reference AND an unambiguous Category reference (explicit
    name or known synonym). Department or Category alone is never
    sufficient — a forced match with weak support is a defect, not a
    feature (Brief Section B). Period reference, when present, disambiguates
    among multiple open observations sharing the same Department/Category;
    when absent, a match is only made if exactly one open observation exists
    for that Department/Category pair.
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
            narrowed = candidates[candidates["Period"].isin(period_hits)]
            if not narrowed.empty:
                candidates = narrowed

        if len(candidates) == 0:
            results.append(MatchResult(
                entry.commentary_id, entry.text, None, False,
                f"referenced {dept} / {cat} but no open observation exists for that combination",
            ))
        elif len(candidates) == 1:
            basis = f"matched on Department={dept}, Category={cat}"
            basis += f", Period in {sorted(period_hits)}" if period_hits else " (single open observation for this Department/Category)"
            results.append(MatchResult(
                entry.commentary_id, entry.text, candidates.iloc[0]["Observation ID"], True, basis,
            ))
        else:
            results.append(MatchResult(
                entry.commentary_id, entry.text, None, False,
                f"{dept} / {cat} matches {len(candidates)} open observations across different periods; "
                "no period reference in the commentary to disambiguate",
            ))
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


def _validate_headcount_claim(text, evidence):
    """Check 3/4 for claim_type == 'headcount', backed by
    evidence['headcount_change'] / evidence['variance_pct']."""
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

    if not material_hc_change:
        # No material headcount movement at all directly conflicts with a
        # headcount-driven claim -- Checks 1/2/4 all pass (the claim is
        # specific, checkable, and states a clear driver), so this is
        # Contradicted, not Insufficient.
        return Phase6Result(
            CONTRADICTED, True, True, False, True, None, "Headcount Change", f"{hc_change:+.2f}",
            f"The commentary attributes the movement to headcount, but the evidence package shows a "
            f"headcount change of {hc_change:+.2f} for this department -- within the "
            f"+/-{headcount_band} band treated as no material headcount driver.",
        )

    same_direction = (hc_change > 0 and variance_pct > 0) or (hc_change < 0 and variance_pct < 0)

    if generic_only:
        return Phase6Result(
            INSUFFICIENT, True, True, None, False, 4, "Headcount Change", f"{hc_change:+.2f}",
            "The claim is checkable and a material headcount change exists in the evidence, but the "
            "commentary gives no scale, role, or timing detail -- too generic to compare meaningfully "
            "against the evidence.",
        )

    if same_direction:
        return Phase6Result(
            SUPPORTED, True, True, True, True, None, "Headcount Change", f"{hc_change:+.2f}",
            f"Headcount changed {hc_change:+.2f} in the same direction as the variance "
            f"({variance_pct:+.1%}) -- consistent with (not proof of) the claimed driver.",
        )
    return Phase6Result(
        CONTRADICTED, True, True, False, True, None, "Headcount Change", f"{hc_change:+.2f}",
        f"The commentary attributes the movement to headcount, but headcount moved {hc_change:+.2f} "
        f"while the variance moved {variance_pct:+.1%} -- opposite directions.",
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
def accepted_commentary_prompt_lines(records_by_observation_id, observation_register):
    """v4-era helper, unchanged behavior, still used by the dashboard's own
    'accepted commentary preview' panel (Section E display only). Phase 7
    reads ONLY the text of the version marked accepted_version_number --
    never an unaccepted, superseded, or AI-generated substitute (Brief
    Section G). Returns formatted lines, each traceable to a specific
    accepted commentary version.

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
        lines.append(
            f"  - {obs['Department']} / {obs['Category']} ({obs['Period']}, {obs['Type']}): "
            f"{text} [accepted version {rec.accepted_version_number}]"
        )
    return lines


# ---------------------------------------------------------------------------
# Section G — Executive-output handoff, THREE-WAY (Brief v5, rewritten)
# ---------------------------------------------------------------------------
def _obs_label(obs_row):
    return f"{obs_row['Department']} / {obs_row['Category']} ({obs_row['Period']}, {obs_row['Type']})"


def build_narrative_commentary_section(observation_register, records_by_observation_id, commentary_file_supplied):
    """Brief v5, Section G. Determines which of the three required states
    applies and returns a single formatted block ready to insert into
    rollups.build_user_prompt()'s prompt (empty string if nothing to add).

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
            f"  - {_obs_label(obs)}: identified by Phase 2/3 validation; no Controller commentary "
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
    accepted_lines = accepted_commentary_prompt_lines(records_by_observation_id, observation_register)
    unresolved_lines = []
    for _, obs in observation_register.iterrows():
        oid = obs["Observation ID"]
        rec = records_by_observation_id.get(oid)
        if rec is not None and rec.accepted_text() is not None:
            continue  # already covered by accepted_lines
        unresolved_lines.append(
            f"  - {_obs_label(obs)}: identified by Phase 2/3 validation; a commentary process was "
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
