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
                             match_manufacturer, normalize_name)
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
