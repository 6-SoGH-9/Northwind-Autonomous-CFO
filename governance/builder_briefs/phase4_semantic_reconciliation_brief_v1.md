# Builder Brief — Phase 4 Matching & Semantic Reconciliation (Final Scope)

**Status:** **ACTIVE — authorized by the principal.** This Brief now governs Phase 4 implementation and supersedes `phase4_6_commentary_validation_brief_v5.md`'s Section B (only). Supersedes `phase4_6_commentary_validation_brief_v6_DRAFT.md` in full (that draft was withdrawn prior to authorization, never activated). v5 remains the last *implemented* Brief and its Sections C (Phase 6), D (Phase 5), E (Dashboard, except as amended below), F (version model), and K (judging-model rationale) remain unchanged and unaffected — this document changes only Section B (Phase 4 matching) and adds the semantic-reconciliation, exclusivity, and failure-mode requirements below. **Implementation status: authorized, not yet implemented.** No Builder Return Report exists yet against this Brief; nothing below should be read as evidence of completion.
**Governs (once activated):** the complete replacement of Phase 4's matching behavior, per Sections 1–5 below, layered onto v5's otherwise-unchanged Phase 5/6/Dashboard/version-model implementation.
**Constrained by:** D13 — In Progress, not moved by this Brief. Handbook Section 2a (AI Role Boundaries) and this Brief together define the corrected requirement; Handbook Section 13 records this as one of D13's two independent outstanding requirements.
**Does not reopen:** D10, D11, D12, D14, the Human Approval Gate, Phase 6's bounded evidence model, commentary versioning, the accepted-version concept, Phase 7's accepted-commentary handoff, HTML/PPTX generation, or final human approval authority.
**Author:** Architect
**Precedence:** Project Handbook (v2.14) > this Brief (Active) > v5 (still authoritative for everything this Brief doesn't change) > archived Briefs.

---

## 1. Matching — Deterministic Pass (revised)

**Required identifying information for a deterministic match:**
- Department
- Category
- Value (the commentary's stated monetary figure, when present)
- Period — **required only when the commentary explicitly states one**

**Deterministic match condition:** a commentary matches an observation deterministically only when Department and Category both resolve unambiguously (as today, via canonical name or existing synonym dictionary), **and**, if the commentary explicitly states a period, that period matches the candidate observation's period exactly. A commentary that states a period which does not belong to the candidate observation **must not match it** — this is a required condition, not a disambiguation aid to fall back from.

**Value as a matching signal:** when the commentary states a monetary figure, it must be checked against the candidate observation's `Delta ($)` (or `Before ($)`/`After ($)`, whichever the figure most plausibly refers to — Builder's implementation discretion on parsing, not on whether the check happens). A stated value that conflicts with the only remaining Department/Category(/Period) candidate is evidence against that match, not proof of a different one — Builder may treat a value mismatch as a reason to fall through to "no confident match" for the deterministic pass (and, if applicable, let the semantic pass evaluate independently) rather than as an automatic hard rejection, but a stated value must never be silently ignored in a case where using it would change the result. This must be explicit and testable, not merely "considered internally."

**Corrected defect, this Brief:** the current implementation narrows Department/Category candidates by period only when the narrowed set is non-empty, silently keeping a wrong-period single candidate otherwise. This must be fixed: an explicitly-stated period that matches no candidate for that Department/Category is `no confident match` for the deterministic pass, full stop — never a fallback to an unnarrowed, wrong-period candidate.

**Deterministic match means stop:** if the deterministic pass produces a match, that commentary is resolved. There is no LLM call for that commentary under any circumstance, including "reconfirming" or "improving" the deterministic result. The deterministic match is authoritative for that relationship.

## 2. One Observation → One Commentary (new, exclusivity)

**Rule:** each observation may be associated with at most one commentary relationship at a time. An observation that already has an associated commentary (deterministic or semantic-matched, at any point in its version history) is **occupied** and must not receive a second, independent commentary.

**Required behavior:**
- If deterministic or semantic matching would otherwise resolve a commentary to an already-occupied observation, that commentary is **not** attached to it. It is reported as unresolved (or, if the observation was the only candidate, as a specific "observation already has a commentary — consolidate into the existing entry" state, distinguishable from ordinary no-match).
- This is enforced at the point where a match is about to be recorded (today's dashboard glue code in `Northwind_Financial_Dashboard.py`, which currently keys `commentary_records` by `matched_observation_id` and appends a version with no occupancy check — this is the specific defect to fix).
- Revising an *already-accepted or already-associated* commentary (the existing correction-loop path, Section F) is unaffected — that is one commentary gaining a new version, not a second commentary being attached. The distinction is: same `commentary_id`/same Controller submission being revised vs. a genuinely different, separately-submitted commentary entry.
- The Controller-facing remedy for "I have two things to say about one observation" is consolidation into one longer commentary — the system does not solve this automatically and must not.

## 3. Semantic Reconciliation — Strictly Gated Exception Path

**Invocation condition (both must hold):**
1. A commentary entry remains unresolved after the deterministic pass (Section 1) **and** the exclusivity check (Section 2) — i.e., it did not deterministically match, or its deterministic candidate was already occupied.
2. At least one observation remains unmatched/unoccupied.

If either condition fails, semantic reconciliation is not invoked for that commentary. In particular: if no unmatched observations remain, every remaining unresolved commentary stays `Open / Unmatched` without any LLM call — this must be true even if a remaining commentary's text is superficially similar to an already-occupied observation's commentary.

**What semantic reconciliation does:** evaluates whether the meaning of the complete, unresolved commentary text refers to one of the remaining unmatched observations. This is meaning-based interpretation — explicitly not keyword expansion, synonym expansion, financial analysis, evidence validation, or creation of a new observation. It may consider only the currently-unmatched observation set as candidates; an already-occupied observation is never a legal semantic-match target.

**Outputs (exactly one of two):**
- **Confident match:** commentary → a specific, currently-unmatched observation.
- **No confident match.**

No third outcome exists. A forced match because one candidate "seems plausible" is a defect. On ambiguity between two or more remaining candidates, the correct output is no confident match.

## 4. LLM Boundaries (unchanged in spirit, restated precisely for this scope)

The semantic-reconciliation layer must never:
- Perform financial calculation or read/derive figures beyond what's needed to compare against a stated Value (Section 1) if Builder's implementation routes that check through the same layer — Value comparison is a deterministic check, not a semantic judgment, and must remain auditable as such regardless of which function performs it.
- Modify an observation, the observation register, or any financial fact.
- Decide Supported/Contradicted/Insufficient (Phase 6, unchanged, untouched by this Brief).
- Decide or influence close approval/rejection status (D13, unchanged).
- Create a second commentary relationship to an already-occupied observation (Section 2).
- Invent an observation that does not exist in the register.
- Force a match absent sufficient support (Section 3).

## 5. Failure / Degraded Behavior (new, required)

The following must be explicitly defined and tested, not left as accidental behavior:

- **No API key present:** semantic reconciliation is skipped entirely for the affected commentary/commentaries; each remains `Open / Unmatched`. This must not raise an unhandled exception, must not silently fall back to a forced deterministic-style match, and must be visibly distinguishable in the dashboard from "semantic reconciliation ran and found no match" (a neutral "semantic reconciliation unavailable this session" state, analogous to the existing "no commentary imported yet this session" pattern, Brief v5 Section E Criterion 11).
- **API call failure (network/timeout/error response):** same outcome as no API key — commentary remains `Open / Unmatched`, failure is surfaced neutrally, not as a dashboard error blocking other functionality.
- **Unusable/invalid model response** (e.g., malformed output, a claimed match to an observation ID that isn't in the current unmatched set, or a response that isn't cleanly one of the two legal outcomes): treated as no confident match. The system must validate the model's claimed match against the actual current unmatched-observation set before accepting it — never trust a returned observation ID without checking it against real data (this is a direct instance of the standing "AI must not invent/override financial facts" boundary, Handbook Section 2a).
- **In every failure mode:** the deterministic pass's results (Section 1) and the exclusivity enforcement (Section 2) are entirely unaffected. A semantic-layer failure never causes a previously-resolved deterministic match to be reopened, altered, or reconfirmed.

## 6. What Is Unchanged (explicit, to bound scope)

Phase 6 (Section C, v5) — bounded evidence validation, Supported/Contradicted/Insufficient — is untouched. Phase 5 (Section D, v5) — draft note — is untouched. The Commentary Record / version model (Section F, v5) is untouched except that "attaching a new commentary" now additionally requires the occupancy check in Section 2 above; revision/versioning of an already-associated commentary is unaffected. Section G's three-way executive-output handoff is untouched — it already operates on whatever the (corrected) Phase 4/exclusivity logic hands it. The Human Approval Gate, D10, D11, D12, D14 are untouched. `Commentary.xlsx`'s optional status (v5) is untouched.

## 7. Acceptance Criteria

1. A commentary with an explicit, correct Department+Category(+Value)(+Period, if stated) reference matches its target observation deterministically; no LLM call occurs for it (verified by execution trace / call-count assertion, not code inspection alone).
2. A commentary stating a period that does not belong to its otherwise-unique Department/Category candidate does **not** match that candidate (regression test for the corrected defect, Section 1).
3. Two independent commentary entries that would otherwise both resolve to the same observation: the first is attached; the second is reported unresolved/occupied, never silently added as a second version (Section 2).
4. With at least one commentary unresolved after Sections 1–2 and at least one observation still unmatched, semantic reconciliation runs and either returns a confident match to a currently-unmatched observation or an explicit no-confident-match — never an already-occupied observation, never an invented one.
5. With all observations already occupied, any remaining unresolved commentary stays `Open / Unmatched` with **zero** semantic-reconciliation calls (verified by call-count assertion).
6. No-API-key and simulated API-failure paths both leave affected commentary `Open / Unmatched` with a neutral, non-error dashboard state, and zero effect on already-resolved deterministic matches.
7. A simulated invalid/out-of-set model response is treated as no confident match, not accepted at face value.
8. All existing v4/v5 Builder regression fixtures continue to pass for behavior this Brief doesn't change (Phase 5, Phase 6, Section G, Section E's other criteria, the dashboard's zero-exception rendering).

## 8. Required Evidence

- Builder regression evidence for Criteria 1, 2, 3, 5, 6, 7, 8 (Builder may construct its own fixtures for these — they test control-flow and non-regression, not semantic genericity).
- **Independent Test evidence, not substitutable by Builder's own fixture, for Criterion 4's semantic-match case and its ambiguity/no-match companion** — see the UAT specification (governing task's Section 5) for Cases B and C, which must be authored independently per the Validation Independence Principle.
- Canonical synchronization confirmed via fresh clone before any of the above is described as part of the canonical product.

---

*Per the Document Delivery Standard, this is the complete Brief as authorized. It supersedes v5's Section B (only) as the governing Phase 4 specification, effective on principal authorization (recorded in Handbook v2.14). No implementation exists yet against it — Builder has not yet received or acted on this Brief; that is the next governed step, not something this document itself accomplishes.*
