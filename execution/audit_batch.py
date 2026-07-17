#!/usr/bin/env python
"""
audit_batch.py — v13 audit runner. Batch or single URL.

This is the ONLY implementation of the v13 rubric. docs/SKILL.md is the spec;
audit/judge.py embeds it as a system prompt. One rubric, one code path.

Why this exists as Python and not a Claude Code skill:
  SYSTEM_CONTEXT.md is right — Python cannot subprocess Claude Code. But ~70%
  of the v13 rubric is deterministic (PSI API, HTML parsing, regex detection).
  Only the judged tier needs a model, and that is a direct Anthropic API call.
  So the whole pipeline runs headless.

Usage:
  python execution/audit_batch.py --input input/prospects.csv
  python execution/audit_batch.py --input input/prospects.csv --skip-completed
  python execution/audit_batch.py --input input/prospects.csv --dry-run
  python execution/audit_batch.py --url https://example.com
  python execution/audit_batch.py --input input/prospects.csv --no-pdf
"""
import argparse
import csv
import datetime as dt
import os
import re
import sys
import time
from typing import List, Optional, Dict, Any

import requests

# cp1252 guard — Windows Python crashes on em-dashes when stdout is piped or
# running under subprocess, even though interactive sys.stdout.encoding reports
# utf-8. Byte-identical to the block in ghl-triage/prospect_triage.py and
# website-sales-audit/execution/triage_handoff.py. hasattr guard is for <3.7.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit import psi as psi_mod          # noqa: E402
from audit import detect                   # noqa: E402
from audit import judge                    # noqa: E402
from audit import score as score_mod       # noqa: E402
from audit import applicability            # noqa: E402
from audit import render_md                # noqa: E402
from audit.checkpoint import (           # noqa: E402
    write_checkpoint, load_completed_urls)

try:
    from audit import render_pdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

FETCH_TIMEOUT = 30
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "Chrome/121.0.0.0 Safari/537.36")
SUBPAGES = ["/contact", "/contact-us", "/about", "/about-us", "/services"]


# --- io --------------------------------------------------------------------
def normalise(url: str) -> str:
    url = url.strip().rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def slug(url: str) -> str:
    host = re.sub(r"^https?://", "", url).split("/")[0]
    host = re.sub(r"^www\.", "", host)
    return re.sub(r"[^a-z0-9]+", "", host.lower())


def load_urls(path: str) -> List[str]:
    """CSV with a url/website/domain column, or a plain .txt of URLs."""
    urls = []
    if path.lower().endswith(".txt"):
        with open(path, encoding="utf-8") as f:
            return [normalise(l) for l in f if l.strip()
                    and not l.startswith("#")]
    with open(path, newline="", encoding="utf-8-sig") as f:
        rdr = csv.DictReader(f)
        cols = [c for c in (rdr.fieldnames or [])
                if c and c.lower().strip() in
                ("url", "website", "domain", "site", "web")]
        if not cols:
            raise SystemExit(
                f"No url/website/domain column in {path}. "
                f"Found: {rdr.fieldnames}")
        col = cols[0]
        for row in rdr:
            v = (row.get(col) or "").strip()
            if v:
                urls.append(normalise(v))
    return urls


def fetch(url: str) -> Optional[str]:
    try:
        r = requests.get(url, timeout=FETCH_TIMEOUT,
                         headers={"User-Agent": UA})
        if r.status_code != 200:
            print(f"  [fetch] HTTP {r.status_code}")
            return None
        return r.text
    except Exception as e:
        print(f"  [fetch] {e}")
        return None


def fetch_all(url: str) -> Optional[str]:
    """Homepage is required. Subpages are additive; missing ones are noted."""
    home = fetch(url)
    if not home:
        return None
    combined = home
    for sp in SUBPAGES:
        h = fetch(url + sp)
        if h:
            combined += "\n" + h
    return combined


# --- pipeline --------------------------------------------------------------
def audit_one(url: str, outdir: str, want_pdf: bool,
              agency: str, contact: str) -> Optional[Dict[str, Any]]:
    print(f"\n=== {url}")

    html = fetch_all(url)
    if html is None:
        print("  ABORT: site would not load. Not audited.")
        return None

    print("  [1/5] detecting…")
    m = detect.scan(html, url)

    print(f"  [2/5] PageSpeed ({psi_mod.DEFAULT_RUNS} runs)…")
    p = psi_mod.run(url, runs=psi_mod.DEFAULT_RUNS)
    v = psi_mod.verdicts(p)
    if p["measured"]:
        lcp = p.get("lcp_s")
        print(f"        LCP {lcp[0]:.1f}-{lcp[1]:.1f}s ({p['source']}) "
              f"-> {v['lcp']}" if lcp else "        no LCP")
    else:
        print("        NOT MEASURED — Speed will score null")

    print("  [3/5] judging…")
    text = detect._strip_tags(html)
    j = judge.assess(text, m, p, url)
    if j is None:
        print("        judged tier failed — degrading to measured-only")

    print("  [4/5] scoring…")
    judged_scores = (j or {}).get("judged", {})
    sc = score_mod.compute(m, p, judged_scores)
    print(f"        {sc['site_score']}/100 ({sc['band']})"
          if sc["site_score"] is not None else "        not scored")

    ghl_up, mctb, vaai, dq = applicability.evaluate(m, text, j, url)
    if dq:
        print(f"        DISQUALIFIED: {', '.join(dq)}")

    tm = render_md.build_triage_meta(url, m, j, dq, mctb, vaai, ghl_up)
    md = render_md.render(url, m, p, v, sc, j, tm)

    print("  [5/5] writing…")
    os.makedirs(outdir, exist_ok=True)
    today = dt.date.today().isoformat()
    md_path = os.path.join(outdir, f"{slug(url)}-{today}.md")
    with open(md_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    print(f"        {md_path}")

    pdf_path = None
    if want_pdf and PDF_AVAILABLE and not dq:
        pdf_path = os.path.join(outdir, "pdf", f"{slug(url)}-{today}.pdf")
        try:
            render_pdf.render(pdf_path, url, m, p, v, sc, j, agency, contact)
            print(f"        {pdf_path}")
        except Exception as e:
            print(f"        [pdf] failed: {e}")
            pdf_path = None
    elif want_pdf and dq:
        print("        [pdf] skipped — prospect disqualified, do not send")

    return {"url": url, "md": md_path, "pdf": pdf_path,
            "score": sc["site_score"], "band": sc["band"],
            "disqualifiers": dq}


def main():
    ap = argparse.ArgumentParser(description="v13 website audit — batch runner")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", help="CSV or TXT of prospect URLs")
    src.add_argument("--url", help="single URL")
    ap.add_argument("--output", default="output", help="output dir")
    ap.add_argument("--skip-completed", action="store_true",
                    help="resume: skip URLs in today's checkpoint")
    ap.add_argument("--dry-run", action="store_true",
                    help="validate input, fetch nothing")
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--agency", default="Animo Automation")
    ap.add_argument("--contact", default="")
    ap.add_argument("--limit", type=int, help="cap number of prospects")
    args = ap.parse_args()

    urls = [normalise(args.url)] if args.url else load_urls(args.input)
    if args.limit:
        urls = urls[:args.limit]

    today = dt.date.today().isoformat()
    ckpt = os.path.join(args.output, f"audit_{today}.checkpoint")

    if args.skip_completed:
        done = load_completed_urls(ckpt)
        before = len(urls)
        urls = [u for u in urls if u not in done]
        print(f"Resuming: {before - len(urls)} already done, {len(urls)} left")

    if args.dry_run:
        print(f"DRY RUN — {len(urls)} URLs would be audited:")
        for u in urls[:20]:
            print(f"  {u}")
        if len(urls) > 20:
            print(f"  … and {len(urls) - 20} more")
        return

    if not args.no_pdf and not PDF_AVAILABLE:
        print("WARNING: reportlab not installed — PDFs disabled. "
              "pip install reportlab")

    results = []
    t0 = time.time()
    for i, u in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}]", end="")
        try:
            r = audit_one(u, args.output, not args.no_pdf,
                          args.agency, args.contact)
            if r:
                results.append(r)
                write_checkpoint(ckpt, u)
        except KeyboardInterrupt:
            print("\nInterrupted. Resume with --skip-completed")
            break
        except Exception as e:
            print(f"  ERROR: {e}")

    # --- summary ---
    print(f"\n{'='*60}")
    print(f"Audited {len(results)}/{len(urls)} in {time.time()-t0:.0f}s")
    dq = [r for r in results if r["disqualifiers"]]
    if dq:
        print(f"Disqualified: {len(dq)}")
    scored = [r for r in results if r["score"] is not None]
    if scored:
        scored.sort(key=lambda r: r["score"])
        print(f"\nWorst first (best rebuild candidates):")
        for r in scored[:15]:
            flag = " [DQ]" if r["disqualifiers"] else ""
            print(f"  {r['score']:>3}/100  {r['band']:<7} {r['url']}{flag}")


if __name__ == "__main__":
    main()
