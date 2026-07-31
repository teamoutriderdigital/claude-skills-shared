---
name: article-stock-images
description: Find and insert stock images into articles, then upload to NeuronWriter. Takes a NeuronWriter query ID, downloads the live content, analyzes article structure, finds horizontal stock photos that match each section's theme, inserts them evenly throughout the article plus a hero image below H1, and uploads the result back to NeuronWriter. Use this skill whenever the user wants to add images to an article, find stock photos for a page, insert pictures into content, or add visuals to a NeuronWriter page. Also triggers for "find images for [page]", "add stock images", "insert photos into the article", or any request involving illustrating written content with stock photography.
---

# Article Stock Images

Automated workflow: download article from NeuronWriter → analyze sections → find matching horizontal stock images → insert at ~1MP resolution → upload back to NeuronWriter.

## Input

The user provides a **NeuronWriter query ID** (e.g., `dc7bdba5b80fb8ed`). This is the only required input.

## Prerequisites

Before starting, verify these files exist in the current working directory:

1. **`fetch_neuronwriter.py`** — Script to pull content from NeuronWriter
2. **`upload_to_neuronwriter.py`** — Script to upload content back to NeuronWriter
3. **`config.json`** — Must contain `apiKey` for NeuronWriter API

Use `Glob` to check. Do NOT proceed if any are missing.

---

## Phase 1: Download Live Content

Always fetch fresh content from NeuronWriter. Never use a local file that may already exist.

Run the fetch script:

```
echo "{QUERY_ID}" | python fetch_neuronwriter.py
```

This produces:
- `{keyword}-content.md` — Current article content in Markdown
- `{keyword}-requirements.json` — NeuronWriter query metadata

Read both files. Extract:
- The **keyword** and **query_id** from the requirements JSON
- The full article content from the content markdown

---

## Phase 2: Analyze Article Structure

Read the content file and determine:

1. **Word count** — Count words in the body (below the H1). Exclude YAML frontmatter and the SEO metadata block above the H1.
2. **Section map** — List every H2 heading and summarize its topic in 3-5 words. This summary drives the image search queries.
3. **Number of body images needed:**
   - Articles under 1,000 words: **3 body images**
   - Articles 1,000 words or more: **1 image per 400 words** (round to nearest integer, minimum 3)
4. **Hero image** — 1 additional image placed directly below the H1 heading. This image should represent the article's overall topic broadly, not a specific section.

**Total images = 1 hero + N body images.**

### Placement Strategy

Body images should be distributed evenly across the article. Place each image **after** the last paragraph of its target section, immediately before the next H2 heading. The goal is visual rhythm: a reader scrolling should encounter images at roughly equal intervals.

To calculate placement:
- Divide the total number of H2 sections by the number of body images needed
- Place images at those interval points
- Prefer placing images after sections whose themes produce strong visual search results (foundry shots, machine close-ups, finished parts) over abstract sections (cost analysis, decision frameworks)

---

## Phase 3: Find Stock Images

Use the `mcp__stock-images-mcp__search_stock_images` tool to search for images. Run all searches in parallel when possible.

### Search Strategy

For each image slot:

1. **Compose a search query** based on the section's theme. Use concrete, visual nouns. Good queries describe what a photo would literally show:
   - Good: `"CNC milling machine cutting aluminum part coolant"`, `"molten metal pouring sand casting mold foundry workers"`
   - Bad: `"cost optimization manufacturing"`, `"quality standards comparison"`

2. **Search across all platforms** (set `platform: "all"`). Request 5 results per platform (`per_page: 5`).

3. **For the hero image**, search for the article's primary topic at a broader level. If the article is about "ductile iron vs carbon steel", search for something like `"iron steel metal industrial manufacturing"`.

### Selection Criteria

From each search result set, pick the best image using these rules in priority order:

1. **Horizontal orientation only.** The image width must be greater than its height. Check the dimensions in the search results. Reject any image where height >= width.
2. **Relevance to the section.** The image should visually represent what the section discusses. Prefer images showing the actual process, material, or equipment described.
3. **No duplicate images.** Never use the same image (same URL or same Pexels/Unsplash/Pixabay ID) twice in one article.
4. **No duplicate images across articles.** Track which images were used in prior runs during the same session. Avoid reusing the same stock photos across different articles when possible.
5. **Professional quality.** Prefer images with clear subjects, good lighting, and industrial/manufacturing context over artistic or abstract shots.

If a search returns no suitable horizontal images, try a different query with alternative keywords. Do not settle for vertical images.

---

## Phase 4: Insert Images

### Image URL Format

All images must use a resolution parameter that produces approximately 1 megapixel output. Append `?auto=compress&cs=tinysrgb&w=1280` to Pexels URLs. For Unsplash, use `&w=1280`. For Pixabay, use the 1280-width URL provided in the results.

### Markdown Format

Insert each image as a standard Markdown image tag:

```markdown
![Descriptive alt text matching the image content](https://images.pexels.com/photos/XXXXX/pexels-photo-XXXXX.jpeg?auto=compress&cs=tinysrgb&w=1280)
```

### Alt Text Rules

- Describe what the image literally shows, not the section topic
- Keep under 125 characters
- Do not stuff keywords or include the article title
- Example: `"Molten metal being poured from a ladle in an industrial foundry"`

### Insertion Points

- **Hero image:** Insert immediately after the H1 line (and after any introductory text on the same line as H1, if any). Place it before the first body paragraph or Key Takeaways section.
  - If there is an intro paragraph between the H1 and the first H2 (like Key Takeaways), place the hero image between the H1 and that intro paragraph.
- **Body images:** Insert after the last paragraph of the target section, with a blank line above and below, immediately before the next `## ` heading.

### Fix Broken List Formatting

The fetch script sometimes produces broken markdown lists where the dash and the text are separated by blank lines:

```markdown
-

Apparent labor savings of 20-30%...
```

This renders as empty bullet points in NeuronWriter. Before saving the optimized file, run this fix:

```python
import re
content = re.sub(r'^- \n\n', '- ', content, flags=re.MULTILINE)
content = re.sub(r'^(\d+)\. \n\n', r'\1. ', content, flags=re.MULTILINE)
```

This collapses `- \n\nText` into `- Text` for proper list rendering. This is a formatting fix, not a content change.

### Content Integrity

**Do NOT modify any existing content.** The only changes to the file should be:
- Inserted image markdown lines
- The list formatting fix above

Do not:
- Change any text, headings, or wording
- Remove or reorder any content
- Modify links or metadata
- Change the SEO title, meta description, or URL slug

---

## Phase 5: Upload to NeuronWriter

### Step 5.1 — Prepare the Optimized File

Save the article with inserted images as `{keyword}-optimized.md` in the working directory.

### Step 5.2 — Upload with Title

Do NOT use `upload_to_neuronwriter.py` for this skill. That script does not pass the title field, which results in a lower content score in NeuronWriter. Instead, upload directly via Python using the `import-content` API endpoint with both `html` and `title` fields in a single call.

Extract the SEO Title from the article's metadata block (the line starting with `**SEO Title:**`). This becomes the NeuronWriter document title that appears above the body content editor.

```python
import requests, json, markdown, re

with open('config.json', 'r') as f:
    api_key = json.load(f)['apiKey']

with open('{keyword}-optimized.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# Extract SEO Title
title_match = re.search(r'\*\*SEO Title:\*\*\s*(.+)', md_content)
title = title_match.group(1).strip() if title_match else ''

# Ensure blank lines around SEO metadata labels for proper paragraph rendering
lines = md_content.split('\n')
result = []
for line in lines:
    if re.match(r'^\*\*(?:SEO Title|URL|Meta Description)', line):
        if result and result[-1].strip() != '':
            result.append('')
        result.append(line)
        result.append('')
    else:
        result.append(line)
md_content = '\n'.join(result)

# Convert markdown to HTML
html_content = markdown.markdown(md_content, extensions=['tables', 'sane_lists'])

# Upload with title
resp = requests.post(
    'https://app.neuronwriter.com/neuron-api/0.5/writer/import-content',
    headers={'X-API-KEY': api_key},
    json={'query': '{query_id}', 'html': html_content, 'title': title}
)
resp.raise_for_status()
print(resp.json())
```

Report the content score returned by NeuronWriter.

### Step 5.4 — Clean Up

Move intermediate files to `processed/`:

```bash
mkdir -p processed
mv {keyword}-content.md {keyword}-requirements.json processed/
```

Keep `{keyword}-optimized.md` in the working directory for reference.

---

## Phase 6: Report

Print a summary including:
- Number of images inserted (1 hero + N body)
- Article word count
- Each image: position (after which section), alt text, source platform, and URL
- NeuronWriter content score after upload

---

## Important Reminders

1. **Always download fresh content.** Never reuse a local `-content.md` file from a previous run. The NeuronWriter version is the source of truth.
2. **Horizontal images only.** Width must exceed height. No exceptions.
3. **~1MP resolution.** Use `w=1280` parameter on all image URLs.
4. **Do not modify content.** Only add image markdown lines. Everything else stays untouched.
5. **Search all platforms.** Do not limit searches to a single stock photo provider.
6. **Alt text describes the photo, not the article.** Write what a person would see in the image.
7. **Even distribution.** Images should create visual rhythm for the reader scrolling through the article.
