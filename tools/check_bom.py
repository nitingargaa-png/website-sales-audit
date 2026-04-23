#!/usr/bin/env python3
"""
check_bom.py

Rejects staged text files that begin with a UTF-8 BOM.

Why: A UTF-8 BOM (bytes EF BB BF) at the start of a text file is
invisible in most editors but changes the file's hash, confuses some
parsers, and shows up in diffs as mysterious drift. PowerShell's
Out-File and Set-Content default to writing BOMs on full-file
rewrites (Set-Content since PS 5.1 writes UTF-8 without BOM by
default, but Out-File still writes UTF-16 LE with BOM unless
-Encoding utf8 is passed, and even then older hosts wrote UTF-8 with
BOM). This check catches BOMs introduced that way before they are
committed.

Heuristic text detection: read the first 8192 bytes of the staged
blob; if any null byte appears, treat as binary and skip. Otherwise
treat as text and check the first 3 bytes for EF BB BF.

Staged content is read from the git index (git show :path) so that
working-tree changes not yet staged do not influence the check. The
scan covers files that are added, copied, or modified in the index
(git diff --cached --name-only --diff-filter=ACM -z).

Exit codes:
    0 - no staged text file starts with a UTF-8 BOM
    2 - infrastructure problem (not a git repo, git not on PATH, or
        a git plumbing call failed)
    3 - one or more staged text files start with a UTF-8 BOM; each
        offending path is printed to stderr on its own "ERROR:" line
"""

import subprocess
import sys

UTF8_BOM = b"\xef\xbb\xbf"
TEXT_SNIFF_BYTES = 8192


def run_git(args):
    """Run git with the given args, return (rc, stdout_bytes, stderr_text).

    stdout is bytes because we pipe binary blob content through git show.
    stderr is decoded text because it carries diagnostic messages.
    """
    try:
        proc = subprocess.run(
            ["git"] + list(args),
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return None, None, "git not found on PATH"
    except OSError as exc:
        return None, None, "git invocation failed: {}".format(exc)
    return proc.returncode, proc.stdout, proc.stderr.decode(
        "utf-8", errors="replace"
    )


def staged_paths():
    """Return list of paths added/copied/modified in the index, as str.

    Uses -z (NUL-delimited) so paths with spaces or unusual characters
    survive intact. Paths are decoded as UTF-8 with surrogateescape so
    even non-UTF-8 filesystem paths round-trip without raising.
    """
    rc, stdout, stderr = run_git(
        ["diff", "--cached", "--name-only", "--diff-filter=ACM", "-z"]
    )
    if rc is None:
        print("ERROR: {}".format(stderr), file=sys.stderr)
        return None
    if rc != 0:
        print(
            "ERROR: git diff --cached failed (rc={}): {}".format(
                rc, stderr.strip()
            ),
            file=sys.stderr,
        )
        return None
    if not stdout:
        return []
    raw = stdout.decode("utf-8", errors="surrogateescape")
    # -z terminates each entry with NUL, including the last one on
    # modern git. Strip a trailing NUL if present, then split.
    if raw.endswith("\x00"):
        raw = raw[:-1]
    if not raw:
        return []
    return raw.split("\x00")


def staged_blob_bytes(path):
    """Return the staged blob content as bytes, or None on error.

    A missing staged blob (e.g., symlink, gitlink, submodule) surfaces
    as git show rc != 0; we report it to stderr and return None so the
    caller can treat the path as non-scannable without blocking.
    """
    rc, stdout, stderr = run_git(["show", ":" + path])
    if rc is None:
        print(
            "ERROR: could not read staged blob for {}: {}".format(
                path, stderr
            ),
            file=sys.stderr,
        )
        return None
    if rc != 0:
        print(
            "ERROR: git show failed for {} (rc={}): {}".format(
                path, rc, stderr.strip()
            ),
            file=sys.stderr,
        )
        return None
    return stdout


def looks_like_text(head_bytes):
    """Heuristic: first TEXT_SNIFF_BYTES of content contain no null byte."""
    return b"\x00" not in head_bytes[:TEXT_SNIFF_BYTES]


def main():
    paths = staged_paths()
    if paths is None:
        return 2
    if not paths:
        return 0
    offenders = []
    infra_error = False
    for path in paths:
        content = staged_blob_bytes(path)
        if content is None:
            # staged_blob_bytes already printed a specific ERROR;
            # treat as infra problem rather than BOM offense
            infra_error = True
            continue
        if not looks_like_text(content):
            # binary (per null-byte heuristic); skip silently
            continue
        if content[:3] == UTF8_BOM:
            print(
                "ERROR: staged file {} starts with UTF-8 BOM".format(path),
                file=sys.stderr,
            )
            offenders.append(path)
    if offenders:
        return 3
    if infra_error:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
