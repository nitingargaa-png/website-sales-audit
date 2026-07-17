"""
discover.py — Places API (New) searchText.

Slice 0 (2026-07-16, live) established: one searchText call with an
Enterprise-tier field mask returns all four contract fields —
rating, userRatingCount, websiteUri, nationalPhoneNumber. There is no
Details round trip. Stage 3 of the original design does not exist.

Field mask sets the billing SKU. Requesting websiteUri or
nationalPhoneNumber puts the whole request on Enterprise (~$40/1000).
Dropping them would drop to Pro, but then every survivor needs a
Details call at $5/1000 — strictly worse at any realistic reject rate.
Do not "optimize" the mask without re-running that arithmetic.

primaryType / primaryTypeDisplayName are requested because Slice 0 did
NOT request them and a conclusion was nearly drawn from their absence.
Their real value is an open question as of Slice 1 — read them on the
first live run before deciding what gbp_category carries.

TRADE IS A PROPERTY OF THE SEARCH, NOT THE BUSINESS. A prospect found by
"garage door repair Mississauga ON" gets trade="garage door" because that
query found it. A parts supplier that ranks for the same query gets the
same trade and is not a prospect. Known limitation, carried explicitly;
Slice 2's reject-reading is where it surfaces.
"""
import json
import os
import time
import urllib.error
import urllib.request
from typing import Dict, List, Optional

from sourcing import cache as cache_mod

ENDPOINT = "https://places.googleapis.com/v1/places:searchText"

FIELDS = [
    "id",
    "displayName",
    "formattedAddress",
    "addressComponents",
    "types",
    "primaryType",
    "primaryTypeDisplayName",
    "businessStatus",
    "rating",
    "userRatingCount",
    "websiteUri",
    "nationalPhoneNumber",
]
FIELD_MASK = ",".join("places." + f for f in FIELDS) + ",nextPageToken"

PAGE_SIZE = 20      # API max
MAX_PAGES = 3       # API caps at 60 results per query
RATE_LIMIT_S = 1.0  # 1 rps — ported from lead-engine/src/scrapers/google-data.js

_last_call = 0.0


def _throttle() -> None:
    global _last_call
    wait = RATE_LIMIT_S - (time.time() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.time()


def _post(query: str, key: str, page_token: Optional[str] = None) -> Dict:
    body = {"textQuery": query, "pageSize": PAGE_SIZE}
    if page_token:
        body["pageToken"] = page_token
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": key,
            "X-Goog-FieldMask": FIELD_MASK,
        },
    )
    _throttle()
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def search(trade: str, city: str, key: str,
           max_pages: int = MAX_PAGES,
           use_cache: bool = True,
           cache_dir: str = cache_mod.CACHE_DIR) -> List[Dict]:
    """
    Returns raw Places dicts, annotated with the query that found them.

    Raises on HTTP error rather than swallowing — a 403 on page 1 means
    the key or the API enablement is wrong, and every later page will
    fail the same way. Failing loudly on the first call is cheaper than
    a silent empty batch.

    Caching is per PAGE, because a page is what Places bills. A resumed
    or repeated grid costs nothing for cells already fetched, and returns
    the same rows — Places result sets jitter between runs (277 vs 275 an
    hour apart on 2026-07-17), which silently changed a
    multi_location_domain verdict. Cached cells are deterministic.
    """
    query = f"{trade} {city}"
    out: List[Dict] = []
    token = None

    for page in range(max_pages):
        page_key = token or ""
        hit = (cache_mod.get(trade, city, page_key, cache_dir=cache_dir)
               if use_cache else None)
        if hit is not None:
            places = hit["places"]
            d = {"nextPageToken": hit.get("next")}
            print(f"            [cache] page {page + 1}: {len(places)} rows")
        else:
            try:
                d = _post(query, key, token)
            except urllib.error.HTTPError as e:
                detail = e.read().decode("utf-8", "replace")[:400]
                raise SystemExit(
                    f"Places API {e.code} on '{query}' page {page + 1}: "
                    f"{detail}")
            places = d.get("places", [])
            cache_mod.put(trade, city, places, page_key,
                          cache_dir=cache_dir,
                          next_token=d.get("nextPageToken"))

        for p in places:
            # _query_* are provenance, not Places fields. Downstream reads
            # trade from here. See module docstring.
            p["_query_trade"] = trade
            p["_query_city"] = city
        out.extend(places)

        token = d.get("nextPageToken")
        if not token:
            break
        # next_page_token needs a beat to become valid — legacy API needed
        # ~2s; New is faster but not instant.
        time.sleep(2)

    return out
