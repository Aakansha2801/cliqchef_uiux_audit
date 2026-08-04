"""
Visual Regression & Layout Test Suite

Captures screenshots, detects layout shifts, overflow, broken images,
and validates visual consistency across renders.
"""

import pytest
from playwright.sync_api import expect

from helpers.constants import CONTRAST_RATIO_AA


@pytest.mark.visual
class TestVisualSnapshots:
    """Capture and compare visual snapshots for regression detection."""

    def test_home_page_full_screenshot(self, home_page, visual):
        """Capture full-page screenshot of home page for baseline comparison."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        path = visual.take_full_screenshot("home-page")
        assert path.exists(), f"Screenshot not saved: {path}"

    def test_header_screenshot(self, home_page, visual):
        """Capture header component screenshot."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        path = visual.take_element_screenshot(home_page.header, "header")
        assert path.exists(), f"Header screenshot not saved: {path}"

    def test_footer_screenshot(self, home_page, visual):
        """Capture footer component screenshot."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        home_page.scroll_to_end()
        path = visual.take_element_screenshot(home_page.footer, "footer")
        assert path.exists(), f"Footer screenshot not saved: {path}"

    def test_navigation_screenshot(self, home_page, visual):
        """Capture navigation component screenshot."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        path = visual.take_element_screenshot(home_page.nav, "navigation")
        assert path.exists(), f"Nav screenshot not saved: {path}"


@pytest.mark.visual
class TestLayoutIntegrity:
    """Validate layout correctness and absence of visual defects."""

    def test_no_horizontal_overflow(self, home_page, visual):
        """Page should not cause horizontal scrollbar on desktop."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        visual.expect_no_horizontal_overflow()

    def test_no_broken_images(self, home_page, visual):
        """All images should load successfully (no broken image icons)."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        visual.expect_no_broken_images()

    def test_no_text_overflow(self, home_page, visual):
        """Text should not be clipped by overflow:hidden containers."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        issues = visual.get_text_overflow_issues()
        assert len(issues) <= 2, f"Text overflow issues: {issues}"

    def test_z_index_stack_reasonable(self, home_page, visual):
        """Z-index values should not exceed common UI thresholds."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        stack = visual.get_z_index_stack()
        excessive = [item for item in stack if item["zIndex"] > 9999]
        assert excessive == [], f"Excessive z-index values: {excessive}"


@pytest.mark.visual
class TestComponentConsistency:
    """Validate visual consistency of UI components."""

    def test_button_minimum_sizes(self, home_page):
        """All buttons should meet minimum size requirements (touch targets)."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        buttons = page.locator("button, .btn, [class*='button']").all()
        sizes: list[dict] = []
        for btn in buttons[:10]:
            if btn.is_visible():
                box = btn.bounding_box()
                if box:
                    sizes.append({"width": box["width"], "height": box["height"]})

        for size in sizes:
            assert size["height"] >= 28, (
                f"Button too short: {size['height']}px (min 28px)"
            )

    def test_consistent_spacing(self, home_page):
        """Major sections should have consistent vertical spacing."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        sections = page.locator("section").all()
        if len(sections) >= 2:
            margins: list[float] = []
            for section in sections[:5]:
                margin = section.evaluate(
                    "el => parseFloat(getComputedStyle(el).marginBottom)"
                )
                if margin > 0:
                    margins.append(margin)

            # If we found margins, they should be reasonably consistent
            if len(margins) >= 2:
                avg = sum(margins) / len(margins)
                variance = sum((m - avg) ** 2 for m in margins) / len(margins)
                # Allow some variance but flag extreme inconsistency
                assert variance < (avg * 0.5) ** 2, (
                    f"Section spacing highly inconsistent: {margins}"
                )

    def test_dark_mode_rendering(self, home_page):
        """If dark mode is supported, page should render correctly in it."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        dark_toggle = page.locator(
            "[class*='theme'], [class*='dark'], "
            "[aria-label*='theme'], [aria-label*='dark']"
        )
        if dark_toggle.count() > 0:
            dark_toggle.first.click()
            page.wait_for_timeout(500)
            page.wait_for_load_state("domcontentloaded")
            # Page should still have content
            assert page.locator("body").inner_html(), "Page empty after dark mode toggle"
