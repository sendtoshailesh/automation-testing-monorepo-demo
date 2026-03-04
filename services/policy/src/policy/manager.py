"""Core policy management logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import uuid


class PolicyStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class Policy:
    holder_name: str
    coverage_amount: float
    status: PolicyStatus = PolicyStatus.DRAFT
    policy_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    notes: Optional[str] = None


def create_policy(holder_name: str, coverage_amount: float) -> Policy:
    """Create a new policy in DRAFT status.

    Args:
        holder_name: Name of the policy holder.
        coverage_amount: Coverage amount in dollars (must be > 0).

    Returns:
        A new Policy instance.

    Raises:
        ValueError: If holder_name is blank or coverage_amount <= 0.
    """
    if not holder_name or not holder_name.strip():
        raise ValueError("holder_name must not be blank")
    if coverage_amount <= 0:
        raise ValueError(f"coverage_amount must be > 0, got {coverage_amount}")
    return Policy(holder_name=holder_name.strip(), coverage_amount=coverage_amount)


def activate_policy(policy: Policy) -> Policy:
    """Transition a DRAFT policy to ACTIVE.

    Raises:
        ValueError: If the policy is not in DRAFT status.
    """
    if policy.status != PolicyStatus.DRAFT:
        raise ValueError(
            f"Only DRAFT policies can be activated; current status: {policy.status}"
        )
    policy.status = PolicyStatus.ACTIVE
    return policy


def cancel_policy(policy: Policy, reason: str = "") -> Policy:
    """Cancel an ACTIVE or DRAFT policy.

    Raises:
        ValueError: If the policy is already CANCELLED or EXPIRED.
    """
    if policy.status in (PolicyStatus.CANCELLED, PolicyStatus.EXPIRED):
        raise ValueError(
            f"Cannot cancel a policy with status {policy.status}"
        )
    policy.status = PolicyStatus.CANCELLED
    if reason:
        policy.notes = reason
    return policy
