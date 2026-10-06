# D15 Items 3 and 4, Post-Release Fix K (v2.5): "No Flag, No Approval" for Reopen-and-Correct

**STATUS: v2.5. SIGNED BY THE PRINCIPAL, 2026-10-06 05:33 (Europe/London), and released to the Builder as this one file. The text below the signature lines is the text the Principal reviewed (SHA-256 `061f2af5d6a875392300a3dc75d47192e684ca76f64f94b140cdb705af4f0842`). Only the status, signature and release lines differ from it.** This is one consolidated file. It contains v2.4 in full (with the places that changed updated in place) plus Part 0-ter, the v2.5 amendments. The Builder receives this one file, with one hash, and nothing else. No Brief text lives outside it.
**Files superseded by this file (do not give any of them to the Builder):**
1. `governance/builder_briefs/d15_fix_k_no_flag_no_approval_brief.md` (the v2.4 text under the unversioned name, commit `f7d3e39`, SHA-256 `3abc4d6e9c9ada3f0cc1f50dffe102f2507dc1278bb915e26476c911881f3530`).
2. `governance/builder_briefs/d15_fix_k_no_flag_no_approval_brief_v2_3.md` (commit `41bdd9c`).
3. Project copies `architect_reviews/d15_fix_k_no_flag_no_approval_brief_v2_4.md` and `..._v2_3.md` (historical copies).
4. `builder_brief_fix_k_flag_save_failure_DRAFT.md` (v1, already superseded).
5. `architect_reviews/d15_fix_k_v2_5_addendum_draft.md` (the Architect's separate addendum draft, withdrawn).
6. `architect_reviews/fix_k_v2_4_notice_wording_proposals.md` (its wording is now in Message Wording N1 to N5 below, with the Principal's plural rule, which that file did not have).
Not part of this round and **not given to the Builder:** `architect_reviews/fix_k_builder_change_request_round1.md` (the v2.4 change request). The v2.4 delivery already used it. It also contains a withdrawn scope item (A1). Any mention of it in the text below is history only and is not an input to this round.
**v2.4 status (history): APPROVED BY THE PRINCIPAL, 2026-10-01 18:16 (Europe/London), by written statement "This version is good. I validate it and will make it canonical and send it to the builder."** v2.3 was approved and released 2026-10-01 11:56; v2.4 adds the Part 0-bis amendments (A1 to A8). A3-Q (annual labels) and A4 (save-failure wording) are decided. The Principal sends v2.4 to the Builder and makes it canonical. The Architect has not pushed, merged or sent anything.
**Supersedes:** `builder_brief_fix_k_flag_save_failure_DRAFT.md` (v1, session-block design). v1 must not be used.
**v2.5 changes from v2.4:** Part 0-ter added (B1 to B6): this round changes only the wording of five notices N1 to N5 (Message Wording), the guard test that covers them, and the minimum plumbing to produce them. `close_history.py` must not change. T11 on production data becomes an open risk, not a condition (B4). T7 is repeated in full on the v2.5 fingerprints. A5 is the Architect's combined list (accepted 2026-10-03). Updated in place: A1, A5, Part 0 item 3, Item 3 caveat, M8, Message Wording, T7, T11, new T13, Builder Package, Gate (Category B rows, Status, signature), attestation, release rule.
**Reissue of 2026-10-06 (second, after the Principal's review):** (1) A5 no longer points to the 22-item list; the baseline for this round is the Builder's own v2.4 delivery, and the change request is not an input; (2) Builder Package item 1 and the other "three files" wording now say `close_history.py` must not change in this round; (3) the box "in that order" is ticked on the Principal's written instruction and the "pending" wording is removed; (4) Builder Package item 2 now says T1 to T13; (5) B1 gains a rule for reading the earlier Parts. Nothing else changed.
**v2.4 changes from v2.3:** Part 0-bis added: file scope (A1), `attempt_at` correction (A2), "FY" rule and guard (A3), single save-failure message (A4, decided), difference list (A5), item 12 explicit (A6), strengthened equivalence test (A7), verification sequence (A8).
**v2.3 changes from v2.2 (Principal review, two items; nothing else changed):** (1) M11, "What the Controller sees" and T5(c): the notice stays visible until the Controller explicitly dismisses it (dismiss button, per browser session only); replaces "once per page load" and removes the Architect practicality note; (2) Part 1 section 8 Implementation Impact: notice placement near dashboard line 1251 explicitly included. Mechanical: version labels and Brief ID updated to v2.3.
**v2.2 changes from v2.1 (Principal review, six items; nothing else changed):** (1) M11, "What the Controller sees" and T5(c): notice once per page load or launch, not on every rerun; (2) Category D storage row aligned with the Addendum; (3) Minimum-Scope Verification line corrected; (4) message wording marked approved (heading and M8); (5) file renamed and Brief ID stated; (6) code-comment instruction recorded as an Architect recommendation. Mechanical: version labels updated to v2.2.
**v2.1 changes from v2:** D8 notice ON by default (M11), Principal confirmations and storage footnote recorded, Gate and attestation updated.
**Brief ID:** `d15_fix_k_no_flag_no_approval_brief_v2_5` (proposed repository path: `governance/builder_briefs/d15_fix_k_no_flag_no_approval_brief_v2_5.md`; earlier IDs: `..._v2_4`, `..._v2_3`) (file-name convention used by the existing briefs in `governance/builder_briefs/`; assigned by the Architect here). The Decision Log "D" number is not assigned: the governance files I read define no assignment rule and the D16/D18 numbering is unresolved in the Handbook. Proposal: the Architect assigns it when recording this fix in Handbook Section 7 after completion; the Principal may override.
**Date drafted:** 2026-10-01 (v2.5 reissued 2026-10-06)
**Responds to:** Principal Decision "Fix K Mechanism Approved (Option 1)" (via Project Advisor) and the four open items in it.

---

# PART 0-BIS: v2.4 AMENDMENTS (Principal decisions of 2026-10-01 evening; signed 2026-10-01 18:16)

(Retained in full. Part 0-ter below governs the v2.5 round. Where Part 0-ter and this Part differ, Part 0-ter wins.)

Everything in v2.3 stays in force except where this Part says otherwise. Where this Part and v2.3 differ, this Part wins. Nothing here is signed yet. **Nothing is to be pushed or merged until the Principal signs v2.4.**

## A1. Files that may change (resolves the contradiction in the change request)

| File | Status |
|---|---|
| `close_history.py`, `period_lifecycle.py`, `Northwind_Financial_Dashboard.py` | Allowed in the v2.4 round (the three Fix K files). **In the v2.5 round `close_history.py` is NOT allowed to change (B2).** |
| One new guard-test file (A3) | Allowed |
| `rollups.py`, `close_validation.py`, `commentary_workflow.py`, any other file | NOT allowed to change under v2.4 or v2.5 |

For the v2.5 round the narrower limits in B2 apply. If the Builder finds a raw period label that can only be fixed in a file that is not allowed, the Builder stops, lists the exact line and message, and reports. It does not edit that file. Changing it needs a signed amendment. (The Architect's change request item 3 implied wider scope than v2.3 allowed. That was the Architect's error and is withdrawn.)

## A2. M10 correction: keep the original `flagged_at`

- A Fix F clear keeps the mark's original `flagged_at`, exactly as 691e8f4 does.
- The attempt's own time goes in a fifth optional attempt field, `attempt_at`, written whenever an attempt is supplied (marks and Fix F clears). Add it to `ATTEMPT_FIELDS`.
- The M7 grace period is measured from `attempt_at`, falling back to `flagged_at` only when `attempt_at` is absent.
- `resolve_pending_reprocessing` strips `attempt_at` with the other attempt fields.
- Tests: Fix F clear of a mark with a known old `flagged_at` leaves it unchanged and sets `attempt_at`; T5/T6 re-run; marks without `attempt_at` behave as before.
- The Return Report states that this was changed and why.

## A3. "FY" rule (Principal instruction; replaces the "Q# FY####" test in the change request)

- No user-visible message, notice or label produced by Fix K or by the messages it touches may contain "FY". Quarter periods are shown as "Q3 2026" through `R.fmt_period_label`.
- **Only exemptions:** (i) a file path; (ii) quoted operating-system error text, only inside the error detail slot defined under Message Wording (recognized by removing the injected sentinel error string, never by pattern); (iii) a standalone annual label `FY` plus four digits (decision A3-Q below). Internal identifiers that never reach the screen are not shown to the Controller and need no exemption.
- **Guard test:** renders every Fix K message path and every pre-existing message path in the three allowed files with quarter-style inputs, and fails if a fiscal-year token appears in the rendered text outside the **three** exemptions (file path, quoted OS error text, standalone annual label). **Matching rule:** the test matches `FY` only as its own token, never as a raw substring and never case-insensitively. Reference pattern: `\bFY\s?\d{2,4}\b`, which catches "FY2026", "FY 2026", "Q3 FY2026" and "FY26". The only text that passes is a standalone annual label matching `^FY\d{4}$` exactly. Ordinary words ("verify", "notify", "identify", "modify", "FYI") must pass. The test includes these as explicit must-pass cases, plus "Q3 FY2026" as a must-fail case and "FY2026" (standalone) as a must-pass case. This replaces "any FY, any case" in the Principal's earlier wording; the intent is the fiscal-year label, not the two letters.
- **Static scan:** the Builder scans the three allowed files for every place a raw period label is interpolated into a string that can reach the screen (including `archive_close` exception text shown through `st.error`) and fixes each at source, or reports it under A1.
- **Annual label format (verified in the code, not assumed):** `rollups.py` line 101 builds it as `"FY" + year`, with no space, for example "FY2026". Nothing in `rollups.py` or the dashboard produces "FY 2026". The exemption `^FY\d{4}$` matches what the app shows.
- **DECIDED by the Principal (A3-Q), 2026-10-01 18:00 (voice, then "now you can edit it"): Option 1.** Annual period labels that stand alone, of the form `FY` plus four digits (for example "FY2026"), are exempt from the "no FY" rule, because there "FY" marks the fiscal year. The Annual view and `rollups.py` stay unchanged. Quarter labels keep the rule: always "Q3 2026", never "Q3 FY2026". The guard's exemption list is therefore three items: file paths, quoted OS error text, and a standalone `^FY\d{4}$` annual label (not part of a quarter label). A quarter label containing "FY" still fails the guard. Changing annual labels, if ever wanted, is a separate Brief.

## A4. Save-failure message (DECIDED by the Principal, 2026-10-01 18:11)

One message replaces the three variants and the old selection rule. All three variants, the "no flags had been changed" sentence, the "flag changes were undone" sentence and the old selection rule are removed and must not be used.

**Message (exact):** "Q2 2026 was NOT saved. The save failed (*error*). Fix the cause shown above (for example folder permissions or disk space) and approve again."

**Rule:** always show this message when the save fails. It makes no claim about flags. If any undo failed, also show the already-approved undo-failure message once per affected quarter, below it. The exact texts of all approved messages are in the Message Wording section (Part 2), which is authoritative.

## A5. Complete difference list from 691e8f4 (required before any push)

**Status for the v2.5 round.** The Principal decided on 2026-10-03 that the official difference list for the v2.4 delivery is the Architect's combined list (the 22 items of the v2.4 change request plus four items the Builder's list missed, plus the Builder's own further items). That list was applied to the v2.4 delivery and is closed. **It is not an input to this round, and the Builder does not receive the change request.** For v2.5 the baseline is the Builder's own v2.4 delivery (branch `fix-k-no-flag-no-approval`, reported tip `b4f9c6e`). The Return Report lists every behavioural difference between that tip and the v2.5 commit. **The only difference allowed is one line: "Notice texts N1 to N5 changed to the Message Wording of v2.5."** Anything else the Builder finds must be removed or reported and explained. The Principal treats anything not listed as unchanged. Item 12 is explained in A6.

## A6. Item 12 stated explicitly (previously implicit)

A failure while writing the baseline or clearing the reopened quarter's own mark, after the correction is saved, no longer triggers the "flag every later quarter" fallback. It is reported to the Controller, and nothing is relied on. Basis: v2.3 step 7 and M9 (post-save steps reported, never relied on), plus the fact that the downstream marks were already written and verified before the save. This is now listed here so it is a signed item, not an inference.

## A7. T9 Equivalence test (strengthened)

- Compare 691e8f4 with the patched code, same inputs, on at least four scenarios: a downstream quarter affected; a prior unresolved mark then unaffected (a Fix F clear); nothing affected; the reopened quarter carrying its own prior mark with several quarters affected.
- Compare **every field of every file written**, except the four attempt fields plus `attempt_at`, and the single new `attempt_id` in the saved close's `metadata.json`. Any other difference fails the test.
- The setup clock and the approval clock must be different values. (One frozen clock hides timestamp overwrites; the Architect's first harness did exactly that.)

## A8. Verification sequence

1. The Builder implements A1 to A3 and A5 to A7 and returns the report with commit SHA and SHA-256 of every changed file.
2. The Architect re-verifies the new patch independently (hashes, rebuild from the patch, own tests, equivalence run with distinct clocks) and re-shoots every changed message in the live app.
3. Only then does the Principal run T7 himself, with screenshots.
4. Nothing is pushed or merged to `main` until the Principal signs v2.4 and has seen steps 2 and 3.
5. The formal Architect verification note, the Handbook update and the Decision Log number come after T7.

---

# PART 0-TER: v2.5 AMENDMENTS (Principal decisions of 2026-10-03, 2026-10-05 and 2026-10-06, for signature)

Where this Part and any earlier Part differ, this Part wins. The places that changed have also been updated in place, so no contradiction should remain. If the Builder finds one, the Builder stops and reports it. Signed by the Principal on 2026-10-06 05:33 (see v2.5 SIGNATURE). **Nothing is to be pushed or merged until the steps in B6 are complete and the Principal decides the merge.**

## B1. Starting point and what this round changes
- The starting point is the Builder's v2.4 delivery: branch `fix-k-no-flag-no-approval`, reported tip `b4f9c6e`, patch `fix_k_v2_4_691e8f4_to_tip.patch`. Its behavior was verified by the Architect (interim review) and run by the Principal (T7 on the v2.4 fingerprints). **It must not change in this round.**
- This round changes only: (1) the text of five notices, N1 to N5 (Message Wording); (2) the guard test and the new T13 that cover them; (3) the minimum internal plumbing needed to produce them.
- **How to read this file in this round:** Parts 1 and 2 and the earlier Parts describe the full Fix K scope that the v2.4 delivery already built. Wherever an earlier Part says to change a file or write code, B1 and B2 govern: only N1 to N5, the guard test and T13 are to be built. Mentions of the v2.4 change request are history, not an input.
- All earlier scope (M1 to M11, the sequence, Detection design, Scope Out) stands as delivered. When and whether each notice appears, what triggers it, and whether an approval counts as saved or failed do not change.
- **Category:** B (message wording), the same as W1 to W5. **Minimum-Scope Test:** the five notices already exist in the delivered code with Builder-written text. The Principal asked for other wording. A wording change cannot be smaller. No new capability, file or dependency.

## B2. Files that may change in this round
| File | Status |
|---|---|
| `period_lifecycle.py`, `Northwind_Financial_Dashboard.py` | Allowed, for N1 to N5 only |
| `build_test/fixk_fy_label_guard.py` and the Builder's own tests for these messages | Allowed |
| `close_history.py` | **NOT allowed to change.** Its SHA-256 must remain `337d2139f3cc5bb872ee1df86561067709489b09d5aca59473ccfcbdd3fd3e83`. If the Builder believes it must change, the Builder stops and reports. (Architect basis: none of the five texts is built in `close_history.py`; found by searching the three files. The Architect has not proved the negative beyond that search, so the hash check in B6 is the control.) |
| Any other file | NOT allowed |
- Internal plumbing is allowed where N2 needs it, for example recording a failed post-save step as a step name plus an error instead of one text line. It must not change when or whether the step runs, or the outcome "saved".

## B3. Guard test (extension of A3)
- The quoted-error exemption covers the error detail slot in W1 to W5 and N2 to N5, by construction. The guard injects its sentinel error string through that slot, removes exactly that sentinel, and scans what remains. N1 has no error slot and no exemption.
- The guard renders every notice path in Message Wording (all N1 variants, both N2 variants, N3, N4, N5) with quarter-style inputs, and fails if a fiscal-year token appears outside the three A3 exemptions.
- The guard also checks each approved text exactly: the rendered text equals the Message Wording text, with the `Close-order notice: ` prefix on N1 to N5 and none on W3.

## B4. T11 and open risks (Principal decisions 2026-10-05)
- **T11:** the earlier condition "T11 on production-like data" is removed. T11 on the sample dataset stays required. The formal verification note must say plainly that the 0.005 tolerance was checked only on the sample dataset and must be revisited when real data exists.
- **Four open risks. None blocks the merge.** Each carries a trigger, to be recorded in the Decision Log at the Handbook update. The triggers below are the Architect's proposal, for the Principal to confirm or edit at signature.

| Open risk | Trigger (proposed) | Action at the trigger |
|---|---|---|
| T11 on real data | Before any real, non-sample dataset is loaded into the app | Run T11 on that data under the pinned pandas. Revisit 0.005 and decide whether a materiality threshold is wanted (a product decision and a new Brief). |
| Concurrent approvals | Before more than one person, or more than one browser session, approves closes against the same Close History | A concurrency design and its own Brief. W5 already states that other tabs give no warning. |
| Production storage | Before Close History is kept anywhere other than a local folder on one machine (shared drive, network or cloud storage, container volume) | Revisit the storage footnote in the Principal Addendum. Re-test the 15-minute grace rule and the write behavior on that storage. |
| Non-administrator permissions test | Before the app runs under any account that is not the developer's administrator account, or is handed to another user | Run T1 to T4 with a real non-administrator account (the `chmod` case, labelled "non-admin only"). |

## B5. A5 for this round
The official list is the one in A5. The v2.5 Return Report adds the single line stated there.

## B6. Verification sequence (replaces A8 for this round)
1. The Builder implements B1 to B3 and returns the report (Builder Package items 1 to 4), with the commit SHA and the SHA-256 of every changed file, and the unchanged `close_history.py` hash.
2. The Architect re-verifies: hashes; rebuild from the patch; the full incremental difference from the v2.4 tip, read line by line; the Architect's tests, the equivalence run (distinct clocks) and the guard; each of N1 to N5, every variant, by injection or render test, compared with Message Wording.
3. The Principal runs T7 in full (Runs 1 to 3) on the v2.5 fingerprints, with screenshots. Failure criterion: no "Close-order notice" warning in any normal-path step.
4. The Architect writes the formal verification note, listing the open risks (B4) and the evidence limits. The Principal accepts it.
5. Only then does the Principal decide the merge. The Architect pushes and merges nothing.
6. The Handbook update, the Decision Log number and the Fiscal Quarter table item (a separate backlog item, not part of Fix K) come after.

---

# PART 0: ANSWERS TO THE PRINCIPAL'S FOUR OPEN ITEMS

| # | Open item | Status in this Brief |
|---|---|---|
| 1 | Abandoned or interrupted reopen: what signal establishes "no save occurred"? | **Designed; Principal approved** (D6 = 15 minutes, D7 = move incomplete folder aside, D8 = show a notice on release; see "Detection design"). |
| 2 | Scope of the reorder | **Closed.** Stated plainly below. |
| 3 | Tolerance 0.005 (D5) | **Architect technical confirmation. T11 on the sample dataset is required; T11 on production data is an open risk, not a condition (Principal decision 2026-10-05, B4).** Evidence below. No business decision needed unless the Principal wants a materiality threshold (that would be new scope, not proposed). |
| 4 | Test plan | **Included** (Part 2, "Testing"), with the admin-proof failure injection verified. |

### Item 1, in plain words (the most important finding)

**Nothing is written to the Close History folder while the Controller is stepping through a reopen.** The reopen steps ("Request reopen", "Confirm reopen", upload, "Run correction intake", "Continue") live only in the browser session. The downstream marks are written only inside the single click on **"Approve candidate close"**, and under Option 1 they are written a few seconds (measured about 2 seconds for a three-quarter chain, test data) before the correction is saved.

So there are two situations, and only the second needs new detection:

1. **The Controller walks away, the session times out, or the browser closes during the reopen steps.** No mark exists. Nothing to clear. Nothing changes. This is already the case today and stays the case.
2. **The application process dies inside the approval click**, after the marks are written and before the correction is saved (server killed, container reclaimed, power or storage loss). Then marks exist for a correction that was never saved. This is the only orphan window. A failed undo (section M5) creates the same situation and is handled by the same rule.

"Session ended" is **not** used as a signal anywhere in this design.

### Item 2: scope of the reorder

**The reorder applies ONLY to the reopen-and-correct path:** the "Approve candidate close" handler (`Northwind_Financial_Dashboard.py`, the single candidate `archive_close(...)` call site near line 2767).
**It does NOT change:**
- the first-time close of a period (the live "Approve close" handler near line 1802). That handler has no downstream propagation and keeps its current order. No attempt record, no new metadata.
- the Human Approval Gate (D13), the chronological close-order check, or any approval criterion.

### Item 3: tolerance 0.005

**Recommendation: confirm 0.005 as the Architect's technical value, subject to test T11.** Evidence from this review (TEST environment, sample dataset, pandas 3.0.6 rather than the pinned 2.2.3, so indicative only):
- Every compared field is a dollar amount, a dollar variance or a headcount (`CANONICAL_COMPARISON_SET`), so one tolerance is meaningful for all of them.
- Source amounts are whole cents (largest deviation from a 2-decimal value: 3.7e-9).
- The pipeline is deterministic: two independent runs and an Excel save/reload round trip gave zero differences at tolerance 0 on Q2, Q3, Q4.
- A real one-cent change in a Q3 revenue cell is detected at 0.005 and is **missed at 0.02**. So 0.005 is the largest "safe" value: it flags every real change of a cent or more and ignores only sub-cent noise.
- It equals the existing Phase 2 tie-out tolerance in `close_validation.py`.

**Consequence the Principal should understand:** any real change of one cent or more in a later quarter requires that quarter to be reopened. That is stricter than business materiality. If the Principal wants a materiality threshold (for example "ignore differences under $X"), that is a product decision and a new Brief. It is not proposed here. Caveat (amended by B4, Principal decision 2026-10-05): the 0.005 value was checked only on the sample dataset. It must be revisited when real data exists. This is an open risk with a stated trigger, not a condition of this Brief.

---

# PART 1: REQUIRED RESPONSE FORMAT (Architect analysis)

## Repository identification (evidence rules, section 2)

| Item | Value |
|---|---|
| Repository | 6-SoGH-9/Northwind-Autonomous-CFO |
| Branch | main |
| HEAD SHA | 691e8f41810ddf181cc4d7f6fbf4550aaf3dcdb9 (identical to origin/main) |
| Working tree | Clean, read-only, shallow clone. No repository file was modified. |
| Handbook reference commit | 0b1f353. Relation to 691e8f4 is the Builder's report, not verified by the Architect. |
| Files inspected | `period_lifecycle.py`, `close_history.py`, `Northwind_Financial_Dashboard.py`, `project_handbook.md`, `governance/architect/*`, project docs `d15_chronological_gate_required_response.md`, `d15_items_3_4_design_note.md` |

**Evidence classification**
- *Component evidence (CANONICAL):* code read. Flag writer and sidecar: `close_history.py` 523-575. Fallback: `period_lifecycle.py` 1295-1311. Candidate approve handler: dashboard 2736-2884.
- *Experiments run by the Architect in a scratch environment (NOT canonical, TEST):* admin-proof failure injection; tolerance measurements; crash-leftover behaviour of `archive_close`. Results are quoted below. Builder must repeat them on canonical code.
- *UI evidence (TEST, not canonical):* the Principal's Codespace reproduction of the original defect. Codespace SHA not recorded.
- **The normal, no-failure path has not been run in a live app by anyone in this review.**

## 1. REQUIREMENT

**Explicit (Principal):**
1. Option 1: write and verify the downstream marks **before** the correction is saved; if a required mark cannot be saved and read back, refuse the approval, save nothing, undo this attempt's marks.
2. D3: no session-level block. D4: a failed *clear* of an already-resolved mark does not refuse approval; it fails safe (over-blocks) and is reported.
3. Accepted cost: if storage cannot take the write, the correction is held until the cause is fixed.
4. A mark must clear automatically when it is established that no corresponding save occurred, regardless of why the session ended. "Session ended" is not abandonment.
5. The message "none had a saved close" must never appear when later closed quarters exist (from the original finding).

**Assumptions, flagged:**
- A1. The Codespace behaved like canonical main (unverified).
- A2. One approval at a time (see Category D). Two browsers approving at once against the same Close History is not protected today and is not made worse or better here.
- A3. The production Close History is a normal file system with the same atomic-replace behaviour as the Codespace. If production uses network or object storage, D6/M7 need review.

## 2. EXISTING AUTHORITY

| Source | Reference | Content | Class |
|---|---|---|---|
| Principal Decision "Fix K Mechanism Approved (Option 1)" | whole | Option 1, D3, D4, open items 1-4 | Principal decision |
| `d15_chronological_gate_required_response.md` | Section 1 (b), (c) | Affected later quarter must be reopened and re-closed before use; oldest reported first | Principal decision |
| `d15_items_3_4_design_note.md` | Sections 2, 4 | Flag is a per-period sidecar, separate from versioned snapshots | Design note (Principal-confirmed) |
| `project_handbook.md` | Section 7 fixes D, E, F | Damaged control files fail safe; uncomparable period treated as affected; stale flag auto-clearing | Built, Not Verified |
| `project_handbook.md` | Section 11a | Fix E/F/G confirmations open | Open decision |
| `ARCHITECT_GITHUB_AND_EVIDENCE_RULES.md` | Section 9 | Session state is not durable | Governance |

## 3. CLASSIFICATION

| Requirement | Class | Reasoning |
|---|---|---|
| Later affected quarter must be reopened before use; oldest first | **A** | Existing Principal decision. |
| Option 1 sequence: compare, write marks, verify, then save | **A** (approved) | Principal decision of 2026-10-01. |
| Refuse approval and save nothing if a mark cannot be saved and verified | **A** (approved) | Same. |
| Undo this attempt's marks on refusal or failed save | **A** (approved) | "Any marks written during that attempt are undone." |
| Drop session block (D3); failed clear does not refuse (D4) | **A** (approved) | Same. |
| Automatic clearing when no save occurred | **A** (approved principle); mechanism **B** | Principle approved; mechanism is this Brief's recommendation. |
| Attempt record on each mark (attempt id, prior state, expected version) and attempt id in the saved close's metadata | **D** | Technically necessary: without a durable link between a mark and its save, "no save occurred" cannot be established. Minimum-Scope: no smaller design gives that proof (Option 2's marker is the same idea in a separate file; this puts it in the mark itself). |
| Mark evaluated at read time (shows as not-flagged only when proven orphaned) | **D** | Necessary so every reader behaves the same without per-reader changes. Single point: `read_pending_reprocessing`. |
| Move an incomplete version folder aside (rename, never delete) | **B** | Needed so "approve again" in the refusal message can actually work (verified: see M6). Touches Close History, so the Principal decides. |
| Grace period before an unmatched mark is treated as orphaned | **B** | A number the Principal should know about (D6). |
| Notice to the Controller when an orphaned mark is released | **B (Principal decided: ON)** | D8. Finance control: a silent release is not acceptable. |
| Different tolerance or a materiality threshold | **E** | Not proposed. |
| Making other tabs show an "outdated" indicator; "View rendered prompt" expander; D19 rule 2 vs fix G; fix E/F/G confirmations | **Logged, not decided** | Per the Principal. Not in scope. |
| Derived/live comparison (Option 3) | **Separate investigation item** | Read-only, no build. Does not block this Brief. |

## 4. SUPERSEDED / DEFERRED DECISIONS

- v1 session-block design: **superseded** by the Principal (D3).
- v1 classification of durability as an accepted limitation: **withdrawn** (Architect error, corrected in SA-1).
- Design note section 4 (is a closed downstream quarter's content stale after an upstream reopen): still open, untouched.

## 5. GENUINE CONFLICTS

None identified. One interaction to note: Fix F (automatic clearing of marks on quarters that are no longer affected) now runs **before** the save, as the Principal stated. Its clear is therefore also part of the attempt (restorable, see M3/M5).

## 6. GOVERNANCE CHANGES REQUIRED

- New authorization: Category B items by approval of Part 3.
- On completion (Architect, not Builder): Handbook section 7 entry; section 11a updates; retire v1.

## 7. ARCHITECTURE IMPACT

- **Required:** reorder in the candidate approve handler; attempt record on marks and in the saved close's metadata; read-back verification; undo; read-time evaluation in one function; two messages.
- **Technically necessary:** `read_pending_reprocessing` is the only place the sidecar is read. All readers go through it: dashboard narrative gate (line 204), `find_close_order_blocker` (period_lifecycle 1242), `apply_propagation_flags` (1290), `resolve_pending_reprocessing`, and `reprocessing_state_by_period`. One change there covers all of them.
- **One thing the Builder must not miss:** the propagation comparison today reads the *archived copy* (`_archived_folder/rollups_output.xlsx`). Under Option 1 nothing is archived yet, so it must read the candidate's own file (`_cand["rollups_output_path"]`), which `archive_close` copies byte for byte.
- **Future / not now:** Option 3, and any indicator on other tabs.

## 8. IMPLEMENTATION IMPACT

(v2.4 scope. In the v2.5 round `close_history.py` must not change, see B2.) Files: `period_lifecycle.py` (fallback outcome, verification and undo helpers), `close_history.py` (attempt fields on write, read-time evaluation, incomplete-folder handling), `Northwind_Financial_Dashboard.py` (reorder and messages in the candidate handler only; **plus the release notice and its dismiss button, placed with the existing close-order notices near line 1251, which is explicitly in scope under M11**). No change to `rollups.py`, `close_validation.py`, `commentary_workflow.py`. Flag files gain optional fields; **old flag files without them must keep working exactly as today.**

## 9. TESTING IMPACT

See "Testing". The Handbook's cited 16/16 regression suite was not found by the Builder's review. The Builder must state which pre-existing checks it ran and which it could not locate.

## 10. DEPENDENCIES AND BLOCKING

| Dependency | Minimum-Scope Test | Blocking? |
|---|---|---|
| Fix E/F/G Principal confirmation | Brief works independently. If any of them is later rejected, the affected step is revisited. | No |
| Derived-option investigation | Separate, read-only. Option 1 does not need it. | No |
| Principal answers D6, D7, D8 | Answered in the Principal Addendum. | No (cleared) |

## 11. SEQUENCING RECOMMENDATION

Required: none. Convenient: confirm fix E/F/G in the same sitting. No bundling authorised.

## 12. READY FOR BUILDER BRIEF?

**YES, SUBJECT TO PRINCIPAL SIGNATURE OF THE GATE AND EXPLICIT RELEASE.** All Category B decisions are answered (Principal Addendum). Remaining before the Builder starts: the Principal's signature in Part 3.

---

# PART 2: BUILDER BRIEF (DRAFT)

## Objective

After a reopen-and-correct, the app must never end in the state "correction saved, but a later closed quarter that depends on it is silently not marked". It does this by marking and verifying first, saving second, and by releasing marks that provably belong to a save that never happened.

## Problem evidence (TEST, reproduced by the Principal in a Codespace)

With the downstream quarter's folder not writable, the correction was saved, the mark was not, and the page said "none had a saved close" while Q3 had one. The Narrative download for Q3 stayed available. Root cause in code: `flag_all_closed_downstream` swallows per-quarter exceptions (`except Exception: continue`), and the handler writes marks only after `archive_close`.

## Sequence required (candidate "Approve candidate close" handler only)

1. Keep the existing checks (close-order blocker, Human Approval Gate). Compute the expected next version for the reopened period. Generate one `attempt_id`.
2. Run the existing safe comparison and chain walk against the **candidate's** rollups file (not an archived copy). Same affected/unaffected rules, same stop rule, same tolerance.
3. For each affected quarter: write its mark, carrying `attempt_id`, the reopened period, the expected version, and `prior_state` (what the file contained before: nothing, an unresolved mark, a resolved mark, or damaged). For each examined unaffected quarter with an unresolved mark (Fix F): write the resolved state the same way.
4. Read every mark back and compare. If the normal path raised, use the fallback, which must produce an **explicit result per quarter**: `flagged`, `failed (error type and message)`, or `no saved close`. The silent `continue` is removed.
5. If any required mark is not saved and verified: **refuse the approval.** Call `archive_close` zero times. Undo this attempt's marks (M5). Show the refusal message. Stop.
6. Call `archive_close` with the same `attempt_id` in the saved close's metadata (`extra_metadata`, alongside the existing lineage fields). If it raises: undo (M5), move aside any incomplete folder this attempt created (M6), show message W4 (save failure), plus W5 (undo failure) once per quarter whose undo failed. Stop.
7. After a successful save, run the post-save steps: establish the baseline if absent; resolve the reopened quarter's own mark; clean up temp files. A failure here is **reported, not hidden, and not relied on for protection**. It never changes the outcome "saved".

## Scope In (mandatory)

- **M1** Fallback returns a per-quarter outcome. The message may say "no saved close" only for a quarter that genuinely has none. It must never say it for a quarter whose check failed.
- **M2** Reorder as above, candidate path only.
- **M3** Attempt record: marks and Fix F clears carry `attempt_id`, `expected_version` and `prior_state`; the saved close's metadata carries `attempt_id`. All optional fields. Old files unaffected.
- **M4** Read-back verification of every required mark before any save. Refusal on any failure.
- **M5** Undo of this attempt's marks: restore each quarter's exact `prior_state` (delete the file if there was none; if the prior file was damaged, leave the quarter **flagged**, fail-safe). Compare after restoring. If an undo fails, report it plainly with message W5 (undo failure), once per affected quarter, and rely on M7 plus fail-safe over-blocking. Do not raise.
- **M6** If `archive_close` fails after creating its version folder, the folder has no `metadata.json` and `archive_close` will refuse every retry. **Verified in the scratch environment:** `next_version_for_period` keeps offering the same version and the retry raises `FileExistsError`. So the handler must move that incomplete folder aside (rename to `v<n>.incomplete-<UTC timestamp>`; verified that retry then works and the readers ignore the renamed folder). **Never delete.** Only a folder with no `metadata.json` and only the version this attempt expected. This is Category B (D7).
- **M7** Read-time evaluation inside `read_pending_reprocessing` (details below).
- **M8** Messages W1 to W5 and notices N1 to N5 (Message Wording section), approved by the Principal (Addendum 2026-10-01; v2.4 decisions 2026-10-01 evening; N1 to N5 on 2026-10-05, with the plural rule of 2026-10-06).
- **M9** Post-save failures reported (step 7). Failure to clear the reopened quarter's own mark must be reported but does not undo the save.
- **M11 Release notice (D8), with dismiss button.** Whenever `read_pending_reprocessing` evaluates a mark as released (rule step 4), the Controller must see the notice above, one line per released quarter, naming the reopened quarter and the released quarter. **The notice stays visible, in the same place as the existing close-order notices (dashboard near line 1251, `st.warning`), until the Controller explicitly dismisses it with a dismiss button** (Principal decision). It returns after a browser refresh or an app relaunch for as long as the released (orphaned) mark file still exists, and it stops for good once a later approval or reopen touching that quarter replaces the file. **Dismissal is per browser session only:** it is not a persistent "acknowledged" record, and it does not change the mark, the file, or any other reader (blocking and the Narrative gate are unaffected). It must never appear for a mark that has a matching save (rule step 1) or is in doubt (steps 2-3). Any further acknowledgement mechanism is a Principal decision, not Builder discretion.
- **M10** No behaviour change on the no-failure path other than the order and the added optional fields. Same marks, same flags, same blocks as 691e8f4 for the same input (proved by T9).

## Detection design: how "no save occurred" is established

**Principle (Principal's):** if no correction was saved, nothing changed, so the mark is safe to release, regardless of why or how the session ended.

**Signal:** the save is the existence of a complete version folder, meaning one with a readable `metadata.json`. That file is written **last** by `archive_close`, and the existing readers already ignore a version folder without it. It is a durable fact on the same storage as the marks. It does not depend on the session, on Streamlit, on timers in the browser, or on the Codespace.

**Rule in `read_pending_reprocessing(period)`** (a mark that has no `attempt_id` is an old or post-save mark and is returned exactly as today):

1. Look at the reopened period's version folders. If a complete version carries the same `attempt_id` as the mark → **the save happened. Return the mark.** (This holds forever, including after any grace period.)
2. Otherwise, if the mark is younger than the grace period → **in doubt. Return the mark** (the attempt may still be running).
3. Otherwise, if the folder could not be listed or read for any reason → **in doubt. Return the mark** (fail-safe).
4. Otherwise (listing worked, no matching save, grace elapsed) → **established: no save occurred.** Return `prior_state` (nothing, or the earlier mark), as if this attempt never happened.

Properties: it is a pure read (no deletes on read), so a wrong release can be corrected on the next read once the save appears. The physical file is later overwritten or cleaned by the next normal write. Fix F and the baseline logic see the released state.

**Why a time value at all:** only to avoid releasing a mark while a healthy attempt is still inside its few seconds. It is **not** the evidence of abandonment. The evidence is the absence of the save. Proposed grace: **15 minutes** (the whole approval click takes seconds; this leaves a large margin without leaving a quarter blocked for long). D6.

**What the Controller sees:**
- During a real interruption, for up to the grace period: the quarter shows the normal "reopen and close it" block. The Controller can simply approve again for the same reopened quarter; the new attempt replaces the old (its `prior_state` is taken from the effective state, ignoring the in-doubt attempt).
- After the grace period: the block is gone, because nothing changed, **and the Controller is told (D8, Principal decision, ON by default):** "An earlier approval of Q2 2026 did not complete; no correction was saved and Q3 2026 is no longer marked." The notice stays visible until the Controller clicks its dismiss button. Dismissal lasts for that browser session only: it returns after a browser refresh or app relaunch for as long as the released mark file exists, and stops once a later approval or reopen touches that quarter (M11).
- If the save did happen: the mark stays, with the normal message, until Q3 is reopened and re-closed.

**Not covered, stated plainly:** concurrent approvals from two browsers (A2); production storage with delayed visibility (A3).

## Message Wording (APPROVED by the Principal; authoritative text, v2.5)

Periods are always shown as "Q2 2026" style labels. *error* / `<detail>` means the quoted operating-system or exception text, shown verbatim. The Builder implements these texts exactly. They replace the v2.3 refusal text. Change-request section 1a is superseded by this section.

**W1. Refusal, one quarter (earlier approval, last sentence removed on 2026-10-01 18:14):**
"Q2 2026 was NOT saved. Q3 2026 could not be marked as outdated (<error type>: <detail>), so the correction was refused. Fix the cause shown above (for example folder permissions or disk space) and approve again."
(Principal decision 2026-10-01 18:14: the last sentence of the earlier text, "If several quarters are listed, the oldest comes first.", is removed. W1 covers one quarter only.)

**W2. Refusal, several quarters (list format, oldest first):**
"Q2 2026 was NOT saved. The correction was refused because these quarters could not be marked as outdated:
- Q3 2026 (*error*)
- Q4 2026 (*error*)

Fix the cause shown above (for example folder permissions or disk space) and approve again. The oldest quarter is listed first."

**W3. Failed-clear notice:**
"An outdated flag on Q3 2026 could not be cleared (*error*). Q3 2026 stays blocked until it is reopened and re-closed."

**W4. Save failure (decided 2026-10-01 18:11; one message, no claim about flags):**
"Q2 2026 was NOT saved. The save failed (*error*). Fix the cause shown above (for example folder permissions or disk space) and approve again."

**W5. Undo failure (already approved; shown once per affected quarter, below W4 when the save failed):**
"The approval of Q2 2026 did not complete, but a flag for Q3 2026 from this attempt could not be undone (<detail>). Q3 2026 stays blocked for narrative and later closes until a later approval of Q2 2026 completes, the storage problem is fixed and the mark is released, or Q3 2026 is reopened and re-closed. Other tabs still show Q3 2026 figures without any warning."

(The v1 phrase "if another reopen is in progress, finish or cancel it first" is dropped: with no session block there is no such state. W5 is deliberately honest that other tabs give no warning; that gap is logged, not fixed.)

**Notices N1 to N5 (added in v2.5. The Principal approved the texts on 2026-10-05 and the N1 plural rule on 2026-10-06).** Each is shown with the prefix `Close-order notice: ` in front of the text below. The existing display code adds the prefix to plain-text notices, so the stored text does not include it. W3 keeps no prefix. `<error>` is the quoted exception text in the form `ErrorType: detail`, shown verbatim, in the same error detail slot as W1 to W5. Quarters in a list are written oldest first.

**N1. Post-save fallback notice.** Shown after a saved approval when the normal check of later quarters failed and the fallback marked quarters. It has a marked part and a no-saved-close part. Each part is optional. Build the text as: `Q2 2026 was saved. ` then the marked part `As a precaution, <list> <is/are> marked "may be outdated". Reopen and re-close <it/them>[ in that order].` then the no-saved-close part `<list> <has/have> no saved close, so nothing was marked.`
- One marked quarter: `Q2 2026 was saved. As a precaution, Q3 2026 is marked "may be outdated". Reopen and re-close it.`
- Two marked quarters: `Q2 2026 was saved. As a precaution, Q3 2026 and Q4 2026 are marked "may be outdated". Reopen and re-close them in that order.`
- Three or more marked quarters: `Q2 2026 was saved. As a precaution, Q3 2026, Q4 2026 and Q1 2027 are marked "may be outdated". Reopen and re-close them in that order.`
- No-saved-close part, one quarter: `Q4 2026 has no saved close, so nothing was marked.` Two quarters: `Q4 2026 and Q1 2027 have no saved close, so nothing was marked.` Three or more (the same list rule, derived from the marked rule): `Q4 2026, Q1 2027 and Q2 2027 have no saved close, so nothing was marked.`
- Both parts present: the marked part, then a space, then the no-saved-close part.
- No later quarter exists: `Q2 2026 was saved. No later quarter exists, so nothing was marked.`
- Why "in that order" (the Architect confirmed against the code, 2026-10-06): the app blocks closing or re-closing a quarter while an earlier quarter is still marked and unresolved (`find_close_order_blocker`, applied in the candidate approval handler). Re-closing Q4 before Q3 is refused with the existing message "Reopen and close Q3 2026 before closing Q4 2026". The phrase is therefore accurate and prevents a refused first attempt. **The Principal confirmed the phrase on 2026-10-06, given the code check above.**

**N2. Close-order bookkeeping failure (after a saved approval).** One notice per failed follow-up step.
- Recording the close order failed: `Q2 2026 was saved. A follow-up step failed: recording the close order (<error>). The saved version is complete.`
- Clearing Q2's own mark failed: `Q2 2026 was saved. A follow-up step failed: clearing the "may be outdated" mark on Q2 2026 itself (<error>). The saved version is complete.`

**N3. Comparison failed for one later quarter:** `Q3 2026 could not be compared with the corrected figures (<error>). It is treated as affected.`

**N4. Incomplete folder could not be moved aside:** `The incomplete folder for Q2 2026 (v2) could not be moved aside (<error>). It is not a saved version.` Here "v2" is the version number this attempt expected. No manual step is added, because that step is untested.

**N5. Check of later quarters failed:** `The check of later quarters failed (<error>). Every later quarter with a saved close is treated as affected.` N1 follows it and names the quarters.

**When each notice appears and what it triggers on is unchanged from the v2.4 delivery.** Only the text changes.

**Quoted-error exemption, defined narrowly (guard rule).** The exemption covers only the error detail slot: the text substituted for `<error type>: <detail>`, `<error>` or `*error*` inside the parentheses in W1 to W5 and N2 to N5, and nothing else. N1 has no error slot and gets no exemption. The guard recognizes it by construction, not by pattern: each guard test injects a known sentinel error string (for example `OSError: [Errno 13] Permission denied: '/data/close_history/Q2 FY2026/v2'`) through that slot, removes exactly that sentinel from the rendered text, and then scans what remains. Any "FY" token outside the sentinel, including in the fixed wording around it, fails. A path appearing anywhere else in a message is not exempt unless it arrives inside the error detail slot. The folder-path exemption in A3 means this same slot.

## Scope Out (explicit exclusions)

- First-time close path; Human Approval Gate; close-order logic; comparison rules and stop rule.
- Option 3 (derived comparison) and Option 2 as a separate marker file.
- Indicators on other tabs; "View rendered prompt" expander; D19 rule 2 vs fix G; Fix E/F/G wording.
- Retry/repair tooling; deleting anything in Close History; concurrency control; materiality threshold; code-quality tiers from the Builder review.

## Testing (all five required groups, plus regression)

For every test: record the commit SHA tested, state whether it ran on canonical code, and give the command or UI steps.

**Failure injection that an administrator cannot bypass.** Do **not** use `chmod a-w` as the proof: an administrator (root) writes straight through it (**verified: with root, the write succeeded despite read-only permissions**). Use instead a **directory placed where the temporary file must be created** (`<quarter folder>/pending_reprocessing.json.tmp`). **Verified:** as root this makes the write fail with `IsADirectoryError`. For the save step use a **plain file named `v<n>`** where the version folder must be created. `chmod` may be used as a second, labelled "non-admin only" case.

- **T1 Refusal.** Obstruct Q3's mark. Approve a Q2 correction that affects Q3. Expect: no `v<n+1>` folder for Q2, Q2's latest version unchanged, no baseline written, no mark left on Q3 or Q4, refusal message names Q3 and the error, "none had a saved close" absent.
- **T2 Partial.** Q3 writes, Q4 obstructed. Expect Q3 restored byte-for-byte to its prior state, in three variants: no prior mark, prior unresolved mark, prior resolved mark. Also a Fix F clear on a third quarter is restored.
- **T3 Save failure.** Marks succeed, version path obstructed. Expect marks undone, message W4, then retry succeeds after the obstruction is removed. Variant with a crash mid-copy (incomplete folder): incomplete folder moved aside, retry succeeds, no data deleted.
- **T4 Failed undo.** Marks succeed, save fails, undo of Q3 obstructed. Expect message W5 (undo failure) below W4, Q3 blocked on the Narrative tab, `find_close_order_blocker` and the `reprocessing_state_by_period` path. After the obstruction is cleared and the grace period passes (clock injected), Q3 is released by M7, with no manual step.
- **T5 Interrupted approval (the abandonment case).** (a) Controller walks through reopen steps and the session ends: assert no mark file exists at any point before the Approve click. (b) Process killed after the marks are written and before the save: within grace Q3 is blocked everywhere; after grace (clock injected) it is released everywhere (narrative gate, close-order blocker, state map); Q2 shows its prior version. Run (b) with a real killed subprocess, not only a simulated exception. (c) After release, the D8 notice appears with the exact wording, names the right quarters, and **stays visible across in-session reruns and clicks until the dismiss button is clicked; after dismissal it stays hidden for the rest of that browser session, and the mark, the file and every other reader (Narrative gate, close-order blocker, state map) are unchanged by dismissing; it reappears after a browser refresh and after an app relaunch** while the released mark file still exists, and stops once a later approval or reopen touches that quarter. It does not appear in T6, in T7, or during the grace period.
- **T6 False-release guard (critical).** Process killed **after** the save and **before** post-save steps. Expect the mark to survive past the grace period, because the matching complete version exists. Also: version folder unreadable (permissions or unavailable) → mark stays (fail-safe).
- **T7 Normal path, live app.** In a live app on canonical code: close Q1-Q3, reopen Q2, upload corrected data that changes Q3, approve. Expect Q2 v2 saved, Q3 marked, Narrative blocked for Q3, reopen and re-close Q3 clears it. Second run with a correction that changes nothing downstream: no marks and a stale mark cleared. **Status:** run by the Principal on the v2.4 fingerprints, 2026-10-04 and 2026-10-05 (Principal-observed; Python 3.12.3; no byte-for-byte file comparison). It must be **repeated in full (Runs 1 to 3 of the Architect's checklist) on the v2.5 fingerprints**, with this failure criterion added: no "Close-order notice" warning appears in any normal-path step. Principal or Controller screenshots, not Builder narration.
- **T8 Compatibility.** Flag files written by 691e8f4 (no attempt fields) behave exactly as before for every reader.
- **T9 Equivalence.** For the same inputs, the set of marks written is identical to 691e8f4's.
- **T10 First-time close unchanged.** Live "Approve close" writes no marks, no attempt metadata, same order as before.
- **T11 Tolerance.** One-cent change detected; sub-half-cent difference ignored; run on the sample dataset under the pinned pandas 2.2.3, and report any noise above 0.005. Production data is an open risk, not a condition (B4).
- **T12 Regression.** Run whatever pre-existing checks exist; list those that could not be located.
- **T13 Notice wording (v2.5).** For N1 (every variant: one, two, three or more marked quarters; no-saved-close part with one, two and three or more quarters; both parts; no later quarter), N2 (both steps), N3, N4 and N5: the rendered text equals the Message Wording text exactly, with the `Close-order notice: ` prefix, and W3 has none. The label guard covers every path with the sentinel error method. Trigger each notice by failure injection where the UI allows and by a render test otherwise, and say which.

## Builder Package

1. Code changes in `period_lifecycle.py`, `Northwind_Financial_Dashboard.py` and the guard test `build_test/fixk_fy_label_guard.py` (and the Builder's own tests for these messages) only, on a branch, with the tested commit SHA. **`close_history.py` must not change in this round** (B2). The earlier phrase "the three files" in this file refers to the v2.4 round.
2. Return Report with test evidence per T1 to T13, each marked canonical or not, and an explicit list of tests not run.
3. (v2.5) The Return Report also states: the new SHA-256 of every changed file; that `close_history.py` is unchanged (hash `337d2139f3cc5bb872ee1df86561067709489b09d5aca59473ccfcbdd3fd3e83`); a table of N1 to N5 showing the code location and the rendered text for every variant; the A5 line from A5 above; and which tests were re-run on the new commit (T1 to T13), each marked canonical or not.
4. Product-operability answer (required final question): can the Controller, in the actual canonical app, perform a reopen-and-correct, and be refused cleanly when storage fails, without developer intervention? Evidence for each link. Components existing is not an answer.

---

# PART 3: SCOPE AUTHORIZATION GATE (PRINCIPAL SIGN-OFF REQUIRED)

**Brief Title:** D15 Items 3 and 4, Post-Release Fix K (v2): "No Flag, No Approval"

**Status:** v2.3 ☑ approved and released. v2.4 ☑ APPROVED (Principal, 2026-10-01 18:16). v2.5 ☑ APPROVED (Principal, 2026-10-06 05:33)  ☐ BLOCKED  ☐ AWAITING PRINCIPAL DECISION

## PRINCIPAL ADDENDUM (2026-10-01), RECORDED

- Approved as drafted: Option 1 sequence; D6 (15 minutes); D7 (rename incomplete folder aside, never delete); both messages; tolerance 0.005 as an Architect technical value, **conditional on T11 run on production-like data under the pinned pandas 2.2.3**. **[Amended by the Principal 2026-10-05 (B4): the condition is removed. T11 on production data is an open risk with a trigger, not a merge condition. This bullet is kept as the record of the original decision.]**
- **D8 changed by the Principal:** notice on release is ON (finance control). Incorporated as M11.
- Confirmed: (1) the order flip ("mark and verify, then save") is a deliberate reversal of the earlier confirmed design ("save, then mark"); (2) abandoning a reopen before the Approve click leaves no mark; a crash during the click leaves later quarters blocked until the 15-minute grace plus absence of a matching save releases them.
- **Production storage footnote (accepted by the Principal, not a blocker):** the detection design assumes a write either fully completes or fully fails with no partial-visibility window (Codespace file system). **Must be explicitly revisited if the project moves to different storage** (network or object storage with delayed visibility), which could release a mark too early or leave a quarter stuck.
- **Architect recommendation, not a Principal decision (Principal has no objection):** the Builder records the footnote above as a code comment at the evaluation function and in the Return Report. This instruction was added by the Architect.
- Unchanged: reorder scope (reopen-and-correct only); all Category E items remain not authorized.

## CATEGORY A: ALREADY AUTHORIZED

| Requirement | Authoritative Source | Incorporated? |
|---|---|---|
| Later affected quarter must be reopened and re-closed first; oldest first | `d15_chronological_gate_required_response.md` 1(b)(c) | ☑ |
| Marks written and verified before the save; refuse and save nothing on failure; undo this attempt's marks | Principal Decision, Option 1 | ☑ |
| No session block (D3); failed clear does not refuse (D4) | Principal Decision | ☑ |
| Marks clear automatically when no save occurred; session end is not abandonment | Principal Decision, open item 1 | ☑ (principle) |
| Reorder limited to reopen-and-correct | Principal Decision, open item 2 | ☑ |

## CATEGORY B: NEW PRINCIPAL DECISIONS (defaults in bold)

| Decision | Recommendation | Incorporated? |
|---|---|---|
| **D6** Grace before an unmatched mark is treated as orphaned | **15 minutes**; evidence of abandonment is the missing save, not the time | ☑ Principal approved |
| **D7** Move an incomplete version folder aside (rename, never delete) so a retry can work | Include (M6) | ☑ Principal approved |
| **D8** Tell the Controller when a mark is released | **Notice ON** (Principal changed the Architect's default of silent release) | ☑ Principal decided (M11) |
| Message wording, ten texts: W1 refusal (one quarter); W2 refusal (several quarters, list, oldest first); W3 failed-clear notice; W4 save failure (decided 2026-10-01 18:11); W5 undo failure; plus N1 post-save fallback notice, N2 bookkeeping failure, N3 comparison failed, N4 incomplete folder not moved aside, N5 check of later quarters failed | Exact texts in the Message Wording section (Part 2) | ☑ W1 to W5 Principal approved (W1, W2, W3, W5 earlier; W4 on 2026-10-01 18:11). ☑ N1 to N5 texts approved 2026-10-05, N1 plural rule 2026-10-06. ☑ "in that order" in N1 confirmed 2026-10-06 |
| "Close-order notice:" prefix on N1 to N5; none on W3 | Principal decision 2026-10-05 | ☑ Principal decided |
| Route for N1 to N5: part of this consolidated v2.5 Brief | Principal decision 2026-10-05 and 2026-10-06 | ☑ Principal decided |
| Tolerance 0.005 | Architect technical value. T11 required on the sample dataset (pinned pandas 2.2.3). Production data is an open risk with a trigger (B4), not a condition | ☑ Principal approved; condition removed by Principal decision 2026-10-05 |
| Production storage assumption | Footnote; revisit if storage changes | ☑ Principal accepted |

## CATEGORY C: GENUINE CONFLICTS

None identified.

## CATEGORY D: TECHNICAL / PROCEDURAL CONSTRAINTS

| Constraint | Handling | Blocking? |
|---|---|---|
| One approval at a time (no concurrency control exists today) | Unchanged; stated | No |
| Production storage assumed to behave like the Codespace file system | Principal asked that production not be assumed to match; rule uses only file existence/readability and fails safe when unreadable. Principal accepted this as a footnote (Addendum 2026-10-01): not a blocker; revisit only if the project moves to different storage | No |
| Marks need a durable link to their save | Attempt record in the mark and in the saved close's metadata | No |
| Fix E/F/G unconfirmed | Brief independent | No |
| Handbook's 16/16 suite not located | Builder reports what exists | No |

## CATEGORY E: ARCHITECT RECOMMENDATIONS (not authorized)

| Recommendation | Reason | Principal Authorization |
|---|---|---|
| Materiality threshold instead of half a cent | Fewer reopens for trivial differences; changes the business rule | ☐ Not authorized |
| Indicator on other tabs for a marked quarter | Closes the "other tabs show figures with no warning" gap | ☐ Not authorized (logged) |
| Gate the "View rendered prompt" expander | Same | ☐ Not authorized (logged) |
| Option 3 derived comparison | Long-term durability without marks | ☐ Not authorized (separate investigation approved, no build) |

## EXPLICIT EXCLUSIONS

Everything in Part 2 "Scope Out". Authority: Principal decision of 2026-10-01 and the logged-not-decided list.

## MINIMUM-SCOPE VERIFICATION

☑ Minimum implementation identified (v2.4 scope: three files; one read function covers all readers. v2.5 scope: B2)
☑ Claimed dependencies tested (D6, D7 and D8 are all answered in the Principal Addendum; no gating items remain)
☑ Workarounds considered (marker file, derived check, session block: separated)
☑ Optional architecture separated
☑ No unnecessary bundling introduced

## PRINCIPAL APPROVAL GATE

I confirm that:

☐ This Brief includes ALL requirements I have decided.
☐ This Brief includes NO product scope I did not authorize.
☐ The exclusions accurately represent my deferred/out-of-scope decisions.
☐ The Architect has not silently narrowed my authorized scope.
☐ The Architect has not silently expanded my authorized scope.
☐ Architect recommendations are clearly separated from mandatory scope.
☐ I understand that Builder implements ONLY the authorized scope in this Brief.
☐ If the Brief is incomplete, I will request clarification before issuing it.

**Specific confirmations requested:**
Given in the Principal Addendum (recorded above): D6, D7, D8 (notice ON), message wording, tolerance 0.005 (T11 condition amended by B4), order-flip understanding, interrupted-click understanding, storage footnote.
☐ Principal signs below to confirm the Brief as amended (v2.4) and releases it to the Builder. **(v2.4 signature: given 2026-10-01 18:16. The v2.5 signature is in the v2.5 SIGNATURE block below.)**

**Approved by Principal:** by written statement in the session, "I, the Principal, validate the brief", on v2.3, recorded by the Architect. **Date:** 2026-10-01, 11:56 Europe/London. (The eight individual boxes above are the Principal's own; the Architect has not ticked them on the Principal's behalf. Request a ticked copy if the formal checklist must be complete.)

## v2.4 SIGNATURE (Part 0-bis)

☐ Principal signs v2.4 (A1 to A8) (A3-Q already decided: annual `FY####` labels exempt, recorded 2026-10-01 18:00)
☑ Save-failure wording A4: decided by the Principal 2026-10-01 18:11 (single message W4).
**Approved by Principal:** by written statement in the session, "This version is good. I validate it and will make it canonical and send it to the builder", on v2.4, recorded by the Architect. **Date:** 2026-10-01, 18:16 Europe/London. (As with v2.3, the individual Gate boxes are the Principal's own; the Architect has not ticked them on the Principal's behalf.)

## v2.5 SIGNATURE (Part 0-ter)

☑ Principal signs v2.5 (B1 to B6, N1 to N5, T13, the T11 amendment and the open-risk triggers in B4)
☑ N1 plural wording includes "in that order" (ticked by the Architect on the Principal's written instruction of 2026-10-06, given after the code check; the Principal's other boxes below are his own)
☑ B4 triggers confirmed by the Principal as written (T11 on real data, concurrent approvals, production storage, non-administrator permissions), 2026-10-06
**Approved by Principal:** by written statement in the session, "I sign it", on the reissue of 2026-10-06 (SHA-256 `061f2af5d6a875392300a3dc75d47192e684ca76f64f94b140cdb705af4f0842`), recorded by the Architect.   **Date and time (Europe/London):** 2026-10-06, 05:33, as stated by the Principal. (The eight Gate boxes in the Principal Approval Gate above remain the Principal's own. The Architect has not ticked them.)

## ARCHITECT ATTESTATION

☑ Reviewed the relevant Handbook sections and design documents.
☑ Reviewed canonical repository state (main, 691e8f4).
☑ Classified all material scope; applied the Required Response Format and Minimum-Scope Test.
☑ Did not bundle scope without authorization; did not use technical preference as product authority.
☑ Did not silently narrow or expand Principal scope.
☑ This Brief accurately represents the authorized scope, **including the Principal Addendum (D8 notice ON, M11) as of v2.3, the Part 0-bis amendments A1 to A8 as of v2.4, and the Part 0-ter amendments B1 to B6 as of v2.5.** v2.5 changes wording and test coverage only and expands no scope. Attestation is not Principal authorization.

**Architect:** Claude   **Date:** 2026-10-01 (v2.4); 2026-10-06 (v2.5)

## RELEASE RULE

**v2.5 is RELEASED** by the Principal's signature of the v2.5 SIGNATURE block on 2026-10-06 05:33. The Builder receives this one file and nothing else. Nothing is pushed or merged by the Architect.


The Builder Brief was **RELEASED on 2026-10-01 11:56** by the Principal's written approval. (Rule retained: it is not released until the Principal Approval Gate is explicitly approved. The Architect's attestation does not substitute for Principal authorization.)
