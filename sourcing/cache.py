"""
cache.py — grid-cell response cache.

WHAT IS CACHED AND WHY THAT KEY

Places bills per REQUEST, and a request is one page of one grid cell. So
the cache key is the cell, not the business:

    garage door|Mississauga ON|<page_token or "">

lead-engine/src/utils/cache.js keys on `domain` — one row per business.
That is right for a per-business enrichment pass and wrong here: sourcing
never asks Places about a business, it asks about a cell and gets 20 back.
Keying on domain would cache the answers and still re-bill the question.

TTL

7 days, ported in concept from lead-engine's CACHE_TTL_MS. Note that
lead-engine stores `processed_at` but has NO expiry logic in the cache
itself — the TTL lives in the caller (src/scrapers/google-data.js). That
split is easy to lose. Here the cache owns its own expiry.

GBP data is stable: a business's rating, review count, website and phone
do not move meaningfully inside a week. What DOES move is the result SET —
Places returned 277 rows on one 2026-07-17 grid run and 275 on another an
hour later, and `Dr HVAC` fell from 3 rows to 2, dropping below the
multi_location_domain threshold. Caching the cell makes a re-run
deterministic as well as free. See BACKLOG item 3.

STORAGE

One JSON file per cell under sourcing_cache/. Not sqlite: the data is a
handful of KB per cell, write-once, read-rarely, and a directory of JSON
is greppable when a batch looks wrong. lead-engine used sql.js because it
was already a JS project with a bundler; that reason does not carry over.

INVALIDATION

--no-cache skips reads (still writes). --clear-cache empties the dir.
There is deliberately no partial invalidation: the failure mode of a
too-clever cache is serving a stale answer to a question you thought you
were asking fresh.
"""
import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional

CACHE_DIR = "sourcing_cache"
TTL_SECONDS = 7 * 24 * 60 * 60   # 7 days, per lead-engine CACHE_TTL_MS


def _key(trade: str, city: str, page: str = "") -> str:
    raw = f"{trade.lower().strip()}|{city.lower().strip()}|{page}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _path(cache_dir: str, trade: str, city: str, page: str = "") -> str:
    return os.path.join(cache_dir, _key(trade, city, page) + ".json")


def get(trade: str, city: str, page: str = "",
        cache_dir: str = CACHE_DIR,
        ttl: int = TTL_SECONDS) -> Optional[Dict[str, Any]]:
    """
    Returns {"places": [...], "next": token|None} or None if absent/expired.

    The next-page token MUST be cached alongside the rows. A first version
    returned only the places; on a cache hit the caller had no token, so
    the pagination loop broke after page 1 and a cached 60-row cell
    silently became a 20-row cell. Cache the answer AND the continuation.
    """
    p = _path(cache_dir, trade, city, page)
    if not os.path.exists(p):
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            blob = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None  # corrupt or unreadable -> treat as a miss, refetch
    age = time.time() - blob.get("cached_at", 0)
    if age > ttl:
        return None
    return {"places": blob.get("places", []), "next": blob.get("next")}


def put(trade: str, city: str, places: List[Dict[str, Any]],
        page: str = "", cache_dir: str = CACHE_DIR,
        next_token: Optional[str] = None) -> None:
    os.makedirs(cache_dir, exist_ok=True)
    p = _path(cache_dir, trade, city, page)
    blob = {
        "cached_at": time.time(),
        "trade": trade,
        "city": city,
        "page": page,
        "n": len(places),
        "next": next_token,
        "places": places,
    }
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(blob, f)
    os.replace(tmp, p)   # atomic — a killed run leaves no half-written cell


def stats(cache_dir: str = CACHE_DIR,
          ttl: int = TTL_SECONDS) -> Dict[str, Any]:
    if not os.path.isdir(cache_dir):
        return {"cells": 0, "fresh": 0, "stale": 0, "rows": 0}
    fresh = stale = rows = 0
    now = time.time()
    for fn in os.listdir(cache_dir):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(cache_dir, fn), encoding="utf-8") as f:
                b = json.load(f)
        except Exception:
            continue
        if now - b.get("cached_at", 0) > ttl:
            stale += 1
        else:
            fresh += 1
            rows += b.get("n", 0)
    return {"cells": fresh + stale, "fresh": fresh, "stale": stale,
            "rows": rows}


def clear(cache_dir: str = CACHE_DIR) -> int:
    if not os.path.isdir(cache_dir):
        return 0
    n = 0
    for fn in os.listdir(cache_dir):
        if fn.endswith(".json"):
            os.remove(os.path.join(cache_dir, fn))
            n += 1
    return n
