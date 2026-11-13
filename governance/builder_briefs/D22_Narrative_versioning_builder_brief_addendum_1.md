# D22 Number Check Amendment: Builder Brief Addendum 1 (REVISION 5, SIGNED BY THE PRINCIPAL 2026-11-13, NOT YET CANONICAL)

**Revision 5 (2026-11-13, after the Principal's Gate decisions of 10:45).** Two changes, nothing else. (1) B-1 now defines "resolved" as "matched, including by pick" (the Principal's optional request). (2) The ten Gate decisions below are recorded as the Principal stated them in his message of 2026-11-13 10:45; the Principal Approval Gate boxes and the signature are left for the Principal.

**Revision 4 (2026-11-12, after the Principal's requests of 16:29).** Three changes, nothing else. (1) The new Flag field is no longer called `kind`: Release 1's `Flag.kind` already holds the number's kind (dollar, percent, count). The new field is `flag_class`; the word "kind" is now used only for the number's kind. I also checked every other name in this addendum against the Release 1 code and found one more clash, in meaning: B-5 and B-6 said "a new reason in plain words", but Release 1's `Flag.reason` is an internal diagnosis constant, and display text is the UI's job. B-5 and B-6 now name two new reason constants and the data the flag carries (B-7a). (2) The title said revision 2; it now says revision 4. (3) A-5b now has a Gate box, Gate decision 10.

**Revision 3 (2026-11-12, after the Principal's two requests of 14:43).** Changes against revision 2: (1) the budget words are now defined in one place only, A-2; every other mention (Part 1 section 1, Category B-2, Part 0, E-1, B-2/B-3) refers to A-2 and does not repeat the words, so the Builder reads one list; (2) a new false-flag class, budget misses described without a budget word, is listed in A-4 and B-8 with the wordings it covers; (3) a new Category E option E-9 and Gate decision 8, for "Major Miss" and "Watch" as budget words, with the cost of each word; (4) one clarification I found while checking the Release 1 code, A-5b, so that the false flags in A-4 can be cleared by a pick (Category D-5, Part 0 item 3). Nothing else changes. Release 1 stays as it is.

**Revision 2 (2026-11-12, after the Principal's three proposals of 12:25).** Changes against revision 1: A-2 (budget words, and the span of the budget-word test), A-4 (known false flags), B-2, B-3 and B-8 (words below, above, under, over), the acceptance illustrations, and Part 3 (Category E rows E-1, E-7, E-8 and Gate decisions 5 and 6). Everything else is as in revision 1. Your three points are proposals, so each is built in as the Architect's recommended default and marked Category E, with the alternative stated, for your decision at the Gate.

**STATUS: SIGNED by the Principal on 2026-11-13 (Part 3); NOT YET CANONICAL.** No Builder may start from this text. It becomes a Builder instruction only when the Principal makes the signed file canonical on `main`, and the Builder still waits for Release 1 to be on `main` (Gate decision 4).
**Addendum ID:** `d22_narrative_versioning_builder_brief_addendum_1` (proposed path: `governance/builder_briefs/D22_Narrative_versioning_builder_brief_addendum_1.md`; the Principal may override).
**Amends:** WP3 of the signed Brief `governance/builder_briefs/D22_Narrative_versioning_builder_brief.md` (committed `f517ce1`). Nothing else in that Brief changes.
**Authority for scope:** the Principal's written messages of 2026-11-12 (06:45 wishes; 10:17 answers). Letters such as "observation (ad)" refer to `governance/architect_reports/d22_architect_observations_a_to_ag.md`.
**Handbook:** not updated and not asked to be. Recording these decisions waits for the Principal's request.

---

# PART 0: WHAT THE PRINCIPAL MUST LOOK AT FIRST

1. **Build base.** The Builder cannot start until (a) Release 1 is on canonical `main` (after Independent Test's calibration and the Principal's acceptance and push) and (b) this addendum is signed and on `main`. Release 1 is today only on the Builder's local branch (`cd5731c`, unpushed). The amendment edits that file, and a Test Codespace or patch is not canonical. Gate decision 4.
2. **Two parts, separately approvable.** Part A (budget lines) and Part B (direction) are independent. Each has its own Gate decision and can be built, tested and released alone. Part A is small. Part B is larger. Gate decisions 1 and 2.
3. **Defaults the Architect added (Category E, for your review).** You decided the rules in your 10:17 message. The following are details I filled in, each listed again in Part 3:
   - the budget words: one list, in A-2 only. "Planned" and "plans" are left out with the risk stated (E-1, Gate decision 6); the status words "Major Miss" and "Watch" are an option with the cost of each word (E-9, Gate decision 8);
   - how a writer clears a Part A false flag: a pick may name a Budget line, whatever the pool (A-5b, Category D-5, Gate decision 10, so you can approve or reject it). I found this in the Release 1 code: the pick test uses the same figure list as the automatic match, so without A-5b a Budget line could not be picked;
   - the span of the budget-word test: the number's own sentence, plus the previous sentence when the name has to come from there (E-7);
   - "below", "above", "under" and "over" are added as words after a number, but only when a budget word follows them directly (E-8, Gate decision 5);
   - the exact direction words (E-2);
   - the filler words allowed between a direction word and its number, such as "by" and "about" (E-3);
   - a negation before a direction word means the word is not checked (E-4);
   - a word before and a word after a number that disagree make a flag (E-5);
   - a line with several equal figures of different sign counts as agreeing if any agrees (E-6);
   - "more" and "less" after a number are not on the list (E-2).
4. **Two corrections to my 06:45 scoping message.**
   - I said an explicit sign plus a word would be flagged only if they disagree. Following your wording ("an unsigned number with a direction word"), a number with an explicit sign is NOT direction-checked. R3 still applies to it.
   - You said Part A makes "Revenue up 7%" flagged. In the Q4 FY2026 data that is true only because P&L revenue is +6.4% and no actual figure equals 7%. Part A alone does not catch "Revenue up 7% against budget": that sentence has a budget word, matches the Budget line's −6.5% by magnitude and passes. Part B catches it.
5. **Release 2.** Recommendation: wait for this amendment (Part 1, section 11). Gate decision 3.
6. **What this addendum does not do.** It does not change Release 1 as delivered or any screen, and it does not touch `rollups.py` or the Handbook. It adds no separation by heading outside Budget vs Actual, no per-number rule for mixed sentences, and no runtime warning if the heading changes (the heading is pinned by a test only).

---

# PART 1: REQUIRED RESPONSE FORMAT (Architect analysis)

**Repository identification.** `origin/main` = `79aad58` (2026-11-12 05:58, Handbook-only), on `1d7f3ae` (2026-11-12 05:28, tooltip change, dashboard file only). Release 1 (`cd5731c`, base `f517ce1`) is not on `main`. Release 1 files were reviewed from the Builder's pack. The Budget heading was read in `rollups.py` (lines 1578 to 1583 and 1652 to 1654 on `main`).

## 1. REQUIREMENT
- **A.** Lines in the Budget vs Actual section are kept apart from actual lines that share a name. A number is checked against Budget lines only when its sentence (or, under A-2b, the previous sentence) contains a budget word as defined in A-2; otherwise against actual lines only.
- **B.** An unsigned number with a direction word attached is checked against the sign of the printed figure on the line it matches, and flagged when they disagree.

## 2. EXISTING AUTHORITY
D22-D (2), D22-F (1) and D22-G (B1) (line-level matching on the nearest name; no fall-back; Option 4 pick), WP3-3, and accepted known misses (i) to (iii). R3 (an unsigned figure matches on magnitude) is a Builder reading, not authority. Neither the Handbook nor the Brief states it.

## 3. CLASSIFICATION
Both A and B are new Principal decisions (Category B). Details in Part 3.

## 4. SUPERSEDED / DEFERRED DECISIONS
- **Heading-based separation** was undecided in D22-E to D22-H (not considered in observation (ad)). It is now decided for one section only.
- **Known miss (ii)** (a wrong number that is right for the line named) is narrowed by Part B: it no longer passes when a direction word on an unsigned number contradicts the printed sign.
- **R3** stays for sentences with no direction word.

## 5. GENUINE CONFLICTS
None found. D22-H (13) (freeze) is not a veto: the Principal is changing his own decision, which needs this addendum and its Gate.

## 6. GOVERNANCE CHANGES REQUIRED
Handbook: record the decisions, the new known misses and R3's status. Only when the Principal asks.

## 7. ARCHITECTURE IMPACT
One pure function (`narrative_number_check.py`). No screen, no store, no prompt change. New Flag fields `flag_class`, `direction_word` and `direction`, two new reason constants, and a separate acceptance for direction flags (Part B-7 and B-7a), because Release 2's store keeps acceptances. Release 1's `Flag.kind` (the number's kind) is not changed.

## 8. IMPLEMENTATION IMPACT (Architect estimate; the Builder sizes it)
- **A:** small. One section recognizer, one candidate filter, one pinned test.
- **B:** larger. A fixed word list, an attachment rule, a negation rule, two new reason constants and a flag class, and many tests.

## 9. TESTING IMPACT
- Independent Test writes the direction and budget cases (Sets A and B). The Architect and the Builder do not.
- Independent Test calibrates Release 1 first, as the baseline.
- The Builder's own tests include the heading pin (A-6) and regression cases for Release 1 behaviour.

## 10. DEPENDENCIES AND BLOCKING
- Release 1 on `main`.
- The signed addendum on `main`.
- Part B-7's acceptance key must be fixed before Release 2 builds the store.

## 11. SEQUENCING RECOMMENDATION
Release 1 accepted and on `main`, then this amendment (A and/or B), then Release 2. Reasons: Release 2 stores acceptances (key shape), shows flags (two new reasons and new data on a flag) and counts open flags (a new flag class). Building Release 2 first would mean reworking its store afterwards. You lean the same way.

## 12. READY FOR BUILDER BRIEF?
**YES, for the scope in Part 2, subject to the Principal's review and signature.** Not startable until Part 0 item 1 is met.

---

# PART 2: BUILDER BRIEF (ADDENDUM)

## Objective
Amend the Release 1 number check (WP3) so that (A) Budget lines and actual lines sharing a name are separated, and (B) an unsigned number with a direction word is checked against the printed sign. The function stays pure. No screen is built or changed.

## Part A: Budget lines

**A-1. Budget section.** Lines under the heading line that begins `Budget vs Actual — flagged items only`, down to the line that begins `(Flag thresholds`, are **Budget lines**. Every other line is an **actual line**, exactly as in Release 1. When the section holds only `(none flagged Watch or Major Miss this period)`, there are no Budget lines and no error.

**A-2. Budget words (E-1, E-9).** **This is the only list of budget words in this addendum.** Every other mention of "a budget word" means this list.
- **Words:** the whole words "budget", "budgets", "budgeted" and "plan", case-insensitive.
- **Status words (E-9, recommended default included; Gate decision 8):** "Major Miss" (two words, in that order) and "Watch", matched case-sensitively with exactly that capitalization, as printed in the Budget section. If Gate decision 8 says not to include them, this bullet is removed and nothing else changes.
- **Not budget words:** "variance" (decided); "planned" and "plans" (E-1, Gate decision 6).
- **Where it applies:** in A-2b and A-3 (which lines a number is checked against) and in the B-2 tie for "below", "above", "under" and "over" (E-8). The status words also count in that tie; "over Watch" is not natural wording, so this has no effect in practice.
- Words are found with the same tokenizer as the name matching. The Builder confirms with tests that "budget's" and "over-budget" count (the tokenizer reads letters and digits, so apostrophes and hyphens split words).

**A-2b. Span of the budget-word test (E-7).** The test covers the same sentences the name search uses (`_nearest_preceding_name`: the part of the number's sentence before the number, else the previous sentence):
- the number's own whole sentence, before and after the number ("Revenue fell 6.5% below budget" counts); and
- the previous sentence as well, only when the own sentence holds no line name before the number, because the name then comes from the previous sentence. "Line name" for this condition means any line name, Budget or actual, so the test cannot depend on its own result.
- Example: "Revenue missed budget. It was 6.5% short." The second sentence has no name before the number, so the previous sentence is included, a budget word is found, the number is checked against Budget lines, and "Revenue" (previous sentence) names the Budget line. It matches.
- Example: "Revenue missed budget. APAC grew 12%." The second sentence has its own name, so only that sentence is tested: no budget word, actual lines only.
- Alternative (Gate decision, E-7): the own sentence only, as in revision 1, with the first example listed as a known false flag.

**A-3. Which lines a number is checked against.**
- **A budget word is in the number's sentence:** only Budget lines are candidates, for the figure and for the name (nearest-name resolution). All figures on a Budget line count, including its Actual $ figure.
- **No budget word:** Budget lines are neither candidates nor names. Only actual lines are used, as in Release 1.
- Everything else in WP3-3 is unchanged: nearest preceding name, exactly one matching line, no fall-back to any printed figure.

**A-4. Mixed sentences and known false flags.** A sentence that mixes actual and budget numbers is checked as a whole under A-3. The resulting false flag is accepted (Principal, 2026-11-12). No per-number rule. Also listed as known false flags under the span in A-2b:
- a budget sentence followed by a sentence with no name of its own that carries actual figures: "Revenue missed budget. It grew 6.4% on the year." The previous sentence is included, so the 6.4% is checked against Budget lines and flagged;
- a budget word used in another sense, such as "plan" in "following the plan, R&D grew 5%": the sentence goes to Budget lines and its actual numbers are flagged (the same risk applies to "plan" in any sentence, and to "Watch" if included, for example a sentence that starts "Watch headcount: …");
- **new class (revision 3): a budget miss described without a budget word.** The narrative's instruction 5 is "Budget Variance Flags", so such sentences are expected. Release 1 passes them, because the Budget line is a candidate for every "Revenue". Under Part A the sentence has no budget word, so the number is checked against actual lines only and a correct number is flagged ("no close figure equals this number"). This is a false flag, not a miss, and it is a change from Release 1 (a sentence that passed there now flags). Wordings it covers:
  - **status wording:** "Revenue flagged Watch at −6.5%", "a Major Miss", "recurring Watch". If E-9 includes the status words, these leave the class;
  - **other names for the budget:** "6.5% short of target", "target", "forecast", "guidance", "goal", "expectation", "missed our number". No option in this addendum covers them, and none is proposed;
  - **shortfall wordings** that rely on one of those: "a 6.5% shortfall against target". "Short of" and "shortfall" alone are not budget words;
  - **a name sentence without a budget word followed by a number sentence without one:** "Revenue missed. It was 6.5% short." (A-2b finds no budget word in either sentence);
  - **"variance" alone:** "Revenue's variance was −6.5%" (excluded as decided; "budget variance" contains "budget" and is covered).
  
  Every flag in this class can be cleared by the writer: pick the Budget line (A-5b) or edit the sentence to say "budget".

**A-5. Acceptances.** Key unchanged: (number as written, line). A Budget line is a different line from the actual line of the same name.

**A-5b. Picks and candidate lines (Category D-5).** The pool filter of A-3 applies to the automatic match only. A writer's pick (Option 4) is checked against the picked line's own figures, whichever pool it is in, and the flag's `candidate_lines` and `lines_of_kind` list Budget lines and actual lines alike. Reason: in Release 1, `check_numbers` clears a pick only if the picked line is among the lines whose figures equal the number (`equal_ids`, computed over all lines). If A-3 filtered that list, a Budget line could not be picked, and the A-4 false flags could not be cleared by a pick.

**A-6. Heading pin (Category D).** Tests that fail if the heading changes:
- (a) read `rollups.py` source and assert the heading literal is present and equals the constant the parser uses;
- (b) on the Q4 FY2026 fixture, exactly one Budget line is recognized (Revenue, Budget $4,294,336, Actual $4,016,906, Variance −6.5%);
- (c) a block without the heading has no Budget lines and behaves as Release 1 (regression);
- (d) the "(none flagged…)" line yields no Budget lines and no error.

There is no runtime warning if the heading changes. Separation silently stops and the Budget line behaves as a shared name, as in Release 1. Only the test protects against that.

## Part B: Direction

**B-1. When it applies.** To a written number that has **no explicit sign**, after it has matched exactly one line under WP3-3 (including after the writer picks a line, when the check re-runs). Numbers that are already flagged are not direction-checked until resolved. **"Resolved" means matched, including by a pick** (A-5b): a number that was flagged for another reason, and then matched because the writer picked a line, is direction-checked at that point. A flag that is only accepted ("Keep my number") is not a match, so its number is not direction-checked. Explicit-sign numbers stay with R3 only.

**B-2. Fixed word list** (Principal approved a fixed list, 2026-11-12; the specific words are an Architect proposal, E-2, for review at the Gate).
- *Upward:* up, rose, risen, grew, grown, increased, climbed, gained, jumped, surged, expanded.
- *Downward:* down, fell, fallen, dropped, declined, decreased, slipped, dipped, shrank, shrunk, contracted, reduced.
- *After a number:* higher, lower, up, down.
- *After a number, only with a budget word (E-8):* below, under (downward); above, over (upward). The word must be followed directly by a budget word (A-2), optionally after "the", "its" or "our": "6.5% below budget", "5% over the budget", "3% under plan". Without a following budget word these four words are not direction words. Reason: "below budget" and "above plan" are budget wordings; "over the year" and "over last quarter" are not.
- Sign convention checked: in `rollups.py` the Budget variance is Actual minus Budget, divided by Budget, for every line item. A negative printed variance means actual below budget, and a positive one means above, for revenue and expenses alike. So below/under = downward and above/over = upward match the printed sign, and the check follows the sign, not favourability.
- Not on the list: "more", "less", "improved", "worsened", "favourable", "unfavourable", "short of", "behind", "ahead of".

**B-2a. Risk of each added word** (for the Gate; Category E-8). "Tied" means followed directly by a budget word, the recommended default.

| Word | Direction | False-flag risk if added with no condition | Risk when tied to a budget word |
|---|---|---|---|
| below | down | Low to medium. Compared with something other than budget ("5% below the prior quarter", "below the 4% threshold") and checked against the wrong sign. | Low |
| above | up | Low to medium. Same as "below". | Low |
| under | down | Medium. Also means "under review" or "less than"; a comparison with something else. | Low |
| over | up | **High.** It is also a period word: "fell 5% over the year" reads as up, disagrees with "fell", and B-6 flags a correct sentence. | Low |

Cost of the tied default: "6.5% below the prior year" and "5% over last quarter" are not checked, and "6.5% below original budget" is not checked unless "original" or "approved" is added as an allowed word (not proposed).

**B-3. Attachment.**
- *Before the number:* the word, optional fillers (by, about, around, roughly, approximately, nearly, almost, just, some), then the number. No punctuation or other word between.
- *After the number:* the number with its unit, then the word directly ("7% higher", "5% lower", "7% up").
- A word followed (after fillers) by "to" or "from" describes a level and is not attached to any number (Principal, 2026-11-12).
- Words in the sentence that are not attached are ignored.

**B-4. Negation (E-4).** A negation (not, no, never, n't forms, without) within three words before the direction word, in the same sentence, means the word is not checked.

**B-5. Verdict.** The attached word gives a direction (up = +, down = −). If every printed figure on the matched line that equals the number at the precision written has the opposite sign, the number is a **hard flag** with the reason constant `REASON_DIRECTION` and the class "direction" (B-7, B-7a). The flag carries the direction word, its direction and the line, so the screen can say what the text says and what the line shows. A printed zero is not checked. If equal figures on the line differ in sign, the number agrees if any agrees (E-6).

**B-6. Two words (E-5).** If a word before and a word after the same number are both attached and disagree, the number is a hard flag with its own reason constant, `REASON_DIRECTION_WORDS_DISAGREE` ("the two direction words disagree"), and the class "direction" (B-7).

**B-7. Acceptance (Category D).** A direction flag belongs to a new **flag class**, "direction". Every other flag belongs to the class "number" (the Release 1 flags). Release 1's `Flag.kind` is unchanged: it still holds the number's kind (dollar, percent or count), and nothing in this addendum uses "kind" for anything else.
- **New field:** `Flag.flag_class`, with the values "number" (default) and "direction". `Acceptance` gets the same field, default "number".
- **Acceptance key:** a flag of the class "number" keeps the Release 1 key, (number as written, line). A flag of the class "direction" has the key (number as written, line, "direction"). Release 1's `Flag.acceptance_key` and `Acceptance.key` keep returning the pair for the class "number" and return the triple for the class "direction". Release 1 behaviour and tests are unchanged.
- **Effect:** accepting an ordinary flag for the same number and line does not accept the direction flag. Without this, a pick or accept on an ambiguity flag would silently accept a direction mismatch. Release 2 can count and display the two classes separately.

**B-7a. What a direction flag carries (names checked against Release 1).** Release 1's `Flag.reason` is an internal diagnosis constant ("never shown as a tier"), and display text is the UI's job, so a direction flag carries data, not sentences.
- **New constants:** `REASON_DIRECTION` ("the direction word disagrees with the sign printed on the line") and `REASON_DIRECTION_WORDS_DISAGREE` (B-6). They sit beside the existing `REASON_NO_NAME`, `REASON_AMBIGUOUS`, `REASON_NAME_DOES_NOT_CARRY_IT`, `REASON_NO_EQUAL_FIGURE` and `REASON_PICK_MISMATCH`.
- **New fields:** `Flag.direction_word` (the word as written, or None) and `Flag.direction` ("up" or "down", or None). The line and its printed sign are already carried by `Flag.line`. The plain-words text (what the text says, what the line shows) is built by the screen in Release 2.
- **Unchanged and used with their Release 1 meanings:** `Flag.kind`, `kind_words`, `candidate_lines`, `lines_of_kind` (the second is "every line carrying a figure of the kind", the number's kind), `placed`, `CheckedNumber.status`.

**B-8. What it will still miss (openly listed; Principal, 2026-11-12).**
- Words not on the list.
- Noun forms: "an increase of 7%", "growth of 7%", "a decline of 5%", "a 6.5% shortfall".
- "7% more", "5% less".
- Levels described with "to" or "from" ("fell to $3.9M", "up from 5%").
- Explicit-sign numbers ("down −5%"): R3 only.
- Negations outside B-4's pattern, hedges ("flat", "up or down").
- "Below", "above", "under" and "over" when no budget word follows them: "6.5% below the prior year", "5% over the year".
- "Short of", "behind", "ahead of", "shortfall".
- Words between a direction word and its budget word beyond "the", "its" and "our" ("below original budget").
- A word that attaches to the wrong number in a crowded sentence.
- Units glued to letters ("120bps"), as in Release 1.
- Favourable or unfavourable wording.
- Direction of a prior or budget figure in a mixed sentence beyond what A-3 does.

**Possible false flags (accepted by the Principal: extra flags over a missed error):** a correct level written with a direction word and no "to" ("margin fell 33%" read as a change); a negation not caught by B-4; a mixed actual-and-budget sentence (A-4); and the revision 3 class in A-4: a budget miss written without a budget word ("Revenue flagged Watch at −6.5%" if the status words are not included; "6.5% short of target"; "a Major Miss"; "a 6.5% shortfall against target"; "Revenue missed. It was 6.5% short."). Such a number is flagged by Part A first, so Part B's direction check does not reach it until the flag is cleared by a pick (A-5b) or the sentence is edited.

## Scope Out
Any change to Release 1 as delivered, to screens, `Northwind_Financial_Dashboard.py`, `rollups.py` (the prompt), the snapshot module, the store, the Handbook; separation by heading elsewhere (regions, departments); per-number budget rules; a runtime heading warning; noun forms; reading "variance" as a budget word.

## Files that may and may not change
**May:** `narrative_number_check.py` (the Release 1 version on `main`); its tests; new test files; the fixture (additions only). **May not:** everything else.

## Acceptance criteria (illustrations, derived by reading the data and not run; Independent Test writes the actual cases)
- "Revenue was $4.0M." has one candidate (the P&L line) and matches.
- "Revenue was up 7%." (no budget word) is checked against actual lines only; no line carries 7% for Revenue; hard flag.
- "Revenue was up 6.5% against budget." matches the Budget line; Part B flags: text up, line −6.5%.
- "Revenue missed budget by 6.5%." matches the Budget line; no direction word; passes.
- "Revenue missed budget. It was 6.5% short." matches the Budget line (A-2b); passes.
- "Revenue was 6.5% below budget." matches the Budget line; below = down, printed −6.5%; passes.
- "Revenue was 6.5% above budget." matches the Budget line; above = up, printed −6.5%; Part B flags.
- "Revenue came in below the budgeted $4.3M." has a budget word, so it is checked against the Budget line, whose Budget figure $4,294,336 equals $4.3M; passes.
- "Revenue fell 6% over the year." "over" has no budget word after it, so it is not a direction word; only "fell" is checked, and the flag is the one in the "Revenue fell 6%" case above.
- "Revenue missed budget. APAC grew 12%." the second sentence has its own name and no budget word; actual lines only.
- "Revenue flagged Watch at −6.5%." If the status words are included (E-9): a budget word is found, the Budget line matches and the explicit sign agrees; passes. If not: actual lines only; flagged as "no close figure equals this number" (the A-4 class); cleared by picking the Budget line.
- "Revenue came in 6.5% short of target." No option covers "target": checked against actual lines only; flagged (the A-4 class); cleared by picking the Budget line.
- A pick of the Budget line for the flagged "6.5%" in either case above is accepted (A-5b): the pick test uses the picked line's own figures.
- "Revenue fell 6%." matches the P&L line (+6.4% to 6%); Part B flags: text down, line +.
- "Revenue fell to $3.9M." is not direction-checked.
- Release 1 behaviour is unchanged for sentences with no budget word and no direction word.

## Required evidence
Builder: test results including the heading pin and Release 1 regression, reproduced by the Architect. Independent Test: direction and budget cases (Sets A and B) run against the function as built. Builder narration is not evidence. Not canonical until the Principal makes it so.

## Stop-and-report rule
If the Builder finds that a requirement here cannot be built as written or contradicts Release 1, it stops and reports. It does not decide.

---

# PART 3: SCOPE AUTHORIZATION GATE (PRINCIPAL SIGN-OFF REQUIRED)

**Status:** ☑ READY FOR PRINCIPAL APPROVAL  ☐ BLOCKED  ☐ AWAITING PRINCIPAL DECISION

## CATEGORY A: ALREADY AUTHORIZED
Line-level matching on the nearest name, no fall-back, Option 4 pick, hard flags (D22-D (2), D22-F (1), D22-G (B1), WP3-3). Accepted known misses (i) to (iii).

## CATEGORY B: NEW PRINCIPAL DECISIONS (2026-11-12, 06:45 and 10:17)
- B-1. Budget lines separated from actual lines, Budget vs Actual section only.
- B-2. Which words count as budget words: the single list in A-2. Decided by the Principal in steps (10:17: a fixed short list, "variance" excluded; 12:25: proposals on more words, built in as E-1 and E-9). The Builder reads A-2 only.
- B-3. An actual figure on a Budget line counts only with a budget word in the sentence.
- B-4. Mixed sentences: the false flag is accepted. The revision 3 class (A-4, B-8: a budget miss written without a budget word) is listed as a known false flag; signing the addendum accepts it, except for the wordings that Gate decision 8 removes.
- B-5. Direction: unsigned number plus direction word, checked against the printed sign, flagged on disagreement; a fixed list, including words after the number.
- B-6. "to" or "from" after a direction word means a level, not checked.
- B-7. The list of what Part B will still miss (B-8).
- B-8. A test pins the heading.

## CATEGORY C: GENUINE CONFLICTS
None.

## CATEGORY D: TECHNICAL / PROCEDURAL
- D-1. Build base is canonical `main` with Release 1.
- D-2. Direction flags have their own class, acceptance and key; Flag gets the fields `flag_class`, `direction_word` and `direction` (B-7, B-7a). `Flag.kind` is unchanged.
- D-3. The heading pin is test-only.
- D-4. Independent Test authors the cases.
- D-5. A pick is checked against all lines and the candidate lists include Budget lines (A-5b), so every Part A false flag can be cleared by a pick. Without it the false flags in A-4 could not be cleared that way.

## CATEGORY E: ARCHITECT RECOMMENDATIONS (separate from mandatory scope; the Principal may change each)
- E-1. The list of budget words is in A-2 and nowhere else. This row covers two choices on it: "budgets" and "budgeted" are included (on the Principal's proposal); "planned" and "plans" are NOT included. Risk of adding them: "plans" is often a verb ("the company plans to hire") and "planned" an adjective ("planned hiring", "planned maintenance"), so a sentence about actual figures goes to Budget lines and its actual numbers are flagged. "Plan" already carries this risk for the noun ("following the plan"). "Budgeted" and "budgets" carry little: a sentence that says "budgeted" or "budgets" is about budget. If you want "planned" and "plans" in, tell me: it is a one-line change, and the cost is more false flags on prose about plans.
- E-2. The word list in B-2, and "more"/"less" excluded.
- E-3. The fillers in B-3.
- E-4. Negation rule.
- E-5. Two disagreeing words make a flag.
- E-6. Mixed-sign equal figures: agrees if any agrees.
- E-7. Span of the budget-word test (A-2b): the number's own sentence, plus the previous sentence when the name must come from there. Alternative: the own sentence only, with "Revenue missed budget. It was 6.5% short." listed as a known false flag. The recommended span adds one known false flag of its own (A-4: a budget sentence followed by a nameless sentence about actual figures), so each choice has a false flag; the recommended one fits the existing name rule and covers your example.
- E-9. The budget-section status words "Major Miss" and "Watch" as budget words (A-2). **Benefit:** the narrative's instruction 5 is "Budget Variance Flags" and its text speaks of "each Major Miss" and "any Watch item", so these words are expected in budget sentences ("Revenue flagged Watch at −6.5%"); with them included those sentences are checked against the Budget line and pass when correct. **Cost, per word:**
  - **"Major Miss":** low. It is a two-word phrase that ordinary prose rarely uses outside a budget context. Case-sensitive matching (as printed) removes "a major miss in cost control". Remaining cost: a capitalised "Major Miss" in a sentence about actual figures sends that sentence to Budget lines and flags its actual numbers.
  - **"Watch":** medium. Ordinary prose uses it ("one to watch", "watch closely", "watch list", "watchful"). Case-sensitive matching removes the lower-case uses; "watchful" is a different word. Remaining cost: a sentence that starts with "Watch" for another reason ("Watch headcount: G&A is 30."), or "Watch" capitalised in a heading or label, sends the sentence to Budget lines and flags its actual numbers. Without "Watch" the false flag in A-4 stays for "flagged Watch at −6.5%" unless the sentence also says "budget" or "plan".
  - **Both:** the false flags that remain are listed in A-4 (target, forecast, goal, "short of"). They are not covered by this option.
  - **Alternatives (Gate decision 8):** neither (A-4 lists the status wording as a false flag); "Major Miss" only; both, case-sensitive (**recommended**); either word case-insensitive (not recommended: "to watch" and "a major miss" would send ordinary sentences to Budget lines). "Variance" stays out, as decided.
  - **Recommended default:** both, case-sensitive, because the narrative's own instruction 5 invites these words. If you would rather keep Part A as small as possible, "neither" is a legitimate choice and only A-4 changes.
- E-8. "Below", "above", "under" and "over" added as words after a number, only when a budget word follows (B-2, risk table B-2a). Alternative: unconditional (not recommended: "over" is a period word and would flag "fell 5% over the year"), or only some of the four. Not proposed: "short of", "behind", "ahead of".

## PRINCIPAL DECISIONS AT THE GATE
*Recorded from the Principal's message of 2026-11-13 10:45. The Principal confirms them by signing below.*

1. **Part A (budget lines):** ☑ approve  ☐ do not approve  ☐ approve with changes: ______
2. **Part B (direction):** ☑ approve  ☐ do not approve  ☐ approve with changes: ______
3. **Release 2:** ☑ wait for the amendment (recommended)  ☐ run in parallel
4. **Build base:** ☑ after Release 1 is on `main` (recommended)  ☐ other: ______
5. **"Below", "above", "under", "over" (E-8):** ☑ only with a budget word following (recommended)  ☐ unconditional  ☐ only these: ______  ☐ not added
6. **"Planned" and "plans" as budget words (E-1):** ☑ not included (recommended)  ☐ included  ☐ one of them only: ______
7. **Span of the budget-word test (E-7):** ☑ own sentence plus the previous sentence when the name comes from there (recommended)  ☐ own sentence only
8. **Status words "Major Miss" and "Watch" as budget words (E-9):** ☑ both, case-sensitive (recommended)  ☐ "Major Miss" only  ☐ neither (A-4 then lists the status wording as a known false flag)  ☐ other: ______
9. **Other Category E rows (E-1 to E-6):** ☑ approved as built-to  ☐ changes: ______
10. **Picks and candidate lines (A-5b, D-5):** ☑ approve A-5b  ☐ do not approve A-5b. If not approved, the Part A false flags in A-4 cannot be cleared by picking the Budget line; they can be cleared only by editing the sentence to say "budget", or by an acceptance as Release 1 allows it (its acceptance key can carry no line). I have not checked how the Release 2 screen would offer that.

## EXPLICIT EXCLUSIONS
As in Scope Out. In particular: no change to Release 1 as delivered; no Handbook update.

## MINIMUM-SCOPE VERIFICATION
Part A and Part B are independent: neither is needed for the other to work. B-7 (a separate flag class with its own acceptance) is the one cross-dependency with Release 2, and it is needed because acceptance keys would otherwise let an ordinary acceptance hide a direction mismatch. The heading pin is the smallest protection that stops silent failure of A.

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

**Approved by Principal:** Principal, by written instruction of 2026-11-13 10:50 ("I have read all eight confirmations, I approve addendum revision 5, and I authorise you to enter my name and today's date, 13 November 2026, on the signature line"); the line was entered by the Project Advisor at that instruction, not typed by the Principal.   **Date:** 2026-11-13

## ARCHITECT ATTESTATION
I confirm:
☑ I read the relevant Handbook and Brief text, the Principal's messages of 2026-11-12 and the Release 1 files.
☑ I identified canonical state (`79aad58`; Release 1 not on `main`).
☑ I classified all material scope.
☑ I applied the Required Response Format.
☑ I applied the Minimum-Scope Test.
☑ I did not bundle scope without authorization; the two parts are separate.
☑ I did not use technical preference as product authority. The Category E defaults are marked for the Principal.
☑ I did not silently narrow or expand Principal scope. Two corrections to my earlier message are in Part 0 item 4.
☑ The acceptance-criteria illustrations were read from the data, not run.
☑ Revision 4: I read the Release 1 `Flag`, `Acceptance`, `CheckedNumber` and `NumberCheckResult` classes and every `REASON_` constant, and checked each name this addendum introduces (`flag_class`, `direction_word`, `direction`, `REASON_DIRECTION`, `REASON_DIRECTION_WORDS_DISAGREE`) against them: no clash. I searched the addendum for "kind": it now means the number's kind only.
☑ Revision 3: the budget words are defined once (A-2) and every other mention refers to it (checked by searching the file for each word); the new false-flag class is listed in A-4 and B-8; the status words are a Category E option (E-9). I read the Release 1 code to check how a pick is tested (`equal_ids` over all lines) and that the Unicode minus is read as a sign; the clarification A-5b and Category D-5 come from that reading. I did not run any example.
☑ Revision 2: the Principal's three proposals are built in as Category E defaults with the alternatives stated; none is a decision. I checked the sign convention of the Budget variance in `rollups.py` (Actual minus Budget over Budget, every line) and the name-search code in the Release 1 pack (own sentence before the number, else the previous sentence). I did not run any of the examples.

**Architect:** Claude (Architect)   **Date:** 2026-11-12

## RELEASE RULE
Release to the Builder is the Principal's act: the addendum is released when the Principal signs it, makes the signed file canonical on `main` and sends it. The Architect's attestation does not substitute. The Architect has not committed or pushed anything.
