#!/usr/bin/env python3
"""
Detect which services/* directories changed between two git SHAs and emit a
GitHub Actions matrix JSON string + a boolean flag for the ``has_services``
output variable.

Usage (called from the CI workflow)::

    python tools/ci/changed_services.py --base <base_sha> --head <head_sha>

Outputs (written to $GITHUB_OUTPUT when available, otherwise stdout)::

    matrix={"include":[{"service":"pricing"},{"service":"policy"}]}
    has_services=true
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys


SERVICES_DIR = "services"


def get_changed_services(base_sha: str, head_sha: str) -> list[str]:
    """Return the list of service names that contain changes between the two SHAs."""
    result = subprocess.run(
        ["git", "diff", "--name-only", base_sha, head_sha],
        capture_output=True,
        text=True,
        check=True,
    )
    changed_files = result.stdout.splitlines()

    services_root = os.path.join(os.getcwd(), SERVICES_DIR)
    available_services = {
        name
        for name in os.listdir(services_root)
        if os.path.isdir(os.path.join(services_root, name))
    } if os.path.isdir(services_root) else set()

    changed = set()
    for filepath in changed_files:
        parts = filepath.split("/")
        if len(parts) >= 2 and parts[0] == SERVICES_DIR and parts[1] in available_services:
            changed.add(parts[1])

    return sorted(changed)


def write_output(key: str, value: str) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as fh:
            fh.write(f"{key}={value}\n")
    else:
        print(f"{key}={value}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect changed services for CI matrix")
    parser.add_argument("--base", required=True, help="Base commit SHA")
    parser.add_argument("--head", required=True, help="Head commit SHA")
    args = parser.parse_args()

    try:
        changed = get_changed_services(args.base, args.head)
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: git diff failed: {exc.stderr}", file=sys.stderr)
        sys.exit(1)

    if changed:
        matrix = json.dumps({"include": [{"service": s} for s in changed]})
        has_services = "true"
    else:
        # Provide a dummy entry so the matrix job doesn't fail with an empty list.
        matrix = json.dumps({"include": [{"service": "__none__"}]})
        has_services = "false"

    write_output("matrix", matrix)
    write_output("has_services", has_services)
    print(f"Changed services: {changed if changed else '(none)'}")


if __name__ == "__main__":
    main()
