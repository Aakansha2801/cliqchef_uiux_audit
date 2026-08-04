"""
Base Page Object — all page objects extend this.
Provides common navigation, waiting, locators, and helper access.
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page, expect

from helpers import AccessibilityHelper, ContentHelper, PerformanceHelper, UXHelper, VisualHelper
from helpers.constants import BASE_URL


class BasePage:
    """Base page with shared navigation, locators, assertions, and helper injection."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.a11y = AccessibilityHelper(page)
        self.perf = PerformanceHelper(page)
        self.visual = VisualHelper(page)
        self.ux = UXHelper(page)
        self.content = ContentHelper(page)

    # ─── Navigation ───

    def goto(self, path: str = "/") -> None:
        self.page.goto(f"{BASE_URL}{path}", wait_until="load", timeout=60000)
        # Wait for DOM to be interactive (not networkidle — sites with
        # analytics/WebSocket never reach networkidle)
        self.page.wait_for_load_state("domcontentloaded")

    def wait_for_page_load(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")

    def current_url(self) -> str:
        return self.page.url

    def title(self) -> str:
        return self.page.title()

    # ─── Common Locators ───

    @property
    def header(self) -> Locator:
        return self.page.locator("header, [role='banner']").first

    @property
    def footer(self) -> Locator:
        return self.page.locator("footer, [role='contentinfo']").first

    @property
    def main_content(self) -> Locator:
        return self.page.locator("main, [role='main']").first

    @property
    def nav(self) -> Locator:
        return self.page.locator("nav, [role='navigation']").first

    @property
    def skip_link(self) -> Locator:
        return self.page.locator("a[href^='#']").first

    @property
    def all_links(self) -> Locator:
        return self.page.locator("a[href]")

    @property
    def all_images(self) -> Locator:
        return self.page.locator("img")

    @property
    def all_buttons(self) -> Locator:
        return self.page.locator("button, [role='button'], input[type='submit']")

    @property
    def all_headings(self) -> Locator:
        return self.page.locator("h1, h2, h3, h4, h5, h6")

    @property
    def modal_overlay(self) -> Locator:
        return self.page.locator("[role='dialog'], .modal, .overlay").first

    @property
    def cookie_banner(self) -> Locator:
        return self.page.locator(
            "[class*='cookie'], [id*='cookie'], [class*='consent']"
        ).first

    # ─── Common Actions ───

    def click_link_with_text(self, text: str) -> None:
        self.page.locator(f"a:has-text('{text}')").first.click()

    def scroll_to_end(self) -> None:
        self.page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(500)

    def scroll_to_top(self) -> None:
        self.page.evaluate("() => window.scrollTo(0, 0)")
        self.page.wait_for_timeout(500)

    def accept_cookies_if_present(self) -> None:
        accept_btn = self.page.locator(
            "button:has-text('Accept'), button:has-text('OK'), "
            "button:has-text('Got it'), [class*='accept']"
        ).first
        if accept_btn.is_visible():
            accept_btn.click()
            self.page.wait_for_timeout(300)

    # ─── Common Assertions ───

    def expect_page_loaded(self) -> None:
        expect(self.page).to_have_url(BASE_URL)
        expect(self.main_content).to_be_visible()

    def expect_header_visible(self) -> None:
        expect(self.header).to_be_visible()

    def expect_footer_visible(self) -> None:
        expect(self.footer).to_be_visible()

    def expect_nav_visible(self) -> None:
        expect(self.nav).to_be_visible()
