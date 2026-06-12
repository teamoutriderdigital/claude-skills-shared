---
name: research-for-blog-post
description: End-to-end blog post research pipeline. Generates search terms from an article title, searches Google, selects the best competing articles, fetches and converts them to markdown, then produces a comprehensive 2000-5000 word research report. Use this skill whenever the user wants to research a blog post topic, gather competitor article data, create a research report for content writing, or prepare background material before writing an article. Also triggers for requests like "research this topic for writing", "analyze competing articles for [title]", "gather research for a blog post about X", or "run research for [article title]".
allowed-tools: Bash, Read, Write, WebFetch, Glob, AskUserQuestion, TaskCreate, TaskUpdate
---

# Research for Blog Post

Automate the full research pipeline for blog post writing: from article title to a comprehensive research report backed by real competitor articles.

## Credentials

Before starting, read the credentials file:

```bash
cat ~/.claude/credentials/research-for-blog-post.json
```

This file contains:
- `google_api_key` — Google Custom Search API key
- `google_custom_search_id` — Google Programmable Search Engine ID

If the file contains placeholder values (`YOUR_*`), stop and ask the user to populate it with real credentials before proceeding.

## Step 1 — Collect Input

Ask the user for these inputs using AskUserQuestion:

| Input | Required | Description |
|---|---|---|
| **Article title** | Yes | The full title of the blog post (e.g., "17 Best Crowdfunding Sites in 2025") |
| **Main keyword** | Yes | The primary SEO keyword (e.g., "best crowdfunding sites") |
| **Target market** | No | Geographic market, defaults to "us" (e.g., "us", "uk", "us,uk") |

The number of search terms is always **3** — do not ask the user about this.

## Step 2 — Generate 3 Search Terms

Generate exactly 3 Google search terms from the title and main keyword. The first search term is ALWAYS the main keyword itself. The remaining 2 should cover different angles of the topic as expressed in the title.

**How to derive search terms — analyze the title structure:**

- Title: "How to Make Money With Your Voice: Full Guide (+ 9 Top Sites)"
  - Search 1: "How to Make Money With Your Voice" (main keyword)
  - Search 2: "Top Websites to Make Money With Your Voice"
  - Search 3: "Ways to Earn Money Using Your Voice Online"

- Title: "17 Best Crowdfunding Sites in 2025 (Fund Your Campaign Quickly)"
  - Search 1: "Best Crowdfunding Sites in 2025" (main keyword)
  - Search 2: "Best Crowdfunding Sites to Fund Your Campaign"
  - Search 3: "Top Crowdfunding Platforms Comparison 2025"

- Title: "55 Top Selling Summer Products w/ High Profit Margins (2025)"
  - Search 1: "Top Selling Summer Products 2025" (main keyword)
  - Search 2: "Summer Products with High Profit Margins"
  - Search 3: "Best Summer Products to Sell Online 2025"

- Title: "45 Eco-Friendly Products to Sell (+ How to Market to Consumers)"
  - Search 1: "Eco-Friendly Products to Sell" (main keyword)
  - Search 2: "How to Market Eco-Friendly Products"
  - Search 3: "Best Sustainable Products to Sell Online"

The key principle: each search term should surface different types of competitor articles covering different angles of the same topic.

## Step 3 — Search Google

For each of the 3 search terms, call the Google Custom Search API. Read the credentials from the JSON file first, then run:

```bash
curl -s "https://www.googleapis.com/customsearch/v1?key=GOOGLE_API_KEY&cx=GOOGLE_CX_ID&q=ENCODED_QUERY&num=10&siteSearch=reddit.com&siteSearchFilter=e&gl=TARGET_MARKET&hl=en"
```

Parameters:
- `num=10` — 10 results per search term
- `siteSearch=reddit.com` + `siteSearchFilter=e` — excludes Reddit results
- `gl` — set to the target market (default: `us`)
- `hl=en` — English language results

URL-encode the search query. Collect all `items[].title` and `items[].link` from each response.

## Step 4 — Filter and Deduplicate

From the combined results (up to 30 URLs), remove:

1. **Documents** — any result that has a `mime` field (PDFs, DOCs, etc.)
2. **YouTube** — URLs containing `youtube.com/watch`
3. **Quora** — URLs containing `quora.com`
4. **Indeed** — URLs containing `indeed.com`
5. **Duplicates** — remove duplicate URLs, keeping the first occurrence

Present the filtered list (titles + URLs) for the next step.

## Step 5 — Choose Best Articles

From the filtered results, select **3 to 5** of the best articles for in-depth research. Prioritize:

1. **Official sources** — if the topic is about a specific product/service/brand, prioritize the official website
2. **High relevance** — articles that closely match the title's topic and angle
3. **Similar scope** — articles with a similar (or slightly higher, but not 2x-3x) number of items in the title compared to ours
4. **Target market match** — exclude URLs that are clearly not for the target market

**Special rule for pricing/cost keywords:** If the main keyword follows a "brand + pricing/prices/cost" pattern (e.g., "Shopify pricing", "Wix costs"), select ONLY 1-3 URLs from the official brand website. Ignore all non-official sources.

## Step 6 — Fetch and Convert Articles

For each chosen article, fetch the full page content using **WebFetch** (primary method). Then:

1. Extract the main body content (ignore navigation, sidebars, footers, cookie banners)
2. Convert to clean markdown
3. Remove all image references (`![...](...))`)
4. Remove excessive blank lines (collapse multiple newlines into one)
5. Wrap each article:
   ```
   Article Start

   [markdown content here]

   Article End
   ```

### Fallback — Firecrawl API

If WebFetch fails for an article (timeout, 403, empty content, or any error), retry that article using the Firecrawl scrape API:

```bash
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer fc-081d45bb947345409a3471fe9e58383b" \
  -d '{"url": "ARTICLE_URL", "formats": ["markdown"]}'
```

The response JSON contains the markdown content at `data.markdown`. Use that as the article content and apply the same cleanup steps (remove images, collapse blank lines, wrap with Article Start/End).

Only skip an article if **both** WebFetch and Firecrawl fail.

## Step 7 — Generate Research Report

You are a meticulous and highly skilled Research Analyst. Your reports are always comprehensive and thorough — 2000 to 5000 words. Prioritize official sources of information (if topic is product/service review, price guide, prioritize official website as info source).

**Objective:** Perform an exhaustive and in-depth analysis of the provided collection of articles. Based on this analysis, generate a report (in markdown) focused on the article title topic. If the topic includes a number of items, ALWAYS create a report that has the same number of items — do this by selecting the most relevant items from the articles you received. Important: always change the order of the items, put the best ones (in your opinion) on the top. Never copy the order of the items from one of the received articles.

### Core Instructions for Report Generation

1. **Absolute Comprehensiveness:**
   - You MUST extract and include every single relevant fact, statistic, data point, key figure, specific examples, and items mentioned in *all* provided articles that pertain to the topic.
   - Do not summarize to the point of omission. Err on the side of including too much detail rather than too little.
   - If a piece of information seems minor but is related to the topic, include it.
   - Pay close attention to numbers, dates, percentages, monetary values, websites, and specific claims.
   - Always extract external links from all articles along with the sentence where it appears. These are the links with target domain that is not the same as the host domain of the article (the host domain will have majority of the links in an article). DO NOT extract the internal links that point to the host domain.

2. **Ignore** generic website elements like cookie policies, etc.

3. **Information Integrity & Attribution:**
   - Present information as factually as it is stated in the articles.
   - **Crucially, for each piece of information (fact, statistic, item), clearly indicate which article it was sourced from.**
   - If different articles present conflicting information on the same point, you must present both (or all) conflicting pieces of information and clearly state that they are conflicting, attributing each to its source article.

4. **Report Structure:**
   Organize the report logically. Use the following structure, but adapt as necessary based on the nature of the topic and the content of the articles:

   - **A. Executive Summary of Findings:**
     - A brief (1 very short paragraph) overview of the most critical information and overarching themes related to the topic found across all articles.
     - A list of source articles with titles.

   - **B. Detailed Factual Extraction:**
     - This is the main body of the report. Organize this section by sub-themes or categories inherent to the topic if they emerge from the articles.
     - For each fact, statistic, or item:
       - Clearly state the information.
       - Provide the source article identifier (e.g., "[Article 1]").

   - **C. Consolidated Key Statistics and Data Points:**
     - A list or table summarizing all numerical data (percentages, counts, financial figures, dates, etc.) related to the topic. Include source attribution for each.

   - **D. External links with the sentences:**
     - A list of sentences that contain an external link.

   - **E. *(Optional)* Create a comparison table or other table with important info if you have enough data for it.**

5. **Tone and Style:**
   - Maintain an objective, factual, and analytical tone.
   - Avoid speculation, personal opinions, or interpretations not explicitly supported by the text of the articles.
   - Use clear and precise language.

**Final Review Instruction:** Before presenting the final report, mentally re-scan all provided articles one last time specifically looking for any details related to the topic that might have been missed in your initial extraction. The goal is zero missed relevant information.

The report must be ultra comprehensive and include ALL relevant data bits, facts, numbers.

## Step 8 — Save Output

Save the research report to `research-report-KEYWORD.md` in the current working directory, where `KEYWORD` is the main keyword with spaces replaced by hyphens and lowercased (e.g., main keyword "Best Crowdfunding Sites" → `research-report-best-crowdfunding-sites.md`).

Tell the user:
- How many articles were analyzed
- The word count of the report
- The file path where it was saved
