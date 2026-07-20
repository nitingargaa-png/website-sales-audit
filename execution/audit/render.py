"""
render.py — JS-aware fetching.

WHY THIS EXISTS
A static requests.get() on a React/Vue/Angular site returns the shell, not the
content. On the first live run against mississaugaplumbingservices.com the
static fetch returned 17KB of HTML containing 83 characters of visible text —
and the judged tier, handed those 83 chars, hallucinated a 404 error on a site
that returned HTTP 200. Every downstream finding inherited the error.

The irony worth preserving: docs/fixtures_golden.md already recorded the lesson
("synthetic fixtures test the code path the author imagined; real producer
output exercises the code path real data takes") and the synthetic tests passed
while the live run failed on exactly that gap.

PROVIDER CHAIN (mirrors website-audit-builder/execution/extract_business_data.py)
  1. Jina Reader  — free, renders JS. JINA_API_KEY optional (higher rate limits).
  2. Firecrawl    — paid (~$0.01/page), renders JS. FIRECRAWL_API_KEY.
  3. Static       — requests.get. Fast, free, blind to JS.

We ALWAYS keep the static HTML too: script-src detection (platform, chat, FSM,
pixels) needs the raw tags, which the rendered markdown strips out.
"""
import os
import time
from typing import Dict, Any, Optional, Tuple

import requests

from .abort_reason import from_status as _abort_from_status
from .abort_reason import from_exception as _abort_from_exception

JINA_BASE = "https://r.jina.ai/"
FIRECRAWL_URL = "https://api.firecrawl.dev/v1/scrape"
TIMEOUT_SECS = 60
RETRY_DELAY_SECS = 2.0

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "Chrome/121.0.0.0 Safari/537.36")

# Full browser header set. UA alone is not enough: servers that validate
# the Accept header return HTTP 415 to a bare requests.get. Live 2026-07-19:
# ~20 of 226 sites 415'd on a UA-only request. A complete set clears them.
BROWSER_HEADERS = {
    "User-Agent": UA,
    "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
               "image/avif,image/webp,image/apng,*/*;q=0.8"),
    "Accept-Language": "en-CA,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Upgrade-Insecure-Requests": "1",
}

# Statuses that mean "a real server is blocking a bot" rather than "dead".
# We retry these once, then fall through to Jina (different origin). A hard
# failure (SSL, DNS, timeout, 404, 500) is NOT here ? Jina cannot fix those.
SOFT_BLOCK_STATUSES = {202, 403, 429, 503}

# Below this many chars of visible text, a static fetch is presumed blind.
JS_SHELL_THRESHOLD = 500


def _jina_key() -> Optional[str]:
    return os.environ.get("JINA_API_KEY") or None


def _firecrawl_key() -> Optional[str]:
    return os.environ.get("FIRECRAWL_API_KEY") or None


def available_provider() -> str:
    """Which renderer we'd use. Reported in the audit for provenance."""
    if _jina_key() or True:      # Jina works keyless at low volume
        return "jina"
    if _firecrawl_key():
        return "firecrawl"
    return "static"


BLOCKED = "__BLOCKED__"

# Why a module-level recorder and not a changed return type:
# fetch_static returns a bare str/BLOCKED/None and has several callers
# (audit_batch subpage loop, tests) that unpack it positionally. Widening
# the return to a tuple would break every one. fetch_static and fetch are
# always called in sequence on the SAME url, so fetch_static stashes the
# classified failure here and fetch reads it right after. Additive: a caller
# that ignores it sees the exact same behavior as before. Overwritten on
# every fetch_static call, so it only ever describes the most recent fetch.
_LAST_ABORT_REASON: Optional[str] = None


def last_abort_reason() -> Optional[str]:
    """The pitch tag for the most recent hard failure, or None if the last
    fetch_static succeeded or soft-blocked. Read immediately after fetch()."""
    return _LAST_ABORT_REASON


def fetch_static(url: str, quiet: bool = False):
    """
    Raw HTML for script-src detection.

    Returns str (200), BLOCKED (202/403/429/503 bot-wall, retried once,
    caller should try Jina), or None (SSL/DNS/timeout/404/500 - dead,
    Jina cannot help). UA-only drew ~50 aborts on 2026-07-19, many real
    sites (Candoor scored 71, then 202d). Full headers + retry + Jina
    fallback recover them.
    """
    global _LAST_ABORT_REASON
    _LAST_ABORT_REASON = None   # reset per call; only a hard failure sets it
    for attempt in (1, 2):
        try:
            r = requests.get(url, timeout=30, headers=BROWSER_HEADERS)
            if r.status_code == 200:
                return r.text
            if r.status_code in SOFT_BLOCK_STATUSES:
                if attempt == 1:
                    time.sleep(1.5)
                    continue
                if not quiet:
                    print(f"  [fetch] HTTP {r.status_code} bot-block, "
                          f"trying renderer: {url}")
                return BLOCKED
            if not quiet:
                print(f"  [fetch] HTTP {r.status_code}: {url}")
            _LAST_ABORT_REASON = _abort_from_status(r.status_code)
            return None
        except Exception as e:
            if not quiet:
                print(f"  [fetch] {e}")
            _LAST_ABORT_REASON = _abort_from_exception(e)
            return None
    return BLOCKED


def fetch_jina(url: str) -> Optional[str]:
    """
    Jina Reader — renders JS, returns markdown. Free, no key needed at low
    volume. JINA_API_KEY raises the rate limit.
    """
    headers = {"Accept": "text/plain"}
    key = _jina_key()
    if key:
        headers["Authorization"] = f"Bearer {key}"

    try:
        r = requests.get(JINA_BASE + url, headers=headers, timeout=TIMEOUT_SECS)
        if r.status_code == 429:
            print("  [jina] rate limited. Set JINA_API_KEY for higher limits.")
            return None
        if r.status_code != 200:
            print(f"  [jina] HTTP {r.status_code}")
            return None
        return r.text
    except Exception as e:
        print(f"  [jina] {e}")
        return None


def fetch_firecrawl(url: str) -> Optional[str]:
    """Firecrawl — renders JS, returns markdown. Paid. ~$0.01/page."""
    key = _firecrawl_key()
    if not key:
        return None
    try:
        r = requests.post(
            FIRECRAWL_URL,
            headers={"Authorization": f"Bearer {key}",
                     "Content-Type": "application/json"},
            json={"url": url, "formats": ["markdown"],
                  "onlyMainContent": False, "waitFor": 3000},
            timeout=TIMEOUT_SECS)
        if r.status_code != 200:
            print(f"  [firecrawl] HTTP {r.status_code}")
            return None
        data = r.json()
        if not data.get("success"):
            print(f"  [firecrawl] success=false: {data.get('error')}")
            return None
        return (data.get("data") or {}).get("markdown") or data.get("markdown")
    except Exception as e:
        print(f"  [firecrawl] {e}")
        return None


def fetch(url: str, force_render: bool = False) -> Dict[str, Any]:
    """
    Returns:
      {
        "html": raw static HTML or None,      # for script-src detection
        "text": best available visible text,  # for judging
        "text_source": "static"|"jina"|"firecrawl"|None,
        "js_rendered": bool,   # did we need a renderer to see the content
        "static_text_len": int,
        "rendered_text_len": int|None,
      }

    html=None means the homepage did not load. Caller must abort — never audit
    a site we could not fetch.
    """
    from .detect import _strip_tags

    html = fetch_static(url)

    # Soft block (bot-wall): our IP/headers were refused but the site is
    # live. Jina fetches from its own origin and usually gets through.
    # The difference between aborting a real prospect and auditing it.
    # Candoor: 202 to us, renders fine via Jina.
    if html == BLOCKED:
        rendered = fetch_jina(url)
        if rendered:
            txt = rendered.strip()
            print(f"  [render] jina recovered blocked site "
                  f"({len(txt)} chars)")
            # Return the Jina text as html too. The caller aborts on
            # html is None (line 111); a blocked site has no static html
            # but IS live. Script-src detection will not find <script>
            # tags in markdown - same limitation as every JS-shell site
            # audited via Jina. Full content audit beats no audit.
            return {"html": txt, "text": txt, "text_source": "jina",
                    "js_rendered": True, "static_text_len": 0,
                    "rendered_text_len": len(txt)}
        # Soft-blocked AND Jina could not recover it. The site is live (it
        # answered with a block status) but unreachable to us and to a
        # renderer — a real wall, worth a manual look, not a confident tag.
        global _LAST_ABORT_REASON
        _LAST_ABORT_REASON = "auth_wall"
        return {"html": None, "text": None, "text_source": None,
                "js_rendered": False, "static_text_len": 0,
                "rendered_text_len": None}

    if html is None:
        return {"html": None, "text": None, "text_source": None,
                "js_rendered": False, "static_text_len": 0,
                "rendered_text_len": None}

    static_text = _strip_tags(html)
    static_len = len(static_text)

    needs_render = force_render or static_len < JS_SHELL_THRESHOLD
    if not needs_render:
        return {"html": html, "text": static_text, "text_source": "static",
                "js_rendered": False, "static_text_len": static_len,
                "rendered_text_len": None}

    print(f"  [render] static fetch saw {static_len} chars — "
          f"trying a renderer")

    for name, fn in (("jina", fetch_jina), ("firecrawl", fetch_firecrawl)):
        rendered = fn(url)
        if rendered and len(rendered.strip()) > static_len:
            rlen = len(rendered.strip())
            print(f"  [render] {name} returned {rlen} chars "
                  f"({rlen // max(static_len, 1)}x more)")
            return {"html": html, "text": rendered.strip(),
                    "text_source": name, "js_rendered": True,
                    "static_text_len": static_len, "rendered_text_len": rlen}
        time.sleep(RETRY_DELAY_SECS)

    print("  [render] no renderer available — content stays invisible")
    return {"html": html, "text": static_text, "text_source": "static",
            "js_rendered": False, "static_text_len": static_len,
            "rendered_text_len": None}
