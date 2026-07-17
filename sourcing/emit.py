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
    "owner_name",
    "owner_source",
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
