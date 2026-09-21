# D15 Item 2 Corrections — Addendum 1 (RELEASED)

**Governs:** revisions/additions to `D15-Item2-Corrections_builder_brief_RELEASED.md`'s Item A, plus two new items.
**Authority:** Principal decisions made directly in this session (all recorded below).
**Status:** **RELEASED — ACTIVE.** Scope Authorization Gate closed this session.
**Sequencing dependency:** Item A (revised) → Item E → Item F. F consumes both A's and E's output; build in this order.

---

## Item A — REVISED: warn-and-exclude replaces reject-outright

### What changes from the original Brief

Original Item A rejected the entire intake outright on any out-of-period conflict. **Superseded.** Detection logic is unchanged (`period_lifecycle.enforce_period_scoped_correction()`'s row-by-row comparison against each other period's approved values, already built and verified). What changes is the response to a detected conflict.

### Required behavior

1. On detecting one or more out-of-period rows that differ from their period's currently-approved value: **do not raise/reject.** Instead, surface the specific offending rows to the user with a clear message — *"These values fall outside [reopened period] and will not be captured in this close."*
2. Present two explicit choices, mirroring the existing reopen flow's own Cancel/Continue pattern (5.C): **Continue** or **Cancel**.
3. **Cancel:** identical to the original Item A's reject behavior — no candidate created, nothing archived.
4. **Continue:** proceed to build the candidate. For every excluded row, use the approved snapshot's value (never the uploaded value) — this is the existing substitution logic already built and verified for the no-conflict passthrough case; it now also applies to the conflict case once the user has explicitly confirmed exclusion.
5. This applies **regardless of whether the reopened period itself has any genuine change** — a reopen where the only difference from canon is an out-of-period row still surfaces the warning (per Principal confirmation).

### Audit trail — new requirement

The excluded rows (sheet, period, key, approved value, uploaded value — the same detail `CorrectionScopeViolation` already carries) must be persisted into `archive_close()`'s `extra_metadata` at the point the candidate is actually archived, not only displayed once in the UI and discarded. Reuse the existing `extra_metadata`/`build_lineage_metadata()` mechanism (D15 5.I) — additive field, e.g. `excluded_out_of_period_rows`, not a new metadata channel.

### Acceptance criteria

- A-R1. Reopen with only an in-period change: unaffected, behaves as today.
- A-R2. Reopen with an in-period change AND a differing out-of-period value: warning shown, Continue produces a candidate where the out-of-period row is silently reset to its approved value; Cancel aborts with nothing created.
- A-R3. Reopen with ONLY a differing out-of-period value (no genuine in-period change): warning still shown (not skipped).
- A-R4. On Continue, the archived version's `extra_metadata` contains the excluded row detail, independently readable from the archived record after the fact.
- A-R5. Regression: existing in-period-only and identical-out-of-period passthrough behavior (original A1/A3) unaffected.

---

## Item E — NEW: candidate commentary capture (matching-only)

### Scope, explicitly bounded (Principal-confirmed)

**Matching only. No Phase 5 (draft note), no Phase 6 (Supported/Contradicted/Insufficient validation).** The question this answers is "did commentary change," not "is commentary any good" — validation is irrelevant to that question and is explicitly deferred to the wider D15 Item 1 scope, not built here.

### Required behavior

1. During correction intake, once a candidate exists (`_cand["phase3_result"]`'s regenerated observation register is available), offer a commentary entry step for the candidate's own flagged/unresolved observations — same shape as the existing live Commentary Review section, pointed at the candidate's register instead of the live one.
2. Match entered commentary to candidate observations by reusing `commentary_workflow.match_commentary_entries(entries, observation_register)` unmodified — no new matching logic.
3. For each matched observation, build a `CommentaryRecord` and call `add_version(text, source, submitted_by, validation_result=None)` — `validation_result=None` is the honest, already-supported representation of "no Phase 6 was run" (the field is `Optional[Phase6Result]`), not a fabricated result.
4. **Standing rule, not scoped to this feature alone:** whenever commentary is captured for a version, it must be persisted in that version's own archived record. On candidate approval, replace today's `commentary_record=None` with `commentary_workflow.serialize_commentary_records(...)` over the candidate's matched records — the same function the live path already uses, unmodified.

### Acceptance criteria

- E1. A commentary entered and matched during a reopen is retrievable from the archived version's own `commentary_record`, same shape as a live close's commentary.
- E2. No commentary entered during a reopen: `commentary_record` remains `{}`/empty, honestly, not fabricated — same discipline as today.
- E3. `validation_result` on every candidate-path commentary version is `None`, never a synthesized Phase 6 status.
- E4. Regression: the live single-period path's own commentary capture (v4 Brief, Phase 4-6, Section F versioning) is completely unaffected — zero change to that call site or `CommentaryRecord`/`add_version()`'s existing signature.

---

## Item F — NEW: zero-net-change guard

### Required behavior

Before allowing candidate archival, check whether the reopened period genuinely changed, on **both** axes:

1. **Numerical:** the reopened period's own filtered/corrected data (post-Item-A, in-period rows only) is identical to its currently-approved version — i.e., `numerical_impact = False` for the reopened period itself (reusing the existing 5.E comparison, not new logic).
2. **Commentary:** compare the candidate's matched commentary (Item E) against the prior approved version's stored `commentary_record` for the same period, by observation: any commentary **added** (an observation newly commented that had none before), **edited** (existing text differs), or **removed** (previously commented, now absent) counts as a change — all three, per Principal confirmation.

If **neither** axis shows a change: block archival. Show "No change detected in [period] — nothing to correct," and do not offer a version bump. If **either** axis shows a change: proceed normally.

### Note on today's evidentiary limits

Item E didn't exist before this addendum, so historically-archived reopen versions (if any exist by the time this ships) may have `commentary_record = {}` with no way to know whether that means "no commentary was ever entered" or "commentary existed but predates Item E." This is an expected, disclosed limitation of adding the capability now rather than a defect — no action required, but don't let it be read as "commentary never changes" for pre-Item-E versions.

### Acceptance criteria

- F1. Reopen with a genuine numerical change, no commentary: version created.
- F2. Reopen with no numerical change, but commentary added/edited/removed relative to the prior version: version created.
- F3. Reopen with no numerical change AND no commentary change: archival blocked, clear message, no version created.
- F4. Reopen where the only "change" is an out-of-period row that gets excluded via Item A's Continue path, with no other in-period numerical or commentary change: correctly treated as F3 (blocked) — confirms Items A and F compose correctly.
- F5. Regression: the live single-period Approve path is untouched — this guard applies only to the candidate/reopen path.

---

# SCOPE AUTHORIZATION GATE

| Item | Classification | Confirmed how |
|---|---|---|
| A (revised) — warn-and-exclude | Category B, new scope (supersedes original Item A's reject behavior) | Principal-requested and specified this session |
| Audit trail (`extra_metadata`) | Category B, new scope | Principal confirmed: "Yes" |
| E — candidate commentary, matching-only | Category B, new scope, deliberately narrowed | Principal confirmed matching-only, no Phase 5/6; sequencing decision within already-authorized D15 Item 1, not a fresh Decision Log entry |
| F — zero-net-change guard | Category B, new scope | Principal specified: block when no numerical change AND no commentary change; all three commentary-change types count |
| Commentary persistence (Option A) | Category B, new scope, standing rule | Principal confirmed: "If commentaries are delivered, they must be captured in every version" |

**Minimum-scope check:** Item A's revision changes a response path, not the detection logic (already built/verified). Item E reuses `match_commentary_entries()` and `CommentaryRecord`/`add_version()`/`serialize_commentary_records()` unmodified — no new matching or persistence machinery. Item F reuses the existing 5.E comparison for its numerical half; its commentary half is a straightforward set comparison over data Item E already produces. No schema redesign, no new state model.

**Explicit exclusions:** Phase 5 (draft note) and Phase 6 (Supported/Contradicted/Insufficient validation) for the candidate path — deliberately deferred, not silently dropped. The wider D15 Item 1 (full candidate Commentary intake through Phases 4-6) remains open beyond what Item E delivers.

**Architect Attestation:**
☑ Verified via direct code inspection this session that `commentary_record=None` is the current candidate-path state, that `match_commentary_entries()`, `CommentaryRecord.add_version()`, and `serialize_commentary_records()` exist and are reusable unmodified, and that `validation_result` is `Optional[Phase6Result]` (so `None` is a legitimate, non-fabricated value)
☑ No unauthorized bundling — A/E/F are each independently specified with their own acceptance criteria, sequenced only because F genuinely depends on A and E's outputs
☑ Did not silently expand scope — Phase 5/6 explicitly named and excluded rather than left ambiguous

**PRINCIPAL APPROVAL GATE:** ☑ All decisions in this addendum were made directly by the Principal in this session (warn-vs-reject behavior, audit-trail persistence, matching-only scope for Item E, all-three-count for commentary change, Option A commentary persistence as a standing rule). Released to Builder as of this session, together with the original `D15-Item2-Corrections_builder_brief_RELEASED.md`.
