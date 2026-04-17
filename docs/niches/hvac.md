# Niche File: HVAC
# Layer 3 of three-layer prompt system
# Read by generate_website.py when niche == "hvac"
# Last updated: March 2026

---

## DETECTION KEYWORDS
hvac, heating, cooling, air conditioning, furnace, heat pump, ac repair,
ductwork, ventilation, boiler, thermostat, air handler, mini split, hvac system

## PRIMARY EMOTION TO TRIGGER
Urgency + Relief + Trust. HVAC combines emergency (no heat in winter, no AC in
summer) with high-ticket planned work (installs, replacements). The prospect is
either panicking OR making a major financial decision. Copy must handle both:
emergency sections trigger urgency, planned sections build trust and credibility.

---

## CTA BUTTONS
Primary:   "Call Now — 24/7 Emergency Service"   (href="tel:+1[PHONE_DIGITS]")
Secondary: "Get a Free Quote"                     (scrolls to #contact)

## PHONE CTA TEXT (in hero)
"📞 Call [PHONE] — We Answer 24/7"

## MISSED CALL BADGE (in header)
"Missed us? We'll text you back in 60 seconds."

---

## COLOR PALETTE
Primary:   #1a3a6b   (deep navy — trust, professional)
Accent:    #e84040   (emergency red — no heat/AC emergency elements only)
Text:      #1a1a1a   (near-black — readability)
Light bg:  #f7f9fc   (off-white — planned service sections)
Button:    #e84040 hover:#c73232  (emergency CTA)
Secondary button: #1a3a6b hover:#12285a

RULE: Red = emergency elements only (no heat, no AC banners, 24/7 badges).
Navy = planned service sections (installs, maintenance, tune-ups).
Never use purple.

## TYPOGRAPHY (Tailwind classes)
Hero headline:   text-4xl md:text-6xl font-black leading-tight
Section heading: text-3xl font-bold
Body:            text-base md:text-lg leading-relaxed
CTA button:      text-lg font-bold px-8 py-4 rounded-lg

---

## TRUST BAR (4 items — HVAC-specific)
1. ⚡ 24/7 Emergency Service   (no heat/AC emergencies — most critical for HVAC)
2. ✅ Licensed & Insured        (all provinces/states require HVAC licensing)
3. 🏆 Factory Authorized        (brand certifications — use if applicable; otherwise "Certified Technicians")
4. 💰 Financing Available       (high ticket installs — financing is a major trust signal)

## HERO BADGE ROW (below CTA buttons)
"🔒 Licensed & Insured  •  ⭐ [RATING_STRING]  •  ⚡ 24/7 Emergency Service"

---

## SECTION ORDER (HVAC-specific — emergency + planned hybrid)
  1. Sticky header: logo + phone + 60-second text-back badge
  2. Hero: dual-message headline (emergency + planned) + rating + two CTAs
  3. GHL voice widget placeholder
  4. Trust bar (4 items above)
  5. Services: card grid (emergency first, planned installs second)
  6. "Why Choose Us" — 3 differentiators (response time, certifications, financing)
  7. Process: 4 steps
  8. Reviews/testimonials: 3 real GBP reviews
  9. GHL reviews widget placeholder
  10. Service areas: neighborhoods + Google Maps iFrame
  11. Booking section (HVAC is both call + book — booking is prominent)
  12. Contact/quote form
  13. Footer

## NOTE ON BOOKING POSITION
HVAC is a hybrid trade. Emergency calls dominate in peak seasons (January cold
snaps, August heat waves), but planned installs and tune-ups are scheduled in
advance. Place booking section higher than plumbing — after service areas.
Primary CTA is still phone, but booking calendar gets more prominence.

---

## DEFAULT SERVICES LIST
(Used if extraction returns empty — replace with real services from GBP)
Emergency Heating Repair, Emergency AC Repair, Furnace Installation,
Air Conditioner Installation, Heat Pump Installation, HVAC Maintenance & Tune-Up,
Ductwork Installation & Repair, Thermostat Installation, Boiler Service,
Indoor Air Quality, Mini-Split Systems, Commercial HVAC

## SERVICES SECTION RULE
Emergency services FIRST in the card grid:
Card 1: Emergency Heating Repair (red #e84040 icon) — "No heat? We're on the way."
Card 2: Emergency AC Repair (red #e84040 icon) — "No cooling? Same-day service."
Cards 3+: Installs, maintenance, IAQ in navy (#1a3a6b)

---

## HERO HEADLINE FORMULAS
Option A: "No Heat? No AC? [CITY_PROVINCE]'s HVAC Experts — 24/7 Emergency Service"
Option B: "HVAC Emergency in [CITY_PROVINCE]? We Arrive Fast. Installs That Last."
Option C: "[CITY_PROVINCE]'s Trusted HVAC Company — Emergency + Installs"
Recommended: Option A — directly addresses both emergency states in one line.

## HERO SUBHEADLINE
"[RATING_STRING] • Serving [CITY_PROVINCE] and surrounding areas"

---

## WHY CHOOSE US SECTION (3 HVAC differentiators)
1. ⚡ Fast Emergency Response
   "No heat in winter or no AC in summer — we dispatch the same day, often within hours."
2. 🏆 Factory Authorized Technicians
   "Our techs are certified on all major brands. We fix it right the first time."
3. 💰 Flexible Financing
   "New system installs with 0% financing available. Comfort shouldn't break the bank."

---

## PROCESS SECTION (4 steps — HVAC-specific)
Step 1: "Call or Book Online"      — "Available 24/7 for emergencies, scheduled for installs"
Step 2: "Fast Diagnosis"           — "Our tech arrives and diagnoses the issue clearly"
Step 3: "Upfront Quote"            — "You approve the price before we touch anything"
Step 4: "Done Right, Guaranteed"   — "All work warranted — we stand behind every job"

---

## REVIEWS SECTION
Display 3 verbatim reviews from [REVIEWS_3] in quote cards.
Format: ★★★★★ | Quote text | — [First name], Google Review

"Read all [REVIEW_COUNT] reviews on Google →" link to GBP

---

## SERVICE AREAS SECTION
Heading: "Proudly Serving [CITY_PROVINCE] and Surrounding Communities"
List format: specific neighborhood names — never "Greater Area"
Map: Google Maps iFrame centered on [CITY_PROVINCE]

---

## BOOKING SECTION HEADING
"Schedule HVAC Service Online"
Subtext: "For no-heat or no-AC emergencies, call [PHONE] — we answer 24/7."

---

## AUDIT RED FLAGS → GENERATION FIXES

| Audit Finding                        | Generation Rule                                                       |
|--------------------------------------|-----------------------------------------------------------------------|
| Reviews hidden / not displayed       | Rating + count in hero subheadline; 3 review cards prominent          |
| JS-only build (not indexable)        | Semantic HTML: h1, h2, section, article — server-side renderable      |
| No lead capture                      | All 6 GHL placeholder divs, clearly labeled with dashed borders       |
| No tap-to-call                       | tel: href on EVERY phone instance — header, hero, mid-page, footer    |
| No emergency messaging               | "No heat? No AC?" framing in hero; 24/7 badge in header               |
| No financing mentioned               | Financing badge in trust bar + Why Choose Us section                  |
| No brand certifications              | "Factory Authorized" or "Certified Technicians" in trust bar          |
| No service areas                     | Specific neighborhoods in dedicated section + Maps iFrame             |
| No booking option                    | GHL calendar placeholder prominent — HVAC books more than plumbing    |

---

## NICHE-SPECIFIC PROMPT ADDITIONS
Add to the end of the site generation prompt when building for HVAC:

"""
HVAC-SPECIFIC REQUIREMENTS:
- Hero headline must acknowledge BOTH emergency states: no heat (winter) AND no AC (summer)
- Financing must appear in: trust bar item 4, Why Choose Us, and footer or CTA section
- Factory authorization / brand certifications mentioned if client has them
- Services grid: emergency repairs in cards 1-2 with red accent, installs in navy
- Booking calendar placeholder gets more visual prominence than plumbing — HVAC clients book
- Seasonal urgency framing: "Before winter hits" or "Beat the summer rush" in booking section
- Trust bar item 3: certifications (not response time) — HVAC is skill-trust, not just speed
- Mid-page CTA after services: both call button AND "Get a Free Quote" button (dual CTA)
"""

---

## TYPICAL JOB VALUES (for ROI conversations in sales)
Emergency repair:       $250–$800
Furnace replacement:    $3,000–$6,000
AC replacement:         $3,500–$7,000
Heat pump (full):       $5,000–$12,000
Tune-up/maintenance:    $100–$200
Ductwork:               $1,500–$5,000+
Average job value:      ~$1,500–$2,500 blended

## COLD OUTREACH HOOK
"I noticed your [REVIEW_COUNT] five-star Google reviews are nowhere on your website —
HVAC customers always check reviews before a $5,000 install decision.
I put together a 30-second demo using your actual business data."

## PRICING GUIDANCE
Setup fee range:   $2,497 – $3,497 (Growth System recommended — high job values justify it)
Monthly retainer:  $297/month
Key ROI argument:  "One extra furnace install per quarter at $4,000 average = $16,000/year.
                   Our system pays for itself in 3 weeks."

---

## PROMPT_VARIABLES
NICHE_TRADE_LABEL: hvac
NICHE_TRADE_LABEL_CAP: HVAC
NICHE_ICON_EMOJI: 🌡️
NICHE_PAGE_TITLE_TRADE: 24/7 Heating & Cooling
NICHE_META_DESCRIPTION: Licensed HVAC technicians in [CITY_PROVINCE]. Furnace repair, AC service, 24/7 emergency. Free estimates. Call [PHONE].
NICHE_META_TRADE_NOUN: HVAC technicians
NICHE_HERO_HEADLINE: Furnace or AC Emergency in [CITY_PROVINCE]? Fast Service, 24/7.
NICHE_PRIMARY_CTA_TEXT: Call Now — 24/7 Emergency Service
NICHE_MISSED_CALL_BADGE: Missed us? We'll text you back in 60 seconds.
NICHE_HERO_TRUST_BADGE: 24/7 Heating & Cooling Service
PRIMARY_COLOR: #1a3a6b
ACCENT_COLOR: #e84040
NICHE_SERVICES_SUBHEADING: Complete heating and cooling solutions for your home
NICHE_AREAS_SUBHEADING: Fast HVAC service across the region
NICHE_FOOTER_TAGLINE: Your trusted local heating and cooling experts. Comfort guaranteed.
NICHE_FOOTER_HOURS_LABEL: 24/7 Emergency Service
NICHE_FOOTER_EMERGENCY_LINE: Emergency calls: Anytime
NICHE_BOOKING_HEADING: Schedule HVAC Service or Maintenance
NICHE_BOOKING_SUBTEXT: For no-heat or no-AC emergencies, call [PHONE] — we answer 24/7.
NICHE_PROCESS_SUBHEADING: Getting your comfort back is easy
MAPS_LAT: 43.58
MAPS_LNG: -79.65
REGION_LABEL: the GTA
AGENCY_NAME: YourAgencyName
NICHE_TRUST_BAR_BLOCK: ⚡ 24/7 Emergency Service | No heat or no AC — we respond fast | ✅ Licensed & Insured | Certified HVAC technicians | 🏆 Factory Authorized | Trained on major brands | 💰 Financing Available | For installs and replacements
NICHE_WHY_CHOOSE_US_BLOCK: ⚡ Fast Emergency Response | No heat in winter or no AC in summer — we dispatch within the hour. | 💰 Transparent Pricing | Get your quote upfront before any work begins. No hidden fees, ever. | 🏆 [YEARS_IN_BUSINESS] Years Serving [CITY_PROVINCE] | Trusted by homeowners across [CITY_PROVINCE] for over [YEARS_IN_BUSINESS] years.
NICHE_PROCESS_BLOCK: Call or Book Online | Available 24/7 for emergencies | Fast Response | Certified tech arrives promptly | Diagnose & Repair | Upfront pricing before work starts | Comfort Guaranteed | We stand behind every job we do
