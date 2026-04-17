#!/usr/bin/env python3
"""
extract_business_data.py
Pulls structured business data from a website URL and/or Google Business Profile.
Outputs: structured_input.json with all 6 prompt variables pre-filled.

Usage:
  python3 execution/extract_business_data.py --url https://example.com
  python3 execution/extract_business_data.py --business "Acme Plumbing" --city "Mississauga ON"
  python3 execution/extract_business_data.py --url https://example.com --business "Acme Plumbing" --city "Mississauga ON"
  python3 execution/extract_business_data.py --url https://example.com --no-places
"""

import os
import sys
import csv
import json
import argparse
import requests
import re as _re
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv

# ── Load env ──────────────────────────────────────────────────────────────────
load_dotenv()
FIRECRAWL_KEY     = os.getenv("FIRECRAWL_API_KEY", "")
SERPAPI_KEY       = os.getenv("SERPAPI_KEY", "")
SCRAPINGDOG_KEY   = os.getenv("SCRAPINGDOG_KEY", "")
ANTHROPIC_KEY     = os.getenv("ANTHROPIC_API_KEY", "")
JINA_KEY          = os.getenv("JINA_API_KEY", "")
GOOGLE_PLACES_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")

# Scrape provider: Jina (free) preferred, Firecrawl as fallback
SCRAPE_PROVIDER = "jina" if not FIRECRAWL_KEY else "firecrawl"
if FIRECRAWL_KEY:
    SCRAPE_PROVIDER = "firecrawl"

# GBP provider: Scrapingdog preferred (97% cheaper), SerpAPI as fallback
GBP_PROVIDER = "scrapingdog" if SCRAPINGDOG_KEY else ("serpapi" if SERPAPI_KEY else "")

PROJECT_ROOT   = Path(__file__).parent.parent
PROSPECTS_CSV  = PROJECT_ROOT / "input" / "prospects.csv"

PROSPECTS_HEADERS = [
    "url", "business_name", "niche", "audit_date", "audit_score",
    "demo_url", "demo_netlify_url", "demo_password", "demo_noindex_confirmed",
    "status", "last_contact_date", "package_pitched",
    "setup_fee_quoted", "monthly_quoted", "notes",
]

print(f"✅ Scrape provider : {SCRAPE_PROVIDER}")
if not GBP_PROVIDER:
    print("⚠️  No GBP API key found — add SCRAPINGDOG_KEY or SERPAPI_KEY to .env")
else:
    print(f"✅ GBP provider    : {GBP_PROVIDER}")
if GOOGLE_PLACES_KEY:
    print(f"✅ Places API      : enabled")
else:
    print(f"⚠️  Places API      : disabled (add GOOGLE_PLACES_API_KEY to .env)")
if SCRAPE_PROVIDER == "jina" and not ANTHROPIC_KEY:
    print("⚠️  ANTHROPIC_API_KEY not found — Jina markdown extraction will be skipped")

# ── Niche keyword detection ───────────────────────────────────────────────────
NICHE_KEYWORDS = {
    "plumbing":     ["plumber", "plumbing", "drain", "pipe", "water heater", "sump"],
    "hvac":         ["hvac", "heating", "cooling", "furnace", "air conditioning", " ac "],
    "cleaning":     ["cleaning", "cleaner", "maid", "housekeeping", "janitorial"],
    "pest_control": ["pest", "exterminator", "termite", "rodent", "bug", "insect"],
    "roofing":      ["roofing", "roofer", "shingles", "roof", "gutters"],
    "landscaping":  ["landscaping", "lawn", "garden", "snow removal", "yard"],
    "electrical":   ["electrical", "electrician", "wiring", "panel", "circuit"],
    "painting":     ["painting", "painter", "interior paint", "exterior paint"],
    "garage_door":  ["garage door", "garage", "door repair", "opener"],
    "handyman":     ["handyman", "repairs", "maintenance", "odd jobs"],
    "moving":       ["moving", "movers", "relocation", "storage"],
    "junk_removal": ["junk", "junk removal", "hauling", "disposal", "cleanup"],
}


def detect_niche(text: str) -> str:
    text_lower = text.lower()
    scores = {}
    for niche, keywords in NICHE_KEYWORDS.items():
        scores[niche] = sum(1 for kw in keywords if kw in text_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "generic"


# ── Jina Reader scrape ────────────────────────────────────────────────────────
def scrape_with_jina(url: str) -> dict:
    print(f"\n🔍 Jina Reader scraping: {url}")

    headers = {"Accept": "text/markdown"}
    if JINA_KEY:
        headers["Authorization"] = f"Bearer {JINA_KEY}"

    try:
        resp = requests.get(
            f"https://r.jina.ai/{url}",
            headers=headers,
            timeout=30
        )
        resp.raise_for_status()
        markdown = resp.text
        print(f"  ✅ Jina OK — {len(markdown)} chars fetched")
    except requests.exceptions.Timeout:
        print("  ⚠️  Jina Reader timed out (30s). Skipping site scrape.")
        return {}
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Jina Reader error: {e}")
        return {}

    if not markdown or len(markdown) < 100:
        print("  ⚠️  Jina returned empty content")
        return {}

    if not ANTHROPIC_KEY:
        print("  ⚠️  No ANTHROPIC_API_KEY — returning raw markdown only")
        return {"raw_text_sample": markdown[:800]}

    print(f"  🤖 Extracting structured data via Claude API...")

    extraction_prompt = f"""Extract business information from this website content.
Return ONLY valid JSON, no markdown, no explanation.

Required JSON structure:
{{
  "business_name": "full business name",
  "phone": "phone number formatted as (XXX) XXX-XXXX",
  "email": "email address or empty string",
  "address": "full street address or empty string",
  "city": "city and province/state e.g. Toronto ON",
  "services": ["service 1", "service 2", "service 3"],
  "hours": "business hours as string or empty",
  "emergency": "yes or no — is 24/7 or emergency service mentioned?",
  "years_in_business": "number or range e.g. 10+ or empty string",
  "logo_url": "URL of logo image or empty string",
  "photo_urls": ["url1", "url2"],
  "neighborhoods": ["neighborhood1", "neighborhood2"],
  "tagline": "business tagline or empty string",
  "raw_text_sample": "first 500 chars of main content"
}}

Rules:
- Return empty string "" for any field not found — never null
- Return empty array [] for list fields not found
- For services, extract individual service names only
- For phone, ALWAYS format as (XXX) XXX-XXXX — strip country code (+1 or 1)
- For neighborhoods, extract SPECIFIC area/city/neighborhood names only
  Do NOT use "Greater Toronto Area", "GTA", or other vague region names
  If no specific neighborhoods found, return empty array []
- For city, use format "City Province" e.g. "Toronto ON"

Website content:
{markdown[:4000]}"""

    try:
        api_resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": extraction_prompt}],
            },
            timeout=30,
        )
        api_resp.raise_for_status()
        response_data = api_resp.json()
        raw_text = response_data["content"][0]["text"].strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        raw_text = raw_text.strip()

        extracted = json.loads(raw_text)
        extracted["raw_text_sample"] = markdown[:800]
        print(f"  ✅ Claude extraction OK — business: {extracted.get('business_name', '(not found)')}")
        return extracted

    except json.JSONDecodeError as e:
        print(f"  ⚠️  Claude returned invalid JSON: {e} — falling back to raw markdown")
        return {"raw_text_sample": markdown[:800]}
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Claude API error: {e}")
        return {"raw_text_sample": markdown[:800]}


# ── Firecrawl scrape ──────────────────────────────────────────────────────────
def scrape_with_firecrawl(url: str) -> dict:
    print(f"\n🔍 Firecrawl scraping: {url}")

    extract_schema = {
        "type": "object",
        "properties": {
            "business_name":   {"type": "string"},
            "phone":           {"type": "string"},
            "email":           {"type": "string"},
            "address":         {"type": "string"},
            "city":            {"type": "string"},
            "services":        {"type": "array", "items": {"type": "string"}},
            "hours":           {"type": "string"},
            "emergency":       {"type": "string", "description": "yes or no"},
            "years_in_business": {"type": "string"},
            "logo_url":        {"type": "string"},
            "photo_urls":      {"type": "array", "items": {"type": "string"}},
            "neighborhoods":   {"type": "array", "items": {"type": "string"}},
            "tagline":         {"type": "string"},
            "raw_text_sample": {"type": "string"},
        }
    }

    payload = {
        "url": url,
        "formats": ["extract", "markdown"],
        "extract": {
            "schema": extract_schema,
            "prompt": (
                "Extract all business contact details, services, hours, and assets. "
                "For phone, return raw digits in format (XXX) XXX-XXXX or +1XXXXXXXXXX. "
                "For services, return a list of individual service names. "
                "For emergency, return 'yes' if any 24/7 or emergency service is mentioned. "
                "For photo_urls, return up to 3 actual job/service photo URLs (not icons). "
                "For logo_url, return the URL of the business logo image."
            )
        }
    }

    try:
        resp = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={"Authorization": f"Bearer {FIRECRAWL_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()

        if not data.get("success"):
            print(f"  ⚠️  Firecrawl returned success=false: {data.get('error', 'unknown error')}")
            return {}

        extracted = data.get("extract", {}) or {}
        markdown  = data.get("markdown", "") or ""

        if not extracted.get("raw_text_sample") and markdown:
            extracted["raw_text_sample"] = markdown[:800]

        print(f"  ✅ Firecrawl OK — business: {extracted.get('business_name', '(not found)')}")
        return extracted

    except requests.exceptions.Timeout:
        print("  ⚠️  Firecrawl timed out (60s). Skipping site scrape.")
        return {}
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Firecrawl error: {e}")
        return {}


# ── Scrapingdog GBP ───────────────────────────────────────────────────────────
def pull_gbp_scrapingdog(business_name: str = "", city: str = "", url: str = "") -> dict:
    print(f"\n📍 Scrapingdog GBP lookup: '{business_name}' in '{city}'")

    query = f"{business_name} {city}".strip()
    if not query:
        query = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]

    try:
        resp = requests.get(
            "https://api.scrapingdog.com/google_maps/",
            params={"api_key": SCRAPINGDOG_KEY, "query": query, "hl": "en"},
            timeout=30
        )
        resp.raise_for_status()
        maps_data = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Scrapingdog Maps error: {e}")
        return {}

    results = (
        maps_data.get("local_results")
        or maps_data.get("place_results")
        or maps_data.get("search_results")
        or maps_data.get("results")
        or []
    )
    if not results:
        print(f"  ⚠️  No GBP listing found via Scrapingdog")
        print(f"  🔎 Response keys: {list(maps_data.keys())[:10]}")
        return {}

    listing = results[0] if isinstance(results, list) else results

    data_id      = listing.get("data_id") or listing.get("place_id", "")
    rating       = listing.get("rating", "")
    review_count = listing.get("reviews", "") or listing.get("review_count", "")
    phone        = listing.get("phone", "")
    address      = listing.get("address", "")
    hours_raw    = listing.get("hours", {})
    photos       = [p.get("link", "") for p in listing.get("photos", [])[:3] if p.get("link")]

    if isinstance(hours_raw, dict):
        hours_str = " | ".join([f"{k}: {v}" for k, v in list(hours_raw.items())[:3]])
    elif isinstance(hours_raw, str):
        hours_str = hours_raw
    else:
        hours_str = ""

    print(f"  ✅ Found: {rating}★ ({review_count} reviews) | data_id: {str(data_id)[:20]}...")

    reviews_text = []
    if data_id:
        try:
            r2 = requests.get(
                "https://api.scrapingdog.com/google_maps/reviews/",
                params={"api_key": SCRAPINGDOG_KEY, "data_id": data_id, "hl": "en"},
                timeout=30
            )
            r2.raise_for_status()
            reviews_data = r2.json()
            raw_reviews  = (
                reviews_data.get("reviews_results")
                or reviews_data.get("reviews")
                or reviews_data.get("search_results")
                or []
            )
            if not raw_reviews:
                print(f"  🔎 Reviews response keys: {list(reviews_data.keys())[:10]}")
                if reviews_data:
                    first_key = list(reviews_data.keys())[0]
                    sample = reviews_data[first_key]
                    if isinstance(sample, list) and sample:
                        print(f"  🔎 First item keys: {list(sample[0].keys())[:10]}")
            reviews_text = [
                (
                    rv.get("extracted_snippet", {}).get("original")
                    or rv.get("snippet")
                    or rv.get("text")
                    or rv.get("review_text")
                    or rv.get("description")
                    or ""
                )
                for rv in raw_reviews
                if any([
                    rv.get("extracted_snippet", {}).get("original"),
                    rv.get("snippet"),
                    rv.get("text"),
                    rv.get("review_text"),
                    rv.get("description"),
                ])
            ][:5]
            print(f"  ✅ Pulled {len(reviews_text)} review texts")
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Scrapingdog Reviews error: {e}")

    return {
        "rating":       str(rating),
        "review_count": str(review_count),
        "reviews":      reviews_text,
        "phone_gbp":    phone,
        "address_gbp":  address,
        "hours_gbp":    hours_str,
        "place_id":     data_id,
        "gbp_photos":   photos,
    }


# ── SerpAPI GBP (fallback) ────────────────────────────────────────────────────
def pull_gbp_data(business_name: str = "", city: str = "", url: str = "") -> dict:
    print(f"\n📍 SerpApi GBP lookup: '{business_name}' in '{city}'")

    query = f"{business_name} {city}".strip()
    if not query:
        query = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]

    params_maps = {
        "engine":  "google_maps",
        "q":       query,
        "api_key": SERPAPI_KEY,
        "hl":      "en",
        "gl":      "us",
        "type":    "search",
    }

    try:
        resp = requests.get("https://serpapi.com/search", params=params_maps, timeout=30)
        resp.raise_for_status()
        maps_data = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  SerpApi Maps error: {e}")
        return {}

    results = maps_data.get("local_results") or maps_data.get("place_results") or []
    if not results:
        print("  ⚠️  No GBP listing found")
        return {}

    listing = results[0] if isinstance(results, list) else results

    place_id     = listing.get("place_id", "")
    rating       = listing.get("rating", "")
    review_count = listing.get("reviews", "")
    phone        = listing.get("phone", "")
    address      = listing.get("address", "")
    hours_raw    = listing.get("hours", {})
    photos       = [p.get("link", "") for p in listing.get("photos", [])[:3] if p.get("link")]

    if isinstance(hours_raw, dict):
        hours_str = " | ".join([f"{k}: {v}" for k, v in list(hours_raw.items())[:3]])
    elif isinstance(hours_raw, str):
        hours_str = hours_raw
    else:
        hours_str = ""

    print(f"  ✅ Found: {rating}★ ({review_count} reviews) | place_id: {place_id[:20]}...")

    reviews_text = []
    if place_id:
        params_reviews = {
            "engine":    "google_maps_reviews",
            "place_id":  place_id,
            "api_key":   SERPAPI_KEY,
            "hl":        "en",
            "sort_by":   "ratingHigh",
            "num":       5,
        }
        try:
            r2 = requests.get("https://serpapi.com/search", params=params_reviews, timeout=30)
            r2.raise_for_status()
            reviews_data = r2.json()
            raw_reviews  = reviews_data.get("reviews", [])
            reviews_text = [
                (
                    rv.get("extracted_snippet", {}).get("original")
                    or rv.get("snippet")
                    or rv.get("text")
                    or ""
                )
                for rv in raw_reviews
                if rv.get("extracted_snippet", {}).get("original")
                or rv.get("snippet")
                or rv.get("text")
            ][:5]
            print(f"  ✅ Pulled {len(reviews_text)} review texts")
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  SerpApi Reviews error: {e}")

    return {
        "rating":       str(rating),
        "review_count": str(review_count),
        "reviews":      reviews_text,
        "phone_gbp":    phone,
        "address_gbp":  address,
        "hours_gbp":    hours_str,
        "place_id":     place_id,
        "gbp_photos":   photos,
    }


# ── Google Places enrichment ──────────────────────────────────────────────────
def enrich_with_places(business_name: str, city: str) -> dict:
    """
    Calls Google Places API (New) to get rating, review count, sample reviews,
    hours, and derived pitch signals. Returns empty dict if key not set or call fails.
    Cost: ~$0.05 per prospect.
    """
    if not GOOGLE_PLACES_KEY:
        return {}

    print(f"\n📍 Google Places enrichment: '{business_name}' in '{city}'")

    # Step 1: Text Search → place_id
    try:
        search_resp = requests.post(
            "https://places.googleapis.com/v1/places:searchText",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": GOOGLE_PLACES_KEY,
                "X-Goog-FieldMask": "places.id,places.displayName",
            },
            json={"textQuery": f"{business_name} {city}"},
            timeout=10,
        )
        search_resp.raise_for_status()
        places = search_resp.json().get("places", [])
        if not places:
            print(f"  ⚠️  No Places result found")
            return {}
        place_id = places[0]["id"]
        print(f"  ✅ place_id: {place_id}")
    except requests.RequestException as e:
        print(f"  ⚠️  Places Text Search failed: {e}")
        return {}

    # Step 2: Place Details
    try:
        details_resp = requests.get(
            f"https://places.googleapis.com/v1/places/{place_id}",
            headers={
                "X-Goog-Api-Key": GOOGLE_PLACES_KEY,
                "X-Goog-FieldMask": (
                    "rating,userRatingCount,reviews,"
                    "regularOpeningHours,websiteUri,nationalPhoneNumber"
                ),
            },
            timeout=10,
        )
        details_resp.raise_for_status()
        details = details_resp.json()
    except requests.RequestException as e:
        print(f"  ⚠️  Places Details failed: {e}")
        return {}

    rating       = details.get("rating")
    review_count = details.get("userRatingCount")
    has_hours    = bool(details.get("regularOpeningHours"))
    website      = details.get("websiteUri", "")
    raw_reviews  = details.get("reviews", [])[:3]

    sample_reviews = [
        {
            "rating": rv.get("rating"),
            "text":   rv.get("text", {}).get("text", ""),
            "author": rv.get("authorAttribution", {}).get("displayName", ""),
        }
        for rv in raw_reviews
    ]

    # Derive pitch signals
    signals = []
    if rating and rating >= 4.7 and review_count and review_count >= 50:
        signals.append(
            f"HIDDEN_REPUTATION: {review_count} Google reviews at {rating}★ — "
            "social proof not visible on website. Lead angle: make it visible."
        )
    if rating and rating < 4.2 and review_count and review_count >= 10:
        signals.append(
            f"REVIEW_RECOVERY: {rating}★ average. "
            "Lead angle: review request + response workflow."
        )
    if review_count is not None and review_count < 20:
        signals.append(
            f"FEW_REVIEWS: Only {review_count} Google reviews. "
            "Lead angle: automated review request after job completion."
        )
    if not has_hours:
        signals.append(
            "NO_HOURS: Google Business Profile has no hours listed. "
            "Lead angle: GHL profile optimization + booking widget."
        )
    slow_keywords = ["didn't call", "no call back", "slow response",
                     "hard to reach", "never responded", "voicemail"]
    if any(kw in rev.get("text", "").lower() for rev in sample_reviews for kw in slow_keywords):
        signals.append(
            "SLOW_RESPONSE_COMPLAINTS: Reviews mention response issues. "
            "Lead angle: missed-call text-back + voice AI."
        )
    if not website:
        signals.append(
            "NO_WEBSITE_ON_GOOGLE: No website linked in Google profile. "
            "Lead angle: full GHL site build."
        )

    review_count_str = str(review_count) if review_count else ""
    rating_str = f"{rating}★ ({review_count} Google Reviews)" if rating and review_count else ""

    print(f"  ✅ Places OK — {rating}★ / {review_count} reviews / {len(signals)} pitch signals")

    return {
        "places_rating":       rating,
        "places_review_count": review_count_str,
        "places_rating_str":   rating_str,
        "places_has_hours":    has_hours,
        "places_website":      website,
        "sample_reviews":      sample_reviews,
        "pitch_signals":       signals,
        "places_enriched":     True,
    }


# ── Site structure extraction (nav, sub-pages, brand colors) ─────────────────

def _safe_title(label: str) -> str:
    """Title-cases a label without breaking ALL-CAPS tokens like HVAC, FAQ."""
    result = []
    for word in label.strip().split():
        if word.isupper() and len(word) >= 2:
            result.append(word)
        elif word.islower():
            result.append(word.capitalize())
        else:
            result.append(word)
    return " ".join(result)


def extract_nav_pages(base_url: str) -> tuple:
    """
    Fetches the homepage and extracts nav link labels + URLs.
    Returns (nav_labels, nav_urls, confidence) where confidence is "high"|"low"|"none".
    """
    SKIP_LABELS = {
        "privacy policy", "terms", "terms of service", "sitemap",
        "cookie policy", "disclaimer", "legal", "login", "sign in",
        "sign up", "register", "cart", "checkout",
        "facebook", "twitter", "instagram", "youtube", "linkedin",
        "tiktok", "yelp", "houzz", "pinterest",
        "employee portal", "vendor login", "supplier portal",
    }
    PRESERVE_LABELS = {
        "service areas", "service area", "financing", "emergency",
        "emergency service", "coupons", "specials", "offers",
        "schedule", "book online", "locations",
    }
    SKIP_HREF_PATTERNS = [
        "/wp-admin", "/wp-login", "mailto:", "tel:", "sms:",
        "whatsapp", "wa.me", "javascript:",
    ]
    HOME_SYNONYMS = {"home", "homepage", "main", "start", "index"}

    print(f"\n🔍 Extracting nav structure from: {base_url}")

    try:
        resp = requests.get(
            base_url, timeout=12,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        resp.raise_for_status()
        html = resp.text
    except requests.RequestException as e:
        print(f"  ⚠️  Nav fetch failed: {e}")
        return [], {}, "none"

    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
    except ImportError:
        print("  ⚠️  BeautifulSoup not available")
        return [], {}, "none"

    base_parsed = urlparse(base_url)
    base_domain = base_parsed.netloc.lstrip("www.").lower()

    def _canonical(url):
        p = urlparse(url)
        path = p.path.rstrip("/") or "/"
        if p.query:
            keep = [q for q in p.query.split("&")
                    if not q.startswith(("utm_", "ref=", "source=", "fbclid", "gclid"))]
            query = "&".join(keep)
        else:
            query = ""
        return f"{p.netloc.lstrip('www.').lower()}{path}{'?' + query if query else ''}"

    def _is_external(url):
        p = urlparse(url)
        return bool(p.netloc) and p.netloc.lstrip("www.").lower() != base_domain

    def _is_phone_label(label):
        digits = _re.sub(r"[\s\-\(\)\+\.]", "", label)
        return digits.isdigit() and len(digits) >= 7

    primary_zones = soup.find_all(["nav", "header"])
    menu_pattern  = _re.compile(r"\b(nav|menu|navigation|navbar|main-menu|primary-menu|site-nav)\b", _re.I)
    class_zones   = (
        soup.find_all(True, class_=menu_pattern) +
        soup.find_all(True, id=menu_pattern)
    )
    seen_ids = {id(z) for z in primary_zones}
    extra_zones = [z for z in class_zones if id(z) not in seen_ids]

    if primary_zones or extra_zones:
        search_zones = primary_zones + extra_zones
        confidence   = "high"
    else:
        search_zones = [soup.body] if soup.body else []
        confidence   = "low"
        print("  ⚠️  No <nav>/<header>/menu elements — falling back to body scan")

    seen_canonical = set()
    home_pair  = None
    other_pairs = []

    for zone in search_zones:
        if not zone:
            continue
        for a in zone.find_all("a", href=True):
            href  = a["href"].strip()
            label = a.get_text(separator=" ", strip=True)
            if not label or len(label) < 2 or len(label) > 60:
                continue
            if _is_phone_label(label):
                continue
            label_lower = label.lower()
            if label_lower in SKIP_LABELS and label_lower not in PRESERVE_LABELS:
                continue
            if any(p in href for p in SKIP_HREF_PATTERNS):
                continue
            if href.startswith("#"):
                continue
            full_url = urljoin(base_url, href)
            if _is_external(full_url):
                continue
            canon = _canonical(full_url)
            if canon in seen_canonical:
                continue
            seen_canonical.add(canon)
            clean_label = _safe_title(label)
            if label_lower in HOME_SYNONYMS:
                if home_pair is None:
                    home_pair = (clean_label, full_url)
            else:
                other_pairs.append((clean_label, full_url))

    if home_pair:
        ordered_pairs = [home_pair] + other_pairs
    else:
        ordered_pairs = [("Home", base_url.rstrip("/") + "/")] + other_pairs

    ordered_pairs = ordered_pairs[:8]
    nav_labels = [l for l, _ in ordered_pairs]
    nav_urls   = {l: u for l, u in ordered_pairs}

    if len(nav_labels) <= 1:
        confidence = "none" if not nav_labels else "low"

    print(f"  ✅ Nav [{confidence}]: {' | '.join(nav_labels)}" if nav_labels
          else "  ⚠️  No nav links found")

    return nav_labels, nav_urls, confidence


def fetch_subpage_content(nav_urls: dict, max_pages: int = 6) -> dict:
    """
    Fetches up to max_pages sub-pages. Extracts headings, img count, body copy.
    Returns {label: {url, headings, img_count, copy, word_count, status}}
    """
    subpage_content = {}
    count = 0

    for label, url in list(nav_urls.items())[:max_pages]:
        if label.lower() == "home":
            subpage_content[label] = {
                "url": url, "headings": [], "img_count": 0,
                "copy": "", "word_count": 0, "status": "skipped"
            }
            continue

        print(f"  📄 Fetching: {label} → {url}")
        try:
            resp = requests.get(
                url, timeout=12,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            resp.raise_for_status()

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")

            headings = [
                h.get_text(strip=True)
                for h in soup.find_all(["h1", "h2", "h3"])[:8]
                if h.get_text(strip=True)
            ]
            img_count = len(soup.find_all("img"))

            for tag in soup.find_all("header", attrs={"role": "banner"}):
                tag.decompose()
            for tag in soup.find_all(True, class_=_re.compile(r"\bsite-header\b|\bpage-header\b", _re.I)):
                tag.decompose()
            for tag in soup.find_all(["nav", "footer", "script", "style", "svg"]):
                tag.decompose()

            words = soup.get_text(separator=" ", strip=True).split()
            word_count = len(words)

            if word_count < 25:
                print(f"    ⚠️  {label}: {word_count} words — possible challenge page")
                subpage_content[label] = {
                    "url": url, "headings": headings, "img_count": img_count,
                    "copy": "", "word_count": word_count, "status": "empty"
                }
                continue

            raw_snippet = " ".join(words)[:750]
            last_period = max(raw_snippet.rfind(". "), raw_snippet.rfind("! "), raw_snippet.rfind("? "))
            copy_snippet = raw_snippet[:last_period + 1] if last_period > 200 else raw_snippet[:700]

            subpage_content[label] = {
                "url":        url,
                "headings":   headings,
                "img_count":  img_count,
                "copy":       copy_snippet,
                "word_count": word_count,
                "status":     "ok",
            }
            count += 1
            print(f"    ✅ {label}: {len(headings)} headings, {img_count} imgs, {len(copy_snippet)} chars")

        except requests.RequestException as e:
            print(f"    ⚠️  {label} fetch failed: {e}")
            subpage_content[label] = {
                "url": url, "headings": [], "img_count": 0,
                "copy": "", "word_count": 0, "status": "fetch_failed"
            }
        except Exception as e:
            print(f"    ⚠️  {label} parse failed: {e}")
            subpage_content[label] = {
                "url": url, "headings": [], "img_count": 0,
                "copy": "", "word_count": 0, "status": "parse_failed"
            }

    print(f"  ✅ Sub-pages done: {count} OK")
    return subpage_content


def extract_brand_colors(url: str) -> str:
    """
    3-stage priority: theme-color meta → CSS variables → inline <style> hex.
    Returns comma-separated string of max 2 hex colors, or "".
    """
    EXCLUDE_6 = {
        "ffffff", "000000", "f0f0f0", "eeeeee", "cccccc", "999999",
        "333333", "666666", "f5f5f5", "fafafa", "e0e0e0", "d0d0d0",
        "1c1c1c", "212121", "111111", "222222", "444444", "555555",
        "777777", "888888", "aaaaaa", "bbbbbb", "dddddd", "e8e8e8",
        "f8f8f8", "1a1a1a", "2a2a2a", "3a3a3a", "4a4a4a",
        "3b5998", "1da1f2",
    }

    def _norm6(h):
        h = h.lstrip("#").lower()
        return "".join(c * 2 for c in h) if len(h) == 3 else h

    def _is_brand_color(hex6):
        if hex6 in EXCLUDE_6:
            return False
        try:
            r, g, b = int(hex6[0:2], 16), int(hex6[2:4], 16), int(hex6[4:6], 16)
            lightness = (max(r, g, b) + min(r, g, b)) / 2
            if lightness < 20 or lightness > 235:
                return False
            saturation = (max(r, g, b) - min(r, g, b)) / max(max(r, g, b), 1)
            return saturation > 0.25
        except Exception:
            return False

    print(f"  🎨 Extracting brand colors from: {url}")
    try:
        resp = requests.get(
            url, timeout=12,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        html = resp.text
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
    except Exception as e:
        print(f"    ⚠️  Color fetch failed: {e}")
        return ""

    collected = []
    seen = set()

    def _try_add(raw):
        h = _norm6(raw)
        if len(h) != 6:
            return False
        if h in seen or not _is_brand_color(h):
            return False
        seen.add(h)
        collected.append("#" + h)
        return True

    tag = soup.find("meta", attrs={"name": "theme-color"})
    if tag and tag.get("content", "").strip().startswith("#"):
        if _try_add(tag["content"].strip()):
            print(f"    ✅ theme-color: {collected[-1]}")

    if len(collected) < 2:
        css_var_re = _re.compile(
            r"--(?:brand|primary|accent|main|color|theme)[^:]*:\s*(#[0-9a-fA-F]{3,6})",
            _re.IGNORECASE
        )
        for style in soup.find_all("style"):
            for m in css_var_re.finditer(style.get_text()):
                if _try_add(m.group(1)):
                    print(f"    ✅ CSS var: {collected[-1]}")
                if len(collected) >= 2:
                    break
            if len(collected) >= 2:
                break

    if len(collected) < 2:
        hex_re = _re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
        for style in soup.find_all("style"):
            for m in hex_re.finditer(style.get_text()):
                if _try_add(m.group(0)):
                    print(f"    ✅ Style hex: {collected[-1]}")
                if len(collected) >= 2:
                    break
            if len(collected) >= 2:
                break

    if collected:
        result = ", ".join(collected[:2])
        print(f"    ✅ Brand colors: {result}")
        return result

    print("    ⚠️  No brand colors found — niche defaults will apply")
    return ""


# ── Merge + finalize ──────────────────────────────────────────────────────────
def build_structured_input(firecrawl: dict, gbp: dict, places: dict, args,
                           nav_labels=None, nav_urls=None, subpage_content=None,
                           brand_colors="", nav_confidence="none") -> dict:
    """
    Merges Firecrawl + GBP + Places + nav structure data into structured_input.json.
    """
    nav_labels      = nav_labels or []
    nav_urls        = nav_urls or {}
    subpage_content = subpage_content or {}
    business_name = (
        firecrawl.get("business_name")
        or args.business
        or "Unknown Business"
    ).strip()

    phone_raw = (
        firecrawl.get("phone")
        or gbp.get("phone_gbp")
        or ""
    ).strip()
    phone_digits_only = "".join(c for c in phone_raw if c.isdigit())
    if len(phone_digits_only) == 11 and phone_digits_only.startswith("1"):
        phone_digits_only = phone_digits_only[1:]
    if len(phone_digits_only) == 10:
        phone = f"({phone_digits_only[:3]}) {phone_digits_only[3:6]}-{phone_digits_only[6:]}"
    else:
        phone = phone_raw

    city_province = (
        args.city
        or firecrawl.get("city")
        or ""
    ).strip()

    services_raw = firecrawl.get("services") or []
    services_list = ", ".join(services_raw) if services_raw else ""

    neighborhoods_raw = firecrawl.get("neighborhoods") or []
    vague = {"greater toronto area", "gta", "greater vancouver", "lower mainland",
             "greater area", "metro area", "surrounding areas", "and surrounding"}
    neighborhoods_clean = [
        n for n in neighborhoods_raw
        if n.lower().strip() not in vague and len(n) > 2
    ]
    if not neighborhoods_clean:
        gbp_area = gbp.get("service_area") or gbp.get("neighborhood") or ""
        if gbp_area and isinstance(gbp_area, str):
            neighborhoods_clean = [a.strip() for a in gbp_area.split(",") if a.strip()]
    service_areas = ", ".join(neighborhoods_clean) if neighborhoods_clean else city_province

    reviews_3 = gbp.get("reviews", [])[:3]
    reviews_formatted = "\n".join([
        f'Review {i+1}: "{r}"' for i, r in enumerate(reviews_3)
    ]) if reviews_3 else "(No reviews extracted — add manually)"

    years     = firecrawl.get("years_in_business", "")
    emergency = firecrawl.get("emergency", "no")
    logo_url  = firecrawl.get("logo_url", "")
    photo_urls = firecrawl.get("photo_urls") or gbp.get("gbp_photos") or []

    detection_text = firecrawl.get("raw_text_sample", "") or business_name
    niche = detect_niche(detection_text)
    if args.niche:
        niche = args.niche

    # Rating: prefer Places (more reliable), then GBP
    rating_str = places.get("places_rating_str", "")
    review_count_str = places.get("places_review_count", "")
    if not rating_str and gbp.get("rating") and gbp.get("review_count"):
        rating_str = f"{gbp['rating']}★ ({gbp['review_count']} Google Reviews)"
        review_count_str = str(gbp.get("review_count", ""))

    output = {
        "_meta": {
            "source_url":       args.url or "",
            "extracted_at":     __import__("datetime").datetime.now().isoformat(),
            "niche":            niche,
            "place_id":         gbp.get("place_id", ""),
            "firecrawl_ok":     bool(firecrawl),
            "gbp_ok":           bool(gbp),
            "places_enriched":  places.get("places_enriched", False),
            "pitch_signals":    places.get("pitch_signals", []),
            "nav_confidence":   nav_confidence,
        },

        # ── 6 core prompt variables ───────────────────────────────────────────
        "BUSINESS_NAME":  business_name,
        "PHONE":          phone,
        "CITY_PROVINCE":  city_province,
        "SERVICES_LIST":  services_list,
        "SERVICE_AREAS":  service_areas,
        "REVIEWS_3":      reviews_formatted,

        # ── Optional variables ────────────────────────────────────────────────
        "YEARS_IN_BUSINESS": years,
        "EMERGENCY":         emergency,
        "RATING_STRING":     rating_str,
        "REVIEW_COUNT":      review_count_str,
        "LOGO_URL":          logo_url,
        "PHOTO_URLS":        photo_urls[:3],

        # ── Site structure (for multi-page demo generation) ───────────────────
        "NAV_PAGES":       nav_labels,
        "NAV_URLS":        nav_urls,
        "SUBPAGE_CONTENT": subpage_content,
        "BRAND_COLORS":    brand_colors,
        "NAV_CONFIDENCE":  nav_confidence,

        # ── Raw data for debugging ────────────────────────────────────────────
        "_raw": {
            "hours":        firecrawl.get("hours") or gbp.get("hours_gbp", ""),
            "email":        firecrawl.get("email", ""),
            "tagline":      firecrawl.get("tagline", ""),
            "address":      firecrawl.get("address") or gbp.get("address_gbp", ""),
            "all_reviews":  gbp.get("reviews", []),
            "sample_reviews_places": places.get("sample_reviews", []),
        }
    }

    return output


# ── Prospects CSV ─────────────────────────────────────────────────────────────
def upsert_prospect_csv(result: dict, url: str) -> None:
    PROSPECTS_CSV.parent.mkdir(parents=True, exist_ok=True)

    today      = date.today().isoformat()
    niche      = result.get("_meta", {}).get("niche", "")
    name       = result.get("BUSINESS_NAME", "")
    url_key    = url.strip().rstrip("/").lower()

    existing_rows: list[dict] = []
    if PROSPECTS_CSV.exists():
        with open(PROSPECTS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_rows.append(dict(row))

    matched_idx = None
    for i, row in enumerate(existing_rows):
        if row.get("url", "").strip().rstrip("/").lower() == url_key:
            matched_idx = i
            break

    if matched_idx is not None:
        existing_rows[matched_idx]["audit_date"] = today
        action = "updated audit_date for existing entry"
    else:
        new_row = {h: "" for h in PROSPECTS_HEADERS}
        new_row.update({
            "url":           url.strip(),
            "business_name": name,
            "niche":         niche,
            "audit_date":    today,
            "audit_score":   "",
            "status":        "prospect",
        })
        existing_rows.append(new_row)
        action = "added new entry"

    with open(PROSPECTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=PROSPECTS_HEADERS, extrasaction="ignore"
        )
        writer.writeheader()
        for row in existing_rows:
            padded = {h: row.get(h, "") for h in PROSPECTS_HEADERS}
            writer.writerow(padded)

    print(f"  📋 prospects.csv {action} — {PROSPECTS_CSV}")


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Extract business data from website + GBP")
    parser.add_argument("--url",       help="Website URL to scrape")
    parser.add_argument("--business",  help="Business name (for GBP search)")
    parser.add_argument("--city",      help="City and province, e.g. 'Mississauga ON'")
    parser.add_argument("--niche",     help="Override niche detection (e.g. plumbing)")
    parser.add_argument("--output",    default="output/structured_input.json",
                        help="Output file path (default: output/structured_input.json)")
    parser.add_argument("--no-places", action="store_true", default=False,
                        help="Skip Google Places API enrichment (saves cost during testing)")
    args = parser.parse_args()

    if not args.url and not args.business:
        print("❌ Provide --url and/or --business + --city")
        sys.exit(1)

    firecrawl_data = {}
    gbp_data       = {}
    places_data    = {}

    # Site scrape
    if args.url:
        if SCRAPE_PROVIDER == "jina":
            firecrawl_data = scrape_with_jina(args.url)
        elif FIRECRAWL_KEY:
            firecrawl_data = scrape_with_firecrawl(args.url)

    # ── Site structure extraction (nav, sub-pages, brand colors) ─────────────
    nav_labels, nav_urls, nav_confidence = (
        extract_nav_pages(args.url) if args.url else ([], {}, "none")
    )
    subpage_content = fetch_subpage_content(nav_urls) if nav_urls else {}
    brand_colors    = extract_brand_colors(args.url) if args.url else ""

    # GBP pull
    if GBP_PROVIDER:
        business = args.business or firecrawl_data.get("business_name", "")
        city     = args.city     or firecrawl_data.get("city", "")
        if GBP_PROVIDER == "scrapingdog":
            gbp_data = pull_gbp_scrapingdog(business_name=business, city=city, url=args.url or "")
        else:
            gbp_data = pull_gbp_data(business_name=business, city=city, url=args.url or "")

    # Google Places enrichment
    if not args.no_places and GOOGLE_PLACES_KEY:
        business = args.business or firecrawl_data.get("business_name", "")
        city     = args.city     or firecrawl_data.get("city", "")
        if business and city:
            places_data = enrich_with_places(business, city)
        else:
            print("⚠️  Places skipped — business name or city not available yet")

    # Merge
    result = build_structured_input(
        firecrawl_data, gbp_data, places_data, args,
        nav_labels=nav_labels,
        nav_urls=nav_urls,
        subpage_content=subpage_content,
        brand_colors=brand_colors,
        nav_confidence=nav_confidence,
    )

    # Save
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    prospect_url = args.url or result.get("BUSINESS_NAME", "unknown")
    upsert_prospect_csv(result, prospect_url)

    print(f"\n{'='*60}")
    print(f"✅ Extraction complete — {out_path}")
    print(f"{'='*60}")
    print(f"  Business:       {result['BUSINESS_NAME']}")
    print(f"  Phone:          {result['PHONE']}")
    print(f"  City:           {result['CITY_PROVINCE']}")
    print(f"  Niche:          {result['_meta']['niche']}")
    print(f"  Services:       {result['SERVICES_LIST'][:60]}{'...' if len(result['SERVICES_LIST']) > 60 else ''}")
    print(f"  Reviews:        {len(gbp_data.get('reviews', []))} extracted")
    print(f"  Rating:         {result['RATING_STRING']}")
    print(f"  Logo URL:       {'✅' if result['LOGO_URL'] else '⚠️  Not found — add manually'}")
    print(f"  Photos:         {len(result['PHOTO_URLS'])} URLs extracted")
    print(f"  Places enriched: {result['_meta']['places_enriched']}")
    if result['_meta'].get('pitch_signals'):
        print(f"  Pitch signals:")
        for s in result['_meta']['pitch_signals']:
            print(f"    → {s[:80]}")
    print(f"\n  Next step: python3 execution/generate_website.py --input {out_path} --mode bolt")


if __name__ == "__main__":
    main()
