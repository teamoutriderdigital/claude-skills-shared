---
name: ha-seo-titles
description: End-to-end SEO title generation pipeline for HostAdvice articles. Reads keywords from kws.csv, fetches top 10 Google SERP results via DataForSEO, analyzes competitor titles, then crafts 3 optimized SEO title proposals per keyword following strict SOP rules. Validates and saves results to seo_titles.csv. Use this skill whenever the user wants to generate SEO titles, craft title proposals, or run the HA title pipeline. Also triggers for "make SEO titles", "generate titles for keywords", "run the title pipeline", or "craft HostAdvice titles".
allowed-tools: Bash, Read, Write, Edit, Glob, TaskCreate, TaskUpdate
---

# HostAdvice SEO Title Generation Skill

End-to-end pipeline: `kws.csv` -> fetch SERP data -> analyze competitors -> craft 3 titles per keyword -> validate -> `seo_titles.csv`

## Prerequisites

Before running, ensure these files exist in the working directory:

| File | Description |
|---|---|
| `kws.csv` | One keyword per line, no header row |
| `fetch_serp_titles.py` | DataForSEO SERP fetcher script |

If either file is missing, stop and tell the user.

## Step 1 — Fetch SERP Competitor Titles

1. Read `kws.csv` to confirm keywords are present
2. Run `fetch_serp_titles.py` to fetch top 10 Google organic results for each keyword:
   ```
   python fetch_serp_titles.py
   ```
3. Verify `serp_titles.json` was created successfully

## Step 2 — Read SERP Data and Analyze Competitors

Read `serp_titles.json`. For each keyword, note:
- What type of pages are ranking (blog posts, product pages, forums, etc.)
- How competitors position their titles (recency, authority, listicle count, features, ease)
- Common patterns and angles across the top 10

## Step 3 — Craft 3 SEO Title Proposals Per Keyword

For each keyword, craft exactly 3 unique SEO title proposals. **You must craft the titles yourself — do NOT use a script to generate them.**

### Title Crafting Rules (SOP)

**Format:** `[ROOT KEYWORD] + [POSITIONING]`

**Hard constraints:**
- Maximum 60 characters per title
- MUST include parentheses `()` — this increases CTR and drives curiosity
- MUST include the full keyword (you can add small filler words like "in", "for", "on", "of", "and", "vs", "with", "how", "to", "a", "the" for grammar)
- Do NOT include any company/brand name

**Space-saving techniques:**
- Use "w/" instead of "with"
- Use "&" instead of "and"
- Use lowercase to save pixel width
- Use abbreviations where natural

**Positioning categories** (pick the best fit based on SERP analysis):
1. **Ease/simplicity/speed** — "Step-by-step guide", "5 min read", "Easy DIY"
2. **Authoritativeness/experience** — "From actual experts", "Real owner reviews", "Data-backed"
3. **Recency** — "2026", "Updated monthly"
4. **Features/UX** — "w/ Photos", "w/ Pros & Cons", "Sortable list"

**Stack multiple positionings** when possible. Example:
```
Golden Retriever Pros & Cons: Is one right for you? (+expert tips)
[Root Keyword]              [Positioning A]         [Positioning B]
```

**Try to differentiate from competitors** — don't just copy their angles. Consider:
- Leapfrogging (bigger listicle, more detail)
- Contrarian positioning
- Adding unique value props (calculators, data, comparisons)

**Each of the 3 titles should use a DIFFERENT positioning angle** to give variety.

### Example Great Titles

- `43 Best Travel Jobs 2025 (w/ Salaries & Pros + Cons)`
- `77 Best Businesses To Start W/ 10K (& how to pick one)`
- `27 Legit Jobs for Stay-at-Home Moms in 2025 (Earn Fast!)`
- `How To Find All My Debts (& Pay Them Off)`
- `Types of Bank Accounts: How To Set Them Up (& What To Avoid)`

## Step 4 — Validate and Save to CSV

After crafting all titles, create and run a Python validation script:

```python
import csv
import sys

titles = [
    # INSERT ALL CRAFTED TITLES HERE AS DICTS:
    # {"keyword": "...", "title_1": "...", "title_2": "...", "title_3": "..."},
]

# Write CSV
with open("seo_titles.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["keyword", "title_1", "title_2", "title_3"])
    writer.writeheader()
    writer.writerows(titles)

print(f"Wrote {len(titles)} rows to seo_titles.csv")

# Validation
FILLER_WORDS = {"a", "the", "to", "in", "for", "on", "of", "and", "vs", "with", "how", "is", "it", "do", "an", "or"}
errors = []
for row in titles:
    kw = row["keyword"]
    kw_words = [w for w in kw.lower().split() if w not in FILLER_WORDS]
    for col in ["title_1", "title_2", "title_3"]:
        title = row[col]
        if len(title) > 60:
            errors.append(f"  OVER 60 chars ({len(title)}): [{kw}] {col} = {title}")
        if "(" not in title or ")" not in title:
            errors.append(f"  NO PARENS: [{kw}] {col} = {title}")
        title_lower = title.lower()
        for word in kw_words:
            if word not in title_lower:
                errors.append(f"  MISSING KW WORD '{word}': [{kw}] {col} = {title}")
                break

if errors:
    print(f"\n{len(errors)} issues found:")
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print("All titles pass validation (<=60 chars, contain parens, contain keyword)")
```

If validation fails, fix the failing titles and re-run until all pass.

## Output

Final deliverable: `seo_titles.csv` with columns `keyword,title_1,title_2,title_3` — all validated.
