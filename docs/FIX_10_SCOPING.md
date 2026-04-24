# Fix 10 scoping — Layer 2 pipeline in generate_website.py

Status: **open, architectural decision pending.** This memo
captures the reconnaissance and options so the decision does
not get re-derived from scratch next session. It is not a
decision document; it is a working document.

Last updated: 2026-04-19. Author context: reconnaissance via
Claude Code, synthesis in a follow-on session. Both file-level
and cross-repo extraction completed.

## Background

The handoff backlog (`HANDOFF_fix7b_or_beyond.md`) describes
Fix 10 as:

> `generate_website.py` full Layer 2 pipeline, currently only
> `rules_site_structure`. Scope unclear — not examined this
> session.

Reconnaissance in 2026-04-19 session revealed that the one-line
description is under-specified. The real picture is shaped by
two observations the handoff did not surface:

1. **There are two orchestrators, not one.** `generate_website.py`
   in this repo, and `build_from_audit.py` in the sibling
   `website-audit-builder` repo. They have different input
   contracts.
2. **The "full Layer 2 pipeline" already exists — in the other
   orchestrator.** `build_from_audit.py` calls the full
   `generate_layer2()` pipeline. `generate_website.py` calls
   only `rules_site_structure()`. The question is not "build
   the missing pipeline"; it is "reconcile the two paths."

## Current state (grounded, not speculated)

### The two orchestrators

| | `website-sales-audit/execution/generate_website.py` | `website-audit-builder/execution/build_from_audit.py` |
|---|---|---|
| Input | `structured_input.json` (Firecrawl + GBP scrape output) | Audit MD file → `audit_findings.json` via `parse_audit.py` |
| Layer 2 touch | Single call to `rules_site_structure(data)` via importlib inside `_inject_structure_block()` | Full `generate_layer2(findings, business_data)` pipeline, assembling all rules outputs |
| When run | Before the audit (demo pre-sale for cold outreach) | After the audit (production post-sale) |
| Orchestration modes | 5 modes: bolt, lovable, gemini, claude-code, skill-output | Audit-driven (single path) |

### findings_to_layer2.py drift across repos

| | sales-audit copy | builder copy |
|---|---|---|
| Size | 798 lines | 1050 lines |
| Functions | 13 | 17 |
| Extras (builder-only) | — | `rules_booking_tier`, `rules_platform`, `rules_feature_signals`, `rules_icp_framing` |

This is real drift — not sibling-synced like `.shared-templates`
content. Whether the 4 extra functions in builder are net-new
work that never back-ported, or deliberately scope-limited to
the post-audit path, is itself an open question.

### Layered prompt architecture (reference only)

The three-layer architecture is authoritative in
`website-sales-audit/docs/SYSTEM_DESIGN_v2.1.md §The
Three-Layer Prompt Architecture` (lines 346-395). Summary:
Layer 1 is universal rules (`universal_rules.txt`), Layer 2 is
audit-specific rules generated per prospect, Layer 3 is
niche-specific rules (`niches/[trade].md`). Precedence is
L2 > L3 > L1. No reproduction of that content here.

### What `rules_site_structure` does vs. the other 12 functions

`rules_site_structure` emits the SITE STRUCTURE DECISION block
(the `PAGE_MODE:` token consumed by WEBSITE_CLAUDE.md). It is
structural metadata — not content-level rules. The other 12
functions in sales-audit's findings_to_layer2.py
(`rules_first_impressions`, `rules_mobile_experience`,
`rules_contact_booking`, `rules_local_presence`,
`rules_trust_credibility`, `rules_content_clarity`,
`rules_speed`, `rules_photos`, `rules_security`,
`rules_lead_followup`, `apply_structure_rules`, plus the
`generate_layer2` entry point) generate content-derivation
rules that `generate_website.py` never calls.

## The architectural question

**Is the two-orchestrator split intentional or accidental?**

The surface pattern suggests intent: demo-before-sale uses
scrape data only; production-after-sale uses audit findings.
The pre-sale path genuinely cannot consume audit findings
because the audit has not been run yet. This is a coherent
architectural logic.

But the pattern is not rigorous. The demo path could still
generate *more* Layer 2 rules from the scrape data it already
has — ratings, review counts, phone presence, SSL status,
GBP reviews — none of which require a full audit. The fact
that `generate_website.py` calls only `rules_site_structure`
and stops may be deliberate scope-limiting, may be
incomplete-as-shipped, or may be path-of-least-resistance that
nobody revisited.

User's own read: *"partially — there's some intent but I'm
not sure it's fully thought through."* That honesty matters.
Any Fix 10 framing needs to either commit to the intentional
split or treat it as drift to be reconciled.

## Options on the table

All four are live. Each has a different scope shape and
different architectural implications.

### Option A — Shallow audit before demo

Add a fast synthetic or partial-audit step in the sales-audit
demo pipeline. Feed its findings into a full `generate_layer2()`
call. The demo gains richer Layer 2 rules at the cost of added
latency and possibly API cost in the demo pipeline.

**Pros.** Closes the asymmetry between demo and production
outputs; demo sites match production quality. Explicit
coherence: same input shape feeds both orchestrators.

**Cons.** Adds a new pipeline step (shallow audit) that does
not exist today and must be defined. Demo latency increases.
May duplicate work that full-audit does later anyway. Requires
deciding what "shallow" means — which audit signals are cheap
enough to derive at demo time.

**Scope estimate.** Medium-large. 2-3 sessions if including
the shallow-audit definition.

### Option B — Generate Layer 2 from scrape data only

Refactor sales-audit's `findings_to_layer2.py` so its 13
functions (or a subset) can accept `structured_input.json` as
input, not audit findings. The demo uses more Layer 2 rules
without a new audit step.

**Pros.** No new pipeline step. Leverages data already
collected by `extract_business_data.py`. Respects the
demo-before-sale timing constraint. Smallest architectural
change of the four options.

**Cons.** Some Layer 2 rules genuinely depend on audit signals
that scrape data does not contain (e.g., `rules_content_clarity`
triggers on "JS-only build" — an audit detection, not a scrape
field). Not all 13 functions will port cleanly. Requires
per-function triage and possibly splitting each function's
logic into scrape-derivable and audit-only branches.

**Scope estimate.** Medium. One focused session to triage the
13 functions, one session to port the scrape-derivable ones.

### Option C — Consolidate the two orchestrators

Merge `generate_website.py` and `build_from_audit.py` into one
script with a mode flag (demo vs production). Demo mode skips
audit-based rules; production mode uses them.

**Pros.** Eliminates the two-copy findings_to_layer2.py drift
naturally — one orchestrator, one import path. Removes the
architectural ambiguity about which path owns what. Makes
future feature additions land in one place, not two.

**Cons.** Cross-repo refactor. Requires deciding which repo
owns the unified script and how the other becomes a
thin wrapper or gets deprecated. Highest disruption. Risks
breaking the builder's post-audit flow if the refactor is
rushed.

**Scope estimate.** Large. Multi-session. Cross-repo (both
website repos).

### Option D — Close findings_to_layer2.py drift first, defer Fix 10 proper

Resolve the 17 vs. 13 function divergence before any Fix 10
variant ships. Decide: are the 4 builder-only functions
(`rules_booking_tier`, `rules_platform`, `rules_feature_signals`,
`rules_icp_framing`) net-new work that should back-port to
sales-audit, or deliberately post-audit-only and correctly
absent from the demo path?

**Pros.** Every other option operates on cleaner substrate
after D ships. Surfaces the intent-vs-accident question for
the 4 drifted functions, forcing the "intentional split"
question to resolve per-function rather than in the abstract.
Smallest scope of the four.

**Cons.** Does not actually answer the Fix 10 question — it
defers it. Requires a separate planning round afterward to
pick A/B/C.

**Scope estimate.** Small-medium. Single session.

## Provisional recommendation (not locked in)

**D first, then B.** Reasons:

1. **D answers part of the architectural question by forcing
   it.** Deciding per-function whether each of the 4 drifted
   functions belongs in sales-audit or only in builder is a
   concrete version of the "intentional vs accidental split"
   question. Answering it concretely is more tractable than
   answering it abstractly.
2. **B matches the demo path's pre-sale timing constraint
   honestly.** The demo genuinely cannot consume audit
   findings (no audit yet). Generating Layer 2 from scrape
   data is the scope-honest version of "richer demo Layer 2."
3. **A and C are real options but require operational
   evidence to decide.** A's shallow-audit idea depends on
   whether demo output quality improves enough to justify the
   added latency — hard to know without measuring. C's
   consolidation depends on whether the two paths genuinely
   unify or whether the split is real — D's output informs
   that.

This is a preference, not a plan. Future session can override.

## Open questions to resolve before shipping any variant

Before executing A, B, C, or D, answer these:

- **Q1.** Are the 4 builder-only `rules_*` functions
  deliberate (post-audit-only) or accidental drift? (Per-function
  analysis of their internals will answer this.)
- **Q2.** If B: which of the 13 sales-audit functions depend on
  audit-only signals that `structured_input.json` does not
  carry? (Per-function audit of input fields referenced in the
  function body.)
- **Q3.** If A: what is a "shallow audit"? Which signals are
  cheap enough to derive without the full audit pipeline?
  Specifically: which Phase 1 audit steps run without the
  Claude skill?
- **Q4.** If C: which repo owns the unified orchestrator?
  (Builder has the richer pipeline; sales-audit has the
  5-mode output logic. Neither is obviously dominant.)
- **Q5.** Does the existing demo output today feel too thin
  in practice? (If demo output already sells well, the ROI
  case for Fix 10 is weaker and D-only may suffice.)

## What a future session needs before starting

Whichever variant is picked, the next session should:

1. Re-read this memo to re-ground on the state and options
2. Pick A/B/C/D explicitly (do not defer again inside the
   execution session)
3. Work in Claude Code with plan-first gating per the
   established working pattern (see `CLAUDE.md` in
   `ghl-triage` for reference pattern)
4. For B specifically: start with the per-function triage
   (Q2) as a read-only discovery turn before any edits
5. For D specifically: start with per-function analysis of
   the 4 drifted functions (Q1) as a read-only discovery turn

## Verdict (2026-04-19) — Q1 resolved

Q1 answered: the 4 builder-only functions are **all 4 deliberate
post-audit-only**, not drift. Per-function analysis:

| Function | Input source | Verdict |
|---|---|---|
| `rules_booking_tier` | `features.get("booking_tier")` | Deliberate post-audit-only |
| `rules_platform` | `features.get("platform")` | Deliberate post-audit-only |
| `rules_feature_signals` | 7 keys from `features` (ads_pixel, call_tracking, social_media, invoice_payment, financing_widget, membership_plan, appointment_reminder) | Deliberate post-audit-only |
| `rules_icp_framing` | 3 keys from `icp` (icp_strength, decision_maker, sales_cycle) | Deliberate post-audit-only |

All inputs trace back to `findings["feature_detection"]` or
`findings["icp_signals"]`, both produced by `parse_audit.py` —
a module that exists only in `website-audit-builder`. Sales-audit
has no pathway to populate these dicts, so the 4 functions are
structurally unreachable from sales-audit's orchestrator. Nothing
to back-port.

### Architectural implication

The two-orchestrator split is **intentional and correct at the
4-function boundary.** Demo (pre-sale, sales-audit) genuinely
cannot invoke these 4 functions; production (post-sale, builder)
genuinely can. The `findings_to_layer2.py` line-count divergence
(798 vs 1050) is the structural consequence of this correct
split, not accidental drift.

### Side observation — separate drift surfaced

Reconnaissance surfaced one piece of drift in a **shared**
function (`rules_site_structure`): the `NICHE_DEFAULTS` table
has `glass` and `garage_door` entries in builder that are
absent in sales-audit. This is distinct from the 4-function
verdict above and is tracked as a separate follow-up (see
commit message on the follow-up back-port commit).

### Status of A / B / C

- **B** (generate Layer 2 from scrape data only) — still open
  as a future scope option, but independent of the drift
  question. Depends on Q5 (does demo output feel too thin in
  practice?). Not blocked by anything this verdict changes.
- **A** (shallow audit before demo) — still open; independent.
- **C** (consolidate orchestrators) — **weakened** by this
  verdict. The split at the 4-function boundary is real and
  intentional; consolidation would re-introduce the
  reachability question it naturally resolves.

### Memo status going forward

This memo is no longer purely pre-decision. Q1 is closed. Q2-Q5
remain open and scoped to future A / B work. Per the memo's
meta note, when A / B / C ultimately ship (or are explicitly
dropped), this file should be archived or deleted. Until then
it retains provenance.

## Verdict (2026-04-24) — Q5 resolved

Q5 answered: demo output is **not fundamentally thin as a
prospect-facing artifact.** Review of three recent demo outputs
(`output/mrrooter-2026-04-20.md`,
`output/warmandcoollondon-2026-04-20.md`,
`output/mississaugaplumbingservices-2026-04-19.md`) found the
10-area audit grounded in real page evidence, niche-specific
idiom landing through Layer 3, and (on the non-disqualified
case) the full talking-points payload — Feature Detection,
GHL Automation Gap Assessment, Recommended Pitch Tier, ROI
Anchor, Open With, Discovery Questions, Objection Handlers,
5-touch Follow-up Sequence, Close — all substantive.

### Where the thickness is coming from

Three contributors, in rough order of weight:

1. **SKILL.md prompting layer** — the 10-area structure, per-area
   grounding, and talking-points template. Biggest contributor.
2. **Layer 3 niche rules** — trade-specific idiom ("utility
   cupboard for half a day," "burst pipe in a deep freeze").
3. **Layer 2 via the single `rules_site_structure()` call** —
   smallest Layer-2 contribution; absence of the other 12
   `rules_*` functions is not visibly felt in output.

### Implications for A / B / C / D

- **Option A** (shallow audit before demo) — **weakened.** Of
  the weaknesses surfaced in the Q5 review, only one (missing
  real PageSpeed data in AREA 7) sits anywhere near A's scope.
  One signal does not justify adding a new pipeline step.
- **Option B** (Layer 2 from scrape data) — **weakened.** B
  would port `rules_*` functions into the demo path. The review
  did not find their absence as a visible thickness gap. Not
  justified on thickness grounds.
- **Option C** (consolidate orchestrators) — **stays weakened**
  per Q1. Q5 does not rescue it.
- **Option D** (close `findings_to_layer2.py` drift) — **proceeds
  independently as BACKLOG item 2.** D's rationale is drift
  cleanup, not demo thickness. Unaffected by this verdict.

### Overall Fix 10 disposition

A and B are **deferred pending evidence demo output is failing
to sell** (prospect complaints, conversion drop, or comparable
operational signal). If that signal surfaces, reopen A/B with
fresh evidence. D ships as scheduled. C stays dead.

### Enhancement surface surfaced out of scope

The Q5 review also surfaced 16 concrete weaknesses and
enhancement opportunities in current demo output. None are
inside Fix 10 A/B/C/D scope. They land in four buckets:

- **SKILL.md prompt grounding** — ungrounded claims (e.g.
  "branded uniforms appear real" on a page with no readable
  content), generic-feeling ROI framing, weighting of quick-wins.
- **Feature-detection fidelity** — UNKNOWN rows for ads pixel,
  structured data, appointment reminders, invoice tool; missing
  real PageSpeed data.
- **Output schema** — rubric opacity (32/62/83 scores unaudited),
  disqualified-case N/A boilerplate, format drift between recent
  demos, TRIAGE_META / triage-meta YAML duplication.
- **Sales-artifact enhancements** — structured competitor
  benchmarking section, before/after mockup tie-in with bullet
  previews, direct link to prospect's own Google reviews.

These have been captured as new BACKLOG items in the 3-repo
drift cleanup and are not Fix 10 work.

### Enumerated findings (W1–W10, E1–E6)

Ten concrete weaknesses (W) and six enhancement opportunities (E)
surfaced during the Q5 review. Referenced by code from BACKLOG
items 9–12.

**Weaknesses:**

- **W1. Mobile Speed Score always "Not available."** AREA 7 emits
  this uniformly across recent demos; no real PageSpeed data pulled.
  Either wire up the fetch or remove the scored area.
- **W2. Multiple UNKNOWN rows in FEATURE DETECTION SUMMARY.** Ads
  pixel, appointment reminder system, invoice/payment tool,
  LocalBusiness structured data, Service/Review structured data —
  all commonly UNKNOWN. Either detect properly or drop the row.
- **W3. Health score (32/62/83) emitted without rubric.** Operator
  or prospect cannot reconstruct how the number was reached.
- **W4. Disqualified-prospect outputs include full N/A-degraded
  talking-points blocks.** Feature Detection → Tier → ROI → Hook all
  emit as "N/A — disqualified" stanzas. Visual noise; should skip to
  Disqualification Note.
- **W5. Hallucinated-or-unverified competitor stat.** The
  mississaugaplumbingservices demo inline-cites "Mr Rooter Mississauga
  — 2,000+ Google reviews" in an objection handler. Provenance not
  auditable from the pipeline. Grounding-hygiene concern.
- **W6. Format drift between 2026-04-19 and 2026-04-20 outputs.**
  Numbered vs bulleted quick-wins; differing disqualification-note
  structure. Not a regression — more that the output shape isn't
  versioned.
- **W7. `_test_applicability_*` files in `output/` dir.** 2026-04-18,
  fixture-shaped, local-only. Verified gitignored (`output/*.md`).
  Not a repo concern. Closed inline during Q5 review.
- **W8. Ungrounded claim about imagery authenticity.** The mrrooter
  demo asserts "photos appear to feature real service professionals
  in branded uniforms" on a national franchise corporate page with
  JS-shelled content the audit could not have read imagery from.
  Grounding failure.
- **W9. Quick-wins weighting nit.** The warmandcoollondon demo lists
  "add the copyright year to the footer" as a quick-win alongside
  high-impact items like response-time promises. Cosmetic nit given
  equal weight to substantive asks.
- **W10. TRIAGE_META HTML comment + triage-meta fenced YAML both
  present.** Overlapping fields across both. Reads as duplicated
  metadata; may have an intentional separation but unclear.

**Enhancements:**

- **E1. Structured competitor benchmarking section.** One real
  competitor, same city/trade, with their actual review count,
  detected platform, and feature-detection stacked against the
  prospect's. Replaces the W5 one-off inline stat.
- **E2. Before/after mockup tie-in with bullet previews.** The
  closing "I can put together a quick sketch" currently has no
  preview. Including 3 bullet-point previews of what the sketch
  would show strengthens the close.
- **E3. Direct link to prospect's own Google reviews** where the
  audit cites a review count. Reinforces "I looked at your actual
  reviews" — currently the citation is unverifiable at a glance.
- **E4. Trade-specific ROI anchoring.** Current ROI framing is
  generic per trade ($200–$800 plumbing call). Routing ROI through
  Layer 3 niche rules would carry the same trade-specific weight as
  the rest of the demo's idiom.
- **E5. Roll AREA 7 (Speed) into AREA 2 (Mobile Experience) unless
  real data pulled.** If W1 is closed by wiring up PageSpeed, AREA 7
  earns its keep. If not, consolidating reduces structural overhead.
- **E6. Output schema version / changelog comment.** Small metadata
  field (e.g., `output_schema: "1.0"` in the triage-meta YAML) to
  track when the output shape changes. Helps future sessions read
  older outputs consistently.

### Memo status going forward

Q1 and Q5 are now closed. Q2, Q3, Q4 remain open and scoped
to the specific option they support (Q2 → B, Q3 → A, Q4 → C).
With A/B deferred and C dead, Q2/Q3/Q4 are effectively dormant
unless the deferral condition on A/B is triggered.

Fix 10 as a named item is **effectively resolved at the
scoping level.** Option D ships as BACKLOG item 2. This memo
should be archived or deleted once item 2 lands, per the
"Meta note" section at the head of this file.

## Related references

- `website-sales-audit/docs/SYSTEM_DESIGN_v2.1.md §The
  Three-Layer Prompt Architecture` — authoritative layered
  architecture spec
- `website-sales-audit/SYSTEM_CONTEXT.md §Layer 1 / Layer 2 /
  Layer 3` — parallel definition, slightly shorter
- `website-sales-audit/execution/generate_website.py` — demo
  orchestrator (5 modes, minimal Layer 2 use)
- `website-audit-builder/execution/build_from_audit.py` —
  production orchestrator (full Layer 2 pipeline, audit-driven)
- `website-sales-audit/execution/findings_to_layer2.py` — 13
  functions, 798 lines
- `website-audit-builder/execution/findings_to_layer2.py` — 17
  functions, 1050 lines (drifted from sales-audit copy)
- `ghl-triage/ARCHITECTURE.md §7 Future work and known gaps` —
  high-level pointer to Fix 10 in the 3-repo overview

## Meta note

This memo is a scoping artifact, not a spec. It is expected to
be short-lived: once Fix 10 (in whatever variant) ships, this
file should either be deleted, archived under a "resolved
scoping" directory, or referenced-back from the Fix 10 commit
and left for provenance. Future-you or a future session should
not treat it as a durable contract the way BCRO/DESIGN/SKILL.md
are.
