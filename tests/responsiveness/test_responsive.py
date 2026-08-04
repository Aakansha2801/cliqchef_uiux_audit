"""
Responsive Design Test Suite

Tests the website across multiple viewport sizes to ensure
responsive design works correctly at all breakpoints.
"""

import pytest

from helpers.constants import VIEWPORTS


@pytest.mark.responsive
class TestResponsiveViewports:
    """Validate layout at each viewport breakpoint."""

    @pytest.mark.parametrize("viewport_key", list(VIEWPORTS.keys()))
    def test_no_horizontal_overflow_at_viewport(self, page, base_page, visual, viewport_key):
        """Page should not overflow horizontally at any viewport."""
        vp = VIEWPORTS[viewport_key]
        page.set_viewport_size({"width": vp.width, "height": vp.height})
        base_page.goto()
        base_page.accept_cookies_if_present()
        visual.expect_no_horizontal_overflow()

    @pytest.mark.parametrize("viewport_key", list(VIEWPORTS.keys()))
    def test_navigation_accessible_at_viewport(self, page, base_page, viewport_key):
        """Navigation should be accessible (visible or hamburger) at every viewport."""
        vp = VIEWPORTS[viewport_key]
        page.set_viewport_size({"width": vp.width, "height": vp.height})
        base_page.goto()
        base_page.accept_cookies_if_present()

        nav_visible = base_page.nav.is_visible()
        hamburger_visible = page.locator(
            "[class*='hamburger'], [class*='menu-toggle'], [aria-label*='menu']"
        ).is_visible()

        assert nav_visible or hamburger_visible, (
            f"Neither nav nor hamburger visible at {vp.label}"
        )

    @pytest.mark.parametrize("viewport_key", list(VIEWPORTS.keys()))
    def test_readable_font_size_at_viewport(self, page, base_page, viewport_key):
        """Text should be readable (≥12px) at every viewport."""
        vp = VIEWPORTS[viewport_key]
        page.set_viewport_size({"width": vp.width, "height": vp.height})
        base_page.goto()
        base_page.accept_cookies_if_present()

        min_size: float = page.evaluate(
            """() => {
                const els = document.querySelectorAll('p, span, a, label, li');
                let min = Infinity;
                els.forEach(el => {
                    const size = parseFloat(getComputedStyle(el).fontSize);
                    if (size > 0 && size < min) min = size;
                });
                return min;
            }"""
        )
        assert min_size >= 12, f"Font size {min_size}px too small at {vp.label}"

    @pytest.mark.parametrize("viewport_key", list(VIEWPORTS.keys()))
    def test_main_content_visible_at_viewport(self, page, base_page, viewport_key):
        """Main content should be visible at all viewports."""
        vp = VIEWPORTS[viewport_key]
        page.set_viewport_size({"width": vp.width, "height": vp.height})
        base_page.goto()
        base_page.accept_cookies_if_present()

        from playwright.sync_api import expect
        expect(base_page.main_content).to_be_visible()


@pytest.mark.responsive
@pytest.mark.mobile
class TestMobileSpecific:
    """Mobile-specific responsive behavior tests."""

    def test_touch_target_sizes_mobile(self, page, base_page):
        """Interactive elements should meet 44×44px touch target minimum on mobile."""
        page.set_viewport_size({"width": 375, "height": 667})
        base_page.goto()
        base_page.accept_cookies_if_present()

        small_targets: list[str] = page.evaluate(
            """() => {
                const interactives = document.querySelectorAll(
                    'a, button, input, select, textarea, [role="button"]'
                );
                const small = [];
                interactives.forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (rect.width < 44 || rect.height < 44)
                        small.push(el.tagName + ' (' + Math.round(rect.width) + 'x' + Math.round(rect.height) + ')');
                });
                return small;
            }"""
        )
        # Allow small inline text links on mobile
        assert len(small_targets) <= 5, (
            f"Too many undersized touch targets on mobile: {small_targets}"
        )

    def test_no_pinch_zoom_required(self, page, base_page, content):
        """Page should not require pinch-to-zoom (proper viewport meta)."""
        page.set_viewport_size({"width": 375, "height": 667})
        base_page.goto()
        base_page.accept_cookies_if_present()
        content.expect_viewport_meta()

    def test_mobile_menu_toggle(self, page, base_page):
        """Mobile menu toggle should open and close navigation."""
        page.set_viewport_size({"width": 375, "height": 667})
        base_page.goto()
        base_page.accept_cookies_if_present()

        hamburger = page.locator(
            "[class*='hamburger'], [class*='menu-toggle'], [aria-label*='menu']"
        )
        if hamburger.count() > 0 and hamburger.first.is_visible():
            hamburger.first.click()
            page.wait_for_timeout(300)
            # Nav should become visible
            from playwright.sync_api import expect
            expect(base_page.nav).to_be_visible(timeout=1000)

            # Close it
            hamburger.first.click()
            page.wait_for_timeout(300)


@pytest.mark.responsive
@pytest.mark.desktop
class TestDesktopSpecific:
    """Desktop-specific responsive behavior tests."""

    def test_full_navigation_visible_desktop(self, page, base_page):
        """Full navigation links should be visible on desktop (no hamburger)."""
        page.set_viewport_size({"width": 1280, "height": 720})
        base_page.goto()
        base_page.accept_cookies_if_present()

        from playwright.sync_api import expect
        expect(base_page.nav).to_be_visible()

    def test_multi_column_layout_desktop(self, page, base_page):
        """Desktop layout may use multi-column sections."""
        page.set_viewport_size({"width": 1280, "height": 720})
        base_page.goto()
        base_page.accept_cookies_if_present()

        sections = page.locator("section").all()
        multi_column_found = False
        for section in sections[:5]:
            if section.is_visible():
                cols = section.evaluate(
                    """el => {
                        const style = getComputedStyle(el);
                        return style.display === 'grid'
                            ? style.gridTemplateColumns.split(' ').length
                            : style.columnCount || 1;
                    }"""
                )
                if cols > 1:
                    multi_column_found = True
                    break
        # Log but don't fail if no multi-column found
        if multi_column_found:
            print("Multi-column layout detected on desktop ✓")
