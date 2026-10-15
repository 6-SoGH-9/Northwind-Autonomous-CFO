# D22 — Architect observations (a) to (ag), with the (ad) evidence

**Location:** `governance/architect_reports/d22_architect_observations_a_to_ag.md`
**Moved from:** `project_handbook.md`, Handbook v2.28 revision (Section 5, entry D22), on 2026-10-14, at the Principal's request (Handbook Section 2, principle 8: the Handbook records decisions and points to evidence).
**Baseline:** canonical `main` `b20d4b1047884ca6b62ffe90a43132a457ca077f` (Handbook v2.27), the commit at which the measurements in (ad) were made.
**Status of this document:** reference and evidence. It records Architect questions and assessments. It is not a decision record; decisions are in the Handbook (D22-A to D22-H).

## Part 1. Status after the Principal's decisions of 2026-10-14 and 2026-10-15 (added when the text was moved; not part of the verbatim record)

| Observation | Status | Where decided or open |
|---|---|---|
| (ad) which line a number describes | Decided: Option 2, with Option 4 as its accept action; line level, not field level; Option 1 not chosen; no fall-back to any printed figure. Known misses (i) to (iii) accepted | Handbook D22-F (1), D22-G (B1) |
| (ae) point 1 and D22-A | Decided: the proposed wording of point 1 is confirmed as the Principal's wording (D22-F (2)). Its one-sentence restatement for the two-counter model was confirmed on the idea on 2026-10-15, not as literal wording he read (D22-H (1)). Row corrected 2026-10-15: it previously said the restatement was proposed for confirmation | Handbook D22-F (2), D22-H (1), consolidated point 1 |
| (af) deletion of drafts | Decided: deletion on finalization is confirmed, with three conditions | Handbook D22-F (3), D22-G (A5) |
| (ag) numbering after deletion; drafts under an earlier close version | Closed. Numbering: closed by the two-counter model, and the recommendation in the text below is withdrawn. Drafts under an earlier close version: decided 2026-10-15, never touched | Handbook D22-G (A1), (A2), D22-H (4) |
| (ac) who authors Set A | Decided 2026-10-15: Independent Test authors Set A as well as Set B. The Architect and the Advisor are excluded | Handbook D22-H (2) |
| (ab) second part | Answered: finalizing takes the mark, with a manual override (Reading X) | Handbook D22-G (A3) |
| (ab) third part | Decided 2026-10-15: setting the mark by hand re-points to the deck stored at finalization; nothing is rebuilt. A rebuild action is undecided and not in scope | Handbook D22-H (5) |
| (b) of the D22-A observations | Deferred by the Principal (2026-10-15). Its question is answered by (ab) third part except for the rebuild action | Handbook D22-H (5), (6) |
| (ah) what the flag shows when the check cannot place a number | Decided: the flag lists every line carrying a figure of the same kind, each with its figure, and the Principal picks one | Handbook D22-G (B3) |
| (ai) what picking a line does (below) | Decided 2026-10-15: picking a line re-runs the check against that line; equal clears the flag, unequal keeps it open and shows the figure | Handbook D22-H (3) |
| Older drafts: visible or editable? (put to the Architect 2026-10-15) | Not decided. The Architect's answer: on disk only at `b20d4b1`, because no screen reads an earlier close version; if ever shown, read-only | Handbook D22-H (4) |
| (aj) history of mark changes | Decided 2026-10-15: an append-only list of mark changes is kept in the same record as the mark (from which narrative to which, when, by whom; one entry per finalization and per manual pick). It is not proof of what was sent | Handbook D22-H (11) |
| (ak) where "by whom" comes from | Decided 2026-10-15: the app asks for a name once per session, required before the first accept, finalize or manual pick; it records what the person typed; it is not a login and is not authentication | Handbook D22-H (12) |
| (d), (g) of the D22-A observations | Deferred by the Principal (2026-10-15), neither open nor blocked | Handbook D22-H (6) |

Observations (a) and (c), (e), (f), (h) to (y), (z), (aa) and the first part of (ab) were answered earlier; their dispositions are in the verbatim text. Two wordings in the verbatim text are now stale and are left as written: the (ad) text calls Option 2 an Architect recommendation (the Principal has since chosen it), and the (ae) text calls the amended wording of point 1 a proposal (the Principal has since confirmed it). The verbatim text of (ag) recommends not reusing numbers; that recommendation is withdrawn.

### (ah) What the flag shows when the check cannot place a number (raised 2026-10-14; decided the same day)

D22-E (2) says a flag names the comparable close figure for that same line, same kind, or "none". Under Option 2 (D22-F (1)) a number is matched only when the nearest preceding line name belongs to exactly one line whose figure equals it; otherwise the flag lists the candidate lines and the writer chooses the line. The question was what the flag shows when a number equals no printed figure and has no line name before it, and whether each candidate's figure is shown. **Decided by the Principal, Handbook D22-G (B3):** the flag says it is not clear which line the number describes and lists every line carrying a figure of the same kind, each with its figure; the Principal picks one and the pick is recorded.

### (ai) What picking a line does (raised 2026-10-14; decided 2026-10-15)

D22-G (B3) says the Principal picks a line and the pick is recorded. Not stated: if the picked line's figure equals the number, is the number matched and the flag cleared; if it does not, does the flag stay, showing that line's figure, with "Keep my number" and "Edit the text" still available? Optional Architect recommendation, not Principal-authorized scope: picking a line re-runs the check against that line; equal clears the flag with the pick recorded, unequal keeps it. **Decided by the Principal on 2026-10-15 (Handbook D22-H (3)):** this recommendation is adopted. If the picked line's figure equals the number, the number is matched, the flag clears and the pick is recorded; if not, the flag stays open and shows that line's figure, with "Keep my number" and "Edit the text" still available.

### (aj) History of mark changes (raised 2026-10-15; decided 2026-10-15)

The design keeps every finalized narrative and its deck, but the state record recommended in Handbook D22-G (A5) (3) held only the narrative that holds the mark now; finalization times show when the automatic moves happened, but a manual pick leaves no trace. **Decided by the Principal on 2026-10-15 (Handbook D22-H (11)):** the state record keeps a short append-only list of mark changes (from which narrative to which, when, by whom), one entry for each finalization and each manual pick. It records what the app marked as the deck source, not what was sent (the app has no send action), and it must not be described as proof of what was sent.

### (ak) Where "by whom" comes from (raised 2026-10-15; decided 2026-10-15)

At `b20d4b1` the dashboard does not capture who is acting: a closed period's snapshot stores an approval time but no approver, and the commentary library has a `submitted_by` field that the dashboard does not set. Accepting a flag (D22-C (2)) already records who and when, and each mark change entry (D22-H (11)) must too, so the app needs a source for the name. Options: a name typed once and kept for the session; a name typed at each action; the computer's login name (not authenticated); a fixed text for a single-user app. **Decided by the Principal on 2026-10-15 (Handbook D22-H (12)):** the Architect's recommendation is adopted. The app asks for a name once per session and requires it before the first accept, finalize or manual pick; it records what the person typed; it is not a login and must not be described as authentication.

### Known miss (iii) under Option 2 (raised 2026-10-14; accepted the same day)

A number written after the name of a different line, where the number equals that line's figure, is treated as matched, because the nearest preceding line name belongs to a line whose figure equals it. The check cannot see the writer's mis-attribution. It was not in the (ad) text. The Principal accepted it on 2026-10-14 (Handbook D22-G (B1)): "A number written after the name of a different line passes only when the sentence is true of that line as written."

## Part 2. Text moved verbatim from the Handbook (v2.28 revision, entry D22)

Only paragraph breaks were added, at the bold section headings. The wording is otherwise exactly as it stood. References such as "Section 10" and "D22-E (5)" are to the Handbook.

**Architect observations on D22-B (questions for the Principal, not decisions).** (h) The number check needs a definition before it can be briefed: what counts as a near match, how derived figures (differences, percentages) and rounded figures ("$4.0M" for "$4,016,906") are treated, and whether prompt additions are scanned as well as the narrative. (i) is answered by points (15) and (16); point (16) is the Architect's resolution and awaits the Principal's confirmation. **[Confirmed by the Principal on 2026-10-12, D22-C (2).]** (j) The system prompt stays fixed under this reading (my recommendation; the Principal did not address it), since it carries the governed narrative rules.  (k) and (l) are closed: the Principal decided them as points (9) and (10). (m), (n) and (o) are closed: the Principal decided them as points (12), (13) and (14). (p) Meaning of "reopen" in point (12). Reopening a closed period creates a new close version (D15), which starts its own narrative series (D22 point 3); it is not a new sub-version of the same close version. The Principal's wording is read that way. It also presumes that the reopen can proceed when the approved snapshot's commentary cannot be read, which was not checked; if the snapshot itself is damaged, whether it can be reopened is not stated. (q) Which flags the strip counts (point 14). Flags belong to sub-versions. Recommended: count the open flags of the sub-version the screen shows by default (the final-marked one if any, otherwise the latest) for the selected period. The count is a display only and gates no workflow state (point 9). A period with no saved close has no narrative and no count. (r) Draft stage needed for point (16). Accept-or-rework, and a hard flag that blocks finalizing, need a stage in which the narrative text exists and can be reviewed before the deck is generated and the sub-version is finalized. D22 point 2 says one click creates the narrative and the deck together, and D22-A says the same click finalizes it, so with a key no such stage exists as written. This is observation (a). It has to be answered before point (16) can be briefed: with a key, does a first action create the narrative draft, where flags are shown and cleared, and a second action build the deck and finalize it?

**Disposition of the observations above (v2.28).** (a) and (r) are resolved by D22-C (1). (c) is resolved by D22-C (9) point 4, which makes the final-marked sub-version the default and the deck source. (b), (d), (e), (f) and (g) remain open; (b) and (f) are sharpened, see (u). (h) is resolved in part by D22-C (7) and (8): every non-exact number is a hard flag, counts are in, only digits are scanned, prompt additions are not separately decided; what remains is (s) and (t). (i) was answered by points (15) and (16); point (16) is now confirmed by the Principal (D22-C (2)), and the references to a soft notice in points (15) and (16) are superseded by D22-C (7). (j) is resolved: the system prompt stays fixed. (p) and (q) are confirmed yes, and the reopen presumption in (p) has been checked and led to the amendment of point 12 in D22-C (5).

**New Architect observations on D22-C (questions for the Principal, not decisions).** (s) What an exact match is, and what a number is. D22-C (7) says "exact match to a close figure". Not stated: whether a rounded figure is an exact match ("$4.0M" for $4,016,906); how units are read (K, M, B, "million"); whether a derived figure the narrator computes, which is not printed in the data block, is a mismatch; and whether a derived figure that is printed in the data block counts as a close figure. If a rounded figure is not an exact match, every rounded number in a narrative carries a hard flag. E1 was confirmed as "digits only", but which digit strings are not numbers (years, "Q2" and "FY" labels, dates, ordinals, list numbering) was not addressed; the Architect treated this as necessary implementation, which the Principal has not separately confirmed. This is the successor to (h). (t) The tolerance's remaining role. With no soft tier, the 5% and 0.5 percentage-point values the Architect proposed on 2026-10-12 classify nothing and were not confirmed. Point 16's acceptance record names "the close figure it was matched to", and a number far from every close figure has none. Open: whether a nearest close figure is still named on the flag and recorded on acceptance (and, if so, how it is chosen, or whether the record says "none"); the pass rule's "in-tolerance" and "out-of-tolerance" plants also need a value. (u) The final mark at creation. D22-C (9) point 4 marks a new sub-version final when it is created. A draft that is never finalized, or is abandoned (still on the Principal's open list below), would then take the mark from a finalized sub-version that has a deck, and the deck source becomes whatever holds the mark. Open: whether the mark moves at draft creation, as written, or only at finalization; whether the explicit "mark as final" action can select a draft (observation (f)); and whether any action builds a deck from an earlier finalized sub-version without creating a new one (observation (b)), since "Finalize and build deck" acts on a draft. (v) "Two separate areas". D22-C (9) point 2 says the screen shows two separate areas for a sub-version; D22-B point (6) says one screen shows either text with a selector and also offers a side-by-side view. The Architect reads these as consistent (two separate texts) and not as replacing the selector; the Principal is asked to confirm. (w) "Independent Test" is not a role this Handbook defines. D22-C (8) assigns Set B to it. Open: who or what it is, and how its independence from the Builder is shown. (x) The definition of "damaged" in D22-C (5) awaits confirmation, including the wording "damaged or incomplete". (y) Point 6 arrived truncated (it ends at "not a loc"). The relayed point 6 stands until the rest of the Principal's wording arrives; it is also not known whether anything followed point 6 in the message.

**Disposition of observations (s) to (y), after the Principal's answers.** (s) is answered by D22-D (2). (t) is answered by D22-D (3), which leaves the question in (aa). (u) is answered by D22-D (4), the reading confirmed on 2026-10-14, and subject to (ab). (v) is confirmed by D22-D (5). (w) is answered by D22-D (6). (x) is confirmed by D22-D (7). (y) is answered by D22-D (1). D22-A observation (f) is answered by D22-D (4). All of these were confirmed by the Principal on 2026-10-14 (D22-D confirmation record).

**New Architect observations on D22-D (questions for the Principal, not decisions).** (z) The pass rule against the matching rule. D22-D (3) says every planted misstatement gets a hard flag. By D22-D (2) a number that equals a printed close figure at the precision written is a match and is not flagged, so a planted misstatement that happens to equal a different printed figure, or a coarse figure ("$4M") that rounds to a printed one, cannot be flagged. The Architect recorded this limit of the method in D22-C (8). Open: whether Set B excludes such plants, or the rule is "every planted misstatement that matches no printed close figure". **[Answered 2026-10-13 by D22-E (1): such a plant is flagged. Whether the check can do this depends on observation (ad).]** (aa) "The nearest close figure if one exists". With no tolerance, a nearest figure exists whenever the DATA block holds any figure of the same kind (dollar, percentage or count), so the condition is either always true or brings in a cut-off, which would be a tolerance again. **Optional Architect recommendation, not Principal-authorized scope:** name the nearest figure of the same kind, and record "none" only when the DATA block holds no figure of that kind. **[Replaced 2026-10-13 by D22-E (2): the flag names the comparable close figure for the same line, same kind, or "none"; there is no nearest-figure search.]** (ab) Consequences of D22-D (4). First, the status strip (D22-C (3)) was recorded as counting the sub-version shown by default, with the parenthetical "the final-marked one if any, otherwise the latest"; under D22-D (4) the screen shows the newest draft when one exists, so the parenthetical no longer describes the default. Open: which sub-version the strip counts when a newer draft exists. **[Answered 2026-10-13 by D22-E (3).]** Second, finalizing moves the mark, so finalizing a newer draft replaces a final mark the user set explicitly on an earlier sub-version; whether that is intended is not stated. Third, "the deck source stays the finalized sub-version" does not say what "Finalize and build deck" builds from, which is the draft being finalized; whether any action builds a deck from an earlier finalized sub-version without creating a new one remains observation (b). Fourth, an unfinished draft stays the default view until something abandons it, which is still open. **[Answered 2026-10-13 by D22-E (5): finalizing another sub-version deletes it.]** (ac) Who authors Set A. D22-D (6) assigns Set B to Independent Test. Set A (the narrative known to be correct, and the correct roundings the pass rule mentions) is not assigned. The Architect's standing instructions (section 20) bar the Architect from creating independent test cases or expected answers, so the Architect cannot author it. Open: whether Independent Test also authors Set A.

**Disposition after the Principal's decisions of 2026-10-13 (D22-E).** (z) is answered by D22-E (1), subject to the feasibility assessment in (ad). (aa) is answered by D22-E (2), and also needs the line to be known ((ad)). (ab), first part, is answered by D22-E (3). (ab), second and third parts, and (ac) are not decided and remain open (D22-E (6)). (e) of D22-A, what abandons a draft and whether a draft edit is itself a sub-version are answered by D22-E (4) and (5).

**New Architect observations on D22-E (questions for the Principal, not decisions).** (ad) Which line a narrative number describes (the assessment requested in D22-E (1); Architect assessment, not a decision). **Finding: the check cannot determine, deterministically and in general, which DATA-block line a number in free narrative text describes.** Evidence: the real prompt rendered by the repository's own demo (`rollups.py` run in a scratch copy on the sample dataset, Q4 2026 against Q3 2026, at `b20d4b1`; not the live app). No narrative text was available to test on, because the repository and the Project hold no generated narrative and the app has never stored one (Section 10), so the reliability of any option below cannot be given as a percentage; it can be measured only by the calibration test (Set A and Set B). What was measured is structural, by script (scratch file, not committed; the script also reads a few header and note numbers, so the counts are approximate). The block has about 70 figure-carrying lines and about 170 figures (103 dollar, 48 percent, 19 count); 27 lines carry three or more figures (up to five), so a line is not a single number. A name does not identify a line: "R&D" occurs in or under 15 lines, "Revenue" under 32, "G&A" 7, "Customer Success" 6, and each region and product line 3. Of 133 distinct figures, 29 appear on more than one line: 16 are the same segment shown twice (for example $669,939 for APAC in the revenue table and in the regional-investment table), 5 restate the same quantity under another label (a category subtotal and its "Total Variance"; an "Assessment" repeating a share), and 8 are coincidences between different quantities (for example +10.0% for EMEA revenue growth and +10% for Professional Services' share of the revenue variance; Operating Margin 35.0% and Add-on: Forecasting's +35% share; North America +26% and R&D +26%; the 8% flag threshold and Sales & Marketing +8%). A narrative saying "Professional Services revenue grew 10%" (the line says +6.1%) therefore equals a printed figure, and the check could pass it only by ignoring the line. Rounding adds more: written to $0.1M, 49 of the 61 dollar figures large enough to be written in millions have a differently valued look-alike on another line; written to the nearest $K, 31 of 102 do (30%); written as a whole percent, 20 of 48 do (42%). The narrative is free text: the system prompt (rule 4) allows the evidence in the sentence after the finding, rule 8 bars structure, and the words that separate lines ("spend", "cost", "opex") are not fixed. Options (each says what it changes; none is authorized). **Option 1, figures by reference (deterministic).** The app, not the writer, supplies every figure from the close: the model is told to write a placeholder that names a line and a field, the app fills the number, and the in-app editor inserts a figure by picking a line. Any digit string typed or generated is a hard flag. The line is known exactly. It changes the system prompt (the Principal accepted that it stays fixed, D22-C (3)), the way narratives are written and hand-written, and what is stored; it is the largest option. **Option 2, line identified from the writing, flag when unsure (repeatable, not guaranteed correct).** For each number the check lists the lines whose figure equals it at the precision written, and counts it as matched only if the nearest preceding line name (same sentence, or the previous sentence, because of rule 4) belongs to exactly one of those lines. Otherwise it is a hard flag that lists the candidate lines. It never falls back to any figure. It is built to err towards false flags, because a match needs the name and the figure to agree. Known misses: a line carries up to five figures, so a current figure written as the prior one on the same line passes (line-level matching, see below); and a wrong number that is right for the line named but describes something else passes. **Option 3, a second model call decides the line.** It needs an API key (a hand-written narrative with no key could not be checked, against D22-B (5)), is not deterministic, adds a credential and cost surface (Phase 4 Brief, Section 5a), and makes the check depend on the kind of model it checks. **Option 4, the writer names the line.** For a number the check cannot place, the flag asks the writer to choose the line from the candidates, and the acceptance records the line chosen. **Optional Architect recommendation, not Principal-authorized scope:** Option 2, with Option 4 as its accept action. Sub-question: D22-E (1) says "the specific line"; a line carries up to five figures. Matching at line level accepts a current/prior swap on the right line; matching at field level needs the check to read words such as "prior", "versus" and "grew", which is the same attribution problem one level down. Open: line level or field level, and which option. (ae) Point 1 and D22-A (the first check requested in D22-E (5)). Conflict: D22 point 1 as relayed says nothing generated through the main action is lost or silently overwritten; D22-E (5) deletes unfinalized drafts. D22-A does not use the word "permanent"; it says a finalized sub-version is locked and that a draft is directly editable. Its permanence therefore applies to finalized sub-versions by its own terms, and a draft is an editable working copy. **Proposed amended wording of point 1 (Architect proposal, awaiting the Principal's confirmation; not a decision):** "A finalized sub-version is permanent: it is kept and locked, and nothing finalized is lost or overwritten. A draft is an editable working copy. Editing a draft updates that same draft in place and never creates a new sub-version. A new numbered sub-version is created only when the user clicks "Generate draft". When a sub-version is finalized, every other unfinalized draft under the same close version is deleted, after the user has confirmed; the confirmation states how many drafts will be deleted. The on-screen narrative is an editable draft until it is finalized." (af) Deletion of drafts: the other checks requested in D22-E (5). (1) Not silent: the Principal requires the "Finalize and build deck" confirmation to say that the other unfinalized drafts will be deleted and how many. Whether it also names them (for example drafts 4 and 5) is not stated; the wording is for the Brief. (2) Newer drafts: the rule is by state, not by number, so finalizing 3 while 4 and 5 exist deletes 4 and 5 as well; this is workable. What is lost: their prompts (including the user's own notes, which are not in the close and cannot be rebuilt from it), their narrative text and hand edits, and their flags and acceptance records (who, when, matched figure). Nothing is recoverable. (3) D10 and D15, checked at `b20d4b1`: no code today deletes anything from an approved snapshot; the only deletions are session temporary directories for the reopen candidate and one control file in the undo path (`restore_pending_state`), and the only rename in Close History is `move_aside_incomplete_version`. `archive_close` writes a snapshot once at approval and refuses to overwrite it. The snapshot's `narrative.txt` is written at approval from session state that no code sets (Section 10), and D22-B (9) puts narrating after closing, so a draft cannot be inside a snapshot. D22-B (7) places each sub-version in its own folder beside the close version folder, not inside it, so deleting a draft touches only that folder. There is no conflict with D10 (the snapshot stays immutable; sub-versions are outputs generated from it) or D15 (a series belongs to a close version, a reopen starts a new series, and finalizing in one close version deletes only drafts under that close version). These are properties of a design that is not built. **Necessary implementation for the Brief (Category D, not new scope):** delete only the exact sub-version folders recorded in the state record, never by pattern, because the existing discovery treats any `v<number>` folder as a close version; and delete only after the finalization and the deck are durably written, so that a failed build deletes nothing. (4) Convention: the Fix K work moved an incomplete version folder aside and "never deleted" it; D22-E (5) is the first deliberate deletion of persisted content in this area. That is not a conflict (different content, the Principal's decision), and it is recorded. (5) Storage, a fact for the Principal's decision: under the two-stage flow a draft holds no deck, because the deck is built at "Finalize and build deck". A draft is the prompt (7.3 KB rendered for Q4 2026 without a commentary block), the narrative (up to about 6 KB at the current 1,500-token limit) and a small state record, about 15 KB. One hundred drafts are about 1.5 MB. The decision stands; deletion is irreversible and the saving is small, so the Principal may want to confirm that storage is the whole reason. (ag) Numbering after deletion, and drafts under superseded close versions. D22 point 3 numbers sub-versions 1, 2, 3 and so on, none overwritten. After 4 and 5 are deleted, the next "Generate draft" could take 4 again or take 6. Reusing 4 makes "sub-version 4" mean two things over time (in the Principal's notes, in anything that cites a number). Not reusing it needs the highest number issued to be recorded, because a deleted folder leaves nothing; it could sit in the state record of the finalized sub-version. **Optional Architect recommendation, not Principal-authorized scope:** do not reuse numbers, and record the highest number issued. Separately, the rule deletes drafts only under the same close version; drafts under an earlier close version (after a reopen starts a new series) are not touched, and what becomes of them is not stated.

**Remaining open, from the Principal's own list:** what triggers a sub-version to be abandoned without becoming part of the record; and whether every draft edit is itself the draft sub-version or something lighter. **[Both answered 2026-10-13: a draft is abandoned when another sub-version under the same close version is finalized (D22-E (5)); a draft edit is not a sub-version (D22-E (4)).]**

**Architect observations on how D22-A meets points 1 to 6 and D15 (questions for the Principal, not decisions).** (a) Point 2 says one click produces the narrative and the deck together, and D22-A says the same click finalizes the sub-version. Read literally, a sub-version is finalized the moment it is created and is never a draft that can be edited; the sequence in which a draft exists and is then finalized is not stated. (b) D22-A says the deck action takes the final-marked sub-version as its source, but point 2 has the same action create a new narrative each time. Whether the action has a use that builds a deck from an existing narrative without creating a new one is not stated. (c) Point 4 lets the user select an earlier sub-version to feed the deck, and D22-A makes the final mark the default source. Which prevails when both apply is not stated. (d) "Within a close" is read here as within a close version, in line with point 3. Whether the final mark is held per close version, how it is shown when a reopen produces a later close version (D15), and whether it can be set on a quarter flagged outdated (D19) are not stated. (e) Editing a draft changes its text in place, while point 1 says nothing generated is silently overwritten; the Principal has listed this as open. **[Resolved 2026-10-13: editing in place is intended (D22-E (4)); the consequence for point 1 is in D22-E (5) and observation (ae).]** (f) Whether a draft can be marked final, or only a finalized sub-version, is not stated. (g) The lock and the final mark are state held with the narrative; where that state is held touches D10 and D15 and depends on the storage decision.


## Appendix A. The (ad) probe script (added 2026-10-14)

Written by the Architect for observation (ad). It reads a rendered prompt, takes the text between the lines `DATA:` and `TASK:`, and counts figures per line, figures that appear on more than one line, figures whose written form matches a differently valued figure on another line, and how many lines mention each name. It reads no narrative and writes nothing. Run it with the file in Appendix B saved as `rendered_prompt.txt`: `python3 line_attribution_probe.py rendered_prompt.txt`. It was re-run on 2026-10-14 and gave the figures cited in (ad): 71 figure-carrying lines, 170 figures (103 dollar, 48 percent, 19 count), 133 distinct figures of which 29 appear on more than one line, 49 of 61 at $0.1M, 31 of 102 at the nearest $K and 20 of 48 as whole percents with a differently valued look-alike, and 27 lines with three or more figures. The script counts the 29; the division of those 29 into three groups in (ad) (16, 5 and 8) was made by reading the lines and is not produced by the script. The counts are approximate because the script also reads a few header and note numbers.

```python
"""Structural probe for D22-E (1): can a narrative number be tied to the DATA-block line it describes?

Input: the real rendered prompt produced by running rollups.py (scratch copy) on the sample dataset.
No narrative text is used; this measures only the DATA block itself.
"""
import re
import sys
from collections import defaultdict

SRC = sys.argv[1]
text = open(SRC, encoding="utf-8").read().split("\n")

# slice the rendered prompt: from "DATA:" to "TASK:"
start = next(i for i, l in enumerate(text) if l.strip() == "DATA:")
end = next(i for i, l in enumerate(text) if l.strip() == "TASK:")
block = text[start + 1:end]

NUM = re.compile(r"(?<![\w.])([+-]?)(\$?)(-?)(\d[\d,]*(?:\.\d+)?)(%?)")

lines = []  # dict(section, label_text, raw, figures[list of (kind, exact_str, value)])
section = ""
for raw in block:
    s = raw.rstrip()
    if not s.strip():
        continue
    stripped = s.strip()
    # section headers: unindented, no leading dash, not a note/assessment
    if not s.startswith((" ", "-", "(")) and not stripped.startswith(("Assessment", "NOTE", "Total Variance", "Component Breakdown", "Region cut", "Product Line cut")):
        section = stripped
        # a header may itself carry figures (e.g. "Total Variance"), handled below if it is a data line
    # skip pure notes
    if stripped.startswith(("(Volume effect", "(Not a volume", "(Flag thresholds", "NOTE:")):
        # thresholds in notes are still numbers in the DATA block; keep the threshold note only
        if not stripped.startswith("(Flag thresholds"):
            continue
    # strip period labels so "Q4 2026" is not read as a number
    scrub = re.sub(r"Q[1-4] (?:FY)?\d{4}", "", stripped)
    figs = []
    for m in NUM.finditer(scrub):
        sign1, dollar, sign2, digits, pct = m.groups()
        digits_clean = digits.replace(",", "")
        try:
            val = float(digits_clean)
        except ValueError:
            continue
        if sign1 == "-" or sign2 == "-":
            val = -val
        kind = "dollar" if dollar else ("percent" if pct else "count")
        figs.append((kind, m.group(0), val))
    if figs:
        lines.append({"section": section, "text": stripped, "figs": figs})

print(f"DATA-block lines carrying at least one figure: {len(lines)}")
all_figs = [(i, k, raw, v) for i, L in enumerate(lines) for (k, raw, v) in L["figs"]]
print(f"figure instances: {len(all_figs)}  (dollar {sum(1 for f in all_figs if f[1]=='dollar')}, "
      f"percent {sum(1 for f in all_figs if f[1]=='percent')}, count {sum(1 for f in all_figs if f[1]=='count')})")

# 1. same exact figure on more than one line
by_exact = defaultdict(set)
for i, k, raw, v in all_figs:
    by_exact[(k, round(abs(v), 4))].add(i)
multi = {key: idxs for key, idxs in by_exact.items() if len(idxs) > 1}
distinct = len(by_exact)
print(f"\ndistinct exact figures: {distinct}; appearing on 2+ lines: {len(multi)}")
for kind in ("dollar", "percent", "count"):
    ks = [key for key in by_exact if key[0] == kind]
    mk = [key for key in multi if key[0] == kind]
    print(f"   {kind:7s}: {len(mk)} of {len(ks)} distinct figures appear on 2+ lines")
print("   examples (dollar):")
shown = 0
for key, idxs in sorted(multi.items(), key=lambda kv: -len(kv[1])):
    if key[0] != "dollar":
        continue
    print(f"      ${key[1]:,.0f} on {len(idxs)} lines, e.g.:")
    for ix in sorted(idxs)[:3]:
        print("         |", lines[ix]["text"][:95])
    shown += 1
    if shown >= 3:
        break

# 2. look-alikes at plausible written precision: another line, DIFFERENT underlying value, same written form
def forms(kind, v):
    a = abs(v)
    if kind == "dollar":
        out = {"whole $": f"{a:,.0f}", "nearest $K": f"{round(a/1e3):d}K"}
        if a >= 5e4:
            out["$M, 1 dp"] = f"{a/1e6:.1f}M"
        if a >= 5e4:
            out["$M, 2 dp"] = f"{a/1e6:.2f}M"
        return out
    if kind == "percent":
        return {"% 0 dp": f"{a:.0f}%", "% 1 dp": f"{a:.1f}%"}
    return {"integer": f"{round(a):d}"}

print("\nlook-alikes: a figure whose written form also matches a figure of DIFFERENT value on ANOTHER line")
print("(this is the case 'matches somewhere in the DATA block' would wrongly accept)")
fig_forms = defaultdict(lambda: defaultdict(set))  # form_name -> written -> set of (line, exactval)
for i, k, raw, v in all_figs:
    for name, w in forms(k, v).items():
        fig_forms[(k, name)][w].add((i, round(abs(v), 4)))
for (k, name), d in sorted(fig_forms.items()):
    total = set()
    hit = set()
    for w, members in d.items():
        vals = {v for (_, v) in members}
        for (i, v) in members:
            total.add((i, v))
            if len({ln for (ln, vv) in members if vv != v}) >= 1:
                hit.add((i, v))
    print(f"   {k:7s} {name:10s}: {len(hit):3d} of {len(total):3d} line-figures have a different-valued look-alike on another line ({100*len(hit)/len(total):.0f}%)")

# 3. label ambiguity: how many DATA lines mention each name
labels = ["APAC", "EMEA", "LATAM", "North America", "Core Platform", "Professional Services",
          "Add-on: Forecasting", "Add-on: Reporting", "Customer Success", "G&A", "R&D",
          "Sales & Marketing", "Salaries & Benefits", "Software & Tools", "Other Opex", "Revenue", "Operating"]
print("\nnumber of figure-carrying DATA lines (or their section) that mention each name:")
for lab in labels:
    n = sum(1 for L in lines if lab in L["text"] or lab in L["section"])
    nlines_text = sum(1 for L in lines if lab in L["text"])
    print(f"   {lab:22s}: {n:3d} lines (named in the line itself: {nlines_text})")

# 4. figures per line
per = [len(L["figs"]) for L in lines]
print(f"\nfigures per line: min {min(per)}, max {max(per)}, mean {sum(per)/len(per):.1f}; lines with 3+ figures: {sum(1 for p in per if p>=3)}")
```

## Appendix B. The DATA block the probe ran on (added 2026-10-14)

This is the text from `DATA:` to `TASK:` of the user prompt that `rollups.py` rendered for Q4 FY2026 against Q3 FY2026 on the sample dataset, at `b20d4b1`. It came from running `python3 rollups.py` in a scratch copy of the repository, not the live app. The demo rewrites `rollups_output.xlsx` in the working directory and makes a live API call if `ANTHROPIC_API_KEY` is set, so run it in a scratch copy with no key. The dataset is the project's sample data.

```
DATA:

Consolidated P&L:
- Revenue: $4,016,906 vs $3,775,631 (+6.4%)
- Total Opex: $2,482,356 vs $2,454,984 (+1.1%)
- Operating Profit: $1,534,550 vs $1,320,647
- Operating Margin: 38.2% vs 35.0%

Revenue by Region (Q4 2026):
  - APAC: $669,939 vs $633,549 (+5.7%)
  - EMEA: $1,203,534 vs $1,094,086 (+10.0%)
  - LATAM: $322,521 vs $289,104 (+11.6%)
  - North America: $1,820,912 vs $1,758,892 (+3.5%)

Revenue by Product Line (Q4 2026):
  - Add-on: Forecasting: $808,898 vs $725,323 (+11.5%)
  - Add-on: Reporting: $614,830 vs $560,103 (+9.8%)
  - Core Platform: $2,184,198 vs $2,104,687 (+3.8%)
  - Professional Services: $408,979 vs $385,519 (+6.1%)

Regional Go-to-Market Investment / Product Line R&D Investment (Q4 2026) — $ only, no cross-segment % (see note below):
Region cut (net of Sales & Marketing + Customer Success only):
  - APAC: Revenue $669,939, Allocated S&M+CS Opex $189,173, Net of GTM Cost $480,767
  - EMEA: Revenue $1,203,534, Allocated S&M+CS Opex $339,845, Net of GTM Cost $863,689
  - LATAM: Revenue $322,521, Allocated S&M+CS Opex $91,071, Net of GTM Cost $231,450
  - North America: Revenue $1,820,912, Allocated S&M+CS Opex $514,176, Net of GTM Cost $1,306,736
Product Line cut (net of R&D only):
  - Add-on: Forecasting: Revenue $808,898, Allocated R&D Opex $202,275, Net of R&D Cost $606,623
  - Add-on: Reporting: Revenue $614,830, Allocated R&D Opex $153,746, Net of R&D Cost $461,084
  - Core Platform: Revenue $2,184,198, Allocated R&D Opex $546,187, Net of R&D Cost $1,638,011
  - Professional Services: Revenue $408,979, Allocated R&D Opex $0, Net of R&D Cost $408,979
  NOTE: these are investment-proportionality figures ($only) — Net of GTM Cost (region) and Net of R&D Cost (product) — not a margin or profitability measure, and not comparable to each other (different cost bases). No cross-segment % is provided anywhere in this data by design (Professional Services carries zero allocated R&D, so its Net of R&D Cost equals its own revenue). Use the $ figures only to discuss relative segment size or which segment carries the largest/smallest allocated cost — never infer or state a %.

Expenses by Department:
  - Customer Success: $379,949 vs $370,958 (+2.4%)
  - G&A: $445,883 vs $434,372 (+2.7%)
  - R&D: $902,208 vs $902,047 (+0.0%)
  - Sales & Marketing: $754,316 vs $747,607 (+0.9%)

Salaries & Benefits — Volume/Rate Decomposition (pre-calculated, per department):
  - Customer Success: headcount change +1.3, cost-per-head change $-139, Volume effect $12,431, Rate effect $-4,040, total variance $8,390
  - G&A: headcount change -1.3, cost-per-head change $1,096, Volume effect $-15,921, Rate effect $26,671, total variance $10,751
  - R&D: headcount change +1.0, cost-per-head change $-207, Volume effect $10,016, Rate effect $-13,379, total variance $-3,362
  - Sales & Marketing: headcount change +1.0, cost-per-head change $-156, Volume effect $11,093, Rate effect $-7,488, total variance $3,604
(Volume effect = change in headcount x prior period cost-per-head. Rate effect = new headcount x change in cost-per-head. Calculated upstream — narrate, do not recompute.)

Revenue and Expenses — Breadth/Concentration, with per-segment Component Breakdown (pre-calculated, D17-BB-001):
Revenue (by Region) — Q4 2026
Total Variance: $241,275

Component Breakdown:
  APAC: $36,390  | +15%
  EMEA: $109,448  | +45%
  LATAM: $33,417  | +14%
  North America: $62,020  | +26%

Assessment: Broad-based across 4 of 4 segments driving the net movement
Revenue (by Product Line) — Q4 2026
Total Variance: $241,275

Component Breakdown:
  Add-on: Forecasting: $83,576  | +35%
  Add-on: Reporting: $54,728  | +23%
  Core Platform: $79,511  | +33%
  Professional Services: $23,461  | +10%

Assessment: Broad-based across 4 of 4 segments driving the net movement
Expenses — Q4 2026
Total Variance: $27,372

Component Breakdown:
  Other Opex: $11,835  | +43%
  Salaries & Benefits: $19,383  | +71%
  Software & Tools: $-3,846  | -14%

Assessment: Concentrated in Salaries & Benefits (+71% of net variance, threshold 17%), driving the net movement
Salaries & Benefits (by Department) — Q4 2026
Total Variance: $19,383

Component Breakdown:
  Customer Success: $8,390  | +31%
  G&A: $10,751  | +39%
  R&D: $-3,362  | -12%
  Sales & Marketing: $3,604  | +13%

Assessment: Concentrated in G&A (+39% of net variance, threshold 17%), driving the net movement
Software & Tools (by Department) — Q4 2026
Total Variance: $-3,846

Component Breakdown:
  Customer Success: $-1,319  | -5%
  G&A: $166  | +1%
  R&D: $-3,613  | -13%
  Sales & Marketing: $920  | +3%

Assessment: Broad-based across 2 of 4 segments driving the net movement
Other Opex (by Department) — Q4 2026
Total Variance: $11,835

Component Breakdown:
  Customer Success: $1,919  | +7%
  G&A: $595  | +2%
  R&D: $7,136  | +26%
  Sales & Marketing: $2,184  | +8%

Assessment: Concentrated in R&D (+26% of net variance, threshold 17%), driving the net movement
(Not a volume/rate split — measures whether a variance is systemic/broad-based or concentrated in one segment, on a NET (signed), not gross, basis; no gross-variance figure appears anywhere below. Revenue lines (by Region, by Product Line) use their own total and a 60% concentration threshold. Expenses lines (Total Expenses, then each Category, then each Category's Departments) all share ONE denominator — Total Expenses' own net variance — for both their % share and their driving-vs-offsetting classification, at a 17% concentration threshold; a Department's or Category's own "Total Variance" line is still its own subtotal, only its % and classification reference the shared total. An opposing segment carrying >=20% of net variance is flagged as substantially offsetting, for both Revenue and Expenses. Do not add "favorable"/"unfavorable" wording anywhere in this section.)

Headcount:
  - Customer Success: 29 vs 28.0
  - G&A: 24 vs 25.0
  - R&D: 66 vs 64.0
  - Sales & Marketing: 48 vs 48.0
  Company-wide Revenue per Headcount: $24,053 vs $22,883

Budget vs Actual — flagged items only (Watch or Major Miss):
  - Revenue: Budget $4,294,336, Actual $4,016,906, Variance -6.5% — Watch
(Flag thresholds: |Variance %| > 8% = Major Miss, > 4% = Watch, else On Track.)


TASK:
```
