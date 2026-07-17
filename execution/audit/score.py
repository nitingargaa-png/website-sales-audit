"""
score.py — Six areas, two evidence tiers.

The core rule of v13: MEASURED and JUDGED are never averaged into one number.
They have different epistemic status. An owner can argue with a judgment;
they cannot argue with an LCP of 6.2s. Merging them lets the owner dismiss
the measured half by disputing the judged half.

We compute one site_score for internal tiering, but the report always shows
the measured block separately and labels it as measured.
"""
from typing import Dict, Any, Optional, List, Tuple

from . import psi as psi_mod

# Weights from SKILL.md v13. These reflect the convergent view of five
# practitioners independently asked what they check when reviewing a local
# service site: speed, mobile, conversion, SEO basics, trust.
WEIGHTS = {
    "speed": 0.20,
    "mobile": 0.20,
    "conversion": 0.20,
    "seo_local": 0.15,
    "trust": 0.15,
    "lead_capture": 0.10,
}

AREA_LABELS = {
    "speed": "Speed",
    "mobile": "Mobile",
    "conversion": "Getting in touch",
    "seo_local": "Being found",
    "trust": "Trust",
    "lead_capture": "Following up on leads",
}


def score_seo_local(m: Dict[str, Any]) -> int:
    """Mostly measured. Automatic <=2 if content invisible without JS."""
    if m["js_only_suspected"]:
        return 1 if not m["localbusiness_jsonld"] else 2

    pts = 0
    if m["title"]:
        pts += 1
        if m["title_ok"]:
            pts += 1
    if m["meta_desc"]:
        pts += 1
        if m["meta_desc_ok"]:
            pts += 1
    if m["localbusiness_jsonld"]:
        pts += 2
    if m["map_embed"]:
        pts += 1
    if m["gbp_link"]:
        pts += 1

    # 0-8 -> 1-5
    if pts >= 7:
        return 5
    if pts >= 5:
        return 4
    if pts >= 3:
        return 3
    if pts >= 1:
        return 2
    return 1


def score_trust(m: Dict[str, Any], judged: Optional[int] = None) -> int:
    """
    Judged, with hard measured anchors.

    Automatic <=2: social proof exists but the visitor cannot see how much.

    Three shapes of this, all confirmed real:
      - Google badge present, no count anywhere -> the badge implies reviews
        exist and tells the visitor nothing about how many.
      - JSON-LD aggregateRating present, count not rendered on the page.
      - Count only appears after JavaScript runs, so a crawler never sees it.

    Confirmed 2026-07-16 on mississaugaplumbingservices.com: homepage shows a
    "Google Reviews" badge, five gold stars, one testimonial, and no number.
    Google's panel shows 4.8 from 266 reviews. The business earned 266 reviews
    and its homepage displays none of that. Most winnable fix in the audit —
    it must never score above 2.
    """
    if m.get("google_badge") and not m.get("review_count_visible"):
        return min(judged or 2, 2)
    if m.get("aggregate_review_count") and not m.get("review_count_visible"):
        return min(judged or 2, 2)
    if m.get("review_count_after_js") and not m.get("review_count_visible"):
        return min(judged or 2, 2)
    return judged if judged is not None else 3


def score_conversion(m: Dict[str, Any], judged: Optional[int] = None) -> int:
    """Automatic <=2 if phone only exists inside an image."""
    if not m["phone_in_text"] and not m["tel_href"]:
        return 1
    base = judged if judged is not None else 3
    if not m["tel_href"]:
        base = min(base, 2)
    if not m["has_form"]:
        base = min(base, 3)
    return max(1, base)


def score_mobile(m: Dict[str, Any], psi: Dict[str, Any],
                 judged: Optional[int] = None) -> int:
    base = judged if judged is not None else 3
    if not m["viewport_meta"]:
        base = min(base, 2)
    if not m["tel_href"]:
        base = min(base, 3)
    if psi.get("measured") and psi.get("cls") and psi["cls"][1] >= 0.25:
        base = min(base, 3)
    return max(1, base)


def score_lead_capture(m: Dict[str, Any], judged: Optional[int] = None) -> int:
    """
    Mostly inferred. We are guessing most here and the report says so.

    Booking tier 3 means their FSM already covers this — do not pitch booking.
    """
    if m["booking_tier"] == 3:
        return 5
    pts = 0
    if m["has_form"]:
        pts += 1
    if m["booking_tier"] >= 2:
        pts += 1
    if m["chat_vendor"]:
        pts += 1
    if not m["gmail_contact"]:
        pts += 1
    return {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}[pts]


def compute(measured: Dict[str, Any], psi: Dict[str, Any],
            judged: Dict[str, int],
            judge_available: bool = True) -> Dict[str, Any]:
    """
    Six element scores -> site_score.

    CRITICAL: unmeasurable areas are None, NOT 3. v12 scored them 3-as-neutral
    and let that contribute to the total, which silently inflated the score on
    every site where PSI failed. Since PSI was optional in v12, that was
    potentially most sites. Here, a None area is EXCLUDED and the weights are
    renormalised over what we actually measured — and the report says so.

    judge_available=False means the judged tier refused (invisible content).
    In that case the JUDGED areas score None too — we did not see the site, so
    we cannot rate its design or trust. Scoring them 1/5 would be pretending we
    looked. Only the measured areas survive.

    Observed 2026-07-16: a JS-shell site scored 4/100 with every area at 1/5,
    including "Trust 1/5" on a business with 166 five-star reviews we simply
    could not see. That number was theatre.
    """
    speed = psi_mod.element_score(psi)

    if judge_available:
        elements: Dict[str, Optional[int]] = {
            "speed": speed,
            "mobile": score_mobile(measured, psi, judged.get("mobile")),
            "conversion": score_conversion(measured, judged.get("conversion")),
            "seo_local": score_seo_local(measured),
            "trust": score_trust(measured, judged.get("trust")),
            "lead_capture": score_lead_capture(measured, judged.get("lead_capture")),
        }
    else:
        # Only what we can determine from bytes alone.
        elements = {
            "speed": speed,
            "mobile": _mobile_measured_only(measured, psi),
            "conversion": None,
            "seo_local": score_seo_local(measured),
            "trust": None,
            "lead_capture": None,
        }

    scored = {k: v for k, v in elements.items() if v is not None}
    if not scored:
        return {"elements": elements, "site_score": None, "band": None,
                "unscored": list(elements.keys()), "renormalised": False,
                "weight_covered": 0}

    total_weight = sum(WEIGHTS[k] for k in scored)
    raw = sum(v * WEIGHTS[k] * 20 for k, v in scored.items())
    # Renormalise so a missing area doesn't silently drag the score down.
    site_score = round(raw / total_weight * 1.0) if total_weight else None

    unscored = [k for k, v in elements.items() if v is None]

    return {
        "elements": elements,
        "site_score": site_score,
        "band": band(site_score),
        "unscored": unscored,
        "renormalised": bool(unscored),
        "weight_covered": round(total_weight * 100),
    }


def _mobile_measured_only(m: Dict[str, Any], psi: Dict[str, Any]) -> Optional[int]:
    """Mobile from measured signals alone — viewport, tap-to-call, CLS."""
    pts = 0
    if m.get("viewport_meta"):
        pts += 1
    if m.get("tel_href"):
        pts += 2
    if psi.get("measured") and psi.get("cls") and psi["cls"][1] < 0.1:
        pts += 1
    return {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}.get(pts, 3)


def band(score: Optional[int]) -> Optional[str]:
    if score is None:
        return None
    if score >= 80:
        return "green"
    if score >= 55:
        return "yellow"
    return "red"


BAND_LABEL = {
    "green": "🟢 Strong Foundation",
    "yellow": "🟡 Some Gaps",
    "red": "🔴 Needs Significant Work",
}


def disclosure_level(band_name: Optional[str]) -> str:
    """
    How much of the rubric to publish, keyed by band.

    Preserved from v12 (W3 close, session 25): full table on red so the number
    is reconstructable, one line on yellow, band label only on green.
    Never publish the score -> pitch tier mapping. That stays internal.
    """
    return {"red": "full", "yellow": "line", "green": "band"}.get(
        band_name or "", "line")
