#!/usr/bin/env python
"""
run.py — sourcing CLI. discover -> dedupe -> classify -> emit.

Usage:
  # single cell
  python sourcing/run.py --trade "garage door" --city "Mississauga ON"

  # grid from args
  python sourcing/run.py --trades "garage door,plumbing,hvac" \
                         --cities "Mississauga ON,Hamilton ON"

  # grid from a config file (preferred once the grid stops changing)
  python sourcing/run.py --grid sourcing/grids/gta.json

  python sourcing/run.py --grid ... --dry-run     # no calls, no charge
  python sourcing/run.py --grid ... --resume      # skip done cells
  python sourcing/run.py --grid ... --no-cache    # force refetch
  python sourcing/run.py --cache-stats            # what is cached
  python sourcing/run.py --clear-cache

Output lands in sourcing_output/, NOT output/. The audit writes to output/
and mixing them makes a mess of a directory you read by hand.

BATCH NAMES ARE UNIQUE PER RUN. The default was grid-<date>, so two runs
on the same day silently overwrote each other — a 270-row grid was
replaced by a 20-row single cell on 2026-07-17 with no warning. Default is
now grid-<date>-<HHMMSS>. Pass --batch to name one deliberately; an
existing file is refused rather than clobbered.

CHECKPOINT is on the grid cell (trade|city), not the row. Places bills per
request; a resume must not re-fetch pages already paid for. Helpers come
from execution/audit/checkpoint.py — one copy, imported, not lifted.

CACHE is per page, 7-day TTL. A repeated grid costs nothing and returns
the SAME rows: Places result sets jitter between runs (277 vs 275 rows an
hour apart), which silently flipped a multi_location_domain verdict. See
sourcing/cache.py and BACKLOG item 3.

GRID DESIGN: use non-adjacent cities. Mississauga x Brampton share
operators (both Peel), so multi_location_domain fires on genuine
service-area overlap and tells you nothing. Mississauga x Hamilton makes a
shared-domain hit mean something.
"""
import argparse
import datetime as dt
import json
import os
import sys

# cp1252 guard - Windows Python crashes on em-dashes when stdout is piped,
# even though interactive sys.stdout.encoding reports utf-8. Byte-identical
# to the block in execution/audit_batch.py, ghl-triage/prospect_triage.py,
# and execution/triage_handoff.py. hasattr guard is for <3.7.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "execution"))

from dotenv import load_dotenv            # noqa: E402
load_dotenv(os.path.join(_ROOT, ".env"))

from sourcing import discover             # noqa: E402
from sourcing import normalize            # noqa: E402
from sourcing import dedupe               # noqa: E402
from sourcing import status as status_mod  # noqa: E402
from sourcing import emit                 # noqa: E402
from sourcing import cache as cache_mod   # noqa: E402
from audit.checkpoint import (            # noqa: E402
    write_checkpoint, load_completed)

OUTDIR = "sourcing_output"


def slugify(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")


def _split(v):
    return [x.strip() for x in (v or "").split(",") if x.strip()]


def load_grid(path):
    """
    {"trades": [...], "cities": [...], "max_pages": 3}
    or
    {"cells": [["garage door", "Mississauga ON"], ...]}

    Explicit cells beat the cross product when the grid is ragged — not
    every trade is worth every city.
    """
    with open(path, encoding="utf-8") as f:
        g = json.load(f)
    if "cells" in g:
        return [tuple(c) for c in g["cells"]], g.get("max_pages")
    return ([(t, c) for t in g["trades"] for c in g["cities"]],
            g.get("max_pages"))


def main():
    ap = argparse.ArgumentParser(description="Animo sourcing")
    ap.add_argument("--trade", help='single trade, e.g. "garage door"')
    ap.add_argument("--city", help='single city, e.g. "Mississauga ON"')
    ap.add_argument("--trades", help="comma-separated grid trades")
    ap.add_argument("--cities", help="comma-separated grid cities")
    ap.add_argument("--grid", help="path to a grid JSON config")
    ap.add_argument("--output", default=OUTDIR)
    ap.add_argument("--batch", help="batch name; default grid-<date>-<time>")
    ap.add_argument("--max-pages", type=int, default=None,
                    help="1 page = 20 results, API caps at 3")
    ap.add_argument("--resume", action="store_true",
                    help="skip grid cells already in this batch's checkpoint")
    ap.add_argument("--no-cache", action="store_true",
                    help="ignore cached cells (still writes them)")
    ap.add_argument("--cache-stats", action="store_true")
    ap.add_argument("--clear-cache", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="show the grid and field mask, call nothing")
    args = ap.parse_args()

    if args.cache_stats:
        s = cache_mod.stats()
        print(f"cache: {s['cells']} cells ({s['fresh']} fresh, "
              f"{s['stale']} stale), {s['rows']} rows")
        return
    if args.clear_cache:
        print(f"cleared {cache_mod.clear()} cached cells")
        return

    if args.grid:
        cells, grid_pages = load_grid(args.grid)
        max_pages = args.max_pages or grid_pages or discover.MAX_PAGES
    else:
        trades = _split(args.trades) or ([args.trade] if args.trade else [])
        cities = _split(args.cities) or ([args.city] if args.city else [])
        if not trades or not cities:
            raise SystemExit(
                "need --trade/--city, --trades/--cities, or --grid")
        cells = [(t, c) for t in trades for c in cities]
        max_pages = args.max_pages or discover.MAX_PAGES

    key = os.environ.get("GOOGLE_PLACES_API_KEY")
    stamp = dt.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    batch = args.batch or f"grid-{stamp}"
    ckpt = os.path.join(args.output, f"sourcing_{batch}.checkpoint")

    if args.dry_run:
        cs = cache_mod.stats()
        cached = sum(1 for t, c in cells
                     if cache_mod.get(t, c, "") is not None)
        est = (len(cells) - cached) * max_pages
        print("DRY RUN - no API call, no charge")
        print(f"  cells      : {len(cells)}")
        for t, c in cells:
            hit = "cached" if cache_mod.get(t, c, "") is not None else "fetch"
            print(f"               [{hit:>6}] {t} | {c}")
        print(f"  pages/cell : up to {max_pages} x {discover.PAGE_SIZE}")
        print(f"  requests   : up to {est}  (~${est * 0.04:.2f} Enterprise "
              f"SKU; {cached} cells cached)")
        print(f"  key        : {'present' if key else 'MISSING'}")
        print(f"  batch      : {batch}")
        print(f"  checkpoint : {ckpt}")
        return

    if not key:
        raise SystemExit("GOOGLE_PLACES_API_KEY not in .env")

    p_path = os.path.join(args.output, f"prospects_{batch}.csv")
    q_path = os.path.join(args.output, f"audit_queue_{batch}.csv")
    if os.path.exists(p_path) and not args.resume:
        raise SystemExit(
            f"{p_path} exists. Pass a different --batch, or --resume to "
            f"continue it. Refusing to overwrite: a 270-row grid was "
            f"silently replaced by a 20-row cell this way on 2026-07-17.")

    done = load_completed(ckpt) if args.resume else set()
    if done:
        print(f"Resuming: {len(done)} cells already done")

    all_places = []
    for i, (t, c) in enumerate(cells, 1):
        cell = f"{t}|{c}"
        if cell in done:
            print(f"[{i}/{len(cells)}] SKIP (done) {cell}")
            continue
        print(f"[{i}/{len(cells)}] searching: {t} {c}")
        places = discover.search(t, c, key, max_pages=max_pages,
                                 use_cache=not args.no_cache)
        print(f"            {len(places)} results")
        all_places.extend(places)
        write_checkpoint(ckpt, cell)

    if not all_places:
        print("nothing returned - stopping")
        return

    print(f"\n[normalise] {len(all_places)} raw")
    rows = normalize.to_rows(all_places)

    rows, dropped = dedupe.dedupe_by_place_id(rows)
    print(f"[dedupe]    {dropped} duplicate place_id dropped, {len(rows)} left")

    rows = dedupe.flag_multi_location(rows)
    hot = dedupe.domain_counts(rows)
    shared = {d: n for d, n in hot.items()
              if n >= dedupe.MULTI_LOCATION_THRESHOLD}
    if shared:
        print(f"[multi-loc] shared domains (>={dedupe.MULTI_LOCATION_THRESHOLD}):")
        for d, n in sorted(shared.items(), key=lambda x: -x[1]):
            print(f"            {n:>3}  {d}")
    else:
        print("[multi-loc] no shared domains over threshold")

    rows = status_mod.classify_all(rows)
    s = status_mod.summarise(rows)
    print(f"[status]    clean={s['clean']} review={s['review']} "
          f"excluded={s['excluded']}  (no_website lane: {s['no_website_lane']})")

    n_all = emit.write_prospects(rows, p_path)
    n_q = emit.write_audit_queue(rows, q_path)
    print(f"[emit]      {p_path}  ({n_all} rows, every row)")
    print(f"[emit]      {q_path}  ({n_q} rows, clean + has url)")

    rej = [r for r in rows if r.get("status") != "clean"]
    if rej:
        print(f"\nREAD THESE. {len(rej)} rows not clean:")
        for r in rej:
            why = r.get("disqualify_reason") or r.get("review_reason")
            print(f"  {r['status']:<8} {(r.get('business_name') or '')[:38]:<38} {why}")
        print("\nA dead_site rule once binned the best prospects in a batch.")
        print("It was found by reading rejects. Read them.")


if __name__ == "__main__":
    main()
