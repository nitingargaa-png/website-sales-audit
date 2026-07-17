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

JINA_BASE = "https://r.jina.ai/"
FIRECRAWL_URL = "https://api.firecrawl.dev/v1/scrape"
TIMEOUT_SECS = 60
RETRY_DELAY_SECS = 2.0

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "Chrome/121.0.0.0 Safari/537.36")

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


def fetch_static(url: str, quiet: bool = False) -> Optional[str]:
    """Raw HTML. Needed for script-src detection regardless of rendering."""
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": UA})
        if r.status_code != 200:
            if not quiet:
                print(f"  [fetch] HTTP {r.status_code} — {url}")
            return None
        return r.text
    except Exception as e:
        if not quiet:
            print(f"  [fetch] {e}")
        return None


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
