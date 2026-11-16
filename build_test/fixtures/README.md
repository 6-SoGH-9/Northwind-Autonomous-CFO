# build_test/fixtures: provenance

Builder development/regression fixtures for D22 Release 1. They are **not** calibration data
(Set A / Set B belong to Independent Test and are not here) and **not** evidence about any real or
historical close.

## `rendered_prompt_q4_fy2026_demo.txt`

| Item | Value |
|---|---|
| What it is | The user prompt rendered by the repository's own `rollups.build_user_prompt()` |
| Source dataset | `Northwind_Sample_Dataset.xlsx` (the canonical **synthetic** sample dataset shipped in the repo) |
| Code state | `main` at `f517ce1` (`rollups.py` unchanged by Release 1) |
| Caller shape | The `rollups.py` `__main__` demo call: `Q4 FY2026` vs `Q3 FY2026`, no commentary block, `movement_component_sources=MOVEMENT_COMPONENT_SOURCES_Q` |
| Transformations | None (written byte-for-byte as rendered) |
| Used for | The WP3 tests parse its DATA block as "the locked DATA block of a rendered prompt" |
| Suitable for | Builder component tests only |

`build_test/test_number_check.py::TestFixtureProvenance` regenerates the prompt from the live code in a
scratch copy and fails if this file has drifted from what `build_user_prompt()` produces.

To regenerate by hand (offline, no API key; run in a scratch copy, because importing `rollups`
prints its pipeline): `import rollups as R; R.build_user_prompt("Fiscal Quarter", R.quarter_order,
"Q4 FY2026", "Q3 FY2026", "Q3 FY2026", R.pl_q, R.rev_by_region_q, R.rev_by_product_q, R.region_cm_q,
R.product_cm_q, R.exp_by_dept_q, R.sb_volrate_q, R.breadth_all_q, R.hc_dept_q,
R.company_rev_per_hc_q, R.bva_q, movement_component_sources=R.MOVEMENT_COMPONENT_SOURCES_Q)`.

## `narrative_number_check_release1.py`

| Item | Value |
|---|---|
| What it is | A byte-exact copy of the Release 1 module `narrative_number_check.py` as it is on `main` at `9af2f18` |
| SHA-256 | `6960899c48aa0f15bdb6cb6fbe9d1383fb53072fed7a8d77f149023b2ce1016c` (checked by `build_test/test_addendum1_number_check.py`) |
| Added for | D22 Addendum 1, A-6(c): "a block without the heading has no Budget lines and behaves as Release 1" |
| Used for | The Addendum 1 tests load it under the name `narrative_number_check_release1` and compare its results field by field with the amended module |
| Never imported by | The product. Not a test file (`unittest discover` does not import it: the `fixtures` folder is not a package) |
| Suitable for | Builder regression tests only |

## `narrative_number_check_addendum1.py`

| Item | Value |
|---|---|
| What it is | A byte-exact copy of `narrative_number_check.py` as it is on `main` at `43f9695` (Release 1 plus D22 Addendum 1) |
| SHA-256 | `c0a4150daf67be7a6fd454f51c3a8f5e30fe95cfa889433b1d3f48533438572b` (checked by `build_test/test_addendum2_number_check.py`) |
| Added for | D22 Addendum 2, acceptance criterion "Release 1 behaviour is unchanged for names and numbers not touched by A or D1" |
| Used for | The Addendum 2 tests load it under the name `narrative_number_check_addendum1` and compare its results field by field with the amended module |
| Never imported by | The product. Not a test file (`unittest discover` does not import it: the `fixtures` folder is not a package) |
| Suitable for | Builder regression tests only |
