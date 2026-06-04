# Page Type Classification Rules

Classify each keyword into exactly ONE page type. Apply rules in order — first match wins.

These categories are designed to work across any industry. Before classifying, scan the keyword list to understand the client's domain — the same framework applies whether the client is a law firm, SaaS company, plumber, or e-commerce store.

## 1. Route/Location Pair Pages

**Pattern:** Keyword contains TWO geographic locations indicating an origin-destination pair or a service corridor.

**Detection signals:**
- Contains " to " or " from " with state/city names on both sides
- Contains "{place} to {place}" or "from {place} to {place}" patterns
- Implies a directional service between two locations

**Applies to:** Moving companies, logistics, travel, delivery services, any business with origin-destination service areas.

**Examples across industries:**
- "movers from boston to miami"
- "flights new york to london"
- "freight los angeles to chicago"

**Sub-grouping:** Group by location pairs, aggregate volume per route.

**Note:** If the client's industry doesn't involve origin-destination services (e.g., a SaaS company, a local restaurant), this category will simply be empty. That's fine — skip it in the report.

## 2. State/Location Pages

**Pattern:** Keyword contains ONE geographic location (state, city, region, or "near me") but is NOT a route.

**Detection signals:**
- Contains a US state name (all 50 + DC + territories)
- Contains a major metro/city name
- Contains "near me", "in [city]", "in my area", "[city] area"
- Does NOT match Route pattern (no second location)

**US state list (match case-insensitively):**
alabama, alaska, arizona, arkansas, california, colorado, connecticut, delaware, florida, georgia, hawaii, idaho, illinois, indiana, iowa, kansas, kentucky, louisiana, maine, maryland, massachusetts, michigan, minnesota, mississippi, missouri, montana, nebraska, nevada, new hampshire, new jersey, new mexico, new york, north carolina, north dakota, ohio, oklahoma, oregon, pennsylvania, rhode island, south carolina, south dakota, tennessee, texas, utah, vermont, virginia, washington, west virginia, wisconsin, wyoming, puerto rico, district of columbia

**Sub-grouping:** Group by state/city, show total opportunity per location.

## 3. Cost/Calculator/Pricing Pages

**Pattern:** Keyword is about cost, pricing, quotes, estimates, or calculators.

**Detection signals (any of):**
- Contains: cost, price, pricing, quote, calculator, estimate, rates, fee, fees, "how much"
- Contains: cheap, cheapest, affordable, low cost, budget, discount, free
- Implies pricing research or comparison shopping

**Examples across industries:**
- "web design cost per page"
- "personal injury lawyer fees"
- "roof replacement estimate"
- "how much does SEO cost"

## 4. Product/Offering Subtype Pages

**Pattern:** Keyword specifies a particular sub-type of the client's core product or service offering.

**This category is dynamic — discover the subtypes from the data.** Scan the keyword list for recurring nouns or modifiers that narrow the client's main offering into specific variants.

**How to discover subtypes:**
1. Look at the client's existing pages (from the Pages CSV) for product/service categories they already target
2. Scan the keyword gap data for recurring modifiers that appear with the client's core terms
3. Group keywords that share a common product/offering modifier

**Examples by industry:**
- **Legal:** personal injury, family law, estate planning, DUI defense, immigration
- **Home services:** bathroom remodel, kitchen renovation, roof repair, gutter installation
- **SaaS:** CRM software, project management tool, email marketing platform
- **E-commerce:** running shoes, hiking boots, dress shoes, sandals
- **Healthcare:** knee replacement, dental implants, laser eye surgery

**The key signal:** The keyword adds a specificity modifier to the client's general service that would warrant its own dedicated page.

## 5. Service Method/Tier Pages

**Pattern:** Keyword specifies a particular delivery method, service level, or operational approach — not WHAT is offered, but HOW it's delivered.

**This category is also dynamic.** Look for recurring modifiers that describe service delivery rather than service type.

**Common cross-industry patterns:**
- Delivery speed: same-day, next-day, expedited, rush, overnight, standard
- Service scope: full-service, DIY, self-service, managed, consultation-only
- Client segment: residential, commercial, enterprise, small business, B2B, wholesale, government, military
- Geography: local, nationwide, international, remote, on-site, virtual, online
- Quality tier: premium, budget, luxury, basic, professional, certified

**Examples by industry:**
- **Legal:** free consultation, contingency fee, flat rate
- **Home services:** emergency repair, scheduled maintenance, same-day service
- **Marketing:** managed service, done-for-you, white-label, self-service

## 6. How-To / Informational Pages

**Pattern:** Keyword asks a question or seeks educational content.

**Detection signals:**
- Starts with: how, what, why, when, where, can, should, do, does, is, are, will
- Contains: guide, tips, tutorial, explained, 101, checklist, steps, process, learn
- Contains: "how to", "what is", "how does", "how do", "do I need"
- Educational/research intent

**Examples across industries:**
- "how to choose a contractor"
- "what is a demand letter"
- "do I need a permit for a deck"
- "SEO best practices 2026"

## 7. Company/Comparison Pages

**Pattern:** Keyword is about finding, comparing, or evaluating providers/companies.

**Detection signals:**
- Contains: best, top, companies, company, firms, agencies, providers, reviews, rated, reliable, reputable, trusted
- Contains: vs, versus, comparison, compare, alternative, alternatives
- Contains: cheapest, most affordable (when followed by company/provider words)
- Contains: avoid, scam, legit, worth it

**Examples across industries:**
- "best SEO agencies for small business"
- "top personal injury lawyers near me"
- "cheapest web hosting providers"
- "contractor vs handyman"

## 8. General (Catch-All)

**Pattern:** Generic industry terms that don't fit any specific page type above.

These are broad, high-level keywords that describe the client's overall service/product without any specificity modifier. They're typically captured by the homepage or main category pages as overall site authority grows.

**Examples:** Any core industry term without a location, product subtype, service method, pricing, or question modifier.

## Classification Priority

Apply in this order (first match wins):
1. Route/Location Pair (most specific — requires two locations)
2. State/Location (one location)
3. Cost/Calculator/Pricing (price intent)
4. Product/Offering Subtype (specific product/service variant)
5. Service Method/Tier (how it's delivered)
6. How-To/Informational (question/educational)
7. Company/Comparison (evaluation intent)
8. General (catch-all)

## Dynamic Discovery Process

Before classifying, run a quick scan of the keyword data to discover the client's specific vocabulary:

1. **Extract the top 50 keywords by volume** from the gap data
2. **Identify the core service/product terms** (these will become "General" category terms)
3. **Look for recurring modifiers** that pair with those core terms — these reveal the Product Subtypes and Service Methods for this particular client
4. **Build a working vocabulary** of 10-20 subtype/method keywords before starting classification
5. **Check the client's existing URL structure** (from the Pages CSV) for categories they already use — mirror these in the classification

This ensures the page types reflect the client's actual market, not a preset list from another industry.
