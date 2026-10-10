Architect Alignment Charter --- Product Operability & End-to-End Capability
Northwind Autonomous CFO Office

Purpose: Permanent alignment document between the Program Manager / Project Advisor and Architect.
Status: Active
Architect role: Architecture authority
PM role: Product / roadmap / journey / governance authority

1. Why this document exists

The project has reached a point where implementation completeness and product completeness must be kept explicitly separate.

The PM will review the product as a Controller, CFO, FP&A user, administrator and demonstrator. The Architect must use those findings as product constraints and architectural inputs, while retaining full responsibility for architecture.

This document does not transfer architecture ownership to the PM.

It establishes a shared operating boundary:

The PM defines and challenges the business capability, user journey, priorities and acceptance intent.
The Architect determines how that capability should be represented architecturally and identifies architectural consequences, conflicts and constraints.

2. Non-negotiable principles
Business capability must define implementation; implementation must not silently define business capability.
The application must expose and operate the capabilities that are intentionally part of the product.
Documentation must not specify a future capability that cannot be operated through the intended application workflow.
A technical mechanism is not evidence of complete business capability.
Granularity is an intentional product and architecture decision.
Dataset and period lifecycle must be explicit.
Outputs are product artifacts with storage, versioning and retrieval semantics.
Configuration must distinguish business policy from analytical definition and technical constants.
Deterministic financial truth remains deterministic.
LLMs must not become financial truth, calculation authority, invention authority, modification authority or override authority.
Independent verification remains distinct from Builder testing.
GitHub main remains the canonical source of truth.
Repository organization serves delivery; it is not itself a product milestone.
3. PM → Architect input contract

When the PM raises an open product item, the Architect should receive:

business capability;
primary user;
business question;
intended user outcome;
current observed behaviour;
intended behaviour;
known constraints;
known exclusions;
affected financial areas;
relevant dimensions;
required grain;
workflow dependencies;
data lifecycle implications;
period lifecycle implications;
configuration implications;
output implications;
validation / approval implications;
regression implications;
known uncertainty;
specific decisions requested from Architecture.

The PM should not prescribe implementation unless an existing architectural or governance decision already requires it.

4. Architect response contract

For each material item, return:

Decision

What Architecture recommends.

Canonical implementation finding

What the current canonical implementation actually does, where verified.

Architectural impact

What components, data models, workflows or interfaces are affected.

Required changes

What must change, with boundaries.

No-change findings

What should remain untouched.

Conflicts

Any conflict with existing decisions or canonical behaviour.

Documentation changes

What documents must be synchronized.

Builder implications

Only after the capability and architecture are sufficiently defined.

UAT implications

What must be independently verified.

Governance state

Planned / In Progress / Built / Tested / Independently Verified / Architect Reviewed / Accepted / Canonical / Deferred / Blocked / Decision Needed / Uncertain.

Do not silently convert a PM product question into an implementation task.

5. End-to-end capability map

Architecture review must support this complete journey:

Company / workspace setup
Dataset intake and storage
Period lifecycle
Analytical rules and thresholds
Observation generation
Controller commentary
Commentary reconciliation
Evidence / validation
Finance / CFO review
Human approval
HTML output
Board deck / PPTX output
Period closure and archival
Re-running / correction
Navigation, status, errors and discoverability
Demo / play-with-the-product

For every capability, architecture should identify: - system state; - data ownership; - persistence; - versioning; - permissions / role implications; - transitions; - failure modes; - recovery; - audit/history; - UI/API boundary; - output boundary; - testability.

6. Configuration architecture

The intended application configuration areas are:

Company;
Dataset;
Period;
Analytical Rules;
Thresholds;
Output Settings.

Architecture should explicitly classify each configurable item as:

Business policy

User / authorized finance configuration.

Governed analytical definition

Centrally defined or controlled; not necessarily freely editable.

Technical constant

Developer-controlled.

Do not make a value configurable merely because it is currently hardcoded.

The architecture should make it possible to expose genuine business policies without requiring code changes, while preventing uncontrolled modification of core financial definitions.

7. Analytical Rules & Risk Detection

Architecture should treat Analytical Rules & Risk Detection as a first-class capability.

The purpose is not merely to detect a threshold breach.

It is to support:

identification of financial movements, relationships and patterns that may warrant investigation.

Potential signals include: - absolute variance; - percentage variance; - direction; - persistence / trend; - absolute materiality; - expense as % of revenue; - change in expense relative to change in revenue; - reversals; - cross-metric relationships; - dimension-level anomalies.

The Architect must not assume these are automatically approved requirements.

Each candidate must be classified: - approved requirement; - implied dependency; - genuine gap; - candidate improvement; - decision needed; - deferred / out of scope.

The architecture must preserve the downstream chain:

signal → rule → observation → commentary → reconciliation → evidence validation → review → approval → executive output.

8. Observation model

Do not assume Department × Category is universal.

Architecture review must explicitly consider whether the intended product needs coverage for: - Revenue; - Revenue by Region / Product; - Expenses; - Salaries & Benefits; - Headcount; - Efficiency; - Margins / profitability; - operational drivers.

For each intended observation define: - source grain; - calculation grain; - detection grain; - observation grain; - commentary reference grain; - validation grain; - approval grain; - reporting grain.

Different grains are acceptable when intentional and documented.

9. Period and dataset lifecycle architecture

The architecture must explicitly model lifecycle states rather than solving lifecycle gaps with isolated UI actions.

At minimum, investigate:

dataset imported → validated → associated with period → processed → reviewed → approved → closed → archived

and, where business policy permits:

closed → reopened → corrected / replaced → reprocessed → reviewed → approved → closed

For each transition define: - actor; - permission; - prerequisite; - state transition; - data version; - observation consequences; - commentary consequences; - approval consequences; - generated-output consequences; - audit/history consequences.

A "reopen" action is therefore not considered complete until its downstream effects are defined.

10. Commentary lifecycle

Architecture review must account for commentary as a persistent business artifact.

Define: - creation; - editing; - association with observation; - reconciliation; - validation result; - approval relationship; - versioning; - retention; - period closure; - reopening; - archival; - invalidation / regeneration after rerun.

The existing product rule of one observation → one commentary must remain explicit unless a separately approved decision changes it.

11. Output lifecycle

HTML and Board deck / PPTX outputs must have defined product semantics.

Architecture must identify: - generation trigger; - storage location; - naming; - period / dataset association; - version; - current versus historical output; - retrieval; - replacement; - archival; - behaviour after rerun; - relationship to approval.

"Generated successfully" is not sufficient product behaviour if the user cannot reliably find and distinguish the resulting artifact.

12. AI boundary

The LLM is currently lower priority than product operability.

Architecture should preserve the established boundary: - deterministic financial analysis remains authoritative; - LLM does not calculate financial truth; - LLM does not invent observations; - LLM does not modify financial facts; - LLM does not override validation; - semantic reconciliation operates only where the defined deterministic conditions leave unresolved commentary / observations; - degraded behaviour must be explicit for unavailable API key, API failure and invalid response.

AI sophistication must not delay correction of missing setup, lifecycle, configuration, workflow or output capabilities.

13. Review order

The PM and Architect will work through open items in this order:

Company / workspace setup
Dataset intake and storage
Period lifecycle
Analytical rules and thresholds
Observation generation
Controller commentary
Commentary reconciliation
Evidence / validation
Finance / CFO review
Human approval
HTML output
Board deck / PPTX
Period closure and archival
Re-running / correcting
Navigation / status / errors / discoverability
Demo / play-with-the-product

The purpose is to prevent late discovery of dependencies.

14. Change classification

Every Architect review must classify findings as one of:

NO CHANGE REQUIRED
CHANGE REQUIRED --- ADOPT
CONFLICT IDENTIFIED
DOCUMENTATION-ONLY --- NO IMPLEMENTATION IMPACT
DEFERRED --- OUT OF SCOPE
DECISION NEEDED

A recommendation is not an approved implementation task until the appropriate governance decision exists.

15. Builder boundary

The Architect remains responsible for turning approved capability into an implementation-ready Builder Brief.

The Builder Brief must contain: - exact behaviour; - acceptance criteria; - boundaries; - non-goals; - dependencies; - failure/degraded behaviour; - affected existing behaviour; - regression requirements; - evidence required.

The Builder should not have to infer product requirements from architectural prose.

16. Verification boundary

Builder tests demonstrate implementation behaviour.

They do not constitute independent verification.

For material capabilities: - Builder implements; - independent UAT verifies; - Architect reviews architectural conformity; - PM verifies that the delivered capability solves the intended product/user problem.

A capability should not be described as complete merely because it passes its Builder tests.

17. Canonical synchronization

When a decision changes product capability, synchronize the relevant canonical documentation.

At minimum consider: - Project Handbook; - Architect documentation; - Builder Brief; - UAT / acceptance criteria; - continuity / governance record.

Do not create competing sources of truth.

18. Working relationship

The PM may challenge: - architecture; - scope; - sequencing; - missing capabilities; - assumptions; - granularity; - configuration choices; - lifecycle design.

The Architect may challenge: - PM assumptions; - feasibility; - architectural coherence; - data integrity; - security / governance; - unintended consequences; - unnecessary scope.

Neither role should silently take over the other.

The desired relationship is:

PM asks: "Is this the right product capability, for the right user, at the right time?"

Architect asks: "What is the correct architecture to support that capability safely and coherently?"

Builder asks: "What exactly am I authorized to implement?"

Independent Test asks: "Does it actually work as specified?"

19. Immediate shared objective

The immediate objective is:

Make the current CFO workflow a coherent, operable product from setup through final executive output before optimizing AI sophistication.

The next milestone is therefore a Product Operability & End-to-End Capability Review, followed by authorized architectural decisions and implementation work.

The goal is not to produce more files.

The goal is to remove ambiguity before implementation and prevent rework.