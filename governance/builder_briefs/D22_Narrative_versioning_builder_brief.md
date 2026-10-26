# D22 Narrative Versioning, Number Check and Flags: Builder Brief v3 (SIGNED BY THE PRINCIPAL, 2026-10-26)

**STATUS: SIGNED BY THE PRINCIPAL, 2026-10-26 (Part 3 signature block). The text below the signature lines is the text the Principal reviewed (SHA-256 `eecbf42989964f64aea3f163a18cc8d1437bc4731a4297fc2ca5e46f7c372365`, the unsigned v3 committed in `1e2f44c`). Only this status line, the title, the Gate ticks, the signature and the release rule differ from it.** The Principal makes it canonical and sends it to the Builder. The Builder does not start until this signed file is on canonical `main`. The committed path is `governance/builder_briefs/D22_Narrative_versioning_builder_brief.md`; the Brief ID in the header below is unchanged. Briefs v1 and v2 were never released and are superseded by this file.
**Brief ID:** `d22_narrative_versioning_builder_brief_v3` (proposed path: `governance/builder_briefs/d22_narrative_versioning_builder_brief_v3.md`; v1 and v2 were never released and are superseded by this file; ID assigned by the Architect, the Principal may override).
**Date drafted:** 2026-10-26 (v2 and v3 the same day, after the Advisor's two reviews).
**v3 changes from v2 (Advisor note of 2026-10-26, six small fixes, each verified by the Architect; no scope, decision or evidence class changed):** (1) Part 1 section 3, line B, now says Category E, as the Gate does; (2) "four points" corrected to five in Part 0 and Part 1 section 1; (3) a block "If Gate decision 1 is (b)" lists exactly what drops out and what remains; (4) Required evidence is split by release in a table; (5) the consequence of an undeletable draft folder is stated as accepted (WP2-10); (6) the Annual fix is classified the same way in Category A, Part 0 and Gate decision 2.
**v2 changes from v1 (Advisor review of 2026-10-26; analysis for the Principal, each point verified by the Architect against `65d71ca`; no decision reopened, D22-H (13)):** (1) Part 0 item 1 now states that every narrative finalized in this release has no deck and no rebuild exists, and offers the Principal two options; (2) draft numbering reads "present" from the record and from the disk, and the fate of the finalized draft's own folder and of a failed delete is stated (WP2-3, WP2-10); (3) the mark example is restated with gap-free numbers (WP2-11); (4) six missing required tests added; (5) every criterion has an ID (WP*k*-*n*); (6) the live AI call is removed from Builder evidence; (7) the regression set is named; (8) the deck relabel and the Quarterly-only flow move from Category D to Category E and are listed as Principal decisions at the Gate, and WP2 now says the behaviours are required and the layout is the recommendation; (9) the exemption of the user's notes from the check is labelled the Brief's reading; (10) staging recommended, the Annual fix reading stated, the classifier copy named in the Return Report, and the Principal's wording quoted. Part 3 gains a block of five Principal decisions.
**Provenance of the instruction (quoted):** Principal, 2026-10-15, close-out, section 4: "2. Then the Builder Brief for the parts of D22 that do not depend on the deferred items. Please say in the Brief what is in and out of scope, what evidence is required, and which files may and may not be changed. 3. The Brief must be reviewed by me before any building starts." Principal, 2026-10-26 05:37: "so you can now write the builder brief" (taken as his confirmation that v2.28 at `65d71ca` is canonical; the repository cannot show this, so the Principal confirms it at the Gate).
**Responds to:** Principal instruction of 2026-10-26 ("so you can now write the builder brief"), following the close-out of 2026-10-15 (D22-H (12), (13)).
**Canonical state:** repository `6-SoGH-9/Northwind-Autonomous-CFO`, branch `main`, HEAD = `origin/main` = `65d71ca5dcff12bd9a331235a01514b68ba70a9d` ("Add files via upload", 2026-10-15 08:55), working tree clean, checked 2026-10-26. `65d71ca` is the Handbook v2.28 revision and the observations report (SHA-256 of both committed files equals the files the Architect delivered on 2026-10-15). Only these two files changed between `b20d4b1` and `65d71ca`, so every code fact below, checked at `b20d4b1`, still holds at `65d71ca`. The Principal's instruction to write the Brief is taken as his confirmation that v2.28 is canonical.
**Authority for scope:** `project_handbook.md` Section 5, entry D22 (D22-A to D22-H; D22-H (13) freezes it). Letters such as "observation (ad)" refer to `governance/architect_reports/d22_architect_observations_a_to_ag.md`.

---

# PART 0: WHAT THE PRINCIPAL MUST LOOK AT FIRST

This Brief covers the parts of D22 that do not depend on the deferred items. Five points need your eye because they are where the Brief had to make a call. None is a new question to you (close-out rule: build to the Architect's recommendation and say so). Each is marked **[ASSUMED]** where it appears. You may change any of them at review.

1. **The deck is not in this Brief, and every narrative finalized in this release permanently has no deck. This is the one place the Brief departs from your wording.** D22 says "Finalize and build deck". At `65d71ca` there is no deck code at all (no PowerPoint library in `requirements.txt`, no deck function; the only trace is `"board_deck_pptx": None` in `close_history.py`), and the deck's structure and content are Deferred (D22-H (6)). A deck cannot be built from nothing, and the Architect may not invent it. **[ASSUMED]** In this release the second action is labelled **"Finalize narrative"**. It does everything "Finalize and build deck" does except build a deck, and the screen says plainly that no deck is stored. The name "Finalize and build deck" returns with the deck Brief. The record keeps no deck field now; the deck Brief adds one. **Consequence, stated plainly:** "Finalize and build deck" builds only from the draft being finalized (consolidated point 2), and a rebuild action is undecided and not in scope (G4). So a narrative finalized in this release has no deck, and nothing in this release can give it one later. The mark, the "Deck source" badge and the manual pick therefore point at a deck that does not exist; each finalized entry says "No deck is stored for this narrative". **Two options for you (Gate decision 1):** (a) **accept** it: finals made in this release are pre-deck, and the deck Brief decides what becomes of them (**recommended**: the narrative, its checked numbers and its history are worth having now, nothing is lost, and nobody is forced to use the action); (b) **hold** the finalize action, the mark and the history until the deck Brief, and release only drafts and the number check (the items that drop out are listed in Part 2, "If Gate decision 1 is (b)"). Consequence for your final question: see Part 1, section 12.
2. **The new draft-and-finalize flow is Quarterly only.** Under Annual cadence a narrative has no single close version to hang its drafts and finalized series on, and "Annual cadence" is Deferred (D22-H (6)). **[ASSUMED]** Annual keeps today's screen (prompt preview, download or generate, no saving), except for the already-decided fix that its commentary must come from the four approved quarterly snapshots (D22-B (10)), which is in scope. **Classification:** the Annual commentary-source fix is a decided requirement (Category A, D22-B (10)); what needs your confirmation is the Architect's reading of how it sits beside the deferral. **Architect's reading, for your confirmation (Gate decision 2):** D22-B (10) is a decided "required fix" that concerns commentary sourcing only and says Annual's comparison basis stays year over year; "Annual cadence" in the Deferred list (D22-H (6)) concerns what an Annual narrative and deck are. The two are compatible, so the fix is in scope. If you read them the other way, the Annual sentence in WP1-2 is removed and nothing else changes.
3. **"The prompt becomes editable" is built as a separate, labelled "Your own notes" section.** **[ASSUMED]** Everything else in the prompt (the DATA block, the commentary blocks, the TASK instructions) stays locked. Reason: D22-B (2) locks the figures and commentary, D22-B (2a) requires the user's text to be a separate section marked as the user's own, and D22-B (1) says the TASK instructions are "not part of this decision", which the Architect reads as "not made editable". If you meant the TASK text to be editable too, say so at review; that is a one-line change to the lock list.
4. **Known-gap defaults (Section "Known-gap defaults" below).** G1 to G4 and the name-prompt details are listed with the default this Brief builds to. Please confirm or change them when you review.
5. **Staging (Gate decision 3).** **Recommended:** release in two steps. Release 1 = WP1 (a fix to existing behaviour) and WP3 (a pure function). Both can be tested alone, and Independent Test can calibrate WP3 as a function before any screen exists. Release 2 = WP2, WP4, WP5. Nothing requires staging; the Principal may release all at once.

**Five decisions are yours at the Gate (Part 3, "Principal decisions at the Gate"):** (1) deckless finals accepted, or finalize held; (2) the Annual commentary-source fix in scope or not; (3) staged release or all at once; (4) the Quarterly-only flow and the "Your own notes" editable region; (5) the G1 to G4 defaults.

---

# PART 1: REQUIRED RESPONSE FORMAT (Architect analysis)

## Repository identification (evidence rules, section 2)
Repository `Northwind-Autonomous-CFO`; branch `main`; HEAD `65d71ca5dcff12bd9a331235a01514b68ba70a9d`; `origin/main` `65d71ca5dcff12bd9a331235a01514b68ba70a9d`; working tree clean; no difference. The Test Codespace is not canonical and was not consulted. All facts below are **CANONICAL / COMMITTED**.

## 1. REQUIREMENT
**Explicit (Principal):** D22-A to D22-H as frozen by D22-H (13): two-stage flow; drafts and finalized narratives with two counters; final mark moving at every finalization with a manual override; deletion of other drafts on finalization; number check at line level (Option 2 with Option 4) with known misses (i) to (iii) accepted; flag look; picking a line re-runs the check; a name asked once per session; an append-only history of mark changes; damaged-snapshot message; Annual and Quarterly commentary-source fixes; prompt protection; status strip count; Independent Test authors Set A and Set B. The Principal asked for "the Builder Brief for the parts of D22 that do not depend on the deferred items", stating in and out of scope, evidence, and which files may and may not change (close-out, section 4 (2)).
**Implied:** the narrative must be stored durably and survive a Streamlit rerun, restart and new session (D22-B (7); evidence rules section 9).
**Assumptions:** the five in Part 0, and the known-gap defaults.

## 2. EXISTING AUTHORITY
| Item | Source | Class |
|---|---|---|
| Two-stage flow, confirmations | D22-C (1), (4), (9); consolidated points 2 and 5 | Principal decision |
| Prompt editable, locked blocks, user section | D22-B (1), (2), (2a) | Principal decision |
| Storage beside the close version, discovery must not mistake it | D22-B (7) | Principal decision |
| Flags are a record in the narrative folder, not in the register | D22-B (9) | Principal decision |
| Annual and Quarterly commentary source | D22-B (10), (12) as amended by D22-C (5) | Principal decision. The Annual part (D22-B (10)) is a decided requirement (Category A); the Architect's reading that the Annual-cadence deferral does not override it is put to the Principal at Gate decision 2 |
| Unclosed period, preview, status strip | D22-B (11), (13), (14); D22-E (3) | Principal decision |
| Accept or rework; acceptance record | D22-B (15), (16); D22-C (2); D22-G (B3) | Principal decision |
| Every non-exact number is a hard flag; what a number is | D22-C (7); D22-D (2), (3) | Principal decision |
| Line-level matching, Option 2 with Option 4, misses (i) to (iii) | D22-E (1), (2); D22-F (1); D22-G (B1) | Principal decision |
| Pass rule, Set A and Set B by Independent Test | D22-G (B2); D22-H (2); D22-D (6) | Principal decision |
| Flag look; picking a line re-runs the check | D22-G (B3); D22-H (3) | Principal decision |
| Damaged snapshot definition and message | D22-C (5); D22-D (7) | Principal decision |
| Draft editing in place; deletion of other drafts | D22-E (4), (5); D22-F (3) | Principal decision |
| Two counters; mark; viewing; confirmation content | D22-G (A1), (A3), (A4); D22-H (4), (5), (10) | Principal decision |
| History of mark changes | D22-H (11) | Principal decision |
| Name once per session | D22-H (12) | Principal decision |
| Freeze, reopen rule, default rule, known gaps | D22-H (13) | Principal decision |
| Deferred items | D22-H (6) | Principal decision (Deferred) |

## 3. CLASSIFICATION
- **A (already authorized):** every row of section 2. The Brief adds no product scope.
- **B (new Principal decision):** none. The Brief introduces no decision. Part 0 item 1 changes one label because the deck cannot be built; that is recorded as Category E and decided by the Principal at Gate decision 1, not as a new decision and not as a technical constraint.
- **C (genuine conflict):** none (section 5).
- **D (technical or procedural):** see Gate Category D.
- **E (Architect recommendation, built to under the default rule, listed for the Principal):** storage layout, record shape, derived draft counter, entry "kind", long-list presentation, G1 to G4, name-prompt details, **and the two choices that follow from the Principal's deferral of the deck and of Annual cadence: the label "Finalize narrative" with finals that have no deck, and the Quarterly-only flow.** These two are not technical limits and are Principal decisions at the Gate.

## 4. SUPERSEDED / DEFERRED DECISIONS
Superseded and no longer authoritative: the single-action flow (D22-C (1)); the soft-notice tier (D22-C (7)); the tolerance classifiers (D22-D (3)); one shared number line (D22-G (A1)); "nearest figure" and any fall-back to any printed figure (D22-E (1), (2); D22-F (1)); the reopen direction in the Quarterly read-failure message (D22-C (5)); the audit-trail wording (D22-H (11)).
Deferred by the Principal, not a veto, neither open nor blocked (D22-H (6)): D22-A observations (b), (d), (g); deck structure and content; prototype scope; Investment Alignment versus Segment Profitability; the 6.5% budget variance; trend context; Annual cadence; viewing earlier narratives of a quarter flagged outdated; scenario scope. None has been changed by the Principal since. They remain outside this Brief.

## 5. GENUINE CONFLICTS
No genuine conflict identified. Two checked and not conflicts: (a) D22-B (3a) says flags "surface through the existing flag mechanism" while D22-B (9) says they stay out of the register: read together, flags are shown in the same visual style and counted in the status strip, but are stored only in the narrative folder; (b) "Finalize and build deck" with no deck: a scope gap that the Principal's own instruction ("parts that do not depend on the deferred items") anticipated, handled as a note here, so the D22-H (13) reopen test (impossible to build AND not handleable as a Brief note) is not met.

## 6. GOVERNANCE CHANGES REQUIRED
- **Documentation correction:** none required by this Brief.
- **New authorization:** none.
- **Implementation work:** Part 2. After release, the Handbook entry D22 moves from "Planned. Not briefed" to "Briefed" and records the Brief ID; that is the Architect's update after the Principal signs, not part of the Builder's work.

## 7. ARCHITECTURE IMPACT
Required by authorized scope: a per-close-version narrative store beside the close version folders; a number-check function; a rewritten AI Narrative tab body for Quarterly; a read-only damaged-snapshot classifier; a status-strip count. Technically necessary: atomic write of the narrative record; discovery that cannot mistake narrative folders for close versions. Recommended (assumed): the `narratives` layout and record shape (Part 2, WP2). Future: the deck (separate Brief), rebuild action, visibility of older drafts.

## 8. IMPLEMENTATION IMPACT
Smallest implementation: three new modules or one module with three clearly separated parts (store, check, snapshot classifier), plus edits confined to the AI Narrative tab block and the status strip in `Northwind_Financial_Dashboard.py`. No change to `close_history.py`. No new dependency. See Part 2 for the file rules.

## 9. TESTING IMPACT
Component, integration, persistence, UI and product evidence are all required and are kept apart in Part 2, "Required evidence". The calibration test (Set A, Set B) is owned by Independent Test and is **not** Builder evidence.

## 10. DEPENDENCIES AND BLOCKING
| Dependency | Why | Minimum-Scope Test | Workaround | Blocking? |
|---|---|---|---|---|
| Deck structure and content (deferred) | "Build deck" needs a deck | Is any narrative-versioning capability impossible without a deck? No: drafts, number check, finalization, mark, history all work without one | Finalize without building; label "Finalize narrative" (Part 0, item 1) | Blocks only the deck, not this Brief |
| Annual cadence (deferred) | No single close version under Annual | Is the Quarterly flow impossible without Annual? No | Annual keeps today's screen plus the commentary-source fix | Not blocking |
| Number check needs the draft stage | D22-B (15), (16) | The check engine (WP3) can be built and tested without the screen | Build WP3 first as a pure function | Sequencing only |
| Name needed by accept, finalize, pick | D22-C (2), D22-H (11), (12) | Needed by three actions | Name field (WP4) | Sequencing only |
| Commentary-source and damaged fixes | Locked prompt must come from approved text | Independent of the store and the check | none needed | Independent |

## 11. SEQUENCING RECOMMENDATION
**Required sequence:** WP3 before the flag UI in WP4; WP2 before the actions in WP4 that write (generate, edit, finalize, pick); WP1 before WP4's prompt (the locked blocks must be correct before they are stored).
**Convenient sequence:** WP1, WP3, WP2, WP4, WP5.
**Optional bundling:** WP1 can be released and tested alone (it is a fix to existing behaviour). WP3 can be released and tested alone as a function, and Independent Test can calibrate it before any screen exists. **Recommended:** Release 1 = WP1 + WP3; Release 2 = WP2, WP4, WP5 (Gate decision 3). Nothing in the Brief requires staging.

## 12. READY FOR BUILDER BRIEF?
### YES — READY (for the scope in Part 2), subject to the Principal's review.
**Final question (required):** *Can the intended user perform the complete intended business operation in the actual canonical application without developer intervention?*
**For D22 as a whole: NO.** The exact broken link is the deck: the Principal's stated need is "no manual copy-paste in the chain from approved close to board deck" (Handbook D22), and no deck code exists and its content is Deferred. This Brief does not close that link, and the Architect does not claim it will.
**For the operation this Brief covers, from an approved close to a finalized, number-checked, versioned narrative with a recorded mark: not yet verified** (nothing is built). Even when verified, every narrative finalized in this release has no deck (Part 0, item 1). It will be answered YES only with evidence for each link of the trace in evidence rules section 11, listed in Part 2, "Product evidence".

---

# PART 2: BUILDER BRIEF

## Objective
Let the Controller, working on a closed Quarterly period, produce executive narratives that are always generated from approved, locked figures and commentary, checked number by number against the close, kept as editable drafts until finalized, and then kept permanently as a numbered series with a clearly marked deck-source narrative. Nothing is lost, nothing finalized is overwritten, and every number the Controller keeps that does not match the close is explicitly accepted by a named person.

## Business purpose
The narrative that goes to the Board must not carry a figure the approved close does not support, and must not be generated from commentary that was not approved (D13, D22-B). The Principal also needs to see which narrative is the one in use.

## Scope In (mandatory)

### WP1. Commentary source, snapshot-read failure and damaged-snapshot message
**WP1-1.** **Quarterly (D22-B (12), amended by D22-C (5)).** For a closed Quarterly period, if the approved commentary snapshot cannot be read, the app must not build the prompt from session-state commentary. It shows a message that the snapshot is **damaged or incomplete** and needs restoring. It does not tell the user to reopen. At `65d71ca` the tab does the opposite: lines 3192 to 3205 of `Northwind_Financial_Dashboard.py` catch the read error, set the archived commentary to `None`, warn, and then continue with session-state commentary. This is the defect to remove. A narrative or deck already saved is not touched.
**WP1-2.** **Annual (D22-B (10)).** The commentary block reads from the approved snapshots of the four closed quarters of the fiscal year, as Quarterly reads its own, and never from session state. If any of the four is damaged or incomplete, the tab is blocked with the same message naming the quarter. Annual's comparison basis stays year over year. No draft, finalize or mark action is offered under Annual (Part 0, item 2).
**WP1-3.** **Definition (D22-D (7)).** NOT CLOSED: the period has no folder in `close_history`, or no version folder (or legacy root) holds a `metadata.json`. DAMAGED: the latest version's `metadata.json` exists but cannot be parsed or is not a JSON object, or, for narrative generation, its `commentary_record` cannot be rebuilt or its `observations.csv` cannot be read. READABLE: otherwise. A version folder with no `metadata.json` is an interrupted save and is ignored, as today. Damage is judged on the latest version with no fall-back to an older healthy one. The message says "damaged or incomplete" and asserts no cause.
**WP1-4.** **Gate.** For a DAMAGED period the existing "This close has not been approved" block (`_narrative_gate_block`) is replaced by the damaged message. NOT CLOSED keeps today's message. The gate's other blocks (reopen in progress, outdated by an earlier reopen, damaged control file) are unchanged.
**WP1-5.** **No change to `close_history.py`.** Two defects in that area (an uncaught error in the reopen guard on a malformed `commentary_record`; a damaged `metadata.json` reported as `never_closed`) are logged in Handbook Section 10 as separate items and are **not** bundled here (D22-C (6)). Implement the classifier read-only, outside `close_history.py`.

### WP2. Narrative store (durable state)
**The behaviours in items 3 to 11 are required. The layout (item 1) and the record shape (item 2) are the Architect's recommendation [ASSUMED, Category E], not mandatory scope:** the Builder builds to them unless it proposes another layout that meets items 3 to 11, and says so in the Return Report.
**WP2-1.** **Layout.** One `narratives` folder in the period folder, grouped by close version, with type-prefixed folders `draft_<n>` and `final_<n>`, and one state file per close version that is **not** named `metadata.json`. For a legacy unversioned snapshot the same folder sits in the period folder. A narrative folder holds the prompt as sent, the narrative text, the flag record (including acceptances and line picks) and a "prompt differs from the generated default outside the locked blocks" flag (D22-B (2), (4), (9)).
**WP2-2.** **Record (one per close version).** Lists the drafts (number, folder, creation time), the finalized narratives (number, folder, draft number it came from, finalization time), which finalized narrative holds the mark, and the history of mark changes (item 8). Do not store a draft counter. The next draft number is 1 plus the highest draft number found in **either** the record's draft list **or** the `draft_*` folders on disk, or 1 if neither has any (D22-G (A5) (3)). Reading both means a leftover folder can neither block a new draft through the no-overwrite rule nor have its number reused.
**WP2-3.** **Two counters.** Drafts start at 1 and restart at 1 when finalization has cleared every other draft, in the record and on disk. Finalized narratives are numbered 1, 2, 3 without gaps and are never deleted, replaced or renumbered. A finalized draft leaves the draft list ("draft 3" becomes "final 2").
**WP2-4.** **Close version separation.** A reopen that creates a new close version starts its own drafts and its own finalized series. Drafts and finalized narratives of an earlier close version are never read for the screen, never modified, never deleted (D22-H (4), (10)).
**WP2-5.** **Discovery safety (D22-B (7)).** The existing discovery in `close_history.py` (`_version_folders`, `list_approved_closes`, the legacy check, the reopen scan) must not mistake any narrative folder or state file for a close version or a period. Prove it with a test that runs the real functions on a store containing drafts and finals (T9).
**WP2-6.** **No overwrite.** Creating a narrative folder never overwrites an existing folder.
**WP2-7.** **Damaged record.** If the record cannot be read or parsed, the app says the narrative record is damaged and creates and deletes nothing.
**WP2-8.** **History of mark changes (D22-H (11)).** Append-only list in the same record as the mark. One entry per finalization and per manual pick. Each entry: from which narrative to which, time, name (WP4 item 7), and its kind (finalization or manual pick). The first entry has no "from" value; the screen shows it as "first finalized narrative", not a blank. A manual pick of the narrative that already holds the mark changes nothing, writes no entry, and is not offered. The app has no operation that edits or removes an entry. The history records what the app marked as the deck source, not what was sent, and no text on screen or in code comments calls it proof, audit trail or record of what was sent.
**WP2-9.** **Atomic record write.** Write to a temporary file in the same folder and replace in one step, as `_write_json_atomic` in `close_history.py` does (read it; do not import a private function across modules if a copy is cleaner; do not copy `archive_close`'s non-atomic `metadata.json` write).
**WP2-10.** **Finalization order (D22-F (3), D22-H (11)).** (a) Write the final folder durably. (b) Write the record once, atomically, with the new finalized narrative, the moved mark and the history entry, and with the finalized draft removed from the draft list in the same write. (c) Delete the finalized draft's own `draft_<n>` folder and the exact `draft_*` folders of the other drafts the record lists, never by pattern. (d) Update the record to remove the other drafts that were deleted. A failed finalization deletes nothing. If a delete in (c) fails, that draft stays in the record's draft list as an ordinary draft, the screen tells the user that n drafts could not be deleted, and the next finalization deletes it. A leftover `draft_<n>` folder of the finalized draft (not in the record) is ignored by the screen and counted by the draft numbering (item 3). A crash at any step leaves either the old state, or the new state with leftover drafts that the record still lists or leftover folders the record does not list; it never leaves a mark without its history entry. **Accepted consequence (small, not a defect):** a leftover `draft_<n>` folder of the finalized draft is not in the record, so nothing ever deletes it, and the "restart at 1" rule (WP2-3) then no longer fires for that close version, because a draft folder remains on disk. Numbering stays correct and no number is reused. About 15 KB per such folder.
**WP2-11.** **Mark rules (D22-G (A3), D22-D (4))**: finalizing always moves the mark to the narrative just finalized, even if the Principal had set it by hand; creating a draft does not move it; drafts never hold it; at most one holder; a manual pick lasts only until the next finalization. Worked example that must pass (finals are numbered without gaps): finals 1, 2 and 3 exist, each finalized in turn with no manual pick, so three finalization entries exist and 3 holds the mark. Then: finalize a draft (it becomes final 4; mark 4); pick 3 by hand (mark 3); finalize a draft (it becomes final 5; mark 5); pick 3 by hand (mark 3). This adds **four** entries (finalization to 4, pick of 3, finalization to 5, pick of 3), **seven in total**, counting the three earlier finalization entries; the entry that first made 3 the holder is the third of those three. Each entry has the right "from", "to", kind, time and name.

### WP3. Number check (pure function, no screen dependency)
Definitions are in D22-C (7), D22-D (2), (3), D22-E (1), (2), D22-F (1), D22-G (B1), (B3), D22-H (3). Summary of what must be true:
**WP3-1.** **What is checked:** the numbers in the narrative text (not the user's notes, not the prompt). **The exemption of the user's notes is the Brief's reading:** D22-B (3) defines the check on "the numbers in the narrative" and the Handbook does not say whether the notes are exempt. If a number the user types in the notes is carried into the narrative, it is checked there. Years, quarter and FY labels, dates, ordinals and list numbering are not numbers. Dollar amounts, percentages and counts are checked; digits only (spelled-out numbers are not scanned).
**WP3-2.** **Exact match:** a written figure matches when it equals a printed close figure rounded to the precision written ("$4.0M" matches $4,016,906). K, M, B and "million" are read as such. Figures printed in the locked DATA block count, including derived ones printed there. A figure the writer computes that is not printed is a hard flag.
**WP3-3.** **Line level, Option 2:** a number matches only if the nearest preceding line name (same sentence, or the previous sentence) belongs to exactly one of the lines whose printed figure equals it at the precision written. Otherwise it is a hard flag. There is **no fall-back to any printed figure**. The lines are the lines of the DATA block of the rendered prompt for this close. The probe in observation (ad), Appendix A, is a measurement script, not the implementation and not a test oracle.
**WP3-4.** **Every non-exact number is a hard flag.** No tolerance, no soft tier. "Hard", "soft" and "none" are internal words and never appear on screen.
**WP3-5.** **Known misses accepted** and not to be "fixed" by the Builder: (i) a current figure written where the prior figure of the same line belongs; (ii) a wrong number that is the right figure for the line named; (iii) a number written after the name of a different line, where it equals that line's figure.
**WP3-6.** **What a flag carries:** what was written; where the line is known, the line's close figure of the same kind (dollars with dollars, percentages with percentages, counts with counts), or plain wording when the line has no figure of that kind; where the line cannot be placed, every line carrying a figure of the same kind, each with its figure.
**WP3-7.** **Picking a line (Option 4, D22-H (3)):** re-runs the check against the picked line. If its figure equals the number, the flag clears and the pick is recorded. If not, the flag stays open and shows that line's figure. The pick is the writer's statement and is not otherwise verified.
**WP3-8.** **Acceptance:** keyed to the number and the line, not to the display label "Flag n". It records the name, the time, the number as written and the line it was matched to or picked. An acceptance holds for the number as it stands; if the text containing it changes, the check runs again on the new text.
**WP3-9.** **Hand-written narrative** (no API key) is checked identically.
**WP3-10.** **Deterministic:** the same text and the same DATA block give the same flags.

### WP4. AI Narrative tab, Quarterly (screen and actions)
**WP4-1.** **Two areas** on one screen: the prompt and the narrative draft, with a selector and also a side-by-side view (D22-B (6)). Default view **[ASSUMED]**: the narrative, selector on.
**WP4-2.** **Prompt.** The rendered prompt (current expander content) stays visible read-only for an unclosed period (D22-B (13)). For a closed period the prompt has locked blocks refilled from the approved close at the moment of sending, never taken from stored or edited text: the DATA block, and the three commentary blocks (accepted commentary, "Flagged Observations — Unresolved", "Flagged Observations — No Commentary Supplied This Close"). Only Accepted commentary versions are ever included. The user may add a separate, clearly labelled **"Your own notes"** section, shown and sent as the user's own input and never blended into the approved commentary block (D22-B (2a)). **[ASSUMED]** The TASK instructions and the system prompt (`SYSTEM_PROMPT` in `rollups.py`) are not editable. The prompt as sent is stored with each draft, with the "differs from default outside the locked blocks" flag.
**WP4-3.** **"Generate draft"** asks for its own confirmation, then creates the next draft: with a key, from `R.call_claude_narrative`; with no key, an empty draft for writing in the app. The number check runs and flags appear inline with a small marker linking each flag to its sentence. The draft is freely editable; editing updates the same draft in place, never creates a draft, and re-runs the check.
**WP4-4.** **Flags (D22-G (B3)).** Numbered "Flag 1", "Flag 2" as display labels. Each flag has two actions in plain words, **"Keep my number"** (records name, time and matched line) and **"Edit the text"**. For an unplaceable number the flag lists every line with a figure of the same kind; the writer picks one. Presentation of a long list (about 100 dollar figures, 48 percentages or 19 counts on the Q4 sample) is for the Builder **[ASSUMED]**: a searchable selector grouped by DATA section heading is the minimum; the Principal judges it in his product test.
**WP4-5.** **"Finalize narrative"** (label per Part 0, item 1) is enabled only when no hard flag is unresolved. Its confirmation states: the final number the draft will take; the finalized narrative it replaces as deck source, if one exists (the one holding the mark at that moment, which need not be the highest number); how many other unfinalized drafts will be deleted (excluding the one being finalized); and that no deck is stored in this release. It locks the narrative, prompt, flags and acceptances. It never auto-runs.
**WP4-6.** **Mark.** A "mark as final" action, with its own confirmation, selects only a finalized narrative. The screen shows which finalized narrative holds the mark, with a badge that does not use the bare word "final" **[ASSUMED]** (for example "Deck source"; each finalized entry also says "No deck is stored for this narrative" in this release), whenever more than one finalized narrative exists, and shows no mark when none exists. Each finalized entry shows its number, "from draft n", and its finalization time, which disambiguates a restarted draft number (D22-H (7) note).
**WP4-7.** **Name.** The app asks for a name once per session and requires it before the first accept, finalize or manual pick. It records exactly what was typed (trimmed of surrounding spaces; blank is not accepted). Reading, viewing and editing need no name. It is not a login; no text uses "user", "login", "signed in" or "authenticated" for it (D22-H (12)). **[ASSUMED]** The name is asked again in each new session; it is not saved between sessions.
**WP4-8.** **Viewing.** The Controller can view any finalized narrative and any current draft of the close version on screen at any time. The screen shows the newest draft (by creation time) when one exists, otherwise the narrative holding the mark; with neither, an empty state with "Generate draft".
**WP4-9.** **Gate preserved.** The existing blocks in `_narrative_gate_block` still apply and nothing here becomes a path to final output for an unclosed or blocked period (D22-B (11)).
**WP4-10.** **No-key path** keeps working with no manual copy-paste: the user writes the narrative in the app. The old "Download prompt" button may remain as a convenience; it is not removed by this Brief.

### WP5. Status strip
**WP5-1.** The workflow status strip shows a count of currently open narrative flags (flags neither accepted nor cleared) of the narrative on screen.
**WP5-2.** The count follows the screen as the user moves between a draft and finalized narratives (D22-E (3)).
**WP5-3.** Display only: it does not feed Explanations Validated, close approval, `observations.csv` or the observation register (D22-B (9), (14)).

## Known-gap defaults (Principal's review; D22-H (13))
These are undecided. The Brief builds to the default; the Principal may change any of them.
| Gap | Default this Brief builds to |
|---|---|
| G1 Draft creation time | Stored for every draft; not shown as a requirement. The finalization time is shown on every finalized entry. |
| G2 No withdraw action | No withdraw action. The "Finalize narrative" confirmation is the only warning that the deck source will change. |
| G3 Older drafts and earlier close versions | Kept on disk, never shown, never touched. If a later release shows them, read-only. |
| G4 Rebuild action and a damaged stored deck | No rebuild. In this release no deck is stored, so the "damaged deck" case does not arise; the deck Brief must define it. |

## Scope Out (explicit exclusions)
1. Building, storing or editing a deck; the PowerPoint library; any deck layout or content (Deferred, D22-H (6)).
2. D22-A observations (b), (d), (g); prototype scope; Investment Alignment versus Segment Profitability; the 6.5% budget variance; trend context; scenario scope; Annual cadence for the new flow; viewing earlier narratives of an outdated quarter (Deferred).
3. Any screen that shows drafts or finalized narratives of an earlier close version (G3).
4. A withdraw action, a rebuild action, a tamper-proof or "proof of what was sent" claim for the history (G2, G4, D22-H (11)).
5. Any change to the system prompt, the TASK instructions, the DATA content or the commentary workflow.
6. Fixing the two logged `close_history` defects (Section 10).
7. Writing narrative flags to the observation register, `observations.csv`, close approval or the close snapshot (D22-B (9)). The close snapshot's own `narrative.txt` is not changed.
8. Authoring Set A or Set B, or any calibration data (Independent Test only, section 20 of the governance instructions).
9. Authentication, user accounts, or any use of `submitted_by` in the commentary library.
10. New dependencies in `requirements.txt`.

## Files that may and may not change
**May change:** `Northwind_Financial_Dashboard.py`, only the AI Narrative tab block (about lines 3162 to 3294), `_narrative_gate_block` (about lines 319 to 366) for the damaged message, the workflow status strip (about lines 1546 to 1600), and a session name prompt. New modules for the store, the check and the snapshot classifier (names chosen by the Builder). New test files, in a new location outside the existing `build_test` demo scripts or as new files there. `rollups.py` **only** if a change is additive and keeps `build_user_prompt` output byte-identical for every existing caller (as earlier additions did), for example to expose the DATA lines or the locked-block boundaries.
**May not change:** `close_history.py`; `close_validation.py`; `period_lifecycle.py`; `commentary_workflow.py`; `SYSTEM_PROMPT`; `northwind_narrative_prompt.md`; `requirements.txt`; `Northwind_Sample_Dataset.xlsx`; everything under `governance/`; `project_handbook.md`; `assumptions_and_limitations.md`; existing `build_test` scripts. If the Builder believes one of these must change, it **stops and reports** (it does not change it); that is the D22-H (13) reopen test.

## Constraints
- No secret in source, reports or fixtures. **No live API call is part of Builder evidence**: the key-present draft path is tested with a mocked `call_claude_narrative`, which proves the pipeline mechanics (the function itself is not changed by this Brief). The Principal's product test may include one live call with his own key.
- Streamlit executes every tab body on every rerun: no write may happen on a rerun without an explicit click.
- Existing behaviour outside the AI Narrative tab must be byte-for-byte unchanged (regression expectation).

## Acceptance criteria
Every numbered item in WP1 to WP5 is one acceptance criterion with the ID shown (for example WP2-10); an item with parts (a) to (d) is reported per part. The Return Report maps its evidence to these IDs. In addition:
- AC-1. After a browser refresh, a Streamlit rerun, an app restart and a new session, the drafts, finalized narratives, flags, acceptances, mark and history are exactly as left.
- AC-2. Nothing finalized is changed by any later action.
- AC-3. No on-screen text contains "hard", "soft", "audit trail", "login", "authenticated" or "signed in".

## Required evidence
Evidence is classified (evidence rules section 6). A Builder statement is not evidence.
**Component (Builder):** tests for WP3 including each accepted miss recorded as an expected result and a case per rule 1 to 10; tests for WP2 items 3 to 11 including the mark example in WP2-11 (T-seq), a draft counter restart (including a leftover `draft_*` folder on disk, which must not be reused or overwritten), finalizing 3 while 4 and 5 exist (both newer drafts deleted), the first history entry, a pick of the current holder (no entry), and the blank-name refusal. **Also required (each its own test):** the locked blocks are refilled from the approved close at send time and are unaffected by stored or edited text; only Accepted commentary versions are included; the "differs from default outside the locked blocks" flag is set and cleared correctly; "Finalize narrative" is blocked while any flag is open; no write to the store happens on a Streamlit rerun without a click; the finalize confirmation names the final number, names the mark holder at that moment (which need not be the highest number) and counts the other drafts excluding the one being finalized.
**Integration (Builder):** T9 discovery test on the real `close_history` functions with narrative folders present for a versioned and a legacy snapshot; fault injection at each step of the finalization order (kill after (a), after (b), after (c)) leaving a recoverable state; damaged record refuses to create or delete; Quarterly read failure produces the damaged message and builds no prompt from session state; Annual with one damaged quarter is blocked and with four healthy quarters reads from the snapshots.
**Persistence (Builder):** restart test (AC-1), run on the real store, not an in-memory fake.
**UI (Builder):** screenshots or a screen recording of: the name prompt; a Generate draft confirmation; a draft with at least one placed flag and one unplaceable flag; Keep my number; picking a line (equal clears, unequal stays); the Finalize narrative confirmation text; the mark badge; the status strip count following the screen.
**Regression (Builder):** there is no automated suite; `build_test/` holds seven demo scripts and an empty README. The regression set is these seven, run before and after the change, with the outputs compared: `close_orchestrator.py`, `close_v1_v2_simulation.py`, `commentary_workflow_demo.py`, `d15_5a_versioning_demo.py`, `d15_5e_5g_5h_demo.py`, `fixk_fy_label_guard.py`, `phase4_semantic_reconciliation_demo.py`. They run offline with `ANTHROPIC_API_KEY` unset; a script that needs a live call is reported as not runnable offline, not run with a key. Also: a diff of `build_user_prompt` output for an existing caller is byte-identical.
**File discipline (Builder):** the Return Report lists every changed file from `git diff --stat 65d71ca`, and the Architect checks it against "May change". The Return Report also names the place in the new code where the "latest version" logic of `close_history.py` is copied for the damaged-snapshot classifier (WP1-3).
**Evidence by release (applies if Gate decision 3 is "staged"; if "all at once", all rows apply to the single Return Report).** Each release has its own Return Report, its own `git diff --stat` file-discipline check against the commit it starts from, and its own run of the seven-script regression set.
| Evidence | Release 1 (WP1 + WP3) | Release 2 (WP2, WP4, WP5) |
|---|---|---|
| Component | WP1 classifier (NOT CLOSED, DAMAGED, READABLE cases); WP3 cases, including each accepted miss as an expected result | WP2 items 3 to 11 and the added tests (locked blocks refilled, Accepted-only commentary, "differs" flag, finalize blocked, no write on rerun, confirmation text) |
| Integration | WP1: Quarterly read failure gives the damaged message and builds nothing from session state; Annual with one damaged quarter is blocked; Annual with four healthy quarters reads the snapshots | T9 discovery test; finalization fault injection; damaged record refuses to create or delete; the screen calls the same WP3 function that was calibrated |
| Persistence | not applicable (no state is written) | restart test, AC-1 |
| UI | screenshots of the damaged message (Quarterly) and the blocked Annual message | the UI list in this section |
| Regression | seven scripts before and after; byte-identical `build_user_prompt` | the same, again |
| File discipline | yes | yes |
| Calibration | Independent Test calibrates WP3 as a function, before any screen exists | not repeated; Independent Test confirms on the screen that the same function is used |
| Product | none (WP3 has no screen yet) | the product test below; AC-1 to AC-3 |
**Calibration (Independent Test, not the Builder):** Set A and Set B are authored by Independent Test, kept from the Builder and the Architect, with expected results shown to the Principal before each run, run against the Builder's check under the pass rule in D22-G (B2) (clauses (a) to (e)). The Builder's own cases are component evidence and must not be called calibration.
**Product evidence (Principal, with Independent Test):** on the canonical app at the Builder's commit, a Controller who is not a developer: names themself; generates a draft on a closed Quarterly period; sees flags; keeps one number and fixes another by editing; finalizes; generates and finalizes a second narrative; sets the mark back by hand; restarts the app; and sees every state and the history unchanged. Each link of the trace (Principal decision, Handbook, Brief, code, UI, integration, state transition, persistence, downstream behaviour, user verification) is reported; a broken link is reported as such. The Architect will use VERIFIED only for exactly what this evidence supports, and will report DOCUMENTATION / IMPLEMENTATION DRIFT if code and Handbook differ.

## If Gate decision 1 is (b): hold the finalize action
(Everything in this block applies only if the Principal ticks (b). If he ticks (a), ignore it.)
**Removed from this Brief (deferred to the deck Brief together with the deck):** WP2-8 (history of mark changes); WP2-10 (finalization order); WP2-11 (mark rules); WP4-5 ("Finalize narrative" and its confirmation); WP4-6 (the mark action, the badge and the finalized-entry display); WP5-2 (the strip following finalized narratives). **Reduced:** WP2-2 (the record lists drafts only: no finalized list, no mark, no history); WP2-3 (the draft counter only; with nothing finalizing, no draft is cleared, so the draft number never restarts and no draft is deleted); WP2-4 (drafts only); WP4-7 (the name is required before the first **accept** only); WP4-8 (the screen shows the newest draft, there is no finalized narrative to fall back on, and the empty state is unchanged); WP5-1 (counts the open flags of the draft on screen). **Unchanged:** WP1 in full; WP2-1, WP2-5, WP2-6, WP2-7, WP2-9 (the atomic write still protects the record); WP3 in full; WP4-1, WP4-2, WP4-3, WP4-4, WP4-9, WP4-10; WP5-3. Acceptances and line picks are recorded on the draft and, with nothing finalized, are not locked (an edit re-runs the check as in WP3-8).
**Evidence removed:** the mark example (T-seq); the finalization-order fault injection; the finalize-blocked-while-a-flag-is-open test; the finalize confirmation text test; the history, pick-of-holder and first-entry tests; the AC-2 criterion ("nothing finalized is changed"). **Product test becomes:** names themself; generates a draft; sees flags; keeps one number and fixes another by editing; restarts the app; sees the draft and its acceptances unchanged.
**Gate rows removed:** D22-G (A1) finalized series and (A3) mark; D22-H (4), (5), (10) as they concern finals and the mark; D22-H (11); D22-F (3) deletion; the Category E rows for the label "Finalize narrative" and the mark badge. They return, unchanged, in the deck Brief.
**Accepted consequence of (b):** drafts accumulate, because deletion happens only at finalization (about 15 KB each), and no narrative is ever locked. The Principal accepts this by ticking (b).
**What remains:** WP1; drafts with the no-key and key paths; the editable "Your own notes" section and locked blocks; the number check, flags, acceptance and line picks; the damaged-snapshot message; the status strip count. The close-out reopen rule still applies: if the Builder finds this reduced set cannot be built, it stops and reports.

## Stop-and-report rule
If the Builder finds that a confirmed decision cannot be built, or two confirmed decisions contradict, it stops that item and reports it to the Architect with the evidence. It does not choose a reading, narrow a requirement, or add scope.

---

# PART 3: SCOPE AUTHORIZATION GATE (PRINCIPAL SIGN-OFF REQUIRED)

**Brief Title:** D22 Narrative Versioning, Number Check and Flags, Builder Brief v3

**Status:**
☑ READY FOR PRINCIPAL APPROVAL
☐ BLOCKED
☐ AWAITING PRINCIPAL DECISION

## CATEGORY A: ALREADY AUTHORIZED
| Requirement | Authoritative Source | Incorporated? |
|---|---|---|
| Two-stage flow, separate confirmations | D22-C (1), (4), (9); consolidated points 2, 5 | ☑ WP4 items 3, 5 |
| Prompt protection and user's own section | D22-B (1), (2), (2a) | ☑ WP4 item 2 |
| Storage beside the close version; discovery safe | D22-B (7) | ☑ WP2 items 1, 5 |
| Flags stored in the narrative folder only | D22-B (9) | ☑ WP2 item 1, Scope Out 7 |
| Annual and Quarterly commentary source; damaged message and definition. **Annual part: a decided requirement, D22-B (10). Gate decision 2 asks the Principal to confirm the Architect's reading that the deferral of "Annual cadence" does not override it; it is not a new scope item.** | D22-B (10), (12); D22-C (5); D22-D (7) | ☑ WP1 |
| Unclosed preview; status strip count | D22-B (11), (13), (14); D22-E (3) | ☑ WP4 items 2, 9; WP5 |
| Accept or rework; acceptance record | D22-B (15), (16); D22-C (2); D22-G (B3) | ☑ WP3 item 8; WP4 item 4 |
| Every non-exact number is a hard flag; line-level Option 2 with Option 4; misses (i) to (iii); no fall-back | D22-C (7); D22-D (2), (3); D22-E (1), (2); D22-F (1); D22-G (B1) | ☑ WP3 |
| Flag look; picking a line re-runs the check | D22-G (B3); D22-H (3) | ☑ WP3 items 6, 7; WP4 item 4 |
| Draft editing in place; deletion of other drafts with conditions | D22-E (4), (5); D22-F (3) | ☑ WP2 item 10; WP4 items 3, 5 |
| Two counters; mark with manual override; viewing; confirmation content | D22-G (A1), (A3), (A4); D22-H (4), (5), (10) | ☑ WP2 items 3, 4, 11; WP4 items 5, 6, 8 |
| History of mark changes | D22-H (11) | ☑ WP2 item 8 |
| Name once per session, not a login | D22-H (12) | ☑ WP4 item 7 |
| Independent Test authors Set A and Set B; pass rule | D22-D (6); D22-G (B2); D22-H (2) | ☑ Required evidence |

## CATEGORY B: NEW PRINCIPAL DECISIONS
| Requirement | Authorization Reference | Incorporated? |
|---|---|---|
| None. This Brief introduces no new product decision. | — | n/a |

## CATEGORY C: GENUINE CONFLICTS
No genuine conflict identified.

## CATEGORY D: TECHNICAL / PROCEDURAL CONSTRAINTS
| Constraint | Workaround | Blocking? |
|---|---|---|
| `close_history.py` must not change, yet the damaged state cannot be told from "never closed" by its public functions | Read-only classifier outside `close_history.py`; the two logged defects stay logged | No |
| Atomic record write | Temporary file in the same folder, then replace, as `_write_json_atomic` | No |
| Legacy unversioned snapshots keep `metadata.json` in the period folder | `narratives` folder there too; a test proves discovery ignores it | No |
| D22-B (3a) "existing flag mechanism" versus (9) "not in the register" | Same visual style and the status-strip count; stored only in the narrative folder | No |
| The acceptance must survive a changed display label | Keyed to the number and the line, not "Flag n" | No |

## CATEGORY E: ARCHITECT RECOMMENDATIONS
These are NOT Builder-authorized scope unless the Principal approves them. Under the close-out default rule the Brief builds to them and says so.
| Recommendation | Reason | Principal Authorization |
|---|---|---|
| `narratives` folder, type-prefixed names, state file not named `metadata.json` | Cannot collide with close-version discovery | ☐ Not authorized / ☑ Approved as built-to |
| One record per close version; derived draft counter, no stored counter | Mark written in one place; restart is automatic | ☐ Not authorized / ☑ Approved as built-to |
| History entry carries its kind | Readable without comparing times | ☐ Not authorized / ☑ Approved as built-to |
| Label "Finalize narrative" and finals with no deck in this release (moved from Category D: the reason is the Principal's deferral of deck content, not a technical limit) | No deck can be built; no rebuild exists | ☐ Not authorized / ☑ Approved as built-to (Gate decision 1) |
| Quarterly-only new flow (moved from Category D: Annual cadence is Deferred by the Principal) | Annual has no single close version | ☐ Not authorized / ☑ Approved as built-to (Gate decision 4) |
| Editable region is the "Your own notes" section only | D22-B (1), (2), (2a) read together | ☐ Not authorized / ☑ Approved as built-to |
| Mark badge not using the word "final" | "final" has two meanings | ☐ Not authorized / ☑ Approved as built-to |
| Default view: narrative with selector | Not stated by the Principal | ☐ Not authorized / ☑ Approved as built-to |
| Long-list presentation: searchable selector grouped by DATA section | Left to the Brief by D22-G (B3) | ☐ Not authorized / ☑ Approved as built-to |
| Name asked again each session | Reading of "once per session" | ☐ Not authorized / ☑ Approved as built-to |
| G1 to G4 defaults (table above) | D22-H (13) | ☐ Not authorized / ☑ Approved as built-to |

## PRINCIPAL DECISIONS AT THE GATE
These five are not minor. Tick one option in each.
1. Finalized narratives in this release have no deck, and no rebuild exists: ☑ accept (recommended) ☐ hold the finalize action, the mark and the history until the deck Brief (what drops out: Part 2, "If Gate decision 1 is (b)").
2. The Annual commentary-source fix (a decided requirement, D22-B (10), Category A): ☑ I confirm the Architect's reading that the Deferred "Annual cadence" does not override it, so it stays in scope ☐ I read the deferral as covering it, so it is removed from WP1-2.
3. Release: ☑ staged, Release 1 = WP1 + WP3, Release 2 = WP2, WP4, WP5 (recommended) ☐ all at once.
4. The Quarterly-only flow and the "Your own notes" editable region (TASK text and system prompt not editable): ☑ approved ☐ changed as follows: ________
5. The defaults G1 to G4 and the name-prompt details: ☑ approved ☐ changed as follows: ________

## EXPLICIT EXCLUSIONS
| Exclusion | Reason | Authority |
|---|---|---|
| Deck build, storage, content; PowerPoint dependency | Deferred; no code exists | D22-H (6) |
| D22-A (b), (d), (g); deck-content questions | Deferred | D22-H (6) |
| Annual cadence for the new flow; outdated-quarter narratives | Deferred | D22-H (6) |
| Screens for earlier close versions' drafts or finals | Not decided; disk only | D22-H (4), (10); G3 |
| Withdraw action; rebuild action | Not decided; not in scope | D22-H (5), (7); G2, G4 |
| Fix of the two logged `close_history` defects | Logged separately | D22-C (6); Section 10 |
| Flags in the register, `observations.csv`, close approval | Closing and narrating are separate | D22-B (9) |
| Authoring calibration sets | Independent Test only | D22-D (6); D22-H (2); governance section 20 |
| Authentication; new dependencies | Not requested | D22-H (12) |

## MINIMUM-SCOPE VERIFICATION
☑ Minimum implementation identified (store, check, classifier, one tab block, one strip count; no deck, no new dependency)
☑ Claimed dependencies tested (Part 1, section 10)
☑ Workarounds considered (Category D)
☑ Optional architecture separated (Category E; WP2 says the behaviours are required and the layout is the recommendation)
☑ No unnecessary bundling introduced (WP1 and WP3 can be released and tested alone; Part 1, section 11)

## PRINCIPAL APPROVAL GATE
I confirm that:

☑ This Brief includes ALL requirements I have decided.
☑ This Brief includes NO product scope I did not authorize.
☑ The exclusions accurately represent my deferred/out-of-scope decisions.
☑ The Architect has not silently narrowed my authorized scope. (The one change of wording, the label of the second action, and its consequence, are stated in Part 0 item 1 and decided at Gate decision 1.)
☑ The Architect has not silently expanded my authorized scope.
☑ Architect recommendations are clearly separated from mandatory scope.
☑ I understand that Builder implements ONLY the authorized scope in this Brief.
☑ If the Brief is incomplete, I will request clarification before issuing it.

**Approved by Principal:** by written statement in the session on 2026-10-26, 11:47 Europe/London: "I confirmed it but did not confirm the handbook", confirming the Gate answers relayed in his message of the same day (prepared by the Project Advisor): decision 1 accept; decision 2 confirmed in scope; decision 3 staged; decision 4 approved; decision 5 approved; all Category E rows approved as built-to; all eight boxes ticked; his quoted messages of 2026-10-15 and 2026-10-26 confirmed accurate. Recorded by the Architect. The Principal did **not** confirm any Handbook update; none is requested by this Brief.   **Date:** 2026-10-26

## ARCHITECT ATTESTATION
I confirm:
☑ I reviewed the relevant Handbook and Decision Log (D22-A to D22-H, Section 10, Section 11a).
☑ I reviewed the relevant canonical repository state (`65d71ca`, clean, level with `origin/main`).
☑ I classified all material scope.
☑ I applied the Required Response Format.
☑ I applied the Minimum-Scope Test where applicable.
☑ I did not bundle scope without authorization.
☑ I did not use technical preference as product authority.
☑ I did not silently narrow or expand Principal scope. The label "Finalize narrative", finals with no deck, and the Quarterly-only flow are stated openly as assumptions for the Principal's decision.
☑ This Brief accurately represents the authorized scope.

**Architect:** Claude (Architect)   **Date:** 2026-10-26

## RELEASE RULE
The Principal Approval Gate was approved on 2026-10-26 (signature block above). Release to the Builder is the Principal's act: the Brief is released when the Principal makes this signed file canonical and sends it. The Architect's attestation does not substitute for Principal authorization. The Architect has not pushed, merged or sent anything.
