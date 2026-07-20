"""
abort_reason.py — classify a fetch failure into a rebuild-lead pitch tag.

render.fetch collapses every hard failure to html=None and PRINTS the
exception, then discards it. To route a broken site to the right pitch we
need the failure CLASS carried outward, not the string. This module is the
one place that mapping lives, so render.py and audit_batch.py agree and a
tag never means two things.

DESIGN RULE: never guess a confident tag. An SSL error is SSL; a DNS failure
is DNS; anything we cannot positively identify is site_down_unknown, which
routes to a MANUAL check, not to a wrong "your certificate is broken" pitch
sent to a business whose site merely timed out. A wrong tag in an outreach
message is worse than an untagged lead — it burns trust on first contact.

The six positive tags mirror the table agreed in the sourcing design and the
no_website book's pitch language. DNS-dead overlaps the no_website lane
conceptually (a business with a dead domain is functionally no-website) but
is kept distinct here because the pitch differs: no_website is "you have no
site", domain_dead is "you HAD a site and let it lapse".
"""
import socket
from typing import Optional

import requests

# tag -> plain-English meaning, for the CSV and as a pitch reminder. Kept
# next to the classifier so the two never drift.
TAG_MEANING = {
    "site_down_ssl":   "security/certificate error - browser blocks visitors",
    "domain_dead":     "domain does not resolve - lapsed or never existed",
    "site_down_slow":  "connection times out or resets - fails mobile visitors",
    "site_error":      "server returns a 5xx error - site is broken",
    "page_missing":    "homepage 404 - check manually, site may have moved",
    "auth_wall":       "401/403 wall - check manually, may be under construction",
    "site_down_unknown": "did not load, reason unclear - check manually",
}


def from_status(status_code: int) -> Optional[str]:
    """
    HTTP status -> tag. Returns None for a status that is NOT an abort
    (e.g. 200), so the caller can tell 'not a failure' from 'unknown
    failure'. 401 and 403 both mean a wall the visitor also hits; 403 in
    particular reaches here only AFTER render's soft-block retry+Jina path
    has already failed, so it is a real wall, not a transient bot-block.
    """
    if status_code == 404:
        return "page_missing"
    if status_code in (401, 403):
        return "auth_wall"
    if 500 <= status_code <= 599:
        return "site_error"
    return None


def from_exception(exc: BaseException) -> str:
    """
    Requests/urllib exception -> tag. Order matters: SSLError is a subclass
    of ConnectionError in requests, so it MUST be tested first or every
    cert failure would be mislabeled a timeout/DNS. Timeout is also a
    ConnectionError sibling and tested before the generic connection case.

    A DNS failure surfaces as a ConnectionError wrapping socket.gaierror
    ('Name or service not known' / 'getaddrinfo failed'). We detect it by
    walking the cause chain to a gaierror rather than string-matching the
    message, because the message text is OS- and locale-dependent and a
    string match silently stops working on a German-locale Windows box.
    """
    # SSL first — it is a ConnectionError subclass.
    if isinstance(exc, requests.exceptions.SSLError):
        return "site_down_ssl"

    # Timeouts (connect or read) — flaky/slow server.
    if isinstance(exc, requests.exceptions.Timeout):
        return "site_down_slow"

    # DNS: walk the cause chain for a socket.gaierror rather than trusting
    # the message string.
    if _has_dns_failure(exc):
        return "domain_dead"

    # Connection reset / refused / aborted — server dropped us. Same pitch
    # as a timeout: the site fails real visitors.
    if isinstance(exc, requests.exceptions.ConnectionError):
        return "site_down_slow"

    # Anything else (ChunkedEncoding, TooManyRedirects, InvalidURL, a bare
    # socket error) — do NOT guess. Manual check.
    return "site_down_unknown"


def _has_dns_failure(exc: BaseException) -> bool:
    """
    True if a socket.gaierror appears anywhere in the exception's cause/
    context chain. gaierror is what getaddrinfo raises when a name will not
    resolve. urllib3 wraps it several layers deep, so we walk __cause__ and
    __context__ to the bottom.
    """
    seen = set()
    stack = [exc]
    while stack:
        e = stack.pop()
        if e is None or id(e) in seen:
            continue
        seen.add(id(e))
        if isinstance(e, socket.gaierror):
            return True
        # requests wraps urllib3 which wraps the socket error; the args
        # sometimes carry the inner exception rather than __cause__.
        for nxt in (getattr(e, "__cause__", None),
                    getattr(e, "__context__", None)):
            if nxt is not None:
                stack.append(nxt)
        for a in getattr(e, "args", ()):
            if isinstance(a, BaseException):
                stack.append(a)
    return False
