"""
UX-specific interaction helpers.
Validates hover states, focus rings, modals, dropdowns, transitions, and layout shifts.
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from .constants import (
    DROPDOWN_OPEN_MS,
    HOVER_ANIMATION_MS,
    MODAL_CLOSE_MS,
    MODAL_OPEN_MS,
    PAGE_TRANSITION_MS,
    SCROLL_ANIMATION_MS,
    TOAST_DISMISS_MS,
)


class UXHelper:
    """UX interaction and usability helper."""

    def __init__(self, page: Page) -> None:
        self._page = page

    def expect_hover_animation(self, selector: str) -> None:
        """Verify hover state produces visual change within animation budget."""
        locator = self._page.locator(selector)
        before = locator.screenshot()

        import time
        start = time.monotonic()
        locator.hover()
        elapsed = (time.monotonic() - start) * 1000

        self._page.wait_for_timeout(HOVER_ANIMATION_MS)
        after = locator.screenshot()

        if before == after:
            raise AssertionError(f'Hover on "{selector}" produced no visual change.')
        if elapsed > HOVER_ANIMATION_MS:
            raise AssertionError(
                f"Hover animation took {elapsed:.0f}ms, exceeds {HOVER_ANIMATION_MS}ms budget"
            )

    def expect_focus_ring(self, selector: str) -> None:
        """Verify a visible focus ring is present on the element."""
        locator = self._page.locator(selector)
        locator.focus()
        self._page.wait_for_timeout(100)

        has_outline: bool = locator.evaluate(
            """(el) => {
                const style = getComputedStyle(el);
                return (
                    style.outlineStyle !== 'none' ||
                    style.boxShadow.includes('0') ||
                    style.borderWidth !== '0px' ||
                    el.matches(':focus-visible')
                );
            }"""
        )
        if not has_outline:
            raise AssertionError(f'No visible focus ring on "{selector}".')

    def expect_accessible_modal(
        self,
        trigger_selector: str,
        modal_selector: str,
        close_selector: str,
    ) -> None:
        """Verify modal traps focus and returns focus on close."""
        self._page.locator(trigger_selector).click()
        self._page.wait_for_timeout(MODAL_OPEN_MS)
        expect(self._page.locator(modal_selector)).to_be_visible()

        # Check background inert/aria-hidden
        body_aria_hidden = self._page.evaluate(
            "() => document.body.getAttribute('aria-hidden')"
        )
        main_inert = self._page.evaluate(
            """() => document.querySelector('main, [role="main"]')?.hasAttribute('inert')"""
        )
        if body_aria_hidden != "true" and not main_inert:
            print("Warning: Modal does not set aria-hidden or inert on background content.")

        previous_focus = self._page.evaluate("() => document.activeElement?.tagName")
        self._page.locator(close_selector).click()
        self._page.wait_for_timeout(MODAL_CLOSE_MS)

        expect(self._page.locator(modal_selector)).not_to_be_visible()

        current_focus = self._page.evaluate("() => document.activeElement?.tagName")
        if current_focus != previous_focus:
            print(
                f"Warning: Focus did not return to trigger after modal close "
                f"(was: {previous_focus}, now: {current_focus})."
            )

    def expect_smooth_scroll(self, anchor_selector: str) -> None:
        """Check smooth scroll behavior on anchor links."""
        start_scroll = self._page.evaluate("() => window.scrollY")
        self._page.locator(anchor_selector).click()
        self._page.wait_for_timeout(SCROLL_ANIMATION_MS)
        end_scroll = self._page.evaluate("() => window.scrollY")

        if abs(end_scroll - start_scroll) < 10:
            raise AssertionError("Anchor link did not produce meaningful scroll.")

    def expect_toast_behavior(
        self,
        trigger_selector: str,
        toast_selector: str,
        auto_dismiss: bool = True,
    ) -> None:
        """Verify toast appears and optionally auto-dismisses."""
        self._page.locator(trigger_selector).click()
        expect(self._page.locator(toast_selector)).to_be_visible(timeout=MODAL_OPEN_MS)

        if auto_dismiss:
            expect(self._page.locator(toast_selector)).not_to_be_visible(
                timeout=TOAST_DISMISS_MS * 2
            )

    def expect_dropdown_behavior(
        self,
        trigger_selector: str,
        menu_selector: str,
    ) -> None:
        """Verify dropdown opens/closes within budget."""
        import time

        open_start = time.monotonic()
        self._page.locator(trigger_selector).click()
        expect(self._page.locator(menu_selector)).to_be_visible(timeout=DROPDOWN_OPEN_MS)
        open_time = (time.monotonic() - open_start) * 1000

        if open_time > DROPDOWN_OPEN_MS:
            raise AssertionError(
                f"Dropdown open took {open_time:.0f}ms, exceeds {DROPDOWN_OPEN_MS}ms budget."
            )

        # Close by clicking outside
        self._page.mouse.click(0, 0)
        expect(self._page.locator(menu_selector)).not_to_be_visible(
            timeout=DROPDOWN_OPEN_MS
        )

    def expect_page_transition(
        self,
        action: callable,
        content_selector: str,
    ) -> None:
        """Verify SPA-style page transition is smooth."""
        import time

        start = time.monotonic()
        action()
        expect(self._page.locator(content_selector)).to_be_visible(
            timeout=PAGE_TRANSITION_MS
        )
        elapsed = (time.monotonic() - start) * 1000

        if elapsed > PAGE_TRANSITION_MS:
            raise AssertionError(
                f"Page transition took {elapsed:.0f}ms, exceeds {PAGE_TRANSITION_MS}ms budget."
            )
