# Niche File: Cleaning
# Layer 3 of three-layer prompt system
# Read by generate_website.py when niche == "cleaning"
# Last updated: March 2026

---

## DETECTION KEYWORDS
cleaning, house cleaning, maid service, residential cleaning, deep cleaning,
move-in cleaning, move-out cleaning, cleaning service, cleaner, janitorial,
commercial cleaning, office cleaning, recurring cleaning, cleaning company

## PRIMARY EMOTION TO TRIGGER
Relief + Pride. Cleaning customers are busy people who feel guilty about a messy
home or overwhelmed by the task. They are not in an emergency — they are making
a quality-of-life decision. Copy must acknowledge the feeling ("You deserve a
clean home without the stress") and emphasize convenience, reliability, and the
satisfaction of coming home to a spotless space. Trust signals: insurance,
background checks, consistent cleaners.

---

## CTA BUTTONS
Primary:   "Book Your Cleaning Online"    (scrolls to #booking — booking-first trade)
Secondary: "Get a Free Quote"             (scrolls to #contact)
Emergency: NOT APPLICABLE — cleaning is a planned trade, no emergency CTA needed

## PHONE CTA TEXT (in hero)
"📞 Call [PHONE] or Book Online — Easy Scheduling"

## MISSED CALL BADGE (in header)
"Missed us? We'll text you back in 60 seconds."

---

## COLOR PALETTE
Primary:   #1a3a6b   (deep navy — trust, professionalism)
Accent:    #10b981   (emerald green — cleanliness, freshness, nature)
Text:      #1a1a1a   (near-black — readability)
Light bg:  #f0fdf4   (very light green tint — fresh, clean feeling)
Button:    #10b981 hover:#059669  (primary CTA — green)
Secondary: #1a3a6b hover:#12285a

NOTE ON COLOR: Cleaning uses emerald green (#10b981) as primary accent.
Green signals cleanliness, freshness, and eco-friendliness — core cleaning values.
Do NOT use red — there are no emergencies in cleaning. Never use purple.

## TYPOGRAPHY (Tailwind classes)
Hero headline:   text-4xl md:text-6xl font-black leading-tight
Section heading: text-3xl font-bold
Body:            text-base md:text-lg leading-relaxed
CTA button:      text-lg font-bold px-8 py-4 rounded-lg

---

## TRUST BAR (4 items — cleaning-specific, reliability-first)
1. 🔒 Insured & Bonded          (protects client's home — most important trust signal)
2. ✅ Background-Checked Staff   (safety of cleaners entering the home)
3. 🌿 Eco-Friendly Products      (growing customer preference — use if applicable)
4. ⭐ Satisfaction Guaranteed    (strong for recurring clients)

## HERO BADGE ROW (below CTA buttons)
"🔒 Insured & Bonded  •  ⭐ [RATING_STRING]  •  ✅ Background-Checked Staff"

---

## SECTION ORDER (cleaning — booking-first, planned trade)
  1. Sticky header: logo + phone + 60-second text-back badge
  2. Hero: quality-of-life headline + booking CTA prominent (not just phone)
  3. GHL voice widget placeholder
  4. Trust bar (reliability + safety signals)
  5. Services: card grid (recurring first, one-time/specialty second)
  6. Booking section — MOVED UP — cleaning is booking-first, not call-first
  7. "Why Choose Us" — 3 differentiators
  8. Process: 4 steps
  9. Reviews/testimonials: 3 real GBP reviews
  10. GHL reviews widget placeholder
  11. Service areas: neighborhoods + Google Maps iFrame
  12. Contact/quote form
  13. Footer

## NOTE ON BOOKING POSITION
Cleaning is a PLANNED trade — customers book in advance, not in emergencies.
Booking calendar appears ABOVE Why Choose Us — it is the primary conversion action.
Phone is secondary. The booking section should be prominent, above the fold if possible.
Never use emergency language ("24/7", "fast response") for routine cleaning.

---

## DEFAULT SERVICES LIST
(Used if extraction returns empty — replace with real services from GBP)
Recurring Home Cleaning (Weekly/Bi-Weekly/Monthly),
Deep Cleaning, Move-In Cleaning, Move-Out Cleaning,
Post-Construction Cleaning, Airbnb & Short-Term Rental Cleaning,
Office & Commercial Cleaning, Spring Cleaning, Window Cleaning,
Appliance Cleaning, Carpet Cleaning, Upholstery Cleaning

## SERVICES SECTION RULE
Recurring services FIRST — this is where the business makes its money:
Card 1: Recurring Home Cleaning — "Weekly, bi-weekly, or monthly — your schedule"
Card 2: Deep Cleaning — "Perfect for first-time clients or seasonal resets"
Cards 3+: Move-in/out, Airbnb, commercial, specialty in navy

Show PRICING on service cards if available — cleaning customers comparison shop.
Include a "most popular" badge on recurring service card.

---

## HERO HEADLINE FORMULAS
Option A: "Professional House Cleaning in [CITY_PROVINCE] — Come Home to Clean"
Option B: "A Spotless Home in [CITY_PROVINCE] — Reliable, Thorough, Every Time"
Option C: "[CITY_PROVINCE]'s Most Trusted Cleaning Service — Book in 60 Seconds"
Recommended: Option A — emotional benefit first ("come home to clean") then location.

## HERO SUBHEADLINE
"[RATING_STRING] • Serving [CITY_PROVINCE] and surrounding areas"

---

## WHY CHOOSE US SECTION (3 cleaning differentiators)
1. 🔒 Fully Insured & Bonded
   "Your home and belongings are fully protected. Every cleaner is background-checked."
2. ⭐ Consistent Cleaners
   "We send the same team every visit so you never have to re-explain your preferences."
3. 🌿 Eco-Friendly Products
   "Safe for kids, pets, and the planet — we use green products without the extra charge."

---

## PROCESS SECTION (4 steps — cleaning-specific)
Step 1: "Book Online in 60 Seconds"   — "Choose your service, date, and frequency"
Step 2: "We Arrive On Time"           — "Punctual, professional, and ready to work"
Step 3: "Thorough Top-to-Bottom Clean" — "Every surface, corner, and detail"
Step 4: "Come Home to Clean"          — "If anything isn't right, we re-clean for free"

---

## REVIEWS SECTION
Display 3 verbatim reviews from [REVIEWS_3] in quote cards.
Format: ★★★★★ | Quote text | — [First name], Google Review

"Read all [REVIEW_COUNT] reviews on Google →" link to GBP

---

## BOOKING SECTION HEADING (appears ABOVE Why Choose Us in cleaning)
"Book Your Cleaning Online"
Subtext: "Takes 60 seconds. Pick your service, date, and how often."
Include pricing tiers if available:
  - Standard Cleaning: from $X
  - Deep Cleaning: from $X
  - Move-In/Move-Out: from $X

---

## CONTACT SECTION HEADING
"Get a Custom Quote"
Subtext: "Larger homes, commercial spaces, or custom requests — tell us what you need."

---

## AUDIT RED FLAGS → GENERATION FIXES

| Audit Finding                        | Generation Rule                                                        |
|--------------------------------------|------------------------------------------------------------------------|
| Reviews hidden / not displayed       | Rating + count in hero subheadline; 3 review cards prominent           |
| No online booking                    | GHL calendar placeholder prominent, above Why Choose Us                |
| No pricing shown                     | Add pricing tiers in booking section or service cards                  |
| No insurance/bonding mention         | "Insured & Bonded" in hero badge + trust bar item 1                    |
| No background check mention          | Trust bar item 2 + Why Choose Us                                       |
| Red/emergency colors used            | Remove all red — green is the accent for cleaning                      |
| No recurring service emphasis        | Recurring cleaning first in services grid with "most popular" badge    |
| No tap-to-call                       | tel: href on every phone instance                                      |

---

## NICHE-SPECIFIC PROMPT ADDITIONS
Add to the end of the site generation prompt when building for cleaning:

"""
CLEANING-SPECIFIC REQUIREMENTS:
- Primary accent color is emerald green (#10b981) NOT red — cleaning is not an emergency trade
- Never use emergency language ("24/7 emergency", "fast response for disasters") for routine cleaning
- Booking section appears BEFORE Why Choose Us — cleaning is booking-first
- Primary hero CTA is "Book Online" — not "Call Now"
- Services grid: recurring cleaning first with "Most Popular" badge on weekly/bi-weekly card
- Trust signals priority: insured & bonded → background-checked → satisfaction guarantee
- Eco-friendly mention: include even if not confirmed — customers expect it; can be softened
- Show pricing ranges if available: customers comparison shop cleaning more than other trades
- Footer: include recurring service frequency options (weekly, bi-weekly, monthly)
- No red anywhere — this signals emergency and creates wrong emotional tone for cleaning
"""

---

## TYPICAL JOB VALUES (for ROI conversations in sales)
One-time deep clean:        $200–$500
Regular recurring (weekly): $100–$250/visit = $400–$1,000/month
Move-in/move-out:           $250–$600
Airbnb turnover:            $80–$200/turnover
Commercial (small office):  $300–$800/month
Average client LTV:         ~$2,400–$6,000/year (recurring)

## COLD OUTREACH HOOK
"I noticed your [REVIEW_COUNT] five-star reviews aren't showing on your website.
Cleaning customers read reviews more carefully than almost any other trade —
they're trusting you with their home. I built a demo that makes your reputation
the first thing they see."

## PRICING GUIDANCE
Setup fee range:   $1,497 – $1,997 (Foundation or Growth System)
Monthly retainer:  $197–$297/month
Key ROI argument:  "One new recurring client at $150/visit bi-weekly = $300/month.
                   Three new clients = your system cost covered permanently.
                   Our review request automation alone has gotten clients 20+ new reviews."

---

## PROMPT_VARIABLES
NICHE_TRADE_LABEL: cleaning
NICHE_TRADE_LABEL_CAP: Cleaning
NICHE_ICON_EMOJI: ✨
NICHE_PAGE_TITLE_TRADE: Professional House Cleaning
NICHE_META_DESCRIPTION: Professional cleaning services in [CITY_PROVINCE]. Recurring, deep clean, move-in/out. Insured cleaners. Book online. Call [PHONE].
NICHE_META_TRADE_NOUN: cleaning professionals
NICHE_HERO_HEADLINE: Professional Cleaning in [CITY_PROVINCE] — Book in 60 Seconds.
NICHE_PRIMARY_CTA_TEXT: Book Your Clean Online
NICHE_MISSED_CALL_BADGE: Missed us? We'll text you back right away.
NICHE_HERO_TRUST_BADGE: Insured & Background Checked
PRIMARY_COLOR: #1a5c3a
ACCENT_COLOR: #2ecc71
NICHE_SERVICES_SUBHEADING: Residential and commercial cleaning services you can count on
NICHE_AREAS_SUBHEADING: Trusted cleaning service across the region
NICHE_FOOTER_TAGLINE: Professional, insured cleaners who treat your home like their own.
NICHE_FOOTER_HOURS_LABEL: Available Mon–Sat
NICHE_FOOTER_EMERGENCY_LINE: Same-day bookings available
NICHE_BOOKING_HEADING: Book Your Cleaning Online
NICHE_BOOKING_SUBTEXT: Choose your date and time — no phone call required.
NICHE_PROCESS_SUBHEADING: Getting a clean home is easy
MAPS_LAT: 43.58
MAPS_LNG: -79.65
REGION_LABEL: the GTA
AGENCY_NAME: YourAgencyName
NICHE_TRUST_BAR_BLOCK: ✅ Insured & Bonded | Fully covered — your home is protected | 🔍 Background Checked | Every cleaner vetted before hire | ⭐ Satisfaction Guaranteed | We'll re-clean anything you're not happy with | 📅 Easy Online Booking | Schedule in 60 seconds
NICHE_WHY_CHOOSE_US_BLOCK: ✅ Fully Insured & Bonded | Every clean is covered. Your home and belongings are always protected. | ⭐ Satisfaction Guaranteed | Not happy? We come back and fix it — no questions, no excuses. | 🏆 [YEARS_IN_BUSINESS] Years Serving [CITY_PROVINCE] | Hundreds of happy clients trust us with their homes every week.
NICHE_PROCESS_BLOCK: Book Online | Pick your date in 60 seconds | Confirmation Sent | You'll get a reminder the day before | We Clean | Thorough, professional service every time | Enjoy Your Space | Relax — your home is spotless
