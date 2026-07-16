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


def _review_count_visible(text: str) -> bool:
    """
    Is a review COUNT actually on the page?

    A "Leave a Review" link is OUTBOUND — it does not count as social proof.
    The count must be visible to the visitor. This distinction is the difference
    between "they have reviews" and "visitors can see they have reviews", and it
    is one of the most winnable fixes in the whole audit.
    """
    return bool(re.search(
        r"\b\d{2,4}\s*(google\s*)?(\+\s*)?reviews?\b|\breviews?\s*[:\-]?\s*\d{2,4}\b",
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


def scan(html: str, url: str) -> Dict[str, Any]:
    """
    HTML -> measured dict. Every value here is checkable by anyone.

    None means "could not determine", never "probably not".
    """
    text = _strip_tags(html)
    title = _title(html)
    desc = _meta_desc(html)
    fsm = _find(html, FSM_SIGNALS)
    agg = _aggregate_rating(html)

    return {
        # --- binaries, Area 4 + Area 2 ---
        "https": url.lower().startswith("https://"),
        "viewport_meta": bool(re.search(
            r'<meta[^>]+name=["\']viewport["\']', html, re.I)),
        "tel_href": bool(re.search(r'href=["\']tel:', html, re.I)),
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

        # --- JS-only check, Area 4 automatic <=2 ---
        "visible_text_len": len(text),
        "js_only_suspected": len(text) < 500,

        # --- phone in image, Area 3 automatic <=2 ---
        "phone_in_text": bool(re.search(
            r"\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}", text)),

        # --- reviews, Area 5 ---
        "aggregate_rating_value": agg["rating_value"],
        "aggregate_review_count": agg["review_count"],
        "review_count_visible": _review_count_visible(text),
        "review_vendor": _find(html, REVIEW_VENDOR_SIGNALS),
        "google_badge": bool(re.search(
            r"google.{0,20}review|review.{0,20}google", html, re.I)),

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
