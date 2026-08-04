"""
Visual regression & layout integrity helpers.
Provides screenshot comparison, overflow detection, and contrast checking.
"""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from .constants import CONTRAST_RATIO_AA


class VisualHelper:
    """Visual regression and layout helper."""

    SNAPSHOT_DIR = Path("snapshots")

    def __init__(self, page: Page) -> None:
        self._page = page

    def expect_no_horizontal_overflow(self) -> None:
        """Verify no element causes horizontal scrollbar."""
        scroll_width = self._page.evaluate("() => document.documentElement.scrollWidth")
        client_width = self._page.evaluate("() => document.documentElement.clientWidth")
        if scroll_width > client_width:
            raise AssertionError(
                f"Horizontal overflow: scrollWidth={scroll_width}, clientWidth={client_width}"
            )

    def expect_no_broken_images(self) -> None:
        """Verify all images have loaded (no broken images)."""
        broken: list[str] = self._page.evaluate(
            """() => Array.from(document.querySelectorAll('img'))
                .filter(img => !img.complete || img.naturalWidth === 0)
                .map(img => img.src || img.alt || 'unknown')"""
        )
        if broken:
            raise AssertionError(f"Broken images found: {', '.join(broken)}")

    def expect_no_overlaps(self, selector: str) -> None:
        """Check that no elements matching selector overlap (bounding-box check)."""
        overlaps: list[str] = self._page.evaluate(
            """(sel) => {
                const elements = Array.from(document.querySelectorAll(sel));
                const boxes = elements.map((el) => ({
                    id: el.id || el.className || el.tagName,
                    rect: el.getBoundingClientRect(),
                }));
                const overlapping = [];
                for (let i = 0; i < boxes.length; i++) {
                    for (let j = i + 1; j < boxes.length; j++) {
                        const a = boxes[i].rect, b = boxes[j].rect;
                        if (a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top)
                            overlapping.push(boxes[i].id + ' ↔ ' + boxes[j].id);
                    }
                }
                return overlapping;
            }""",
            selector,
        )
        if overlaps:
            raise AssertionError(f"Overlapping elements:\n  {chr(10).join(overlaps)}")

    def get_z_index_stack(self) -> list[dict[str, int | str]]:
        """Get z-index stacking order of positioned elements."""
        return self._page.evaluate(
            """() => {
                const elements = document.querySelectorAll('[style*="z-index"], [class]');
                const stack = [];
                elements.forEach((el) => {
                    const z = parseInt(getComputedStyle(el).zIndex, 10);
                    if (!isNaN(z)) stack.push({
                        selector: el.tagName + (el.id ? '#' + el.id : '.' + el.className.toString().split(' ')[0]),
                        zIndex: z,
                    });
                });
                return stack.sort((a, b) => b.zIndex - a.zIndex);
            }"""
        )

    def get_color_contrast(self, selector: str) -> dict[str, float | str]:
        """Calculate color contrast ratio between foreground and background of element."""
        return self._page.evaluate(
            """(sel) => {
                const el = document.querySelector(sel);
                if (!el) throw new Error('Element not found: ' + sel);
                const style = getComputedStyle(el);
                const fg = style.color, bg = style.backgroundColor;
                const parse = (c) => {
                    const m = c.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
                    return m ? [parseInt(m[1]), parseInt(m[2]), parseInt(m[3])] : [0, 0, 0];
                };
                const [r1, g1, b1] = parse(fg), [r2, g2, b2] = parse(bg);
                const lum = (r, g, b) => {
                    const [rs, gs, bs] = [r, g, b].map(c => {
                        const s = c / 255;
                        return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
                    });
                    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
                };
                const l1 = lum(r1, g1, b1), l2 = lum(r2, g2, b2);
                const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
                return { ratio, fg, bg };
            }""",
            selector,
        )

    def expect_color_contrast_aa(self, selector: str) -> None:
        """Assert element meets WCAG AA color contrast ratio (4.5:1)."""
        result = self.get_color_contrast(selector)
        ratio = result["ratio"]
        if isinstance(ratio, (int, float)) and ratio < CONTRAST_RATIO_AA:
            raise AssertionError(
                f"Color contrast ratio {ratio:.2f} < {CONTRAST_RATIO_AA} for {selector}"
            )

    def get_text_overflow_issues(self, selector: str = "body") -> list[str]:
        """Detect text overflow/truncation issues."""
        return self._page.evaluate(
            """(sel) => {
                const elements = document.querySelectorAll(sel + ' *');
                const issues = [];
                elements.forEach((el) => {
                    const style = getComputedStyle(el);
                    if (style.overflow === 'hidden' && el.scrollWidth > el.clientWidth)
                        issues.push(el.tagName + '.' + el.className + ': ' + el.scrollWidth + 'px > ' + el.clientWidth + 'px');
                });
                return issues;
            }""",
            selector,
        )

    def take_full_screenshot(self, name: str) -> Path:
        """Take a full-page screenshot and save to snapshots directory."""
        path = self.SNAPSHOT_DIR / f"{name}-full.png"
        self.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        self._page.screenshot(path=str(path), full_page=True)
        return path

    def take_element_screenshot(self, locator: Locator, name: str) -> Path:
        """Take a screenshot of a specific element."""
        path = self.SNAPSHOT_DIR / f"{name}-element.png"
        self.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        locator.screenshot(path=str(path))
        return path
