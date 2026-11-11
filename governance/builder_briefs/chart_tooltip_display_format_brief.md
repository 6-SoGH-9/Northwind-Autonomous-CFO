# Chart Tooltip Display Format: Builder Brief v2 (AMENDED, APPROVED BY THE PRINCIPAL, 2026-11-11)

**STATUS: APPROVED BY THE PRINCIPAL, 2026-11-11 11:26 (Europe/London), by his in-session message "I the principal autorized the V2", with the shared helper (Category E) authorized by his answer to the Architect's question in the same session. Released for the Builder. v2 supersedes v1, which was approved on 2026-11-11 05:46 but never sent to the Builder. The Project Advisor's review (2026-11-11 06:11) required the amendments marked [A1] to [A6]. The text below is what the Principal reviewed; the only changes since are the status, the Gate ticks, the attestation and the release rule.**

**Proposed ID / path:** `chart_tooltip_display_format_brief_v2` / `governance/builder_briefs/chart_tooltip_display_format_brief_v2.md` (the Principal commits it; no agent pushes). v1 is not committed and should not be.
**Canonical base:** `main` at `e85cdf4d9dcd0e4b8a2f7dd14d69bada68c8752f` (2026-10-27). The Builder re-checks `origin/main` before starting and reports any newer commit.
**Separate from D22.** Not part of D22; does not change D22's signed Brief; must not be bundled with D22 in any branch, commit or review.

## Change log, v1 to v2

| Mark | Change | Source |
|---|---|---|
| A1 | Helper contradiction resolved: allowed only if the Principal authorizes it in Gate Category E; otherwise no new function (sections 4, 5 and Category E now agree) | Advisor fix 1 |
| A2 | Acceptance criterion 2 reworded: plotted fields identical; a tooltip-only text field may be added | Advisor fix 2 |
| A3 | Missing values: tooltip shows blank, same as the table | Advisor gap 3 |
| A4 | Criterion 1 evidence: read the chart as sent to the screen, every point, all 11 charts | Advisor gap 4 |
| A5 | Rounding: text produced in Python by the table's own rules, for percent AND dollar; fixed test values added | Advisor gap 5, extended to dollars by the Architect |
| A6 | Altair note: already a Streamlit dependency, so using it needs no `requirements.txt` change | Advisor verification, re-checked by the Architect |

---

## 1. What the Principal decided

1. The hover tooltip on dashboard charts must be readable: currency symbol on dollar values, percent sign on percentages, no long decimals. (Principal request, 2026-11-10, relayed.)
2. **Format = exactly what the "Revenue detail" table shows** for `$` and `%` values (Principal, 2026-11-11 05:40).
3. **Hover tooltips only.** Axis labels unchanged (Principal, 2026-11-11 05:44, "no", confirmed by his approval of v1).
4. **Display only.** No number changes (Principal, 2026-11-10).
5. **Priority:** wanted before D22 is validated, to help the Principal check D22. D22 does not depend on this change and this change does not depend on D22 (Principal, 2026-11-11).

6. Confirmed by the Principal's approval of v2 (2026-11-11 11:26): half-point rounding in the hover, and blank for missing values (A3). The shared helper (A1) is authorized in Gate Category E.

## 2. Required behaviour

For every point of the 11 charts in section 3, the tooltip shows the same text the table helper produces for the same value:

| Value type | Rule (existing helper `_base_format_map`) | Example |
|---|---|---|
| Dollar | `${:,.0f}` (whole dollars, thousands separator) | `479546.84` shows `$479,547` |
| Percent (stored as a fraction) | `fmt_pct_half`: x 100, rounded to the nearest 0.5, one decimal, `%` | `0.7120461332` shows `71.0%` |

Half-point rounding is inherited from the table on purpose, so hover and table never disagree. It means a hover cannot show the finer percentage.

**[A3] Missing values.** The trend charts reindex to the full period list, so a period can have no value. The table shows blank for missing values (`na_rep=""`). The tooltip must show blank too, with no `$nan`, `nan%`, `NaN`, `None` or `$0` text. The sample dataset has no missing points at `e85cdf4` (every chart has its full grid), so Test needs a fixture with a missing period.

Unchanged: plotted values, series, colours, stacking, x-axis chronological order (`_chrono_index`), titles and captions, the tooltip labels the user sees (including Streamlit's `index`, `value`, `color`), axis labels and scales.

## 3. The 11 charts (call sites at `e85cdf4`)

| Tab | Chart | Line | Unit |
|---|---|---|---|
| Revenue Performance | Revenue by Region, full trend | 1121 | $ |
| Revenue Performance | Revenue by Product Line, full trend | 1129 | $ |
| Revenue Performance | Revenue Mix (%), by Region | 1139 | % |
| Revenue Performance | Revenue Mix (%), by Product Line | 1141 | % |
| Cost Structure | Expenses by Department, full trend | 1161 | $ |
| Cost Structure | Opex per Employee | 1249 | $ |
| Headcount & Efficiency | Revenue per Headcount | 1295 | $ |
| Regional Revenue & GTM Investment | Net of GTM Cost ($) | 3101 | $ |
| Regional Revenue & GTM Investment | Net of GTM Cost (%) trend | 3122 | % |
| Product Line Revenue & R&D Investment | Net of R&D Cost ($) | 3132 | $ |
| Product Line Revenue & R&D Investment | Net of R&D Cost (%) trend | 3161 | % |

Excluded: Headcount by Department (line 1260). Whole-number counts, no defect; its chart specification stays identical.

## 4. Constraints

- Streamlit's native `st.line_chart` / `st.bar_chart` have no tooltip format parameter (Streamlit 1.60.0). The Builder may use any approach that leaves the plotted data untouched.
- **[A5] Text is produced in Python, not by the chart library's number format.** Percent text comes from `fmt_pct_half` itself (or an exact reproduction). Dollar text comes from `"${:,.0f}"` itself. Reason: Python rounds exact halves to the even number and a chart library rounds them up, so a library format would make hover and table disagree (for example `479546.5`: Python `$479,546`, library `$479,547`; `0.0625`: Python `6.0%`, round-half-up `6.5%`). The formatted text travels as an extra tooltip-only field.
- **[A1] Shared helper.** One new shared display helper is authorized by the Principal (Gate Category E, 2026-11-11). It is permitted, not required: the Builder may use it for all 11 charts and adds no other new function.
- **[A6] No new dependency.** `requirements.txt` must not change. Altair is already a Streamlit dependency (Streamlit 1.60.0 requires it), so `st.altair_chart` needs no change. If the approach needs anything else, the Builder stops and reports.
- Apply in every cadence in which the chart renders.
- The Builder does not push, merge or open pull requests (Handbook, Repository write authority).
- No secret in source or reports. No live API call.

## 5. Files that may and may not change

**May change:** `Northwind_Financial_Dashboard.py`, only the 11 chart call sites in section 3 and, **because authorized in Gate Category E [A1]**, one new display helper. New test files in a new location.
**May not change:** the AI Narrative tab block and D22 areas; `rollups.py`; `close_history.py`; `close_validation.py`; `period_lifecycle.py`; `commentary_workflow.py`; `requirements.txt`; `Northwind_Sample_Dataset.xlsx`; everything under `governance/`; `project_handbook.md`; existing `build_test` scripts; table formatting (`_base_format_map`, `fmt_pct_half`, `style_variance_df`, etc.). If the Builder believes one of these must change, it stops and reports.

## 6. Acceptance criteria and evidence

1. **Tooltip text [A4].** Evidence must be read from the chart as the app sends it to the screen (its chart specification and data), covering **every point of all 11 charts**. Each point's tooltip text is compared with the table helper's output for the same underlying value. A check that calls the helper and compares the result with itself does not count.
2. **No number changed [A2].** The plotted fields (x, y, series) of each of the 11 charts are identical before and after: same values, same order, same series. A tooltip-only text field may be added. The extra field must not appear as an additional visible row in the tooltip.
3. **Missing values [A3].** With a fixture that has a missing period, the tooltip is blank for that point and shows no `nan`, `None` or `$0`.
4. **Rounding [A5].** The fixed test values give: `0.0625` shows `6.0%`; `0.3125` shows `31.0%`; `479546.5` shows `$479,546`; `1234.5` shows `$1,234`. A tooltip that follows round-half-up fails.
5. **Headcount by Department chart:** specification identical before and after.
6. **Axis labels, titles, captions, colours, ordering:** unchanged.
7. **Diff scope:** only what section 5 allows.
8. **Regression:** existing suites pass; the app runs without exception as on `main`.
9. **Principal product check:** the Principal hovers a chart on each of the five tabs in the running app.

The Builder's narration is not evidence. Independent Test reproduces criteria 1 to 6 from the code on the branch.

## 7. Out of scope

Axis tick labels; table formatting; renaming tooltip labels; any number, calculation or data change; any D22 work; the Headcount by Department chart; the dashboard-versus-narrative percent difference (recorded separately as an observation, not scope here).

---

# SCOPE AUTHORIZATION GATE (PRINCIPAL SIGN-OFF REQUIRED)

**Brief Title:** Chart Tooltip Display Format, Builder Brief v2
**Status:** ☒ APPROVED BY PRINCIPAL, 2026-11-11 11:26

## CATEGORY A — ALREADY AUTHORIZED

| Requirement | Authoritative Source | Incorporated? |
|---|---|---|
| None for chart tooltips. The table convention is existing table behaviour used as the format source, not authority for charts. | Searched Handbook, Decision Log, Briefs, assumptions at `e85cdf4` | n/a |

## CATEGORY B — NEW PRINCIPAL DECISIONS

| Requirement | Authorization Reference | Incorporated? |
|---|---|---|
| Format chart hover tooltips; display only | Principal request 2026-11-10 (relayed) | ☒ |
| Format = Revenue detail table format, $ and % | Principal, 2026-11-11 05:40 | ☒ |
| Hover only, no axis labels | Principal, 2026-11-11 05:44, confirmed by approval of v1 | ☒ |
| Separate Brief, kept out of D22; wanted before D22 validation | Principal, 2026-11-10 and 2026-11-11 | ☒ |
| Half-point percent in the hover (inherited from the table) | Principal approval of v2, 2026-11-11 11:26 | ☒ |
| Blank tooltip for missing values (same as table) | Principal approval of v2, 2026-11-11 11:26 | ☒ |
| One shared display helper | Principal answer to the Architect's question, 2026-11-11 (see Category E) | ☒ |

## CATEGORY C — GENUINE CONFLICTS

No genuine conflict identified. (D22's signed Brief forbids chart changes inside D22, which is why this is a separate Brief. The v1 internal contradiction on the helper is resolved by [A1].)

## CATEGORY D — TECHNICAL / PROCEDURAL CONSTRAINTS

| Constraint | Workaround | Blocking? |
|---|---|---|
| Native `st.line_chart` / `st.bar_chart` cannot format tooltips | Chart specification (Altair, already a dependency) with a Python-formatted tooltip-only field; plotted data unchanged | No |
| Percent values are fractions; half-point rounding must match the table | Call `fmt_pct_half` itself | No |
| Chart-library rounding differs from Python for exact halves ($ and %) | Produce all tooltip text in Python | No |
| Chart code and D22 narrative block sit in one file | Separate branch and review; no line overlap. The Advisor simulated a minimal edit at line 3161 against the D22 Release 1 candidate (`cd5731c`) and it merged cleanly (Advisor-reported, not independently checked by the Architect; real result depends on the Builder's change) | No |

## CATEGORY E — ARCHITECT RECOMMENDATIONS

| Recommendation | Reason | Principal Authorization |
|---|---|---|
| One shared display helper rather than 11 separate edits (Advisor also recommends) | Smallest change, one place to correct, keeps hover and table rules in one place | ☒ Authorized by the Principal, 2026-11-11  ☐ Not authorized |
| Friendlier tooltip labels instead of `index` / `value` / `color` | Readability | ☒ Not authorized |

## EXPLICIT EXCLUSIONS

| Exclusion | Reason | Authority |
|---|---|---|
| Axis labels | Hover only | Principal, 2026-11-11 |
| Headcount by Department chart | Whole numbers, no defect | Architect finding, `e85cdf4` |
| Tables, numbers, calculations | Display only | Principal, 2026-11-10 |
| Any D22 content | Separate Brief | Principal, 2026-11-10 |
| Dashboard vs narrative percent difference | Recorded as a separate observation | Advisor request, 2026-11-11 |

## MINIMUM-SCOPE VERIFICATION

☒ Minimum implementation identified (11 hover labels, data untouched)
☒ Claimed dependencies tested (D22 does not need this; this does not need D22; priority is the Principal's choice)
☒ Workarounds considered
☒ Optional architecture separated (Category E)
☒ No unnecessary bundling introduced

## PRINCIPAL APPROVAL GATE

☒ This Brief includes ALL requirements I have decided.
☒ This Brief includes NO product scope I did not authorize.
☒ The exclusions accurately represent my deferred/out-of-scope decisions.
☒ The Architect has not silently narrowed my authorized scope.
☒ The Architect has not silently expanded my authorized scope.
☒ Architect recommendations are clearly separated from mandatory scope.
☒ I understand that Builder implements ONLY the authorized scope in this Brief.
☒ If the Brief is incomplete, I will request clarification before issuing it.

**Approved by Principal:** recorded from the Principal's in-session message, "I the principal autorized the V2", plus his answer authorizing the helper (the Principal may countersign when committing the file)  **Date:** 2026-11-11 11:26

## ARCHITECT ATTESTATION

☒ Reviewed Handbook and Decision Log · ☒ Reviewed canonical state (`e85cdf4`) · ☒ Classified all scope · ☒ Applied Required Response Format · ☒ Applied Minimum-Scope Test · ☒ No unauthorized bundling · ☒ No technical preference as product authority · ☒ No silent narrowing or expansion · ☒ Brief accurately represents authorized scope

**Architect:** Claude (Architect)  **Date:** 2026-11-11

**RELEASE RULE:** Released: the Principal Approval Gate was explicitly approved on v2 on 2026-11-11 11:26. The Architect's attestation does not substitute for it.
