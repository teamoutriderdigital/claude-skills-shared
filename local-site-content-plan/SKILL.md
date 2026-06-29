---
name: local-site-content-plan
description: >
  End-to-end local business content plan generator. Reads services and locations from
  Content Brain and onboarding docs, builds a service x location page matrix with Near Me
  pages, fetches keyword volumes from SEMrush, crafts SEO titles (ALL CAPS first word +
  benefit in parentheses), fetches People Also Ask questions from Google SERP via DataForSEO,
  filters for customer-intent blog topics, and produces a CSV + visual HTML dashboard.
  Optionally publishes to GitHub Pages. Works for any industry and any local business.
  Use this skill whenever the user wants to create a content plan for a local business site,
  plan service pages across locations, generate a service page matrix, or build a local SEO
  content strategy. Also triggers for "plan service pages", "content plan for local business",
  "service page matrix", or "local site content plan".
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebFetch, Agent, AskUserQuestion, mcp__claude_ai_Semrush__keyword_research, mcp__claude_ai_Semrush__get_report_schema, mcp__claude_ai_Semrush__execute_report
effort: high
---

# Local Site Content Plan

Generate a complete content plan for a local business website: service pages (one per service per location), Near Me pages (one per service), and blog posts sourced from People Also Ask questions. Includes keyword volumes, SEO titles, URLs, CSV export, and a visual HTML dashboard.

This skill is **industry-agnostic**. It reads all business specifics (services, locations, name, differentiators) from the Content Brain and onboarding documents in the working directory.

---

## Prerequisites Check

Before starting, verify ALL of the following exist. Use `Glob` to check. If any are missing, stop and tell the user exactly what is needed.

### Required Files

1. **`Content brain/contentbrain.md`** -- Client voice, positioning, services taxonomy, and geographic presence. This is the primary source of truth for services and locations.
2. **`Content brain/*onboarding*` or `Content brain/*-onboarding*`** -- An onboarding document (`.md`) with business details, services offered, and service areas. Glob for `Content brain/*onboarding*.md` or `Content brain/*-onboarding*.md`.
3. **`config.json`** -- Must contain `dataForSeoToken`, `locationCode`, and `languageCode` for SERP/PAA fetching.
4. **`fetch_serp_titles.py`** -- Script to fetch SERP results and PAA questions from DataForSEO API.

### Optional Files

5. **Local SEO guide** -- Glob for `*Local SEO*` or `*local-seo*` in the working directory. If present, read it for title tag best practices. If absent, use the default SEO title rules defined in this skill.

If prerequisites are missing, tell the user:
- "Content brain/contentbrain.md" is needed for services, locations, and brand voice
- "config.json" with DataForSEO credentials is needed for PAA fetching
- "fetch_serp_titles.py" is needed for Google SERP data

Do NOT proceed until all required files are confirmed.

---

## Phase 1: Extract Business Data

Read `Content brain/contentbrain.md` and the onboarding document in full. Extract the following and present it to the user for confirmation:

### 1.1 Business Identity
- **Business name** (from Content Brain header or onboarding)
- **Domain** (website URL)
- **Industry/niche**
- **Tagline/slogan** (if present)
- **State abbreviation** (for SEO titles, e.g., TX, CA, FL)

### 1.2 Services List
Extract ALL services from the Content Brain's services taxonomy. Look for sections titled "Services Taxonomy", "Services Offered", or similar. Capture:
- Core services (revenue drivers)
- Specialty services
- Any additional services listed

Present the full services list and ask the user: **"Are these the services you want pages for? Should any be added or removed?"**

### 1.3 Locations List
Extract ALL locations from the Content Brain's geographic presence section or the onboarding document's "Service Area" field. Capture:
- City names
- State
- Primary/HQ location

Present the locations list and ask the user: **"Are these the locations you want pages for? Should any be added or removed?"**

### 1.4 Trust Signals
Extract trust signals that will be used in SEO title benefits:
- BBB rating (if present)
- Licensed/bonded/insured status
- Satisfaction guarantee
- Free quotes/estimates
- Years in business
- Any certifications

These become the rotating benefit phrases in parentheses at the end of SEO titles.

---

## Phase 2: Validate Service Keywords Against SEMrush

Before building the page matrix, validate that the extracted service names match what people actually search for. A service may be called one thing internally but searched differently by customers.

### 2.1 Generate Candidate Keywords

For each extracted service, create a list of keyword candidates:
- The service name exactly as listed in the Content Brain
- Common alternative phrasings (e.g., "carpet extraction" vs. "carpet cleaning", "day porter" vs. "porter service", "HVAC repair" vs. "AC repair")
- Industry-standard synonyms you can reasonably infer
- Add the word "commercial", "professional", or "residential" as a prefix where it may be the more common search phrasing

Use ONE representative city from the locations list (pick the largest metro) and test all candidates as `{candidate keyword} {city}`.

### 2.2 Batch Query SEMrush for Validation

Use the SEMrush MCP tools to check volumes:

1. Call `mcp__claude_ai_Semrush__keyword_research` to discover available reports
2. Call `mcp__claude_ai_Semrush__get_report_schema` with `report: "phrase_these"`
3. Call `mcp__claude_ai_Semrush__execute_report` with all candidate keywords in semicolon-separated batches

```
params: {
  phrase: "carpet cleaning houston;carpet extraction houston;commercial carpet cleaning houston;...",
  database: "us",
  export_columns: "Ph,Nq,Cp,Co,Kd"
}
```

### 2.3 Evaluate Results and Pick Best Keywords

For each service, compare the volume of all tested candidate keywords:

- **If the Content Brain name has good volume** (>0): Use it as the primary keyword. Note any higher-volume alternatives as secondary keywords.
- **If the Content Brain name has 0 volume but an alternative has volume:** Recommend the alternative as the primary keyword. Present both to the user with volumes.
- **If ALL candidates have 0 volume:** Flag the service. It may still be worth creating pages for strategic reasons, but the user should decide.

### 2.4 Present Keyword Validation Results

Show the user a comparison table:

```
| Service (Content Brain) | Tested Keywords                    | Volume | Recommendation       |
|-------------------------|------------------------------------|--------|----------------------|
| Carpet Extraction       | carpet extraction houston          | 0      |                      |
|                         | carpet cleaning houston            | 390    | Use as primary       |
|                         | commercial carpet cleaning houston  | 70     | Use as secondary     |
| Day Porter              | day porter houston                 | 0      | 0 vol, keep anyway?  |
|                         | porter service houston             | 0      |                      |
```

Ask: **"Based on the search data, here are my keyword recommendations. Should I proceed with these, or adjust any?"**

Wait for user confirmation before building the matrix.

---

## Phase 3: Build Service x Location Matrix

### 3.1 Generate All Combinations

Using the validated/approved keywords from Phase 2, create one page entry for every service x location combination:
- **Total pages** = (number of services) x (number of locations)
- **URL pattern:** `/service/{service-slug}-{city-slug}/` (e.g., `/service/roof-repair-houston/`)
- **Primary keyword:** The validated keyword + city name in lowercase (e.g., `roof repair houston`)
- **Secondary keyword** (if identified in Phase 2): Note it for on-page use but do not create a separate page

### 3.2 Present the Matrix

Show the user the complete matrix as a table:
```
| # | Service | Location | URL | Primary Keyword | Secondary Keyword |
```

Ask: **"Does this matrix look correct? Any pages to add or remove?"**

---

## Phase 4: Build Near Me Pages

### 4.1 Generate Near Me Entries

Create one Near Me page per service (NOT per location):
- **URL pattern:** `/service/{service-slug}-near-me/`
- **Primary keyword:** `{validated service keyword} near me`
- These pages cover ALL locations and link to each city-specific page

### 4.2 Near Me Title Rule

Near Me page SEO titles must **NOT contain any location name** (no city, no state). They target location-agnostic "near me" search intent.

---

## Phase 5: Fetch Full Keyword Volumes from SEMrush

### 5.1 Batch Keyword Queries

Now fetch volumes for ALL finalized keywords (service+city pairs AND near me keywords) using the SEMrush MCP tools.

Use `mcp__claude_ai_Semrush__execute_report` with `report: "phrase_these"` for batches of keywords.

**Batch strategy:** SEMrush `phrase_these` accepts semicolon-separated keywords. Group keywords into batches of 10-15 per call to stay efficient:
```
params: {
  phrase: "keyword1;keyword2;keyword3;...",
  database: "us",
  export_columns: "Ph,Nq,Cp,Co,Kd"
}
```

Query ALL keywords:
- All service+city combinations
- All "near me" variations

### 5.2 Record Volumes

Record the monthly search volume (Nq) for each keyword. If a keyword returns 0 volume, still include it in the plan (some pages are strategic, not search-driven). Flag 0-volume keywords for the user.

---

## Phase 6: Craft SEO Titles

### 6.1 Title Structure Rules

Every SEO title must follow this format:
```
{CAPS_WORD} {Service Name} in {City}, {State} ({Benefit})
```

**Rules:**
- **First word in ALL CAPS** -- Rotate through: BEST, TRUSTED, LICENSED, CUSTOM, RELIABLE, and other short power words. Do not repeat the same word on consecutive pages within the same service group.
- **Max 65 characters** -- Trim "in" or state abbreviation if needed to fit
- **City + state abbreviation** for location pages (e.g., "Houston, TX")
- **NO location** for Near Me pages
- **Benefit in parentheses** at the end -- Rotate through benefits derived from the client's trust signals (Phase 1.4). Common options:
  - (Satisfaction Guarantee)
  - (A+ BBB Rated)
  - (Free Quotes)
  - (Licensed & Insured)
  - (Free Estimates)
  - Adapt to whatever trust signals the specific client has

### 6.2 Blog Post Titles

Blog post SEO titles follow a different pattern:
```
{CAPS_WORD} {Rest of PAA Question}? ({Benefit or Descriptor})
```
- The first word of the PAA question is made ALL CAPS
- The exact PAA question text must be preserved (only fix grammar if broken)
- Add a short benefit/descriptor in parentheses if it fits within 65 characters
- Common descriptors: (Complete Guide), (Price Guide), (Key Differences), (Answered), (Honest Answer), (Pros and Cons), (Expert Answer)

---

## Phase 7: Fetch PAA Questions from DataForSEO

### 7.1 Create Batch Wrapper

Write a Python script called `fetch_all_paa.py` in the working directory. This script:

1. Imports core functions from `fetch_serp_titles.py` (`load_config`, `build_headers`, `post_task`, `fetch_result`)
2. Defines ALL keywords from the service page matrix + Near Me pages
3. Posts all SERP tasks in rapid succession (with 0.5s delay between posts to avoid rate limits)
4. Waits 30 seconds for all tasks to process
5. Fetches results for each task with `initial_wait=0` (since we already waited)
6. Collects all PAA questions, deduplicates by question text (case-insensitive)
7. Tags each question with its source keyword and parent service category
8. Saves to `all-paa-questions.json`

**Service mapping:** Build a mapping dictionary from keyword patterns to service names so each PAA question is tagged with its parent service.

### 7.2 Run the Script

Execute `python fetch_all_paa.py` from the working directory. This takes 1-3 minutes depending on the number of keywords.

Expected output: a JSON file with all unique PAA questions across all keywords.

---

## Phase 8: Filter PAA Questions

### 8.1 Filtering Criteria

Review every PAA question and **REMOVE** questions that are:

**Remove -- Service Provider / Job Seeker Intent:**
- Questions about what to CHARGE for a service ("How much should a [provider] charge?")
- Questions about hourly rates FROM the provider perspective
- Questions about how to START a business in this industry
- Questions about salaries, earnings, or pay for workers in this field
- Questions about hiring/careers/jobs in the industry

**Remove -- Residential / Consumer DIY:**
- Questions about doing the work yourself at home
- Questions about residential (not commercial) services, IF the client is B2B only
- Questions about renting equipment to do it yourself
- Questions about home remedies or DIY methods

**Remove -- Irrelevant:**
- Questions about specific competitor brands by name
- Questions completely unrelated to the industry (city trivia, salary comparisons, celebrity facts)
- Questions too generic to make actionable blog content
- Duplicate questions that are near-identical in meaning (keep the better-phrased one)

### 8.2 Keep -- Customer Intent

Keep questions that a potential CUSTOMER would ask:
- "What is [service]?" -- Definitional
- "Is [service] worth it?" -- Value assessment
- "How much does [service] cost?" -- Pricing from buyer perspective
- "What's included in [service]?" -- Scope understanding
- "What's the difference between [service A] and [service B]?" -- Comparison
- "Is [service] necessary?" -- Need validation
- "Are professional [providers] worth it?" -- Professional vs. DIY from buyer side

### 8.3 Present Filtered Results

Show the user the filtered list organized by service category. State how many were kept vs. removed and the removal reasons. Ask: **"Should any of these be added back or removed?"**

---

## Phase 9: Create Blog Post Entries

### 9.1 For Each Kept PAA Question

- **Keyword:** The exact PAA question text. Only fix grammar if it's genuinely broken (e.g., missing question mark). Do not rephrase.
- **URL:** `/blog/{slugified-question}/` -- Convert the question to a URL slug (lowercase, hyphens, remove question marks and apostrophes)
- **Service category:** The parent service this question maps to (from the tagging in Phase 7)
- **Search volume:** Leave blank. Do NOT fetch volume for PAA questions.
- **SEO title:** Follow the blog post title rules from Phase 6.2

---

## Phase 10: Generate CSV

### 10.1 File Structure

Write `service-pages-plan.csv` with these columns:
```
Page #,Type,Service Category,Location,URL,Primary Keyword,Search Volume (mo),SEO Title
```

### 10.2 Row Order

1. **Service pages** (grouped by service, ordered by location) -- Type: "Service Page"
2. **Near Me pages** (one per service) -- Type: "Near Me Page"
3. Empty separator row
4. Header row: `,BLOG POSTS,,,,,`
5. **Blog posts** (grouped by parent service) -- Type: "Blog Post"

Blog post rows have no search volume value (leave blank or use a dash).

### 10.3 CSV Formatting

- Wrap SEO titles in double quotes (they contain commas)
- Use UTF-8 encoding
- Page numbers are sequential across all types (service pages 1-N, Near Me N+1 to N+M, blog posts continue from there)

---

## Phase 11: Generate HTML Dashboard

### 11.1 Create `service-pages-plan.html`

Build a single self-contained HTML file (no external dependencies) with a modern, professional dashboard layout.

**Design system:**
- Clean sans-serif font stack (Inter, system fonts)
- Professional color palette (dark header, white cards, colored service badges)
- Each service category gets a unique badge color
- Responsive layout (works on desktop and mobile)

**Sections:**

1. **Sticky header** -- Business name + "Content Plan" title, domain, generation date
2. **Sticky nav** -- Links to: Summary, Service Pages, Near Me Pages, Blog Posts
3. **Search bar** -- JavaScript filter that shows/hides table rows matching the search query
4. **Summary cards** -- Total content pieces, service pages count, blog posts count, total monthly search volume, top priority city (highest volume)
5. **Service Pages section** -- Grouped by service category, each group has:
   - Service badge + name + total volume for the group
   - Table with columns: #, Location, URL, Primary Keyword, Volume (with visual bar), SEO Title
   - SEO title formatting: first word bold/dark, benefit text in green
6. **Near Me Pages section** -- Single table, service badge per row, same column structure
7. **Blog Posts section** -- Grouped by parent service, each group has:
   - Service badge + name + post count
   - Table with columns: #, Type badge, URL, Keyword (PAA Question), SEO Title

**Table formatting:**
- NO sticky `thead` on inner tables (causes overlap on small tables)
- Alternating row hover effect
- Volume bars: proportional width within each service group (highest = 100%)
- Monospace font for URLs
- Print-friendly CSS (static positioning, no sticky elements)

**JavaScript:**
- Search/filter function on all `tr.searchable` rows
- Scroll spy for nav highlighting

**Footer:** Business name, page/post counts, total volume, generation date

### 11.2 Important HTML Rules

- All self-contained: inline CSS, inline JS, no external resources
- Do NOT use sticky positioning on table headers (`thead th`)
- Volume bars should use percentage widths relative to the max volume in each group
- Service badge colors should be visually distinct (use different hue for each service)

---

## Phase 12: Optional GitHub Pages Publishing

After generating the HTML, ask the user: **"Would you like to publish this to GitHub Pages?"**

If yes, ask for:
- GitHub account name (or detect from `gh auth status`)
- Repository name (default: `client-reports`)
- Subfolder name (default: slugified business name)

Then:
1. `gh auth status` to verify login
2. `gh repo view {account}/{repo}` to check if repo exists
3. Clone the repo to `/tmp/{repo}`
4. Create subfolder and copy HTML as `index.html`
5. Git add, commit, push
6. Verify GitHub Pages is enabled with `gh api repos/{account}/{repo}/pages`
7. Report the live URL: `https://{account}.github.io/{repo}/{subfolder}/`

If the user declines publishing, skip this phase entirely.

---

## Output Summary

At the end, present a final summary:

```
Content Plan Complete
=====================
Business:        {business name}
Domain:          {domain}
Services:        {N} services
Locations:       {M} locations
Service Pages:   {N x M} pages
Near Me Pages:   {N} pages
Blog Posts:      {P} posts (from PAA questions)
Total Pieces:    {total}
Total Volume:    {sum} monthly searches
Top City:        {city with highest total volume}
Top Service:     {service with highest total volume}

Files Created:
- service-pages-plan.csv
- service-pages-plan.html
- all-paa-questions.json
- fetch_all_paa.py
{if published: - Live at: https://....github.io/.../ }
```

---

## Important Rules

1. **Content Brain is the source of truth** for services, locations, and business identity. If the onboarding doc and Content Brain conflict, Content Brain wins.
2. **Always confirm with the user** before proceeding past Phase 1 (services/locations extraction) and Phase 7 (PAA filtering). These are the key decision points.
3. **SEO titles must be max 65 characters.** If a title exceeds this, shorten by removing filler words like "in" or abbreviating. Never sacrifice the keyword or the benefit.
4. **Near Me pages never include location names** in the SEO title.
5. **Blog post keywords are the exact PAA questions** -- only fix grammar, never rephrase.
6. **0-volume keywords are still valid pages.** Some services or locations may have low/no search volume but are strategically important. Include them but flag them.
7. **Customer intent filter is critical.** Blog posts must target questions a potential BUYER would ask, not questions from service providers, job seekers, or DIYers.
8. **HTML table headers must NOT be sticky** (`position: sticky` on `thead th` causes rows to be hidden behind the header on small tables).
9. **Batch SEMrush queries** using semicolons in `phrase_these` (max ~15 keywords per batch) to minimize API calls.
10. **Batch DataForSEO tasks** by posting all tasks first, waiting once, then fetching all results -- avoids serial 20-second waits per keyword.
