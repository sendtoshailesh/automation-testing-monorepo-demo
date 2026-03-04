"""Unit tests for the policy manager."""

import pytest

from policy.manager import (
    Policy,
    PolicyStatus,
    create_policy,
    activate_policy,
    cancel_policy,
)


class TestCreatePolicy:
    def test_creates_draft_policy(self):
        policy = create_policy("Alice Smith", 50000.0)
        assert policy.holder_name == "Alice Smith"
        assert policy.coverage_amount == 50000.0
        assert policy.status == PolicyStatus.DRAFT
        assert policy.policy_id  # non-empty UUID

    def test_strips_whitespace_from_holder_name(self):
        policy = create_policy("  Bob Jones  ", 10000.0)
        assert policy.holder_name == "Bob Jones"

    def test_blank_holder_name_raises(self):
        with pytest.raises(ValueError, match="holder_name"):
            create_policy("   ", 10000.0)

    def test_zero_coverage_raises(self):
        with pytest.raises(ValueError, match="coverage_amount"):
            create_policy("Alice", 0)

    def test_negative_coverage_raises(self):
        with pytest.raises(ValueError, match="coverage_amount"):
            create_policy("Alice", -100)


class TestActivatePolicy:
    def test_activates_draft_policy(self):
        policy = create_policy("Alice", 50000.0)
        activated = activate_policy(policy)
        assert activated.status == PolicyStatus.ACTIVE

    def test_cannot_activate_non_draft(self):
        policy = create_policy("Alice", 50000.0)
        activate_policy(policy)
        with pytest.raises(ValueError, match="Only DRAFT"):
            activate_policy(policy)


class TestCancelPolicy:
    def test_cancels_active_policy(self):
        policy = create_policy("Alice", 50000.0)
        activate_policy(policy)
        cancelled = cancel_policy(policy, "Customer request")
        assert cancelled.status == PolicyStatus.CANCELLED
        assert cancelled.notes == "Customer request"

    def test_cancels_draft_policy(self):
        policy = create_policy("Alice", 50000.0)
        cancel_policy(policy)
        assert policy.status == PolicyStatus.CANCELLED

    def test_cannot_cancel_already_cancelled(self):
        policy = create_policy("Alice", 50000.0)
        cancel_policy(policy)
        with pytest.raises(ValueError, match="Cannot cancel"):
            cancel_policy(policy)
