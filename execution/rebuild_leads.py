"""
rebuild_leads.py — turn audit ABORTs into callable rebuild leads.

WHY THIS EXISTS (and why it's a standalone script, not part of the audit)
A site that won't load is not a failure to discard — it's the strongest
rebuild pitch there is: a business with a Google listing and reviews whose
website is DOWN is losing customers right now. But the audit pipeline
(audit_batch.py) only receives bare URLs and aborts before it has any
business data, so it cannot produce a callable lead on its own.

This script joins after the fact, touching NONE of the audit code:
  1. read the sourcing prospect CSV  (business_name, phone, gbp_* per URL)
  2. read the audit queue            (the URLs that were meant to be audited)
  3. scan output/                    (which URLs got a report = audited OK)
  4. the queue URLs with NO report = aborted = broken sites
  5. re-fetch each once to classify WHY (ssl / dns / timeout / 500 / 404 / 401)
  6. join to the prospect row for name + phone
  7. append callable leads to the SAME rebuild_leads.csv the no_website
     book uses — same columns, so the two lead types merge into one file.

Run AFTER an audit batch:  python execution/rebuild_leads.py --input <queue.csv>
"""
import argparse
import csv
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_batch          # for slug() and normalise()
from audit import render    # for the same fetch the audit uses

# Same synced destination as the no_website book, so both lead types
# accumulate in one place. Override with --rebuild-book.
REBUILD_BOOK = os.path.join(
    os.path.expanduser("~"), "OneDrive", "animo_leads", "rebuild_leads.csv")

# Columns match the no_website book plus url + reason, so the two files
# are the same shape and can be concatenated / merged trivially (Piece 3).
FIELDS = ["business_name", "trade", "city", "phone", "url", "reason",
          "gbp_review_count", "gbp_rating", "gbp_category",
          "gbp_place_id", "first_seen"]


def classify_error(url):
    """
    One fetch, mapped to a pitch-shaped reason tag. Returns (reason, None)
    if the site is DOWN (a lead), or (None, "ok") if it actually loads now
    (not a broken-site lead — skip it).
    """
    import requests
    try:
        r = requests.get(url, timeout=20, headers=render.BROWSER_HEADERS)
        code = r.status_code
        if code == 200:
            return None, "ok"            # loads now — not a broken lead
        if code in (202, 403, 429, 503):
            # bot-wall: the audit recovers these via Jina, so a missing
            # report means Jina ALSO failed — treat as reachable-but-hard,
            # not a clean "site down" pitch. Flag for manual look.
            return "blocked_manual_check", None
        if code == 404:
            return "page_missing", None
        if code == 401:
            return "auth_wall", None
        if 500 <= code < 600:
            return "site_error", None
        return f"http_{code}", None
    except requests.exceptions.SSLError:
        return "site_down_ssl", None
    except requests.exceptions.ConnectionError as e:
        msg = str(e).lower()
        if "getaddrinfo failed" in msg or "name or service" in msg \
                or "nameresolution" in msg:
            return "domain_dead", None       # DNS: domain expired/gone
        return "site_down_slow", None        # reset / refused
    except requests.exceptions.Timeout:
        return "site_down_slow", None
    except Exception as e:
        return "unreachable", None


def load_prospects(path):
    """url -> full prospect row, for the phone/name join."""
    by_url = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            u = (row.get("url") or "").strip()
            if u:
                by_url[audit_batch.normalise(u)] = row
    return by_url


def audited_ok_slugs(outdir):
    """slugs that have at least one report file = audited successfully."""
    slugs = set()
    if os.path.isdir(outdir):
        for fn in os.listdir(outdir):
            if fn.endswith(".md"):
                # report name is <slug>-<date>.md ; strip the -<date>.md tail
                stem = fn.rsplit("-", 3)[0] if fn.count("-") >= 3 else fn[:-3]
                slugs.add(stem)
    return slugs


def append_dedup(path, leads):
    """Append-and-dedup on url. first_seen preserved across runs."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    existing, order = {}, []
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                k = (row.get("url") or "").strip()
                if not k:
                    k = f"__nourl__{len(order)}"
                existing[k] = row
                order.append(k)
    added = already = 0
    for lead in leads:
        k = lead["url"]
        if k in existing:
            already += 1
            continue
        existing[k] = lead
        order.append(k)
        added += 1
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for k in order:
            row = existing[k]
            w.writerow({c: row.get(c, "") for c in FIELDS})
    return {"added": added, "already": already, "total": len(order)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True,
                    help="the audit queue CSV that was run")
    ap.add_argument("--prospects", required=True,
                    help="sourcing prospect CSV (has phone + business_name)")
    ap.add_argument("--output", default="output",
                    help="the audit output dir to scan for reports")
    ap.add_argument("--rebuild-book", default=REBUILD_BOOK)
    ap.add_argument("--dry-run", action="store_true",
                    help="classify and print, but do not write the book")
    args = ap.parse_args()

    queue = audit_batch.load_urls(args.input)
    prospects = load_prospects(args.prospects)
    done = audited_ok_slugs(args.output)
    today = dt.date.today().isoformat()

    aborted = [u for u in queue if audit_batch.slug(u) not in done]
    print(f"queue: {len(queue)} · audited-ok: {len(queue)-len(aborted)} · "
          f"aborted (broken candidates): {len(aborted)}")

    leads, skipped_ok, no_match = [], 0, 0
    for u in aborted:
        reason, ok = classify_error(u)
        if ok == "ok":
            skipped_ok += 1
            print(f"  loads-now, skip: {u}")
            continue
        p = prospects.get(audit_batch.normalise(u), {})
        if not p:
            no_match += 1
        leads.append({
            "business_name": p.get("business_name", ""),
            "trade": p.get("trade", ""),
            "city": p.get("city", ""),
            "phone": p.get("phone", ""),
            "url": u,
            "reason": reason,
            "gbp_review_count": p.get("gbp_review_count", ""),
            "gbp_rating": p.get("gbp_rating", ""),
            "gbp_category": p.get("gbp_category", ""),
            "gbp_place_id": p.get("gbp_place_id", ""),
            "first_seen": today,
        })
        tag = f"[{reason}]"
        print(f"  {tag:<22} {p.get('business_name','(no GBP match)'):<35} "
              f"{p.get('phone','')}")

    print(f"\nbroken-site leads: {len(leads)} "
          f"(loads-now skipped: {skipped_ok}, no GBP match: {no_match})")

    if args.dry_run:
        print("DRY RUN — nothing written")
        return
    res = append_dedup(args.rebuild_book, leads)
    print(f"[book] {args.rebuild_book}")
    print(f"       {res['total']} total (+{res['added']} new, "
          f"{res['already']} already there)")


if __name__ == "__main__":
    main()
