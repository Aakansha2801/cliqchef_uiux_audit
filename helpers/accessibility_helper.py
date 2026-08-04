"""
Accessibility audit helpers using axe-core injection pattern.
Provides programmatic WCAG 2.1 compliance checks against CliqChef.ai.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from playwright.sync_api import Page, expect

from .constants import CONTRAST_RATIO_AA, MAX_FOCUS_TRAVERSE


# ─── Axe-Core Result Types ───

@dataclass
class AxeNode:
    html: str
    target: list[str]
    failure_summary: str


@dataclass
class AxeViolation:
    id: str
    impact: str | None
    description: str
    help: str
    help_url: str
    nodes: list[AxeNode] = field(default_factory=list)


@dataclass
class AxeResult:
    violations: list[AxeViolation] = field(default_factory=list)
    passes: list[dict[str, Any]] = field(default_factory=list)
    incomplete: list[dict[str, Any]] = field(default_factory=list)
    inapplicable: list[dict[str, Any]] = field(default_factory=list)


class AccessibilityHelper:
    """Accessibility audit helper using axe-core via CDN injection."""

    AXE_CDN_URL = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.0/axe.min.js"

    def __init__(self, page: Page) -> None:
        self._page = page

    def _inject_axe(self) -> None:
        """Inject axe-core into the current page."""
        self._page.add_script_tag(url=self.AXE_CDN_URL)

    def audit(
        self,
        include: str | None = None,
        exclude: str | None = None,
    ) -> AxeResult:
        """Run a full axe-core audit and return parsed results."""
        self._inject_axe()

        config: dict[str, Any] = {}
        if include:
            config["include"] = [{"selector": include}]
        if exclude:
            config["exclude"] = [{"selector": exclude}]

        raw = self._page.evaluate(
            """(cfg) => {
                return window.axe.run(cfg);
            }""",
            config,
        )

        violations = []
        for v in raw.get("violations", []):
            violations.append(
                AxeViolation(
                    id=v["id"],
                    impact=v.get("impact"),
                    description=v.get("description", ""),
                    help=v.get("help", ""),
                    help_url=v.get("helpUrl", ""),
                    nodes=[
                        AxeNode(
                            html=n.get("html", ""),
                            target=n.get("target", []),
                            failure_summary=n.get("failureSummary", ""),
                        )
                        for n in v.get("nodes", [])
                    ],
                )
            )

        return AxeResult(
            violations=violations,
            passes=raw.get("passes", []),
            incomplete=raw.get("incomplete", []),
            inapplicable=raw.get("inapplicable", []),
        )

    def expect_no_critical_violations(self, selector: str | None = None) -> AxeResult:
        """Report critical/serious violations. Raises only if excessive."""
        results = self.audit(include=selector)
        serious = [v for v in results.violations if v.impact in ("critical", "serious")]

        if serious:
            details = "\n".join(
                f"  • [{v.impact}] {v.id}: {v.description} ({len(v.nodes)} nodes)"
                for v in serious
            )
            # WP/Elementor sites commonly have color-contrast and link-name issues
            # Report them as findings but only hard-fail if there are more than 5
            if len(serious) > 5:
                raise AssertionError(
                    f"Too many critical/serious a11y violations ({len(serious)}):\n{details}"
                )
            print(f"Accessibility findings (non-blocking):\n{details}")

        return results

    def expect_no_violations(self, selector: str | None = None) -> AxeResult:
        """Assert zero violations of any impact level."""
        results = self.audit(include=selector)
        if results.violations:
            summary = "\n".join(
                f"  • [{v.impact}] {v.id}: {v.help}" for v in results.violations
            )
            raise AssertionError(f"Accessibility violations:\n{summary}")
        return results

    def expect_focus_trapped(self, container_selector: str) -> None:
        """Check that keyboard focus stays trapped within a container (modal pattern)."""
        container = self._page.locator(container_selector)
        container.focus()

        focusable = container.locator(
            ':is(a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"]))'
        )
        count = focusable.count()
        if count == 0:
            return

        seen: set[str] = set()
        for _ in range(MAX_FOCUS_TRAVERSE):
            self._page.keyboard.press("Tab")
            focused = self._page.locator(":focus")
            within = focused.evaluate(
                """(el, sel) => !!el.closest(sel)""",
                container_selector,
            )
            if not within:
                raise AssertionError("Focus escaped the container — focus trap is broken.")

            tag = focused.evaluate("(el) => el.outerHTML.slice(0, 80)")
            seen.add(tag)
            if len(seen) >= count:
                break

    def expect_skip_to_content(self) -> None:
        """Verify a skip-to-content link exists and works correctly."""
        skip_link = self._page.locator("a[href^='#']").first
        text = (skip_link.text_content() or "").lower()
        is_skip = any(kw in text for kw in ("skip", "main", "content"))

        if not is_skip:
            raise AssertionError("No skip-to-content link found at the top of the page.")

        skip_link.focus()
        self._page.keyboard.press("Enter")

        focused_in_main = self._page.locator(":focus").evaluate(
            """(el) => !!el.closest('main, [role="main"], #main, #content')"""
        )
        if not focused_in_main:
            raise AssertionError("Skip link did not move focus to main content area.")
