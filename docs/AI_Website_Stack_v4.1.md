# AI Website Building Stack for Local Home Service Businesses
## v4.1 — Updated per 5-LLM peer review of v4.0 (second round)
## Date: March 2026
## Status: All v4.0 issues resolved. One open question for v4.1 review in Section 9.

---

## WHAT CHANGED FROM v3.3 → v4.0

| Item | v3.3 Claim | v4.0 Correction | Source |
|---|---|---|---|
| Lovable Pro credits | "~250 total/month" | ~150/month realistic floor; 250 requires daily login — use 150 for planning | Confirmed by 4 of 5 reviewers |
| generate_website.py --mode claude-code | "Python invokes Claude Code" | WRONG — Python cannot subprocess Claude Code. Corrected to --mode skill-output (outputs package file) | Architecture fix |
| netlify deploy command | Unspecified | `netlify deploy --dir=dist --prod` — --dir=dist is MANDATORY | Critical bug fix |
| GHL Voice AI widget | "Floating only / unclear" | Embedded/Inline placement confirmed — must enable Labs first | GHL docs confirmed |
| React + GHL widget | Unspecified | Place GHL script in index.html body BEFORE <div id="root"> — not in JSX (hydration race) | GHL + React pattern fix |
| Canadian SMS | "Separate from A2P" | Converging 10DLC regime — full decision tree by purchase date and direction | GHL Feb 2026 docs |
| GHL Starter sub-accounts | "Covers 3 clients" | Confirmed: 3 sub-accounts (1 agency + 2 clients) — official GHL pricing page | Resolved ✅ |
| GHL Voice AI COGS | Not specified | $97/month per sub-account (AI Employee add-on) — not included in base Unlimited plan | Corrected |
| Package 3 COGS | ~$57/month | ~$130–$180/month with Voice AI add-on | Corrected |
| Time estimates | "5 min per site / 15 min per client" | Demo draft: 15–30 min. Production-ready: 2–4 hours | Corrected per all reviewers |
| QA checklist | Missing | Full 25+ item QA checklist added to GHL_SETUP_CHECKLIST_v3.md | Added |
| GHL Snapshot | Missing entirely | Full Snapshot procedure added — saves 3+ hours per client | Added |
| Domain cutover | One-liner | Full SOP added: DNS records, propagation check, SSL, rollback | Added |
| Review request trigger | "Post-job" (undefined) | 3 concrete options defined: tech form, manual CRM, missed-call proxy | Added |
| API keys in documents | Keys in plain text in v1 | NEVER in documents — .env only | Security fix |
| SerpApi at agency volume | Free tier assumed | Paid plan ($50–75/month) needed at >5 extractions/day | Added |

---

## RECOMMENDATION: OPTION B — LOVABLE FOR EVERYTHING

No change from v3.3. Lovable remains the recommended primary tool.
Fewer moving parts. No demo/delivery gap. One tool to master.
Revisit Option A (Gemini cinematic) at 5+ clients for a visual-premium tier.

---

## SECTION 1: CONFIRMED ARCHITECTURE

### The Stack
```
[Bolt.new free] → demo site → [Netlify Drop]
                                    ↓ (if client signs)
[Lovable Pro $25/mo] → production site → [Netlify via GitHub]
                                               ↓
                                   [GHL JS snippet embed]
                                               ↓
                         [GHL: Voice AI, CRM, missed call text-back,
                          review requests, calendar, follow-up workflows]
```

### GHL Embed — Confirmed With Tested Caveats
- GHL chat/voice widget and calendar/form iFrames work on external hosts
- Standard Netlify deployments have no CSP restrictions by default
- **Test each deployment:** script placement, ad-blocking, mobile rendering
- **React placement:** GHL scripts in `index.html` body BEFORE `<div id="root">`, not in JSX
- **Voice AI Labs:** must be enabled per sub-account before inline widget functions

### A2P 10DLC — Mandatory for US SMS
Register before activating any US SMS workflows. Unregistered numbers fail silently.

### Canadian SMS — Converging 10DLC Framework
NOT simply "separate from A2P." Decision tree:
- CA→US (any direction): A2P mandatory for all Canadian numbers
- CA→CA, number bought AFTER March 26, 2025: A2P OR Persona verification required
- CA→CA, number bought BEFORE March 26, 2025: grandfathered but loses exemption if US messages sent
- CASL consent, sender ID, and STOP mechanism required regardless of A2P status
- French opt-out keywords (ARRET, FIN, DÉSABONNER): legally required for Quebec
  recipients under Quebec's Charter of the French Language — not a CASL requirement.
  For GTA/Ontario-only campaigns, English STOP is legally sufficient. Supporting
  French keywords is recommended as Canadian carriers may enforce bilingual opt-out.
Full decision tree: GHL_SETUP_CHECKLIST_v3.md Section 1.5

---

## SECTION 2: TOOL REFERENCE — FINAL

### PRIMARY TOOL

**Lovable (lovable.dev)**
- Full-stack: frontend + Supabase backend + auth + API from chat prompts
- ARR: ~$400M estimated February 2026 (treat as unverified — not official press release)
- **Free tier: 5 credits/day, hard cap 30/month, NO rollover — 2–4 light demos/month maximum**
- **Pro plan ($25/month): 100 monthly credits + 5 daily credits**
  - Realistic working capacity: **~150 total actions/month** (use this for planning)
  - Theoretical maximum: ~250/month (requires logging in every single day — not reliable)
  - Source of 150 vs 250 conflict: daily credits do not accumulate if you miss a day
- **Design Templates: Business plan ($50/month) only — on Pro, manually duplicate master project**
- Note: verify at lovable.dev/pricing before committing — plan details shift
- GitHub sync: you own the code
- GBP data: manually copy/paste into prompt (no native GBP integration — this is the competitive advantage at premium price points)

### TESTING / PRE-REVENUE TOOL

**Bolt.new**
- Free tier: ~1M tokens/month — enough for 5–10 simple demo builds
- Bolt Cloud V2: native database, auth, and hosting — Supabase optional
- For home service sites (no backend needed): ignore backend features entirely
- File upload: logos, photos, screenshots directly in chatbox
- Deploy: bolt.host (native) or Netlify
- Best use: build the first demo per niche, test the prompt before spending Lovable credits
- **Known quirk:** index.html edits via chat may not redeploy to bolt.host
  Workaround: download ZIP → edit manually → deploy to Netlify Drop
  Note: observed behavior, not formally documented platform limitation — test and recheck

### AUTONOMOUS PRODUCTION TOOL

**Claude Code (via WEBSITE_GENERATION_SKILL.md)**
- Agentic coding environment — reads files, writes files, runs terminal commands
- Invoked from VS Code, not from Python
- Correct workflow:
  1. `generate_website.py --mode skill-output` → JSON package
  2. Open Claude Code → "execute WEBSITE_GENERATION_SKILL.md using [package]"
  3. Claude Code builds → `npm run build` → `netlify deploy --dir=dist --prod`
- `--dir=dist` is the correct flag for standard Vite builds (default `outDir`).
  If `vite.config.js` overrides `build.outDir`, deploy that directory instead.
  Generated `vite.config.js` should always explicitly set `build: { outDir: 'dist' }`.
- Claude Code + Netlify CLI: validated workflow pattern — test in your environment
  before treating as confirmed production standard

### AI GENERATION TOOLS

**Google AI Studio + Gemini 3.1 Pro Preview**
- Released February 19, 2026
- 64k token output (65,536) — complete multi-page React app in one response
- Three-Tier Thinking: Low/Medium/High reasoning — use HIGH for site generation
- Free in AI Studio with rate limits (per-minute and daily)
- Rate limit note: sufficient for 1–2 demo builds per session, not automated batch
- Best for: maximum visual impact, cinematic demo sites, Option A workflow
- Converter prompt: rewrites multi-file React to single vanilla HTML for GHL Custom HTML embed

**Creator's Antigravity CLI** (distinct from Google's Antigravity IDE)
- Custom community-built script calling Gemini API
- NOT part of Google's ecosystem — from YouTube tutorial creators
- Produces React/Vite/Tailwind sites via Gemini in one shot
- Use if you've tested and verified the specific creator's CLI works

**Google Antigravity IDE** (distinct from the CLI above)
- Official Google product: agentic development IDE (VS Code fork)
- Launched November 2025
- Deep Gemini integration, autonomous task execution
- NOT a website builder — for complex development workflows

### SITUATIONAL TOOLS

**Reloom** — sitemap + wireframe generation (use as planning Step 1)
**Readdy.ai** (confirmed real product, correct spelling) — clone competitor site structure
**Replit Agent 3** — full-stack, 30+ integrations, Google Sheets routing
**Mocha (getmocha.com)** — zero-config infrastructure (provisional — not yet validated)
**Base44** — auto-builds backend (acquired by Wix $80M — confirmed legitimate)
**Hostinger Horizons** — budget tier, 45-second generation, lower design quality

### TOOLS NOT RECOMMENDED

**Aightbuilder.co** — could not be independently verified as current public product
**Localo** — GBP-support site, not for premium agency delivery
**GHL's native site builder** — lower design quality than external tools

---

## SECTION 3: GBP DATA INTEGRATION

### Manual Workflow for Lovable (Your Competitive Advantage)

The manual 7-minute GBP data collection is a premium differentiator, not a shortcoming.
AI auto-import tools (Brizy, Duda) miss GTA neighborhood nuance.
At $2,000+ setup fees, the manual workflow is justified and differentiating.

**Step 1 — Collect from GBP (5 min):**
- Business name, phone, address
- Specific service area neighborhoods (Streetsville vs Port Credit vs Cooksville — not "Mississauga")
- Services list, hours, emergency availability
- Review count + star rating
- Top 3 reviews verbatim

**Step 2 — Save assets (2 min):**
- Right-click save logo
- Save 2–3 job/service photos

**Step 3 — Build prompt:**
Using `generate_website.py --mode bolt` if extraction ran, or manually fill the
`plumbing_bolt_prompt.txt` template variables.

### Native GBP Tools (situational use)
| Tool | GBP Integration | Agency Suitability | Notes |
|---|---|---|---|
| Brizy AI | ✅ One-click pull | Budget tier only | Block-based, less customizable |
| Duda | ✅ Bi-directional sync | Supported (test before relying) | Agency-grade platform |
| Localo | ✅ Auto-pull | ❌ Not for delivery | localo.site subdomain only |

---

## SECTION 4: GHL TIER REFERENCE (March 2026)

| Plan | Price | Sub-accounts | Best for |
|---|---|---|---|
| Starter | $97/month | 3 (1 agency + 2 clients) | First 1–2 client onboards |
| Unlimited | $297/month | Unlimited | 4+ clients, ~$1,500+/month revenue |
| SaaS Pro / Agency Pro | $497/month | Unlimited + SaaS Mode | White-label/reselling |
| AI Employee add-on | $97/month per sub | — | Covers Conversation AI + basic Voice AI. Voice AI Widget (inline embed) and Agent Studio may have additional per-use charges — verify in billing |

**Starter sub-account limit (confirmed):**
GHL Starter = 3 sub-accounts (1 for your agency + 2 for clients). Confirmed on
official GHL pricing page. Upgrade to Unlimited when onboarding client 3.

**Voice AI cost:** The $97/month AI Employee add-on is required for Package 3 clients.
This is not covered by the Unlimited or Starter base plan.
Enable SaaS Mode re-billing so clients pay LC Phone usage directly.

### GHL Embed Reference
| Feature | Method | Critical Setup Step |
|---|---|---|
| Voice AI widget — inline | JS in index.html before React root | Enable in Labs first. See dual placement note below. |
| Chat widget — floating | JS before </body> | Standard |

**GHL widget placement — dual approach:**
The inline voice widget and floating chat widget require different placement:

- **Floating chat widget** (`id="ghl-chat-widget"`): JS snippet before `</body>` in
  `index.html`. Appends to `<body>` which exists before React mounts. ✅ Standard.

- **Inline voice widget** (`id="ghl-voice-inline"`): Lives inside the React tree — the
  div does NOT exist in the DOM before React mounts. Placing the script before
  `<div id="root">` causes silent failure (widget falls back to floating mode).
  Two correct options:
  - Option A: Place `id="ghl-voice-inline"` as a static HTML element in `index.html`
    outside `<div id="root">`, so it exists before React hydrates.
  - Option B: Use `useEffect(() => { /* inject GHL script */ }, [])` in the React
    component that renders the inline placeholder, so the div exists first.
| Booking calendar | iFrame | None |
| Lead capture form | JS or iFrame | None |
| Missed call text-back | Backend only | A2P/Canadian SMS required |
| Review request | Backend only | A2P/Canadian SMS + trigger defined |

---

## SECTION 5: AGENCY COST STRUCTURE (corrected)

| Phase | Tools | Monthly Cost |
|---|---|---|
| Phase 1 — Pre-revenue | Bolt.new free | $0 |
| Phase 2 — First client (no Voice AI) | Lovable Pro + GHL Starter/Unlimited | $122–$322 |
| Phase 3 — 4+ clients (no Voice AI) | Lovable Pro + GHL Unlimited | $297 + $25 = $322 |
| Phase 3 — Voice AI clients | Add $97/sub for AI Employee base | +$97 per Package 3 client (floor only — Voice AI Widget and Agent Studio may add per-use charges on top; verify in GHL billing) |
| Phase 4 — White-label scale | Lovable Business + GHL SaaS Pro | $497 + $50 = $547 |
| SerpApi (agency volume) | Needed at >5 extractions/day | +$50–75/month |

All phases: Netlify hosting = $0 on free tier

**⚠️ Netlify account-level suspension risk (critical at 5+ clients):**
Free tier = 100GB bandwidth + 300 build minutes/month, applied account-wide.
When any limit is exceeded, ALL sites on that account pause until next month —
not just the site that triggered it. One client traffic spike can take all clients offline.

Mitigation:
- **Netlify Pro ($19/month):** Eliminates suspension. Recommended at 5+ clients.
- **Separate account per client:** Isolates overage risk. More admin, but zero cross-client impact.
- Monitor: Netlify → Team Settings → Usage. Set email alerts at 75% of limits.

**Margin example (corrected):**
- 10 clients, 8 at $297/month (no Voice AI), 2 at $497/month (Voice AI)
- Revenue: $2,376 + $994 = $3,370/month recurring
- Costs: $322 (platform) + $194 (2x AI Employee) = $516
- Net before time: ~$2,854/month at 10 clients

---

## SECTION 6: WHAT HOME SERVICE BUSINESSES NEED

No overengineering. Complete requirements:

| Need | Solution | Complexity |
|---|---|---|
| Click-to-call prominent | Header sticky + hero + footer | Zero |
| Quote/contact form | Native in Lovable/Bolt | Zero |
| Services with cards | Static content | Zero |
| Service area map | Google Maps iFrame | Zero |
| Reviews/testimonials | Manual from GBP | Zero |
| Photo gallery | Uploaded images | Zero |
| Online booking | GHL calendar iFrame | Zero |
| Mobile-responsive | Native in all tools | Zero |
| Local SEO structure | Semantic HTML + meta tags | Zero |
| Voice AI receptionist | GHL widget (Labs enabled) | Low |
| Missed call text-back | GHL workflow | Low |
| Review requests post-job | GHL workflow + defined trigger | Low |

**What they do NOT need:** User login, database, on-site Stripe checkout,
blog (unless upsold as SEO content), video backgrounds.

---

## SECTION 7: QA STANDARDS (summary — full checklist in GHL_SETUP_CHECKLIST_v3.md)

No site goes live without passing all items. Key checks:

**Mobile (real iPhone, not DevTools):**
- Loads on iPhone Safari and Android Chrome
- Sticky header works
- Every phone number opens phone dialer when tapped
- No horizontal scroll at 390px
- All GHL placeholder divs visible with dashed borders

**Content:**
- No placeholder text remaining ([BUSINESS_NAME], [PHONE], Lorem Ipsum)
- Dynamic copyright year (not hardcoded)
- Professional favicon
- Specific neighborhood names (not "Greater [City] Area")

**Technical:**
- HTTPS active
- Lighthouse Performance ≥ 75, Accessibility ≥ 80
- OG tags correct (test at opengraph.xyz)
- No builder badge scripts in page source

**GHL (after widgets connected):**
- Test form submission → CRM → follow-up SMS
- Test missed call → text-back within 60 seconds
- Test booking → confirmation SMS
- Voice AI inline widget renders correctly

---

## SECTION 8: IMMEDIATE NEXT ACTIONS (updated)

**Completed ✅**
1. Plumber master prompt built and tested (Bolt.new demo live)
2. All 6 GHL placeholder divs in demo site
3. All visual fixes applied
4. `extract_business_data.py` built
5. `generate_website.py` built (corrected architecture)
6. `WEBSITE_GENERATION_SKILL.md` built
7. `universal_rules.txt` built
8. `plumbing.md` niche file built
9. `plumbing_bolt_prompt.txt` built
10. `GHL_SETUP_CHECKLIST_v3.md` built (all peer review fixes)
11. `_NICHE_TEMPLATE.md` built

**This week:**
1. Rotate API keys if any were exposed in shared documents
2. Verify GHL Starter sub-account limit in your actual account
3. Run extraction script test:
   ```bash
   python3 execution/extract_business_data.py \
     --url https://mississaugaplumbingservices.com \
     --business "Mississauga Plumbing Services" \
     --city "Mississauga ON"
   ```
4. Cold outreach to mississaugaplumbingservices.com:
   "Saw your GBP — built this in advance using your business data and voice AI already integrated"
   Include: live bolt.host link + Calendly for discovery call

**On first client signed:**
5. Complete Section 1.5 of GHL_SETUP_CHECKLIST_v3.md (Canadian SMS decision tree)
6. Upgrade to Lovable Pro ($25/month)
7. Set up GHL sub-account — apply Snapshot if available
8. Run: `generate_website.py --url [client url] --mode skill-output`
9. Execute WEBSITE_GENERATION_SKILL.md in Claude Code
10. Complete QA checklist (Section 11 of GHL_SETUP_CHECKLIST_v3.md) before sharing

**After first client onboarded:**
11. Build GHL Master Snapshot immediately (Section 8.5 of checklist)

**Next verticals after plumber:**
- HVAC (emergency CTAs, seasonal messaging, financing badge)
- Cleaning (booking primary, team photos, recurring plans)
- Pest control (same-day, no bug photos, clinical design)

---

## SECTION 9: QUESTIONS FOR PEER REVIEW (v4.0)

Questions from v3.3 that are now resolved — do not re-review:
- Antigravity CLI vs IDE: confirmed distinct ✅
- Lovable credits: 150/month planning number confirmed ✅
- Lovable Design Templates: Business only confirmed ✅
- GHL embed on external hosts: confirmed with test-per-deploy caveat ✅
- GHL Voice AI inline widget: confirmed ✅
- Canadian SMS: full decision tree added ✅
- Bolt index.html quirk: observed behavior documented ✅
- Claude Code Netlify deployment: production-ready with --dir=dist ✅

**New questions for v4.1 peer review:**

1. **GHL AI Employee inline widget charges:** The $97/month AI Employee add-on
   covers Conversation AI, Reviews AI, and basic Voice AI call handling. Do the
   Voice AI Widget (inline embed) and Agent Studio incur additional per-use charges
   on top? Confirm in live GHL billing before finalizing Package 3 margins.

2. **Netlify account-level suspension at scale:** Free tier limits (100GB bandwidth,
   300 build minutes/month) apply account-wide — one overage pauses ALL sites on
   the account simultaneously. At 10+ clients, is separate-account-per-client the
   right mitigation, or upgrade to Netlify Pro ($19/month)?

3. **GHL AI Employee add-on pricing (2026):** Is $97/month per sub-account still
   the correct price for Voice AI features? Is it flat-rate or usage-based?
   Some sources suggest usage-based components on top of the flat rate.

4. **`netlify deploy --dir=dist --prod` for Vite/React:** Is `dist/` confirmed as
   the correct build output directory for all Vite + React configurations?
   Or does it vary by `vite.config.js` settings?

5. **React + GHL script placement:** Is placing GHL scripts in `index.html` body
   before `<div id="root">` the accepted React-safe pattern, or should
   `useEffect` with an empty dependency array be used instead?

6. **CASL French language requirement (Ontario):** Is French opt-out text mandatory
   for SMS sent by Ontario-based businesses, or only Quebec/federally regulated?

7. **SerpApi `google_maps_reviews` 2026 field schema:** Are `snippet` and
   `extracted_snippet.original` still the current field names? API schemas
   sometimes change between versions.

8. **GHL Snapshot plan portability:** Can Snapshots be created on a Starter plan
   and applied to Unlimited plan sub-accounts? Or is Snapshot creation
   restricted to higher plan tiers?

9. **Netlify free tier bandwidth limits:** Does the Netlify free tier impose
   bandwidth or concurrent build limits that become a constraint at 10+ client sites?

10. **Overall v4.0 readiness:** With all v3.3 issues resolved — corrected Claude Code
    architecture, confirmed Voice AI inline embed, full Canadian SMS decision tree,
    corrected COGS, QA checklist, GHL Snapshot procedure, and domain cutover SOP —
    is this stack complete enough to reliably deliver the first 10 clients as a
    one-person agency operating part-time?

---

## SECTION 10: PEER REVIEW VERDICT SUMMARY (v3.3 round — for reference)

| Claim | Verdict | Confidence | Action Taken |
|---|---|---|---|
| Core architecture (external site + GHL embed) | ✅ Confirmed | High | No change |
| Gemini 3.1 Pro Preview Feb 19, 2026 | ✅ Confirmed | High | No change |
| Gemini 3.1 64k output + Three-Tier Thinking | ✅ Confirmed | High | No change |
| Two Antigravity products (Google IDE vs creator CLI) | ✅ Confirmed | High | No change |
| Converter prompt rewrites to vanilla HTML | ✅ Confirmed | High | No change |
| Lovable free tier: 30/month hard cap | ✅ Confirmed | High | No change |
| Lovable Pro: ~150/month realistic planning number | ✅ Confirmed | High | Updated from 250 |
| Lovable Design Templates: Business plan only | ✅ Confirmed | High | No change |
| Bolt Cloud V2 native backend | ✅ Confirmed | High | No change |
| Readdy.ai is real (not "Ready.ai") | ✅ Confirmed | High | No change |
| Aightbuilder.co not verified | ✅ Supported | High | No change |
| Brizy GBP integration works | ✅ Confirmed | High | No change |
| GHL embed on external hosts (test recommended) | ✅ Supported | Medium-High | Test caveat added |
| GHL tiers: Starter $97 / Unlimited $297 / SaaS Pro $497 | ✅ Confirmed | High | No change |
| GHL Starter sub-accounts | ⚠️ Conflicted | Low | Flagged for v4 review |
| Option B (Lovable) recommended for agency stage | ✅ Strategic | High | No change |
| Manual GBP = competitive advantage at $2k+ | ✅ Strategic | High | No change |
| generate_website.py --mode claude-code | ❌ Architecture error | Critical | Fixed → skill-output |
| netlify deploy --dir=dist required | ❌ Missing | Critical | Added everywhere |
| Canadian SMS = same as US A2P | ❌ Incorrect | Critical | Fixed → full decision tree |
| Voice AI inline embed | ❌ Unclear in v1 | Critical | Fixed → confirmed + Labs step |
| API keys in documents | ❌ Security breach | Critical | Fixed → .env only |

### Changes v4.0 → v4.1 (second peer review round — March 2026)

| Item | v4.0 Claim | v4.1 Correction |
|---|---|---|
| GHL Starter sub-accounts | "~3 (verify — may be 1)" | Confirmed 3 — uncertainty language removed |
| Lovable daily credit rollover | "250 if daily login" | Confirmed strictly resets — 150/month is correct cap |
| AI Employee inline widget | "$97/month covers Voice AI" | Added: inline widget + Agent Studio may add per-use charges — treat as floor not ceiling |
| React inline widget placement | "Script before div id=root" | Logic flaw fixed — dual approach: Option A static HTML outside root / Option B useEffect |
| CASL French requirement | "Add French per CASL" | Corrected: legally required for Quebec only; English sufficient for Ontario; French keywords are best practice nationwide |
| Netlify suspension risk | Not mentioned | Added: 100GB/300min limit is account-wide — all sites pause on overage |
| Firecrawl "~98% accuracy" | Stated as fact | Softened to "high reliability" — unsourced precision removed |
| Firecrawl promo expiry | "Through April 2026" | Corrected to approximately January 2026 — verify live status |
| vite.config outDir | "dist is mandatory" | Added caveat: dist is Vite default; if overridden in vite.config.js, deploy that folder |

---

*v4.1 finalized March 2026*
*All v4.0 peer review issues resolved*
*One open question in Section 9 for next review round (AI Employee widget per-use charges)*
