---
name: ha-draft-article
description: End-to-end HostAdvice blog article drafting pipeline. Reads article parameters from Content Management.csv, uses a research report as input, creates a structured content brief, gathers internal links and People Also Ask questions, then writes a full SEO-optimized article matching the HostAdvice writing style. Updates the CSV with the output file path and word count. Use this skill whenever the user wants to draft a HostAdvice blog article, write an AI draft from research, create an article from a content brief, or produce a blog post based on research-report.md. Also triggers for "draft the article", "write the HostAdvice post", "create AI draft for [keyword]", or "generate blog post from research".
allowed-tools: Bash, Read, Write, Edit, WebFetch, Glob, AskUserQuestion, TaskCreate, TaskUpdate, mcp__dfs-mcp__serp_organic_live_advanced
---

# HostAdvice Article Drafting Skill

End-to-end pipeline: CSV input -> content brief -> internal links + PAA -> full article -> save + update CSV.

## Prerequisites

Before running, ensure these files exist in the working directory:

| File | Description | Source |
|---|---|---|
| `Content Management.csv` | Article parameters (title, keyword, word count, NLP keywords, etc.) | User provides |
| `research-report-KEYWORD.md` | Research report from `/research-for-blog-post` skill (keyword in filename) | Run `/research-for-blog-post` first |
| `internal-links.md` | List of existing + future HostAdvice article URLs | User provides |

If no `research-report-*.md` file is found, stop and tell the user to run `/research-for-blog-post` first.

## Step 1 — Read CSV and Select Article

Read `Content Management.csv` from the working directory. Parse the CSV columns:
- **SEO Title** (column 0)
- **Main Keyword** (column 1)
- **Word Count** (column 2)
- **NLP Keywords** (column 3 — newline-separated list)
- **Heading Keywords** (column 4 — newline-separated list)
- **# of headings** (column 5 — range like "17-35")
- **AI Draft Doc** (column 6 — will be updated with output path)
- **AI Draft Words** (column 7 — will be updated with word count)
- **Targ. Market** (column 8)

Show the user a numbered list of available rows (SEO Title + Main Keyword) and ask which article to draft using AskUserQuestion. Skip empty rows.

Extract all fields for the selected row. Convert the NLP Keywords and Heading Keywords from newline-separated text to comma-separated lists.

## Step 2 — Read Research Report

Find the research report file by globbing for `research-report-*.md` in the working directory. If multiple matches exist, ask the user which one to use. Read the selected file and store the full content for use in the brief creation step.

## Step 3 — Capitalize NLP Keywords

Take the NLP Keywords list and fix capitalization: capitalize proper nouns and acronyms (VPS, URL, SEO, UTM, API, etc.) while keeping regular words in lowercase. Do not capitalize every word. Output the fixed keyword list in the same comma-separated formatting.

## Step 4 — Create Content Brief

Generate a structured content brief using the research report. Follow these exact instructions:

---

**System message:** You are an elite-level SEO expert and copywriter capable of producing highly optimized content that ranks on Google's first page. You create engaging, informative, and valuable content that resonates deeply with human readers. Your writing is clear, interesting, and optimized for readability.

**Brief creation instructions:**

Read the reference file for a properly structured content brief example:
```
~/.claude/skills/ha-draft-article/references/brief-example.md
```
(If that file does not exist, use the example embedded below.)

<brief-example>
# H1: LinkedIn Marketing Strategy: The Ultimate Guide for B2B Success

## H2: Understanding the Importance of LinkedIn for B2B Marketing

### H3: The Rise of LinkedIn as a B2B Powerhouse

*   LinkedIn is a premier professional network, specifically designed for business, not just another social platform.
*   **Key Characteristics**:
    *   Connects users with executives, managers, and decision-makers.
    *   Functions as a virtual networking event for brand visibility, partnerships, and brand building.
    *   Platform where deals happen and lead generation thrives.
*   **Statistics**:
    *   62% of B2B marketers identify LinkedIn as their top source for lead generation. [Link](https://business.linkedin.com/marketing-solutions/success/lead-generation).
    *   Leads from LinkedIn convert twice as effectively compared to other social media platforms.
    *   Purchase intent on LinkedIn is 33% higher than average digital platforms.
*   Core Benefit: Builds trust and credibility as professionals use it for learning, industry insights, and business decisions. Essential for B2B.

## H2: 3 Benefits of LinkedIn Marketing for B2B

### H3: 1. Lead Generation Machine
*   Advanced search filters (job title, industry, company size, skills, groups), ability to see profile viewers.

### H3: 2. Boosting Brand Awareness
*   Consistent sharing of interesting content keeps the business visible to the target audience.
*   Builds brand familiarity and trust through repeated exposure and engagement.

### H3: 3. Networking with Industry Leaders
*   Connect with leaders, collaborate with partners, recruit talent.
*   LinkedIn groups for engagement, LinkedIn ads for targeted content delivery.

## H2: Setting Clear Objectives and Identifying Your Target Audience

### H3: Defining Your LinkedIn Marketing Goals

*   Clear goals are necessary to guide marketing efforts and measure progress effectively.
*   Utilize SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound). [Link](this will link to a website article)
*   Specific goal ("Increase qualified leads by 20% in Q3") vs. Vague goal ("Get more leads").
*   **Common Objectives & KPIs**:
    *   Build brand awareness (Track: followers, reach, impressions).
    *   Generate leads (Track: website clicks, form submissions, conversion rates).
    *   Increase engagement (Track: likes, shares, comments).
    *   Establish thought leadership (Action: Share insights, grow credibility).
*   **Alignment**: Ensure LinkedIn goals support broader business objectives and focus on overall growth.

### H3: Understanding Your Ideal B2B Audience on LinkedIn

*   Knowing the audience (needs, challenges) is crucial for an effective strategy.

**Create Buyer Personas**
*   Develop detailed profiles of ideal customers (job title, industry, company size, goals, pain points, content preferences).

**Use LinkedIn Analytics**
*   Provides data on audience demographics, interests, and engagement patterns.
*   Use insights to refine content strategy and marketing techniques.
*   Deep audience understanding allows for resonant content creation and is fundamental to success.

## H2: Final Thoughts

*   LinkedIn is a vital platform for B2B success. A strategic approach is key.

## H2: Next Steps: What Now?

## H2: Frequently Asked Questions About LinkedIn Marketing Strategy
</brief-example>

Using the research report and article parameters, create the content brief following these rules:

1. You work in HostAdvice content production team, they are affiliates for the service being written about. Talk about both pros and cons, but overall tone of the intro and the whole article must be positive.
2. The total number of subheadings MUST be within the range from the "# of headings" field.
3. Use info, data, facts, and stats from the research report to create the article brief. Make it into a fact-rich but also short and concise content brief — like the example above.
4. You have to use majority of keywords from the Heading Keywords list in subheadings. Some keywords may sound odd in subheading — do not use these. ALWAYS write the subheading in Title Case and capitalize acronyms even if keyword phrases are in all lowercase. ALWAYS write interesting and attractive subheadings that will inspire the reader to continue reading.
5. The brief must have all factual data and stats needed to write the article later. Under each subheading insert 2 to 6 SHORT bullet points with data. Make a sublist or table under some bullet points — the article needs to be formatted intelligently to make it visually appealing. You must use a table if you see it in the research report.
6. Use the figures & facts ONLY FROM the "B. Detailed Factual Extraction for..." and "C. Consolidated Key Statistics and Data Points" sections of research to support what you say. Make sure you link to info sources and websites/products you mention, IF the sources are authoritative (.edu, .gov, .org, or well-known research companies or tech media outlets). Avoid linking to non-US info sources. DO NOT mention sources in the form [Article X].
7. Always create but do not fill subheadings: `## H2: Next Steps: What Now?` and `## H2: Frequently Asked Questions About [MAIN_KEYWORD]`.
8. ALWAYS output the text in markdown.

---

## Step 5 — Get Internal Links

Read `internal-links.md` from the working directory. This file should contain two sections:
- **Existing articles**: Published HostAdvice URLs
- **Future articles**: Planned article titles (not yet published)

Analyze the content brief and select 6 highly relevant articles:
- 3 existing articles (with real URLs)
- 3 future articles (with placeholder anchors in format: `(placeholder anchor for link to [Title of Article])`)

The link to `https://hostadvice.com/vps/` (or its subcategory pages) must always be included if present in the list.

## Step 6 — Get People Also Ask Questions

Use the `mcp__dfs-mcp__serp_organic_live_advanced` tool with:
- **keyword**: the main keyword from the CSV
- **location_code**: 2840 (United States)
- **language_code**: "en"
- **device**: "desktop"
- **os**: "windows"
- **depth**: 10
- **people_also_ask_click_depth**: 1

Extract all `people_also_ask_element` items from the response — these are the PAA questions that will become the FAQ section.

## Step 7 — Write the Full Article

This is the core article writing step. Read the writing style sample first:

```
~/.claude/skills/ha-draft-article/references/writing-style-blogstyle1.md
```

Then write the article using ALL gathered inputs. Follow these exact instructions:

---

**System message:** You are an elite-level SEO expert and copywriter capable of producing highly optimized content that ranks on Google's first page. You create engaging, informative, and valuable content that resonates deeply with target audience — People who are interested in VPS and web hosting services. Your writing is clear, accessible, and optimized for readability.

**Article writing instructions:**

You work in HostAdvice content production team, take that into account when writing the content. They are affiliates for this service that you are creating article about. You need to talk about both pros and cons, but overall tone of the intro and the whole article must be positive.

Use the content brief, internal links, writing style sample, capitalized NLP keywords, and PAA questions to write the article.

**Key Requirements:**

1. The article must be valuable to the target audience. Always output the whole article in markdown.

2. **Facts & Figures Source Links:** Make sure you link to info sources as you see in the content brief. DO NOT use any link that is not in the brief. Keep the anchor text 1-4 words long, ensure it is descriptive, link naturally within the sentence. Avoid linking to non-US info sources. Avoid making naked URL links in the article.

3. **Internal links & Anchor Text:** Use the provided HostAdvice internal links in the article text. If you can, distribute the links evenly throughout the article, but this is not a strict requirement. Do not write odd-sounding sentences just to insert the link. Use descriptive anchor text in relation to the topic of target article (but it does not have to match URL), keep the anchor text 1-4 words long. You also must make placeholder anchors for Future Articles that you received. Example sentence with this structure: Check our guide on [hosting n8n in regulated industries](placeholder anchor for link to [Hosting n8n in Regulated Industries (GDPR, HIPAA Considerations)]) for GDPR and HIPAA considerations.

4. **Tone & Style:** Write in an engaging, informative, and helpful tone. Use a style that is approachable and easily understandable. Maintain a conversational feel. Use "bucket brigades" in your writing. DO NOT mention the current year (2026) in the article, except if already mentioned in H1 title in the brief.

5. **Avoid "Fluffy" writing:** Avoid Repetition — Don't say the same thing again and again, it's boring. Avoid fluffy sentences. Avoid filler words.
   Example (with filler words):
   "Actually, I was really so impressed with the incredibly beautiful scenery on our trip. Basically, it was just very picturesque and literally took my breath away."
   Example (revised without filler words):
   "I was impressed with the beautiful scenery on our trip. It was picturesque and took my breath away."

6. **Readability:** Target a readability level suitable for a 8th-grade reader. Use clear language, shorter sentences where appropriate, and explain any potentially complex concepts simply.

7. **Formatting:**
   - Remove H2:, H3:, H4: subheading labels, but always keep the numbering if present. But keep the markdown marking for subheadings (##, ### etc.)
   - Use short sentences and paragraphs (typically 2-4 sentences).
   - Avoid walls of text.
   - Use a table if present in the brief.
   - Use bullet points where they make sense.
   - Ensure smooth transitions between paragraphs and sections.

8. **Article Structure:**
   - **Introduction:** Write 3 versions (one below another) of creative and engaging 50-word introduction under h1, that hooks the reader and clearly states what the article will cover. Avoid copying the intro from the writing style sample. Always break them in two paragraphs.
   - **Key Takeaways:** Immediately after the introduction, include a section titled "Key Takeaways". List 5-7 ULTRA SHORT bullet points summarizing the most crucial information in the article. It should be short, straight to the point, and only one short sentence per line. No links or bolds in the Key Takeaways section.
   - **Body:** Develop the main content based on the provided outline, expanding on each point. DO NOT delete the part about web hosting and the link.
   - **Conclusion (always make an h2 for it):** Make a concise (60 words) conclusion that summarizes the main points briefly and offers a final thought or call to action (if appropriate based on the outline). Do not introduce new information here.
   - **"Next Steps: What Now?":** Always write logical next steps for the reader (4-7 steps formatted as bullet list — sentences must have dot at the end, up to 80 words total).
   - **Frequently Asked Questions About [MAIN_KEYWORD]:** This is the very last section. The whole h2 subheading should be in Title case. Each question must be bolded and have a line break after it, then write the answer. Avoid using Q: and A: markings. Write VERY SHORT answers to the PAA questions gathered in Step 6.

9. **Voice:** Mimic the voice and style from the sample writing style text.

10. **What is "X" definition:** Clearly define terms by starting the definition with "X is a..".
    Example of a good definition of a Bank:
    "A bank is a financial institution that accepts deposits from the public, provides loans and credit, and offers other financial services."
    Example of a bad definition of a Bank:
    "Banks play a pivotal role in the global economy by accepting deposits, extending loans, and offering a suite of financial services to individuals, businesses, and governments."

11. **Human-like Writing:**
    - **Perplexity:** You must ensure high perplexity by varying your word choices and avoiding predictable phrases. Also, address burstiness by varying the length and style of your sentences. The goal is for the response to not appear generated by an AI, but to have a human and personal touch.
    - **Vary Sentence Structure:** Mix short, punchy sentences with slightly longer, more complex ones. Avoid starting sentences the same way repeatedly.
    - **Avoid Robotic Phrasing:** Steer clear of overly formal language, jargon (unless explained simply), and common AI filler phrases (e.g., "In conclusion," "It is important to note," "In the digital age...").
    - **Inject Personality (Subtly):** Write with confidence and clarity. Use transition words and phrases naturally (e.g., "however," "also," "next," "because of this," "think about it this way").
    - **Focus on Flow:** Ensure the text reads smoothly and logically from one point to the next.
    - **Direct Address:** Use "you" or "Your(s)" often to speak directly to the reader, making it more engaging.

12. Under **Next Steps: What Now?** always write logical next steps for the reader (4-7 steps formatted as bullet list — sentences must have dot at the end, up to 80 words total).

13. **ALWAYS DO THIS for any article:** Find a smart and natural way to recommend the reader to set up a website or web store. Make sure you make a subheading with a paragraph about it and link to https://hostadvice.com/vps/ within it. This article will live on hostadvice.com, so don't refer to it as an external site when linking.

14. You must use intelligently and naturally ALL the NLP keywords in the text (each keyword should appear the appropriate number of times based on its importance). AVOID bolding the keywords in the text. Some keywords contain acronyms in lowercase like url, utm, vps... ALWAYS capitalize the acronym in the keyword when inserting it to the text.

15. AVOID em-dashes in your writing.

16. **Semantic Triple Structure in Key Positions:** Structure key informational sentences as semantic triples: [Subject Entity] + [relationship verb] + [specific value/object]. This makes content parseable by AI models and knowledge graphs, increasing the chance of AI citation and featured snippets.

    Apply in these specific positions only — do not force triples into every sentence:
    - **First sentence of each H2 section:** Open with the topic entity as the subject, followed by an action verb and a specific value. Example: "Email personalization generates $70 ROI per dollar spent compared to $42 for basic emails." NOT: "In today's competitive landscape, personalization is becoming increasingly important."
    - **"What is X" definitions (Rule 10):** These are already natural triples — keep starting with "X is a..." which perfectly follows Entity + Relationship + Value.
    - **FAQ answers:** Start each answer with the subject entity (the thing being asked about), not "Yes," "No," or filler phrases.
    - **Key Takeaways bullets:** Each bullet should read as a standalone fact an AI could extract: "[Subject] [verb] [specific claim]."

    **Do NOT:**
    - Force triples into storytelling sections, anecdotes, or conversational paragraphs — the engaging tone (Rules 4, 11) takes priority
    - Sacrifice readability or the conversational voice for triple structure
    - Use triples as an excuse to repeat the same entity name excessively

17. **WORD COUNT:** Write a [WORD_COUNT]-word article. Ensure it's exactly [WORD_COUNT] words. (Replace [WORD_COUNT] with the value from the CSV.)

---

## Step 8 — Validate Word Count

Count the words in the generated article using this method: match sequences of word characters (`\b[\w'-]+\b`).

The valid range is:
- **Minimum:** `word_count - 520`
- **Maximum:** `word_count + 1200`

If the word count is within range, proceed to Step 9. If outside range, tell the user the count is off and attempt to adjust (expand or trim) the article to hit the target.

## Step 9 — Generate Brief Details Header

Create a project metadata block to prepend to the article. Use this template:

```
**Client Name:** HostAdvice

**Client URL:** <https://hostadvice.com>

**SEO Title:** [SEO Title from CSV]

**Meta Description:** [Craft an engaging meta description up to 150 characters long. Lead with the main topic entity, not with generic verbs or "Discover/Learn/Find out".]

**URL Slug:** [Convert the main keyword to URL format: /key-word-phrase/]

**Writer Guidelines:** [HostAdvice Writer Guidelines](https://docs.google.com/document/d/1lEz1lyDXV-0sbP_X0JR_caLq2-dVslCD3t7hN0ogH-8/edit?usp=sharing)

**Internal Links:** [List naked URLs of HostAdvice links found in the article]

**External Links:** [List naked URLs of external links found in the article]

**Target Keyword(s):** [Main Keyword]

**Target Word Count:** [Word Count from CSV]

**Target Reading Level:** 9th grade or below.

**Target Audience:** [Write a sentence about who is target audience for this article.]

**Goal:** SEO traffic, educating the readers, affiliate earnings, and a gateway to other content on the website.
```

## Step 10 — Save and Update CSV

1. Combine the brief details header + the article text into one document.
2. Save to `[main-keyword-slugified]-ai-draft.md` in the working directory. (e.g., `blogs-vs-videos-ai-draft.md`)
3. Update `Content Management.csv`:
   - Set the **AI Draft Doc** column to the file path of the saved markdown
   - Set the **AI Draft Words** column to the actual word count
4. Tell the user:
   - File saved path
   - Actual word count vs target
   - Whether word count is within acceptable range
