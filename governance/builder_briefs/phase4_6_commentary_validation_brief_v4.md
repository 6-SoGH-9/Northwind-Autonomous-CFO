# Builder Brief — Phases 4–6: Commentary Matching, Finance Collaboration, Explanation Validation

**Status:** Active — v4 (supersedes v1, v2, and v3 in full; all archived — see Revision Note below)
**Governs:** Implementation of Phase 4 (Commentary Matching), Phase 5 (Finance Collaboration), Phase 6 (Explanation Validation), and the minimum Dashboard changes required to make the workflow operable
**Constrained by:** D13 (Machine Recommends, Human Decides) — Planned, becomes Verified only against this Brief's evidence
**Does not reopen:** D10, D11, D12, D14 — all remain Verified and unmodified. v4 resolves the two remaining product-definition questions carried from v3: commentary-file format and Commentary Record persistence relative to D10.
**Prerequisite Handbook state:** v2.6 (Cost Structure Investigation Views / D14 complete and Verified)
**Author:** Architect
**Precedence:** Project Handbook (v2.6) > this Brief > archived Briefs (including v1 of this Brief), per Handbook Section "Source of Truth"

---

## Revision Note (v3 → v4)

v4 resolves the two remaining product-definition questions explicitly left open in v3:

1. **Commentary-file format is now fixed:** the initial Controller commentary input is a separate `.xlsx` workbook with one sheet named `Commentary` and exactly two required columns: `Commentary_ID` and `Commentary_Text`. Each row is one complete commentary entry. The file contains no observation ID, validation status, AI assessment, or correction fields; matching remains a genuine Phase 4 responsibility.
2. **Commentary Record persistence relative to D10 is now fixed:** the complete Commentary Record, including the original imported version, every subsequent complete revision, each version's validation result, and the accepted version identifier, is included in the immutable D10 Close History snapshot when the close is approved. No intermediate version is discarded from the approved-close audit trail.

The target observation and actual UAT commentary content remain principal-supplied and are not architectural open questions.

## Revision Note (v2 → v3)

v2 had three structural non-compliances against the principal's stated deliverable structure, identified on principal-requested self-audit:
1. Section J was mislabeled — the principal specified J = Independent Test package; v2 used J for an unrelated open-items list and buried Test evidence inside Section I.
2. Phase 6's validation checks (Section C/D) collapsed the principal's four distinct checks into three, omitting "is the explanation sufficiently specific to be useful" as its own check.
3. Phase 5 and Phase 6 sections did not use the exact labeled sub-structure (Input / Processing / Output / etc.) the principal specified.

All three are corrected below. No product-behavior content changed as a result — this is a structural/completeness correction, not a redesign.

## Revision Note (v1 → v2)

v1 of this Brief assumed a Controller-facing collaboration loop: Phase 5 drafting a clarification communication addressed toward the Controller. **This was a design error, corrected by the principal.** The actual product workflow is:

- The Controller completes the close process **entirely outside the product** and supplies a close package: the financial dataset (already handled — D12) and a **separate commentary file** containing the Controller's explanations of relevant movements.
- The product **consumes** both files. It never presents any interface to the Controller — no login, no dashboard, no submission form, no direct communication channel to the Controller.
- The **finance/CFO user** is the only human operator of the dashboard. They review AI-matched, AI-validated commentary, and — when correction is needed — edit the **complete commentary text** themselves and resubmit it for revalidation.
- Phase 5 is reinterpreted accordingly: its output is a draft **for the finance/CFO user's own reference** (explaining what's missing or inconsistent), never an outbound Controller communication.

v1 is archived. This document is the sole governing Brief for Phases 4–6 going forward.

---

## A. Current State

**Already existing (Verified, unmodified by this Brief):**
- Dataset intake and canonical resolution (D12).
- D11 detection: Phase 2 (historical-revision diff) and Phase 3 (plausibility/headcount-band), producing the observation register for a close.
- D14 investigation views: Department × Cost Category and company-wide Cost Category-only breakdowns, giving a human investigator the detail a flagged observation needs.
- Existing dashboard tabs/pages (IA #1–9, per Handbook Section 3), Close Validation Status page.
- Executive narrative generation (Phase 7, reused) and the (not-yet-built, separately scoped) HTML/PPTX output (Phase 8).

**To be built (this Brief):**
- Commentary-file intake using the fixed `Commentary.xlsx` contract defined in Section B (a separate input artifact, imported alongside the dataset).
- Phase 4: commentary matching against the observation register.
- Phase 6: commentary validation against a bounded evidence package.
- Phase 5: draft output for the finance/CFO user's own reference (not sent anywhere).
- Dashboard: a review/edit/resubmit/accept interface for the finance/CFO user (Section E).
- Complete-commentary resubmission and revalidation: the resubmit action triggers an independent, fresh Phase 6 run on the full revised text (Section C, Criterion 6) — distinct from the initial validation pass.
- A version/data model distinguishing original, revised, and accepted commentary states (Section F).
- The handoff of the accepted commentary version into the existing Phase 7 narrative input (Section G).

---

## B. Phase 4 — Commentary Matching

**Input:**
- The current close's observation register (every D11 flag: department, category, period, flag type, $/% variance).
- The imported commentary file, parsed into discrete commentary entries (see below).

**Commentary-file structure — fixed product requirement:**
- The Controller supplies a separate Excel workbook named `Commentary.xlsx` as part of the close package.
- The workbook contains exactly one required sheet named `Commentary`.
- The sheet contains exactly two required columns:
  - `Commentary_ID` — a unique identifier for each commentary entry within the file.
  - `Commentary_Text` — the complete free-text commentary supplied by the Controller.
- Each populated row is exactly one complete commentary entry.
- `Commentary_Text` must not be pre-linked to an observation. There is **no observation ID, department/category key, validation status, AI assessment, or correction field** in the input file.
- Blank commentary rows are not valid input entries and must not be treated as commentary.
- The product imports this workbook; it does not ask the Controller to structure, submit, or correct commentary through the dashboard.
- This fixed format is part of the product contract. Builder must not choose an alternative file format or invent additional required columns.
- An entry may or may not explicitly name a department/category/period. Matching logic must handle both explicit and inferable references — the input format must not make matching trivial.

**Matching logic:**
- For each commentary entry, determine which observation in the register (if any) it refers to, based on identifiable references within the entry's text — not on plausibility alone.
- The complete, unmodified commentary entry text is what gets matched and carried forward — matching never truncates or summarizes the entry.

**Output:**
- Each commentary entry resolves to either a single matched observation ID, or an explicit "no confident match" result.
- A forced match with weak support is a defect, not a feature.

**Failure states:**
- **No confident match:** the entry is retained (not discarded), flagged as unmatched, and surfaced to the finance/CFO user in the dashboard for manual reconciliation (a dashboard action — associating an entry to an observation manually — not a new AI capability, and not routed to the Controller).
- **Observation with no corresponding commentary entry at all:** remains an open, uncommented flag; visible in the dashboard as such.

**Acceptance criteria:**
1. A commentary entry with an explicit, correct reference matches its target observation.
2. A commentary entry with only inferable (non-explicit) references still matches correctly when the inference is well-supported.
3. An entry with no well-supported match returns "no confident match," not a forced guess.
4. The full, unaltered entry text is preserved and carried into Phase 6 — matching never edits or shortens it.

---

## C. Phase 6 — Explanation Validation

**Input:** the complete commentary text for the observation under review (whichever version is currently under review — original or a resubmitted revision, per Section F) and that observation's evidence package (below).

**Evidence package** — the bounded set of financial data Phase 6 is allowed to check a claim against; reuses D11/D14 output, computes nothing new:
- Department, cost category, current period, prior period, current value, prior value, $ variance, % variance.
- Which check flagged it (Phase 2 or Phase 3) and the threshold crossed.
- Department headcount current vs. prior, where headcount-band-relevant.
- The corresponding D14 Department × Cost Category breakdown row, where relevant.
- **Never** the raw dataset, other observations, or other periods. If Phase 6 needs a field not present here, the required output is Insufficient — not an expanded data pull.

**Validation logic — four distinct checks, all four must be visible in the output, not collapsed into a bare label:**
1. **Specific claim present?** Does the commentary text contain a specific explanation at all (as opposed to no claim / pure description of the number itself)? If not → Insufficient, stop.
2. **Checkable against available evidence?** Does the evidence package contain a field capable of corroborating or contradicting *this specific claim type*? A claim can pass Check 1 and still fail here (e.g., a claim about vendor pricing or invoice timing — no such field exists in the evidence package). If not checkable → Insufficient, stop.
3. **Supported or contradicted?** If checkable, does the actual evidence-package value corroborate or conflict with the claim?
4. **Sufficiently specific to be useful?** Independent of checkability — even a checkable, evidence-consistent claim can be too generic to be a useful explanation (e.g., "costs went up because of hiring," with no indication of scale, timing, or which role, when the evidence package shows a headcount change of a very different magnitude than the variance would suggest). This check can downgrade an otherwise-Supported or otherwise-Contradicted result toward Insufficient if the claim's generality prevents a meaningful comparison to the evidence, even where Check 2 nominally found a relevant field.

**Output — one of three assessments, each carrying the full four-check trace:**
- **Supported** — worded as *consistent with corroborating financial evidence*, never as proof of causation. Requires the claim to pass Checks 1–4.
- **Contradicted** — cites the specific conflicting data point. Requires the claim to pass Checks 1, 2, and 4, and fail Check 3.
- **Insufficient / Requires Clarification** — states which check (1, 2, or 4) failed and why.

**Must not:**
- Default an uncheckable or vague claim to Supported or Contradicted (silence is evidence for neither).
- Invent a cause the evidence package cannot establish.
- Set, imply, or influence close approval/rejection status (D13).

**Limitations to state explicitly in the output text itself, not just in this Brief:** the system evaluates consistency between a claim and available financial data; it cannot establish causation, and a Supported result is not a determination that the claim is true.

**Acceptance criteria:**
1. A commentary with a specific, checkable, sufficiently specific claim consistent with the evidence package returns Supported, citing the corroborating field.
2. A commentary with a specific, checkable, sufficiently specific claim conflicting with the evidence package returns Contradicted, citing the conflicting field.
3. A commentary with no specific claim, an unclaimable claim type, or a claim too generic to compare against the evidence returns Insufficient, stating which of Checks 1/2/4 failed.
4. The full four-check trace is present in every output, for all three outcomes.
5. Output wording for Supported never uses causal/proof language — verified by direct text inspection.
6. Re-running Phase 6 on a **resubmitted, revised** commentary for the same observation produces an independent, fresh assessment across all four checks — it does not carry over or average against the prior version's result.

---

## D. Phase 5 — Finance Collaboration (Reinterpreted)

**Input:** Phase 6's Insufficient result and its specific failed-check reason (Section C, Checks 1/2/4), or Phase 4's "no confident match" result.

**Processing:** formats the specific failure reason into a short, plain-language explanation of what's missing or unclear — no independent judgment logic beyond restating Phase 6's (or Phase 4's) own stated reason in a form suited to a dashboard reader; Phase 5 does not re-derive or re-assess anything Phase 6 or Phase 4 already determined.

**Output:** a draft explanation, for the finance/CFO user's own reference (e.g., "no specific driver was identified for this movement" or "the claimed driver type cannot be checked against available fields" or "the explanation given is too general to compare against the evidence"). This is not a message to anyone — it is dashboard-displayed guidance the finance/CFO user can act on however they choose (including, at their discretion and entirely outside the product, contacting the Controller — the product has no role in that).

**Human interaction:** the finance/CFO user reads this draft, then either edits the complete commentary themselves (Section E/F) or manually reconciles an unmatched entry. No other human interaction exists in this phase.

**Failure states:** if Phase 5's draft cannot identify a specific missing element (e.g., the entry was simply blank), it states that plainly rather than fabricating a plausible-sounding gap description.

**Must not:**
- Create, address, format, or offer to send any communication to the Controller.
- Imply the product has a Controller-facing channel of any kind.

**Acceptance criteria:**
1. Draft output is never transmitted anywhere — no send action exists in the implementation.
2. Draft output correctly reflects Phase 6's specific failed check (1, 2, or 4) or Phase 4's no-match reason, not a generic template.
3. No Controller-addressed language, field, or UI element exists anywhere in this phase's implementation.

---

## E. Dashboard Specification (Minimum Required Changes)

A new review interface (added to the existing dashboard file, not a redesign of existing pages) must let the finance/CFO user:

1. See the imported commentary entry (currently active version) in full.
2. See which observation it was matched to (or its unmatched/no-match state).
3. See that observation's evidence package (reusing D11/D14 data already computed — no new calculation).
4. See the current Phase 6 validation result and its four-step trace.
5. Edit the **complete commentary text** in a single text field — no fragment/append/clarification-only field.
6. Submit the complete revised text, which triggers a fresh Phase 6 run (Section C, Criterion 6).
7. See the new validation result for the resubmitted version.
8. View all prior versions for that observation (original + each revision), each with its own stored validation result, clearly labeled and timestamped.
9. See which version, if any, is currently marked **Accepted**.
10. Explicitly mark the currently-displayed version as Accepted (a distinct human action — not implied by merely viewing a Supported result).

**Must not:** any Controller-facing element, login, or submission form. Only the finance/CFO user operates this interface.

---

## F. Data / Version Model

Each matched (or manually reconciled) observation carries a **Commentary Record**:

- `observation_id`
- `versions`: an ordered list, each entry containing:
  - `version_number`
  - `text` (the complete commentary text for that version — never a fragment)
  - `source`: `original_import` (v1, from the Controller's file) or `user_revision` (v2+, from the finance/CFO user)
  - `submitted_by`, `timestamp`
  - `validation_result`: the full Phase 6 output (assessment + four-step trace) for that specific version
- `accepted_version_number`: null until the finance/CFO user explicitly accepts one version

**Requirements:**
- The original imported version is never overwritten or deleted, regardless of how many revisions follow.
- Each revision is a new, complete version — not a patch applied to a prior version.
- Every version retains its own independently-computed validation result; a later version's result never overwrites an earlier version's stored result.
- Exactly one version per observation may be marked Accepted at a time; accepting a new version does not delete the version history.
- The complete Commentary Record is working-state data before close approval.
- When the close is approved, the **entire Commentary Record** is copied into the immutable D10 Close History snapshot for that approved close, including:
  - the original imported version;
  - every subsequent complete revision;
  - each version's stored validation result;
  - the `accepted_version_number`.
- No intermediate commentary version is discarded from the approved-close snapshot.
- The D10 snapshot is immutable after approval, consistent with D10's existing Close History behavior.

---

## G. Executive-Output Handoff

- Phase 7 (Executive Insight Engine) reads, for each observation with an accepted commentary, **only the `text` of the version marked `accepted_version_number`** — never an unaccepted, superseded, or AI-generated substitute.
- An observation with no accepted commentary at the time Phase 7 runs is a defect for the close-level Human Approval Gate to catch (per D13, the gate is where this is enforced) — Phase 7 itself does not decide whether to proceed; that decision belongs to the gate.
- The Board deck and HTML story must be traceable to specific accepted commentary versions — not to the original import if a revision was accepted instead.

---

## H. UAT Specification

Three principal-supplied commentary entries, each targeting the same flagged observation, satisfying the structural properties below (Architect defines structure; principal authors content — Validation Independence):

| Case | Required property | Expected Phase 6 result |
|---|---|---|
| A — Supported | Specific, checkable claim; evidence-package field corroborates it | Supported |
| B — Contradicted | Specific, checkable claim; evidence-package field conflicts with it | Contradicted |
| C — Insufficient | No specific claim, or claim type not covered by any evidence-package field | Insufficient / Requires Clarification |

**Correction-loop demonstration (required, using at least one failed case — B or C):**
1. Original commentary imported (v1) → Phase 4 matches it → Phase 6 returns Contradicted or Insufficient.
2. Finance/CFO user edits the complete commentary in the dashboard (v2) — this text is also principal-supplied, not Builder- or Architect-authored, to preserve Validation Independence on the correction path itself.
3. v2 submitted → Phase 6 re-runs independently on v2 (not influenced by v1's result).
4. v2's result displayed, distinguishable from v1's stored result.
5. Finance/CFO user marks v2 Accepted.
6. Accepted v2 text is confirmed as what would flow to Phase 7 (Section G) — verified by inspection, not narration.

Expected results for all cases are recorded before execution, per the Architect's standing Test procedure.

---

## I. Builder Package

**Scope of change:**
- New module(s) implementing Phase 4 (matching) and Phase 6 (validation) logic — naming/structure at Builder's discretion, documented in the Active File Manifest once built.
- Phase 5's draft-generation logic, reusing Phase 6's failure output as its sole input (no independent logic beyond formatting the specific reason).
- Dashboard additions to the existing dashboard file per Section E — additive, not a redesign of existing pages.
- A persistence mechanism for the Commentary Record / version model (Section F), including capture of the **complete version history in the immutable D10 Close History snapshot at close approval**.

**Acceptance criteria:** the union of Sections B, C, D, E, F, G's numbered criteria above.

**Required Builder regression evidence:**
- A separate, Builder-authored fixture (different observation, different commentary text from the principal's UAT set) exercising all three outcomes plus one correction-loop pass, proving non-regression only — explicitly not cited as genericity evidence, per the Validation Independence Principle.

**Explicit out of scope:**
- Any Controller-facing interface, login, submission form, or outbound communication of any kind.
- Sending Phase 5's draft anywhere.
- The close-level Human Approval Gate's interactive control (`st.button` or equivalent) — remains separately-scoped open technical debt (Handbook Section 10).
- Phase 7/8 modification beyond the input-source change in Section G.
- Multi-observation-per-entry or multi-entry-per-observation edge cases beyond what's needed to prove non-hardcoding.
- Redesign of D10, D11, D12, or D14.

---

## J. Independent Test Package

**Validation Independence applies directly here:** Builder must not author, extend, or tune the UAT commentary set (Section H) used to prove Phase 4/6 genericity. That set is principal-supplied. Builder's own fixture (Section I) proves non-regression only and is never substituted for this evidence.

**What independent Test must verify:**
1. Phase 4 correctly matches (or correctly returns no-match for) each of the three principal-supplied UAT commentary entries against the real observation register for the target close.
2. Phase 6 returns Supported for Case A, Contradicted for Case B, and Insufficient for Case C — each with the full four-check trace (Section C) and citing the specific corroborating/conflicting/failed-check field.
3. The full correction-loop demonstration (Section H): original commentary → Phase 6 result → finance/CFO-user-supplied revision → independent Phase 6 re-run on the revision → both results retained and distinguishable → Accepted marking → confirmed handoff to Phase 7 per Section G.
4. Phase 5's draft output, where triggered, correctly reflects the specific failed check — not a generic template — and no send/transmission path exists anywhere in the implementation (verified by code inspection, not narration).
5. No Controller-facing element exists anywhere in the delivered dashboard changes (verified by direct inspection of the delivered UI code, not by Builder's description of it).

**Evidence Test must produce:**
- Predictions for each of the above, recorded in writing before execution — per the Architect's standing Test procedure (Architect Instructions, Section 7).
- Actual execution output (not narration) for each item, run against the principal-supplied UAT set and the real (or agreed controlled-fixture) target observation — see Section 13, Item 3.
- A record of who ran the test and confirmation they did not construct or see the UAT commentary content in advance if that content was authored by someone other than the tester (standard Validation Independence disclosure).

**When this becomes sufficient for a "Verified" claim:** only once both Builder's regression evidence (Section I) and this independent Test evidence exist and have been reviewed by the Architect — matching the standard already applied to D11. Neither alone is sufficient for a genericity claim on Phases 4–6 or for moving D13 off "Planned."

---

## Resolution of v3 Open Items

The following items are resolved and are no longer implementation ambiguities:

1. **Commentary Record persistence relative to D10:** the complete Commentary Record — original version, all revisions, all validation results, and the accepted-version identifier — is captured in the immutable D10 Close History snapshot when the close is approved. Intermediate versions are retained.
2. **Commentary-file format:** fixed to `Commentary.xlsx`, one `Commentary` sheet, with exactly `Commentary_ID` and `Commentary_Text` as required columns.
3. **Target observation and UAT commentary content:** remain principal-supplied test inputs under Section H. They are test-data dependencies, not unresolved product-design questions.

*Per the Document Delivery Standard, this is the complete v4 Brief, ready to save to `governance/builder_briefs/` as-is, superseding v1, v2, and v3 in full.*
