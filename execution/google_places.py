"""
google_places.py
----------------
Google Places API (New) integration for the lead enrichment pipeline.

Setup:
  1. Enable "Places API (New)" at console.cloud.google.com
  2. Create an API key restricted to Places API only
  3. Add to your .env file:  GOOGLE_PLACES_API_KEY=your_key_here

Cost reference:
  Text Search   → $0.032 / request
  Place Details → $0.017 / request
  Total per prospect ≈ $0.05  (~$5.00 per 100 prospects)
"""

import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────

PLACES_API_KEY: str = os.getenv("GOOGLE_PLACES_API_KEY", "")

BASE_URL = "https://places.googleapis.com/v1"

# Fields pulled in Place Details — only pay for what you request
DETAIL_FIELDS = (
    "rating,"
    "userRatingCount,"
    "reviews,"
    "regularOpeningHours,"
    "websiteUri,"
    "nationalPhoneNumber,"
    "formattedAddress,"
    "businessStatus"
)


# ── Core calls ────────────────────────────────────────────────────────────────

def find_place_id(business_name: str, city: str) -> Optional[str]:
    """
    Text Search → returns the best-match place_id for a business.

    Returns None if:
      - No results found
      - API key is missing / invalid
      - Request fails
    """
    if not PLACES_API_KEY:
        logger.warning("GOOGLE_PLACES_API_KEY not set — skipping Places lookup")
        return None

    url = f"{BASE_URL}/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": PLACES_API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName",
    }
    payload = {"textQuery": f"{business_name} {city}"}

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        r.raise_for_status()
        places = r.json().get("places", [])
        if not places:
            logger.info(f"No Places results for: {business_name} {city}")
            return None
        place_id = places[0]["id"]
        logger.info(f"Found place_id={place_id} for {business_name}")
        return place_id
    except requests.RequestException as e:
        logger.error(f"Places Text Search failed for {business_name}: {e}")
        return None


def get_place_details(place_id: str) -> dict:
    """
    Place Details → returns rating, reviews, hours, contact info.

    Returns empty dict on failure so callers can safely use .get()
    """
    if not PLACES_API_KEY:
        return {}

    url = f"{BASE_URL}/places/{place_id}"
    headers = {
        "X-Goog-Api-Key": PLACES_API_KEY,
        "X-Goog-FieldMask": DETAIL_FIELDS,
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        logger.error(f"Places Detail fetch failed for {place_id}: {e}")
        return {}


# ── Enrichment helper (called from lead_pipeline.py) ─────────────────────────

def enrich_prospect_with_places(prospect: dict) -> dict:
    """
    Main entry point for the pipeline.

    Adds the following keys to the prospect dict:
      google_rating         float | None
      review_count          int   | None
      sample_reviews        list  (up to 3 review dicts)
      has_hours_listed      bool
      places_website        str   | None   (cross-check vs scraped site)
      places_phone          str   | None
      places_address        str   | None
      business_status       str   | None   ("OPERATIONAL", "CLOSED_PERMANENTLY", etc.)
      places_audit_signals  list  (human-readable flags for Claude to use)
      place_id              str   | None
    """
    business_name = prospect.get("business_name", "")
    city = prospect.get("city", "") or prospect.get("location", "")

    if not business_name or not city:
        logger.warning("Missing business_name or city — skipping Places enrichment")
        return prospect

    place_id = find_place_id(business_name, city)
    prospect["place_id"] = place_id

    if not place_id:
        prospect["places_audit_signals"] = ["⚠️ Not found on Google Places — GBP setup opportunity"]
        return prospect

    details = get_place_details(place_id)

    # ── Core fields
    prospect["google_rating"]    = details.get("rating")
    prospect["review_count"]     = details.get("userRatingCount")
    prospect["has_hours_listed"] = bool(details.get("regularOpeningHours"))
    prospect["places_website"]   = details.get("websiteUri")
    prospect["places_phone"]     = details.get("nationalPhoneNumber")
    prospect["places_address"]   = details.get("formattedAddress")
    prospect["business_status"]  = details.get("businessStatus")

    # ── Sample reviews (top 3, strip verbose fields)
    raw_reviews = details.get("reviews", [])[:3]
    prospect["sample_reviews"] = [
        {
            "author":   r.get("authorAttribution", {}).get("displayName", ""),
            "rating":   r.get("rating"),
            "text":     r.get("text", {}).get("text", ""),
            "relative": r.get("relativePublishTimeDescription", ""),
        }
        for r in raw_reviews
    ]

    # ── Audit signals for Claude outreach personalisation
    prospect["places_audit_signals"] = _build_audit_signals(prospect)

    return prospect


# ── Signal builder ─────────────────────────────────────────────────────────────

def _build_audit_signals(p: dict) -> list[str]:
    """
    Translates Places data into actionable GHL pitch angles.
    These are injected into the Claude prompt in claude_extractor.py.
    """
    signals = []
    rating       = p.get("google_rating")
    review_count = p.get("review_count", 0) or 0
    has_hours    = p.get("has_hours_listed")
    reviews      = p.get("sample_reviews", [])

    # ── Reputation signals
    if rating and rating >= 4.7 and review_count >= 50:
        signals.append(
            f"STRONG REPUTATION ({rating}* / {review_count} reviews) — "
            "hidden from website; showcasing it = instant trust lift"
        )
    elif rating and rating < 4.0 and review_count >= 10:
        signals.append(
            f"BELOW-AVERAGE RATING ({rating}*) — "
            "review recovery workflow is a high-priority pitch"
        )
    elif review_count < 20:
        signals.append(
            f"LOW REVIEW VOLUME ({review_count} reviews) — "
            "automated review request workflow pitch"
        )

    # ── Hours
    if not has_hours:
        signals.append(
            "NO BUSINESS HOURS ON GOOGLE — "
            "GBP optimisation + GHL booking page angle"
        )

    # ── Review content patterns
    negative_keywords = ["slow", "no call", "didn't call", "voicemail", "no response", "wait"]
    for rev in reviews:
        text = rev.get("text", "").lower()
        if any(kw in text for kw in negative_keywords):
            signals.append(
                "RECENT REVIEW MENTIONS SLOW/MISSED RESPONSE — "
                "missed-call text-back is the lead hook"
            )
            break  # one signal is enough

    # ── Website mismatch
    scraped_site   = p.get("website", "")
    places_website = p.get("places_website", "")
    if scraped_site and places_website and scraped_site not in places_website:
        signals.append(
            "WEBSITE ON GOOGLE DOESN'T MATCH SCRAPED URL — "
            "possible outdated GBP listing"
        )

    return signals
