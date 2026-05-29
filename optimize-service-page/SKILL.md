---
name: optimize-service-page
description: End-to-end service page content optimization. Fetches NeuronWriter data and Google SERP/PAA, optimizes content for keyword compliance and SEO, then uploads back to NeuronWriter. Requires a NeuronWriter query ID. Works for any client with a Content Brain and supporting scripts.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion
---

# Service Page Content Optimization

Fully automated workflow: fetch NeuronWriter data → fetch Google SERP/PAA → optimize content → keyword compliance loop → upload to NeuronWriter → archive files.

## Input

The user provides a **NeuronWriter query ID** (e.g., `90b738d35df43d13`). This is the only required input.

## Prerequisites Check

Before starting, verify ALL of the following exist in the current working directory. If any are missing, stop and tell the user what's needed.

1. **`fetch_neuronwriter.py`** — Script to pull content and requirements from NeuronWriter
2. **`fetch_serp_titles.py`** — Script to pull SERP titles and PAA questions from DataForSEO
3. **`upload_to_neuronwriter.py`** — Script to upload optimized content back to NeuronWriter
4. **`config.json`** — Must contain `apiKey` for NeuronWriter API
5. **`Content brain/contentbrain.md`** — Client voice, positioning, and terminology guide
6. **`internal_urls.csv`** — List of internal site URLs available for linking

Use `Glob` to verify these files exist. Do NOT proceed if any are missing.

---

## Phase 1: Data Collection

### Step 1.1 — Fetch from NeuronWriter

Run the fetch script with the provided query ID:

```
echo "{QUERY_ID}" | python fetch_neuronwriter.py
```

This produces two files:
- `{keyword}-content.md` — Current page content in Markdown
- `{keyword}-requirements.json` — NeuronWriter optimization requirements

### Step 1.2 — Fetch SERP and PAA

Run the SERP titles script (auto-detects the requirements file):

```
python fetch_serp_titles.py
```

This produces two more files:
- `{keyword}-serp.json` — Organic SERP results
- `{keyword}-paa.json` — People Also Ask questions from Google

**Wait for both scripts to complete before proceeding.** The SERP script takes ~30 seconds due to API polling.

---

## Phase 2: Pre-Analysis

Read ALL input files before writing anything. This phase is critical — skipping it leads to keyword stuffing and word count violations.

### Step 2.1 — Read Content Brain

Read `Content brain/contentbrain.md` in full. This is the #1 authority on voice and positioning. Extract and internalize:
- **Mandatory positioning** (e.g., "U.S. manufacturer" not "sourcing company")
- **Forbidden terms** (e.g., "outsourcing," "broker," "contract manufacturing")
- **Tone and voice rules** (e.g., hybrid we/you, consultative, no ChatGPT slop)
- **Terminology rules** (what to always use, never use, handle with care)

**If Content Brain rules conflict with any NeuronWriter keyword target, Content Brain wins.** For example, if NeuronWriter recommends the keyword "sourcing" but Content Brain forbids it, do NOT use "sourcing."

### Step 2.2 — Read Requirements JSON

From `{keyword}-requirements.json`, extract:
- `metrics.word_count.target` — Competitor word count target
- `content_basic_w_ranges` — Primary keywords with usage ranges (HARD LIMITS)
- `content_extended_w_ranges` — Extended/LSI keywords to add naturally
- `h1_terms` and `h2_terms` — Heading keyword recommendations with `usage_pc`
- `competitors` — Top-ranking pages for context
- `people_also_ask` — NeuronWriter PAA (may be empty)

### Step 2.3 — Read Current Content and Lock Word Count

Read `{keyword}-content.md` and count its words. This word count becomes your target:

- **If original word count > NeuronWriter target:** Your optimized content must be within ±10% of the ORIGINAL word count. Do not inflate or deflate.
- **If original word count < NeuronWriter target:** Expand to 120% of the NeuronWriter target (target × 1.2).

**State the word count target explicitly** before writing (e.g., "Original: 950 words. Target range: 855–1,045 words.").

### Step 2.4 — Pre-Optimization Keyword Audit

**Before writing anything**, run the Python keyword counter on the ORIGINAL content to understand what's currently stuffed vs. missing. This creates a "before" baseline and tells you exactly which keywords need reduction vs. addition.

Run this Python script via Bash, substituting the content filename and the keywords parsed from `content_basic_w_ranges`:

```python
import re

with open('{keyword}-content.md', 'r', encoding='utf-8') as f:
    text = f.read().lower()

words = len(text.split())
print(f'Original word count: {words}')
print()

# Parse keywords from content_basic_w_ranges
keywords = {
    # 'keyword': (lower_bound, upper_bound),
    # ... populate from requirements JSON ...
}

print(f'{"Keyword":<35} {"Count":>5} {"Range":>10} {"Status":>10}')
print('-' * 65)

for kw, (lo, hi) in sorted(keywords.items(), key=lambda x: x[1][1]):
    count = len(re.findall(re.escape(kw), text))
    if count > hi:
        status = 'STUFFED'
    elif count < lo:
        status = 'MISSING'
    else:
        status = 'OK'
    print(f'{kw:<35} {count:>5} {lo}-{hi:>3}x {status:>10}')
```

Review the output. Note which keywords are STUFFED (must reduce) and which are MISSING (must add). This informs the rewrite strategy.

### Step 2.5 — Read PAA and Internal URLs

- Read `{keyword}-paa.json` for FAQ questions
- Read `internal_urls.csv` for internal linking targets
- Identify the page's own URL (to avoid self-linking) by matching the keyword to the most relevant URL in the list

---

## Phase 3: Content Optimization

You are an expert SEO copywriter. Rewrite the content following these rules strictly and in priority order.

### Rule 1: Minimal Rewriting Principle

Make the fewest changes necessary to meet optimization targets. Do not restructure paragraphs, change the narrative flow, or rewrite sentences that are already well-optimized. If a sentence already contains the right keywords in natural density, leave it alone.

### Rule 2: Content Basic Keywords — STRICT Range Enforcement

**This is the highest-priority rule.** Treat `content_basic_w_ranges` ranges as hard limits.

**CRITICAL — Substring Awareness:** Keywords share substrings. For example:
- "sand casting foundry" increments counts for "sand casting", "casting", AND "foundry"
- "cost-effectiveness" contains "cost-effective"
- "casting manufacturer" contains both "casting" and "manufacturer"

When adding a compound keyword, mentally increment ALL parent substring keywords and check they remain in range.

**Reducing keyword stuffing is the #1 goal.** Original content is typically keyword-stuffed — many keywords appear 3x to 10x above their target range. You MUST fix this.

Rules:
- **NEVER exceed the upper bound of any range.** This is a hard constraint.
- If a keyword is already within range, leave it alone.
- If underused, add naturally until it reaches the lower bound.
- **If overused, aggressively reduce it.** Use these de-stuffing techniques:
  - Replace with pronouns: "it," "they," "these," "this process," "the facility"
  - Replace with synonyms: "the foundry," "our operations," "this method," "the plant"
  - Replace location repetitions with: "here," "locally," "at this facility," "on-site"
  - Remove entire redundant sentences that exist only to repeat keywords

**Common stuffing patterns to eliminate:**
- The same phrase repeated in consecutive sentences or paragraphs
- Keyword in both the heading AND the first sentence of that section
- Keyword appearing in every bullet point in a list
- Gratuitous repetition of location + service name (e.g., "sand casting Mexico" in every section)

### Rule 3: Content Extended Keywords

Review `content_extended_w_ranges`. Add the **majority** (target 80%+) of these extended keywords where they fit naturally. Skip any that would feel forced or off-topic.

**Budget check:** After mentally placing extended keywords, verify that basic keyword ranges are still respected. Extended keywords often contain basic keywords as substrings.

### Rule 4: Proper Noun Capitalization

The requirements file lists all keywords in lowercase. Always capitalize proper nouns correctly:
- Country names: "India," "Mexico," "China," "United States"
- City/region names: "Gujarat," "Coimbatore," "Seattle"
- Company names: "Redstone," "Redstone Manufacturing"

### Rule 5: Word Count Compliance

Stay within ±10% of the word count target established in Step 2.3. If the original content was 950 words, your output must be between 855–1,045 words. Do NOT inflate content beyond the original length.

### Rule 6: Subheading Optimization (H2)

Only change an H2 if:
- The `h2_terms` list contains a keyword with `usage_pc` of 40 or above AND that keyword is completely absent from current subheadings.
- Even then, adjust wording slightly rather than replacing entire subheadings.

### Rule 7: Internal Linking

Insert **5 to 6 internal links** from `internal_urls.csv` into body content.

Rules:
- Links go in body text paragraphs only. **Never in headings (H1, H2, H3).**
- Do NOT link to the page's own URL.
- Choose topically related URLs (related services, country pages, material pages).
- **Anchor text ratio:** ~60% keyword-rich, ~40% generic/natural.
- Distribute links naturally throughout — not clustered in one section.

### Rule 8: FAQ Section

- If `{keyword}-paa.json` contains questions: Replace the FAQ section with these PAA questions. Write 2–3 sentence answers, direct and authoritative, in Content Brain voice. Skip PAA questions that are completely off-topic for the client's business.
- If PAA file has no questions: Preserve the original FAQ section as-is.
- Use Title Case for FAQ headings.

### Rule 9: SEO Metadata Block

Output at the very top of the content (before H1):

```
**SEO Title Option 1:** [title]
**SEO Title Option 2:** [title]
**SEO Title Option 3:** [title]
**URL:** [page URL from internal_urls.csv]
**Meta Description Option 1:** [description]
**Meta Description Option 2:** [description]
```

**SEO Title rules:**
- 3 options, each ≤60 characters
- End with parenthetical benefit: "(ISO Certified)", "(Fast Lead Times)", "(Competitive Pricing)", etc.
- Do NOT include the brand name in the title
- Primary keyword near the beginning; add small grammatical words for natural reading

**Meta Description rules:**
- 2 options, each ≤155 characters
- Include primary keyword + clear value proposition or CTA

### Output Format

Write the optimized content to `{keyword}-optimized.md` as clean Markdown:
- SEO metadata block at the top
- Same heading hierarchy (H1, H2, H3) as original
- Same section order
- Tables in Markdown format
- Internal links as `[anchor text](URL)`

---

## Phase 4: Keyword Compliance Loop

**This phase is mandatory. Do NOT skip it.**

After writing the optimized content, run the keyword compliance check using Python via Bash. Use the exact script pattern below, populated with ALL keywords from `content_basic_w_ranges`:

```python
import re

with open('{keyword}-optimized.md', 'r', encoding='utf-8') as f:
    text = f.read().lower()

words = len(text.split())
print(f'Total word count: {words}')
print()

keywords = {
    # Populate ALL keywords from content_basic_w_ranges
    # 'keyword': (lower_bound, upper_bound),
}

print(f'{"Keyword":<35} {"Count":>5} {"Range":>10} {"Status":>10}')
print('-' * 65)

issues = []
for kw, (lo, hi) in sorted(keywords.items(), key=lambda x: x[1][1]):
    count = len(re.findall(re.escape(kw), text))
    if count > hi:
        status = 'STUFFED'
        issues.append((kw, count, lo, hi))
    elif count < lo:
        status = 'MISSING'
        issues.append((kw, count, lo, hi))
    else:
        status = 'OK'
    print(f'{kw:<35} {count:>5} {lo}-{hi:>3}x {status:>10}')

if issues:
    print(f'\n=== {len(issues)} ISSUES FOUND ===')
    for kw, count, lo, hi in issues:
        print(f'  {kw}: {count}x (target {lo}-{hi}x)')
else:
    print('\nAll keywords within range!')
```

### Compliance Loop Rules

1. **If ALL keywords are within range:** Proceed to Phase 5.
2. **If issues exist:** Fix them using targeted `Edit` calls on the optimized file:
   - Fix the MOST over-limit keyword first (the one furthest above its upper bound)
   - Fixing one keyword often fixes others due to substring overlap
   - For STUFFED keywords: replace excess occurrences with synonyms, pronouns, or rephrase
   - For MISSING keywords: insert naturally into existing sentences
   - After edits, re-run the Python compliance check
3. **Repeat up to 3 total passes.** If issues remain after 3 passes, show the remaining issues and ask the user for guidance.
4. Also verify the word count is within ±10% of the target on each pass.

Also check extended keyword coverage on the final pass:

```python
# Add this to the compliance script
extended = [
    # List all extended keywords from content_extended_w_ranges
]
present = sum(1 for kw in extended if re.findall(re.escape(kw), text))
print(f'\nExtended keywords: {present}/{len(extended)} ({round(present/len(extended)*100)}%)')
```

Target: 80%+ of extended keywords present.

---

## Phase 5: Upload and Cleanup

### Step 5.1 — Upload to NeuronWriter

Run the upload script:

```
python upload_to_neuronwriter.py
```

This auto-detects the requirements file, reads `{keyword}-optimized.md`, converts to HTML, and uploads. Report the content score returned by NeuronWriter.

### Step 5.2 — Archive Intermediate Files

Create a `processed/` subfolder (if it doesn't exist) and move intermediate files there:

```bash
mkdir -p processed
mv {keyword}-content.md {keyword}-requirements.json {keyword}-serp.json {keyword}-paa.json processed/
```

Keep `{keyword}-optimized.md` in the working directory for reference.

### Step 5.3 — Update Optimized URLs Tracker

Maintain a CSV file called `optimized_urls.csv` in the **root folder** of the working directory. This is a running log of all optimized pages.

**Columns (all capitalized):**

```
QUERY ID,KEYWORD,WEBSITE URL,NEURONWRITER EDIT URL,NEURONWRITER READ URL,DATE,CONTENT SCORE,OLD WORD COUNT,NEW WORD COUNT
```

**Where to get each value:**
- **QUERY ID** — The NeuronWriter query ID provided by the user
- **KEYWORD** — From `{keyword}-requirements.json` → `keyword`
- **WEBSITE URL** — The page URL inferred from `internal_urls.csv` (same one used in the SEO metadata block)
- **NEURONWRITER EDIT URL** — From `{keyword}-requirements.json` → `share_url`
- **NEURONWRITER READ URL** — From `{keyword}-requirements.json` → `readonly_url`
- **DATE** — Today's date in `YYYY-MM-DD` format
- **CONTENT SCORE** — The score returned by the upload script (from the NeuronWriter API response)
- **OLD WORD COUNT** — Word count of the original `{keyword}-content.md`
- **NEW WORD COUNT** — Word count of the optimized `{keyword}-optimized.md`

**Rules:**
- If `optimized_urls.csv` does **not** exist, create it with the header row and then append the data row.
- If `optimized_urls.csv` **already exists**, read it first, then append a new row. Do NOT overwrite existing rows.
- If the same QUERY ID already has a row, **update that row** in place (replace with new values) rather than adding a duplicate.
- Use Python via Bash to handle the CSV read/append/update to avoid formatting issues.

Example Python snippet:

```python
import csv
import os
from datetime import date

csv_file = 'optimized_urls.csv'
headers = ['QUERY ID', 'KEYWORD', 'WEBSITE URL', 'NEURONWRITER EDIT URL',
           'NEURONWRITER READ URL', 'DATE', 'CONTENT SCORE', 'OLD WORD COUNT', 'NEW WORD COUNT']

new_row = {
    'QUERY ID': '{query_id}',
    'KEYWORD': '{keyword}',
    'WEBSITE URL': '{website_url}',
    'NEURONWRITER EDIT URL': '{share_url}',
    'NEURONWRITER READ URL': '{readonly_url}',
    'DATE': str(date.today()),
    'CONTENT SCORE': '{content_score}',
    'OLD WORD COUNT': '{old_word_count}',
    'NEW WORD COUNT': '{new_word_count}',
}

rows = []
exists = os.path.exists(csv_file)
if exists:
    with open(csv_file, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

# Update existing row or append new one
updated = False
for i, row in enumerate(rows):
    if row.get('QUERY ID') == new_row['QUERY ID']:
        rows[i] = new_row
        updated = True
        break
if not updated:
    rows.append(new_row)

with open(csv_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)

print(f'Tracker {"updated" if updated else "appended"}: {csv_file}')
```

### Step 5.4 — Report Results

Print a summary:
- NeuronWriter content score (before → after, if available)
- Word count (original → optimized)
- Keyword compliance status (all within range / X issues remaining)
- Extended keyword coverage (X/Y, Z%)
- Number of internal links inserted
- FAQ questions used

---

## Important Reminders

1. **Content Brain is the #1 authority.** All voice, positioning, and terminology rules from `Content brain/contentbrain.md` override everything else, including NeuronWriter keyword suggestions.
2. **De-stuffing is the primary goal.** Original content is almost always keyword-stuffed. Staying within keyword ranges is more important than any other optimization objective.
3. **Never compromise readability for keyword density.** Natural language always wins. If a keyword cannot be inserted without awkwardness, skip it.
4. **Word count discipline.** Do not inflate content beyond the original length. The ±10% guardrail is a hard constraint.
5. **Substring awareness is critical.** Every compound keyword also increments all its parent keyword counts. Track this as you write.
6. **Python verification is mandatory.** Never rely on internal counting — always run the Python script to verify compliance.
7. **Proper nouns are always capitalized** regardless of how they appear in the requirements data.
