---
name: article-ai-images
description: Generate AI images and insert them into articles, then upload to NeuronWriter. Takes a NeuronWriter query ID, downloads the live content, analyzes article structure, generates horizontal 16:9 AI images using the Gemini 3.1 Flash Image API that match each section's theme, inserts them evenly throughout the article plus a featured image below H1, uploads images to Google Drive, and uploads the final article back to NeuronWriter. Use this skill whenever the user wants to add AI-generated images to an article, create custom images for a page, generate illustrations for content, or add AI visuals to a NeuronWriter page. Also triggers for "generate images for [page]", "add AI images", "create images for the article", "illustrate article with AI", or any request involving generating custom images for written content.
---

# Article AI Images

Automated workflow: download article from NeuronWriter → analyze sections → generate matching AI images with Gemini 3.1 Flash Image API → upload images to Google Drive → insert into article → upload back to NeuronWriter.

## Input

The user provides a **NeuronWriter query ID** (e.g., `dc7bdba5b80fb8ed`). This is the only required input.

## Prerequisites

Before starting, verify these files and tools exist:

1. **`fetch_neuronwriter.py`** — Script to pull content from NeuronWriter (in working directory)
2. **`config.json`** — Must contain `apiKey` (NeuronWriter), `geminiApiKey`, and `googleDrive` fields (in working directory):
   ```json
   {
     "apiKey": "...",
     "geminiApiKey": "...",
     "googleDrive": {
       "folderId": "...",
       "delegateEmail": "team@outriderdigital.com",
       "serviceAccount": { ... }
     }
   }
   ```
3. **Python `google-genai` library** (v2.0.0+) — `python -c "from google import genai; print('OK')"`
4. **Python `google-api-python-client` and `google-auth` libraries** — `python -c "from googleapiclient.discovery import build; from google.oauth2 import service_account; print('OK')"`
5. **Python `markdown` library** — `python -c "import markdown; print('OK')"`

If any Python library is missing, install:
```bash
pip install google-genai google-api-python-client google-auth markdown
```

Use `Glob` and `Bash` to check. Do NOT proceed if any required item is missing.

**Optional:** `branding/` folder in working directory containing brand images (logos, signage, uniform photos). Only used when the article promotes a specific business.

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
2. **Section map** — List every H2 heading and summarize its topic in 3-5 words. This summary drives the image generation prompts.
3. **Detect existing images** — Scan the entire article for markdown image tags (`![...](...)`) that are already present. For each existing image found, record:
   - Its position in the article (which section/H2 it falls under, or "after H1" for featured position)
   - Whether it occupies the **featured slot** (between the H1 and the first body paragraph or Key Takeaways)
   - Which **section slot** it occupies (the H2 section it appears after/within)
4. **Number of body images needed (adjusted):**
   - Calculate the raw target: `ceil(word_count / 500)`
   - Subtract the number of existing body images (images NOT in the featured slot) from this raw target
   - If the result is 0 or negative, no body images need to be generated
   - Examples: raw target 4 with 2 existing body images → generate 2 new body images
5. **Featured image (adjusted):**
   - If an image already exists in the featured slot (between H1 and first paragraph/Key Takeaways), do NOT generate a featured image
   - If no featured image exists, generate 1 featured image as usual
6. **Total images to generate = (0 or 1 featured, based on check) + adjusted body image count.**

If all slots are already filled (total to generate = 0), report that the article already has sufficient images and skip Phases 3-6. Proceed directly to Phase 9 with a summary.

### Placement Strategy

Body images should be distributed evenly across the article, BUT must avoid sections that already contain an image. Place each new image **after** the last paragraph of its target section, immediately before the next H2 heading. The goal is visual rhythm: a reader scrolling should encounter images at roughly equal intervals.

To calculate placement:
- Build a list of all H2 sections
- Mark which sections are **occupied** (already contain an image)
- From the remaining **unoccupied** sections, select placement points that maintain even visual spacing across the full article (not just among unoccupied sections — consider occupied slots as part of the rhythm)
- Prefer placing images after sections whose themes produce strong visual imagery over abstract sections (cost analysis, decision frameworks)

**Example:** Article has 8 H2 sections, raw target is 4 body images, and sections 2 and 5 already have images. That means 2 new body images are needed. The occupied slots (2, 5) already provide rhythm at those points. Place the 2 new images in unoccupied sections that best fill the gaps — e.g., sections 4 and 7 — to maintain even spacing across all 8 sections.

---

## Phase 3: Check Branding

1. Use `Glob` to check if a `branding/` folder exists in the working directory (`branding/*`).

**If the `branding/` folder exists**, branding images are MANDATORY for ALL generated images:
- Read all image files from the `branding/` folder — these will be passed as reference images to the Gemini API alongside the text prompt
- **Every image generation script MUST include the branding images as `types.Part.from_bytes()` in the `contents` list.** This applies to ALL images — featured and body images alike. The model needs these input images to incorporate the brand's visual identity (logos, uniform style, signage design) naturally into every scene.
- Each image should depict its section topic while naturally incorporating brand elements (logos, signage, colors, uniforms) from the branding folder
- Keep it natural and authentic — the brand elements should be woven into realistic scenes, not logo mockups

**If the `branding/` folder does not exist**, skip branding entirely. Generate only generic topic images.

---

## Phase 4: Generate AI Images

Use the Gemini 3.1 Flash Image API via Python scripts for all image generation. Generate images efficiently by running multiple `Bash` tool calls in parallel, each executing an independent Python script for one image.

### Fixed Parameters for ALL Images

Every image generation script MUST use these exact settings:

- **Model:** `gemini-3.1-flash-image`
- **Aspect ratio:** `16:9` — Widescreen horizontal format.
- **Output format:** JPEG — Images are saved as `.jpg` files.
- **No-text instruction:** Every prompt MUST include: "Do not include any text, watermarks, logos, words, letters, typography, numbers, captions, subtitles, or title overlays in the image."
- **Output filenames:** Save to the working directory with descriptive filenames:
  - Featured image: `{keyword}-img-featured.jpg`
  - Body images: `{keyword}-img-1.jpg`, `{keyword}-img-2.jpg`, etc.

### Prompt Style

All prompts should request **photorealistic, stock-photo-style imagery** but with creative variety across the set. Vary these elements across different images in the same article:

- **Angles:** overhead/bird's-eye, close-up macro, wide establishing shot, eye-level, low angle looking up, Dutch angle
- **Zoom/framing:** tight crop on detail, medium shot, wide environmental scene
- **Lighting:** natural daylight, studio lighting, golden hour warmth, dramatic side lighting, soft diffused light
- **Depth of field:** shallow bokeh background blur, deep focus showing full scene, tilt-shift miniature effect

Each prompt should clearly specify: **subject** (what is shown), **composition** (angle and framing), **lighting**, and **setting/environment**.

### Prompt Construction

Wrap each image prompt with this rendering guidance:

```
Create a photorealistic, stock-photo-style image with the following requirements:
- Photorealistic quality suitable for a professional article
- Do not include any text, watermarks, logos, words, letters, typography, numbers, captions, subtitles, or title overlays in the image
- High-quality, natural lighting and composition

Image to create:
{SECTION_SPECIFIC_PROMPT}
```

### Python Script (without branding)

Generate and run this script for each image (adapt the prompt and output filename):

```python
import json, sys, base64
from google import genai
from google.genai import types

with open('config.json') as f:
    config = json.load(f)

client = genai.Client(api_key=config['geminiApiKey'])

prompt = """Create a photorealistic, stock-photo-style image with the following requirements:
- Photorealistic quality suitable for a professional article
- Do not include any text, watermarks, logos, words, letters, typography, numbers, captions, subtitles, or title overlays in the image
- High-quality, natural lighting and composition

Image to create:
{SECTION_SPECIFIC_PROMPT}"""

response = client.models.generate_content(
    model='gemini-3.1-flash-image',
    contents=prompt,
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
        ),
    ),
)

for part in response.parts:
    if part.inline_data:
        with open("{OUTPUT_FILENAME}", "wb") as f:
            f.write(part.inline_data.data)
        print(f"Image saved: {OUTPUT_FILENAME}")
        break
else:
    print("ERROR: No image was generated", file=sys.stderr)
    sys.exit(1)
```

### Python Script (with branding)

When branding is active (Phase 3 found a `branding/` folder), pass the branding images as reference inputs alongside the text prompt using `types.Part.from_bytes()`:

```python
import json, sys, glob
from google import genai
from google.genai import types

with open('config.json') as f:
    config = json.load(f)

client = genai.Client(api_key=config['geminiApiKey'])

# Load branding images as Parts
branding_parts = []
for img_path in sorted(glob.glob('branding/*')):
    with open(img_path, 'rb') as f:
        img_bytes = f.read()
    ext = img_path.lower().rsplit('.', 1)[-1]
    mime = 'image/jpeg' if ext in ('jpg', 'jpeg') else 'image/png'
    branding_parts.append(types.Part.from_bytes(data=img_bytes, mime_type=mime))

prompt = """Create a photorealistic, stock-photo-style image with the following requirements:
- Photorealistic quality suitable for a professional article
- Do not include any text, watermarks, logos, words, letters, typography, numbers, captions, subtitles, or title overlays in the image
- High-quality, natural lighting and composition
- Naturally incorporate the brand elements shown in the reference images (logos, signage, colors, uniforms) into the scene

Image to create:
{SECTION_SPECIFIC_PROMPT}"""

contents = branding_parts + [prompt]

response = client.models.generate_content(
    model='gemini-3.1-flash-image',
    contents=contents,
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
        ),
    ),
)

for part in response.parts:
    if part.inline_data:
        with open("{OUTPUT_FILENAME}", "wb") as f:
            f.write(part.inline_data.data)
        print(f"Image saved: {OUTPUT_FILENAME}")
        break
else:
    print("ERROR: No image was generated", file=sys.stderr)
    sys.exit(1)
```

### Featured Image

- Represents the article's overall topic at a broad level
- Must be visually striking and work as a standalone hero/thumbnail
- No text of any kind
- Use a wider, more dramatic composition than body images

### Branding (if `branding/` folder exists)

When branding is active (Phase 3 found a `branding/` folder), **every image generation script** must include the branding images as `types.Part.from_bytes()` in the `contents` list (use the "with branding" script variant above). This applies to the featured image and all body images — not just one slot. The model uses these references to naturally incorporate brand elements (logo, signage, colors, uniform style) into each scene. Each image should still match its section topic — the branding elements are woven in, not the focus.

### If Generation Fails

If the Gemini API returns an error or produces an unsatisfactory result, modify the prompt and regenerate. Try:
- Simplifying the prompt
- Removing specific details that may confuse the model
- Using different compositional language
- Retry up to 2 times with modified prompts

### Replacing Images

When the user asks to replace one or more images after the initial run:

1. **Generate new images** with different prompts/compositions for the slots being replaced.
2. **Use new filenames with a version suffix** — append a letter suffix to the image name so they get unique Google Drive file IDs:
   - First replacement: `img-2b.jpg`, `img-3b.jpg`
   - Second replacement: `img-2c.jpg`, `img-3c.jpg`
   - And so on alphabetically
3. **Upload to Google Drive** with the new filenames so they get unique thumbnail URLs.
4. **Update the optimized markdown** — replace the old image URLs and alt text with the new ones.
5. **Re-upload to NeuronWriter** using the same upload flow (strip frontmatter, tighten lists, convert to HTML, upload with title).
6. **Local files** — save the new images with the suffixed filenames (e.g., `{keyword}-img-2b.jpg`). After uploading to Google Drive, delete both the old and new local image files.

---

## Phase 5: Upload Images to Google Drive

Read credentials from `config.json` (`googleDrive` section). Upload each image to the Google Drive folder using domain-wide delegation, set public permissions, and construct thumbnail URLs.

```python
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

with open('config.json') as f:
    config = json.load(f)

gd = config['googleDrive']
SCOPES = ['https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_info(
    gd['serviceAccount'], scopes=SCOPES
)
delegated = credentials.with_subject(gd['delegateEmail'])
service = build('drive', 'v3', credentials=delegated)

keyword = '{keyword}'
files = [
    f'{keyword}-img-featured.jpg',
    f'{keyword}-img-1.jpg',
    f'{keyword}-img-2.jpg',
    # ... for each generated image
]

for local_file in files:
    file_metadata = {
        'name': local_file,
        'parents': [gd['folderId']]
    }
    media = MediaFileUpload(local_file, mimetype='image/jpeg')
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = file.get('id')

    # Make publicly accessible
    service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    url = f'https://drive.google.com/thumbnail?id={file_id}&sz=w1200'
    print(f'{local_file} -> {url}')
```

Store the mapping of local filenames to Google Drive thumbnail URLs — these are needed for inserting images into the article in Phase 6.

---

## Phase 6: Insert Images into Article

### Markdown Format

Insert each image as a standard Markdown image tag using the Google Drive thumbnail URL:

```markdown
![Descriptive alt text matching the image content](https://drive.google.com/thumbnail?id={FILE_ID}&sz=w1200)
```

### Alt Text Rules

- Describe what the image literally shows, not the section topic
- Keep under 125 characters
- Do not stuff keywords or include the article title
- Example: `"Molten metal being poured from a ladle in an industrial foundry"`

### Insertion Points

- **Featured image:** Insert immediately after the H1 line. Place it before the first body paragraph or Key Takeaways section. If there is an intro paragraph between the H1 and the first H2, place the featured image between the H1 and that intro paragraph.
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

## Phase 7: Upload to NeuronWriter

### Step 7.1 — Prepare the Optimized File

Save the article with inserted images as `{keyword}-optimized.md` in the working directory.

### Step 7.2 — Upload with Title

Do NOT use `upload_to_neuronwriter.py` for this skill. That script does not pass the title field, which results in a lower content score in NeuronWriter. Instead, upload directly via Python using the `import-content` API endpoint with both `html` and `title` fields in a single call.

Extract the SEO Title from the article's metadata block (the line starting with `**SEO Title:**`). This becomes the NeuronWriter document title.

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

---

## Phase 8: Verify Formatting After Upload

**This phase is critical.** The markdown-to-HTML conversion and NeuronWriter import can break tables, lists, and other formatting. After uploading, re-download the article and verify everything rendered correctly.

### Step 8.1 — Re-download from NeuronWriter

Run the fetch script again with the same query ID:

```
echo "{QUERY_ID}" | python fetch_neuronwriter.py
```

This produces a fresh `{keyword}-content.md` reflecting what NeuronWriter actually stored.

### Step 8.2 — Compare and Check Formatting

Read the re-downloaded content and check for these common formatting problems:

1. **Broken tables** — Verify all markdown tables still have proper pipe (`|`) delimiters, header separator rows (`|---|---|`), and correct column alignment. Tables should not be collapsed into plain text or have missing cells.

2. **Broken lists** — Check that all bullet lists (`- item`) and numbered lists (`1. item`) render as proper list items. Watch for:
   - Bare dashes (`-`) on their own line separated from content
   - List items that lost their dash/number prefix
   - Nested lists that lost indentation

3. **Broken headings** — Verify all `## H2` and `### H3` headings are intact and not merged into paragraph text.

4. **Image tags present** — Confirm all inserted `![alt text](URL)` image tags survived the round-trip. Count them — the number should match what was inserted.

5. **Merged paragraphs** — Check that separate paragraphs didn't get concatenated into a single block. Look for missing blank lines between paragraphs.

6. **SEO metadata block** — Verify the `**SEO Title:**`, `**URL:**`, and `**Meta Description:**` lines are still properly formatted as separate bold-labeled lines.

7. **Links** — Verify `[anchor text](URL)` links are intact and not broken into plain text.

### Step 8.3 — Fix and Re-upload if Needed

If ANY formatting issues are found:

1. Start from the `{keyword}-optimized.md` file (the pre-upload version that was correct)
2. Identify what caused the breakage — usually one of:
   - Missing blank lines before/after tables (tables need blank lines above and below to render)
   - Missing blank lines before/after lists
   - Markdown library not handling a specific construct (try adding `'extra'` to the extensions list)
3. Apply targeted fixes to the optimized markdown
4. Re-convert to HTML and re-upload using the same upload code from Phase 7
5. Re-download and verify again
6. Repeat until the formatting is clean (maximum 3 attempts)

**Common fixes:**
- Add blank lines before and after every table
- Add blank lines before and after every list block
- Ensure table header separators use at least 3 dashes: `|---|---|`
- For multi-line list items, ensure continuation lines are indented

### Step 8.4 — Clean Up

Only after formatting verification passes, clean up local files:

```bash
mkdir -p processed
mv {keyword}-content.md {keyword}-requirements.json processed/

# Delete local image files — they are already uploaded to Google Drive
rm -f {keyword}-img-featured.jpg {keyword}-img-*.jpg
```

Keep `{keyword}-optimized.md` in the working directory for reference. Delete all generated image `.jpg` files since they have been uploaded to Google Drive and are no longer needed locally.

---

## Phase 9: Report

Print a summary including:
- Existing images detected (count, positions, and whether featured slot was occupied)
- Number of new images generated (featured + body breakdown)
- Article word count
- Each new image: position (after which section), alt text, generation prompt used, Google Drive thumbnail URL
- Whether branding was applied and to which images
- NeuronWriter content score after upload
- Formatting verification result: PASS or list of issues found and fixed

---

## Important Reminders

1. **Always download fresh content.** Never reuse a local `-content.md` file from a previous run. The NeuronWriter version is the source of truth.
2. **Always use `gemini-3.1-flash-image` model.** Use `client.models.generate_content()` with `response_modalities=["IMAGE"]` and `image_config=types.ImageConfig(aspect_ratio="16:9")`.
3. **16:9 widescreen.** Every image uses `aspect_ratio: "16:9"`.
4. **No text in images.** The no-text instruction must be included in every generation prompt.
5. **Do not modify content.** Only add image markdown lines. Everything else stays untouched.
6. **Alt text describes the image, not the article.** Write what a person would see in the image.
7. **Even distribution.** Images should create visual rhythm for the reader scrolling through the article.
8. **Branding is limited to ONE image maximum**, only when `branding/` folder exists AND article is promotional. That one branding image **MUST** include branding folder images as `types.Part.from_bytes()` reference inputs — never generate it without the reference images.
9. **Google Drive upload required.** All images must be uploaded to Google Drive and referenced by thumbnail URL. Never embed base64 or use local file paths in the article.
10. **Generate efficiently.** Run multiple Python generation scripts in parallel via separate `Bash` tool calls to save time.
11. **Respect existing images.** Always scan for existing `![...](...)` tags before calculating how many images to generate. Subtract existing images from the target count and skip their occupied slots during placement. Never double-up images in the same section or generate a featured image when one already exists.
