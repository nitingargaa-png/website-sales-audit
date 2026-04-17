# Niche File: Roofing
# Layer 3 of three-layer prompt system
# Read by generate_website.py when niche == "roofing"
# Last updated: March 2026

---

## DETECTION KEYWORDS
roofing, roofer, roof repair, roof replacement, roof installation, shingles,
flat roof, metal roof, eavestroughs, gutters, siding, storm damage, leak repair,
insurance claim, roof inspection, soffit, fascia, skylight, flat roofing

## PRIMARY EMOTION TO TRIGGER
Protection + Trust + Value. Roofing is the highest-ticket trade in your niche.
Customers are making a $5,000–$20,000 decision and they are scared of being
ripped off. The emotional state is: worried about their home, anxious about
cost, and skeptical of contractors. Copy must lead with protection (your home
is safe with us), social proof (reviews + years in business), and transparency
(free inspection, no pressure quotes). Financing is critical for high-ticket jobs.

---

## CTA BUTTONS
Primary:   "Get a Free Roof Inspection"   (scrolls to #contact — inspection is the foot in the door)
Secondary: "Call Now"                     (href="tel:+1[PHONE_DIGITS]")

## PHONE CTA TEXT (in hero)
"📞 [PHONE] — Free Inspections, No Pressure"

## MISSED CALL BADGE (in header)
"Missed us? We'll text you back in 60 seconds."

---

## COLOR PALETTE
Primary:   #1a3a6b   (deep navy — trust, stability, professionalism)
Accent:    #dc6b19   (burnt orange — strength, warmth, roofing materials)
Text:      #1a1a1a   (near-black — readability)
Light bg:  #fef9f5   (very light warm tint — complements orange)
Button:    #dc6b19 hover:#b85a14  (primary CTA — burnt orange)
Emergency: #e84040 hover:#c73232  (storm damage emergency banner only)
Secondary: #1a3a6b hover:#12285a

NOTE ON COLOR: Roofing uses burnt orange (#dc6b19) as primary accent.
Orange signals strength, durability, and the physical nature of roofing materials.
Reserve red (#e84040) for storm damage emergency banners only.
Never use purple.

## TYPOGRAPHY (Tailwind classes)
Hero headline:   text-4xl md:text-6xl font-black leading-tight
Section heading: text-3xl font-bold
Body:            text-base md:text-lg leading-relaxed
CTA button:      text-lg font-bold px-8 py-4 rounded-lg

---

## TRUST BAR (4 items — roofing-specific, high-ticket trust signals)
1. 🏆 [YEARS_IN_BUSINESS] Years Experience  (longevity = stability for high-ticket decisions)
2. ✅ Licensed, Bonded & Insured             (absolute requirement for any roof work)
3. 💰 Financing Available                   (high ticket — financing removes the barrier)
4. 🛡️ Workmanship Warranty                  (peace of mind — how long is it guaranteed?)

## HERO BADGE ROW (below CTA buttons)
"🏆 [YEARS_IN_BUSINESS] Years  •  ⭐ [RATING_STRING]  •  🛡️ Workmanship Warranty"

---

## SECTION ORDER (roofing — inspection-first, high-ticket planned)
  1. Sticky header: logo + phone + 60-second text-back badge
  2. Hero: protection headline + free inspection CTA + social proof
  3. Emergency storm damage banner (conditional — appears at top if storm season)
  4. GHL voice widget placeholder
  5. Trust bar (longevity + credentials + financing + warranty)
  6. Services: card grid (repairs + replacements + specialty)
  7. "Why Choose Us" — 3 differentiators (experience, warranty, financing)
  8. Process: 4 steps (inspection → quote → install → warranty)
  9. Reviews/testimonials: 3 real GBP reviews
  10. GHL reviews placeholder
  11. Service areas: neighborhoods + Google Maps iFrame
  12. Booking / inspection request section
  13. Contact/quote form
  14. Footer

## NOTE ON BOOKING POSITION
Roofing is primarily a planned trade with a long sales cycle.
The conversion goal is NOT an immediate call — it is a FREE INSPECTION booking.
Primary CTA: "Get a Free Roof Inspection" (form/calendar).
Secondary CTA: phone call.
Booking section appears after reviews — customer needs to trust you before booking
a large-ticket inspection that leads to a $10K+ proposal.

---

## DEFAULT SERVICES LIST
(Used if extraction returns empty — replace with real services from GBP)
Roof Replacement, Roof Repair, Flat Roof Systems, Shingle Installation,
Metal Roofing, Storm Damage Repair, Eavestrough & Gutter Installation,
Siding Installation, Roof Inspections, Skylight Installation,
Soffit & Fascia, Ice Dam Removal, Insurance Claim Assistance

## SERVICES SECTION RULE
High-demand services FIRST:
Card 1: Roof Replacement (orange icon) — "Full replacement with [YEARS_IN_BUSINESS]-year warranty"
Card 2: Storm Damage Repair (orange icon) — "Insurance claims accepted — we handle the paperwork"
Cards 3+: Repairs, gutters, siding, inspections in navy
Always include "Insurance Claim Assistance" as a visible service — major differentiator.

---

## HERO HEADLINE FORMULAS
Option A: "Trusted Roofing in [CITY_PROVINCE] — Free Inspections, Honest Quotes"
Option B: "Protect Your Home with [CITY_PROVINCE]'s Most Trusted Roofers"
Option C: "Roof Repair & Replacement in [CITY_PROVINCE] — [YEARS_IN_BUSINESS] Years, Warranted Work"
Recommended: Option B — leads with emotional outcome (protection) over service.

## HERO SUBHEADLINE
"[RATING_STRING] • Free Inspections • Financing Available • Serving [CITY_PROVINCE]"

---

## WHY CHOOSE US SECTION (3 roofing differentiators)
1. 🏆 [YEARS_IN_BUSINESS] Years of Proven Work
   "We've roofed thousands of homes in [CITY_PROVINCE]. Our track record speaks for itself."
2. 🛡️ Workmanship Warranty
   "Every installation comes with a workmanship warranty on top of manufacturer coverage."
3. 💰 Flexible Financing Options
   "Don't let budget stop you from protecting your home. Ask about 0% financing."

---

## PROCESS SECTION (4 steps — roofing/inspection-specific)
Step 1: "Book a Free Inspection"    — "No pressure, no obligation — just an honest assessment"
Step 2: "Detailed Written Quote"    — "Itemized pricing. No hidden fees. Compare it to anyone."
Step 3: "Professional Installation" — "On time, on budget, cleaned up completely when done"
Step 4: "Warranty & Follow-Up"      — "Workmanship guaranteed — we stand behind every nail"

---

## REVIEWS SECTION
Display 3 verbatim reviews from [REVIEWS_3] in quote cards.
Prioritize reviews that mention: price transparency, warranty, insurance help, cleanup.
Format: ★★★★★ | Quote text | — [First name], Google Review

"Read all [REVIEW_COUNT] reviews on Google →" link to GBP

---

## BOOKING SECTION HEADING
"Book Your Free Roof Inspection"
Subtext: "No obligation. Takes 30 minutes. You'll know exactly what your roof needs."
Include urgency trigger: "Spots fill fast — especially after storm season."

---

## CONTACT SECTION HEADING
"Get Your Free Roofing Quote"
Subtext: "Tell us about your project and we'll be in touch within 2 hours."

---

## AUDIT RED FLAGS → GENERATION FIXES

| Audit Finding                        | Generation Rule                                                         |
|--------------------------------------|-------------------------------------------------------------------------|
| Reviews hidden / not displayed       | Rating + count in hero; 3 review cards; years in trust bar              |
| No warranty mention                  | Workmanship warranty in trust bar, Why Choose Us, and process step 4    |
| No financing mention                 | Financing in trust bar item 3 + hero subheadline + Why Choose Us        |
| No insurance claim assistance        | Include as a services card — major roofing differentiator               |
| No free inspection CTA               | Primary hero CTA is inspection booking — not just "call now"            |
| No tap-to-call                       | tel: href on every phone instance                                       |
| No years in business shown           | [YEARS_IN_BUSINESS] in trust bar item 1 and Why Choose Us               |
| No service areas                     | Specific neighborhoods in dedicated section + Maps iFrame               |
| Generic contractor look              | Burnt orange accent differentiates from commodity roofing sites         |

---

## NICHE-SPECIFIC PROMPT ADDITIONS
Add to the end of the site generation prompt when building for roofing:

"""
ROOFING-SPECIFIC REQUIREMENTS:
- Primary accent color is burnt orange (#dc6b19) NOT red — roofing is not primarily emergency
- Primary hero CTA is "Get a Free Roof Inspection" — NOT "Call Now" (inspection = lead magnet)
- Financing must appear in: hero subheadline, trust bar, Why Choose Us, and CTA section
- Workmanship warranty must appear in: trust bar, Why Choose Us section, process step 4
- Insurance claim assistance must be a visible services card — it is a key differentiator
- Years in business [YEARS_IN_BUSINESS] must appear in trust bar item 1
- Storm damage repair in top 2 service cards with orange accent
- Booking section heading: "Book Your Free Roof Inspection" — emphasize free + no obligation
- Add urgency trigger in booking section: "Spots fill fast after storm season"
- Reserve red (#e84040) for storm damage emergency banner only (conditional element)
- Photo gallery section strongly recommended if client provides job photos
"""

---

## TYPICAL JOB VALUES (for ROI conversations in sales)
Roof inspection (leads to):   free
Roof repair:                  $500–$3,000
Full shingle replacement:     $8,000–$18,000
Metal roofing:                $12,000–$30,000+
Flat roof system:             $5,000–$20,000+
Eavestrough/gutters:          $800–$3,000
Siding:                       $8,000–$25,000+
Average job value:            ~$10,000–$15,000

## COLD OUTREACH HOOK
"I noticed your [REVIEW_COUNT] five-star Google reviews are buried — not visible
on your website. Roofing customers spend 3–5 days researching before calling.
If your reviews and credentials aren't front and center, you're losing jobs
to whoever shows up first in search. I built a 30-second demo using your data."

## PRICING GUIDANCE
Setup fee range:   $2,497 – $3,497 (Growth System — high job values justify top package)
Monthly retainer:  $297/month
Key ROI argument:  "One extra roof job per quarter at $12,000 average = $48,000/year.
                   Our missed-call text-back alone has recovered deals for clients —
                   a homeowner calls 3 roofers, the first one to respond wins.
                   At $297/month, your system pays for itself on the first call it catches."

---

## PROMPT_VARIABLES
NICHE_TRADE_LABEL: roofing
NICHE_TRADE_LABEL_CAP: Roofing
NICHE_ICON_EMOJI: 🏠
NICHE_PAGE_TITLE_TRADE: Licensed Roofing Contractor
NICHE_META_DESCRIPTION: Licensed roofers in [CITY_PROVINCE]. Roof repair, replacement, emergency tarping. Free estimates. [YEARS_IN_BUSINESS] years experience. Call [PHONE].
NICHE_META_TRADE_NOUN: roofing contractors
NICHE_HERO_HEADLINE: Roof Damage in [CITY_PROVINCE]? Get a Free Estimate Today.
NICHE_PRIMARY_CTA_TEXT: Get a Free Roof Inspection
NICHE_MISSED_CALL_BADGE: Missed us? We'll text you back right away.
NICHE_HERO_TRUST_BADGE: Free Estimates · Licensed & Insured
PRIMARY_COLOR: #2c1810
ACCENT_COLOR: #c0392b
NICHE_SERVICES_SUBHEADING: Complete roofing solutions for homeowners and commercial properties
NICHE_AREAS_SUBHEADING: Trusted roofing service across the region
NICHE_FOOTER_TAGLINE: Protecting [CITY_PROVINCE] homes since [YEARS_IN_BUSINESS] years ago. Built to last.
NICHE_FOOTER_HOURS_LABEL: Mon–Sat 7AM–7PM
NICHE_FOOTER_EMERGENCY_LINE: Emergency tarping: Anytime
NICHE_BOOKING_HEADING: Schedule Your Free Roof Inspection
NICHE_BOOKING_SUBTEXT: No pressure — just an honest assessment. Or call [PHONE].
NICHE_PROCESS_SUBHEADING: Getting your roof fixed is straightforward
MAPS_LAT: 43.58
MAPS_LNG: -79.65
REGION_LABEL: the GTA
AGENCY_NAME: YourAgencyName
NICHE_TRUST_BAR_BLOCK: 🛡️ Licensed & Fully Insured | WSIB + $5M liability coverage | 📋 Free Roof Inspection | No pressure, honest assessment | ⚡ Emergency Tarping | Same-day response for leaks | 🏆 [YEARS_IN_BUSINESS] Years Experience | Local roofers who stand behind their work
NICHE_WHY_CHOOSE_US_BLOCK: 🛡️ Fully Licensed & Insured | We carry WSIB and full liability — you're protected every step of the way. | 📋 Free, Honest Estimates | No upsells, no pressure. Just a clear report on what your roof actually needs. | 🏆 [YEARS_IN_BUSINESS] Years in [CITY_PROVINCE] | Local roofers who stand behind their work — we're here after the job is done.
NICHE_PROCESS_BLOCK: Free Inspection | We assess your roof honestly with no obligation | Written Estimate | Clear pricing with no hidden costs | Expert Installation | Licensed roofers, quality materials | Warranty Backed | Manufacturer and workmanship warranty included
