---
name: local-seo-audit
description: >
  Local SEO checklist audit for local service businesses. Checks the 16 highest-impact
  items from the Game Changers and Technical & Content tiers of the Local SEO Impact
  Checklist. Audits Google Business Profile via browser automation and website technical
  SEO via page fetching. Produces a checklist-style HTML scorecard report with
  pass/needs-work/fail status per item, evidence screenshots, and a prioritized action plan.
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
  - Bash(ls *)
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
---

# Local SEO Checklist Audit

You are conducting a local SEO checklist audit for **$domain** located in **$location**.

This audit checks the 16 highest-impact items from the Local SEO Impact Checklist, covering two tiers:
- **Game Changers** (9 items) — GBP and business fundamentals
- **Technical & Content** (7 items) — website-level checks

Each item is scored as **PASS**, **NEEDS WORK**, or **FAIL** with evidence and recommendations.

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

**If full-page capture is needed**, add `fullPage: true`:
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
| 2 | `screenshots/gbp-overview.png` | Client's GBP listing overview showing name, address, rating |
| 2 | `screenshots/gbp-categories.png` | GBP About tab showing primary + secondary categories |
| 2 | `screenshots/gbp-reviews.png` | Recent reviews section showing velocity |
| 2 | `screenshots/gbp-hours.png` | Business hours section |
| 2 | `screenshots/gbp-photos.png` | Photos tab showing count and recency |
| 3 | `screenshots/serp-ads.png` | SERP showing LSA/ad placements for primary keyword |
| 4 | `screenshots/pagespeed-mobile.png` | PageSpeed Insights mobile results |

At the end of each phase that requires screenshots, run:
```bash
ls -la screenshots/
```
to confirm files are accumulating. If a screenshot is missing, go back and capture it before moving to the next phase.

---

## Phase 1: Business Discovery

- Fetch `https://www.$domain/` and `https://www.$domain/sitemap.xml` (or sitemap) via WebFetch
- Extract: business name, full address, phone, services offered, service areas, hours
- Identify all page types: service pages, location/area pages, blog posts
- Count total pages by type
- Build a list of the business's core services (needed for later checks)

---

## Phase 2: Google Business Profile Checklist (Game Changers)

This phase checks GBP-related items from the Game Changers tier using browser automation.

### Step 1: Find the GBP Listing

Search Google Maps in the browser for the exact business name to find the GBP listing.

### Step 2: Check Item #01 — Visible Address (Brick-and-Mortar) vs Hidden SAB

- Look at the GBP listing for a visible physical address
- If the address is shown: the business has a storefront/office listing (stronger for Local Pack)
- If the address is hidden and only a service area is shown: it's a Service Area Business (SAB)
- **Score:** PASS if visible address shown, NEEDS WORK if SAB (note: SAB is valid but generally weaker for pack rankings)
- **Evidence:** Note whether address is displayed or hidden

### Step 3: Check Item #02 — Physical Location Within City Boundaries

- Read the address from the GBP listing
- Compare the city in the address to the target city ($location)
- If the address is in the target city: strong ranking boost for city-name keywords
- If the address is outside the city or in a suburb: weaker positioning for city keywords
- **Score:** PASS if inside target city, NEEDS WORK if nearby but outside, FAIL if address is in a different city
- **Evidence:** Note the listed address and target city

### Step 4: Check Item #04 — Keywords in Business Name

- Read the exact business name from the GBP listing
- Check if it contains:
  - Service keywords (e.g., "cleaning", "plumbing", "concrete")
  - City/location keywords
- A business name with relevant keywords ranks significantly better
- **Score:** PASS if name contains service + location keywords, NEEDS WORK if partial match (service OR city only), FAIL if generic name with no keywords
- **Evidence:** Note the exact business name and what keywords it contains/lacks
- **Recommendation if not passing:** Consider filing a DBA that includes service + city keywords

### Step 5: Check Item #05 — GBP Categories (Primary + All Slots)

- Navigate to the GBP About tab or business details to see categories
- Extract the primary category and ALL secondary categories
- Assess:
  - Is the primary category the most specific match for the core service?
  - Are all available category slots filled with genuinely applicable categories?
  - Are there obvious missing categories?
- **Score:** PASS if primary is optimal and multiple relevant secondaries filled, NEEDS WORK if primary is good but secondaries are sparse or missing obvious ones, FAIL if primary category is wrong or too generic
- **Evidence:** List all current categories

**SCREENSHOT:** The GBP About tab showing categories. Save as `screenshots/gbp-categories.png`.

### Step 6: Check Item #08 — Review Velocity

- Look at the reviews section of the GBP listing
- Check:
  - Total review count
  - Star rating
  - Dates of the most recent 5-10 reviews to assess velocity
  - Calculate approximate reviews per month over the last 3-6 months
  - How recent is the latest review?
- **Score:** PASS if consistent recent reviews (2+ per month) with latest within 2 weeks, NEEDS WORK if sporadic reviews or latest older than 1 month, FAIL if no reviews in 3+ months or very few total reviews
- **Evidence:** Note total count, rating, latest review date, estimated monthly velocity

**SCREENSHOT:** Recent reviews section. Save as `screenshots/gbp-reviews.png`.

### Step 7: Check Item #09 — Extended GBP Hours

- Check the listed business hours
- Assess:
  - Are hours set for every day the business is reachable?
  - Are hours restrictive (e.g., 9-5 only when they answer phones 7am-8pm)?
  - Does "Closed" show during times competitors are listed as open?
  - Is 24/7 listed (via answering service)?
- **Score:** PASS if hours cover the full answerability window (extended hours or 24/7), NEEDS WORK if standard business hours only, FAIL if hours are missing or overly restrictive
- **Evidence:** Note listed hours for each day

**SCREENSHOT:** Business hours section. Save as `screenshots/gbp-hours.png`.

### Step 8: Check Item #29 — GBP Photos (Monthly Refresh)

- Navigate to the Photos tab of the GBP listing
- Check:
  - Total photo count
  - Types of photos: real work photos, team, premises (vs stock/logo only)
  - Recency: when were the most recent photos added?
  - Are photos being added at least monthly?
- **Score:** PASS if 20+ photos with recent additions (last 30 days), real work/team shots, NEEDS WORK if photos exist but are stale (60+ days) or mostly stock/logo, FAIL if very few photos (<5) or no recent additions in 3+ months
- **Evidence:** Note total count, types, and recency

**SCREENSHOT:** Photos tab. Save as `screenshots/gbp-photos.png`.

**SCREENSHOT:** Overall GBP listing. Save as `screenshots/gbp-overview.png`.

---

## Phase 3: Google Ads & Press Release Check (Game Changers)

### Step 1: Check Item #03 — Google Ads / LSAs

- In the browser, search Google for the primary service keyword + city (e.g., "commercial cleaning $location")
- Check the SERP for:
  - Are Local Services Ads (LSAs) showing? (These appear at the very top with a green checkmark)
  - Is the client appearing in LSAs?
  - Are standard Google Ads (search ads) showing for this keyword?
  - Is the client running Google Ads?
- **Score:** PASS if client has active LSAs and/or search ads, NEEDS WORK if ads exist in the market but client isn't running them, FAIL if LSAs dominate the SERP and client has no ad presence at all
- **Evidence:** Note what ad types appear and whether client is present

**SCREENSHOT:** The SERP showing ad placements. Save as `screenshots/serp-ads.png`.

### Step 2: Check Item #06 — Strategic Press Releases

- Use WebSearch to search for: `"$businessName" press release` and `"$businessName" site:prnewswire.com OR site:businesswire.com OR site:globenewswire.com OR site:prweb.com`
- Also search: `"$businessName" news`
- Check:
  - Has the business published any press releases?
  - How recent are they?
  - Do they link to relevant service pages (not just homepage)?
  - Are they using brand anchors (good) or keyword-rich anchors (bad)?
- **Score:** PASS if recent press releases (within 6 months) with brand anchors linking to service pages, NEEDS WORK if press releases exist but are old or poorly executed, FAIL if no press release history at all
- **Evidence:** Note any press releases found with dates and links

---

## Phase 4: Website & Content Checklist (Technical & Content)

### Step 1: Check Item #07 — Dedicated, Optimized Service Pages

Using the sitemap and page list from Phase 1:
- Check if there is one dedicated page per core service
- For each service page, fetch via WebFetch and check:
  - Does the title tag contain service + city? (e.g., "Commercial Cleaning in $location")
  - Is there a clear conversion path (phone number, form, CTA)?
  - Does it include process details, pricing signals, and proof (testimonials/case studies)?
- **Score:** PASS if every core service has a dedicated page with service+city in title and conversion path, NEEDS WORK if pages exist but titles are weak or missing conversion elements, FAIL if services are lumped onto a single page or major services lack dedicated pages
- **Evidence:** List each service and whether it has a dedicated page with proper title

### Step 2: Check Item #23 — Title Tags (Service + City First)

- Fetch the homepage and all key service pages via WebFetch
- Extract the `<title>` tag from each
- Check if service keyword + city appear near the start of the title
- Note any titles that are generic, too long without the key terms, or missing city
- **Score:** PASS if all service page titles lead with service+city, NEEDS WORK if some titles are weak or missing city, FAIL if titles are generic/brand-only across the board
- **Evidence:** List each page URL and its title tag with assessment

### Step 3: Check Item #24 — Structured Data Markup

- Fetch the homepage and 1-2 service pages via WebFetch
- Search the HTML for `<script type="application/ld+json">` blocks
- Check for:
  - `LocalBusiness` schema (with correct NAP, hours, geo coordinates)
  - `Service` schema on service pages
  - `FAQPage` schema if FAQ sections exist
  - `Organization` schema
- Verify schema data matches the GBP listing (name, address, phone, hours)
- **Score:** PASS if LocalBusiness + Service schema present and matching GBP data, NEEDS WORK if partial schema (e.g., only Organization, or schema has mismatches), FAIL if no structured data at all
- **Evidence:** Note what schema types are present and any mismatches

### Step 4: Check Item #25 — Mobile-First, Fast, Frictionless UX

**Part A: PageSpeed Insights Test**

1. In the browser, navigate to `https://pagespeed.web.dev/`
2. Enter the client URL and run the mobile test
3. Wait for results (15-45 seconds). Use `mcp__claude-in-chrome__computer` with `action: wait`, `duration: 30`. Check if results loaded. If still loading, wait another 15 seconds.
4. Extract:
   - Core Web Vitals: LCP, INP, CLS (Pass/Fail)
   - Lighthouse Performance score
   - Key metrics: FCP, LCP, TBT, CLS, Speed Index

**SCREENSHOT:** PageSpeed Insights results. Save as `screenshots/pagespeed-mobile.png`.

**Part B: UX Check**

- Fetch the mobile version of the homepage via WebFetch
- Check for:
  - Sticky call button or floating CTA
  - Phone number clickable (tel: link) within one tap
  - Contact form accessible without excessive scrolling
  - No intrusive interstitials or popups blocking content
- **Score:** PASS if CWV passes + one-tap phone/form + sticky CTA, NEEDS WORK if performance is ok but UX elements missing (no sticky CTA, buried phone number), FAIL if poor CWV scores AND bad mobile UX
- **Evidence:** Note CWV scores, Lighthouse performance, and UX findings

### Step 5: Check Item #26 — Internal Linking Strategy

- Fetch 3-4 key pages (service pages, blog posts) via WebFetch
- Check:
  - Do informational pages (blog posts) link to the service pages they support?
  - Do service pages cross-link to related services?
  - Are there orphan pages (pages not linked from navigation or other content)?
  - Is the navigation clean and exposes the most important pages?
- Check the sitemap page count vs pages reachable from navigation
- **Score:** PASS if service pages are well cross-linked and blog/info content links to relevant service pages, NEEDS WORK if some linking exists but inconsistent or orphan pages found, FAIL if pages are isolated with minimal internal linking
- **Evidence:** Note linking patterns found and any orphan pages

### Step 6: Check Item #27 — City/Service-Area Pages

- Check the sitemap for location-specific pages (e.g., /areas/cityname, /service-area/cityname)
- If they exist, fetch 2-3 via WebFetch and audit:
  - Is the content unique per city or templated/thin?
  - Does it include real local details (local jobs done, area-specific info, local reviews)?
  - Does it have area-specific FAQs?
  - Does it have a map embed?
- **Score:** PASS if location pages exist with genuinely unique local content per area, NEEDS WORK if pages exist but are thin/templated with just city name swaps, FAIL if no location pages exist despite serving multiple areas
- **Note:** If the business only serves one city, this can be N/A (not scored)
- **Evidence:** List location pages found and content quality assessment

### Step 7: Check Item #28 — Unique, Experience-Based Content

- Review the service pages and any blog content fetched in earlier steps
- Assess:
  - Does the content include real pricing or pricing ranges?
  - Are there project breakdowns or case studies?
  - Is there opinionated/expert content (comparisons, recommendations)?
  - Does it feel like it was written by someone who does the work, or is it generic AI-templated content?
  - Are there real photos of actual work (not stock photos)?
- **Score:** PASS if content shows clear firsthand experience (pricing, real projects, expert opinions), NEEDS WORK if some unique content but mostly generic descriptions, FAIL if all content is clearly templated/AI-generated with no unique expertise
- **Evidence:** Note specific examples of experience signals or lack thereof

---

## Phase 5: Compile Checklist Scorecard

Create a scorecard summarizing all 16 items:

### Game Changers
| # | Item | Status | Key Finding |
|---|------|--------|-------------|
| 01 | Visible address vs SAB | PASS/NEEDS WORK/FAIL | ... |
| 02 | Location within city | PASS/NEEDS WORK/FAIL | ... |
| 03 | Google Ads / LSAs | PASS/NEEDS WORK/FAIL | ... |
| 04 | Keywords in business name | PASS/NEEDS WORK/FAIL | ... |
| 05 | GBP categories | PASS/NEEDS WORK/FAIL | ... |
| 06 | Strategic press releases | PASS/NEEDS WORK/FAIL | ... |
| 07 | Dedicated service pages | PASS/NEEDS WORK/FAIL | ... |
| 08 | Review velocity | PASS/NEEDS WORK/FAIL | ... |
| 09 | Extended GBP hours | PASS/NEEDS WORK/FAIL | ... |

### Technical & Content
| # | Item | Status | Key Finding |
|---|------|--------|-------------|
| 23 | Title tags | PASS/NEEDS WORK/FAIL | ... |
| 24 | Structured data | PASS/NEEDS WORK/FAIL | ... |
| 25 | Mobile-first UX | PASS/NEEDS WORK/FAIL | ... |
| 26 | Internal linking | PASS/NEEDS WORK/FAIL | ... |
| 27 | Location pages | PASS/NEEDS WORK/FAIL/N/A | ... |
| 28 | Content quality | PASS/NEEDS WORK/FAIL | ... |
| 29 | GBP photos | PASS/NEEDS WORK/FAIL | ... |

Calculate:
- Total passing: X / 16 (or X / 15 if item 27 is N/A)
- Game Changers score: X / 9
- Technical & Content score: X / 7 (or 6)

Generate prioritized recommendations grouped by:
- **Fix Now** (FAIL items — biggest impact, most urgent)
- **Improve Soon** (NEEDS WORK items — meaningful gains)
- **Maintain** (PASS items — keep doing what works)

---

## Phase 6: Generate HTML Report

Create a professional HTML report with a checklist-style layout. The report must include:

1. **Header:** Client business name, domain, audit date, overall score badge (X/16)
2. **Executive Summary:** Overall score, count of PASS/NEEDS WORK/FAIL items, top 3 most impactful findings
3. **Section 1: Game Changers** — Each of the 9 items displayed as a card with:
   - Item number and title
   - Status badge: green (PASS), amber (NEEDS WORK), red (FAIL)
   - Evidence summary (what was found)
   - Recommendation (if not passing)
   - Relevant screenshot embedded (if applicable)
4. **Section 2: Technical & Content** — Each of the 7 items in the same card format
5. **Section 3: Priority Action Plan** — Three groups:
   - Fix Now (FAIL items with specific action steps)
   - Improve Soon (NEEDS WORK items with specific action steps)
   - Maintain (PASS items — brief note on what to keep doing)

### Styling Guidelines

Use a clean, professional design with:
- Status colors: `#10b981` (green/PASS), `#f59e0b` (amber/NEEDS WORK), `#ef4444` (red/FAIL)
- Dark navy header with white text
- Card-based layout for each checklist item
- Print-friendly CSS
- Responsive/mobile-friendly
- Score gauge or progress indicator in the header

Embed ALL screenshots from the `screenshots/` folder at their relevant checklist items with descriptive captions.

Write the report to `LOCAL-SEO-AUDIT-REPORT.html` in the working directory. Open in browser for verification.

---

## Phase 7: Publish Report to GitHub Pages

Publish the completed report to `https://growtharchon.github.io/client-reports/` so the client can view it online.

### Step 1: Create a client subfolder name
Derive a URL-safe folder name from the business name or domain. Use lowercase, hyphens only, no special characters.

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

Copy the HTML report as `index.html` (so it loads at the folder URL) and all screenshots:
```bash
cp "{working-directory}/LOCAL-SEO-AUDIT-REPORT.html" "$CLIENT_FOLDER/index.html"
cp -r "{working-directory}/screenshots" "$CLIENT_FOLDER/" 2>/dev/null
```

### Step 4: Commit and push
```bash
git add -A
git commit -m "Add {business-name} - Local SEO Checklist Audit

- 16-point checklist audit: Game Changers + Technical & Content
- Scorecard with pass/needs-work/fail per item
- Evidence screenshots and prioritized action plan"
git push origin main
```

### Step 5: Verify GitHub Pages deployment
```bash
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

---

## Output Checklist

Before finishing, verify:
- [ ] All 7 phases completed
- [ ] All 16 checklist items scored (PASS / NEEDS WORK / FAIL)
- [ ] Screenshots captured for: GBP overview, categories, reviews, hours, photos, SERP ads, PageSpeed
- [ ] HTML report generated with checklist scorecard format
- [ ] Each item has evidence and recommendation (if not passing)
- [ ] Action plan prioritized by impact
- [ ] Report opened in browser for user review
- [ ] Report published to GitHub Pages and live URL provided to user
