"""
judge.py — The JUDGED tier. The only part that needs a model.

Everything deterministic already happened in detect.py and psi.py. This module
handles what genuinely requires judgment: design quality, copy clarity, trust
feel, and the evidence/impact/fix prose.

Retry shape mirrors ghl-triage/triage/talking_points.py::_invoke_haiku
deliberately: 2 attempts, fixed 2.0s backoff, 60s timeout, bare Exception catch,
None return on failure. Callers handle None by degrading, not crashing.
"""
import json
import os
import re
import time
from typing import Dict, Any, Optional

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

MODEL = "claude-sonnet-4-6"
TIMEOUT_SECS = 60
RETRY_DELAY_SECS = 2.0
MAX_ATTEMPTS = 2
MAX_HTML_CHARS = 60000

SYSTEM_PROMPT = """You are auditing a local home service business website for its owner.

You are given: (1) the page text, (2) a dict of MEASURED facts already
determined deterministically, (3) PageSpeed data.

Do NOT re-derive the measured facts. They are settled. Your job is the JUDGED
tier only, plus the prose.

VOICE
Write to the owner, not a marketer. Short sentences. 6th-8th grade level.
"you" and "your customers", never "the user".

BANNED WORDS — never use, not even explained:
SEO, CTA, UX, schema markup, meta tags, H1, above the fold, conversion rate,
bounce rate, responsive design, optimize, leverage, streamline, boost, enhance,
seamless, robust, comprehensive, unlock, transform, elevate, game-changer,
cutting-edge, actionable, holistic, journey, funnel, KPI, indexing, SSL.

NO HYPE. "Could help get more calls." Never "will transform your business."

THE IMPACT RULE — THIS IS THE MOST IMPORTANT RULE IN THIS PROMPT
Impact is a STATED GAP AGAINST A BENCHMARK. It is NEVER a predicted number.

GOOD: "Your homepage takes 6.2 seconds to show its main content on a phone.
       Google's threshold for a good experience is 2.5 seconds. You're 2.5x over."
GOOD: "Most established plumbers in a market this size show 100-300 Google
       reviews on their homepage. Yours shows none, though you have 166."

FORBIDDEN: "Fixing this will get you 30% more calls."
FORBIDDEN: "This is costing you $4,000/month."
FORBIDDEN: "You could see a 15-25% lift."  <- a range of invented numbers is
           still invented. Ranges are not a fix for made-up figures.

You do not have their traffic, conversion rate, or close rate. You cannot
compute revenue impact. State the measurement, state the benchmark, state the
gap. The owner knows their job value; let them do the arithmetic.

The only numbers you may state are ones in the MEASURED dict or citable public
thresholds (LCP 2.5s, INP 200ms, CLS 0.1, title 55-60 chars, meta 150-160).

FINDINGS
Every finding has exactly three fields. If you cannot fill all three, drop it.
  evidence: what you observed — cite the specific page/element
  impact:   the gap against a benchmark — no invented numbers
  fix:      what to do

OUTPUT
Return ONLY valid JSON. No preamble, no markdown fences.

{
  "judged": {
    "mobile": 1-5,
    "conversion": 1-5,
    "trust": 1-5,
    "lead_capture": 1-5
  },
  "judged_rationale": {
    "mobile": "one sentence",
    "conversion": "one sentence",
    "trust": "one sentence",
    "lead_capture": "one sentence"
  },
  "top_findings": [
    {"evidence": "...", "impact": "...", "fix": "..."},
    {"evidence": "...", "impact": "...", "fix": "..."},
    {"evidence": "...", "impact": "...", "fix": "..."}
  ],
  "working": ["specific observed positive", "..."],
  "overview": "3-4 sentences. One analogy allowed, trade-relevant. Then concrete.",
  "hook": "the single most specific finding, for internal sales use",
  "trade": "plumbing|hvac|cleaning|landscaping|electrical|pest_control|painting|garage_door|roofing|glass|other",
  "business_name": "...",
  "city": "..." or null,
  "region": "..." or null
}

SCORING SCALE
5 = working, nothing to fix
4 = minor polish, not costing calls
3 = visible friction, fixable
2 = actively reducing inquiries
1 = costing customers right now

Never inflate to soften. A broken mobile site is a 1.

"working" must be specific and observed. Do not pad it. If there are only two
real positives, list two. If there are none, return an empty list.
"""


def _client() -> Optional[Any]:
    if Anthropic is None:
        print("  [judge] anthropic package not installed")
        return None
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("  [judge] ANTHROPIC_API_KEY not set")
        return None
    return Anthropic(api_key=key, timeout=TIMEOUT_SECS)


def _invoke(prompt: str) -> Optional[str]:
    """2 attempts, fixed backoff. Mirrors ghl-triage's _invoke_haiku."""
    client = _client()
    if client is None:
        return None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=4000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join(
                b.text for b in resp.content if getattr(b, "type", "") == "text")
        except Exception as e:
            if attempt < MAX_ATTEMPTS:
                print(f"  [judge] attempt {attempt} failed ({e}); "
                      f"retrying in {RETRY_DELAY_SECS}s")
                time.sleep(RETRY_DELAY_SECS)
            else:
                print(f"  [judge] generation failed: {e}")
    return None


def _parse_json(raw: str) -> Optional[Dict[str, Any]]:
    txt = raw.strip()
    txt = re.sub(r"^```(?:json)?\s*", "", txt)
    txt = re.sub(r"\s*```$", "", txt)
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", txt, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
    print("  [judge] could not parse JSON response")
    return None


def assess(page_text: str, measured: Dict[str, Any],
           psi: Dict[str, Any], url: str) -> Optional[Dict[str, Any]]:
    """
    Returns judged scores + findings, or None on failure.

    None is handled by the caller: the audit still emits with measured-only
    scoring and a note. A failed judge call degrades the report; it does not
    fabricate one.
    """
    # Strip the measured dict of raw text fields before sending — the model
    # doesn't need them and they eat tokens.
    slim = {k: v for k, v in measured.items()
            if k not in ("title", "meta_desc")}

    prompt = f"""URL: {url}

MEASURED FACTS (settled — do not re-derive, do not contradict):
{json.dumps(slim, indent=2)}

PAGESPEED (mobile, {psi.get('runs_ok', 0)} runs, source={psi.get('source')}):
{json.dumps({k: v for k, v in psi.items() if k != 'measured'}, indent=2)}

PAGE TEXT:
{page_text[:MAX_HTML_CHARS]}
"""

    raw = _invoke(prompt)
    if not raw:
        return None
    return _parse_json(raw)
