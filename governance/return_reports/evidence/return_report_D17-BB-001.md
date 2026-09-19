# Builder Return Report — D17-BB-001: Movement-Concentration Narrative Component Detail

**Round 3 of this Brief.** This supersedes the Round 1 and Round 2 Return Reports in full. Round 2 corrected the data model (gross variance removed, Expenses hierarchy, threshold split — all per the Principal's direct review of Round 1's output). Round 3 (Section 7a below) fixes a real environment failure the Principal reported after testing Round 1's patch in their own D15 setup. Implemented against the same clone, HEAD `29691e7f94db58385f3aa5850a8f607e38992294`.

**Note on process:** the Principal is reviewing and correcting this work directly in this session rather than through the Architect. The corrections below (gross-variance removal, the Expenses hierarchy/shared-denominator model, the 17%/60% threshold split) are Principal instructions given directly, confirmed back in plain language and checked against the Principal's own worked numbers before implementation. They are recorded here as Principal-authorized changes to the original Brief's Section 3 design, not Builder-initiated scope changes.

---

## 1. What changed from Round 1 (Principal-directed)

1. **Gross variance removed entirely.** No `Gross Variance ($)` column, no gross-based calculation, anywhere in Breadth/Concentration (Revenue or Expenses).
2. **Expenses restructured into a three-level hierarchy sharing one denominator**, replacing the two flat, category-siloed line items from Round 1:
   - **Total Expenses** (new line item, "Expenses") — segments = its 3 Categories.
   - **Category** (Salaries & Benefits — new; Software & Tools; Other Opex) — segments = that category's Departments.
   - **Department**, nested under each Category.
   - At every level, a row's **% share and its driving-vs-offsetting classification** are computed against **Total Expenses' own net variance** — never a Category subtotal. A row's **displayed `Total Variance ($)`** is still its own subtotal.
3. **Salaries & Benefits added as a third Expenses category** (previously absent from Breadth/Concentration entirely).
4. **Revenue is explicitly unchanged in structure** — own total, own denominator, 60% threshold, per your confirmation.
5. **Threshold split:** Expenses (Total / Category / Department, all three levels) now use `abs(share) >= 17%`. Revenue keeps `abs(share) >= 60%`. `OFFSET_MATERIALITY_THRESHOLD` (20%) stays a single shared, independent constant — not tied to either concentration threshold, per your explicit instruction.
6. **The driver-check sign bug flagged in Round 1 is now fixed** (`abs(top_driver_share) >= threshold`, both domains) — this was your direct instruction for Revenue, and was already required by the switch to an absolute-value Expenses threshold, so both got the fix.

## 2. Verification against your worked numbers

I derived the algorithm from your Q2 FY2025 expenses table by reverse-engineering the denominator pattern (every row divides by the Total Expenses net variance, $48,307 — not its own subtotal), then reproduced **every single row in your table exactly**:

| Row | Your value | Computed |
|---|---|---|
| Salaries & Benefits — Driver % | 79% | 79.30% |
| ...Customer Success (driver) | 43% | 42.82% |
| ...R&D (offsetting) | -18% | -17.95% |
| Software & Tools — G&A (driver) | 3% | 2.76% |
| ...R&D (offsetting) | -4% | -3.79% |
| Other Opex — R&D (driver) | 19% | 19.09% |
| ...Sales & Marketing (offsetting) | -5% | -4.64% |

All match. I also confirmed the mechanism behind your Software & Tools example directly: Software & Tools' own category subtotal is **negative** (−$1,128), yet G&A (positive) is correctly the "driver" and R&D (negative) is correctly the "offsetter" — this only works because the sign test at the Department level is against **Total Expenses' sign** (positive), not Software & Tools' own (negative) sign. Confirmed this reproduces every sign in your table with no exceptions.

## 3. Live evidence (Streamlit `AppTest`, actual generated narrative)

For Q4 FY2026, the live dashboard now renders four Expenses blocks (Total, then 3 Categories) instead of the prior two:

```
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
```

**Self-consistency check I ran on this live output** (not asked for, but the cleanest available proof the shared-denominator model is actually working end to end): each Category's own department shares sum to that Category's own share of Total Expenses, not to 100% — e.g. Software & Tools' four departments (−5%, +1%, −13%, +3%) sum to **−14%**, exactly matching Software & Tools' own −14% share of Total Expenses shown in the "Expenses" block above. Same holds for Salaries & Benefits (31+39−12+13 = 71%, matching its own 71% share) and Other Opex (7+2+26+8 = 43%, matching its own 43% share). This only works if every level is genuinely referencing the same shared denominator — confirms the design end to end, live, not just in isolated unit checks.

Live app: **0 exceptions**, all 8 tabs render, breadth table shows the new 6-row structure (Revenue ×2, Expenses, and 3 categories) with the new column set live in the UI, not just in code.

## 4. Full regression re-run on this final state

- **`rollups.py` internal tie-outs: 19/19**, up from 18 — added a new check (`breadth_expenses_total_q`'s net variance vs `pl_q`'s `Total Opex QoQ/YoY Var ($)`, the same pattern the pre-existing Revenue-by-Region check already used), confirming the new "Expenses" grand total independently ties to the P&L, not just internally self-consistent. Max diff: float-noise (`~4e-10`).
- **`build_test/commentary_workflow_demo.py`: 49/49**, unchanged.
- `close_history.py`, `close_validation.py`, `period_lifecycle.py`, everything under `governance/`: confirmed byte-identical to canonical throughout.

## 5. Files changed (cumulative, all rounds)

```
 Northwind_Financial_Dashboard.py |  22 ++-
 commentary_workflow.py           | 101 ++++++++++++++
 northwind_narrative_prompt.md    |   7 +-
 rollups.py                       | 283 +++++++++++++++++++++++++++++++++------
 4 files changed, 367 insertions(+), 46 deletions(-)
```

Patch file (full `git diff`) delivered alongside this report, supersedes the Round 1 patch.

## 6. Implementation notes

- `build_breadth_concentration()` gained one new optional parameter, `grand_total_by_period` — a `{period: total}` dict. When given, it overrides both the % denominator and the sign reference (never the displayed `Total Variance ($)`, which stays each row's own subtotal). Used for the three Expenses Category/Department calls; not used for Revenue or for the "Expenses" Total row itself (whose own segments already sum to the grand total by construction, so no override is needed there — verified this is mathematically identical either way).
- The grand-total lookup is read directly off the **already-computed "Expenses" row's own output** (`dict(zip(breadth_expenses_total_q["Fiscal Quarter"], breadth_expenses_total_q["Total Variance ($)"]))`), not recomputed independently — single source of truth, so the denominator every Category/Department row uses is guaranteed identical to what's displayed as the Total Expenses row.
- `commentary_workflow.build_movement_component_detail()` now takes both `total_var` (own subtotal, header line) and a separate `share_reference_total` (grand total where applicable, used only for the per-segment % calc) — these were one parameter in Round 1 and had to be split once Category/Department rows needed a different value for each.
- `MOVEMENT_COMPONENT_SOURCES_Q`/`_Y` entries are now 3-tuples (`dim_col`, `component_df`, `share_reference_dict_or_None`) instead of 2-tuples.
- Both prompt-text locations (`rollups.py`'s live `SYSTEM_PROMPT` rule 2d, and the inline instruction inside `build_user_prompt`'s f-string) and `northwind_narrative_prompt.md` were all updated together to describe the new model consistently — this is the same content-correspondence concern flagged in Round 1, re-applied here.
- Dashboard: formatting dict no longer has a `Gross Variance ($)` entry; the Cost Structure caption now states both thresholds separately (60% Revenue / 17% Expenses) instead of one shared number.

## 7. Still open from Round 1 (not resolved by this round, unrelated to the Principal's corrections above)

- **Segment display order** inside each Component Breakdown remains natural/alphabetical (not a specific business-defined order) — this question is orthogonal to the restructuring and wasn't raised in this round's correction.
- **Money formatting** still uses the project's existing `fmt_money()` (`"$-3,846"` style), not the accounting-parens style from the original Brief's illustrative example.
- **The Handbook/D17 provenance gap** (no D15/D16/D17 entries anywhere in canonical `project_handbook.md` v2.19) is unchanged — still a housekeeping item, not a code blocker.

## 7a. Round 3 — module-boundary fix (Principal-reported failure, real-environment test)

The Principal applied the Round 1 patch in their own test environment and ran D15's "Run correction intake" step, which failed:

```
Candidate pipeline run failed — corrected data was not accepted.
ModuleNotFoundError: No module named 'commentary_workflow'
  File "/tmp/d15_candidate_<id>/rollups.py", line 36, in <module>
    import commentary_workflow
```

This is exactly the module-boundary deviation flagged as an open item in every prior round of this report: D15's correction-intake candidate pipeline stages and executes `rollups.py` **standalone**, in an isolated temp directory, without `commentary_workflow.py` co-located — confirmed by the traceback's own path (`/tmp/d15_candidate_.../rollups.py`). The hard top-level `import commentary_workflow` I added for Section 4's wiring broke that pipeline outright, since that candidate run only needs `rollups.py`'s deterministic Phase 2/3 tie-out logic and never touches narrative generation.

**Fix:** the import is now guarded (`try/except ImportError`), setting a module-level `COMMENTARY_WORKFLOW` flag (`commentary_workflow` on success, `None` on failure). `build_user_prompt()`'s component-detail wiring now checks `COMMENTARY_WORKFLOW is not None` before calling into it; when it's `None`, every line item falls back to the pre-D17-BB-001 one-line summary (the original, always-worked behavior) instead of `rollups.py` failing to import at all.

**This does not touch any D15 file** — `period_lifecycle.py` remains explicitly out of scope per the Brief and was not modified. The fix is entirely contained within `rollups.py`, one of this Brief's own in-scope files.

**Verified by direct reproduction**, not just reasoning about it: built a temp directory containing only `rollups.py` + `close_history.py` + the dataset (matching the traceback's own file layout) and confirmed:
- `import rollups` now succeeds cleanly (previously: `ModuleNotFoundError`).
- All 19 internal tie-out checks still run and pass inside that isolated sandbox.
- `R.COMMENTARY_WORKFLOW is None` → `True` in that sandbox, confirming graceful degradation, not a silent partial failure.
- Running `python3 rollups.py` directly in that same sandbox (exercising the `__main__` narrative-demo path, the same code path D15's candidate pipeline exercises) completes with **exit code 0** and zero errors/exceptions in the output.

**Also re-confirmed the normal (full-checkout) case is unaffected**: with `commentary_workflow.py` present alongside `rollups.py` (the standard dashboard environment), `COMMENTARY_WORKFLOW is not None` → `True`, and the full regression suite still passes clean: **19/19 internal tie-outs, 49/49 `commentary_workflow_demo.py`, 0 AppTest exceptions.**

This closes the specific failure the Principal reported. It does **not** resolve the underlying design question of whether this wiring approach is the right one long-term (still flagged below) — it makes the current approach safe to run in both environments rather than hard-failing in one of them.

## 7b. Still open — module boundary (design question, not a bug)

`rollups.py` importing `commentary_workflow` — now guarded, but still a real coupling that didn't exist before this Brief, and D15's own architecture apparently depends on `rollups.py` being safely standalone-importable (confirmed by its sandboxed candidate-pipeline design). If there's a preferred long-term shape for this — e.g. moving the wiring itself, not just guarding the import — that's a design call I'd rather get direction on than invent, per the standing discipline. The guard makes the current shape safe; it doesn't necessarily make it the *right* shape.

## 8. Blockers

None. All four files build, import, and render cleanly, **in both environments** (the normal full-checkout dashboard environment, and D15's isolated candidate-pipeline sandbox); the full regression suite (19/19 + 49/49) passes; every number in the implementation reproduces your worked table exactly; the live narrative is self-consistent under direct arithmetic check; the reported `ModuleNotFoundError` is fixed and reproduced-then-confirmed-fixed directly, not just reasoned about.

## 9. Canonical synchronization

Not yet performed — same standing constraint as prior rounds (no push credentials in this environment). This remains a principal-facilitated step. **Recommend applying this Round 3 patch directly (it is a complete, standalone diff against clean canonical `main` — see the separate note on not stacking it on top of the Round 1 patch) rather than the Round 1 or Round 2 patches**, since only this version has been verified against your actual D15 environment's failure mode.

