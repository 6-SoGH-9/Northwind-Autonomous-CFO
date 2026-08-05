# Assumptions and Limitations — for the write-up's limitations section

Running log, built alongside the pipeline. Feed directly into the submission
document (Section 7 of the project brief) rather than reconstructing this
from memory later.

---

## Fiscal calendar

FY runs July-June, labeled by the calendar year it ends in (FY2024 = Jul 2023-
Jun 2024). Chosen because the dataset's 36 months split into exactly 3 clean
fiscal years on this convention, with no partial year.

## Headcount

Headcount is a stock, not a flow. Rollups report both **average headcount**
(mean of the monthly values in the period) and **ending headcount** (last
month's snapshot) — never a sum. Starting company-wide headcount (Jul 2023) =
135; ending (Jun 2026) = 167.

## Regional Revenue & Go-to-Market Investment / Product Line Revenue & R&D
## Investment — allocation method and framing (Cycle 2 reframe)

**This section supersedes an earlier draft's "Segment margin views (partial)
— naming and allocation method" section in full**, per the Cycle 2 Task 1
brief. Two prior margin-style labels were tried and retired for this same
underlying data (a standard-margin term, then an "adjusted" variant of it —
see `rename_instruction_contribution_margin.md`, now superseded, for the
exact prior wording) — and both were found to still invite a per-segment
profitability reading that the data cannot support (see the
mathematical-identity
limitation below). The fix this time is a data-shape change, not another
label: **no cross-segment % appears anywhere in these pages, tables, or the
AI narrative.** Only $ figures are shown side-by-side across segments; % is
retained solely as a single-segment trend view (one segment's own % over
its own history, never placed next to another segment's %).

**(a) Allocation math is unchanged from the prior cycle** — only the
framing, labeling, and what's displayed changed.

**Region cut**: Sales & Marketing + Customer Success opex allocated to
region by that region's share of total revenue in the period.
`Region Net of GTM Cost = Region Revenue - (Region Revenue / Total Revenue) x (S&M + CS Opex)`

**Product line cut**: R&D opex allocated to product line by that product
line's share of revenue *among the R&D-allocation-base product lines only*
(see the Professional Services exclusion below).
`Product Net of R&D Cost = Product Revenue - (Product Revenue / R&D-Allocation-Base Revenue) x R&D Opex`

**G&A is excluded from both cuts** and reported separately as unallocated
corporate overhead — no plausible tie to a region or product.

**Why these departments, why revenue share**: S&M and CS are go-to-market
cost centers organized around markets; R&D maps to what's being built, not
where it's sold. Revenue share is the allocation key because the dataset has
no finer driver available (no rep count by region, no engineer count by
product line, no time-tracking).

**(c) Fix — Professional Services excluded from the R&D allocation base
(RETAINED from the prior cycle; this was a math correction, not a framing
choice, so the reframe below doesn't touch it).** Professional Services is a
services line, not something R&D builds, so it must not receive an R&D
allocation. R&D opex is split only across Core Platform, Add-on:
Forecasting, and Add-on: Reporting, by their relative revenue share among
those three product lines only. Professional Services' Allocated R&D Opex
($) = 0, so its Net of R&D Cost ($) equals its own revenue exactly (its own
% trend is a fixed 100% every period, by construction — not a data
anomaly). Example, Q4 FY2026: Core Platform's Net of R&D Cost moved from
$1,693,621 under a method that included Professional Services in the
allocation base, to $1,638,011 after excluding it — a real dollar shift
from a real correction, unaffected by this cycle's reframe. *(Figure
rounded to the nearest dollar for readability; exact pipeline output is
$1,638,011.09.)*

**These are two separate, partial views, not a full segment P&L, and they
are NOT comparable to each other** (different cost bases subtracted by
design — do not compare a region's figures to a product line's figures).
- Region Net of GTM Cost is net of S&M + CS ONLY — R&D and G&A are not
  included.
- Product Net of R&D Cost is net of R&D ONLY (and, for Professional
  Services, net of nothing at all) — S&M, CS, and G&A are not included.
- Summing all four regions' Net of GTM Cost $ equals Total Revenue - S&M -
  CS, not Operating Profit. Same logic for product lines vs R&D. Verified
  exactly (zero-cent tie-out) in the pipeline's verification step, every
  quarter — the Professional Services exclusion does not break this
  identity, since Professional Services still contributes $0 of allocated
  R&D to the sum.
- A true full-margin view isn't achievable with this dataset, since S&M
  cannot be attributed to product lines any more precisely than R&D can be
  attributed to regions.
- The split of R&D between Core Platform and the Add-on lines should be read
  with low confidence — Core Platform likely carries foundational
  engineering cost that benefits all product lines, and this dataset has no
  way to separate platform-maintenance spend from feature-specific spend.

**(b) The reframe decision, and why it's a data-shape change rather than a
wording fix.** The root defect is mathematical, not linguistic: under ANY
proportional (revenue-share) allocation key, the resulting % is identical
across every segment sharing an allocation base in the same period —

```
Net-of-cost % = 1 - (allocated opex / segment revenue) = 1 - (total opex / allocation-base revenue)
```

— regardless of which departments are allocated to which cut. No label —
not the standard-margin term this data was originally called, not the
"adjusted" variant tried after that, not any future synonym — changes
that identity, because the identity lives in the arithmetic, not the name.
In the Region cut this identity holds across all four regions (the
allocation base is total company revenue). In the Product cut it holds
across the three R&D-allocation-base product lines (Core Platform, Add-on:
Forecasting, Add-on: Reporting); Professional Services sits outside that
identity entirely at a fixed 100%, since it receives no allocation at all.
Because no wording change can prevent a reader from placing two segments' %
side by side and drawing a profitability conclusion the data doesn't
support, the decision this cycle was to **remove the cross-segment %
entirely from every artifact** — dashboard tables/charts, the AI narrative's
input data, and its output — rather than layer another caveat onto a
misleading table shape. $ figures remain fully comparable across segments
within the same cut (they reflect real revenue/segment size); % is
demoted to a single-segment trend view, the one context where it's
mathematically meaningful. Consequently:
- Net-of-cost $ differences across segments in the same period and cut ARE
  meaningful (they reflect revenue/segment size) and are the primary KPI on
  both pages now.
- Net-of-cost % is never displayed cross-sectionally anywhere in this
  project as of this cycle.
- Net-of-cost % IS meaningful, and is shown, as a period-over-period trend
  within a single segment (the reader picks one region or one product line
  at a time).

**(d) One documented principle, applied twice, stated once.** The same
attribution problem — a company-wide or shared figure divided by a
segment's own denominator, producing a ratio whose cross-sectional variation
is an artifact of the allocation math rather than a real performance
difference — was also identified in department-level Revenue-per-Employee
metrics (company-wide revenue has no real per-department attribution basis
any more than S&M/R&D opex has a real per-region/per-product attribution
basis). That metric has been removed under the same reasoning (Cycle 2 Task
2) rather than re-deriving a separate justification for it: the Headcount &
Efficiency page's department table now shows headcount only (no revenue or
opex column at all), and company-wide Revenue per Headcount is a
structurally separate table with no Department column, so it cannot be
misread as department-level even by accident. The company-wide
Revenue-per-Employee trend itself is unaffected and remains valid.

A related but distinct metric — **Opex per Employee, by department**
(department Opex ÷ department Ending Headcount) — is genuinely
department-level (both the opex and the headcount belong to that
department, unlike revenue) and was moved to the Cost Structure page rather
than removed. It answers a cost-discipline question (is this department's
spend per head rising or falling), not a workforce-efficiency question, so
it doesn't belong on the Headcount & Efficiency page even though it's a
legitimate department-level ratio.

This constraint — no cross-segment ratio built from a proportionally
allocated shared cost or shared revenue figure — is enforced directly in
the narrative-generation prompt (system prompt rule 2c, and the Investment
Alignment task instructions) so the AI output cannot reconstruct a
cross-sectional claim the data shape no longer supports even if the input
happened to contain one.

## Revenue Mix (%) — Revenue Performance page (Cycle 2 Task 2 addition)

`Revenue Mix (%) = Segment Revenue / Total Revenue`, by region and by
product line, for the same period. This is a direct ratio of actual revenue
figures — not a proportionally allocated cost divided by a segment's own
revenue — so it does NOT reduce to the mathematical-identity problem
described above. A segment's mix % genuinely varies period to period and
segment to segment because it's built from real revenue, not from an
allocation rule applied uniformly across segments. This is a valid,
intentional cross-segment comparison and is shown side-by-side across all
regions/product lines on the Revenue Performance page.
