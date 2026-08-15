# Builder Brief — Phase 6 Headcount Claim Direction-Aware Validation

Document status: Final, ready for Builder handoff.
Brief ID: `phase6_headcount_direction_fix_brief_v1.md`
Governs: `commentary_workflow.py` only, specifically `_validate_headcount_claim()`.
Relationship to prior Briefs: a scoped fix layered on top of the already-implemented, already-canonical-synced v4/v5 scope (commits `789351b`, `5709c9e`). Does not reopen, redesign, or re-litigate v4 or v5.
Governing Decision Log entry: D13 (Machine Recommends, Human Decides) — this fix is a precondition for D13 reaching Verified. It does not itself change D13's decision text or rationale.

---

## A. Context — What Was Found

Two independent Test executions of the principal-supplied D13 UAT set (Case A — Supported, Case B — Contradicted, Case C — Insufficient, plus a correction-loop revision) were run against canonical commit `5709c9e` and reconciled by the Architect via direct source inspection (not narration-acceptance).

Confirmed finding, source-verified at `5709c9e`: `_validate_headcount_claim()` never parses or compares the direction asserted in the commentary text (increase / decrease / no change) against the evidence. It only:

1. Detects that the claim is topically about headcount (via a keyword list with no direction terms in it),
2. Applies the ±2 materiality band to the actual headcount change, and
3. If material, compares the actual headcount-change sign against the actual variance sign — never against what the commentary claims.

Consequence: Case A ("headcount increase of 1.0") and Case B ("no change in headcount") — two commentary texts asserting opposite things — currently produce byte-identical `Phase6Result` objects. This is a gap against the governing v4 Brief's own Check 3 definition ("does the actual evidence-package value corroborate or conflict with the claim?"), not a UAT-authoring artifact.

Confirmed non-issue, no fix needed: Phase 4 matching, Case C handling, the no-commentary UNEXPLAINED path, Commentary Record versioning/correction-loop mechanics, and the ±2 materiality band's own threshold value all behave correctly and are not touched by this Brief.

---

## B. Scope — In Scope

Direction-aware evaluation of `headcount`-type claims within `_validate_headcount_claim()`:

1. Determine, from the commentary text, whether the claim asserts an increase, a decrease, no change, or has no discernible direction.
2. Compare that asserted direction against the actual `headcount_change` value in the evidence package, producing Supported / Contradicted / Insufficient per Section C.
3. Ensure claims asserting opposite directions can no longer produce identical `Phase6Result` outputs for the same underlying evidence.
4. Update the `reason` string so it accurately reflects which comparison drove the result.
5. Document the new business rule via inline comments/docstring, per this project's standing convention.

Builder may rename or internally reorganize the direction-comparison logic itself (e.g., extracting a helper function for direction parsing), but must not refactor, rename, or restructure any other function, claim type, or module in this file, or in any other file.

No other part of `commentary_workflow.py`'s structure — claim-type dispatch, the `Phase6Result` shape, `_validate_category_reallocation_claim()`, matching, versioning — is in scope for reorganization, even incidentally.

---

## C. Required Behavior

### C1 — Claim direction parsing

The commentary text must be evaluated for a headcount-direction assertion, independent of whether it already contains a number.

**Increase:**
- "increase"
- "hire/hiring/hired"
- "grew"
- "added"
- "expanded"
(headcount context)

**Decrease:**
- "decrease"
- "layoff(s)"
- "reduction"
- "reduced"
- "attrition"

**No change:**
- "no change"
- "unchanged"
- "flat"
- "stayed the same"
- "did not change"

**Ambiguous terms:**

"backfill" alone must not automatically be classified as a decrease. A backfill can be direction-neutral — replacing a departure is not necessarily a net reduction.

Unless the same claim also contains unambiguous decrease language, "backfill" alone resolves to **unspecified**, not decrease.

If none of the above are present but a headcount keyword is present (per the existing `CHECKABLE_CLAIM_TYPES["headcount"]` list), direction is **unspecified**.

### C2 — Do not alter the materiality band

`DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND = 2` and its use in `close_validation.py` are out of scope and must not change.

Within `commentary_workflow.py`, the ±2 threshold continues to determine whether a headcount movement counts as a material driver — this Brief only changes what the movement is compared against, not the threshold.

### C3 — Evaluation rules

**Asserted "no change":**

- `|headcount_change| ≤ band` → **Supported** — immaterial movement is consistent with a "no change" claim.
- `|headcount_change| > band` → **Contradicted**, citing the actual change — the claim's premise is directly false.

**Asserted "increase" or "decrease":**

- `|headcount_change| ≤ band` → **Contradicted** (materiality gate) — the movement isn't material enough to be a real driver, regardless of which direction is claimed.
- Reason text must state this is a materiality-gate result, not a direction mismatch.

- `|headcount_change| > band` and actual sign matches asserted direction → **Supported**, worded as consistency, not proof.

- `|headcount_change| > band` and actual sign is opposite the asserted direction → **Contradicted**, reason text must explicitly state this is a direction mismatch.

**Unspecified direction:**

Must not fall through to the old variance-direction default.

Route through the existing genericity check (Check 4) → **Insufficient**, stating Check 4 as the failing check, unless it also fails Check 1/2 first per existing check-ordering.

### C4 — Reason-string distinctness

The `reason` field must make it possible, from the field alone, to tell whether a result was driven by:

a. the materiality band  
b. a direction match  
c. a direction mismatch  
d. an unspecified/generic claim

Reusing one sentence template across mechanically different outcomes must not recur.

### C5 — No new claim types

This Brief does not add new `CHECKABLE_CLAIM_TYPES` entries.

It only changes how the existing `headcount` type is evaluated.

---

## D. Explicit Non-Goals / Out of Scope

Do not:

- Change `DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND` or any logic in `close_validation.py`.
- Modify `_validate_category_reallocation_claim()`, `CATEGORY_REALLOCATION_MATERIALITY_RATIO`, or any other claim type's logic.
- Modify Phase 4 matching, Commentary Record versioning, or `close_history.py`.
- Modify `build_narrative_commentary_section()` or any v5 Section G narrative-handoff logic.
- Add, wire, or stub a Human Approval Gate control (`st.button` or otherwise).
- Modify the dashboard UI (`Northwind_Financial_Dashboard.py`) in any way.
- Modify `UNCHECKABLE_CLAIM_TYPES` or `_CAUSAL_MARKERS` logic.
- Change the wording rule that Supported results must be phrased as consistency, never proof.
- Author or alter the principal-supplied UAT case text under any circumstance.
- Restructure, rename, or reorganize any function, claim type, or file outside the direction-comparison logic itself.

---

## E. Post-Fix Expected Outcomes — Principal-Supplied UAT

The cases below are fixed inputs and must not be changed.

| Case | Text | Original prediction | Post-fix expected outcome | Why |
|---|---|---|---|---|
| A | "headcount increase of 1.0" | Supported | **Contradicted** (materiality gate) | `+1.0` is within ±2; asserted increase fails materiality gate |
| B | "no change in headcount" | Contradicted | **Supported** | `+1.0` is within ±2; immaterial movement is consistent with "no change" |
| C | "advertising agency" | Insufficient | **Insufficient** | No causal marker or listed keyword is present in the literal text; Check 1 fails. The assessment remains Insufficient and is unchanged. |
| Correction v1 | Identical text to Case B | loop predicted Supported after v2 | **Supported** | Same rule as Case B |
| Correction v2 | Identical text to Case A | Supported | **Contradicted** (materiality gate) | Same rule as Case A |
| No-commentary | — | UNEXPLAINED | **UNEXPLAINED** | Not touched by this fix |

The original correction-loop prediction of Supported after resubmission is therefore not met post-fix. This is expected and must not be treated as a fix failure or regression.

---

## F. Acceptance Criteria

1. Case A → **Contradicted**, with reason explicitly citing the materiality gate.
2. Case B → **Supported**, with reason stating the movement is immaterial and consistent with "no change."
3. Increase claim + materially negative actual (e.g. `-3.0`) → **Contradicted**, explicitly naming direction mismatch.
4. Increase claim + materially positive actual (e.g. `+3.0`) → **Supported**, consistency wording.
5. Decrease claim + materially negative actual (e.g. `-3.0`) → **Supported**, consistency wording.
6. Decrease claim + materially positive actual (e.g. `+3.0`) → **Contradicted**, explicitly naming direction mismatch.
7. Headcount claim with no parseable direction → **Insufficient**, failing Check 4.
8. Correction v1 → **Supported**; correction v2 → **Contradicted**, independently and freshly computed.
9. Case C remains Insufficient via Check 1, `claim_type=None`.
10. `category_reallocation` evaluation remains unaffected, confirmed by full regression, byte-identical for non-headcount cases.
11. No change to `DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND` or any read site in `close_validation.py`; confirmed by diff.
12. `reason` differs substantively between materiality-gate, direction-match, direction-mismatch, and unspecified-direction outcomes.

---

## G. Regression Requirements

### v4 fixture

**49/49.**

Must still pass, with the sole permitted exceptions being any checks that directly assert the old Case-B-identical-to-Case-A behavior, if such a check exists.

Any such exception must be individually listed.

If no such check exists, 49/49 must be byte-identical to the current baseline.

### v5 fixture

**23/23.**

Must remain unaffected and byte-identical.

### Rollups

**18/18 tie-outs.**

Must remain unaffected.

### AppTest

**0 exceptions, 8/8 tabs.**

Must be re-confirmed unaffected.

### Mandatory new direction cases

All seven must be individually reported:

1. Increase claim + material positive actual → Supported
2. Increase claim + material negative actual → Contradicted
3. Decrease claim + material negative actual → Supported
4. Decrease claim + material positive actual → Contradicted
5. No-change claim + immaterial actual → Supported
6. No-change claim + material actual → Contradicted
7. Headcount claim with no discernible direction → Insufficient

---

## H. Evidence Requirements — Builder Return Report

The Return Report must include clearly separated sections:

1. Actual diff to `commentary_workflow.py`, with updated `_validate_headcount_claim()` shown in full, plus inline comments/docstring documenting the new business rule.
2. Full Builder regression evidence:
   - v4 49/49
   - v5 23/23
   - all seven mandatory new cases.
3. Builder's own rerun of the exact principal-supplied UAT:
   - Case A
   - Case B
   - Case C
   - correction v1
   - correction v2
   - no-commentary
   
   The exact commentary text must be used unaltered.

   This is Builder confirmation evidence only. It is **not independent Test evidence**.
4. Explicit before/after comparison for Case A and Case B, including full reason strings and mechanism.
5. Rollups 18/18 confirmation.
6. AppTest baseline: 0 exceptions / 8/8 tabs.
7. Confirmation that `close_validation.py` is byte-identical to its pre-fix state, with zero diff.

The Architect must independently re-verify items 1–7 against the actual delivered files. Narration alone is insufficient.

### Governance sequence

Acceptance of the Builder Return Report confirms implementation correctness and regression non-breakage only.

It does **not** satisfy D13's independent-evidence requirement.

A separate Test session must subsequently and independently execute the identical, unaltered principal-supplied UAT set against the delivered fix, using the same clean-room discipline as the prior Test executions.

The independent Test must use the **original specified fixture**:

- Sales & Marketing / Other Opex
- `$47,857.52 → $97,857.52`
- headcount change **+1.0**
- Q4 FY2026

Builder's substituted Q3 fixture must **not** be used for the closing Test record.

D13's eventual move to Verified additionally depends on the separately tracked Human Approval Gate status.

---

## I. Non-Goals — Summary

This Brief does not:

- Change the ±2 materiality band.
- Move D13 to Verified by itself.
- Reopen v4/v5 scope.
- Build the Human Approval Gate.
- Modify the dashboard.
- Constitute a new architectural decision.

It is a corrective fix to already-approved acceptance criteria for Check 3.

---

## Final governance state

Architect acceptance of the Builder Return Report has been granted.

Status:

**Builder implementation: ACCEPTED**

**Regression evidence: ACCEPTED**

**Independent Test: COMPLETED AND PASSED.** Executed against the exact original fixture (Sales & Marketing / Other Opex, $47,857.52 → $97,857.52, headcount change +1.0, Q4 FY2026) and the exact principal-supplied UAT text. Reviewed and accepted by the Architect.

**D13 independent evidence for this fix: SATISFIED.**

**Canonical GitHub synchronization: NOT YET SATISFIED.** The accepted fix has not been promoted to canonical GitHub.

**D13 overall status: IN PROGRESS — NOT VERIFIED.** Canonical promotion of this fix is outstanding, and the Human Approval Gate remains a separate, unmet condition.

**Human Approval Gate: separately tracked and still outstanding.**

**Next required action: principal-authorized promotion of the accepted fix and this corrected Brief to canonical GitHub, followed by fresh-clone confirmation of synchronization.** Promotion alone does not make D13 Verified — the Human Approval Gate remains a separate, unresolved condition.
