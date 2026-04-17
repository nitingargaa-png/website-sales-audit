# AI-Powered Local Business Website Agency — Complete System Context
## For LLM Peer Review
## Version: 1.0 — March 2026
## Author: Nitin, Etobicoke, Ontario

---

## PURPOSE OF THIS DOCUMENT

This document explains what this entire software system does, how every file fits
together, and the business logic behind each design decision. It is written for
peer review by other LLMs who have not seen this codebase before.

Please review for: logical consistency, missing edge cases, security risks,
scalability gaps, incorrect assumptions, and any broken workflows.

---

## SECTION 1: BUSINESS CONTEXT

### What This Is

A one-person digital agency that sells websites and marketing automation systems
to local home service businesses in the USA and Canada (primary focus: Greater
Toronto Area). Target trades: plumbing, HVAC, cleaning, pest control, roofing,
landscaping, electrical, painting, garage door, handyman, moving, junk removal.

### The Product

Two components sold together as a single system:

1. **A premium website** — built externally using AI tools (Bolt.new, Lovable,
   Claude Code), hosted on Netlify. NOT built inside GoHighLevel (GHL) because
   external AI tools produce significantly better design quality.

2. **A GHL automation stack** — voice AI receptionist, missed call text-back,
   review request workflows, CRM pipeline, booking calendar. Connects to the
   external website via JavaScript snippet embeds.

The website is the front-end. GHL is the back-end engine. They communicate via
JS embed codes that GHL generates and the website hosts as placeholder divs.

### Revenue Model

- Setup fee: $997–$5,497 (one-time, collected before production work begins)
- Monthly retainer: $97–$497/month (recurring)
- Goal: $10,000/month recurring retainer revenue

### Current Status

Pre-first-client. One prospect identified (mississaugaplumbingservices.com),
audited (score 1/10), demo site built (bolt.host), cold outreach not yet sent.

---

## SECTION 2: THE THREE PACKAGES

### Package 1 — Foundation ($997–$1,497 setup + $97/month)
Website only. No GHL automation. Basic quote form connected to email.
Intended for skeptical or budget-conscious buyers. Upsell path to Package 2
after 30–60 days via a specific follow-up email template.

### Package 2 — Growth System ($2,497–$3,497 setup + $297/month) ← sweet spot
Website + full GHL automation: missed call text-back, lead follow-up SMS,
booking calendar, CRM pipeline, chat widget, review request automation.
Recommended for most prospects, especially emergency trades (plumbing, HVAC).

### Package 3 — Full System ($3,997–$5,497 setup + $497/month)
Everything in Package 2 + voice AI receptionist inline widget + review AI.
Requires GHL AI Employee add-on ($97/month per sub-account, not covered by
base plan). Cost floor for Package 3 is approximately $130–$180/month in
platform costs before labor — margins are thinner here.

---

## SECTION 3: THE COMPLETE WORKFLOW (END TO END)

### Demo Mode (before client signs — no cost to build)

```
Step 1: Find a prospect
  └── Google Maps search or lead_pipeline.py script

Step 2: Run the audit
  └── Claude Code: "audit https://[url] and prepare full call prep"
  └── SKILL.md (v9) executes → 4-output report saved to output/

Step 3: Generate the site prompt
  └── python3 execution/generate_website.py --url https://[url] --mode bolt
  └── Internally: runs extract_business_data.py → structured_input.json
  └── Assembles three-layer prompt → saves to output/prompt_packages/

Step 4: Verify extracted data
  └── Open output/structured_input.json, confirm all fields correct
  └── grep -o "\[.*\]" output/prompt_packages/[file].txt (check no unfilled vars)

Step 5: Build demo site
  └── Paste prompt into Bolt.new (free tier, ~1M tokens/month)
  └── Attach logo + photos in chatbox before sending
  └── Bolt builds complete React + Tailwind site (~2–5 min)

Step 6: Deploy demo
  └── netlify deploy --dir=dist --prod  (--dir=dist is mandatory for Vite builds)
  └── OR: drag dist/ folder to netlify.com/drop
  └── Live URL returned (e.g., demo-business.netlify.app)

Step 7: Cold outreach
  └── One goal only: get them to view the demo link
  └── Do NOT pitch pricing on first contact
  └── Use SALES_SCRIPT_v2.md for call script and objection handlers
```

### Production Mode (after client signs)

```
Step 8: Collect setup fee (50% upfront, 50% on go-live)

Step 9: Run production extraction + build
  └── python3 execution/generate_website.py --url https://[url] --mode skill-output
  └── Saves JSON package to output/prompt_packages/

Step 10: Build production site in Claude Code
  └── In Claude Code (VS Code): "execute WEBSITE_GENERATION_SKILL.md using [package].json"
  └── Claude Code: scaffolds React project → pulls 21st.dev components →
      builds all components → npm run build → netlify deploy --dir=dist --prod
  └── Returns live Netlify URL

Step 11: QA checklist
  └── GHL_SETUP_CHECKLIST_v3.md Section 11 — 25+ items
  └── Real iPhone testing mandatory (not just DevTools)

Step 12: GHL setup
  └── GHL_SETUP_CHECKLIST_v3.md Sections 1–10 in order
  └── Critical dependencies (must not be skipped or reordered):
      - Section 1.5 (A2P SMS registration) BEFORE any SMS workflow
      - Section 8 (CRM pipeline) BEFORE Section 4 (lead follow-up workflow)
      - Voice AI Labs enabled BEFORE voice widget setup

Step 13: Domain cutover
  └── GHL_SETUP_CHECKLIST_v3.md Section 12
  └── DNS propagation: 24–48 hours

Step 14: After first client fully live — build GHL Master Snapshot
  └── Saves 3+ hours on every subsequent client
```

---

## SECTION 4: THE THREE-LAYER PROMPT SYSTEM

Every website prompt is assembled from three layers, stacked in order:

### Layer 1 — Universal Rules (docs/master_prompts/universal_rules.txt)
Applies to every site regardless of niche. Contains:
- Phone number placement rules (4 locations, always href="tel:+1XXXXXXXXXX")
- Mandatory section order (header → hero → GHL voice widget → trust bar → services
  → process → service areas → reviews → booking → contact → footer)
- All 6 GHL placeholder div specifications (exact IDs, required on every site)
- Technical requirements (React + Tailwind, mobile-first 390px, no video backgrounds,
  dynamic copyright year, no Lorem Ipsum)
- Design principles (trust-first, speed-first, generous whitespace)
- What NOT to include (no login, no Stripe checkout, no blog, no pricing page)

### Layer 2 — Audit-Specific Rules (generated per prospect)
Maps audit findings directly to generation rules. Not stored as a file —
assembled inline from structured_input.json. Examples:
- Audit: 166 reviews hidden → Rule: rating + count in hero subheadline; 3 review cards
- Audit: JS-only build → Rule: semantic HTML, server-renderable structure
- Audit: No tap-to-call → Rule: tel: href on every phone instance

### Layer 3 — Niche Rules (docs/niches/[trade].md)
Per-trade design rules. Currently built for: plumbing, hvac, electrical, cleaning,
roofing, generic (fallback). Still to build: pest_control, landscaping.

Each niche file defines:
- Primary emotion to trigger (urgency for plumbing, safety for electrical, etc.)
- CTA button text and primary action
- Color palette (all niches use navy primary; accent varies by emergency level)
- Section order overrides (cleaning is booking-first; plumbing is call-first)
- Trust bar items specific to the trade
- Default services list (fallback if extraction returns empty)
- Audit red flags → generation fixes mapping table
- Typical job values (for ROI conversations during sales)
- Cold outreach hook (specific to the trade)
- Pricing guidance

### Layer Precedence
When universal rules and niche rules conflict, niche rules always override.
Example: universal default is booking below reviews; cleaning niche overrides
booking to be above reviews (cleaning is a planned trade, not emergency).

### Variable Fill System
After the three layers are assembled, generate_website.py replaces 13 bracket
variables with real business data from structured_input.json:

| Variable | Source | Notes |
|---|---|---|
| [BUSINESS_NAME] | Firecrawl extraction | |
| [PHONE] | Firecrawl, fallback GBP | Formatted (647) XXX-XXXX |
| [PHONE_DIGITS] | Derived from PHONE | 1XXXXXXXXXX for tel: href |
| [CITY_PROVINCE] | CLI arg or Firecrawl | e.g., "Mississauga, ON" |
| [CITY] | Derived from CITY_PROVINCE | First word before comma |
| [SERVICES_LIST] | Firecrawl extraction | Comma-separated |
| [SERVICE_AREAS] | Firecrawl extraction | Specific neighborhoods |
| [REVIEWS_3] | SerpApi GBP reviews | 3 verbatim review texts |
| [REVIEW_COUNT] | SerpApi GBP | Total review count (e.g., 166) |
| [YEARS_IN_BUSINESS] | Firecrawl extraction | Falls back to "10+" |
| [RATING_STRING] | Derived from GBP data | e.g., "4.9★ (166 Google Reviews)" |
| [LOGO_URL] | Firecrawl extraction | URL to download logo |
| [NICHE] | Auto-detected | From _meta.niche in JSON |

---

## SECTION 5: THE DATA EXTRACTION SYSTEM

### Overview
Two API calls per prospect. Takes ~30–60 seconds. Outputs one JSON file.

### execution/extract_business_data.py

**Input:** Website URL and/or business name + city (command line args)
**Output:** output/structured_input.json (all 13 prompt variables + raw debug data)

**Step 1 — Firecrawl scrape (if URL provided):**
- Calls api.firecrawl.dev/v1/scrape with structured extraction schema
- Extracts: business name, phone, email, address, city, services list, hours,
  emergency availability, years in business, logo URL, photo URLs, neighborhoods
- Also returns raw markdown for niche keyword detection
- Timeout: 60 seconds. Gracefully skips on failure.

**Step 2 — SerpApi GBP pull (if SERPAPI_KEY present):**
- First call: engine=google_maps → finds listing, gets place_id, rating, review count
- Second call: engine=google_maps_reviews → pulls up to 5 verbatim review texts
- Falls back to domain as search query if no business name provided

**Step 3 — Merge and output:**
- Firecrawl is source of truth for site data
- GBP fills gaps (phone, address if Firecrawl missed them) and adds reviews
- Niche auto-detected via keyword scoring across NICHE_KEYWORDS dict
- CLI --niche flag overrides detection
- Saves structured_input.json to output/ (or custom --output path)
- Prints summary to terminal including extraction quality indicators

**Key design decisions:**
- Both API calls are optional — script degrades gracefully if keys missing
- Manual verification step is documented as mandatory (2–5 minutes)
  because automated extraction has gaps on unusual CMS platforms
- REVIEW_COUNT written separately from RATING_STRING so templates can use either

### execution/generate_website.py

**Input:** structured_input.json (via --input) or URL (runs extraction first)
**Output:** Assembled prompt saved to output/prompt_packages/ as .txt or .json

**Five output modes:**

| Mode | Output | Use case |
|---|---|---|
| bolt | .txt prompt for Bolt.new chatbox | Demo builds (free) |
| lovable | .txt prompt (same as bolt) | Demo/production on Lovable |
| gemini | .txt with cinematic additions | Gemini 3.1 Pro Preview in AI Studio |
| claude-code | .txt for Claude Code in VS Code | Single index.html, no build step |
| skill-output | .json package | Autonomous Claude Code production build |

**Assembly logic:**
1. Load structured_input.json
2. Detect niche from _meta.niche
3. Check if pre-built prompt exists (e.g., plumbing_bolt_prompt.txt)
   - If yes: load it, run fill_variables(), return filled prompt
   - If no: assemble from universal_rules.txt + niche file, build prompt inline
4. Run fill_variables() to replace all [BRACKET] variables
5. Save to output/prompt_packages/ with timestamped filename
6. Print next-steps instructions to terminal

**Important architecture note:**
This script cannot invoke Claude Code. Python cannot subprocess Claude Code.
For production builds, this script outputs a JSON package which Claude Code
then reads and executes autonomously via WEBSITE_GENERATION_SKILL.md.

---

## SECTION 6: THE SIX GHL PLACEHOLDER DIVS

Every site, every niche, every mode must include all 6. IDs are exact and cannot
be renamed — GHL JavaScript looks for these specific IDs.

```html
<!-- 1. Voice AI inline widget — between hero and trust bar -->
<div id="ghl-voice-inline">...</div>

<!-- 2. Booking calendar — in booking section -->
<div id="ghl-calendar">...</div>

<!-- 3. Contact/quote form — in contact section -->
<div id="ghl-contact-form">...</div>

<!-- 4. Live Google Reviews widget — below testimonial cards -->
<div id="ghl-reviews">...</div>

<!-- 5. Pay Invoice link — in footer -->
<a href="#" id="ghl-payment-link">Pay Invoice</a>

<!-- 6. Floating chat widget — last element before </body> -->
<div id="ghl-chat-widget"></div>
```

### Critical: Voice AI Widget Placement (React-specific)

The inline voice widget (#1) requires special handling in React apps because
the placeholder div lives inside the React component tree and doesn't exist in
the DOM until React mounts. Two safe options:

**Option A (recommended):** Place ghl-voice-inline as static HTML in index.html
OUTSIDE `<div id="root">`, so it exists before React hydrates:
```html
<div id="ghl-voice-inline"></div>
<script>/* GHL inline widget JS */</script>
<div id="root"></div>
```

**Option B:** Use useEffect in the React component that renders the placeholder:
```javascript
useEffect(() => {
  const s = document.createElement('script');
  s.innerHTML = `/* GHL widget init */`;
  document.getElementById('ghl-voice-inline').appendChild(s);
}, []);
```

**Wrong (silently fails):** Placing the GHL script before `<div id="root">` —
the target div doesn't exist yet, the widget falls back to floating mode with
no error message.

**Prerequisite:** Voice AI must be enabled in GHL Labs for the sub-account
BEFORE the widget will function. Skipping this step fails silently.

---

## SECTION 7: THE WEBSITE AUDIT SKILL (docs/SKILL.md)

### What It Does
Fetches a prospect's website, evaluates it across 10 areas, and produces 4 outputs
in a single Claude Code session triggered by: `"audit https://[url] and prepare full call prep"`

### The 10 Checks
1. First impressions & design (modern vs dated, builder badges, email type)
2. Mobile experience (viewport meta, tap-to-call, responsive layout)
3. Contact & booking (forms, phone prominence, response promise)
4. Local presence (city name, specific neighborhoods vs vague "Metro Area")
5. Trust & credibility (reviews count, real vs stock photos, licenses)
6. Content completeness (trade-specific checklist — different per niche)
7. Speed & performance (PageSpeed API attempt; mobile score thresholds)
8. Photos & visual authenticity (real team photos vs generic stock)
9. Site security (HTTPS)
10. Lead capture & follow-up system (form, CRM signals, automation)

### The 4 Outputs (produced every time, mandatory)
- **Report A:** Short (under 350 words) — owner-facing, punchy, lead with business impact
- **Report B:** Medium (800–1,200 words) — owner-facing, detailed area-by-area breakdown
- **Report C:** Content & Components Gap Summary — checklist format, owner-facing
- **Talking Points:** Internal sales reference — not shared with client

### Key Design Rules Built Into SKILL.md
- Banned words list (50+ terms): SEO, CTA, UX, leverage, streamline, boost, etc.
- No fabricated scores — if PageSpeed API unavailable, write "Not available"
- No hype: never use "transform," "revolutionize," "skyrocket"
- Every finding must be observable — cite the specific page/element
- One analogy maximum per full output set (Overview section only)
- Domain knowledge section (trade job values, how customers decide, competitive benchmarks)
  ensures reports sound like they came from someone who understands the business

### Known Issue
Fetching competitor sites in Claude Code can hang for 30+ minutes.
Fix: Press Escape → type "stop fetching. write all four report outputs now
based on what you gathered, skip competitor section, save to output/[filename].md"

---

## SECTION 8: THE AUTONOMOUS BUILDER (docs/WEBSITE_GENERATION_SKILL.md)

### What It Does
A Claude Code skill that reads a skill-output JSON package and autonomously:
1. Checks prerequisites (Node 18+, Netlify CLI, auth)
2. Scaffolds a React + Tailwind project with npm create vite@latest
3. Selects designer components from 21st.dev (prevents generic AI aesthetics)
4. Builds all 11 components (Header, Hero, TrustBar, Services, Process, Reviews,
   ServiceAreas, Booking, Contact, Footer + favicon)
5. Places all 6 GHL placeholder divs
6. Runs npm run build — verifies no errors
7. Deploys: netlify deploy --dir=dist --prod
8. Returns a live Netlify URL

### The 21st.dev Integration
Before writing any component, the skill selects pre-built designer components
from 21st.dev to replace generic AI-generated equivalents:
- Hero background: dot grid or animated paths (removes flat color hero)
- Service cards: glassmorphism or feature cards (removes plain white boxes)
- CTA buttons: shimmer or gradient variants (removes default Tailwind button)
- Trust bar: animated stat counters (removes static numbers)

This is the primary mechanism that separates agency-quality output from
generic AI-generated sites.

### Invocation
This skill CANNOT be called from Python. It can only be invoked interactively:
In Claude Code (VS Code): `"execute WEBSITE_GENERATION_SKILL.md using [package].json"`

---

## SECTION 9: GHL PLATFORM SETUP (docs/GHL_SETUP_CHECKLIST_v3.md)

### Plan Tiers (March 2026)
| Plan | Price | Sub-accounts | When to upgrade |
|---|---|---|---|
| Starter | $97/month | 3 (1 agency + 2 clients) | Upgrade before client 3 |
| Unlimited | $297/month | Unlimited | Client 3+ |
| SaaS Pro | $497/month | Unlimited + white-label | At scale/reselling |

Voice AI add-on: $97/month per sub-account (not included in base plans).
Inline widget and Agent Studio may have additional per-use charges on top of
the flat $97 — verify in GHL billing before committing to Package 3 pricing.

### SMS Compliance — Canadian Clients (GTA Focus)
This is the most complex compliance area in the system. The decision tree:

```
Was the GHL number purchased BEFORE March 26, 2025?
  YES → CA→CA messaging: no A2P required (grandfathered)
       BUT: if ANY messages go to US numbers → A2P mandatory
       RECOMMENDED: register A2P anyway (carriers converging)
  NO  → CA→CA: A2P OR Persona verification required
       CA→US: A2P mandatory (no Persona option)

CASL applies regardless of A2P status:
  - Express consent required before first message
  - Sender ID in every message ("— Business Name")
  - STOP opt-out in every first message
  - French opt-out keywords (ARRET, FIN): legally required for Quebec recipients
    under Quebec's Charter of the French Language; English STOP is sufficient
    for Ontario-only campaigns; French keywords recommended as best practice
```

### Section Dependencies (must be completed in order)
- Section 1.5 (A2P registration) → BEFORE any SMS workflow goes live
- Section 8 (CRM pipeline) → BEFORE Section 4 (lead follow-up workflow)
- Voice AI Labs enabled → BEFORE voice widget setup in Sites

### Section 11 — QA Acceptance Checklist
25+ items checked before any site goes live, including mandatory real iPhone
testing (DevTools is insufficient). Key items:
- Tap-to-call opens phone dialer on real device
- All 6 GHL placeholder divs visible with dashed borders
- No [BRACKET] variables remaining in any visible text
- Dynamic copyright year (not hardcoded)
- No builder badge scripts in page source

---

## SECTION 10: SALES SYSTEM

### docs/SALES_SCRIPT_v2.md
Cold call script with:
- Pre-call prep checklist (5 pieces of info to know before dialing)
- Gatekeeper script (for businesses with spouse/office manager answering)
- Opening (60 seconds)
- The Hook — 8 variants based on specific audit finding
- Two-minute bridge (transition when time is up)
- Discovery questions
- Soft close
- Full objection handlers: "website works fine," "get business from referrals,"
  "can't afford it," "already tried a website," "friend handles our website,"
  "too busy," "happy with current site," "how much does it cost," "have SEO/ads"

### docs/PACKAGING_PRICING_GUIDE_v2.md
Three packages with full detail:
- What's included vs excluded per package
- Pricing ranges (setup + monthly)
- Upsell path from Package 1 → 2 → 3
- Founding client framing ("Case Study Credit" — reduces price without discounting)
- ROI anchors per trade (one missed plumbing emergency = $400–$800 recovered cost)
- Monthly cost structure per client at different scales

---

## SECTION 11: THE NICHE FILE SYSTEM (docs/niches/)

### Built Niches (7 files)
- **plumbing.md** — emergency + urgency primary emotion; call-first design;
  60-minute arrival promise; navy/red palette; booking BELOW reviews
- **hvac.md** — emergency + planned work dual track; financing badge; seasonal
  messaging; equipment brands listed
- **electrical.md** — safety first (unique among emergency trades); credentials
  and licensing lead copy; "done right" over "done fast"
- **cleaning.md** — relief + pride emotion; booking ABOVE reviews (booking-first);
  no emergency CTA; recurring service options; bonded/insured prominent
- **roofing.md** — highest-ticket trade; protection + trust; free inspection
  as primary CTA (foot-in-the-door); insurance claim handling differentiator;
  financing critical
- **generic.md** — fallback for unrecognized trades; professional/reliable tone;
  generic service defaults; used when niche detection scores zero
- **_NICHE_TEMPLATE.md** — blank template for adding new niches (15–30 min to fill)

### Still To Build
- pest_control.md — same-day urgency; "safe for kids and pets" critical
- landscaping.md — seasonal services; visual portfolio primary trust signal

### How Niche Detection Works
extract_business_data.py scores the scraped text against keyword lists for each
niche. Highest score wins. Falls back to "generic" if all scores are zero.
CLI --niche flag overrides detection entirely for edge cases.

---

## SECTION 12: THE PROMPT FILES (docs/master_prompts/)

### universal_rules.txt (Layer 1)
~150 lines. Loaded for every site regardless of niche or mode.
Not editable by niche — add niche-specific rules in Layer 3 only.

### plumbing_bolt_prompt.txt
Pre-built complete prompt for plumbing + Bolt.new/Lovable.
Structured as 14 numbered sections with exact copy, colors, and layout instructions.
Includes fallback copy for every variable (if extraction returns empty).
Loaded by generate_website.py when niche=plumbing AND mode=bolt or lovable.

### plumbing_gemini_prompt.txt
Cinematic variant for Gemini 3.1 Pro Preview in Google AI Studio.
Adds scroll-triggered animations, parallax, CSS keyframe entrance animations.
Includes a "converter prompt" to rewrite the multi-file React output as
single vanilla HTML for cases where a build step isn't practical.
Use thinking level HIGH.

### plumbing_claude_code_prompt.txt
Variant for Claude Code in VS Code. Outputs single index.html (no build step).
Includes Puppeteer screenshot loop — Claude Code takes screenshots at 390px
after each major section and self-corrects before continuing.
Checks for CLAUDE.md (WEBSITE_CLAUDE.md) before writing any code.

### Lovable mode
No separate file — uses plumbing_bolt_prompt.txt (same React/Tailwind stack).

---

## SECTION 13: PROJECT CONFIGURATION FILES

### CLAUDE.md (root)
Claude Code project configuration. Claude Code reads this before every action
in the project. Contains:
- Project purpose and context
- Trigger commands ("audit [url]" → executes SKILL.md)
- Key file locations for all 25+ files
- Known issue: competitor fetch hang fix
- API keys reminder (in .env only)
- Deploy command reminder (netlify deploy --dir=dist --prod)

### EXECUTION_GUIDE.md (root)
Complete step-by-step operating manual. Eight parts:
- Part 1: One-time setup (60 minutes)
- Part 2: Demo mode workflow (Phases A–G)
- Part 3: Production mode workflow (Steps 1–7)
- Part 4: Reference table (what each doc does)
- Part 5: Adding a new niche
- Part 6: Daily operating rhythm
- Part 7: Cost structure at each stage
- Part 8: Quick command reference

### docs/WEBSITE_CLAUDE.md
Copied into every new client project folder as CLAUDE.md before building.
This is the "design skill" — Claude Code reads it before every frontend action.
Contains: color rules (no purple, navy/red only), phone rule (tel: href always),
GHL placeholder rule, screenshot loop rule, section order, code quality rules,
deploy checklist. Enforced automatically without mentioning in prompts.

### docs/CLAUDE_CODE_SETUP.md
One-time setup guide for the claude-code workflow. Run once globally:
- Install Puppeteer (for screenshot loop)
- Install Netlify CLI + authenticate
- Per-client: copy WEBSITE_CLAUDE.md into client folder as CLAUDE.md

---

## SECTION 14: API KEYS AND SECURITY

All API keys stored in .env at project root. Never in any document.

Required keys:
- FIRECRAWL_API_KEY — site scraping via Firecrawl
- SERPAPI_KEY — Google Business Profile data via SerpApi
- NETLIFY_AUTH_TOKEN — deployment via Netlify CLI
- NETLIFY_SITE_ID — optional, omit to create new site automatically

If any key is ever committed to Git or pasted into a document: rotate immediately.
.env is in .gitignore. output/prompt_packages/ is also in .gitignore
(generated files with business data should not be committed).

---

## SECTION 15: COST STRUCTURE

### Pre-Revenue (right now)
| Tool | Cost |
|---|---|
| Bolt.new free tier | $0 |
| Netlify free tier | $0 |
| SerpApi free tier | $0 (<5 extractions/day) |
| Firecrawl | $0–$50/month (verify at app.firecrawl.dev — promo with Lovable expired ~Jan 2026) |
| **Total** | **$0–$50/month** |

### First Client Signed
| Tool | Cost |
|---|---|
| GHL Starter | $97/month |
| Lovable Pro (production builds) | $25/month |
| **Total** | **$122/month** |

### At 4+ Clients
| Tool | Cost |
|---|---|
| GHL Unlimited | $297/month |
| Lovable Pro | $25/month |
| Netlify Pro (critical at 5+) | $19/month |
| SerpApi paid (>5 extractions/day) | $50–75/month |
| **Total** | **~$391–$416/month** |

### Package 3 Clients (Voice AI)
Add $97/month per sub-account for GHL AI Employee.
Treat $130–$180/month as cost floor for Package 3 — Voice AI Widget and
Agent Studio may add per-use charges on top of the flat $97.

### Netlify Free Tier Risk
100GB bandwidth + 300 build minutes per month apply account-wide.
One traffic spike pauses ALL sites on that account simultaneously.
Upgrade to Netlify Pro ($19/month) at 5+ clients, or use one Netlify account
per client to isolate overage risk.

---

## SECTION 16: TECHNOLOGY STACK DECISIONS

### Why External Site + GHL Embed (Not GHL's Native Builder)
GHL's native site builder produces lower design quality than external AI tools.
GHL automations (voice AI, workflows, CRM) connect via JS embed regardless of
hosting platform. External hosting + GHL back-end is confirmed architecture.

### Why Netlify (Not GHL Hosting)
Netlify provides automatic HTTPS, instant deploys, custom domains, and no
per-site cost at free tier. GHL hosting is less flexible. Netlify CLI enables
one-command deploys from any build tool.

### Why React + Tailwind (Not WordPress/Elementor)
All primary AI tools (Bolt.new, Lovable, v0, AI Studio) output React/Tailwind
natively. No translation layer needed. Claude Code can build and deploy React
projects autonomously. Template-based WordPress requires manual editing that
defeats the AI-first workflow.

### Why Bolt.new for Demos (Not Lovable)
Bolt.new free tier: ~1M tokens/month, sufficient for 5–10 demo sites.
Lovable free tier: 30 credits/month hard cap — insufficient for demos.
Lovable Pro (150 credits/month realistic) is reserved for production builds.

### The Claude Code Architecture (Important)
Claude Code is an agentic VS Code extension that reads files, writes files,
and runs terminal commands autonomously. It is NOT invocable from Python.
The correct production workflow is:
1. Python generates skill-output JSON package
2. Human opens Claude Code and types the execute command
3. Claude Code reads the package and builds autonomously

There is no fully automated end-to-end pipeline. Step 2 requires a human
to open VS Code and run the command. This is intentional for quality control.

---

## SECTION 17: KNOWN LIMITATIONS AND OPEN QUESTIONS

### Architecture Limitations
- No fully automated pipeline — human opens Claude Code for production builds
- `input/prospects.csv` exists and is gitignored; it is partially populated with test rows
  from the extraction pipeline. The tracking schema is defined in EXECUTION_GUIDE.md
  (PROSPECTS TRACKER section). It is not yet being updated consistently after every outreach
  action — make this a daily operating habit once outreach begins.
- No automated bracket check before Bolt paste (manual grep required)
- Lovable Pro limit: ~150 actions/month realistically — may constrain at scale

### Open Questions — Resolved (Round 2 Peer Review, April 2026)

All 7 open questions from this section were answered by the 6-LLM Round 2 review.
Answers are recorded in PEER_REVIEW_ROUND2_SYNTHESIS.md. Summary:

1. **GHL AI Employee $97/month** — Platform license only. Voice AI adds ~$0.05–$0.15/min
   telephony charges. Busy emergency trades (500 min/month) = +$50–75/month on top.
   Document in proposals as "$97 base + variable telephony — typically $15–40/month."

2. **Netlify suspension mitigation** — Per-client Netlify accounts by client 5.
   Cloudflare Pages at 50+ clients. Both confirmed superior to single-account Pro plan.
   See updated scaling table in EXECUTION_GUIDE.md.

3. **SerpApi field schema** — Use `extracted_snippet.original` first, then `snippet`
   fallback. Field `text` is deprecated. Code updated in extract_business_data.py.

4. **Snapshots across plan tiers** — YES, Starter snapshots apply to Unlimited
   sub-accounts. Snapshots are agency-level assets, not plan-locked. Confirmed 5/5.

5. **CASL French opt-out** — French keywords (ARRET, FIN) legally required for Quebec
   recipients only. Ontario-only campaigns: English STOP is sufficient. French keywords
   recommended as national best practice for all Canadian clients. See GHL_SETUP_CHECKLIST.

6. **Firecrawl reliability** — Gaps expected on unusual CMS platforms (some Wix, custom
   PHP, heavy JS). Manual verification step (2–5 min) catches these. Keep the step.

7. **Bolt.new free tier at scale** — 1M tokens/month covers 5–10 demo builds. At 10+
   builds/week, free tier will hit limits. Upgrade to Bolt Pro or alternate to Lovable.

### Remaining Open Architecture Questions (Post Round 2)
1. ~~Call recording consent~~ — RESOLVED: v1.5 prompt hardcodes AI disclosure + recording
   disclosure as the first line of every call (Section 2.1, 2.3). No manual fix needed.
2. Voicemail detection: does GHL's Voice AI reliably detect voicemail systems before
   speaking, or does it occasionally leave partial messages? v1.5 Section 10.17 handles
   outbound voicemail — test with real carriers on first live deployment.
3. Google Places API exact SKU tier for combined Basic + Contact data requests —
   confirm actual per-prospect cost in GCP billing console after first 10 extractions.

### Bugs Fixed (Previously Known, Now Resolved)
- [REVIEW_COUNT] was never written to structured_input.json (now fixed)
- generate_website.py used str | None syntax incompatible with Python 3.9 (now fixed)
- EXECUTION_GUIDE Phase C showed --business and --city flags not accepted by
  generate_website.py (now fixed)
- phantom `npx claude-skills install frontend-design --global` command appeared in
  4 files — no such npm package exists (now removed from all files)
- subprocess.run() in run_extraction() lacked check=True — extraction failures
  were silently swallowed (now fixed)
- GHL voice widget placement instruction in SYSTEM_DESIGN Section 11 still had
  the old wrong "BEFORE root" instruction despite fix being documented in
  Section 18 change log (now fixed)

### Round 2 Fixes Applied (April 2026)
- `.gitignore` updated: added `output/*.md`, `input/*.csv`, `input/*.xlsx`,
  `.cache/`, `.vscode/` — all PII-containing file patterns now excluded from git
- `prospects.csv` contradiction resolved: file exists, is gitignored, partially
  populated; needs consistent update habit once outreach begins
- GHL upgrade timing corrected: client 4 (not client 3) — math documented in
  GHL_SETUP_CHECKLIST_v3.md with cost-per-client rationale
- Netlify scaling plan added to EXECUTION_GUIDE: per-client accounts by client 5,
  Cloudflare Pages at 50+ clients, with table and setup notes
- GCP billing alert documented in EXECUTION_GUIDE: set at $50/month
- CASL M-C3 consent gap fixed: first SMS must be consent request, not commercial
  message; `sms-consent-given` tag required before commercial follow-up
- After-hours SOP rewritten in GHL_SETUP_CHECKLIST: three paths (A/B/C) with
  carrier USSD codes for Rogers, Bell, Telus, AT&T, Verizon, T-Mobile
- KB maintenance process documented in GHL_SETUP_CHECKLIST
- Post-import validation checklist added (5 tests): Voice AI fires, notification
  recipients correct, calendar reference correct, primary bot active, custom fields present
- Voice AI Snapshot update noted: agents NOW transfer via snapshot (minus phone number);
  GHL_SETUP_CHECKLIST updated to include "Voice AI" component in snapshot export
- Voice AI prompt v1.5 Universal Template deployed (22 niches, 14 sections, 57 fixes):
  supersedes v1.4 patch plan — all v1.4 fixes are incorporated in v1.5 natively.
  Deployment guide: docs/master_prompts/VOICE_AI_PROMPT_v1.5_DEPLOY_GUIDE.md
  New in v1.5 vs v1.3: business hours gating via is_business_hours workflow (S4.2),
  availability_framing custom value replaces hardcoded same-day promise (S5.3),
  life-safety 911 override (S2.7), Universal System Fallback (S10.19), 22 niche
  emergency trigger blocks (S6.3), 22 niche qualification handler blocks (S8.1)
- Client number messaging corrected in SALES_SCRIPT_v2.md: "you get a new AI number;
  your existing number stays as-is" — removed misleading "route behind the scenes" language
- Client offboarding SOP added to EXECUTION_GUIDE: 7-step process covering data export,
  Netlify handoff/deletion, GHL wind-down, DNS, records, and final communication
- SYSTEM_CONTEXT open questions section updated: all 7 questions answered and closed;
  3 new post-Round-2 questions added

---

## SECTION 18: FILE INVENTORY

```
website-sales-audit/
│
├── CLAUDE.md                          ← Claude Code project config, trigger commands
├── EXECUTION_GUIDE.md                 ← Complete step-by-step operating manual
├── SYSTEM_CONTEXT.md                  ← This document (add to project root)
├── requirements.txt                   ← Python deps: requests, python-dotenv
│
├── docs/
│   ├── SKILL.md (v9)                  ← Website audit skill (1,293 lines)
│   ├── SKILL_website-sales-audit.md   ← Duplicate of SKILL.md for Claude Code context
│   ├── WEBSITE_GENERATION_SKILL.md    ← Autonomous React builder for Claude Code
│   ├── WEBSITE_CLAUDE.md              ← Per-client CLAUDE.md (design rules)
│   ├── CLAUDE_CODE_SETUP.md           ← One-time setup guide for claude-code mode
│   ├── SYSTEM_DESIGN_v2.1.md          ← Full system design doc (peer-reviewed, 2 rounds)
│   ├── AI_Website_Stack_v4.1.md       ← Tech stack decisions and validation
│   ├── GHL_SETUP_CHECKLIST_v3.md      ← GHL onboarding procedure (606 lines)
│   ├── SALES_SCRIPT_v2.md             ← Cold call script + objection handlers (379 lines)
│   ├── PACKAGING_PRICING_GUIDE_v2.md  ← Three packages + pricing logic (288 lines)
│   │
│   ├── master_prompts/
│   │   ├── universal_rules.txt        ← Layer 1: rules for every site
│   │   ├── plumbing_bolt_prompt.txt   ← Complete Bolt/Lovable prompt (plumbing)
│   │   ├── plumbing_gemini_prompt.txt ← Cinematic Gemini prompt (plumbing, 866 lines)
│   │   ├── plumbing_claude_code_prompt.txt ← Single-file Claude Code prompt
│   │   └── VOICE_AI_PROMPT_v1.5_DEPLOY_GUIDE.md ← v1.5 Universal deployment guide:
│   │                                              custom values table (10 values),
│   │                                              business hours workflow, SWAP items,
│   │                                              M-C1 structure, go-live test matrix
│   │
│   └── niches/
│       ├── _NICHE_TEMPLATE.md         ← Blank template for new niches
│       ├── generic.md                 ← Fallback for unrecognized trades
│       ├── plumbing.md                ← Plumbing niche rules (Layer 3)
│       ├── hvac.md                    ← HVAC niche rules (Layer 3)
│       ├── electrical.md              ← Electrical niche rules (Layer 3)
│       ├── cleaning.md                ← Cleaning niche rules (Layer 3)
│       └── roofing.md                 ← Roofing niche rules (Layer 3)
│
├── docs/archive/
│   └── BOLT_PLUMBING_TEMPLATE_deprecated.md  ← archived; not loaded by any script
│
├── execution/
│   ├── extract_business_data.py       ← Firecrawl + SerpApi extraction (~380 lines) ✅
│   ├── generate_website.py            ← Prompt assembler + orchestrator (~450 lines) ✅
│   │
│   │   NOTE: The 4 scripts below exist on the owner's local machine from a prior
│   │   project phase but are NOT included in this document zip. They are part of
│   │   the full project at C:\Users\canad\projects\website-sales-audit\ but managed
│   │   separately. Reviewers: you do not need these files to review this system.
│   ├── lead_pipeline.py               ← Lead gen from Google Maps (local machine only)
│   ├── email_verifier.py              ← Email verification (local machine only)
│   ├── utils.py                       ← Shared utilities (local machine only)
│   └── claude_extractor.py            ← Claude-based extraction (local machine only)
│
├── input/
│   └── urls.txt                       ← Prospect URLs for batch processing
│
└── output/
    ├── prompt_packages/               ← Generated prompt files saved here (gitignored)
    └── mississaugaplumbingservices-2026-03-08.md ← First audit report
```

---

## SECTION 19: WHAT SUCCESS LOOKS LIKE

### First Client Closed
1. mississaugaplumbingservices.com has viewed the demo at bolt.host
2. Discovery call scheduled
3. Growth System ($2,497 setup + $297/month) proposed
4. 50% setup fee collected
5. Production site built in Claude Code via WEBSITE_GENERATION_SKILL.md
6. GHL_SETUP_CHECKLIST_v3.md Sections 1–10 complete
7. QA checklist passed on real iPhone
8. Site live on client's domain
9. GHL workflows active: missed call text-back, review requests
10. GHL Master Snapshot built for use on all future clients

### First $10K/Month

**Target client mix (verified math):**

| Mix | Monthly Revenue |
|---|---|
| 34 clients at $297/month | $10,098 ✅ |
| 25 × $297 + 5 × $497 | $7,425 + $2,485 = $9,910 ≈ $10K ✅ |
| 20 × $297 + 4 × $497 | $5,940 + $1,988 = $7,928 (not $10K) |

**Recommended path:** 25 Growth System clients + 5 Full System clients.
This is more realistic than 34 pure $297 accounts — Package 3 closes at higher
intent and the $497 retainer takes 2 fewer clients to hit the number.

> Note: "~25–30 clients at $297/month = $10K" was incorrect math (30 × $297 = $8,910).
> The correct target is ~34 clients at $297-only, or a mixed portfolio as above.

- Platform cost at that scale: ~$415–$500/month (GHL $497 + Netlify Pro $19)
- Net margin before owner labor: ~93–95%

---

*Document version: 1.0*
*Last updated: March 2026*
*Status: Ready for peer review*
