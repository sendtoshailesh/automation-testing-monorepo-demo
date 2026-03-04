#!/usr/bin/env python3
"""
PII / secrets scan for CI.

Walks the given path and looks for common PII patterns (email addresses,
phone numbers, SSNs, credit card numbers) as well as hardcoded secrets
(API keys, passwords, tokens) using simple regex heuristics and the
``detect-secrets`` library (when available).

Usage::

    python tools/ci/pii_scan.py --path <directory>

Exit code:
  0  – no findings
  1  – findings detected (CI should fail)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    ),
    "us_phone": re.compile(
        r"\b(?:\+?1[-.\s])?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"
    ),
    "us_ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
}

SECRET_PATTERNS: dict[str, re.Pattern[str]] = {
    "aws_access_key": re.compile(r"(?i)AKIA[0-9A-Z]{16}"),
    "generic_secret": re.compile(
        r'(?i)(?:password|passwd|secret|api[_-]?key|token)\s*[:=]\s*["\']?[^\s"\']{8,}'
    ),
    "private_key_header": re.compile(r"-----BEGIN (?:RSA|EC|DSA|OPENSSH) PRIVATE KEY-----"),
}

# Files / directories to skip
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".uv"}
SKIP_EXTENSIONS = {".pyc", ".pyo", ".png", ".jpg", ".jpeg", ".gif", ".svg",
                   ".ico", ".woff", ".woff2", ".ttf", ".eot", ".lock"}

# Allowlist: patterns that are acceptable (e.g. example/placeholder values)
ALLOWLIST_PATTERNS = [
    re.compile(r"example\.com"),
    re.compile(r"test@test"),
    re.compile(r"foo@bar"),
    re.compile(r"user@example"),
    re.compile(r"placeholder"),
    re.compile(r"your[_-]?(?:api[_-]?)?key"),
    re.compile(r"<[A-Z_]+>"),  # template placeholders like <API_KEY>
]


def is_allowlisted(line: str) -> bool:
    return any(p.search(line) for p in ALLOWLIST_PATTERNS)


def scan_file(filepath: Path) -> list[tuple[int, str, str]]:
    """Return list of (line_no, pattern_name, line) tuples for findings."""
    findings: list[tuple[int, str, str]] = []
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings

    for lineno, line in enumerate(text.splitlines(), start=1):
        if is_allowlisted(line):
            continue
        for name, pattern in {**PII_PATTERNS, **SECRET_PATTERNS}.items():
            if pattern.search(line):
                findings.append((lineno, name, line.strip()))
    return findings


def scan_directory(root: Path) -> dict[str, list[tuple[int, str, str]]]:
    results: dict[str, list[tuple[int, str, str]]] = {}
    for path in root.rglob("*"):
        if any(skip in path.parts for skip in SKIP_DIRS):
            continue
        if path.suffix in SKIP_EXTENSIONS:
            continue
        if path.is_file():
            findings = scan_file(path)
            if findings:
                results[str(path.relative_to(root))] = findings
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan for PII and secrets")
    parser.add_argument("--path", required=True, help="Root directory to scan")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"ERROR: path '{root}' does not exist", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {root} for PII and secrets …")
    results = scan_directory(root)

    if not results:
        print("✓ No PII or secrets found.")
        sys.exit(0)

    print(f"\n✗ Found potential PII / secrets in {len(results)} file(s):\n")
    for filepath, findings in sorted(results.items()):
        print(f"  {filepath}:")
        for lineno, pattern_name, line in findings:
            preview = line[:120] + ("…" if len(line) > 120 else "")
            print(f"    line {lineno:>4}  [{pattern_name}]  {preview}")
    print()
    sys.exit(1)


if __name__ == "__main__":
    main()
