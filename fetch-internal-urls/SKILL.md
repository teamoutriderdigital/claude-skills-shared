---
name: fetch-internal-urls
description: >
  Crawl a website's XML sitemap and extract all real page and post URLs, filtering out
  tags, categories, images, media, feeds, pagination, and other non-content URLs. Saves
  results as a plain-text CSV (one URL per line). Use this skill whenever the user wants
  to get a list of pages from a website, extract internal URLs from a sitemap, build a
  URL inventory, or audit which pages exist on a site. Also triggers for requests like
  "crawl the sitemap", "get all pages from this domain", "fetch the URLs", or
  "build an internal URL list". Even if the user just mentions needing a list of URLs
  from a website, this skill applies.
---

# Fetch Internal URLs

Extract all real page and post URLs from a website's XML sitemap. This is useful for
content audits, SEO workflows, and any task that needs a clean list of a site's actual
content pages.

## How it works

A bundled Python script handles the heavy lifting:

1. **Auto-detects the sitemap** — tries `/sitemap.xml` first, then falls back to
   `/sitemap_index.xml`, `/wp-sitemap.xml`, and other common locations
2. **Follows sitemap indexes** — if the root sitemap is an index pointing to child
   sitemaps, it follows them all (skipping image/video/news sitemaps)
3. **Filters aggressively** — removes URLs that are clearly not content pages:
   - Tag, category, and author archive pages
   - WordPress admin/system paths
   - Media files (images, PDFs, videos, etc.)
   - Pagination URLs (`/page/2/`, etc.)
   - Feed and comment URLs
4. **Deduplicates** — ensures no URL appears twice
5. **Outputs a clean file** — one URL per line, no headers, no extra columns

## Usage

Run the bundled script from this skill's directory:

```bash
python "<skill-path>/scripts/fetch_sitemap_urls.py" <domain> --output internal_urls.csv
```

Where `<domain>` is just the domain name (e.g., `example.com` — the script adds `https://` automatically if missing).

The `--output` flag defaults to `internal_urls.csv` in the current working directory.

## When the user provides a domain

If the user gives you a domain or website URL, extract just the domain and run the script.
If the user doesn't specify a domain, ask them for one.

## Output format

The output is a plain text file with one URL per line — no CSV headers, no columns, just
URLs. Example:

```
https://example.com/services/widget-repair/
https://example.com/about/
https://example.com/blog/how-to-fix-widgets/
```

## After fetching

Once the script finishes, report:
- How many URLs were found
- The output file path
- A brief sample of the first few URLs so the user can verify the results look right

If the user wants to exclude or include additional URL patterns, you can modify the
filter lists in the script or post-process the output file.
