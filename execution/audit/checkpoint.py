"""
checkpoint.py — append-only resume log.

Originally lifted verbatim from ghl-triage/triage/output.py into
execution/audit_batch.py. Extracted here when sourcing/ needed the same
helpers: a third copy would have been drift, and importing from
audit_batch.py would have dragged the whole audit CLI (judge, render_pdf,
reportlab, anthropic, psi) into a sourcing run that touches none of it.

This module imports nothing but os. That is the point — it is safe to
import from anywhere in the repo.

Contract: one entry per line, UTF-8, flushed on every write so a kill -9
mid-batch loses at most the in-flight item. Entries are opaque strings;
the audit checkpoints URLs, sourcing checkpoints "trade|city|page" cells.
"""
import os


def write_checkpoint(path: str, entry: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(entry + "\n")
        f.flush()


def load_completed_urls(path: str) -> set:
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


# Alias — sourcing checkpoints grid cells, not URLs. Same file format,
# honest name at the call site.
load_completed = load_completed_urls
