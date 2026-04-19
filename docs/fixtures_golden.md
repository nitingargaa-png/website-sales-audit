# Golden audit fixtures

This file pins expected `TRIAGE_META` values for a small set of real
prospect URLs that collectively span the decision-space edges of the
website-sales-audit skill. Each fixture records a URL, a rationale for
why that URL tests a specific edge, and the expected values the audit
should produce for that URL per the current `SKILL.md` grounding rules
(Fix 7b Phase E as of commit `d3b1170`).

The fixtures are the reference side of a manual smoke test: run the
audit against each URL, tail the saved `TRIAGE_META` block, and diff
against the expected block here. Any mismatch is either a fixture bug,
a SKILL.md rule gap, or a real audit regression — the diff tells you
which. The smoke test itself is not yet run; see the "Smoke test
procedure" section at the bottom of this file.

This file is additive to SKILL.md and WEBSITE_CLAUDE.md and does not
duplicate rule content — it ties expected outputs to specific inputs.

## Schema reference

The audit emits a `triage-meta` fenced code block at the end of each
saved audit report. The current schema (v1.0):

```yaml
schema_version: "1.0"           # pinned; bump on breaking changes
audit_generated_at: "..."        # ISO 8601 UTC timestamp
business_name: "..."             # extracted in Phase 1 Step 3
business_url: "..."              # canonical audited URL
trade: plumbing                  # one of the supported trades
ghl_upgrade_candidate: false     # lateral-migration signal (Fix 5a)
mctb_applicable: true            # missed-call text-back fit
vaai_applicable: true            # voice AI agent fit
disqualifiers: []                # list of disqualifier enum strings
```

The four fields that fixtures primarily pin are `mctb_applicable`,
`vaai_applicable`, `disqualifiers`, and `ghl_upgrade_candidate`.
`schema_version` and `trade` are stable but included in expected
blocks. `audit_generated_at`, `business_name`, and `business_url` are
non-fixture values — they vary per run and are not diffed.

## Fixture 1 — Applicable baseline (single-location SMB, Canada)

**URL:** `https://mississaugaplumbingservices.com/`

### Rationale

Single-location plumbing SMB in Mississauga, Ontario. Owner-operated,
166 Google reviews at 4.9 stars, SiteBuilder build with no FSM vendor,
no franchise language, no enterprise signals, and visible 24/7 emergency
language paired with no chat widget and no automated booking. This is
the canonical "yes to both" case: every `mctb_applicable: true` signal
the rules look for is present, and the small-shop operator profile
combined with sustained review velocity satisfies `vaai_applicable: true`
as well. No disqualifier fires. Not on GHL, so `ghl_upgrade_candidate`
is false. This fixture guards against regressions that would suppress
applicability flags on the cleanest possible applicable prospect.

### Expected values

Taken verbatim from the real saved audit dated 2026-04-17
(`output/mississaugaplumbingservices-2026-04-16.md`):

```yaml
schema_version: "1.0"
business_name: "Mississauga Plumbing Services"
business_url: "https://mississaugaplumbingservices.com"
trade: plumbing
ghl_upgrade_candidate: false
mctb_applicable: true
vaai_applicable: true
disqualifiers: []
```

### Source

Real audit run, not predicted. The `audit_generated_at` timestamp in
the source file is `2026-04-17T02:43:37Z`.

## Fixture 2 — National chain disqualifier (franchise corporate)

**URL:** `https://www.mrrooter.com/`

### Rationale

Mr. Rooter Plumbing corporate site — a Neighborly company, with an
"Own a Franchise" navigation CTA, "Each location is independently
owned and operated" disclosure in the footer, and the IFA (International
Franchise Association) logo. This is the textbook pattern the
`national_chain` rule looks for: visible franchise disclosure on the
page, not merely a brand-sounding name. The page also lists service
across the entire United States, which independently satisfies the
"3+ states/regions" variant of the rule. Trade is plumbing. This
fixture tests that the disqualifier fires cleanly on the most
unambiguous possible case. The mctb/vaai flags are emitted as `null`
per the rules: the corporate page exposes no small-shop operator
profile, no FSM vendor signature, no review velocity proxy (reviews
are routed to franchisee-level pages behind a ZIP code gate), and no
after-hours gap signals — the rules say to emit `null` when signals
are mixed or genuinely unobservable rather than guessing.

### Expected values

Predicted from SKILL.md grounding rules as of Fix 7b Phase E; not yet
smoke-tested:

```yaml
schema_version: "1.0"
business_name: "Mr. Rooter Plumbing"
business_url: "https://www.mrrooter.com"
trade: plumbing
ghl_upgrade_candidate: false
mctb_applicable: null
vaai_applicable: null
disqualifiers:
  - national_chain
```

### Source

Predicted from rules, not from a saved audit. See the "Known gap"
section below regarding the `null` values on the applicability flags
when a disqualifier fires — this prediction follows the literal rule
text in SKILL.md. Actual audit runtime behavior may differ; the smoke
test resolves.

## Fixture 3 — Out-of-service-area disqualifier (UK)

**URL:** `https://warmandcoollondon.co.uk/`

### Rationale

HVAC business based in London, UK. `.co.uk` TLD, "Warming London
homes since 2007" tagline, UK-specific product mentions (Vaillant
boilers, the Boiler Upgrade Scheme grant, Heat Geek accreditation).
Phase 1 Step 3 extracts London as city and UK as country
unambiguously, with no countervailing US/Canada branch or service
area mentioned. This is the binary-clean case for the
`out_of_service_area` rule: not US/Canada, no head-office edge case
to adjudicate, no ambiguity in the extracted city/country pair. Trade
is HVAC (boilers, heat pumps, air conditioning). As with Fixture 2,
the mctb/vaai flags are emitted as `null` per literal SKILL.md
behavior when a disqualifier fires.

### Expected values

Predicted from SKILL.md grounding rules as of Fix 7b Phase E; not yet
smoke-tested:

```yaml
schema_version: "1.0"
business_name: "Warm & Cool London"
business_url: "https://warmandcoollondon.co.uk"
trade: hvac
ghl_upgrade_candidate: false
mctb_applicable: null
vaai_applicable: null
disqualifiers:
  - out_of_service_area
```

### Source

Predicted from rules, not from a saved audit. Same caveat as Fixture
2 regarding `null` applicability flags.

## Deferred — Tier 3 FSM counter-signal

The original Phase F scope (per `HANDOFF_phase_F.md`) called for a
fourth fixture exercising the `mctb_applicable: false` /
`vaai_applicable: false` branch, keyed on ServiceTitan Tier 3 booking
with SMS consent embedded in the flow. No URL was identified during
the Phase F drafting session where this signal is visible in static
page content — the Tier 3 signal requires inspecting the rendered
booking widget's iframe source, which static fetches do not surface.
Candidate URLs considered (`dallasplumbing.com`, `ogd.com`,
`precision-door.com`) did not expose the required signal in their
homepage markup.

This fixture is deferred to a follow-up session in which the booking
widget can be inspected in a live browser. When added, the expected
block should look roughly like:

```yaml
# template — values pending confirmation against a real Tier 3 prospect
mctb_applicable: false
vaai_applicable: false
disqualifiers: []
```

with `ghl_upgrade_candidate` dependent on whether the prospect shows
GHL-specific signals independent of the FSM.

## Known gap — disqualifier short-circuit behavior

SKILL.md's `mctb_applicable` and `vaai_applicable` grounding rules
define true/false/null emission solely from visible site signals.
Neither section references disqualifiers, and the disqualifiers
section does not state what happens to the applicability flags when a
disqualifier fires. The literal reading is that each field is emitted
independently per its own rule.

Fixtures 2 and 3 follow that literal reading and expect `null` on the
applicability flags. However, ghl-triage's runtime pipeline
(`prospect_triage.py`) enforces a precedence order — the Fix 8
disqualifier gate at Step 3.4 runs before the Fix 7 applicability
gate at Step 3.5 — so at the consumer side, disqualified prospects
never reach applicability evaluation at all. If the audit producer
mirrors this behavior (short-circuiting at the triage-meta emission
step), actual audit runs against Mr. Rooter and Warm & Cool London
may emit `false` rather than `null` on the applicability flags.

This is a documentation gap in SKILL.md, not a fixture bug. The Phase
F smoke test is the resolution point:

- If actual runs emit `null`, the fixtures are correct and SKILL.md's
  literal reading is what the pipeline implements.
- If actual runs emit `false`, either the fixtures need updating to
  match, or SKILL.md needs a new rule statement making the
  short-circuit explicit — the Phase F smoke-test follow-up session
  decides which, and the outcome is recorded back into SKILL.md
  and/or this file.

## Smoke test procedure

Manual verification loop, adapted from `HANDOFF_phase_F.md` with the
Phase E correction to the ghl-triage entry point:

1. Run the audit against the fixture URL:
   `audit <URL>` (or the skill's actual invocation)
2. Tail the saved audit's `triage-meta` block:
   `tail -n 12 output/<saved-file>.md`
3. Diff the `triage-meta` block against this file's Expected values
   block for that fixture. Ignore `audit_generated_at`,
   `business_name`, and `business_url` — those are run-specific.
4. Run the ghl-triage audit-mode handoff:
   `python prospect_triage.py --audit output/<saved-file>.md`
   (verify the exact invocation before running; the handoff flagged
   this as the expected command but recommended confirming against
   current ghl-triage behavior)
5. Confirm the Fix 7 / Fix 8 skip logic activates or doesn't activate
   as expected per fixture profile (baseline should be processed;
   franchise and overseas should be skipped at the disqualifier gate).

Run all three fixtures; report any mismatch against this file. A
follow-up commit updates either the fixture expected values, SKILL.md
rules, or both — depending on what the diff reveals.
