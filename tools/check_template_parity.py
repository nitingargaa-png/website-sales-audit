#!/usr/bin/env python3
"""
check_template_parity.py

Verifies that artifacts listed in manifests at <project_root> are
identical across this project and a sibling project. Three manifests
are supported, each with its own granularity and its own sibling:

    .shared-templates   whole-file byte-identity after CRLF normalization
    .shared-functions   named Python functions extracted via AST,
                        normalized (CRLF -> LF, then rstrip per line),
                        then compared for strict equality
    .shared-sections    named text regions delimited by HTML-comment
                        markers (<!-- shared-section:<tag> start --> /
                        ... end -->), CRLF-normalized, then compared
                        for strict equality

Every file listed in any manifest also passes a trailing-newline
hygiene check: exactly one LF at end of file (after CRLF
normalization). Zero or two-plus trailing LFs fail with rc=1.

Why: Some artifacts (e.g. WEBSITE_CLAUDE.md, or the small YAML-subset
sub-parser shared between the triage and audit-builder parsers) are
intentionally duplicated across sibling projects so each project is
self-contained. Silent drift between copies is a real risk. This
script catches drift at commit time via a pre-commit hook.

.shared-templates format:
    One path per line, relative to project root.
    Blank lines and # comments ignored.
    File must be LF-only and have no UTF-8 BOM; manifests are
    enforced byte-level to catch silent drift.
    A manifest-level sibling directive on its own line, before the
    first entry, pins the sibling for this manifest:
        # sibling: <name-or-path>
    Env var SHARED_TEMPLATE_SIBLING overrides if directive absent.
    If both are absent, exit code 2 (infrastructure problem).

.shared-functions format:
    One entry per line. Blank lines and # comments ignored.
    File must be LF-only and have no UTF-8 BOM; manifests are
    enforced byte-level to catch silent drift.
    A manifest-level sibling directive on its own line, before the
    first entry, pins the sibling for this manifest:
        # sibling: <name-or-path>
    A bare name resolves as a sibling folder (../<name>). A path with
    a separator resolves relative to project root. Absolute paths are
    used as-is. Env var SHARED_FUNCTION_SIBLING overrides if directive
    absent. If both are absent, exit code 2 (infrastructure problem).

    Each entry is a function-location pair:
        <local/path.py>::<fn>   [<=> <remote/path.py>::<fn>]
    The right side is optional; when absent the local side is used on
    both ends (function name and path identical across repos).

.shared-sections format:
    One entry per line. Blank lines and # comments ignored.
    File must be LF-only and have no UTF-8 BOM; manifests are
    enforced byte-level to catch silent drift.
    A manifest-level sibling directive on its own line, before the
    first entry, pins the sibling for this manifest:
        # sibling: <name-or-path>
    Env var SHARED_SECTION_SIBLING overrides if directive absent.
    Empty manifest (no entries, after stripping blanks and comments)
    is a silent no-op: check_sections returns (False, [], None) so the
    scaffolding file can land before any sections are listed. This is
    an intentional divergence from templates/functions, which would
    error on "no sibling configured" in that state.
    Duplicate entries (same local-path + local-tag) raise with
    exit code 2.

    Each entry is a section-location pair:
        <local/path>::<tag>   [<=> <remote/path>::<tag>]
    The right side is optional; when absent the local side is used on
    both ends (path and tag identical across repos).

    Within each file, the section is delimited by a single-purpose
    marker line pair:
        <!-- shared-section:<tag> start -->
        ... section content ...
        <!-- shared-section:<tag> end -->
    Each marker line must contain only the marker (surrounding
    whitespace allowed). Extra content on a marker line, missing
    markers, duplicate markers, and end-before-start are hard errors
    at check time (printed to stderr, section treated as mismatch).

Exit codes:
    0 - all listed artifacts match
    1 - at least one artifact differs or has an invalid trailing newline,
        one "MISMATCH: <what>" line each
    2 - sibling project not found, or manifest malformed
"""

import ast
import hashlib
import os
import sys
from pathlib import Path

TEMPLATES_MANIFEST = ".shared-templates"
FUNCTIONS_MANIFEST = ".shared-functions"
SECTIONS_MANIFEST = ".shared-sections"
SIBLING_DIRECTIVE = "# sibling:"
PAIR_SEP = "<=>"
FN_SEP = "::"
SECTION_START_FMT = "<!-- shared-section:{} start -->"
SECTION_END_FMT = "<!-- shared-section:{} end -->"


def resolve_sibling(project_root, name_or_path):
    """Resolve a sibling path.

    `name_or_path` must be non-None and can be:
        - a bare name (no path separators): sibling folder under
          project_root.parent (most common case: directive like
          '# sibling: ghl-triage')
        - a relative path (contains '/' or '\\'): resolved relative to
          project_root (escape hatch for non-sibling layouts)
        - an absolute path: used as-is
    """
    p = Path(name_or_path)
    if p.is_absolute():
        return p.resolve()
    # No path separator -> treat as sibling folder name
    if "/" not in name_or_path and "\\" not in name_or_path:
        return (project_root.parent / name_or_path).resolve()
    return (project_root / name_or_path).resolve()


def sha256_normalized_bytes(data_bytes):
    """SHA256 of bytes with CRLF normalized to LF.

    core.autocrlf=true on Windows causes checked-out files to have CRLF
    while sibling working trees may have LF. Normalizing before hashing
    ensures we only detect real content drift, not line-ending drift.
    """
    return hashlib.sha256(data_bytes.replace(b"\r\n", b"\n")).hexdigest()


def sha256_normalized_file(path):
    return sha256_normalized_bytes(path.read_bytes())


def _count_trailing_lf_bytes(data):
    """Return count of trailing \\n bytes in `data` after CRLF normalization.

    Pure-bytes helper so callers that already have the file's bytes in
    memory (e.g., the section extractor) don't re-read from disk.
    """
    data = data.replace(b"\r\n", b"\n")
    i = len(data)
    while i > 0 and data[i - 1:i] == b"\n":
        i -= 1
    return len(data) - i


def count_trailing_lf(path):
    """Return count of trailing \\n bytes after CRLF normalization.

    0 means no trailing newline (includes 0-byte files); 1 means
    exactly one trailing newline (the pass case); >=2 means a trailing
    blank line or worse. CRLF is normalized to LF first so
    core.autocrlf=true checkouts are not flagged spuriously, matching
    the hash helper above.

    Thin wrapper over `_count_trailing_lf_bytes` that reads the file.
    """
    return _count_trailing_lf_bytes(path.read_bytes())


def normalize_text(s):
    """Normalize extracted source text: CRLF -> LF, then strip trailing
    whitespace on each line. Matches what any sane editor/formatter does
    on save, so invisible whitespace drift never triggers a mismatch."""
    s = s.replace("\r\n", "\n")
    return "\n".join(line.rstrip() for line in s.split("\n"))


def validate_manifest_bytes(manifest_path):
    """Validate manifest file is LF-only and has no UTF-8 BOM.

    Manifests (.shared-templates, .shared-functions, .shared-sections)
    declare what is checked; .shared-sections and .shared-functions are
    not byte-compared across repos (only .shared-templates is, via
    self-reference), so silent byte-level drift (e.g., `Add-Content`
    writing CRLF into an otherwise-LF file) can go undetected. This
    validator enforces the design-lock invariant: LF throughout, no BOM.

    Returns True on pass. On fail, prints a specific ERROR to stderr
    and returns False.
    """
    data = manifest_path.read_bytes()
    if data[:3] == b"\xef\xbb\xbf":
        print(
            "ERROR: manifest {} starts with UTF-8 BOM (expected no BOM)".format(
                manifest_path
            ),
            file=sys.stderr,
        )
        return False
    cr_count = data.count(b"\r")
    if cr_count > 0:
        print(
            "ERROR: manifest {} contains {} CR byte(s) (expected LF-only)".format(
                manifest_path, cr_count
            ),
            file=sys.stderr,
        )
        return False
    return True


def read_simple_manifest(manifest_path):
    """Read .shared-templates: returns (sibling_directive, entries).

    sibling_directive is the value of the first '# sibling: <name>'
    comment, or None if absent. entries is a list of paths relative
    to project root.
    """
    if not validate_manifest_bytes(manifest_path):
        return None, None
    sibling_directive = None
    entries = []
    for raw in manifest_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.lower().startswith(SIBLING_DIRECTIVE):
            # first directive wins; later ones ignored silently
            if sibling_directive is None:
                sibling_directive = line[len(SIBLING_DIRECTIVE):].strip()
            continue
        if line.startswith("#"):
            continue
        entries.append(line)
    return sibling_directive, entries


def read_functions_manifest(manifest_path):
    """Read .shared-functions: returns (sibling_directive, entries).

    sibling_directive is the value of the first '# sibling: <name>'
    comment, or None if absent. entries is a list of
    (local_path, local_fn, remote_path, remote_fn) tuples.
    """
    if not validate_manifest_bytes(manifest_path):
        return None, None
    sibling_directive = None
    entries = []
    for raw in manifest_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.lower().startswith(SIBLING_DIRECTIVE):
            # first directive wins; later ones ignored silently
            if sibling_directive is None:
                sibling_directive = line[len(SIBLING_DIRECTIVE):].strip()
            continue
        if line.startswith("#"):
            continue
        # parse <local>::<fn> [<=> <remote>::<fn>]
        if PAIR_SEP in line:
            left, right = [s.strip() for s in line.split(PAIR_SEP, 1)]
        else:
            left, right = line, line
        if FN_SEP not in left or FN_SEP not in right:
            print(
                "ERROR: malformed .shared-functions entry (need '{}'): {!r}".format(
                    FN_SEP, line
                ),
                file=sys.stderr,
            )
            return None, None
        local_path, local_fn = [s.strip() for s in left.split(FN_SEP, 1)]
        remote_path, remote_fn = [s.strip() for s in right.split(FN_SEP, 1)]
        if not (local_path and local_fn and remote_path and remote_fn):
            print(
                "ERROR: malformed .shared-functions entry (empty part): {!r}".format(
                    line
                ),
                file=sys.stderr,
            )
            return None, None
        entries.append((local_path, local_fn, remote_path, remote_fn))
    return sibling_directive, entries


def extract_function_source(py_path, fn_name):
    """Return normalized source of the top-level function `fn_name` in
    `py_path`, or None if the file can't be read, can't be parsed, or
    the function isn't a top-level def. Prints a specific error and
    returns None; caller treats None as a mismatch."""
    try:
        src = py_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(
            "ERROR: cannot read {}: {}".format(py_path, exc), file=sys.stderr
        )
        return None
    try:
        tree = ast.parse(src, filename=str(py_path))
    except SyntaxError as exc:
        print(
            "ERROR: cannot AST-parse {}: {}".format(py_path, exc),
            file=sys.stderr,
        )
        return None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == fn_name:
                segment = ast.get_source_segment(src, node)
                if segment is None:
                    print(
                        "ERROR: could not extract source for {}::{}".format(
                            py_path, fn_name
                        ),
                        file=sys.stderr,
                    )
                    return None
                return normalize_text(segment)
    print(
        "ERROR: function '{}' not found at top level of {}".format(
            fn_name, py_path
        ),
        file=sys.stderr,
    )
    return None


def _extract_section(path, tag):
    """Return normalized section content for `tag` in `path`, or None on error.

    The section is the text between two single-purpose marker lines:
        <!-- shared-section:<tag> start -->
        ... content ...
        <!-- shared-section:<tag> end -->

    CRLF is normalized to LF before extraction, matching the hash and
    trailing-newline helpers. Marker lines must contain only the marker
    (surrounding whitespace is allowed); any extra content on a marker
    line is a hard error. Missing markers, duplicate markers, and end
    before start are also hard errors. On any error, a specific message
    is printed to stderr and None is returned; the caller treats None
    as a mismatch.
    """
    try:
        data = path.read_bytes()
    except OSError as exc:
        print(
            "ERROR: cannot read {}: {}".format(path, exc), file=sys.stderr
        )
        return None
    try:
        text = data.replace(b"\r\n", b"\n").decode("utf-8")
    except UnicodeDecodeError as exc:
        print(
            "ERROR: cannot decode {} as UTF-8: {}".format(path, exc),
            file=sys.stderr,
        )
        return None

    start_marker = SECTION_START_FMT.format(tag)
    end_marker = SECTION_END_FMT.format(tag)

    # splitlines(keepends=True) preserves the trailing "\n" on each
    # line so line-level repr() in error messages shows the exact
    # offending bytes (e.g. stray CRs stripped by normalization above
    # can't reach us, but stray spaces before the marker do).
    lines = text.splitlines(keepends=True)
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        bare = line.rstrip("\n").strip()
        if start_marker in line:
            if bare != start_marker:
                print(
                    "ERROR: start marker line has extra content for "
                    "section {!r} in {}: {!r}".format(tag, path, line),
                    file=sys.stderr,
                )
                return None
            if start_idx is not None:
                print(
                    "ERROR: duplicate start marker for section {!r} in "
                    "{}".format(tag, path),
                    file=sys.stderr,
                )
                return None
            start_idx = i
            continue
        if end_marker in line:
            if bare != end_marker:
                print(
                    "ERROR: end marker line has extra content for "
                    "section {!r} in {}: {!r}".format(tag, path, line),
                    file=sys.stderr,
                )
                return None
            if start_idx is None:
                print(
                    "ERROR: end marker before start marker for section "
                    "{!r} in {}".format(tag, path),
                    file=sys.stderr,
                )
                return None
            if end_idx is not None:
                print(
                    "ERROR: duplicate end marker for section {!r} in "
                    "{}".format(tag, path),
                    file=sys.stderr,
                )
                return None
            end_idx = i

    if start_idx is None:
        print(
            "ERROR: start marker not found for section {!r} in {}".format(
                tag, path
            ),
            file=sys.stderr,
        )
        return None
    if end_idx is None:
        print(
            "ERROR: end marker not found for section {!r} in {}".format(
                tag, path
            ),
            file=sys.stderr,
        )
        return None

    # Content between markers, exclusive of marker lines themselves.
    # keepends preserves newlines, so joining with "" reassembles the
    # exact bytes that lived between the two marker lines.
    return "".join(lines[start_idx + 1:end_idx])


def read_sections_manifest(manifest_path):
    """Read .shared-sections: returns (sibling_directive, entries).

    sibling_directive is the value of the first '# sibling: <name>'
    comment, or None if absent. entries is a list of
    (local_path, local_tag, remote_path, remote_tag) tuples.

    Duplicate entries (same local-path + local-tag) raise: returns
    (None, None) after printing an ERROR, matching the malformed-entry
    error style.
    """
    if not validate_manifest_bytes(manifest_path):
        return None, None
    sibling_directive = None
    entries = []
    seen_keys = set()
    for raw in manifest_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.lower().startswith(SIBLING_DIRECTIVE):
            # first directive wins; later ones ignored silently
            if sibling_directive is None:
                sibling_directive = line[len(SIBLING_DIRECTIVE):].strip()
            continue
        if line.startswith("#"):
            continue
        # parse <local>::<tag> [<=> <remote>::<tag>]
        if PAIR_SEP in line:
            left, right = [s.strip() for s in line.split(PAIR_SEP, 1)]
        else:
            left, right = line, line
        if FN_SEP not in left or FN_SEP not in right:
            print(
                "ERROR: malformed .shared-sections entry (need '{}'): {!r}".format(
                    FN_SEP, line
                ),
                file=sys.stderr,
            )
            return None, None
        local_path, local_tag = [s.strip() for s in left.split(FN_SEP, 1)]
        remote_path, remote_tag = [s.strip() for s in right.split(FN_SEP, 1)]
        if not (local_path and local_tag and remote_path and remote_tag):
            print(
                "ERROR: malformed .shared-sections entry (empty part): {!r}".format(
                    line
                ),
                file=sys.stderr,
            )
            return None, None
        key = (local_path, local_tag)
        if key in seen_keys:
            print(
                "ERROR: duplicate .shared-sections entry: {!r}".format(
                    "{}{}{}".format(local_path, FN_SEP, local_tag)
                ),
                file=sys.stderr,
            )
            return None, None
        seen_keys.add(key)
        entries.append((local_path, local_tag, remote_path, remote_tag))
    return sibling_directive, entries


def check_templates(project_root):
    """Run .shared-templates checks. Returns (ran, mismatches, sibling_root)."""
    manifest = project_root / TEMPLATES_MANIFEST
    if not manifest.is_file():
        return False, [], None
    directive, entries = read_simple_manifest(manifest)
    if entries is None:
        # malformed manifest; read_simple_manifest already printed
        return True, ["__manifest_malformed__"], None
    # sibling resolution: manifest directive > env > error
    env_override = os.environ.get("SHARED_TEMPLATE_SIBLING")
    sibling_name_or_path = directive or env_override
    if sibling_name_or_path is None:
        print(
            "ERROR: no sibling configured for {}".format(TEMPLATES_MANIFEST),
            file=sys.stderr,
        )
        print(
            "  set the '# sibling: <name>' directive in {} or "
            "SHARED_TEMPLATE_SIBLING env var.".format(TEMPLATES_MANIFEST),
            file=sys.stderr,
        )
        return True, ["__sibling_missing__"], None
    sibling_root = resolve_sibling(
        project_root, sibling_name_or_path
    )
    if not sibling_root.is_dir():
        print(
            "ERROR: sibling project not found at {} (for {})".format(
                sibling_root, TEMPLATES_MANIFEST
            ),
            file=sys.stderr,
        )
        print(
            "  set the '# sibling: <name>' directive in {} or "
            "SHARED_TEMPLATE_SIBLING env var.".format(TEMPLATES_MANIFEST),
            file=sys.stderr,
        )
        return True, ["__sibling_missing__"], sibling_root
    mismatches = []
    for rel in entries:
        local = project_root / rel
        remote = sibling_root / rel
        if not local.is_file():
            print(
                "MISMATCH: {} (missing locally: {})".format(rel, local),
                file=sys.stderr,
            )
            mismatches.append(rel)
            continue
        if not remote.is_file():
            print(
                "MISMATCH: {} (missing in sibling: {})".format(rel, remote),
                file=sys.stderr,
            )
            mismatches.append(rel)
            continue
        if sha256_normalized_file(local) != sha256_normalized_file(remote):
            print("MISMATCH: {}".format(rel), file=sys.stderr)
            mismatches.append(rel)
        # Trailing-newline hygiene: both sides checked independently.
        # Append-guarded by `rel not in mismatches` so a byte-identity
        # failure and a trailing-newline failure on the same entry
        # stay as one list entry while still printing separate
        # MISMATCH lines to stderr (operator sees both signals).
        # 0-byte files are exempt: the trailing-newline concept does
        # not apply to empty content, and scaffolding manifests
        # (e.g. an empty .shared-sections) must be able to land on
        # both repos without spurious MISMATCH spew.
        for side_path, side_label in ((local, "locally"), (remote, "in sibling")):
            if side_path.stat().st_size == 0:
                continue
            n = count_trailing_lf(side_path)
            if n == 1:
                continue
            if n == 0:
                print(
                    "MISMATCH: {} (no trailing newline {}: {})".format(
                        rel, side_label, side_path
                    ),
                    file=sys.stderr,
                )
            else:
                print(
                    "MISMATCH: {} ({} trailing newlines {}: {})".format(
                        rel, n, side_label, side_path
                    ),
                    file=sys.stderr,
                )
            if rel not in mismatches:
                mismatches.append(rel)
    if not mismatches:
        print(
            "OK: {} template(s) in sync with {}".format(
                len(entries), sibling_root
            )
        )
    return True, mismatches, sibling_root


def check_functions(project_root):
    """Run .shared-functions checks. Returns (ran, mismatches, sibling_root)."""
    manifest = project_root / FUNCTIONS_MANIFEST
    if not manifest.is_file():
        return False, [], None
    directive, entries = read_functions_manifest(manifest)
    if entries is None:
        # malformed manifest; read_functions_manifest already printed
        return True, ["__manifest_malformed__"], None
    # sibling resolution: manifest directive > env > error
    env_override = os.environ.get("SHARED_FUNCTION_SIBLING")
    sibling_name_or_path = directive or env_override
    if sibling_name_or_path is None:
        print(
            "ERROR: no sibling configured for {}".format(FUNCTIONS_MANIFEST),
            file=sys.stderr,
        )
        print(
            "  set the '# sibling: <name>' directive in {} or "
            "SHARED_FUNCTION_SIBLING env var.".format(FUNCTIONS_MANIFEST),
            file=sys.stderr,
        )
        return True, ["__sibling_missing__"], None
    sibling_root = resolve_sibling(
        project_root, sibling_name_or_path
    )
    if not sibling_root.is_dir():
        print(
            "ERROR: sibling project not found at {} (for {})".format(
                sibling_root, FUNCTIONS_MANIFEST
            ),
            file=sys.stderr,
        )
        print(
            "  set the '# sibling: <name>' directive in {} or "
            "SHARED_FUNCTION_SIBLING env var.".format(FUNCTIONS_MANIFEST),
            file=sys.stderr,
        )
        return True, ["__sibling_missing__"], sibling_root
    mismatches = []
    trailing_checked = set()
    for local_rel, local_fn, remote_rel, remote_fn in entries:
        local_path = project_root / local_rel
        remote_path = sibling_root / remote_rel
        tag = "{}::{}".format(local_rel, local_fn)
        if local_rel != remote_rel or local_fn != remote_fn:
            tag = "{}::{} <=> {}::{}".format(
                local_rel, local_fn, remote_rel, remote_fn
            )
        if not local_path.is_file():
            print(
                "MISMATCH: {} (local file missing: {})".format(
                    tag, local_path
                ),
                file=sys.stderr,
            )
            mismatches.append(tag)
            continue
        if not remote_path.is_file():
            print(
                "MISMATCH: {} (remote file missing: {})".format(
                    tag, remote_path
                ),
                file=sys.stderr,
            )
            mismatches.append(tag)
            continue
        local_src = extract_function_source(local_path, local_fn)
        remote_src = extract_function_source(remote_path, remote_fn)
        if local_src is None or remote_src is None:
            # extractor already printed a specific error
            mismatches.append(tag)
            continue
        if local_src != remote_src:
            print("MISMATCH: {}".format(tag), file=sys.stderr)
            mismatches.append(tag)
        # Trailing-newline hygiene on the file itself (not the function
        # extract). Dedup by absolute path so a .py file with multiple
        # shared-function entries is only checked once per side per
        # run. Append-guarded so one file's trailing-newline failure
        # produces one mismatches entry regardless of how many function
        # entries reference it. 0-byte files are exempt (mirrors
        # check_templates): empty content has no trailing-newline
        # concept, and the earlier function-extractor step has already
        # produced a specific mismatch for the missing function.
        for side_rel, side_path, side_label in (
            (local_rel, local_path, "locally"),
            (remote_rel, remote_path, "in sibling"),
        ):
            key = str(side_path.resolve())
            if key in trailing_checked:
                continue
            trailing_checked.add(key)
            if side_path.stat().st_size == 0:
                continue
            n = count_trailing_lf(side_path)
            if n == 1:
                continue
            if n == 0:
                print(
                    "MISMATCH: {} (no trailing newline {}: {})".format(
                        side_rel, side_label, side_path
                    ),
                    file=sys.stderr,
                )
            else:
                print(
                    "MISMATCH: {} ({} trailing newlines {}: {})".format(
                        side_rel, n, side_label, side_path
                    ),
                    file=sys.stderr,
                )
            if side_rel not in mismatches:
                mismatches.append(side_rel)
    if not mismatches:
        print(
            "OK: {} function(s) in sync with {}".format(
                len(entries), sibling_root
            )
        )
    return True, mismatches, sibling_root


def check_sections(project_root):
    """Run .shared-sections checks. Returns (ran, mismatches, sibling_root).

    Intentional divergence from check_templates/check_functions: when
    the manifest file exists but has zero entries, this returns
    (False, [], None) -- a silent no-op -- so the scaffolding manifest
    can land before any sections are listed. Templates and functions
    would error on "no sibling configured" in that state.
    """
    manifest = project_root / SECTIONS_MANIFEST
    if not manifest.is_file():
        return False, [], None
    directive, entries = read_sections_manifest(manifest)
    if entries is None:
        # malformed manifest; read_sections_manifest already printed
        return True, ["__manifest_malformed__"], None
    if not entries:
        # Empty manifest: intentional silent no-op (see docstring).
        return False, [], None
    # sibling resolution: manifest directive > env > error
    env_override = os.environ.get("SHARED_SECTION_SIBLING")
    sibling_name_or_path = directive or env_override
    if sibling_name_or_path is None:
        print(
            "ERROR: no sibling configured for {}".format(SECTIONS_MANIFEST),
            file=sys.stderr,
        )
        print(
            "  set the '# sibling: <name>' directive in {} or "
            "SHARED_SECTION_SIBLING env var.".format(SECTIONS_MANIFEST),
            file=sys.stderr,
        )
        return True, ["__sibling_missing__"], None
    sibling_root = resolve_sibling(project_root, sibling_name_or_path)
    if not sibling_root.is_dir():
        print(
            "ERROR: sibling project not found at {} (for {})".format(
                sibling_root, SECTIONS_MANIFEST
            ),
            file=sys.stderr,
        )
        print(
            "  set the '# sibling: <name>' directive in {} or "
            "SHARED_SECTION_SIBLING env var.".format(SECTIONS_MANIFEST),
            file=sys.stderr,
        )
        return True, ["__sibling_missing__"], sibling_root
    mismatches = []
    trailing_checked = set()
    for local_rel, local_tag, remote_rel, remote_tag in entries:
        local_path = project_root / local_rel
        remote_path = sibling_root / remote_rel
        # tag_id is the stderr-friendly identity; mirrors check_functions.
        tag_id = "{}{}{}".format(local_rel, FN_SEP, local_tag)
        if local_rel != remote_rel or local_tag != remote_tag:
            tag_id = "{}{}{} {} {}{}{}".format(
                local_rel, FN_SEP, local_tag,
                PAIR_SEP,
                remote_rel, FN_SEP, remote_tag,
            )
        if not local_path.is_file():
            print(
                "MISMATCH: {} (local file missing: {})".format(
                    tag_id, local_path
                ),
                file=sys.stderr,
            )
            if local_rel not in mismatches:
                mismatches.append(local_rel)
            continue
        if not remote_path.is_file():
            print(
                "MISMATCH: {} (remote file missing: {})".format(
                    tag_id, remote_path
                ),
                file=sys.stderr,
            )
            if local_rel not in mismatches:
                mismatches.append(local_rel)
            continue
        local_section = _extract_section(local_path, local_tag)
        remote_section = _extract_section(remote_path, remote_tag)
        if local_section is None or remote_section is None:
            # extractor already printed a specific error
            if local_rel not in mismatches:
                mismatches.append(local_rel)
            continue
        if local_section != remote_section:
            print("MISMATCH: {}".format(tag_id), file=sys.stderr)
            if local_rel not in mismatches:
                mismatches.append(local_rel)
        # Trailing-newline hygiene on the file itself (not the section
        # extract). Dedup by absolute path so multiple sections in the
        # same file only trigger one print per side per run. Identity
        # in the mismatches list is local_rel -- matches check_templates'
        # dedup pattern so one entry with BOTH a byte-identity failure
        # and a trailing-newline failure collapses to ONE list entry
        # while both MISMATCH lines still print to stderr. 0-byte
        # files are exempt (mirrors check_templates): empty content
        # has no trailing-newline concept, and the earlier section
        # extractor has already produced a specific missing-marker
        # mismatch for the entry.
        for side_rel, side_path, side_label in (
            (local_rel, local_path, "locally"),
            (remote_rel, remote_path, "in sibling"),
        ):
            key = str(side_path.resolve())
            if key in trailing_checked:
                continue
            trailing_checked.add(key)
            if side_path.stat().st_size == 0:
                continue
            n = count_trailing_lf(side_path)
            if n == 1:
                continue
            if n == 0:
                print(
                    "MISMATCH: {} (no trailing newline {}: {})".format(
                        side_rel, side_label, side_path
                    ),
                    file=sys.stderr,
                )
            else:
                print(
                    "MISMATCH: {} ({} trailing newlines {}: {})".format(
                        side_rel, n, side_label, side_path
                    ),
                    file=sys.stderr,
                )
            if local_rel not in mismatches:
                mismatches.append(local_rel)
    if not mismatches:
        print(
            "OK: {} section(s) in sync with {}".format(
                len(entries), sibling_root
            )
        )
    return True, mismatches, sibling_root


def main():
    project_root = Path(__file__).resolve().parent.parent

    templates_ran, templates_mm, _ = check_templates(project_root)
    functions_ran, functions_mm, _ = check_functions(project_root)
    sections_ran, sections_mm, _ = check_sections(project_root)

    if not templates_ran and not functions_ran and not sections_ran:
        print(
            "ERROR: no manifest found (looked for {}, {}, {})".format(
                TEMPLATES_MANIFEST, FUNCTIONS_MANIFEST, SECTIONS_MANIFEST
            ),
            file=sys.stderr,
        )
        return 2

    # Sibling-missing surfaces as exit 2 (infrastructure problem),
    # content mismatches surface as exit 1.
    sentinel_mm = {"__sibling_missing__", "__manifest_malformed__"}
    all_mm = templates_mm + functions_mm + sections_mm
    if any(m in sentinel_mm for m in all_mm):
        return 2
    if all_mm:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
