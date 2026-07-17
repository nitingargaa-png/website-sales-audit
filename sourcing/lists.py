"""
lists.py — data, not logic.

Ported from clean_leads_franchise_chain_detector_reconstructed_v4_6.py and
lead_cleaning_pipeline_v4_7_garage_detroit.py. Both are archived; this is
the surviving copy. Three deliberate departures from the sources, each of
which was a live bug:

1. BARE "overhead door" IS NOT IN FRANCHISE_BRANDS.
   v4.6 listed both "overhead door company" (a real franchise) and bare
   "overhead door" (what the product is called). Tested against the live
   2026-07-17 Mississauga batch and plausible variants:

       Mississauga Overhead Door Repair  -> MATCHED (independent, wrong)
       Smith Overhead Door Service       -> MATCHED (independent, wrong)
       Overhead Door Company of Toronto  -> MATCHED (franchise, right)
       Candoor Overhead Doors Ltd.       -> no match, BY ACCIDENT
                                            ("Candoor" breaks the token
                                             boundary; the rule did not
                                             save it, luck did)

   This is the dead_site failure again: a rule firing on the trade term
   itself, silently binning the independents the whole pipeline exists to
   find. Pinned by tests/test_sourcing_lists.py::test_overhead_door_
   generic_term_does_not_match_independents. DO NOT re-add bare
   "overhead door" from v4.6.

2. DIRECTORY_DOMAINS and SOCIAL_DOMAINS ARE SEPARATE SETS.
   v4.6's AGGREGATOR_DOMAINS lumped facebook/instagram/linkedin with
   yelp/angi/homeadvisor. They are different facts:
       yelp.com/biz/x  -> the business is a listing on a directory.
                          Nothing to audit, nothing to sell. EXCLUDED.
       facebook.com/x  -> the business has a social page and no website.
                          That is the no_website LANE, which is the
                          highest-value segment (A1). NOT a reject.
   Porting the merged set would hard-exclude the best prospects.

3. NO bare r"\bfranchise\b" PATTERN.
   v4.6's EXPLICIT_FRANCHISE_PATTERNS matched against `combined` — a blob
   of name + category + address + WEBSITE URL. Any prospect whose domain
   contained "franchise" was hard-excluded at high confidence, with the
   reason "Explicit franchise language detected" — which reads like a
   page-content finding but never touched a page.

SCOPE: FRANCHISE_BRANDS is matched against business NAME and DOMAIN only.
Never page text. Page-derived franchise disclosure is a different rule
with a different name (national_chain), owned by
execution/audit/applicability.py, and it stays there. See BACKLOG.
"""

# Directories. The business is a listing here, not the owner of the site.
# Nothing to audit -> excluded.
DIRECTORY_DOMAINS = {
    "angi.com",
    "angieslist.com",
    "bark.com",
    "bbb.org",
    "birdeye.com",
    "buildzoom.com",
    "chamberofcommerce.com",
    "expertise.com",
    "foursquare.com",
    "homeadvisor.com",
    "houzz.com",
    "mapquest.com",
    "manta.com",
    "merchantcircle.com",
    "networx.com",
    "nextdoor.com",
    "porch.com",
    "superpages.com",
    "thumbtack.com",
    "yellowpages.com",
    "yellowbook.com",
    "yelp.com",
}

# Social. The business has a page here and no website of its own.
# -> no_website lane. NOT a reject. See departure 2 above.
SOCIAL_DOMAINS = {
    "facebook.com",
    "fb.com",
    "instagram.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "tiktok.com",
    "youtube.com",
}

# Franchise brand names. Matched on NAME + DOMAIN only.
# Every entry must be brand-shaped: a name a franchisor owns, not a phrase
# describing the trade. If you are about to add a term that an independent
# operator could plausibly put in its own name, it does not belong here.
FRANCHISE_BRANDS = {
    # Garage door
    "a1 garage door service",
    "a-1 garage door",
    "precision door service",
    "precision garage door",
    "precision door",
    "overhead door company",   # the franchise. NOT bare "overhead door".
    "champion overhead",
    "sears garage",
    "garageexperts",
    "garage experts",
    "prolift garage doors",

    # Plumbing / HVAC / electrical / restoration
    "aire serv",
    "benjamin franklin plumbing",
    "bluefrog plumbing drain",
    "clockwork home services",
    "glass doctor",
    "mr electric",
    "mr rooter",
    "one hour heating air conditioning",
    "one hour heating and air conditioning",
    "puroclean",
    "rainbow restoration",
    "roto rooter",
    "roto-rooter",
    "servicemaster restore",
    "servpro",
    "the sunny plumber",

    # Cleaning / landscaping / pest / exterior
    "college hunks hauling junk moving",
    "five star painting",
    "grounds guys",
    "leaf home",
    "leaffilter",
    "molly maid",
    "mosquito joe",
    "orkin",
    "stanley steemer",
    "terminix",
    "the cleaning authority",
    "the maids",
    "trugreen",
    "weed man",

    # Home improvement / windows
    "renewal by andersen",
    "window world",

    # Franchisors / parent brands (v4.7)
    "neighborly",
    "authority brands",
}

# Franchise-owned domains. Exact registrable-domain match.
FRANCHISE_DOMAINS = {
    "a1garage.com",
    "precisiondoor.net",
    "precisiondoor.com",
    "overheaddoor.com",
    "searshomeservices.com",
    "neighborly.com",
    "authoritybrands.com",
    "mrrooter.com",
    "rotorooter.com",
    "servpro.com",
    "molymaid.com",
    "mollymaid.com",
}

# Manufacturer / dealer signals. Ambiguous -> review, never excluded.
# A dealer may be a perfectly good independent that also sells a brand.
MANUFACTURER_TERMS = {
    "clopay",
    "wayne dalton",
    "wayne-dalton",
    "amarr",
    "chi overhead",
    "raynor",
    "liftmaster",
    "chamberlain",
    "genie",
    "haas door",
    "carrier",
    "lennox",
    "trane",
    "rheem",
    "goodman",
}
