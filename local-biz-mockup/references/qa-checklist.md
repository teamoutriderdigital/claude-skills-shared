# Visual QA Testing Checklist

Run this checklist after building the mockup site, before deploying.

## Setup

1. Start the dev server: `npm run dev`
2. Open browser MCP tools
3. Navigate to each page and take screenshots at desktop width (1280px+)
4. Optionally resize to mobile (375px) for responsive checks

## Per-Page Checks

Run these checks on **every page** of the mockup.

### Text & Typography

- [ ] **Hero heading is readable** — white or light text over dark overlay. NOT black text on dark image.
- [ ] **All body text has sufficient contrast** — dark text on light backgrounds, light text on dark backgrounds.
- [ ] **No text truncation** — all headings and paragraphs fully visible, not cut off.
- [ ] **Font families loading** — heading font (serif/display) distinct from body font (sans-serif). Not falling back to system fonts.
- [ ] **Heading hierarchy** — exactly one h1 per page (in hero), h2 for section titles, h3 for cards/subsections.
- [ ] **Section labels styled** — small uppercase gold text above section headings ("WHO WE ARE", "OUR SERVICES", etc).

### Images

- [ ] **No broken images** — every `<img>` loads. No placeholder icons or 404s.
- [ ] **Hero image is landscape orientation** — fills full width without awkward vertical cropping.
- [ ] **Hero overlay provides contrast** — text is readable over the image in all areas.
- [ ] **Logo loads in header** — correct size, not pixelated, not oversized.
- [ ] **Logo loads in footer** — same check.
- [ ] **Project/work images are relevant** — showing actual business work, not stock photos or unrelated content.

### Layout & Structure

- [ ] **Header is fixed/sticky** — stays at top when scrolling.
- [ ] **Header has proper spacing** — logo and nav don't overlap, items centered vertically.
- [ ] **Sections alternate backgrounds** — visual rhythm (white → gray → white → dark → gold, etc).
- [ ] **Content is contained** — nothing overflows horizontally. No horizontal scrollbar.
- [ ] **Card grids are even** — cards are same height within a row. No ragged layouts.
- [ ] **Footer renders completely** — all 3 columns visible, contact info present, copyright line at bottom.

### Navigation

- [ ] **All nav links work** — Home, Services, Contact (and others) navigate correctly.
- [ ] **Active page highlighted** — current page's nav link is gold with underline accent.
- [ ] **Mobile hamburger works** — toggle opens/closes mobile menu. Menu items are tappable.
- [ ] **Logo links to home** — clicking the header logo navigates to /.
- [ ] **CTA button in header** — "Free Estimate" or equivalent links to /contact.

### Buttons & CTAs

- [ ] **Primary CTAs visible** — gold/brand-color buttons stand out on every page.
- [ ] **Button text is readable** — sufficient contrast between button text and button background.
- [ ] **Buttons are pill-shaped** — rounded-full styling, consistent across all pages.
- [ ] **Hover states work** — buttons darken/lift on hover (test in browser).
- [ ] **CTA banner present** — gold/brand-color banner at bottom of every page before footer.

### Color Palette

- [ ] **Brand primary color used** — CTAs, section labels, accents match approved palette.
- [ ] **Dark sections use brand dark** — header, footer, stats bar, social proof section.
- [ ] **No stray default colors** — no unexpected blues, grays, or browser defaults.
- [ ] **Gold accent line on footer** — thin gold bar at top of footer (gold-accent-top class).

### Forms (Contact page)

- [ ] **All fields visible** — labels, inputs, selects render properly.
- [ ] **Labels are styled** — small uppercase tracking, not default browser labels.
- [ ] **Placeholder text present** — guiding text in each field.
- [ ] **Required indicators** — asterisks or "required" text on mandatory fields.
- [ ] **Submit button prominent** — gold/brand primary, full width or clearly visible.
- [ ] **Focus states work** — clicking a field shows a brand-colored ring.

### Animations

- [ ] **Scroll fade-in working** — sections animate in as they enter viewport (fade-in-up class).
- [ ] **Staggered delays** — cards in a grid animate in sequence, not all at once.
- [ ] **No flash of unstyled content** — elements don't appear then jump.

### SEO & Meta

- [ ] **Page title set** — each page has `<title>` with format "Page | Business Name".
- [ ] **Meta description set** — each page has a unique meta description.
- [ ] **Alt text on images** — hero images can have empty alt, but content images should have descriptive alt.

## Build Verification

- [ ] `npm run build` completes with zero errors
- [ ] All expected pages generated in `dist/` directory
- [ ] No warnings about missing files or broken imports

## Common Issues & Fixes

| Issue | Cause | Fix |
|---|---|---|
| Hero text is black/dark | Global CSS heading color overrides Tailwind classes | Remove global `color` rule on h1-h4, or use `:where()` for zero specificity |
| Broken images | Image path doesn't match filename in public/images/ | Verify every `src="/images/..."` path exists |
| Hero image crops badly | Portrait-orientation image in landscape hero | Replace with landscape image or adjust `object-position` |
| Cards different heights | Varying description lengths | Add `min-h` or use flexbox `flex-1` on description |
| Mobile menu doesn't work | Script not loading or ID mismatch | Check `id` attributes match between button, menu, and icons |
| Gold accent not showing | `::before` pseudo-element not rendering | Ensure parent has `position: relative` and `overflow: hidden` |
