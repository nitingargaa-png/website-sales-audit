"""
detect.py — Deterministic HTML scan. The MEASURED tier.

Everything here has a right answer. No judgment, no LLM, no guessing.
If it can't be determined from the bytes, it's None — not a guess.

Ported from SKILL.md v13 Phase 1.4 detection scan.
"""
import re
from typing import Dict, Any, Optional, List

# --- platform -------------------------------------------------------------
PLATFORM_SIGNALS = [
    ("scorpion", r"scorpion\.co"),
    ("wordpress", r"wp-content|wp-includes"),
    ("wix", r"wixstatic\.com|parastorage\.com"),
    ("squarespace", r"squarespace\.com|sqsp\.net"),
    ("webflow", r"webflow\.io|webflow\.com"),
    ("gohighlevel", r"msgsndr\.com|highlevel|leadconnectorhq"),
    ("thryv", r"thryv\.com"),
    ("hibu", r"hibu\.com|yodle\.com"),
    ("townsquare", r"townsquareinteractive\.com"),
    ("duda", r"dudaone|duda\.co"),
    ("godaddy", r"godaddysites\.com"),
    ("weebly", r"weebly\.com"),
]

# Pitch shifts by platform — not a score, a routing hint.
PLATFORM_PITCH = {
    "scorpion": "Solid site. Do NOT pitch rebuild. Automation layer only.",
    "wix": "Strong rebuild candidate.",
    "squarespace": "Strong rebuild candidate.",
    "godaddy": "Strong rebuild candidate.",
    "weebly": "Strong rebuild candidate.",
    "gohighlevel": "Already a GHL client. Advanced workflows only.",
    "thryv": "Paying for mediocre all-in-one. Displacement pitch.",
    "hibu": "Paying for mediocre all-in-one. Displacement pitch.",
    "wordpress": "Depends on build quality. Judge on merits.",
}

CHAT_SIGNALS = [
    ("mav.ai", r"mav\.ai|mavarick"),
    ("podium", r"podium\.com"),
    ("tidio", r"tidio\.com"),
    ("drift", r"drift\.com"),
    ("intercom", r"intercom\.io|intercom\.com"),
    ("smith.ai", r"smith\.ai"),
    ("crisp", r"crisp\.chat"),
    ("tawk.to", r"tawk\.to"),
    ("livechat", r"livechat\.com"),
    ("freshchat", r"freshchat|freshworks"),
]

FSM_SIGNALS = [
    ("servicetitan", r"servicetitan\.com"),
    ("housecallpro", r"housecallpro\.com"),
    ("jobber", r"getjobber\.com|jobber\.com"),
    ("fieldedge", r"fieldedge\.com"),
    ("workiz", r"workiz\.com"),
    ("servicefusion", r"servicefusion\.com"),
    ("kickserv", r"kickserv\.com"),
]

REVIEW_VENDOR_SIGNALS = [
    ("birdeye", r"birdeye\.com"),
    ("nicejob", r"nicejob\.com"),
    ("broadly", r"broadly\.com"),
    ("grade.us", r"grade\.us"),
    ("reviewbuzz", r"reviewbuzz\.com"),
    ("podium", r"podium\.com"),
]

CALL_TRACKING_SIGNALS = [
    ("callrail", r"callrail\.com"),
    ("callfire", r"callfire\.com"),
    ("marchex", r"marchex\.com"),
    ("whatconverts", r"whatconverts\.com"),
]

AD_PIXEL_SIGNALS = [
    ("meta_pixel", r"connect\.facebook\.net|fbevents\.js"),
    ("google_ads", r"googleads\.g\.doubleclick|gtag/js\?id=AW-"),
    ("gtm", r"googletagmanager\.com"),
    ("ga4", r"gtag/js\?id=G-"),
]

FRANCHISE_PATTERNS = [
    r"independently owned and operated",
    r"own a franchise",
    r"franchise opportunit",
    r"international franchise association",
    r"each location is independently",
]

PLACEHOLDER_PATTERNS = [
    r"coming soon",
    r"lorem ipsum",
    r"under construction",
    r"site is being built",
    r"this domain is parked",
]


def _find(html: str, signals) -> Optional[str]:
    low = html.lower()
    for name, pat in signals:
        if re.search(pat, low):
            return name
    return None


def _find_all(html: str, signals) -> List[str]:
    low = html.lower()
    return [name for name, pat in signals if re.search(pat, low)]


def _title(html: str) -> Optional[str]:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    return m.group(1).strip() if m else None


def _meta_desc(html: str) -> Optional[str]:
    m = re.search(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
        html, re.I | re.S)
    if not m:
        m = re.search(
            r'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']',
            html, re.I | re.S)
    return m.group(1).strip() if m else None


def _strip_tags(html: str) -> str:
    """Remove script and style CONTENT, not just the tags."""
    h = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    h = re.sub(r"<style[^>]*>.*?</style>", " ", h, flags=re.I | re.S)
    h = re.sub(r"<[^>]+>", " ", h)
    return re.sub(r"\s+", " ", h).strip()


def _aggregate_rating(html: str) -> Dict[str, Optional[float]]:
    out = {"rating_value": None, "review_count": None}
    if not re.search(r"aggregateRating", html, re.I):
        return out
    m = re.search(r'"ratingValue"\s*:\s*"?([\d.]+)"?', html)
    if m:
        try:
            out["rating_value"] = float(m.group(1))
        except ValueError:
            pass
    m = re.search(r'"reviewCount"\s*:\s*"?(\d+)"?', html)
    if m:
        try:
            out["review_count"] = int(m.group(1))
        except ValueError:
            pass
    return out


def _headings(html: str, rendered_text: Optional[str]) -> Dict[str, Any]:
    """
    H1/H2 structure from raw HTML.

    On a JS site these live in the rendered output only — same class of bug as
    tel_href and google_badge. Markdown from Jina/Firecrawl represents headings
    as leading '#' so we can count them there too.
    """
    h1_raw = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
    h2_raw = re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.I | re.S)
    h1_texts = [re.sub(r"<[^>]+>", " ", h).strip() for h in h1_raw]
    h1_texts = [t for t in h1_texts if t]

    h1_md = h2_md = 0
    if rendered_text:
        h1_md = len(re.findall(r"^#\s+\S", rendered_text, re.M))
        h2_md = len(re.findall(r"^##\s+\S", rendered_text, re.M))

    return {
        "h1_count": len(h1_texts) or h1_md,
        "h1_text": h1_texts[0] if h1_texts else None,
        "h2_count": len(h2_raw) or h2_md,
        "headings_in_raw_html": bool(h1_raw or h2_raw),
    }


def _internal_links(html: str, url: str) -> Dict[str, Any]:
    """
    Internal links from raw HTML.

    Zero internal links on a JS site is expected and is itself the finding —
    a crawler following links finds nothing to follow.
    """
    try:
        host = re.sub(r"^https?://", "", url).split("/")[0].replace("www.", "")
    except Exception:
        host = ""

    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html, re.I)
    internal, external = 0, 0
    for h in hrefs:
        hl = h.lower().strip()
        if hl.startswith(("#", "mailto:", "tel:", "javascript:", "whatsapp:")):
            continue
        if hl.startswith("/") or (host and host in hl):
            internal += 1
        elif hl.startswith("http"):
            external += 1
    return {"internal_links": internal, "external_links": external}


SERVICE_PAGE_HINTS = [
    r"/services?/", r"/plumbing", r"/hvac", r"/heating", r"/cooling",
    r"/drain", r"/repair", r"/installation", r"/emergency", r"/residential",
    r"/commercial", r"/roofing", r"/electrical", r"/cleaning",
]


def _service_pages(html: str) -> int:
    """Distinct service-looking internal URLs. Proxy for per-service pages."""
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html, re.I)
    hits = set()
    for h in hrefs:
        hl = h.lower()
        for pat in SERVICE_PAGE_HINTS:
            if re.search(pat, hl):
                hits.add(hl.split("?")[0].rstrip("/"))
                break
    return len(hits)


def _city_in_title(title: Optional[str], rendered_text: Optional[str]) -> Optional[bool]:
    """
    Does the title name a place? Weak heuristic — a title of 'Home' obviously
    doesn't, which is the case that matters.
    """
    if not title:
        return False
    if len(title) < 12:
        return False
    return bool(re.search(r",\s*[A-Z]{2}\b|\bin\s+[A-Z][a-z]+", title))


def _tel_href(html: str) -> bool:
    """tel: link present in the raw HTML — what a crawler sees on first load."""
    return bool(re.search(r'href=["\']tel:', html, re.I))


def _tel_in_rendered(rendered_text: Optional[str]) -> bool:
    """
    Phone rendered as a link after JS runs.

    Jina/Firecrawl emit markdown, so a tel: anchor becomes either a
    [647-550-4003](tel:6475504003) link or bare text. Look for the scheme.
    """
    if not rendered_text:
        return False
    return bool(re.search(r"\(tel:|tel:\+?\d", rendered_text, re.I))


def _review_count_in_text(text: str) -> bool:
    """
    Is a review COUNT actually stated?

    A "Google Reviews" badge with five gold stars and no number is NOT a
    review count. Neither is a single testimonial. The visitor must be able to
    read how many.

    Confirmed against mississaugaplumbingservices.com 2026-07-16: the homepage
    shows a Google Reviews badge, five stars, and one testimonial from a named
    customer — and no number anywhere. Google's own panel says 4.8 from 266
    reviews. That gap IS the pitch.
    """
    return bool(re.search(
        r"\b\d{2,4}\s*\+?\s*(google\s*)?reviews?\b"
        r"|\breviews?\s*[:\-(]?\s*\d{2,4}\b"
        r"|\bbased on\s+\d{2,4}\b",
        text, re.I))


def _booking_tier(html: str, fsm: Optional[str]) -> int:
    """
    1 = form/phone only, 2 = embedded form no calendar, 3 = full wizard+calendar.

    KNOWN LIMIT: Tier 3 detection is best-effort from static HTML. The real
    Tier 3 signal (multi-step wizard, live calendar, SMS consent) lives inside
    the booking widget's iframe, which a static fetch does not surface. See
    docs/fixtures_golden.md "Deferred — Tier 3 FSM counter-signal".

    We approximate: FSM booking subdomain present -> assume Tier 3. This catches
    the decision that matters (don't pitch booking to someone who has it) even
    though it is not the full signal set.
    """
    low = html.lower()
    if re.search(r"book\.servicetitan\.com|book\.housecallpro", low):
        return 3
    if fsm and re.search(r"schedule|book(ing)?", low):
        return 3
    if re.search(r"<form", low) and re.search(r"calendar|calendly|cal\.com", low):
        return 3
    if re.search(r"<form", low):
        return 2
    return 1


def _aggregate_rating_from_text(text: str) -> Optional[Dict[str, Optional[float]]]:
    """
    Pull rating/count from rendered prose when JSON-LD isn't in static HTML.

    Matches the shapes real sites use:
      "4.9 stars based on 166 reviews"
      "Rated 4.9 / 5 from 166 Google reviews"
      "166 Google Reviews"  (count only)
    """
    out: Dict[str, Optional[float]] = {"rating_value": None, "review_count": None}

    m = re.search(r"([0-5]\.\d)\s*(?:out of 5|/\s*5|stars?)", text, re.I)
    if m:
        try:
            out["rating_value"] = float(m.group(1))
        except ValueError:
            pass

    m = re.search(r"(\d{1,4})\+?\s*(?:google\s*)?reviews?\b", text, re.I)
    if not m:
        m = re.search(r"reviews?\s*[:\-(]?\s*(\d{1,4})", text, re.I)
    if m:
        try:
            out["review_count"] = int(m.group(1))
        except ValueError:
            pass

    return out if (out["rating_value"] or out["review_count"]) else None


def scan(html: str, url: str, rendered_text: Optional[str] = None) -> Dict[str, Any]:
    """
    HTML -> measured dict. Every value here is checkable by anyone.

    None means "could not determine", never "probably not".

    rendered_text: visible text from a JS renderer (Jina/Firecrawl). On a
    JS-built site the static HTML contains almost nothing, so every
    text-derived signal — phone, reviews, Gmail, franchise language — comes
    back blank and the applicability rules silently read those blanks as
    absence.

    Bug observed 2026-07-16: mississaugaplumbingservices.com rendered to 3,685
    chars via Jina, but detect.scan() only ever saw the 4-char static shell.
    Result: aggregate_review_count=None on a business with 166 reviews, and
    TRIAGE_META emitted null/null where fixture 1 pins true/true.

    TAG-DERIVED signals (script src, meta, JSON-LD, tel: href) still come from
    `html` — a renderer's markdown strips the tags we need.
    TEXT-DERIVED signals prefer `rendered_text` when present.
    """
    static_text = _strip_tags(html)
    # Prefer rendered text for anything read from prose; keep static as floor.
    text = rendered_text if rendered_text and len(rendered_text) > len(static_text) \
        else static_text

    title = _title(html)
    desc = _meta_desc(html)
    fsm = _find(html, FSM_SIGNALS)

    # JSON-LD may be injected by JS — check both sources.
    agg = _aggregate_rating(html)
    if agg["review_count"] is None and rendered_text:
        agg = _aggregate_rating_from_text(rendered_text) or agg

    hd = _headings(html, rendered_text)
    il = _internal_links(html, url)

    return {
        # --- binaries, Area 4 + Area 2 ---
        "https": url.lower().startswith("https://"),
        "viewport_meta": bool(re.search(
            r'<meta[^>]+name=["\']viewport["\']', html, re.I)),
        # tel_href = in raw HTML, i.e. what a crawler sees on first load.
        # tel_rendered = present only after JS runs.
        # The distinction matters: a JS-injected tel: link works for a human
        # with JavaScript on, and does not exist for anything reading the page
        # as delivered. Reporting a flat "NO" contradicted the judged tier,
        # which had read the rendered page and correctly saw a call button.
        "tel_href": _tel_href(html),
        "tel_rendered": _tel_in_rendered(rendered_text),
        "tel_js_only": (not _tel_href(html)) and _tel_in_rendered(rendered_text),
        "localbusiness_jsonld": bool(re.search(
            r'"@type"\s*:\s*"[^"]*(LocalBusiness|Plumber|HVACBusiness|'
            r'RoofingContractor|Electrician|HomeAndConstructionBusiness)',
            html, re.I)),
        "map_embed": bool(re.search(
            r"google\.com/maps/embed|maps\.google\.com/maps\?", html, re.I)),
        "gbp_link": bool(re.search(
            r"g\.page|goo\.gl/maps|maps\.app\.goo\.gl|business\.google\.com",
            html, re.I)),
        "has_form": bool(re.search(r"<form", html, re.I)),

        # --- title / meta lengths, Area 4 ---
        "title": title,
        "title_len": len(title) if title else None,
        "title_ok": (55 <= len(title) <= 60) if title else False,
        "meta_desc": desc,
        "meta_desc_len": len(desc) if desc else None,
        "meta_desc_ok": (150 <= len(desc) <= 160) if desc else False,
        "city_in_title": _city_in_title(title, rendered_text),

        # --- page structure, Area 4 ---
        "h1_count": hd["h1_count"],
        "h1_text": hd["h1_text"],
        "h2_count": hd["h2_count"],
        "headings_in_raw_html": hd["headings_in_raw_html"],
        "internal_links": il["internal_links"],
        "external_links": il["external_links"],
        "service_pages": _service_pages(html),

        # --- JS-only check, Area 4 automatic <=2 ---
        # ALWAYS measured against STATIC text, never rendered. The whole point
        # is "what does Google see on first load" — if a renderer had to
        # execute JavaScript to find the content, that IS the finding.
        "visible_text_len": len(static_text),
        "js_only_suspected": len(static_text) < 500,
        "script_count": len(re.findall(r"<script", html, re.I)),
        "rendered_text_len": len(rendered_text) if rendered_text else None,

        # --- phone in image, Area 3 automatic <=2 ---
        "phone_in_text": bool(re.search(
            r"\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}", text)),

        # --- reviews, Area 5 ---
        "aggregate_rating_value": agg["rating_value"],
        "aggregate_review_count": agg["review_count"],
        # visible on FIRST LOAD — a count that only appears after JS is not
        # visible to a crawler, and a badge with no number is not a count at all.
        "review_count_visible": _review_count_in_text(static_text),
        "review_count_after_js": _review_count_in_text(rendered_text) if rendered_text else False,
        "review_vendor": _find(html, REVIEW_VENDOR_SIGNALS),
        # Badge is often JS-injected, same as everything else on these sites.
        # Check both sources or the hidden-social-proof cap silently misses.
        "google_badge": bool(re.search(
            r"google.{0,20}review|review.{0,20}google", html + " " + (rendered_text or ""),
            re.I)),

        # --- vendors ---
        "platform": _find(html, PLATFORM_SIGNALS),
        "chat_vendor": _find(html, CHAT_SIGNALS),
        "fsm_vendor": fsm,
        "booking_tier": _booking_tier(html, fsm),
        "call_tracking": _find(html, CALL_TRACKING_SIGNALS),
        "ad_pixels": _find_all(html, AD_PIXEL_SIGNALS),

        # --- disqualifier inputs ---
        "franchise_language": bool(any(
            re.search(p, text, re.I) for p in FRANCHISE_PATTERNS)),
        "placeholder_signals": sum(
            1 for p in PLACEHOLDER_PATTERNS if re.search(p, text, re.I)),

        # --- misc ---
        "copyright_year": _copyright_year(text),
        "gmail_contact": bool(re.search(
            r"[\w.\-]+@(gmail|yahoo|hotmail|outlook|aol)\.", text, re.I)),
    }


def _copyright_year(text: str) -> Optional[int]:
    years = re.findall(r"(?:©|copyright|&copy;)\s*(?:\d{4}\s*[-–]\s*)?(\d{4})",
                       text, re.I)
    if not years:
        return None
    try:
        return max(int(y) for y in years)
    except ValueError:
        return None
