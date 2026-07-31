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
7. **`Content brain/ai-buzzwords.md`** -- AI buzzword avoidance guide (words and phrases to never use)

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
- `h2_terms` -- Heading keyword recommendations with `usage_pc` (used for both H2 and H3 optimization)
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
- Whether it shares whole words with other keywords (word-level overlap awareness)

Also parse `content_extended_w_ranges` for extended keyword targets.

### Step 4.5 -- Read AI Buzzwords Avoidance List

Read `Content brain/ai-buzzwords.md` in full. Internalize ALL categories of words and phrases to avoid:
- **Universal top offenders** (delve, showcasing, aligns, notably, etc.)
- **Transition words** (moreover, furthermore, consequently, hence, etc.)
- **Buzzword adjectives** (crucial, pivotal, transformative, robust, seamless, etc.)
- **AI-tell verbs** (delve, leverage, utilize, facilitate, foster, navigate, etc.)
- **Filler phrases and openers** ("In today's fast-paced...", "It's important to note...", etc.)
- **Abstract nouns** (landscape, tapestry, journey, realm, paradigm, etc.)
- **Industry-specific AI clusters** (hollow innovation, vague efficiency, corporate solutions language)
- **Structural red flags** ("It's not about X, it's about Y", uniform sentence length, etc.)

**These words and phrases are BANNED from the content you write.** If you catch yourself reaching for any of them, replace with specific, concrete language relevant to the actual service being described.

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

**CRITICAL -- Word-Level Overlap Awareness:** Keywords are counted using whole-word boundary matching, not substring matching. This means "suv" does NOT count as "uv", and "glossy" does NOT count as "gloss". However, multi-word phrases still overlap at the word level. For example:
- The text "digital marketing agency" increments counts for "digital marketing" (consecutive whole words), "marketing" (whole word), AND "agency" (whole word)
- "consulting services" increments both "consulting" and "services" (each word is whole)
- But "suv" does NOT increment "uv" (not a whole-word match)
- And "glossier" does NOT increment "gloss" (not a whole-word match)

When adding a compound keyword, mentally increment ALL single-word and overlapping multi-word keywords that share whole words, and check they remain in range.

Rules:
- **Stay within the upper bound of each range, with a small overflow tolerance.** The allowed overflow depends on the keyword's upper bound:
  - **Max <= 5x:** 1 extra instance allowed (e.g., a keyword with range 1-3x is acceptable at 4x)
  - **Max 6-10x:** 2 extra instances allowed (e.g., a keyword with range 2-7x is acceptable at 9x)
  - **Max > 10x:** 3 extra instances allowed (e.g., a keyword with range 10-27x is acceptable at 30x)
  - Aim for within-range first. The overflow tolerance exists for cases where structural content (product names, navigation, pricing tables) makes exact compliance impossible.
- Target the middle of each range for a natural distribution.
- **Track compound keywords carefully.** Every time you write a multi-word keyword, also count it against all overlapping whole-word keywords.

### Rule 3: Content Extended Keywords

Review `content_extended_w_ranges`. Add a majority of these extended keywords where they fit naturally. Skip any that would feel forced or off-topic.

**Extended keyword coverage targets (based on target word count from Phase 2):**
- **Pages with 1,000+ words:** Target **75%** or more of extended keywords present.
- **Pages under 1,000 words:** Target **65%** or more of extended keywords present.

**Budget check:** After mentally placing extended keywords, verify that basic keyword ranges are still respected. Extended keywords often share whole words with basic keywords (e.g., "best ceramic coating" contains the whole word "coating").

### Rule 4: Proper Noun Capitalization

The requirements file lists all keywords in lowercase. Always capitalize proper nouns correctly:
- Country names: "India," "Mexico," "China," "United States"
- City/region names: "Gujarat," "Coimbatore," "Seattle"
- Company names as specified in Content Brain

### Rule 5: Word Count Compliance

Stay within +/-5% of the target word count approved in Phase 2.

### Rule 6: Heading Optimization (H1, H2, and H3)

**H1:** Include the primary keyword. Use Title Case. Check `h1_terms` for high-usage keywords (usage_pc >= 40).

**H2 and H3 subheadings:** NeuronWriter provides a single `h2_terms` list of heading keywords, each with a `usage_pc` value (percentage of top-ranking competitors using that keyword in their headings). NeuronWriter scores keywords higher when they appear in H2s and lower when in H3s. Place the most important keywords in H2 headings and medium-importance ones in H3 headings.

**Sort the `h2_terms` list by `usage_pc` descending, then apply these tiers:**

| Tier | `usage_pc` | Place in | Action |
|------|-----------|----------|--------|
| Top tier | >= 40 | **H2** | MUST appear in an H2. Adapt the most relevant heading from the template structure to incorporate this keyword. |
| Mid tier | 20-39 | **H3** | Should appear in an H3. Create H3 subsections under the most relevant H2, or adapt existing H3s from the template. |
| Low tier | < 20 | Either | Only incorporate if it fits naturally into an existing heading. Do not force these. |

**How to build headings:**
- **Combine multiple keywords into one heading when they naturally fit together.** Look for keywords that overlap or complement each other and can form a single coherent heading. For example, if `h2_terms` includes both "sand casting" and "sand casting process," the H2 "Our Sand Casting Process" covers both. Similarly, "investment casting" + "investment casting tolerances" can become "Investment Casting Tolerances and Capabilities." Only combine when the result reads naturally -- never force unrelated keywords into the same heading.
- **Adapt from the template, don't copy.** Use the template's heading hierarchy as a structural blueprint, but rewrite each heading to incorporate the target keyword's `h2_terms`. The template tells you WHAT sections to have; `h2_terms` tells you HOW to phrase them.
- **Match the keyword to the right section.** Only place a keyword in a heading whose section content actually covers that topic. Never put a keyword in an unrelated heading just to score points.
- **Use Title Case for all headings.**
- Where natural, structure H2s as semantic relationships: "How [Brand] Delivers [Service] for [Audience]" rather than vague labels like "Our Services" or "What We Offer."

**Constraints (these always apply):**
- **Content Brain overrides heading keywords.** If a heading keyword conflicts with Content Brain terminology rules (e.g., a forbidden term), do NOT use it.
- **Keyword overlap awareness applies to headings.** Keywords in headings count toward `content_basic_w_ranges` totals. When adding a keyword to a heading, check that it doesn't push any basic keyword over its hard max.
- **Never put internal links in headings** (Rule 7 still applies).

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
- Lead with the brand/company entity name, not with action verbs, pronouns, or generic phrases

**Note:** Keywords in the SEO metadata block (everything above the H1) are NOT counted toward keyword compliance ranges. The compliance scripts automatically exclude this block, so you can freely use keywords in titles and meta descriptions without inflating counts.

### Rule 10: No Bold Formatting on Keywords

Never bold keywords in the body text. Write them as normal text. 

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
- **Full buzzword avoidance list:** Refer to `Content brain/ai-buzzwords.md` (read in Step 4.5). Any word or phrase listed there is banned from the content.

### Rule 15: Semantic Triple Structure in Key Positions

Structure key sentences as semantic triples: [Entity] + [relationship verb] + [value/object]. This helps AI models and knowledge graphs parse your content as structured facts rather than keyword soup.

Apply in these specific positions — do not force triples into every sentence:

1. **First sentence of each H2 section:** Open with the company/brand name or the service as the subject, followed by an action verb and a specific value. Example: "Redstone Manufacturing produces investment castings at tolerances of ±0.005 inches." NOT: "We are proud to offer high-quality casting services."
2. **H1 and H2 headings (where natural):** Where it doesn't conflict with Rule 6, prefer headings that express a relationship: "How [Company] Reduces [Problem] for [Audience]" over vague noun phrases like "Our Approach to Solutions."
3. **Meta descriptions (Rule 9):** Lead with the brand entity, not action verbs or pronouns.
4. **FAQ answers:** Start each answer with the subject entity (the thing being asked about), not "Yes," "No," or "It depends."
5. **Opening paragraph (under H1):** The very first sentence of the page should be a complete semantic triple containing brand + core service + location or audience qualifier.

**Do NOT:**
- Force every sentence into triple structure — vary sentence patterns per Rule 14 (Human-Like Writing)
- Sacrifice keyword compliance for triple structure — keyword ranges are the higher priority
- Use triples as an excuse to repeat the brand name excessively — follow NeuronWriter keyword limits

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

# Exclude SEO metadata block above H1 from counting
if '\n# ' in text:
    text = text[text.index('\n# '):]

# Strip markdown link URLs — only count anchor text, not URLs
# [anchor](url) -> anchor
text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)

def count_kw(kw, text):
    """Count whole-word matches of a keyword (single or multi-word).
    Uses word boundaries so 'uv' won't match inside 'suv'
    and 'gloss' won't match inside 'glossy'."""
    words = kw.split()
    pattern = r'\b' + r'\s+'.join(re.escape(w) for w in words) + r'\b'
    return len(re.findall(pattern, text))

def overflow_tolerance(hi):
    """Allowed instances above upper bound based on max limit."""
    if hi <= 5:
        return 1
    elif hi <= 10:
        return 2
    else:
        return 3

words = len(text.split())
print(f'Total word count: {words}')
print()

keywords = {
    # Populate ALL keywords from content_basic_w_ranges
    # 'keyword': (lower_bound, upper_bound),
}

print(f'{"Keyword":<35} {"Count":>5} {"Range":>10} {"Hard Max":>9} {"Status":>10}')
print('-' * 75)

issues = []
for kw, (lo, hi) in sorted(keywords.items(), key=lambda x: x[1][1]):
    count = count_kw(kw, text)
    tolerance = overflow_tolerance(hi)
    hard_max = hi + tolerance
    if count > hard_max:
        status = 'STUFFED'
        issues.append((kw, count, lo, hi, hard_max))
    elif count > hi:
        status = 'OVER-OK'
    elif count < lo:
        status = 'MISSING'
        issues.append((kw, count, lo, hi, hard_max))
    else:
        status = 'OK'
    print(f'{kw:<35} {count:>5} {lo}-{hi:>3}x {hard_max:>7}x {status:>10}')

if issues:
    print(f'\n=== {len(issues)} ISSUES FOUND ===')
    for kw, count, lo, hi, hard_max in issues:
        print(f'  {kw}: {count}x (target {lo}-{hi}x, hard max {hard_max}x)')
else:
    print('\nAll keywords within range!')
```

### Compliance Loop Rules

1. **If ALL keywords are within range or within overflow tolerance (OVER-OK):** Proceed to Phase 7. Keywords marked OVER-OK are above the ideal range but within the allowed overflow tolerance and do not need fixing.
2. **If STUFFED or MISSING issues exist:** Fix them using targeted `Edit` calls on the file:
   - Fix the MOST over-limit keyword first (the one furthest above its hard max)
   - Fixing one keyword often fixes others due to word-level overlap
   - For STUFFED keywords: replace excess occurrences with synonyms, pronouns, or rephrase
   - For MISSING keywords: insert naturally into existing sentences
   - After edits, re-run the Python compliance check
3. **Repeat up to 3 total passes.** If issues remain after 3 passes, show the remaining issues and ask the user for guidance.
4. Also verify the word count is within +/-5% of the target on each pass.

Also check extended keyword coverage on the final pass:

```python
# Add this to the compliance script (count_kw function must be defined above)
extended = [
    # List all extended keywords from content_extended_w_ranges
]
present = sum(1 for kw in extended if count_kw(kw, text))
print(f'\nExtended keywords: {present}/{len(extended)} ({round(present/len(extended)*100)}%)')
```

Target: **75%+** for pages with 1,000+ words, **65%+** for pages under 1,000 words (based on the target word count from Phase 2).

---

## Phase 6.5: AI Buzzword Compliance Check

**This phase is mandatory. Run it after keyword compliance passes and before upload.**

Scan the content in `{keyword}-optimized.md` against the buzzword categories from `Content brain/ai-buzzwords.md`. Run this Python script via Bash:

```python
import re

with open('{keyword}-optimized.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Buzzword lists from ai-buzzwords.md
ai_words = [
    'delve', 'leverage', 'utilize', 'facilitate', 'foster', 'harness',
    'navigate', 'underscore', 'endeavor', 'augment', 'elevate', 'empower',
    'propel', 'catalyze', 'galvanize', 'streamline', 'unleash', 'turbocharge',
    'robust', 'seamless', 'cutting-edge', 'state-of-the-art', 'pivotal',
    'transformative', 'groundbreaking', 'revolutionary', 'unprecedented',
    'profound', 'invaluable', 'paramount', 'stellar', 'comprehensive',
    'innovative', 'tapestry', 'paradigm', 'synergy', 'ecosystem',
    'cornerstone', 'catalyst', 'arsenal', 'methodology', 'showcasing',
]

ai_phrases = [
    "in today's fast-paced",
    'in the ever-evolving',
    "it's important to note",
    "it's worth mentioning",
    'in the realm of',
    "let's dive into",
    "let's explore",
    'unlock the power of',
    'in an ever-evolving landscape',
    'as we navigate',
    'plays a vital role',
    'plays a crucial role',
    'plays a significant role',
    'serves as a testament',
    'as we delve deeper',
    'welcome to the world of',
    'in conclusion',
    'in summary',
    'a wide range of',
    'designed to meet your needs',
    'when it comes to',
    'this allows for',
    'in the digital age',
    "it's not about",
    'moreover',
    'furthermore',
    'consequently',
    'hence',
    'notably',
    'nevertheless',
    'nonetheless',
    'notwithstanding',
    'revolutionize',
    'redefining what',
    'a new era of',
    'drive operational excellence',
    'digital transformation journey',
    'mission-critical',
    'next-generation',
    'game-changer',
    'unprecedented precision',
]

text_lower = text.lower()
found = []

for word in ai_words:
    matches = re.findall(r'\b' + re.escape(word) + r'\b', text_lower)
    if matches:
        found.append((word, len(matches), 'WORD'))

for phrase in ai_phrases:
    matches = re.findall(re.escape(phrase), text_lower)
    if matches:
        found.append((phrase, len(matches), 'PHRASE'))

if found:
    print(f'=== {len(found)} AI BUZZWORD VIOLATIONS FOUND ===')
    print(f'{"Type":<8} {"Count":>5}  Term')
    print('-' * 60)
    for term, count, typ in sorted(found, key=lambda x: -x[1]):
        print(f'{typ:<8} {count:>5}  {term}')
else:
    print('No AI buzzword violations found!')
```

### Buzzword Compliance Rules

1. **If no violations found:** Proceed to Phase 7 (Upload).
2. **If violations found:** Fix them using targeted `Edit` calls:
   - Replace each flagged word/phrase with specific, concrete language
   - Do NOT replace with another word from the buzzword list
   - After edits, re-run the buzzword scan AND the keyword compliance check (fixes must not break keyword ranges)
3. **Repeat up to 2 passes.** If violations remain after 2 passes, show them to the user.

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
4. **Word count discipline.** Stay within +/-5% of the approved target. Do not inflate content with filler.
5. **Word-level overlap awareness is critical.** Keywords are matched as whole words (using `\b` word boundaries), so "suv" does not count as "uv" and "glossy" does not count as "gloss". However, multi-word phrases still overlap at the word level: "ceramic coating services" increments both "ceramic coating" and "coating". Track these whole-word overlaps as you write.
6. **Python verification is mandatory.** Never rely on internal counting. Always run the Python script to verify compliance.
7. **Proper nouns are always capitalized** regardless of how they appear in the requirements data.
8. **User interaction points.** This skill has TWO mandatory user interaction points: word count approval (Phase 2, Step 2.3) and template selection (Phase 3, Step 3.1). Do NOT skip these.
9. **Never use em-dashes or en-dashes** in the content. Replace with commas, colons, or rephrase.
10. **Never use foreign words**, even if they appear in NeuronWriter keyword requirements. Skip any non-English term.
11. **No ChatGPT slop.** No filler phrases, no empty superlatives, no generic conclusions. Every sentence must carry information.
12. **Semantic triples are a writing technique, not a compliance metric.** Use Entity + Relationship + Value structure in section openers, the opening paragraph, meta descriptions, and FAQ answers. This improves AI parseability but never overrides keyword compliance, word count, or Content Brain rules.
13. **AI buzzwords are banned.** Every word, phrase, and structural pattern listed in `Content brain/ai-buzzwords.md` must be avoided. The buzzword compliance check in Phase 6.5 catches violations, but aim to avoid them during writing.
