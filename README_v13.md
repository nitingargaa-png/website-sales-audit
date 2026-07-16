# v13 audit — batch runner

Replaces the Claude Code skill path. `docs/SKILL.md` is now the SPEC;
`execution/audit/judge.py` embeds it as a system prompt. One rubric, one code path.

## Install

    pip install -r requirements-v13.txt

## Env (.env at project root)

    ANTHROPIC_API_KEY=...     # required — judged tier
    PSI_API_KEY=...           # optional — only if you hit PSI rate limits

## Run

    python execution/audit_batch.py --input input/prospects.csv --dry-run
    python execution/audit_batch.py --url https://mississaugaplumbingservices.com
    python execution/audit_batch.py --input input/prospects.csv
    python execution/audit_batch.py --input input/prospects.csv --skip-completed
    python execution/audit_batch.py --input input/prospects.csv --no-pdf --limit 10

Input: CSV with a url/website/domain column, or a .txt of one URL per line.

## Output

    output/{slug}-{date}.md          audit + TRIAGE_META footer
    output/pdf/{slug}-{date}.pdf     one-page lead magnet (skipped if disqualified)
    output/audit_{date}.checkpoint   resume state

## Test

    python -m pytest tests/test_fixtures_golden.py -v

Locks the three fixtures in docs/fixtures_golden.md against synthetic HTML.
Fast inner loop — does NOT replace the manual smoke test against the real URLs.

## Downstream — unchanged

TRIAGE_META schema_version stays "1.0". After a run:

    python execution/triage_handoff.py --audit output/{slug}-{date}.md

## Module map

    execution/audit_batch.py        CLI + orchestrator
    execution/audit/psi.py          PSI API, N runs, returns RANGES
    execution/audit/detect.py       HTML -> measured dict (deterministic)
    execution/audit/judge.py        Claude API -> judged tier + prose
    execution/audit/score.py        6 areas -> site_score, null-not-3
    execution/audit/applicability.py  mctb/vaai/disqualifiers
    execution/audit/render_md.py    -> .md + TRIAGE_META
    execution/audit/render_pdf.py   -> one-page PDF

## Costs per 200 prospects

    PSI          free (600 calls, limit 25k/day)
    Claude       ~$2-6 (Sonnet, judged tier only)

## Known limits

- Tier 3 booking detection is best-effort from static HTML. The real signal is
  inside the booking iframe. See docs/fixtures_golden.md "Deferred".
- No GBP-only path. Website-only.
- Score has no fixture. Routing is pinned; the rubric is not.
