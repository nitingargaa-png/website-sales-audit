"""
status.py — the three-way. Deterministic facts are lanes; ambiguous
signals are reviews.

    excluded  directory_domain | missing_business_name | out_of_area
    review    franchise_brand | manufacturer_dealer | multi_location_domain
    clean     everything else, including the no_website lane

WHY THREE STATES AND NOT A BOOL
The contract asks for `disqualified: bool`. A review lane is a third
state. Carrying `status` as the truth and deriving
`disqualified = (status == "excluded")` satisfies the contract literally
while leaving the third state expressible. Shape borrowed from v4.6's
detection_status.

WHAT IS NOT HERE

  no_website  A deterministic fact, not a judgment. status stays clean,
              url stays null, emit.write_audit_queue drops it on the url
              test. It is the highest-value segment (A1), not a reject.

  toll_free   A signal, carried, routed nowhere. Note the sign: v4.7 sent
              it to verify_manually as a risk. applicability.py treats
              call_tracking as a STRONG positive ("paid ads active — every
              missed call was paid for"). Same fact, opposite sign. It is
              evidence, not a problem.

  gbp_category / gbp_types
              Not a filter input. The live 2026-07-17 Mississauga batch
              returned primaryType="supplier" for 19 of 20 garage door
              companies and "service" for the 20th. Zero discriminating
              power. Three rows were miscategorised outright (a garage door
              company tagged parking_lot). Carried, never routed. A field
              that routes nothing cannot route a wrong value into a review
              lane — see the review-lane note below.

  national_chain
              Page-derived franchise disclosure. Different rule, different
              input, different name, owned by
              execution/audit/applicability.py. franchise_brand is
              GBP-derived (name + domain, before any page exists). They
              disagree on purpose: a single-location Neighborly franchisee
              with a generic name trips the audit and not the scraper; a
              franchise brand whose local page carries no disclosure trips
              the scraper and not the audit. Two rules, one label would
              mean picking which answer is wrong.

THE REVIEW LANE HOLDS CASES WHERE A HUMAN LOOK CHANGES THE OUTCOME.
Is this franchise-named business actually a franchise. Is this shared
domain one operator or four. Those are guesses about corporate structure
made from a string — exactly what a human is for and a regex is not.
"Google mislabelled a garage door company as a parking lot" changes
nothing: the name says garage door, the query says garage door, the site
will say garage door. Routing it to review means opening a queue to
conclude "yes, still a garage door company". Do that three times in twenty
rows on a field declared useless and the lane becomes a dumping ground for
anything unexpected — which is how it stops getting opened.
"""
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

from sourcing import lists

# Non-US/CA TLDs. Mirrors execution/audit/applicability.py NON_NA_TLDS.
# Not shared: that module is page-derived and imports differently. If this
# list grows a third copy, extract it.
NON_NA_TLDS = (".co.uk", ".uk", ".au", ".nz", ".ie", ".za", ".in", ".de",
               ".fr", ".es", ".it", ".nl", ".sg", ".ae")


def normalize_name(name: Optional[str]) -> str:
    """
    Lowercase, strip punctuation, collapse whitespace.

    NOT used for dedupe. v4.6 normalised names and deduped on them, which
    collapses two real businesses called "A1 Garage Door" in different
    cities into one row. Dedupe is place_id only. See sourcing/dedupe.py.
    """
    n = (name or "").lower()
    n = re.sub(r"[^a-z0-9\s]", " ", n)
    return re.sub(r"\s+", " ", n).strip()


def match_franchise_brand(name: str, domain: str) -> Optional[str]:
    """
    Brand match on NAME + DOMAIN only. Never page text.

    Phrase-boundary matched, longest brand first, so "precision garage
    door" wins over "precision door" on the same string.
    """
    if domain and domain in lists.FRANCHISE_DOMAINS:
        return domain
    n = normalize_name(name)
    if not n:
        return None
    padded = f" {n} "
    for brand in sorted(lists.FRANCHISE_BRANDS, key=len, reverse=True):
        b = normalize_name(brand)
        if b and f" {b} " in padded:
            return brand
    return None


def match_manufacturer(name: str) -> Optional[str]:
    n = normalize_name(name)
    padded = f" {n} "
    for term in sorted(lists.MANUFACTURER_TERMS, key=len, reverse=True):
        t = normalize_name(term)
        if t and f" {t} " in padded:
            return term
    return None


_CITY_ALT = "|".join(lists.LOCATION_PATH_CITIES)

# Explicit multi-location path prefixes. A business with one of these in the
# URL is telling you it has more than one location, regardless of name.
_LOC_PREFIX = (r"location|locations|branch|branches|area|areas"
               r"|service-area|service-areas|franchise|dealer|dealers"
               r"|store|stores")

# Campaign / ad landing prefixes. NEVER franchise structure — any business
# runs ads to a city-named landing page. Live 2026-07-19:
# "Drain 1 Plumbers ... /ads/mississauga" was a Google Ads path, not a chain.
_CAMPAIGN_PREFIX = ("ads", "lp", "landing", "ppc", "go", "promo", "campaign")

# City appears after an explicit location prefix: unambiguous chain.
LOCATION_PATH_PREFIXED = re.compile(
    r"/(?:" + _LOC_PREFIX + r")/(?:" + _CITY_ALT + r")", re.I)

# City appears as a bare path segment (/mississauga, /hamilton-oakville):
# a chain signal UNLESS the business name already contains that city and
# nothing else flags it — see match_location_path.
LOCATION_PATH_BARE = re.compile(
    r"/(?:" + _CITY_ALT + r")(?:-(?:" + _CITY_ALT + r"))?/?$", re.I)

# Kept as the public name the tests import; = prefixed OR bare.
LOCATION_PATH = re.compile(
    r"/(?:(?:" + _LOC_PREFIX + r")/)?(?:" + _CITY_ALT + r")"
    r"(?:-(?:" + _CITY_ALT + r"))?/?$", re.I)


def _name_contains_city(name: Optional[str], city: str) -> bool:
    if not name:
        return False
    return city.replace("-", "") in re.sub(r"[^a-z]", "", name.lower())


def match_location_path(url: Optional[str], name: Optional[str] = None,
                        other_signal: bool = False) -> Optional[str]:
    """
    A city in the URL PATH is a multi-location signal. In the DOMAIN it is
    not (local operators name their city constantly — see the domain tests).

    Three refinements from the live 2026-07-19 batch, where the bare-city
    rule over-fired on plumbing/HVAC "of <City>" businesses:

      1. Campaign prefixes (/ads/, /lp/, ...) never count. An ad landing
         page named for a city says nothing about location count.

      2. An explicit /location(s)/<city> or /branch/<city> prefix ALWAYS
         counts, even if the name contains the city — the prefix is the
         business declaring multiple sites (Fortify, Enercare, LG here).

      3. A BARE /<city> path is spared ONLY when the business name already
         contains that city AND no other rule flagged the row. "Plumber On
         Demand of Mississauga" at /mississauga is naming its one location,
         same as garagerepairmississauga.ca does in the domain. But if
         franchise_brand or multi_location_domain also fired (Mr Rooter,
         John The Plumber, Dr HVAC), the row is a chain and stays flagged.

    Genuinely ambiguous by path alone: a single bare /<city>, city in name,
    nothing else — e.g. "The Super Plumber - Hamilton" at /hamilton/. Cannot
    be told from an independent by URL structure. Resolved toward PROSPECT
    (not flagged); worst case the audit runs on a small local chain, which
    is cheap. The review lane is for what a signal can decide; this the
    signal cannot.

    Returns the matched path (for the review_reason) or None.
    """
    if not url:
        return None
    path = urlparse(url).path or "/"
    seg = [p for p in path.split("/") if p]
    if not seg:
        return None

    if seg[0].lower() in _CAMPAIGN_PREFIX:
        return None

    if LOCATION_PATH_PREFIXED.search(path):
        return path

    if LOCATION_PATH_BARE.search(path):
        city = seg[-1]
        if _name_contains_city(name, city) and not other_signal:
            return None
        return path

    return None


def is_out_of_area(domain: str) -> bool:
    if not domain:
        return False
    return any(domain.endswith(t.lstrip(".")) or domain.endswith(t)
               for t in NON_NA_TLDS)


def classify(row: Dict) -> Dict:
    """
    Mutates and returns row: sets status, review_reason, disqualify_reason.

    Precedence: excluded beats review beats clean. A directory listing that
    is also franchise-named is excluded — there is nothing to review.
    """
    name = row.get("business_name") or ""
    domain = row.get("domain") or ""

    # --- excluded: deterministic, terminal ---
    if not name.strip():
        row["status"] = "excluded"
        row["disqualify_reason"] = "missing_business_name"
        return row

    if domain and domain in lists.DIRECTORY_DOMAINS:
        row["status"] = "excluded"
        row["disqualify_reason"] = "directory_domain"
        return row

    if is_out_of_area(domain):
        row["status"] = "excluded"
        row["disqualify_reason"] = "out_of_area"
        return row

    # --- no_website lane: deterministic fact, NOT a reject ---
    # A social page is not a website. It is the lane, per lists.py
    # departure 2. Falls through to clean with url cleared.
    if domain and domain in lists.SOCIAL_DOMAINS:
        row["url"] = None
        row["domain"] = ""
        row["review_reason"] = "no_website_lane"
        row["status"] = "clean"
        return row

    # --- review: genuinely ambiguous, a human look changes the outcome ---
    reasons: List[str] = []

    brand = match_franchise_brand(name, domain)
    if brand:
        reasons.append(f"franchise_brand:{brand}")

    mfr = match_manufacturer(name)
    if mfr:
        reasons.append(f"manufacturer_dealer:{mfr}")

    # other_signal: has any franchise/manufacturer/multi-location rule
    # already fired? If so, a bare /<city> path is NOT spared even when the
    # name contains the city — the row is already known to be a chain.
    other_signal = bool(reasons) or row.get("multi_location_domain", False)
    loc = match_location_path(row.get("url"), row.get("business_name"),
                              other_signal)
    if loc:
        reasons.append(f"location_path:{loc}")

    if row.get("multi_location_domain"):
        reasons.append("multi_location_domain")

    if reasons:
        row["status"] = "review"
        row["review_reason"] = ";".join(reasons)
        return row

    row["status"] = "clean"
    return row


def classify_all(rows: List[Dict]) -> List[Dict]:
    return [classify(r) for r in rows]


def summarise(rows: List[Dict]) -> Dict[str, int]:
    out = {"clean": 0, "review": 0, "excluded": 0, "no_website_lane": 0}
    for r in rows:
        out[r.get("status", "clean")] = out.get(r.get("status", "clean"), 0) + 1
        if r.get("review_reason") == "no_website_lane":
            out["no_website_lane"] += 1
    return out
