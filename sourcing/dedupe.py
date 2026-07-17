"""
dedupe.py — place_id only, plus batch-scoped shared-domain detection.

DEDUPE ON place_id. NEVER ON NAME.
v4.6 normalised business names and deduped on the result. Two real,
separate businesses called "A1 Garage Door" in different cities collapse
into one row and you lose a prospect silently. place_id is Google's
identity for a location and is the only safe key.

MULTI-LOCATION IS NOT A DEDUPE.
Rows sharing a registrable domain are not duplicates — they are either one
operator with several locations, or several franchisees under one brand
site. Both are real rows worth keeping and both need a human look, so the
rule flags and does not drop.

BATCH-SCOPED, KNOWN LIMITATION.
The count is over the current batch only. A four-location operator that
surfaces two rows in a 100-batch is not flagged; the same operator in a
500-batch might be. Accepted for now. Fixing it means persisting domain
counts across batches, which is a different piece of infrastructure.

GRID DESIGN MATTERS HERE. Adjacent cities share operators: nearly every
Mississauga plumber also serves Brampton, so a Mississauga x Brampton grid
fires this rule on genuine service-area overlap and tells you nothing
about franchises. Mississauga x Hamilton makes a shared-domain hit mean
something.
"""
from collections import Counter
from typing import Dict, List, Tuple

MULTI_LOCATION_THRESHOLD = 3   # >=3 rows on one domain -> flag


def dedupe_by_place_id(rows: List[Dict]) -> Tuple[List[Dict], int]:
    """First occurrence wins. Returns (rows, n_dropped)."""
    seen = set()
    out = []
    for r in rows:
        pid = r.get("gbp_place_id")
        if pid and pid in seen:
            continue
        if pid:
            seen.add(pid)
        out.append(r)
    return out, len(rows) - len(out)


def flag_multi_location(rows: List[Dict],
                        threshold: int = MULTI_LOCATION_THRESHOLD
                        ) -> List[Dict]:
    """Sets multi_location_domain on every row of an over-threshold domain."""
    counts = Counter(r.get("domain") for r in rows if r.get("domain"))
    hot = {d for d, n in counts.items() if n >= threshold}
    for r in rows:
        r["multi_location_domain"] = bool(r.get("domain") in hot)
    return rows


def domain_counts(rows: List[Dict]) -> Counter:
    return Counter(r.get("domain") for r in rows if r.get("domain"))
