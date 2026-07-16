"""
render_md.py — findings -> .md report + TRIAGE_META footer.

TRIAGE_META contract is UNCHANGED from v12 (schema_version 1.0). Downstream
parsers (ghl-triage/triage/audit_parser.py, website-audit-builder's
parse_audit.py) are unaffected by v13.

See docs/fixtures_golden.md — Fixtures 1/2/3 pin the six diffable fields.
"""
import datetime as dt
from typing import Dict, Any, Optional, List

from .score import AREA_LABELS, BAND_LABEL, WEIGHTS, disclosure_level

RULE = "━" * 50


def _fmt_range(rng, unit="", dp=1) -> str:
    if not rng:
        return "not measured"
    lo, hi = rng
    if abs(hi - lo) < (0.05 if dp == 1 else 0.005):
        return f"{lo:.{dp}f}{unit}"
    return f"{lo:.{dp}f}–{hi:.{dp}f}{unit}"


def _measured_block(m: Dict[str, Any], psi: Dict[str, Any],
                    verdicts: Dict[str, Optional[str]]) -> str:
    lines = ["MEASURED"]

    if psi.get("measured"):
        lines.append(
            f"Loading (mobile):  LCP {_fmt_range(psi.get('lcp_s'), 's')}"
            f"  ·  target under 2.5s  ·  {verdicts.get('lcp') or '—'}")
        if psi.get("inp_ms"):
            lines.append(
                f"Responsiveness:    INP {_fmt_range(psi['inp_ms'], 'ms', 0)}"
                f"  ·  target under 200ms ·  {verdicts.get('inp') or '—'}")
        elif psi.get("tbt_ms"):
            lines.append(
                f"Blocking time:     TBT {_fmt_range(psi['tbt_ms'], 'ms', 0)}"
                f"  ·  lab proxy, not INP")
        lines.append(
            f"Layout stability:  CLS {_fmt_range(psi.get('cls'), '', 2)}"
            f"  ·  target under 0.1   ·  {verdicts.get('cls') or '—'}")
    else:
        lines.append("Loading (mobile):  not measured — data unavailable")

    lines.append(f"Secure (https):    {'YES' if m['https'] else 'NO'}")
    lines.append(f"Tap-to-call:       {'YES' if m['tel_href'] else 'NO'}")
    if m.get("title_len"):
        lines.append(f"Page title:        {m['title_len']} chars · target 55–60")
    else:
        lines.append("Page title:        MISSING")
    lines.append(
        f"Business listing info for Google: "
        f"{'PRESENT' if m['localbusiness_jsonld'] else 'MISSING'}")

    if psi.get("measured"):
        src = "field data (real visitors)" if psi["source"] == "field" \
            else "lab data (simulated)"
        lines.append(
            f"[Source: Google PageSpeed Insights, {src}, "
            f"{psi['runs_ok']} runs, {dt.date.today().isoformat()}]")
    return "\n".join(lines)


def _area_table(sc: Dict[str, Any]) -> str:
    parts = []
    for k, label in AREA_LABELS.items():
        v = sc["elements"].get(k)
        parts.append(f"{label} [{v if v is not None else 'n/a'}/5]")
    return " · ".join(parts)


def _full_rubric_table(sc: Dict[str, Any]) -> str:
    rows = ["| Area | Score | Weight | Contribution |", "|---|---|---|---|"]
    for k, label in AREA_LABELS.items():
        v = sc["elements"].get(k)
        w = WEIGHTS[k]
        if v is None:
            rows.append(f"| {label} | not measured | {int(w*100)}% | — |")
        else:
            rows.append(
                f"| {label} | {v}/5 | {int(w*100)}% | {v * w * 4:.1f} |")
    return "\n".join(rows)


def render(url: str, m: Dict[str, Any], psi: Dict[str, Any],
           verdicts: Dict[str, Optional[str]], sc: Dict[str, Any],
           judged: Optional[Dict[str, Any]],
           triage_meta: str) -> str:
    name = (judged or {}).get("business_name") or url
    today = dt.date.today().isoformat()
    score = sc.get("site_score")
    band_name = sc.get("band")

    head = f"{RULE}\nWEBSITE REVIEW: {name.upper()}\n{url} · Reviewed {today}\n{RULE}\n"

    if score is None:
        overall = "OVERALL: not scored — insufficient data"
    else:
        suffix = ""
        if sc.get("renormalised"):
            missing = ", ".join(AREA_LABELS[k] for k in sc["unscored"])
            suffix = f" ({missing.lower()} not measured)"
        overall = f"OVERALL: {BAND_LABEL.get(band_name, '')} {score}/100{suffix}"

    out = [head, overall, "", _measured_block(m, psi, verdicts), ""]

    if judged and judged.get("top_findings"):
        out.append("THE THREE THINGS COSTING YOU MOST")
        for i, f in enumerate(judged["top_findings"][:3], 1):
            out.append(f"{i}. {f.get('evidence','')}")
            out.append(f"   → {f.get('impact','')}")
            out.append(f"   → Fix: {f.get('fix','')}")
            out.append("")
    else:
        out.append("THE THREE THINGS COSTING YOU MOST")
        out.append("[judged tier unavailable — measured findings only]")
        out.append("")

    if judged and judged.get("working"):
        out.append("WHAT'S WORKING")
        for w in judged["working"]:
            out.append(f"✅ {w}")
        out.append("")

    if judged and judged.get("overview"):
        out.append("OVERVIEW")
        out.append(judged["overview"])
        out.append("")

    # Score disclosure keyed by band — preserved from v12 W3 close.
    level = disclosure_level(band_name)
    if level == "full":
        out.append("AREA SCORES")
        out.append(_full_rubric_table(sc))
    elif level == "line":
        out.append("AREA SCORES")
        out.append(_area_table(sc))
        out.append("")
        out.append("Score from six weighted areas; speed, mobile, and getting "
                   "in touch weighted heaviest.")
    else:
        out.append(f"AREA SCORES\n{BAND_LABEL.get(band_name, '')}")
    out.append("")

    out.append("WANT TO SEE WHAT'S POSSIBLE?")
    out.append("I can put together a quick sketch of what this could look like.")
    out.append(RULE)
    out.append("")
    out.append("```triage-meta")
    out.append(triage_meta)
    out.append("```")

    return "\n".join(out)


def build_triage_meta(url: str, m: Dict[str, Any],
                      judged: Optional[Dict[str, Any]],
                      disqualifiers: List[str],
                      mctb: Optional[bool], vaai: Optional[bool],
                      ghl_upgrade: bool) -> str:
    """
    schema_version stays "1.0". Contract unchanged from v12.

    PRODUCER/CONSUMER SPLIT — DO NOT COLLAPSE.
    When a disqualifier fires we still emit mctb/vaai per their OWN rules —
    usually null, because the signals are unobservable on a disqualified
    prospect. We emit null because we couldn't observe, NOT false because a
    disqualifier fired.

    The consumer (ghl-triage/prospect_triage.py) short-circuits: the Fix 8
    disqualifier gate at Step 3.4 runs before the Fix 7 applicability gate at
    Step 3.5, so these values are never read on a disqualified prospect.

    Collapsing this would break fixtures 2 and 3 in docs/fixtures_golden.md,
    both of which pin null and both of which passed the 2026-04-20 smoke test
    byte-for-byte. Flag any change here against that file.
    """
    j = judged or {}
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    norm_url = url.lower().rstrip("/")

    def yaml_bool(v):
        return "null" if v is None else ("true" if v else "false")

    lines = [
        'schema_version: "1.0"',
        f'audit_generated_at: "{ts}"',
        f'business_name: "{j.get("business_name") or ""}"',
        f'business_url: "{norm_url}"',
        f'trade: {j.get("trade") or "other"}',
        f'ghl_upgrade_candidate: {yaml_bool(ghl_upgrade)}',
        f'mctb_applicable: {yaml_bool(mctb)}',
        f'vaai_applicable: {yaml_bool(vaai)}',
    ]
    if disqualifiers:
        lines.append("disqualifiers:")
        for d in disqualifiers:
            lines.append(f"  - {d}")
    else:
        lines.append("disqualifiers: []")
    return "\n".join(lines)
