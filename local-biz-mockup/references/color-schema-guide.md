# Color Schema Design Guide

How to derive a professional color palette from a business's existing brand assets.

## Step 1: Extract Logo Colors

Use browser JavaScript on the business website to find logo image URLs:

```javascript
const images = Array.from(document.querySelectorAll('img'));
images.map(img => ({ src: img.src.split('?')[0], alt: img.alt, w: img.naturalWidth, h: img.naturalHeight }));
```

Visually identify 2-4 dominant colors in the logo. Common patterns:
- **2-color logos**: Primary + accent (e.g., blue + orange)
- **3-color logos**: Primary + secondary + accent
- **Monochrome logos**: Need to derive accent colors from industry norms

## Step 2: Extract Website CSS

Use browser JavaScript to pull current site colors:

```javascript
const allElements = document.querySelectorAll('*');
const bgs = new Set();
const colors = new Set();
Array.from(allElements).forEach(el => {
  const cs = getComputedStyle(el);
  if (cs.backgroundColor !== 'rgba(0, 0, 0, 0)') bgs.add(cs.backgroundColor);
  colors.add(cs.color);
});
JSON.stringify({ backgrounds: Array.from(bgs), textColors: Array.from(colors) });
```

## Step 3: Build the Palette

### Primary Palette (5 colors)

| Role | Purpose | How to Choose |
|---|---|---|
| **Brand Primary** | CTAs, highlights, headings | Dominant logo color or most distinctive brand color |
| **Brand Secondary** | Secondary buttons, badges, accents | Second logo color or complementary color |
| **Dark** | Header, footer, text | Near-black (#1C1C1C range) — warm or cool based on brand |
| **Light Background** | Alternating sections | Very light tint of brand primary or warm neutral (#F2F0ED range) |
| **White** | Main content areas | Pure white or off-white |

### Secondary Palette (5 colors)

| Role | Purpose | How to Choose |
|---|---|---|
| **Brand Primary Dark** | Hover state for primary | Darken brand primary by 15-20% |
| **Body Text** | Paragraphs, descriptions | Dark gray (#3A3A3A range) |
| **Muted** | Subtle text, borders | Medium gray (#8C8C84 range) |
| **Highlight Background** | Callout boxes, testimonials | Very light tint of brand primary (10% opacity feel) |
| **Alert/Urgency** | Phone numbers, limited-time CTAs | Warm orange or red — use sparingly |

## Step 4: Industry Color Norms

Match palette warmth to industry:
- **Construction/trades**: Warm golds, oranges, earth tones + dark charcoal
- **Healthcare/dental**: Cool blues, greens, clean whites
- **Legal/financial**: Navy, dark green, burgundy + gold accents
- **Food/restaurant**: Warm reds, oranges, natural greens
- **Beauty/salon**: Pastels, rose gold, soft neutrals
- **Auto/mechanical**: Dark grays, reds, metallic silvers
- **Tech/IT**: Blues, purples, electric accents

## Step 5: Accessibility Check

Verify WCAG AA contrast ratios (minimum 4.5:1 for body text, 3:1 for large text):

| Combination | Minimum Ratio |
|---|---|
| Body text on white background | 4.5:1 (AAA preferred at 7:1) |
| White text on dark background | 4.5:1 |
| White text on brand primary button | 3:1 (large text) or 4.5:1 |
| Dark text on brand primary button | 4.5:1 |
| White text on brand secondary | 4.5:1 |

If brand primary is too light for white text, use dark text on brand buttons instead.

## Step 6: Generate CSS Variables

Output format for Tailwind 4 `@theme` block:

```css
@theme {
  --color-brand-primary: #HEXVAL;
  --color-brand-primary-dark: #HEXVAL;
  --color-brand-secondary: #HEXVAL;
  --color-brand-secondary-dark: #HEXVAL;
  --color-dark: #HEXVAL;
  --color-dark-light: #HEXVAL;
  --color-light-bg: #HEXVAL;
  --color-highlight-bg: #HEXVAL;
  --color-muted: #HEXVAL;
  --color-alert: #HEXVAL;

  --font-heading: 'DISPLAY_FONT', Georgia, serif;
  --font-body: 'BODY_FONT', system-ui, sans-serif;
}
```

## Step 7: Application Guide

Document how each color applies to page elements:

- **Header/Footer**: Dark background, white text, brand primary for accents
- **Hero**: Image with dark gradient overlay, white headings, brand primary CTAs
- **Stats/Trust Bar**: Dark background, brand primary numbers
- **Service Cards**: White bg, dark text, brand primary icon containers and hover accents
- **CTA Banners**: Brand primary background, dark text, dark buttons
- **Forms**: Light-bg input fields, brand primary focus rings, brand primary submit button
- **Badges/Pills**: Brand primary tinted backgrounds with brand primary text
