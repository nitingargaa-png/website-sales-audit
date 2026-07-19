"""
normalize.py — raw Places dict -> contract row.

No owner_name / owner_source. Both were cut 2026-07-17 after two probes
measured 0% coverage against a 40-70% expectation. See emit.py for the
measurement and the reason. Do not re-add without a source that fills them.

Slice 1 does no filtering. Every row comes out status="clean" except the
no_website lane, which is a deterministic fact and not a judgment. Filters
land in Slice 2 (sourcing/status.py).

City extraction prefers addressComponents (structured) over parsing
formattedAddress (a string that varies by country). Falls back to the
query city, which is what was searched and is right often enough for
Slice 1. Verify on the first live run.
"""
from typing import Dict, List, Optional
from urllib.parse import (parse_qsl, urlencode, urlparse, urlsplit,
                          urlunsplit)

# Suffixes where the registrable domain is three labels, not two.
COMPOUND_SUFFIXES = {"co.uk", "com.au", "co.nz", "co.za", "com.br", "co.jp"}

# Tracking params Places hands back on the business's registered websiteUri.
# Seen live 2026-07-17:
#   bmgaragedoor.com/ca?utm_source=GoogleMyBusiness&utm_medium=...&utm_campaign=LIMMO
#   doddsdoors.com/location/mississauga/?utm_source=google&utm_medium=organic
# These do NOT affect dedupe (that is place_id) and do NOT affect domain_of()
# (urlparse().netloc never sees the query). The problem is narrower: the url
# column feeds audit_batch.py, so PSI measures a tracked URL and the report
# shows one to the prospect. Strip them from the emitted url only.
TRACKING_PREFIXES = ("utm_", "gclid", "fbclid", "mc_", "_hs", "msclkid",
                     "dclid", "yclid", "igshid", "ref_", "campaignid")


def strip_tracking(url: Optional[str]) -> Optional[str]:
    """
    Remove tracking params, keep everything else.

    Conservative: only known tracking prefixes are dropped. A query param
    that is not on the list stays, because some sites route real content
    through one (?page=, ?id=). Dropping the whole query string would be
    simpler and would occasionally fetch the wrong page.
    """
    if not url:
        return url
    parts = urlsplit(url)
    if not parts.query:
        return url
    kept = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
            if not any(k.lower().startswith(p) for p in TRACKING_PREFIXES)]
    return urlunsplit((parts.scheme, parts.netloc, parts.path,
                       urlencode(kept), parts.fragment))


def domain_of(url: Optional[str]) -> str:
    """Registrable domain, lowercased, no www. '' when absent."""
    if not url:
        return ""
    host = urlparse(url if "//" in url else "https://" + url).netloc.lower()
    host = host.split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    if len(parts) >= 3 and ".".join(parts[-2:]) in COMPOUND_SUFFIXES:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


TOLL_FREE_PREFIXES = {"800", "888", "877", "866", "855", "844", "833"}


def is_toll_free(phone: Optional[str]) -> bool:
    """
    NANP toll-free. Signal only — routed nowhere.

    Note the sign: v4.7 treated toll_free as a risk needing manual review.
    applicability.mctb_applicable treats call_tracking as a STRONG signal
    ("paid ads active — every missed call was paid for"). Same fact,
    opposite sign. It is positive evidence here, carried and not filtered.
    """
    if not phone:
        return False
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return len(digits) == 10 and digits[:3] in TOLL_FREE_PREFIXES


def _city_from_components(p: Dict) -> Optional[str]:
    comps = p.get("addressComponents") or []
    for want in ("locality", "postal_town", "administrative_area_level_2"):
        for c in comps:
            if want in (c.get("types") or []):
                return c.get("longText") or c.get("shortText")
    return None


def to_row(p: Dict) -> Dict:
    name = (p.get("displayName") or {}).get("text") or ""
    url = strip_tracking(p.get("websiteUri") or None)
    phone = p.get("nationalPhoneNumber") or None

    row = {
        "url": url,
        "business_name": name,
        "trade": p.get("_query_trade"),
        "city": _city_from_components(p) or p.get("_query_city"),
        "gbp_place_id": p.get("id"),
        "gbp_rating": p.get("rating"),

        # LOCKED: this column only. Never m["aggregate_review_count"].
        # See emit.py docstring.
        "gbp_review_count": p.get("userRatingCount"),

        "gbp_category": (p.get("primaryTypeDisplayName") or {}).get("text")
                        or p.get("primaryType"),
        "phone": phone,
        "disqualify_reason": None,

        "review_reason": None,
        "toll_free": is_toll_free(phone),
        "multi_location_domain": False,   # Slice 2 (batch-scoped)
        "domain": domain_of(url),
        "gbp_primary_type": p.get("primaryType"),
        "gbp_types": ";".join(p.get("types") or []),
        "business_status": p.get("businessStatus"),
        "query_trade": p.get("_query_trade"),
        "query_city": p.get("_query_city"),
    }

    # no_website lane: deterministic fact, not a judgment. A real prospect
    # the audit cannot read (it needs a URL). Stays clean, stays out of the
    # queue via emit.write_audit_queue's url test.
    row["status"] = "clean"
    if not url:
        row["review_reason"] = "no_website_lane"

    return row


def to_rows(places: List[Dict]) -> List[Dict]:
    return [to_row(p) for p in places]
