#!/usr/bin/env python3
"""
check_template_parity.py

Verifies that files listed in <project_root>/.shared-templates are
byte-identical across this project and a sibling project.

Why: Some files (e.g. skill templates, prompt templates) are
intentionally duplicated across sibling projects to keep each
project self-contained. Silent drift between copies is a real risk.
This script catches drift at commit time via a pre-commit hook.

Usage:
    python tools/check_template_parity.py           # quiet on success
    python tools/check_template_parity.py --verbose # prints OK summary

Sibling project:
    Defaults to '../website-audit-builder' relative to project root.
    Override with env var SIBLING_PROJECT_NAME to use a different
    sibling folder name (same parent directory).

Exit codes:
    0 - all listed files match, or sibling project absent (non-fatal)
    1 - at least one file differs, is missing, or manifest is malformed
"""

import hashlib
import os
import sys
from pathlib import Path

DEFAULT_SIBLING_NAME = "website-audit-builder"
MANIFEST_FILENAME = ".shared-templates"


def sha256(path: Path) -> str:
    """SHA256 of file contents with CRLF normalized to LF.

    core.autocrlf=true on Windows causes checked-out files to have CRLF
    while sibling working trees may have LF. Normalizing before hashing
    ensures we only detect real content drift, not line-ending drift.
    """
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def read_manifest(manifest_path: Path) -> list[str]:
    if not manifest_path.is_file():
        print(f"ERROR: manifest not found at {manifest_path}", file=sys.stderr)
        sys.exit(1)
    entries = []
    for raw in manifest_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        entries.append(line)
    return entries


def main() -> int:
    verbose = "--verbose" in sys.argv

    project_root = Path(__file__).resolve().parent.parent
    sibling_name = os.environ.get("SIBLING_PROJECT_NAME", DEFAULT_SIBLING_NAME)
    sibling_root = project_root.parent / sibling_name

    if not sibling_root.is_dir():
        print(
            f"WARN: sibling project '{sibling_name}' not found at {sibling_root}. "
            f"Skipping template-parity check.",
            file=sys.stderr,
        )
        return 0

    manifest = project_root / MANIFEST_FILENAME
    entries = read_manifest(manifest)

    if not entries:
        if verbose:
            print("OK: manifest empty, nothing to check.")
        return 0

    mismatches = []
    for rel in entries:
        local = project_root / rel
        remote = sibling_root / rel
        if not local.is_file():
            print(f"ERROR: missing locally: {local}", file=sys.stderr)
            mismatches.append(rel)
            continue
        if not remote.is_file():
            print(f"ERROR: missing in sibling: {remote}", file=sys.stderr)
            mismatches.append(rel)
            continue
        local_hash = sha256(local)
        remote_hash = sha256(remote)
        if local_hash != remote_hash:
            print(f"DRIFT: {rel}", file=sys.stderr)
            print(f"  local  ({local}): {local_hash}", file=sys.stderr)
            print(f"  remote ({remote}): {remote_hash}", file=sys.stderr)
            print(
                f"  sync with: cp '{remote}' '{local}'   (or the other way)",
                file=sys.stderr,
            )
            mismatches.append(rel)

    if mismatches:
        print(
            f"\n{len(mismatches)} file(s) out of sync with sibling '{sibling_name}'. "
            f"Resolve before committing (or bypass with: git commit --no-verify).",
            file=sys.stderr,
        )
        return 1

    if verbose:
        print(f"OK: {len(entries)} template(s) match sibling '{sibling_name}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
