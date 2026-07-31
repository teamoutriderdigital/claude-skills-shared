---
name: redstone-draft-blog-post
description: End-to-end Redstone Manufacturing blog post drafting pipeline. Fetches NeuronWriter requirements and SERP/PAA data, uses a pre-generated research report, creates a content brief, selects hub-and-spoke internal links, writes a full SEO-optimized blog post in Redstone's B2B manufacturing voice per Content Brain, runs keyword and terminology compliance, and optionally uploads to NeuronWriter. Use this skill whenever the user wants to draft a Redstone blog post, write a blog from research for a keyword, create a Redstone article, or generate a blog post from a NeuronWriter query. Also triggers for "draft Redstone blog post", "write blog for [keyword]", "create Redstone article for [keyword]", or "generate blog post from NeuronWriter query".
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebFetch, AskUserQuestion, TaskCreate, TaskUpdate
---

# Redstone Manufacturing Blog Post Drafting

End-to-end pipeline: NeuronWriter query ID + research report -> content brief -> hub-and-spoke internal links + PAA -> full blog post -> keyword & terminology compliance -> optional NeuronWriter upload -> CSV tracking.

## Prerequisites

Before running, verify ALL of the following exist in the working directory. If any are missing, stop and tell the user what is needed.

| File | Description |
|---|---|
| `fetch_neuronwriter.py` | Script to pull content and requirements from NeuronWriter |
| `fetch_serp_titles.py` | Script to pull SERP titles and PAA questions from DataForSEO |
| `upload_to_neuronwriter.py` | Script to upload optimized content back to NeuronWriter |
| `config.json` | Must contain `apiKey` for NeuronWriter API |
| `Content brain/contentbrain.md` | Client voice, positioning, and terminology guide |
| `internal_urls.csv` | List of internal site URLs for hub-and-spoke linking |
| `Content brain/ai-buzzwords.md` | AI buzzword avoidance guide (words and phrases to never use) |
| `research-report-*.md` | Research report from `/research-for-blog-post` skill |

Use `Glob` to verify these files exist. If no `research-report-*.md` file is found, stop and tell the user to run `/research-for-blog-post` first.

**Input:** The user provides a **NeuronWriter query ID** (e.g., `9688462b954b84b3`). This is the only required input.

---

## Phase 1: Data Collection

### Step 1.1 -- Fetch from NeuronWriter

Run the fetch script with the provided query ID:

```
echo "{QUERY_ID}" | python fetch_neuronwriter.py
```

This produces two files:
- `{keyword}-content.md` -- Current page content in Markdown (may be empty for a new blog post, that is expected)
- `{keyword}-requirements.json` -- NeuronWriter optimization requirements

### Step 1.2 -- Fetch SERP and PAA

Run the SERP titles script (auto-detects the requirements file):

```
python fetch_serp_titles.py
```

This produces two more files:
- `{keyword}-serp.json` -- Organic SERP results
- `{keyword}-paa.json` -- People Also Ask questions from Google

Wait for both scripts to complete before proceeding. The SERP script takes ~30 seconds due to API polling.

### Step 1.3 -- Read Research Report

Glob for `research-report-*.md` in the working directory. If multiple matches exist, ask the user which one corresponds to this blog topic. Read the selected file in full. Extract and store:
- Section A: Executive Summary
- Section B: Detailed Factual Extraction (primary data source for the brief)
- Section C: Consolidated Key Statistics (numbers, percentages, financial figures)
- Section D: External Links with sentences (potential authoritative source links)
- Comparison tables if present

---

## Phase 2: Pre-Analysis & Word Count

### Step 2.1 -- Read Content Brain

Read `Content brain/contentbrain.md` in full. This is the #1 authority on voice and positioning. For blog posts specifically, internalize:
- **Voice:** Third-person for objectivity, first-person plural for Redstone-specific claims
- **Tone hierarchy:** Engineer-to-engineer > spec-first > under-promised > direct > proof-led
- **Active voice:** 65-75% target
- **All forbidden terms** (Section 4 and Section 7)
- **Hub-and-spoke model** (Section 5): blogs are spokes that must link to parent hub service page
- **FAQ:** 3-5 pairs for blog posts
- **Internal links:** Minimum 2 per page, descriptive anchor text

**If Content Brain rules conflict with any NeuronWriter keyword target, Content Brain wins.**

### Step 2.2 -- Read Requirements JSON

From `{keyword}-requirements.json`, extract:
- `content_basic_w_ranges` -- Primary keywords with usage ranges (HARD LIMITS)
- `content_extended_w_ranges` -- Extended/LSI keywords to add naturally
- `h1_terms` and `h2_terms` -- Heading keyword recommendations with `usage_pc`
- `competitors` -- Top-ranking pages for context (headings, structure, word counts)
- `people_also_ask` -- NeuronWriter PAA (backup if DataForSEO PAA is empty)
- `serp_summary` -- Search intent data

### Step 2.3 -- Read PAA and Internal URLs

- Read `{keyword}-paa.json` for FAQ questions (prefer these over NeuronWriter PAA if available)
- Read `internal_urls.csv` for internal linking targets

### Step 2.4 -- Calculate Target Word Count

From `{keyword}-requirements.json`, read the `competitors` array. Take top 5 by rank. Filter: only include competitors with `word_count` between 500 and 5000. Calculate the average, round to nearest 50. Apply a minimum floor of 1200 words (blogs need depth to rank for informational intent).

Run this calculation via Python in Bash:

```python
import json

with open('{keyword}-requirements.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

competitors = data.get('competitors', [])
competitors_sorted = sorted(competitors, key=lambda c: int(c.get('rank', 999)))[:5]

print("Top 5 Competitors:")
print(f"{'Rank':<6} {'Word Count':>10} {'Qualifies':>10}  URL")
print("-" * 80)

qualifying = []
for c in competitors_sorted:
    wc = int(c.get('word_count', 0))
    qualifies = 500 <= wc <= 5000
    if qualifies:
        qualifying.append(wc)
    print(f"{c.get('rank', '?'):<6} {wc:>10} {'YES' if qualifies else 'NO':>10}  {c.get('url', 'N/A')[:60]}")

if qualifying:
    raw_avg = sum(qualifying) / len(qualifying)
    target = max(1200, round(raw_avg / 50) * 50)
    print(f"\nQualifying pages: {len(qualifying)}/{len(competitors_sorted)}")
    print(f"Average word count: {raw_avg:.0f}")
    print(f"Rounded target (floor 1200): {target} words")
else:
    print("\nNo qualifying pages found. Defaulting to 1500 words.")
    target = 1500
```

**STOP and ask the user for approval.** Present the competitor word counts and calculated target. Ask: "The calculated target word count is **{target} words**. Should I proceed with this target, or would you like to adjust it?" Wait for response.

### Step 2.5 -- Auto-Detect Hub Service Page

Analyze the blog keyword and map it to a parent hub service page from `internal_urls.csv`. Logic:
1. Extract the core service topic from the keyword (e.g., "die casting defects" -> "die casting", "CNC machining tolerances" -> "CNC machining", "investment casting vs die casting" -> both)
2. Match against `/services/` URLs in `internal_urls.csv`
3. If the topic also relates to a country (e.g., "die casting in Mexico"), also identify the country-specific service page
4. Present the detected hub(s) to the user for confirmation

If no hub can be auto-detected, ask the user to specify which service page(s) this blog supports.

### Step 2.6 -- Terminology Pre-Check

Scan NeuronWriter `content_basic_w_ranges` and `content_extended_w_ranges` for any keywords that violate Content Brain forbidden terms. Build a skip-list of keywords that must NOT be used regardless of NeuronWriter targets:

- Any keyword containing "source" or "sourcing"
- Any keyword containing "global"
- Any keyword containing "factory" or "factories"
- Any keyword containing "precision engineering"
- Any keyword containing "contract manufactur"
- Any keyword containing "outsourc"
- Any keyword containing "broker" or "middleman"

Inform the user which NeuronWriter keywords are being skipped and why. Adjust keyword compliance targets accordingly (these keywords are excluded from the compliance check in Phase 6).

### Step 2.7 -- Competitor Content Gap Analysis

Briefly analyze competitor headings from `{keyword}-requirements.json` (the `competitors[].headers` field) and SERP titles from `{keyword}-serp.json`:
- Common topics covered by all top 5 competitors (must include these)
- Topics covered by only 1-2 competitors (differentiation opportunities)
- Topics NO competitor covers (unique angle opportunities)

Present a 10-line summary to the user for context before brief creation. This informs the brief but does not block the workflow.

### Step 2.8 -- Parse Keyword Ranges

Parse ALL keywords from `content_basic_w_ranges` into a structured reference. For each keyword, note:
- The keyword string
- Lower bound (minimum occurrences)
- Upper bound (maximum occurrences)
- Whether it is a substring of other keywords (substring awareness)

Also parse `content_extended_w_ranges` for extended keyword targets.

### Step 2.9 -- Read AI Buzzwords Avoidance List

Read `Content brain/ai-buzzwords.md` in full. Internalize ALL categories of words and phrases to avoid:
- **Universal top offenders** (delve, showcasing, aligns, notably, etc.)
- **Transition words** (moreover, furthermore, consequently, hence, etc.)
- **Buzzword adjectives** (crucial, pivotal, transformative, robust, seamless, etc.)
- **AI-tell verbs** (delve, leverage, utilize, facilitate, foster, navigate, etc.)
- **Filler phrases and openers** ("In today's fast-paced...", "It's important to note...", etc.)
- **Abstract nouns** (landscape, tapestry, journey, realm, paradigm, etc.)
- **Industry-specific AI clusters** (hollow innovation, vague efficiency, corporate solutions language)
- **Structural red flags** ("It's not about X, it's about Y", uniform sentence length, etc.)

**These words and phrases are BANNED from the content you write.** If you catch yourself reaching for any of them, replace with specific, concrete language relevant to the actual manufacturing process, material, or service being described.

---

## Phase 3: Content Brief Creation

Generate a structured content brief using the research report and NeuronWriter data.

**System message:** You are an expert B2B manufacturing content strategist creating a content brief for a blog post on the Redstone Manufacturing website. The audience is U.S. and Canadian engineers and procurement managers evaluating manufacturing services, materials, or processes.

**Brief creation instructions:**

1. Use info, data, facts, and stats from the research report sections B, C, and D to populate the brief. Make it fact-rich but concise.
2. Structure the brief with H1, H2, and H3 headings. The total number of subheadings should align with competitor heading counts from the requirements JSON.
3. Use majority of keywords from `h2_terms` (where `usage_pc` >= 40) in subheadings. Write subheadings in Title Case. Use question format where appropriate per Content Brain rules ("Is Die Casting Right For Your Product?", "How Does CNC Machining Compare to...?").
4. Under each subheading, insert 2-6 SHORT bullet points with data. Use tables for spec comparisons, material properties, tolerance ranges, or process comparisons per Content Brain formatting rules.
5. Use figures and facts ONLY from the research report. Link to authoritative sources (.edu, .gov, .org, well-known engineering publications like Thomas Net, Modern Machine Shop, The Fabricator, SAE International, ASM International). Avoid linking to non-U.S. sources. Do NOT mention sources in the form [Article X].
6. Create but do NOT fill: `## FAQ: [Topic Name]`
7. Include a bullet point noting where the hub service page link should appear (from Step 2.5).
8. Include a bullet point noting where the Redstone CTA section should go. The CTA connects the blog topic to Redstone's services naturally, not as a hard sell.
9. If the topic relates to a non-China country (detected in Step 2.5), include a section for vs-China comparison angle.
10. If the topic relates to supply chain decisions or geographic manufacturing, include a note about tariff angle with date disclaimer requirement.
11. Always output in markdown.

---

## Phase 4: Internal Link Selection (Hub-and-Spoke)

Read `internal_urls.csv` and select internal links following the Content Brain blog linking pattern.

**Mandatory links:**
1. **Parent hub service page** (identified in Step 2.5). This is non-negotiable for hub-and-spoke.
2. At least 1 related blog post or comparison article from `internal_urls.csv`

**Additional links (select 3-5 more, for a total of 5-7):**
- Related service pages (e.g., if the blog is about die casting defects, link to aluminum die casting, zinc die casting)
- Relevant material/alloy pages (e.g., A380 aluminum, 6061 aluminum)
- Relevant comparison articles
- Country-specific service pages if the topic has a geographic angle

**Link rules (from Content Brain):**
- Links go in body text paragraphs only, never in headings
- Descriptive anchor text (not "click here" or "learn more")
- ~60% keyword-rich anchors, ~40% natural/generic
- Distribute throughout the article, not clustered in one section
- All real URLs from `internal_urls.csv`. No placeholder anchors.

---

## Phase 5: Full Article Writing

Read `Content brain/contentbrain.md` before writing. Use the content brief, internal links, PAA questions, and keyword data to write the article.

**System message:** You are an expert SEO copywriter specializing in B2B manufacturing content. You write for a dual audience of engineers and procurement managers. Your tone is engineer-to-engineer, spec-first, and proof-led. You are writing a blog post for Redstone Manufacturing's website.

### Rule 1: Voice and Person (Blog-Specific)

Use third-person for objectivity in educational/informational content ("Manufacturers typically achieve..." / "The sintering process removes..."). Switch to first-person plural when making Redstone-specific claims ("At Redstone, we provide..." / "Our Seattle facility operates..."). Never use second-person in a chatbot or infomercial way ("Are YOU tired of bad castings?!").

### Rule 2: Tone Hierarchy (Ranked, from Content Brain)

1. **Engineer-to-engineer.** No consumer or marketing register.
2. **Spec-first.** Numbers before adjectives. Tolerance, volume, lead time, cert ID. Always pick a number over a claim.
3. **Cautiously under-promised.** Say 20%, not 30%. Say "consistently short," not "industry-leading."
4. **Direct, plainspoken.** Short sentences. One idea per line. No jargon stacking.
5. **Proof-led.** Lead with certifications, tenure, and named capabilities. Proof before claim, not after.

### Rule 3: Article Structure

- **H1:** Include primary keyword, Title Case
- **Introduction:** Write 2 versions (one below another), 60-80 words each. Open with a specific number, stat, or fact that hooks the reader. Break into 2 paragraphs each. Third-person opening, transitioning to what the article covers.
- **Key Takeaways:** Immediately after the introduction, include a section titled "Key Takeaways". List 4-6 ULTRA SHORT bullet points. One short sentence per line. No links or bolds. Each bullet is a standalone fact an AI could extract: [Subject] [verb] [specific claim].
- **Body:** Develop the main content from the brief. Use tables for spec comparisons. Use bullet points for capabilities, process steps, and scannable information. Incorporate NLP keywords naturally.
- **Redstone CTA Section:** One H2 section (naturally integrated, not a separate sales pitch) that connects the blog topic to Redstone's services. Link to the hub service page. Use CTA language from Content Brain: "Request Quote" or "Start My Project." Do NOT make this a hard sell. It should read as "if you need this capability, here is how Redstone handles it."
- **FAQ Section:** Title: "Frequently Asked Questions About [Topic]" in Title Case. Use 3-5 pairs from PAA questions (Step 2.3). Bold each question, line break, then write 2-3 sentence answer. Start each answer with the subject entity (not "Yes," "No," or filler). Skip off-topic PAA questions.

### Rule 4: Formatting Rules (from Content Brain)

- Title Case all headings (H1, H2, H3)
- Oxford comma always
- No em dashes anywhere (use comma or period)
- Bold for key service terms, material names, process names on first mention only. Use sparingly in body paragraphs.
- Tables for spec comparisons, material properties, capability matrices, process comparisons
- Short paragraphs (2-4 sentences)
- Numbers as numerals for metrics: 99%, 5-axis, 0.005", ±0.0005"
- Introduce acronyms with full form + acronym in parentheses on first mention: "Metal Injection Molding (MIM)"

### Rule 5: Keyword Integration -- STRICT Range Enforcement

Treat `content_basic_w_ranges` ranges as hard limits.

**CRITICAL -- Substring Awareness:** Keywords share substrings. For example:
- "aluminum die casting" increments counts for "die casting", "aluminum", AND "casting"
- "CNC machining services" contains both "CNC machining" and "machining"

When adding a compound keyword, mentally increment ALL parent substring keywords and check they remain in range.

Rules:
- **NEVER exceed the upper bound of any range.** This is a hard constraint.
- Target the middle of each range for a natural distribution.
- Track compound keywords carefully.
- Skip keywords on the terminology skip-list (from Step 2.6).
- Target 80%+ of `content_extended_w_ranges` keywords present.
- Never bold keywords in body text.
- Capitalize proper nouns correctly regardless of how NeuronWriter lists them.

### Rule 6: Internal Links

Insert the 5-7 internal links selected in Phase 4.

- Links go in body text paragraphs only. **Never in headings.**
- The parent hub service page link is mandatory and should appear in the first third of the article if possible.
- Descriptive anchor text, 1-4 words. ~60% keyword-rich, ~40% natural.
- Distribute naturally throughout, not clustered.

### Rule 7: Facts and Source Links

Use authoritative source links from the research report and content brief. Keep anchor text 1-4 words, descriptive. Link naturally within sentences. Avoid non-U.S. sources. No naked URLs.

### Rule 8: Terminology Compliance (from Content Brain)

Never use any term from the Content Brain "Never Use" list. This includes but is not limited to:
- "Source," "sourcing," "sourced" in any form
- "Global" in any form
- "Factory," "factories"
- "Precision engineering"
- "Contract manufacturing"
- "Outsource," "outsourcing"
- "Broker," "middleman"
- Superlatives: "world-class," "best-in-class," "premier," "industry-leading," "premium"
- "Made in USA," "domestic foundry"
- "Build it" as a CTA
- Em dashes and en dashes

Use the "Always Use" replacements from Content Brain Section 4.

Never use ChatGPT slop phrases:
- "In today's fast-paced world..."
- "It's important to note that..."
- "In conclusion..."
- "When it comes to..."
- "In the ever-evolving landscape of..."
- "Let's dive in..."
- "At the end of the day..."
- "[Topic] is a game-changer..."
- "Navigating the complexities of..."
- Any sentence that could be removed without losing information

### Rule 9: Human-Like Writing

- **High perplexity:** Vary word choices, avoid predictable phrases. Do not default to the same adjectives, transitions, or sentence openers repeatedly.
- **Burstiness:** Mix short punchy sentences (8-12 words) with medium ones (15-25 words). Rarely exceed 35 words. Vary paragraph lengths.
- **Varied sentence openers:** Never start three or more sentences in a row with the same word or pattern. Restructure to lead with the benefit, the process, the material, or the outcome.
- **No robotic phrasing:** No overly formal constructions, unnecessary hedging, or AI filler. If a phrase sounds like it could appear in any AI-generated article on any topic, replace it with something specific to the actual manufacturing process being described.
- **Full buzzword avoidance list:** Refer to `Content brain/ai-buzzwords.md` (read in Step 2.9). Any word or phrase listed there is banned from the content.

### Rule 10: Semantic Triple Structure in Key Positions

Structure key informational sentences as semantic triples: [Subject Entity] + [relationship verb] + [specific value/object].

Apply in these specific positions only:
- **First sentence of each H2 section:** Open with the topic entity as the subject, followed by an action verb and a specific value. Example: "Aluminum die casting produces components at tolerances of ±0.005 inches." NOT: "In today's competitive landscape, casting is becoming increasingly important."
- **FAQ answers:** Start each answer with the subject entity.
- **Key Takeaways bullets:** Each bullet reads as a standalone fact.
- **Opening paragraph:** First sentence should be a complete semantic triple.

Do NOT force triples into storytelling sections or conversational paragraphs. Readability and the Content Brain voice take priority.

### Rule 11: Conditional Sections

**If the topic relates to a non-China country** (detected in Step 2.5): Include a vs-China comparison section deeper in the article (not in the opening). Use a comparison table. Follow Content Brain country page template rules. Research real, current tariff rates via WebFetch if needed. Always add a date disclaimer on tariff numbers.

**If the topic relates to supply chain or geographic manufacturing:** Include a tariff/trade context section as a comparison-table block. No tariff-led messaging in the hero or opening. Verify current tariff data rather than relying on training data.

### Rule 12: Readability and Language

- Target 10th-grade reading level or below (Flesch-Kincaid)
- Active voice 65-75% of sentences
- Never use foreign words, even if they appear in NeuronWriter keyword lists. Skip any non-English term entirely.
- All content in standard American English.

### Rule 13: Word Count

Write to the target word count approved in Phase 2. Stay within +/-10% of the target.

### Output Format

Write the article as clean Markdown with heading hierarchy, tables in Markdown format, and internal links as `[anchor text](URL)`.

---

## Phase 6: Keyword & Terminology Compliance Loop

**This phase is mandatory. Do NOT skip it.**

### Check 1: Keyword Compliance

After writing the article, run the keyword compliance check using Python via Bash. Use the exact script pattern below, populated with ALL keywords from `content_basic_w_ranges` (excluding the terminology skip-list from Step 2.6):

```python
import re

with open('{keyword}-blog-draft.md', 'r', encoding='utf-8') as f:
    text = f.read().lower()

# Exclude SEO metadata block above H1 from counting
if '\n# ' in text:
    text = text[text.index('\n# '):]

# Strip markdown link URLs — only count anchor text, not URLs
text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)

words = len(text.split())
print(f'Total word count: {words}')
print()

keywords = {
    # Populate ALL keywords from content_basic_w_ranges (excluding skip-list)
    # 'keyword': (lower_bound, upper_bound),
}

print(f'{"Keyword":<40} {"Count":>5} {"Range":>10} {"Status":>10}')
print('-' * 70)

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
    print(f'{kw:<40} {count:>5} {lo}-{hi:>3}x {status:>10}')

if issues:
    print(f'\n=== {len(issues)} ISSUES FOUND ===')
    for kw, count, lo, hi in issues:
        print(f'  {kw}: {count}x (target {lo}-{hi}x)')
else:
    print('\nAll keywords within range!')
```

Also check extended keyword coverage on each pass:

```python
extended = [
    # List all extended keywords from content_extended_w_ranges
]
present = sum(1 for kw in extended if re.findall(re.escape(kw), text))
print(f'\nExtended keywords: {present}/{len(extended)} ({round(present/len(extended)*100) if extended else 0}%)')
```

### Check 2: ContentBrain Terminology Violation Scan

Run a second Python check that scans for forbidden terms from Content Brain:

```python
import re

with open('{keyword}-blog-draft.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Skip SEO metadata block
if '\n# ' in text:
    text_body = text[text.index('\n# '):]
else:
    text_body = text

forbidden = [
    (r'\bsourc(?:e|ing|ed)\b', 'source/sourcing (Content Brain #1 ban)'),
    (r'\bglobal\b', 'global (Content Brain #2 ban)'),
    (r'\bfactor(?:y|ies)\b', 'factory/factories (Content Brain #2 ban)'),
    (r'\bprecision engineering\b', 'precision engineering (Content Brain #2 ban)'),
    (r'\bcontract manufactur\w*\b', 'contract manufacturing (Content Brain #10)'),
    (r'\boutsourc\w*\b', 'outsourcing (Content Brain #5)'),
    (r'\bbroker\b', 'broker (Content Brain)'),
    (r'\bmiddleman\b', 'middleman (Content Brain)'),
    (r'\bworld[\s-]class\b', 'world-class (superlative ban)'),
    (r'\bbest[\s-]in[\s-]class\b', 'best-in-class (superlative ban)'),
    (r'\bpremier\b', 'premier (superlative ban)'),
    (r'\bindustry[\s-]leading\b', 'industry-leading (superlative ban)'),
    (r'\bpremium\b', 'premium (superlative ban)'),
    (r'\bmade in (?:usa|the usa|u\.s\.a?)\b', 'made in USA (Content Brain #20)'),
    (r'\bdomestic foundry\b', 'domestic foundry (Content Brain #20)'),
    (r'\bbuild it\b', 'build it (CTA ban)'),
    (r'\u2014', 'em dash (Content Brain #14)'),
    (r'\u2013', 'en dash (Content Brain #14)'),
    (r"in today'?s (?:fast|competitive|ever)", 'ChatGPT slop phrase'),
    (r"it'?s important to note", 'ChatGPT slop phrase'),
    (r'when it comes to', 'ChatGPT slop phrase'),
    (r'in the ever[\s-]evolving', 'ChatGPT slop phrase'),
    (r"let'?s dive in", 'ChatGPT slop phrase'),
    (r'at the end of the day', 'ChatGPT slop phrase'),
    (r'is a game[\s-]changer', 'ChatGPT slop phrase'),
    (r'navigating the complexities', 'ChatGPT slop phrase'),
    (r'without further ado', 'ChatGPT slop phrase'),
]

text_lower = text_body.lower()
violations = []
for pattern, label in forbidden:
    matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
    if matches:
        violations.append((label, len(matches), [m.group() for m in matches[:3]]))

if violations:
    print(f'=== {len(violations)} TERMINOLOGY VIOLATIONS ===')
    for label, count, examples in violations:
        print(f'  {label}: {count}x — e.g., "{examples[0]}"')
else:
    print('No terminology violations found!')
```

### Compliance Loop Rules

1. **If ALL keywords in range AND no terminology violations:** Proceed to Phase 7.
2. **If issues exist:** Fix them using targeted `Edit` calls on the file:
   - For STUFFED keywords: replace excess occurrences with synonyms, pronouns, or rephrase
   - For MISSING keywords: insert naturally into existing sentences
   - For terminology violations: replace with Content Brain approved alternatives
   - After edits, re-run both compliance checks
3. **Repeat up to 3 total passes.** If issues remain after 3 passes, show the remaining issues and ask the user for guidance.
4. Also verify the word count is within +/-10% of the target on each pass.

---

## Phase 6.5: AI Buzzword Compliance Check

**This phase is mandatory. Run it after keyword and terminology compliance passes and before output.**

Scan the content in `{keyword}-blog-draft.md` against the buzzword categories from `Content brain/ai-buzzwords.md`. Run this Python script via Bash:

```python
import re

with open('{keyword}-blog-draft.md', 'r', encoding='utf-8') as f:
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

1. **If no violations found:** Proceed to Phase 7 (Output & Upload).
2. **If violations found:** Fix them using targeted `Edit` calls:
   - Replace each flagged word/phrase with specific, concrete language
   - Do NOT replace with another word from the buzzword list
   - After edits, re-run the buzzword scan AND the keyword compliance check (fixes must not break keyword ranges)
3. **Repeat up to 2 passes.** If violations remain after 2 passes, show them to the user.

---

## Phase 7: Output & Upload

### Step 7.1 -- Generate SEO Metadata Block

Create a project metadata block to prepend to the article:

```
**Client Name:** Redstone Manufacturing

**Client URL:** <https://redstonemanufacturing.com>

**SEO Title Option 1:** [title, <=60 chars, primary keyword near front]
**SEO Title Option 2:** [title, different angle]
**SEO Title Option 3:** [title, different angle]

**URL Slug:** /blog/[keyword-slugified]/

**Meta Description Option 1:** [<=155 chars, lead with entity name or topic]
**Meta Description Option 2:** [<=155 chars, different angle]

**Hub Service Page:** [URL of the parent hub service page from Step 2.5]

**Internal Links:** [List naked URLs of Redstone links used in the article]

**External Links:** [List naked URLs of external source links used in the article]

**Target Keyword(s):** [Main Keyword from requirements JSON]

**Target Word Count:** [Approved target from Phase 2]

**Actual Word Count:** [Final word count after compliance loop]

**Target Audience:** Engineers and procurement managers evaluating [topic area]

**Goal:** SEO traffic, hub-and-spoke authority building for [hub service page], thought leadership for engineers and procurement professionals
```

**SEO Title rules:**
- 3 options, each <=60 characters
- Do NOT include the brand name in the title
- Primary keyword near the beginning
- Can end with parenthetical benefit where appropriate

**Meta Description rules:**
- 2 options, each <=155 characters
- Lead with "Redstone Manufacturing" or the topic entity per Content Brain semantic triple rules
- Include primary keyword + clear value proposition

### Step 7.2 -- Save Article

Combine the metadata block + the article text into one document. Save to `{keyword-slugified}-blog-draft.md` in the working directory.

### Step 7.3 -- Upload to NeuronWriter (Optional)

Ask the user: "Would you like to upload this blog post to NeuronWriter?"

If yes:
1. Copy `{keyword}-blog-draft.md` to `{keyword}-optimized.md` (the upload script expects this filename pattern)
2. Run `python upload_to_neuronwriter.py`
3. Report the content score returned by NeuronWriter
4. Remove the `-optimized.md` copy (keep `-blog-draft.md` as the canonical file)

If no: skip upload.

### Step 7.4 -- Archive Intermediate Files

Move intermediate files to `processed/`:

```bash
mkdir -p processed
mv {keyword}-content.md {keyword}-requirements.json {keyword}-serp.json {keyword}-paa.json processed/
```

Keep in the working directory:
- `{keyword}-blog-draft.md` (the final output)
- `research-report-*.md` (user may need for future reference)

---

## Phase 8: Tracking & Summary

### Step 8.1 -- Update Blog Posts Tracker

Maintain `blog_posts.csv` in the working directory. This is a separate tracker from `created_urls.csv` and `optimized_urls.csv` (those track service pages).

**Columns:**
```
QUERY ID,KEYWORD,BLOG URL SLUG,HUB SERVICE PAGE,DATE,CONTENT SCORE,WORD COUNT,TARGET WORD COUNT,RESEARCH REPORT FILE
```

Use Python via Bash to handle the CSV:

```python
import csv
import os
from datetime import date

csv_file = 'blog_posts.csv'
headers = ['QUERY ID', 'KEYWORD', 'BLOG URL SLUG', 'HUB SERVICE PAGE',
           'DATE', 'CONTENT SCORE', 'WORD COUNT', 'TARGET WORD COUNT',
           'RESEARCH REPORT FILE']

new_row = {
    'QUERY ID': '{query_id}',
    'KEYWORD': '{keyword}',
    'BLOG URL SLUG': '/blog/{keyword-slugified}/',
    'HUB SERVICE PAGE': '{hub_service_page_url}',
    'DATE': str(date.today()),
    'CONTENT SCORE': '{content_score}',
    'WORD COUNT': '{word_count}',
    'TARGET WORD COUNT': '{target_word_count}',
    'RESEARCH REPORT FILE': '{research_report_filename}',
}

rows = []
exists = os.path.exists(csv_file)
if exists:
    with open(csv_file, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

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

print(f'Blog tracker {"updated" if updated else "appended"}: {csv_file}')
```

### Step 8.2 -- Report Results

Print a summary:
- NeuronWriter content score (if uploaded)
- Word count (actual vs target)
- Keyword compliance status (all within range / X issues remaining)
- Extended keyword coverage (X/Y, Z%)
- ContentBrain terminology violations (0 or list remaining)
- Number of internal links inserted
- Hub service page linked: [URL]
- FAQ questions used (count and source: DataForSEO PAA vs NeuronWriter PAA)
- Research report used: [filename]

---

## Important Reminders

1. **Content Brain is the #1 authority.** All voice, positioning, and terminology rules from `Content brain/contentbrain.md` override everything else, including NeuronWriter keyword suggestions.
2. **Research report is mandatory.** If no `research-report-*.md` exists, stop and tell the user to run `/research-for-blog-post` first.
3. **Hub-and-spoke linking is mandatory.** Every blog post must link to its parent hub service page.
4. **Never compromise readability for keyword density.** Natural language always wins. If a keyword cannot be inserted without awkwardness, skip it.
5. **Substring awareness is critical.** Every compound keyword also increments all its parent keyword counts.
6. **Python verification is mandatory.** Never rely on internal counting. Always run the Python scripts to verify compliance.
7. **Proper nouns are always capitalized** regardless of how they appear in NeuronWriter data.
8. **User interaction points:** This skill has THREE mandatory interaction points: word count approval (Step 2.4), hub service page confirmation (Step 2.5), and upload decision (Step 7.3). Do NOT skip these.
9. **Never use em-dashes or en-dashes** anywhere in the content. Replace with commas, colons, or rephrase.
10. **Never use foreign words**, even if they appear in NeuronWriter keyword requirements. Skip entirely.
11. **No ChatGPT slop.** No filler phrases, no empty superlatives, no generic conclusions. Every sentence must carry information.
12. **Dual audience rule.** Every blog post must serve both engineers (technical specifics, tolerances, material properties) and procurement managers (cost, lead times, risk mitigation, supplier credibility). If the article leans too heavily toward one audience, rebalance.
13. **Semantic triples are a writing technique, not a compliance metric.** Use Entity + Relationship + Value structure in section openers, the opening paragraph, meta descriptions, and FAQ answers. Never override keyword compliance, word count, or Content Brain rules for triple structure.
14. **AI buzzwords are banned.** Every word, phrase, and structural pattern listed in `Content brain/ai-buzzwords.md` must be avoided. The buzzword compliance check in Phase 6.5 catches violations, but aim to avoid them during writing.
