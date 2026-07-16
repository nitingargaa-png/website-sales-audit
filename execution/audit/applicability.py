"""
applicability.py — TRIAGE_META judgment fields.

Ported verbatim in intent from SKILL.md v13's expanded definitions.
Every rule is grounded in an OBSERVED signal. Never in trade typicality.

When signals are mixed or absent -> None (emits as null). Not False.
Guessing false is as dishonest as guessing true.
"""
from typing import Dict, Any, Optional, List, Tuple

# Platforms GHL would laterally replace. A first-time sale to a greenfield
# prospect is NOT an upgrade — different downstream triage path.
UPGRADE_PLATFORMS = {
    "servicetitan", "housecallpro", "jobber", "podium", "thryv",
    "hubspot", "keap", "activecampaign",
}


def ghl_upgrade_candidate(m: Dict[str, Any]) -> bool:
    """
    True ONLY for lateral migration — they run a platform GHL replaces.

    Greenfield (no CRM, or just Google Workspace + site + phone) is False.
    A solo operator on WordPress with a phone is False. That is a first-time
    buyer, not an upgrade.
    """
    fsm = m.get("fsm_vendor")
    if fsm and fsm in UPGRADE_PLATFORMS:
        return True
    if m.get("platform") in ("thryv",):
        return True
    if m.get("chat_vendor") == "podium":
        return True
    return False


def mctb_applicable(m: Dict[str, Any], text: str) -> Optional[bool]:
    """
    True when they lose inbound calls with no automated recovery path.

    Grounded in observed signals only. Returns None when genuinely mixed.
    """
    low = text.lower()
    emergency = any(s in low for s in ("24/7", "24 hour", "emergency", "same day"))

    # --- false signals (checked first — they are counter-evidence) ---
    if m.get("booking_tier") == 3 and m.get("fsm_vendor") == "servicetitan":
        return False  # FSM already covers inbound response at scale
    if m.get("platform") == "gohighlevel":
        return False  # already have it
    if m.get("chat_vendor") in ("podium", "mav.ai"):
        return False  # existing MCTB vendor — replacement pitch, not gap pitch

    # --- true signals ---
    # Weighted: STRONG signals are evidence of THIS prospect losing calls.
    # WEAK signals (marketing copy) are consistent with losing calls but are
    # also present on every corporate franchise page. One weak signal alone
    # is not evidence — it is a vibe. Emit null instead.
    #
    # This threshold is pinned by docs/fixtures_golden.md Fixture 2: the
    # Mr. Rooter corporate page has "24/7 emergency" copy and no chat widget,
    # but exposes no small-shop operator profile, no FSM signature, and no
    # review velocity proxy. The fixture expects null. An earlier version of
    # this function returned true on that single weak signal and failed the
    # fixture — that is exactly what the fixture exists to catch.
    strong = 0
    weak = 0

    if m.get("gmail_contact"):
        strong += 1  # a real business using Gmail is a small shop, observed
    rc = m.get("aggregate_review_count") or 0
    if rc >= 50 and not m.get("chat_vendor"):
        strong += 1  # demonstrated call volume, no recovery path
    if m.get("call_tracking") and not m.get("chat_vendor"):
        strong += 1  # paid ads active — every missed call was paid for
    if not m.get("chat_vendor") and not m.get("tel_href") and m.get("phone_in_text"):
        strong += 1  # phone present but not tappable, no chat fallback

    if emergency and not m.get("chat_vendor"):
        weak += 1  # true of every franchise corporate page ever written

    if strong >= 1:
        return True
    if weak >= 2:
        return True
    return None  # weak-only or no signal — do not guess


def vaai_applicable(m: Dict[str, Any], text: str) -> Optional[bool]:
    """
    True when call volume AND an after-hours gap are both visible.

    Call volume is not directly detectable. Infer from proxies: GBP review
    volume, FSM sophistication, 24/7 claims + small-shop profile.

    NEVER True on trade typicality alone. Marking every plumber applicable
    dilutes downstream routing to noise.
    """
    low = text.lower()
    emergency = any(s in low for s in ("24/7", "24 hour", "emergency"))
    rc = m.get("aggregate_review_count") or 0

    # --- false signals ---
    if m.get("chat_vendor") == "smith.ai":
        return False  # answering service present
    if m.get("booking_tier") == 3 and m.get("fsm_vendor") == "servicetitan":
        return False  # live dispatch answers at scale
    if 0 < rc < 10:
        return False  # not enough call volume for voice AI to matter

    # --- true signals ---
    # Voice AI needs BOTH: demonstrated call volume AND an after-hours gap.
    # Emergency copy alone proves neither — every franchise corporate page in
    # the trade says "24/7 emergency service". Review count is the only volume
    # proxy visible from outside, so without it we cannot establish volume and
    # must emit null.
    #
    # Pinned by docs/fixtures_golden.md Fixtures 2 and 3: both pages carry
    # emergency copy and no chat widget, and both expect null because reviews
    # are behind a ZIP gate (Mr. Rooter) or absent (Warm & Cool). An earlier
    # version returned true on emergency-copy-alone and failed both.
    if rc >= 100 and not m.get("chat_vendor"):
        return True
    if (rc >= 30 and emergency and not m.get("chat_vendor")
            and not m.get("fsm_vendor")):
        # Volume proxy + after-hours gap + solo profile. Both halves present.
        return True

    return None  # no volume proxy visible — cannot establish fit


def disqualifiers(m: Dict[str, Any], text: str,
                  region: Optional[str], url: str) -> List[str]:
    """
    List, multiple allowed, [] default.

    Emit only on observed evidence. Ambiguous -> leave out, don't guess.
    """
    out: List[str] = []
    low = text.lower()

    # national_chain — franchise disclosure must be VISIBLE.
    # A corporate-sounding name alone is not enough.
    if m.get("franchise_language"):
        out.append("national_chain")
    elif any(s in low for s in ("throughout the united states",
                                "nationwide", "all 50 states",
                                "locations across")):
        out.append("national_chain")

    # under_construction — 2+ placeholder signals.
    # A bad website is not a placeholder website.
    if m.get("placeholder_signals", 0) >= 2:
        out.append("under_construction")
    elif m.get("js_only_suspected") and m.get("placeholder_signals", 0) >= 1:
        out.append("under_construction")

    # out_of_service_area — binary: not US/Canada.
    if _is_out_of_area(url, region, low):
        out.append("out_of_service_area")

    # dead_site
    if m.get("visible_text_len", 0) < 100:
        out.append("dead_site")

    return out


NON_NA_TLDS = (".co.uk", ".uk", ".au", ".nz", ".ie", ".za", ".in", ".de",
               ".fr", ".es", ".it", ".nl", ".sg", ".ae")


def _is_out_of_area(url: str, region: Optional[str], text: str) -> bool:
    u = url.lower()
    if any(u.split("/")[2].endswith(t) for t in NON_NA_TLDS if "/" in u):
        return True
    for t in NON_NA_TLDS:
        if t in u.split("?")[0]:
            return True
    return False


def evaluate(m: Dict[str, Any], text: str, judged: Optional[Dict[str, Any]],
             url: str) -> Tuple[bool, Optional[bool], Optional[bool], List[str]]:
    """
    Returns (ghl_upgrade, mctb, vaai, disqualifiers).

    NOTE: mctb/vaai are evaluated INDEPENDENTLY of disqualifiers. See
    render_md.build_triage_meta docstring for why. Do not short-circuit here.
    """
    region = (judged or {}).get("region")
    return (
        ghl_upgrade_candidate(m),
        mctb_applicable(m, text),
        vaai_applicable(m, text),
        disqualifiers(m, text, region, url),
    )
