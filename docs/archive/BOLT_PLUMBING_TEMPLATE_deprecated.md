# ⚠️ DEPRECATED — NOT LOADED BY ANY SCRIPT
# This file is superseded by docs/master_prompts/plumbing_bolt_prompt.txt
# which is what generate_website.py actually loads for plumbing + bolt mode.
# This file is kept for reference only. Do not edit or rely on it.
# To update the plumbing Bolt prompt: edit master_prompts/plumbing_bolt_prompt.txt
# ─────────────────────────────────────────────────────────

# BOLT PLUMBING TEMPLATE — v3.0
# Niche: Plumbing | Aligned with docs/niches/plumbing.md
# ─────────────────────────────────────────────────────────
# SOURCE OF TRUTH: plumbing.md defines all design decisions.
# This file translates those decisions into a Bolt.new prompt.
# Never change colors, section order, or copy rules here —
# change them in plumbing.md first, then update this file.
#
# VARIABLES — filled automatically by generate_website.py fill_variables()
# ─────────────────────────────────────────────────────────
# [BUSINESS_NAME]      e.g.  Mississauga Plumbing Services
# [PHONE]              e.g.  (647) 550-4003
# [PHONE_DIGITS]       e.g.  16475504003
# [CITY]               e.g.  Mississauga
# [CITY_PROVINCE]      e.g.  Mississauga, ON
# [SERVICE_AREAS]      e.g.  Mississauga, Brampton, Oakville, Burlington, Etobicoke
# [YEARS_IN_BUSINESS]  e.g.  15+
# [REVIEW_COUNT]       e.g.  166
# [RATING_STRING]      e.g.  ⭐⭐⭐⭐⭐ 4.9/5 · 166 Google Reviews
# [REVIEWS_3]          e.g.  block of 3 verbatim reviews from GBP
#
# MANUAL FILL (not in fill_variables — update by hand before pasting):
# ADDRESS              e.g.  55 Kingsbridge Garden Cir, Mississauga, ON L5R 1Y1
# EMAIL                e.g.  plumbers4mississauga@gmail.com
# GOOGLE_MAPS_URL      e.g.  https://www.google.com/maps/embed?pb=!1m18...
# ─────────────────────────────────────────────────────────
# PASTE EVERYTHING BELOW THIS LINE INTO BOLT.NEW
# ═════════════════════════════════════════════════

Build a high-converting website for a local plumbing company.
Mobile-first lead generation site. Primary goal: phone calls and form submissions.
This is an emergency trade — urgency and trust are the two emotions to trigger.

---

## BUSINESS INFO

Business name: [BUSINESS_NAME]
Phone: [PHONE]
Address: ADDRESS
Email: EMAIL
Service area: [SERVICE_AREAS]
Years in business: [YEARS_IN_BUSINESS]
Google rating: [RATING_STRING]

---

## COLOR PALETTE (do not deviate)

Primary (trust/background):  #1a3a6b  (deep navy)
Accent (emergency elements):  #e84040  (emergency red)
Accent hover:                 #c73232
Secondary button:             #1a3a6b  hover: #12285a
Body text:                    #1a1a1a
Light section background:     #f7f9fc
White:                        #ffffff

RULE: Navy = trust. Red = emergency only. Never use blue as emergency color.
RULE: Never use purple — it is Tailwind's default and signals generic AI output.
Red is used ONLY on: emergency CTAs, 24/7 badges, emergency service cards 1-2.

---

## TYPOGRAPHY (Tailwind classes)

Hero headline:   text-4xl md:text-6xl font-black leading-tight
Section heading: text-3xl font-bold
Body:            text-base md:text-lg leading-relaxed
CTA button:      text-lg font-bold px-8 py-4 rounded-lg

---

## SECTION ORDER (exact — do not reorder)

1.  Sticky header
2.  Hero
3.  GHL voice widget placeholder
4.  Trust bar
5.  Services
6.  Why Choose Us
7.  Process (4 steps)
8.  Reviews / Testimonials
9.  GHL reviews placeholder
10. Service Areas + Map
11. Booking section
12. Contact / Quote form
13. Footer

---

## SECTION SPECIFICATIONS

### 1. STICKY HEADER
- Logo left: "[BUSINESS_NAME]" with wrench icon
- Nav links (hidden on mobile — class="hidden md:flex"): Services | About | Areas | Book Now (anchors to #booking)
- Phone button top right: red (#e84040) background, white text, href="tel:+[PHONE_DIGITS]" — visible on ALL screen sizes
- Missed call badge next to phone (hidden on mobile — class="hidden md:block"):
  "⚡ Missed us? We'll text you back in 60 seconds."
- MOBILE RULE: On screens < 768px, show ONLY logo + phone button. Hide nav links and missed call badge entirely.

### 2. HERO
- Background: use CSS only — no external image URLs (they are blocked at runtime in Bolt)
- Implement this exact CSS on the hero section element:
  ```css
  background-color: #1a3a6b;
  background-image:
    linear-gradient(rgba(26,58,107,0.92), rgba(26,58,107,0.92)),
    repeating-linear-gradient(
      45deg,
      rgba(255,255,255,0.03) 0px,
      rgba(255,255,255,0.03) 1px,
      transparent 1px,
      transparent 12px
    ),
    repeating-linear-gradient(
      -45deg,
      rgba(255,255,255,0.02) 0px,
      rgba(255,255,255,0.02) 1px,
      transparent 1px,
      transparent 12px
    );
  ```
- Add an inline SVG wrench icon (white, 120px, opacity 0.06) absolutely positioned bottom-right as watermark
- Do NOT use any external image URL — Bolt's CSP blocks them at runtime
- Headline: "Plumbing Emergency in [CITY]? We Arrive in 60 Minutes."
  font-black, white text, 4xl mobile / 6xl desktop
- Subheadline: "[RATING_STRING] • Serving [CITY_PROVINCE] and surrounding areas"
- Two CTA buttons:
  - Primary (red #e84040): "📞 Call Now — 24/7 Emergency Service" href="tel:+[PHONE_DIGITS]"
  - Secondary (white outline): "Get a Free Quote" scrolls to #contact
- Badge row below buttons:
  "🔒 Licensed & Insured  •  [RATING_STRING]  •  ⚡ 24/7 Emergency Available"

### 3. GHL VOICE WIDGET PLACEHOLDER
- id="ghl-voice-inline"
- Background: #f5f5f5, dashed border #cccccc, padding 20px, border-radius 8px
- Centered text: "🎙️ Voice AI Widget — activates after GHL setup"
- <!-- GHL: paste voice AI widget snippet here -->

### 4. TRUST BAR
4 items in a row (icon + title + subtitle):
1. ⚡ Available 24/7         — "Emergency service, including holidays"
2. ✅ Licensed & Insured     — "Fully certified and covered"
3. ⏱️ Arrive in 60 Minutes  — "Fast dispatch, every time"
4. 📋 Free Estimates         — "No obligation quotes"

### 5. SERVICES
8 cards in a grid (4 col desktop / 2 col tablet / 1 col mobile).
Cards 1-2: red (#e84040) icon accent. Cards 3-8: navy (#1a3a6b) icon accent.
Card hover: transform translateY(-4px), box-shadow increase, transition 0.2s.

Card order (emergency first):
1. 🚨 Emergency Plumbing         — Burst pipes, floods, no hot water — fast response, 24/7
2. 🚿 Drain Cleaning              — Kitchen, bathroom, floor drains, hydro jetting
3. 🔍 Leak Detection & Repair    — Water line leaks, hidden leaks, pipe repair
4. 🔥 Water Heater Services      — Install, repair, replace, tank and tankless
5. 🪠 Toilet & Faucet Repair     — Running toilets, dripping faucets, fixture replacement
6. 💧 Sump Pump Services         — Installation, maintenance, backup systems
7. 🔧 Pipe Repair & Replacement  — Old pipes, frozen pipes, repiping
8. 🏠 Bathroom & Kitchen Plumbing — Renovation plumbing, fixture installs

Mid-page phone CTA below services grid:
"📞 Call [PHONE] for Service" — red button, href="tel:+[PHONE_DIGITS]"

### 6. WHY CHOOSE US
3 columns with icons:
1. ⚡ Fast Emergency Response
   "We dispatch within 30 minutes. Plumbing emergencies can't wait."
2. 💯 Upfront Pricing
   "No surprises. We give you the price before we start — guaranteed."
3. 🏆 [YEARS_IN_BUSINESS] Years of Local Experience
   "Trusted by homeowners in [CITY] for over [YEARS_IN_BUSINESS] years."

### 7. PROCESS (4 steps)
Step 1: "Call or Text Us"          — "Available 24/7 including holidays"
Step 2: "Fast Arrival"             — "Our team arrives in 60 minutes or less"
Step 3: "Diagnose & Fix"           — "Upfront pricing before any work begins"
Step 4: "Satisfaction Guaranteed"  — "We're not done until you're 100% happy"

### 8. REVIEWS / TESTIMONIALS
Heading: "What Our Customers Say" + [RATING_STRING]
Display these 3 verbatim reviews as quote cards (★★★★★ | quote | — Google Reviewer):
[REVIEWS_3]
"Read all [REVIEW_COUNT] reviews on Google →" link below cards

### 9. GHL REVIEWS PLACEHOLDER
Full width below review cards:
- id="ghl-reviews", min-height: 200px, dashed border
- Centered text: "Live Google Reviews load here (GHL embed)"
- <!-- GHL: paste reviews widget snippet here -->

### 10. SERVICE AREAS
Heading: "Proudly Serving [CITY] and Surrounding Communities"
- Google Maps iFrame src: GOOGLE_MAPS_URL, zoom level 13
- Neighborhood list: [SERVICE_AREAS]
- "Not sure if we cover your area? Give us a call."
- Phone CTA button: href="tel:+[PHONE_DIGITS]"

### 11. BOOKING SECTION (id="booking")
Heading: "Schedule Non-Emergency Plumbing Service"
Subtext: "For emergencies, call [PHONE] — we answer 24/7."
GHL calendar placeholder:
- id="ghl-calendar", min-height: 150px, dashed border
- Centered text: "Booking Calendar loads here (GHL embed)"
- <!-- GHL: paste calendar snippet here -->

### 12. CONTACT / QUOTE FORM (id="contact")
Heading: "Get Your Free Quote"
Subtext: "Fill out the form and we'll call you within 2 hours."
GHL form placeholder:
- id="ghl-contact-form", min-height: 150px, dashed border
- Centered text: "Contact Form loads here (GHL embed)"
- <!-- GHL: paste contact form snippet here -->

### 13. FOOTER
4 columns, dark navy background (#1a3a6b), white text:
Col 1: [BUSINESS_NAME] + tagline: "Your trusted plumbing experts in [CITY_PROVINCE]"
Col 2: Contact Us
  - Phone as tap-to-call: href="tel:+[PHONE_DIGITS]", white underline
  - Email: EMAIL
Col 3: Location
  - ADDRESS
Col 4: Hours
  - "24/7 Emergency Service" in red (#e84040)
  - "Mon–Sun: 7:00 AM – 9:00 PM"
  - "Emergency calls: Anytime"
  - Pay Invoice button: id="ghl-payment-link"
  - <!-- GHL: paste payment link snippet here -->

Copyright: "© [CURRENT_YEAR] [BUSINESS_NAME]. All rights reserved. • Licensed & Insured • Serving the GTA"
Use JavaScript for year: document.write(new Date().getFullYear()) — never hardcode.

---

## GHL PLACEHOLDER CHECKLIST
(All 6 must be present before first publish)

| ID                | Location                        | Comment label                   |
|-------------------|---------------------------------|---------------------------------|
| ghl-voice-inline  | Between Hero and Trust Bar      | paste voice AI widget snippet   |
| ghl-calendar      | Booking section (id="booking")  | paste calendar snippet          |
| ghl-reviews       | Below testimonial cards         | paste reviews widget snippet    |
| ghl-contact-form  | Contact section (id="contact")  | paste contact form snippet      |
| ghl-payment-link  | Footer Pay Invoice button       | paste payment link snippet      |
| ghl-chat-widget   | Last div before </body>         | paste chat/voice widget snippet |

Add this exactly before </body>:
<div id="ghl-chat-widget" style="min-height:0; height:0; padding:0; margin:0; line-height:0; font-size:0;"></div>
<!-- GHL: paste chat/voice widget snippet here -->

---

## TECHNICAL REQUIREMENTS

- Stack: React + Tailwind CSS
- Mobile-first — perfect at 390px iPhone width
- ALL phone instances must use href="tel:+[PHONE_DIGITS]" — no exceptions
- Page title: "[BUSINESS_NAME] | 24/7 Emergency Plumber | [PHONE]"
- Meta description: "Licensed plumbers in [CITY]. [YEARS_IN_BUSINESS] years experience, 24/7 emergency service, free estimates. Call [PHONE]"
- OG tags: og:title, og:description, og:image=/og-image.jpg, og:type=website
- Create plumbing wrench SVG at /public/favicon.svg — link in index.html
- Do NOT include bolt.new badge script in index.html
- No blank space below footer
- Animations: subtle fade-in on scroll only — no heavy effects

---

## PRE-PUBLISH VERIFICATION CHECKLIST

- [ ] All 6 GHL placeholder IDs present and labeled with HTML comments
- [ ] All phone links use href="tel:+[PHONE_DIGITS]"
- [ ] Hero has dark navy CSS background — not flat colour, not external image
- [ ] Red accent (#e84040) used only on emergency elements
- [ ] No purple anywhere — if present, remove immediately
- [ ] Process section (4 steps) present
- [ ] Booking heading says "Non-Emergency" with phone fallback
- [ ] "Book Now" nav link anchors to #booking
- [ ] Missed call badge hidden on mobile (class="hidden md:block")
- [ ] Footer Pay Invoice button present with id="ghl-payment-link"
- [ ] Maps iframe present in Service Areas section
- [ ] No bolt.new badge script in index.html
- [ ] No blank space below footer

Deploy to bolt.host when complete.
