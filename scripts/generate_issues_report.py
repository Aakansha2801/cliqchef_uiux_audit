#!/usr/bin/env python3
"""
CliqChef.ai — UI/UX Issues & Remediation Report
Focused document: only the 11 issues found, their priority, and how to fix them.
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem, KeepTogether, HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# ─── Font Registration ───
FONT_DIR = "/usr/share/fonts"
pdfmetrics.registerFont(TTFont("NotoSerifSC", f"{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Regular.ttf"))
pdfmetrics.registerFont(TTFont("NotoSerifSC-Bold", f"{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Bold.ttf"))
pdfmetrics.registerFont(TTFont("NotoSerifSC-SemiBold", f"{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-SemiBold.ttf"))
pdfmetrics.registerFont(TTFont("NotoSerifSC-Light", f"{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Light.ttf"))
registerFontFamily("NotoSerifSC", normal="NotoSerifSC", bold="NotoSerifSC-Bold")

# ─── Colors (Cascade Palette) ───
PAGE_BG       = colors.HexColor('#f2f3f3')
SECTION_BG    = colors.HexColor('#f0f1f2')
CARD_BG       = colors.HexColor('#ebedef')
TABLE_STRIPE  = colors.HexColor('#edf0f1')
HEADER_FILL   = colors.HexColor('#455963')
COVER_BLOCK   = colors.HexColor('#54798b')
BORDER        = colors.HexColor('#c1cbcf')
ICON          = colors.HexColor('#436e83')
ACCENT        = colors.HexColor('#3992be')
ACCENT_2      = colors.HexColor('#a96047')
TEXT_PRIMARY   = colors.HexColor('#212324')
TEXT_MUTED     = colors.HexColor('#757c7f')
SEM_SUCCESS   = colors.HexColor('#3c8254')
SEM_WARNING   = colors.HexColor('#ad8d4e')
SEM_ERROR     = colors.HexColor('#8c4a44')
SEM_INFO      = colors.HexColor('#597b9e')

# Priority badge colors
PRIORITY_HIGH   = colors.HexColor('#DC2626')
PRIORITY_MED    = colors.HexColor('#D97706')
PRIORITY_LOW    = colors.HexColor('#16A34A')
BADGE_HIGH_BG   = colors.HexColor('#FEE2E2')
BADGE_MED_BG    = colors.HexColor('#FEF3C7')
BADGE_LOW_BG    = colors.HexColor('#DCFCE7')

# ─── Page Setup ───
PAGE_W, PAGE_H = A4
MARGIN = 50
CONTENT_W = PAGE_W - 2 * MARGIN
output_path = "/home/z/my-project/download/CliqChef_UIUX_Issues_Audit.pdf"

doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=MARGIN, bottomMargin=MARGIN,
    title="CliqChef.ai UI/UX Issues Audit Report",
    author="Z.ai",
    subject="UI/UX issues, priority, and remediation for cliqchef.ai",
)

# ─── Styles ───
base_styles = getSampleStyleSheet()

cover_title = ParagraphStyle("CoverTitle", parent=base_styles["Title"],
    fontName="NotoSerifSC-Bold", fontSize=28, leading=34,
    textColor=colors.white, alignment=TA_LEFT, spaceAfter=8)

cover_sub = ParagraphStyle("CoverSub", parent=base_styles["Normal"],
    fontName="NotoSerifSC-Light", fontSize=14, leading=20,
    textColor=colors.HexColor("#B0C4D8"), alignment=TA_LEFT, spaceAfter=4)

h1 = ParagraphStyle("H1", parent=base_styles["Heading1"],
    fontName="NotoSerifSC-Bold", fontSize=20, leading=26,
    textColor=HEADER_FILL, spaceBefore=18, spaceAfter=8)

h2 = ParagraphStyle("H2", parent=base_styles["Heading2"],
    fontName="NotoSerifSC-Bold", fontSize=14, leading=18,
    textColor=ACCENT, spaceBefore=12, spaceAfter=6)

h3 = ParagraphStyle("H3", parent=base_styles["Heading3"],
    fontName="NotoSerifSC-SemiBold", fontSize=12, leading=16,
    textColor=HEADER_FILL, spaceBefore=8, spaceAfter=4)

body = ParagraphStyle("Body", parent=base_styles["Normal"],
    fontName="NotoSerifSC", fontSize=10, leading=16,
    textColor=TEXT_PRIMARY, alignment=TA_JUSTIFY, spaceAfter=6)

body_bold = ParagraphStyle("BodyBold", parent=body,
    fontName="NotoSerifSC-Bold")

bullet = ParagraphStyle("Bullet", parent=body,
    leftIndent=18, bulletIndent=6, spaceBefore=2, spaceAfter=2)

small = ParagraphStyle("Small", parent=body,
    fontSize=9, leading=13, spaceAfter=4)

caption = ParagraphStyle("Caption", parent=body,
    fontSize=8, leading=11, textColor=TEXT_MUTED, alignment=TA_CENTER)

# Table styles
th_s = ParagraphStyle("TH", parent=body, fontName="NotoSerifSC-Bold",
    fontSize=9, leading=12, textColor=colors.white, alignment=TA_CENTER)

td_s = ParagraphStyle("TD", parent=body, fontSize=9, leading=12, alignment=TA_LEFT)

td_c = ParagraphStyle("TDC", parent=td_s, alignment=TA_CENTER)

# ─── Helpers ───
def hr():
    return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceBefore=6, spaceAfter=6)

def badge(text, bg_color, text_color):
    return Paragraph(f'<font color="{text_color}"><b>{text}</b></font>',
        ParagraphStyle("Badge", parent=td_c, fontSize=9, backColor=bg_color))

def section_header(text):
    return Paragraph(text, h1)

story = []

# ═══════════════════════════════════════════
# COVER PAGE
# ═══════════════════════════════════════════
# Dark background cover using a full-width table
cover_data = [[""]]
cover_table = Table(cover_data, colWidths=[CONTENT_W], rowHeights=[PAGE_H - 2*MARGIN])
cover_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), HEADER_FILL),
    ('VALIGN', (0,0), (-1,-1), 'M'),
    ('LEFTPADDING', (0,0), (-1,-1), 30),
    ('RIGHTPADDING', (0,0), (-1,-1), 30),
    ('TOPPADDING', (0,0), (-1,-1), 0),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
]))

# Build cover content
cover_spacer = Spacer(1, 40)
cover_title_p = Paragraph("CliqChef.ai", cover_title)
cover_subtitle_p = Paragraph("UI/UX Issues Audit Report", ParagraphStyle("cs2", parent=cover_sub, fontSize=18, leading=24, textColor=colors.white, fontName="NotoSerifSC-Bold"))
cover_desc_p = Paragraph("Issues Found, Priority Assessment, and Remediation Guide", cover_sub)
cover_date_p = Paragraph(f"Audit Date: {datetime.now().strftime('%B %d, %Y')}", ParagraphStyle("cd", parent=cover_sub, fontSize=11, textColor=colors.HexColor("#8AAFC4")))
cover_url_p = Paragraph("Target: https://cliqchef.ai/", ParagraphStyle("cu", parent=cover_sub, fontSize=11, textColor=colors.HexColor("#8AAFC4")))

# Stats row
stat_style = ParagraphStyle("Stat", parent=cover_sub, fontSize=28, leading=32, textColor=colors.white, fontName="NotoSerifSC-Bold", alignment=TA_CENTER)
stat_label = ParagraphStyle("StatL", parent=cover_sub, fontSize=10, leading=13, textColor=colors.HexColor("#8AAFC4"), alignment=TA_CENTER)

stat_w = CONTENT_W * 0.25 - 15
stat_data = [
    [Paragraph("11", stat_style), Paragraph("6", stat_style), Paragraph("4", stat_style), Paragraph("1", stat_style)],
    [Paragraph("Total Issues", stat_label), Paragraph("High Priority", stat_label), Paragraph("Medium Priority", stat_label), Paragraph("Low Priority", stat_label)],
]
stat_table = Table(stat_data, colWidths=[stat_w]*4, rowHeights=[40, 20])
stat_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#3A5060")),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('TOPPADDING', (0,0), (-1,0), 8),
    ('BOTTOMPADDING', (0,0), (-1,0), 2),
    ('TOPPADDING', (0,1), (-1,1), 0),
    ('BOTTOMPADDING', (0,1), (-1,1), 8),
    ('LEFTPADDING', (0,0), (-1,-1), 4),
    ('RIGHTPADDING', (0,0), (-1,-1), 4),
]))

# Assemble cover as a nested table
cover_inner = [[cover_spacer], [cover_title_p], [cover_subtitle_p], [Spacer(1,4)], [cover_desc_p], [Spacer(1,30)], [cover_date_p], [cover_url_p], [Spacer(1,40)], [stat_table]]
cover_inner_table = Table(cover_inner, colWidths=[CONTENT_W - 60])
cover_inner_table.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('LEFTPADDING', (0,0), (-1,-1), 0),
    ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ('TOPPADDING', (0,0), (-1,-1), 0),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
]))

cover_table = Table([[cover_inner_table]], colWidths=[CONTENT_W])
cover_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), HEADER_FILL),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('LEFTPADDING', (0,0), (-1,-1), 30),
    ('RIGHTPADDING', (0,0), (-1,-1), 30),
    ('TOPPADDING', (0,0), (-1,-1), 30),
    ('BOTTOMPADDING', (0,0), (-1,-1), 30),
]))

story.append(cover_table)
story.append(PageBreak())

# ═══════════════════════════════════════════
# 1. EXECUTIVE SUMMARY
# ═══════════════════════════════════════════
story.append(section_header("1. Executive Summary"))
story.append(hr())
story.append(Paragraph(
    "This report presents the <b>11 UI/UX issues</b> discovered on <b>cliqchef.ai</b> through a comprehensive "
    "automated audit using Python + Playwright across 112 test cases spanning accessibility, performance, SEO, "
    "responsive design, visual layout, UX interactions, navigation, and forms. Each finding is classified by "
    "priority (High / Medium / Low) based on its impact on user experience and search engine visibility, and "
    "accompanied by a specific, actionable remediation guide. The site is built on WordPress/Elementor, and "
    "several findings are characteristic of that platform. None of the issues are severe enough to cause "
    "immediate site failure, but addressing them will meaningfully improve accessibility compliance, page load "
    "performance, and search engine rankings.", body))
story.append(Spacer(1,6))

# Priority summary table
ps_h = [Paragraph("<b>Priority</b>", th_s), Paragraph("<b>Count</b>", th_s), Paragraph("<b>Issues</b>", th_s), Paragraph("<b>Action</b>", th_s)]
ps_d = [
    [badge("HIGH", BADGE_HIGH_BG, PRIORITY_HIGH), Paragraph("6", td_c),
     Paragraph("P1, P2, P3, P4, S1, S2", td_s),
     Paragraph("Fix immediately - significant perf/UX/SEO impact", td_s)],
    [badge("MEDIUM", BADGE_MED_BG, PRIORITY_MED), Paragraph("4", td_c),
     Paragraph("A1, A2, S3, S4", td_s),
     Paragraph("Fix in next sprint - compliance and visibility", td_s)],
    [badge("LOW", BADGE_LOW_BG, PRIORITY_LOW), Paragraph("1", td_c),
     Paragraph("U1", td_s),
     Paragraph("Fix when convenient - minor cosmetic issue", td_s)],
]
ps_t = Table([ps_h] + ps_d, colWidths=[CONTENT_W*0.12, CONTENT_W*0.08, CONTENT_W*0.18, CONTENT_W*0.62])
ps_t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), HEADER_FILL),
    ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#FFF5F5')),
    ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#FFFBEB')),
    ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#F0FDF4')),
    ('GRID', (0,0), (-1,-1), 0.5, BORDER),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
    ('RIGHTPADDING', (0,0), (-1,-1), 6),
]))
story.append(ps_t)

# ═══════════════════════════════════════════
# 2. HIGH PRIORITY ISSUES
# ═══════════════════════════════════════════
story.append(section_header("2. High Priority Issues"))
story.append(hr())
story.append(Paragraph(
    "These six issues have the greatest negative impact on page performance, user experience, and search visibility. "
    "They should be addressed as the first priority in your remediation roadmap. Issues P1-P4 directly "
    "affect page load speed and resource efficiency (which are Google ranking factors), while S1-S2 affect "
    "SEO signals (which determine how the site appears in search results). Left unaddressed, they will "
    "progressively worsen as the site accumulates more content and assets.", body))
story.append(Spacer(1,6))

# --- P1 ---
story.append(Paragraph("P1 | Performance | Page Weight 1,543 KB Exceeds 500 KB Budget", h2))
story.append(Paragraph(
    "<b>What was found:</b> The total page weight of cliqchef.ai is 1,543 KB, which is more than "
    "three times the recommended budget of 500 KB for a landing page. This is primarily driven by "
    "Elementor's CSS framework (which loads widget styles for all registered widgets regardless of "
    "which ones are actually used on the page), Font Awesome icon libraries (both v5 and v4-shims "
    "compatibility CSS), and image assets that have not been converted to modern formats. On a fast "
    "broadband connection this is tolerable, but on 3G/4G mobile connections the page will take "
    "5-8 seconds to become interactive, creating a poor first impression for mobile visitors who "
    "represent a growing majority of web traffic.", body))
story.append(Paragraph("<b>Impact:</b> High - Directly affects mobile user experience, increases bounce rate, and is a negative signal for Google's Core Web Vitals assessment.", body))
story.append(Paragraph(
    "<b>How to fix it:</b> This requires a multi-pronged approach applied in order of effort-to-impact ratio. "
    "First, enable Brotli or gzip compression at the server level (most hosts offer this as a one-click toggle in "
    "cPanel or a single line in .htaccess). This alone can reduce transfer size by 60-70% for text-based assets. "
    "Second, convert all images to WebP format with JPEG fallbacks using a plugin like ShortPixel or Imagify. "
    "Third, audit Elementor widgets and disable any that are not used on the site - each active widget adds CSS/JS "
    "to the page load. Fourth, install an asset optimization plugin such as Asset CleanUp or Perfmatters to "
    "conditionally load scripts only on pages that need them, rather than globally. Fifth, consider lazy-loading "
    "below-fold images using the native loading='lazy' attribute or a plugin that adds it automatically.", body))
story.append(Spacer(1,8))

# --- P2 ---
story.append(Paragraph("P2 | Performance | 5 Render-Blocking CSS Resources Delay First Paint", h2))
story.append(Paragraph(
    "<b>What was found:</b> Five CSS files are loaded in the document head without the defer or async "
    "attribute, causing the browser to block rendering until all five are downloaded and parsed. The "
    "blocking resources are: Font Awesome all.min.css (the complete icon library), Font Awesome "
    "v4-shims.min.css (backward compatibility for older icon names), Jeg Elementor Kit CSS (a theme "
    "extension stylesheet), Elementor frontend CSS (the core Elementor rendering styles), and a "
    "post-specific Elementor stylesheet. Together, these contribute to a First Contentful Paint (FCP) "
    "of 2,196 ms, which is near the 2,500 ms threshold where Google considers the experience 'poor'.", body))
story.append(Paragraph("<b>Impact:</b> High - Render-blocking resources are the primary cause of slow perceived page load. Users see a blank white screen for over 2 seconds, which significantly increases bounce rates.", body))
story.append(Paragraph(
    "<b>How to fix it:</b> The most effective approach is to install a performance optimization plugin "
    "that handles CSS deferral automatically. WP Rocket, LiteSpeed Cache, and FlyingPress all offer "
    "one-click options to 'Optimize CSS Delivery' or 'Defer non-critical CSS.' These plugins identify "
    "above-the-fold CSS, inline it in the HTML, and defer the remaining stylesheets using the "
    "media='print' onload pattern. Alternatively, if you prefer manual optimization, you can extract "
    "critical CSS for the above-fold content using a tool like CriticalCSS, inline those rules in a "
    "style tag in the document head, and add media='print' onload=\"this.media='all'\" to the remaining "
    "link tags. Elementor 3.x also includes experimental CSS printing optimization features in "
    "Settings > Experiments that can reduce the number of render-blocking stylesheets.", body))
story.append(Spacer(1,8))

# --- P3 ---
story.append(Paragraph("P3 | Performance | 64 Network Requests Exceed 60-Request Budget", h2))
story.append(Paragraph(
    "<b>What was found:</b> The initial page load of cliqchef.ai triggers 64 HTTP network requests, "
    "exceeding the 60-request budget. This is a direct consequence of the WordPress/Elementor "
    "architecture, which loads separate CSS and JS files for each active widget, theme component, "
    "and plugin. Specifically, the page loads Font Awesome (2 CSS files), Jeg Elementor Kit, "
    "Elementor frontend and pro modules, Google Fonts, jQuery, and multiple third-party scripts. "
    "Each additional request adds latency due to HTTP connection setup, TLS negotiation, and "
    "server processing time. On HTTP/2 connections, requests are multiplexed which reduces the "
    "per-request cost, but on HTTP/1.1 connections (still used by some mobile carriers and older "
    "browsers), each request requires a separate TCP connection or waits for a connection slot "
    "in the browser's connection pool (typically 6 concurrent connections per hostname).", body))
story.append(Paragraph("<b>Impact:</b> High - Excessive requests increase Time to Interactive (TTI) and consume mobile data allowance. Each request adds 50-200ms of overhead depending on network conditions.", body))
story.append(Paragraph(
    "<b>How to fix it:</b> The primary strategy is to reduce the number of individual files the browser "
    "must fetch. Install a performance plugin that combines and minifies CSS and JS files - WP Rocket, "
    "LiteSpeed Cache, and FastVelocity Minify all offer this feature. When CSS files are combined into "
    "a single stylesheet and JS files into a single script, the browser needs far fewer HTTP requests. "
    "Additionally, audit your active Elementor widgets and disable any that are not used on the site, "
    "as each widget typically registers its own CSS/JS file. Remove unused Font Awesome icon subsets "
    "by switching to a plugin that loads only the icons actually used on the page (e.g., Font Awesome "
    "Optimize). Finally, ensure your server supports HTTP/2 so that multiplexing can reduce the "
    "per-request connection overhead. These changes can reduce the request count from 64 to "
    "approximately 20-30.", body))
story.append(Spacer(1,8))

# --- P4 ---
story.append(Paragraph("P4 | Performance | Page Load Time 9,743ms Exceeds 5,000ms Budget", h2))
story.append(Paragraph(
    "<b>What was found:</b> The full page load time for cliqchef.ai is approximately 9,743ms "
    "(with observed variation up to 10,404ms), which is nearly double the 5,000ms budget. "
    "The navigation timing breakdown reveals the specific bottleneck: DOM parsing takes 4,468ms "
    "(46% of total time), and DOMContentLoaded fires at 5,550ms. This indicates the browser is "
    "spending significant time parsing and executing the heavy DOM structure that Elementor generates "
    "with its deeply nested containers and widgets. The server-side response is reasonable (TTFB "
    "757ms), and the TCP/SSL overhead is normal for a remote server. The bottleneck is entirely "
    "on the client side: too much HTML, too many scripts executing during DOM parsing, and too "
    "many deferred scripts waiting to run after DOMContentLoaded.", body))
story.append(Paragraph("<b>Impact:</b> High - A 10-second page load is classified as 'poor' by Google's Core Web Vitals assessment and will directly harm search rankings. Users on mobile devices or slow connections will experience an even worse load time (15-20 seconds on 3G).", body))
story.append(Paragraph(
    "<b>How to fix it:</b> Since the bottleneck is DOM parsing (4,468ms), the focus should be on "
    "reducing the amount of HTML the browser must process. First, simplify the Elementor page "
    "structure by reducing unnecessary nesting - Elementor often creates deeply nested containers "
    "that inflate the DOM node count. Use the 'Flatten' option in Elementor's container settings "
    "where available. Second, defer all non-critical JavaScript using a performance plugin's "
    "'Delay JS Execution' feature (WP Rocket and FlyingPress both offer this). This moves script "
    "execution from the critical parsing path to after the page is interactive. Third, consider "
    "implementing server-side caching (page caching) so that the server returns a pre-rendered "
    "HTML response without executing PHP on every request, which reduces TTFB and allows the "
    "browser to start parsing sooner. Fourth, if the site uses Google Tag Manager or analytics "
    "scripts, delay their loading until after the page becomes interactive (user interaction or "
    "a 3-second timeout). Combined, these optimizations can reduce page load time to "
    "approximately 3-5 seconds.", body))
story.append(Spacer(1,8))

# --- S1 ---
story.append(Paragraph("S1 | SEO | Missing Meta Description Tag", h2))
story.append(Paragraph(
    "<b>What was found:</b> The home page of cliqchef.ai does not include a meta description tag. "
    "This tag provides the snippet text that search engines display beneath the page title in search "
    "result pages (SERPs). Without it, Google will auto-generate a snippet from the page content, "
    "which often results in truncated, irrelevant, or generic text that fails to communicate the "
    "site's value proposition. This directly reduces click-through rates (CTR) from search results, "
    "as users are less likely to click on a result with a poor or missing description.", body))
story.append(Paragraph("<b>Impact:</b> High - A missing meta description can reduce CTR from search results by 15-30% compared to a well-crafted description. It also means you have zero control over how your site appears in Google.", body))
story.append(Paragraph(
    "<b>How to fix it:</b> If you have an SEO plugin installed (Yoast SEO, Rank Math, or All in One SEO), "
    "navigate to the home page settings in the plugin and enter a meta description between 50 and 160 "
    "characters. For example: 'CliqChef AI - Transform your cooking with intelligent recipe recommendations "
    "and personalized meal planning powered by artificial intelligence.' If no SEO plugin is installed, "
    "install Rank Math (free) or Yoast SEO (free) from the WordPress plugin directory, then configure the "
    "home page meta description in the plugin's settings panel. This fix takes approximately 5 minutes and "
    "immediately gives you control over your search snippet.", body))
story.append(Spacer(1,8))

# --- S2 ---
story.append(Paragraph("S2 | SEO | Missing h1 Tag (No Top-Level Heading)", h2))
story.append(Paragraph(
    "<b>What was found:</b> The page does not contain an h1 element. The h1 tag is the most important "
    "on-page SEO signal, communicating the primary topic of the page to search engine crawlers. While "
    "the page does use h2 and h5 tags for section headings, the absence of an h1 means there is no "
    "clear top-level heading that tells Google what this page is about. This is a common oversight in "
    "Elementor-built sites where the hero headline is often set as an h2 for visual sizing reasons, "
    "but best practice requires exactly one h1 per page that matches the page's primary keyword target.", body))
story.append(Paragraph("<b>Impact:</b> High - Without an h1, search engines have a weaker signal about the page's topic, which can reduce ranking potential for target keywords.", body))
story.append(Paragraph(
    "<b>How to fix it:</b> In the Elementor editor, select the hero headline widget on the home page. "
    "In the Content tab, verify the text content is your primary heading (e.g., the site name or tagline). "
    "Then go to the Advanced tab > HTML Tag and change the value from its current setting (likely h2) to h1. "
    "This is a single dropdown change that takes approximately 2 minutes. If the visual size changes "
    "unwantedly after switching to h1, add custom CSS to the widget to maintain the desired font size "
    "and weight while keeping the correct semantic tag. Ensure there is only one h1 on the page.", body))
story.append(Spacer(1,8))

# ═══════════════════════════════════════════
# 3. MEDIUM PRIORITY ISSUES
# ═══════════════════════════════════════════
story.append(section_header("3. Medium Priority Issues"))
story.append(hr())
story.append(Paragraph(
    "These four issues affect accessibility compliance and social media visibility. While they do not "
    "cause immediate usability failures, they represent missed opportunities and potential compliance "
    "gaps, particularly for organizations that need to meet WCAG 2.1 AA standards or maintain strong "
    "social media presence.", body))
story.append(Spacer(1,6))

# --- A1 ---
story.append(Paragraph("A1 | Accessibility | Missing main Landmark (No &lt;main&gt; Element)", h2))
story.append(Paragraph(
    "<b>What was found:</b> The site does not use a &lt;main&gt; element or an element with role='main'. "
    "Screen readers use the main landmark to provide a keyboard shortcut that jumps directly to the "
    "page's primary content, bypassing the navigation and header. Without this landmark, assistive "
    "technology users must tab through every element in the header and navigation before reaching the "
    "actual content. On a page with a complex navigation bar, this can mean pressing Tab 20-30 times "
    "before reaching the first meaningful content. This is a WCAG 2.1 best practice violation under "
    "criterion 1.3.1 (Info and Relationships) and is flagged by automated accessibility scanners "
    "such as axe-core.", body))
story.append(Paragraph("<b>Impact:</b> Medium - Screen reader users experience significant navigation friction. Not a hard WCAG failure but a widely recognized best practice.", body))
story.append(Paragraph(
    "<b>How to fix it:</b> In Elementor, edit the home page and select the outermost container that "
    "wraps all primary content (the section containing the hero, features, testimonials, etc.). In the "
    "container's Advanced tab > HTML Tag, change the value from the default (likely 'div') to 'main'. "
    "This tells the browser and assistive technologies that this section contains the primary content of "
    "the page. If your theme uses a custom wrapper, you can also add role='main' as an HTML attribute. "
    "This fix takes approximately 10 minutes and immediately improves the page's accessibility profile "
    "for screen reader users.", body))
story.append(Spacer(1,8))

# --- A2 ---
story.append(Paragraph("A2 | Accessibility | Heading Hierarchy Skips (h2 to h5)", h2))
story.append(Paragraph(
    "<b>What was found:</b> The audit detected heading level skips from h2 directly to h5 at two "
    "locations on the page. Proper heading hierarchy (h1, h2, h3, h4, h5) is essential for screen "
    "reader navigation because users often jump between heading levels using keyboard shortcuts (H key "
    "for next heading, 2 for next h2, 3 for next h3, etc.). Skipping levels (e.g., going from h2 to h5) "
    "creates confusion about the document's organizational structure - screen reader users may think "
    "they missed content or that the page structure is broken. This is a common issue in Elementor-built "
    "sites where heading widgets are chosen based on their default visual appearance (font size) rather "
    "than their semantic meaning in the document outline.", body))
story.append(Paragraph("<b>Impact:</b> Medium - Screen reader users lose structural navigation cues. Also affects SEO (search engines use heading hierarchy to understand content structure).", body))
story.append(Paragraph(
    "<b>How to fix it:</b> Review all heading elements on the page in the Elementor editor. For each "
    "heading, determine its correct level in the document outline: the page title should be h1 (per S2), "
    "major section titles should be h2, sub-sections within those should be h3, and so on. Change the "
    "HTML Tag in each widget's Advanced tab to match the correct semantic level. If the visual "
    "appearance changes unwantedly, use Elementor's Typography controls in the Style tab to set the "
    "desired font size, weight, and color independently of the HTML tag. The principle is: use the "
    "correct semantic tag for structure, and CSS for visual styling. This requires a content audit of "
    "all heading elements but is straightforward within the Elementor editor.", body))
story.append(Spacer(1,8))

# --- S3 ---
story.append(Paragraph("S3 | SEO | Missing Open Graph Tags for Social Sharing", h2))
story.append(Paragraph(
    "<b>What was found:</b> The page lacks Open Graph (og:) meta tags, which control how content "
    "appears when shared on social media platforms such as Facebook, LinkedIn, and Twitter/X. Without "
    "OG tags, these platforms will guess the preview title, description, and image from the page content, "
    "often resulting in unattractive or irrelevant previews. For example, Facebook might choose a random "
    "image from the page as the share image, or display a truncated version of the first paragraph as "
    "the description. This significantly reduces the visual appeal and click-through rate of shared links, "
    "undermining any social media marketing efforts.", body))
story.append(Paragraph("<b>Impact:</b> Medium - Poor social sharing appearance reduces organic reach and undermines marketing campaigns. Does not affect search rankings directly.", body))
story.append(Paragraph(
    "<b>How to fix it:</b> Most WordPress SEO plugins automatically generate Open Graph tags from the "
    "meta title and description. If you are using Yoast SEO, navigate to Social > Facebook and enable "
    "Open Graph metadata, then set the fallback image in the plugin's social settings. If using Rank Math, "
    "go to General Settings > Social Meta and enable OpenGraph, then configure the default social share "
    "image. At minimum, the following tags should be present: og:title (the page title), og:description "
    "(matching or extending the meta description), og:image (a high-quality 1200x630px image representing "
    "the site), og:url (the canonical page URL), and og:type (set to 'website' for the home page). "
    "For Twitter/X, also add twitter:card='summary_large_image'. This fix requires no code changes and "
    "can be completed in under 15 minutes with an SEO plugin.", body))
story.append(Spacer(1,8))

# --- S4 ---
story.append(Paragraph("S4 | SEO | Heading Hierarchy Skips Affect Search Structure", h2))
story.append(Paragraph(
    "<b>What was found:</b> In addition to the accessibility impact described in A2, the heading "
    "skips from h2 directly to h5 also affect how search engines understand the page structure. "
    "Google's crawlers use heading hierarchy to build an internal outline of the page's content, "
    "determining which sections are top-level and which are sub-sections. When headings skip levels, "
    "crawlers may interpret the h5 content as a deeply nested sub-section of a non-existent h3 and h4, "
    "rather than as a peer-level heading. This can dilute the SEO weight of important content that is "
    "marked up with inappropriately deep heading levels.", body))
story.append(Paragraph("<b>Impact:</b> Medium - Heading skips confuse search engine crawlers about content hierarchy, potentially reducing the SEO weight of important content sections.", body))
story.append(Paragraph(
    "<b>How to fix it:</b> This is the same fix as A2. Correct the heading hierarchy to follow a "
    "sequential order (h1, h2, h3) and use CSS for visual styling. Once the heading levels are "
    "semantically correct, both the accessibility and SEO impacts are resolved simultaneously.", body))
story.append(Spacer(1,8))

# ═══════════════════════════════════════════
# 4. LOW PRIORITY ISSUES
# ═══════════════════════════════════════════
story.append(section_header("4. Low Priority Issues"))
story.append(hr())
story.append(Paragraph(
    "This single low-priority issue is a minor cosmetic concern that does not affect functionality "
    "or accessibility, but should be cleaned up during routine maintenance to eliminate console errors "
    "and ensure reliable font rendering.", body))
story.append(Spacer(1,6))

# --- U1 ---
story.append(Paragraph("U1 | UX | CORS Error on Cross-Origin Font Loading", h2))
story.append(Paragraph(
    "<b>What was found:</b> A CORS (Cross-Origin Resource Sharing) error was detected in the browser "
    "console when the page attempted to load a font file from cc.abhisheksajan.com. This indicates that "
    "the font files are hosted on a different domain than the main site (cliqchef.ai), and the font "
    "host server is not returning the Access-Control-Allow-Origin HTTP header that permits the browser "
    "to use the font. Browsers enforce CORS for font files as a security measure - if the header is "
    "missing, the browser rejects the font and falls back to system fonts. While this does not break "
    "any visible functionality, it can cause a Flash of Unstyled Text (FOUT) where the page initially "
    "displays text in a system font and then re-renders once a fallback font loads, creating a visible "
    "layout shift that degrades perceived performance.", body))
story.append(Paragraph("<b>Impact:</b> Low - Does not break functionality. May cause brief visual inconsistency (FOUT) and produces a console error that could mask other issues during debugging.", body))
story.append(Paragraph(
    "<b>How to fix it:</b> On the font host server (cc.abhisheksajan.com), add the HTTP response header "
    "Access-Control-Allow-Origin: * for font file types (woff2, woff, ttf, otf, eot). This can be done "
    "via server configuration. For Apache, add the following to the .htaccess file or virtual host "
    "configuration: &lt;FilesMatch \"\\.(woff2|woff|ttf|otf|eot)$\"&gt; Header set Access-Control-Allow-Origin "
    "\"*\" &lt;/FilesMatch&gt;. For Nginx, add a location block with: add_header Access-Control-Allow-Origin "
    "\"*\". If you do not have server-level access, contact your hosting provider and request that CORS "
    "headers be enabled for font file types on the cc.abhisheksajan.com domain. This fix takes approximately "
    "15 minutes with server access.", body))
story.append(Spacer(1,8))

# ═══════════════════════════════════════════
# 5. CONSOLIDATED REMEDIATION ROADMAP
# ═══════════════════════════════════════════
story.append(section_header("5. Consolidated Remediation Roadmap"))
story.append(hr())
story.append(Paragraph(
    "The following roadmap orders fixes by their return on investment (impact divided by effort). "
    "Items in Phase 1 deliver the greatest improvement for the least development time and should be "
    "completed first. Phase 2 items require more significant technical work but address the largest "
    "performance bottlenecks. Phase 3 is a maintenance task that can be scheduled alongside other "
    "content updates.", body))
story.append(Spacer(1,6))

story.append(Paragraph("Phase 1: Quick Wins (5-15 minutes each, immediate impact)", h3))
roadmap1 = [
    ["S1", "Add meta description", "SEO plugin settings", "5 min", "Higher CTR from search"],
    ["S2", "Add h1 tag", "Elementor HTML Tag dropdown", "2 min", "Stronger SEO signal"],
    ["A1", "Add main landmark", "Elementor HTML Tag = main", "10 min", "Screen reader nav"],
    ["S3", "Add Open Graph tags", "SEO plugin social settings", "10 min", "Better social previews"],
    ["U1", "Fix CORS for fonts", "Server .htaccess / Nginx", "15 min", "No console errors"],
]
rm1_h = [Paragraph("<b>ID</b>", th_s), Paragraph("<b>Fix</b>", th_s), Paragraph("<b>Where</b>", th_s), Paragraph("<b>Time</b>", th_s), Paragraph("<b>Benefit</b>", th_s)]
rm1_d = [[Paragraph(r[0], td_c), Paragraph(r[1], td_s), Paragraph(r[2], td_s), Paragraph(r[3], td_c), Paragraph(r[4], td_s)] for r in roadmap1]
rm1_t = Table([rm1_h] + rm1_d, colWidths=[CONTENT_W*0.06, CONTENT_W*0.22, CONTENT_W*0.28, CONTENT_W*0.10, CONTENT_W*0.34])
rm1_t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), HEADER_FILL),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F0FDF4')),
    ('GRID', (0,0), (-1,-1), 0.5, BORDER),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
    ('RIGHTPADDING', (0,0), (-1,-1), 6),
]))
story.append(rm1_t)
story.append(Spacer(1,10))

story.append(Paragraph("Phase 2: Performance Optimization (1-4 hours, high impact)", h3))
roadmap2 = [
    ["P1", "Reduce page weight", "Brotli + WebP + widget audit + lazy loading", "2-4 hrs", "Faster mobile load"],
    ["P2", "Eliminate render-blocking CSS", "Perf plugin or critical CSS extraction", "1-2 hrs", "Faster first paint"],
    ["P3", "Reduce network requests", "Combine/minify CSS+JS, HTTP/2, disable unused widgets", "1-2 hrs", "Faster TTI"],
    ["P4", "Reduce page load time", "Defer JS, simplify DOM, page caching, delay analytics", "2-4 hrs", "Under 5s load"],
]
rm2_h = [Paragraph("<b>ID</b>", th_s), Paragraph("<b>Fix</b>", th_s), Paragraph("<b>How</b>", th_s), Paragraph("<b>Time</b>", th_s), Paragraph("<b>Benefit</b>", th_s)]
rm2_d = [[Paragraph(r[0], td_c), Paragraph(r[1], td_s), Paragraph(r[2], td_s), Paragraph(r[3], td_c), Paragraph(r[4], td_s)] for r in roadmap2]
rm2_t = Table([rm2_h] + rm2_d, colWidths=[CONTENT_W*0.06, CONTENT_W*0.20, CONTENT_W*0.40, CONTENT_W*0.10, CONTENT_W*0.24])
rm2_t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), HEADER_FILL),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#FFF5F5')),
    ('GRID', (0,0), (-1,-1), 0.5, BORDER),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
    ('RIGHTPADDING', (0,0), (-1,-1), 6),
]))
story.append(rm2_t)
story.append(Spacer(1,10))

story.append(Paragraph("Phase 3: Content Audit (30-60 minutes, paired with content updates)", h3))
roadmap3 = [
    ["A2/S4", "Fix heading hierarchy", "Audit all headings, use CSS for styling", "30-60 min", "A11y + SEO compliance"],
]
rm3_h = [Paragraph("<b>ID</b>", th_s), Paragraph("<b>Fix</b>", th_s), Paragraph("<b>How</b>", th_s), Paragraph("<b>Time</b>", th_s), Paragraph("<b>Benefit</b>", th_s)]
rm3_d = [[Paragraph(r[0], td_c), Paragraph(r[1], td_s), Paragraph(r[2], td_s), Paragraph(r[3], td_c), Paragraph(r[4], td_s)] for r in roadmap3]
rm3_t = Table([rm3_h] + rm3_d, colWidths=[CONTENT_W*0.08, CONTENT_W*0.20, CONTENT_W*0.38, CONTENT_W*0.12, CONTENT_W*0.22])
rm3_t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), HEADER_FILL),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#FFFBEB')),
    ('GRID', (0,0), (-1,-1), 0.5, BORDER),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
    ('RIGHTPADDING', (0,0), (-1,-1), 6),
]))
story.append(rm3_t)
story.append(Spacer(1,12))

# ═══════════════════════════════════════════
# 6. COMPLETE ISSUE MATRIX
# ═══════════════════════════════════════════
story.append(section_header("6. Complete Issue Matrix"))
story.append(hr())
story.append(Paragraph(
    "The table below provides a single-page reference of all 11 issues with their category, priority, "
    "and estimated remediation effort. Use this as a quick reference when assigning fixes to team members "
    "or planning sprint backlogs.", body))
story.append(Spacer(1,6))

matrix = [
    ["P1", "Performance", "Page weight 1,543 KB exceeds budget", "High", "Medium"],
    ["P2", "Performance", "5 render-blocking CSS resources", "High", "Medium"],
    ["P3", "Performance", "64 network requests (budget: 60)", "High", "Medium"],
    ["P4", "Performance", "Page load 9,743ms (budget: 5,000ms)", "High", "Medium"],
    ["S1", "SEO", "Missing meta description tag", "High", "Low"],
    ["S2", "SEO", "Missing h1 tag", "High", "Low"],
    ["A1", "Accessibility", "Missing main landmark", "Medium", "Low"],
    ["A2", "Accessibility", "Heading hierarchy skips (h2 to h5)", "Medium", "Low"],
    ["S3", "SEO", "Missing Open Graph tags", "Medium", "Low"],
    ["S4", "SEO", "Heading hierarchy skips (SEO impact)", "Medium", "Low"],
    ["U1", "UX", "CORS error on font loading", "Low", "Low"],
]
mx_h = [Paragraph("<b>ID</b>", th_s), Paragraph("<b>Category</b>", th_s), Paragraph("<b>Issue</b>", th_s), Paragraph("<b>Priority</b>", th_s), Paragraph("<b>Effort</b>", th_s)]
mx_d = []
for r in matrix:
    pc = {"High": PRIORITY_HIGH, "Medium": PRIORITY_MED, "Low": PRIORITY_LOW}.get(r[3], TEXT_MUTED)
    ec = {"High": PRIORITY_HIGH, "Medium": PRIORITY_MED, "Low": PRIORITY_LOW}.get(r[4], TEXT_MUTED)
    mx_d.append([
        Paragraph(r[0], ParagraphStyle("CB", parent=td_c, fontName="NotoSerifSC-Bold")),
        Paragraph(r[1], td_c),
        Paragraph(r[2], td_s),
        Paragraph(f'<font color="{pc}"><b>{r[3]}</b></font>', td_c),
        Paragraph(f'<font color="{ec}"><b>{r[4]}</b></font>', td_c),
    ])
mx_t = Table([mx_h] + mx_d, colWidths=[CONTENT_W*0.06, CONTENT_W*0.13, CONTENT_W*0.49, CONTENT_W*0.14, CONTENT_W*0.14])
# Alternate row colors
mx_styles = [
    ('BACKGROUND', (0,0), (-1,0), HEADER_FILL),
    ('GRID', (0,0), (-1,-1), 0.5, BORDER),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
    ('RIGHTPADDING', (0,0), (-1,-1), 6),
]
for i in range(1, len(mx_d) + 1):
    bg = TABLE_STRIPE if i % 2 == 0 else colors.white
    mx_styles.append(('BACKGROUND', (0,i), (-1,i), bg))
mx_t.setStyle(TableStyle(mx_styles))
story.append(mx_t)

# ─── Build PDF ───
doc.build(story)
print(f"PDF generated: {output_path}")
print(f"File size: {os.path.getsize(output_path) / 1024:.0f} KB")
