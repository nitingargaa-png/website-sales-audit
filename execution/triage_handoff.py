#!/usr/bin/env python3
"""
triage_handoff.py — Automatic handoff from website-sales-audit to ghl-triage.

Watches the audit output directory for new or recently modified audit reports
and runs ghl-triage against them automatically. Designed to be called either:

  A) Automatically — invoked by Claude Code at the end of every audit run
     (wired into website-sales-audit CLAUDE.md as a post-audit step)

  B) Manually — run directly against a specific audit file or the whole
     output directory

Usage:
  # Auto mode — called by Claude Code after audit completes (pass the audit file)
  python3 execution/triage_handoff.py --audit output/[businessname]-[date].md

  # Manual mode — specific file, specific service
  python3 execution/triage_handoff.py --audit output/[file].md --service MCTB

  # Manual mode — all four services (default when --service not specified)
  python3 execution/triage_handoff.py --audit output/[file].md

  # Batch mode — run triage on all audit files not yet triaged
  python3 execution/triage_handoff.py --batch

  # Batch mode — force re-triage even if already done
  python3 execution/triage_handoff.py --batch --force

  # Dry run — show what would be triaged without running anything
  python3 execution/triage_handoff.py --batch --dry-run

Prerequisites:
  - ghl-triage project must exist at ../ghl-triage/ relative to this file
    (i.e. projects/website-sales-audit/ and projects/ghl-triage/ are siblings)
  - ANTHROPIC_API_KEY must be set in .env
  - ghl-triage/prospect_triage.py must have the --from-audit flag (v2+)

Output:
  - Triage results land in ghl-triage/output/ as normal
  - A handoff log is maintained at output/triage_handoff_log.json
    so batch mode knows which files have already been triaged
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

THIS_DIR      = Path(__file__).resolve().parent          # execution/
PROJECT_ROOT  = THIS_DIR.parent                          # website-sales-audit/
AUDIT_OUT_DIR = PROJECT_ROOT / "output"
TRIAGE_DIR    = PROJECT_ROOT.parent / "ghl-triage"
TRIAGE_SCRIPT = TRIAGE_DIR / "prospect_triage.py"
HANDOFF_LOG   = AUDIT_OUT_DIR / "triage_handoff_log.json"

PHASE1_SERVICES = ["MCTB", "VAAI", "GRM", "WEB"]


# ---------------------------------------------------------------------------
# Handoff log — tracks which audit files have been triaged
# ---------------------------------------------------------------------------

def load_log() -> dict:
    """Load handoff log. Returns empty dict if not found or corrupt."""
    if not HANDOFF_LOG.exists():
        return {}
    try:
        with open(HANDOFF_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_log(log: dict) -> None:
    """Persist handoff log to disk."""
    AUDIT_OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(HANDOFF_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def mark_triaged(log: dict, audit_path: Path, services: list, result: str) -> None:
    """Record a completed triage in the log."""
    log[str(audit_path.name)] = {
        "audit_file":   audit_path.name,
        "triaged_at":   datetime.now().isoformat(timespec="seconds"),
        "services":     services,
        "result":       result,           # "success" | "error" | "skipped"
    }


def already_triaged(log: dict, audit_path: Path) -> bool:
    """Return True if this audit file has been successfully triaged before."""
    entry = log.get(str(audit_path.name))
    if not entry:
        return False
    return entry.get("result") == "success"


# ---------------------------------------------------------------------------
# Prerequisite checks
# ---------------------------------------------------------------------------

def check_prerequisites() -> list[str]:
    """
    Return a list of error messages. Empty list = all good.
    """
    errors = []

    if not TRIAGE_DIR.exists():
        errors.append(
            f"ghl-triage project not found at: {TRIAGE_DIR}\n"
            f"  Expected folder structure:\n"
            f"    projects/\n"
            f"      website-sales-audit/   ← this project\n"
            f"      ghl-triage/            ← must exist here"
        )

    if not TRIAGE_SCRIPT.exists():
        errors.append(
            f"prospect_triage.py not found at: {TRIAGE_SCRIPT}\n"
            f"  Make sure ghl-triage is set up and prospect_triage.py has "
            f"the --from-audit flag (v2+)."
        )

    # Check ANTHROPIC_API_KEY (needed by triage for Haiku generation)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        # Try loading from ghl-triage .env
        triage_env = TRIAGE_DIR / ".env"
        if triage_env.exists():
            with open(triage_env, "r") as f:
                for line in f:
                    if line.startswith("ANTHROPIC_API_KEY="):
                        key = line.split("=", 1)[1].strip()
                        if key:
                            os.environ["ANTHROPIC_API_KEY"] = key
                            break
        if not os.environ.get("ANTHROPIC_API_KEY"):
            errors.append(
                "ANTHROPIC_API_KEY not set. Add it to .env in either project."
            )

    return errors


# ---------------------------------------------------------------------------
# Core triage runner
# ---------------------------------------------------------------------------

def run_triage(audit_path: Path, services: list, dry_run: bool = False) -> str:
    """
    Run prospect_triage.py --from-audit against the given audit file.

    For a single service: runs once with --service [SERVICE]
    For multiple services: runs with --service ALL (one pass, four outputs)

    Returns "success", "error", or "skipped".
    """
    if not audit_path.exists():
        print(f"  ❌ Audit file not found: {audit_path}")
        return "error"

    # Determine service argument
    if set(services) == set(PHASE1_SERVICES) or "ALL" in services:
        service_arg = "ALL"
    elif len(services) == 1:
        service_arg = services[0].upper()
    else:
        # Multiple but not all — run ALL and accept the extra output
        service_arg = "ALL"

    cmd = [
        sys.executable,
        str(TRIAGE_SCRIPT),
        "--service", service_arg,
        "--from-audit", str(audit_path),
    ]

    print(f"\n  {'[DRY RUN] Would run' if dry_run else 'Running'}:")
    print(f"  {' '.join(cmd)}")

    if dry_run:
        return "skipped"

    try:
        result = subprocess.run(
            cmd,
            cwd=str(TRIAGE_DIR),
            capture_output=False,   # stream output to terminal
            text=True,
            timeout=300,            # 5 min max per audit
        )
        if result.returncode == 0:
            print(f"  ✅ Triage complete — {audit_path.name}")
            return "success"
        else:
            print(f"  ❌ Triage failed (exit code {result.returncode}) — {audit_path.name}")
            return "error"
    except subprocess.TimeoutExpired:
        print(f"  ⏱ Triage timed out after 5 minutes — {audit_path.name}")
        return "error"
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return "error"


# ---------------------------------------------------------------------------
# Batch mode — find all untriaged audit files
# ---------------------------------------------------------------------------

def find_audit_files() -> list[Path]:
    """
    Return all .md files in the audit output directory that look like
    audit reports (named [businessname]-[date].md).
    Sorted oldest-first so batch processing runs in chronological order.
    """
    if not AUDIT_OUT_DIR.exists():
        return []

    files = []
    for f in AUDIT_OUT_DIR.glob("*.md"):
        # Skip the handoff log itself and any non-audit files
        if f.name.startswith("triage_") or f.name.startswith("_"):
            continue
        # Must match pattern: something-YYYY-MM-DD.md
        import re
        if re.search(r"-\d{4}-\d{2}-\d{2}\.md$", f.name):
            files.append(f)

    files.sort(key=lambda p: p.stat().st_mtime)
    return files


def run_batch(services: list, force: bool, dry_run: bool) -> None:
    """
    Run triage on all audit files not yet triaged (or all if --force).
    """
    audit_files = find_audit_files()
    if not audit_files:
        print(f"No audit files found in {AUDIT_OUT_DIR}")
        return

    log = load_log()
    pending = []

    for f in audit_files:
        if force or not already_triaged(log, f):
            pending.append(f)
        else:
            print(f"  [SKIP — already triaged] {f.name}")

    if not pending:
        print("\nAll audit files already triaged. Use --force to re-run.")
        return

    print(f"\n[BATCH] {len(pending)} file(s) to triage")
    print(f"[BATCH] Services: {', '.join(services)}")

    for i, audit_path in enumerate(pending):
        print(f"\n[{i+1}/{len(pending)}] {audit_path.name}")
        result = run_triage(audit_path, services, dry_run=dry_run)
        if not dry_run:
            mark_triaged(log, audit_path, services, result)
            save_log(log)

    print(f"\n[BATCH DONE] Processed {len(pending)} audit file(s)")
    if not dry_run:
        print(f"[BATCH LOG]  {HANDOFF_LOG}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Handoff: website-sales-audit → ghl-triage"
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--audit", type=str,
        help="Path to a specific audit .md file to triage"
    )
    mode.add_argument(
        "--batch", action="store_true",
        help="Run triage on all untriaged audit files in output/"
    )

    parser.add_argument(
        "--service", type=str, default="ALL",
        help="Service(s) to score: MCTB, VAAI, GRM, WEB, or ALL (default: ALL)"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-triage even if already triaged (batch mode only)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would run without executing anything"
    )

    args = parser.parse_args()

    # Resolve services
    service_upper = args.service.upper()
    if service_upper == "ALL":
        services = PHASE1_SERVICES
    else:
        services = [s.strip().upper() for s in service_upper.split(",")]
        invalid = [s for s in services if s not in PHASE1_SERVICES]
        if invalid:
            print(f"ERROR: Unknown service(s): {', '.join(invalid)}")
            print(f"       Valid: {', '.join(PHASE1_SERVICES)} or ALL")
            sys.exit(1)

    # Prerequisite check
    errors = check_prerequisites()
    if errors:
        print("❌ Prerequisites not met:\n")
        for err in errors:
            print(f"  • {err}\n")
        sys.exit(1)

    # Run
    if args.batch:
        run_batch(services, force=args.force, dry_run=args.dry_run)
    else:
        audit_path = Path(args.audit)
        if not audit_path.is_absolute():
            # Resolve relative to project root (not execution/)
            audit_path = PROJECT_ROOT / audit_path

        print(f"\n[HANDOFF] Audit: {audit_path.name}")
        print(f"[HANDOFF] Services: {', '.join(services)}")

        result = run_triage(audit_path, services, dry_run=args.dry_run)

        if not args.dry_run:
            log = load_log()
            mark_triaged(log, audit_path, services, result)
            save_log(log)
            print(f"[HANDOFF LOG] {HANDOFF_LOG}")

        sys.exit(0 if result in ("success", "skipped") else 1)


if __name__ == "__main__":
    main()
