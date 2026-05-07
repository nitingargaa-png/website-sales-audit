# Animo Automation v1.1 — CRO Wave Tracker

**Project:** TRIAGE_META v1.0 → v1.1 schema bump + page-mode decision +
lead-leakage estimation + section-architecture (Layer 2.5) + HighLevel
builder mode + accessibility/performance scoring + before/after detection +
post-launch measurement SOP.

**Goal:** Close gaps surfaced by the ChatGPT "AI CRO Operating System"
review against the three-repo codebase, scoped to actionable items aligned
with the $10K/mo recurring revenue target.

**Started:** [DATE — fill in when Wave 0 lands]
**Target completion (pre-paid-client scope):** [DATE — fill in]
**Source analysis:** Deliverable 1 (granular comparison) + Deliverable 2
(implementation plan) — see conversation thread or copy to
`docs/V1_1_DELIBERATIONS.md` if you want a permanent record.

---

## Project structure

- **A + C combined.** Tracker doc (this file) is the single source of truth
  for status. Per-repo feature branches do the work.
- **Branches:** `feature/v1.1-cro` in all three repos (website-sales-audit,
  website-audit-builder, ghl-triage). Cut from main; merge back after each
  wave is shipped + tested.
- **Commit granularity:** One commit per file pair. Each wave lands in 3–6
  commits across one or more repos.
- **Execution medium:** Claude Code on Windows box, using the per-wave
  execution package as spec. Operator drives the edits; tracker captures
  the result.

---

## Status legend

- ⬜ **Not Started** — wave not yet begun
- 🟦 **In Progress** — wave actively being worked
- 🟧 **Blocked** — wave cannot proceed; reason in Notes column
- 🟨 **Shipped — Pending Test** — code committed, tests not yet run
- ✅ **Shipped — Verified** — committed + tested + done-criteria met
- ⏸️ **Deferred** — out of current scope, target post-paid-client
- ❌ **Cancelled** — explicitly de-scoped

---

## Wave status — current scope (pre-paid-client)

| # | Wave | Status | Repos touched | Est. hours | Done | Notes |
|---|---|---|---|---|---|---|
| 0 | TRIAGE_META v1.0 → v1.1 schema bump | ⬜ | wsa, wab, gt | 2 | / | Prerequisite for Waves 2, 3, 5, 7 |
| 1 | TRIAGE_META schema contract test | ⬜ | gt | 2 | / | Validates Wave 0; locks contract for future bumps |
| 2 | Page-mode decision (M1) | ⬜ | wsa, wab | 4 | / | Adds `recommended_page_mode` + `--page-mode` flag |
| 3 | Lead-leakage estimation ($) | ⬜ | gt | 5 | / | New Step 7.5 in prospect_triage.py; sales-internal |
| 9 | Post-launch measurement SOP | ⬜ | wsa | 3 | / | Pure SOP, no code; unblocks cold email Step 2 case study |

**Total estimated effort (current scope):** 16 hours

**Critical path:** 0 → 2 (others ship in parallel after Wave 0)

---

## Wave status — deferred (post-paid-client)

| # | Wave | Status | Reason for deferral | Trigger to revisit |
|---|---|---|---|---|
| 4 | Per-trade page-mode conventions (M4) | ⏸️ | Wave 2 has fallback to "single"; per-trade conventions are refinement | Ship after Wave 2 if page-mode recommendations feel off |
| 5 | Before/after Playwright detection | ⏸️ | High-risk wave; Playwright dependency + JS-rendered detection accuracy | Verify on 3 known before/after sites first; then ship |
| 6 | Accessibility/performance scoring | ⏸️ | Health score works; rebalance non-critical | Ship after dry-run rebalance on all 6 existing audits |
| 7 | Layer 2.5 section-architecture (M2) | ⏸️ | Most complex wave; current implicit section logic adequate | Ship when first paid client requires custom section list |
| 8 | HighLevel AI Studio builder mode | ⏸️ | Bolt mode adequate for current demos; HL value unlocks at 3+ DFW clients | Ship when 3+ paid clients on GHL |

---

## Wave status — explicitly out of scope

| Item | Reason |
|---|---|
| Component library (Part 11 ChatGPT) | Bucket-3 push-back; deferred until 10+ paying clients |
| ICE/RICE prioritization | Already covered by health score + tier classification |
| Lovable / v0 / Cursor / Replit AI builder modes | Maintenance tax, no client demand |
| "Operating System" rebrand | Framing inflation, no real change |
| Cross-trade conventions doc (M8) | Adequate at current scale |
| Audit observability doc (M6) | Flagged for later, not committed |

---

## Per-wave detail

### Wave 0 — TRIAGE_META v1.0 → v1.1 schema bump

**Status:** ⬜ Not Started
**Branch:** `feature/v1.1-cro` (all three repos)
**Spec:** Deliverable 2 §"WAVE 0"
**Execution package:** [pending — produced when wave begins]

**Files touched:**
- [ ] `website-sales-audit/docs/SKILL.md` — bump schema_version, add 3 fields, add expanded definitions
- [ ] `website-sales-audit/docs/WEBSITE_CLAUDE.md` — mirror schema additions (parity-enforced)
- [ ] `website-audit-builder/docs/WEBSITE_CLAUDE.md` — same (mirrored copy)
- [ ] `ghl-triage/triage/audit_parser.py` — read 3 new fields with null fallback
- [ ] `website-audit-builder/execution/parse_audit.py` — same
- [ ] `website-sales-audit/docs/fixtures_golden.md` — update fixtures with 3 new fields as null

**Done criteria:**
- [ ] All v1.0 audits parse cleanly with new fields as `null`
- [ ] Hand-edited v1.1 fixture round-trips correctly through both parsers
- [ ] Parity hook passes (`tools/check_template_parity.py`)
- [ ] `git diff` shows zero behavior change in CSV output for existing audits

**Commits:**
- [ ] [hash] — wsa: SKILL.md schema bump v1.0 → v1.1
- [ ] [hash] — wsa+wab: WEBSITE_CLAUDE.md mirror (parity)
- [ ] [hash] — gt: audit_parser.py tolerant fallback for v1.1 fields
- [ ] [hash] — wab: parse_audit.py tolerant fallback for v1.1 fields
- [ ] [hash] — wsa: fixtures_golden.md add v1.1 fixtures

**Test runs:**
- [ ] creedplumbing v1.0 → audit_parser.py — pass / fail / [output]
- [ ] mississaugaplumbingservices v1.0 → audit_parser.py — pass / fail / [output]
- [ ] mrrooter v1.0 → audit_parser.py — pass / fail / [output]
- [ ] hand-edited v1.1 fixture → both parsers — pass / fail / [output]
- [ ] ghl-triage --from-audit on v1.0 vs v1.1 — same CSV output? yes / no / [diff]

**Blockers:** None
**Started:** [DATE]
**Shipped:** [DATE]

---

### Wave 1 — TRIAGE_META schema contract test

**Status:** ⬜ Not Started
**Branch:** `feature/v1.1-cro` (ghl-triage only)
**Spec:** Deliverable 2 §"WAVE 1"
**Prerequisite:** Wave 0 shipped + verified
**Execution package:** [pending]

**Files touched:**
- [ ] `ghl-triage/tests/audit_mode/test_triage_meta_schema.py` — new test file
- [ ] `ghl-triage/tests/fixtures/triage_meta_v1_0.md` — new fixture
- [ ] `ghl-triage/tests/fixtures/triage_meta_v1_1_full.md` — new fixture
- [ ] `ghl-triage/tests/fixtures/triage_meta_v1_1_nulls.md` — new fixture
- [ ] `ghl-triage/CLAUDE.md` — document new test file in File responsibilities table

**Done criteria:**
- [ ] All three test cases pass against current parser
- [ ] Test runnable via `pytest tests/audit_mode/test_triage_meta_schema.py`
- [ ] Documented in CLAUDE.md

**Commits:**
- [ ] [hash] — gt: schema contract test + 3 fixtures

**Blockers:** None (after Wave 0)
**Started:** [DATE]
**Shipped:** [DATE]

---

### Wave 2 — Page-mode decision (M1)

**Status:** ⬜ Not Started
**Branch:** `feature/v1.1-cro` (wsa + wab)
**Spec:** Deliverable 2 §"WAVE 2"
**Prerequisite:** Wave 0 shipped + verified
**Execution package:** [pending]

**Files touched:**
- [ ] `website-sales-audit/docs/SKILL.md` — new Phase 2 sub-step §"Page Mode Recommendation"
- [ ] `website-sales-audit/docs/WEBSITE_CLAUDE.md` — document v1.1 fields with detection notes (parity)
- [ ] `website-audit-builder/docs/WEBSITE_CLAUDE.md` — same (mirrored)
- [ ] `website-audit-builder/execution/build_from_audit.py` — add `--page-mode` argparse arg + resolution order
- [ ] Output: prompt package gains `PAGE_MODE: single|multi` line in header

**Done criteria:**
- [ ] Recommendation emits correctly on 3 test prospects spanning trades
- [ ] Override flag wins over recommendation (logged as "operator-override")
- [ ] Auto mode falls through to niche default cleanly
- [ ] v1.0 audits don't crash the builder

**Commits:**
- [ ] [hash] — wsa: SKILL.md Phase 2 page-mode logic
- [ ] [hash] — wsa+wab: WEBSITE_CLAUDE.md schema docs (parity)
- [ ] [hash] — wab: build_from_audit.py --page-mode flag

**Test runs:**
- [ ] HVAC prospect (4+ services, 100+ reviews) → recommended "multi" / [actual]
- [ ] Plumber (3 services, low reviews) → recommended "single" / [actual]
- [ ] --page-mode multi override on single-recommended prospect → builds multi / [actual]
- [ ] v1.0 audit + --page-mode auto → falls to "single" fallback / [actual]

**Blockers:** None (after Wave 0)
**Started:** [DATE]
**Shipped:** [DATE]

---

### Wave 3 — Lead-leakage estimation ($)

**Status:** ⬜ Not Started
**Branch:** `feature/v1.1-cro` (ghl-triage only)
**Spec:** Deliverable 2 §"WAVE 3"
**Prerequisite:** Wave 0 shipped + verified
**Execution package:** [pending]

**Files touched:**
- [ ] `ghl-triage/triage/leakage_estimator.py` — new module
- [ ] `ghl-triage/prospect_triage.py` — insert Step 7.5 between scoring and tier classification
- [ ] `ghl-triage/triage/signal_maps.py` — add LEAKAGE_FACTORS (TRADE_JOB_VALUE, missed-call tiers)
- [ ] `ghl-triage/triage/output.py` — add `estimated_monthly_leakage_usd` column to CSV writer
- [ ] `ghl-triage/triage/talking_points.py` — pass leakage figure into Haiku prompt
- [ ] `ghl-triage/docs/GHL_TRIAGE_DESIGN_v2.3.md` — document Step 7.5 in §10 architecture
- [ ] `ghl-triage/CLAUDE.md` — update File responsibilities + critical rules

**Done criteria:**
- [ ] Step 7.5 runs on every triage row (live mode + --from-audit mode)
- [ ] CSV has new column populated (or empty for null)
- [ ] Talking points reference figure when present
- [ ] Unit tests pass; numbers plausible against creedplumbing fixture
- [ ] `null` when GBP review count missing (no fabricated number)

**Commits:**
- [ ] [hash] — gt: leakage_estimator module + signal_maps factors
- [ ] [hash] — gt: prospect_triage Step 7.5 integration
- [ ] [hash] — gt: output.py CSV column + talking_points Haiku prompt
- [ ] [hash] — gt: design doc + CLAUDE.md updates

**Test runs:**
- [ ] Plumber 50 reviews → leakage in $1,800–$2,800 range / [actual]
- [ ] Roofer 200 reviews → leakage in $14,000–$20,000 range / [actual]
- [ ] Cleaner 10 reviews → leakage in $200–$400 range / [actual]
- [ ] No GBP review count → null / [actual]
- [ ] CSV column present and populated → [confirmed]
- [ ] Talking point references figure → [confirmed]

**Blockers:** None (after Wave 0)
**Started:** [DATE]
**Shipped:** [DATE]

---

### Wave 9 — Post-launch measurement SOP

**Status:** ⬜ Not Started
**Branch:** `feature/v1.1-cro` (website-sales-audit only)
**Spec:** Deliverable 2 §"WAVE 9"
**Prerequisite:** None (independent)
**Execution package:** [pending]

**Files touched:**
- [ ] `website-sales-audit/docs/POST_LAUNCH_MEASUREMENT_v1.md` — new SOP doc
- [ ] `website-sales-audit/docs/GHL_SETUP_CHECKLIST_v3.md` — add reference at "30 days post go-live" section
- [ ] `website-sales-audit/EXECUTION_GUIDE.md` — add post-launch measurement to operating sequence

**Done criteria:**
- [ ] Doc exists with full SOP structure (pre-flight → day 30 data pull → delta calculation → output)
- [ ] GHL_SETUP_CHECKLIST references it
- [ ] Walk-through with hypothetical mississaugaplumbingservices day-30 data produces coherent 1-page delta report

**Commits:**
- [ ] [hash] — wsa: POST_LAUNCH_MEASUREMENT_v1 SOP
- [ ] [hash] — wsa: GHL_SETUP_CHECKLIST + EXECUTION_GUIDE references

**Blockers:** None
**Started:** [DATE]
**Shipped:** [DATE]

---

## Schema migration log

### v1.0 → v1.1

**Bumped in:** Wave 0
**Date:** [DATE]
**New fields:**
- `recommended_page_mode` — enum: "single" | "multi" | null. Emitted by SKILL.md (Wave 2).
- `page_mode_reasoning` — string | null. Sales-internal one-liner explaining the recommendation. Emitted by SKILL.md (Wave 2).
- `estimated_monthly_leakage_usd` — int | null. Sales-internal $ estimate of monthly lead leakage. **Asymmetric: SKILL.md emits null; ghl-triage Step 7.5 populates** (Wave 3).
- `has_before_after_content` — bool | null. Emitted by SKILL.md via Playwright detector (Wave 5, deferred).

**Migration pattern:** Parallel-write. Both consumers (audit_parser.py + parse_audit.py) tolerate v1.0 audits with null defaults for v1.1 fields.

**Backward compatibility:** v1.0 audits parse correctly with v1.1 parser. v1.1 audits with null fields parse correctly. v1.1 audits with populated fields parse correctly.

---

## Backlog (post-paid-client surfaced items)

Items that surfaced during v1.1 work but don't fit the current scope. Move to active waves when triggered.

- [Empty — populate during execution]

---

## Daily log

(Operator: append entries as you work. Format: `### YYYY-MM-DD` then notes.)

### [DATE — first entry placeholder]

- v1.1 project kicked off. Tracker created. Beginning Wave 0.
