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


F1_HTML = """<html><head>
<title>Mississauga Plumbing Services - Emergency Plumber Mississauga</title>
<meta name="viewport" content="width=device-width">
<script src="https://static.wixstatic.com/x.js"></script></head>
<body><h1>Mississauga Plumbing Services</h1>
<p>24/7 emergency plumbing. Call (905) 555-1234. info@gmail.com</p>
<img src="Google-Reviews-badge.png">
<script type="application/ld+json">
{"@type":"Plumber","aggregateRating":{"ratingValue":"4.9","reviewCount":"166"}}
</script></body></html>"""

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
        {"ghl_upgrade_candidate": False, "mctb_applicable": True,
         "vaai_applicable": True, "disqualifiers": []},
        id="f1_applicable_baseline"),
    pytest.param(
        "fixture-2-national-chain",
        F2_HTML, "https://www.mrrooter.com",
        {"ghl_upgrade_candidate": False, "mctb_applicable": None,
         "vaai_applicable": None, "disqualifiers": ["national_chain"]},
        id="f2_national_chain"),
    pytest.param(
        "fixture-3-out-of-service-area",
        F3_HTML, "https://warmandcoollondon.co.uk",
        {"ghl_upgrade_candidate": False, "mctb_applicable": None,
         "vaai_applicable": None, "disqualifiers": ["out_of_service_area"]},
        id="f3_out_of_service_area"),
]


@pytest.mark.parametrize("name,html,url,expected", FIXTURES)
def test_triage_meta_fields(name, html, url, expected):
    m = detect.scan(html, url)
    text = detect._strip_tags(html)
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
    """166 reviews earned, zero shown. Most winnable fix in the audit.
    Must never score above 2."""
    from audit import score as sm
    m = detect.scan(F1_HTML, "https://mississaugaplumbingservices.com")
    assert m["aggregate_review_count"] == 166
    assert not m["review_count_visible"]
    assert sm.score_trust(m, judged=5) <= 2


def test_unmeasured_speed_is_null_not_three():
    """
    v12 scored unmeasurable areas 3-as-neutral and let that contribute to the
    total, silently inflating the score on every site where PSI failed. Since
    PSI was optional in v12, that was potentially most sites.
    """
    from audit import psi as pm
    assert pm.element_score({"measured": False}) is None
    assert pm.element_score({"measured": True, "lcp_s": None}) is None
