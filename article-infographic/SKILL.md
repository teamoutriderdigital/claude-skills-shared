---
name: article-infographic
description: |
  Generate tall infographics for articles and pages. Uses Gemini 3.1 Flash Image API to produce a single tall 9:16 image at 2K resolution with accurate text rendering, then uploads to Google Drive and returns a ready-to-use thumbnail link. Use this skill whenever the user wants to create an infographic for an article, blog post, or page. Also triggers for "make an infographic about", "create an infographic for", "generate an infographic", "design an infographic", "infographic showing", or any request to create a visual infographic summarizing information for content.
---

# Article Infographic Generator

Generate tall infographics via the Gemini 3.1 Flash Image API (9:16 aspect ratio, 2K resolution), upload to Google Drive, and return a thumbnail link.

## Input

The user provides a **text prompt** describing the infographic. The prompt should describe:
- The topic and title of the infographic
- The key data points, steps, facts, or sections to include
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

## Phase 1: Generate the Infographic

Build and run a Python script that calls the Gemini 3.1 Flash Image API with fixed settings optimized for tall infographics.

### Prompt Construction

Wrap the user's prompt with infographic-specific rendering guidance:

```
Create a tall, visually engaging infographic with the following requirements:
- Use a clear visual hierarchy: bold title at top, distinct sections flowing top to bottom
- All text must be perfectly legible and spelled correctly
- Use clear, bold fonts with high contrast against the background
- Numbers and data labels must be precisely accurate
- Use icons or simple illustrations to support each section
- Maintain consistent styling throughout: same fonts, colors, and spacing
- Ensure adequate spacing between sections for readability
- Include a clear title/header at the top and a conclusion/footer at the bottom

Infographic to create:
{user_prompt}
```

### Python Script

Generate and run this script (adapt the prompt):

```python
import json
import sys
import base64
from google import genai

with open('config.json') as f:
    config = json.load(f)

client = genai.Client(api_key=config['geminiApiKey'])

prompt = """Create a tall, visually engaging infographic with the following requirements:
- Use a clear visual hierarchy: bold title at top, distinct sections flowing top to bottom
- All text must be perfectly legible and spelled correctly
- Use clear, bold fonts with high contrast against the background
- Numbers and data labels must be precisely accurate
- Use icons or simple illustrations to support each section
- Maintain consistent styling throughout: same fonts, colors, and spacing
- Ensure adequate spacing between sections for readability
- Include a clear title/header at the top and a conclusion/footer at the bottom

Infographic to create:
{USER_PROMPT_HERE}"""

interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input=prompt,
    generation_config={{"thinking_level": "high"}},
    response_format={{
        "type": "image",
        "mime_type": "image/jpeg",
        "aspect_ratio": "9:16",
        "image_size": "2K"
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

Use a descriptive output filename, e.g., `seo-steps-infographic.png`, `remote-work-benefits-infographic.png`.

### If Generation Fails

If the API returns an error or no image:
- Simplify the prompt — reduce the number of sections or data points
- Remove overly specific layout instructions
- Retry up to 2 times with modified prompts

---

## Phase 2: Upload to Google Drive

Upload the generated infographic to Google Drive and make it publicly accessible. Reads credentials from `config.json`. Uses domain-wide delegation to impersonate the delegate email.

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

service.permissions().create(
    fileId=file_id,
    body={'type': 'anyone', 'role': 'reader'}
).execute()

print(f'File uploaded and shared. ID: {file_id}')
```

---

## Phase 3: Return the Link

Construct the thumbnail URL:

```
https://drive.google.com/thumbnail?id={FILE_ID}&sz=w1000
```

Present the link to the user. Delete the local image file after successful upload.

---

## Output Format

After completion, present:

```
Infographic generated and uploaded to Google Drive.

Thumbnail link:
https://drive.google.com/thumbnail?id={FILE_ID}&sz=w1000
```
