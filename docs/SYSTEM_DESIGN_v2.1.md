# AI-Powered Local Business Website Agency — Complete System Design
## Version: 2.1
## Date: March 2026
## Status: Updated per 5-LLM peer review of v2 (second round)
## Changes from v2: See Section 18 change log

---

## SECTION 1: BUSINESS CONTEXT

### The Agency Model
- **Owner:** Nitin, based in Etobicoke, Ontario (GTA)
- **Target clients:** Local home service businesses (plumbing, HVAC, cleaning, pest control,
  roofing, landscaping, electrical, painting, garage door, handyman, moving, junk removal)
- **Primary market:** USA + Canada (GTA focus)
- **Platform:** GoHighLevel (GHL) for CRM, automations, voice AI, review management
- **Revenue model:** Setup fee ($997–$5,497) + monthly retainer ($97–$497/month)
- **Target:** $10K/month recurring retainers
- **Current state:** Pre-first-client. First prospect identified: mississaugaplumbingservices.com
  (audited, scored 1/10 red, demo site built in Bolt.new and live at bolt.host)

### The Core Value Proposition
The agency sells two things together:
1. A premium AI-built website (front-end)
2. A GHL automation stack (back-end engine): voice AI, missed call text-back,
   review request workflows, CRM pipeline

These are sold as one system, not separately. The website is the front-end.
GHL is the engine. They work together via a JS embed snippet.

---

## SECTION 2: THE COMPLETE TECHNOLOGY STACK

### Front-End (Website)
The website is built externally — NOT hosted on GHL. External AI-built sites
produce significantly higher design quality than GHL's native site builder.
GHL automations connect via JS snippet regardless of hosting platform.

**Website hosting:**
- Netlify (recommended) — drag and drop deploy, custom subdomain, automatic HTTPS
- Bolt Cloud (built into Bolt.new)
- Lovable hosting (built into Lovable)
- Vercel

**Hosting cost note:** Free entry points are sufficient for demos and early clients,
subject to current usage limits — verify before committing to client pricing.

**⚠️ Netlify account-level suspension risk (critical for 5+ clients):**
Free tier = 100GB bandwidth + 300 build minutes per month.
When any limit is hit, ALL sites on that Netlify account pause simultaneously
for the remainder of the month — not just the site that triggered the overage.
At 10 clients on one account, one traffic spike takes all 10 offline at once.

Mitigation:
- Netlify Pro ($19/month): eliminates suspension — recommended at 5+ clients
- Separate Netlify account per client: limits are isolated per account
- Monitor usage at Team settings → Usage; set alerts at 75% of limits

### Back-End Automation Engine (GHL)
GHL handles everything behind the website:
- Voice AI receptionist (JS widget — inline embedded or floating)
- Missed call text-back (backend workflow — no embed needed)
- Review request automation (triggered post-job)
- CRM pipeline with stage tracking
- Calendar/booking (iFrame embedded on site)
- Contact form (iFrame embedded on site)
- Live reviews display (JS widget)
- Payment links

### The Bridge
GHL provides JS snippets and iFrame embeds for all client-facing features.
These work on standard external hosts (Netlify, Lovable hosting, Bolt Cloud, Vercel).

**Important deployment note:** Test each deployment for:
- Script placement — see dual approach below
- CSP headers (standard Netlify has none by default — only a risk if you add custom CSP)
- Ad-blocking (advise clients to test on a real device without blockers)

**GHL script placement — dual approach (inline vs floating widget):**
These two widget types require different placement strategies:

- **Floating chat widget** (`id="ghl-chat-widget"`): Place JS snippet in `index.html`
  body before `</body>`. The widget appends to `<body>` which already exists — no
  React dependency.

- **Inline voice widget** (`id="ghl-voice-inline"`): The placeholder div lives inside
  the React component tree, so it doesn't exist in the DOM until React mounts.
  Two safe options:
  - Option A: Move `id="ghl-voice-inline"` to a static HTML element in `index.html`
    outside `<div id="root">`, so it exists before React mounts.
  - Option B: Use `useEffect(() => { /* inject GHL script here */ }, [])` inside
    the component that renders the placeholder div, so the div exists before the
    script runs.
  Do NOT place the inline widget script before `<div id="root">` — the target div
  doesn't exist yet and the widget will fail silently or fall back to floating mode.

**GHL Voice AI widget — inline embed confirmed:**
GHL now supports Embedded/Inline placement for the Voice AI widget (not just floating).
Setup path: sub-account → Sites → Chat Widget → Voice AI type → Style tab →
Widget Placement → Embedded/Inline.
**Prerequisite:** Voice AI must be enabled in GHL Labs for the sub-account BEFORE
the widget will function. This is a mandatory step that silently fails if skipped.

**Canadian SMS compliance:**
Canadian SMS is NOT simply "separate from A2P." There is a converging 10DLC regime:
- CA→US messaging: A2P registration is mandatory for ALL Canadian numbers
- CA→CA messaging (numbers purchased on or after March 26, 2025): A2P OR Persona verification required
- CA→CA messaging (numbers purchased before March 26, 2025): grandfathered, but loses exemption if any US messages sent
- CASL (Canada's Anti-Spam Legislation) applies to ALL commercial SMS regardless of A2P status
See GHL_SETUP_CHECKLIST_v3.md Section 1.5 for the full decision tree.

---

## SECTION 3: THE THREE WEBSITE CREATION PATHS

### Path A — Demo Sites (Pre-client-sign)
**Tool:** Creator's custom Antigravity CLI + Gemini 3.1 Pro Preview OR Bolt.new
**Purpose:** Visually impressive demo to close the deal
**Hosting:** Netlify Drop or bolt.host

**Antigravity naming clarification (confirmed by all 5 peer reviewers):**
Two distinct products share the "Antigravity" name:
1. Google's official Antigravity IDE — an agentic development platform (VS Code fork)
   launched November 2025. Not a website builder.
2. Creator's custom Antigravity CLI — a community-built script that calls the
   Gemini API to generate React/Vite/Tailwind sites. Not part of Google's ecosystem.

**Gemini 3.1 Pro Preview (confirmed):**
- Released February 19, 2026 — current flagship model
- 64k token output limit (65,536 tokens) — can generate complete multi-page React app
- Three-Tier Thinking: Low/Medium/High reasoning levels
- Available in Google AI Studio (free, with rate limits)
- Rate limit note: AI Studio free tier has per-minute and daily limits —
  sufficient for 1–2 demo builds per session, not for automated batch generation

**Gemini converter prompt:**
After generating a React/Vite site in AI Studio, Gemini can REWRITE (not compress)
the multi-file app as a single vanilla HTML/JS/CSS file. This is for demo/closing only.
Production delivery should always use the source project, not the single-file output.

### Path B — Production Sites (Post-client-sign) ← RECOMMENDED
**Tool:** Lovable (primary) OR Claude Code autonomous builder (secondary)
**Purpose:** Production-ready deliverable with GitHub sync, maintainable source
**Hosting:** Netlify (with GitHub auto-deploy for ongoing client management)

**Why Lovable for production:**
- Same React/Tailwind stack as demo prompts — no translation layer
- GitHub sync — you own the code, can move anywhere
- Chat-based edits for ongoing client changes
- Manual project duplication on Pro achieves template-per-niche at $25/month

**Lovable credit reality (confirmed by all 5 reviewers — use 150 as planning number):**
- Free tier: 5 credits/day, hard cap of 30/month — not sufficient for agency volume
- Pro plan ($25/month): 100 monthly credits + 5 daily credits
  Theoretical maximum: ~250/month (requires daily logins)
  Realistic working estimate: ~150/month (use this for capacity planning)
  Source of conflict resolved: 250 requires logging in every single day; 150 is the safe floor
- Design Templates: Business plan ($50/month) only — on Pro, manually duplicate master project
- Verify at lovable.dev/pricing before committing capacity to any plan number

**Why Claude Code as secondary production option:**
Claude Code can read files, write files, run terminal commands, and chain steps
autonomously. It can build a complete React project, run `npm run build`, and
deploy via Netlify CLI.

**CRITICAL ARCHITECTURE CORRECTION FROM V1:**
`generate_website.py --mode claude-code` cannot invoke Claude Code as a subprocess.
Python cannot call Claude Code programmatically.

**Correct workflow:**
1. `generate_website.py --mode skill-output` → outputs JSON package to disk
2. Open Claude Code in VS Code
3. Run: "execute WEBSITE_GENERATION_SKILL.md using [package].json"
4. Claude Code reads package → builds React project → `npm run build` → deploys

**Netlify CLI deploy — MANDATORY FLAG (standard Vite config):**
```bash
netlify deploy --dir=dist --prod
```
`dist/` is Vite's default build output directory. If `build.outDir` is customized
in `vite.config.js`, deploy that folder instead. To prevent ambiguity, the generated
`vite.config.js` should always explicitly set `build: { outDir: 'dist' }`.

### Path C — Quick Demo (Bolt.new)
**Tool:** Bolt.new
**Purpose:** Rapid prototyping, niche template testing
**Free tier:** ~1M tokens/month — sufficient for 5–10 simple demo sites

**Bolt.new index.html deployment quirk:**
Index.html edits made via chat do not always redeploy correctly to bolt.host.
This is an observed behavior, not a formally documented platform limitation.
**Fix:** Download ZIP → edit index.html manually → deploy to Netlify Drop.
Items to fix manually in index.html:
- Remove Bolt badge script: `<script async src="...bolt.new/badge.js...">`
- Replace `/vite.svg` favicon with trade-appropriate icon
- Set correct OG title, description, image meta tags

---

## SECTION 4: THE AUTOMATED DATA EXTRACTION SYSTEM

### API Keys
API keys are stored in `.env` only. They are NEVER included in design documents,
markdown files, or any document shared externally.

`.env` file (not committed to Git — add to `.gitignore`):
```
FIRECRAWL_API_KEY=your_key_here
SERPAPI_KEY=your_key_here
NETLIFY_AUTH_TOKEN=your_key_here
NETLIFY_SITE_ID=your_site_id_here  # optional — omit to create new site
```

**Security policy:** If any key is ever exposed in a document or committed to Git,
rotate it immediately at the provider dashboard. Do not wait.

### Firecrawl
- Scrapes JavaScript-rendered sites via headless browser
- Returns structured data via schema-based extraction
- High extraction reliability on standard contractor sites — best-effort, not guaranteed
- **Reliability caveat:** Extraction quality varies on unusual CMS platforms,
  unusual CMS platforms, anti-bot sites, or heavily nested JS frameworks
- Manual review step (2–3 minutes) catches extraction gaps
- Free for Lovable users through approximately January 2026 (promotional — verify
  current status in Lovable dashboard before relying on free tier; budget $10–50/month
  for Firecrawl if promo has ended)

### SerpApi
- Pulls Google Business Profile data via `engine=google_maps`
- Pulls review texts via `engine=google_maps_reviews` (requires `place_id` from first call)
- Returns: rating, review count, phone, address, hours, up to 5 review texts
- **Coverage note:** SerpApi covers most GBP data needed for this use case.
  It is a third-party layer — not a full substitute for Google Places API in all cases.
  Suitable for prospecting and data prefill; manual verification required for delivery.
- **Rate limits:** Free tier sufficient for < 5 extractions/day.
  At agency volume (10+ prospects/day), upgrade to SerpApi Basic (~$50–75/month).
  Add to agency overhead budget.

### What Gets Automated vs Manual

**Automated (script handles):**
- Business name, phone, email, address
- Services list
- Hours + emergency availability
- Star rating + review count (from GBP via SerpApi)
- Top 3–5 review texts (from SerpApi)
- Logo URL + photo URLs (from Firecrawl)
- Business type detection (keyword matching)

**Manual (2–5 minutes — every extracted field verified before delivery):**
- Confirm phone number is correct (call it)
- Confirm service areas include specific neighborhoods (not just the city)
- Download logo and photos from provided URLs
- Confirm price positioning
- Verify GBP is claimed and belongs to the correct business

**Minimum input to trigger extraction:**
- Option A: Existing website URL → Firecrawl + SerpApi GBP lookup
- Option B: Business name + city → SerpApi GBP lookup only (no site scrape)

### Script Locations
```
execution/extract_business_data.py   ← Firecrawl + SerpApi extraction
execution/generate_website.py        ← orchestrator: reads JSON, assembles prompt package
```

### Orchestrator Architecture (corrected from v1)

**Command:**
```bash
# Demo build — paste prompt into Bolt/Lovable
python3 execution/generate_website.py --url https://example.com --mode bolt

# Production build — outputs package for Claude Code
python3 execution/generate_website.py --url https://example.com --mode skill-output
```

**What it does:**
1. Runs Firecrawl + SerpApi extraction → `output/structured_input.json`
2. Detects business niche
3. Reads `docs/niches/[trade].md` (Layer 3)
4. Reads `docs/master_prompts/universal_rules.txt` (Layer 1)
5. If pre-built prompt exists for niche (`[niche]_bolt_prompt.txt`): fills variables and outputs
6. If no pre-built prompt: assembles from the three layers
7. Saves complete prompt package to `output/prompt_packages/`

**What it does NOT do:**
- Does not invoke Claude Code (Python cannot subprocess Claude Code)
- Does not deploy to Netlify (deployment happens in Claude Code or manually)

---

## SECTION 5: THE WEBSITE SALES AUDIT SKILL (EXISTING)

### Location
`docs/SKILL.md` (v12) — also `docs/SKILL_website-sales-audit.md`

### What It Does
Analyzes a local home service business website and produces four outputs:
1. Short report (under 350 words, owner-facing)
2. Medium report (800–1,200 words, owner-facing) — includes weighted 0–100 health score
3. Content & Components Gap Summary (checklist format)
4. Talking Points (internal sales reference — includes Feature Detection Table,
   GHL Automation Gap Assessment, Competitor Edge, and 5-touch Follow-Up Sequence)

Triggered by: "audit [URL]" or "audit https://url and prepare full call prep"

### The 10 Checks (each contributes to a weighted 0–100 health score)
1. First impressions & design (modern vs dated) — 10%
2. Mobile experience (viewport, tap-to-call, responsive) — 15%
3. Contact & booking (forms, phone, response promise) — 15%
4. Local presence (city name, specific neighborhoods) — 10%
5. Trust & credibility (reviews, licenses, real photos) — 15%
6. Content completeness (trade-specific checklist) — 10%
7. Speed & performance (PageSpeed API attempt first) — 5%
8. Photos & visual authenticity (real vs stock) — 5%
9. Site security (HTTPS) — 5%
10. Lead capture & follow-up system (form, CRM, automation signals) — 10%

### Score Bands and Pitch Tier
- 🟢 Strong Foundation (80–100) → automation-only pitch, no rebuild
- 🟡 Some Gaps (55–79) → Package 1 + automation add-ons OR Package 2
- 🔴 Needs Significant Work (0–54) → Package 2 or Package 3 minimum

### Critical Known Issue
Fetching competitor sites can hang for 30+ minutes in Claude Code.
Fix: Press Escape → "stop fetching. write all four report outputs now
based on what you gathered, skip competitor section, save to output/[filename].md"

### First Live Audit Result
mississaugaplumbingservices.com — score 1/10 red
Key findings: 166 Google reviews (4.9 stars) hidden, JS-only build not indexable,
no lead capture, no tap-to-call.
Report: `output/mississaugaplumbingservices-2026-03-08.md`

---

## SECTION 6: THE WEBSITE GENERATION SYSTEM

### Overview
The audit skill identifies what's BROKEN on a prospect's site.
The generation system builds everything the audit would PRAISE.
Every audit finding maps directly to a generation rule.

### The Three-Layer Prompt Architecture

**Layer 1 — Universal Rules (every site, every niche)**
```
File: docs/master_prompts/universal_rules.txt
Covers: phone placement, GHL placeholder divs, section structure, technical requirements
```

**Layer 2 — Audit-Specific Rules (per prospect)**
```
Generated per prospect from audit findings.
Examples:
  Audit: 166 reviews hidden → Rule: rating + count in hero subheadline; 3 review cards
  Audit: JS-only build → Rule: semantic HTML, server-renderable structure
  Audit: No tap-to-call → Rule: tel: href on every phone instance
```

**Layer 3 — Niche-Specific Rules (per trade)**
```
File: docs/niches/[trade].md
Each file defines: CTAs, colors, section order, trust signals, ROI anchors
```

**Prompt length note:** When all three layers are assembled for a complex niche,
the combined prompt can push against Bolt/Lovable input limits. Keep Layer 2
(audit-specific) concise — bullet points, not paragraphs.

**Layer precedence (highest to lowest):**

```
Layer 2 (audit-specific, per-prospect) > Layer 3 (niche) > Layer 1 (universal)
```

When rules conflict, the more specific layer always wins:

- **Layer 2 beats Layer 3:** If the audit found this specific client has 0 reviews,
  the Layer 2 rule ("omit rating line from hero — shows 0.0/5") overrides the
  plumbing niche default ("show rating_string in hero subheadline").
- **Layer 3 beats Layer 1:** If the roofing niche file specifies a 4-step process
  (Inspection→Insurance→Install→Warranty), that overrides the universal default
  (Call→Quote→Work→Done).
- **Layer 1 is always the floor:** Everything in universal_rules.txt applies unless
  explicitly overridden by a more specific layer. The 6 GHL placeholder divs,
  phone placement rules, and technical requirements in Layer 1 are non-negotiable
  and cannot be overridden by Layer 3.

In practice: Layer 2 rules are short audit bullets. Layer 3 is the full niche
personality. Layer 1 is the structural skeleton. All three stack — they don't
replace each other except where they directly conflict on the same element.

### The Six GHL Placeholder Divs (All Sites, All Niches)

All 6 required. IDs are exact — do not rename.

```html
<!-- 1. Voice AI inline — between hero and trust bar -->
<div id="ghl-voice-inline" style="width:100%; min-height:80px;
  background:#f5f5f5; border:2px dashed #ccc; border-radius:8px;
  display:flex; align-items:center; justify-content:center; padding:20px;">
  <p style="color:#999; text-align:center; margin:0;">
    🎙️ Voice AI Widget — activates after GHL setup
  </p>
</div>
<!-- GHL SETUP:
  1. Enable Voice AI in sub-account Labs FIRST (silently fails if skipped)
  2. Sites → Chat Widget → New → select Voice AI type
  3. Style tab → Widget Placement → Embedded/Inline
  4. Copy JS snippet → apply using ONE of:
     Option A (recommended): Place ghl-voice-inline as static HTML in index.html
       OUTSIDE <div id="root">, so it exists before React mounts:
         <div id="ghl-voice-inline"></div>
         <script>/* GHL inline widget JS */</script>
         <div id="root"></div>
     Option B: Use useEffect in the React component that renders the placeholder:
         useEffect(() => {
           const s = document.createElement('script');
           s.innerHTML = `/* GHL widget init */`;
           document.getElementById('ghl-voice-inline').appendChild(s);
         }, []);
  ⚠️ Do NOT place script before <div id="root"> — the target div doesn't exist yet. -->

<!-- 2. Booking calendar -->
<div id="ghl-calendar" style="width:100%; min-height:150px;
  border:2px dashed #ccc; border-radius:8px; display:flex;
  align-items:center; justify-content:center;">
  <p style="color:#999; margin:0;">Booking Calendar loads here (GHL embed)</p>
</div>

<!-- 3. Contact form -->
<div id="ghl-contact-form" style="width:100%; min-height:150px;
  border:2px dashed #ccc; border-radius:8px; display:flex;
  align-items:center; justify-content:center;">
  <p style="color:#999; margin:0;">Contact Form loads here (GHL embed)</p>
</div>

<!-- 4. Live reviews -->
<div id="ghl-reviews" style="width:100%; min-height:150px;
  border:2px dashed #ccc; border-radius:8px; display:flex;
  align-items:center; justify-content:center;">
  <p style="color:#999; margin:0;">Live Google Reviews load here (GHL embed)</p>
</div>

<!-- 5. Pay invoice — in footer -->
<a href="#" id="ghl-payment-link" style="display:inline-block;
  background:#1a2744; color:white; padding:10px 24px;
  border-radius:6px; text-decoration:none; font-size:14px;">
  Pay Invoice
</a>
<!-- GHL: replace href="#" with GHL payment link URL -->

<!-- 6. Chat widget — LAST element before </body> -->
<div id="ghl-chat-widget"></div>
<!-- GHL: paste chat/voice widget JS snippet here before </body> -->
```

**GHL backend-only features (no embed needed):**
- Missed call text-back — GHL workflow triggers on missed call event
- Review request automation — GHL workflow triggers on pipeline stage change

---

## SECTION 7: THE NICHE FILE SYSTEM

### Design Principle
Adding a new niche = fill in `docs/niches/_NICHE_TEMPLATE.md` and save as `[trade].md`.
The engine does not change. Estimated time: 15–30 minutes per niche.
(Note from peer review: 15 minutes assumes the niche file is the only thing being created.
Full niche addition including audit checklist updates and prompt testing: ~2 hours.)

### File Structure
```
docs/niches/
  _NICHE_TEMPLATE.md     ← blank template for any new niche ✅
  generic.md             ← fallback for unrecognized trades ✅
  plumbing.md            ← built ✅
  hvac.md                ← built ✅
  cleaning.md            ← built ✅
  electrical.md          ← built ✅
  roofing.md             ← built ✅
  pest_control.md        ← still to build
  landscaping.md         ← still to build
```

### Niche Detection Logic
```python
NICHE_KEYWORDS = {
    "plumbing":     ["plumber", "plumbing", "drain", "pipe", "water heater", "sump"],
    "hvac":         ["hvac", "heating", "cooling", "furnace", "air conditioning"],
    "cleaning":     ["cleaning", "cleaner", "maid", "housekeeping", "janitorial"],
    "pest_control": ["pest", "exterminator", "termite", "rodent", "bug", "insect"],
    "roofing":      ["roofing", "roofer", "shingles", "roof", "gutters"],
    "landscaping":  ["landscaping", "lawn", "garden", "snow removal", "yard"],
    "electrical":   ["electrical", "electrician", "wiring", "panel", "circuit"],
    "painting":     ["painting", "painter", "interior paint", "exterior paint"],
    "garage_door":  ["garage door", "garage", "door repair", "opener"],
    "handyman":     ["handyman", "repairs", "maintenance", "odd jobs"],
    "moving":       ["moving", "movers", "relocation", "storage"],
    "junk_removal": ["junk", "junk removal", "hauling", "disposal", "cleanup"],
}
```

Falls back to `generic.md` if no match or niche file doesn't exist yet.

---

## SECTION 8: THE COMPLETE FILE ARCHITECTURE

### Project Location
`C:\Users\canad\projects\website-sales-audit\`

### Current Files (Built ✅)
```
docs/
  SKILL.md (v12)                     ← website sales audit skill (weighted 0–100 score)
  SKILL_website-sales-audit.md       ← duplicate for Claude Code context
  SALES_SCRIPT_v2.md                 ← cold call script
  GHL_SETUP_CHECKLIST_v3.md          ← GHL client onboarding (v3 with all fixes)
  PACKAGING_PRICING_GUIDE_v2.md      ← packages and pricing
  SYSTEM_DESIGN_v2.1.md              ← this document
  AI_Website_Stack_v4.1.md           ← validated tech stack
  WEBSITE_GENERATION_SKILL.md        ← Claude Code autonomous builder ✅
  WEBSITE_CLAUDE.md                  ← per-client CLAUDE.md design rules ✅
  CLAUDE_CODE_SETUP.md               ← one-time setup guide for claude-code mode ✅
  master_prompts/
    universal_rules.txt              ← Layer 1 ✅
    plumbing_bolt_prompt.txt         ← Bolt/Lovable prompt (plumbing) ✅
    plumbing_gemini_prompt.txt       ← Gemini cinematic prompt (plumbing) ✅
    plumbing_claude_code_prompt.txt  ← Claude Code single-file prompt (plumbing) ✅
  niches/
    _NICHE_TEMPLATE.md               ← blank template ✅
    generic.md                       ← fallback for unrecognized trades ✅
    plumbing.md                      ← plumbing niche file ✅
    hvac.md                          ← HVAC niche file ✅
    cleaning.md                      ← cleaning niche file ✅
    electrical.md                    ← electrical niche file ✅
    roofing.md                       ← roofing niche file ✅

output/
  mississaugaplumbingservices-2026-03-08.md  ← first audit report

execution/
  extract_business_data.py           ← Firecrawl + SerpApi extraction ✅
  generate_website.py                ← orchestrator (corrected architecture) ✅
  lead_pipeline.py                   ← lead generation pipeline
  email_verifier.py                  ← email verification
  utils.py                           ← shared utilities
  claude_extractor.py                ← Claude-based extraction
```

### Still To Build
```
docs/niches/
  pest_control.md
  landscaping.md

docs/master_prompts/
  hvac_bolt_prompt.txt
  cleaning_bolt_prompt.txt
  electrical_bolt_prompt.txt
  roofing_bolt_prompt.txt
  [remaining niche Gemini + Claude Code prompts]

Other:
  First outreach to mississaugaplumbingservices.com
  GHL Master Snapshot (after first client fully onboarded)
  input/prospects.csv (prospect tracking)
```

---

## SECTION 9: PROMPT COMPATIBILITY ACROSS BUILDERS

### Universal Prompt Language
Prompts are written in React + Tailwind. Compatibility:

| Builder | Compatibility | Notes |
|---|---|---|
| Bolt.new | 100% | Native stack |
| Lovable | ~90% | Same React/Tailwind — paste works |
| v0 by Vercel | ~80% | Next.js — minor adjustments |
| Google AI Studio | ~90% | Same stack for Gemini output |
| Replit | ~75% | Framework spec may need adjustment |
| Hostinger Horizons | ~20% | Proprietary — does not accept React prompts |

---

## SECTION 10: THE SIX INPUT VARIABLES

The only fields that change per client. Everything else is locked in the prompt.

```
[BUSINESS_NAME]    → e.g., "Mississauga Plumbing Service Ltd."
[PHONE]            → e.g., "(647) 550-4003"
[PHONE_DIGITS]     → e.g., "16475504003" (auto-computed by generate_website.py)
[CITY_PROVINCE]    → e.g., "Mississauga, ON"
[SERVICES_LIST]    → e.g., "Emergency Plumbing, Drain Cleaning, Water Heater..."
[SERVICE_AREAS]    → e.g., "Mississauga, Brampton, Oakville, Streetsville, Port Credit..."
[REVIEWS_3]        → 3 verbatim review texts from GBP
```

Optional:
```
[YEARS_IN_BUSINESS]  → e.g., "15+"
[EMERGENCY]          → "yes" or "no"
[RATING_STRING]      → e.g., "4.9/5 · 166 Google Reviews"
[LOGO_URL]           → URL of logo to download
[PHOTO_URLS]         → list of job photo URLs to download
```

The extraction script auto-fills all of these.
Manual step: download the image files from the provided URLs.

---

## SECTION 11: THE COMPLETE WORKFLOW (END-TO-END)

### Time Estimates (corrected from v1 per peer review)
- Demo draft (first build per niche): 30–60 minutes
- Demo draft (subsequent clients, same niche): 15–30 minutes
- Production-ready delivery: 2–4 hours total
  (includes QA checklist, image cleanup, GHL widget activation, client approval)
- "5 min per site" = rough first draft only, not client-ready

### Pre-Revenue Phase (Demo to close)
```
1. Find prospect (Google Maps or lead pipeline)

2. Run audit:
   "audit https://[url] and prepare full call prep" in Claude Code
   → 4-output report saved to output/

3. Run extraction + prompt generation:
   python3 execution/generate_website.py --url https://[url] --mode bolt
   → output/prompt_packages/[business]_bolt_prompt_[date].txt

4. Paste prompt in Bolt.new (free tier)
   Attach logo + photos in chatbox → build

5. Review output — fix any issues in Bolt chat

6. Deploy to Netlify Drop (free, no account needed):
   netlify deploy --dir=dist --prod   ← --dir=dist is MANDATORY
   OR: drag dist/ folder to netlify.com/drop

7. Cold outreach with live demo link
   Goal of first call: get them to view the demo link only
   Do NOT pitch pricing on the first cold call
```

### Post-Sign Phase
```
8. Collect setup fee

9. Upgrade to Lovable Pro ($25/month)

10. Set up GHL sub-account:
    - Verify GHL plan supports new sub-account (Starter: ~3 subs; Unlimited: unlimited)
    - Complete SMS compliance (Section 1.5 of GHL_SETUP_CHECKLIST_v3.md)
    - For Canadian clients: complete Canadian SMS decision tree (CASL + A2P rules)

11. Run production build:
    python3 execution/generate_website.py --url https://[url] --mode skill-output
    → output/prompt_packages/[business]_claude_code_package_[date].json

12. Open Claude Code → execute WEBSITE_GENERATION_SKILL.md using package file
    → Claude Code builds React project
    → npm run build
    → netlify deploy --dir=dist --prod   ← MANDATORY FLAG
    → returns live URL

13. Run QA checklist (Section 11 of GHL_SETUP_CHECKLIST_v3.md)
    Every item must pass before sharing with client

14. Paste client's GHL widget snippets into deployed site
    → Voice AI inline widget: use Option A or Option B (see Section 2 dual approach)
      Option A: static <div id="ghl-voice-inline"> in index.html OUTSIDE <div id="root">
      Option B: useEffect in the React component that holds the placeholder
      ⚠️ Do NOT place the inline widget script before <div id="root"> — the div doesn't exist yet
    → Chat widget (floating): last element before </body> in index.html — standard placement

15. Activate GHL workflows:
    Voice AI (enable Labs first), missed call text-back, review requests
    Define review request trigger with client (form / manual / missed-call proxy)

16. Point client's domain to Netlify
    Follow DOMAIN_CUTOVER_SOP in GHL_SETUP_CHECKLIST_v3.md Section 12

17. After first client fully configured:
    Build GHL Master Snapshot → saves 3+ hours on every subsequent client
    (GHL_SETUP_CHECKLIST_v3.md Section 8.5)
```

---

## SECTION 12: GHL INTEGRATION REFERENCE

### GHL Tier Structure (March 2026)
| Plan | Price | Sub-accounts | Best for |
|---|---|---|---|
| Starter | $97/month | 3 (1 agency + 2 clients) | First 1–2 client onboards |
| Unlimited | $297/month | Unlimited | Client 4+ |
| SaaS Pro / Agency Pro | $497/month | Unlimited + white-label SaaS | Reselling GHL |

**Sub-account limit (confirmed):**
GHL Starter = 3 sub-accounts (1 for your agency + 2 for clients). This is confirmed
on the official GHL pricing page. Upgrade to Unlimited when onboarding client 3.

**Voice AI add-on cost:**
GHL AI Employee add-on: $97/month per sub-account for Package 3 clients (Voice AI included).
This is NOT covered by the Unlimited plan base price.
LC Phone usage (per-SMS, per-minute): pass through to client via SaaS Mode re-billing.
**Enable SaaS Mode re-billing before first client goes live.**

### GHL Embed Reference
| Feature | Embed Method | Setup Note |
|---|---|---|
| Voice AI widget — inline | JS snippet in index.html body | Enable Labs first; Embedded/Inline in Style tab |
| Chat widget — floating | JS snippet before </body> | Standard setup |
| Booking calendar | iFrame | Confirm in Section 3 of checklist |
| Contact form | JS or iFrame | Confirm in Section 2 |
| Missed call text-back | Backend only — no embed | A2P required |
| Review request | Backend only — no embed | A2P required; define trigger in Section 6 |

---

## SECTION 13: WEBSITE BEST PRACTICES BY NICHE

### Universal (All Niches)
- Phone in 4 locations: sticky header, hero, mid-page CTA band, footer
- All phone numbers: `href="tel:+1[digits]"` — never plain text
- Trust bar immediately after hero (4 items)
- Process section: 4 steps (niche-specific labels)
- Google Maps iFrame in service area section
- Specific neighborhoods — never "Greater [City] Area"
- Mobile-first: 390px iPhone width as baseline
- No video backgrounds
- Sticky header always visible
- Dynamic copyright: `{new Date().getFullYear()}`
- Professional favicon (not Vite default)

### Trade-Specific Primary CTAs
| Trade | Primary CTA | Secondary CTA | Booking Position |
|---|---|---|---|
| Plumbing | "Call Now — 24/7" | "Get Free Quote" | Below reviews |
| HVAC | "Emergency Service" | "Book Tune-Up" | Above reviews |
| Cleaning | "Book Your Clean" | "Get a Quote" | Above testimonials |
| Pest Control | "Same-Day Treatment" | "Free Inspection" | Below reviews |
| Roofing | "Free Inspection" | "Get a Quote" | Below reviews |
| Landscaping | "Free Quote" | "See Our Work" | Below testimonials |

---

## SECTION 14: KNOWN ISSUES AND FIXES

| Issue | Fix |
|---|---|
| Bolt badge on deployed site | Remove `<script async src="...bolt.new/badge.js...">` from index.html |
| Wrong OG image | Fix og:image in index.html manually |
| Vite favicon | Replace `/vite.svg` with custom favicon.svg in /public |
| Blank space below footer | GHL div with no content — add `min-height:0` |
| Maps showing wrong area | Update coordinates in iFrame src attribute |
| `netlify deploy` deploys source | Always use `netlify deploy --dir=dist --prod` |
| GHL voice widget not showing | Not enabled in Labs for sub-account — enable first |
| React hydration race with GHL | Place GHL script in index.html body, not JSX |
| SMS not delivering (US) | A2P 10DLC not registered — complete Section 1.5 |
| SMS not delivering (Canada) | Canadian A2P or Persona verification required (see Section 1.5) |
| Competitor fetch hangs 30+ min | Escape → "stop fetching, write outputs based on what you have" |
| index.html not redeploying via Bolt chat | Download ZIP → edit manually → deploy to Netlify Drop |
| Firecrawl returns incomplete data | Expected on unusual CMS — manual verification step catches this |
| SerpApi rate limit | Upgrade to paid plan at agency volume (>5 extractions/day) |

---

## SECTION 15: PRICING STRUCTURE

### Agency Packages
| Package | Setup Fee | Monthly | What's Included |
|---|---|---|---|
| Foundation | $997–$1,497 | $97/month | Website + GBP optimization + basic form |
| Growth System | $2,497–$3,497 | $297/month | Website + full GHL automation stack |
| Full System | $3,997–$5,497 | $497/month | Website + full stack + voice AI + reviews |

### Corrected Cost Structure per Client

**Platform costs (shared across clients):**
| Active Clients | GHL Share | SMS Usage | Total Platform COGS |
|---|---|---|---|
| 3 clients | ~$99–$166 | ~$10–15 | ~$109–$181 |
| 5 clients | ~$60–$99 | ~$10–15 | ~$70–$114 |
| 10 clients | ~$30–$50 | ~$10–15 | ~$40–$65 |

**Voice AI / Package 3 clients — additional:**
- GHL AI Employee: $97/month per sub-account (covers Conversation AI, Reviews AI,
  basic Voice AI call handling)
- **Important:** The Voice AI Widget (inline embed) and Agent Studio may incur
  additional per-use charges on top of the $97/month flat fee. Verify in your
  GHL billing before quoting Package 3 pricing.
- Treat $130–$180/month as a cost floor for Package 3, not a ceiling.
- Margin at $497 retainer: ~60–65% floor (may be lower depending on widget usage)

**Additional tooling:**
- Lovable Pro: $25/month (agency account — not per client)
- Netlify hosting: $0
- SerpApi: $0 free tier / $50–75/month at agency volume
- Domain: ~$12/year (client pays)

---

## SECTION 16: SALES DELIVERY STANDARDS

### Demo Build SLA
- First build per niche: 30–60 minutes
- Subsequent clients (same niche): 15–30 minutes
- Deliverable: Live Netlify URL to send in cold outreach

### Production Delivery SLA
- Total time: 2–4 hours
- Includes: Build + QA checklist + GHL widget activation + client approval round
- Domain cutover: additional 24–48 hours DNS propagation (schedule separately)

### Content Quality Standards
Before any site goes live, a human must verify:
- No placeholder text ([BUSINESS_NAME], [PHONE], Lorem Ipsum) remaining
- All phone numbers are the actual client phone number and tap-to-call works
- Service areas list specific neighborhoods (not city-wide vague language)
- Reviews are real, verbatim, attributed correctly
- All claims (licenses, guarantees, years in business) confirmed with client

### Legal and Compliance Pages
Every production site must include:
- Privacy Policy (basic — client's information handling)
- Terms of Service link (minimum)
- SMS consent language on any form that collects phone numbers:
  "By submitting this form, you consent to receive text messages from [Business Name].
  Reply STOP to unsubscribe."
  For Canadian clients sending to Quebec recipients: French opt-out text is legally
  required under Quebec's Charter of the French Language (not CASL itself).
  For GTA/Ontario-only campaigns, English STOP is legally sufficient under CASL —
  supporting French keywords (ARRET, FIN) is recommended as a carrier best practice.

---

## SECTION 17: QUESTIONS FOR PEER REVIEW (v2)

The following questions from v1 are now resolved — do not re-review:
- Antigravity CLI vs IDE: confirmed distinct ✅
- Lovable Pro credits: locked at ~150/month planning number ✅
- Lovable Design Templates: confirmed Business plan only ✅
- GHL tiers: confirmed $97/$297/$497 ✅
- GHL Voice AI inline embed: confirmed supported ✅
- Canadian SMS: full decision tree documented ✅
- Claude Code Netlify deployment: confirmed production-ready with --dir=dist ✅

**Questions for v2.1 review:**

1. **GHL AI Employee inline widget charges:** Beyond the $97/month AI Employee
   add-on, do the Voice AI Widget (inline embed) and Agent Studio incur additional
   per-use charges in 2026? Multiple sources suggest yes — confirm in your GHL
   account billing before finalizing Package 3 margins.

2. **Netlify account-level suspension:** When bandwidth (100GB) or build minutes
   (300/month) are exceeded on a free Netlify account, all sites on that account
   pause simultaneously for the month. At 10+ clients, is separate-account-per-client
   the right mitigation, or Netlify Pro ($19/month)?

3. **GHL AI Employee add-on pricing:** Is $97/month per sub-account still correct
   for full Voice AI features in 2026? Or is it usage-based?

4. **CASL French language requirement:** Is including French opt-out text mandatory
   for Ontario (GTA) businesses, or only for Quebec or federally-regulated entities?

5. **SerpApi `google_maps_reviews` field names:** Are `snippet` and
   `extracted_snippet.original` still the correct field names in the 2026 API?

6. **Netlify free tier limits:** Does Netlify's free tier impose bandwidth or
   build minute limits that would affect a 10+ client agency at scale?

7. **React + GHL widget hydration:** Is placing the GHL widget script in
   `index.html` body before `<div id="root">` confirmed as the correct
   React-safe placement, or is there a better pattern?

8. **GHL Snapshot portability:** Can a Snapshot built on a Starter plan be
   applied to sub-accounts on an Unlimited plan? Or is Snapshot creation
   restricted by plan tier?

9. **Firecrawl Lovable integration status:** Is the Firecrawl free-for-Lovable-users
   promotion still active as of the review date, or has it reverted to standard pricing?

10. **Overall v2 architecture validity:** With the --mode claude-code bug fixed,
    the Canadian SMS decision tree added, the GHL Voice AI inline placement confirmed,
    and the QA checklist added — is this system design now complete enough to
    execute reliably as a one-person agency for the first 10 clients?

---

## SECTION 18: WHAT'S BEEN BUILT AND VALIDATED

### Validated by Peer Review (all 5 LLMs across 2 rounds)
- Core architecture: external site + GHL automation via embed ✅
- Gemini 3.1 Pro Preview released Feb 19, 2026 ✅
- Bolt Cloud V2 has native backend ✅
- Lovable free tier: 30/month hard cap ✅
- Lovable Pro: ~150/month realistic planning number ✅
- Lovable Design Templates: Business plan only ✅
- GHL tiers: Starter $97 / Unlimited $297 / SaaS Pro $497 ✅
- GHL embed works on external hosts (test per deployment recommended) ✅
- GHL Voice AI widget: Embedded/Inline placement confirmed ✅
- Three-layer prompt architecture: sound and scalable ✅
- Claude Code + Netlify CLI: production-ready with --dir=dist ✅
- Two distinct Antigravity products: confirmed ✅
- SerpApi reviews endpoint: reliable for agency use ✅
- Firecrawl: JS-rendered sites handled well ✅

### Critical Fixes Applied (from v1 → v2)
- API keys removed from all documents — .env only ✅
- `--mode claude-code` architecture corrected to `--mode skill-output` ✅
- `netlify deploy --dir=dist --prod` documented everywhere ✅
- Canadian SMS: full decision tree added ✅
- GHL Voice AI: Labs activation step documented ✅
- React hydration: GHL script placement in index.html documented ✅
- GHL Snapshot: full procedure added to checklist ✅
- Domain cutover: full SOP added to checklist ✅
- Review request trigger: 3 concrete options defined ✅
- QA acceptance checklist: 25+ item checklist added ✅
- Time estimates corrected: demo 15–30 min, production 2–4 hours ✅
- Voice AI COGS corrected: ~$130–$180/month for Package 3 ✅
- SerpApi paid plan: noted for agency volume ✅

### Changes v2 → v2.1 (second peer review round — March 2026)
- GHL Starter = 3 sub-accounts confirmed — all uncertainty language removed ✅
- Lovable daily credit rollover confirmed: strictly resets, no accumulation — 150/month locked ✅
- AI Employee inline widget surcharge: added "floor not ceiling" caveat to COGS ✅
- React inline widget placement: logic flaw fixed — dual approach documented (Option A static HTML / Option B useEffect) ✅
- CASL French requirement: corrected from blanket requirement to Quebec-specific legal + national best practice ✅
- Netlify account-level suspension risk: documented with mitigation options ✅
- Firecrawl "~98% accuracy": unsourced precision removed — softened to "high reliability" ✅
- Firecrawl promo date: corrected from April 2026 to approximately January 2026 — verify live ✅
- vite.config outDir caveat: added to all Netlify deploy command references ✅
- vite.config outDir caveat applied to: SYSTEM_DESIGN_v2.1, AI_Website_Stack_v4.1, GHL_SETUP_CHECKLIST_v3, WEBSITE_GENERATION_SKILL.md ✅

### Built and Deployed
- Bolt.new plumbing demo: https://mississauga-plumbing-l1i4.bolt.host ✅
- All 6 GHL placeholder divs added ✅
- All known Bolt visual issues fixed ✅

### Built (Code Files)
- `execution/extract_business_data.py` ✅
- `execution/generate_website.py` (corrected architecture) ✅
- `docs/WEBSITE_GENERATION_SKILL.md` ✅
- `docs/master_prompts/universal_rules.txt` ✅
- `docs/master_prompts/plumbing_bolt_prompt.txt` ✅
- `docs/niches/plumbing.md` ✅
- `docs/niches/_NICHE_TEMPLATE.md` ✅
- `docs/GHL_SETUP_CHECKLIST_v3.md` ✅

### Still To Build
- `docs/niches/hvac.md` + `hvac_bolt_prompt.txt`
- `docs/niches/cleaning.md` + `cleaning_bolt_prompt.txt`
- `docs/niches/pest_control.md`, `roofing.md`, `landscaping.md`, `generic.md`
- First outreach to mississaugaplumbingservices.com
- GHL Master Snapshot (after first client fully onboarded)

---

*Document version: 2.0*
*Updated: March 2026*
*All v1 peer review issues resolved. New questions for v2 review in Section 17.*
