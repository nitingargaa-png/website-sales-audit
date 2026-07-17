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

# REFUSAL THRESHOLD.
#
# Below this many characters of visible text, the model has nothing real to
# judge and will pattern-match instead. Observed 2026-07-16 on the first live
# run: handed 83 chars from a JS shell, the model reported "The homepage shows
# a 404 'Page Not Found' error" on a site that returned HTTP 200 with 17KB of
# HTML. It saw the string "Page Not Found" in a pre-hydration React component
# and built three findings, an overview, and a fix plan on top of it. The
# report told a working plumbing business to call their host about a broken
# homepage.
#
# A refusal is honest. A fabricated 404 in a prospect's inbox is not.
MIN_TEXT_FOR_JUDGMENT = 400

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

NEVER QUOTE THE MEASURED DICT AT THE OWNER.
The MEASURED facts are given to you as a JSON dict with field names like
tel_href, localbusiness_jsonld, js_only_suspected, aggregate_review_count.
Those are internal variable names. The owner has never seen them and they mean
nothing to him.

FORBIDDEN: "the measured fact 'tel_href: false' means it is not a phone link"
CORRECT:   "Your phone number is written as plain text, so it can't be tapped
            to call on a phone."

Never write a field name, a JSON key, a colon-value pair, or the word
"measured fact" in owner-facing prose. Describe what is true in plain words.

NO CODE IN FIXES. Do not write HTML tags, angle brackets, or code snippets —
the report renders to PDF and tags get stripped, leaving nonsense. Say "ask
your web person to make the number a tap-to-call link", not "<a href=...>".

DO NOT INVENT DETAILS ABOUT THE TEST ITSELF.
The number of PageSpeed runs is in the data you were given. Do not say "across
two runs" when it says three. If you are unsure, don't mention it.

DO NOT INVENT COMPETITOR NUMBERS.
"a competitor showing 4.8 stars and 150 reviews" is a fabricated benchmark.
You have no competitor data. Say "most established plumbers in a market this
size show their rating and review count" — a general pattern, no fake figures.

DO NOT OPINE ON REBUILD VS REPAIR.
Never write "without rebuilding the site from scratch" or "this needs a full
rebuild". That is a sales conversation, not an audit finding. Report what is
broken and what fixing it involves. The reader decides the scope.

TAP-TO-CALL: READ tel_js_only BEFORE PRAISING THE PHONE LINK.
The page text you are given comes from a renderer that executed the site's
JavaScript. A phone number may appear as a working link there and still not
exist in the page as delivered.

If tel_js_only is true: the tap-to-call link is NOT working properly. Do not
list it under "working". It only exists after scripts finish, which on a slow
site means it is missing for the first several seconds, and search engines
never see it at all. Treat it as a problem, not a positive.

If tel_href is true: the link is in the page as delivered. Safe to praise.

Never contradict the MEASURED block. If it says tap-to-call only works after
scripts run, do not write that the phone number is a working tap-to-call link.

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


# Internal field names that must never reach a prospect. A prompt rule is a
# guideline; this is the mechanism. Your own repo's lesson, learned on
# commit-message escaping: "Mechanisms beat guidelines under execution
# pressure." The model leaked "the measured fact 'tel_href: false'" into a
# prospect-facing finding on the 2026-07-16 live run despite the voice rules.
LEAK_PATTERNS = [
    r"\btel_href\b", r"\blocalbusiness_jsonld\b", r"\bjs_only_suspected\b",
    r"\baggregate_review_count\b", r"\breview_count_visible\b",
    r"\bvisible_text_len\b", r"\bviewport_meta\b", r"\bphone_in_text\b",
    r"\bmeta_desc_ok\b", r"\btitle_ok\b", r"\bbooking_tier\b",
    r"\bgmail_contact\b", r"\bscript_count\b", r"\bfsm_vendor\b",
    r"\bchat_vendor\b", r"\bad_pixels\b", r"\bplaceholder_signals\b",
    r"measured fact", r"<a\s+href", r"</\w+>",
]

PROSE_FIELDS = ("evidence", "impact", "fix")


def _leaks(judged: Dict[str, Any]) -> list:
    """Return list of (where, pattern) for any internal name in owner prose."""
    found = []
    blobs = []
    for f in judged.get("top_findings", []) or []:
        for k in PROSE_FIELDS:
            if f.get(k):
                blobs.append((f"finding.{k}", f[k]))
    for k in ("overview", "hook"):
        if judged.get(k):
            blobs.append((k, judged[k]))
    for w in judged.get("working", []) or []:
        blobs.append(("working", w))

    for where, txt in blobs:
        for pat in LEAK_PATTERNS:
            if re.search(pat, txt, re.I):
                found.append((where, pat))
    return found


def _strip_contradictions(judged: Dict[str, Any],
                          measured: Dict[str, Any]) -> Dict[str, Any]:
    """
    MECHANISM, not guideline.

    The judged tier reads renderer output, where a JS-injected tel: link looks
    like a working tap-to-call. The MEASURED block reads the delivered HTML,
    where it does not exist. On the 2026-07-16 run the report said, two inches
    apart:

        MEASURED  Tap-to-call: YES, but only after scripts run
        WORKING   "Your phone number appears as a tap-to-call link in the
                   footer, making it easy to dial from a phone"

    A prospect who spots that stops trusting the document. The prompt now warns
    about it; this drops it if the warning doesn't hold.
    """
    if not judged or not measured.get("tel_js_only"):
        return judged

    tap_praise = re.compile(
        r"tap[- ]to[- ]call|click[- ]to[- ]call|tap the (number|phone)"
        r"|dial (directly|straight)|phone number.{0,40}link", re.I)

    working = judged.get("working") or []
    kept = [w for w in working if not tap_praise.search(w)]
    if len(kept) != len(working):
        print("  [judge] dropped tap-to-call praise — contradicts MEASURED "
              "(link only exists after scripts run)")
        judged["working"] = kept
    return judged


def assess(page_text: str, measured: Dict[str, Any],
           psi: Dict[str, Any], url: str) -> Optional[Dict[str, Any]]:
    """
    Returns judged scores + findings, or None on failure.

    REFUSAL GUARD — see MIN_TEXT_FOR_JUDGMENT.

    None is handled by the caller: the audit still emits with measured-only
    scoring and a note. A failed judge call degrades the report; it does not
    fabricate one.
    """
    if len(page_text.strip()) < MIN_TEXT_FOR_JUDGMENT:
        print(f"  [judge] REFUSING — only {len(page_text.strip())} chars of "
              f"visible text (need {MIN_TEXT_FOR_JUDGMENT}). Judging this "
              f"would be fabrication.")
        return None

    # Strip the measured dict of raw text fields before sending — the model
    # doesn't need them and they eat tokens.
    slim = {k: v for k, v in measured.items()
            if k not in ("title", "meta_desc", "h1_text")}

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
    parsed = _parse_json(raw)
    if not parsed:
        return None

    # Mechanism, not guideline: reject and retry once if internal field names
    # leaked into owner-facing prose.
    parsed = _strip_contradictions(parsed, measured)

    leaks = _leaks(parsed)
    if leaks:
        where = ", ".join(f"{w} ({p})" for w, p in leaks[:3])
        print(f"  [judge] leak detected in owner prose: {where} — retrying")
        retry = _invoke(
            prompt + "\n\nYOUR PREVIOUS ATTEMPT LEAKED INTERNAL FIELD NAMES "
                     "OR CODE INTO OWNER-FACING TEXT. The owner has never seen "
                     "the MEASURED dict and does not know what its keys mean. "
                     "Rewrite every finding in plain words a plumber would use. "
                     "No field names, no JSON keys, no 'measured fact', no HTML "
                     "tags.")
        if retry:
            reparsed = _parse_json(retry)
            if reparsed and not _leaks(reparsed):
                return _strip_contradictions(reparsed, measured)
            if reparsed:
                print("  [judge] leak persisted after retry — dropping affected "
                      "findings rather than sending them")
                reparsed["top_findings"] = [
                    f for f in (reparsed.get("top_findings") or [])
                    if not any(re.search(p, " ".join(
                        str(f.get(k, "")) for k in PROSE_FIELDS), re.I)
                        for p in LEAK_PATTERNS)]
                return reparsed
        return None

    return parsed
