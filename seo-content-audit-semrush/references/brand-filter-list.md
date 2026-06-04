# Navigational/Brand Keyword Filter

Keywords where users are searching for a specific company or platform are navigational — they won't convert for the client. Remove them before calculating opportunity metrics.

## Step 1: Dynamic Competitor Brand Extraction

Extract brand filter patterns from each competitor domain listed in the keyword gap CSV columns.

**Process:**
1. Read the competitor domain names from the keyword gap CSV header row
2. For each competitor domain, derive brand name patterns:
   - Strip the TLD (.com, .net, .org, etc.)
   - Split on common business-type words (services, solutions, group, inc, llc, pro, plus, digital, online, agency, co)
   - The remaining prefix is the brand name
   - Generate filter variants: "{brand}", "{brand} {industry-word}", "{industry-word} {brand}"

**Example pattern extraction (generic):**
- `acmeplumbing.com` → filter: "acme plumbing", "acme"
- `bestlawncare.net` → filter: "best lawn care" (but be careful — "best" alone is too generic, see exceptions below)
- `smithandjoneslaw.com` → filter: "smith and jones", "smith jones", "s&j law"
- `quickfixrepair.com` → filter: "quickfix", "quick fix repair"

**Also extract:**
- Common abbreviations (first letters of multi-word brands)
- Misspellings you spot in the keyword data (people often misspell brand names)
- The full domain without TLD as a filter pattern

## Step 2: Universal Platform Filters

These platforms appear as navigational searches across virtually all industries. Always filter them:

**Search/Social/General:**
- google, bing, yahoo
- facebook, instagram, tiktok, youtube, pinterest, twitter/x
- reddit, quora
- wikipedia, wiki
- amazon, ebay, craigslist, walmart
- yelp, bbb (better business bureau), trustpilot, glassdoor

**These are almost always navigational** when they appear as the primary subject of a keyword. However, do NOT filter keywords where these platforms are incidental context (e.g., "how to get reviews on yelp" might be relevant for a marketing client).

## Step 3: SEMrush Intent Flag

Also remove any keyword where the SEMrush `Intents` column contains "Navigational" as the sole or primary intent.

## How to Apply

Case-insensitive substring matching against the keyword text. If any filter pattern appears in the keyword, remove it.

**Critical exceptions — do NOT filter:**
- The **client's own brand** (they should rank for their own name)
- Generic words that happen to be part of a brand (e.g., "freedom" alone is too broad — only filter "freedom [industry term]" or the full brand name)
- Industry terms where a brand word is coincidental (e.g., don't filter "express delivery" just because "Express" is a competitor name — filter "express logistics inc" instead)
- Keywords where a platform name is the object, not the subject (e.g., "how to advertise on facebook" is relevant for a marketing agency)

**Rule of thumb:** A filter pattern should be specific enough that it only matches when someone is clearly looking for that specific brand, not when the word appears in a generic context.
