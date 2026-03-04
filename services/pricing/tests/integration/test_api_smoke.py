"""Integration smoke tests for the pricing service API.

These tests require the service to be running (via docker-compose or uvicorn).
The base URL is read from the PRICING_URL environment variable (default: http://localhost:8001).
"""

import os

import pytest
import requests

BASE_URL = os.environ.get("PRICING_URL", "http://localhost:8001")


@pytest.fixture(scope="module")
def service_url():
    return BASE_URL.rstrip("/")


class TestHealthEndpoint:
    def test_health_returns_ok(self, service_url):
        resp = requests.get(f"{service_url}/health", timeout=5)
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestPremiumEndpoint:
    def test_calculate_low_risk_premium(self, service_url):
        payload = {"age": 30, "risk_level": "low", "discount_pct": 0}
        resp = requests.post(f"{service_url}/premium", json=payload, timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert data["premium"] == pytest.approx(145.0)
        assert data["discounted_premium"] == pytest.approx(145.0)
        assert data["risk_level"] == "low"

    def test_calculate_with_discount(self, service_url):
        payload = {"age": 30, "risk_level": "medium", "discount_pct": 10}
        resp = requests.post(f"{service_url}/premium", json=payload, timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert data["discounted_premium"] < data["premium"]

    def test_invalid_risk_level_returns_422(self, service_url):
        payload = {"age": 30, "risk_level": "unknown"}
        resp = requests.post(f"{service_url}/premium", json=payload, timeout=5)
        assert resp.status_code == 422
