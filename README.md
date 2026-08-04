# 🔍 CliqChef.ai — UI/UX Audit Suite

Industry-standard **Playwright + Python** testing codebase for comprehensive UI/UX auditing of [cliqchef.ai](https://cliqchef.ai/).

## 📋 What This Tests

| Suite | What It Covers | Marker |
|-------|---------------|--------|
| **Accessibility** | WCAG 2.1 AA, axe-core audit, keyboard nav, ARIA, focus rings, color contrast | `@pytest.mark.accessibility` |
| **Visual Regression** | Screenshots, layout integrity, overflow, broken images, z-index, component consistency | `@pytest.mark.visual` |
| **Responsive Design** | 8 viewport breakpoints, touch targets, mobile menu, multi-column layouts | `@pytest.mark.responsive` |
| **Performance** | Core Web Vitals (LCP/FID/CLS/FCP/TTFB), page weight, DOM count, lazy loading, render-blocking | `@pytest.mark.performance` |
| **Navigation** | Internal/external links, anchor links, scroll behavior, back-to-top | `@pytest.mark.navigation` |
| **Forms** | Input labels, validation, required fields, submission feedback, form structure | `@pytest.mark.forms` |
| **Content & SEO** | Title, meta description, OG tags, canonical, heading hierarchy, placeholder detection | `@pytest.mark.content` |
| **UX Interactions** | Hover states, focus management, modal/dropdown behavior, animations, error handling | `@pytest.mark.ux` |

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/Aakansha2801/cliqchef_uiux_audit.git
cd cliqchef_uiux_audit

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -e .

# Install Playwright browsers
playwright install --with-deps chromium firefox webkit

# Run all tests
pytest

# Run with visible browser
pytest --headed

# Run specific suite
pytest tests/accessibility/    # Accessibility only
pytest tests/visual/           # Visual regression only
pytest tests/performance/      # Performance only
pytest tests/responsiveness/   # Responsive design only

# Run by marker
pytest -m accessibility
pytest -m "smoke or critical"
pytest -m performance

# Run across multiple browsers
pytest --browser chromium --browser firefox --browser webkit

# Run in parallel (4 workers)
pytest -n 4

# Generate HTML report
pytest --html=reports/audit-report.html --self-contained-html
```

## 🏗️ Project Structure

```
cliqchef_uiux_audit/
├── .github/workflows/
│   └── playwright.yml          # CI/CD pipeline
├── pages/                      # Page Object Model
│   ├── base_page.py            # Base page with shared locators & helpers
│   └── home_page.py            # Home/landing page object
├── helpers/                    # Reusable test utilities
│   ├── constants.py            # All thresholds, viewports, budgets
│   ├── accessibility_helper.py # axe-core audit, focus trap, skip links
│   ├── performance_helper.py   # Core Web Vitals, navigation timing
│   ├── visual_helper.py        # Screenshots, overflow, contrast, z-index
│   ├── ux_helper.py            # Hover, modal, dropdown, transitions
│   └── content_helper.py       # SEO, OG tags, heading hierarchy
├── tests/                      # Test suites
│   ├── accessibility/          # WCAG 2.1 AA compliance
│   ├── visual/                 # Visual regression & layout
│   ├── responsiveness/         # Multi-viewport testing
│   ├── performance/            # Core Web Vitals & speed
│   ├── navigation/             # Routing & link validation
│   ├── forms/                  # Form interaction & validation
│   ├── content/                # SEO & content quality
│   └── ux/                     # Usability & interactions
├── conftest.py                 # Pytest fixtures & config
├── pyproject.toml              # Project config, deps, pytest settings
└── snapshots/                  # Visual regression baselines
```

## ⚙️ Configuration

### Performance Budgets (in `helpers/constants.py`)

| Metric | Budget | Description |
|--------|--------|-------------|
| LCP | 2,500 ms | Largest Contentful Paint |
| FCP | 1,800 ms | First Contentful Paint |
| FID | 100 ms | First Input Delay |
| CLS | 0.1 | Cumulative Layout Shift |
| TTFB | 800 ms | Time to First Byte |
| DOM Nodes | 1,500 | Max DOM complexity |

### Viewport Breakpoints

| Name | Size | Usage |
|------|------|-------|
| Mobile Small | 320×568 | iPhone SE |
| Mobile | 375×667 | iPhone 8 |
| Mobile Large | 428×926 | iPhone 14 Pro Max |
| Tablet | 768×1024 | iPad |
| Tablet Landscape | 1024×768 | iPad landscape |
| Desktop | 1280×720 | Standard desktop |
| Desktop Large | 1440×900 | Large desktop |
| Desktop Wide | 1920×1080 | Full HD |

## 🔄 CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/playwright.yml`) runs:

- **On every push/PR**: lint + accessibility + visual + performance + responsive
- **Nightly (2 AM UTC)**: full audit across Chromium, Firefox, and WebKit
- **On demand** (workflow_dispatch): full cross-browser audit

Each suite runs as a separate job with HTML + JUnit reports uploaded as artifacts.

## 🧪 Running Specific Tests

```bash
# Smoke tests only (fast critical path)
pytest -m smoke

# Critical business flows
pytest -m critical

# Mobile-only tests
pytest -m mobile

# Skip slow tests
pytest -m "not slow"

# Single test file
pytest tests/ux/test_ux.py

# Single test by name
pytest -k "test_no_critical_violations"

# Debug mode (slow, step-through)
pytest --debug --headed -vv
```

## 📊 Reports

```bash
# HTML report (auto-opens in browser)
pytest --html=reports/audit.html --self-contained-html

# Allure report (rich interactive)
pytest --alluredir=reports/allure
allure serve reports/allure

# JUnit XML (for CI)
pytest --junitxml=reports/results.xml
```

## 🛠️ Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Lint
ruff check pages/ helpers/ tests/

# Format
ruff format pages/ helpers/ tests/

# Type check
mypy pages/ helpers/ --ignore-missing-imports
```

## 📝 License

MIT
