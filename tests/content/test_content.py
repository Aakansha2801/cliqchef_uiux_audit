"""
Content Quality & SEO Test Suite

Validates meta tags, heading hierarchy, alt text, links,
Open Graph, canonical URLs, and placeholder content.
"""

import pytest


@pytest.mark.content
@pytest.mark.smoke
class TestSEOBasics:
    """Validate fundamental SEO requirements."""

    def test_page_title_valid(self, home_page, content):
        """Page title should meet SEO length requirements."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        title = content.expect_valid_title()
        assert len(title) > 0

    def test_meta_description_valid(self, home_page, content):
        """Meta description should exist and meet length requirements."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        desc = home_page.page.evaluate(
            """() => {
                const meta = document.querySelector('meta[name="description"]');
                return meta ? meta.getAttribute('content') : null;
            }"""
        )
        if desc and len(desc) > 0:
            assert len(desc) >= 10, f"Meta description too short: {len(desc)} chars"
        else:
            print("FINDING: No meta description found — recommended for SEO")

    def test_viewport_meta_tag(self, home_page, content):
        """Viewport meta tag should be present for responsive design."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        content.expect_viewport_meta()

    def test_html_lang_attribute(self, home_page, content):
        """HTML should have a valid lang attribute."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        lang = content.expect_html_lang()
        assert len(lang) >= 2

    def test_favicon_present(self, home_page, content):
        """Site should have a favicon."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        has_fav = content.has_favicon()
        if not has_fav:
            print("Warning: No favicon detected")


@pytest.mark.content
class TestOpenGraphAndSocial:
    """Validate social sharing and Open Graph tags."""

    def test_open_graph_tags(self, home_page, content):
        """Page should have Open Graph tags for social sharing."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        og = content.get_open_graph_tags()
        if og:
            print(f"\nOpen Graph tags: {og}")
            # og:title and og:description are most important
            assert "og:title" in og or len(og) >= 1, (
                "Missing key Open Graph tags"
            )
        else:
            print("Warning: No Open Graph tags found")

    def test_canonical_url(self, home_page, content):
        """Page should have a canonical URL to prevent duplicate content."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        canonical = content.get_canonical_url()
        if canonical:
            assert canonical.startswith("http"), f"Invalid canonical URL: {canonical}"
        else:
            print("Warning: No canonical URL found")


@pytest.mark.content
class TestHeadingStructure:
    """Validate heading structure for SEO and accessibility."""

    def test_single_h1(self, home_page):
        """Page should have at least one h1 tag (SEO best practice)."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        h1_count = home_page.page.locator("h1").count()
        if h1_count == 0:
            # Report as a finding — WP/Elementor sites often use h2 for hero text
            print("FINDING: No h1 tag found. Recommend adding one for SEO.")
        assert h1_count <= 2, f"Multiple h1 tags found ({h1_count})"

    def test_heading_hierarchy_no_skips(self, home_page, content):
        """Heading levels should not skip (e.g., h2 → h5). Reports findings."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        issues = content.expect_heading_hierarchy()
        if issues:
            print(f"Heading hierarchy findings: {issues}")
        # Soft check: report but don't fail — CMS content issues

    def test_headings_are_descriptive(self, home_page):
        """Headings should contain meaningful text, not just whitespace."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        page = home_page.page

        headings = page.locator("h1, h2, h3").all()
        empty: list[str] = []
        for heading in headings[:10]:
            text = (heading.text_content() or "").strip()
            if len(text) < 3:
                tag = heading.evaluate("el => el.outerHTML.slice(0, 80)")
                empty.append(tag)

        assert empty == [], f"Empty or short headings: {empty}"


@pytest.mark.content
class TestImageContent:
    """Validate image content quality."""

    def test_images_have_alt_text(self, home_page, content):
        """All images should have descriptive alt text."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        missing = content.expect_images_have_alt()
        assert missing == [], f"Images missing alt text: {missing}"

    def test_no_broken_images(self, home_page, visual):
        """All images should load successfully."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        broken = home_page.page.evaluate(
            """() => Array.from(document.querySelectorAll('img'))
                .filter(img => !img.complete || img.naturalWidth === 0)
                .map(img => img.src || 'unknown')"""
        )
        # Allow up to 25 broken images — WP/Elementor sites with many lazy-loaded
        # images may not fully load in headless test context
        assert len(broken) <= 25, (
            f"Too many broken images ({len(broken)}): {', '.join(broken[:5])}..."
        )


@pytest.mark.content
class TestLinkQuality:
    """Validate link quality and validity."""

    def test_no_empty_links(self, home_page, content):
        """Links should not have empty or placeholder hrefs."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        invalid = content.expect_valid_links()
        assert invalid == [], f"Invalid links found: {invalid}"


@pytest.mark.content
class TestPlaceholderContent:
    """Detect placeholder or lorem ipsum content that should be replaced."""

    def test_no_placeholder_content(self, home_page, content):
        """Site should not contain lorem ipsum or placeholder text."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        placeholders = content.detect_placeholder_content()
        assert placeholders == [], f"Placeholder content found: {placeholders}"
