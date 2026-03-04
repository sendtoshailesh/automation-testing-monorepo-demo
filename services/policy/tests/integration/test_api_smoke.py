"""Integration smoke tests for the policy service API.

Requires the service to be running.
Set POLICY_URL env var (default: http://localhost:8002).
"""

import os

import pytest
import requests

BASE_URL = os.environ.get("POLICY_URL", "http://localhost:8002")


@pytest.fixture(scope="module")
def service_url():
    return BASE_URL.rstrip("/")


class TestHealthEndpoint:
    def test_health_returns_ok(self, service_url):
        resp = requests.get(f"{service_url}/health", timeout=5)
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestPolicyLifecycle:
    def test_create_and_activate_policy(self, service_url):
        # Create
        payload = {"holder_name": "Integration User", "coverage_amount": 75000}
        resp = requests.post(f"{service_url}/policies", json=payload, timeout=5)
        assert resp.status_code == 201
        policy = resp.json()
        assert policy["status"] == "draft"
        pid = policy["policy_id"]

        # Activate
        resp = requests.post(f"{service_url}/policies/{pid}/activate", timeout=5)
        assert resp.status_code == 200
        assert resp.json()["status"] == "active"

    def test_cancel_policy(self, service_url):
        payload = {"holder_name": "Cancel User", "coverage_amount": 10000}
        resp = requests.post(f"{service_url}/policies", json=payload, timeout=5)
        pid = resp.json()["policy_id"]

        resp = requests.post(
            f"{service_url}/policies/{pid}/cancel",
            json={"reason": "Test cancellation"},
            timeout=5,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_get_nonexistent_policy_returns_404(self, service_url):
        resp = requests.get(f"{service_url}/policies/nonexistent-id", timeout=5)
        assert resp.status_code == 404
