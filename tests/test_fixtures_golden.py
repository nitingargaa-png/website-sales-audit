"""
test_fixtures_golden.py — locks the three fixtures in docs/fixtures_golden.md.

These use synthetic HTML carrying the same signals the real pages carry, so the
suite runs offline and deterministically. That is a DELIBERATE tradeoff, and it
has a known cost: docs/fixtures_golden.md itself records the lesson —

    "A passing test suite against synthetic fixtures does not prove the
     consumer handles real producer output. Synthetic fixtures test the code
     path the author imagined; real producer output exercises the code path
     real data takes."

So this suite catches rule regressions, NOT fetch/parse regressions against the
live pages. Keep running the manual smoke test in docs/fixtures_golden.md
against the real URLs as well. This is a faster inner loop, not a replacement.

Run:  python -m pytest tests/test_fixtures_golden.py -v
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "execution"))

from audit import detect, applicability  # noqa: E402


# Fixture 1 HTML CORRECTED 2026-07-16 against the live page.
#
# The original version of this fixture contained '"reviewCount":"166"' in
# JSON-LD. That number was NEVER on the site — it came from GBP data pulled via
# SerpApi during a v12 run, and it was stale (Google now shows 266).
#
# The real homepage, verified by screenshot: a "Google Reviews" badge, five
# gold stars, one testimonial from a named customer, and NO number anywhere.
# The site is also JS-built, so the static shell carries essentially nothing.
#
# The fixture asserted a signal the page does not emit, so it passed while the
# live run failed. docs/fixtures_golden.md already warned about exactly this:
# "synthetic fixtures test the code path the author imagined; real producer
# output exercises the code path real data takes."
F1_HTML = """<html><head>
<title>Home</title>
<meta name="viewport" content="width=device-width">
<script src="https://static.wixstatic.com/x.js"></script>
<script src="/app.js"></script><script src="/vendor.js"></script>
</head><body><div id="root"></div></body></html>"""

# What Jina recovers from that shell. Note: NO review count — matches reality.
F1_RENDERED = """Mississauga Plumbing Service Ltd. Residential & Commercial.
Call the best, flush the rest. 647-550-4003 plumbers4mississauga@gmail.com
[647-550-4003](tel:6475504003) GET IT FIXED FAST. No matter what time of the
day, we are here to help our customers. Whether it's a leak in the basement,
broken water pipe, drain blockage or frozen pipe, we will handle the case
immediately. WhatsApp Call/Chat Now. THE SERVICES WE OFFER: Piping, Drain &
Sewer Lines, Repair Leaks, Toilets, Unclogging. We provide friendly and
professionally plumbing service with reasonable price across GTA with the best
quality services over 15 years! SATISFIED CUSTOMERS. Google Reviews. The
Plumber was on time, polite, and provided excellent service. STEVE JOSEPH.
Eglinton Ave W and Hurontario St, Mississauga, On."""

F2_HTML = """<html><head><title>Mr. Rooter Plumbing</title></head><body>
<h1>Mr. Rooter Plumbing</h1>
<a href="/franchise">Own a Franchise</a>
<p>Serving throughout the United States. 24/7 emergency service.</p>
<footer>Each location is independently owned and operated.
A Neighborly Company. International Franchise Association member.</footer>
</body></html>"""

F3_HTML = """<html><head><title>Warm &amp; Cool London</title></head><body>
<h1>Warm &amp; Cool London</h1>
<p>Warming London homes since 2007. Vaillant boilers, Boiler Upgrade Scheme,
Heat Geek accredited. 24 hour emergency callout.</p></body></html>"""


FIXTURES = [
    pytest.param(
        "fixture-1-applicable-baseline",
        F1_HTML, "https://mississaugaplumbingservices.com",
        # vaai CORRECTED true -> null 2026-07-16. The page states no review
        # count, so no call-volume proxy is observable from the site. Google
        # shows 266 reviews; the homepage shows a badge and one testimonial.
        # Emitting true would mean guessing volume from trade typicality, which
        # the rule explicitly forbids. null is the honest answer.
        {"ghl_upgrade_candidate": False, "mctb_applicable": True,
         "vaai_applicable": None, "disqualifiers": []},
        F1_RENDERED,
        id="f1_applicable_baseline"),
    pytest.param(
        "fixture-2-national-chain",
        F2_HTML, "https://www.mrrooter.com",
        {"ghl_upgrade_candidate": False, "mctb_applicable": None,
         "vaai_applicable": None, "disqualifiers": ["national_chain"]},
        None,
        id="f2_national_chain"),
    pytest.param(
        "fixture-3-out-of-service-area",
        F3_HTML, "https://warmandcoollondon.co.uk",
        {"ghl_upgrade_candidate": False, "mctb_applicable": None,
         "vaai_applicable": None, "disqualifiers": ["out_of_service_area"]},
        None,
        id="f3_out_of_service_area"),
]


@pytest.mark.parametrize("name,html,url,expected,rendered", FIXTURES)
def test_triage_meta_fields(name, html, url, expected, rendered):
    m = detect.scan(html, url, rendered_text=rendered)
    text = rendered or detect._strip_tags(html)
    ghl, mctb, vaai, dq = applicability.evaluate(m, text, {}, url)
    got = {"ghl_upgrade_candidate": ghl, "mctb_applicable": mctb,
           "vaai_applicable": vaai, "disqualifiers": dq}
    for k, v in expected.items():
        assert got[k] == v, f"{name}: {k} expected {v!r}, got {got[k]!r}"


def test_disqualified_still_emits_applicability_independently():
    """
    PRODUCER/CONSUMER SPLIT — the contract point fixtures_golden.md asks us
    to flag on any change.

    When a disqualifier fires, the producer must still evaluate mctb/vaai per
    their OWN rules. They come out null here because the signals are genuinely
    unobservable on a franchise corporate page — NOT because a disqualifier
    fired. If someone "optimises" this by short-circuiting to False when
    disqualifiers is non-empty, this test fails. That is the point.
    """
    m = detect.scan(F2_HTML, "https://www.mrrooter.com")
    text = detect._strip_tags(F2_HTML)
    _, mctb, vaai, dq = applicability.evaluate(m, text, {}, "https://www.mrrooter.com")
    assert dq == ["national_chain"]
    assert mctb is None, "must be null (unobservable), never False (short-circuit)"
    assert vaai is None, "must be null (unobservable), never False (short-circuit)"


def test_hidden_social_proof_caps_trust():
    """
    Badge, five stars, one testimonial, NO number. Google shows 4.8 from 266.
    Verified by screenshot 2026-07-16. Most winnable fix in the audit — must
    never score above 2 no matter how good the design looks.
    """
    from audit import score as sm
    m = detect.scan(F1_HTML, "https://mississaugaplumbingservices.com",
                    rendered_text=F1_RENDERED)
    assert m["google_badge"], "badge is present in rendered content"
    assert not m["review_count_visible"], "no count on first load"
    assert not m["review_count_after_js"], "no count even after JS"
    assert sm.score_trust(m, judged=5) <= 2


def test_js_shell_is_not_dead_site():
    """
    REGRESSION — caught on the first live run, 2026-07-16.

    mississaugaplumbingservices.com is a JS-only build. A static fetch returns
    a near-empty shell, and the original dead_site rule (visible_text < 100)
    fired on it. The site is a live business with 166 reviews — arguably the
    best rebuild prospect in the list — and it was being silently disqualified
    out of every batch.

    A JS shell has structure: a title, scripts, sometimes schema. A dead site
    has nothing. That is the distinction.
    """
    js_shell = """<html><head><title>Mississauga Plumbing Services</title>
    <script src="/app.js"></script><script src="/vendor.js"></script>
    <script src="/runtime.js"></script></head>
    <body><div id="root"></div></body></html>"""
    m = detect.scan(js_shell, "https://mississaugaplumbingservices.com")
    text = detect._strip_tags(js_shell)
    _, _, _, dq = applicability.evaluate(
        m, text, {}, "https://mississaugaplumbingservices.com")

    assert m["js_only_suspected"], "should flag as JS-rendered"
    assert "dead_site" not in dq, "JS shell is a live business, not a dead site"


def test_genuinely_dead_site_is_flagged():
    """The counter-case: nothing at all. No title, no scripts, no phone."""
    dead = "<html><body></body></html>"
    m = detect.scan(dead, "https://example-parked.com")
    text = detect._strip_tags(dead)
    _, _, _, dq = applicability.evaluate(m, text, {}, "https://example-parked.com")
    assert "dead_site" in dq


def test_judge_refuses_on_invisible_content():
    """
    REGRESSION — the fabricated 404, live run 2026-07-16.

    Handed 83 chars from a JS shell, the judged tier reported "The homepage
    shows a 404 'Page Not Found' error" on a site that returned HTTP 200 with
    17KB of HTML. It had seen the string "Page Not Found" in a pre-hydration
    React component. Three findings, an overview, and a fix plan were built on
    top of that error. The report told a working plumbing business with 166
    five-star reviews to call their host about a broken homepage.

    Below the threshold the judge must return None without calling the API.
    """
    from audit import judge
    shell_text = "Page Not Found"
    result = judge.assess(shell_text, {}, {}, "https://example.com")
    assert result is None, "must refuse, not fabricate"


def test_scoring_nulls_judged_areas_when_judge_refused():
    """
    If we could not see the site, we cannot rate its trust or conversion.
    Scoring them 1/5 pretends we looked.

    The 4/100 from the live run had Trust at 1/5 on a business with 166
    five-star reviews that were simply invisible to a static fetch.
    """
    from audit import score as sm
    m = detect.scan("<html><head><title>X</title></head><body></body></html>",
                    "https://example.com")
    psi = {"measured": True, "source": "lab", "runs_ok": 3,
           "lcp_s": (18.4, 24.7), "inp_ms": None, "tbt_ms": (26, 1508),
           "cls": (0.0, 0.0), "perf_score": (31, 55)}

    sc = sm.compute(m, psi, {}, judge_available=False)
    assert sc["elements"]["trust"] is None
    assert sc["elements"]["conversion"] is None
    assert sc["elements"]["lead_capture"] is None
    assert sc["elements"]["speed"] == 1, "speed IS measured — 18s LCP"
    assert sc["elements"]["seo_local"] is not None, "title/meta ARE measurable"
    assert sc["weight_covered"] < 100, "must report partial coverage"


JS_SHELL_STATIC = """<html><head><title>Home</title>
<script src="/a.js"></script><script src="/b.js"></script>
<script src="/c.js"></script></head><body><div id="root"></div></body></html>"""

JS_RENDERED_TEXT = """Mississauga Plumbing Service Ltd. 24/7 Emergency Plumber
in Mississauga. Call 647-550-4003 or WhatsApp us. Eglinton Ave W and Hurontario
St, Mississauga, ON. Rated 4.9 stars based on 166 Google reviews. Drain
cleaning, water heater installation, sump pump repair, emergency callout.
Licensed and insured. Serving Mississauga since 2011."""


def test_rendered_text_feeds_text_derived_signals():
    """
    REGRESSION — live run 2026-07-16.

    Jina recovered 3,685 chars from a JS site, but detect.scan() only ever saw
    the 4-char static shell. Every text-derived signal came back blank:
    aggregate_review_count=None on a business with 166 reviews. The rendered
    text reached the judge but never reached the detector or the applicability
    rules, so TRIAGE_META emitted null/null where fixture 1 pins true/true.
    """
    m_static = detect.scan(JS_SHELL_STATIC, "https://mississaugaplumbingservices.com")
    assert m_static["aggregate_review_count"] is None, "static sees nothing"

    m_rendered = detect.scan(JS_SHELL_STATIC,
                             "https://mississaugaplumbingservices.com",
                             rendered_text=JS_RENDERED_TEXT)
    assert m_rendered["aggregate_review_count"] == 166
    assert m_rendered["aggregate_rating_value"] == 4.9
    assert m_rendered["phone_in_text"], "phone is in the rendered text"


def test_js_only_flag_uses_static_text_even_when_rendered():
    """
    js_only_suspected must ALWAYS reflect what a static fetch saw. If a
    renderer had to run JavaScript to find the content, that IS the finding —
    Google has the same problem. Rendering must not mask it.
    """
    m = detect.scan(JS_SHELL_STATIC, "https://example.com",
                    rendered_text=JS_RENDERED_TEXT)
    assert m["js_only_suspected"] is True
    assert m["visible_text_len"] < 500
    assert m["rendered_text_len"] > 100


def test_leak_validator_catches_internal_field_names():
    """
    MECHANISM, not guideline.

    The 2026-07-16 report shipped this to a prospect-facing finding:
      "the measured fact 'tel_href: false' means it is not coded as a real
       phone link"
    tel_href is an internal variable name. The voice rules in the system prompt
    said not to do this. It did it anyway. Hence a validator.
    """
    from audit import judge
    leaked = {"top_findings": [
        {"evidence": "The measured fact 'tel_href: false' means no phone link.",
         "impact": "Customers cannot tap.", "fix": "Add one."}]}
    assert judge._leaks(leaked), "must catch tel_href"

    html_leak = {"top_findings": [
        {"evidence": "Phone is plain text.", "impact": "Cannot tap.",
         "fix": 'Wrap it like <a href="tel:6475504003">647-550-4003</a>'}]}
    assert judge._leaks(html_leak), "must catch HTML tags — PDF strips them"

    clean = {"top_findings": [
        {"evidence": "Your phone number is plain text, not a tap-to-call link.",
         "impact": "On a phone, customers must dial by hand.",
         "fix": "Ask your web person to make the number tappable."}]}
    assert not judge._leaks(clean), "clean prose must pass"


def test_structure_detectors():
    """(c) — headings, internal links, service pages, city-in-title."""
    html = """<html><head><title>Plumbing Services in Mississauga, ON | Acme</title>
    </head><body><h1>Acme Plumbing</h1><h2>Our Services</h2><h2>About Us</h2>
    <a href="/services/drain-cleaning">Drains</a>
    <a href="/services/water-heater">Water heaters</a>
    <a href="/emergency">Emergency</a>
    <a href="/about">About</a><a href="/contact">Contact</a>
    <a href="https://facebook.com/acme">FB</a>
    <a href="tel:9055551234">Call</a><a href="#top">Top</a>
    </body></html>"""
    m = detect.scan(html, "https://acmeplumbing.ca")
    assert m["h1_count"] == 1
    assert m["h1_text"] == "Acme Plumbing"
    assert m["h2_count"] == 2
    assert m["internal_links"] == 5, "tel:, #anchor, and external excluded"
    assert m["external_links"] == 1
    assert m["service_pages"] >= 3
    assert m["city_in_title"] is True


def test_js_site_shows_zero_internal_links():
    """
    A JS shell has no links for a crawler to follow. That is the finding, not
    a detector failure — Google hits the same wall.
    """
    m = detect.scan(JS_SHELL_STATIC, "https://example.com",
                    rendered_text=JS_RENDERED_TEXT)
    assert m["internal_links"] == 0
    assert m["h1_count"] == 0


def test_checklist_covers_all_five_groups():
    """(a) — every group the practitioner feedback named must appear."""
    from audit import checklist
    m = detect.scan(F1_HTML, "https://mississaugaplumbingservices.com",
                    rendered_text=F1_RENDERED)
    psi = {"measured": True, "source": "lab", "runs_ok": 3,
           "lcp_s": (18.6, 22.0), "inp_ms": None, "tbt_ms": (1363, 2789),
           "cls": (0.0, 0.0), "perf_score": (31, 55)}
    cl = checklist.build(m, psi, {"lcp": "FAIL", "inp": None, "cls": "PASS"})
    for _, key in checklist.GROUPS:
        assert key in cl and cl[key], f"group {key} is empty"


def test_unmeasurable_items_say_not_checked_not_fail():
    """
    NOT CHECKED is load-bearing honesty. Thumb-friendliness and 'modern look'
    need a rendered screenshot. Scoring them FAIL would be pretending we
    looked; omitting them would imply we had nothing to say.
    """
    from audit import checklist
    m = detect.scan(F1_HTML, "https://x.com", rendered_text=F1_RENDERED)
    psi = {"measured": False}
    cl = checklist.build(m, psi, {})
    labels = {lbl: st for items in cl.values() for lbl, st, _ in items}
    assert labels["Buttons sized for thumbs"] == checklist.NOT_CHECKED
    assert labels["Overall look and feel"] == checklist.NOT_CHECKED
    assert labels["Real photos of your work"] == checklist.NOT_CHECKED
    # INP has no CrUX record for low-traffic sites — must not be invented.
    assert labels["Responsiveness to taps"] == checklist.NOT_CHECKED


def test_reason_line_names_actual_failures():
    """(b) — 'Being found 1/5' alone tells the owner nothing."""
    from audit import checklist
    items = [("Page title", checklist.FAIL, "4 characters"),
             ("Secure connection", checklist.PASS, ""),
             ("Section headings", checklist.FAIL, "0 found")]
    line = checklist.reason_line("seo_local", items)
    assert "page title" in line
    assert "section headings" in line
    assert "secure" not in line, "passes must not appear in the reason line"

    all_pass = [("Page title", checklist.PASS, "")]
    assert checklist.reason_line("seo_local", all_pass) == "all checks passed"


def test_strips_tap_to_call_praise_when_js_only():
    """
    REGRESSION — live run 2026-07-16. The same report said, two inches apart:

      MEASURED  Tap-to-call: YES, but only after scripts run
      WORKING   "Your phone number appears as a tap-to-call link in the
                 footer, making it easy to dial from a phone"

    The judge reads renderer output where the link exists; the measured block
    reads delivered HTML where it doesn't. A prospect who spots the
    contradiction stops trusting the whole document. Prompt rules did not hold
    on the first attempt, so this is a mechanism.
    """
    from audit import judge
    measured = {"tel_js_only": True, "tel_href": False, "tel_rendered": True}
    judged = {"working": [
        "The site is served over a secure connection.",
        "Your phone number appears as a tap-to-call link in the footer, "
        "making it easy to dial from a phone.",
        "WhatsApp is offered as a contact option.",
    ]}
    out = judge._strip_contradictions(judged, measured)
    assert len(out["working"]) == 2
    assert not any("tap-to-call" in w.lower() for w in out["working"])
    assert any("secure" in w.lower() for w in out["working"]), "keeps the rest"


def test_keeps_tap_to_call_praise_when_genuinely_present():
    """The counter-case: a real tel: link in delivered HTML is worth praising."""
    from audit import judge
    measured = {"tel_js_only": False, "tel_href": True, "tel_rendered": True}
    judged = {"working": [
        "Your phone number is a tap-to-call link at the top of the page."]}
    out = judge._strip_contradictions(judged, measured)
    assert len(out["working"]) == 1


def test_unmeasured_speed_is_null_not_three():
    """
    v12 scored unmeasurable areas 3-as-neutral and let that contribute to the
    total, silently inflating the score on every site where PSI failed. Since
    PSI was optional in v12, that was potentially most sites.
    """
    from audit import psi as pm
    assert pm.element_score({"measured": False}) is None
    assert pm.element_score({"measured": True, "lcp_s": None}) is None
