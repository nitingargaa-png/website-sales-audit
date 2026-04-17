# Niche File: [TRADE NAME]
# Copy this template → fill in all fields → save as docs/niches/[trade].md
# Time to complete: ~15–30 minutes
# Layer 3 of the three-layer prompt system

---

## DETECTION KEYWORDS
# Comma-separated words that identify this niche from scraped content
[keyword1], [keyword2], [keyword3], [keyword4], [keyword5]

---

## PRIMARY EMOTION TO TRIGGER
# One of: urgency | relief | pride | protection | trust | value
# Describe the emotional state of the customer when they search for this trade.
[e.g., "Urgency + Relief — customer is stressed, needs fast trusted solution"]

---

## CTA BUTTONS
Primary:   "[Button text]"   (href="tel:+1XXXXXXXXXX" for emergency trades)
Secondary: "[Button text]"   (scrolls to #contact or #booking)

## PHONE CTA TEXT (in hero)
"[e.g., 📞 Call [PHONE] — We Answer 24/7]"

## MISSED CALL BADGE (in header)
"[e.g., Missed us? We'll text you back in 60 seconds.]"

---

## COLOR PALETTE
Primary:   #[hex]   [description — e.g., deep navy — trust, professional]
Accent:    #[hex]   [description — e.g., red for emergency, green for nature trades]
Text:      #1a1a1a  (near-black — keep consistent)
Light bg:  #f7f9fc  (off-white sections — keep consistent)
Button:    #[hex] hover:#[slightly darker hex]

---

## TRUST BAR (4 items — replaces universal defaults for this niche)
1. [Icon] [Title]          [Subtitle e.g., "Available 24/7" or "Same-day service"]
2. ✅ Licensed & Insured   [Subtitle — always include this]
3. [Icon] [Niche-specific] [e.g., "Arrive in 60 min" or "Bonded & Insured"]
4. 📋 Free Estimates       [Subtitle — always include this]

## HERO BADGE ROW (below CTA buttons)
"[e.g., 🔒 Licensed & Insured  •  ⭐ [RATING_STRING]  •  ⚡ 24/7 Emergency]"

---

## SECTION ORDER
# Adjust from universal default based on trade behavior (planned vs emergency)
# Emergency trades: phone first, booking last
# Planned trades (cleaning, landscaping): booking prominent, form primary CTA

  1. Sticky header
  2. Hero
  3. GHL voice widget placeholder
  4. Trust bar
  5. [Trade-specific section — e.g., "Why Choose Us" or "Before/After Gallery"]
  6. Services
  7. Process
  8. Reviews / testimonials
  9. GHL reviews placeholder
  10. Service areas + map
  11. Booking section [position here or earlier depending on trade]
  12. Contact/quote form
  13. Footer

## NOTE ON BOOKING POSITION
# Emergency trades (plumbing, electrical): booking BELOW reviews — call is primary
# Planned trades (cleaning, HVAC, landscaping): booking ABOVE or near top — form is primary
[State which applies to this trade and why]

---

## DEFAULT SERVICES LIST
# Used if extraction returns empty — replace with real extracted services from GBP
[Service 1], [Service 2], [Service 3], [Service 4], [Service 5], [Service 6]

## SERVICES SECTION RULE
# What appears in cards 1–2? Emergency/high-value services first?
[e.g., "Emergency services first with red accent" or "Recurring services first"]

---

## HERO HEADLINE FORMULAS
Option A: "[Adjective] [Trade] in [CITY_PROVINCE] — [Key differentiator]"
Option B: "[Problem statement]? [Solution in one line]."
Option C: "[City]'s [Superlative] [Trade] — [Trust element]"
Recommended: Option [A/B/C] because [reason]

## HERO SUBHEADLINE
"[RATING_STRING] • Serving [CITY_PROVINCE] and surrounding areas"

---

## WHY CHOOSE US SECTION (3 differentiators)
1. [Icon] [Heading]
   "[1-2 sentence proof point]"

2. [Icon] [Heading]
   "[1-2 sentence proof point]"

3. [Icon] [Heading]
   "[1-2 sentence proof point — mention YEARS_IN_BUSINESS if available]"

---

## PROCESS SECTION (4 steps — trade-specific labels)
Step 1: [Label]   | [Subtitle — e.g., "Available 24/7"]
Step 2: [Label]   | [Subtitle]
Step 3: [Label]   | [Subtitle]
Step 4: [Label]   | [Subtitle — always include guarantee/satisfaction]

---

## REVIEWS SECTION
Display 3 verbatim reviews from [REVIEWS_3] in quote cards.
Format: ★★★★★ | Quote text | — [First name], Google Review

"Read all [REVIEW_COUNT] reviews on Google →" link to GBP

---

## BOOKING SECTION HEADING
"[e.g., Schedule Non-Emergency Service Online]"
Subtext: "[e.g., For emergencies, call [PHONE] — we answer 24/7.]"

---

## AUDIT RED FLAGS → GENERATION FIXES

| Audit Finding | Generation Rule |
|---|---|
| Reviews hidden | Rating + count in hero; 3 review cards prominent |
| JS-only build | Semantic HTML: h1, h2, section, article |
| No lead capture | All 6 GHL placeholder divs with dashed borders |
| No tap-to-call | tel: href on every phone instance |
| [Trade-specific flag] | [Trade-specific fix] |
| [Trade-specific flag] | [Trade-specific fix] |

---

## NICHE-SPECIFIC PROMPT ADDITIONS
# Add to end of site generation prompt when building for this trade.
# Keep these as concrete code rules, not vague style suggestions.

"""
[TRADE]-SPECIFIC REQUIREMENTS:
- [Specific rule about what must appear where]
- [Color/styling rule tied to trade psychology]
- [Content rule — what words/sections are mandatory]
- [Layout rule — section order or positioning]
"""

---

## TYPICAL JOB VALUES (for ROI conversations in sales)
Small job: $[min]–$[max]
Mid job:   $[min]–$[max]
Large job: $[min]–$[max]
Emergency premium: [+X% or not applicable]
Recurring value: $[X]/month or not applicable
Average job value: ~$[amount]

## COLD OUTREACH HOOK
"[1–2 sentence personalized hook referencing what a typical bad site in this niche
is missing — e.g., reviews hidden, no tap-to-call, no emergency messaging]"

## PRICING GUIDANCE
Setup fee range:   $[min] – $[max] ([Package tier recommended])
Monthly retainer:  $[amount]/month
Key ROI argument:  "[One specific number — e.g., one extra job/month at $X avg = $Y — covers retainer]"

---

## PROMPT_VARIABLES
# Machine-readable variables for universal_claude_code_prompt.txt
# Parsed by parse_niche_variables() in generate_website.py
# Rules:
#   - Keys must match [BRACKET_VARS] in the template exactly
#   - Values may contain [BASE_VARS] like [PHONE], [CITY_PROVINCE], [YEARS_IN_BUSINESS]
#     — these resolve in a second pass via fill_variables()
#   - Pipe-separated values in BLOCK fields are for readability; Claude Code reads them as-is
#   - MAPS_LAT/LNG: default to nearest major city; generate_website.py will geocode from
#     [CITY_PROVINCE] in a future update
#   - AGENCY_NAME: set once globally — consider moving to .env or CLAUDE.md

NICHE_TRADE_LABEL: [trade slug e.g. plumbing]
NICHE_TRADE_LABEL_CAP: [Title Case e.g. Plumbing]
NICHE_ICON_EMOJI: [single emoji representing the trade]
NICHE_PAGE_TITLE_TRADE: [e.g. 24/7 Emergency Plumber]
NICHE_META_DESCRIPTION: [Full meta description — may use [CITY_PROVINCE], [YEARS_IN_BUSINESS], [PHONE]]
NICHE_META_TRADE_NOUN: [plural noun e.g. plumbers, electricians]
NICHE_HERO_HEADLINE: [Use Option B from HERO HEADLINE FORMULAS above — may use [CITY_PROVINCE]]
NICHE_PRIMARY_CTA_TEXT: [e.g. Call Now — 24/7 Emergency Service]
NICHE_MISSED_CALL_BADGE: [e.g. Missed us? We'll text you back in 60 seconds.]
NICHE_HERO_TRUST_BADGE: [Short phrase for badge row e.g. 24/7 Emergency Available]
PRIMARY_COLOR: [hex — trust/brand color]
ACCENT_COLOR: [hex — CTA/urgency color]
NICHE_SERVICES_SUBHEADING: [e.g. Professional plumbing solutions for every need]
NICHE_AREAS_SUBHEADING: [e.g. Fast, reliable service across the region]
NICHE_FOOTER_TAGLINE: [1 sentence brand tagline for footer]
NICHE_FOOTER_HOURS_LABEL: [e.g. 24/7 Emergency Service or Mon–Sat 8AM–6PM]
NICHE_FOOTER_EMERGENCY_LINE: [e.g. Emergency calls: Anytime or Same-day bookings available]
NICHE_BOOKING_HEADING: [e.g. Schedule Non-Emergency Service]
NICHE_BOOKING_SUBTEXT: [e.g. For emergencies, call [PHONE] — we answer 24/7.]
NICHE_PROCESS_SUBHEADING: [e.g. Getting your [trade] fixed is easy]
MAPS_LAT: [decimal latitude of primary city]
MAPS_LNG: [decimal longitude of primary city — negative for west]
REGION_LABEL: [e.g. the GTA or Southern Ontario]
AGENCY_NAME: YourAgencyName
NICHE_TRUST_BAR_BLOCK: [Item1 icon] [Title] | [Subtitle] | [Item2 icon] [Title] | [Subtitle] | [Item3 icon] [Title] | [Subtitle] | [Item4 icon] [Title] | [Subtitle]
NICHE_WHY_CHOOSE_US_BLOCK: [Icon] [Heading] | [1-2 sentence proof point] | [Icon] [Heading] | [proof point] | [Icon] [Heading] | [proof point — use [YEARS_IN_BUSINESS] and [CITY_PROVINCE]]
NICHE_PROCESS_BLOCK: [Step 1 label] | [Step 1 subtitle] | [Step 2 label] | [subtitle] | [Step 3 label] | [subtitle] | [Step 4 label] | [subtitle — always ends with guarantee/satisfaction]
