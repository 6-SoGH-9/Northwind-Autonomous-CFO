# D22 Number Check Amendment: Builder Brief Addendum 2 (REVISION 2, SIGNED BY THE PRINCIPAL 2026-11-13, NOT YET CANONICAL)

**Revision 2 (2026-11-13, after the Principal's Gate decisions of 21:38).** Changes against draft 1, nothing else: (1) R1 and R2 are named the **Line Naming Rule** wherever the addendum refers to them (Part 0 item 3, Part 1 section 2, N-0, Part 3); (2) Part 1 section 6 corrected: the Principal ruled on the reverse of known miss (i) on 2026-11-13, so the statement that he had not is removed, and the rulings for the next Handbook update now include his two further rulings; (3) the seven Gate decisions are recorded as the Principal stated them; the Principal Approval Gate boxes and the signature are left for him.

**STATUS: SIGNED by the Principal on 2026-11-13 (Part 3); NOT YET CANONICAL.** No Builder may start from this text. It becomes a Builder instruction only when the Principal makes the signed file canonical on `main`, and the Builder still waits for Release 1 to be on `main` (Part 0 item 6).
**Addendum ID:** `d22_narrative_versioning_builder_brief_addendum_2` (proposed path: `governance/builder_briefs/D22_Narrative_versioning_builder_brief_addendum_2.md`; the Principal may override).
**Amends:** WP3 of the signed Brief (`governance/builder_briefs/D22_Narrative_versioning_builder_brief.md`, committed `f517ce1`), on top of Addendum 1 (`governance/builder_briefs/D22_Narrative_versioning_builder_brief_addendum_1.md`, on `main` at `8cb1dca`). Addendum 2 is separate from Addendum 1 and does not change it.
**Authority for scope:** the Principal's message of 2026-11-13 21:22 (decisions 1 to 5) and the options assessment of 21:16 that it answers. Letters such as "observation (ad)" refer to `governance/architect_reports/d22_architect_observations_a_to_ag.md`.
**Handbook:** not updated and not asked to be (Part 1, section 6).
**Test sentences:** this addendum contains none and states no expected results. Independent Test writes the cases (Part 2, Evidence).

---

# PART 0: WHAT THE PRINCIPAL MUST LOOK AT FIRST

1. **Scope is exactly two options, and nothing else.**
   - **Option A (collapse duplicates):** a number matches when every line the written name matches that carries the figure has the same value.
   - **Option D1 (leading qualifiers):** a fixed list of leading qualifiers, such as "Company-wide" and "Total", is ignorable when a written name is compared with a printed label.
   - Not included, as decided: options B, C and D2/D3 from the 21:16 assessment, and anything else.
2. **One thing in D1 needs your answer before you sign: the "Total" qualifier, as literally decided, would add new false flags in the Q4 prompt.** This is the main finding of my check of the fixture.
   - In the Q4 prompt, "Total" leads the label of six "Total Variance" lines and of "Total Opex". Removing it leaves the one-word aliases "Variance" and "Opex".
   - Those words are common in narrative prose. Under the existing rule the nearest name wins, so "variance" or "opex" written near a number would take the name slot from the real subject (for example a department name), and the number would be checked against the "Total Variance" or "Total Opex" lines instead. That adds flags to sentences that pass today, and it can let a wrong number pass when it equals one of those totals.
   - "Company-wide" is not affected: its only use in the Q4 prompt is "Company-wide Revenue per Headcount", which leaves the three-word alias "Revenue per Headcount".
   - **My default (Category E, Gate decision 3):** the list contains both words you named, with a guard: a qualifier is ignored only when at least two words of the label remain. With the guard, "Total" gives no alias in the Q4 prompt, and the "Total Variance" and "Total Opex" labels are unchanged. Without the guard, the Q4 prompt gets the two one-word aliases above. This was a narrowing of what you wrote, so I asked. You approved the guard on 2026-11-13 (Gate decision 3).
3. **A line's name: the Line Naming Rule (Release 1 readings R1 and R2), the single working definition (Gate decision 7).** It is stated once, in Part 2, section N-0, so the Builder reads one definition. R3 and R4 and R5 of the Release 1 module docstring are not part of this addendum; Addendum 1 already amends R3 for sentences with a direction word.
4. **Handbook:** it needs an addition, not a correction (Part 1, section 6). Nothing to do now.
5. **Other defaults I applied** (Category E, each for your decision): same value includes the sign; the line reported for a collapsed number is the first in block order; qualifiers are matched at the start of a label, one at a time, as whole words. Details in Part 3.
6. **Release 2 waits for both addenda** (your decision 4). Nothing here changes Release 1, which you accepted against the signed Brief and will push yourself.

---

# PART 1: REQUIRED RESPONSE FORMAT (Architect analysis)

**Repository identification.** `origin/main` = `8cb1dca` (2026-11-13 11:00), which holds the signed Brief (`f517ce1`) and Addendum 1. Release 1 (`cd5731c`) is not yet on `main`; the Principal has accepted it and will push it. Release 1 files were read from the Builder's pack (`narrative_number_check.py`, `parse_data_block`, `_name_occurrences`, `check_numbers`) and the Q4 FY2026 fixture.

## 1. REQUIREMENT
- **A.** When the written name matches more than one line carrying the figure and all of those lines carry the same value, the number matches.
- **D1.** A written name matches a printed label when it equals the label, or equals the label with one leading qualifier from a fixed list removed.

## 2. EXISTING AUTHORITY
D22-F (1) and D22-G (B1) (line level; the nearest name must belong to exactly one of the lines whose figure equals the number); WP3-3; observation (ad) (29 repeated figures). Names of lines: the **Line Naming Rule** (Release 1 readings R1 and R2), confirmed by the Principal on 2026-11-13 as the working definition for now; the Handbook and Brief text do not define a name.

## 3. CLASSIFICATION
Both are new Principal decisions (Category B), made 2026-11-13. The guard, the same-value definition and the other defaults in Part 3 are Category E.

## 4. SUPERSEDED / DEFERRED DECISIONS
- **"Exactly one of the lines"** (D22-F (1), WP3-3) is replaced for matching by "exactly one distinct printed value among the lines the name matches". Where two or more lines carry different values, the number is still a flag.
- **Not decided here (deferred as options B, C and D2/D3):** names after the number, category words, partial labels, changing prompt labels. They remain open; they are not vetoed.

## 5. GENUINE CONFLICTS
None found. Addendum 1 B-1, B-5 and E-6 speak of "a matched line"; Part 2 section N-4 says how they read after collapse.

## 6. GOVERNANCE CHANGES REQUIRED
**Does the Handbook need a correction?** No. I searched the Handbook on `main` (v2.31) for a definition of a line's name, for the label rule, and for any mention of Addendum 1 or Release 1. It defines no name, so the Line Naming Rule does not contradict it, and nothing in it is wrong. It does need an addition, when the Principal asks. The Principal's rulings to record there:
- **The Line Naming Rule** (Release 1 readings R1 and R2, as stated in N-0) as the working definition of a line's name, for now.
- **Addendum 1 and Addendum 2** as amendments to D22-F (1) and WP3-3.
- **The reverse of known miss (i)** (a prior figure written as current; Independent Test's K1 and K2): ruled by the Principal on 2026-11-13, in his instructions to Independent Test, as a known miss of class (i), reverse direction. (Draft 1 said he had not ruled; that was stale and is corrected.)
- **Direction words** are recorded as class (ii) until Addendum 1 is built (Principal's ruling).
- **Derived numbers** (true but not printed in the DATA block) are tested as a separate Set C and kept out of the false-flag rate (Principal's ruling).
- **The D22 status text**, which already carries the documentation-drift item that the Handbook logged at v2.29.

## 7. ARCHITECTURE IMPACT
One pure function (`narrative_number_check.py`). No screen, no store, no prompt, no new Flag field, no new reason constant. Two new constants (N-2).

## 8. IMPLEMENTATION IMPACT (Architect estimate; the Builder sizes it)
Small. A: one branch in `check_numbers` where `len(overlap) > 1`. D1: extra aliases added in `parse_data_block`, using the alias mechanism Release 1 already has for the part of a label after a colon.

## 9. TESTING IMPACT
Independent Test writes the cases and expected results. The Builder's own tests cover the rules in Part 2 and the Release 1 regression. No test sentence or expected result is authored in this addendum.

## 10. DEPENDENCIES AND BLOCKING
Release 1 on `main`; Addendum 1 on `main`; this addendum signed and on `main`. Release 2 waits for both addenda.

## 11. SEQUENCING
Both addenda edit the same function. Whether the Builder builds them in one task or two is Gate decision 5.

## 12. READY FOR BUILDER BRIEF?
**YES for the scope in Part 2.** Gate decisions 1 to 7 are recorded; the Principal's signature is outstanding. Not startable until Part 0 item 6's conditions and the base are met.

---

# PART 2: BUILDER BRIEF (ADDENDUM 2)

## Objective
Reduce false flags from two causes, without leaving line-level matching: lines that share a name and carry the same value (A), and printed labels with a leading qualifier that the writer leaves off (D1).

## N-0. The Line Naming Rule: definition of a line's name (single definition; Principal, 2026-11-13)
This is the **Line Naming Rule**: the definition in the Release 1 module docstring (R1 and R2), confirmed by the Principal as the working definition "for now". The Builder reads this and not the docstring. Nothing in it changes except what N-2 adds.
- **A line (R1):** one printed line of the DATA block that carries a figure.
- **Its name (R1):** the label before the last colon that precedes its first figure (for example "Revenue", or "Add-on: Forecasting"). The part after a colon inside a label is an extra alias. Only a labelled line can be named. Note lines with no label can be candidate lines but cannot be named. A line such as "Assessment: Concentrated in …(+71% …, threshold 17%)" is therefore named "Assessment", not by the department mentioned in its text.
- **Matching names (R2):** names are matched on word tokens, case-insensitive, with "&" read as "and". The nearest preceding name is the closest occurrence that ends before the number, in the same sentence, else in the previous sentence. Where occurrences overlap, the longer one wins.
- **Aliases:** each line's name tokens, plus the part after a colon, are its aliases. Several lines can share an alias.

## Part A: Collapse duplicates

**A-1. Rule.** Release 1 builds the list of lines the written name belongs to and whose printed figure equals the number at the precision written (`overlap`). It matches only when that list has exactly one line. Replace this with:
- match when the list has exactly one line (unchanged); or
- match when the list has two or more lines and the figures that equal the number at the precision written, taken over all those lines, form **one distinct printed value** (same kind, same magnitude, same sign: E-A1).
- Otherwise the number is a flag, with the existing reason (`REASON_AMBIGUOUS` when the list has two or more lines).

**A-2. What is unchanged.** The name rule, the one-line rule when the lines carry different values, the precision rule (WP3-2), no fall-back to any printed figure, picks (A-5b of Addendum 1: a pick is checked against the picked line's own figures), acceptances, and Addendum 1's pools (A-3 of Addendum 1) all stay as they are. The collapse works on the lines left by the pool filter.

**A-3. The matched line.** A number matched by collapse is reported as matched against the first of the collapsed lines in DATA-block order (WP3-10: deterministic). No new field.

**A-4. What it lets through (accepted known misses, to be recorded):** (iv) a number that equals the shared value of two same-named lines but describes the measure of only one of them; the check cannot tell which. The Principal has accepted the false-flag trade-off in the options assessment of 21:16.

## Part D1: Leading qualifiers

**D1-1. Rule.** For each printed label, in addition to its existing aliases (N-0), add one alias: the label with a leading qualifier removed, when all of the following hold:
- the label begins with a qualifier from the list in D1-2, matched as whole words, case-insensitive;
- one qualifier is removed, at the start only;
- at least `MIN_TOKENS_AFTER_QUALIFIER` words remain (D1-3).
The full label stays an alias. The new alias is treated exactly like the part after a colon today: it can be shared by several lines, and the existing "exactly one line" and Part A rules decide what happens.

**D1-2. The list (fixed; Principal, 2026-11-13).** `IGNORABLE_QUALIFIERS`: "Company-wide" and "Total". The Principal wrote "such as"; no other word is added by this addendum. The tokenizer reads "Company-wide" as the two words "company" and "wide", so the Builder matches the qualifier on its tokens. Any addition is a Gate decision, not a Builder choice (Gate decision 4).

**D1-3. The guard (E-D1, Gate decision 3).** `MIN_TOKENS_AFTER_QUALIFIER = 2` is the recommended default. With 2, a qualifier is ignored only if at least two words remain.
- In the Q4 prompt this gives the alias "Revenue per Headcount" for "Company-wide Revenue per Headcount", and no alias for "Total Variance" (six lines) or "Total Opex".
- If the Principal decides against the guard, the constant is 1 and the one-word aliases "Variance" and "Opex" appear (Part 0 item 2).

**D1-4. What it lets through (accepted known misses, to be recorded):** (v) a number written under a shortened name that equals the figure of the qualified line, when the writer meant another entity. The check cannot see the writer's intent, as in known miss (iii).

## Scope Out
Options B (names after the number), C (category words, section titles as names) and D2/D3 (partial labels, changing prompt labels); any qualifier beyond the list; qualifiers removed from the middle or end of a label; two qualifiers at once; fuzzy or partial matching; any change to the prompt (`rollups.py`); any change to Release 1 or Addendum 1 behaviour other than what Part A and Part D1 state; screens; the Handbook.

## Files that may and may not change
**May:** `narrative_number_check.py` (the Release 1 version on `main`, after Addendum 1 if built first); its tests; new test files; the fixture (additions only). **May not:** everything else.

## N-4. Reading Addendum 1 after collapse
- **B-1 (direction applies "after it has matched exactly one line"):** read as "after it has matched, including by collapse or by pick".
- **B-5 and E-6 (printed figures on the matched line):** read as the printed figures on the matched line or collapsed lines. After collapse every line carries the same value, so the sign is the same on all of them.
- **B-7 (direction acceptance key):** the line in the key is the first collapsed line in block order (A-3).
- **A-3 and A-5b (pools and picks):** unchanged.

## Acceptance criteria (rules, not examples)
- A number whose written name belongs to two or more lines that carry the same printed value is matched (A-1).
- A number whose written name belongs to two or more lines that carry different printed values is a flag with `REASON_AMBIGUOUS` (A-1).
- Two lines carrying the same magnitude with different signs are not the same value (E-A1).
- The result is the same on every run (WP3-10).
- A written name equal to a label without its leading qualifier matches the line (D1-1); with the guard at 2, a label with one remaining word gets no new alias (D1-3).
- A label that begins with a word that is not in the list gets no new alias; the full label still matches as in Release 1.
- Release 1 behaviour is unchanged for names and numbers not touched by A or D1.

## Required evidence
- **Builder:** test results for the rules above and the Release 1 regression, reproduced by the Architect. Builder narration is not evidence.
- **Independent Test:** the cases and expected results, written before any run, and a run against the function as built. It also measures the false-flag rate on the same material as the 21:16 report, so the effect of A and D1 is shown against the baseline of 18 of 87.
- Not canonical until the Principal makes it so.

## Stop-and-report rule
If the Builder finds that a requirement here cannot be built as written, or contradicts Release 1 or Addendum 1, it stops and reports. It does not decide.

---

# PART 3: SCOPE AUTHORIZATION GATE (PRINCIPAL SIGN-OFF REQUIRED)

**Status:** ☑ SIGNED BY PRINCIPAL  ☐ BLOCKED  ☐ AWAITING PRINCIPAL DECISION (Gate decisions 1 to 7 recorded from the Principal's message of 2026-11-13 21:38; Approval Gate ticked and signature line entered at his written instruction of 21:44)

## CATEGORY A: ALREADY AUTHORIZED
Line-level matching (Option 2 with Option 4); no fall-back; picks re-run the check; acceptances keyed to number and line; known misses (i) to (iii) (D22-F (1), D22-G (B1), WP3-3 to WP3-5). Addendum 1 on `main`.

## CATEGORY B: NEW PRINCIPAL DECISIONS (2026-11-13, 21:22)
- B-1. Option A: collapse duplicates ("a number matches if every line the name matches that carries the figure has the same value").
- B-2. Option D1: a fixed list of ignorable leading qualifiers, such as "Company-wide" and "Total".
- B-3. Options B, C and D2/D3 are not included.
- B-4. R1 and R2 are the working definition of a line's name, for now, named the **Line Naming Rule** (21:38).
- B-5. Release 2 waits for both addenda.
- B-6. Independent Test writes the cases; the Architect writes no test sentence or expected result.

## CATEGORY C: GENUINE CONFLICTS
None.

## CATEGORY D: TECHNICAL / PROCEDURAL
- D-1. Build base: canonical `main` with Release 1 and Addendum 1.
- D-2. The matched line after collapse is the first in block order; no new field, reason or class.
- D-3. Two new constants, `IGNORABLE_QUALIFIERS` and `MIN_TOKENS_AFTER_QUALIFIER`; neither name appears in Release 1 (searched).

## CATEGORY E: ARCHITECT DEFAULTS (separate from mandatory scope; the Principal may change each)
- E-A1. "Same value" means the same kind, magnitude and sign of the printed figure. Two lines with the same magnitude and opposite signs are not the same value. (Alternative: compare at the precision written, which would also collapse lines whose printed values differ but round to the written figure; not recommended, because it hides real differences.)
- E-A2. Collapse needs exactly one distinct printed value among all the figures that equal the number, over all the lines in the list. A line that carries two different values that both equal the number at the precision written keeps the number a flag.
- E-D1. The guard: at least two words must remain after the qualifier (D1-3). This narrows your examples in the way Part 0 item 2 describes. Alternative: no guard.
- E-D2. Matching rule for the qualifier: leading position only, one qualifier at a time, whole words, case-insensitive; the new alias is added beside the full label.
- E-D3. The new alias is shared like any other alias; collisions are left to the existing rules.

## PRINCIPAL DECISIONS AT THE GATE
*Recorded from the Principal's message of 2026-11-13 21:38. The Principal confirms them by signing below.*

1. **Option A (collapse duplicates):** ☑ approve  ☐ do not approve  ☐ approve with changes: ______
2. **Option D1 (leading qualifiers):** ☑ approve  ☐ do not approve  ☐ approve with changes: ______
3. **The guard on D1 (E-D1):** ☑ at least two words must remain (recommended)  ☐ no guard (the aliases "Variance" and "Opex" appear in the Q4 prompt)  ☐ other: ______
4. **The qualifier list:** ☑ "Company-wide" and "Total" only (as written)  ☐ add these words: ______
5. **Build arrangement:** ☑ one Builder task for Addendum 1 and Addendum 2, with separate evidence for each (recommended)  ☐ two tasks, Addendum 1 first
6. **Other Category E rows (E-A1, E-A2, E-D2, E-D3):** ☑ approved as built-to  ☐ changes: ______
7. **The Line Naming Rule (R1 and R2) as stated in N-0:** ☑ confirmed as the working definition for now (message of 2026-11-13 21:38)  ☐ changes: ______

## EXPLICIT EXCLUSIONS
As in Scope Out. In particular: options B, C, D2 and D3; the prompt; Release 1 and Addendum 1 text; the Handbook; and any test sentence or expected result.

## MINIMUM-SCOPE VERIFICATION
Option A and Option D1 are independent; neither is needed for the other to work, and each can be approved alone. D1 can add collisions (a stripped alias equal to another alias); Option A and the existing rules handle them, so D1 needs no extra rule. The guard is the one place where my default is narrower than your wording, and it is a Gate decision for that reason.

## PRINCIPAL APPROVAL GATE
I confirm that:

☑ This addendum includes ALL requirements I have decided.
☑ This addendum includes NO product scope I did not authorize.
☑ The exclusions accurately represent my deferred/out-of-scope decisions.
☑ The Architect has not silently narrowed my authorized scope.
☑ The Architect has not silently expanded my authorized scope.
☑ Architect recommendations are clearly separated from mandatory scope.
☑ I understand that the Builder implements ONLY the authorized scope in this addendum.
☑ If the addendum is incomplete, I will request clarification before issuing it.

**Approved by Principal:** Principal, by written instruction of 2026-11-13 21:44 ("I have read all eight confirmations, I approve Addendum 2 revision 2, and I authorise you to enter my name and today's date, 13 November 2026, on the signature line"); the line was entered by the Project Advisor at that instruction, not typed by the Principal.   **Date:** 2026-11-13

## ARCHITECT ATTESTATION
I confirm:
☑ I read the Release 1 code (`parse_data_block`, `_name_occurrences`, `check_numbers` and the result classes), the Q4 FY2026 fixture, the signed Brief WP3, Addendum 1 on `main`, and the Handbook on `main` (v2.31).
☑ I identified canonical state (`8cb1dca`; Release 1 not yet on `main`).
☑ I classified all material scope.
☑ I applied the Required Response Format and the Minimum-Scope Test.
☑ I did not bundle scope: options B, C and D2/D3 are excluded and listed.
☑ I did not use technical preference as product authority. Every default that is narrower or different from the Principal's wording is Category E and a Gate decision.
☑ I did not silently narrow or expand Principal scope; the one narrowing (the guard) is in Part 0 item 2 and Gate decision 3.
☑ I wrote no test sentence and no expected result.
☑ Revision 2: I made the three changes the Principal asked for and no other (checked by comparing the file with draft 1), and recorded Gate decisions 1 to 7 as he stated them. I did not tick the Principal Approval Gate boxes or sign.
☑ I did not run any new code for this addendum; the label facts come from reading the Q4 fixture with the Release 1 parser.

**Architect:** Claude (Architect)   **Date:** 2026-11-13

## RELEASE RULE
Release to the Builder is the Principal's act: the addendum is released when the Principal signs it, makes the signed file canonical on `main` and sends it. The Architect's attestation does not substitute. The Architect has not committed or pushed anything.
