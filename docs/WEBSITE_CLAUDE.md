# CLAUDE.md — Website Project Rules
# Copy this file into every new client website folder.
# Claude Code reads this before every action in this project.
# Last updated: April 2026 — v4 (niche palette extended to match SKILL.md v12 trades)

---

## PROJECT CONTEXT

This is a local home service business website built for a digital agency.
Goal: high-converting lead generation site with GHL automation placeholders.
The site will be handed off to GHL once client signs.

---

## OUTPUT FORMAT

- Single file: index.html
- ALL CSS inline in <style> tag
- ALL JS inline in <script> tag before </body>
- No React, no Vite, no npm, no build step required
- Mobile-first: design at 390px, scale up to desktop

---

## MANDATORY FIRST STEPS (before writing any code)

1. Read the prompt — find the line that says exactly:
      PAGE_MODE: multi
   OR:
      PAGE_MODE: single

   This is the ONLY signal that determines which mode to build.
   Do NOT infer mode from page count, PROPOSED list, or anything else.
   Do NOT build multi-page if PAGE_MODE says single.
   Do NOT build single-page if PAGE_MODE says multi.

2. If PAGE_MODE: multi — find the PROPOSED: line.
   Build exactly those pages in that order. No additions, no removals.

3. Create screenshots/ folder:
      mkdir screenshots

---

## CSS PRE-HIDE RULE — ADD FIRST (multi-page only)

If PAGE_MODE is multi, add this at the TOP of your <style> block,
before any other CSS. This prevents page flash before JS fires.

```css
.page { display: none; }
#page-home { display: block; }
```

---

## PAGE MODE A — SINGLE PAGE

Trigger: prompt contains PAGE_MODE: single

Build one continuous scrollable page. No routing. No .page divs.

SECTION ORDER (do not reorder):
  1.  Sticky header
  2.  Hero
  3.  GHL voice widget placeholder
  4.  Trust bar
  5.  Services grid
  6.  Why Choose Us
  7.  How It Works (4 steps)
  8.  Reviews (3 cards + star rating)
  9.  GHL reviews placeholder
  10. Service Areas + Google Maps iFrame
  11. Booking (id="booking")
  12. Contact form (id="contact") + GHL form placeholder
  13. Footer + GHL chat widget

---

## PAGE MODE B — MULTI-PAGE WITH HASH ROUTING

Trigger: prompt contains PAGE_MODE: multi

Build each PROPOSED page as a FULLY DESIGNED standalone page inside one HTML file.
Use hash-based JS routing so the Back button works and pages are shareable.


### ANTI-DUPLICATION RULE

Do NOT copy layout blocks from Home onto other pages.
Each page must feel designed for its own purpose.

Wrong: Services page = Home page with different text
Right: Services page has service cards, process steps, pricing callout

Unique elements required per page:
  Home     — star rating in hero, trust bar, services overview, reviews section
  Services — service cards grid, How It Works steps, pricing/estimate callout
  About    — founding story, stats row, team, certifications
  Reviews  — 3 full review cards, GHL reviews widget, 'Leave a review' CTA
  Contact  — GHL form, click-to-call, map, hours, emergency CTA


### ROUTING IMPLEMENTATION

Paste this full JS block in <script> before </body>:

```javascript
function showPage(pageId) {
  // Hide all pages
  document.querySelectorAll('.page').forEach(function(p) {
    p.style.display = 'none';
    p.setAttribute('aria-hidden', 'true');
  });

  // Show target page
  var target = document.getElementById('page-' + pageId);
  if (!target) { showPage('home'); return; }
  target.style.display = 'block';
  target.setAttribute('aria-hidden', 'false');

  // Update nav active state + accessibility
  document.querySelectorAll('.nav-link').forEach(function(l) {
    l.classList.remove('active');
    l.removeAttribute('aria-current');
  });
  var activeLink = document.querySelector('[data-page="' + pageId + '"]');
  if (activeLink) {
    activeLink.classList.add('active');
    activeLink.setAttribute('aria-current', 'page');
  }

  // Update page title
  var pageName = activeLink ? activeLink.textContent.trim() : pageId;
  var siteName = document.title.split(' | ').pop().trim();
  document.title = pageName + ' | ' + siteName;

  // Update URL hash (enables Back button + shareable links)
  if (window.location.hash !== '#' + pageId) {
    history.pushState(null, '', '#' + pageId);
  }

  // Move focus to H1 for screen readers
  var heading = target.querySelector('h1');
  if (heading) { heading.setAttribute('tabindex', '-1'); heading.focus(); }

  window.scrollTo(0, 0);
}

function loadFromHash() {
  var hash = window.location.hash.replace('#', '');
  var pages = Array.from(document.querySelectorAll('.page'))
                   .map(function(p) { return p.id.replace('page-', ''); });
  if (hash && pages.indexOf(hash) !== -1) {
    showPage(hash);
  } else {
    showPage('home');
  }
}

document.addEventListener('DOMContentLoaded', loadFromHash);
window.addEventListener('popstate', loadFromHash);
window.addEventListener('hashchange', loadFromHash);  // CRITICAL — handles nav link clicks
```

Note: uses history.pushState for Back button support.
- popstate handles Back/Forward navigation
- hashchange handles nav link clicks (href="#page-id")
- DOMContentLoaded handles direct URL loads (index.html#services)


### NAV LINK TEMPLATE

```html
<a href="#[page-id]" class="nav-link" data-page="[page-id]">[Page Name]</a>
```

href="#[page-id]" is the click handler — no onclick needed.
The hashchange/popstate listener handles routing automatically.

Page ID slugging — convert PROPOSED label to lowercase-hyphenated:
  Home         → home
  Services     → services
  About        → about
  Our Work     → our-work
  Reviews      → reviews
  Contact      → contact
  FAQ          → faq
  Service Area → service-area
  Financing    → financing


### PAGE WRAPPER TEMPLATE

```html
<div class="page" id="page-[page-id]" aria-hidden="true">
  <main>
    <h1>[Page Headline]</h1>
    <!-- Rest of page content -->
  </main>
</div>
```

Every .page div must have aria-hidden="true" (toggled by JS to false when shown).
Every page must start with an H1 — required for focus management.


### SHARED HEADER (appears once, above all .page divs)

```html
<header class="sticky-header" id="site-header" role="banner">
  <div class="header-inner">
    <a href="#home" class="logo" data-page="home">[BUSINESS_NAME]</a>
    <nav role="navigation" aria-label="Main navigation">
      <!-- One nav-link per PROPOSED page, in PROPOSED order -->
    </nav>
    <a href="tel:+1[PHONE_DIGITS]" class="header-cta">[PHONE]</a>
  </div>
</header>
```


### SHARED FOOTER (appears once, after all .page divs)

```html
<footer role="contentinfo">
  <div class="footer-inner">
    <div>[BUSINESS_NAME] | [PHONE] | [CITY_PROVINCE]</div>
    <nav aria-label="Footer navigation"><!-- same links as header --></nav>
    <div>© <span id="year"></span> [BUSINESS_NAME]. All rights reserved.</div>
    <div id="ghl-payment-link" style="border:2px dashed #ccc;padding:12px;margin-top:12px;">
      <!-- GHL: paste Pay Invoice link here -->
      [Pay Invoice — GHL Payment Widget]
    </div>
  </div>
</footer>
<div id="ghl-chat-widget" style="border:2px dashed #ccc;padding:8px;">
  <!-- GHL: paste chat widget snippet here -->
  [Live Chat — GHL Chat Widget]
</div>
```

---

## COLOR RULES

Read the BRAND COLORS block in the Layer 2 prompt. Priority order:

1. BRAND_COLORS non-empty in prompt:
   - First color  → PRIMARY (nav bg, headings, button fills, footer bg)
   - Second color → ACCENT (CTAs, phone buttons, hover, badges)
   - Apply these. Override all niche defaults below.

2. BRAND_COLORS empty:
   - Use niche default palette:

   Plumbing     → #1a3a6b primary + #e84040 accent
   HVAC         → #2c4a7c primary + #e87d2a accent
   Electrical   → #1a1a2e primary + #f5c518 accent
   Roofing      → #5c3d2e primary + #c0392b accent
   Landscaping  → #2d6a4f primary + #e9c46a accent
   Cleaning     → #0077b6 primary + #ffffff accent
   Pest Control → #386641 primary + #bc4749 accent
   Painting     → #2b4590 primary + #e8a838 accent
   Glass        → #1b3a57 primary + #7dd3fc accent
   Garage Door  → #2f2f2f primary + #d4a017 accent
   Generic      → #1a3a6b primary + #e84040 accent

Body text: #1a1a1a
Section bg (alternating): #f7f9fc
Cards/inputs: #ffffff

NEVER use purple. Purple = generic AI output. Remove it if you see it.

---

## PHONE NUMBER RULE

Every phone number on every page: href="tel:+1[PHONE_DIGITS]"
No exceptions. Plain-text phone numbers with no tel: link = failure.

---

## GOOGLE REVIEWS LINK RULE

Every instance of a Google reviews reference must be a clickable link.
This includes: star rating badges, "X Google Reviews" text, "Read all reviews on Google" links,
review count in hero subheadline, and any other mention of Google reviews.

Use this URL everywhere:  [GOOGLE_REVIEWS_URL]

Examples:
  CORRECT:  <a href="[GOOGLE_REVIEWS_URL]" target="_blank" rel="noopener">5★ (247 Google Reviews)</a>
  CORRECT:  <a href="[GOOGLE_REVIEWS_URL]" target="_blank" rel="noopener">Read all 247 reviews on Google →</a>
  WRONG:    <span>5★ (247 Google Reviews)</span>  ← not clickable, failure

Every review card star rating must also link to [GOOGLE_REVIEWS_URL].
All review links must open in a new tab: target="_blank" rel="noopener"

---

## GHL PLACEHOLDER RULE

All 6 GHL placeholders required. Place on the correct page in multi-page mode:

  id="ghl-voice-inline"  → Home page, between hero and trust bar
  id="ghl-reviews"       → Home OR Reviews page, below the 3 static review cards
  id="ghl-contact-form"  → Contact page — this is the PRIMARY lead capture element
  id="ghl-calendar"      → Contact page, below the contact form
  id="ghl-payment-link"  → Footer template (already shown above)
  id="ghl-chat-widget"   → After footer template (already shown above)

Each placeholder must have:
  - style="border:2px dashed #cccccc; padding:16px;"
  - Descriptive label text: "[Widget name] — paste GHL embed here"
  - HTML comment: <!-- GHL: paste [type] snippet here -->

Star ratings in review cards are STATIC and DECORATIVE.
Do NOT add any Google API calls, Places API, or live review embeds.

---

## SCREENSHOT LOOP RULE

After writing Home page (or section), Services page, and Contact page:
  - Screenshot at 390px width via Puppeteer
  - Check: purple colors, overflow, phone buttons, routing, GHL placeholders
  - Verify Back button navigates correctly (hash routing)
  - Fix issues before continuing
  - Save to screenshots/

---

## CODE QUALITY RULES

- html { scroll-behavior: smooth; }
- Year: document.getElementById('year').textContent = new Date().getFullYear();
- Sticky header box-shadow on scroll:
    window.addEventListener('scroll', function() {
      document.getElementById('site-header').style.boxShadow =
        window.scrollY > 10 ? '0 2px 12px rgba(0,0,0,0.12)' : 'none';
    });
- Multi-page fade-in: add transition: opacity 0.2s to .page, set opacity 0
  then 1 after display block in showPage()
- No Lorem Ipsum
- No external image URLs (blocked in demo environments)
- No blank space below footer
- No builder badge scripts in <head>

---

## DEPLOY CHECKLIST

  [ ] PAGE_MODE correctly read from prompt — multi or single
  [ ] CSS pre-hide added (.page display:none, #page-home display:block)
  [ ] All 6 GHL placeholder IDs on correct pages
  [ ] All phone numbers use tel: href
  [ ] No purple colors
  [ ] Sticky header box-shadow on scroll
  [ ] Back button works (history.pushState + popstate)
  [ ] index.html#services loads correct page directly
  [ ] aria-hidden toggled correctly on page switch
  [ ] Mobile layout correct at 390px
  [ ] No blank space below footer
  [ ] Year dynamic
  [ ] No builder badge in source
  [ ] No Lorem Ipsum
  [ ] No Google API calls for reviews

---

## DEPLOY COMMANDS

Demo (prospect):
  Drag index.html to netlify.com/drop
  Share as: https://[netlify-url] (loads Home)
  Share specific page: https://[netlify-url]#services

Production (after client signs):
  git push to GitHub → connect Vercel → auto-deploys

---

## TRIAGE_META Schema (v1.0)

TRIAGE_META is the machine-readable sidecar footer that every website-sales-audit
report ends with. It is the **contract** between the emitter
(website-sales-audit, via docs/SKILL.md) and the consumers
(website-audit-builder's parse_audit.py and ghl-triage's audit_parser.py). Any
change to this schema requires bumping `schema_version` and updating parsers in
both downstream repos.

The block is a fenced code block with the language identifier `triage-meta`,
containing YAML. It is appended AFTER the four narrative sections and must be
the last content in the audit file.

### Fields

| Field | Type | Allowed values / meaning |
|---|---|---|
| `schema_version` | string | Current version: `"1.0"`. Bump on any breaking change. |
| `audit_generated_at` | string | ISO 8601 UTC timestamp of when the audit was written. |
| `business_name` | string \| null | Business name as identified in the audit. `null` if unknown. |
| `business_url` | string \| null | Input URL, normalized: lowercase host, no trailing slash. `null` if unknown. |
| `trade` | enum \| null | One of: `plumbing`, `hvac`, `cleaning`, `landscaping`, `electrical`, `pest_control`, `painting`, `garage_door`, `roofing`, `glass`, `other`. |
| `ghl_upgrade_candidate` | bool \| null | `true` ONLY if the prospect is currently running a CRM, booking, or communications platform that GHL would replace in a lateral migration. See expanded definition below. |
| `mctb_applicable` | bool \| null | `true` if missed-call-text-back would meaningfully lift their phone/lead flow. |
| `vaai_applicable` | bool \| null | `true` if a voice AI agent fits their call volume and after-hours pattern. |
| `disqualifiers` | list of strings | Known disqualifiers detected. Empty list `[]` if none. |

Unknown fields are represented as `null` (not empty string, not omitted).

### `ghl_upgrade_candidate` — expanded definition

The word "upgrade" here means **lateral migration**, not "first-time sale." A
first-time GHL sale to a greenfield prospect follows a different triage path
downstream — do not conflate the two.

Set **`true`** only if the prospect is currently running one of these
platforms (or another comparable one) that GHL would directly replace:

- HubSpot
- Keap / Infusionsoft
- Salesforce Essentials
- ActiveCampaign
- ServiceTitan
- Housecall Pro
- Jobber (with communications tier)
- Podium
- Thryv

Set **`false`** for:

- Greenfield prospects — no CRM at all, or only Google Workspace + a basic
  website + a phone
- Prospects with major problems we can solve but no existing platform to
  migrate FROM (first-time buyer, not an upgrade)
- Solo operators running the business from a phone and a WordPress site

### Allowed `disqualifiers` values

- `national_chain` — franchise/enterprise, not SMB
- `under_construction` — site is a placeholder
- `out_of_service_area` — not US/Canada
- `wrong_trade` — not one of the home service trades listed above
- `dead_site` — domain resolves but site 404s or is parked

### Example

```triage-meta
schema_version: "1.0"
audit_generated_at: "2026-04-16T21:30:00Z"
business_name: "Mississauga Plumbing Services"
business_url: "https://mississaugaplumbingservices.com"
trade: plumbing
ghl_upgrade_candidate: false
mctb_applicable: true
vaai_applicable: true
disqualifiers: []
```

### Schema evolution

- Additive non-breaking changes (e.g. new optional field with a safe default):
  keep `schema_version: "1.0"`.
- Breaking changes (removed field, changed type, new required field without a
  safe default): bump to `"1.1"` or `"2.0"` and update both consumer parsers
  before rolling out the new emitter.
