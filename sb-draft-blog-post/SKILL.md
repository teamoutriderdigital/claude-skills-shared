---
name: sb-draft-blog-post
description: End-to-end Smith Bros Mobile Detailing blog post drafting pipeline. Fetches NeuronWriter requirements and SERP/PAA data, uses a pre-generated research report, creates a content brief, selects hub-and-spoke internal links, writes a full SEO-optimized blog post in Smith Bros' warm, approachable local-business voice per Content Brain, runs keyword and terminology compliance, and optionally uploads to NeuronWriter. Use this skill whenever the user wants to draft an SB Mobile Detailing blog post, write a blog from research for a keyword, create a Smith Bros article, or generate a blog post from a NeuronWriter query. Also triggers for "draft SB blog post", "write SB blog for [keyword]", "create Smith Bros article for [keyword]", "generate SB blog post from NeuronWriter query", or "sb blog post".
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebFetch, AskUserQuestion, TaskCreate, TaskUpdate
---

# Smith Bros Mobile Detailing Blog Post Drafting

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

For SB blog topics, the research report may include competitor pricing data, local market information, and San Diego-specific climate/environment context. Extract these specifically as they inform pricing sections and local SEO angles.

---

## Phase 2: Pre-Analysis & Word Count

### Step 2.1 -- Read Content Brain

Read `Content brain/contentbrain.md` in full. This is the #1 authority on voice and positioning. For blog posts specifically, internalize:
- **Voice:** "We" for Smith Bros, "you" for the customer. First-person plural default.
- **Tone hierarchy:** Confident > Approachable > Trustworthy > Helpful > Warm
- **Active voice:** 85%+ target
- **All forbidden terms** (terminology mandates and ChatGPT slop sections)
- **Hub-and-spoke model:** Hubs are main service pages, Spokes are location pages, Supporting content is blog posts and vehicle-specific pages
- **FAQ:** 5-8 pairs for blog posts (accordion format, target People Also Ask queries)
- **Internal links:** Minimum 3 per page (excluding navigation), descriptive anchor text
- **Trust signals:** Minimum 1 per content piece, rotate from approved proof points
- **Mobile-first identity:** Must mention mobile service convenience in every piece
- **Phone number:** (760) 310-1532 must appear in every piece
- **Pricing context:** Always include "Starting at $X" when discussing services

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

From `{keyword}-requirements.json`, read the `competitors` array. Take top 5 by rank. Filter: only include competitors with `word_count` between 500 and 5000. Calculate the average, round to nearest 50. Apply a minimum floor of 1000 words (local service blogs need depth to rank but trend shorter than B2B technical content).

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
    target = max(1000, round(raw_avg / 50) * 50)
    print(f"\nQualifying pages: {len(qualifying)}/{len(competitors_sorted)}")
    print(f"Average word count: {raw_avg:.0f}")
    print(f"Rounded target (floor 1000): {target} words")
else:
    print("\nNo qualifying pages found. Defaulting to 1200 words.")
    target = 1200
```

**STOP and ask the user for approval.** Present the competitor word counts and calculated target. Ask: "The calculated target word count is **{target} words**. Should I proceed with this target, or would you like to adjust it?" Wait for response.

### Step 2.5 -- Auto-Detect Hub Service Page and Location Page

Analyze the blog keyword and map it to a parent hub service page AND a location page from `internal_urls.csv`.

**Hub service page detection:**
1. Extract the core service topic from the keyword (e.g., "ceramic coating maintenance tips" -> "ceramic coating", "best car detailing san marcos" -> "mobile auto detailing", "window tint legal limits california" -> "window tinting")
2. Match against service URLs in `internal_urls.csv`:
   - "detailing" / "detail" / "wash" / "clean" / "wax" -> mobile auto detailing service page
   - "ceramic" / "coating" -> ceramic coating service page
   - "tint" / "window film" -> window tinting service page
   - "ppf" / "protection film" / "paint protection" -> PPF service page
   - "motorcycle" -> motorcycle detailing service page
   - "boat" / "marine" -> boat detailing service page
   - "rv" / "motorhome" / "camper" -> RV detailing service page
   - "fleet" -> fleet detailing service page
3. Present the detected hub to the user for confirmation

**Location page detection:**
1. If the keyword contains a city or neighborhood name, match against location slugs in `internal_urls.csv` (under `/mobile-detailing/`, `/mobile-ceramic-coating/`, `/mobile-window-tinting/`, `/paint-protection-film/` paths)
2. Common San Diego locations to match: San Marcos, Carlsbad, Encinitas, Escondido, Del Mar, La Jolla, Oceanside, Poway, Rancho Santa Fe, Vista, 4S Ranch, Solana Beach, etc.
3. If a location page exists for the matching service + city combination, present it for confirmation
4. If no city is in the keyword, suggest the San Marcos location page (HQ) as default

If no hub can be auto-detected, ask the user to specify which service page(s) this blog supports.

### Step 2.6 -- Terminology Pre-Check

Scan NeuronWriter `content_basic_w_ranges` and `content_extended_w_ranges` for any keywords that violate Content Brain forbidden terms. Build a skip-list of keywords that must NOT be used regardless of NeuronWriter targets:

- Any keyword containing "car wash" (unless the blog is explicitly comparing detailing vs car wash, and even then use it only in that comparative context)
- Any keyword containing "cheap" or "cheapest"
- Any keyword containing "discount" or "budget"
- Any keyword containing "diy"
- Any keyword containing "basic" as a service tier name (use "Mini" or "Bronze" instead)
- Any keyword matching a competitor name (Blueberry, Dennis Details, Fresh Layer, etc.)

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

**These words and phrases are BANNED from the content you write.** If you catch yourself reaching for any of them, replace with specific, concrete language relevant to the actual vehicle, service, product, or San Diego context being described.

Also watch for auto-detailing-specific AI slop:
- "Restore your vehicle to its former glory"
- "Make your car shine like new"
- "Treat your vehicle to the pampering it deserves"
- "Your car will thank you"
- "Give your car the love it deserves"
- "A spa day for your car"

---

## Phase 3: Content Brief Creation

Generate a structured content brief using the research report and NeuronWriter data.

**System message:** You are an expert local SEO content strategist creating a content brief for a blog post on the Smith Bros Mobile Detailing website (sbmobiledetailing.com). The audience is vehicle owners in North San Diego County who are researching auto detailing, ceramic coating, window tinting, PPF, or vehicle care. Write for a mix of everyday car owners and car enthusiasts.

**Brief creation instructions:**

1. Use info, data, facts, and stats from the research report sections B, C, and D to populate the brief. Make it fact-rich but concise.
2. Structure the brief with H1, H2, and H3 headings. The total number of subheadings should align with competitor heading counts from the requirements JSON.
3. Use majority of keywords from `h2_terms` (where `usage_pc` >= 40) in subheadings. Write subheadings in Title Case for H1-H2, Sentence case acceptable for H3+. Use question format where appropriate per Content Brain rules ("How Often Should You Detail Your Car?", "Is Ceramic Coating Worth It?").
4. Under each subheading, insert 2-6 SHORT bullet points with data. Use tables for service tier comparisons, pricing comparisons, and product feature comparisons per Content Brain formatting rules.
5. Use figures and facts ONLY from the research report. Link to authoritative sources (Consumer Reports, Car and Driver, Edmunds, IDA, SEMA, manufacturer sites like 3M, Xpel, Llumar, .edu, .gov). Avoid linking to competitor detailing businesses. Do NOT mention sources in the form [Article X].
6. Create but do NOT fill: `## FAQ: [Topic Name]`
7. Include a bullet point noting where the hub service page link AND the location page link should appear (from Step 2.5).
8. Include a bullet point noting where the Smith Bros CTA section should go. The CTA connects the blog topic to Smith Bros' services naturally, includes phone number (760) 310-1532, and uses approved CTA language ("Book Now," "Get a Free Quote," "Call (760) 310-1532"). Not a hard sell.
9. If the topic relates to a specific location in the service area, include a section with local context (neighborhoods, local landmarks, San Diego climate factors affecting vehicle care -- UV exposure, coastal salt air, freeway debris on I-5/I-15).
10. If the topic relates to pricing or cost, include a section with Smith Bros' actual tier pricing and a note that pricing should include "Starting at $X for sedans" format per Content Brain.
11. Include a bullet point noting where a trust signal block should go. Rotate from: 32+ years in business, 1,000+ five-star reviews, 512 Google reviews, 491 Yelp reviews, 100% satisfaction guarantee, certified/licensed/insured/bonded, eco-friendly products, open 7 days a week.
12. Always output in markdown.

---

## Phase 4: Internal Link Selection (Hub-and-Spoke)

Read `internal_urls.csv` and select internal links following the Content Brain blog linking pattern.

**Mandatory links:**
1. **Parent hub service page** (identified in Step 2.5). This is non-negotiable for hub-and-spoke.
2. **At least 1 location page** from `internal_urls.csv` matching the service category and a relevant city. This strengthens local hub-and-spoke architecture.
3. At least 1 related service page or blog post from `internal_urls.csv`

**Additional links (select 3-5 more, for a total of 5-8):**
- Related service pages (e.g., if the blog is about ceramic coating maintenance, link to detailing, PPF, window tinting)
- Relevant vehicle-specific pages (e.g., `/cars/tesla-expert-san-diego`, `/cars/bmw-san-diego`, `/cars/exotic-car-detailing-san-diego`)
- Relevant location pages for other cities mentioned in the content
- Specialty service pages if relevant (e.g., vomit cleanup, odor removal, rodent remediation)

**Link rules (from Content Brain):**
- Links go in body text paragraphs only, never in headings
- Descriptive anchor text (not "click here" or "learn more")
- ~60% keyword-rich anchors, ~40% natural/generic
- Distribute throughout the article, not clustered in one section
- All real URLs from `internal_urls.csv`. No placeholder anchors.

---

## Phase 5: Full Article Writing

Read `Content brain/contentbrain.md` before writing. Use the content brief, internal links, PAA questions, and keyword data to write the article.

**System message:** You are an expert local SEO copywriter specializing in auto detailing and vehicle protection content. You write for vehicle owners in San Diego County, from daily drivers to exotic car collectors. Your tone is warm, confident, and knowledgeable, like a trusted friend who happens to be an expert detailer. You are writing a blog post for Smith Bros Mobile Detailing's website (sbmobiledetailing.com).

### Rule 1: Voice and Person (Blog-Specific)

Use first-person plural ("we/our") when referring to Smith Bros ("We bring our mobile detailing unit to your location" / "Our technicians use Opti-Coat Pro ceramic coating"). Use second-person ("you/your") when addressing the reader ("Your vehicle's paint faces UV damage every day in San Diego"). On location-specific blogs, lead with the location name, then transition to "we" voice. Never use "they" when talking about Smith Bros. Never use "I" unless directly quoting founder Luke Smith.

### Rule 2: Tone Hierarchy (Ranked, from Content Brain)

1. **Confident.** State capabilities as fact with proof points. "We bring 32 years of expertise to every detail."
2. **Approachable.** Conversational, not corporate. "Here's what actually happens when..." not "It is important to understand that..."
3. **Trustworthy.** Lead with proof: reviews, years, warranties, certifications. Proof before claim, not after.
4. **Helpful.** Educate without condescending. Explain ceramic vs. wax simply. Give the reader something useful even if they never book.
5. **Warm.** Family-business feel. "We treat your vehicle as if it were one of our own." Not generic corporate language.

### Rule 3: Article Structure

- **H1:** Include primary keyword, Title Case. For location-targeted posts, use "[Service/Topic] in [City], CA" format.
- **Introduction:** Write 2 versions (one below another), 60-80 words each. Open with a relatable scenario, specific stat, or local San Diego context that hooks the reader. Break into 2 paragraphs each. First-person plural voice. **Must mention mobile service convenience within the intro.** Must include at least one trust signal (32 years, 1,000+ reviews, etc.).
- **Key Takeaways:** Immediately after the introduction, include a section titled "Key Takeaways". List 4-6 ULTRA SHORT bullet points. One short sentence per line. No links or bolds. Each bullet is a standalone fact an AI could extract: [Subject] [verb] [specific claim].
- **No horizontal rules:** Do NOT insert horizontal rules (`---`, `***`, or `___`) anywhere in the article. Sections are separated by headings only.
- **Body:** Develop the main content from the brief. Use tables for tier/pricing comparisons, product feature comparisons, service package breakdowns. Use bullet points for "What's Included" lists, tips, and scannable information. Incorporate NLP keywords naturally. Include pricing context where relevant ("Starting at $X for sedans").
- **Smith Bros CTA Section:** One H2 section (naturally integrated, not a separate sales pitch) that connects the blog topic to Smith Bros' services. **Must include phone number (760) 310-1532.** Use CTA language from Content Brain: "Book Now," "Request a Quote," "Get a Free Quote," "Call (760) 310-1532," "Schedule Your Detail Today." Do NOT make this a hard sell. It should read as "if you're looking for this service, here's how we can help."
- **FAQ Section:** Title: "Frequently Asked Questions About [Topic]" in Title Case. Use 5-8 pairs from PAA questions (Step 2.3). Each question is an H3 heading (`###`). The answer is a normal paragraph (no bold, no special formatting). Start each answer with the subject entity (not "Yes," "No," or filler). Frame as customer concerns, not technical questions. Skip off-topic PAA questions.

### Rule 4: Formatting Rules (from Content Brain)

- Title Case for H1 and H2 headings. Sentence case acceptable for H3+.
- Oxford comma always
- No em dashes or en dashes anywhere (use comma, colon, or period instead)
- Bold for key differentiators, pricing, and warranty terms on first mention only. Bold service tier names (Bronze, Silver, Gold, Mini, Complete) on first mention. Use sparingly in body paragraphs.
- Tables for pricing/tier comparisons, product feature comparisons, service package breakdowns
- Short paragraphs (2-4 sentences)
- Numbers as numerals for pricing ($249), percentages (99%), and measurements. Spell out one through nine, use numerals for 10+.
- Phone number always formatted as (760) 310-1532 or 760-310-1532
- Product names always capitalized exactly: **Opti-Coat Pro**, **TEC582**, **GeoShield**
- Service tier names always capitalized: **Bronze**, **Silver**, **Gold**, **Mini Detail**, **Complete Detail**
- Introduce acronyms with full form + acronym in parentheses on first mention: "Paint Protection Film (PPF)". Exceptions: UV, SUV, RV -- never spell out.

### Rule 5: Keyword Integration -- STRICT Range Enforcement

Treat `content_basic_w_ranges` ranges as hard limits.

**CRITICAL -- Substring Awareness:** Keywords share substrings. For example:
- "mobile detailing san diego" increments counts for "mobile detailing", "detailing", "san diego", AND "detailing san diego"
- "ceramic coating cost" contains both "ceramic coating" and "coating"

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

Insert the 5-8 internal links selected in Phase 4.

- Links go in body text paragraphs only. **Never in headings.**
- The parent hub service page link is mandatory and should appear in the first third of the article if possible.
- A location page link should appear if the topic has geographic relevance.
- Descriptive anchor text, 1-4 words. ~60% keyword-rich, ~40% natural.
- Distribute naturally throughout, not clustered.

### Rule 7: Facts and Source Links

Use authoritative source links from the research report and content brief. Keep anchor text 1-4 words, descriptive. Link naturally within sentences. Avoid linking to competitor detailing businesses. Prefer consumer-facing authoritative sources (Consumer Reports, Car and Driver, Edmunds, IDA, SEMA, manufacturer sites like 3M, Xpel, Llumar, .edu, .gov). No naked URLs.

### Rule 8: Terminology Compliance (from Content Brain)

Never use any term from the Content Brain "Never Use" list. This includes but is not limited to:
- "Car wash" or "car wash service" in any form
- "Cheap," "cheapest," "discount detailing," "budget detailing"
- "DIY alternative" or suggesting the customer can do it themselves
- "Basic" as a tier name (use Mini or Bronze)
- "Workers" or "employees" (use "technicians" or "detailing professionals")
- "Consumers" (use "clients" or "customers")
- "Best in the world," "number one in the country" (unsubstantiated)
- Any competitor name (Blueberry, Dennis Details, Fresh Layer, etc.)
- "Unlike our competitors" or any comparative competitor reference
- "Trust us" without pairing with a proof point
- "I" in brand content (exception: attributed Luke Smith quotes)
- Em dashes and en dashes
- "Buy Now," "Sign Up," "Don't Miss Out," "Act Now Before It's Too Late," "Limited Time Offer" (unless an actual promotion exists)

Use the "Always Use" replacements from Content Brain terminology mandates section.

Never use ChatGPT slop phrases:
- "In today's fast-paced world..."
- "When it comes to..."
- "Look no further than..."
- "In the realm of..."
- "It's important to note that..."
- "At the end of the day..."
- "Game-changer"
- "Elevate your..."
- "Seamless" (unless describing a physical seam)
- "Leverage" (as a verb)
- "Holistic approach"
- "Robust"
- "Harness the power of..."
- "Delve into..."
- "Rest assured..."
- "Boasts"
- "Pivotal," "Myriad," "Plethora," "Paramount," "Meticulous"
- "Navigating the complexities of..."
- "Embark on a journey..."
- "Nestled in..."
- "Cutting-edge," "Revolutionize"
- Any sentence that could be removed without losing information

### Rule 9: Human-Like Writing

- **High perplexity:** Vary word choices, avoid predictable phrases. Do not default to the same adjectives, transitions, or sentence openers repeatedly.
- **Burstiness:** Mix short punchy sentences (8-12 words) with medium ones (15-25 words). Rarely exceed 35 words. Vary paragraph lengths.
- **Varied sentence openers:** Never start three or more sentences in a row with the same word or pattern. Restructure to lead with the benefit, the service, the product, or the outcome.
- **No robotic phrasing:** No overly formal constructions, unnecessary hedging, or AI filler. If a phrase sounds like it could appear in any AI-generated article on any topic, replace it with something specific to the actual vehicle, service, product, or San Diego context being described. Reference specific products (Opti-Coat Pro, TEC582, GeoShield), specific service tiers (Bronze, Silver, Gold), specific locations (San Marcos, Carlsbad, Encinitas), or specific vehicle types.
- **Full buzzword avoidance list:** Refer to `Content brain/ai-buzzwords.md` (read in Step 2.9). Any word or phrase listed there is banned from the content.
- **Detailing-specific AI slop -- also banned:**
  - "Restore your vehicle to its former glory"
  - "Make your car shine like new"
  - "Treat your vehicle to the pampering it deserves"
  - "Your car will thank you"
  - "Give your car the love it deserves"
  - "A spa day for your car"

### Rule 10: Semantic Triple Structure in Key Positions

Structure key informational sentences as semantic triples: [Subject Entity] + [relationship verb] + [specific value/object].

Apply in these specific positions only:
- **First sentence of each H2 section:** Open with the topic entity as the subject, followed by an action verb and a specific value. Example: "Professional ceramic coating protects paint for 3 to 5 years with a single application." NOT: "In today's world, keeping your car looking great is more important than ever."
- **FAQ answers:** Start each answer with the subject entity. Example: "Ceramic coating lasts 3 to 5 years depending on the tier and maintenance." NOT: "Great question! There are many factors that determine..."
- **Key Takeaways bullets:** Each bullet reads as a standalone fact.
- **Opening paragraph:** First sentence should be a complete semantic triple.

Do NOT force triples into storytelling sections or conversational paragraphs. Readability and the Content Brain voice take priority.

### Rule 11: Conditional Sections

**If the topic relates to a specific San Diego location:** Include a section with local context. Mention the neighborhood, local landmarks or context, driving conditions (coastal salt air for beach communities like Carlsbad, Encinitas, Del Mar; intense sun exposure for inland areas like Escondido, Poway, 4S Ranch), and why residents in that area benefit from the service. This should feel genuinely local, not template-swapped.

**If the topic relates to pricing or cost comparison:** Include a pricing context section with Smith Bros' actual tier pricing. Always format as "Starting at $X for sedans." Include a tier comparison table if the service has multiple tiers (detailing, ceramic, and tint all have Bronze/Silver/Gold tiers).

**If the topic relates to vehicle protection (ceramic, PPF, tint):** Include a section on San Diego-specific environmental factors: UV exposure (300+ sunny days per year), coastal salt air, freeway debris on I-5/I-15, and how these factors make protection services particularly valuable for local vehicle owners.

### Rule 12: Readability and Language

- Target 8th-grade reading level or below (Flesch-Kincaid). The audience is general vehicle owners, not specialists.
- Active voice 85%+ of sentences. Passive voice acceptable only for process descriptions ("Your vehicle is hand-washed with deionized water").
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
    (r'\bcar wash\b', 'car wash (Content Brain #1 ban)'),
    (r'\bcheap(?:est)?\b', 'cheap/cheapest (Content Brain terminology)'),
    (r'\bdiscount\b', 'discount (Content Brain terminology)'),
    (r'\bbudget\b', 'budget (Content Brain terminology)'),
    (r'\b(?:workers?|employees?)\b', 'workers/employees (use "technicians")'),
    (r'\bconsumers?\b', 'consumers (use "clients" or "customers")'),
    (r'\bdiy\b', 'DIY (never suggest customer can do it)'),
    (r'\bbasic\b(?!\s+(?:steps?|concepts?|understanding|information|maintenance|knowledge|ideas?))', 'basic (use tier names: Mini, Bronze)'),
    (r'\btrust us\b', 'trust us (must pair with proof point)'),
    (r'\bbest in the world\b', 'best in the world (unsubstantiated)'),
    (r'\bnumber one in\b', 'number one in (unsubstantiated)'),
    (r'\bblueberry\b', 'competitor name (Blueberry)'),
    (r'\bdennis\s*details?\b', 'competitor name (Dennis Details)'),
    (r'\bfresh layer\b', 'competitor name (Fresh Layer)'),
    (r'\bbuy now\b', 'banned CTA (use Book Now)'),
    (r'\bsign up\b', 'banned CTA (not subscription-based)'),
    (r"don'?t miss out", 'banned CTA (false urgency)'),
    (r'act now before', 'banned CTA (pressure tactics)'),
    (r'\u2014', 'em dash (use comma, colon, or period)'),
    (r'\u2013', 'en dash (use comma, colon, or period)'),
    (r"in today'?s (?:fast|competitive|ever)", 'ChatGPT slop phrase'),
    (r"it'?s important to note", 'ChatGPT slop phrase'),
    (r'when it comes to', 'ChatGPT slop phrase'),
    (r'in the ever[\s-]evolving', 'ChatGPT slop phrase'),
    (r"let'?s dive in", 'ChatGPT slop phrase'),
    (r'at the end of the day', 'ChatGPT slop phrase'),
    (r'game[\s-]changer', 'ChatGPT slop phrase'),
    (r'navigating the complexities', 'ChatGPT slop phrase'),
    (r'look no further', 'ChatGPT slop phrase'),
    (r'in the realm of', 'ChatGPT slop phrase'),
    (r'nestled in', 'ChatGPT slop phrase'),
    (r'elevate your', 'ChatGPT slop phrase'),
    (r'embark on a journey', 'ChatGPT slop phrase'),
    (r'unlock the secrets', 'ChatGPT slop phrase'),
    (r'rest assured', 'ChatGPT slop phrase'),
    (r'a testament to', 'ChatGPT slop phrase'),
    (r'\bboasts\b', 'ChatGPT slop phrase'),
    (r'\bpivotal\b', 'ChatGPT slop phrase'),
    (r'\bmyriad\b', 'ChatGPT slop phrase'),
    (r'\bplethora\b', 'ChatGPT slop phrase'),
    (r'\bparamount\b', 'ChatGPT slop phrase'),
    (r'\bmeticulous\b', 'ChatGPT slop (use "thorough" or "detailed")'),
    (r'\brobust\b', 'ChatGPT slop phrase'),
    (r'\bdelve\b', 'ChatGPT slop phrase'),
    (r'\bseamless\b', 'ChatGPT slop phrase'),
    (r'\bleverage\b', 'ChatGPT slop phrase'),
    (r'\bcutting[\s-]edge\b', 'ChatGPT slop phrase'),
    (r'\brevolutionize\b', 'ChatGPT slop phrase'),
    (r'\bholistic\b', 'ChatGPT slop phrase'),
    (r'former glory', 'detailing AI slop'),
    (r'shine like new', 'detailing AI slop'),
    (r'pampering it deserves', 'detailing AI slop'),
    (r'car will thank you', 'detailing AI slop'),
    (r'spa day for your', 'detailing AI slop'),
    (r'love it deserves', 'detailing AI slop'),
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
        print(f'  {label}: {count}x -- e.g., "{examples[0]}"')
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
    'mission-critical',
    'next-generation',
    'game-changer',
    'restore your vehicle to its former glory',
    'make your car shine like new',
    'treat your vehicle to the pampering',
    'your car will thank you',
    'give your car the love it deserves',
    'a spa day for your car',
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

Create a short SEO metadata block to prepend above the H1 title. This block contains ONLY the SEO titles, URL slug, and meta descriptions. Nothing else goes here.

```
**SEO Title Option 1:** [Primary Keyword] [City] ([Reader Benefit]) [<=60 chars]
**SEO Title Option 2:** [Different angle with primary keyword] ([Reader Benefit]) [<=60 chars]
**SEO Title Option 3:** [Different angle] ([Reader Benefit]) [<=60 chars]

**URL Slug:** /blog/[keyword-slugified]/

**Meta Description Option 1:** [<=155 chars, benefit + primary keyword + trust signal. End with: Call (760) 310-1532.]
**Meta Description Option 2:** [<=155 chars, different angle. End with: Call (760) 310-1532.]
```

Do NOT include client name, client URL, hub service page, location page, internal/external link lists, target keywords, word counts, target audience, or goal in this block. Those details are reported in the Phase 8 summary instead.

**SEO Title rules:**
- 3 options, each <=60 characters
- Format: `[Primary Keyword] [City] ([Reader Benefit])`
- End each title with a parenthetical reader benefit that tells the searcher what they will gain from clicking (e.g., "(Rules & Tips)", "(Avoid Fines)", "(Full Guide)", "(What to Know)", "(Save Time & Money)", "(Pricing & Options)")
- Do NOT append the business name ("-- Smith Bros") to blog post SEO titles
- Include city name for location-targeted posts
- Primary keyword near the beginning

**Meta Description rules:**
- 2 options, each <=155 characters
- Lead with benefit or topic entity + primary keyword + clear value proposition
- Include a trust signal
- **Must end with phone number:** "Call (760) 310-1532."

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

Maintain `blog_posts.csv` in the working directory. This is a separate tracker from `optimized_urls.csv` (that tracks service/location pages).

**Columns:**
```
QUERY ID,KEYWORD,BLOG URL SLUG,HUB SERVICE PAGE,LOCATION PAGE,DATE,CONTENT SCORE,WORD COUNT,TARGET WORD COUNT,RESEARCH REPORT FILE
```

Use Python via Bash to handle the CSV:

```python
import csv
import os
from datetime import date

csv_file = 'blog_posts.csv'
headers = ['QUERY ID', 'KEYWORD', 'BLOG URL SLUG', 'HUB SERVICE PAGE', 'LOCATION PAGE',
           'DATE', 'CONTENT SCORE', 'WORD COUNT', 'TARGET WORD COUNT',
           'RESEARCH REPORT FILE']

new_row = {
    'QUERY ID': '{query_id}',
    'KEYWORD': '{keyword}',
    'BLOG URL SLUG': '/blog/{keyword-slugified}/',
    'HUB SERVICE PAGE': '{hub_service_page_url}',
    'LOCATION PAGE': '{location_page_url}',
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

Print a summary that includes the project metadata (moved out of the article file) and performance data:

**Project metadata:**
- Client Name: Smith Bros Mobile Detailing
- Client URL: https://www.sbmobiledetailing.com
- Hub Service Page: [URL of the parent hub service page from Step 2.5]
- Location Page: [URL of the location page from Step 2.5, if applicable]
- Internal Links: [List naked URLs of Smith Bros links used in the article]
- External Links: [List naked URLs of external source links used in the article]
- Target Keyword(s): [Main Keyword from requirements JSON]
- Target Word Count: [Approved target from Phase 2]
- Actual Word Count: [Final word count after compliance loop]
- Target Audience: Vehicle owners in [City/North San Diego County] researching [topic area]
- Goal: SEO traffic, hub-and-spoke authority building for [hub service page], local visibility for [location], thought leadership for vehicle care

**Performance data:**
- NeuronWriter content score (if uploaded)
- Keyword compliance status (all within range / X issues remaining)
- Extended keyword coverage (X/Y, Z%)
- ContentBrain terminology violations (0 or list remaining)
- Phone number (760) 310-1532 included: Yes/No
- FAQ questions used (count and source: DataForSEO PAA vs NeuronWriter PAA)
- Research report used: [filename]

---

## Important Reminders

1. **Content Brain is the #1 authority.** All voice, positioning, and terminology rules from `Content brain/contentbrain.md` override everything else, including NeuronWriter keyword suggestions.
2. **Research report is mandatory.** If no `research-report-*.md` exists, stop and tell the user to run `/research-for-blog-post` first.
3. **Hub-and-spoke linking is mandatory.** Every blog post must link to its parent hub service page AND at least one location page.
4. **Never compromise readability for keyword density.** Natural language always wins. If a keyword cannot be inserted without awkwardness, skip it.
5. **Substring awareness is critical.** Every compound keyword also increments all its parent keyword counts.
6. **Python verification is mandatory.** Never rely on internal counting. Always run the Python scripts to verify compliance.
7. **Proper nouns are always capitalized** regardless of how they appear in NeuronWriter data. Product names: Opti-Coat Pro, TEC582, GeoShield. Tier names: Bronze, Silver, Gold, Mini, Complete.
8. **User interaction points:** This skill has THREE mandatory interaction points: word count approval (Step 2.4), hub/location page confirmation (Step 2.5), and upload decision (Step 7.3). Do NOT skip these.
9. **Never use em-dashes or en-dashes** anywhere in the content. Replace with commas, colons, or rephrase.
10. **Mobile-first identity.** Every blog post must mention that Smith Bros is a mobile service that comes to the customer. This is a core differentiator.
11. **Phone number (760) 310-1532 is mandatory.** Must appear in the article body at least once (in the CTA section at minimum), plus in the metadata block meta descriptions.
12. **Pricing transparency.** When discussing any Smith Bros service, include "Starting at $X for sedans" or equivalent pricing context. Customers comparison-shop, and price transparency builds trust.
13. **No competitor names ever.** Never mention Blueberry, Dennis Details, Fresh Layer, or any competitor by name. Differentiate through Smith Bros' own strengths.
14. **No ChatGPT slop.** No filler phrases, no empty superlatives, no generic conclusions. Every sentence must carry information.
15. **Dual audience rule.** Blog posts should serve both everyday vehicle owners (clear explanations, pricing transparency, convenience) and car enthusiasts (technical product details, protection specs, brand names). If the article leans too heavily toward one audience, rebalance.
16. **Semantic triples are a writing technique, not a compliance metric.** Use Entity + Relationship + Value structure in section openers, the opening paragraph, meta descriptions, and FAQ answers. Never override keyword compliance, word count, or Content Brain rules for triple structure.
17. **AI buzzwords are banned.** Every word, phrase, and structural pattern listed in `Content brain/ai-buzzwords.md` must be avoided. The buzzword compliance check in Phase 6.5 catches violations, but aim to avoid them during writing.
18. **Warranty specificity.** Window tinting = lifetime warranty. Ceramic coating = 3-year or 5-year depending on tier. Never generalize warranties.
19. **Location pages are linking targets.** SB blog posts should link to relevant location pages from `internal_urls.csv` to strengthen the local hub-and-spoke structure across service areas.
20. **Trust signals are mandatory.** Every blog post must include at least one trust signal from the approved list. Rotate them across posts to avoid repetition.
