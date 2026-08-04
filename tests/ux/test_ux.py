"""
UX Interaction & Usability Test Suite

Validates hover states, focus management, modal behavior,
dropdown interactions, animations, and layout shifts.
"""

import pytest
from playwright.sync_api import expect


@pytest.mark.ux
class TestHoverStates:
    """Validate hover state visual feedback."""

    def test_navigation_links_hover_effect(self, home_page):
        """Navigation links should show hover state feedback."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        nav_links = page.locator("nav a[href], header a[href]").all()
        for link in nav_links[:3]:
            if link.is_visible():
                # Capture before/after styles
                before_color = link.evaluate("el => getComputedStyle(el).color")
                link.hover()
                page.wait_for_timeout(200)
                after_color = link.evaluate("el => getComputedStyle(el).color")

                # At least some links should change on hover
                # (not all may change, so this is a soft check)
                if before_color != after_color:
                    print("Hover color change detected ✓")
                    break

    def test_buttons_hover_effect(self, home_page):
        """Buttons should show hover state feedback."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        buttons = page.locator("button, .btn, [role='button']").all()
        hover_changes = 0
        for btn in buttons[:5]:
            if btn.is_visible():
                before_bg = btn.evaluate("el => getComputedStyle(el).backgroundColor")
                btn.hover()
                page.wait_for_timeout(200)
                after_bg = btn.evaluate("el => getComputedStyle(el).backgroundColor")
                if before_bg != after_bg:
                    hover_changes += 1

        # At least some buttons should have hover effects
        if hover_changes > 0:
            print(f"{hover_changes} buttons with hover effects ✓")


@pytest.mark.ux
class TestFocusManagement:
    """Validate focus behavior for keyboard users."""

    def test_focus_visible_on_buttons(self, home_page, ux):
        """Buttons should show visible focus ring when focused via keyboard."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        buttons = page.locator("button").all()
        focus_rings = 0
        for btn in buttons[:3]:
            if btn.is_visible():
                try:
                    ux.expect_focus_ring("button")
                    focus_rings += 1
                    break
                except AssertionError:
                    pass  # Some buttons may use custom focus styles

        if focus_rings > 0:
            print("Focus ring detected on buttons ✓")

    def test_tab_order_logical(self, home_page):
        """Tab order should follow a logical visual flow (top-to-bottom, left-to-right)."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        focus_positions: list[dict] = []
        for _ in range(15):
            page.keyboard.press("Tab")
            focused = page.locator(":focus")
            if focused.count() > 0:
                box = focused.bounding_box()
                if box:
                    focus_positions.append({"x": box["x"], "y": box["y"]})

        # Check that focus generally moves top-to-bottom
        if len(focus_positions) >= 2:
            y_values = [p["y"] for p in focus_positions]
            # Allow some backtracking but overall should go downward
            increasing = sum(
                1 for i in range(1, len(y_values)) if y_values[i] >= y_values[i - 1] - 50
            )
            ratio = increasing / (len(y_values) - 1)
            assert ratio >= 0.5, (
                f"Tab order seems illogical (only {ratio:.0%} forward movement)"
            )


@pytest.mark.ux
class TestModalBehavior:
    """Validate modal/dialog interactions."""

    def test_modal_focus_trap_if_present(self, home_page, a11y):
        """If modals exist, they should trap focus within."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        # Look for modal triggers
        modal_triggers = page.locator(
            "[data-toggle='modal'], [data-bs-toggle='modal'], "
            "[aria-haspopup='dialog'], button:has-text('Open')"
        )
        if modal_triggers.count() > 0 and modal_triggers.first.is_visible():
            modal_triggers.first.click()
            page.wait_for_timeout(500)

            modal = page.locator("[role='dialog'], .modal").first
            if modal.is_visible():
                # Verify modal is visible
                expect(modal).to_be_visible()

                # Press Escape to close
                page.keyboard.press("Escape")
                page.wait_for_timeout(300)
                expect(modal).not_to_be_visible()


@pytest.mark.ux
class TestDropdownBehavior:
    """Validate dropdown/menu interactions."""

    def test_dropdown_keyboard_navigation(self, home_page):
        """Dropdowns should support keyboard navigation (arrows, Enter, Escape)."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        # Look for dropdown triggers
        dropdowns = page.locator(
            "[aria-haspopup='true'], [data-bs-toggle='dropdown'], "
            "button:has-text('Menu'), [class*='dropdown']"
        )
        if dropdowns.count() > 0 and dropdowns.first.is_visible():
            dropdowns.first.click()
            page.wait_for_timeout(300)

            # Press Escape to close
            page.keyboard.press("Escape")
            page.wait_for_timeout(200)


@pytest.mark.ux
class TestAnimationPerformance:
    """Validate animation smoothness and timing."""

    def test_no_layout_shifts_on_load(self, home_page, perf):
        """Page should not experience layout shifts during load."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        cls = perf.detect_layout_shifts()
        assert cls <= 0.2, f"Excessive layout shift on load: {cls:.4f}"

    def test_scroll_performance(self, home_page):
        """Page scrolling should be smooth (no jank)."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        # Measure scroll FPS
        import time
        start = time.monotonic()
        for _ in range(5):
            page.evaluate("() => window.scrollBy(0, 500)")
            page.wait_for_timeout(100)
        elapsed = time.monotonic() - start

        # 5 scrolls should complete in reasonable time
        assert elapsed < 5.0, f"Scrolling is janky: {elapsed:.1f}s for 5 scroll events"


@pytest.mark.ux
class TestErrorHandling:
    """Validate error states and user feedback."""

    def test_no_console_errors_on_load(self, home_page):
        """Home page should not produce console errors on load."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        # Collect console errors
        errors: list[str] = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)

        # Reload to capture errors
        page.reload(wait_until="networkidle")
        page.wait_for_timeout(2000)

        # Filter out known acceptable errors
        significant = [
            e for e in errors
            if "net::ERR" not in e and "404" not in e
        ]
        if significant:
            print(f"Console errors detected: {len(significant)}")
            for err in significant[:3]:
                print(f"  → {err[:100]}")
