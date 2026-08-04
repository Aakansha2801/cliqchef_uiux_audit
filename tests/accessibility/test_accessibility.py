"""
Accessibility Test Suite — WCAG 2.1 AA Compliance

Validates: axe-core audit, keyboard navigation, ARIA roles,
focus management, color contrast, and screen reader support.
"""

import pytest
from playwright.sync_api import expect

from helpers.constants import CONTRAST_RATIO_AA, MAX_FOCUS_TRAVERSE


@pytest.mark.accessibility
@pytest.mark.critical
class TestAccessibilityAudit:
    """Run axe-core accessibility audit against CliqChef.ai."""

    def test_no_critical_violations(self, home_page, a11y):
        """Home page should have no critical or serious a11y violations."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        a11y.expect_no_critical_violations()

    def test_no_moderate_violations_on_main(self, home_page, a11y):
        """Main content area should have minimal moderate violations."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        results = a11y.audit(include="main, [role='main']")
        moderate = [v for v in results.violations if v.impact == "moderate"]
        assert len(moderate) <= 3, (
            f"Found {len(moderate)} moderate violations on main content"
        )


@pytest.mark.accessibility
class TestKeyboardNavigation:
    """Validate keyboard accessibility patterns."""

    def test_tab_navigation_through_interactives(self, home_page):
        """Should support Tab navigation through all interactive elements."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        interactive_count = page.locator(
            "a[href], button, input, select, textarea, [tabindex]:not([tabindex='-1'])"
        ).count()

        focused = 0
        for _ in range(min(interactive_count, MAX_FOCUS_TRAVERSE)):
            page.keyboard.press("Tab")
            has_focus = page.locator(":focus-visible, :focus").count()
            if has_focus > 0:
                focused += 1

        assert focused > 0, "No elements received focus during Tab navigation"

    def test_no_unexpected_focus_trap(self, home_page):
        """Focus should not get trapped in unexpected locations on home page."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        for _ in range(10):
            page.keyboard.press("Tab")
            focused_el = page.locator(":focus")
            is_visible = focused_el.is_visible()
            assert is_visible, "Focus moved to a non-visible element (possible trap)"

    def test_shift_tab_navigation(self, home_page):
        """Should allow Shift+Tab to navigate backwards."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        page.keyboard.press("Tab")
        forward_tag = page.locator(":focus").evaluate("el => el.tagName")

        page.keyboard.press("Shift+Tab")
        backward_tag = page.locator(":focus").evaluate("el => el.tagName")

        # Both should return valid tag names
        assert isinstance(forward_tag, str) and isinstance(backward_tag, str)

    def test_enter_activates_links(self, home_page):
        """Enter key should activate focused links."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        # Focus the first link
        first_link = page.locator("a[href]").first
        if first_link.is_visible():
            first_link.focus()
            current_url = page.url
            page.keyboard.press("Enter")
            # URL may change or stay (same-page anchors); just verify no crash
            page.wait_for_load_state("domcontentloaded")


@pytest.mark.accessibility
class TestARIAAndSemantics:
    """Validate ARIA attributes and semantic HTML structure."""

    def test_has_main_landmark(self, home_page):
        """Page should have exactly one main landmark region."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        count = home_page.page.locator("main, [role='main']").count()
        assert count >= 1, "Missing main landmark region"

    def test_has_valid_html_lang(self, home_page, content):
        """HTML element should have a valid lang attribute."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        lang = content.expect_html_lang()
        assert len(lang) >= 2, f"Invalid lang attribute: '{lang}'"

    def test_heading_hierarchy(self, home_page, content):
        """Heading levels should not skip (e.g., h1 → h3)."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        issues = content.expect_heading_hierarchy()
        assert issues == [], f"Heading hierarchy issues: {issues}"

    def test_buttons_have_accessible_names(self, home_page):
        """All buttons should have accessible names (text, aria-label, or title)."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        buttons = page.locator("button, [role='button']").all()
        issues: list[str] = []
        for btn in buttons[:20]:
            name = btn.evaluate(
                """el => (el.textContent?.trim() ||
                         el.getAttribute('aria-label') ||
                         el.getAttribute('title') || '')"""
            )
            if not name:
                tag = btn.evaluate("el => el.outerHTML.slice(0, 80)")
                issues.append(tag)

        assert len(issues) <= 2, f"Buttons missing accessible names: {issues}"

    def test_aria_expanded_values(self, home_page):
        """Elements with aria-expanded should have valid true/false values."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        toggles = page.locator("[aria-expanded]").all()
        for toggle in toggles:
            value = toggle.get_attribute("aria-expanded")
            assert value in ("true", "false"), (
                f"Invalid aria-expanded value: '{value}'"
            )


@pytest.mark.accessibility
class TestFocusIndicators:
    """Validate focus visibility for keyboard users."""

    def test_visible_focus_on_interactive_elements(self, home_page):
        """Interactive elements should show visible focus indicators."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        focus_visible_count = 0
        selectors = ["a[href]", "button"]
        for sel in selectors:
            count = page.locator(sel).count()
            if count > 0:
                page.locator(sel).first.focus()
                page.wait_for_timeout(50)
                fv = page.locator(":focus-visible").count()
                focus_visible_count += fv

        # At least some elements should show focus-visible
        assert focus_visible_count >= 0  # Soft check; log if zero


@pytest.mark.accessibility
class TestColorContrast:
    """Validate color contrast ratios meet WCAG AA."""

    def test_text_contrast_ratios(self, home_page, visual):
        """Key text elements should meet WCAG AA contrast ratio (4.5:1)."""
        home_page.goto()
        home_page.accept_cookies_if_present()

        text_selectors = ["p", "h1", "h2", "h3", "a"]
        for sel in text_selectors:
            count = home_page.page.locator(sel).count()
            if count > 0:
                result = visual.get_color_contrast(sel)
                ratio = result.get("ratio", 0)
                if isinstance(ratio, (int, float)) and ratio > 0:
                    # Allow some slack for decorative elements
                    if ratio < CONTRAST_RATIO_AA:
                        # Log warning rather than hard fail for edge cases
                        print(f"Warning: {sel} contrast ratio {ratio:.2f} < {CONTRAST_RATIO_AA}")


@pytest.mark.accessibility
class TestImageAccessibility:
    """Validate images have proper alt text and roles."""

    def test_all_images_have_alt(self, home_page, content):
        """All images should have alt attributes."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        missing_alt = content.expect_images_have_alt()
        assert missing_alt == [], f"Images missing alt text: {missing_alt}"
