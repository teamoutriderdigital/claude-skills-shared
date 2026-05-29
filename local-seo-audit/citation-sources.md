# Citation Sources for NAP Consistency Audit

Check each source below. Use WebFetch to search for the business. Extract Name, Address, Phone, Website URL. Compare against canonical GBP NAP.

## Tier 1: Major Platforms (Always Check)

| # | Source | Search URL Pattern | Priority |
|---|--------|-------------------|----------|
| 1 | **Google Business Profile** | maps.google.com (already audited in Phase 4) | Required |
| 2 | **Yelp** | `https://www.yelp.com/search?find_desc={business_name}&find_loc={city,state}` | Required |
| 3 | **Facebook** | `https://www.facebook.com/search/pages/?q={business_name} {city}` | Required |
| 4 | **BBB** | `https://www.bbb.org/search?find_text={business_name}&find_loc={city,state}` | Required |
| 5 | **Apple Maps** | Search via `https://maps.apple.com/?q={business_name}+{city}` | Required |
| 6 | **Bing Places** | `https://www.bing.com/maps?q={business_name}+{city}+{state}` | Required |

## Tier 2: Directories (Check All)

| # | Source | Search URL Pattern | Priority |
|---|--------|-------------------|----------|
| 7 | **Yellow Pages** | `https://www.yellowpages.com/search?search_terms={business_name}&geo_location_terms={city}+{state}` | High |
| 8 | **MapQuest** | `https://www.mapquest.com/search/{business_name}-{city}-{state}` | High |
| 9 | **Angi (Angie's List)** | `https://www.angi.com/companylist/{city}_{state}/{service}.htm` | High |
| 10 | **Nextdoor** | Search within the platform for business name | Medium |
| 11 | **Foursquare** | `https://foursquare.com/explore?near={city}+{state}&q={business_name}` | Medium |
| 12 | **Manta** | `https://www.manta.com/search?search={business_name}&search_location={city}+{state}` | Medium |

## Tier 3: Industry / Aggregators

| # | Source | Search URL Pattern | Priority |
|---|--------|-------------------|----------|
| 13 | **Thumbtack** | `https://www.thumbtack.com/search/{service}/{city}-{state}` | For service businesses |
| 14 | **HomeAdvisor** | `https://www.homeadvisor.com/rated.{service}.{city}.{state}.html` | For home services |
| 15 | **Houzz** | For home/construction businesses | If applicable |
| 16 | **Local Chamber of Commerce** | Search `{city} chamber of commerce member directory` | Medium |
| 17 | **Google Search** | `"{business_name}" "{phone_number}"` to find other citations | Supplementary |

## What to Check for Each Citation

For every citation found, record:

1. **Name** — Exact business name as listed (check for abbreviations, missing suffixes like LLC/Inc)
2. **Address** — Full street address, suite number, city, state, zip (check for old addresses)
3. **Phone** — Primary number (check for old numbers, tracking numbers, wrong area codes)
4. **Website** — URL listed (check http vs https, www vs non-www, trailing slashes, old domains)
5. **Categories** — What category the business is listed under
6. **Status** — Is the listing claimed/verified by the owner?

## Common Issues to Flag

- Different phone numbers across platforms (especially old/disconnected numbers)
- Address variations (Suite vs Ste vs #, Street vs St, different zip codes)
- Business name variations (Smith Bros vs Smith Brothers vs Smith Bros Mobile Detailing)
- HTTP vs HTTPS website URLs
- Old addresses from a previous location
- Missing citations on platforms where competitors are listed
- Unclaimed listings (not managed by the business owner)
- Duplicate listings on the same platform
