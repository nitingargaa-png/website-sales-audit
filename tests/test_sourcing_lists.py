"""
Regression tests for sourcing list content and matching scope.

These pin INCIDENTS, not preferences. Each test names the bug it prevents
and the real data that exposed it. Same shape as the dead_site guard in
execution/audit/applicability.py: a case that failed before and passes now.

If one of these fails, do not adjust the test. The list changed and it
probably changed back toward v4.6.
"""
import os
import sys

import pytest

# Repo root on the path so `sourcing` resolves. Mirrors the sys.path.insert
# in tests/test_fixtures_golden.py, which does the same for execution/.
# There is no conftest.py and no pytest config in this repo; tests carry
# their own path setup. Following that rather than adding a new mechanism.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sourcing import lists  # noqa: E402
from sourcing.status import (classify, match_franchise_brand,  # noqa: E402
                             match_location_path, match_manufacturer,
                             normalize_name)
from sourcing.normalize import strip_tracking  # noqa: E402
from sourcing.dedupe import (dedupe_by_place_id,              # noqa: E402
                             flag_multi_location)


def _row(**kw):
    r = {"business_name": "", "domain": "", "url": None, "status": None,
         "review_reason": None, "disqualify_reason": None,
         "multi_location_domain": False}
    r.update(kw)
    return r


# --- INCIDENT 1: bare "overhead door" binned independents ----------------
#
# v4.6's KNOWN_CHAIN_BRANDS listed both "overhead door company" (a real
# franchise) and bare "overhead door" (what the product is called).
# Matched as a phrase, the bare term fires on independent operators whose
# names simply describe their trade. This is the dead_site failure again:
# a rule firing on the trade term itself, silently binning the prospects
# the pipeline exists to find.
#
# Exposed 2026-07-17 by testing the list against the live Mississauga
# garage door batch and plausible variants. "Candoor Overhead Doors Ltd."
# survived only because "Candoor" breaks the token boundary — luck, not
# design.

INDEPENDENTS_WITH_TRADE_TERM = [
    "Mississauga Overhead Door Repair",
    "Smith Overhead Door Service",
    "Candoor Overhead Doors Ltd.",
    "Toronto Overhead Doors",
    "Peel Overhead Door & Gate",
]


@pytest.mark.parametrize("name", INDEPENDENTS_WITH_TRADE_TERM)
def test_overhead_door_generic_term_does_not_match_independents(name):
    """Bare 'overhead door' must never be in FRANCHISE_BRANDS."""
    assert match_franchise_brand(name, "") is None, (
        f"{name!r} matched a franchise brand. If bare 'overhead door' was "
        f"re-added to lists.FRANCHISE_BRANDS from v4.6, remove it — it is "
        f"a trade term, not a brand. See lists.py departure 1.")


def test_bare_overhead_door_absent_from_brand_list():
    """Direct guard on the list itself, independent of matching."""
    assert "overhead door" not in lists.FRANCHISE_BRANDS
    assert "overhead doors" not in lists.FRANCHISE_BRANDS


def test_overhead_door_company_still_matches():
    """The actual franchise must still be caught. Deleting the bare term
    must not blind the rule to the real brand."""
    assert match_franchise_brand("Overhead Door Company of Toronto", "")
    assert match_franchise_brand("", "overheaddoor.com")


# --- INCIDENT 2: social domains are the lane, not a reject ---------------
#
# v4.6's AGGREGATOR_DOMAINS merged facebook/instagram/linkedin with
# yelp/angi/homeadvisor. A prospect whose GBP website is a Facebook page
# has no website — that is the no_website lane, the highest-value segment
# — not a directory listing. Porting the merged set would hard-exclude
# the best prospects.

def test_social_domain_routes_to_lane_not_excluded():
    r = classify(_row(business_name="Bob's Garage Doors",
                      domain="facebook.com",
                      url="https://facebook.com/bobsgaragedoors"))
    assert r["status"] == "clean"
    assert r["review_reason"] == "no_website_lane"
    assert r["url"] is None


def test_directory_domain_is_excluded():
    r = classify(_row(business_name="Bob's Garage Doors",
                      domain="yelp.com",
                      url="https://yelp.com/biz/bobs"))
    assert r["status"] == "excluded"
    assert r["disqualify_reason"] == "directory_domain"


def test_social_and_directory_sets_are_disjoint():
    assert not (lists.SOCIAL_DOMAINS & lists.DIRECTORY_DOMAINS)


# --- INCIDENT 3: no bare \bfranchise\b against a URL blob ----------------
#
# v4.6's EXPLICIT_FRANCHISE_PATTERNS matched r"\bfranchise\b" against a
# blob containing the website URL, hard-excluding any prospect whose domain
# contained the word, with a reason that read like a page-content finding
# but never touched a page.

def test_franchise_word_in_domain_does_not_exclude():
    r = classify(_row(business_name="Franchise City Garage Doors",
                      domain="franchisecitydoors.ca",
                      url="https://franchisecitydoors.ca"))
    assert r["status"] != "excluded"


# --- live data: the rule must still catch the real franchise ------------
#
# From the live 2026-07-17 Mississauga batch: 20 real names, exactly one
# franchise. Zero false positives is the bar.

LIVE_MISSISSAUGA_20 = [
    "Ontario Garage Doors", "The Garage Door Depot", "Motion Garage Doors",
    "DOORMASTER GARAGE DOORS", "JT Garage Door",
    "Precision Garage Door Service", "Garage Master Tech",
    "Dodds Garage Doors", "People's Garage Doors",
    "Mississauga Garage Door Repair Pro", "Zenith Garage Door",
    "Royal Garage Doors", "Adams Door Systems Inc",
    "Mississauga Garage Door Repairs", "Prime Garage Door",
    "ADA Door Repair", "Garage Door Expert",
    "Mississauga Garage Door Repair Master", "Candoor Overhead Doors Ltd.",
    "Garage One Inc.",
]


def test_live_batch_catches_precision_only():
    hits = {n for n in LIVE_MISSISSAUGA_20 if match_franchise_brand(n, "")}
    assert hits == {"Precision Garage Door Service"}, (
        f"expected exactly one franchise in the live batch, got {hits}")


# --- dedupe: place_id only ----------------------------------------------

def test_dedupe_never_collapses_same_name_different_place():
    """Two real businesses, same name, different cities. v4.6 normalised
    names and deduped on them, silently losing one."""
    rows = [_row(business_name="A1 Garage Door", gbp_place_id="P1"),
            _row(business_name="A1 Garage Door", gbp_place_id="P2")]
    out, dropped = dedupe_by_place_id(rows)
    assert len(out) == 2 and dropped == 0


def test_dedupe_drops_repeat_place_id():
    rows = [_row(gbp_place_id="P1"), _row(gbp_place_id="P1")]
    out, dropped = dedupe_by_place_id(rows)
    assert len(out) == 1 and dropped == 1


def test_multi_location_flags_all_rows_on_hot_domain():
    rows = [_row(domain="chain.com") for _ in range(3)] + [_row(domain="solo.ca")]
    flag_multi_location(rows)
    assert [r["multi_location_domain"] for r in rows] == [True, True, True, False]


def test_multi_location_below_threshold_not_flagged():
    rows = [_row(domain="two.com") for _ in range(2)]
    flag_multi_location(rows)
    assert not any(r["multi_location_domain"] for r in rows)


# --- precedence ----------------------------------------------------------

def test_excluded_beats_review():
    """A directory listing that is also franchise-named is excluded.
    There is nothing to review."""
    r = classify(_row(business_name="Mr Rooter Plumbing", domain="yelp.com",
                      url="https://yelp.com/biz/mr-rooter"))
    assert r["status"] == "excluded"
    assert r["disqualify_reason"] == "directory_domain"


def test_franchise_routes_to_review_not_excluded():
    """franchise_brand is a guess about corporate structure from a string.
    A human look changes the outcome, so it reviews, not excludes."""
    r = classify(_row(business_name="Precision Garage Door Service",
                      domain="precisiondoor.ca",
                      url="https://precisiondoor.ca"))
    assert r["status"] == "review"
    assert "franchise_brand" in r["review_reason"]


def test_out_of_area_excluded():
    r = classify(_row(business_name="Warm & Cool London",
                      domain="warmandcoollondon.co.uk",
                      url="https://warmandcoollondon.co.uk"))
    assert r["status"] == "excluded"
    assert r["disqualify_reason"] == "out_of_area"


def test_clean_row_stays_clean():
    r = classify(_row(business_name="Motion Garage Doors",
                      domain="motiongaragedoors.ca",
                      url="https://motiongaragedoors.ca"))
    assert r["status"] == "clean"
    assert r["review_reason"] is None


# --- INCIDENT 4: a franchise scored 70 and was queued for a pitch --------
#
# doddsdoors.com/location/mississauga/ reached the audit queue, scored
# 70/100, would have been pitched. Dodds is a chain. Neither franchise_brand
# (no name match) nor multi_location_domain (needs 3+ rows) could see it.
# A city in the URL PATH is the signal.
#
# The rule was then refined on the live 2026-07-19 plumbing/HVAC batch,
# where a bare-city rule over-fired on "of <City>" businesses. Three
# refinements — see match_location_path docstring:
#   1. campaign prefixes (/ads/) never count
#   2. explicit /location(s)/<city> always counts
#   3. bare /<city> spared when name has the city AND nothing else flags it

CHAINS_FLAGGED = [
    ("The Garage Door Depot", "http://x.ca/mississauga-oakville", False),
    ("Dodds Garage Doors", "http://x.ca/location/mississauga/", False),
    ("Fortify Services Mississauga", "http://x.ca/locations/mississauga/", False),
    ("Enercare", "http://x.ca/locations/mississauga", False),
    ("LG Home Comfort", "http://x.ca/locations/mississauga/", False),
    ("Reliance Heating", "http://x.ca/mississauga/", False),
    ("Canadian Heating and Air", "http://x.ca/hamilton/", False),
    ("Maple Leaf Plumber", "http://x.ca/hamilton/", False),
    ("Beyond HVAC", "http://x.ca/mississauga", False),
    # name has city BUT another signal fires -> stays flagged
    ("Mr Rooter Plumbing of Mississauga ON", "http://mrrooter.ca/mississauga/", False),
    ("John The Plumber", "http://johntheplumber.ca/mississauga", True),
    ("Dr HVAC", "http://drhvac.ca/mississauga/", True),
]

INDEPENDENTS_CLEARED = [
    # /ads/ campaign path
    ("Drain 1 Plumbers In Mississauga", "http://d1.ca/ads/mississauga", False),
    # name is the city, bare path, nothing else flags
    ("PLUMBER ON DEMAND of MISSISSAUGA ON", "http://pod.ca/mississauga", False),
    ("Plumber On Dial Of Mississauga", "http://pd.ca/mississauga", False),
    # city in DOMAIN not path
    ("Garage Repair Mississauga", "http://garagerepairmississauga.ca/", False),
    ("Ontario Garage Doors", "https://ontariogaragedoors.ca/", False),
]


@pytest.mark.parametrize("name,url,multi", CHAINS_FLAGGED)
def test_location_path_flags_chains(name, url, multi):
    r = classify(_row(business_name=name, domain=url.split("/")[2], url=url,
                      multi_location_domain=multi))
    assert r["status"] == "review", f"{name} {url} should be flagged"


@pytest.mark.parametrize("name,url,multi", INDEPENDENTS_CLEARED)
def test_location_path_clears_independents(name, url, multi):
    r = classify(_row(business_name=name, domain=url.split("/")[2], url=url,
                      multi_location_domain=multi))
    assert r["status"] == "clean", (
        f"{name} {url} should clear. Live 2026-07-19 false positives: "
        f"/ads/ landing paths and 'of <City>' names on bare /<city>.")


def test_mr_rooter_flagged_despite_name_city():
    """Mr Rooter of Mississauga at /mississauga/ — name contains the city,
    so refinement 3 would spare it, BUT franchise_brand also fires. The
    other_signal guard keeps it flagged. Regression: if other_signal is
    dropped, a known franchise clears."""
    r = classify(_row(business_name="Mr Rooter Plumbing of Mississauga ON",
                      domain="mrrooter.ca",
                      url="http://mrrooter.ca/mississauga/"))
    assert r["status"] == "review"
    assert "mr rooter" in r["review_reason"]


def test_ads_path_never_franchise():
    """A /ads/<city> path is a Google Ads landing page, never franchise
    structure. Must clear even when the name does NOT contain the city —
    otherwise the guard is dead code masked by refinement 3. Live 2026-07-19:
    'Drain 1 Plumbers In Mississauga' /ads/mississauga."""
    from sourcing.status import match_location_path
    # name without the city: only the /ads/ guard can clear these
    assert match_location_path("http://x.ca/ads/mississauga",
                               name="Quality Drain Co") is None
    assert match_location_path("http://x.ca/lp/hamilton",
                               name="Best Plumbers") is None
    assert match_location_path("http://x.ca/landing/toronto",
                               name="Acme HVAC") is None


def test_explicit_location_prefix_beats_name_city():
    """Fortify Services Mississauga at /locations/mississauga/ — name has the
    city, but the /locations/ prefix is explicit multi-site declaration and
    wins over refinement 3."""
    from sourcing.status import match_location_path
    assert match_location_path(
        "http://x.ca/locations/mississauga/",
        name="Fortify Services Mississauga") is not None


def test_location_pattern_requires_slash_before_city():
    """The mechanism that keeps city-in-domain out. Independent of urlparse:
    verified by stubbing urlparse, at which point city-in-domain still did
    not match because the pattern requires a '/' before the city."""
    from sourcing.status import LOCATION_PATH
    assert not LOCATION_PATH.search("garagerepairmississauga.ca")
    assert not LOCATION_PATH.search("/garagerepairmississauga")
    assert LOCATION_PATH.search("/mississauga")


# --- INCIDENT 5: tracking params reached the audit -----------------------
#
# Places returns the business's registered websiteUri, tracking params and
# all. Live 2026-07-17:
#   bmgaragedoor.com/ca?utm_source=GoogleMyBusiness&...&utm_campaign=LIMMO
# PSI then measures the tracked URL and the report shows one to the
# prospect. Dedupe was never affected (that is place_id) and neither was
# domain_of() (urlparse().netloc does not see the query).

def test_strip_tracking_removes_utm():
    out = strip_tracking(
        "https://www.bmgaragedoor.com/ca?utm_source=GoogleMyBusiness"
        "&utm_medium=GoogleMyBusiness&utm_campaign=LIMMO")
    assert out == "https://www.bmgaragedoor.com/ca"


def test_strip_tracking_keeps_real_params():
    """Only known tracking prefixes go. Some sites route real content
    through a query param; dropping the whole string would fetch the wrong
    page."""
    assert strip_tracking("https://example.com/p?id=42&utm_source=x") == \
        "https://example.com/p?id=42"


def test_strip_tracking_passthrough():
    assert strip_tracking("https://ontariogaragedoors.ca/") == \
        "https://ontariogaragedoors.ca/"
    assert strip_tracking(None) is None
