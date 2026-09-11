# Architect Report — Product Operability Gaps (Gaps 1-4)

**Type:** Architect Documentation & Alignment Report (evidence-pointer convention — see Handbook Section 9, "Architect Documentation & Alignment Report" rows).
**Status of the recommendations below:** Gap 1's finding and recommendation stand and are fully incorporated into `governance/builder_briefs/builder_brief_operability_gaps_1_2_3.md`. Gap 2 and Gap 3's *code findings* (what currently exists) stand unchanged and are relied on directly by that Brief. Gap 2 and Gap 3's *scope recommendations* below (the narrower options) were superseded by an explicit principal decision electing the fuller scope for both — see the Brief for the authoritative, currently-governing scope. Gap 4's finding (no gap, correctly deferred) stands unchanged.
**Basis:** Fresh clone of canonical `main`, HEAD `3439378926ed27df43ea4b4ee4f0acce1c0ac5b8` at the time of this report (superseded by later commits; code citations below reflect that HEAD, re-verified against current HEAD `b745d48f72bbb030e337802043d80cffaa889f52` where the Brief relies on them).
**Retained per:** Handbook Section 2, Principle 8 (Handbook records conclusions and points to evidence — this report is that evidence, not reproduced in the Handbook body).

---

Architect Documentation & Alignment Report — Product Operability Gaps (Gaps 1–4)

To: PM / Project Advisor
From: Architect
Basis: Fresh clone of canonical main, HEAD 3439378926ed27df43ea4b4ee4f0acce1c0ac5b8 (confirmed matching the Handbook's recorded HEAD), direct code execution, not narration or memory.

Preliminary finding, cross-cutting, reported before the four gaps because it affects how several of them should be read:

Direct diff (git diff 628a737 HEAD) shows the repository has moved since the Handbook's last-documented commit in ways the Handbook (v2.15, itself present at HEAD) does not yet reflect:

commentary_workflow.py and Northwind_Financial_Dashboard.py now contain the audit-trail addendum (match_method/match_basis on CommentaryRecord, persisted in to_dict(), displayed in the Commentary Review UI as "Matched via: …") — this is now canonical, contradicting the Handbook's own text (Section 13) which still says this addendum is "not yet canonical-synced." This is a genuine documentation-drift instance: the Handbook's claim about its own commit is stale relative to that same commit's actual contents.
northwind_narrative_prompt.md now contains Rule 10, the no-invention/accepted-commentary boundary described in the same addendum — also canonical, also under-recorded.
A new build_test/phase4_semantic_reconciliation_demo.py exists at HEAD.

This does not change any Decision Log entry or D13's Implementation Status. It is a documentation-currency gap, recorded as such, not silently corrected here (Handbook editing is a separate, explicit act).

Gap 1 — Latest Available Period and Processing Workflow
1. Product interpretation

The latest available period should be selectable in the general dashboard-wide period selector (it drives most pages' current/prior comparison), and the Close Validation Status page's Phase 2/3 processing target should be transparent and, ideally, consistent with whatever the user believes they are reviewing. There is no approved product requirement that the close-processing workflow track an arbitrary sidebar selection — but there is an implicit requirement that a Controller/Finance user not be misled about which period is actually being validated.

2. Current capability

Two independent period-selection mechanisms exist, and they are not the same thing:

Sidebar current_period selector (Northwind_Financial_Dashboard.py lines 204–208): built from [p for p in period_order if period_order.index(p) > 0] (drops only the very first period, which has no prior for comparison). Directly executed against the canonical dataset: selectable_periods = ['Q2 FY2024' … 'Q4 FY2026'], defaulting to 'Q4 FY2026'. The true latest period (Q4 FY2026) is selectable and is the default. Any earlier period, including Q3 FY2026, is also selectable here and drives most of the dashboard's other tabs (Revenue Performance, Cost Structure, Headcount, BvA, Region/Product views).
Close Validation Status processing target: run_phase3_plausibility_review() is called (dashboard line ~545) with no target_period argument. _resolve_target_period() (close_validation.py line 259) falls back to period_order[-1] whenever target_period is None — i.e., it always resolves to the dataset's actual latest quarter (Q4 FY2026), regardless of what the sidebar's current_period is set to. Phase 2 similarly runs against the full current dataset vs. the latest approved prior close, not against whatever period the sidebar has selected.

So the sidebar selector is real and does include the latest period — but it does not govern the close-processing workflow at all. Selecting any period other than the true latest in the sidebar has zero effect on which period Phase 2/3, the observation register, or Commentary Review process; they are permanently pinned to the dataset's actual last quarter.

A newly-confirmed, more precise defect beyond what the Handbook's existing Known Technical Debt entry records: the Commentary Review section's Phase 6 evidence-package construction (hc_current_df, hc_prior_df, _dept_category_breakdown_for(), dashboard lines 772–784) is built from current_period (the sidebar selection), not from the observation register's own period (which is always the true latest). When current_period happens to equal the true latest (the default), this is invisible. When a user selects any other period in the sidebar — which the UI freely permits — Phase 6 validates Q4 FY2026 observations against headcount/category-breakdown data pulled for whatever earlier period is selected instead. This is a real correctness defect, not merely a UX/visibility issue, and it was not previously isolated at this level of precision in the Handbook.

This matches, and sharpens, the existing Known Technical Debt entry ("Dashboard sidebar period selector does not affect the Close Validation Status page"). The PM's framing ("the latest period was not available for selection") is imprecise — the latest period is selectable — but the underlying architectural problem the PM is pointing at is real: the sidebar selector's relationship to the close-processing workflow is not what a demonstrator would reasonably expect, and in the evidence-package case, the mismatch is silently wrong rather than merely inert.

3. Actual gap

Two distinct things, previously conflated:

(a) Decoupling gap (known, now precisely confirmed): Close Validation Status Phase 2/3 ignore the sidebar entirely; always process the true latest period. Cosmetically inert as long as the user leaves the sidebar at its default.
(b) Newly identified correctness defect: the Phase 6 evidence package used to validate commentary against Q4 FY2026 observations is built from whatever period the sidebar happens to show, which can silently diverge from Q4 FY2026 if the user has navigated elsewhere in the dashboard first.
4. Gap classification

(a) Workflow gap / documentation issue (already substantially recorded in Known Technical Debt; the "terminal period" framing was not an existing product concept and should not be introduced).
(b) Implementation gap (genuine defect) — newly confirmed, not previously isolated at this precision in the Handbook.

5. Existing architecture to preserve
The "process the dataset's actual latest close" default behavior for Phase 2/3 is architecturally sound and should not be redesigned — it matches D10's "canonical object is the Approved Financial Close" model; there is no approved concept of processing an arbitrary historical period as "the close."
The sidebar's general-purpose period explorer for the other eight dashboard pages is working as intended and should not be removed or restricted.
6. Architectural implications

None to the close-processing target-period logic itself. The evidence-package construction (b) needs to key off the observation register's own Period field per-observation, not off the sidebar's current_period — this is a scoping/wiring fix, not an architectural change.

7. Dependencies

Gap 2 (Phase 4–6 visibility) inherits this: the Commentary Review section's correctness depends on (b) being fixed, since Phase 6's assessment (Supported/Contradicted/Insufficient) is what gets surfaced to the Controller.

8. Options and trade-offs
Option A (minimal): wire the evidence-package construction to the observation register's own period rather than the sidebar's current_period, and leave the sidebar/Close-Validation decoupling as documented, accepted behavior (no new concept, no new UI).
Option B: introduce an explicit, labeled "period being closed" indicator on the Close Validation Status tab, distinct from the general sidebar, so users are never in doubt which period Phase 2/3/4–6 concern. Slightly more UI surface, closes the visibility question at its root.
Option C: make the close-processing target period configurable — rejected; this would introduce a new, unapproved "process an arbitrary historical period as a live close" capability with no defined lifecycle, conflicting with D10.
9. Architect recommendation

Fix (b) as a minimum correctness item (Option A component). Adopt Option B's labeling as a small, additive clarity improvement — not a new screen, just a caption/label already partially present (the tab's own caption text). Do not make the target period configurable (reject Option C).

10. E2E impact

Does not block Scenario 1/Scenario 2 as long as the sidebar is left at its default (which it is, out of the box). It becomes a real risk the moment a demonstrator navigates the dashboard before reaching Commentary Review — a real and likely sequence in a live demo.

11. Verification impact

Does not affect D13 as currently scoped (Section H/J UAT targets the matching/validation logic itself, using a controlled fixture, not sidebar navigation). But it should be an explicit precondition/caveat in the Section H/J UAT instructions: the UAT must be run with the sidebar at its default (latest) period, or the evidence-package defect will contaminate results in a way unrelated to what's being tested.

12. Implementation requirement

Yes, for (b) — small, scoped fix. (a) requires no implementation change, only accurate documentation (it's intended behavior, already substantially recorded).

13. If implementation is required

Before Builder receives a task: confirm with the principal that (b) is accepted as a genuine defect (not a reinterpretation of intended behavior), and specify precisely — evidence-package construction must derive its period from obs_row['Period'] (the observation register), never from the sidebar's current_period.

14. If implementation is not required (for part (a))

Documented as accepted, intentional architecture. Update the Known Technical Debt entry to reflect the more precise mechanism found here rather than leaving the "terminal period" framing unaddressed.

Gap 2 — Phase 4–6 Results and User Workflow
1. Product interpretation

Observation → Commentary → Reconciliation → Validation should be visible to the Finance/CFO user (not the Controller, who doesn't operate the dashboard) as: which observation, what commentary, how it was matched, what Phase 6 concluded, and why.

2. Current capability

Substantially more complete than the PM's observation suggests. Direct inspection of the Commentary Review section (Northwind_Financial_Dashboard.py, lines ~703–983) confirms:

Observation register table — rendered directly, every flagged item.
Per-observation expander, titled {Department} / {Category} ({Period}) — {status_label}, showing: the observation itself (before/after/delta), the current commentary text and its version number/source, "Matched via: {method}" (deterministic/semantic/manual — the audit-trail addendum, now canonical per the preliminary finding above), the Phase 6 result headline (**Phase 6 result: {assessment}** — i.e. Supported/Contradicted/Insufficient literally rendered), the reason text, the cited evidence field/value, and all four validation sub-checks as individual metrics.
Version history table with accepted-version marker.
Accepted-commentary preview — the exact lines that will flow into the Phase 7 narrative handoff, shown before generation.
Human Approval Gate status and controls, explicitly decoupled from Phase 6's assessment per D13.

This is a real, working, fairly complete Observation → Commentary → Match → Validation → Accept chain, already operable in the live dashboard — not merely underlying logic with no surface.

3. Actual gap

Two genuine gaps remain, narrower than "results aren't visible":

Correctness dependency on Gap 1(b): the visible Phase 6 result can be wrong if the sidebar isn't at the default period (see above).
No consolidated summary view: the visibility that exists is per-observation (inside individual expanders), not a single Observation/Commentary/Match/Validation table a Controller/CFO could scan at a glance across all flagged items in one place. This is a genuine, if modest, information-architecture gap — a real user could reasonably need to open every expander to get the full picture.
4. Gap classification

Workflow gap (a), Documentation/verification gap (the "not visible" claim itself), and a genuine minor UI/information-architecture gap (the missing consolidated view).

5. Existing architecture to preserve

The per-observation expander model, the accepted-commentary preview, the Human Approval Gate's independence from Phase 6 outcome, and the existing Commentary Record versioning model should all be preserved unchanged.

6. Architectural implications

A consolidated summary table (if pursued) is purely additive — it reads from data already computed (observation_register, commentary_records) and introduces no new state, persistence, or data-model change.

7. Dependencies

Depends on Gap 1(b)'s correctness fix to be trustworthy.

8. Options and trade-offs
Option A: no change — the per-observation expanders already satisfy the product information requirement; treat "not sufficiently visible" as a demonstration-sequencing/evidence-gathering issue (i.e., go look at the actual live page) rather than a product gap.
Option B: add one small, additive summary table above the expanders (Observation | Commentary status | Match method | Phase 6 assessment) for at-a-glance scanning, without removing the detail expanders.
9. Architect recommendation

Option A is largely correct on the evidence — the underlying claim that Phase 4–6 results are "not sufficiently visible" is not well supported by direct inspection of the live code. Recommend the PM/Principal re-examine the actual live page (post Gap 1(b) fix) before authorizing any UI work. If, after that, a summary table is still wanted, Option B is minimal and low-risk.

10. E2E impact

No blocking impact — the underlying capability required for Scenario 1 already exists and renders.

11. Verification impact

None to D13's Section H/J UAT requirement, which concerns the correctness of the matching/validation logic, not its UI presentation.

12. Implementation requirement

Not required as a precondition of anything currently blocked. Optional (Option B) only if the PM, after direct observation of the current UI, still judges it insufficient.

13. If implementation is required

Define exact columns/scope for the summary table; confirm it must not become a second, divergent source of the same facts (single-source-of-truth risk).

14. If implementation is not required

Document as: current capability confirmed sufficient by direct inspection; PM's original observation attributable to either (a) not having exercised the live Commentary Review section, or (b) Gap 1(b)'s correctness defect making a result look wrong/absent in a specific navigation sequence.

Gap 3 — Analytical Rules, Thresholds and Governance
1. Classification of relevant values

Direct inspection of close_validation.py (lines 88–94):

DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD = 0.25 — Analytical definition. This threshold defines what the plausibility methodology itself considers "anomalous" and is cross-referenced by multiple downstream fixtures (Human Approval Gate Case 5, the register-semantics investigation fixture) as a fixed point of the methodology. Changing it silently would invalidate those fixtures — already flagged in memory as a standing principle.
DEFAULT_PLAUSIBILITY_HEADCOUNT_BAND = 2 — Analytical definition, same reasoning.
DEFAULT_EXCLUDED_CATEGORIES = ("Salaries & Benefits",) — Analytical definition, not business policy: it reflects a structural fact about the methodology (S&B has its own volume/rate bridge, so folding it into the generic QoQ plausibility check would double-count/misattribute), not a discretionary organizational choice.

None of the three read as genuine business policy in the sense of "an authorized finance user should be able to change this without a governed re-verification step" — they are load-bearing constants that downstream test evidence is built against.

2–3. Product / governance interpretation

Both run_phase3_plausibility_review() and the dashboard confirm these are accepted as function parameters with defaults, never overridden anywhere in the call chain — confirmed by direct grep: the dashboard's only references to headcount_band are to display the already-computed value (line 672) and to pass it through unchanged into the evidence package (line 790). No configuration surface exists anywhere in the dashboard.

4. Current architectural support

None for user-facing configuration. The values are read-only, displayed but not editable, anywhere in the live product.

5. Actual gap

No user-facing configuration mechanism exists. Separately: no explicit rule-version record exists in Close History's snapshot metadata — archive_close()'s metadata.json (close_history.py lines 181–191) captures pipeline_git_commit_hash (an indirect, code-level version pointer) but does not explicitly capture the threshold values (qoq_threshold, headcount_band, exclude_categories) actually used to produce that snapshot's flags. Reconstructing "what threshold produced this flag" today requires cross-referencing the commit hash against source history — technically possible, not explicit or auditable at a glance.

6. Gap classification

Governance issue (no explicit rule-version audit field) + Documentation issue (no stated classification of these constants as policy/definition/technical). Not a missing-configuration-screen product requirement — per the PM's own explicit instruction not to assume that.

7. Existing architecture to preserve

The constants must remain centrally governed, non-user-editable code values. The Validation Independence Principle's existing prohibition on silently changing DEFAULT_PLAUSIBILITY_QOQ_THRESHOLD (already recorded — direct edits would invalidate downstream fixtures) should not be weakened by introducing ad hoc user configuration.

8. Versioning/audit implications

If this is judged worth closing, the correct minimal fix is additive metadata only: record the actual qoq_threshold/headcount_band/exclude_categories values used into archive_close()'s metadata.json at archive time. This requires no new UI, no new configuration mechanism, and no reopening of D11. It simply makes an already-deterministic, already-fixed fact explicit and auditable per snapshot, rather than requiring commit-hash archaeology to reconstruct.

9. Workflow implications

None — Phase 3 behavior is unchanged either way.

10. E2E impact

None. Neither scenario is blocked by the absence of a config screen or explicit rule-version metadata.

11. Options/trade-offs
Option A (recommended): classify the three constants explicitly in the Handbook as Analytical Definition (centrally governed, not user-configurable) — a documentation-only decision, closing the "unclear governance model" concern without any code change. Optionally add the metadata capture described in (8) as a small, additive Builder item.
Option B (reject): build a settings/configuration screen — explicitly out of scope per the PM's own non-goals list (Section 13), and would create exactly the "changing a load-bearing analytical constant outside the governed re-verification path" risk the Validation Independence Principle exists to prevent.
12. Architect recommendation

Option A. Document the classification; optionally close the audit-metadata gap as a small, additive, non-UI Builder item if the PM/Principal judges it worth doing before the write-up.

13. Whether implementation is required

Not for the classification (documentation-only). Optionally, yes, for the metadata-capture addition — small, low-risk, additive.

14. Whether user-facing configuration is actually required

No. Explicitly recommend against it.

15. If deferred, recommended roadmap placement

The metadata-capture addition, if pursued, fits naturally alongside the existing audit-trail addendum (which already touches Close History serialization) rather than as a separate initiative.

Gap 4 — Closed Period Correction / Reopen / Reprocess
1–3. Product interpretation / current architectural support

Direct inspection confirms: archive_close() (close_history.py line 168) raises FileExistsError on any attempt to write a snapshot for a period label that already exists — snapshots are structurally immutable, by design, consistent with D10. A grep across Northwind_Financial_Dashboard.py, close_history.py, close_validation.py, and commentary_workflow.py for reopen/reprocess/correction logic returns nothing beyond the already-known, narrower, in-session re-validation path (editing commentary before approval, or after approval which resets close_approval_status to not_yet_decided — this is Commentary-Record-level revision within a still-open, not-yet-archived close, not reopening an archived one).

No mechanism of any kind exists to reopen, correct, or reprocess an already-archived close. This is exactly as the Handbook already states, and exactly as the Handbook already defers it (Phase 9, explicitly out of scope for the current milestone, per Section 4's scenario definitions, neither of which touches Phase 9).

4. Actual gap

None beyond what's already documented and already deferred. This is not a newly-discovered gap — it is confirmed, by direct inspection, to be exactly the scope the Handbook already describes as deferred.

5. Gap classification

Legitimately deferred. No material gap beyond what's already recorded.

6. Existing architecture to preserve

Immutable-snapshot archival (D10) must not be weakened. Any future reopen/correct capability would need its own full lifecycle design (actor, permission, data versioning, observation/commentary/approval/output consequences) per the Alignment Charter's Section 9 — none of that exists today, and building it without that design first would be exactly the kind of premature implementation the PM's own document warns against.

7. Data/version implications

Not applicable now — no implementation exists to have implications.

8–9. State-transition / downstream implications

Not applicable now.

10. E2E impact

None. Neither Scenario 1 nor Scenario 2 (Section 4 of the Handbook) exercises Phase 9 or any reopen path. This capability's absence does not block the current milestone.

11. Options/trade-offs
Option A (recommended): confirm the existing roadmap deferral as architecturally sound; no action needed now.
Option B: begin lifecycle design work now, ahead of need — rejected; premature relative to the current milestone's actual scope, and exactly the kind of scope creep the PM's own package instructs against (Section 13 non-goals explicitly excludes "implementation of reopen/correction").
12. Architect recommendation

No implementation, no design work, now. Reconfirm the existing deferral.

13. Whether current implementation is required

No.

14. If deferred, recommended roadmap position

Unchanged — post-E2E-demonstration, post-write-up, Phase 9-adjacent, as already recorded.

15. Any architectural decision needed now to avoid future rework

None identified. The immutable-archival model (D10) is already the correct foundation for a future reopen capability (an explicit new version/supersession record layered on top of immutability, rather than in-place mutation) — no decision is needed today to keep that door open; D10 already keeps it open.

Cross-Cutting Findings
Product state model (10.1): Dataset → Validated → Processed → Reviewed → Approved → Closed → Archived is present and coherent for the forward path (confirmed by direct code walk: Phase 2/3 → observation register → Commentary Review → Human Approval Gate → archive_close()). The reverse/reopen half of the model (10.1's second sequence) has no implementation, consistent with Gap 4.
Data versioning (10.2): the pipeline code version is captured (pipeline_git_commit_hash); the analytical rule/threshold version is not explicitly captured (Gap 3, item 8).
Configuration architecture (10.4): the three constants examined in Gap 3 are Analytical Definition, not Business Policy — no other configuration surface was found to review.
Output lifecycle (10.5): out of scope for this package (no gap raised against it here); flagged only that it remains a known open item (HTML/PPTX not yet built) per the existing Handbook, unaffected by anything found in Gaps 1–4.
Decision Map (Section 15 format)
Gap	What is actually wrong?	What is already supported?	Decision needed?	Current milestone?	Implementation?
1. Latest period	Close-processing target is decoupled from the sidebar (as already known) plus a newly-confirmed defect: Phase 6's evidence package silently uses the wrong period's data when the sidebar isn't at default	Sidebar selector itself works correctly and includes the latest period; close-processing correctly always targets the true latest	Yes — confirm (b) as a defect, not a reinterpretation	Yes — real risk in a live demo sequence	Yes, small scoped fix for (b); no change needed for (a)
2. Phase 4–6 visibility	Largely a documentation/evidence gap, not a product gap — full Observation→Commentary→Match→Validation detail is already rendered per-observation, including the newly-canonical "Matched via" label	Nearly everything the PM asked about	Recommend re-observing the live page before authorizing anything	No blocking impact	No, unless PM still judges a consolidated summary table necessary after direct observation
3. Rules/thresholds	No explicit rule-version audit metadata; no stated policy/definition/technical classification	Constants are already correctly centrally governed, non-editable, and load-bearing	Yes — governance classification (documentation decision)	No	Documentation-only; optional small additive metadata capture
4. Closed-period correction	Nothing — confirmed exactly as already documented and already deferred	Immutable archival (D10), in-session revision-before-close only	No	No	No

Also flagging, separately from the four gaps but discovered in the course of this review: the Handbook's own text about the audit-trail addendum's canonical-sync status is stale relative to the actual HEAD commit it describes — recommend a Handbook revision to correct this specific claim before it propagates further.