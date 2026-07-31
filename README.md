# Shared Claude Code Skills

Shared Claude Code skills for the team.

## Skills included

| Slash command | Description |
|---|---|
| `/abs-draft-blog-post` | End-to-end ABS Commercial Cleaning blog post drafting pipeline. Fetches NeuronWriter requirements and SERP/PAA data, uses a pre-generated research report, creates a content brief, selects hub-and-spoke internal links, writes a full SEO-optimized blog post in ABS's voice per Content Brain, runs keyword and terminology compliance, and optionally uploads to NeuronWriter. |
| `/article-ai-images` | Generate AI images and insert them into articles, then upload to NeuronWriter. Takes a NeuronWriter query ID, downloads the live content, analyzes article structure, generates horizontal 16:9 AI images using the Gemini API that match each section's theme, inserts them throughout the article, uploads images to Google Drive, and uploads the final article back to NeuronWriter. |
| `/article-graphic` | Generate data-driven graphics for articles and pages -- bar charts, checklists, comparison tables, process diagrams, step-by-step visuals, statistical charts, timelines, and similar structured visuals. Uses Gemini API to produce images with accurate text rendering, then uploads to Google Drive. |
| `/article-infographic` | Generate tall infographics for articles and pages. Uses Gemini API to produce a single tall 9:16 image at 2K resolution with accurate text rendering, then uploads to Google Drive and returns a ready-to-use thumbnail link. |
| `/article-stock-images` | Find and insert stock images into articles, then upload to NeuronWriter. Takes a NeuronWriter query ID, downloads the live content, analyzes article structure, finds horizontal stock photos that match each section's theme, inserts them evenly throughout the article plus a hero image below H1, and uploads the result back to NeuronWriter. |
| `/create-content-brain` | Creates a comprehensive contentbrain.md style guide for any client. Reads call transcripts and analyzes the client's live website to extract positioning, writing style, terminology rules, and SEO guidelines. |
| `/create-service-page-b2b` | End-to-end B2B service page content creation from scratch. Fetches NeuronWriter requirements and Google SERP/PAA, calculates target word count from top competitors, analyzes a template page for structure, then creates new content following Content Brain rules, keyword compliance, and SEO best practices. Uploads to NeuronWriter when complete. |
| `/fetch-internal-urls` | Crawl a website's XML sitemap and extract all real page and post URLs, filtering out tags, categories, images, media, feeds, pagination, and other non-content URLs. Saves results as a plain-text CSV (one URL per line). |
| `/ha-draft-article` | End-to-end HostAdvice blog article drafting pipeline. Reads article parameters from Content Management.csv, uses a research report as input, creates a structured content brief, gathers internal links and People Also Ask questions, then writes a full SEO-optimized article matching the HostAdvice writing style. Updates the CSV with the output file path and word count. |
| `/local-biz-mockup` | End-to-end local business mockup website generator. Researches the business, gathers images and brand assets from public sources, designs a color schema, codes a responsive Astro + Tailwind 4 site, runs visual QA testing, and deploys to Vercel via GitHub. |
| `/local-seo-audit` | Comprehensive local SEO and Google Maps audit with HTML report. |
| `/local-site-content-plan` | End-to-end local business content plan generator. Reads services and locations from Content Brain and onboarding docs, builds a service x location page matrix with Near Me pages, fetches keyword volumes from SEMrush, crafts SEO titles, fetches People Also Ask questions from Google SERP via DataForSEO, filters for customer-intent blog topics, and produces a CSV + visual HTML dashboard. |
| `/optimize-service-page` | End-to-end service page content optimization. Fetches NeuronWriter data and Google SERP/PAA, optimizes content for keyword compliance and SEO, then uploads back to NeuronWriter. Requires a NeuronWriter query ID. |
| `/performance` | Optimize web performance for faster loading and better user experience. Deep performance optimization based on Lighthouse audits focusing on loading speed, runtime efficiency, and resource optimization. |
| `/redstone-draft-blog-post` | End-to-end Redstone Manufacturing blog post drafting pipeline. Fetches NeuronWriter requirements and SERP/PAA data, uses a pre-generated research report, creates a content brief, selects hub-and-spoke internal links, writes a full SEO-optimized blog post in Redstone's B2B manufacturing voice per Content Brain, runs keyword and terminology compliance, and optionally uploads to NeuronWriter. |
| `/research-for-blog-post` | End-to-end blog post research pipeline. Generates search terms from an article title, searches Google, selects the best competing articles, fetches and converts them to markdown, then produces a comprehensive 2000-5000 word research report. |
| `/sb-draft-blog-post` | End-to-end Smith Bros Mobile Detailing blog post drafting pipeline. Fetches NeuronWriter requirements and SERP/PAA data, uses a pre-generated research report, creates a content brief, selects hub-and-spoke internal links, writes a full SEO-optimized blog post in Smith Bros' warm, approachable local-business voice per Content Brain, runs keyword and terminology compliance, and optionally uploads to NeuronWriter. |
| `/semrush-keyword-cleanup` | Cleans up SEMrush organic keyword export files. Removes unnecessary columns, filters by position, sorts by URL/Traffic/Search Volume, and keeps top keywords per URL. Use when processing SEMrush keyword research Excel files. |
| `/semrush-site-audit` | Run a full SEMrush technical site audit for a client domain. Finds the correct Chrome profile, launches Chrome with remote debugging, creates the SEMrush project, configures audit settings, starts the audit, waits for completion, captures the Issues tab screenshot, and saves it to the working directory. |
| `/seo-content-audit-semrush` | End-to-end SEO content audit powered by SEMrush CSV exports. Processes organic keywords, top pages, competitors, keyword gap data, and domain authority screenshot to produce an actionable HTML report with opportunities sorted by attainability. |

## Installation

Clone this repo directly into your Claude Code skills directory:

```bash
# Mac/Linux
git clone https://github.com/teamoutriderdigital/claude-skills-shared.git ~/.claude/skills-shared

# Then symlink each skill into your skills folder:
ln -s ~/.claude/skills-shared/abs-draft-blog-post ~/.claude/skills/abs-draft-blog-post
ln -s ~/.claude/skills-shared/article-ai-images ~/.claude/skills/article-ai-images
ln -s ~/.claude/skills-shared/article-graphic ~/.claude/skills/article-graphic
ln -s ~/.claude/skills-shared/article-infographic ~/.claude/skills/article-infographic
ln -s ~/.claude/skills-shared/article-stock-images ~/.claude/skills/article-stock-images
ln -s ~/.claude/skills-shared/create-content-brain ~/.claude/skills/create-content-brain
ln -s ~/.claude/skills-shared/create-service-page-b2b ~/.claude/skills/create-service-page-b2b
ln -s ~/.claude/skills-shared/fetch-internal-urls ~/.claude/skills/fetch-internal-urls
ln -s ~/.claude/skills-shared/ha-draft-article ~/.claude/skills/ha-draft-article
ln -s ~/.claude/skills-shared/local-biz-mockup ~/.claude/skills/local-biz-mockup
ln -s ~/.claude/skills-shared/local-seo-audit ~/.claude/skills/local-seo-audit
ln -s ~/.claude/skills-shared/local-site-content-plan ~/.claude/skills/local-site-content-plan
ln -s ~/.claude/skills-shared/optimize-service-page ~/.claude/skills/optimize-service-page
ln -s ~/.claude/skills-shared/performance ~/.claude/skills/performance
ln -s ~/.claude/skills-shared/redstone-draft-blog-post ~/.claude/skills/redstone-draft-blog-post
ln -s ~/.claude/skills-shared/research-for-blog-post ~/.claude/skills/research-for-blog-post
ln -s ~/.claude/skills-shared/sb-draft-blog-post ~/.claude/skills/sb-draft-blog-post
ln -s ~/.claude/skills-shared/semrush-keyword-cleanup ~/.claude/skills/semrush-keyword-cleanup
ln -s ~/.claude/skills-shared/semrush-site-audit ~/.claude/skills/semrush-site-audit
ln -s ~/.claude/skills-shared/seo-content-audit-semrush ~/.claude/skills/seo-content-audit-semrush
```

```powershell
# Windows (PowerShell as Administrator)
git clone https://github.com/teamoutriderdigital/claude-skills-shared.git "$env:USERPROFILE\.claude\skills-shared"

# Then symlink each skill:
$src = "$env:USERPROFILE\.claude\skills-shared"
$dst = "$env:USERPROFILE\.claude\skills"
New-Item -ItemType Junction -Path "$dst\abs-draft-blog-post"        -Target "$src\abs-draft-blog-post"
New-Item -ItemType Junction -Path "$dst\article-ai-images"          -Target "$src\article-ai-images"
New-Item -ItemType Junction -Path "$dst\article-graphic"            -Target "$src\article-graphic"
New-Item -ItemType Junction -Path "$dst\article-infographic"        -Target "$src\article-infographic"
New-Item -ItemType Junction -Path "$dst\article-stock-images"       -Target "$src\article-stock-images"
New-Item -ItemType Junction -Path "$dst\create-content-brain"       -Target "$src\create-content-brain"
New-Item -ItemType Junction -Path "$dst\create-service-page-b2b"    -Target "$src\create-service-page-b2b"
New-Item -ItemType Junction -Path "$dst\fetch-internal-urls"        -Target "$src\fetch-internal-urls"
New-Item -ItemType Junction -Path "$dst\ha-draft-article"           -Target "$src\ha-draft-article"
New-Item -ItemType Junction -Path "$dst\local-biz-mockup"           -Target "$src\local-biz-mockup"
New-Item -ItemType Junction -Path "$dst\local-seo-audit"            -Target "$src\local-seo-audit"
New-Item -ItemType Junction -Path "$dst\local-site-content-plan"    -Target "$src\local-site-content-plan"
New-Item -ItemType Junction -Path "$dst\optimize-service-page"      -Target "$src\optimize-service-page"
New-Item -ItemType Junction -Path "$dst\performance"                -Target "$src\performance"
New-Item -ItemType Junction -Path "$dst\redstone-draft-blog-post"   -Target "$src\redstone-draft-blog-post"
New-Item -ItemType Junction -Path "$dst\research-for-blog-post"     -Target "$src\research-for-blog-post"
New-Item -ItemType Junction -Path "$dst\sb-draft-blog-post"         -Target "$src\sb-draft-blog-post"
New-Item -ItemType Junction -Path "$dst\semrush-keyword-cleanup"    -Target "$src\semrush-keyword-cleanup"
New-Item -ItemType Junction -Path "$dst\semrush-site-audit"         -Target "$src\semrush-site-audit"
New-Item -ItemType Junction -Path "$dst\seo-content-audit-semrush"  -Target "$src\seo-content-audit-semrush"
```

## Updating

```bash
cd ~/.claude/skills-shared && git pull
```

Slash commands update automatically -- no re-linking needed.
