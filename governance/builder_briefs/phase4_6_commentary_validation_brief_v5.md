# Builder Brief — Phases 4–6: Commentary Matching, Finance Collaboration, Explanation Validation

**Status:** Active — v5 (supersedes v4 in full). Activated per principal decision following the v4 correction cycle's acceptance (implementation-complete, regression-verified, canonical-synced at commit `789351b`). v4's implementation is not reopened or redone by this activation — v5 adds new requirements on top of it. v5's own acceptance criteria are not yet implemented.
**Governs (once active):** Implementation of Phase 4 (Commentary Matching), Phase 5 (Finance Collaboration), Phase 6 (Explanation Validation), and the minimum Dashboard changes required to make the workflow operable
**Constrained by:** D13 (Machine Recommends, Human Decides) — Planned, becomes Verified only against this Brief's evidence
**Does not reopen:** D10, D11, D12, D14 — all remain Verified and unmodified.
**Prerequisite Handbook state:** v2.6 (Cost Structure Investigation Views / D14 complete and Verified)
**Author:** Architect
**Precedence:** Project Handbook (v2.6) > this Brief (once active) > archived Briefs, per Handbook Section "Source of Truth"

---

## Revision Note (v4 → v5)

**Trigger:** the official challenge page states every submission must be built against the required Northwind sample dataset, so judges can validate submissions consistently, and gives no indication that judges will supply a candidate-specific `Commentary.xlsx` alongside it. The principal identified this as a real judging-risk gap in v4's assumptions: v4 treated `Commentary.xlsx` as an expected input to the workflow generally, when the challenge's actual judging model cannot be assumed to provide one.

**Product decision (principal, this revision):** `Commentary.xlsx` becomes an **optional** capability layered on top of the core workflow, not a prerequisite for it. Three consequences, all new to v5:

1. **The dashboard, financial analysis, and executive narrative must be fully functional with the required dataset alone and no commentary file supplied at all.** This was already true by construction in the v4 implementation for the specific case of zero D11 flags (independently confirmed by the Architect via AppTest), but had never been tested or required for the case that actually matters here: **flags exist and no commentary file was ever supplied.**
2. **The executive narrative's treatment of flagged observations now has three distinct required states, not two:**
   - No flags at all (commentary file present or absent is irrelevant) → normal narrative, unchanged from pre-Phase-4-6 behavior.
   - Flags exist and commentary was supplied → existing v4 Section G behavior (accepted commentary reported), **plus** any flagged observation that still has no accepted commentary despite a file having been supplied must be explicitly reported as **unresolved** — not silently omitted.
   - Flags exist and no commentary file was supplied at all → the narrative must explicitly state that observations were identified but no Controller commentary was supplied, and that they remain unexplained. The system must not invent an explanation to fill the gap.
3. Section G's prior framing — "an observation with no accepted commentary... is a defect for the Human Approval Gate to catch" — assumed commentary was always expected, making its absence anomalous. That assumption no longer holds for the no-file case and is rewritten below.

**What does not change:** Sections C (Phase 6 logic), D (Phase 5), F (version model), H (UAT), and J (Independent Test package) are unaffected by this decision and are reproduced below unchanged from v4, per the Document Delivery Standard's requirement that a superseding document be complete, not a diff. Sections A, B, E, G, and I are revised. A new Section K is added.

*(Prior revision notes — v1 through v4 — are preserved in the archived v4 document and are not repeated here; see `governance/builder_briefs/` archive. v4's implementation, including two Architect-review correction rounds — claim-type coverage genuinely wired to D14 data, a narrative wording defect fixed — is complete, regression-verified (49/49, independently reproduced), and canonical-synced at commit `789351b`. That work is not reopened by this activation.)*

---

## A. Current State

**Already existing (Verified, unmodified by this Brief):**
- Dataset intake and canonical resolution (D12).
- D11 detection: Phase 2 (historical-revision diff) and Phase 3 (plausibility/headcount-band), producing the observation register for a close.
- D14 investigation views: Department × Cost Category and company-wide Cost Category-only breakdowns, giving a human investigator the detail a flagged observation needs.
- Existing dashboard tabs/pages (IA #1–9, per Handbook Section 3), Close Validation Status page.
- Executive narrative generation (Phase 7, reused) and the (not-yet-built, separately scoped) HTML/PPTX output (Phase 8).
- **The full challenge workflow using only `Northwind_Sample_Dataset.xlsx`** — dataset → dashboard → financial analysis → narrative → Board output — **must work correctly with zero dependency on `Commentary.xlsx` ever being present.** This is now an explicit, load-bearing product requirement (Revision Note above), not an incidental property of how Phase 4–6 happened to be built.

**To be built (this Brief):**
- Commentary-file intake using the fixed `Commentary.xlsx` contract defined in Section B — **optional**, not required to run the core workflow.
- Phase 4: commentary matching against the observation register (only runs at all if a commentary file is supplied).
- Phase 6: commentary validation against a bounded evidence package.
- Phase 5: draft output for the finance/CFO user's own reference (not sent anywhere).
- Dashboard: a review/edit/resubmit/accept interface for the finance/CFO user (Section E), which must not be required for the dashboard's other pages to function.
- Complete-commentary resubmission and revalidation: the resubmit action triggers an independent, fresh Phase 6 run on the full revised text (Section C, Criterion 6).
- A version/data model distinguishing original, revised, and accepted commentary states (Section F).
- **Three-way executive-narrative handoff logic** (Section G, rewritten this revision): accepted-commentary reporting, unresolved-despite-commentary reporting, and no-commentary-supplied reporting, each distinguishable and none silently omitted.

---

## B. Phase 4 — Commentary Matching

**Input:**
- The current close's observation register (every D11 flag: department, category, period, flag type, $/% variance).
- The imported commentary file, parsed into discrete commentary entries — **only if one was supplied.**

**Commentary-file structure — fixed product requirement, optional presence:**
- The Controller *may* supply a separate Excel workbook named `Commentary.xlsx` as part of the close package. Supplying it is optional; the core workflow (dataset intake through executive output) must run correctly whether or not one is present.
- When supplied, the workbook contains exactly one required sheet named `Commentary`, with exactly two required columns: `Commentary_ID` and `Commentary_Text`. Each populated row is exactly one complete commentary entry. No observation ID, department/category key, validation status, AI assessment, or correction field belongs in the input file. Blank commentary rows are not valid input entries.
- When **not** supplied, Phase 4/5/6 simply do not run for this close. This is not an error state and must not be presented as one — no warning, no degraded-mode messaging beyond a neutral statement that no commentary was provided (see Section G for how this is represented downstream, in the narrative, not as a dashboard error).
- This fixed format (when a file is supplied) is part of the product contract. Builder must not choose an alternative file format or invent additional required columns, and must not make the file's absence trigger any error path.
- An entry may or may not explicitly name a department/category/period. Matching logic must handle both explicit and inferable references.

**Matching logic:** unchanged from v4 — for each commentary entry, determine which observation in the register (if any) it refers to, based on identifiable references within the entry's text, not on plausibility alone. The complete, unmodified commentary entry text is what gets matched and carried forward.

**Output:** unchanged from v4 — each commentary entry resolves to either a single matched observation ID, or an explicit "no confident match" result. A forced match with weak support is a defect, not a feature.

**Failure states:** unchanged from v4 for the case where a file was supplied (no-confident-match handling, open-uncommented-flag visibility). **New:** the case where no file was supplied at all is not a failure state — it is a normal, expected configuration that Section G must represent explicitly downstream.

**Acceptance criteria:**
1. A commentary entry with an explicit, correct reference matches its target observation.
2. A commentary entry with only inferable (non-explicit) references still matches correctly when the inference is well-supported.
3. An entry with no well-supported match returns "no confident match," not a forced guess.
4. The full, unaltered entry text is preserved and carried into Phase 6 — matching never edits or shortens it.
5. **New:** with no commentary file uploaded, the dashboard's Commentary Review section and every other existing page render correctly with zero exceptions — confirmed by actual execution (AppTest or equivalent), not source inspection alone. (The Architect has already confirmed this for the zero-flag case; this criterion requires confirming it for the flags-exist case too.)

---

## C. Phase 6 — Explanation Validation

*(Unchanged from v4.)*

**Input:** the complete commentary text for the observation under review (whichever version is currently under review — original or a resubmitted revision, per Section F) and that observation's evidence package (below).

**Evidence package** — the bounded set of financial data Phase 6 is allowed to check a claim against; reuses D11/D14 output, computes nothing new:
- Department, cost category, current period, prior period, current value, prior value, $ variance, % variance.
- Which check flagged it (Phase 2 or Phase 3) and the threshold crossed.
- Department headcount current vs. prior, where headcount-band-relevant.
- The corresponding D14 Department × Cost Category breakdown row, where relevant.
- **Never** the raw dataset, other observations, or other periods. If Phase 6 needs a field not present here, the required output is Insufficient — not an expanded data pull.

**Validation logic — four distinct checks, all four must be visible in the output, not collapsed into a bare label:**
1. **Specific claim present?** Does the commentary text contain a specific explanation at all? If not → Insufficient, stop.
2. **Checkable against available evidence?** Does the evidence package contain a field capable of corroborating or contradicting *this specific claim type*? If not checkable → Insufficient, stop.
3. **Supported or contradicted?** If checkable, does the actual evidence-package value corroborate or conflict with the claim?
4. **Sufficiently specific to be useful?** Independent of checkability — even a checkable, evidence-consistent claim can be too generic to be useful. This check can downgrade an otherwise-Supported or otherwise-Contradicted result toward Insufficient if the claim's generality prevents a meaningful comparison to the evidence.

**Output — one of three assessments, each carrying the full four-check trace:**
- **Supported** — worded as *consistent with corroborating financial evidence*, never as proof of causation. Requires the claim to pass Checks 1–4.
- **Contradicted** — cites the specific conflicting data point. Requires the claim to pass Checks 1, 2, and 4, and fail Check 3.
- **Insufficient / Requires Clarification** — states which check (1, 2, or 4) failed and why.

**Must not:**
- Default an uncheckable or vague claim to Supported or Contradicted.
- Invent a cause the evidence package cannot establish.
- Set, imply, or influence close approval/rejection status (D13).

**Acceptance criteria:** unchanged from v4, Criteria 1–6.

---

## D. Phase 5 — Finance Collaboration (Reinterpreted)

*(Unchanged from v4.)*

**Input:** Phase 6's Insufficient result and its specific failed-check reason, or Phase 4's "no confident match" result.

**Processing:** formats the specific failure reason into a short, plain-language explanation — no independent judgment logic.

**Output:** a draft explanation for the finance/CFO user's own reference. Not a message to anyone; never addressed to, formatted for, or sendable to the Controller.

**Acceptance criteria:** unchanged from v4, Criteria 1–3.

---

## E. Dashboard Specification (Minimum Required Changes)

A new review interface (added to the existing dashboard file, not a redesign of existing pages) must let the finance/CFO user, **when a commentary file has been supplied**:

1. See the imported commentary entry (currently active version) in full.
2. See which observation it was matched to (or its unmatched/no-match state).
3. See that observation's evidence package.
4. See the current Phase 6 validation result and its four-step trace.
5. Edit the **complete commentary text** in a single text field.
6. Submit the complete revised text, triggering a fresh Phase 6 run.
7. See the new validation result for the resubmitted version.
8. View all prior versions for that observation, each with its own stored validation result, clearly labeled and timestamped.
9. See which version, if any, is currently marked **Accepted**.
10. Explicitly mark the currently-displayed version as Accepted.

**New this revision:**

11. **When no commentary file has been supplied, this entire section must not block, degrade, or add error states to any other part of the dashboard.** The observation register (already-existing D11/D14 output) remains visible on its own, exactly as it does today. A neutral, non-alarming indication that no commentary has been imported this session is acceptable (already present in the v4 implementation: "No commentary imported yet this session"); nothing further is required of the dashboard itself for this case — the narrative-level representation belongs to Section G, not to a dashboard warning.

**Must not:** any Controller-facing element, login, or submission form. Only the finance/CFO user operates this interface. The absence of a commentary file must never be presented as an error, misconfiguration, or missing-required-input state anywhere in the dashboard.

---

## F. Data / Version Model

*(Unchanged from v4.)*

Each matched (or manually reconciled) observation carries a **Commentary Record**: `observation_id`, an ordered `versions` list (each with `version_number`, complete `text`, `source`, `submitted_by`, `timestamp`, `validation_result`), and `accepted_version_number` (null until explicitly accepted). The original imported version is never overwritten; each revision is a new complete version; every version retains its own independently-computed validation result; exactly one version may be Accepted at a time.

---

## G. Executive-Output Handoff (Rewritten this revision)

Phase 7 (Executive Insight Engine) must represent flagged observations in one of three distinct ways, determined by the combination of (a) whether the close has any D11 flags at all, and (b) whether a commentary file was supplied this close. **None of the three may be silently collapsed into another; the system must never invent an explanation to fill a gap in any of them.**

1. **No flags at all.** Commentary-file presence or absence is irrelevant. The narrative is generated exactly as it was before Phase 4–6 existed — unchanged, byte-identical prompt behavior for this case (already confirmed by the Architect for the existing implementation).

2. **Flags exist and a commentary file was supplied.**
   - For each flagged observation with an **accepted** commentary version: report it using that accepted version's text only (unchanged from v4) — never an unaccepted, superseded, or AI-generated substitute.
   - For each flagged observation that still has **no accepted commentary** — whether because it was never matched, matched but never resubmitted past Insufficient/Contradicted, or simply never reviewed — the narrative must explicitly report it as **unresolved**: identified, commentary process attempted, no accepted explanation exists yet. This must be worded distinguishably from case 3 below (a commentary process happened but didn't conclude, versus no process happened at all).
   - The close-level Human Approval Gate remains where this is ultimately meant to be caught before publication (per D13); this requirement governs what Phase 7 does if it runs anyway (e.g., during standalone testing before the Gate exists) — it must still represent the true state, not omit it.

3. **Flags exist and no commentary file was supplied at all.** Every flagged observation must be reported explicitly: identified by Phase 2/3, no Controller commentary was supplied this close, and it remains unexplained. The system must not invent, infer, or guess at a plausible cause to fill this gap — the narrative states the absence of an explanation as a fact, not a problem to be smoothed over.

**Must not, all three cases:**
- Silently omit any flagged observation from the narrative's awareness, regardless of which of the three states applies.
- Blur the wording between "unresolved despite a commentary process" (case 2) and "no commentary process occurred" (case 3) — a reader of the narrative should be able to tell which situation produced an unexplained item.
- Invent a cause, driver, or explanation for any observation the evidence package and commentary process did not actually establish.

The Board deck and HTML story must be traceable to whichever of the three representations actually applied to each observation.

**Acceptance criteria:**
1. Case 1 (no flags) produces a prompt byte-identical to pre-Phase-4-6 behavior, regardless of commentary-file presence.
2. Case 2 (flags + file): accepted commentary reported correctly (unchanged v4 behavior), **and** any observation without an accepted commentary is explicitly reported as unresolved, not omitted.
3. Case 3 (flags + no file): every flagged observation is explicitly reported as identified-but-unexplained-due-to-no-commentary-supplied — verified by direct inspection of actual rendered prompt/narrative output, not narration.
4. Cases 2's "unresolved" and Case 3's "unexplained, no commentary supplied" are lexically distinguishable in the actual output text.
5. No invented cause, driver, or explanation appears anywhere in Case 2's unresolved items or Case 3's unexplained items — verified by direct text inspection.

---

## H. UAT Specification

*(Unchanged from v4.)*

Three principal-supplied commentary entries, each targeting the same flagged observation:

| Case | Required property | Expected Phase 6 result |
|---|---|---|
| A — Supported | Specific, checkable claim; evidence-package field corroborates it | Supported |
| B — Contradicted | Specific, checkable claim; evidence-package field conflicts with it | Contradicted |
| C — Insufficient | No specific claim, or claim type not covered by any evidence-package field | Insufficient / Requires Clarification |

Correction-loop demonstration (unchanged, required, using at least one failed case): original commentary → Phase 6 result → finance/CFO-user-supplied revision → independent Phase 6 re-run → distinguishable results → Accepted marking → confirmed handoff to Phase 7.

**New for v5, once active:** the principal-supplied UAT set should also allow exercising Section G Case 3 directly — i.e., confirming the target close's UAT run can be repeated with the commentary file withheld entirely, to verify the "unexplained, no commentary supplied" narrative path against the same real flagged observation used for Cases A/B/C.

---

## I. Builder Package

**Scope of change (updated this revision):**
- New module(s) implementing Phase 4 (matching) and Phase 6 (validation) logic.
- Phase 5's draft-generation logic.
- Dashboard additions per Section E, **explicitly not gating any other dashboard functionality on commentary-file presence.**
- Persistence mechanism for the Commentary Record (Section F), including capture in the immutable D10 Close History snapshot at close approval.
- **New: the three-way Section G handoff logic**, replacing the current binary (commentary-present-and-accepted vs. absent) framing with the three explicit cases above.

**Acceptance criteria:** the union of Sections B, C, D, E, F, G's numbered criteria above.

**Required Builder regression evidence (expanded this revision):**
- The existing Builder-authored fixture (Section I, v4) proving Phase 4/5/6 non-regression.
- **New:** a fixture run covering flags-exist-with-no-commentary-file-supplied, confirming (a) the dashboard renders cleanly with zero exceptions, and (b) the Phase 7 prompt contains the explicit "identified, no commentary supplied, unexplained" language for every such observation, with no invented cause.
- **New:** a fixture run covering flags-exist-with-a-file-supplied where at least one flagged observation deliberately has no accepted commentary, confirming it is reported as "unresolved" (Section G, Case 2) and is lexically distinct from the no-file case's wording.

**Explicit out of scope:** unchanged from v4 — no Controller-facing interface, no send/transmit path, no Human Approval Gate control, no Phase 7/8 modification beyond the Section G input-source logic, no redesign of D10/D11/D12/D14.

---

## J. Independent Test Package

*(Unchanged from v4.)* Builder must not author or tune the UAT commentary set (Section H). Independent Test verifies Phase 4/6 correctness against the principal-supplied set, the correction loop, Phase 5's draft behavior, and the absence of any Controller-facing element — with predictions recorded before execution and actual output as evidence. **New scope, once v5 is active:** Independent Test also verifies Section G's three-way narrative behavior, including the no-commentary-file case, using the same discipline (predictions recorded before execution, actual rendered output as evidence).

---

## K. Judging-Model Rationale (new section, v5)

This section exists to make the underlying business reasoning durable and auditable, separate from the technical requirements above, since it originates from an external constraint (the challenge's judging model) rather than an internal architectural decision.

- The official challenge page states every submission must be built against the required Northwind sample dataset so judges can validate submissions consistently, and does not state that judges will supply a candidate-specific commentary file.
- Treating `Commentary.xlsx` as mandatory would risk the core workflow (dataset → dashboard → narrative → Board output) failing or degrading during judging if no such file is ever provided — an unacceptable risk to the graded submission's baseline functionality.
- Treating it as optional preserves the differentiator (commentary matching/validation, D13's "Machine Recommends, Human Decides" loop) as an additional demonstrated capability, without making the base submission dependent on an input the judging process may never supply.
- This is a product-scoping decision made by the principal in response to an external requirement, not a reopening of D10/D11/D12/D14, and not a reversal of any Phase 4–6 architecture already built — it changes what's *required* to run, not how Phase 4–6 behaves when it does run.

---

*Per the Document Delivery Standard, this is the complete v5 Brief, ready to save to `governance/builder_briefs/` and commit, superseding v4 as the Active governing Brief for Phases 4–6. v4's implementation is unaffected — it is complete, regression-verified, canonical-synced, and remains the foundation v5 builds on.
