"""Pytest fixtures for Selenium tests."""

from __future__ import annotations

import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

PORTAL_URL = os.environ.get("PORTAL_URL", "http://localhost:8080")


@pytest.fixture(scope="session")
def portal_url() -> str:
    return PORTAL_URL.rstrip("/")


@pytest.fixture(scope="function")
def driver():
    """Headless Chrome WebDriver fixture."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")

    # Use webdriver-manager if chromedriver is not on PATH
    try:
        drv = webdriver.Chrome(options=options)
    except Exception:
        from webdriver_manager.chrome import ChromeDriverManager
        drv = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )

    yield drv
    drv.quit()
