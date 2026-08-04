"""
Application constants and thresholds for CliqChef.ai UI/UX audit.
All performance budgets, WCAG thresholds, and viewport presets
are defined here as single source of truth.
"""

from dataclasses import dataclass


# ─── Application ───

APP_NAME: str = "CliqChef"
BASE_URL: str = "https://cliqchef.ai"
TITLE_KEYWORD: str = "CliqChef"


# ─── Viewport Presets ───

@dataclass(frozen=True)
class Viewport:
    width: int
    height: int
    label: str


VIEWPORTS: dict[str, Viewport] = {
    "mobile_small": Viewport(320, 568, "Mobile Small (320×568)"),
    "mobile": Viewport(375, 667, "Mobile (375×667)"),
    "mobile_large": Viewport(428, 926, "Mobile Large (428×926)"),
    "tablet": Viewport(768, 1024, "Tablet (768×1024)"),
    "tablet_landscape": Viewport(1024, 768, "Tablet Landscape (1024×768)"),
    "desktop": Viewport(1280, 720, "Desktop (1280×720)"),
    "desktop_large": Viewport(1440, 900, "Desktop Large (1440×900)"),
    "desktop_wide": Viewport(1920, 1080, "Desktop Wide (1920×1080)"),
}


# ─── WCAG 2.1 Compliance Thresholds ───

CONTRAST_RATIO_AA: float = 4.5           # Normal text (WCAG AA)
CONTRAST_RATIO_AA_LARGE: float = 3.0     # Large text (WCAG AA)
CONTRAST_RATIO_AAA: float = 7.0          # Normal text (WCAG AAA)
MAX_FOCUS_TRAVERSE: int = 50             # Max focus-trap escape attempts


# ─── Performance Budgets ───

LCP_BUDGET_MS: float = 2500.0            # Largest Contentful Paint
FID_BUDGET_MS: float = 100.0             # First Input Delay
CLS_BUDGET: float = 0.1                  # Cumulative Layout Shift
FCP_BUDGET_MS: float = 2500.0            # First Contentful Paint (relaxed for WP/Elementor)
TTFB_BUDGET_MS: float = 1000.0           # Time to First Byte (relaxed for WP hosting)
INP_BUDGET_MS: float = 200.0             # Interaction to Next Paint
PAGE_LOAD_MS: float = 5000.0             # Full page load timeout
DOM_READY_MS: float = 3000.0             # DOMContentLoaded budget
MAX_DOM_NODES: int = 1500                # Maximum DOM node count
MAX_DOC_SIZE_KB: int = 500               # Maximum document size
MAX_IMAGE_WEIGHT_KB: int = 2048          # Maximum total image weight
MAX_REQUESTS_ON_LOAD: int = 60           # Max network requests on load (relaxed for WP/Elementor)


# ─── Animation & UX Timing ───

HOVER_ANIMATION_MS: int = 300            # Hover/transition animations
MODAL_OPEN_MS: int = 500                 # Modal open animation
MODAL_CLOSE_MS: int = 400                # Modal close animation
DROPDOWN_OPEN_MS: int = 300              # Dropdown open animation
PAGE_TRANSITION_MS: int = 1000           # SPA page transition
SEARCH_DEBOUNCE_MS: int = 500            # Search input debounce
TOAST_DISMISS_MS: int = 5000             # Toast auto-dismiss
SCROLL_ANIMATION_MS: int = 600           # Scroll animation duration


# ─── SEO & Content ───

MIN_TITLE_LENGTH: int = 10               # Minimum page title length
MAX_TITLE_LENGTH: int = 100              # Maximum page title length (relaxed for branded titles)
MIN_DESC_LENGTH: int = 50                # Minimum meta description length
MAX_DESC_LENGTH: int = 160               # Maximum meta description length
