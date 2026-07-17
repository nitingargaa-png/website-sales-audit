# Sourcing BACKLOG

Deferrals and known limitations for `sourcing/`. Each entry records what
was measured, not what was assumed. Items here are decisions taken
knowingly, not oversights.

## 1. The no_website lane has no consumer

18 of 270 rows (6.7%) in the 2026-07-17 grid had no website. Per A1 these
are the highest-value segment: a business with a GBP listing and no site
cannot be audited (audit_batch.py needs a URL) and is the strongest
rebuild prospect available.

They land in `prospects_*.csv` with `status=clean, url=null` and nothing
reads them. `emit.write_audit_queue` drops them on the url test, correctly
— the audit cannot read them.

Needs a GBP-only pitch path. v13 has no such path and this has been
flagged before. Until then the column accumulates rows nobody opens.

## 2. DIRECTORY_DOMAINS may be dead code

22 domains ported from v4.6. Fired ZERO times in 270 rows.

Places API returns the business's own `websiteUri`, not a directory
listing. The v4.6 list was inherited from a pipeline fed by a different
scraper that saw different data. Expected to stay dead. Watch across a few
more batches before removing — one grid is not proof.

`SOCIAL_DOMAINS` is a different matter and must stay: it routes to the
no_website lane, not to excluded. See lists.py departure 2.

## 3. multi_location_domain is batch-scoped AND jitter-sensitive

Two separate problems.

The count is over the current batch only. A four-location operator showing
two rows in a 100-batch is not flagged; the same operator in a 500-batch
might be. Fixing it means persisting domain counts across batches — a
different piece of infrastructure.

SECOND PROBLEM, found live: Places result sets jitter between runs. Two
runs of the identical grid an hour apart on 2026-07-17 returned 277 and
275 rows, and `Dr HVAC` surfaced 3 rows in one and 2 in the other —
dropping below the threshold and losing its flag. Same operator, same
command, different verdict. The 7-day cell cache (sourcing/cache.py) makes
a repeated grid deterministic, which contains the symptom but not the
cause: a fresh fetch after TTL expiry can still flip a marginal domain.

Caught `John The Plumber` (x3) and `Dr HVAC` (x3) on the 2026-07-17
Mississauga x Hamilton grid. Both are unbranded multi-location operators
invisible to every other rule. Grid design matters: adjacent cities
(Mississauga x Brampton, both Peel) fire this on genuine service-area
overlap and tell you nothing.

## 4. owner_name / owner_source: CUT 2026-07-17

Removed from the contract after two probes measured 0% coverage against a
40-70% expectation. Full measurement in `sourcing/emit.py`'s docstring.

Short version: SMB home-service businesses do not publish owner names on
customer-facing surfaces. Reviews name the company ("WOW Drain & Plumbing
responded immediately" IS the owner, unnamed) or, at enterprise scale,
technicians. About pages either do not exist (~6/15) or exist with
2119-9375 chars of real content and no name (~9/15). Jina rendered every
About page; js_shell_recovered was 0, so the JS concern was not the cause.

Source gap, not a tuning problem. If needed later, the Ontario BIN
registry is the only candidate with a structural reason to work (a
business name registration names its registrant). Separate build, own
probe, Ontario only. Do not re-add the columns without a source that
fills them.

Not tested, deliberately: Facebook (a customer-facing surface — expected
to fail the same way), LinkedIn (where the one real owner name in this
project actually came from; login-walled and hostile to scraping, likely
a manual step rather than a pipeline stage).

## 5. primaryType is trade-dependent, not useless

2026-07-17 grid, 270 rows:

    plumbing     83/88   plumber              precise
    garage door  70/78   supplier             useless
    hvac         76/104  general_contractor   generic

Google has a `plumber` type and no `garage_door` type. The field is as
informative as Google's taxonomy allows for that trade. It is a WEAK
NEGATIVE signal at best — ~12/270 rows where the tag contradicts the query
(`plumbing, manufacturer`; `garage door, roofing_contractor`). Not worth a
rule at that rate. Carried, never routed.

An earlier conclusion drawn from garage door alone ("primaryType is dead")
was wrong. The multi-trade grid found it.

## 6. Fixture 1 consumer-side routing under vaai: null

`docs/fixtures_golden.md` recorded Fixture 1 routing as "MCTB/VAAI Tier 1
at score 89" — captured when `vaai_applicable` was `true`. The corrected
value is `null`. If `prospect_triage.py` tiers on `vaai_applicable`, that
route may now differ. Re-verify next time ghl-triage is open.

## 7. JINA_API_KEY was absent from .env

Discovered 2026-07-17: the key was never in `.env` despite being listed as
present. Added during the About-page probe. The repo's
`execution/audit_batch.py` fetches with plain `requests` and has no Jina
path; the newer standalone `audit_batch.py` imports a `render` module that
is not in this repo. Worth reconciling — if `render.fetch()` needs Jina,
it was running without it.

## 8. Trade is a property of the search, not the business

Every row gets `trade` from the query that found it. A parts supplier that
ranks for "garage door repair" gets `trade=garage door`. Name matching
catches some; `gbp_types` does not discriminate (the `supplier` tag
appears on real garage door companies and parts suppliers alike). Known
limitation, carried explicitly. Surfaces in the reject read.

## 9. Batch names collided silently (fixed)

The default batch name was `grid-<date>`, so two runs on the same day
wrote the same files. On 2026-07-17 a 270-row grid was replaced by a
20-row single-cell run with no warning — the second run simply overwrote
the first. Fixed: default is now `grid-<date>-<HHMMSS>`, and an existing
`prospects_<batch>.csv` is refused rather than clobbered unless --resume
is passed.

## 10. Cache invalidation is all-or-nothing, deliberately

`--no-cache` skips reads (still writes), `--clear-cache` empties the
directory. There is no per-cell or partial invalidation. The failure mode
of a clever cache is serving a stale answer to a question you believed you
were asking fresh — worse than no cache, because it looks like a fetch.

Cache is per PAGE, keyed on `trade|city|page_token`, 7-day TTL, one JSON
file per cell under `sourcing_cache/`. Not sqlite: a few KB per cell,
write-once, read-rarely, and a directory of JSON is greppable when a batch
looks wrong. lead-engine used sql.js because it was already a JS project
with a bundler — that reason does not carry over.
