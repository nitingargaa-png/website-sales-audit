"""
Tests for sourcing/cache.py.

Pins INCIDENTS. Each test names the bug it prevents.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sourcing import cache as c  # noqa: E402


@pytest.fixture
def cdir(tmp_path):
    return str(tmp_path / "cache")


def test_round_trip(cdir):
    c.put("garage door", "Mississauga ON", [{"id": "P1"}], "", cache_dir=cdir)
    hit = c.get("garage door", "Mississauga ON", "", cache_dir=cdir)
    assert hit["places"] == [{"id": "P1"}]


def test_miss_returns_none(cdir):
    assert c.get("hvac", "Hamilton ON", "", cache_dir=cdir) is None


# --- INCIDENT: cached page token ----------------------------------------
#
# A first version cached only the places, not the nextPageToken. On a cache
# hit the caller had no token, the pagination loop broke after page 1, and
# a cached 60-row cell silently became a 20-row cell. Cache the answer AND
# the continuation.

def test_next_token_is_cached(cdir):
    c.put("garage door", "Mississauga ON", [{"id": "P1"}], "",
          cache_dir=cdir, next_token="TOK1")
    hit = c.get("garage door", "Mississauga ON", "", cache_dir=cdir)
    assert hit["next"] == "TOK1", (
        "the page token must survive the cache or paginated cells "
        "silently truncate to page 1")


def test_pages_cache_independently(cdir):
    c.put("garage door", "Mississauga ON", [{"id": "A"}], "",
          cache_dir=cdir, next_token="TOK1")
    c.put("garage door", "Mississauga ON", [{"id": "B"}], "TOK1",
          cache_dir=cdir, next_token=None)
    assert c.get("garage door", "Mississauga ON", "",
                 cache_dir=cdir)["places"] == [{"id": "A"}]
    assert c.get("garage door", "Mississauga ON", "TOK1",
                 cache_dir=cdir)["places"] == [{"id": "B"}]


# --- key hygiene ---------------------------------------------------------

def test_key_is_case_and_space_insensitive(cdir):
    c.put("Garage Door", "Mississauga ON", [{"id": "P1"}], "", cache_dir=cdir)
    assert c.get("garage door", "  mississauga on ", "", cache_dir=cdir)


def test_different_cells_do_not_collide(cdir):
    c.put("plumbing", "Hamilton ON", [{"id": "A"}], "", cache_dir=cdir)
    c.put("hvac", "Hamilton ON", [{"id": "B"}], "", cache_dir=cdir)
    assert c.get("plumbing", "Hamilton ON", "",
                 cache_dir=cdir)["places"] == [{"id": "A"}]


# --- expiry --------------------------------------------------------------

def test_ttl_expiry(cdir):
    c.put("plumbing", "Hamilton ON", [{"id": "P1"}], "", cache_dir=cdir)
    assert c.get("plumbing", "Hamilton ON", "", cache_dir=cdir, ttl=0) is None
    assert c.get("plumbing", "Hamilton ON", "", cache_dir=cdir, ttl=99999)


def test_default_ttl_is_seven_days():
    """Ported in concept from lead-engine CACHE_TTL_MS. Note lead-engine
    kept the TTL in the CALLER (google-data.js) and the cache had no expiry
    at all — a split that is easy to lose. Here the cache owns it."""
    assert c.TTL_SECONDS == 7 * 24 * 60 * 60


# --- robustness ----------------------------------------------------------

def test_corrupt_file_is_a_miss_not_a_crash(cdir):
    c.put("hvac", "Hamilton ON", [{"id": "X"}], "", cache_dir=cdir)
    f = os.path.join(cdir, os.listdir(cdir)[0])
    with open(f, "w") as fh:
        fh.write("{not json")
    assert c.get("hvac", "Hamilton ON", "", cache_dir=cdir) is None


def test_stats_and_clear(cdir):
    c.put("a", "b", [{"id": "1"}, {"id": "2"}], "", cache_dir=cdir)
    s = c.stats(cache_dir=cdir)
    assert s["fresh"] == 1 and s["rows"] == 2
    assert c.clear(cache_dir=cdir) == 1
    assert c.stats(cache_dir=cdir)["cells"] == 0
