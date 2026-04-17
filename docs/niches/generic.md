# Niche File: Generic (Fallback)
# Fallback niche — used when extract_business_data.py cannot match a specific trade.
# Covers general home services. Works for handyman, moving, junk removal, painting,
# garage door, and any trade not yet covered by a dedicated niche file.
# Read by generate_website.py when niche == "generic" or niche file not found.
# Last updated: March 2026

---

## DETECTION KEYWORDS
home service, contractor, repair, installation, maintenance, service, professional,
local, licensed, insured, free estimate, free quote

## PRIMARY EMOTION TO TRIGGER
Trust + Reliability. Generic service customers are making a hiring decision with limited
context. Lead with professionalism, credentials, and local presence. The message:
"We're a real local business, we're licensed, and we show up when we say we will."

---

## CTA BUTTONS
Primary:   "Call Now for a Free Quote"     (href="tel:+1[PHONE_DIGITS]")
Secondary: "Get a Free Estimate"           (scrolls to #contact)

## PHONE CTA TEXT (in hero)
"📞 Call [PHONE] — Free Estimates, Fast Response"

## MISSED CALL BADGE (in header)
"Missed us? We'll text you back in 60 seconds."

---

## COLOR PALETTE
Primary:   #1a3a6b   (deep navy — trust, professional)
Accent:    #2e7d32   (forest green — reliability, local)
Text:      #1a1a1a   (near-black — readability)
Light bg:  #f7f9fc   (off-white — sections)
Button:    #1a3a6b hover:#12285a

## TYPOGRAPHY (Tailwind classes)
Hero headline:   text-4xl md:text-6xl font-black leading-tight
Section heading: text-3xl font-bold
Body:            text-base md:text-lg leading-relaxed
CTA button:      text-lg font-bold px-8 py-4 rounded-lg

---

## TRUST BAR (4 items — generic defaults)
1. ✅ Licensed & Insured
2. 🏆 [YEARS_IN_BUSINESS]+ Years Experience
3. 📋 Free Estimates
4. ⭐ [RATING_STRING]

## HERO BADGE ROW (below CTA buttons)
"🔒 Licensed & Insured  •  📋 Free Estimates  •  ⭐ [RATING_STRING]"

---

## SECTION ORDER (generic — universal default)
  1. Sticky header: logo + phone + text-back badge
  2. Hero: headline + rating subheadline + two CTAs + badge row
  3. GHL voice widget placeholder
  4. Trust bar (4 items above)
  5. Services: card grid
  6. "Why Choose Us" — 3 differentiators
  7. Process: 4 steps
  8. Reviews/testimonials
  9. GHL reviews widget placeholder
  10. Service areas: neighborhoods + Google Maps iFrame
  11. Booking section
  12. Contact/quote form
  13. Footer

---

## DEFAULT SERVICES LIST
(Replace with real services from extraction)
Free Estimates, Emergency Service, Installation, Repair, Maintenance,
Inspection, Consultation, Cleanup

---

## HERO HEADLINE FORMULAS
Option A: "Trusted [City] Home Service Professionals — Licensed & Insured"
Option B: "Fast, Reliable Service in [CITY_PROVINCE] — Free Estimates"
Option C: "[CITY_PROVINCE]'s Trusted Local Contractors — On Time, Every Time"

## HERO SUBHEADLINE
"[RATING_STRING] • Serving [CITY_PROVINCE] and surrounding areas"

---

## WHY CHOOSE US SECTION (3 differentiators)
1. ✅ Licensed & Fully Insured
   "We carry full liability coverage — your home and family are always protected."
2. ⏱️ Fast Response Times
   "We show up when we say we will. No all-day waiting windows."
3. 💯 Upfront, Honest Pricing
   "You'll know the cost before we start — no hidden fees, ever."

---

## PROCESS SECTION (4 steps — generic)
Step 1: "Call or Request a Quote"   — "Free estimates, no obligation"
Step 2: "We Come to You"            — "Fast scheduling, flexible hours"
Step 3: "Expert Service"            — "Done right the first time"
Step 4: "Satisfaction Guaranteed"   — "We're not done until you're happy"

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
"Schedule Your Service"
Subtext: "Or call [PHONE] — we answer fast."

---

## AUDIT RED FLAGS → GENERATION FIXES

| Audit Finding                    | Generation Rule                                              |
|----------------------------------|--------------------------------------------------------------|
| Reviews hidden                   | Rating + count in hero subheadline; 3 review cards          |
| No tap-to-call                   | tel: href on EVERY phone instance                            |
| No lead capture                  | All 6 GHL placeholder divs with dashed borders              |
| No service areas                 | Specific neighborhood names + Maps iFrame                   |
| No trust signals                 | Trust bar, licensed/insured badge, rating in hero           |
| No process explanation           | 4-step process section mandatory                            |
| No booking/contact form          | GHL form placeholder + response promise                     |

---

## TYPICAL JOB VALUES (for ROI conversations)
Varies widely by trade — research the specific trade before sales call.
General home service average: $200–$1,500 per job.

## COLD OUTREACH HOOK
"I noticed your [REVIEW_COUNT] Google reviews aren't showing on your website —
customers check reviews before calling, so you're leaving trust on the table.
I built a quick preview using your actual business info."

## PRICING GUIDANCE
Setup fee range:   $997 – $1,997 (Foundation or Growth System)
Monthly retainer:  $97–$297/month
Recommend Package 2 (Growth System) if the business takes phone calls for leads.
