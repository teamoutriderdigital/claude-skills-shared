# Shared Claude Code Skills

Shared Claude Code skills for the team.

## Skills included

| Slash command | Description |
|---|---|
| `/create-content-brain` | Creates a comprehensive contentbrain.md style guide for any client. Reads call transcripts and analyzes the client's live website to extract positioning, writing style, terminology rules, and SEO guidelines. |
| `/create-service-page-b2b` | End-to-end B2B service page content creation from scratch. Fetches NeuronWriter requirements and Google SERP/PAA, calculates target word count from top competitors, analyzes a template page for structure, then creates new content following Content Brain rules, keyword compliance, and SEO best practices. Uploads to NeuronWriter when complete. |
| `/optimize-service-page` | End-to-end service page content optimization. Fetches NeuronWriter data and Google SERP/PAA, optimizes content for keyword compliance and SEO, then uploads back to NeuronWriter. Requires a NeuronWriter query ID. |
| `/local-biz-mockup` | End-to-end local business mockup website generator. Researches the business, gathers images and brand assets from public sources, designs a color schema, codes a responsive Astro + Tailwind 4 site, runs visual QA testing, and deploys to Vercel via GitHub. |
| `/local-seo-audit` | Comprehensive local SEO and Google Maps audit with HTML report. |
| `/fetch-internal-urls` | Crawl a website's XML sitemap and extract all real page and post URLs, filtering out tags, categories, images, media, feeds, pagination, and other non-content URLs. Saves results as a plain-text CSV (one URL per line). |
| `/seo-content-audit-semrush` | End-to-end SEO content audit powered by SEMrush CSV exports. Processes organic keywords, top pages, competitors, keyword gap data, and domain authority screenshot to produce an actionable HTML report with opportunities sorted by attainability. |
| `/redstone-draft-blog-post` | End-to-end Redstone Manufacturing blog post drafting pipeline. Fetches NeuronWriter requirements and SERP/PAA data, uses a pre-generated research report, creates a content brief, selects hub-and-spoke internal links, writes a full SEO-optimized blog post in Redstone's B2B manufacturing voice per Content Brain, runs keyword and terminology compliance, and optionally uploads to NeuronWriter. |
| `/research-for-blog-post` | End-to-end blog post research pipeline. Generates search terms from an article title, searches Google, selects the best competing articles, fetches and converts them to markdown, then produces a comprehensive 2000-5000 word research report. |

## Installation

Clone this repo directly into your Claude Code skills directory:

```bash
# Mac/Linux
git clone https://github.com/teamoutriderdigital/claude-skills-shared.git ~/.claude/skills-shared

# Then symlink each skill into your skills folder:
ln -s ~/.claude/skills-shared/create-content-brain ~/.claude/skills/create-content-brain
ln -s ~/.claude/skills-shared/create-service-page-b2b ~/.claude/skills/create-service-page-b2b
ln -s ~/.claude/skills-shared/optimize-service-page ~/.claude/skills/optimize-service-page
ln -s ~/.claude/skills-shared/local-biz-mockup ~/.claude/skills/local-biz-mockup
ln -s ~/.claude/skills-shared/local-seo-audit ~/.claude/skills/local-seo-audit
ln -s ~/.claude/skills-shared/fetch-internal-urls ~/.claude/skills/fetch-internal-urls
ln -s ~/.claude/skills-shared/seo-content-audit-semrush ~/.claude/skills/seo-content-audit-semrush
ln -s ~/.claude/skills-shared/redstone-draft-blog-post ~/.claude/skills/redstone-draft-blog-post
ln -s ~/.claude/skills-shared/research-for-blog-post ~/.claude/skills/research-for-blog-post
```

```powershell
# Windows (PowerShell as Administrator)
git clone https://github.com/teamoutriderdigital/claude-skills-shared.git "$env:USERPROFILE\.claude\skills-shared"

# Then symlink each skill:
$src = "$env:USERPROFILE\.claude\skills-shared"
$dst = "$env:USERPROFILE\.claude\skills"
New-Item -ItemType Junction -Path "$dst\create-content-brain"      -Target "$src\create-content-brain"
New-Item -ItemType Junction -Path "$dst\create-service-page-b2b"   -Target "$src\create-service-page-b2b"
New-Item -ItemType Junction -Path "$dst\optimize-service-page"     -Target "$src\optimize-service-page"
New-Item -ItemType Junction -Path "$dst\local-biz-mockup"          -Target "$src\local-biz-mockup"
New-Item -ItemType Junction -Path "$dst\local-seo-audit"           -Target "$src\local-seo-audit"
New-Item -ItemType Junction -Path "$dst\fetch-internal-urls"       -Target "$src\fetch-internal-urls"
New-Item -ItemType Junction -Path "$dst\seo-content-audit-semrush" -Target "$src\seo-content-audit-semrush"
New-Item -ItemType Junction -Path "$dst\redstone-draft-blog-post"  -Target "$src\redstone-draft-blog-post"
New-Item -ItemType Junction -Path "$dst\research-for-blog-post"  -Target "$src\research-for-blog-post"
```

## Updating

```bash
cd ~/.claude/skills-shared && git pull
```

Slash commands update automatically — no re-linking needed.
