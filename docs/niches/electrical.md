# Niche File: Electrical
# Layer 3 of three-layer prompt system
# Read by generate_website.py when niche == "electrical"
# Last updated: March 2026

---

## DETECTION KEYWORDS
electrician, electrical, wiring, panel upgrade, circuit breaker, outlets,
generator, ev charger, lighting installation, electrical repair, rewiring,
electrical inspection, permit, code compliance, licensed electrician

## PRIMARY EMOTION TO TRIGGER
Safety + Trust. Electrical work triggers a unique psychological state — customers
are not just hiring for speed, they are trusting someone with their family's
safety. Copy must lead with safety, credentials, and code compliance before
speed. Unlike plumbing, rushing an electrical job feels dangerous. The right
message: "Safe, certified, done right — and fast when you need it."

---

## CTA BUTTONS
Primary:   "Call Now — Licensed Electricians"      (href="tel:+1[PHONE_DIGITS]")
Secondary: "Get a Free Estimate"                    (scrolls to #contact)

## PHONE CTA TEXT (in hero)
"📞 Call [PHONE] — Licensed & Permitted Work"

## MISSED CALL BADGE (in header)
"Missed us? We'll text you back in 60 seconds."

---

## COLOR PALETTE
Primary:   #1a3a6b   (deep navy — trust, safety, professionalism)
Accent:    #f59e0b   (amber/yellow — electricity, energy — replaces red for this niche)
Text:      #1a1a1a   (near-black — readability)
Light bg:  #f7f9fc   (off-white — sections)
Button:    #f59e0b hover:#d97706  (primary CTA — amber)
Emergency button: #e84040 hover:#c73232 (emergency only — power outage, sparks)

NOTE ON COLOR: Electrical uses amber (#f59e0b) as primary accent — it signals
electricity visually and differentiates from generic navy/red sites.
Reserve red (#e84040) for genuine emergencies only (power outage, burning smell).

## TYPOGRAPHY (Tailwind classes)
Hero headline:   text-4xl md:text-6xl font-black leading-tight
Section heading: text-3xl font-bold
Body:            text-base md:text-lg leading-relaxed
CTA button:      text-lg font-bold px-8 py-4 rounded-lg

---

## TRUST BAR (4 items — electrical-specific, safety-first order)
1. ⚡ Licensed & Permitted     (permits pulled, code-compliant — most important for electrical)
2. 🔒 Bonded & Insured         (liability protection — customers are paying attention to this)
3. ✅ All Work to Code          (pass inspection guarantee)
4. 📋 Free Estimates            (no obligation quotes)

## HERO BADGE ROW (below CTA buttons)
"⚡ Licensed & Permitted  •  ⭐ [RATING_STRING]  •  🔒 Bonded & Insured"

---

## SECTION ORDER (electrical — safety-first, hybrid emergency/planned)
  1. Sticky header: logo + phone + 60-second text-back badge
  2. Hero: safety + credentials headline + rating + two CTAs
  3. GHL voice widget placeholder
  4. Trust bar (safety credentials first — different from plumbing)
  5. Services: card grid (emergency/safety first, planned work second)
  6. "Why Choose Us" — 3 differentiators (licensed, permitted, guaranteed)
  7. Process: 4 steps
  8. Reviews/testimonials: 3 real GBP reviews
  9. GHL reviews widget placeholder
  10. Service areas: neighborhoods + Google Maps iFrame
  11. Booking section
  12. Contact/quote form
  13. Footer

## NOTE ON BOOKING POSITION
Electrical is a blend of emergency (power out, burning smell, tripping breakers)
and planned work (panel upgrades, EV chargers, rewires, additions).
Booking appears after reviews — same position as plumbing.
Primary CTA is always phone. Emergency messaging must stay prominent.

---

## DEFAULT SERVICES LIST
(Used if extraction returns empty — replace with real services from GBP)
Panel Upgrades & Replacements, Electrical Repairs, Outlet & Switch Installation,
Lighting Installation, Wiring & Rewiring, EV Charger Installation,
Generator Installation & Service, Electrical Inspections, Surge Protection,
Smoke & CO Detector Installation, Ceiling Fan Installation, Home Additions Wiring

## SERVICES SECTION RULE
Emergency/safety services FIRST in card grid:
Card 1: Electrical Repairs & Troubleshooting (amber icon) — "Burning smell? Tripping breakers? Call now."
Card 2: Panel Upgrades & Replacements (amber icon) — "Outdated panels are a fire risk."
Cards 3+: Planned work in navy (#1a3a6b) — EV chargers, lighting, generators, inspections

---

## HERO HEADLINE FORMULAS
Option A: "Licensed Electricians in [CITY_PROVINCE] — Safe, Permitted, Done Right"
Option B: "Electrical Problem in [CITY_PROVINCE]? [YEARS_IN_BUSINESS] Years. Every Job Permitted."
Option C: "[CITY_PROVINCE]'s Trusted Electricians — From Repairs to Full Rewires"
Recommended: Option A — leads with the credential that matters most (licensed + permitted).

## HERO SUBHEADLINE
"[RATING_STRING] • Serving [CITY_PROVINCE] and surrounding areas"

---

## WHY CHOOSE US SECTION (3 electrical differentiators)
1. ⚡ Licensed & Fully Permitted
   "Every job is permitted and inspected. You get paperwork that protects your home's value."
2. 🔒 Safety Is Our Standard
   "We don't cut corners. All work meets or exceeds current electrical code — guaranteed."
3. 🏆 [YEARS_IN_BUSINESS] Years of Local Experience
   "Trusted by homeowners and businesses in [CITY_PROVINCE] for over [YEARS_IN_BUSINESS] years."

---

## PROCESS SECTION (4 steps — electrical-specific)
Step 1: "Call or Book Online"     — "Available for emergencies 24/7 and scheduled work"
Step 2: "On-Site Assessment"      — "We diagnose the issue and explain your options clearly"
Step 3: "Upfront Quote"           — "You approve the price and timeline before we begin"
Step 4: "Permitted & Inspected"   — "Work is permitted, inspected, and fully guaranteed"

---

## REVIEWS SECTION
Display 3 verbatim reviews from [REVIEWS_3] in quote cards.
Format: ★★★★★ | Quote text | — [First name], Google Review

"Read all [REVIEW_COUNT] reviews on Google →" link to GBP

---

## BOOKING SECTION HEADING
"Schedule Electrical Service"
Subtext: "For emergencies (burning smell, power out, sparks), call [PHONE] immediately."

---

## AUDIT RED FLAGS → GENERATION FIXES

| Audit Finding                        | Generation Rule                                                        |
|--------------------------------------|------------------------------------------------------------------------|
| Reviews hidden / not displayed       | Rating + count in hero subheadline; 3 review cards prominent           |
| No licensing/permit info             | License number + "all work permitted" in hero badge + trust bar        |
| No emergency messaging               | "Burning smell? Sparks? Call now." in hero or trust bar                |
| No tap-to-call                       | tel: href on EVERY phone instance                                      |
| No safety language                   | "Code compliant," "permitted," "inspected" throughout                  |
| No EV charger mention                | Include as a service card — growing demand, high search volume         |
| No generator mention                 | Include as a service card — high-ticket, seasonal demand               |
| No service areas                     | Specific neighborhoods in dedicated section + Maps iFrame              |

---

## NICHE-SPECIFIC PROMPT ADDITIONS
Add to the end of the site generation prompt when building for electrical:

"""
ELECTRICAL-SPECIFIC REQUIREMENTS:
- Primary accent color is amber (#f59e0b) NOT red — red reserved for emergencies only
- "Licensed & Permitted" must appear in: hero badge row, trust bar item 1, footer
- Safety language mandatory: "code compliant," "permitted," "inspected" — use throughout
- Panel upgrades and EV charger installation must be visible in the services grid
- Emergency framing: "burning smell," "sparks," "tripping breakers" — not just "24/7"
- Trust bar priority order: licensed → bonded → code compliant → free estimates
- Booking section subtext must include emergency escalation: "For sparks or burning smell, call immediately"
- Do not use red as the primary button color — use amber (#f59e0b)
"""

---

## TYPICAL JOB VALUES (for ROI conversations in sales)
Small repair (outlet, switch, breaker):  $150–$400
Lighting installation:                   $300–$1,500
Panel upgrade (100A→200A):               $1,500–$3,500
EV charger installation:                 $800–$2,500
Whole-home generator:                    $5,000–$15,000+
Rewire (full home):                      $8,000–$20,000+
Average job value:                       ~$600–$1,200 blended

## COLD OUTREACH HOOK
"I noticed your [REVIEW_COUNT] five-star Google reviews aren't showing on your website.
For electrical work, customers research harder than almost any other trade — safety
is on the line. I built a demo that puts your credentials front and center."

## PRICING GUIDANCE
Setup fee range:   $1,997 – $2,497 (Growth System)
Monthly retainer:  $297/month
Key ROI argument:  "One panel upgrade at $2,500 average covers your entire year's retainer.
                   One missed call that books instead = system paid for itself."

---

## PROMPT_VARIABLES
NICHE_TRADE_LABEL: electrical
NICHE_TRADE_LABEL_CAP: Electrical
NICHE_ICON_EMOJI: ⚡
NICHE_PAGE_TITLE_TRADE: Licensed Electrician
NICHE_META_DESCRIPTION: Licensed electricians in [CITY_PROVINCE]. Panel upgrades, EV chargers, 24/7 emergency electrical. Free estimates. Call [PHONE].
NICHE_META_TRADE_NOUN: electricians
NICHE_HERO_HEADLINE: Electrical Emergency in [CITY_PROVINCE]? Licensed & On the Way.
NICHE_PRIMARY_CTA_TEXT: Call Now — 24/7 Emergency
NICHE_MISSED_CALL_BADGE: Missed us? We'll text you back instantly.
NICHE_HERO_TRUST_BADGE: 24/7 Emergency Electrical
PRIMARY_COLOR: #1a2e4a
ACCENT_COLOR: #f5a623
NICHE_SERVICES_SUBHEADING: Professional electrical services for homes and businesses
NICHE_AREAS_SUBHEADING: Trusted electrical service across the region
NICHE_FOOTER_TAGLINE: Licensed electricians you can trust. Safe work, every time.
NICHE_FOOTER_HOURS_LABEL: 24/7 Emergency Available
NICHE_FOOTER_EMERGENCY_LINE: Emergency electrical: Anytime
NICHE_BOOKING_HEADING: Schedule Electrical Service
NICHE_BOOKING_SUBTEXT: For urgent electrical issues, call [PHONE] — available 24/7.
NICHE_PROCESS_SUBHEADING: Safe, fast electrical service in 4 steps
MAPS_LAT: 43.58
MAPS_LNG: -79.65
REGION_LABEL: the GTA
AGENCY_NAME: YourAgencyName
NICHE_TRUST_BAR_BLOCK: ⚡ 24/7 Emergency | Electrical emergencies can't wait | ✅ Licensed & Insured | ESA-certified electricians | 🔒 Code Compliant | All work meets provincial code | 📋 Free Estimates | No obligation quotes
NICHE_WHY_CHOOSE_US_BLOCK: ⚡ Emergency Response | Electrical issues are urgent. We dispatch immediately — no waiting. | ✅ ESA Certified | All our electricians are licensed and carry full liability coverage. | 🏆 [YEARS_IN_BUSINESS] Years of Experience | Serving [CITY_PROVINCE] homes and businesses for over [YEARS_IN_BUSINESS] years.
NICHE_PROCESS_BLOCK: Call or Book Online | 24/7 for emergencies | Fast Dispatch | Licensed electrician arrives promptly | Safe Assessment | Clear diagnosis and upfront price | Code-Compliant Work | Permitted and inspected where required
