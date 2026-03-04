#!/usr/bin/env python3
"""
Shared session state store for the multi-agent testing pipeline.

Each agent (Test Orchestrator, Test Design, Test Execution,
Validation & Assertion, Failure Analysis, Reporting & Feedback) reads and
writes a single ``agent-sessions.json`` file in the repository root.

Usage::

    # Start a new session (called by the Orchestrator)
    python tools/agents/session_state.py new \
        --trigger pr \
        --services claims-api pricing \
        --pr 42 \
        --sha abc1234

    # Write a block to an existing session
    python tools/agents/session_state.py write \
        --session <uuid> \
        --key test_execution \
        --data '{"service":"claims-api","exit_code":0,"tests_run":9}'

    # Read a block from a session
    python tools/agents/session_state.py read \
        --session <uuid> \
        --key validation

    # List all sessions (newest first)
    python tools/agents/session_state.py list

    # Mark a session complete
    python tools/agents/session_state.py complete \
        --session <uuid> \
        --status passed
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_default_state_file = Path(__file__).parent.parent.parent / "agent-sessions.json"
STATE_FILE = Path(os.environ.get("AGENT_SESSION_FILE", str(_default_state_file)))


# ── Helpers ──────────────────────────────────────────────────────────────────


def _now() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load() -> dict[str, Any]:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def _save(data: dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(data, indent=2) + "\n")


def _require_session(data: dict[str, Any], session_id: str) -> dict[str, Any]:
    if session_id not in data:
        print(f"ERROR: session not found: {session_id}", file=sys.stderr)
        sys.exit(1)
    return data[session_id]


# ── Commands ─────────────────────────────────────────────────────────────────


def cmd_new(args: argparse.Namespace) -> None:
    data = _load()
    session_id = str(uuid.uuid4())
    session: dict[str, Any] = {
        "session_id": session_id,
        "created_at": _now(),
        "updated_at": _now(),
        "status": "in_progress",
        "trigger": args.trigger,
        "services": args.services,
        "pr": args.pr or None,
        "sha": args.sha or None,
        "run_id": args.run_id or None,
        "blocks": {},
    }
    data[session_id] = session
    _save(data)
    # Print the session ID so the caller can pass it to sub-agents.
    print(session_id)


def cmd_write(args: argparse.Namespace) -> None:
    data = _load()
    session = _require_session(data, args.session)

    try:
        block = json.loads(args.data)
    except json.JSONDecodeError as exc:
        print(f"ERROR: --data is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    key = args.key
    existing = session["blocks"].get(key)
    session["updated_at"] = _now()
    if isinstance(existing, list):
        session["blocks"][key] = existing + [block]
    elif existing is not None:
        # Upgrade scalar/dict value to list so multiple writes accumulate.
        session["blocks"][key] = [existing, block]
    else:
        session["blocks"][key] = block

    _save(data)
    print(f"Written block '{key}' to session {args.session}")


def cmd_read(args: argparse.Namespace) -> None:
    data = _load()
    session = _require_session(data, args.session)
    key = args.key
    if key:
        block = session["blocks"].get(key)
        if block is None:
            print(f"Block '{key}' not found in session {args.session}", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(block, indent=2))
    else:
        print(json.dumps(session, indent=2))


def cmd_list(_args: argparse.Namespace) -> None:
    data = _load()
    if not data:
        print("No sessions found.")
        return
    sessions = sorted(data.values(), key=lambda s: s["created_at"], reverse=True)
    for s in sessions:
        svc_str = ", ".join(s.get("services") or [])
        print(
            f"{s['session_id']}  "
            f"{s['created_at']}  "
            f"trigger={s['trigger']}  "
            f"status={s['status']}  "
            f"services=[{svc_str}]"
        )


def cmd_complete(args: argparse.Namespace) -> None:
    data = _load()
    session = _require_session(data, args.session)
    session["status"] = args.status
    session["completed_at"] = _now()
    session["updated_at"] = _now()
    _save(data)
    print(f"Session {args.session} marked {args.status}")


# ── CLI ───────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agent session state store for the testing pipeline"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # new
    new_p = sub.add_parser("new", help="Create a new session and print its ID")
    new_p.add_argument("--trigger", required=True,
                       choices=["pr", "nightly", "manual", "docs"],
                       help="What triggered this session")
    new_p.add_argument("--services", nargs="+", required=True,
                       help="Services in scope for this session")
    new_p.add_argument("--pr", default="", help="Pull request number (for PR triggers)")
    new_p.add_argument("--sha", default="", help="Head commit SHA")
    new_p.add_argument("--run-id", default="", help="GitHub Actions run ID")

    # write
    write_p = sub.add_parser("write", help="Write a JSON block to a session")
    write_p.add_argument("--session", required=True, help="Session ID")
    write_p.add_argument("--key", required=True,
                         help="Block name (e.g. test_execution, validation, failure_analysis)")
    write_p.add_argument("--data", required=True, help="JSON string to store")

    # read
    read_p = sub.add_parser("read", help="Read a block (or the full session) as JSON")
    read_p.add_argument("--session", required=True, help="Session ID")
    read_p.add_argument("--key", default="",
                        help="Block name; omit to read the full session")

    # list
    sub.add_parser("list", help="List all sessions (newest first)")

    # complete
    complete_p = sub.add_parser("complete", help="Mark a session as complete")
    complete_p.add_argument("--session", required=True, help="Session ID")
    complete_p.add_argument("--status", required=True,
                            choices=["passed", "failed", "cancelled"])

    args = parser.parse_args()
    dispatch = {
        "new": cmd_new,
        "write": cmd_write,
        "read": cmd_read,
        "list": cmd_list,
        "complete": cmd_complete,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
