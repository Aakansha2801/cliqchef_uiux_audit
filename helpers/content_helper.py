"""
SEO & content quality helpers.
Validates meta tags, heading hierarchy, alt text, links, and placeholder content.
"""

from __future__ import annotations

from playwright.sync_api import Page

from .constants import MAX_DESC_LENGTH, MAX_TITLE_LENGTH, MIN_DESC_LENGTH, MIN_TITLE_LENGTH


class ContentHelper:
    """Content quality and SEO helper."""

    def __init__(self, page: Page) -> None:
        self._page = page

    def expect_valid_title(self) -> str:
        """Verify page title meets SEO standards."""
        title = self._page.title()

        if len(title) < MIN_TITLE_LENGTH:
            raise AssertionError(
                f"Title too short ({len(title)} chars, min {MIN_TITLE_LENGTH}): \"{title}\""
            )
        if len(title) > MAX_TITLE_LENGTH:
            raise AssertionError(
                f"Title too long ({len(title)} chars, max {MAX_TITLE_LENGTH}): \"{title}\""
            )
        return title

    def expect_valid_meta_description(self) -> str:
        """Verify meta description exists and meets length requirements."""
        desc = self._page.locator('meta[name="description"]').get_attribute("content")

        if not desc:
            raise AssertionError("Missing meta description.")
        if len(desc) < MIN_DESC_LENGTH:
            raise AssertionError(
                f"Meta description too short ({len(desc)} chars, min {MIN_DESC_LENGTH})."
            )
        if len(desc) > MAX_DESC_LENGTH:
            raise AssertionError(
                f"Meta description too long ({len(desc)} chars, max {MAX_DESC_LENGTH})."
            )
        return desc

    def expect_heading_hierarchy(self) -> list[str]:
        """Check for proper heading hierarchy (h1→h2→h3, no skipping). Returns list of issues."""
        return self._page.evaluate(
            """() => {
                const headings = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6'));
                const issues = [];
                const h1Count = headings.filter(h => h.tagName === 'H1').length;
                if (h1Count === 0) issues.push('No h1 tag found.');
                if (h1Count > 1) issues.push('Multiple h1 tags found (' + h1Count + ').');
                const levels = headings.map(h => parseInt(h.tagName[1], 10));
                for (let i = 1; i < levels.length; i++) {
                    if (levels[i] - levels[i-1] > 1)
                        issues.push('Heading level skipped: h' + levels[i-1] + ' → h' + levels[i] + ' at index ' + i);
                }
                return issues;
            }"""
        )

    def expect_images_have_alt(self) -> list[str]:
        """Verify all images have alt text. Returns list of images missing alt."""
        return self._page.evaluate(
            """() => Array.from(document.querySelectorAll('img'))
                .filter(img => !img.hasAttribute('alt'))
                .map(img => img.src || 'unknown')"""
        )

    def expect_valid_links(self) -> list[str]:
        """Verify all links have valid href (not empty or #). Returns invalid link names."""
        return self._page.evaluate(
            """() => Array.from(document.querySelectorAll('a'))
                .filter(a => {
                    const href = a.getAttribute('href');
                    return !href || href === '#' || href === 'javascript:void(0)';
                })
                .map(a => a.textContent?.trim() || 'unnamed link')"""
        )

    def expect_viewport_meta(self) -> None:
        """Check for proper viewport meta tag."""
        content = self._page.locator('meta[name="viewport"]').get_attribute("content")
        if not content:
            raise AssertionError("Missing viewport meta tag.")
        if "width=device-width" not in content:
            raise AssertionError("Viewport meta tag missing width=device-width.")

    def get_open_graph_tags(self) -> dict[str, str]:
        """Retrieve all Open Graph meta tags."""
        return self._page.evaluate(
            """() => {
                const tags = {};
                document.querySelectorAll('meta[property^="og:"]').forEach(meta => {
                    tags[meta.getAttribute('property')] = meta.getAttribute('content') || '';
                });
                return tags;
            }"""
        )

    def get_canonical_url(self) -> str | None:
        """Get the canonical link URL."""
        return self._page.locator('link[rel="canonical"]').get_attribute("href")

    def expect_html_lang(self) -> str:
        """Check lang attribute on html element."""
        lang = self._page.locator("html").get_attribute("lang")
        if not lang:
            raise AssertionError("Missing lang attribute on <html> element.")
        return lang

    def has_favicon(self) -> bool:
        """Check if the page has a favicon."""
        for rel in ("icon", "shortcut icon", "apple-touch-icon"):
            count = self._page.locator(f'link[rel="{rel}"]').count()
            if count > 0:
                return True
        return False

    def detect_placeholder_content(self) -> list[str]:
        """Scan for placeholder/lorem ipsum content."""
        return self._page.evaluate(
            """() => {
                const pattern = /lorem|ipsum|dolor sit|placeholder|todo|fixme|tbd|coming soon/i;
                const findings = [];
                document.querySelectorAll('p,h1,h2,h3,h4,h5,h6,span,a,button,label')
                    .forEach(el => {
                        const text = (el.textContent || '').trim();
                        if (text.length > 0 && pattern.test(text))
                            findings.push(el.tagName + ': "' + text.slice(0, 60) + '"');
                    });
                return findings;
            }"""
        )
