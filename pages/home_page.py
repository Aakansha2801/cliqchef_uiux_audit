"""
Home Page Object for CliqChef.ai landing page.
Encapsulates home-page-specific selectors and actions.
"""

from __future__ import annotations

from playwright.sync_api import Page

from .base_page import BasePage


class HomePage(BasePage):
    """Home / landing page with hero, CTA, features, pricing, testimonials."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def hero_section(self):
        return self.page.locator(
            "[class*='hero'], [class*='banner'], section"
        ).first

    @property
    def cta_button(self):
        return self.page.locator(
            "a:has-text('Get Started'), a:has-text('Sign Up'), "
            "a:has-text('Try'), button:has-text('Get Started')"
        ).first

    @property
    def features_section(self):
        return self.page.locator(
            "[class*='feature'], [id*='feature']"
        ).first

    @property
    def testimonials_section(self):
        return self.page.locator(
            "[class*='testimonial'], [class*='review']"
        ).first

    @property
    def pricing_section(self):
        return self.page.locator(
            "[class*='pricing'], [id*='pricing']"
        ).first

    @property
    def faq_section(self):
        return self.page.locator(
            "[class*='faq'], [id*='faq']"
        ).first

    # ─── Page-Specific Actions ───

    def click_cta(self) -> None:
        self.cta_button.click()

    def scroll_to_features(self) -> None:
        if self.features_section.is_visible():
            self.features_section.scroll_into_view_if_needed()

    def scroll_to_pricing(self) -> None:
        if self.pricing_section.is_visible():
            self.pricing_section.scroll_into_view_if_needed()

    def scroll_to_testimonials(self) -> None:
        if self.testimonials_section.is_visible():
            self.testimonials_section.scroll_into_view_if_needed()
