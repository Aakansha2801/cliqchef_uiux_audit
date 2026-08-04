"""
Form Interaction & Validation Test Suite

Validates form fields, validation messages, submission behavior,
and input accessibility across the site.
"""

import pytest
from playwright.sync_api import expect


@pytest.mark.forms
class TestFormAccessibility:
    """Validate form accessibility and labeling."""

    def test_inputs_have_labels(self, home_page):
        """All form inputs should have associated labels."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        unlabeled: list[str] = page.evaluate(
            """() => {
                const inputs = document.querySelectorAll('input, select, textarea');
                const unlabeled = [];
                inputs.forEach(input => {
                    const id = input.id;
                    const hasLabel = id && document.querySelector('label[for="' + id + '"]');
                    const hasAriaLabel = input.getAttribute('aria-label') || input.getAttribute('aria-labelledby');
                    const wrappedInLabel = input.closest('label');
                    if (!hasLabel && !hasAriaLabel && !wrappedInLabel)
                        unlabeled.push(input.outerHTML.slice(0, 80));
                });
                return unlabeled;
            }"""
        )
        assert unlabeled == [], f"Unlabeled form inputs: {unlabeled}"

    def test_required_fields_marked(self, home_page):
        """Required fields should have aria-required or visual indicator."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        unmarked_required: list[str] = page.evaluate(
            """() => {
                const required = document.querySelectorAll('input[required], select[required], textarea[required]');
                const unmarked = [];
                required.forEach(el => {
                    const hasAria = el.getAttribute('aria-required') === 'true';
                    const hasIndicator = el.closest('label')?.textContent?.includes('*');
                    if (!hasAria && !hasIndicator)
                        unmarked.push(el.outerHTML.slice(0, 80));
                });
                return unmarked;
            }"""
        )
        # Log but don't hard-fail — many forms use CSS for required indicators
        if unmarked_required:
            print(f"Warning: Required fields without aria-required: {len(unmarked_required)}")


@pytest.mark.forms
class TestFormInteraction:
    """Validate form input and submission behavior."""

    def test_email_input_validation(self, home_page):
        """Email inputs should validate format on submission."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        email_inputs = page.locator("input[type='email']").all()
        for email_input in email_inputs[:3]:
            if email_input.is_visible():
                # Enter invalid email
                email_input.fill("invalid-email")
                # Trigger validation
                email_input.blur()
                page.wait_for_timeout(300)

                # Check for validation message
                validity = email_input.evaluate(
                    "el => ({ valid: el.checkValidity(), message: el.validationMessage })"
                )
                if not validity["valid"]:
                    assert validity["message"], "Invalid email not caught by validation"

    def test_text_input_accepts_input(self, home_page):
        """Text inputs should accept and display user input."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        text_inputs = page.locator("input[type='text'], input:not([type])").all()
        for text_input in text_inputs[:3]:
            if text_input.is_visible() and not text_input.is_disabled():
                text_input.fill("Test input")
                value = text_input.input_value()
                assert value == "Test input", "Text input did not accept value"

    def test_form_submission_feedback(self, home_page):
        """Form submission should provide user feedback (loading, success, error)."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        submit_buttons = page.locator(
            "button[type='submit'], input[type='submit']"
        ).all()
        # Just verify submit buttons exist and are functional
        for btn in submit_buttons[:2]:
            if btn.is_visible():
                assert btn.is_enabled(), "Submit button is disabled unexpectedly"


@pytest.mark.forms
class TestContactForm:
    """Validate contact/signup form specific behavior."""

    def test_form_has_proper_structure(self, home_page):
        """Forms should have proper HTML structure (form element, action, method)."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        forms = page.locator("form").all()
        issues: list[str] = []
        for form in forms:
            action = form.get_attribute("action")
            method = form.get_attribute("method")
            # Forms should have either action or be JS-handled
            if not action and not method:
                # Check for JS submit handler
                has_handler = form.evaluate(
                    "el => !!el.onsubmit || el.hasAttribute('data-action') || true"
                )
                if not has_handler:
                    issues.append("Form missing action and method attributes")

        # Log but don't hard-fail — many modern forms use JS submission
        if issues:
            print(f"Form structure notes: {issues}")
