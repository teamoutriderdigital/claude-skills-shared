---
name: seo-content-audit-semrush
description: >
  End-to-end SEO content audit powered by SEMrush CSV exports. Processes client
  organic keywords, top pages, competitors, keyword gap data, competitor keyword
  files, and a domain authority comparison screenshot. Produces a beautiful,
  actionable HTML report with all keyword opportunities organized by page type
  and sorted by an attainability score derived from domain authority analysis.
  Uses 4 parallel sub-agents for data processing. Publishes the final report to
  GitHub Pages. Works for any website in any industry. Use this skill whenever
  the user wants to perform an SEO content audit, keyword gap analysis, competitor
  SEO comparison, or content opportunity assessment from SEMrush data. Also use
  when the user says "SEMrush audit", "content audit", "keyword gap analysis",
  "SEO audit from CSV", "competitor keyword analysis", or asks to find content
  opportunities for a client website using SEMrush exports.
argument-hint: "[domain]"
arguments: [domain]
effort: high
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Agent
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
---

# SEO Content Audit (SEMrush)

You are performing a comprehensive SEO content audit for **$domain** using SEMrush CSV exports. The audit produces an actionable HTML report with keyword opportunities organized by page type and sorted by attainability — prioritizing keywords the client can realistically rank for given their domain authority.

## Why this workflow matters

Most keyword gap analyses present raw opportunity lists that ignore authority differences — recommending KD 80 keywords to a domain with authority score 20. This skill filters everything through an **attainability lens**: it extracts domain authority from a screenshot, scores every keyword by how realistic it is for this specific client, removes navigational/brand keywords that inflate numbers, and organizes recommendations by page type so the client knows exactly what to build.

## Phase 0: Setup

Create the working directory:
```bash
mkdir -p analysis
```

## Phase 1: Data Collection

Ask the user to export these files from SEMrush and save them to the current working directory. Present this as a checklist:

> **Please export the following from SEMrush and save the CSV files here. Let me know when they're ready.**
>
> 1. **Client Organic Keywords** — Organic Research > Positions > Export all keywords
> 2. **Client Top Pages** — Organic Research > Pages > Export
> 3. **Client Competitors** — Organic Research > Competitors > Export
> 4. **Keyword Gap** — Keyword Gap tool (client vs top 3-5 competitors) > Export all
> 5. **Competitor Keywords** (3-5 files) — Organic Research > Positions > Export for each top competitor
> 6. **Authority Comparison Screenshot** — Compare Domains tool > screenshot showing Authority Score, Backlinks, Ref. Domains for all domains (save as PNG/JPG)
> 7. **Internal URLs CSV** — A CSV with all published page URLs on the client website (one URL per line). Can be generated from the sitemap using `/fetch-internal-urls`, or exported from Screaming Frog, or manually compiled. Name it `internal_urls.csv`.
>
> The keyword gap export is the most important file — it contains the core opportunity data.
> The internal URLs file is important because SEMrush often doesn't index all pages — the client may already have pages targeting gap keywords that simply aren't ranking yet.

Wait for the user to confirm files are ready before proceeding.

## Phase 2: File Discovery & Validation

Use `Glob` to find all CSV and image files:
```
*.csv
*.png
*.jpg
*.jpeg
```

SEMrush CSV exports follow recognizable naming patterns:
- Client positions: contains the client domain name and `organic.Positions`
- Client pages: contains client domain and `PagesV3`
- Client competitors: contains client domain and `Competitors`
- Keyword gap: starts with `gap.keywords` or contains `gap`
- Competitor positions: contains a competitor domain and `organic.Positions`
- Internal URLs: named `internal_urls.csv` or contains `internal` — a simple CSV with one URL per line

Read the first 3 lines of each CSV to verify column headers match expected SEMrush formats:

| File Type | Key Columns |
|-----------|-------------|
| Client/Competitor Keywords | Keyword, Position, Search Volume, Keyword Difficulty, CPC, URL, Traffic |
| Client Pages | URL, Traffic (%), Number of Keywords, Traffic, Traffic Change, Answer Engines, Top Keyword |
| Client Competitors | Domain, Competitor Relevance, Common Keywords, Organic Keywords, Organic Traffic |
| Keyword Gap | Keyword, Intents, Volume, Keyword Difficulty, CPC, [domain columns with positions] |
| Internal URLs | Single column of URLs (one per line), or a URL column among others |

Report what was found and ask the user to confirm the file mapping. This matters because misclassified files will produce incorrect analysis.

**Internal URLs validation:** Count total URLs found. Compare against the number of unique URLs in the Client Pages SEMrush export. If the internal URLs file has significantly more pages (e.g., 500 internal vs 200 in SEMrush), that gap represents pages SEMrush hasn't indexed — these are important for the "hidden pages" analysis in Phase 4.

## Phase 3: Authority Context Extraction

Read the authority comparison screenshot (the PNG/JPG image file). Extract for each domain:
- **Domain name**
- **Authority Score** (AS)
- **Backlinks count**
- **Referring Domains count**

Then classify each domain's relationship to the client:

| Client AS vs Competitor AS | Classification | Attainability Multiplier |
|---|---|---|
| Competitor AS <= Client AS - 5 | Weaker | x1.5 when they rank top 20 |
| Competitor AS within 5 of Client AS | Equal | x1.5 when they rank top 20 |
| Competitor AS > Client AS + 5 | Stronger | x1.0 (no bonus) |

Store this authority context — it drives the attainability scoring in Phase 4.

### Attainability Score Formula

```
Base = Volume / (KD + 1)

Multipliers (cumulative):
  x 1.5  if an equal-or-weaker authority competitor ranks positions 1-20
  x 1.3  if ANY competitor ranks positions 1-10
  x 0.7  if ONLY stronger-authority competitors rank AND only in positions 30-50
```

Higher score = bigger volume relative to difficulty, validated by peers the client can realistically compete with.

## Phase 4: Parallel Data Analysis (4 Sub-Agents)

Launch all 4 agents simultaneously using `run_in_background: true`. Each agent receives the authority context and file paths.

### Agent 1 — Client Current State

**Prompt the agent with:**
- Client keywords CSV path and client pages CSV path
- Internal URLs CSV path
- The client domain name
- Instructions to use Python (via Bash) for CSV processing

**The agent must produce `analysis/01-client-current-state.md` containing:**

1. **Traffic Overview**: total organic traffic, total keywords, traffic cost value
2. **Top 20 Keywords by Traffic**: table with keyword, position, search volume, traffic, intent, URL
3. **Position Distribution**: count keywords in 1-3, 4-10, 11-20, 21-50, 51-100
4. **Intent Distribution**: keywords and traffic by informational, commercial, navigational, transactional
5. **Branded vs Non-Branded Split**: identify branded keywords (containing client brand name), show traffic split — this is often the most revealing metric
6. **Top 10 Pages by Traffic**: URL, traffic, keyword count, traffic change, top keyword
7. **Underperforming Pages**: pages with high keyword count (>10) but low traffic — optimization candidates
8. **Quick Wins**: keywords in positions 4-20 with volume > 100 — close to page 1
9. **AI/Answer Engine Visibility**: pages appearing in Answer Engines or with LLM Prompts > 0
10. **Indexation Gap**: Compare internal URLs against SEMrush Pages export. Identify pages that exist on the site but are NOT appearing in SEMrush data. Count: total internal URLs, URLs in SEMrush, URLs missing from SEMrush. Categorize missing URLs by type (blog posts, service pages, location pages, etc.) based on URL path patterns. These are pages that exist but have zero organic visibility — they may need technical SEO fixes (noindex, canonicalization, thin content) or content improvements to start ranking.

### Agent 2 — Competitor Landscape

**Prompt the agent with:**
- Client competitors CSV path
- All competitor keyword CSV paths
- Authority context (AS, backlinks, ref domains per domain)

**The agent must produce `analysis/02-competitor-landscape.md` containing:**

1. **Top 20 Organic Competitors** from the competitors export
2. **Head-to-Head Comparison**: client vs each competitor — keywords, traffic, traffic cost, branded %, avg position
3. **Competitor Strengths by Topic**: for each competitor, top 15 keywords grouped by topic cluster
4. **Branded vs Non-Branded** per competitor: what % is brand searches vs generic
5. **Position Distribution Comparison**: per competitor — keywords in top 3, 4-10, 11-20
6. **Content Strategy Patterns**: analyze competitor URL structures — what types of pages do they have (blog, location, service, product, etc.)
7. **Keyword Overlap**: pairwise overlap between competitors, unique keywords per competitor

### Agent 3 — Keyword Gap Analysis (Authority-Adjusted)

This is the most important agent. **Prompt it with:**
- Keyword gap CSV path
- Authority context with domain classifications (equal/weaker/stronger)
- The attainability formula
- Brand filter instructions (see below)

**Brand/Navigational Keyword Filtering:**

The agent must remove keywords that are navigational searches for other companies. Build the filter list dynamically:

1. **Competitor brand names**: Extract from each competitor domain (e.g., `sgtautotransport.com` → filter "sgt", "sgt auto", "sgt transport")
2. **Common platform brands** (always filter): Read `${CLAUDE_SKILL_DIR}/references/brand-filter-list.md` for the default list
3. **Keywords where SEMrush Intent = "Navigational"**: also remove these

**Additional filters:**
- Only count competitor positions 1-50 (positions 51+ are not meaningful validation)
- Only include keywords with Volume >= 100
- Only include keywords with KD <= 60 (above this is unrealistic for most sites)

**The agent must produce `analysis/03-keyword-gap-opportunities.md` containing:**

1. **Authority-Adjusted Gap Overview**: total keywords, volume, breakdown by competitor validation
2. **Attainability Tiers**:
   - Tier 1 (KD 0-30, equal/weaker authority validates): ALL keywords with vol >= 100
   - Tier 2 (KD 0-30, any competitor top 20): ALL keywords with vol >= 100
   - Tier 3 (KD 31-45, competitor in top 20): ALL keywords with vol >= 200
   - Tier 4 (KD 46-60, multiple competitors in top 30): ALL keywords with vol >= 500
3. **Quick Wins**: KD <= 20, volume >= 100, competitor in top 10 — list ALL
4. **Most "Stealable" Keywords**: keywords where equal/weaker authority competitors rank top 20
5. **Executive Summary** with realistic traffic opportunity estimate

Do NOT truncate keyword tables — include every qualifying keyword. Comprehensive data is the point.

### Agent 4 — Content Gap & Page Type Classification

**Prompt the agent with:**
- Client pages CSV path
- Internal URLs CSV path
- Keyword gap CSV path (already filtered by Agent 3's rules)
- All competitor keyword CSV paths
- Page type classification rules from `${CLAUDE_SKILL_DIR}/references/page-type-classification.md`

**The agent must produce two files:**

**`analysis/04-content-gap-analysis.md`:**
- Client's current content map (categorize URLs by type, show traffic per category)
- Competitor URL pattern analysis (what pages do they have that the client doesn't)
- **Hidden Pages Analysis**: Cross-reference gap keywords against ALL internal URLs (not just SEMrush pages). For each gap keyword, check if the client already has a published page that could target it by matching URL slugs and path segments against keyword terms. For example, if the gap keyword is "motorcycle shipping" and the client has `/motorcycle-transport-services/` in their internal URLs but it doesn't appear in SEMrush — that page exists but isn't ranking. These are high-priority optimization targets because the page already exists; it just needs SEO improvement (better content, internal links, technical fixes) rather than being created from scratch. Flag these as "EXISTING PAGE - NOT RANKING" in the recommendations.
- New pages needed (with target keywords, volume, KD) — only recommend creating new pages for keywords where NO matching internal URL exists
- Existing pages to optimize (with additional keywords they could target)
- Content consolidation opportunities (duplicate/competing pages)

**`analysis/05-opportunities-by-page-type.md`:**
- Classify ALL attainable gap keywords into page types (see reference file for rules)
- For each page type: summary stats, sub-groupings, full keyword table sorted by attainability
- Master summary table of page types ranked by total attainable volume

## Phase 5: Report Synthesis

After all 4 agents complete, read all analysis files and generate `SEO-CONTENT-AUDIT.md`.

The report must be **action-first** — organized by what to do, not by what's wrong. Structure:

1. **Executive Summary** — current state KPIs + opportunity KPIs (brief, one section)
2. **Authority Context** — domain comparison table with attainability formula
3. **Opportunity Overview by Page Type** — summary table, all page types ranked by attainability
4. **Sections 1-8: One per page type** — each section has:
   - Stats bar (keywords, volume, avg KD, avg attainability)
   - Specific action to take (CREATE, OPTIMIZE, CONSOLIDATE)
   - Top keywords table sorted by attainability with competitor positions
   - Existing client pages to fix (if applicable)
   - For keywords matched to hidden pages (exist on site but not in SEMrush): flag as "PAGE EXISTS - NOT RANKING" with the matching internal URL
   - Reference to full keyword list in analysis/05 file
5. **Hidden Pages Report** — Pages found in internal URLs but absent from SEMrush, matched to gap keywords they could target. This is a high-ROI section because these pages already exist and just need optimization, not creation.
6. **Content Consolidation Fixes** — cannibalization issues to resolve
7. **30/60/90-Day Action Plan** — specific page actions with target volumes. Hidden pages that match gap keywords should be prioritized in Days 1-30 since they require optimization, not creation.

## Phase 6: HTML Report Generation

Convert the markdown report to a beautiful, self-contained HTML file.

Read the CSS template from `${CLAUDE_SKILL_DIR}/assets/report-template.html` and use its styling. The HTML report must include:

- Dark theme (navy background, cyan/indigo accents)
- KPI cards grid (red values for problems, green for opportunities)
- Color-coded KD badges: green (0-30), yellow (31-45), red (46+)
- Position indicators: green (#1-10), cyan (#11-20), gray (#21-50), dim (not ranking)
- Attainability scores: green (high), yellow (medium), orange (low)
- Action labels: green (CREATE), yellow (OPTIMIZE), orange (CONSOLIDATE), red (FIX)
- Priority badges on each section header
- Timeline phases with colored left borders (green/yellow/purple for 30/60/90 days)
- Sticky table headers and hover effects on rows
- Print-friendly styles
- Fully self-contained (all CSS inline, no external dependencies)

Write to `SEO-CONTENT-AUDIT.html`.

## Phase 7: Verification

Spot-check the report's key claims against source CSVs:

```python
# Verify with Python via Bash:
# 1. Total keywords count matches source CSV row count
# 2. Branded traffic percentage is calculated correctly
# 3. Gap keyword count matches after filters
# 4. Top keyword volumes match source data
```

Report any discrepancies found. Fix the report if needed.

## Phase 8: Publish to GitHub Pages

Derive a URL-safe folder name from the client domain:
- `mercuryautotransport.com` → `mercury-auto-transport`
- `example-plumbing.com` → `example-plumbing`

Use lowercase, hyphens, no special characters.

```bash
TMPDIR=$(mktemp -d)
cd "$TMPDIR"
git clone https://github.com/growtharchon/client-reports.git
cd client-reports

CLIENT_FOLDER="{folder-name}"
mkdir -p "$CLIENT_FOLDER"

# Copy HTML as index.html so it loads at the folder URL
cp "{working-directory}/SEO-CONTENT-AUDIT.html" "$CLIENT_FOLDER/index.html"
cp "{working-directory}/SEO-CONTENT-AUDIT.md" "$CLIENT_FOLDER/" 2>/dev/null

git add -A
git commit -m "Add {domain} - SEO Content Audit Report

- Authority-adjusted keyword gap analysis
- Opportunities organized by page type, sorted by attainability
- 30/60/90-day action plan"
git push origin main
```

Verify GitHub Pages is enabled:
```bash
gh api repos/growtharchon/client-reports/pages 2>&1
```

Report the live URL:
```
https://growtharchon.github.io/client-reports/{folder-name}/
```

## Output Checklist

Before finishing, verify:
- [ ] All CSV files correctly identified and classified (including internal URLs)
- [ ] Authority scores extracted from screenshot
- [ ] Internal URLs cross-referenced against SEMrush pages and gap keywords
- [ ] 4 analysis files generated in analysis/ folder
- [ ] Opportunities-by-page-type file has ALL qualifying keywords (not truncated)
- [ ] Navigational/brand keywords filtered out
- [ ] Attainability scores use authority-adjusted multipliers
- [ ] HTML report generated with dark theme, KPI cards, color-coded tables
- [ ] Key claims spot-checked against source CSVs
- [ ] Report published to GitHub Pages
- [ ] Live URL provided to user
