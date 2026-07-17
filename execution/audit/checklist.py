"""
checklist.py — turns the measured dict into (b) reason lines and (a) a full
grouped checklist.

WHY BOTH, AND WHY THEY DON'T DUPLICATE
  (b) reason lines  = the SUMMARY layer. One line per area score, naming what
                      failed. Answers "why 1/5?" on page 1.
  (a) checklist     = the EVIDENCE layer. Every check, grouped, on page 2.
                      Answers "what exactly did you look at?"

The one-pager was a real finding from practitioner feedback ("a one-page
summary beats a 20-page report every time"), so page 1 stays the pitch and
page 2 is what you point at when challenged.

NOT_CHECKED IS LOAD-BEARING.
Some things genuinely cannot be assessed from outside without a rendered
screenshot: thumb-friendly buttons, "modern look", whether photos are real.
Saying NOT CHECKED is honest. Omitting them silently implies we looked.
"""
from typing import Dict, Any, List, Tuple, Optional

PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"
NOT_CHECKED = "NOT CHECKED"

# Owner-facing labels. No field names, no jargon — same rule as the judge.
GROUPS = [
    ("Speed and performance", "speed"),
    ("Mobile usability", "mobile"),
    ("Conversion basics", "conversion"),
    ("Being found online", "seo_local"),
    ("Trust and professionalism", "trust"),
]


def build(m: Dict[str, Any], psi: Dict[str, Any],
          verdicts: Dict[str, Optional[str]]) -> Dict[str, List[Tuple[str, str, str]]]:
    """
    Returns {group_key: [(label, status, detail), ...]}

    detail is a short plain-language fact, or "" when the label says it all.
    """
    out: Dict[str, List[Tuple[str, str, str]]] = {}

    # ---- 1. Speed ----------------------------------------------------------
    speed: List[Tuple[str, str, str]] = []
    if psi.get("measured") and psi.get("lcp_s"):
        lo, hi = psi["lcp_s"]
        speed.append(("Time until main content appears (phone)",
                      verdicts.get("lcp") or WARN,
                      f"{lo:.1f}–{hi:.1f}s · target under 2.5s"))
    else:
        speed.append(("Time until main content appears (phone)", NOT_CHECKED,
                      "PageSpeed data unavailable"))

    if psi.get("inp_ms"):
        lo, hi = psi["inp_ms"]
        speed.append(("Responsiveness to taps", verdicts.get("inp") or WARN,
                      f"{lo:.0f}–{hi:.0f}ms · target under 200ms"))
    else:
        speed.append(("Responsiveness to taps", NOT_CHECKED,
                      "needs real visitor data from Google; "
                      "not enough traffic on record"))

    if psi.get("cls"):
        lo, hi = psi["cls"]
        speed.append(("Page stays still while loading",
                      verdicts.get("cls") or WARN,
                      f"{hi:.2f} · target under 0.1"))
    else:
        speed.append(("Page stays still while loading", NOT_CHECKED, ""))

    if psi.get("tbt_ms"):
        lo, hi = psi["tbt_ms"]
        speed.append(("Time blocked by scripts", WARN if hi > 300 else PASS,
                      f"{lo:.0f}–{hi:.0f}ms (simulated test)"))
    speed.append(("Number of scripts on the page",
                  WARN if m.get("script_count", 0) > 6 else PASS,
                  f"{m.get('script_count', 0)} scripts"))
    out["speed"] = speed

    # ---- 2. Mobile usability ----------------------------------------------
    mob: List[Tuple[str, str, str]] = []
    mob.append(("Scales to phone screens",
                PASS if m.get("viewport_meta") else FAIL, ""))
    if m.get("tel_js_only"):
        mob.append(("Tap-to-call the phone number", FAIL,
                    "works in a browser, but not present in the page as "
                    "delivered — search engines don't see it"))
    else:
        mob.append(("Tap-to-call the phone number",
                    PASS if m.get("tel_href") else FAIL, ""))
    mob.append(("Contact form to fill in",
                PASS if m.get("has_form") else FAIL,
                "" if m.get("has_form") else "no form found"))
    mob.append(("Buttons sized for thumbs", NOT_CHECKED,
                "needs a visual check on a real device"))
    mob.append(("Text readable without zooming", NOT_CHECKED,
                "needs a visual check on a real device"))
    out["mobile"] = mob

    # ---- 3. Conversion basics ---------------------------------------------
    conv: List[Tuple[str, str, str]] = []
    conv.append(("Phone number readable as text",
                 PASS if m.get("phone_in_text") else FAIL,
                 "" if m.get("phone_in_text") else
                 "number may only exist inside an image"))
    conv.append(("Contact form present",
                 PASS if m.get("has_form") else FAIL, ""))
    bt = m.get("booking_tier", 1)
    conv.append(("Online booking or quote request",
                 PASS if bt >= 3 else (WARN if bt == 2 else FAIL),
                 {1: "phone or form only", 2: "form, no calendar",
                  3: "full booking flow"}.get(bt, "")))
    conv.append(("Live chat or messaging",
                 PASS if m.get("chat_vendor") else FAIL,
                 m.get("chat_vendor") or "none found"))
    conv.append(("Pages for individual services",
                 PASS if m.get("service_pages", 0) >= 3 else
                 (WARN if m.get("service_pages", 0) >= 1 else FAIL),
                 f"{m.get('service_pages', 0)} found"))
    conv.append(("Clear headline and offer", NOT_CHECKED,
                 "needs a visual check"))
    out["conversion"] = conv

    # ---- 4. Being found online --------------------------------------------
    seo: List[Tuple[str, str, str]] = []
    tl = m.get("title_len")
    seo.append(("Page title",
                PASS if m.get("title_ok") else FAIL,
                f"{tl} characters · target 55–60" if tl else "missing"))
    dl = m.get("meta_desc_len")
    seo.append(("Search result description",
                PASS if m.get("meta_desc_ok") else FAIL,
                f"{dl} characters · target 150–160" if dl else "not set"))
    seo.append(("Town or city named in the title",
                PASS if m.get("city_in_title") else FAIL, ""))
    seo.append(("Main heading on the page",
                PASS if m.get("h1_count", 0) == 1 else
                (WARN if m.get("h1_count", 0) > 1 else FAIL),
                f"{m.get('h1_count', 0)} found · should be exactly 1"))
    seo.append(("Section headings",
                PASS if m.get("h2_count", 0) >= 2 else FAIL,
                f"{m.get('h2_count', 0)} found"))
    seo.append(("Content readable without scripts running",
                FAIL if m.get("js_only_suspected") else PASS,
                f"{m.get('visible_text_len', 0)} characters visible on first "
                f"load" if m.get("js_only_suspected") else ""))
    seo.append(("Links between your own pages",
                PASS if m.get("internal_links", 0) >= 5 else FAIL,
                f"{m.get('internal_links', 0)} found"))
    seo.append(("Business details for Google to read",
                PASS if m.get("localbusiness_jsonld") else FAIL,
                "" if m.get("localbusiness_jsonld") else
                "no structured business information found"))
    seo.append(("Secure connection", PASS if m.get("https") else FAIL, ""))
    out["seo_local"] = seo

    # ---- 5. Trust ----------------------------------------------------------
    tr: List[Tuple[str, str, str]] = []
    rc = m.get("aggregate_review_count")
    if m.get("review_count_visible"):
        tr.append(("Review count visible to visitors", PASS,
                   f"{rc} reviews shown" if rc else ""))
    elif m.get("google_badge") or rc:
        tr.append(("Review count visible to visitors", FAIL,
                   "a reviews badge is shown but no number — visitors can't "
                   "see how many reviews you have"))
    else:
        tr.append(("Review count visible to visitors", FAIL,
                   "no reviews shown on the page"))
    tr.append(("Star rating visible to visitors",
               PASS if m.get("aggregate_rating_value") else FAIL, ""))
    # Address: the map embed / GBP link are proxies. If neither is present we
    # genuinely can't tell from markup whether the address is on the page —
    # the footer text may carry it. NOT CHECKED, not a warning.
    if m.get("map_embed") or m.get("gbp_link"):
        tr.append(("Business address shown", PASS, ""))
    else:
        tr.append(("Business address shown", NOT_CHECKED,
                   "no map or listing link found to confirm it"))
    tr.append(("Link to your Google listing",
               PASS if m.get("gbp_link") else FAIL, ""))
    yr = m.get("copyright_year")
    if yr:
        tr.append(("Copyright year current",
                   PASS if yr >= 2025 else FAIL, f"shows {yr}"))
    else:
        tr.append(("Copyright year current", NOT_CHECKED,
                   "no copyright line found"))
    tr.append(("Business email on own domain",
               FAIL if m.get("gmail_contact") else PASS,
               "uses a free email address" if m.get("gmail_contact") else ""))
    tr.append(("Real photos of your work", NOT_CHECKED,
               "needs a visual check"))
    tr.append(("Overall look and feel", NOT_CHECKED,
               "needs a visual check"))
    out["trust"] = tr

    return out


def reason_line(group_key: str, items: List[Tuple[str, str, str]]) -> str:
    """
    (b) — one line naming what failed in this area.

    Only failures. If everything passed, say so. Never longer than ~90 chars
    of content; this sits under a score on page 1.
    """
    fails = [label for label, status, _ in items if status == FAIL]
    if not fails:
        checked = [i for i in items if i[1] != NOT_CHECKED]
        return "all checks passed" if checked else "not enough data to check"
    shown = fails[:3]
    line = "; ".join(s.lower() for s in shown)
    if len(fails) > 3:
        line += f"; +{len(fails) - 3} more"
    return line


def counts(items: List[Tuple[str, str, str]]) -> Tuple[int, int, int]:
    p = sum(1 for i in items if i[1] == PASS)
    f = sum(1 for i in items if i[1] == FAIL)
    n = sum(1 for i in items if i[1] == NOT_CHECKED)
    return p, f, n
