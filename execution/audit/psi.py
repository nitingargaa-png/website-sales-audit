"""
psi.py — Google PageSpeed Insights API client.

Runs N times and returns RANGES, not point values. PSI fluctuates by several
points between runs; a single number the prospect can't reproduce destroys
credibility the moment they re-run it themselves.

Free tier: 25,000 queries/day, no API key required at low volume.
Set PSI_API_KEY in .env if you hit rate limits.

Field data (CrUX, real users) beats lab data (Lighthouse, synthetic).
We report which one we used — never silently mix them.
"""
import os
import time
from typing import Optional, Dict, Any, List, Tuple

import requests

PSI_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
TIMEOUT_SECS = 60
RETRY_DELAY_SECS = 2.0
RATE_LIMIT_ATTEMPTS = 3
DEFAULT_RUNS = 3

# Google Core Web Vitals thresholds. These are the citable numbers.
# Do not adjust these to make a prospect look worse.
LCP_GOOD_S = 2.5
INP_GOOD_MS = 200.0
CLS_GOOD = 0.1


def _api_key() -> Optional[str]:
    return os.environ.get("PSI_API_KEY") or None


def _single_run(url: str, strategy: str = "mobile") -> Optional[Dict[str, Any]]:
    """
    One PSI call, with backoff on 429.

    Without an API key PSI allows only a handful of requests per minute per IP.
    With a free key it is 25,000/day. If you are batching, get a key:
    https://developers.google.com/speed/docs/insights/v5/get-started
    """
    params = {
        "url": url,
        "strategy": strategy,
        "category": "performance",
    }
    key = _api_key()
    if key:
        params["key"] = key

    backoff = 4.0
    for attempt in range(1, RATE_LIMIT_ATTEMPTS + 1):
        try:
            resp = requests.get(PSI_ENDPOINT, params=params, timeout=TIMEOUT_SECS)
            if resp.status_code == 429:
                if attempt < RATE_LIMIT_ATTEMPTS:
                    print(f"  [psi] rate limited (429), waiting {backoff:.0f}s")
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                print("  [psi] rate limited (429) after retries."
                      + ("" if key else
                         " Set PSI_API_KEY in .env — without a key PSI allows"
                         " only a few requests per minute per IP."))
                return None
            if resp.status_code != 200:
                print(f"  [psi] HTTP {resp.status_code} for {url}")
                return None
            return resp.json()
        except requests.exceptions.Timeout:
            # PSI is slow on heavy sites; a 60s timeout is not unusual and is
            # worth one retry. Observed 2026-07-16: 1 of 3 runs timed out,
            # leaving a "range" of 25.0-25.0s from the two that survived.
            if attempt < RATE_LIMIT_ATTEMPTS:
                print(f"  [psi] timed out, retrying ({attempt}/"
                      f"{RATE_LIMIT_ATTEMPTS})")
                time.sleep(backoff)
                backoff *= 2
                continue
            print("  [psi] timed out after retries")
            return None
        except Exception as e:
            print(f"  [psi] request failed: {e}")
            return None
    return None


def _extract_field(payload: Dict[str, Any]) -> Optional[Dict[str, float]]:
    """CrUX field data — real users. Preferred when present."""
    le = payload.get("loadingExperience") or {}
    metrics = le.get("metrics") or {}
    if not metrics:
        return None

    out = {}
    lcp = metrics.get("LARGEST_CONTENTFUL_PAINT_MS")
    inp = metrics.get("INTERACTION_TO_NEXT_PAINT")
    cls = metrics.get("CUMULATIVE_LAYOUT_SHIFT_SCORE")

    if lcp and "percentile" in lcp:
        out["lcp_s"] = lcp["percentile"] / 1000.0
    if inp and "percentile" in inp:
        out["inp_ms"] = float(inp["percentile"])
    if cls and "percentile" in cls:
        # CrUX reports CLS x100
        out["cls"] = cls["percentile"] / 100.0

    return out or None


def _extract_lab(payload: Dict[str, Any]) -> Optional[Dict[str, float]]:
    """Lighthouse lab data — synthetic. Fallback when no field data exists."""
    lr = payload.get("lighthouseResult") or {}
    audits = lr.get("audits") or {}
    if not audits:
        return None

    out = {}
    lcp = audits.get("largest-contentful-paint", {}).get("numericValue")
    cls = audits.get("cumulative-layout-shift", {}).get("numericValue")
    tbt = audits.get("total-blocking-time", {}).get("numericValue")

    if lcp is not None:
        out["lcp_s"] = lcp / 1000.0
    if cls is not None:
        out["cls"] = float(cls)
    if tbt is not None:
        # TBT is a lab proxy for INP. Label it honestly downstream —
        # it is NOT the same metric.
        out["tbt_ms"] = float(tbt)

    cats = lr.get("categories") or {}
    perf = cats.get("performance", {}).get("score")
    if perf is not None:
        out["perf_score"] = float(perf) * 100.0

    return out or None


def _rng(values: List[float]) -> Optional[Tuple[float, float]]:
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    return (min(vals), max(vals))


def run(url: str, runs: int = DEFAULT_RUNS, strategy: str = "mobile") -> Dict[str, Any]:
    """
    Run PSI `runs` times, return ranges.

    Returns:
      {
        "measured": bool,
        "source": "field" | "lab" | None,
        "runs_ok": int,
        "lcp_s": (min, max) | None,
        "inp_ms": (min, max) | None,      # field only
        "tbt_ms": (min, max) | None,      # lab only — NOT INP
        "cls": (min, max) | None,
        "perf_score": (min, max) | None,  # lab only
      }

    measured=False means we could not measure. Downstream MUST score Speed as
    null and say "not measured" — never guess, never fall back to an impression.
    """
    field_runs: List[Dict[str, float]] = []
    lab_runs: List[Dict[str, float]] = []

    for i in range(runs):
        if i:
            time.sleep(RETRY_DELAY_SECS)
        payload = _single_run(url, strategy)
        if not payload:
            continue
        f = _extract_field(payload)
        if f:
            field_runs.append(f)
        l = _extract_lab(payload)
        if l:
            lab_runs.append(l)

    if not field_runs and not lab_runs:
        return {"measured": False, "source": None, "runs_ok": 0,
                "lcp_s": None, "inp_ms": None, "tbt_ms": None,
                "cls": None, "perf_score": None}

    # Field data wins when available — it is what real visitors experienced.
    if field_runs:
        src, rows = "field", field_runs
    else:
        src, rows = "lab", lab_runs

    def col(k):
        return _rng([r.get(k) for r in rows if r.get(k) is not None])

    return {
        "measured": True,
        "source": src,
        "runs_ok": len(rows),
        "lcp_s": col("lcp_s"),
        "inp_ms": col("inp_ms") if src == "field" else None,
        "tbt_ms": col("tbt_ms") if src == "lab" else None,
        "cls": col("cls"),
        "perf_score": _rng([r.get("perf_score") for r in lab_runs
                            if r.get("perf_score") is not None]),
    }


def verdicts(psi: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """
    PASS/FAIL against Google's published thresholds.

    Uses the WORST value in the range. If any run failed the threshold, the
    site fails it — a site that's sometimes fast is a site that's sometimes slow,
    and the prospect who bounced got the slow one.
    """
    out: Dict[str, Optional[str]] = {"lcp": None, "inp": None, "cls": None}
    if not psi.get("measured"):
        return out

    if psi.get("lcp_s"):
        out["lcp"] = "PASS" if psi["lcp_s"][1] < LCP_GOOD_S else "FAIL"
    if psi.get("inp_ms"):
        out["inp"] = "PASS" if psi["inp_ms"][1] < INP_GOOD_MS else "FAIL"
    if psi.get("cls"):
        out["cls"] = "PASS" if psi["cls"][1] < CLS_GOOD else "FAIL"
    return out


def element_score(psi: Dict[str, Any]) -> Optional[int]:
    """
    Speed area element score 1-5, or None if unmeasured.

    None is not 3. v12 scored unmeasurable areas 3-as-neutral and let that
    contribute to the total, silently inflating every site where PSI failed.
    None means null means "we did not measure this" and the area is excluded.
    """
    if not psi.get("measured") or not psi.get("lcp_s"):
        return None

    worst_lcp = psi["lcp_s"][1]
    if worst_lcp < 2.5:
        base = 5
    elif worst_lcp < 4.0:
        base = 3
    elif worst_lcp < 6.0:
        base = 2
    else:
        base = 1

    # CLS is a real user-facing failure — things moving under your thumb.
    if psi.get("cls") and psi["cls"][1] >= 0.25 and base > 1:
        base -= 1

    return base
