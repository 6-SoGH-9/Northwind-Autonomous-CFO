# Builder Brief — Cycle 3, Task 1
**Status:** Active
**Precedence reminder:** Handbook > this Brief > code/docs > archived briefs > archived reports.
**Depends on:** Cycle 2 batch (Live-promoted) — do not modify pipeline calculation logic, only data-resolution and archival behavior.

---

## Context

Per D10 (new): the canonical object of the Live system is the **Approved Financial Close**, not a single active dataset. This task implements the minimal version of that: an immutable, folder-based Close History, with the pipeline resolving the latest approved close instead of a hardcoded filename.

**Explicitly not in scope** — do not build any of these, even partially:
- A database or query layer
- Retention/lifecycle management
- `dashboard.html` static export or `board_deck.pptx` generation (schema has fields for these; leave them absent/placeholder, do not fabricate stub files)
- Automated close-approval workflow (approval remains a manual/simulated step for now)

---

## Item 1 — Close History storage convention

For this challenge, Close History is stored as a folder structure (GitHub-hosted) — one immutable folder per approved close:

```
close_history/
    <PERIOD_LABEL>/
        raw_dataset.xlsx
        rollups_output.xlsx
        observations.csv
        narrative.txt
        metadata.json
```

**Note on scope:** this folder convention is this challenge's storage implementation, not the product architecture. The workflow's actual requirement is the *concept* of an immutable Approved Financial Close — the same logic should hold regardless of whether the underlying store is a Git repo, SharePoint, S3, or anything else. Don't hardcode assumptions that only work for a local folder (e.g. don't rely on filesystem-specific ordering tricks) where a simpler, storage-neutral approach works just as well.

- `raw_dataset.xlsx`: copy of the input dataset for that close, frozen at approval time.
- `rollups_output.xlsx`: only copied in at approval — while a close is in progress, the existing "regenerate, don't keep" rule still applies (Section 12, unchanged).
- `observations.csv`: Phase 2/3 flagged items for that close (the same data currently shown on the Close Validation Status page).
- `narrative.txt`: whatever the narrative step actually produced (AI-generated text, or the prompt file if no API key was available — reflect actual behavior, don't assume one path).
- `metadata.json`: at minimum — period label, approval timestamp, workflow state (should be "Archived"), Phase 2/3 flag counts, and **the git commit hash of the pipeline code that produced this close**.

## Item 2 — Required behavior, not prescribed implementation

The pipeline must resolve **the latest approved close** from Close History dynamically, with no hardcoded dataset filename anywhere in the resolution path. How this is implemented (function name, structure, lookup method) is a Build-stage decision — choose whatever's cleanest, as long as it meets the acceptance criteria below.

**Bootstrap case — must be handled explicitly, not left to fail:** a newly deployed Live system has an empty `close_history/`. In that state, there is no "previous approved close" to diff against. The resolution logic must detect this and initialize the first approved close (i.e., the incoming dataset becomes Close History's first snapshot, with Phase 2's diff-against-prior step correctly skipped or reporting "no prior close to compare" rather than erroring). This is a real, expected first-run state — not an edge case to leave undefined.

**This is a resolution-logic change only.** Do not touch tie-out calculation logic, allocation math, or anything already verified in Cycle 2.

## Item 3 — Demonstrate the full loop using existing simulation data, exercising both code paths

Start from a genuinely empty `close_history/` — do not hand-place any snapshot folder. Use the existing Close v1/v2 simulation data to drive this sequence:

- Close v1 → run through the pipeline against an empty Close History. This must go through the **bootstrap path** (Item 2) — the first snapshot is created by that logic, not manually constructed. This is what actually proves 2b works, rather than just describing it.
- Close v2 → processed next, now with Close v1 present. This exercises the **normal path** — dynamic resolution finds Close v1 as the latest approved close, diffs against it, then archives Close v2 as the second snapshot.

This should reproduce the exact same Phase 2/3 catches already verified (1 historical revision, 1 plausibility anomaly) — proving the new resolution logic doesn't change *what* gets caught, only *how* the comparison baseline is found, while also proving both the bootstrap and normal paths are real, not just one demonstrated and one assumed.

---

## Acceptance Criteria

| # | Criterion |
|---|---|
| 1 | `close_history/` starts empty; Close v1 is created via the bootstrap path (not hand-placed) and Close v2 via the normal path — 2 snapshot folders result, each containing all 5 files (or explicit note where a file is legitimately empty, e.g. no API key) |
| 2 | Pipeline resolves "latest approved close" dynamically — no hardcoded filename anywhere in the resolution path |
| 2b | Bootstrap case handled: with `close_history/` empty, the incoming dataset is correctly initialized as the first approved close, and Phase 2 correctly reports "no prior close" rather than erroring |
| 3 | Phase 2 diff against Close v1 still catches exactly 1 flagged row, matching previously verified constants exactly |
| 4 | Phase 3 still catches exactly 1 flagged anomaly, matching previously verified constants exactly |
| 5 | `metadata.json` present per snapshot, includes git commit hash |
| 6 | 12/12 tie-outs still pass — no regression from the resolution-logic change |
| 7 | No `dashboard.html` or `board_deck.pptx` fabricated — confirm their absence is explicit, not silently skipped |

Report with actual file listings, actual diff output, and actual tie-out output — not status claims.
