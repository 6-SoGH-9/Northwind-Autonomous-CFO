# D15 Item 2 Corrections — Addendum 2 (RELEASED)

**Governs:** one new item (G), plus a full re-review of Item E's existing implementation.
**Status:** Item G — **RELEASED — ACTIVE.** Item E's exclusivity gap — **SEND BACK, fix required before this closes out.**

---

## Item G — NEW: auto-clear the reopen file uploaders

### Required behavior

Both the "Corrected raw dataset" uploader (`reopen_corrected_dataset_upload`) and the "Commentary.xlsx for this candidate" uploader (`candidate_commentary_uploader`) must reset to empty (no file attached) after any of the following:

1. A successful "Run correction intake" — both the immediate/no-violation path and the post-"Continue" path.
2. "Cancel" on the out-of-period-conflict warning.
3. A successful "Approve candidate close."
4. "Reject candidate."
5. "Start over."

### Design (minimum-scope — no other behavior changes)

Streamlit's `file_uploader` has no direct "clear" call; the standard, minimal way to reset one is to change its `key`. Use a single shared counter, e.g. `st.session_state["reopen_uploader_generation"]` (starts at 0), incremented by 1 at each of the five points above. Both uploaders derive their key from it:

```python
_gen = st.session_state.get("reopen_uploader_generation", 0)
_corrected_file = st.file_uploader(..., key=f"reopen_corrected_dataset_upload_{_gen}")
...
_cand_commentary_file = st.file_uploader(..., key=f"candidate_commentary_uploader_{_gen}")
```

Nothing else changes — no change to matching logic, candidate rebuild behavior, or Item F's guard.

### Acceptance criteria

- G1. After a successful "Run correction intake," both uploaders show no file attached.
- G2. After "Cancel" on the out-of-period warning, the dataset uploader is empty.
- G3. After "Approve candidate close" succeeds, both uploaders are empty.
- G4. After "Reject candidate," both uploaders are empty.
- G5. After "Start over," both uploaders are empty.
- G6. Regression: existing intake/approve/reject/reset flows behave identically otherwise — this is purely a widget-key change.

---

## Item E — full re-audit (requested this session)

Re-read the entire section fresh: `match_commentary_entries()`, the candidate matching loop, `commentary_changed()`'s consumption of it, and the archive call. Confirmed correct:

- Reactive matching (fires on every rerun while a file is attached, not gated behind a button) works as intended and is genuinely idempotent for identical (source, text) pairs — re-running with the same file doesn't create duplicate versions.
- `validation_result=None` is correctly never anything else — confirmed again, no path sets a fabricated Phase 6 result.
- The candidate's `commentary_records` dict is deliberately rebuilt from scratch (`{}`) every time "Run correction intake" runs — this is documented in the code as intentional, and is the exact behavior behind the "commentary isn't versioned across separate intake runs" observation from earlier in this session. Confirmed, not a bug — still an open design question (see below).
- Archive-time persistence (`CWF.serialize_commentary_records()`) is unchanged and correct.
- Empty/no-match/empty-register cases are all handled with a message, not a crash.

### New finding — exclusivity is missing within a single commentary upload

`match_commentary_entries()`'s own docstring states plainly: *"This function performs ONLY the deterministic pass. Exclusivity ... [is] applied afterward by `resolve_commentary_matches()`, which wraps this function — call that, not this one, for the full Phase 4 pipeline."* Item E calls `match_commentary_entries()` directly, not `resolve_commentary_matches()`.

I originally called this the right minimal-scope choice, reasoning `resolve_commentary_matches()` only added Phase 6-adjacent behavior. That reasoning was wrong. `resolve_commentary_matches()` is two genuinely separable pieces:

1. **Exclusivity enforcement** — pure logic, no API call, no cost/credential concern. Tracks which observations are already occupied (including within the *same* upload batch) and marks a second entry claiming an already-claimed observation as unresolved/occupied instead of silently attaching it.
2. **Gated semantic reconciliation** — the actual LLM call. This is correctly out of scope for a matching-only candidate feature.

Calling the raw function skipped both, including the free, cheap, clearly-in-scope first piece.

**Reproduced:** built two commentary entries with different, conflicting text, both referencing the same department/category/period. Both come back `matched=True` against the *same* observation, with no conflict signal:

```
C-1 matched: True -> oid: OBS-1
C-2 matched: True -> oid: OBS-1
```

In the dashboard, this means: if a single uploaded `Commentary.xlsx` has two rows that both resolve to the same observation — a duplicate, a copy-paste mistake, two people's conflicting notes — both get silently appended as separate versions of that observation's record, with no warning that anything unusual happened. That's not a deliberate revision; it's an unflagged data-entry conflict being treated as one.

### Required fix

Call `resolve_commentary_matches()` instead of `match_commentary_entries()`, with the semantic step disabled — pass a `semantic_fn` that always returns `(None, "semantic reconciliation not available in candidate matching-only scope")` (the parameter exists exactly for this — it's injectable). This gets exclusivity for free without touching any LLM path, API cost, or credential concern. `commentary_records` passed in should be the candidate's own current dict (so exclusivity is checked against what's already been captured *in this candidate*, not the live path's).

### Acceptance criteria

- E-fix1. Two entries in one upload resolving to the same observation: only the first is attached; the second is reported unresolved/occupied (reuse the existing unmatched-entry display, same as today's unmatched case).
- E-fix2. A single entry, unambiguous: unaffected, behaves exactly as today.
- E-fix3. Confirm no live model/API call occurs anywhere in this path — `semantic_fn` is the disabled stub, never the real `semantic_reconcile_commentary`.
- E-fix4. Regression: existing candidate matching tests (from Addendum 1's Item E acceptance) still pass.

---

## Still open, not resolved by this addendum

Two questions from earlier in this session remain unanswered and are **not** included in Item G or the Item E fix:

1. Should re-running "Run correction intake" preserve previously-entered candidate commentary when the observation register is unchanged, instead of wiping it?
2. Should the live "Commentary Review (Phase 4-6)" section be hidden or flagged when a reopen is active on the same period it targets?

Both need your decision before I write them up.

---

**Architect Attestation:** Item G verified by direct code inspection (exact widget keys, exact reset points) — minimum-scope, single mechanism, no other behavior touched. Item E's exclusivity gap independently reproduced this session, not inferred from the docstring alone. Semantic reconciliation confirmed to remain genuinely out of scope in the proposed fix — the disabled stub never calls the real function.
