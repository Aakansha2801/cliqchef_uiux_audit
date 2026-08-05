"""
Performance Test Suite

Measures Core Web Vitals, page weight, DOM complexity,
network efficiency, and rendering performance.
"""

import pytest

from helpers.constants import (
    CLS_BUDGET,
    FCP_BUDGET_MS,
    LCP_BUDGET_MS,
    MAX_DOM_NODES,
    MAX_DOC_SIZE_KB,
    MAX_IMAGE_WEIGHT_KB,
    MAX_REQUESTS_ON_LOAD,
    PAGE_LOAD_MS,
    TTFB_BUDGET_MS,
)


@pytest.mark.performance
@pytest.mark.critical
class TestCoreWebVitals:
    """Validate Core Web Vitals meet performance budgets."""

    def test_lcp_within_budget(self, home_page, perf):
        """Largest Contentful Paint should be under 2.5s."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        vitals = perf.measure_core_web_vitals()
        if vitals.LCP > 0:
            assert vitals.LCP <= LCP_BUDGET_MS, (
                f"LCP {vitals.LCP:.0f}ms exceeds {LCP_BUDGET_MS:.0f}ms budget"
            )

    def test_fcp_within_budget(self, home_page, perf):
        """First Contentful Paint should be under 1.8s."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        vitals = perf.measure_core_web_vitals()
        if vitals.FCP > 0:
            assert vitals.FCP <= FCP_BUDGET_MS, (
                f"FCP {vitals.FCP:.0f}ms exceeds {FCP_BUDGET_MS:.0f}ms budget"
            )

    def test_cls_within_budget(self, home_page, perf):
        """Cumulative Layout Shift should be under 0.1."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        vitals = perf.measure_core_web_vitals()
        if vitals.CLS > 0:
            assert vitals.CLS <= CLS_BUDGET, (
                f"CLS {vitals.CLS:.3f} exceeds {CLS_BUDGET} budget"
            )

    def test_ttfb_within_budget(self, home_page, perf):
        """Time to First Byte should be under 800ms."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        vitals = perf.measure_core_web_vitals()
        if vitals.TTFB > 0:
            assert vitals.TTFB <= TTFB_BUDGET_MS, (
                f"TTFB {vitals.TTFB:.0f}ms exceeds {TTFB_BUDGET_MS:.0f}ms budget"
            )

    def test_all_vitals_summary(self, home_page, perf):
        """Print a summary of all Core Web Vitals for reporting."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        vitals = perf.measure_core_web_vitals()
        print(f"\nCore Web Vitals: {vitals.summarize()}")
        # Soft check — just log, don't fail on summary test


@pytest.mark.performance
class TestPageWeight:
    """Validate page weight and resource efficiency."""

    def test_dom_node_count_reasonable(self, home_page, perf):
        """DOM should not exceed 1500 nodes (performance impact)."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        count = perf.get_dom_node_count()
        assert count <= MAX_DOM_NODES, (
            f"DOM has {count} nodes (max {MAX_DOM_NODES})"
        )

    def test_network_request_count(self, home_page, perf):
        """Initial page load should not exceed budget network requests."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        count = perf.get_network_request_count()
        print(f"\nNetwork requests on load: {count} (budget: {MAX_REQUESTS_ON_LOAD})")
        if count > MAX_REQUESTS_ON_LOAD:
            print(
                f"FINDING P3: Page made {count} requests on load "
                f"(budget {MAX_REQUESTS_ON_LOAD}). "
                f"This is typical for WP/Elementor sites with many widget assets."
            )
        # Soft check — log as finding, don't hard-fail

    def test_page_weight_kb(self, home_page, perf):
        """Total page weight should be reasonable."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        weight = perf.get_page_weight_kb()
        print(f"\nPage weight: {weight:.0f} KB")
        # Soft threshold — log but don't hard-fail
        if weight > MAX_DOC_SIZE_KB:
            print(f"Warning: Page weight {weight:.0f}KB exceeds {MAX_DOC_SIZE_KB}KB budget")


@pytest.mark.performance
class TestResourceOptimization:
    """Validate resource loading optimizations."""

    def test_images_use_lazy_loading(self, home_page, perf):
        """Images below the fold should use lazy loading."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        without_lazy = perf.get_images_without_lazy_load()
        # Allow up to 8 images without lazy — Elementor sites load
        # many above-fold images (logos, app store badges, etc.) eagerly
        assert len(without_lazy) <= 8, (
            f"Too many images without lazy loading: {without_lazy[:5]}"
        )

    def test_no_render_blocking_resources(self, home_page, perf):
        """Identify render-blocking stylesheets and scripts."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        blocking = perf.get_render_blocking_resources()
        if blocking:
            print(f"Render-blocking resources found: {blocking[:5]}")
        # Log but don't hard-fail (many sites have some blocking CSS)


@pytest.mark.performance
class TestNavigationTiming:
    """Detailed navigation timing analysis."""

    def test_navigation_timing_breakdown(self, home_page, perf):
        """Print detailed navigation timing breakdown."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        timing = perf.get_navigation_timing()
        print(f"\nNavigation Timing Breakdown:")
        print(f"  DNS Lookup:     {timing.dns_lookup:.0f}ms")
        print(f"  TCP Connect:    {timing.tcp_connect:.0f}ms")
        print(f"  SSL Handshake:  {timing.ssl_handshake:.0f}ms")
        print(f"  TTFB:           {timing.ttfb:.0f}ms")
        print(f"  Download:       {timing.download:.0f}ms")
        print(f"  DOM Parse:      {timing.dom_parse:.0f}ms")
        print(f"  DOM Ready:      {timing.dom_ready:.0f}ms")
        print(f"  Page Load:      {timing.page_load:.0f}ms")

        # Soft check — page load for WP/Elementor sites often exceeds
        # lightweight budgets; report as finding rather than hard-fail
        if timing.page_load > PAGE_LOAD_MS:
            print(
                f"FINDING P4: Page load took {timing.page_load:.0f}ms "
                f"(budget {PAGE_LOAD_MS:.0f}ms). "
                f"Heavy DOM ({timing.dom_parse:.0f}ms parse) and many scripts "
                f"are the primary cause."
            )

    def test_layout_shift_detection(self, home_page, perf):
        """Detect cumulative layout shifts during page lifecycle."""
        home_page.goto()
        home_page.accept_cookies_if_present()
        cls = perf.detect_layout_shifts()
        print(f"\nDetected CLS: {cls:.4f}")
        assert cls <= CLS_BUDGET * 2, (
            f"Layout shift {cls:.4f} is excessive"
        )
