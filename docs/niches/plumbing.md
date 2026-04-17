# Niche File: Plumbing
# Layer 3 of three-layer prompt system
# Read by generate_website.py when niche == "plumbing"
# Last updated: March 2026
# FIXED: [CITY] → [CITY_PROVINCE] throughout (matched to fill_variables() in generate_website.py)
# FIXED: [REVIEW_COUNT] now supported via generate_website.py fill_variables()

---

## DETECTION KEYWORDS
plumber, plumbing, drain, pipe, water heater, sump pump, sewer, faucet,
leak repair, clog, toilet, bathroom plumbing, kitchen plumbing

## PRIMARY EMOTION TO TRIGGER
Urgency + Relief. Plumbing emergencies are stressful. The prospect is
already anxious. Copy should acknowledge the stress and immediately
position the business as the fast, trusted solution.

---

## CTA BUTTONS
Primary:   "Call Now — 24/7 Emergency Service"   (href="tel:+1[PHONE_DIGITS]")
Secondary: "Get a Free Quote"                     (scrolls to contact form)

## PHONE CTA TEXT (in hero)
"📞 Call [PHONE] — We Answer 24/7"

## MISSED CALL BADGE (in header)
"Missed us? We'll text you back in 60 seconds."

---

## COLOR PALETTE
Primary:   #1a3a6b   (deep navy — trust, professional)
Accent:    #e84040   (emergency red — urgency, 24/7 elements)
Text:      #1a1a1a   (near-black — readability)
Light bg:  #f7f9fc   (off-white — sections)
Button:    #e84040 hover:#c73232  (emergency CTA)
Secondary button: #1a3a6b hover:#12285a

## TYPOGRAPHY (Tailwind classes)
Hero headline:   text-4xl md:text-6xl font-black leading-tight
Section heading: text-3xl font-bold
Body:            text-base md:text-lg leading-relaxed
CTA button:      text-lg font-bold px-8 py-4 rounded-lg

---

## TRUST BAR (4 items — replaces universal defaults)
1. ⚡ Available 24/7        (emergency availability — most important for plumbing)
2. ✅ Licensed & Insured
3. ⏱️ Arrive in 60 Minutes  (or "Fast Response" if can't guarantee timing)
4. 📋 Free Estimates

## HERO BADGE ROW (below CTA buttons)
"🔒 Licensed & Insured  •  ⭐ [RATING_STRING]  •  ⚡ 24/7 Emergency Available"

---

## SECTION ORDER (plumbing-specific — overrides universal default)
  1. Sticky header: logo + phone + 60-second text-back badge
  2. Hero: urgency headline + rating subheadline + two CTAs + badge row
  3. GHL voice widget placeholder
  4. Trust bar (4 items above)
  5. Services: card grid (emergency services FIRST)
  6. "Why Choose Us" — 3 differentiators with icons
  7. Process: 4 steps (Call → Quote → Arrive in 60 min → Done + Guaranteed)
  8. Reviews/testimonials: 3 real GBP reviews
  9. GHL reviews widget placeholder
  10. Service areas: neighborhoods + Google Maps iFrame
  11. Booking section (BELOW reviews — plumbing is call-first, not booking-first)
  12. Contact/quote form
  13. Footer

## NOTE ON BOOKING POSITION
Plumbing is an emergency trade. Most customers call, not book online.
Booking calendar appears BELOW reviews (not above like cleaning/HVAC).
Primary CTA is always phone. Booking is for non-emergency quote requests.

---

## DEFAULT SERVICES LIST
(Used if extraction returns empty — replace with real services from GBP)
Emergency Plumbing, Drain Cleaning, Water Heater Repair & Replacement,
Pipe Repair & Replacement, Toilet Repair & Installation,
Faucet & Fixture Repair, Sump Pump Installation, Sewer Line Repair,
Bathroom Plumbing, Kitchen Plumbing, Leak Detection, Backflow Prevention

## SERVICES SECTION RULE
List emergency services FIRST in the card grid:
Card 1: Emergency Plumbing (with 🚨 icon)
Card 2: Drain Cleaning
Card 3: Water Heater
...remaining services

---

## HERO HEADLINE FORMULAS
Option A: "Fast, Reliable Plumbing in [CITY_PROVINCE] — 24/7 Emergency Service"
Option B: "Plumbing Emergency in [CITY_PROVINCE]? We Arrive in 60 Minutes."
Option C: "[CITY_PROVINCE]'s Trusted Plumbers — On Time, Every Time"
Recommended: Option B for maximum urgency and specificity.

## HERO SUBHEADLINE
"[RATING_STRING] • Serving [CITY_PROVINCE] and surrounding areas"
Example: "⭐⭐⭐⭐⭐ 4.9/5 · 166 Google Reviews • Serving Mississauga, ON"

---

## WHY CHOOSE US SECTION (3 differentiators)
1. ⚡ Fast Emergency Response
   "We dispatch within 30 minutes. Plumbing emergencies can't wait."
2. 💯 Upfront Pricing
   "No surprises. We give you the price before we start — guaranteed."
3. 🏆 [YEARS_IN_BUSINESS] Years of Local Experience
   "Trusted by homeowners in [CITY_PROVINCE] for over [YEARS_IN_BUSINESS] years."

---

## PROCESS SECTION (4 steps — plumbing-specific labels)
Step 1: "Call or Text Us"           — "Available 24/7 including holidays"
Step 2: "Fast Arrival"              — "Our team arrives in 60 minutes or less"
Step 3: "Diagnose & Fix"            — "Upfront pricing before any work begins"
Step 4: "Satisfaction Guaranteed"   — "We're not done until you're 100% happy"

---

## REVIEWS SECTION
Display 3 verbatim reviews from [REVIEWS_3] in quote cards.
Format: ★★★★★ | Quote text | — [First name], Google Review

"Read all [REVIEW_COUNT] reviews on Google →" (link to GBP)

---

## SERVICE AREAS SECTION
Heading: "Proudly Serving [CITY_PROVINCE] and Surrounding Communities"
List format: specific neighborhood names, never "Greater Area"
Map: Google Maps iFrame centered on [CITY_PROVINCE]

---

## BOOKING SECTION HEADING
"Schedule Non-Emergency Plumbing Service"
Subtext: "For emergencies, call [PHONE] — we answer 24/7."

---

## AUDIT RED FLAGS → GENERATION FIXES

| Audit Finding                        | Generation Rule                                                    |
|--------------------------------------|--------------------------------------------------------------------|
| Reviews hidden / not displayed       | Rating + count in hero subheadline; 3 review cards prominent       |
| JS-only build (not indexable)        | Semantic HTML: h1, h2, section, article — server-side renderable   |
| No lead capture                      | All 6 GHL placeholder divs, clearly labeled with dashed borders    |
| No tap-to-call                       | tel: href on EVERY phone instance — header, hero, mid-page, footer |
| No emergency messaging               | 24/7 badge in sticky header + hero trust bar + process step label  |
| No service areas listed              | Specific neighborhood names in dedicated section + Maps iFrame     |
| No trust signals                     | Trust bar, years badge, licensed/insured badge, rating in hero     |
| Outdated design                      | Clean modern card grid, generous whitespace, professional palette  |
| No process explanation               | 4-step process section mandatory                                   |
| No booking/contact form              | GHL form placeholder + response promise                            |

---

## NICHE-SPECIFIC PROMPT ADDITIONS
Add to the end of the site generation prompt when building for plumbing:

"""
PLUMBING-SPECIFIC REQUIREMENTS:
- The word "Emergency" must appear in: header badge, hero headline or CTA, trust bar item 1, process step label
- Phone number in sticky header must have a red/accent background button — not just a text link
- Services grid: emergency services in cards 1-2 with red accent color
- Hero color scheme: navy (#1a3a6b) dominant, red (#e84040) accent for emergency elements only
- Do NOT use blue as the primary emergency color — navy is trust, red is emergency
- Trust bar item 3: "⏱️ Arrive in 60 Minutes" — this is a specific response time promise
- Footer must include: 24/7 availability statement in hours column
- Every section break between major sections should have the phone number as a mid-page CTA
- The booking section heading should clarify it's for non-emergencies — primary is call
"""

---

## TYPICAL JOB VALUES (for ROI conversations in sales)
Small job (clog, faucet):  $150–$400
Mid job (water heater):    $800–$2,000
Large job (sewer, pipe):   $2,000–$8,000+
Emergency premium:         +30–50% on any job
Average job value:         ~$500–$800

## COLD OUTREACH HOOK
"I noticed your [REVIEW_COUNT] five-star Google reviews are completely invisible on your website —
most customers check the site before calling, so you're leaving trust on the table.
I built a 30-second preview using your actual business data."

## PRICING GUIDANCE
Setup fee range:   $1,997 – $2,497 (Growth System recommended for emergency trades)
Monthly retainer:  $297/month (includes GHL automations — voice AI, missed call text-back)
Key ROI argument:  "One missed emergency call is $400–$800. Our missed-call text-back
                   pays for the first year in the first week."

---

## PROMPT_VARIABLES
# Machine-readable key:value pairs for fill_variables() in generate_website.py
# These power the universal_claude_code_prompt.txt template.
# Key names must match [BRACKET_VARS] in the template exactly.
# Do NOT rename keys. Add new keys to the template if adding new sections.

NICHE_TRADE_LABEL: plumbing
NICHE_TRADE_LABEL_CAP: Plumbing
NICHE_ICON_EMOJI: 🔧
NICHE_PAGE_TITLE_TRADE: 24/7 Emergency Plumber
NICHE_META_DESCRIPTION: Licensed plumbers in [CITY_PROVINCE]. [YEARS_IN_BUSINESS] years experience, 24/7 emergency, free estimates. Call [PHONE].
NICHE_META_TRADE_NOUN: plumbers
NICHE_HERO_HEADLINE: Plumbing Emergency in [CITY_PROVINCE]? We Arrive in 60 Minutes.
NICHE_PRIMARY_CTA_TEXT: Call Now — 24/7 Emergency Service
NICHE_MISSED_CALL_BADGE: Missed us? We'll text you back in 60 seconds.
NICHE_HERO_TRUST_BADGE: 24/7 Emergency Available
PRIMARY_COLOR: #1a3a6b
ACCENT_COLOR: #e84040
NICHE_SERVICES_SUBHEADING: Professional plumbing solutions for every need
NICHE_AREAS_SUBHEADING: Fast, reliable plumbing service across the region
NICHE_FOOTER_TAGLINE: Your trusted local 24/7 plumbing professionals. We answer when others don't.
NICHE_FOOTER_HOURS_LABEL: 24/7 Emergency Service
NICHE_FOOTER_EMERGENCY_LINE: Emergency calls: Anytime
NICHE_BOOKING_HEADING: Schedule Non-Emergency Plumbing Service
NICHE_BOOKING_SUBTEXT: For emergencies, call [PHONE] — we answer 24/7.
NICHE_PROCESS_SUBHEADING: Getting your plumbing fixed is easy
MAPS_LAT: 43.58
MAPS_LNG: -79.65
REGION_LABEL: the GTA
AGENCY_NAME: YourAgencyName
NICHE_TRUST_BAR_BLOCK: ⚡ Available 24/7 | Emergency service including holidays | ✅ Licensed & Insured | Fully certified and covered | ⏱️ Arrive in 60 Minutes | Fast dispatch every time | 📋 Free Estimates | No obligation quotes
NICHE_WHY_CHOOSE_US_BLOCK: ⚡ Fast Emergency Response | We dispatch within 30 minutes. Plumbing emergencies can't wait. | 💯 Upfront Pricing | No surprises. We give you the price before we start — guaranteed. | 🏆 [YEARS_IN_BUSINESS] Years of Local Experience | Trusted by homeowners in [CITY_PROVINCE] for over [YEARS_IN_BUSINESS] years.
NICHE_PROCESS_BLOCK: Call or Text Us | Available 24/7 including holidays | Fast Arrival | Our team arrives in 60 minutes or less | Diagnose & Fix | Upfront pricing before any work begins | Satisfaction Guaranteed | We're not done until you're 100% happy
