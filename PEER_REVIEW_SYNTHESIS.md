# Peer Review Synthesis — 5 LLM Round
## AI-Powered Local Business Website Agency
## March 2026 | Based on SYSTEM_CONTEXT.md v1.0

---

## HOW TO READ THIS DOCUMENT

Issues are ranked by **consensus weight** (how many of the 5 reviewers raised it)
and **business impact** (what breaks if ignored). The consensus column tells you
how settled each finding is — if 4 of 5 reviewers flagged the same thing
independently, that is effectively a confirmed issue, not an opinion.

Reviewers: GPT-4o (R1), GPT-4.5 (R2), Gemini Pro (R3), Claude (R4), Perplexity (R5)

---

## PART 1: OPEN QUESTIONS — ANSWERED

These were your explicit open questions from Section 17. All 5 reviewers addressed
them. Here is the synthesized answer for each.

---

### Q1: Does the $97/month AI Employee cover Voice AI Widget and Agent Studio, or are there per-use charges?

**Consensus answer (5/5 reviewers):** The $97/month is a platform license fee,
not an all-inclusive rate. Voice AI usage incurs additional per-minute telephony
charges on top. Estimates from reviewers:

- ~$0.05–$0.15 per minute for voice engine + LLM tokens
- A busy plumbing office (emergency trade, high inbound) could add $50–$75/month
  in voice charges alone at 500 minutes/month
- Agent Studio likely has separate generative node costs for complex agent flows

**Action required:** Change your cost documentation from "$130–$180/month cost
floor" to "$97 base + variable telephony usage" with a realistic range of
$130–$250/month depending on inbound call volume. For Package 3 proposals, either
build a simple usage estimator or include a fair-use clause: "Voice AI included
up to 300 minutes/month; heavy usage billed at cost."

---

### Q2: Netlify — Pro plan vs separate accounts per client?

**Consensus answer (5/5):** Netlify Pro ($19/month) is the right answer.
Separate Free accounts per client creates login fatigue, fragmented billing, and
no consolidated dashboard. The math is simple: Pro adds 1TB bandwidth and 25K
build minutes at $19/month — less than the time cost of managing 5+ separate logins.

**Timing trigger (consensus):** Upgrade at 5 clients OR when any single site
approaches 50GB bandwidth in a month — whichever comes first.

**Key detail confirmed:** On the Free tier, exceeding any limit (bandwidth OR
build minutes) pauses ALL sites on the account until the next billing cycle —
not just the site that triggered it. This is harsher than most users expect.

---

### Q3: SerpApi `google_maps_reviews` field names — are `snippet` and `text` still correct?

**Consensus answer (4/5 reviewers, one partial disagreement):**

- `snippet` — valid, the short review text field ✅
- `extracted_snippet.original` — preferred, full review text ✅ (use this first)
- `text` — NOT consistently present in the API response; treat as deprecated ❌

**Action required:** Update `extract_business_data.py` review extraction to:
```python
rv.get("extracted_snippet", {}).get("original") or rv.get("snippet") or ""
```
One reviewer (R3) also mentioned a `body` field appearing in some responses —
add it as a third fallback. Current code uses `snippet` then `text` which is
the wrong priority order.

---

### Q4: Can GHL Snapshots created on Starter be applied to Unlimited plan sub-accounts?

**Consensus answer (5/5):** Yes. Snapshots are agency-level assets, not plan-locked.
A Snapshot created on Starter can be applied to Unlimited sub-accounts. The only
plan restriction is Snapshot *sharing to other agencies* (SaaS Pro only).

**One important caveat (R3):** If the Snapshot contains features that require
paid add-ons (e.g., AI Employee workflows) that aren't enabled in the target
sub-account, those specific workflows import in a "Draft" or "Broken" state.
Always test the Snapshot in a clean-room sub-account before first client delivery.

---

### Q5: CASL French opt-out — mandatory for Ontario or Quebec-only?

**Consensus answer (5/5):** Legally mandatory only for Quebec recipients under
Quebec's Charter of the French Language. English STOP is legally sufficient for
Ontario-only campaigns.

**Practical recommendation (4/5 reviewers):** Default all Canadian client SMS
templates to include both STOP and ARRET/FIN. The cost is zero and the benefits
are: looks more professional at $297/month, protects clients who expand service
areas, handles GTA's French-speaking population naturally. Make it opt-out rather
than opt-in for individual clients.

---

### Q6: Firecrawl reliability on unusual CMSes?

**Range of estimates:**
- R2: 60–75% "good" extractions without manual fixes
- R3: 15–20% failure rate on older home service sites
- R5: No hard number; build your own success rate tracking

**Why the range:** Older home service sites (2015–2018 WordPress with page
builders, custom PHP, older Wix/Squarespace) fail more. Modern sites (standard
WordPress, newer builders) succeed more. Home service businesses skew toward older.

**Consensus:** Your mandatory manual verification step is the right and sufficient
mitigation. Do not remove it. One reviewer added: flag low-confidence extractions
(missing phone, empty services list, no city) in the terminal output to force
extra scrutiny on those specific fields.

---

### Q7: Bolt.new free tier at 10+ demos/week?

**Consensus answer (4/5):** Not viable at that volume.

- Your assumption: ~1M tokens covers 5–10 demos/month ✅ at moderate detail
- Reality: Complex React + Tailwind site + photo attachments + iterative corrections
  = 200–400K tokens per build session
- At 10+ demos/week (40+/month): 8–16M tokens needed vs 1M available

**Practical cap:** 5–8 demos/month at current prompt verbosity on the free tier.
Plan for Bolt Pro or shift more demo builds to Lovable Pro earlier than the
"first client signed" trigger.

---

## PART 2: NEW ISSUES NOT IN ORIGINAL OPEN QUESTIONS

Grouped by how many reviewers raised each issue independently.

---

### CRITICAL — Raised by 2+ reviewers, action required before first outreach

---

**C1: Demo site legal exposure — prospect PII without consent**
Raised by: R4 (critical), R5 (data handling section)

You are building and publicly hosting live URLs that contain a prospect's:
business name, phone number, logo, verbatim Google reviews — scraped without
their knowledge or consent, before any business relationship exists.

In Canada (PIPEDA) and for US prospects, this is a grey zone at best. A single
complaint from a prospect who finds their business info on a live URL they didn't
authorize could create a compliance headache.

**Recommended fix (R4):** Add one of these to every demo before sharing:
- A visible "Demo Preview — Not Live" banner in the site header that disappears
  after client signs, OR
- Deploy demos to a password-protected Netlify URL (Netlify supports this on Pro),
  sharing the password only with the prospect

Also add a note to EXECUTION_GUIDE.md: "Demo sites contain prospect business data.
Do not index them (add robots noindex). Delete within 30 days if prospect does
not convert."

---

**C2: `output/structured_input.json` not in `.gitignore`**
Raised by: R4 (critical), R5 (security section)

Your `.gitignore` already covers `output/prompt_packages/` but NOT
`output/structured_input.json`. This file contains:
- Business phone numbers
- Physical addresses
- Verbatim customer review texts
- Email addresses

One accidental `git add .` commits all of this as PII to your repo history.

**Fix (2 lines):**
```
output/structured_input.json
output/*.json
```
Add both to `.gitignore` immediately.

---

**C3: Voice widget — Option A has a layout problem**
Raised by: R4 (critical), R2 (significant), R3 (flagged MutationObserver as safer)

Section 6 recommends Option A (static div in index.html outside `<div id="root">`)
as the primary approach. R4 correctly identifies: a div placed outside the React
root has no layout context relative to the component tree. Placing it "between
hero and trust bar" via CSS would require absolute positioning or z-index hacks —
fragile and likely to break on different screen sizes.

**Consensus fix:**
- Option B (useEffect) should be the primary recommendation for component-relative
  placement. It places the widget exactly where it belongs in the component tree.
- Option A should be the fallback for cases where the React component order cannot
  be controlled (third-party templates, etc.)
- R3 suggests a third option: wrap the GHL init in a MutationObserver that waits
  for the DOM element to exist before firing — handles slow connections and
  hydration timing without race conditions.

**Update WEBSITE_GENERATION_SKILL.md and WEBSITE_CLAUDE.md** to swap the
recommendation order: Option B primary, Option A secondary.

---

**C4: GHL AI Employee cost — documentation needs updating**
Raised by: R1, R2, R3, R4 (all independently)

See Q1 above. The current "$130–$180/month cost floor" language in SYSTEM_DESIGN,
AI_Website_Stack, and PACKAGING_PRICING_GUIDE is misleading — it implies this is
a fixed cost when it's actually a floor that scales with call volume.

**Files to update:** SYSTEM_DESIGN_v2.1.md Section 15, AI_Website_Stack_v4.1.md
Section 5, PACKAGING_PRICING_GUIDE_v2.md Package 3 cost section.

---

**C5: Extraction validation missing — no gate before prompt generation**
Raised by: R1, R2, R5

There is no automated check that blocks prompt generation when high-risk fields
are empty or malformed. Current behavior: missing phone → [PHONE] renders blank
in 4 locations on the live site. Missing city → [CITY_PROVINCE] renders blank
in hero headline and service areas.

**Recommended fix (R1):** Add a validation step in `generate_website.py` before
prompt assembly that checks:
- Phone contains at least 10 digits (valid pattern)
- BUSINESS_NAME is non-empty
- CITY_PROVINCE is non-empty
- SERVICES_LIST has at least one entry

If any fail, print a specific warning and pause for manual fix — same pattern as
the existing missing-field pause already in `load_structured_input()`.

---

**C6: Netlify suspension — consequence not documented clearly enough**
Raised by: R1, R2, R3, R4, R5 (all 5)

The current docs say "one traffic spike pauses ALL client sites simultaneously."
Reviewers note this understates the severity: it pauses ALL sites until the
NEXT BILLING CYCLE — potentially 3–4 weeks, not a day. For a home service
business in a plumbing emergency, their site being down for 3 weeks is a
client-ending event.

**Fix:** Add this exact language to EXECUTION_GUIDE Part 6 and PACKAGING_PRICING_GUIDE:
"On Netlify Free tier, exceeding 100GB bandwidth OR 300 build minutes pauses
ALL sites on the account until the next calendar month — not until the next day.
At 5+ clients, upgrade to Netlify Pro ($19/month) before this becomes a risk."

---

### HIGH — Raised by 1–2 reviewers, action strongly recommended

---

**H1: CASL express consent vs cold outreach contradiction**
Raised by: R4

Section 9 states "express consent required before first message." But your entire
outreach model is cold (no prior relationship). These two things conflict.

The fix is not to change your outreach — it's to ensure the GHL contact form
on every client site has a CASL-compliant consent checkbox:
*"By submitting this form, you consent to receive text messages from [Business Name]. Reply STOP to unsubscribe."*

This consent applies to leads who submit the form. Your cold outreach to prospects
(the business owners) is governed by CASL's business-to-business implied consent
rules, which are more permissive — but this distinction needs to be explicitly
documented in GHL_SETUP_CHECKLIST_v3.md Section 1.5.

---

**H2: Layer 2 vs Layer 3 precedence is undefined**
Raised by: R4

The system documents that Layer 3 (niche) overrides Layer 1 (universal). But
Layer 2 (audit-specific, generated per prospect) has no documented precedence
relative to Layer 3.

Example conflict: Cleaning niche (Layer 3) says booking above reviews. An audit
finding (Layer 2) could generate a rule moving something above the booking section.
Which wins?

**Recommended precedence:** L2 (audit-specific) > L3 (niche) > L1 (universal).
The audit finding is the most specific data point about this particular business
and should take precedence. Document this in SYSTEM_DESIGN Section 4 and
universal_rules.txt.

---

**H3: A2P registration lead time not documented**
Raised by: R4

US A2P registration currently takes 2–6 weeks for carrier approval. If a Canadian
client occasionally texts US numbers (cross-border customers, snowbirds), they
need A2P before any SMS workflow goes live — and that 2–6 week clock starts
the day you submit, not the day the client signs.

**Fix:** Add to GHL_SETUP_CHECKLIST_v3.md Section 1.5 and EXECUTION_GUIDE
Production Mode Step 12: "Submit A2P registration on the day the client signs —
not as a pre-launch step. US approval takes 2–6 weeks. Running any workflow
before approval results in silently blocked messages."

---

**H4: DNS TTL not managed before domain cutover**
Raised by: R4

Current cutover SOP: "Update A record, wait 24–48 hours for propagation."
Standard mitigation not mentioned: lower the client's DNS TTL to 300–600 seconds
24–48 hours *before* cutover. This reduces actual propagation time from 24–48
hours to 5–10 minutes.

For a home service business, 24–48 hours of split traffic (some users seeing
old broken site, some seeing new site) means real missed calls. This is a free
fix that takes 2 minutes.

**Fix:** Add to GHL_SETUP_CHECKLIST_v3.md Section 12 as Step 0:
"48 hours before cutover: log into client's registrar and change DNS TTL on
existing A record to 300 seconds. This makes the actual cutover take minutes
instead of days."

---

**H5: Review data goes stale with no update mechanism**
Raised by: R4, R2

`[REVIEWS_3]` and `[REVIEW_COUNT]` are pulled at extraction time and baked into
static HTML. A client who goes from 166 to 250 reviews has no update path without
a full rebuild.

For a $297/month retainer, clients will notice and ask. Options to document in
PACKAGING_PRICING_GUIDE:
1. GHL Reviews widget replaces static review cards at go-live (best option —
   widget always shows current reviews from GBP)
2. Quarterly review refresh included in retainer (manual rebuild trigger)
3. New review count updates billed as a minor update

---

**H6: First $10K/month math is wrong**
Raised by: R4

Section 19: "~25–30 clients at $297/month." 30 × $297 = $8,910 — not $10K.
You need ~34 Growth System clients, or a mix: e.g., 25 at $297 + 5 at $497
= $7,425 + $2,485 = $9,910 ≈ $10K.

Fix the math in SYSTEM_CONTEXT.md Section 19 and set a realistic client mix target.

---

**H7: Two production architectures — decision not documented**
Raised by: R4

`plumbing_bolt_prompt.txt` → React + Tailwind with build step (production Lovable)
`plumbing_claude_code_prompt.txt` → single index.html, no build step (demo-grade)

The choice between these is never documented for production use. EXECUTION_GUIDE
should explicitly state: "For production builds via WEBSITE_GENERATION_SKILL.md,
always use `--mode skill-output`. Never use `--mode claude-code` for client delivery
— the single-file output is demo quality only."

---

**H8: Package 1 placeholders — 6 GHL divs with no scripts = dead UI**
Raised by: R5

You correctly require all 6 GHL placeholder divs on every site. But Package 1
doesn't include GHL setup — those divs render as empty dashed boxes with no
functionality. A "Pay Invoice" button that links to "#" and a blank calendar area
look broken to the client.

**Fix:** In universal_rules.txt, add a Package 1 rendering rule: when GHL is
not yet connected, each placeholder should show either:
1. A phone CTA fallback ("To book, call [PHONE]") inside the calendar div
2. CSS that hides the div entirely until GHL script is injected

---

**H9: Logo fallback not documented**
Raised by: R4

If Firecrawl can't find a logo URL (common for micro-businesses), what renders
in the header? Currently undefined. Options to document:
1. Text business name in header if no logo (simplest)
2. A generic wrench/flame/bolt SVG favicon used as placeholder logo
3. Prompt includes instruction to Claude to generate a simple SVG logo from
   the brand colors

Also raised by R4: logo images are currently hotlinked from their original URL.
If the prospect changes their logo (or their old site goes down), the demo site
header breaks. **Fix:** Download and self-host logos in the Netlify deploy, not
hotlink from external URLs.

---

**H10: Post-build variable leak check needs a real validator**
Raised by: R1, R2, R5

Current approach: `grep -o "\[.*\]" output/prompt_packages/[file].txt`

This is fragile — any legitimate copy that uses brackets (CSS selectors,
code examples, legal text) creates false positives. Also, it checks the
*prompt* before Bolt builds, not the *output* after the build.

**Better approach (consensus):** A small Python script that:
1. Loads the known variable list from fill_variables()
2. Checks the assembled prompt for any of those specific bracket patterns
3. After Bolt build: scans the dist/ folder HTML for any `ghl-` IDs that are
   empty (no inner content beyond the placeholder text)

---

### MEDIUM — Single reviewer, worth tracking

---

**M1: Prospect tracking system** (mentioned by all reviewers, already flagged in your system)
Add `input/prospects.csv` with: url, business_name, audit_date, demo_url,
demo_netlify_url, status, last_contact_date, package_pitched, notes.
Run a simple append from extract_business_data.py on each extraction.

**M2: Netlify deploy token scope**
Current setup uses one global `NETLIFY_AUTH_TOKEN` for all deploys. A leaked
token allows deletion or replacement of all client sites simultaneously.
Netlify supports per-site deploy tokens — generate one scoped token per client
after the Netlify Pro upgrade.

**M3: DEPRECATED BOLT_PLUMBING_TEMPLATE.md needs to be deleted or archived**
The deprecation notice is added (good), but the file still lives in docs/niches/
where Claude Code might use it. Move to an `/archive/` folder or delete entirely.
Also remove it from CLAUDE.md context paths.

**M4: Data retention policy**
`structured_input.json` and audit reports contain PII. Add to EXECUTION_GUIDE:
"Delete prospect JSON and audit reports for non-converting prospects after 60 days.
Archive converting prospects in an encrypted folder."

**M5: Payment terms inconsistent across documents**
"50% upfront, 50% on go-live" appears in EXECUTION_GUIDE but not in
PACKAGING_PRICING_GUIDE or SALES_SCRIPT. Add a payment terms section to both so
the answer is consistent when a prospect asks during a call.

**M6: Phone number validation before 4-location placement**
A wrong phone number (e.g., a supplier's number accidentally scraped from the
footer) gets embedded in 4 locations on the live site. Add to the extraction
validation check (H5 above): confirm extracted phone matches GBP phone before
allowing it to proceed.

---

## PART 3: CONSENSUS PRIORITY ORDER

What to fix, in what order:

### Do immediately (before first outreach):
1. **Add `output/structured_input.json` to `.gitignore`** — 5 minutes, zero risk
2. **Add "Demo Preview" banner or password-protect demo URLs** — 30 minutes
3. **Fix SerpApi field order** in extract_business_data.py (`extracted_snippet.original` → `snippet`) — 10 minutes

### Do this week (before first client signs):
4. **Swap Option B/A recommendation** for GHL voice widget placement in WEBSITE_GENERATION_SKILL.md and WEBSITE_CLAUDE.md
5. **Add extraction validation gate** to generate_website.py (phone digits, non-empty name/city/services)
6. **Update Package 3 cost language** — "$97 base + variable voice usage" in all three pricing docs
7. **Add Netlify suspension exact consequence** — "until next billing cycle" — to EXECUTION_GUIDE and PACKAGING_PRICING_GUIDE
8. **Document Layer 2 > Layer 3 > Layer 1 precedence** in SYSTEM_DESIGN Section 4
9. **Add A2P day-1 submit instruction** to GHL_SETUP_CHECKLIST_v3.md Section 1.5
10. **Add DNS TTL pre-cutover step** to GHL_SETUP_CHECKLIST_v3.md Section 12

### Do before client 3 (scaling prep):
11. Add prospects.csv tracking
12. Fix $10K math in SYSTEM_CONTEXT Section 19
13. Document production architecture choice (skill-output only for delivery)
14. Add logo fallback rule to universal_rules.txt
15. Add data retention policy to EXECUTION_GUIDE
16. Upgrade Netlify to Pro and switch to scoped deploy tokens
17. Add French opt-out keywords as default for all Canadian clients
18. Add Package 1 placeholder fallback (phone CTA inside empty GHL divs)
19. Move BOLT_PLUMBING_TEMPLATE.md to /archive/ or delete

---

## PART 4: WHAT ALL REVIEWERS AGREED IS WORKING WELL

The following received consistent praise with no significant pushback:

- **Three-layer prompt architecture** — "One of the stronger parts" (R2), "brilliant"
  (R3). Clean separation with deterministic variable fill and explicit precedence.
- **Separation of demo (Bolt) vs production (Claude Code)** — Consistent with the
  Python/Claude Code constraint and avoids over-stretching any tool.
- **GHL section dependency ordering in checklist** — A2P before SMS, pipeline before
  workflows, Voice Labs before widget. "Reflects real production pain most agency
  systems miss" (R2).
- **SKILL.md banned-words list** — "Unusually rigorous, will produce significantly
  more credible audit reports" (R4).
- **Manual verification step for extraction** — Every reviewer endorsed keeping it.
  "The ROI on catching one wrong phone number is worth 5 minutes" (R3).
- **Founding client "Case Study Credit" framing** — "Strategically sound" (R4).
- **Overall architecture: external site + GHL embed** — Confirmed by all 5 reviewers
  as the correct and officially supported integration pattern.

---

## PART 5: OVERALL VERDICT

All 5 reviewers gave the system a green light for first outreach. Direct quotes:

- R2: "Green light to start outreach with current system — production-ready for
  first 1–5 clients with existing manual gates."
- R3: "The Three-Layer Prompt is brilliant."
- R4: "The system is well-thought-out for a pre-revenue solo operation."
- R5: "No fundamental design flaws."

The consensus risk ranking:
1. **Client data handling** (demo sites + gitignore gap) — fix before first URL is sent
2. **Voice AI cost variability** — fix before first Package 3 quote
3. **Netlify suspension severity** — fix documentation now, actual upgrade at 5 clients
4. **Sales velocity** — the biggest remaining risk is not technical

R2 summary: "The biggest remaining risk isn't technical — it's sales velocity.
Focus outreach energy on the identified plumbing prospect. Closing the first one
and getting that Master Snapshot unlocks the real efficiency."

---

*Synthesis compiled from 5 LLM peer reviews of SYSTEM_CONTEXT.md v1.0*
*March 2026*
