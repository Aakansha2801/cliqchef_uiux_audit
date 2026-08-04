"""
Performance measurement helpers using Performance API & CDP.
Measures Core Web Vitals, navigation timing, and resource metrics.
"""

from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import Page

from .constants import (
    CLS_BUDGET,
    FCP_BUDGET_MS,
    FID_BUDGET_MS,
    LCP_BUDGET_MS,
    TTFB_BUDGET_MS,
)


# ─── CWV Measurement Script (injected into page) ───

_CWV_SCRIPT = """
() => {
    return new Promise((resolve) => {
        const result = {};

        try {
            new PerformanceObserver((list) => {
                const entries = list.getEntries();
                if (entries.length > 0) result.LCP = entries[entries.length - 1].startTime;
            }).observe({ type: 'largest-contentful-paint', buffered: true });
        } catch (e) {}

        try {
            new PerformanceObserver((list) => {
                const entries = list.getEntries();
                if (entries.length > 0) result.FID = entries[0].startTime;
            }).observe({ type: 'first-input', buffered: true });
        } catch (e) {}

        try {
            new PerformanceObserver((list) => {
                let cls = 0;
                for (const entry of list.getEntries()) {
                    if (!entry.hadRecentInput) cls += entry.value;
                }
                result.CLS = cls;
            }).observe({ type: 'layout-shift', buffered: true });
        } catch (e) {}

        try {
            new PerformanceObserver((list) => {
                const entries = list.getEntries();
                if (entries.length > 0) result.FCP = entries[0].startTime;
            }).observe({ type: 'paint', buffered: true });
        } catch (e) {}

        try {
            const nav = performance.getEntriesByType('navigation')[0];
            if (nav) result.TTFB = nav.responseStart - nav.requestStart;
        } catch (e) {}

        setTimeout(() => resolve(result), 3000);
    });
}
"""


@dataclass(frozen=True)
class CoreWebVitals:
    LCP: float
    FID: float
    CLS: float
    FCP: float
    TTFB: float

    def summarize(self) -> str:
        return (
            f"LCP={self.LCP:.0f}ms  FCP={self.FCP:.0f}ms  "
            f"FID={self.FID:.0f}ms  CLS={self.CLS:.3f}  TTFB={self.TTFB:.0f}ms"
        )


@dataclass(frozen=True)
class NavigationTimingMetrics:
    dns_lookup: float
    tcp_connect: float
    ssl_handshake: float
    ttfb: float
    download: float
    dom_parse: float
    dom_ready: float
    page_load: float


class PerformanceHelper:
    """Performance measurement helper using browser Performance API."""

    def __init__(self, page: Page) -> None:
        self._page = page

    def measure_core_web_vitals(self) -> CoreWebVitals:
        """Measure Core Web Vitals via injected performance observers."""
        raw: dict[str, float] = self._page.evaluate(_CWV_SCRIPT)
        return CoreWebVitals(
            LCP=raw.get("LCP", -1),
            FID=raw.get("FID", -1),
            CLS=raw.get("CLS", -1),
            FCP=raw.get("FCP", -1),
            TTFB=raw.get("TTFB", -1),
        )

    def expect_vitals_within_budget(self) -> CoreWebVitals:
        """Assert all Core Web Vitals are within defined budgets."""
        vitals = self.measure_core_web_vitals()
        errors: list[str] = []

        if 0 < vitals.LCP > LCP_BUDGET_MS:
            errors.append(f"LCP {vitals.LCP:.0f}ms > {LCP_BUDGET_MS:.0f}ms budget")
        if 0 < vitals.FCP > FCP_BUDGET_MS:
            errors.append(f"FCP {vitals.FCP:.0f}ms > {FCP_BUDGET_MS:.0f}ms budget")
        if 0 < vitals.CLS > CLS_BUDGET:
            errors.append(f"CLS {vitals.CLS:.3f} > {CLS_BUDGET} budget")
        if 0 < vitals.TTFB > TTFB_BUDGET_MS:
            errors.append(f"TTFB {vitals.TTFB:.0f}ms > {TTFB_BUDGET_MS:.0f}ms budget")

        if errors:
            raise AssertionError(
                f"Core Web Vitals exceeded budget:\n  " + "\n  ".join(errors)
            )

        return vitals

    def get_page_weight_kb(self) -> float:
        """Get total page weight in KB from network requests."""
        total: int = self._page.evaluate(
            """() => performance.getEntriesByType('resource')
                .reduce((sum, r) => sum + r.transferSize, 0)"""
        )
        return total / 1024

    def get_dom_node_count(self) -> int:
        """Count total DOM nodes on the page."""
        return self._page.evaluate("() => document.querySelectorAll('*').length")

    def get_network_request_count(self) -> int:
        """Count network requests since page load."""
        return self._page.evaluate("() => performance.getEntriesByType('resource').length")

    def get_navigation_timing(self) -> NavigationTimingMetrics:
        """Measure detailed navigation timing metrics."""
        raw: dict[str, float] = self._page.evaluate(
            """() => {
                const nav = performance.getEntriesByType('navigation')[0];
                return {
                    dns_lookup: nav.domainLookupEnd - nav.domainLookupStart,
                    tcp_connect: nav.connectEnd - nav.connectStart,
                    ssl_handshake: nav.secureConnectionStart > 0
                        ? nav.connectEnd - nav.secureConnectionStart : 0,
                    ttfb: nav.responseStart - nav.requestStart,
                    download: nav.responseEnd - nav.responseStart,
                    dom_parse: nav.domInteractive - nav.responseEnd,
                    dom_ready: nav.domContentLoadedEventEnd - nav.fetchStart,
                    page_load: nav.loadEventEnd - nav.fetchStart,
                };
            }"""
        )
        return NavigationTimingMetrics(**raw)

    def get_images_without_lazy_load(self) -> list[str]:
        """Check which images are missing lazy loading attributes."""
        return self._page.evaluate(
            """() => Array.from(document.querySelectorAll('img:not([loading])'))
                .filter(img => !img.src.startsWith('data:'))
                .map(img => img.src)"""
        )

    def get_render_blocking_resources(self) -> list[str]:
        """Identify render-blocking stylesheets and scripts."""
        return self._page.evaluate(
            """() => {
                const blocking = [];
                document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
                    if (!link.media || link.media === 'all' || link.media === 'screen')
                        blocking.push(link.href);
                });
                document.querySelectorAll('script[src]:not([async]):not([defer])')
                    .forEach(script => {
                        if (!script.type || script.type === 'text/javascript' || script.type === 'module')
                            blocking.push(script.src);
                    });
                return blocking;
            }"""
        )

    def detect_layout_shifts(self) -> float:
        """Detect cumulative layout shifts during page lifecycle."""
        return self._page.evaluate(
            """() => new Promise((resolve) => {
                let cls = 0;
                try {
                    new PerformanceObserver((list) => {
                        for (const entry of list.getEntries()) {
                            if (!entry.hadRecentInput) cls += entry.value;
                        }
                    }).observe({ type: 'layout-shift', buffered: true });
                } catch (e) {}
                setTimeout(() => resolve(cls), 2000);
            })"""
        )
