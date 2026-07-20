"""
rebuild_leads.py — the broken-site consumer.

render.fetch returns html=None for a site that would not load. audit_batch
used to print "ABORT" and drop it. But a business with a GBP listing, reviews,
and a website that does not load is the STRONGEST rebuild pitch there is: they
are losing every customer who clicks their listing, right now, and do not know
it. This module records those aborts as leads instead of discarding them.

It is the sibling of sourcing/emit.write_no_website_book. Same permanent,
synced OneDrive destination (animo_leads/), same append-and-dedup discipline,
same first_seen-preserved-across-runs contract. Two rebuild lanes — no_website
(never had a site) and broken_site (has one, it is down) — living side by side,
both pitched "you need a working site, I build those".

DEDUP KEY IS THE URL, lowercased and trimmed. A broken site always has a URL
(that is how we tried and failed to load it) — unlike the no_website book,
which has no URL and must key on phone. So this book has no no-phone-dup
problem the no_website book has. One clean key.
"""
import csv
import datetime as dt
import os
from typing import Dict, List, Optional

from audit.abort_reason import TAG_MEANING

# Columns for a broken-site lead. url + tag are what you act on; the plain
# meaning is carried so the CSV is readable without this code in front of you.
# gbp_* fields come from the sourcing row when available (the audit queue
# carries them), so a caller CAN pass business_name/phone/city for outreach —
# but the module works with url+tag alone.
BOOK_FIELDS = ["url", "tag", "meaning", "business_name", "phone", "city",
               "trade", "first_seen", "last_seen"]


def _norm_url(url: str) -> str:
    return (url or "").strip().rstrip("/").lower()


def capture_broken_site(url: str, tag: str, book_path: str,
                        meta: Optional[Dict] = None) -> Dict[str, int]:
    """
    Append one broken-site lead to book_path, dedup on normalized URL.

    If the URL is already in the book, first_seen is preserved and last_seen
    is refreshed to today (so a lead that stays broken across runs shows how
    long it has been down — a stronger pitch than a single date). tag is
    updated too: a site that was site_down_slow last week and domain_dead
    today has genuinely changed, and the latest read is the truthful one.

    meta is an optional dict of {business_name, phone, city, trade} from the
    sourcing row, so the lead is actionable (phone to call) not just a URL.

    Returns {total, added, updated}.
    """
    meta = meta or {}
    today = dt.date.today().isoformat()
    nurl = _norm_url(url)

    rows: List[Dict] = []
    if os.path.exists(book_path):
        with open(book_path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

    added = updated = 0
    found = False
    for r in rows:
        if _norm_url(r.get("url", "")) == nurl:
            found = True
            r["tag"] = tag
            r["meaning"] = TAG_MEANING.get(tag, "")
            r["last_seen"] = today
            # backfill any meta that was missing before (e.g. first captured
            # from an abort with no sourcing row, now enriched)
            for k in ("business_name", "phone", "city", "trade"):
                if not r.get(k) and meta.get(k):
                    r[k] = meta[k]
            updated += 1
            break

    if not found:
        rows.append({
            "url": url.strip(),
            "tag": tag,
            "meaning": TAG_MEANING.get(tag, ""),
            "business_name": meta.get("business_name", ""),
            "phone": meta.get("phone", ""),
            "city": meta.get("city", ""),
            "trade": meta.get("trade", ""),
            "first_seen": today,
            "last_seen": today,
        })
        added += 1

    os.makedirs(os.path.dirname(book_path) or ".", exist_ok=True)
    tmp = book_path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=BOOK_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, book_path)   # atomic — a crash mid-write cannot truncate

    return {"total": len(rows), "added": added, "updated": updated}
