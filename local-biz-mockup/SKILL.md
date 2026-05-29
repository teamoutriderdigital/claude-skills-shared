---
name: local-biz-mockup
description: End-to-end local business mockup website generator. This skill should be used when the user wants to create a website mockup, site mockup, landing page, or demo site for a local business, contractor, service company, or small business. It researches the business, gathers images and brand assets from public sources, designs a color schema, codes a responsive Astro + Tailwind 4 site, runs visual QA testing, and deploys to Vercel via GitHub. Triggers for requests like "create a mockup for [business]", "build a demo site for [company]", "make a website for [local business]", or "[domain.com] please build a mockup".
---

# Local Business Mockup Website Generator

This skill generates professional, production-ready mockup websites for local businesses using a standardized 7-phase workflow. The output is a fully coded Astro + Tailwind 4 static site deployed to Vercel.

## Prerequisites

- Node.js 22+ installed
- `gh` CLI authenticated with target GitHub account
- `vercel` CLI installed and authenticated
- Browser MCP tools available for visual QA
- WebFetch and WebSearch tools available for research

## Workflow

Execute all phases in order. Do not skip phases. Present results to the user at each gate checkpoint before proceeding.

### Phase 0 — Scope Selection

Gather initial parameters from the user:

1. Confirm the business name, website domain, and industry/niche
2. Present mockup tier options via AskUserQuestion:

| Tier | Pages | Included |
|---|---|---|
| **Starter (3 pages)** | Home, Services, Contact | Core pages only |
| **Standard (5 pages)** | Home, Services, About, Contact, Projects/Gallery | Adds company story and portfolio |
| **Full (10 pages)** | Home, 4-5 individual service pages, About, Team, Projects, Testimonials, Contact | Complete site |

3. Store the selected tier — it determines which pages are built in Phase 5

### Phase 1 — Business Research

Reference: `references/research-checklist.md`

Gather comprehensive business intelligence:

1. **Fetch the business website** — visit every page (home, about, services, contact, gallery). Extract all services, team members, contact details, taglines, and copy.
2. **Web search** for the business name + location to find directory listings, reviews, and public records.
3. **Check 10+ local directories**: Google Business, Yelp, BBB, Yahoo Local, and state-specific registrars (e.g., AZ ROC for contractors).
4. **Check 10+ national directories**: Manta, Blue Book, Procore, BuildZoom, Buzzfile, Levelset, OpenCorporates, etc.
5. **Extract**: services offered, location/address, phone/email, business hours, team members, licenses/certifications, reviews/ratings, years in business, revenue estimates, ownership details (woman-owned, minority-owned, etc.).
6. **Save** all findings to `{project}/business-research.md` using a structured format with tables.

**IMPORTANT**: Do NOT use Facebook or Instagram for research or image gathering. These platforms require per-click approval and will slow down the workflow significantly. Stick to the business website, Google Maps, and public directories.

**Gate**: Present a summary of key findings to the user before proceeding.

### Phase 2 — Asset Collection

1. **Logo**: Download from the business website. Use browser JS to extract image URLs from `<img>` tags and background images.
2. **Project/work photos**: Download all relevant images from the website's services, portfolio, and gallery pages.
3. **Google Maps photos**: Navigate to the business's Google Maps listing, extract `googleusercontent` image URLs via browser JS, download at high resolution (`=w1200-h900-k-no` suffix).
4. **Naming convention**: Use descriptive filenames — `logo-{business}.png`, `project-{description}.jpg`, `team-{name}.png`, `hero-{description}.jpg`.
5. **Save** to `{project}/images/` and create `IMAGE-INDEX.md` documenting each file, its source, and description.
6. **Audit images**: Check orientation (prefer landscape for heroes), resolution (minimum 800px wide), and quality. Flag portrait-only images as unsuitable for hero backgrounds.

Skip: Facebook, Instagram, LinkedIn, or any source requiring authentication.

### Phase 3 — Color Schema

Reference: `references/color-schema-guide.md`

1. **Analyze the logo** — use browser JS on the business website to extract image URLs, then visually identify dominant colors (2-4 colors typically).
2. **Extract website CSS** — use browser JS (`getComputedStyle`) to pull existing background colors, text colors, button colors, and accent colors.
3. **Design the palette**:
   - 5 primary colors: dominant brand color, secondary accent, dark (header/footer), light (section bg), neutral white
   - 5 secondary colors: hover states, muted text, highlight bg, alert/urgency, dark variant
4. **Check accessibility**: Calculate WCAG contrast ratios for key combinations (text on bg, button text on button bg). Ensure AA compliance minimum.
5. **Generate CSS variables** using `@theme` block for Tailwind 4.
6. **Save** to `{project}/color-schema.md` with hex codes, RGB values, usage guide, and CSS variable block.

**Gate**: Present the color palette to the user for approval. Adjust if requested.

### Phase 4 — Plan & Confirm

Reference: `references/page-templates.md`

1. Based on the selected tier, generate a **page plan** listing every page with its sections.
2. For each page, specify:
   - Hero image (which downloaded image to use)
   - Section layout (refer to page-templates.md blueprints)
   - Key copy points (headlines, CTAs)
   - Data source (which research findings feed this section)
3. Determine copy direction based on the business niche:
   - **B2B** (contractors, wholesalers): Direct, proof-driven, short sentences, lead with numbers
   - **B2C** (restaurants, salons, retail): Warmer, benefit-focused, lifestyle-oriented
   - **Professional services** (lawyers, dentists): Trust-forward, credentials prominent, reassuring tone

**Gate**: Present the page plan to the user via AskUserQuestion. Confirm before coding.

### Phase 5 — Code the Mockup

1. **Copy template**: Copy `assets/astro-template/` to `{project}/site/`.
2. **Install dependencies**: Run `npm install` in the site directory.
3. **Copy images**: Move downloaded images from `{project}/images/` to `{project}/site/public/images/`.
4. **Customize theme**: Update `src/styles/global.css` `@theme` block with the approved color palette CSS variables. Update font families.
5. **Build components**: Customize Header (logo, nav links), Footer (contact info, license, badges), and all page-specific content.
6. **Build pages**: Create each `.astro` page file using the component library. Write all copy using research data. Use SVG icons (inline path strings) instead of Unicode characters for service cards.
7. **Verify images**: Ensure every `src="/images/..."` reference points to an actual file in `public/images/`. No broken image paths.
8. **Build test**: Run `npm run build` — must complete with zero errors and generate all expected pages.

Design principles to follow:
- Use the `frontend-design` skill aesthetic guidelines if available
- Left-align hero text on desktop for modern feel
- Use gradient overlays on hero images (diagonal, not flat)
- Pill-shaped buttons (`rounded-full`) with hover lift effect
- Gold/accent top-border animation on cards
- Scroll-triggered fade-in animations
- Staggered animation delays on grid children
- Grain texture on hero sections

### Phase 6 — Visual QA

Reference: `references/qa-checklist.md`

1. Start the dev server: `npm run dev`
2. Use browser MCP tools to navigate to each page and take screenshots at desktop width.
3. Check each page against the QA checklist:

| Check | What to Verify |
|---|---|
| **Text readability** | All headings and body text visible against backgrounds. No black-on-dark or white-on-light issues. Heading color classes (`text-white`, `text-charcoal`) override global defaults. |
| **Hero images** | Landscape orientation, properly covering full width, overlay provides sufficient contrast for text. |
| **Broken images** | No missing image placeholders. Every `src` path resolves. |
| **Heading hierarchy** | One h1 per page (in hero). h2 for sections, h3 for cards. |
| **Buttons** | All CTAs visible, consistent styling (pill shape, brand colors), hover states work. |
| **Navigation** | Logo links home. Nav links highlight active page. Mobile hamburger toggles menu. |
| **Footer** | Complete with contact info, license/credentials, links, copyright year. |
| **Color palette** | Matches the approved schema. No stray default colors. |
| **Forms** | Labels visible, fields styled, placeholder text present, submit button prominent. |
| **Responsive** | Content doesn't overflow on mobile widths. Images scale down. Grid stacks properly. |

4. **Fix any issues** found during QA immediately.
5. **Re-verify** after fixes — take new screenshots to confirm.

### Phase 7 — Deploy

1. Initialize git in the site directory: `git init`
2. Stage and commit all files with a descriptive commit message.
3. Ask the user for their GitHub account/org name.
4. Create a GitHub repo: `gh repo create {org}/{repo-name} --public --source . --push`
5. Deploy to Vercel: `vercel --yes`
6. Report the live URLs to the user:
   - GitHub repo URL
   - Vercel production URL

## Component Library

The template includes these reusable Astro components:

| Component | Purpose | Key Props |
|---|---|---|
| `BaseLayout.astro` | HTML shell with meta, fonts, scroll animation JS | `title`, `description` |
| `Header.astro` | Fixed nav with logo, links, CTA, mobile hamburger | `currentPath` |
| `Footer.astro` | Dark footer with 3-col layout, contact, badges | (none — customize inline) |
| `Hero.astro` | Full-width hero with gradient overlay, badges, CTAs | `title`, `subtitle`, `image`, `compact`, `badges`, `primaryCta`, `secondaryCta` |
| `ServiceCard.astro` | Card with SVG icon, title, description, hover accent | `title`, `description`, `icon`, `large` |
| `StatBar.astro` | Dark stats strip with gold numbers | (none — customize inline) |
| `ContactForm.astro` | Visual-only form with fields for project inquiries | (none — customize inline) |

## Important Constraints

- **Never use Facebook or Instagram** for scraping images or data. These require per-click user approval.
- **Always verify image paths** before building — broken images are the #1 QA failure.
- **Use `:where()` or avoid global heading color rules** in CSS — Tailwind utility classes like `text-white` must be able to override heading defaults.
- **Prefer landscape images for heroes** — portrait images crop poorly in wide hero sections.
- **Ask before deploying** — confirm GitHub org/account and repo name with user before pushing.
