#!/usr/bin/env python3
from __future__ import annotations
"""
findings_to_layer2.py
Translates parsed audit findings into Layer 2 prompt instructions.

This is the core of the new system — the missing link between audit and generation.

Architecture:
  Layer 1: universal_rules.txt  — global rules for every site (unchanged)
  Layer 2: THIS MODULE          — rules derived from THIS prospect's audit findings
  Layer 3: niches/[trade].md    — trade-specific rules (unchanged)

Layer 2 precedence: L2 overrides L3 which overrides L1.
Audit-specific findings are the most specific data and always win.

Each area (1–10) has:
  - A base rule set that fires when the area is rated ❌ or ⚠️
  - Severity-specific additions (❌ is stronger than ⚠️)
  - The "What a new site would do" text from the audit, quoted verbatim
    as a design brief (this is already perfect generation language)
  - Specific technical instructions derived from the finding type
"""


# ── Area → base rules mapping ─────────────────────────────────────────────────
# Each entry maps area_key → callable that takes (area_dict, business_data) → str

def rules_first_impressions(area: dict, biz: dict) -> str:
    rating = area["rating"]
    if rating == "✅":
        return ""
    lines = ["AREA 1 — FIRST IMPRESSIONS (audit finding: {})".format(rating)]

    if rating == "❌":
        lines += [
            "- The current site is dated/low-quality — the new site must look modern, clean, and premium from the first second",
            "- Professional layout: generous whitespace, consistent typography, clear visual hierarchy",
            "- Business name and trade ('plumber', 'HVAC', etc.) and city must be in the H1 or subtitle — immediately visible",
            "- Phone number visible without scrolling in sticky header — this is non-negotiable",
            "- No builder badges, no Gmail addresses, no free-tier platform branding anywhere in the HTML",
            "- Copyright footer must use dynamic year: {new Date().getFullYear()}",
            "- If the audit found SiteBuilder/Wix/Weebly/Google Sites: the new site must look dramatically better than what was there",
        ]
    elif rating == "⚠️":
        lines += [
            "- Improve design quality over current site — cleaner layout, better visual hierarchy",
            "- Ensure phone number is prominent without scrolling",
            "- Remove any builder branding from HTML output",
        ]

    if area.get("action"):
        lines.append(f"- DESIGN BRIEF (from audit): {area['action']}")

    return "\n".join(lines)


def rules_mobile_experience(area: dict, biz: dict) -> str:
    rating = area["rating"]
    if rating == "✅":
        return ""
    lines = ["AREA 2 — MOBILE EXPERIENCE (audit finding: {})".format(rating)]

    if rating in ("❌", "⚠️"):
        lines += [
            "- MOBILE-FIRST: design at 390px width first, then scale to desktop",
            "- All phone numbers must use href=\"tel:+1{PHONE_DIGITS}\" — tap-to-call on first tap",
            "- Phone button must be visible without scrolling on 390px viewport",
            "- No horizontal scroll at any screen width",
            "- Sticky header stays visible during scroll on mobile",
            "- Buttons and links must be thumb-sized (min 44px tap target)",
            "- No table-based layouts — use CSS flexbox/grid",
            "- Fast loading: no video backgrounds, no heavy JS loading content, compress all images",
        ]
        if rating == "❌":
            lines += [
                "- The audit found the current site fails on mobile — the new site must be demonstrably better",
                "- Test at exactly 390px (iPhone standard) — nothing should overflow or be cut off",
            ]

    if area.get("action"):
        lines.append(f"- MOBILE BRIEF (from audit): {area['action']}")

    return "\n".join(lines)


def rules_contact_booking(area: dict, biz: dict) -> str:
    rating = area["rating"]
    if rating == "✅":
        return ""
    lines = ["AREA 3 — CONTACT & BOOKING (audit finding: {})".format(rating)]

    if rating in ("❌", "⚠️"):
        lines += [
            "- GHL contact form placeholder MUST be present and prominent",
            "- GHL booking calendar placeholder MUST be present",
            "- Response promise visible near form: 'We respond within 2 hours'",
            "- Phone number as alternative contact clearly stated near form",
        ]
        if rating == "❌":
            lines += [
                "- The current site has NO quote form — the new site must make requesting a quote extremely easy",
                "- For urgent trades: emergency/24-hour contact path must be visible on every page",
                "- After-hours: GHL chat widget placeholder must be present so visitors can leave info outside business hours",
                "- 'Contact Me' is wrong — use 'Contact Us' or 'Get a Free Quote'",
                "- Do NOT use mailto: links — GHL form placeholder only",
            ]

    # Extract specific gaps from audit finding
    found = area.get("found", "")
    if "24/7" in found or "emergency" in found.lower():
        lines.append("- Emergency/24-hour service must be explicitly visible — not hidden in a subpage")
    if "hours" in found.lower():
        lines.append("- Business hours must be stated clearly — preferably in the footer and contact section")

    if area.get("action"):
        lines.append(f"- CONTACT BRIEF (from audit): {area['action']}")

    return "\n".join(lines)


def rules_local_presence(area: dict, biz: dict) -> str:
    rating = area["rating"]
    if rating == "✅":
        return ""
    lines = ["AREA 4 — LOCAL PRESENCE (audit finding: {})".format(rating)]

    if rating in ("❌", "⚠️"):
        lines += [
            "- City/province ([CITY_PROVINCE]) must appear in: H1 or hero subtitle, service areas section, footer, page title meta tag",
            "- Service areas section MUST list specific neighborhood names — never 'Greater Area' or 'Metro Region'",
            "- Use [SERVICE_AREAS] variable for neighborhood list — if empty, prompt user to fill in",
            "- Google Maps iFrame must be embedded in service areas section",
            "- Local phone number in header (not 1-800)",
        ]
        if rating == "❌":
            lines.append("- The audit found poor local presence — city name and specific neighborhoods are critical to fix")

    if area.get("action"):
        lines.append(f"- LOCAL BRIEF (from audit): {area['action']}")

    return "\n".join(lines)


def rules_trust_credibility(area: dict, biz: dict) -> str:
    rating = area["rating"]
    if rating == "✅":
        return ""
    lines = ["AREA 5 — TRUST & CREDIBILITY (audit finding: {})".format(rating)]

    found = area.get("found", "")

    # Review-specific rules (most impactful)
    has_reviews = "[REVIEW_COUNT]" or "reviews" in found.lower()

    if rating == "❌":
        lines += [
            "- CRITICAL: Reviews are hidden on the current site — this site MUST display them prominently",
            "- Hero subheadline MUST include: [RATING_STRING] (star rating + review count)",
            "- Dedicated reviews section with 3 verbatim quote cards from [REVIEWS_3]",
            "- 'Read all [REVIEW_COUNT] reviews on Google →' link below review cards",
            "- GHL reviews widget placeholder below the static review cards",
            "- Trust bar (immediately after hero): 4 items including ✅ Licensed & Insured",
            "- 'Licensed & Insured' statement must appear in trust bar — not just in footer",
            "- Years in business ([YEARS_IN_BUSINESS]) must be stated — hero badge row or trust bar",
            "- Real team/truck/job photos strongly preferred over stock — see Area 8",
        ]
    elif rating == "⚠️":
        lines += [
            "- Improve trust signals: add review count to hero, add Licensed & Insured to trust bar",
            "- Hero subheadline: include [RATING_STRING]",
            "- Reviews section with at least 3 quote cards from [REVIEWS_3]",
        ]

    # Check for specific trust items mentioned in audit
    if "homestars" in found.lower():
        lines.append("- Mention HomeStars rating if available (Canadian market trust signal)")
    if "guarantee" in found.lower() or "warranty" in found.lower():
        lines.append("- Add guarantee/warranty statement to trust bar or below CTA buttons")

    if area.get("action"):
        lines.append(f"- TRUST BRIEF (from audit): {area['action']}")

    return "\n".join(lines)


def rules_content_clarity(area: dict, biz: dict) -> str:
    rating = area["rating"]
    if rating == "✅":
        return ""
    lines = ["AREA 6 — CONTENT CLARITY (audit finding: {})".format(rating)]

    found = area.get("found", "")

    if rating in ("❌", "⚠️"):
        lines += [
            "- All content must be in real semantic HTML text — NO JavaScript-loaded content",
            "- Use h1, h2, h3, section, article, nav elements — Google must be able to read every word",
            "- Services section: each service must have a name AND a 1-line description (not just a title)",
            "- Services pulled from [SERVICES_LIST] — if empty, use niche file defaults",
            "- Page title meta tag: '[BUSINESS_NAME] | [Trade] in [CITY_PROVINCE]'",
            "- Meta description: '[BUSINESS_NAME] — [trade] in [CITY_PROVINCE]. [RATING_STRING]. Call [PHONE].'",
        ]
        if rating == "❌":
            lines += [
                "- The current site loads via JavaScript — Google literally cannot read it",
                "- React/Tailwind output must have semantic HTML structure that degrades gracefully without JS",
                "- Every service from [SERVICES_LIST] must appear as real readable text in the HTML",
            ]
        if "can't" in found.lower() or "cannot" in found.lower():
            lines.append("- CRITICAL: Google currently cannot read this site's content — semantic HTML is the #1 fix")

    if area.get("action"):
        lines.append(f"- CONTENT BRIEF (from audit): {area['action']}")

    return "\n".join(lines)


def rules_speed(area: dict, biz: dict) -> str:
    rating = area["rating"]
    if rating == "✅":
        return ""
    lines = ["AREA 7 — SPEED (audit finding: {})".format(rating)]

    if rating in ("❌", "⚠️"):
        lines += [
            "- NO video backgrounds — they are the #1 performance killer on mobile",
            "- No heavy third-party scripts in <head> — defer everything possible",
            "- Images: use modern formats, add loading='lazy' to all below-fold images",
            "- Hero: use a CSS gradient or lightweight texture instead of a full-bleed photo if no real photos available",
            "- Minimise JavaScript — content must be visible before JS executes",
            "- No animations that block rendering (IntersectionObserver is fine for reveal effects)",
        ]
        if rating == "❌":
            lines += [
                "- The current site is slow due to JS-only content loading — the new site must load in under 2 seconds on mobile",
                "- Vite/React build will be optimised — do not add anything that undoes that (no jQuery, no large icon libraries)",
            ]

    if area.get("action"):
        lines.append(f"- SPEED BRIEF (from audit): {area['action']}")

    return "\n".join(lines)


def rules_photos(area: dict, biz: dict) -> str:
    rating = area["rating"]
    if rating == "✅":
        return ""
    lines = ["AREA 8 — PHOTOS & VISUAL AUTHENTICITY (audit finding: {})".format(rating)]

    if rating in ("❌", "⚠️"):
        lines += [
            "- Style all photo slots to accept real team/truck/job photos (not stock images)",
            "- Add HTML comments on every photo slot: <!-- Replace with real photo of [team/truck/job] -->",
            "- If LOGO_URL is available from extraction: use it in header",
            "- If PHOTO_URLS are available from extraction: use them in services/gallery sections",
            "- Hero background: use real photo if available, otherwise navy gradient (#1a3a6b) — never generic stock",
            "- Services cards: use trade-appropriate icons (not generic stock photos of strangers)",
        ]
        if rating == "❌":
            lines.append("- The audit could not confirm whether current photos are real — new site must be built for real photo insertion")

    found = area.get("found", "")
    if "instagram" in found.lower() or "facebook" in found.lower():
        lines.append("- NOTE from audit: prospect has social media presence suggesting real photos exist — flag in output to download and use them")

    if area.get("action"):
        lines.append(f"- PHOTOS BRIEF (from audit): {area['action']}")

    return "\n".join(lines)


def rules_security(area: dict, biz: dict) -> str:
    rating = area["rating"]
    if rating == "✅":
        return ""
    lines = ["AREA 9 — SITE SECURITY (audit finding: {})".format(rating)]

    if rating == "❌":
        lines += [
            "- Current site has SSL/security errors — this is catastrophic for trust",
            "- New site hosted on Netlify: HTTPS is automatic and error-free — this issue is resolved by deployment",
            "- No mixed content (HTTP resources on HTTPS page) — all external scripts must use https://",
            "- Contact form must look trustworthy — no broken elements, no error states on load",
        ]
    elif rating == "⚠️":
        lines += [
            "- Ensure HTTPS on all pages — Netlify handles this automatically",
            "- No mixed content warnings",
        ]

    found = area.get("found", "")
    if "525" in found or "ssl" in found.lower() or "handshake" in found.lower():
        lines.append("- Audit found SSL handshake failures on subpages — new site on Netlify resolves this completely")

    if area.get("action"):
        lines.append(f"- SECURITY BRIEF (from audit): {area['action']}")

    return "\n".join(lines)


def rules_lead_followup(area: dict, biz: dict) -> str:
    rating = area["rating"]
    if rating == "✅":
        return ""
    lines = ["AREA 10 — LEAD FOLLOW-UP SYSTEM (audit finding: {})".format(rating)]

    if rating == "❌":
        lines += [
            "- CRITICAL: Current site has NO lead capture system at all",
            "- ALL SIX GHL placeholder divs are mandatory on this site — this prospect needs all of them",
            "- GHL voice widget placeholder: between hero and trust bar",
            "- GHL booking calendar placeholder: in booking section",
            "- GHL contact form placeholder: prominent in contact section — NO mailto: links",
            "- GHL reviews widget placeholder: below static review cards",
            "- GHL payment link: in footer",
            "- GHL chat widget: last element before </body>",
            "- Response promise near contact form: 'We respond within 2 hours'",
            "- Missed call text-back badge in sticky header: 'Missed us? We\\'ll text you back in 60 seconds'",
            "- After-hours messaging: 'Can\\'t call now? Leave your info and we\\'ll text you back'",
        ]
    elif rating == "⚠️":
        lines += [
            "- Lead capture needs improvement — all 6 GHL placeholder divs required",
            "- Add response promise near contact form",
            "- Add missed call text-back badge to header",
        ]

    found = area.get("found", "")
    if "no form" in found.lower() or "no contact form" in found.lower():
        lines.append("- No form exists on current site — GHL form placeholder is the primary CTA for leads")
    if "no booking" in found.lower() or "scheduling" in found.lower():
        lines.append("- No booking tool on current site — GHL calendar placeholder is critical for non-emergency scheduling")
    if "no chat" in found.lower() or "chat widget" in found.lower():
        lines.append("- No chat widget on current site — GHL chat placeholder captures after-hours leads")

    if area.get("action"):
        lines.append(f"- FOLLOWUP BRIEF (from audit): {area['action']}")

    return "\n".join(lines)


# ── Site structure intelligence ───────────────────────────────────────────────

def apply_structure_rules(nav_pages, subpage_content, nav_confidence="high"):
    """
    Audits detected nav pages and returns proposed page plan + change log.
    Returns {"detected", "proposed", "changes", "page_mode"}
    """
    from datetime import datetime as _dt

    def norm(s):
        return s.lower().strip()

    def _has_services(pages):
        keywords = ["service", "what we do", "solutions", "specialty", "specialties"]
        return any(any(kw in norm(p) for kw in keywords) for p in pages)

    def _has_contact(pages):
        keywords = ["contact", "reach", "get in touch", "connect", "call us"]
        return any(any(kw in norm(p) for kw in keywords) for p in pages)

    def _has_reviews(pages):
        keywords = ["review", "testimonial", "feedback", "rating", "what our"]
        return any(any(kw in norm(p) for kw in keywords) for p in pages)

    def _reviews_have_content(page_label):
        content = subpage_content.get(page_label, {})
        return (
            len(content.get("headings", [])) >= 2
            or content.get("word_count", 0) >= 50
        )

    proposed = list(nav_pages)
    changes  = []
    allow_drops = nav_confidence == "high"
    cap = 6 if nav_confidence == "high" else 8

    # MERGE: Gallery + Projects → Our Work
    has_gallery  = any(norm(p) in ("gallery", "photos", "photo gallery") for p in proposed)
    has_projects = any(norm(p) in ("projects", "our work", "portfolio", "work") for p in proposed)
    if has_gallery and has_projects:
        proposed = [p for p in proposed
                    if norm(p) not in ("gallery", "photos", "photo gallery",
                                       "projects", "portfolio", "work")]
        proposed.insert(min(2, len(proposed)), "Our Work")
        changes.append({"action": "MERGE", "page": "Gallery + Projects",
                        "result": "Our Work", "reason": "Two visual pages merged"})

    # MERGE: Team + About → About
    has_team  = any(norm(p) in ("team", "our team", "meet the team") for p in proposed)
    has_about = any("about" in norm(p) or "our story" in norm(p) for p in proposed)
    if has_team and has_about:
        proposed = [p for p in proposed
                    if norm(p) not in ("team", "our team", "meet the team")]
        changes.append({"action": "MERGE", "page": "Team + About",
                        "result": "About", "reason": "Team merged into About"})

    DROP_ALWAYS = {
        "careers", "jobs", "join us", "work with us",
        "partners", "affiliates", "vendors",
        "events", "upcoming events",
        "sitemap", "login", "sign in", "my account",
        "store", "shop", "privacy policy", "terms of service",
    }
    PRESERVE_ALWAYS = {
        "service areas", "service area", "financing", "emergency",
        "emergency service", "coupons", "specials", "offers",
        "schedule", "book online", "locations",
    }

    if allow_drops:
        for page in list(proposed):
            pn = norm(page)
            if pn in PRESERVE_ALWAYS:
                continue
            if pn in DROP_ALWAYS:
                proposed.remove(page)
                changes.append({"action": "DROP", "page": page,
                                "reason": "Not relevant for home-service lead gen"})
                continue
            # Stale blog — dynamic year (24-month window)
            if pn in ("news", "blog", "articles", "updates", "press"):
                content      = subpage_content.get(page, {})
                text         = (content.get("copy", "") + " ".join(content.get("headings", []))).lower()
                current_year = _dt.now().year
                stale_years  = [str(y) for y in range(2015, current_year - 2)]
                stale        = stale_years + ["no posts", "coming soon"]
                if any(s in text for s in stale) or content.get("word_count", 0) < 25:
                    proposed.remove(page)
                    changes.append({"action": "DROP", "page": page,
                                    "reason": "Blog/news stale or empty"})
                    continue
            # Thin gallery
            if pn in ("gallery", "photos", "photo gallery"):
                content  = subpage_content.get(page, {})
                if (len(content.get("headings", [])) < 2
                        and content.get("img_count", 0) < 4
                        and len(content.get("copy", "")) < 100):
                    proposed.remove(page)
                    changes.append({"action": "DROP", "page": page,
                                    "reason": "Gallery thin — photos moved to Home"})

    RENAME_MAP = {
        "works": "Our Work", "our work": "Our Work",
        "what we do": "Services", "our services": "Services",
        "reach us": "Contact", "contact us": "Contact",
        "get in touch": "Contact", "connect": "Contact",
        "call us": "Contact", "get a quote": "Contact",
        "who we are": "About", "our story": "About", "about us": "About",
        "testimonials": "Reviews", "client reviews": "Reviews",
        "google reviews": "Reviews", "customer reviews": "Reviews",
        "faqs": "FAQ", "faq": "FAQ",
        "service areas": "Service Areas", "areas we serve": "Service Areas",
    }
    renamed = []
    for page in proposed:
        new_name = RENAME_MAP.get(norm(page))
        if new_name and new_name != page:
            changes.append({"action": "RENAME", "page": page, "result": new_name,
                            "reason": "Clearer label for home-service buyers"})
            renamed.append(new_name)
        else:
            renamed.append(page)
    proposed = renamed

    # ADD: Services
    if not _has_services(proposed):
        proposed.insert(min(1, len(proposed)), "Services")
        changes.append({"action": "ADD", "page": "Services",
                        "reason": "No services page — critical for user intent"})

    # ADD: Contact
    if not _has_contact(proposed):
        proposed.append("Contact")
        changes.append({"action": "ADD", "page": "Contact",
                        "reason": "No contact page found"})

    # Reviews — P2-10: keep as nav page if real content, else demote to Home section
    if _has_reviews(proposed):
        reviews_page = next(
            (p for p in proposed if any(kw in norm(p) for kw in
                                        ["review", "testimonial", "rating"])),
            None
        )
        if reviews_page and not _reviews_have_content(reviews_page):
            proposed.remove(reviews_page)
            changes.append({
                "action": "DROP->Home section", "page": reviews_page,
                "reason": "Reviews page thin — adding as Home section instead"
            })
    else:
        changes.append({
            "action": "ADD (Home section)", "page": "Reviews",
            "reason": "No reviews page — adding Reviews section to Home page"
        })

    # PROMOTE — deterministic ordering
    PRIORITY_ORDER = [
        "home", "services", "our services", "our work",
        "about", "about us", "service areas",
        "reviews", "testimonials", "financing", "faq", "contact",
    ]

    def _priority(page):
        pn = norm(page)
        for i, p in enumerate(PRIORITY_ORDER):
            if p in pn or pn in p:
                return i
        return 50

    home_pages  = [p for p in proposed if norm(p) == "home"]
    other_pages = [p for p in proposed if norm(p) != "home"]
    other_pages.sort(key=_priority)
    proposed = home_pages + other_pages

    if len(proposed) > cap:
        dropped  = proposed[cap:]
        proposed = proposed[:cap]
        for d in dropped:
            changes.append({"action": "DROP", "page": d,
                            "reason": f"Trimmed to max {cap} nav pages"})

    page_mode = "multi" if len(proposed) >= 2 else "single"

    return {
        "detected":  nav_pages,
        "proposed":  proposed,
        "changes":   changes,
        "page_mode": page_mode,
    }


def rules_site_structure(business_data: dict) -> str:
    """
    Generates the SITE STRUCTURE DECISION block for Layer 2.
    Emits explicit PAGE_MODE: token consumed by WEBSITE_CLAUDE.md.
    """
    nav_pages       = business_data.get("NAV_PAGES", [])
    subpage_content = business_data.get("SUBPAGE_CONTENT", {})
    brand_colors    = business_data.get("BRAND_COLORS", "")
    nav_confidence  = business_data.get("NAV_CONFIDENCE", "high")
    niche           = business_data.get("_meta", {}).get("niche", "generic") \
                      if isinstance(business_data.get("_meta"), dict) else "generic"

    NICHE_DEFAULTS = {
        "plumbing":     "#1a3a6b, #e84040",
        "hvac":         "#2c4a7c, #e87d2a",
        "electrical":   "#1a1a2e, #f5c518",
        "roofing":      "#5c3d2e, #c0392b",
        "landscaping":  "#2d6a4f, #e9c46a",
        "cleaning":     "#0077b6, #ffffff",
        "pest_control": "#386641, #bc4749",
        "painting":     "#2b4590, #e8a838",
        "generic":      "#1a3a6b, #e84040",
    }
    niche_color_fallback = NICHE_DEFAULTS.get(niche, NICHE_DEFAULTS["generic"])

    if not nav_pages or len(nav_pages) <= 1:
        lines = [
            "━" * 72, "SITE STRUCTURE DECISION", "━" * 72,
            "DETECTED:   (nav not reliably detected — JS-rendered or blocked)",
            "PROPOSED:   Single-page scrollable layout", "",
            "PAGE_MODE: single", "",
            "Build one continuous scrollable page. No JS routing.",
        ]
        lines.append(f"BRAND_COLORS: {brand_colors}" if brand_colors
                     else f"BRAND_COLORS: not extracted")
        lines.append(f"NICHE_DEFAULTS: {niche_color_fallback}")
        return "\n".join(lines) + "\n"

    result    = apply_structure_rules(nav_pages, subpage_content, nav_confidence)
    detected  = result["detected"]
    proposed  = result["proposed"]
    changes   = result["changes"]
    page_mode = result["page_mode"]

    lines = ["━" * 72, "SITE STRUCTURE DECISION", "━" * 72,
             f"DETECTED:        {' | '.join(detected) if detected else '(none)'}",
             f"PROPOSED:        {' | '.join(proposed)}",
             f"NAV_CONFIDENCE:  {nav_confidence}", ""]

    if changes:
        lines.append("CHANGES:")
        for c in changes:
            result_str = f" → {c['result']}" if c.get("result") else ""
            lines.append(f"  {c['action']}: {c['page']}{result_str} — {c['reason']}")
    lines += ["", f"DEMO WILL BUILD: {len(proposed)} page(s)", "━" * 72, "",
              f"PAGE_MODE: {page_mode}", ""]

    if page_mode == "single":
        lines += ["Build one continuous scrollable page. Use standard section order.",
                  "No JS routing.", ""]
    else:
        lines += [f"Build {len(proposed)} fully-designed pages with JS hash routing.", "",
                  "ROUTING RULES:",
                  "  - Each page: <div class=\"page\" id=\"page-[slug]\">",
                  "  - Nav: href=\"#[slug]\" class=\"nav-link\" data-page=\"[slug]\"",
                  "  - CSS: .page{display:none} #page-home{display:block}",
                  "  - 3 event listeners: DOMContentLoaded, popstate, hashchange",
                  "  - Default page: home", ""]
        lines.append("PER-PAGE DESIGN BRIEFS:")

        PAGE_BRIEFS = {
            "home": ["Hero: H1 + city + trade + star rating CTA",
                     "GHL voice widget placeholder (id=ghl-voice-inline)",
                     "Trust bar: years, review count, licensed & insured",
                     "Services grid: 4-6 cards", "Reviews section (3 cards)",
                     "Secondary CTA"],
            "services": ["Short hero with trade headline",
                         "Service cards — one per service in SERVICES_LIST",
                         "Each card: icon + name + 2-sentence description + CTA",
                         "Bottom CTA: phone button"],
            "about": ["Company story (from SUBPAGE_CONTENT if available)",
                      "Stats: years in business, jobs, service area",
                      "Certifications / licensed & insured statement",
                      "CTA linking to Contact"],
            "reviews": ["Headline + RATING_STRING badge",
                        "3 verbatim review cards from REVIEWS_3",
                        "'See all REVIEW_COUNT reviews on Google' link",
                        "GHL reviews placeholder (id=ghl-reviews)",
                        "IMPORTANT: star ratings are STATIC — no live API"],
            "contact": ["GHL contact form (id=ghl-contact-form) — PRIMARY",
                        "Click-to-call phone button",
                        "Business hours if available",
                        "Google Maps embed placeholder",
                        "GHL calendar (id=ghl-calendar)",
                        "NEVER use mailto: links"],
            "our-work": ["Before/after headline", "Photo grid (6 items min)",
                         "Project descriptions from SUBPAGE_CONTENT", "CTA"],
            "service-areas": ["'Areas We Serve' headline",
                              "City/neighborhood grid from SERVICE_AREAS",
                              "Maps placeholder", "CTA"],
            "faq": ["Accordion (min 6 items)",
                    "Use SUBPAGE_CONTENT if available, else generate trade FAQs",
                    "CTA linking to Contact"],
        }

        for page in proposed:
            slug  = page.lower().replace(" ", "-")
            brief = PAGE_BRIEFS.get(slug) or PAGE_BRIEFS.get(page.lower())
            lines.append(f"  [{page.upper()}]  (id=\"page-{slug}\")")
            if brief:
                for b in brief:
                    lines.append(f"    - {b}")
            else:
                content  = subpage_content.get(page, {})
                headings = content.get("headings", [])
                lines.append("    - Hero + 2-3 content sections + CTA to Contact")
                if headings:
                    lines.append(f"    - Original headings: {', '.join(headings[:3])}")
            lines.append("")

    lines += ["━" * 72, "COLORS", "━" * 72]
    if brand_colors:
        lines += [f"BRAND_COLORS: {brand_colors}",
                  "  First color → primary (nav/headings/buttons)",
                  "  Second color → accent (badges/highlights)",
                  f"NICHE_DEFAULTS (fallback): {niche_color_fallback}"]
    else:
        lines += [f"BRAND_COLORS: not extracted",
                  f"NICHE_DEFAULTS: {niche_color_fallback}  ← use these"]
    lines += ["NEVER use purple.", "",
              "━" * 72, "CONTENT RULES", "━" * 72,
              "  - Use real BUSINESS_NAME, PHONE, CITY_PROVINCE, SERVICE_AREAS",
              "  - Use real RATING_STRING and REVIEW_COUNT",
              "  - Use verbatim REVIEWS_3 for review cards",
              "  - NEVER use Lorem Ipsum",
              "  - NEVER invent a phone number",
              "  - Shared header and footer on ALL pages", ""]

    return "\n".join(lines)


# ── Area dispatcher ────────────────────────────────────────────────────────────

AREA_RULE_FUNCTIONS = {
    "first_impressions":       rules_first_impressions,
    "mobile_experience":       rules_mobile_experience,
    "contact_and_booking":     rules_contact_booking,
    "local_presence":          rules_local_presence,
    "trust_and_credibility":   rules_trust_credibility,
    "content_clarity":         rules_content_clarity,
    "speed":                   rules_speed,
    "photos_and_authenticity": rules_photos,
    "site_security":           rules_security,
    "lead_followup_system":    rules_lead_followup,
}


# ── Main Layer 2 assembler ─────────────────────────────────────────────────────

def generate_layer2(findings: dict, business_data: dict) -> str:
    """
    Convert parsed audit findings into Layer 2 prompt instructions.

    Args:
        findings: output of parse_audit.parse_audit_file()
        business_data: output of extract_business_data.py (structured_input.json)
                       May be empty dict if not yet extracted.

    Returns:
        Layer 2 prompt string — ready to inject between Layer 1 and Layer 3.
    """
    areas = findings.get("areas", [])
    business = findings.get("business", {})
    gaps = findings.get("gaps", {})
    summary = findings.get("summary", {})

    business_name = business.get("business_name") or business_data.get("BUSINESS_NAME", "this business")
    trade = business.get("trade", "home service")
    audit_date = business.get("audit_date", "")

    # Count severity
    critical = summary.get("critical_count", 0)
    warnings = summary.get("warning_count", 0)
    clean = summary.get("clean_count", 0)

    header = f"""================================================================================
LAYER 2 — AUDIT-SPECIFIC RULES
Business: {business_name}
Trade: {trade.title()}
Audit date: {audit_date}
Audit score: {critical} critical issues (❌) | {warnings} warnings (⚠️) | {clean} passing (✅)

These rules are derived from a real audit of {business_name}'s current website.
Every rule below addresses a specific observed problem or confirmed gap.
Layer 2 overrides Layer 3 (niche rules) when they conflict.
Layer 2 overrides Layer 1 (universal rules) when they conflict.
The audit findings are the most specific data about this prospect — always follow them.
================================================================================

PRIORITY HIERARCHY FOR THIS SITE:
"""

    # List critical areas first as explicit priorities
    critical_areas = [a for a in areas if a["is_critical"]]
    warning_areas  = [a for a in areas if a["has_issue"] and not a["is_critical"]]

    if critical_areas:
        header += "\nCRITICAL ISSUES TO FIX (❌ — these are the biggest problems on the current site):\n"
        for a in critical_areas:
            header += f"  ❌ Area {a['area_num']}: {a['area_title']}\n"

    if warning_areas:
        header += "\nWARNINGS TO ADDRESS (⚠️):\n"
        for a in warning_areas:
            header += f"  ⚠️  Area {a['area_num']}: {a['area_title']}\n"

    clean_areas = [a for a in areas if not a["has_issue"]]
    if clean_areas:
        header += "\nALREADY WORKING (✅ — preserve these strengths):\n"
        for a in clean_areas:
            header += f"  ✅ Area {a['area_num']}: {a['area_title']}\n"

    header += "\n" + "="*80 + "\n"

    # Generate rules for each area
    section_parts = []
    for area in areas:
        key = area.get("area_key", "")
        rule_fn = AREA_RULE_FUNCTIONS.get(key)
        if rule_fn:
            rule_text = rule_fn(area, business_data)
            if rule_text.strip():
                section_parts.append(rule_text)

    # Add gap items summary from Report C
    critical_gaps = gaps.get("critical", [])
    warning_gaps  = gaps.get("warning", [])

    gap_section = ""
    if critical_gaps or warning_gaps:
        gap_section = "\n" + "="*80 + "\n"
        gap_section += "SPECIFIC GAPS FROM AUDIT CHECKLIST (Report C)\n"
        gap_section += "Build the new site so every ❌ below becomes a ✅\n"
        gap_section += "="*80 + "\n\n"

        if critical_gaps:
            gap_section += "MISSING — CRITICAL:\n"
            for g in critical_gaps:
                gap_section += f"  ❌ {g}\n"
        if warning_gaps:
            gap_section += "\nMISSING — SHOULD HAVE:\n"
            for g in warning_gaps:
                gap_section += f"  ⚠️  {g}\n"

    footer = """
================================================================================
END LAYER 2 — AUDIT-SPECIFIC RULES
The rules above are derived from real observations on this prospect's site.
Every ❌ listed above is a specific thing that costs this business customers today.
The new site must address all of them.
================================================================================
"""

    return header + "\n\n".join(section_parts) + gap_section + "\n\n" + rules_site_structure(business_data) + footer
