---
name: local-seo-audit
description: >
  Comprehensive local SEO and Google Maps audit for local service businesses.
  Analyzes Google Business Profile, local pack rankings, organic positions,
  competitor landscape, schema markup, page speed, technical SEO, and citation
  consistency. Captures screenshots of key findings via browser automation.
  Produces a client-ready HTML report with embedded evidence screenshots.
  Use when auditing a local business website for local search performance.
argument-hint: [domain] [city, state]
arguments: [domain, location]
disable-model-invocation: true
effort: high
allowed-tools:
  - WebFetch
  - WebSearch
  - Write
  - Read
  - Bash(mkdir *)
  - Bash(cp *)
  - Bash(start *)
  - Bash(gh *)
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
  - mcp__claude-in-chrome__tabs_context_mcp
  - mcp__claude-in-chrome__tabs_create_mcp
  - mcp__claude-in-chrome__navigate
  - mcp__claude-in-chrome__computer
  - mcp__claude-in-chrome__get_page_text
  - mcp__claude-in-chrome__read_page
  - mcp__chrome-devtools__take_screenshot
  - mcp__chrome-devtools__navigate_page
  - mcp__chrome-devtools__list_pages
  - mcp__dfs-mcp__serp_organic_live_advanced
  - mcp__dfs-mcp__dataforseo_labs_google_competitors_domain
  - mcp__dfs-mcp__backlinks_summary
  - mcp__semrush__organic_research
  - mcp__semrush__overview_research
  - mcp__semrush__execute_report
  - mcp__semrush__get_report_schema
---

# Local SEO & Google Maps Audit

You are conducting a comprehensive local SEO audit for **$domain** located in **$location**.

## Setup

1. Create the working directory and screenshots folder:
   ```
   mkdir -p screenshots
   ```
2. Initialize browser: call `mcp__claude-in-chrome__tabs_context_mcp` with `createIfEmpty: true`, then create a new tab with `mcp__claude-in-chrome__tabs_create_mcp`

## CRITICAL: How to Take and Save Screenshots

Throughout this audit, you MUST capture screenshots at key moments. Screenshots are the visual evidence that makes the report credible. **Do NOT skip screenshots.** The HTML report embeds these files — without them the report has broken images.

### Screenshot Procedure (use this EVERY time instructions say "SCREENSHOT")

**Primary method — `mcp__chrome-devtools__take_screenshot`:**

This tool saves screenshots directly to disk. It is the ONLY reliable way to save screenshots to files.

1. First, load the tool (once per session):
   ```
   ToolSearch query: "select:mcp__chrome-devtools__take_screenshot"
   ```

2. Make sure the correct page is visible in the browser tab you want to capture.

3. Take and save the screenshot in one call:
   ```
   mcp__chrome-devtools__take_screenshot
     filePath: "screenshots/{filename}.png"
   ```
   Use a relative path — it saves relative to the current working directory.

4. Verify the file was saved:
   ```bash
   ls -la screenshots/{filename}.png
   ```

**If full-page capture is needed** (e.g., long PageSpeed results), add `fullPage: true`:
```
mcp__chrome-devtools__take_screenshot
  filePath: "screenshots/{filename}.png"
  fullPage: true
```

**Fallback — if chrome-devtools is unavailable:**
Ask the user: "I've navigated to [page]. Please take a screenshot and save it as `screenshots/{filename}.png`"

### Required Screenshots Checklist

You MUST capture at minimum these screenshots during the audit. After each one, verify the file exists.

| Phase | Filename | What to Capture |
|-------|----------|----------------|
| 2 | `screenshots/serp-{keyword-1}.png` | Google Maps local pack for primary keyword |
| 2 | `screenshots/serp-{keyword-2}.png` | Google Maps local pack for secondary keyword |
| 4 | `screenshots/gbp-listing-primary.png` | Client's main GBP listing overview |
| 4 | `screenshots/gbp-duplicates.png` | All listings if duplicates found |
| 5 | `screenshots/competitor-{name-1}.png` | Top competitor GBP listing |
| 5 | `screenshots/competitor-{name-2}.png` | Second competitor GBP listing |
| 6 | `screenshots/schema-client.png` | Google Rich Results Test for client |
| 6 | `screenshots/schema-competitor.png` | Rich Results Test for top competitor |
| 7 | `screenshots/pagespeed-cwv.png` | PageSpeed Insights CWV section |
| 7 | `screenshots/pagespeed-lighthouse.png` | Lighthouse scores section |
| 8 | `screenshots/citation-{source}-issue.png` | Any NAP mismatch found (if applicable) |

At the end of each phase that requires screenshots, run:
```bash
ls -la screenshots/
```
to confirm files are accumulating. If a screenshot is missing, go back and capture it before moving to the next phase.

## Phase 1: Business Discovery

- Fetch `https://www.$domain/` and `https://www.$domain/sitemap` (or sitemap.xml) via WebFetch
- Extract: business name, full address, phone, email, services offered, service areas, hours
- Identify all page types: service pages, location/area pages, blog posts, specialty pages
- Count total pages by type

## Phase 2: Google Maps / Local Pack Analysis

Determine 8-10 high-value keywords based on the business type and services discovered in Phase 1. Use patterns like:
- `[primary service] [city]` (e.g., "concrete contractor tulare ca")
- `[secondary service] [city]` (e.g., "stamped concrete tulare")
- `[service] near me` from the client's city
- `[service] [neighboring cities]`

For each keyword, use `mcp__dfs-mcp__serp_organic_live_advanced` with:
- `language_code: "en"`
- `location_name: "[City],[State],United States"`
- `depth: 20`

Record for each keyword: local pack position (or "Not showing"), top 3 local pack winners with review counts, and any Local Services Ads.

**SCREENSHOT:** Navigate to Google Maps in the browser, search 2-3 key terms, and take screenshots showing where the client ranks (or doesn't) in the local pack. Save as `screenshots/serp-{keyword-slug}.png`.

## Phase 3: Organic Search Rankings

From the same SERP data collected in Phase 2, extract organic positions for the client's domain. Note keywords where the client ranks organically but NOT in the local pack — this pattern indicates GBP issues rather than website issues.

## Phase 4: Google Business Profile Audit

Search Google Maps in the browser for the exact business name + phone number to find ALL GBP listings.

**Critical: Check for duplicate listings.** Search for:
- Exact business name
- Business name + city
- Phone number
- Variations of the name

For EACH listing found, capture via `get_page_text` and screenshots:
- Business name (exact), review count, rating, address (or "none"), primary category
- Secondary categories (check About tab)
- Google Posts (latest date), review responses (does owner respond?), photo activity
- Business description, services section, hours, attributes, payments
- Whether it can appear in local pack (has physical address = yes)

**SCREENSHOT:** Each GBP listing overview. If duplicates found, screenshot the search results page showing all listings together. Save as `screenshots/gbp-listing-{a|b|c}.png`.

If duplicate listings are found, this becomes the #1 critical finding. Calculate total reviews across all listings and note the split.

## Phase 5: Competitor Research

Use `mcp__dfs-mcp__dataforseo_labs_google_competitors_domain` to find organic keyword competitors:
- `target: "$domain"`
- `exclude_top_domains: true`
- `limit: 15`

Then search Google Maps for the top 5-8 direct competitors to get:
- Review count, rating, GBP listing count (check for their duplicates too)
- Address/location (to understand proximity advantage)

Use WebFetch on the top 3-4 competitor websites to analyze:
- Schema markup, content strategy, pricing transparency, location pages, blog, certifications
- Unique differentiators

Build a comprehensive competitor comparison table.

**SCREENSHOT:** Top 2-3 competitor GBP listings. Save as `screenshots/competitor-{name}.png`.

## Phase 6: Website Technical SEO

### Schema Markup
Use WebFetch on the client's homepage to check for JSON-LD structured data. Also check a service page and a location page.

Navigate the browser to `https://search.google.com/test/rich-results` and test the client URL. Wait for results.
**SCREENSHOT:** The Rich Results Test results. Save as `screenshots/schema-client.png`.

Test the top competitor's URL for comparison.
**SCREENSHOT:** Save as `screenshots/schema-competitor.png`.

### On-Page SEO
Audit one key service page via WebFetch:
- Title tag, meta description, H1, content depth (word count), FAQ sections, pricing
- Image alt text quality, internal linking, breadcrumbs, map embed

### Location Pages
If the client has location pages, audit 2-3 for:
- Unique vs templated content, local keywords, embedded maps, local testimonials
- LocalBusiness schema per page

## Phase 7: Page Performance, Technical Audit & Core Web Vitals

### Step 1: Ask User for Technical Audit Data

Use AskUserQuestion to ask:

> "Do you have any of the following technical audit data to provide? These tools require paid accounts that I can't access directly, but their data significantly strengthens the report."
>
> Options:
> 1. **SEMrush Site Audit screenshot** — Shows Health Score, errors, warnings, top issues (crawlability, HTTPS, performance, internal linking, markup)
> 2. **Ahrefs Site Audit screenshot** — Shows Health Score, crawled URLs, errors/warnings/notices, top issues
> 3. **PageSpeed Insights screenshot** — Shows Core Web Vitals, Lighthouse scores
> 4. **I don't have any of these** — Skip to automated checks
>
> Allow multiple selections. If they select any, ask them to save the screenshot files to the working directory and provide the filenames.

### Step 2: Process User-Provided Technical Audit Data

If the user provides a **SEMrush Site Audit** screenshot, read the image and extract:
- **Site Health Score** (0-100%)
- **Errors count** (critical issues)
- **Warnings count** (important issues)
- **Notices count** (minor issues)
- **Top Issues** with affected page counts. Common SEMrush issues include:
  - X pages have duplicate title tags
  - X pages have duplicate meta descriptions
  - X pages returned 4XX status codes
  - X pages have broken internal links
  - X pages have slow load speed
  - X pages have no meta description
  - X images don't have alt attributes
  - X pages have duplicate content
  - X pages have redirect chains
  - Sitemap issues, robots.txt issues, HTTPS issues
  - Internal linking issues, crawl depth issues
  - Hreflang issues, canonical issues

Include all extracted data in the report under Section 3B: Technical Site Audit. Reference the screenshot image in the HTML report.

If the user provides an **Ahrefs Site Audit** screenshot, extract similarly:
- Health Score, crawled URLs, error/warning/notice counts
- Top issues with page counts (canonical-to-redirect, non-canonical in sitemap, 3XX receiving traffic, etc.)

If the user provides **PageSpeed Insights** data, extract:
- CWV pass/fail status
- Real user data: LCP, INP, CLS, FCP, TTFB
- Lighthouse lab scores: Performance, Accessibility, Best Practices, SEO
- Lab metrics: FCP, LCP, TBT, CLS, Speed Index

### Step 3: Automated PageSpeed Insights Test via Browser

**Always run this step** — even if the user provided a screenshot, fresh data confirms current state.

1. Get browser context: `mcp__claude-in-chrome__tabs_context_mcp` with `createIfEmpty: true`
2. Create a new tab: `mcp__claude-in-chrome__tabs_create_mcp`
3. Navigate to PageSpeed Insights: `mcp__claude-in-chrome__navigate` to `https://pagespeed.web.dev/`
4. Wait 2 seconds for page load
5. Find the URL input field using `mcp__claude-in-chrome__read_page` with `filter: "interactive"`
6. Click on the URL input field, then type the client URL: `mcp__claude-in-chrome__computer` with `action: type`, `text: "https://www.$domain/"`
7. Press Enter to start the analysis: `mcp__claude-in-chrome__computer` with `action: key`, `text: "Enter"`
8. **Wait for analysis to complete** — this takes 15-45 seconds. Use `mcp__claude-in-chrome__computer` with `action: wait`, `duration: 30`. Then check if results loaded by taking a screenshot. If still loading (spinner visible), wait another 15 seconds.
9. Once results are loaded, the page shows two sections:
   - **Top section:** "Discover what your real users are experiencing" — Core Web Vitals Assessment (Pass/Fail) with LCP, INP, CLS, FCP, TTFB
   - **Bottom section:** "Diagnose performance issues" — Lighthouse scores (Performance, Accessibility, Best Practices, SEO) with detailed lab metrics

10. **SCREENSHOT the CWV section:** Scroll to the top of results. Take screenshot. Save as `screenshots/pagespeed-cwv.png`

11. **Extract CWV data** using `mcp__claude-in-chrome__get_page_text`. Look for:
    - "Core Web Vitals Assessment: Passed" or "Failed"
    - LCP value and status (green/amber/red)
    - INP value and status
    - CLS value and status
    - FCP value and status
    - TTFB value and status

12. **Scroll down to Lighthouse scores section.** Take screenshot. Save as `screenshots/pagespeed-lighthouse.png`

13. **Extract Lighthouse data** from page text:
    - Performance score (0-100)
    - Accessibility score (0-100)
    - Best Practices score (0-100)
    - SEO score (0-100)
    - Lab metrics: FCP, LCP, Total Blocking Time, CLS, Speed Index

14. Record all data for the report. Classify each metric:
    - **Good (green):** LCP < 2.5s, CLS < 0.1, INP < 200ms, FCP < 1.8s, TTFB < 0.8s
    - **Needs Improvement (amber):** Between good and poor thresholds
    - **Poor (red):** LCP > 4.0s, CLS > 0.25, INP > 500ms, FCP > 3.0s, TTFB > 1.8s

### Step 4: Basic Automated Technical Checks

Regardless of whether user data was provided, perform these checks that Claude CAN do directly:

1. **Fetch robots.txt** — `WebFetch https://www.$domain/robots.txt` — check for blocked important paths
2. **Fetch sitemap** — `WebFetch https://www.$domain/sitemap.xml` — count pages, check structure
3. **Indexation estimate** — Use `WebSearch` with `site:$domain` to estimate indexed page count; compare against sitemap count
4. **Spot-check canonicals** — Fetch 5 key pages via WebFetch, check if canonical tags point to themselves or to redirects
5. **HTTPS check** — Verify the site loads on HTTPS and redirects from HTTP

## Phase 8: Citation Consistency Audit

This is a critical step for local SEO. Check the client's NAP (Name, Address, Phone) consistency across citation sources.

**Canonical NAP:** Use the primary GBP listing's name, address, and phone as the reference.

For each citation source listed in `${CLAUDE_SKILL_DIR}/citation-sources.md`:
1. Use WebFetch to search for the business on that platform
2. Extract the listed: name, address, phone, website URL
3. Compare against canonical NAP
4. Flag: exact match, partial match (minor variation), mismatch, or not found

Build a citation consistency table:

| Source | Name | Address | Phone | Website | Status |
|--------|:----:|:-------:|:-----:|:-------:|:------:|
| Google GBP | match/mismatch | match/mismatch | ... | ... | OK/Issue |

Calculate overall citation consistency score: (matching citations / total checked) x 100%.

Flag specific issues:
- Old addresses, wrong phone numbers, misspelled names, HTTP vs HTTPS website URLs
- Missing citations that competitors have
- Inconsistent business name formats

**SCREENSHOT:** Any citation listing showing a clear NAP mismatch. Save as `screenshots/citation-{source}-issue.png`.

## Phase 9: Compile Prioritized Action Plan

Organize ALL findings into a prioritized action plan:

### Critical (Do This Week)
- Duplicate GBP listings (if found)
- Major citation inconsistencies
- Missing GBP categories or services

### High Priority (Within 30 Days)
- Schema markup implementation
- Technical SEO fixes (canonical issues, sitemap cleanup)
- Page speed improvements
- GBP engagement gaps

### Medium Priority (30-60 Days)
- Content gaps (blog, enhanced location pages)
- Citation building for missing directories
- Competitive content strategies to adopt

### Ongoing
- Review generation, Google Posts, content publishing, ranking monitoring

Create a 90-day roadmap and success metrics table (current vs target).

## Phase 10: Generate HTML Report

Create a professional HTML report using the design template at `${CLAUDE_SKILL_DIR}/report-template.html` as reference for CSS styling. The report must include:

1. **Header:** Client business name, domain, audit date
2. **Executive Summary:** Top 3 issues, key stats (reviews, local pack appearances, health score)
3. **Section 1:** Google Maps / Local Pack — ranking tables with screenshots
4. **Section 2:** GBP Audit — listing comparison table, duplicate finding, screenshots
5. **Section 3:** Website Technical SEO — schema comparison, on-page audit
6. **Section 3A:** Page Performance — CWV data, Lighthouse scores (if available)
7. **Section 3B:** Technical Audit — health score, errors (if Ahrefs data provided)
8. **Section 4:** Citation Consistency — NAP comparison table, consistency score, screenshots
9. **Section 5:** Competitor Benchmarking — full comparison table with all competitors
10. **Section 6:** Prioritized Action Plan — tables by priority level
11. **Section 7:** 90-Day Roadmap — timeline visualization
12. **Section 8:** Quick Reference — what they do well + what needs to change

Embed ALL screenshots from the `screenshots/` folder at their relevant sections with descriptive captions.

Write the report to `LOCAL-SEO-AUDIT-REPORT.html` in the working directory. Open in browser for verification.

## Phase 11: Publish Report to GitHub Pages

Publish the completed report to `https://growtharchon.github.io/client-reports/` so the client can view it online.

### Step 1: Create a client subfolder name
Derive a URL-safe folder name from the business name or domain. Examples:
- `gvgconcrete.com` in Tulare → `gvg-concrete-tulare`
- `sbmobiledetailing.com` in San Marcos → `smith-bros-mobile-detailing`

Use lowercase, hyphens only, no special characters.

### Step 2: Clone the reports repo
```bash
TMPDIR=$(mktemp -d)
cd "$TMPDIR"
git clone https://github.com/growtharchon/client-reports.git
cd client-reports
```

### Step 3: Create the client folder and copy files
```bash
CLIENT_FOLDER="{client-folder-name}"
mkdir -p "$CLIENT_FOLDER"
```

Copy the HTML report as `index.html` (so it loads at the folder URL), the markdown report, and all screenshots:
```bash
cp "{working-directory}/LOCAL-SEO-AUDIT-REPORT.html" "$CLIENT_FOLDER/index.html"
cp "{working-directory}/LOCAL-SEO-AUDIT-REPORT.md" "$CLIENT_FOLDER/" 2>/dev/null
cp -r "{working-directory}/screenshots" "$CLIENT_FOLDER/" 2>/dev/null
```

Also copy any client-provided screenshot files from the working directory root:
```bash
cp "{working-directory}"/*.png "$CLIENT_FOLDER/" 2>/dev/null
cp "{working-directory}"/*.jpg "$CLIENT_FOLDER/" 2>/dev/null
```

### Step 4: Commit and push
```bash
git add -A
git commit -m "Add {business-name} - Local SEO & Google Maps Audit Report

- Comprehensive local SEO audit with Google Maps, GBP, and technical analysis
- Competitive benchmarking across local market competitors
- Citation consistency audit
- PageSpeed and technical SEO findings
- Prioritized action plan with 90-day roadmap"
git push origin main
```

### Step 5: Verify GitHub Pages deployment
```bash
# Check if Pages is enabled with legacy build
gh api repos/growtharchon/client-reports/pages 2>&1
```

If Pages is not configured, enable it:
```bash
gh api repos/growtharchon/client-reports/pages -X POST --input - <<EOF
{
  "build_type": "legacy",
  "source": { "branch": "main", "path": "/" }
}
EOF
```

Wait for the build to complete:
```bash
sleep 20
gh api repos/growtharchon/client-reports/pages/builds/latest 2>&1 | grep -o '"status":"[^"]*"'
```

### Step 6: Report the live URL to the user

The report is now live at:
```
https://growtharchon.github.io/client-reports/{client-folder-name}/
```

Tell the user the URL and confirm it's accessible.

## Output Checklist

Before finishing, verify:
- [ ] All 11 phases completed
- [ ] Screenshots captured for: GBP listings, SERP results, schema tests, PageSpeed, competitor GBPs, citation issues
- [ ] Citation consistency score calculated
- [ ] Competitor table includes ALL competitors found (primary + local)
- [ ] HTML report generated with embedded screenshots
- [ ] Action plan is prioritized with measurable targets
- [ ] Report opened in browser for user review
- [ ] Report published to GitHub Pages and live URL provided to user
