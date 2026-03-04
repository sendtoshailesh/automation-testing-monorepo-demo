#!/usr/bin/env python3
"""
Quarantine manager for flaky tests.

Reads / writes a ``quarantine.json`` file that records tests which have been
marked as flaky so they can be skipped in the main CI run and tracked for
eventual fixing.

Usage::

    # List quarantined tests
    python tools/ci/quarantine.py list

    # Add a test to quarantine
    python tools/ci/quarantine.py add --service pricing \\
        --test "tests/unit/test_calculator.py::test_edge_case" \\
        --reason "Flaky: intermittent timeout" \\
        --issue "https://github.com/org/repo/issues/42"

    # Remove a test from quarantine (once fixed)
    python tools/ci/quarantine.py remove --service pricing \\
        --test "tests/unit/test_calculator.py::test_edge_case"

    # Generate a pytest ``--deselect`` argument string for a service
    python tools/ci/quarantine.py deselect --service pricing
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

QUARANTINE_FILE = Path(__file__).parent.parent.parent / "quarantine.json"


def load_quarantine() -> dict:
    if QUARANTINE_FILE.exists():
        return json.loads(QUARANTINE_FILE.read_text())
    return {}


def save_quarantine(data: dict) -> None:
    QUARANTINE_FILE.write_text(json.dumps(data, indent=2) + "\n")


def cmd_list(args: argparse.Namespace) -> None:
    data = load_quarantine()
    if not data:
        print("No tests are currently quarantined.")
        return
    for service, tests in sorted(data.items()):
        print(f"\nService: {service}")
        for entry in tests:
            print(f"  {entry['test']}")
            print(f"    reason : {entry.get('reason', '-')}")
            print(f"    issue  : {entry.get('issue', '-')}")
            print(f"    added  : {entry.get('added', '-')}")


def cmd_add(args: argparse.Namespace) -> None:
    data = load_quarantine()
    service_list: list[dict] = data.setdefault(args.service, [])
    existing = [e for e in service_list if e["test"] == args.test]
    if existing:
        print(f"Test already quarantined: {args.test}")
        return
    entry: dict = {
        "test": args.test,
        "reason": args.reason or "",
        "issue": args.issue or "",
        "added": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"),
    }
    service_list.append(entry)
    save_quarantine(data)
    print(f"Quarantined: {args.test}")


def cmd_remove(args: argparse.Namespace) -> None:
    data = load_quarantine()
    if args.service not in data:
        print(f"No quarantine entries for service: {args.service}")
        sys.exit(1)
    before = len(data[args.service])
    data[args.service] = [e for e in data[args.service] if e["test"] != args.test]
    if len(data[args.service]) == before:
        print(f"Test not found in quarantine: {args.test}")
        sys.exit(1)
    if not data[args.service]:
        del data[args.service]
    save_quarantine(data)
    print(f"Removed from quarantine: {args.test}")


def cmd_deselect(args: argparse.Namespace) -> None:
    data = load_quarantine()
    tests = data.get(args.service, [])
    flags = " ".join(f"--deselect {e['test']}" for e in tests)
    print(flags)


def main() -> None:
    parser = argparse.ArgumentParser(description="Quarantine manager for flaky tests")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List quarantined tests")

    add_p = sub.add_parser("add", help="Add a test to quarantine")
    add_p.add_argument("--service", required=True)
    add_p.add_argument("--test", required=True)
    add_p.add_argument("--reason", default="")
    add_p.add_argument("--issue", default="")

    rm_p = sub.add_parser("remove", help="Remove a test from quarantine")
    rm_p.add_argument("--service", required=True)
    rm_p.add_argument("--test", required=True)

    ds_p = sub.add_parser("deselect", help="Print --deselect flags for pytest")
    ds_p.add_argument("--service", required=True)

    args = parser.parse_args()
    dispatch = {"list": cmd_list, "add": cmd_add, "remove": cmd_remove, "deselect": cmd_deselect}
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
