"""
Fetch all page/post URLs from a website's XML sitemap(s).

Usage:
    python fetch_sitemap_urls.py <domain> [--output internal_urls.csv]

The script:
1. Fetches /sitemap.xml from the domain
2. Handles sitemap index files (follows child sitemaps)
3. Filters out non-content URLs (tags, categories, images, feeds, etc.)
4. Writes one URL per line to the output file
"""

import argparse
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

# URL path segments that indicate non-content pages
EXCLUDED_PATH_SEGMENTS = [
    "/tag/",
    "/tags/",
    "/category/",
    "/categories/",
    "/author/",
    "/wp-content/",
    "/wp-admin/",
    "/wp-includes/",
    "/wp-json/",
    "/feed/",
    "/feeds/",
    "/comments/",
    "/trackback/",
    "/attachment/",
    "/embed/",
    "/cart/",
    "/checkout/",
    "/my-account/",
    "/wp-login",
    "/xmlrpc",
    "/wp-cron",
    "/uncategorized/",
]

# Exact path slugs for legal/utility pages that aren't real content
EXCLUDED_SLUGS = [
    "privacy-policy",
    "privacy",
    "terms-of-use",
    "terms-of-service",
    "terms-and-conditions",
    "terms-conditions",
    "terms",
    "cookie-policy",
    "cookies",
    "accessibility",
    "accessibility-statement",
    "disclaimer",
    "legal",
    "legal-notice",
    "gdpr",
    "data-protection",
    "refund-policy",
    "return-policy",
    "shipping-policy",
    "acceptable-use-policy",
    "dmca",
    "copyright",
    "quote-confirmation",
    "thank-you",
    "thankyou",
    "confirmation",
]

# File extensions that indicate media/non-page resources
EXCLUDED_EXTENSIONS = [
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".bmp", ".ico",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".zip", ".rar", ".gz", ".tar",
    ".mp3", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm",
    ".css", ".js", ".xml", ".json", ".txt",
    ".woff", ".woff2", ".ttf", ".eot",
]

# Pagination pattern
PAGINATION_PATTERN = re.compile(r"/page/\d+/?$")

# Common sitemap XML namespaces
SITEMAP_NS = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "image": "http://www.google.com/schemas/sitemap-image/1.1",
    "video": "http://www.google.com/schemas/sitemap-video/1.1",
    "news": "http://www.google.com/schemas/sitemap-news/0.9",
}


def normalize_domain(domain: str) -> str:
    """Ensure domain has https:// prefix and no trailing slash."""
    domain = domain.strip().rstrip("/")
    if not domain.startswith(("http://", "https://")):
        domain = "https://" + domain
    return domain


def fetch_url(url: str) -> str:
    """Fetch URL content as string."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; SitemapCrawler/1.0)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_sitemap(xml_content: str) -> tuple[list[str], list[str]]:
    """
    Parse sitemap XML and return (page_urls, child_sitemap_urls).
    Handles both sitemap index files and regular sitemaps.
    """
    page_urls = []
    child_sitemaps = []

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return page_urls, child_sitemaps

    # Strip namespace for easier tag matching
    tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

    if tag == "sitemapindex":
        # This is a sitemap index — collect child sitemap URLs
        for sitemap in root.findall("sm:sitemap/sm:loc", SITEMAP_NS):
            if sitemap.text:
                child_sitemaps.append(sitemap.text.strip())
        # Fallback without namespace
        if not child_sitemaps:
            for sitemap in root.iter():
                stag = sitemap.tag.split("}")[-1] if "}" in sitemap.tag else sitemap.tag
                if stag == "loc" and sitemap.text:
                    parent_tag = ""
                    # Walk up to check parent
                    for parent in root.iter():
                        for child in parent:
                            if child is sitemap:
                                parent_tag = parent.tag.split("}")[-1] if "}" in parent.tag else parent.tag
                    if parent_tag == "sitemap":
                        child_sitemaps.append(sitemap.text.strip())
    else:
        # Regular sitemap — collect page URLs
        for url_elem in root.findall("sm:url/sm:loc", SITEMAP_NS):
            if url_elem.text:
                page_urls.append(url_elem.text.strip())
        # Fallback without namespace
        if not page_urls:
            for elem in root.iter():
                etag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                if etag == "loc" and elem.text:
                    page_urls.append(elem.text.strip())

    return page_urls, child_sitemaps


def is_content_url(url: str) -> bool:
    """Return True if the URL looks like an actual page or post."""
    url_lower = url.lower()
    parsed = urlparse(url_lower)
    path = parsed.path

    # Exclude URLs with non-content path segments
    for segment in EXCLUDED_PATH_SEGMENTS:
        if segment in path:
            return False

    # Exclude legal/utility pages by slug (last meaningful path segment)
    slug = path.strip("/").split("/")[-1] if path.strip("/") else ""
    if slug in EXCLUDED_SLUGS:
        return False

    # Exclude media/file extensions
    for ext in EXCLUDED_EXTENSIONS:
        if path.endswith(ext):
            return False

    # Exclude pagination
    if PAGINATION_PATTERN.search(path):
        return False

    # Exclude image/video sitemap URLs (they often have image/video in the sitemap URL itself)
    if "image-sitemap" in url_lower or "video-sitemap" in url_lower:
        return False

    return True


def crawl_sitemap(domain: str) -> list[str]:
    """Crawl the sitemap tree starting from /sitemap.xml and return filtered URLs."""
    base_url = normalize_domain(domain)
    sitemap_url = f"{base_url}/sitemap.xml"

    all_urls = []
    sitemaps_to_process = [sitemap_url]
    processed_sitemaps = set()

    while sitemaps_to_process:
        current_sitemap = sitemaps_to_process.pop(0)
        if current_sitemap in processed_sitemaps:
            continue
        processed_sitemaps.add(current_sitemap)

        print(f"Fetching: {current_sitemap}")
        try:
            content = fetch_url(current_sitemap)
        except Exception as e:
            print(f"  Warning: Could not fetch {current_sitemap}: {e}")
            # Try common alternatives if the main sitemap fails
            if current_sitemap == sitemap_url:
                alternatives = [
                    f"{base_url}/sitemap_index.xml",
                    f"{base_url}/wp-sitemap.xml",
                    f"{base_url}/post-sitemap.xml",
                    f"{base_url}/page-sitemap.xml",
                ]
                for alt in alternatives:
                    if alt not in processed_sitemaps:
                        print(f"  Trying alternative: {alt}")
                        sitemaps_to_process.append(alt)
            continue

        page_urls, child_sitemaps = parse_sitemap(content)

        # Filter child sitemaps — skip image/video sitemaps entirely
        for child in child_sitemaps:
            child_lower = child.lower()
            if any(skip in child_lower for skip in ["image-sitemap", "video-sitemap", "news-sitemap"]):
                print(f"  Skipping non-content sitemap: {child}")
                continue
            if child not in processed_sitemaps:
                sitemaps_to_process.append(child)

        all_urls.extend(page_urls)

    # Filter and deduplicate
    filtered = []
    seen = set()
    for url in all_urls:
        if url not in seen and is_content_url(url):
            seen.add(url)
            filtered.append(url)

    return filtered


def main():
    parser = argparse.ArgumentParser(description="Fetch page/post URLs from a website's XML sitemap")
    parser.add_argument("domain", help="Domain to crawl (e.g., example.com)")
    parser.add_argument("--output", "-o", default="internal_urls.csv", help="Output file path (default: internal_urls.csv)")
    args = parser.parse_args()

    urls = crawl_sitemap(args.domain)

    if not urls:
        print("No content URLs found. The site may not have an accessible sitemap.")
        sys.exit(1)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(urls) + "\n")

    print(f"\nDone! Saved {len(urls)} URLs to {args.output}")


if __name__ == "__main__":
    main()
