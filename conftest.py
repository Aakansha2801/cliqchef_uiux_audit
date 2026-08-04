"""
Pytest configuration and fixtures for CliqChef.ai UI/UX audit.
Provides page objects, helpers, and common setup/teardown.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from helpers import (
    AccessibilityHelper,
    ContentHelper,
    PerformanceHelper,
    UXHelper,
    VisualHelper,
)
from pages import BasePage, HomePage


# ─── Page Object Fixtures ───

@pytest.fixture
def base_page(page: Page) -> BasePage:
    """Provide a BasePage instance with all helpers attached."""
    return BasePage(page)


@pytest.fixture
def home_page(page: Page) -> HomePage:
    """Provide a HomePage instance for the CliqChef.ai landing page."""
    return HomePage(page)


# ─── Helper Fixtures ───

@pytest.fixture
def a11y(page: Page) -> AccessibilityHelper:
    """Provide an AccessibilityHelper for the current page."""
    return AccessibilityHelper(page)


@pytest.fixture
def perf(page: Page) -> PerformanceHelper:
    """Provide a PerformanceHelper for the current page."""
    return PerformanceHelper(page)


@pytest.fixture
def visual(page: Page) -> VisualHelper:
    """Provide a VisualHelper for the current page."""
    return VisualHelper(page)


@pytest.fixture
def ux(page: Page) -> UXHelper:
    """Provide a UXHelper for the current page."""
    return UXHelper(page)


@pytest.fixture
def content(page: Page) -> ContentHelper:
    """Provide a ContentHelper for the current page."""
    return ContentHelper(page)


# ─── Common Setup Fixture ───

@pytest.fixture(autouse=True)
def accept_cookies(home_page: HomePage):
    """Auto-accept cookie banners before each test (if present)."""
    yield
    # Teardown: no-op for now


# ─── Viewport Parametrize Fixtures ───

DESKTOP_VIEWPORTS = [
    pytest.param({"width": 1280, "height": 720}, id="desktop-1280x720"),
    pytest.param({"width": 1440, "height": 900}, id="desktop-1440x900"),
    pytest.param({"width": 1920, "height": 1080}, id="desktop-1920x1080"),
]

MOBILE_VIEWPORTS = [
    pytest.param({"width": 320, "height": 568}, id="mobile-320x568"),
    pytest.param({"width": 375, "height": 667}, id="mobile-375x667"),
    pytest.param({"width": 428, "height": 926}, id="mobile-428x926"),
]

TABLET_VIEWPORTS = [
    pytest.param({"width": 768, "height": 1024}, id="tablet-768x1024"),
    pytest.param({"width": 1024, "height": 768}, id="tablet-1024x768"),
]


# ─── Custom Markers ───

def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers for UI/UX test categories."""
    markers = [
        "smoke: smoke tests (critical path, fast)",
        "critical: critical business-flow tests",
        "accessibility: WCAG 2.1 accessibility tests",
        "visual: visual regression & snapshot tests",
        "responsive: responsive design / viewport tests",
        "performance: performance & Core Web Vitals tests",
        "navigation: navigation & routing tests",
        "forms: form interaction & validation tests",
        "content: content quality & SEO tests",
        "ux: UX interaction & usability tests",
        "mobile: mobile-specific tests",
        "desktop: desktop-specific tests",
        "slow: slow-running tests (>10s)",
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)
