---
name: article-graphic
description: |
  Generate data-driven graphics for articles and pages — bar charts, checklists, comparison tables, process diagrams, step-by-step visuals, statistical charts, timelines, and similar structured visuals. Uses Gemini 3.1 Flash Image API directly to produce images with accurate text rendering, then uploads to Google Drive and returns a ready-to-use thumbnail link. Use this skill whenever the user wants to create a chart, checklist graphic, comparison visual, process diagram, timeline, or any structured data graphic for an article or page. Also triggers for "make a bar chart for", "create a checklist image", "generate a comparison table graphic", "visualize these stats", "create a process diagram", or any request to turn structured data into a visual for content.
---

# Article Graphic Generator

Generate structured data visuals (charts, checklists, tables, diagrams) via the Gemini 3.1 Flash Image API, upload to Google Drive, and return a thumbnail link.

## Input

The user provides a **text prompt** describing the desired graphic. The prompt should describe:
- The type of graphic (bar chart, checklist, comparison table, process diagram, timeline, etc.)
- The data or content to display
- Any specific styling preferences (optional)

## Prerequisites

Before starting, verify these exist:

1. **`config.json`** in the working directory — contains all credentials:
   ```json
   {
     "geminiApiKey": "...",
     "googleDrive": {
       "folderId": "...",
       "delegateEmail": "team@outriderdigital.com",
       "serviceAccount": { ... }
     }
   }
   ```
2. **Python `google-genai` library** (v2.0.0+) — `python -c "from google import genai; print('OK')"`
3. **Python `google-api-python-client` and `google-auth` libraries** — `python -c "from googleapiclient.discovery import build; from google.oauth2 import service_account; print('OK')"`

If any Python library is missing, install:
```bash
pip install google-genai google-api-python-client google-auth
```

Do NOT proceed if `config.json` is missing — ask the user.

---

## Phase 1: Analyze the Prompt and Select Aspect Ratio

Read the user's prompt and determine the best aspect ratio based on the graphic type:

| Graphic Type | Aspect Ratio | Reason |
|---|---|---|
| Bar charts (horizontal bars) | `16:9` | Bars need horizontal space |
| Bar charts (vertical bars) | `4:3` | Balanced for vertical bars with labels |
| Comparison tables (2-3 columns) | `16:9` | Columns need width |
| Checklists, vertical lists | `3:4` | Tall format fits more items |
| Step-by-step processes (horizontal flow) | `16:9` | Left-to-right flow |
| Step-by-step processes (vertical flow) | `3:4` | Top-to-bottom flow |
| Pie charts, donut charts | `1:1` | Circular shape needs square canvas |
| Timelines (horizontal) | `16:9` | Left-to-right chronology |
| Timelines (vertical) | `3:4` | Top-to-bottom chronology |
| Statistical callouts (1-3 big numbers) | `16:9` | Wide banner format |
| Process diagrams, flowcharts | `4:3` | Balanced for complex layouts |
| Default / unclear | `16:9` | Safe horizontal default |

**Checklists are ALWAYS portrait (`3:4`).** Even if the user's prompt specifies landscape or 16:9, override to `3:4` for any graphic that is primarily a checklist or vertical list. Checklists need vertical space to fit all items legibly.

Classify the aspect ratio as **horizontal** (`16:9`, `3:2`, `4:3`, `5:4`, `21:9`, `1:1`) or **vertical** (`2:3`, `3:4`, `4:5`, `9:16`) — this determines the thumbnail URL format later.

---

## Phase 2: Generate the Image

Build and run a Python script that calls the Gemini 3.1 Flash Image API. The script must:

1. Read credentials from `config.json`
2. Wrap the user's prompt with rendering guidance (see Prompt Construction below)
3. Call the Interactions API with `thinking_level: "high"` for accurate text
4. Save the output image

### Prompt Construction

Prepend the user's prompt with this rendering guidance to ensure text accuracy:

```
Create a clean, professional graphic with the following requirements:
- All text must be perfectly legible and spelled correctly
- Use clear, bold fonts with high contrast against the background
- Numbers and data labels must be precisely accurate
- Use a clean, modern design style suitable for a professional article
- No decorative elements that could interfere with readability
- Ensure adequate spacing between all text elements

Graphic to create:
{user_prompt}
```

### Python Script

Generate and run this script (adapt the prompt and aspect_ratio):

```python
import json
import sys
import base64
from google import genai

with open('config.json') as f:
    config = json.load(f)

client = genai.Client(api_key=config['geminiApiKey'])

prompt = """Create a clean, professional graphic with the following requirements:
- All text must be perfectly legible and spelled correctly
- Use clear, bold fonts with high contrast against the background
- Numbers and data labels must be precisely accurate
- Use a clean, modern design style suitable for a professional article
- No decorative elements that could interfere with readability
- Ensure adequate spacing between all text elements

Graphic to create:
{USER_PROMPT_HERE}"""

interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input=prompt,
    generation_config={{"thinking_level": "high"}},
    response_format={{
        "type": "image",
        "mime_type": "image/jpeg",
        "aspect_ratio": "{ASPECT_RATIO}",
        "image_size": "1K"
    }},
)

image_data = interaction.output_image
if image_data:
    with open("{OUTPUT_FILENAME}", "wb") as f:
        f.write(base64.b64decode(image_data.data))
    print(f"Image saved: {OUTPUT_FILENAME}")
else:
    print("ERROR: No image was generated", file=sys.stderr)
    sys.exit(1)
```

Use a descriptive output filename based on the graphic content, e.g., `revenue-bar-chart.png`, `seo-checklist.png`.

### If Generation Fails

If the API returns an error or no image:
- Simplify the prompt — remove complex formatting instructions
- Reduce the amount of text/data in the graphic
- Try a different aspect ratio
- Retry up to 2 times with modified prompts

---

## Phase 3: Upload to Google Drive

Upload the generated image to Google Drive and make it publicly accessible. Reads folder ID, delegate email, and service account credentials from `config.json`. Uses domain-wide delegation to impersonate the delegate email.

Run this Python script (adapt the filename):

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

# Upload file
file_metadata = {
    'name': '{FILENAME}',
    'parents': [gd['folderId']]
}
media = MediaFileUpload('{LOCAL_PATH}', mimetype='image/png')
file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id'
).execute()

file_id = file.get('id')
print(f'FILE_ID={file_id}')

# Make publicly accessible
service.permissions().create(
    fileId=file_id,
    body={'type': 'anyone', 'role': 'reader'}
).execute()

print(f'File uploaded and shared. ID: {file_id}')
```

---

## Phase 4: Return the Link

Construct the thumbnail URL based on orientation:

- **Horizontal or square** (aspect ratios `16:9`, `3:2`, `4:3`, `5:4`, `21:9`, `1:1`):
  ```
  https://drive.google.com/thumbnail?id={FILE_ID}&sz=w1200
  ```

- **Vertical** (aspect ratios `2:3`, `3:4`, `4:5`, `9:16`):
  ```
  https://drive.google.com/thumbnail?id={FILE_ID}&sz=w800
  ```

Present the link to the user. Also delete the local image file after successful upload.

---

## Output Format

After completion, present:

```
Image generated and uploaded to Google Drive.

Thumbnail link:
https://drive.google.com/thumbnail?id={FILE_ID}&sz=w1200

Aspect ratio: 16:9 (horizontal)
```
