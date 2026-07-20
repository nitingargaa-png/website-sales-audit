"""
emit.py — two CSVs, one shape.

WHY TWO FILES

  prospects_<batch>.csv   every row found, including rejects, full contract
  audit_queue_<batch>.csv derived projection: clean + has url, url column

One file cannot do both jobs. If the CSV drops rejects, `disqualified`
and `disqualify_reason` are columns nothing can ever populate — a schema
whose fields are unreachable. If instead audit_batch.py learns to skip
disqualified rows, the audit becomes dependent on the sourcing schema and
every hand-made CSV needs the column. So: the full record is the record,
the queue is a projection, and audit_batch.py/load_urls change not at all.

The rejects file is not bookkeeping. A dead_site rule once binned the best
prospects in a batch and it was found by reading rejects. Slice 2 reads
every one.

WHY THERE IS NO owner_name / owner_source

The original contract carried both, nullable, with a 40-70% coverage
expectation. Two probes measured the actual sources before any extractor
was written. Both returned ZERO.

  probe_reviews.py (2026-07-17), 11 businesses, 55 reviews:
      0 full names. Enterprise reviews name TECHNICIANS (Abid, Vedesh,
      Dexter T.) because the reviewer met one of hundreds and that is the
      salient fact. SMB reviews name the COMPANY — "WOW Drain & Plumbing
      responded immediately to our emergency" IS the owner responding,
      unnamed. The SMB hit rate (27%) was WORSE than enterprise (64%), the
      opposite of the hypothesis. The 8 SMB hits included "When",
      "Vaughan", "Owner", and one person spelled two ways (Olek/Oleh).

  probe_about.py (2026-07-17), 15 prospects in the 10-150 review band:
      0 role-adjacent names. ~6 have no About page at all. ~9 have a real
      one, 2119-9375 chars of genuine content, and none names an owner.
      Jina rendered every one of them — js_shell_recovered was 0. On
      garagerepairshamilton.ca Jina returned MORE text than static (4658
      vs 3544) and still found nothing. The JS-rendering concern was
      reasonable and was not the problem.

Both failed for the same non-technical reason: SMB home-service businesses
do not publish the owner's name on customer-facing surfaces, because
customers do not care. They want a phone number and a price. Owner names
live where they serve a different purpose — a registry (legal), LinkedIn
(professional networking). The one real owner name seen in this project
(Walli Amir, Mississauga Plumbing) came from LinkedIn.

This is a SOURCE GAP, not a tuning problem. No pattern work moves it. The
fields were removed rather than kept nullable: a column nothing can ever
populate is the same defect the two-CSV split above exists to fix — an
unreachable schema field that the next reader will trust.

If owner names are needed later, the Ontario BIN registry is the only
candidate with a structural reason to work (a business name registration
names its registrant). That is a separate build with its own probe, and it
covers Ontario only. Do not re-add these columns without a source that
fills them.

THE LOCKED CONSTRAINT

  gbp_review_count is written HERE and nowhere else.

It must never reach m["aggregate_review_count"] in the audit. That field
is page-derived (JSON-LD aggregateRating) and three thresholds in
applicability.py read it. GBP says 209; the page may say nothing. The GAP
between them is the pitch line — it exists only while the two fields stay
separate. Merge them and you silently rewrite mctb/vaai for every prospect
and Fixture 1's honest `null` becomes a fabricated `true`.

STATUS vs DISQUALIFIED

  status is the truth: clean | review | excluded   (shape from v4.6)
  disqualified is the projection: (status == "excluded")

The contract asked for a bool. A review lane is a third state. Carrying
status and deriving the bool satisfies the stated contract literally while
leaving the third state expressible.
"""
import csv
import datetime as _dt
import os
from typing import Dict, List

# Contract order. Do not reorder — downstream reads by name, humans read
# by position.
CONTRACT_FIELDS = [
    "url",
    "business_name",
    "trade",
    "city",
    "gbp_place_id",
    "gbp_rating",
    "gbp_review_count",
    "gbp_category",
    "phone",
    "disqualified",
    "disqualify_reason",
]

# Sourcing-side columns beyond the contract. Carried, not filtered on.
EXTRA_FIELDS = [
    "status",
    "review_reason",
    "toll_free",
    "multi_location_domain",
    "domain",
    "gbp_primary_type",
    "gbp_types",
    "business_status",
    "query_trade",
    "query_city",
]

ALL_FIELDS = CONTRACT_FIELDS + EXTRA_FIELDS


def _bool(v) -> str:
    return "true" if v else "false"


def write_prospects(rows: List[Dict], path: str) -> int:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        wtr = csv.DictWriter(f, fieldnames=ALL_FIELDS, extrasaction="ignore")
        wtr.writeheader()
        for r in rows:
            out = {k: r.get(k) for k in ALL_FIELDS}
            out["disqualified"] = _bool(r.get("status") == "excluded")
            out["toll_free"] = _bool(r.get("toll_free"))
            out["multi_location_domain"] = _bool(r.get("multi_location_domain"))
            for k, v in out.items():
                if v is None:
                    out[k] = ""
            wtr.writerow(out)
    return len(rows)


def write_audit_queue(rows: List[Dict], path: str) -> int:
    """
    Projection: status == clean AND url present.

    The no_website lane is status=clean with url=None — a real prospect
    the audit cannot read. It belongs in prospects.csv and not here.
    Excluding it is the whole reason this filter tests url separately
    from status.

    Emits a single `url` column. load_urls() accepts url/website/domain/
    site/web and takes the first match; `url` is unambiguous.
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    q = [r for r in rows if r.get("status") == "clean" and r.get("url")]
    with open(path, "w", newline="", encoding="utf-8") as f:
        wtr = csv.DictWriter(f, fieldnames=["url"])
        wtr.writeheader()
        for r in q:
            wtr.writerow({"url": r["url"]})
    return len(q)


# Columns kept for a no-website lead. This is a WORKING lead record, not an
# audit input — phone and review count are what you pitch on, so they lead.
_BOOK_FIELDS = ["business_name", "trade", "city", "phone",
                "gbp_review_count", "gbp_rating", "gbp_category",
                "gbp_place_id", "first_seen"]


def write_no_website_book(rows: List[Dict], path: str) -> Dict[str, int]:
    """
    Append-and-dedup the no_website lane into a PERMANENT lead book.

    The no_website lane (status=clean, url=None) is the highest-value
    segment — a business with a GBP listing and reviews but no site, which
    cannot be audited (nothing to score) and is the strongest first-build
    pitch available. It has no other consumer: write_audit_queue drops it on
    the url test, correctly, and prospects.csv is disposable churn under
    sourcing_output/.

    This writes to a path OUTSIDE the repo (a synced drive), because the
    requirement is permanence and retrieval, not convenience. See BACKLOG 1.

    APPEND-AND-DEDUP, keyed on phone:
      - a business with no site today may build one next month (drops out of
        the lane); a new one appears next grid. The book should GROW and
        dedup, not be overwritten by each run's snapshot.
      - dedup on phone, not name: "Hamilton Plumber" and "Hamilton Plumbing"
        are different strings, same number is the same business. A row with
        no phone is kept (cannot dedup it) but flagged in the return count.
      - first_seen is preserved across runs — the date a lead first entered
        the book, not the date of the latest grid. Re-running never resets it.

    Idempotent: re-running the same grid adds nothing. Returns
    {"added": n, "already": n, "no_phone": n, "total": n}.
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    today = _dt.date.today().isoformat()

    lane = [r for r in rows
            if r.get("status") == "clean" and not r.get("url")]

    # Load existing book, key on phone.
    existing: Dict[str, Dict] = {}
    order: List[str] = []          # preserve file order for stable output
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                key = (r.get("phone") or "").strip()
                # rows without a phone get a synthetic unique key so they
                # are never merged together
                if not key:
                    key = f"__nophone__{len(order)}"
                existing[key] = r
                order.append(key)

    added = already = no_phone = 0
    for r in lane:
        phone = (r.get("phone") or "").strip()
        rec = {
            "business_name": r.get("business_name") or "",
            "trade": r.get("trade") or "",
            "city": r.get("city") or "",
            "phone": phone,
            "gbp_review_count": r.get("gbp_review_count") or "",
            "gbp_rating": r.get("gbp_rating") or "",
            "gbp_category": r.get("gbp_category") or "",
            "gbp_place_id": r.get("gbp_place_id") or "",
            "first_seen": today,
        }
        if not phone:
            # cannot dedup — always append, flag it
            key = f"__nophone__{len(order)}"
            existing[key] = rec
            order.append(key)
            no_phone += 1
            added += 1
            continue
        if phone in existing:
            # keep the ORIGINAL first_seen; do not overwrite the record
            already += 1
            continue
        existing[phone] = rec
        order.append(phone)
        added += 1

    with open(path, "w", newline="", encoding="utf-8") as f:
        wtr = csv.DictWriter(f, fieldnames=_BOOK_FIELDS)
        wtr.writeheader()
        for key in order:
            row = existing[key]
            # ensure every field present even for legacy/hand-edited rows
            wtr.writerow({k: row.get(k, "") for k in _BOOK_FIELDS})

    return {"added": added, "already": already, "no_phone": no_phone,
            "total": len(order)}
