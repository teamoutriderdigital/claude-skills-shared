---
name: create-content-brain
description: Creates a comprehensive contentbrain.md style guide for any client. Reads call transcripts and analyzes the client's live website to extract positioning, writing style, terminology rules, and SEO guidelines. Use when setting up a new client's content standards for AI-generated content.
allowed-tools: Read, Write, Glob, Grep, WebFetch, Agent, AskUserQuestion
---

# Create Content Brain

Generate a comprehensive `contentbrain.md` file for a client that serves as the single source of truth for all AI-generated content.

## Prerequisites

Before running this skill, ensure the following files exist in the client's project directory under a `Content brain\` folder:

1. **Call transcripts** (`.md` files) -- Transcripts of strategy calls between the team and the client. These are the primary source for client preferences, positioning mandates, and terminology rules. Client opinions are always top priority.
2. **Website URL file** (`website url.txt`) -- A text file containing the client's website URL.

## Process

### Step 1: Read Source Materials

1. Use `Glob` to find all files in the `Content brain\` folder
2. Read all `.md` transcript files to extract:
   - **Client positioning mandates** -- How the client wants to be described, what they are NOT, identity boundaries
   - **Terminology preferences** -- Words to always use, never use, or handle carefully
   - **Business context** -- Services, industries, target audience, competitive advantages
   - **Content strategy preferences** -- What types of content to prioritize, how content should be structured
   - **Do/don't rules** -- Any explicit instructions about content style, approach, or framing
3. Read `website url.txt` to get the client's website URL

### Step 2: Analyze the Live Website

Using `WebFetch` or browser automation tools, visit and analyze:

1. **Homepage** -- Note tone, positioning, key messages, CTAs, metrics used
2. **About page** -- Note narrative style, founder story, company values, voice/person
3. **2-3 service pages** -- Note content structure, heading patterns, voice (we/you/they), technical language level, CTA placement and style, FAQ format
4. **2-3 blog posts or resource pages** -- Note article structure, tone differences from service pages, use of technical vs accessible language

For each page, extract:
- Writing tone (formal/casual/technical/conversational)
- Voice and person (first/second/third, and how they mix)
- Sentence structure patterns (short vs long, active vs passive)
- Heading style (Title Case? Question format? Descriptive?)
- Technical jargon level and how terms are explained
- CTA language and placement
- Content structure (section order, use of lists/tables/FAQs)
- Brand language and recurring phrases

### Step 3: Synthesize into contentbrain.md

Create `Content brain\contentbrain.md` with these 8 sections:

#### Section 1 -- Preamble
- State this is the single source of truth for AI-generated content
- When this document conflicts with AI defaults, this document wins
- Include last-updated date

#### Section 2 -- Client Identity & Positioning (HIGHEST PRIORITY)
- **Who We Are** -- Core identity statement, facilities, capabilities
- **Who We Are NOT** -- Hard boundaries the client has explicitly set (table format: what they're not + why it matters)
- **Positioning formula** -- A fill-in-the-blank template for consistent framing
- Source everything from client's own words in transcripts

#### Section 3 -- Business Context
- Business model and value proposition
- Target audience (describe each segment and what they need)
- Priority industries (ranked by strategic value)
- Complete services taxonomy (hierarchical list of all services and sub-services)
- Certifications and quality standards
- Geographic presence
- Key quality/performance metrics

#### Section 4 -- Writing Style Guide
- **Voice & person rules** -- Verified against the live site, not assumed. Include actual examples from the site.
- **Tone spectrum** -- Professional descriptors with what-to-do and what-not-to-do
- **Sentence structure** -- Word count ranges by purpose, active voice target percentage
- **Formatting rules** -- Heading case, punctuation conventions, bold usage, table usage, list preferences, number formatting, acronym handling
- **Technical language rules** -- How to handle jargon for dual audiences, with good/bad examples

#### Section 5 -- Terminology Rules (Mandatory)
- **Always Use** table -- "Instead of X, use Y" format
- **Never Use** list -- Banned words/phrases with no alternatives (just don't say it)
- **ChatGPT slop phrases** -- List of filler patterns that must never appear
- **Handle with Care** table -- Terms that are okay in some contexts but dangerous in others, with specific guidance

#### Section 6 -- SEO & Content Strategy Rules
- Hub-and-spoke model explanation (if applicable)
- Keyword integration rules
- FAQ/schema requirements
- Internal linking rules and minimums
- Meta/title tag patterns

#### Section 7 -- Brand Anchors & Proof Points
- Reusable quality metrics
- Trust language phrases (rotate across content)
- CTA language (approved phrases + banned phrases)
- CTA placement rules

#### Section 8 -- Things to Absolutely Avoid
- Numbered checklist of anti-patterns, combining positioning violations, style violations, and content quality violations
- Each item should be specific and actionable, not vague

### Step 4: Add Quick Reference Card

At the end of the document, add a table summarizing the most critical rules for rapid AI reference when starting any content piece.

## Key Principles

1. **Client opinions are always top priority.** If the client said it in a transcript, it goes in the content brain as a rule, not a suggestion.
2. **Verify against the live site.** Don't assume voice/person/style rules -- check actual pages and include real examples.
3. **Be specific, not vague.** "Professional tone" is useless. "Confident without being boastful -- let metrics speak, not superlatives" is actionable.
4. **Include examples.** Good examples and bad examples for every style rule. Pull good examples from the live site.
5. **Make it AI-readable.** Tables for lookups, clear section headers, no ambiguity. An AI should be able to apply every rule without interpretation.
6. **No fabrication.** If a metric, certification, or capability isn't confirmed in transcripts or on the live site, don't include it. Use `[VERIFY: ...]` placeholders.

## Output

The final file is saved at `Content brain\contentbrain.md` in the client's project directory.
