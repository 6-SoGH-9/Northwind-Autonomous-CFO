# D22 — Addendum 3 (revision 3): list-numbering fix in the number check

**Status:** DRAFT by the Architect. **NOT SIGNED. NOT RELEASED.** The Builder must not start until the Principal signs the Gate at the end.
**Revision 3 (2026-11-22), after the Principal's answers:** the Project Advisor, not the Principal, is named as having checked Brief v3 WP3 (Category C and the attestation); B-1, B-2 and B-3 are left **unticked** for the Principal to tick at signing; the behaviour of lowercase "5m" and "5b" is stated from a probe (section 1); B-1a and the build base stay blank for the Principal.
**Revision 2 (2026-11-21), after the Principal's review with the Advisor:** B-1 widened from "percent" to "a unit: percent, or a K, M or B suffix"; a test for each unit; B-2 (residual miss accepted) and B-3 (own task) recorded as the Principal's decisions; one new question, B-1a, about other units; Architect attestation completed, with what I could not check stated.
**Canonical base:** `main` at `52bb5c5` (re-checked 2026-11-21: `origin/main` is still `52bb5c5`).
**Amends:** D22 Brief v3 WP3, as already amended by Addenda 1 and 2. Release 1 behaviour is changed only as described here.

## 1. The defect (Architect-reproduced on `52bb5c5`, 2026-11-19 and 2026-11-21)

`_is_list_numbering` in `narrative_number_check.py` drops a plain integer at the start of a line when it is followed by "." or ")" and then a space, tab, `*`, `_`, newline or the end of text. Its test for "plain integer" is that the digits have no "." and no ",". A unit does not stop it, so a figure with a unit counts as a plain integer. The same figure in the middle of a line is checked; so it is one defect, with a unit.

| Text (line-leading) | Scanned | Flags | Same figure mid-line |
|---|---|---|---|
| `"EMEA grew\n99%."` | none | 0 | flagged |
| `"EMEA grew\n5M."` | none | 0 | flagged |
| `"EMEA grew\n5K."`, `"…\n5B."` | none | 0 | flagged |
| `"* 99%. EMEA grew."` | none | 0 | flagged |
| `"EMEA grew\n5M)"` | none | 0 | not probed |
| `"3. EMEA grew."`, `"3) EMEA grew"`, `"12. Headcount rose."` | none | 0 | correct: list numbering |
| `"EMEA grew\n6.4%."`, `"EMEA grew\n5.5K."` | scanned | per DATA | decimals are not affected |
| `"EMEA grew\n$5M."` | scanned | per DATA | dollar figures are not affected |
| `"EMEA grew\n5 percent."`, `"…\n5 million."`, `"…\n5 pp."`, `"…\n5 dollars."` | scanned | per DATA | written with a word, not affected |

The Release 1 copy in `build_test/fixtures/` behaves identically on the percent and K/M/B cases (probe 2026-11-21), so this is a **Release 1 defect**, not caused by either addendum. Effect: a wrapped line that begins with a figure carrying a unit and a full stop (or ")") is never checked, so a wrong figure there raises no flag.

**Lowercase "m" and "b" (Architect probe on `52bb5c5`, 2026-11-22).** "5m" and "5b" are never scanned as numbers, at line start or mid-line, with or without a following full stop, because the scanner reads lowercase single-letter "m" and "b" as units only after a dollar sign (comment at `narrative_number_check.py` line 279; digits glued to other letters are skipped). Results: `"EMEA grew\n5m."`, `"EMEA grew\n5b."`, `"EMEA grew 5m."`, `"EMEA grew 5b."`, `"EMEA grew 5m in Q4"`, `"EMEA grew\n5m in Q4"`: scanned 0, flags 0. With a dollar sign (`"$5m."`, `"$5b."`), line-leading and mid-line: scanned and flagged per DATA. So lowercase "5m." and "5b." at line start are **not** dropped by the list-numbering rule; they are dropped by the existing unit rule, the same as mid-line. This fix does not change that and the fix is not expected to change any result for them. It is a separate behaviour, already outside this addendum's scope (section 6).

**Further forms with the same defect, found in the probe and not in the Principal's wording (see B-1a):** `"…\n5 %."`, `"…\n5k."`, `"…\n5MM."`, `"…\n5mm."`, `"…\n5bn."`, `"…\n5mn."`, `"…\n5x."`. Each is dropped at line start and flagged mid-line. 

## 2. What the Principal decided and what is still open (Category B)

**B-1 (stated in the Principal's message of 2026-11-21; to be ticked by the Principal at signing).** A token that carries a unit, meaning a percent, or a K, M or B suffix, is **not** list numbering. A bare integer is still list numbering. *(My earlier draft said "percent" only; the Principal widened it.)*

**B-1a (open — Principal to decide).** The scanner already reads other forms as units, and they have the same defect (section 1, last paragraph): "5 %", lowercase "5k", "MM"/"mm", "bn", "mn", and "x" ("2.3x"). If B-1 is read as only the literal words "percent, K, M, B", those stay dropped at line start and become residual known misses.
- *Architect recommendation (not scope until you tick it):* extend B-1 to every unit the scanner already recognises, because the minimum code is the same single condition ("the scanner read a unit on this token"), and listing letters one by one leaves a visible gap for no saving. The list is then the scanner's list, not a new list.
- Alternative: exactly your wording. Then the forms in section 1's last paragraph go into B-2's accepted misses.

**B-2 (stated 2026-11-21: as recommended; to be ticked at signing).** Residual known miss accepted: a **bare integer** at line start followed by "." or ")" (for example a wrapped line starting "12. Headcount…" where 12 is a figure) is still skipped as list numbering. If B-1a is "your wording only", the forms in B-1a are accepted residual misses too.

**B-3 (stated 2026-11-21: as recommended; to be ticked at signing).** This fix is its own task. It is not bundled with Release 2 or with anything else.

## 3. Mandatory scope (once the Principal signs)

1. In `narrative_number_check.py`, change the list-numbering rule so that a token carrying a unit (B-1, and B-1a if ticked) is not list numbering. A bare integer is still list numbering. No other behaviour is changed.
2. **A Builder test for each unit** the signed B-1 covers: at least percent ("99%."), K ("5K."), M ("5M.") and B ("5B."); and, if B-1a is ticked, one for each further form in section 1's last paragraph. Each test shows that the figure at line start is now scanned and gets exactly the result the same figure gets mid-line (flag or no flag, for a right and for a wrong value).
3. Tests that the following are unchanged: "3. …", "3) …", "12. …" (bare integer, still skipped); "6.4%" and "5.5K" at line start; "$5M" at line start; "5 percent" and "5 million" at line start; a figure in the middle of a line; dates, ordinals and years; lowercase "5m." and "5b." at line start (not scanned, as before).
4. Existing Release 1, Addendum 1 and Addendum 2 tests must still pass. If any must change, the Builder reports each by name and reason and does not change it silently.
5. Return Report in the form of the Addendum 1 and 2 reports, with evidence classes kept apart. The Builder's tests are Builder evidence only.

## 4. May / may not

**May touch:** `narrative_number_check.py`; `build_test/test_number_check.py`, `build_test/test_addendum1_number_check.py` and `build_test/test_addendum2_number_check.py` (only as in 3.4); new test files under `build_test/`.
**May not touch:** the two earlier-version copies in `build_test/fixtures/`; `narrative_snapshot.py`; the dashboard; the prompt; the Handbook; any Independent Test case or expected result; any other number-check behaviour (pools, collapse, qualifiers, direction, acceptance keys, the bare-year, ordinal and date rules, the lowercase "m"/"b" rule).

## 5. Verification

- **Independent Test** writes and owns the cases and records the expected results before the run, as under D22-G (B2), and shows them to the Principal. The Builder does not write them. The Architect may reproduce them but does not author them. **Independent Test's cases and expected results are not put in the repository; only its summary is.**
- The earlier Sets A, B and C and the Addendum 1 and 2 case sets are re-run unchanged. Any change in a result must be explained by this fix. Expected: the only changes are cases that begin a line with a unit-bearing integer and a full stop.
- False-flag levels are compared with the accepted levels (Set A 23 of 80; realistic narrative 10 of 87). A change is reported to the Principal, not absorbed.

## 6. Explicit exclusions

No Release 2 work. No change to options B, C, D2, D3 of Addendum 2. No change to the Line Naming Rule. No Handbook edit (the Handbook batch records the defect). No change to how lowercase "m" and "b" are read. No new known-miss class other than those named in B-2.

## 7. Minimum-scope verification
- Minimum implementation: one condition in one function (the unit test on the token). The scanner already computes the unit before the list rule runs, so no new parsing is needed (read in `_scan`, 2026-11-21).
- Claimed dependencies tested: none. The fix does not depend on Release 2.
- Workaround considered: editing sentences so no figure starts a line. It does not meet the purpose, because the check exists for text a person did not write carefully.
- No bundling: B-3.

---

# SCOPE AUTHORIZATION GATE — PRINCIPAL SIGN-OFF REQUIRED

**Brief Title:** D22 Addendum 3 (revision 2) — list-numbering fix
**Status:** ☑ AWAITING PRINCIPAL DECISION (ticks, B-1a and the build base)  ☐ READY FOR PRINCIPAL APPROVAL  ☐ BLOCKED

**Category A — already authorized:** the number check as a Release 1 function (D22 Brief v3 WP3, signed 2026-10-26); the behaviour of Addenda 1 and 2, which this does not change.
**Category B — new Principal decisions:** B-1, B-2, B-3 (stated 2026-11-21, to be ticked at signing); B-1a (open).
**Category C — genuine conflicts:** none found. The Project Advisor checked Brief v3 WP3 against the fix and found no contradiction (reported by the Principal, 2026-11-21); my own check is in the attestation.
**Category D — constraints:** only the Principal pushes to `main`; Independent Test owns the cases.
**Category E — Architect recommendations:** the B-1a extension. Not authorized until ticked.

## Principal decisions at the Gate
*B-1, B-2 and B-3 were stated in the Principal's message of 2026-11-21. They are left unticked: the Principal ticks them at signing.*

1. **B-1 (a token with a unit — percent, or a K, M or B suffix — is not list numbering; a bare integer still is):** ☑ approve  ☐ do not approve  ☐ approve with changes: ______
2. **B-1a (other units the scanner already reads: "5 %", "k", "MM"/"mm", "bn", "mn", "x"):** ☑ include (recommended)  ☐ not included, exactly the wording of B-1
3. **B-2 (residual bare-integer miss accepted):** ☑ accept  ☐ do not accept
4. **B-3 (own task):** ☑ own task (recommended)  ☐ bundle with: ______
5. **Build base:** ☑ `52bb5c5` (recommended)  ☐ other: ______ *(not stated in the Principal's message, so left blank)*

## Principal approval gate
I confirm that:
☑ This Brief includes ALL requirements I have decided.
☑ This Brief includes NO product scope I did not authorize.
☑ The exclusions accurately represent my deferred/out-of-scope decisions.
☑ The Architect has not silently narrowed my authorized scope.
☑ The Architect has not silently expanded my authorized scope.
☑ Architect recommendations are clearly separated from mandatory scope.
☑ I understand that Builder implements ONLY the authorized scope in this Brief.
☑ If the Brief is incomplete, I will request clarification before issuing it.

**Approved by Principal:** Principal, by written instruction of 2026-11-22 07:16 ("I read it and accept. Put my name on it"), given after the Gate decisions of the same morning; the line was entered by the Project Advisor at that instruction, not typed by the Principal.   **Date:** 2026-11-22

## Architect attestation (completed 2026-11-21)
I confirm the following, each with what it rests on:
☑ I reviewed the relevant Handbook and Decision Log, **for list numbering only.** I searched the Handbook for "list numbering" and read the two places that define it as "not a number for the check" (the D22-C (7) text and the D22 row summary). The fix keeps that rule. **I did not read the whole Decision Log again for this addendum.**
☑ I reviewed the canonical repository state: `origin/main` = `52bb5c5`; the function and the scanner read; the probes in section 1 run on `main` and on the Release 1 copy.
☑ I classified all material scope (section 2 and the Gate categories).
☑ I applied the Minimum-Scope Test (section 7).
☑ I did not bundle scope without authorization (B-3; B-1a is a separate, unticked decision).
☑ I did not use technical preference as product authority. B-1 is the Principal's wording; my extension is B-1a, marked as a recommendation.
☑ I did not silently narrow or expand Principal scope: B-1 is as the Principal widened it; the forms beyond it are listed, not included.
☑ I read Brief v3 WP3-1 to WP3-10 in full on 2026-11-21 and found no contradiction with the fix. WP3-1 says list numbering is not a number and that K, M, B and "million" are read as such (WP3-2); the fix keeps the first and is consistent with the second. WP3-5's known misses (i) to (iii) are not touched. The Project Advisor checked the same text independently (reported by the Principal, 2026-11-21); I have not seen the Advisor's own record.
☐ **I applied the Required Response Format in full: not done.** This is a short addendum. I used the Scope Authorization Gate and covered requirement, authority, classification, conflicts, testing impact, dependencies and sequencing in sections 1 to 7; I did not write the twelve numbered sections.
☐ **This Brief accurately represents the authorized scope:** I attest to this for B-1, B-2 and B-3 as stated in the Principal's message of 2026-11-21, which the Principal confirms by ticking them. B-1a and the build base are the Principal's and are blank.

**What I could not check:** I did not read the Builder's code for the fix (none exists yet). I did not probe every unit form with every kind of line prefix (for example "> 5M." or "** 5M."); the prefix rule is unchanged by this fix and the Builder's tests should cover the common prefixes.

**Architect:** Claude (Architect)  **Date:** 2026-11-21

*The Brief is NOT RELEASED until the Principal approves the Gate. The attestation does not substitute for that.*
