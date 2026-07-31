---
name: abs-draft-blog-post
description: End-to-end ABS Commercial Cleaning blog post drafting pipeline. Fetches NeuronWriter requirements and SERP/PAA data, uses a pre-generated research report, creates a content brief, selects hub-and-spoke internal links, writes a full SEO-optimized blog post in ABS's confident, caring commercial-cleaning voice per Content Brain, runs keyword and terminology compliance, and optionally uploads to NeuronWriter. Use this skill whenever the user wants to draft an ABS blog post, write a blog from research for a keyword, create an ABS Commercial Cleaning article, or generate a blog post from a NeuronWriter query. Also triggers for "draft ABS blog post", "write ABS blog for [keyword]", "create ABS article for [keyword]", "generate ABS blog post from NeuronWriter query", or "abs blog post".
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebFetch, AskUserQuestion, TaskCreate, TaskUpdate
---

# ABS Commercial Cleaning Blog Post Drafting

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

For ABS blog topics, the research report may include facility-type compliance data (healthcare OSHA standards, school safety protocols, church event flexibility), local Texas market information, and industry-specific cleaning standards. Extract these specifically as they inform compliance sections and local SEO angles.

---

## Phase 2: Pre-Analysis & Word Count

### Step 2.1 -- Read Content Brain

Read `Content brain/contentbrain.md` in full. This is the #1 authority on voice and positioning. For blog posts specifically, internalize:
- **Voice:** "We/you" -- first person plural for ABS, second person for the reader. Never "I" or third person in body copy.
- **Tone hierarchy:** Confident > Direct > Approachable > Caring > Professional > Solution-focused
- **Active voice:** 90%+ target
- **Sentence lengths:** Hero sentences 8-15 words, body 15-25 words, max 30 words
- **All forbidden terms** (Content Brain Sections 5 and 8)
- **Hub-and-spoke model:** Hubs are main service pages (/services/) and location pages; spokes are service+location pages, facility-type pages (/facilities/), blog posts
- **FAQ:** 4-6 pairs for blog posts (Content Brain says minimum 4 for service/facility pages, max 4 sentences per answer)
- **Internal links:** Minimum 3 per page, descriptive anchor text
- **Trust signals:** Minimum 1 per content piece, rotate from Section 7 proof points
- **Phone number:** (800) 640-9446 must appear in every piece
- **No pricing specifics** -- use "customized plan" or "flexible pricing based on your facility's needs"
- **Care-first messaging** -- employee care flows to service quality. This is ABS's core differentiator.
- **Max 1 exclamation mark per page** (CTAs only)
- **Contractions OK** (don't, we're, you'll) -- keeps tone approachable

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

From `{keyword}-requirements.json`, read the `competitors` array. Take top 5 by rank. Filter: only include competitors with `word_count` between 500 and 5000. Calculate the average, round to nearest 50. Apply a minimum floor of 1000 words (commercial cleaning blogs need depth to rank but trend shorter than B2B technical content).

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

### Step 2.5 -- Auto-Detect Hub Service Page, Facility Page, and Location

Analyze the blog keyword and map it to a parent hub service page AND optionally a facility-type page from `internal_urls.csv`.

**Hub service page detection:**
1. Extract the core service topic from the keyword (e.g., "commercial carpet cleaning tips" -> "carpet cleaning", "office cleaning checklist Houston" -> "office cleaning", "VCT floor maintenance best practices" -> "floor stripping and waxing")
2. Match against `/services/` URLs in `internal_urls.csv`:
   - "commercial cleaning" / "janitorial" / "office cleaning" / "office" -> office cleaning pages (e.g., `/services/office-cleaning-austin/`)
   - "floor" / "VCT" / "stripping" / "waxing" / "floor maintenance" -> floor stripping and waxing pages (e.g., `/services/houston-floor-stripping-and-waxing/`)
   - "carpet" / "extraction" / "carpet cleaning" -> carpet cleaning pages (e.g., `/services/commercial-carpet-cleaning-austin/`)
   - "window" / "glass" / "window cleaning" -> window cleaning pages (e.g., `/services/window-cleaning-austin/`)
   - "porter" / "day porter" -> day porter service page (`/services/day-porter-services/`)
   - "post-construction" / "construction cleanup" -> post-construction cleanup pages (e.g., `/services/post-construction-cleanup-austin/`)
   - "pressure washing" / "power washing" -> pressure washing pages (e.g., `/services/pressure-washing-austin/`)
   - "disinfect" / "electrostatic" / "sanitiz" -> disinfection page (`/services/disinfection-and-electrostatic-spraying/`)
   - "restroom" / "bathroom" -> restroom page (`/services/restroom-cleaning-and-sanitation/`)
3. Present the detected hub to the user for confirmation

**Facility-type page detection:**
1. If the keyword references a facility type, also identify the matching `/facilities/` page:
   - "church" / "religious" / "worship" -> `/facilities/church-and-religious-facility-cleaning/`
   - "school" / "charter" / "education" / "classroom" -> `/facilities/school-and-charter-school-cleaning/`
   - "medical" / "clinic" / "healthcare" / "doctor" / "dental" -> `/facilities/medical-office-and-clinic-cleaning/`
   - "warehouse" / "industrial" / "manufacturing" / "factory" (note: "factory" is fine as a facility descriptor, just not for ABS) -> `/facilities/industrial-and-warehouse-cleaning/`
   - "gym" / "fitness" / "fitness center" -> `/facilities/gym-and-fitness-center-cleaning/`
   - "daycare" / "childcare" / "preschool" -> `/facilities/daycare-and-childcare-cleaning/`
   - "retail" / "store" / "shop" -> `/facilities/retail-store-cleaning/`
   - "restaurant" / "food service" / "kitchen" / "dining" -> `/facilities/restaurant-and-food-service-cleaning/`
2. Present detected facility page to user for confirmation

**Location detection:**
1. If the keyword contains a city name, match against location-specific service URLs in `internal_urls.csv`:
   - "Austin" -> URLs ending in `-austin/`
   - "Houston" -> URLs containing `houston-`
   - "San Antonio" -> URLs containing `san-antonio-`
   - "Dallas" -> URLs containing `dallas-` (note: limited URLs currently available)
   - "Fort Worth" -> URLs containing `fort-worth-` (note: limited URLs currently available)
2. Select the location-specific version of the matching service page if it exists
3. If no city in the keyword, suggest the Austin version (HQ market) as default
4. If the keyword mentions a city for which no location-specific URL exists (e.g., Dallas, Fort Worth), note this and suggest the user add one later. Fall back to the non-location service URL or the closest available.

If no hub can be auto-detected, ask the user to specify which service page(s) this blog supports.

### Step 2.6 -- Terminology Pre-Check

Scan NeuronWriter `content_basic_w_ranges` and `content_extended_w_ranges` for any keywords that violate Content Brain forbidden terms. Build a skip-list of keywords that must NOT be used regardless of NeuronWriter targets:

- Any keyword containing "maid" or "maid service"
- Any keyword containing "cheap" or "cheapest"
- Any keyword containing "discount" or "budget"
- Any keyword containing "residential" or "house cleaning" or "home cleaning"
- Any keyword containing "diy"
- Any keyword containing "janitor" as a job title (the word may appear in search queries -- skip it as a keyword target)
- Any keyword matching a competitor name

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

**These words and phrases are BANNED from the content you write.** If you catch yourself reaching for any of them, replace with specific, concrete language relevant to the actual facility type, service, cleaning process, or Texas market being described.

Also watch for commercial-cleaning-specific AI slop:
- "Sparkling clean"
- "Leave your space spotless"
- "Crystal clear results"
- "A clean space is a productive space"
- "Clean is more than a look, it's a feeling"
- "We take pride in every detail"

---

## Phase 3: Content Brief Creation

Generate a structured content brief using the research report and NeuronWriter data.

**System message:** You are an expert local SEO content strategist creating a content brief for a blog post on the ABS Commercial Cleaning website (abscleaning.com). The audience is facility managers and business owners in Texas metro markets (Austin, Houston, San Antonio, Dallas, Fort Worth) who are researching commercial cleaning services, janitorial solutions, floor maintenance, or facility care. Write for a mix of facility managers who know the industry and business owners who need plain-language explanations.

**Brief creation instructions:**

1. Use info, data, facts, and stats from the research report sections B, C, and D to populate the brief. Make it fact-rich but concise.
2. Structure the brief with H1, H2, and H3 headings. The total number of subheadings should align with competitor heading counts from the requirements JSON.
3. Use majority of keywords from `h2_terms` (where `usage_pc` >= 40) in subheadings. Write subheadings in Title Case for H1-H2, Sentence case acceptable for H3+. Use question format where appropriate per Content Brain rules ("How Often Should Your Office Be Deep Cleaned?", "Is Green Cleaning Worth the Investment?").
4. Under each subheading, insert 2-6 SHORT bullet points with data. Use tables for service comparisons and facility-type breakdowns per Content Brain formatting rules.
5. Use figures and facts ONLY from the research report. Link to authoritative sources (ISSA, BSCAI, OSHA, CDC, EPA, GBAC, ARCSI, CleanLink, Facility Executive, .edu, .gov). Avoid linking to competitor cleaning businesses. Do NOT mention sources in the form [Article X].
6. Create but do NOT fill: `## FAQ: [Topic Name]`
7. Include a bullet point noting where the hub service page link AND the facility-type page link should appear (from Step 2.5).
8. Include a bullet point noting where the ABS CTA section should go. The CTA connects the blog topic to ABS's services naturally, includes phone number (800) 640-9446, and uses approved CTA language ("Get a Free Quote," "Request a Quote," "Call (800) 640-9446," "Let's Talk," "Schedule Your Service Today!"). Not a hard sell.
9. If the topic relates to a specific Texas city/metro, include a section with local context (city-specific industries, local business districts, facility types common in that market -- e.g., Austin tech campuses and state government offices, Houston medical center and energy sector offices, San Antonio military-adjacent and tourism/hospitality facilities, Dallas/Fort Worth corporate parks and logistics corridors).
10. No pricing specifics -- ABS uses customized pricing. Note where to say "customized plan based on your facility's size, schedule, and needs" or "flexible pricing." Never quote specific dollar amounts unless verified with the client.
11. Include a bullet point noting where a trust signal block should go. Rotate from: 20+ years of combined experience, 500+ facilities cleaned daily, 5 major Texas markets, 100+ Google reviews/4.9-star average, 1,000+ customers served, less than 1-hour average response time, A+ BBB rating, 10,000+ projects completed, licensed/bonded/fully insured.
12. If the topic relates to a specific facility type (healthcare, churches, schools, industrial), include a note about compliance context: healthcare = OSHA/infection control standards/EPA-registered disinfectants, schools = child safety/after-hours scheduling, churches = event-driven flexibility/multi-use space cleaning, industrial = OSHA workplace standards/floor safety, daycare = child-safe products/sanitization protocols.
13. Always output in markdown.

---

## Phase 4: Internal Link Selection (Hub-and-Spoke)

Read `internal_urls.csv` and select internal links following the Content Brain blog linking pattern.

**Mandatory links:**
1. **Parent hub service page** (identified in Step 2.5). This is non-negotiable for hub-and-spoke.
2. **At least 1 facility-type page** from `internal_urls.csv` if the topic relates to a specific facility type or if a relevant facility page exists. This strengthens hub-and-spoke architecture.
3. At least 1 related service page or location-specific service page from `internal_urls.csv`

**Additional links (select 2-5 more, for a total of 5-8):**
- Related service pages (e.g., if the blog is about floor maintenance, link to carpet cleaning, office cleaning)
- Relevant facility-type pages (e.g., if the blog discusses healthcare cleaning compliance, link to medical office page AND school cleaning page for cross-linking)
- Location-specific versions of the same service for other cities mentioned in content
- Related blog posts (once `blog_posts.csv` has entries)

**Link rules (from Content Brain):**
- Links go in body text paragraphs only, never in headings
- Descriptive anchor text (not "click here" or "learn more")
- ~60% keyword-rich anchors, ~40% natural/generic
- Distribute throughout the article, not clustered in one section
- All real URLs from `internal_urls.csv`. No placeholder anchors.

---

## Phase 5: Full Article Writing

Read `Content brain/contentbrain.md` before writing. Use the content brief, internal links, PAA questions, and keyword data to write the article.

**System message:** You are an expert local SEO copywriter specializing in commercial cleaning and facility maintenance content. You write for facility managers and business owners across Texas metro markets. Your tone is confident, direct, and caring, like a trusted cleaning partner who genuinely invests in their people and your facility's success. You are writing a blog post for ABS Commercial Cleaning's website (abscleaning.com).

### Rule 1: Voice and Person (Blog-Specific)

Use first-person plural ("we/our") when referring to ABS ("We assign dedicated crews to every facility" / "Our team members are background-checked and professionally trained"). Use second-person ("you/your") when addressing the reader ("Your facility deserves consistent, reliable cleaning"). On location-specific blogs, lead with the location name, then transition to "we" voice. Never use "they" when talking about ABS. Never use "I" or first person singular. Never use third person in body copy (save for meta descriptions and schema only).

### Rule 2: Tone Hierarchy (Ranked, from Content Brain)

1. **Confident.** Let metrics speak. "We clean 500+ Texas facilities daily." No boasting without proof.
2. **Direct.** Short, clear sentences. Get to the point. No hedging or filler. "We strive to provide" becomes "We provide."
3. **Approachable.** Use contractions (don't, we're, you'll). Conversational rhythm. Not corporate-speak or stiff.
4. **Caring.** Emphasize employee care, client relationships, responsiveness. "We pay above-average wages because better-paid teams deliver better results." Not sappy or emotional.
5. **Professional.** Proper grammar. Cite credentials and metrics. No slang, humor, or exclamation-heavy copy.
6. **Solution-focused.** Frame everything as solving the client's problem. Don't dwell on problems without presenting the solution.

### Rule 3: Article Structure

- **H1:** Include primary keyword, Title Case. For location-targeted posts, use "[Service/Topic] in [City], TX" format.
- **Introduction:** Write 2 versions (one below another), 60-80 words each. Open with a relatable facility manager scenario, specific stat, or local Texas context that hooks the reader. Break into 2 paragraphs each. First-person plural voice. **Must mention ABS's care-first differentiator or employee investment within the intro.** Must include at least one trust signal (20+ years, 500+ facilities, etc.).
- **Key Takeaways:** Immediately after the introduction, include a section titled "Key Takeaways". List 4-6 ULTRA SHORT bullet points. One short sentence per line. No links or bolds. Each bullet is a standalone fact an AI could extract: [Subject] [verb] [specific claim].
- **No horizontal rules:** Do NOT insert horizontal rules (`---`, `***`, or `___`) anywhere in the article. Sections are separated by headings only.
- **Body:** Develop the main content from the brief. Use tables for service comparisons, facility-type breakdowns. Use bullet points for "What's Included" lists, tips, and scannable information. Incorporate NLP keywords naturally. **No pricing specifics** -- use "customized plan" language. Use the technical term + benefit in plain language pattern for dual audience (facility managers who know the industry + business owners who don't).
- **ABS CTA Section:** One H2 section (naturally integrated, not a separate sales pitch) that connects the blog topic to ABS's services. **Must include phone number (800) 640-9446.** Use CTA language from Content Brain: "Get a Free Quote," "Request a Quote," "Schedule Your Service Today!," "Let's Talk," "Call (800) 640-9446." Do NOT make this a hard sell. It should read as "if you need this service for your facility, here's how we can help."
- **FAQ Section:** Title: "Frequently Asked Questions About [Topic]" in Title Case. Use 4-6 pairs from PAA questions (Step 2.3). Each question is an H3 heading (`###`). The answer is a normal paragraph (no bold, no special formatting). Start each answer with the subject entity or a direct factual statement (not "Yes," "No," "Great question!" or filler). **Max 4 sentences per answer.** Direct answer first, then supporting detail. Skip off-topic PAA questions.

### Rule 4: Formatting Rules (from Content Brain)

- Title Case for H1 and H2 headings. Sentence case acceptable for H3 and below.
- Oxford comma always
- No em dashes or en dashes anywhere (use comma, colon, or period instead)
- Bold for key differentiators, credentials, and critical metrics on first mention only. Use sparingly in body paragraphs. Not for entire sentences.
- Tables for service comparisons, facility-type breakdowns, and structured data
- Short paragraphs (2-4 sentences max)
- Numbers: spell out one through nine. Use numerals for 10+. Always use numerals for metrics (20+ years, 500+ facilities).
- Phone number always formatted as (800) 640-9446. Never 800-640-9446 or 8006409446.
- Ampersands: use "&" in headings and taglines, "and" in body copy
- Max 1 exclamation mark per page (reserve for CTA only)
- Introduce acronyms with full form + acronym in parentheses on first mention: "vinyl composite tile (VCT)." After first use, acronym only.

### Rule 5: Keyword Integration -- STRICT Range Enforcement

Treat `content_basic_w_ranges` ranges as hard limits.

**CRITICAL -- Substring Awareness:** Keywords share substrings. For example:
- "commercial carpet cleaning austin" increments counts for "commercial carpet cleaning", "carpet cleaning", "cleaning", AND "carpet cleaning austin"
- "office cleaning services" contains both "office cleaning" and "cleaning services"

When adding a compound keyword, mentally increment ALL parent substring keywords and check they remain in range.

Rules:
- **NEVER exceed the upper bound of any range.** This is a hard constraint.
- Target the middle of each range for a natural distribution.
- Track compound keywords carefully.
- Skip keywords on the terminology skip-list (from Step 2.6).
- Target 60%+ of `content_extended_w_ranges` keywords present.
- Never bold keywords in body text.
- Capitalize proper nouns correctly regardless of how NeuronWriter lists them.

### Rule 6: Internal Links

Insert the 5-8 internal links selected in Phase 4.

- Links go in body text paragraphs only. **Never in headings.**
- The parent hub service page link is mandatory and should appear in the first third of the article if possible.
- A facility-type page link should appear if the topic has facility-specific relevance.
- Descriptive anchor text, 1-4 words. ~60% keyword-rich, ~40% natural.
- Distribute naturally throughout, not clustered.

### Rule 7: Facts and Source Links

Use authoritative source links from the research report and content brief. Keep anchor text 1-4 words, descriptive. Link naturally within sentences. Avoid linking to competitor cleaning businesses. Prefer industry-authoritative sources: ISSA, BSCAI, OSHA, CDC, EPA, GBAC, ARCSI, CleanLink, Facility Executive, .edu, .gov. No naked URLs.

### Rule 8: Terminology Compliance (from Content Brain)

Never use any term from the Content Brain "Never Use" list. This includes but is not limited to:
- "Maid" or "maid service" in any form (residential connotation)
- "Cheap," "cheapest," "discount," "budget" (undermines positioning)
- "Janitor," "cleaner" as job titles (use "team member," "cleaning professional," "crew")
- "Customer" (use "client")
- "Contract" (use "plan," "agreement," "service agreement")
- "Workers," "employees" (use "team members," "professionals," "crews")
- "Residential," "home cleaning," "house cleaning" (commercial only)
- "Best in Texas," "best commercial cleaning" (unsubstantiated superlative)
- "State-of-the-art," "world-class," "cutting-edge," "synergy" (vague/overused)
- "Guarantee results" or "guaranteed ROI" (legal risk)
- "Touch base" (corporate jargon)
- "I" in brand content (use "we")
- Em dashes and en dashes
- Any competitor name
- "Sign up now," "Buy now," "Don't miss out," "Limited time offer," "Act now," "Click here" (banned CTAs)

Use the "Always Use" replacements from Content Brain Section 5.

Never use ChatGPT slop phrases:
- "In today's fast-paced world..."
- "It's important to note that..."
- "When it comes to [topic]..."
- "In the realm of..."
- "Are you looking for..."
- "Look no further!"
- "Let's dive in"
- "Without further ado"
- "In conclusion" (as a section header)
- "It goes without saying"
- "Needless to say"
- "At the forefront of"
- "Navigating the landscape of"
- "Leveraging our expertise"
- "A holistic approach"
- "Unlock the potential"
- "Elevate your experience"
- "Embark on a journey"
- "Delve into"
- "Tapestry of"
- "Bustling"
- "Comprehensive suite of solutions"
- "Seamless" (unless describing an actual integration)
- "Robust" (unless describing a physical object)
- "Pivotal"
- "At the end of the day"
- "Game-changer"
- Any sentence that could be removed without losing information

Cleaning-specific AI slop -- also banned:
- "Sparkling clean"
- "Leave your space spotless"
- "Crystal clear results"
- "A clean space is a productive space"
- "Clean is more than a look, it's a feeling"
- "We take pride in every detail"

### Rule 9: Human-Like Writing

- **High perplexity:** Vary word choices, avoid predictable phrases. Do not default to the same adjectives, transitions, or sentence openers repeatedly.
- **Burstiness:** Mix short punchy sentences (8-12 words) with medium ones (15-25 words). Rarely exceed 30 words. Vary paragraph lengths, but NEVER write a paragraph longer than 300 characters.
- **Varied sentence openers:** Never start three or more sentences in a row with the same word or pattern. Restructure to lead with the benefit, the service, the facility type, or the outcome.
- **No robotic phrasing:** No overly formal constructions, unnecessary hedging, or AI filler. If a phrase sounds like it could appear in any AI-generated article on any topic, replace it with something specific to the actual facility type, cleaning service, compliance context, or Texas market being described. Reference specific services (VCT floor maintenance, carpet extraction, day porter), specific facility types (medical office, church, warehouse), specific Texas cities (Austin, Houston, San Antonio, Dallas, Fort Worth), or specific compliance contexts (OSHA, EPA, infection control).
- **Full buzzword avoidance list:** Refer to `Content brain/ai-buzzwords.md` (read in Step 2.9). Any word or phrase listed there is banned from the content.

### Rule 10: Semantic Triple Structure in Key Positions

Structure key informational sentences as semantic triples: [Subject Entity] + [relationship verb] + [specific value/object].

Apply in these specific positions only:
- **First sentence of each H2 section:** Open with the topic entity as the subject, followed by an action verb and a specific value. Example: "Professional commercial cleaning reduces workplace illness by up to 46% according to ISSA research." NOT: "In today's world, keeping your facility clean is more important than ever."
- **FAQ answers:** Start each answer with the subject entity. Example: "VCT floor maintenance extends the life of vinyl tile by 5 to 10 years with regular stripping and waxing." NOT: "Great question! There are many factors that determine..."
- **Key Takeaways bullets:** Each bullet reads as a standalone fact.
- **Opening paragraph:** First sentence should be a complete semantic triple.

Do NOT force triples into storytelling sections or conversational paragraphs. Readability and the Content Brain voice take priority.

### Rule 11: Conditional Sections

**If the topic relates to a specific Texas city/metro:** Include a section with local context. Mention the city's key industries, business districts, facility density, and why local businesses in that market benefit from the service. Austin = tech campuses, state government offices, university-adjacent facilities, The Domain and downtown office corridors. Houston = Texas Medical Center, energy sector offices, industrial parks along the Ship Channel. San Antonio = military-adjacent (Fort Sam Houston, Lackland), tourism/hospitality near the Riverwalk, healthcare facilities. Dallas/Fort Worth = corporate parks, logistics/warehouse corridors near DFW airport, financial district offices. This should feel genuinely local, not template-swapped.

**If the topic relates to a specific facility type:** Include a compliance/context section. Healthcare = OSHA standards, infection control protocols, EPA-registered disinfectants, HIPAA-aware cleaning (access to patient areas). Schools = child safety standards, LEED considerations, after-hours scheduling requirements. Churches = event-driven flexibility, multi-use space cleaning (sanctuaries, fellowship halls, classrooms), weekend scheduling. Industrial/warehouse = OSHA workplace standards, floor safety (slip resistance), equipment-safe cleaning. Daycare = child-safe products, sanitization protocols, health department compliance. Gym/fitness = sanitization frequency, equipment cleaning, locker room hygiene.

**If the topic relates to pricing or cost:** Never quote specific dollar amounts unless verified with the client. Use "customized plan based on your facility's size, schedule, and needs." Mention "flexible pricing" and "satisfaction guarantee." If comparison context is needed, frame as value: "A customized cleaning plan costs less than the productivity lost to an unhealthy work environment."

### Rule 12: Readability and Language

- Target 8th-10th grade reading level (Flesch-Kincaid). The audience ranges from facility managers to business owners who are not cleaning industry experts.
- Active voice 90%+ of sentences. Passive voice acceptable only for process descriptions ("Your floors are stripped and recoated using commercial-grade equipment").
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
pct = round(present/len(extended)*100) if extended else 0
print(f'\nExtended keywords: {present}/{len(extended)} ({pct}%)')
if pct < 60:
    print(f'  BELOW MINIMUM — must include at least 60% of extended keywords ({len(extended) * 60 // 100} of {len(extended)})')
else:
    print('  Extended keyword coverage OK (>=60%)')
```

**Extended keyword coverage below 60% is a compliance failure** and must be fixed before proceeding, just like basic keyword range violations.

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
    (r'\bmaid\b', 'maid (Content Brain - residential connotation)'),
    (r'\bmaid service\b', 'maid service (Content Brain - residential)'),
    (r'\bcheap(?:est)?\b', 'cheap/cheapest (Content Brain terminology)'),
    (r'\bdiscount\b', 'discount (Content Brain terminology)'),
    (r'\bbudget\b', 'budget (Content Brain terminology)'),
    (r'\bjanitor\b', 'janitor (use "team member" or "cleaning professional")'),
    (r'\bcleaner\b(?!\s+(?:air|water|environment|product|solution|facility|space))', 'cleaner as job title (use "team member")'),
    (r'\bcustomer\b', 'customer (use "client")'),
    (r'\bcontract\b(?!\s+(?:clean|work|or))', 'contract (use "plan" or "agreement")'),
    (r'\b(?:workers?|employees?)\b', 'workers/employees (use "team members")'),
    (r'\bresidential\b', 'residential (commercial only)'),
    (r'\bhome cleaning\b', 'home cleaning (commercial only)'),
    (r'\bhouse cleaning\b', 'house cleaning (commercial only)'),
    (r'\bbest in texas\b', 'best in Texas (unsubstantiated)'),
    (r'\bbest commercial cleaning\b', 'best commercial cleaning (unsubstantiated)'),
    (r'\bstate[\s-]of[\s-]the[\s-]art\b', 'state-of-the-art (Content Brain ban)'),
    (r'\bworld[\s-]class\b', 'world-class (Content Brain ban)'),
    (r'\bcutting[\s-]edge\b', 'cutting-edge (Content Brain ban)'),
    (r'\bsynerg\w*\b', 'synergy (Content Brain ban)'),
    (r'\btouch base\b', 'touch base (Content Brain ban)'),
    (r'\bgame[\s-]changer\b', 'game-changer (Content Brain ban)'),
    (r'\bguarantee(?:d)? (?:results?|roi)\b', 'guarantee results/ROI (legal risk)'),
    (r'\u2014', 'em dash (use comma, colon, or period)'),
    (r'\u2013', 'en dash (use comma, colon, or period)'),
    (r'\bbuy now\b', 'banned CTA'),
    (r'\bsign up\b', 'banned CTA'),
    (r"don'?t miss out", 'banned CTA'),
    (r'act now', 'banned CTA'),
    (r'limited time offer', 'banned CTA'),
    (r'\bclick here\b', 'banned CTA'),
    # ChatGPT slop
    (r"in today'?s (?:fast|competitive|ever)", 'ChatGPT slop phrase'),
    (r"it'?s important to note", 'ChatGPT slop phrase'),
    (r'when it comes to', 'ChatGPT slop phrase'),
    (r'in the ever[\s-]evolving', 'ChatGPT slop phrase'),
    (r"let'?s dive in", 'ChatGPT slop phrase'),
    (r'at the end of the day', 'ChatGPT slop phrase'),
    (r'navigating the (?:complexities|landscape)', 'ChatGPT slop phrase'),
    (r'look no further', 'ChatGPT slop phrase'),
    (r'in the realm of', 'ChatGPT slop phrase'),
    (r'elevate your', 'ChatGPT slop phrase'),
    (r'embark on a journey', 'ChatGPT slop phrase'),
    (r'rest assured', 'ChatGPT slop phrase'),
    (r'a testament to', 'ChatGPT slop phrase'),
    (r'\bboasts\b', 'ChatGPT slop phrase'),
    (r'\bpivotal\b', 'ChatGPT slop phrase'),
    (r'\bmyriad\b', 'ChatGPT slop phrase'),
    (r'\bplethora\b', 'ChatGPT slop phrase'),
    (r'\bparamount\b', 'ChatGPT slop phrase'),
    (r'\bmeticulous\b', 'ChatGPT slop phrase'),
    (r'\brobust\b', 'ChatGPT slop phrase'),
    (r'\bdelve\b', 'ChatGPT slop phrase'),
    (r'\bseamless\b', 'ChatGPT slop phrase'),
    (r'\bleverage\b', 'ChatGPT slop phrase'),
    (r'\brevolutionize\b', 'ChatGPT slop phrase'),
    (r'\bholistic\b', 'ChatGPT slop phrase'),
    (r'\bbustling\b', 'ChatGPT slop phrase'),
    # Cleaning-specific AI slop
    (r'sparkling clean', 'cleaning AI slop'),
    (r'leave your space spotless', 'cleaning AI slop'),
    (r'crystal clear results', 'cleaning AI slop'),
    (r'clean space is a productive', 'cleaning AI slop'),
    (r"clean is more than a look", 'cleaning AI slop'),
    (r'we take pride in every detail', 'cleaning AI slop'),
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

1. **If ALL basic keywords in range AND extended keyword coverage >= 60% AND no terminology violations:** Proceed to Phase 7.
2. **If issues exist:** Fix them using targeted `Edit` calls on the file:
   - For STUFFED keywords: replace excess occurrences with synonyms, pronouns, or rephrase
   - For MISSING keywords: insert naturally into existing sentences
   - For extended keywords below 60%: identify which extended keywords are missing and weave them into existing sentences or add new supporting sentences
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
    # Cleaning-specific AI slop
    'sparkling clean',
    'leave your space spotless',
    'crystal clear results',
    'a clean space is a productive space',
    'clean is more than a look',
    'we take pride in every detail',
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

**Meta Description Option 1:** [<=155 chars, benefit + primary keyword + trust signal. End with: Call (800) 640-9446.]
**Meta Description Option 2:** [<=155 chars, different angle. End with: Call (800) 640-9446.]
```

Do NOT include client name, client URL, hub service page, facility page, location page, internal/external link lists, target keywords, word counts, target audience, or goal in this block. Those details are reported in the Phase 8 summary instead.

**SEO Title rules:**
- 3 options, each <=60 characters
- Format: `[Primary Keyword] [City] ([Reader Benefit])`
- End each title with a parenthetical reader benefit that tells the searcher what they will gain from clicking (e.g., "(Tips & Checklist)", "(What Managers Need to Know)", "(Full Guide)", "(Costs & Options)", "(Save Time & Money)", "(Compliance Guide)")
- Do NOT append the business name ("| ABS Commercial Cleaning") to blog post SEO titles
- Include city name for location-targeted posts
- Primary keyword near the beginning

**Meta Description rules:**
- 2 options, each <=155 characters
- Lead with benefit or topic entity + primary keyword + clear value proposition
- Include a trust signal
- **Must end with phone number:** "Call (800) 640-9446."

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
QUERY ID,KEYWORD,BLOG URL SLUG,HUB SERVICE PAGE,FACILITY PAGE,LOCATION PAGE,DATE,CONTENT SCORE,WORD COUNT,TARGET WORD COUNT,RESEARCH REPORT FILE
```

Use Python via Bash to handle the CSV:

```python
import csv
import os
from datetime import date

csv_file = 'blog_posts.csv'
headers = ['QUERY ID', 'KEYWORD', 'BLOG URL SLUG', 'HUB SERVICE PAGE', 'FACILITY PAGE', 'LOCATION PAGE',
           'DATE', 'CONTENT SCORE', 'WORD COUNT', 'TARGET WORD COUNT',
           'RESEARCH REPORT FILE']

new_row = {
    'QUERY ID': '{query_id}',
    'KEYWORD': '{keyword}',
    'BLOG URL SLUG': '/blog/{keyword-slugified}/',
    'HUB SERVICE PAGE': '{hub_service_page_url}',
    'FACILITY PAGE': '{facility_page_url}',
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
- Client Name: ABS Commercial Cleaning, LLC
- Client URL: https://www.abscleaning.com
- Hub Service Page: [URL of the parent hub service page from Step 2.5]
- Facility Page: [URL of the facility-type page from Step 2.5, if applicable]
- Location Page: [URL of the location-specific page, if applicable]
- Internal Links: [List naked URLs of ABS links used in the article]
- External Links: [List naked URLs of external source links used in the article]
- Target Keyword(s): [Main Keyword from requirements JSON]
- Target Word Count: [Approved target from Phase 2]
- Actual Word Count: [Final word count after compliance loop]
- Target Audience: Facility managers and business owners in [City/Texas] researching [topic area]
- Goal: SEO traffic, hub-and-spoke authority building for [hub service page], local visibility for [location], thought leadership for commercial cleaning

**Performance data:**
- NeuronWriter content score (if uploaded)
- Keyword compliance status (all within range / X issues remaining)
- Extended keyword coverage (X/Y, Z%)
- ContentBrain terminology violations (0 or list remaining)
- Phone number (800) 640-9446 included: Yes/No
- FAQ questions used (count and source: DataForSEO PAA vs NeuronWriter PAA)
- Research report used: [filename]

---

## Important Reminders

1. **Content Brain is the #1 authority.** All voice, positioning, and terminology rules from `Content brain/contentbrain.md` override everything else, including NeuronWriter keyword suggestions.
2. **Research report is mandatory.** If no `research-report-*.md` exists, stop and tell the user to run `/research-for-blog-post` first.
3. **Hub-and-spoke linking is mandatory.** Every blog post must link to its parent hub service page AND at least one facility-type or location page.
4. **Never compromise readability for keyword density.** Natural language always wins. If a keyword cannot be inserted without awkwardness, skip it.
5. **Substring awareness is critical.** Every compound keyword also increments all its parent keyword counts.
6. **Python verification is mandatory.** Never rely on internal counting. Always run the Python scripts to verify compliance.
7. **Proper nouns are always capitalized** regardless of how they appear in NeuronWriter data. City names, "ABS Commercial Cleaning," certification names (OSHA, EPA, ISSA).
8. **User interaction points:** This skill has THREE mandatory interaction points: word count approval (Step 2.4), hub/facility/location page confirmation (Step 2.5), and upload decision (Step 7.3). Do NOT skip these.
9. **Never use em-dashes or en-dashes** anywhere in the content. Replace with commas, colons, or rephrase.
10. **Care-first identity.** Every blog post must mention ABS's care-first approach -- investing in team members leads to better service quality. This is a core differentiator. "We pay above-average wages because better-paid teams deliver better results."
11. **Phone number (800) 640-9446 is mandatory.** Must appear in the article body at least once (in the CTA section at minimum), plus in the metadata block meta descriptions.
12. **No pricing specifics.** Never quote dollar amounts unless verified with the client. Use "customized plan based on your facility's needs," "flexible pricing," or "satisfaction guarantee."
13. **No competitor names ever.** Never mention competitors by name. Differentiate through ABS's own strengths.
14. **No ChatGPT slop.** No filler phrases, no empty superlatives, no generic conclusions. Every sentence must carry information.
15. **Dual audience rule.** Blog posts should serve both facility managers who know the industry (compliance context, process specifics, scheduling logistics) and business owners who don't (plain-language benefits, what to look for in a cleaning partner). If the article leans too heavily toward one audience, rebalance. Use the technical term + benefit in plain language pattern.
16. **Semantic triples are a writing technique, not a compliance metric.** Use Entity + Relationship + Value structure in section openers, the opening paragraph, meta descriptions, and FAQ answers. Never override keyword compliance, word count, or Content Brain rules for triple structure.
17. **AI buzzwords are banned.** Every word, phrase, and structural pattern listed in `Content brain/ai-buzzwords.md` must be avoided. The buzzword compliance check in Phase 6.5 catches violations, but aim to avoid them during writing.
18. **Never position ABS as residential.** Commercial facilities only. No references to homes, apartments, maid service, or residential work.
19. **Facility-type pages are linking targets.** ABS blog posts should link to relevant `/facilities/` pages from `internal_urls.csv` to strengthen the facility-type hub-and-spoke structure.
20. **Trust signals are mandatory.** Every blog post must include at least one trust signal from the approved list in Content Brain Section 7. Rotate them across posts to avoid repetition.
21. **Max 1 exclamation mark per page.** Reserve for CTA only ("Schedule Your Service Today!").
22. **Sanitize vs disinfect.** Use "disinfect" for healthcare and high-compliance contexts. Use "sanitize" for general commercial spaces. They are not interchangeable.
23. **"Guaranteed" only with "satisfaction guarantee."** This is a real ABS policy. Never guarantee specific outcomes, timelines, or cost savings.
