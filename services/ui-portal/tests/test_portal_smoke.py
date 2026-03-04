"""Selenium smoke tests for the UI Portal.

These tests run against a live browser and require a self-hosted runner
with Chrome and chromedriver installed.

Set the PORTAL_URL environment variable to point at the portal
(default: http://localhost:8080).

NOTE: The tests are intentionally written as *smoke tests* that verify
basic navigation and page structure.  Actual login/logout flows require a
running portal instance.
"""

from __future__ import annotations

import os

import pytest

PORTAL_URL = os.environ.get("PORTAL_URL", "http://localhost:8080")
SKIP_REASON = "PORTAL_URL not set to a running instance; skipping live Selenium tests"


def portal_is_available() -> bool:
    """Return True if the portal is reachable."""
    import urllib.request
    try:
        with urllib.request.urlopen(PORTAL_URL, timeout=3):
            return True
    except Exception:
        return False


skip_if_unavailable = pytest.mark.skipif(
    not portal_is_available(),
    reason=SKIP_REASON,
)


@skip_if_unavailable
class TestPortalSmoke:
    def test_title_is_present(self, driver, portal_url):
        driver.get(portal_url)
        assert driver.title, "Page title should not be empty"

    def test_page_loads_without_js_errors(self, driver, portal_url):
        driver.get(portal_url)
        logs = driver.get_log("browser")
        severe = [e for e in logs if e.get("level") == "SEVERE"]
        assert not severe, f"Unexpected JS errors on load: {severe}"

    def test_login_page_has_form(self, driver, portal_url):
        driver.get(f"{portal_url}/login")
        # Should have at least one input element
        inputs = driver.find_elements("tag name", "input")
        assert len(inputs) >= 1, "Login page should have at least one input field"
