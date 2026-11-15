# Return Report: Release 1 tests moved into `build_test`

Layout change only, made at your request of 2026-11-15. This is Builder evidence only, not independent validation, and nothing was pushed.

## What changed

| From | To | Edits inside the file |
|---|---|---|
| `tests/test_snapshot_classifier.py` | `build_test/test_snapshot_classifier.py` | run command in the docstring |
| `tests/test_number_check.py` | `build_test/test_number_check.py` | **fixture path** (`build_test/fixtures/…`), README mention and run command in the docstring |
| `tests/test_narrative_integration.py` | `build_test/test_narrative_integration.py` | run command, and one comment naming the classifier test file |
| `tests/fixtures/README.md` | `build_test/fixtures/README.md` | title, and the name of the test that checks the fixture |
| `tests/fixtures/rendered_prompt_q4_fy2026_demo.txt` | `build_test/fixtures/rendered_prompt_q4_fy2026_demo.txt` | none (byte-identical) |

- 8 lines changed in total across the 5 files. No test logic changed.
- The tests locate the repository root as "the folder above the test file's folder". `build_test/` is one level down, just as `tests/` was, so that calculation is unchanged.
- The `tests/` folder no longer exists.
- No other file changed. The dashboard, both modules, the existing `build_test` scripts and `build_test/README.md` are untouched.

**Run command, from the repository root:**

```
python -m unittest discover -s build_test -v
```

`discover -s build_test -t .` does **not** work, because `build_test` is not a Python package: it has no `__init__.py`. I did not add one, because you didn't ask for it. Single files also run as `python -m unittest build_test.test_number_check`, or as a plain script, `python build_test/test_number_check.py`.

## Results (Python 3.13.17, pinned venv: pandas 2.2.3, numpy 2.5.1, openpyxl 3.1.5, streamlit 1.60.0; `ANTHROPIC_API_KEY` unset; no API call)

| Run, from the repository root | Result |
|---|---|
| `python -m unittest discover -s build_test -v` on the branch | **125 tests, OK**: 44 classifier, 73 number check, 8 integration |
| The same command on a copy of `ea6e8aa` with the package's patch applied | **125 tests, OK** |
| Each file by module name (`python -m unittest build_test.<name>`) | 44 OK, 73 OK, 8 OK |
| Each file as a plain script (`python build_test/<name>.py`) | 44 OK, 73 OK, 8 OK |
| The seven existing `build_test` scripts | Same exit codes as before. Output is identical to the 2026-11-14 run of the same code (0 differing lines after normalising temp paths and timestamps). `close_orchestrator.py` still exits 1 with the pre-existing `AttributeError`; the other six exit 0. |

The lines starting `OK  Revenue by Region…` in the test output are `rollups.py`'s own self-checks. They are printed when the fixture test imports it, and they are not test results.

## Files in this package (upload onto `main` at `ea6e8aa`)

| SHA-256 | Path |
|---|---|
| `65f93cfec2922a7a776e04a76fe95fb2359729054b0d268f7517d7cd07dd5d0f` | `Northwind_Financial_Dashboard.py` (unchanged from yesterday) |
| `6960899c48aa0f15bdb6cb6fbe9d1383fb53072fed7a8d77f149023b2ce1016c` | `narrative_number_check.py` (unchanged from yesterday) |
| `162e853ca840a4c476070c71b38afad5692978d65c558cbc36e5b218cfd63b9b` | `narrative_snapshot.py` (unchanged from yesterday) |
| `7387d26a8edaf6ac55a225382037df50af77b9c90f58abfa1422cd18bd57ce24` | `build_test/fixtures/README.md` |
| `4426f878d8c0a6f5ae6becc0c988723fc810564bdf4e01a61d739d62e9c0d433` | `build_test/fixtures/rendered_prompt_q4_fy2026_demo.txt` |
| `189262fc23198617beee9659110b1bc0168e86455bf8c8463a56f93fc0c5bf23` | `build_test/test_narrative_integration.py` |
| `9a6d7f021ed838973ed92d5a6ff3c018bb7be6729a902a91e49160f9a021060e` | `build_test/test_number_check.py` |
| `c4a51c69b87939f227d6933f024faa4256e3fe7b6e9b331248f5afb75a1753f3` | `build_test/test_snapshot_classifier.py` |

- **This replaces yesterday's list.** Do not upload anything under `tests/`.
- **If you have already uploaded yesterday's `tests/` files**, delete those 5 files and add the 5 above. The other 3 files are byte-identical to yesterday's.
- To check the files: from inside `files/`, run `sha256sum -c ../SHA256SUMS.txt`.
- **With git:** `git am release1_build_test_layout_4037eef.patch` on `main` at `ea6e8aa` applies the two commits strictly: Release 1, then the move. Or fetch the bundle (it requires `ea6e8aa`):

  ```
  git fetch release1_build_test_layout_4037eef.bundle builder/d22-release1-build-test-layout:release1
  ```

- Patch SHA-256: `763f47738fd8b256b492ccc669e09dbbb684f997cb8f180be556aa4ebf876267`
- Bundle SHA-256: `ad5296b5b2eb5e3395988a5354bb6a15f4069207302904934f673257f5dcc29c`

## Points to note

1. **Anything that runs every script in `build_test/`** (for example `for f in build_test/*.py`) will now also run the three test files. Each passes when run as a script. The integration file takes about 15 seconds.
2. **Stale wording in two product files.** The docstrings of `narrative_snapshot.py` (1 line) and `narrative_number_check.py` (2 lines) still mention `tests/test_…py`. They are comments only, with no effect on behaviour. I left them because you asked me to change only the tests and fixtures. Updating them would change two more files.
3. **Base.** I did not re-check `origin/main`, because you didn't authorize a fetch this time. The base is still `ea6e8aa`, as fetched on 2026-11-14.

## Repository actions

- **Local branch:** `builder/d22-release1-build-test-layout`, made from `f53eabc` in the existing worktree `/home/claude/6-sogh-9/nw-release1`.
- **Local commit:** one, `4037eefab180e7047e5806ce455c1d9d1073e27a` (parent `f53eabc`).
- **Other commits:** `cd5731c`, `0f6c90a` and `f53eabc` are unchanged.
- **Working tree:** clean.
- **Not attempted:** no fetch, no push, no other remote command, no `add_repo`, no change to remotes, credentials or access. The addenda and the Handbook are unedited.
