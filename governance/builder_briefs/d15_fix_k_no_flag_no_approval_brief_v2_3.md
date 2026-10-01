# D15 Items 3 and 4, Post-Release Fix K (v2): "No Flag, No Approval" for Reopen-and-Correct

**STATUS: v2.3. APPROVED AND RELEASED TO THE BUILDER by the Principal, 2026-10-01 11:56 (Europe/London).** Principal decisions D6, D7, D8, message wording and tolerance were given in the Principal Addendum (2026-10-01, later same day) and are incorporated below. D8 is CHANGED from the Architect's default. The Principal's written statement "I, the Principal, validate the brief" (recorded in Part 3) is the approval and release. No content changed after v2.3 was issued.
**Supersedes:** `builder_brief_fix_k_flag_save_failure_DRAFT.md` (v1, session-block design). v1 must not be used.
**v2.3 changes from v2.2 (Principal review, two items; nothing else changed):** (1) M11, "What the Controller sees" and T5(c): the notice stays visible until the Controller explicitly dismisses it (dismiss button, per browser session only); replaces "once per page load" and removes the Architect practicality note; (2) Part 1 section 8 Implementation Impact: notice placement near dashboard line 1251 explicitly included. Mechanical: version labels and Brief ID updated to v2.3.
**v2.2 changes from v2.1 (Principal review, six items; nothing else changed):** (1) M11, "What the Controller sees" and T5(c): notice once per page load or launch, not on every rerun; (2) Category D storage row aligned with the Addendum; (3) Minimum-Scope Verification line corrected; (4) message wording marked approved (heading and M8); (5) file renamed and Brief ID stated; (6) code-comment instruction recorded as an Architect recommendation. Mechanical: version labels updated to v2.2.
**v2.1 changes from v2:** D8 notice ON by default (M11), Principal confirmations and storage footnote recorded, Gate and attestation updated.
**Brief ID:** `d15_fix_k_no_flag_no_approval_brief_v2_3` (file-name convention used by the existing briefs in `governance/builder_briefs/`; assigned by the Architect here). The Decision Log "D" number is not assigned: the governance files I read define no assignment rule and the D16/D18 numbering is unresolved in the Handbook. Proposal: the Architect assigns it when recording this fix in Handbook Section 7 after completion; the Principal may override.
**Date drafted:** 2026-10-01
**Responds to:** Principal Decision "Fix K Mechanism Approved (Option 1)" (via Project Advisor) and the four open items in it.

---

# PART 0: ANSWERS TO THE PRINCIPAL'S FOUR OPEN ITEMS

| # | Open item | Status in this Brief |
|---|---|---|
| 1 | Abandoned or interrupted reopen: what signal establishes "no save occurred"? | **Designed; Principal approved** (D6 = 15 minutes, D7 = move incomplete folder aside, D8 = show a notice on release; see "Detection design"). |
| 2 | Scope of the reorder | **Closed.** Stated plainly below. |
| 3 | Tolerance 0.005 (D5) | **Architect technical confirmation, conditional on test T11.** Evidence below. No business decision needed unless the Principal wants a materiality threshold (that would be new scope, not proposed). |
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

**Consequence the Principal should understand:** any real change of one cent or more in a later quarter requires that quarter to be reopened. That is stricter than business materiality. If the Principal wants a materiality threshold (for example "ignore differences under $X"), that is a product decision and a new Brief. It is not proposed here. Caveat: the check must be repeated on production-like data (T11) before the value is called confirmed.

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

Files: `period_lifecycle.py` (fallback outcome, verification and undo helpers), `close_history.py` (attempt fields on write, read-time evaluation, incomplete-folder handling), `Northwind_Financial_Dashboard.py` (reorder and messages in the candidate handler only; **plus the release notice and its dismiss button, placed with the existing close-order notices near line 1251, which is explicitly in scope under M11**). No change to `rollups.py`, `close_validation.py`, `commentary_workflow.py`. Flag files gain optional fields; **old flag files without them must keep working exactly as today.**

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
6. Call `archive_close` with the same `attempt_id` in the saved close's metadata (`extra_metadata`, alongside the existing lineage fields). If it raises: undo (M5), move aside any incomplete folder this attempt created (M6), show the failure message. Stop.
7. After a successful save, run the post-save steps: establish the baseline if absent; resolve the reopened quarter's own mark; clean up temp files. A failure here is **reported, not hidden, and not relied on for protection**. It never changes the outcome "saved".

## Scope In (mandatory)

- **M1** Fallback returns a per-quarter outcome. The message may say "no saved close" only for a quarter that genuinely has none. It must never say it for a quarter whose check failed.
- **M2** Reorder as above, candidate path only.
- **M3** Attempt record: marks and Fix F clears carry `attempt_id`, `expected_version` and `prior_state`; the saved close's metadata carries `attempt_id`. All optional fields. Old files unaffected.
- **M4** Read-back verification of every required mark before any save. Refusal on any failure.
- **M5** Undo of this attempt's marks: restore each quarter's exact `prior_state` (delete the file if there was none; if the prior file was damaged, leave the quarter **flagged**, fail-safe). Compare after restoring. If an undo fails, report it plainly (variant message), and rely on M7 plus fail-safe over-blocking. Do not raise.
- **M6** If `archive_close` fails after creating its version folder, the folder has no `metadata.json` and `archive_close` will refuse every retry. **Verified in the scratch environment:** `next_version_for_period` keeps offering the same version and the retry raises `FileExistsError`. So the handler must move that incomplete folder aside (rename to `v<n>.incomplete-<UTC timestamp>`; verified that retry then works and the readers ignore the renamed folder). **Never delete.** Only a folder with no `metadata.json` and only the version this attempt expected. This is Category B (D7).
- **M7** Read-time evaluation inside `read_pending_reprocessing` (details below).
- **M8** Messages (below). Both **approved by the Principal as drafted** (Addendum 2026-10-01).
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

## Message Wording (APPROVED by the Principal as drafted, Addendum 2026-10-01)

**Refusal (marks could not be saved, or save failed, undo succeeded):**
"Q2 2026 was NOT saved. Q3 2026 could not be marked as outdated (<error type>: <detail>), so the correction was refused. Fix the cause shown above (for example folder permissions or disk space) and approve again. If several quarters are listed, the oldest comes first."

**Undo failure variant:**
"The approval of Q2 2026 did not complete, but a flag for Q3 2026 from this attempt could not be undone (<detail>). Q3 2026 stays blocked for narrative and later closes until a later approval of Q2 2026 completes, the storage problem is fixed and the mark is released, or Q3 2026 is reopened and re-closed. Other tabs still show Q3 2026 figures without any warning."

(The v1 phrase "if another reopen is in progress, finish or cancel it first" is dropped: with no session block there is no such state.) The second message is deliberately honest that other tabs give no warning; that gap is logged, not fixed.

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
- **T3 Save failure.** Marks succeed, version path obstructed. Expect marks undone, failure message, then retry succeeds after the obstruction is removed. Variant with a crash mid-copy (incomplete folder): incomplete folder moved aside, retry succeeds, no data deleted.
- **T4 Failed undo.** Marks succeed, save fails, undo of Q3 obstructed. Expect the undo-failure message, Q3 blocked on the Narrative tab, `find_close_order_blocker` and the `reprocessing_state_by_period` path. After the obstruction is cleared and the grace period passes (clock injected), Q3 is released by M7, with no manual step.
- **T5 Interrupted approval (the abandonment case).** (a) Controller walks through reopen steps and the session ends: assert no mark file exists at any point before the Approve click. (b) Process killed after the marks are written and before the save: within grace Q3 is blocked everywhere; after grace (clock injected) it is released everywhere (narrative gate, close-order blocker, state map); Q2 shows its prior version. Run (b) with a real killed subprocess, not only a simulated exception. (c) After release, the D8 notice appears with the exact wording, names the right quarters, and **stays visible across in-session reruns and clicks until the dismiss button is clicked; after dismissal it stays hidden for the rest of that browser session, and the mark, the file and every other reader (Narrative gate, close-order blocker, state map) are unchanged by dismissing; it reappears after a browser refresh and after an app relaunch** while the released mark file still exists, and stops once a later approval or reopen touches that quarter. It does not appear in T6, in T7, or during the grace period.
- **T6 False-release guard (critical).** Process killed **after** the save and **before** post-save steps. Expect the mark to survive past the grace period, because the matching complete version exists. Also: version folder unreadable (permissions or unavailable) → mark stays (fail-safe).
- **T7 Normal path, live app.** In a live app on canonical code: close Q1-Q3, reopen Q2, upload corrected data that changes Q3, approve. Expect Q2 v2 saved, Q3 marked, Narrative blocked for Q3, reopen and re-close Q3 clears it. Second run with a correction that changes nothing downstream: no marks and a stale mark cleared. **Nobody has run this yet.** Principal or Controller screenshots, not Builder narration.
- **T8 Compatibility.** Flag files written by 691e8f4 (no attempt fields) behave exactly as before for every reader.
- **T9 Equivalence.** For the same inputs, the set of marks written is identical to 691e8f4's.
- **T10 First-time close unchanged.** Live "Approve close" writes no marks, no attempt metadata, same order as before.
- **T11 Tolerance.** One-cent change detected; sub-half-cent difference ignored; run on production-like data and the pinned pandas 2.2.3, and report any noise above 0.005.
- **T12 Regression.** Run whatever pre-existing checks exist; list those that could not be located.

## Builder Package

1. Code in the three files above, on a branch, with the tested commit SHA.
2. Return Report with test evidence per T1-T12, each marked canonical or not, and an explicit list of tests not run.
3. Product-operability answer (required final question): can the Controller, in the actual canonical app, perform a reopen-and-correct, and be refused cleanly when storage fails, without developer intervention? Evidence for each link. Components existing is not an answer.

---

# PART 3: SCOPE AUTHORIZATION GATE (PRINCIPAL SIGN-OFF REQUIRED)

**Brief Title:** D15 Items 3 and 4, Post-Release Fix K (v2): "No Flag, No Approval"

**Status:** ☑ APPROVED AND RELEASED (v2.3)  ☐ BLOCKED  ☐ AWAITING PRINCIPAL DECISION

## PRINCIPAL ADDENDUM (2026-10-01), RECORDED

- Approved as drafted: Option 1 sequence; D6 (15 minutes); D7 (rename incomplete folder aside, never delete); both messages; tolerance 0.005 as an Architect technical value, **conditional on T11 run on production-like data under the pinned pandas 2.2.3**.
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
| Message wording (refusal and undo-failure) | As drafted above | ☑ Principal approved |
| Tolerance 0.005 | Architect technical value, conditional on T11 (production-like data, pinned pandas 2.2.3) | ☑ Principal approved, condition stands |
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

☑ Minimum implementation identified (three files; one read function covers all readers)
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
Given in the Principal Addendum (recorded above): D6, D7, D8 (notice ON), message wording, tolerance 0.005 (conditional on T11), order-flip understanding, interrupted-click understanding, storage footnote.
☐ Principal signs below to confirm the Brief as amended (v2.3) and releases it to the Builder.

**Approved by Principal:** by written statement in the session, "I, the Principal, validate the brief", on v2.3, recorded by the Architect. **Date:** 2026-10-01, 11:56 Europe/London. (The eight individual boxes above are the Principal's own; the Architect has not ticked them on the Principal's behalf. Request a ticked copy if the formal checklist must be complete.)

## ARCHITECT ATTESTATION

☑ Reviewed the relevant Handbook sections and design documents.
☑ Reviewed canonical repository state (main, 691e8f4).
☑ Classified all material scope; applied the Required Response Format and Minimum-Scope Test.
☑ Did not bundle scope without authorization; did not use technical preference as product authority.
☑ Did not silently narrow or expand Principal scope.
☑ This Brief accurately represents the authorized scope, **including the Principal Addendum (D8 notice ON, M11) as of v2.3.** Attestation is not Principal authorization.

**Architect:** Claude   **Date:** 2026-10-01

## RELEASE RULE

The Builder Brief was **RELEASED on 2026-10-01 11:56** by the Principal's written approval. (Rule retained: it is not released until the Principal Approval Gate is explicitly approved. The Architect's attestation does not substitute for Principal authorization.)
