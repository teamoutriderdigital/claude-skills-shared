---
name: create-service-page-b2b
description: End-to-end B2B service page content creation from scratch. Fetches NeuronWriter requirements and Google SERP/PAA, calculates target word count from top competitors, analyzes a template page for structure, then creates new content following Content Brain rules, keyword compliance, and SEO best practices. Uploads to NeuronWriter when complete. Requires a NeuronWriter query ID. Works for any B2B client with a Content Brain and supporting scripts.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebFetch, Agent, AskUserQuestion
---

# Create Service Page B2B

Create a new B2B service page from scratch: fetch NeuronWriter data -> fetch Google SERP/PAA -> calculate word count from competitors -> select and analyze template page -> write content -> keyword compliance loop -> upload to NeuronWriter -> track in CSV.

## Input

The user provides a **NeuronWriter query ID** (e.g., `90b738d35df43d13`). This is the only required input. Template selection and word count approval happen interactively during the workflow.

## Prerequisites Check

Before starting, verify ALL of the following exist in the current working directory. If any are missing, stop and tell the user what's needed.

1. **`fetch_neuronwriter.py`** -- Script to pull content and requirements from NeuronWriter
2. **`fetch_serp_titles.py`** -- Script to pull SERP titles and PAA questions from DataForSEO
3. **`upload_to_neuronwriter.py`** -- Script to upload content to NeuronWriter
4. **`config.json`** -- Must contain `apiKey` for NeuronWriter API
5. **`Content brain/contentbrain.md`** -- Client voice, positioning, and terminology guide
6. **`internal_urls.csv`** -- List of internal site URLs available for linking

Use `Glob` to verify these files exist. Do NOT proceed if any are missing.

---

## Phase 1: Data Collection

### Step 1.1 -- Fetch from NeuronWriter

Run the fetch script with the provided query ID:

```
echo "{QUERY_ID}" | python fetch_neuronwriter.py
```

This produces two files:
- `{keyword}-content.md` -- Current page content in Markdown (may be empty or minimal for a new page)
- `{keyword}-requirements.json` -- NeuronWriter optimization requirements

**Note:** For new pages, the content file may be empty or contain placeholder text. This is expected. We are creating content from scratch, not optimizing existing content.

### Step 1.2 -- Fetch SERP and PAA

Run the SERP titles script (auto-detects the requirements file):

```
python fetch_serp_titles.py
```

This produces two more files:
- `{keyword}-serp.json` -- Organic SERP results
- `{keyword}-paa.json` -- People Also Ask questions from Google

**Wait for both scripts to complete before proceeding.** The SERP script takes ~30 seconds due to API polling.

---

## Phase 2: Word Count Calculation

### Step 2.1 -- Extract Competitor Word Counts

From `{keyword}-requirements.json`, read the `competitors` array. Each competitor has a `word_count` field.

Take the competitors ranked 1 through 5 (by `rank` field). If fewer than 5 competitors exist, use all available.

### Step 2.2 -- Filter and Calculate Average

Apply the word count filter: **only include competitors with word_count between 300 and 4000 words.** This removes outliers (thin pages under 300 words and mega-pages over 4000 words that skew the average).

Calculate the average word count of the qualifying competitors. Round to the nearest 50.

Run this calculation via Python in Bash:

```python
import json

with open('{keyword}-requirements.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

competitors = data.get('competitors', [])
# Sort by rank and take top 5
competitors_sorted = sorted(competitors, key=lambda c: int(c.get('rank', 999)))[:5]

print("Top 5 Competitors:")
print(f"{'Rank':<6} {'Word Count':>10} {'Qualifies':>10}  URL")
print("-" * 80)

qualifying = []
for c in competitors_sorted:
    wc = int(c.get('word_count', 0))
    qualifies = 300 <= wc <= 4000
    if qualifies:
        qualifying.append(wc)
    print(f"{c.get('rank', '?'):<6} {wc:>10} {'YES' if qualifies else 'NO':>10}  {c.get('url', 'N/A')[:50]}")

if qualifying:
    raw_avg = sum(qualifying) / len(qualifying)
    target = round(raw_avg / 50) * 50  # Round to nearest 50
    print(f"\nQualifying pages: {len(qualifying)}/{len(competitors_sorted)}")
    print(f"Average word count: {raw_avg:.0f}")
    print(f"Rounded target: {target} words")
else:
    print("\nNo qualifying pages found (all outside 300-4000 range).")
    print("Defaulting to NeuronWriter target.")
    target = data.get('metrics', {}).get('word_count', {}).get('target', 1000)
    print(f"NeuronWriter target: {target} words")
```

### Step 2.3 -- User Approval

**STOP and ask the user for approval before proceeding.** Present:
- The list of top 5 competitors with their word counts and qualification status
- The calculated target word count
- Ask: "The calculated target word count is **{target} words**. Should I proceed with this target, or would you like to adjust it?"

Wait for the user's response. If they provide a different number, use that instead.

**Fallback:** If no competitors qualify (all outside 300-4000 range), use the NeuronWriter `metrics.word_count.target` value and inform the user.

---

## Phase 3: Template Selection and Analysis

### Step 3.1 -- Propose Template URLs

Read `internal_urls.csv` and propose **5 service page URLs** for the user to choose from as structural templates. Select URLs that are:
1. Service pages (identify by URL patterns such as `/services/`, `/solutions/`, or other service-related paths on the site)
2. Topically related to the target keyword where possible
3. Not the page being created (match keyword to URL to exclude it)

Present the 5 options in a numbered list:

```
Choose a template page (an existing service page whose structure the new page will follow):

1. [URL 1]
2. [URL 2]
3. [URL 3]
4. [URL 4]
5. [URL 5]

Enter a number (1-5), or paste your own URL:
```

Wait for the user's response.

### Step 3.2 -- Fetch and Analyze Template Page

Use `WebFetch` to fetch the chosen template URL. Analyze the page and extract:

1. The complete heading hierarchy (H1, H2, H3) in order
2. For each section (defined by its heading), the content type: intro paragraph, capabilities list, process/methodology description, benefits list, industries/clients served, credentials/certifications, FAQ, CTA section, table, etc.
3. The approximate word count of each section
4. Notable content patterns: tables, bullet lists, numbered steps, CTAs
5. The overall flow/narrative structure

### Step 3.3 -- Build Template Outline

From the analysis, create a structural outline that maps:
- Section order (H1, each H2, each H3)
- Content type per section (paragraph, table, list, FAQ, CTA)
- Approximate word allocation per section (proportional to the approved target word count)

Store this outline mentally for use in Phase 5.

---

## Phase 4: Pre-Analysis

Read ALL input files before writing anything. This phase is critical for producing well-targeted content.

### Step 4.1 -- Read Content Brain

Read `Content brain/contentbrain.md` in full. This is the #1 authority on voice and positioning. Extract and internalize:
- **Mandatory positioning** (how the company must be described)
- **Forbidden terms** (words and phrases that must never appear)
- **Tone and voice rules** (person, style, sentence structure)
- **Terminology rules** (what to always use, never use, handle with care)

**If Content Brain rules conflict with any NeuronWriter keyword target, Content Brain wins.** For example, if NeuronWriter recommends a keyword but Content Brain forbids that term, do NOT use it.

### Step 4.2 -- Read Requirements JSON

From `{keyword}-requirements.json`, extract:
- `content_basic_w_ranges` -- Primary keywords with usage ranges (HARD LIMITS)
- `content_extended_w_ranges` -- Extended/LSI keywords to add naturally
- `h1_terms` and `h2_terms` -- Heading keyword recommendations with `usage_pc`
- `competitors` -- Top-ranking pages for context (headings, structure)
- `people_also_ask` -- NeuronWriter PAA (may be empty)
- `serp_summary` -- Search intent data

### Step 4.3 -- Read PAA and Internal URLs

- Read `{keyword}-paa.json` for FAQ questions (prefer these over NeuronWriter PAA if available)
- Read `internal_urls.csv` for internal linking targets
- Identify the page's own URL (to avoid self-linking) by matching the keyword to the most relevant URL in the list

### Step 4.4 -- Parse Keyword Ranges

Parse ALL keywords from `content_basic_w_ranges` into a structured reference. For each keyword, note:
- The keyword string
- Lower bound (minimum occurrences)
- Upper bound (maximum occurrences)
- Whether it is a substring of other keywords (substring awareness)

Also parse `content_extended_w_ranges` for extended keyword targets.

---

## Phase 5: Content Creation

You are an expert SEO copywriter creating a new B2B service page from scratch. Follow these rules strictly and in priority order.

### Rule 1: Follow the Template Structure

Use the structural outline from Phase 3 as your blueprint. The new page must follow the same:
- Section order and heading hierarchy
- Content types per section (tables where the template has tables, lists where it has lists, etc.)
- General proportions (if the template devotes 30% of words to process description, do the same)

Adapt heading text and content to the NEW keyword/topic, but keep the structural pattern.

### Rule 2: Content Basic Keywords -- STRICT Range Enforcement

**This is the highest-priority rule.** Treat `content_basic_w_ranges` ranges as hard limits.

**CRITICAL -- Substring Awareness:** Keywords share substrings. For example:
- "digital marketing agency" increments counts for "digital marketing", "marketing", AND "agency"
- "cost-effectiveness" contains "cost-effective"
- "consulting services" contains both "consulting" and "services"

When adding a compound keyword, mentally increment ALL parent substring keywords and check they remain in range.

Rules:
- **NEVER exceed the upper bound of any range.** This is a hard constraint.
- Target the middle of each range for a natural distribution.
- **Track compound keywords carefully.** Every time you write a multi-word keyword, also count it against all parent keywords.

### Rule 3: Content Extended Keywords

Review `content_extended_w_ranges`. Add the **majority** (target 80%+) of these extended keywords where they fit naturally. Skip any that would feel forced or off-topic.

**Budget check:** After mentally placing extended keywords, verify that basic keyword ranges are still respected. Extended keywords often contain basic keywords as substrings.

### Rule 4: Proper Noun Capitalization

The requirements file lists all keywords in lowercase. Always capitalize proper nouns correctly:
- Country names: "India," "Mexico," "China," "United States"
- City/region names: "Gujarat," "Coimbatore," "Seattle"
- Company names as specified in Content Brain

### Rule 5: Word Count Compliance

Stay within +/-10% of the target word count approved in Phase 2. If the approved target is 1200 words, your output must be between 1,080 and 1,320 words.

### Rule 6: Heading Optimization (H1 and H2)

- **H1:** Include the primary keyword. Use Title Case. Check `h1_terms` for high-usage keywords (usage_pc >= 40).
- **H2s:** Adapt from the template structure. Incorporate keywords from `h2_terms` where `usage_pc` is 40 or above. Use question format where appropriate per Content Brain rules. Title Case.

### Rule 7: Internal Linking

Insert **5 to 6 internal links** from `internal_urls.csv` into body content.

Rules:
- Links go in body text paragraphs only. **Never in headings (H1, H2, H3).**
- Do NOT link to the page's own URL.
- Choose topically related URLs (related services, industry pages, resource pages, location pages).
- **Anchor text ratio:** ~60% keyword-rich, ~40% generic/natural.
- Distribute links naturally throughout, not clustered in one section.

### Rule 8: FAQ Section

- If `{keyword}-paa.json` contains questions: Use these PAA questions as the FAQ. Write 2-3 sentence answers, direct and authoritative, in Content Brain voice. Skip PAA questions that are completely off-topic.
- If PAA file has no questions: Use NeuronWriter `people_also_ask` questions from the requirements JSON.
- If neither source has questions: Write 4-6 FAQ pairs based on common questions about the service/keyword topic, following Content Brain style.
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
- 3 options, each <=60 characters
- End with parenthetical benefit appropriate for the keyword: "(Fast Lead Times)" etc.
- Do NOT include the brand name in the title
- Primary keyword near the beginning; add small grammatical words for natural reading

**Meta Description rules:**
- 2 options, each <=155 characters
- Include primary keyword + clear value proposition or CTA

### Rule 10: No Bold Formatting on Keywords

Never bold keywords in the body text. Write them as normal text. Bold is reserved for key service terms, material names, and critical differentiators on first mention only, per Content Brain rules.

### Rule 11: Readability Level

All sentences must target a 10th-grade reading level or lower (Flesch-Kincaid Grade Level 10 or below). Write in short, clear sentences. Avoid long run-on sentences, complex clause stacking, and unnecessarily technical vocabulary when simpler words convey the same meaning. If a sentence feels dense or academic, break it into two shorter sentences.

### Rule 12: No Em-Dashes

**Never use em-dashes or en-dashes anywhere in the content.** This includes headings, body text, bullet points, FAQ answers, and metadata. Replace with commas, colons, periods, or rephrase the sentence.

### Rule 13: English Only -- No Foreign Words

**Never use foreign words or phrases in the content**, even if they appear in NeuronWriter keyword requirements lists (`content_basic_w_ranges`, `content_extended_w_ranges`, `h1_terms`, `h2_terms`). Skip any non-English term entirely. All content must be in standard American English.

### Rule 14: Human-Like Writing

The content must read as if written by a knowledgeable human, not generated by AI. Apply the following principles throughout:

- **High perplexity:** Vary your word choices and avoid predictable phrases. Do not default to the same adjectives, transitions, or sentence openers repeatedly. If you just wrote "This ensures...", do not start the next sentence with "This provides..." or "This allows...".
- **Burstiness:** Vary the length and style of both sentences and paragraphs. Mix short, punchy sentences (8-12 words) with slightly longer, more complex ones (18-25 words). A paragraph can be two sentences or six, depending on the point being made. Avoid uniform paragraph lengths.
- **Varied sentence openers:** Never start three or more sentences in a row with the same word or pattern. Avoid chains of "We provide... We offer... We ensure..." or "Our team... Our facility... Our process...". Restructure to lead with the benefit, the process, the material, or the outcome instead.
- **No robotic phrasing:** Steer clear of overly formal constructions, unnecessary hedging, and common AI filler phrases. Banned patterns include: "It is important to note," "In conclusion," "In today's competitive landscape," "When it comes to," "This allows for," "In the digital age," "plays a crucial role," "a wide range of," "designed to meet your needs." If a phrase sounds like it could appear in any AI-generated article on any topic, replace it with something specific to the actual service, material, or process being described.

### Output Format

Write the created content to `{keyword}-optimized.md` as clean Markdown:
- SEO metadata block at the top
- Heading hierarchy matching the template structure (H1, H2, H3)
- Tables in Markdown format
- Internal links as `[anchor text](URL)`

**Important:** The file MUST be named `{keyword}-optimized.md` (not `-created.md`) so the upload script can find it.

---

## Phase 6: Keyword Compliance Loop

**This phase is mandatory. Do NOT skip it.**

After writing the content, run the keyword compliance check using Python via Bash. Use the exact script pattern below, populated with ALL keywords from `content_basic_w_ranges`:

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

1. **If ALL keywords are within range:** Proceed to Phase 7.
2. **If issues exist:** Fix them using targeted `Edit` calls on the file:
   - Fix the MOST over-limit keyword first (the one furthest above its upper bound)
   - Fixing one keyword often fixes others due to substring overlap
   - For STUFFED keywords: replace excess occurrences with synonyms, pronouns, or rephrase
   - For MISSING keywords: insert naturally into existing sentences
   - After edits, re-run the Python compliance check
3. **Repeat up to 3 total passes.** If issues remain after 3 passes, show the remaining issues and ask the user for guidance.
4. Also verify the word count is within +/-10% of the target on each pass.

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

## Phase 7: Upload and Cleanup

### Step 7.1 -- Upload to NeuronWriter

Run the upload script:

```
python upload_to_neuronwriter.py
```

This auto-detects the requirements file, reads `{keyword}-optimized.md`, converts to HTML, and uploads. Report the content score returned by NeuronWriter.

### Step 7.2 -- Archive Intermediate Files

Create a `processed/` subfolder (if it doesn't exist) and move intermediate files there:

```bash
mkdir -p processed
mv {keyword}-content.md {keyword}-requirements.json {keyword}-serp.json {keyword}-paa.json processed/
```

Keep `{keyword}-optimized.md` in the working directory for reference.

### Step 7.3 -- Update Created URLs Tracker

Maintain a CSV file called `created_urls.csv` in the **root folder** of the working directory. This is a running log of all created pages, separate from `optimized_urls.csv` (which tracks optimizations of existing pages).

**Columns (all capitalized):**

```
QUERY ID,KEYWORD,WEBSITE URL,NEURONWRITER SHARE URL,NEURONWRITER READ URL,DATE,CONTENT SCORE,WORD COUNT,TARGET WORD COUNT,TEMPLATE URL
```

**Where to get each value:**
- **QUERY ID** -- The NeuronWriter query ID provided by the user
- **KEYWORD** -- From `{keyword}-requirements.json` -> `keyword`
- **WEBSITE URL** -- The page URL inferred from `internal_urls.csv` (same one used in the SEO metadata block)
- **NEURONWRITER SHARE URL** -- From `{keyword}-requirements.json` -> `share_url`
- **NEURONWRITER READ URL** -- From `{keyword}-requirements.json` -> `readonly_url`
- **DATE** -- Today's date in `YYYY-MM-DD` format
- **CONTENT SCORE** -- The score returned by the upload script (from the NeuronWriter API response)
- **WORD COUNT** -- Word count of the created `{keyword}-optimized.md`
- **TARGET WORD COUNT** -- The target word count approved in Phase 2
- **TEMPLATE URL** -- The template page URL selected in Phase 3

**Rules:**
- If `created_urls.csv` does **not** exist, create it with the header row and then append the data row.
- If `created_urls.csv` **already exists**, read it first, then append a new row. Do NOT overwrite existing rows.
- If the same QUERY ID already has a row, **update that row** in place (replace with new values) rather than adding a duplicate.
- Use Python via Bash to handle the CSV read/append/update to avoid formatting issues.

Example Python snippet:

```python
import csv
import os
from datetime import date

csv_file = 'created_urls.csv'
headers = ['QUERY ID', 'KEYWORD', 'WEBSITE URL', 'NEURONWRITER SHARE URL',
           'NEURONWRITER READ URL', 'DATE', 'CONTENT SCORE', 'WORD COUNT',
           'TARGET WORD COUNT', 'TEMPLATE URL']

new_row = {
    'QUERY ID': '{query_id}',
    'KEYWORD': '{keyword}',
    'WEBSITE URL': '{website_url}',
    'NEURONWRITER SHARE URL': '{share_url}',
    'NEURONWRITER READ URL': '{readonly_url}',
    'DATE': str(date.today()),
    'CONTENT SCORE': '{content_score}',
    'WORD COUNT': '{word_count}',
    'TARGET WORD COUNT': '{target_word_count}',
    'TEMPLATE URL': '{template_url}',
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

### Step 7.4 -- Report Results

Print a summary:
- NeuronWriter content score
- Word count (created vs. target)
- Keyword compliance status (all within range / X issues remaining)
- Extended keyword coverage (X/Y, Z%)
- Number of internal links inserted
- FAQ questions used (count and source: PAA vs. custom)
- Template page used

---

## Important Reminders

1. **Content Brain is the #1 authority.** All voice, positioning, and terminology rules from `Content brain/contentbrain.md` override everything else, including NeuronWriter keyword suggestions.
2. **This is CREATION, not optimization.** You are writing from scratch. There is no "original content" to preserve. But you ARE following a template page's STRUCTURE.
3. **Never compromise readability for keyword density.** Natural language always wins. If a keyword cannot be inserted without awkwardness, skip it.
4. **Word count discipline.** Stay within +/-10% of the approved target. Do not inflate content with filler.
5. **Substring awareness is critical.** Every compound keyword also increments all its parent keyword counts. Track this as you write.
6. **Python verification is mandatory.** Never rely on internal counting. Always run the Python script to verify compliance.
7. **Proper nouns are always capitalized** regardless of how they appear in the requirements data.
8. **User interaction points.** This skill has TWO mandatory user interaction points: word count approval (Phase 2, Step 2.3) and template selection (Phase 3, Step 3.1). Do NOT skip these.
9. **Never use em-dashes or en-dashes** in the content. Replace with commas, colons, or rephrase.
10. **Never use foreign words**, even if they appear in NeuronWriter keyword requirements. Skip any non-English term.
11. **No ChatGPT slop.** No filler phrases, no empty superlatives, no generic conclusions. Every sentence must carry information.
