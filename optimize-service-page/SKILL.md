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
7. **`Content brain/ai-buzzwords.md`** — AI buzzword avoidance guide (words and phrases to never use)

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
- `h2_terms` — Heading keyword recommendations with `usage_pc` (used for both H2 and H3 optimization)
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

words = len(text.split())
print(f'Original word count: {words}')
print()

# Parse keywords from content_basic_w_ranges
keywords = {
    # 'keyword': (lower_bound, upper_bound),
    # ... populate from requirements JSON ...
}

def overflow_tolerance(hi):
    """Allowed instances above upper bound based on max limit."""
    if hi <= 5:
        return 1
    elif hi <= 10:
        return 2
    else:
        return 3

print(f'{"Keyword":<35} {"Count":>5} {"Range":>10} {"Hard Max":>9} {"Status":>10}')
print('-' * 75)

for kw, (lo, hi) in sorted(keywords.items(), key=lambda x: x[1][1]):
    count = count_kw(kw, text)
    hard_max = hi + overflow_tolerance(hi)
    if count > hard_max:
        status = 'STUFFED'
    elif count > hi:
        status = 'OVER-OK'
    elif count < lo:
        status = 'MISSING'
    else:
        status = 'OK'
    print(f'{kw:<35} {count:>5} {lo}-{hi:>3}x {hard_max:>7}x {status:>10}')
```

Review the output. Note which keywords are STUFFED (above hard max, must reduce) vs. OVER-OK (above range but within tolerance, acceptable) vs. MISSING (must add). This informs the rewrite strategy.

### Step 2.5 — Read PAA and Internal URLs

- Read `{keyword}-paa.json` for FAQ questions
- Read `internal_urls.csv` for internal linking targets
- Identify the page's own URL (to avoid self-linking) by matching the keyword to the most relevant URL in the list

### Step 2.6 — Read AI Buzzwords Avoidance List

Read `Content brain/ai-buzzwords.md` in full. Internalize ALL categories of words and phrases to avoid:
- **Universal top offenders** (delve, showcasing, aligns, notably, etc.)
- **Transition words** (moreover, furthermore, consequently, hence, etc.)
- **Buzzword adjectives** (crucial, pivotal, transformative, robust, seamless, etc.)
- **AI-tell verbs** (delve, leverage, utilize, facilitate, foster, navigate, etc.)
- **Filler phrases and openers** ("In today's fast-paced...", "It's important to note...", etc.)
- **Abstract nouns** (landscape, tapestry, journey, realm, paradigm, etc.)
- **Industry-specific AI clusters** (hollow innovation, vague efficiency, corporate solutions language)
- **Structural red flags** ("It's not about X, it's about Y", uniform sentence length, etc.)

**These words and phrases are BANNED from the content you write.** If you catch yourself reaching for any of them, replace with specific, concrete language relevant to the actual service being described. When de-stuffing keywords (replacing overused keywords with alternatives), do NOT substitute with AI buzzwords.

---

## Phase 3: Content Optimization

You are an expert SEO copywriter. Rewrite the content following these rules strictly and in priority order.

### Rule 1: Minimal Rewriting Principle

Make the fewest changes necessary to meet optimization targets. Do not restructure paragraphs, change the narrative flow, or rewrite sentences that are already well-optimized. If a sentence already contains the right keywords in natural density, leave it alone.

### Rule 2: Content Basic Keywords — STRICT Range Enforcement

**This is the highest-priority rule.** Treat `content_basic_w_ranges` ranges as hard limits.

**CRITICAL — Word-Level Overlap Awareness:** Keywords are counted using whole-word boundary matching, not substring matching. This means "suv" does NOT count as "uv", and "glossy" does NOT count as "gloss". However, multi-word phrases still overlap at the word level. For example:
- The text "sand casting foundry" increments counts for "sand casting" (consecutive whole words), "casting" (whole word), AND "foundry" (whole word)
- "ceramic coating services" increments both "ceramic coating" and "coating" (each word is whole)
- But "suv" does NOT increment "uv" (not a whole-word match)
- And "glossier" does NOT increment "gloss" (not a whole-word match)

When adding a compound keyword, mentally increment ALL single-word and overlapping multi-word keywords that share whole words, and check they remain in range.

**Reducing keyword stuffing is the #1 goal.** Original content is typically keyword-stuffed — many keywords appear 3x to 10x above their target range. You MUST fix this.

Rules:
- **Stay within the upper bound of each range, with a small overflow tolerance.** The allowed overflow depends on the keyword's upper bound:
  - **Max ≤ 5x:** 1 extra instance allowed (e.g., a keyword with range 1-3x is acceptable at 4x)
  - **Max 6-10x:** 2 extra instances allowed (e.g., a keyword with range 2-7x is acceptable at 9x)
  - **Max > 10x:** 3 extra instances allowed (e.g., a keyword with range 10-27x is acceptable at 30x)
  - Aim for within-range first. The overflow tolerance exists for cases where structural content (testimonials, navigation, product names, pricing tables) makes exact compliance impossible.
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

Review `content_extended_w_ranges`. Add a majority of these extended keywords where they fit naturally. Skip any that would feel forced or off-topic.

**Extended keyword coverage targets (based on word count target from Step 2.3):**
- **Pages with 1,000+ words:** Target **75%** or more of extended keywords present.
- **Pages under 1,000 words:** Target **65%** or more of extended keywords present.

**Budget check:** After mentally placing extended keywords, verify that basic keyword ranges are still respected. Extended keywords often share whole words with basic keywords (e.g., "best ceramic coating" contains the whole word "coating").

### Rule 4: Proper Noun Capitalization

The requirements file lists all keywords in lowercase. Always capitalize proper nouns correctly:
- Country names: "India," "Mexico," "China," "United States"
- City/region names: "Gujarat," "Coimbatore," "Seattle"
- Company names: "Redstone," "Redstone Manufacturing"

### Rule 5: Word Count Compliance

Stay within ±10% of the word count target established in Step 2.3. If the original content was 950 words, your output must be between 855–1,045 words. Do NOT inflate content beyond the original length.

### Rule 6: Subheading Optimization (H2 and H3)

NeuronWriter provides a single `h2_terms` list of heading keywords, each with a `usage_pc` value (percentage of top-ranking competitors using that keyword in their headings). NeuronWriter scores keywords higher when they appear in H2s and lower when in H3s. Use this to your advantage: place the most important keywords in H2 headings and medium-importance ones in H3 headings.

**Sort the `h2_terms` list by `usage_pc` descending, then apply these tiers:**

| Tier | `usage_pc` | Place in | Action |
|------|-----------|----------|--------|
| Top tier | ≥ 40 | **H2** | MUST appear in an H2. Modify the most topically relevant existing H2 to incorporate the keyword. |
| Mid tier | 20–39 | **H3** | Should appear in an H3. Modify an existing H3, or add a new H3 under the most relevant H2 section if the content supports a logical subsection. |
| Low tier | < 20 | Either | Only incorporate if it fits naturally into an existing H2 or H3. Do not force these. |

**How to modify headings:**
- **Adjust wording, don't replace meaning.** Keep the original intent of the heading. For example, "Our Casting Process" can become "Our Sand Casting Process" to incorporate "sand casting," but should NOT become a completely unrelated heading.
- **Match the keyword to the right section.** Only place a keyword in a heading whose section content actually covers that topic. Never put a keyword in an unrelated heading just to score points.
- **Combine multiple keywords into one heading when they naturally fit together.** Look for keywords that overlap or complement each other and can form a single coherent heading. For example, if `h2_terms` includes both "sand casting" and "sand casting process," the H2 "Our Sand Casting Process" covers both. Similarly, "investment casting" + "investment casting tolerances" can become "Investment Casting Tolerances and Capabilities." Only combine when the result reads naturally — never force unrelated keywords into the same heading.
- **Creating new H3s is acceptable** when a mid-tier keyword doesn't match any existing H3 but does match the topic of an H2 section. Add the H3 as a logical subsection with supporting content beneath it (2-3 sentences minimum). Do NOT create empty or stub subsections.
- **Do NOT create new H2 sections** solely to accommodate heading keywords. Only modify existing H2s.

**Constraints (these always apply):**
- **Content Brain overrides heading keywords.** If a heading keyword conflicts with Content Brain terminology rules (e.g., a forbidden term), do NOT use it.
- **Keyword overlap awareness applies to headings.** Keywords in headings count toward `content_basic_w_ranges` totals. When adding a keyword to a heading, check that it doesn't push any basic keyword over its hard max.
- **Preserve the page's heading hierarchy and logical flow.** Do not rearrange sections to fit heading keywords.
- **Capitalize heading keywords as proper nouns where applicable** (Rule 4 still applies).
- **Never put internal links in headings** (Rule 7 still applies).

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
- Lead with the brand/company entity name, not with action verbs, pronouns, or generic phrases

**Note:** Keywords in the SEO metadata block (everything above the H1) are NOT counted toward keyword compliance ranges. The compliance scripts automatically exclude this block, so you can freely use keywords in titles and meta descriptions without inflating counts.

### Rule 10: Semantic Triple Structure in Key Positions

Structure key sentences as semantic triples: [Entity] + [relationship verb] + [value/object]. This makes content parseable by AI models and knowledge graphs.

Apply in these specific positions only — do not force triples into every sentence:

1. **First sentence of each H2 section:** Open with the company/brand name or the service as the subject, followed by an action verb and a specific value. Example: "Redstone Manufacturing produces investment castings at tolerances of ±0.005 inches." NOT: "We are proud to offer high-quality casting services."
2. **Meta descriptions (Rule 9):** Lead with the brand entity, not action verbs or pronouns. Example: "Redstone Manufacturing delivers precision sand castings..." NOT: "Discover our premium casting solutions..."
3. **FAQ answers:** Start each answer with the subject entity (the thing being asked about), not "Yes," "No," or "It depends."

**Do NOT:**
- Restructure paragraphs solely to create triples — the Minimal Rewriting Principle (Rule 1) still applies
- Sacrifice keyword compliance for triple structure — keyword ranges are the higher priority
- Add word count just to fit more triples — word count discipline still applies

### Output Format

Write the optimized content to `{keyword}-optimized.md` as clean Markdown:
- SEO metadata block at the top
- Same heading hierarchy (H1, H2, H3) as original
- Same section order
- Tables in Markdown format
- Internal links as `[anchor text](URL)`
- **Bullet list formatting (CRITICAL):** Every bullet item MUST be written as `- Item text` on a single line. The dash and the item text must be on the same line with a space between them. NEVER split a bullet into a bare `-` on one line with the text on the next line. Bare dashes separated from their content by blank lines will NOT render as list items in the HTML upload and will break formatting in NeuronWriter. If the original content has bare dashes with text on separate lines, fix them during optimization. Example of CORRECT formatting: `- 100% Hand Wash w/ Deionized Water`. Example of WRONG formatting: `-\n\n100% Hand Wash w/ Deionized Water`.

---

## Phase 4: Keyword Compliance Loop

**This phase is mandatory. Do NOT skip it.**

After writing the optimized content, run the keyword compliance check using Python via Bash. Use the exact script pattern below, populated with ALL keywords from `content_basic_w_ranges`:

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

words = len(text.split())
print(f'Total word count: {words}')
print()

keywords = {
    # Populate ALL keywords from content_basic_w_ranges
    # 'keyword': (lower_bound, upper_bound),
}

def overflow_tolerance(hi):
    """Allowed instances above upper bound based on max limit."""
    if hi <= 5:
        return 1
    elif hi <= 10:
        return 2
    else:
        return 3

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

1. **If ALL keywords are within range or within overflow tolerance (OVER-OK):** Proceed to Phase 5. Keywords marked OVER-OK are above the ideal range but within the allowed overflow tolerance and do not need fixing.
2. **If STUFFED or MISSING issues exist:** Fix them using targeted `Edit` calls on the optimized file:
   - Fix the MOST over-limit keyword first (the one furthest above its hard max)
   - Fixing one keyword often fixes others due to word-level overlap
   - For STUFFED keywords: replace excess occurrences with synonyms, pronouns, or rephrase
   - For MISSING keywords: insert naturally into existing sentences
   - After edits, re-run the Python compliance check
3. **Repeat up to 3 total passes.** If issues remain after 3 passes, show the remaining issues and ask the user for guidance.
4. Also verify the word count is within ±10% of the target on each pass.

Also check extended keyword coverage on the final pass:

```python
# Add this to the compliance script (count_kw function must be defined above)
extended = [
    # List all extended keywords from content_extended_w_ranges
]
present = sum(1 for kw in extended if count_kw(kw, text))
print(f'\nExtended keywords: {present}/{len(extended)} ({round(present/len(extended)*100)}%)')
```

Target: **75%+** for pages with 1,000+ words, **65%+** for pages under 1,000 words (based on the word count target from Step 2.3).

---

## Phase 4.5: AI Buzzword Compliance Check

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

1. **If no violations found:** Proceed to Phase 5 (Upload).
2. **If violations found:** Fix them using targeted `Edit` calls:
   - Replace each flagged word/phrase with specific, concrete language
   - Do NOT replace with another word from the buzzword list
   - After edits, re-run the buzzword scan AND the keyword compliance check (fixes must not break keyword ranges)
3. **Repeat up to 2 passes.** If violations remain after 2 passes, show them to the user.

---

## Phase 5: Upload and Cleanup

### Step 5.1 — Fix Multi-Line Markdown Links

**Before uploading**, fix any markdown links that are split across multiple lines. The NeuronWriter fetch script often produces links where the `[`, anchor text, and `](url)` are on separate lines. These render as broken plaintext (visible brackets and URLs) instead of clickable links. Run this Python script via Bash:

```python
import re

filepath = '{keyword}-optimized.md'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix multi-line markdown links: [ \n text \n ](url) -> [text](url)
fixed = re.sub(
    r'\[\s*\n\s*\n?(.*?)\s*\n\s*\n?\]\(([^)]+)\)',
    lambda m: '[' + m.group(1).strip() + '](' + m.group(2) + ')',
    content,
    flags=re.DOTALL
)

# Clean up excessive blank lines (3+ consecutive newlines -> 2)
fixed = re.sub(r'\n{3,}', '\n\n', fixed)

changes = content != fixed
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(fixed)

# Verify: check for remaining orphan "[" on its own line
remaining = re.findall(r'^\[$', fixed, re.MULTILINE)
proper = len(re.findall(r'\[[^\]]+\]\([^)]+\)', fixed))
print(f'Link fix applied: {"yes" if changes else "no changes needed"}')
print(f'Remaining orphan "[" lines: {len(remaining)}')
print(f'Properly formatted links: {proper}')
```

If orphan `[` lines remain after the first pass, inspect the surrounding lines and fix manually with a targeted string replacement. The most common residual pattern is `[\n\ntext](url)` where a blank line separates the bracket from the anchor text. Proceed to the next step only when orphan `[` lines = 0.

### Step 5.2 — Fix Bullet Formatting

Run this Python script to fix any bare-dash bullet items that survived from the original content. Bare dashes (`-` on their own line, text on the next) do not render as list items in HTML and will break formatting in NeuronWriter.

```python
import re

filepath = '{keyword}-optimized.md'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix bare dashes: a line with only "-" followed by blank line(s) and then text
fixed = re.sub(r'\n-\n\n+([^\n-])', r'\n- \1', content)

fixes = content != fixed
if fixes:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fixed)

bare_remaining = len(re.findall(r'\n-\n', fixed))
proper = len(re.findall(r'\n- [^\n]', fixed))
print(f'Bullet fix applied: {"yes" if fixes else "no changes needed"}')
print(f'Bare dashes remaining: {bare_remaining}')
print(f'Proper list items: {proper}')
```

If bare dashes remain after the first pass, run the script again (some nested patterns may need a second pass). Proceed to upload only when bare dashes = 0.

### Step 5.3 — Upload to NeuronWriter

Run the upload script:

```
python upload_to_neuronwriter.py
```

This auto-detects the requirements file, reads `{keyword}-optimized.md`, converts to HTML, and uploads. Report the content score returned by NeuronWriter.

### Step 5.4 — Archive Intermediate Files

Create a `processed/` subfolder (if it doesn't exist) and move intermediate files there:

```bash
mkdir -p processed
mv {keyword}-content.md {keyword}-requirements.json {keyword}-serp.json {keyword}-paa.json processed/
```

Keep `{keyword}-optimized.md` in the working directory for reference.

### Step 5.5 — Update Optimized URLs Tracker

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

### Step 5.6 — Report Results

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
5. **Word-level overlap awareness is critical.** Keywords are matched as whole words (using `\b` word boundaries), so "suv" does not count as "uv" and "glossy" does not count as "gloss". However, multi-word phrases still overlap at the word level: "ceramic coating services" increments both "ceramic coating" and "coating". Track these whole-word overlaps as you write.
6. **Python verification is mandatory.** Never rely on internal counting — always run the Python script to verify compliance.
7. **Proper nouns are always capitalized** regardless of how they appear in the requirements data.
8. **Semantic triples are a writing technique, not a compliance metric.** Use Entity + Relationship + Value structure in section openers, meta descriptions, and FAQ answers. Never sacrifice keyword compliance or word count discipline for triple structure.
9. **AI buzzwords are banned.** Every word, phrase, and structural pattern listed in `Content brain/ai-buzzwords.md` must be avoided. When de-stuffing keywords, never replace them with AI buzzwords. The buzzword compliance check in Phase 4.5 catches violations, but aim to avoid them during writing.
10. **Never use em-dashes (—) in the content.** Em-dashes are an AI writing tell and must not appear anywhere in the optimized output. Use commas, periods, colons, or restructured sentences instead. For parenthetical asides, use commas. For separate thoughts, use periods. For introducing lists or explanations, use colons.
