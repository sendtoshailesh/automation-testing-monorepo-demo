#!/usr/bin/env python3
"""
Generate PR evidence from a Markdown template and JUnit XML test result files.

Usage::

    python tools/ci/generate_pr_evidence.py \\
        --template evidence/templates/pr-evidence.md \\
        --artifacts /tmp/test-artifacts \\
        --pr 42 \\
        --sha abc1234 \\
        --output evidence/pr/pr-42.md
"""

from __future__ import annotations

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


def parse_junit(xml_path: Path) -> dict:
    """Parse a JUnit XML file and return a summary dict."""
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as exc:
        return {"error": str(exc), "tests": 0, "failures": 0, "errors": 0, "skipped": 0}

    root = tree.getroot()
    # Handle both <testsuites> and <testsuite> root elements
    suites = root.findall(".//testsuite") or [root]

    totals: dict[str, int] = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    for suite in suites:
        for key in totals:
            totals[key] += int(suite.get(key, 0))
    return totals


def collect_results(artifacts_dir: Path) -> list[dict]:
    """Walk the artifacts directory and collect JUnit XML summaries."""
    results = []
    for xml_file in sorted(artifacts_dir.rglob("*.xml")):
        summary = parse_junit(xml_file)
        rel = xml_file.relative_to(artifacts_dir)
        results.append({"file": str(rel), **summary})
    return results


def render_results_table(results: list[dict]) -> str:
    if not results:
        return "_No test result files found._\n"
    lines = [
        "| Suite | Tests | Failures | Errors | Skipped |",
        "|-------|------:|---------:|-------:|--------:|",
    ]
    for r in results:
        if "error" in r:
            lines.append(f"| {r['file']} | – | – | – | – |  _(parse error: {r['error']})_")
        else:
            passed = r["tests"] - r["failures"] - r["errors"] - r["skipped"]
            status = "✅" if r["failures"] == 0 and r["errors"] == 0 else "❌"
            lines.append(
                f"| {status} `{r['file']}` "
                f"| {r['tests']} "
                f"| {r['failures']} "
                f"| {r['errors']} "
                f"| {r['skipped']} |"
            )
    return "\n".join(lines) + "\n"


def overall_status(results: list[dict]) -> str:
    for r in results:
        if r.get("failures", 0) > 0 or r.get("errors", 0) > 0:
            return "❌ FAILED"
    return "✅ PASSED"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate PR evidence document")
    parser.add_argument("--template", required=True, help="Path to Markdown template")
    parser.add_argument("--artifacts", required=True, help="Directory containing test artifacts")
    parser.add_argument("--pr", required=True, help="Pull request number")
    parser.add_argument("--sha", required=True, help="Head commit SHA")
    parser.add_argument("--output", required=True, help="Output Markdown file path")
    args = parser.parse_args()

    template_path = Path(args.template)
    artifacts_dir = Path(args.artifacts)
    output_path = Path(args.output)

    if not template_path.exists():
        print(f"ERROR: template not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    results = collect_results(artifacts_dir) if artifacts_dir.exists() else []
    table = render_results_table(results)
    status = overall_status(results)
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    template = template_path.read_text()
    rendered = (
        template
        .replace("{{PR_NUMBER}}", args.pr)
        .replace("{{SHA}}", args.sha)
        .replace("{{TIMESTAMP}}", timestamp)
        .replace("{{OVERALL_STATUS}}", status)
        .replace("{{TEST_RESULTS_TABLE}}", table)
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered)
    print(f"PR evidence written to: {output_path}")


if __name__ == "__main__":
    main()
