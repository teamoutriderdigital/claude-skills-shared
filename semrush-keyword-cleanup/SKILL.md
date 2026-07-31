---
name: semrush-keyword-cleanup
description: Cleans up SEMrush organic keyword export files. Removes unnecessary columns, filters by position, sorts by URL/Traffic/Search Volume, and keeps top keywords per URL. Use when processing SEMrush keyword research Excel files.
allowed-tools: Bash, Glob, Read
---

# SEMrush Keyword Cleanup

Process SEMrush organic keyword export Excel files (.xlsx) with a 4-step cleanup.

## What This Skill Does

1. **Delete unnecessary columns**: Traffic (%), Traffic Cost, Competition, Number of Results, Trends, Timestamp, SERP Features by Keyword
2. **Sort data**: By URL (A-Z), then Traffic (highest first), then Search Volume (highest first)
3. **Filter by position**: Remove rows where Position >= 50
4. **Keep top keywords**: Retain only top 15 rows per URL

## Instructions

When the user invokes this skill, run the following Python script on all `.xlsx` files in the current directory (excluding temp files starting with `~$`):

```python
import pandas as pd
import glob
import os

# Get all xlsx files (excluding temp files)
files = [f for f in glob.glob('*.xlsx') if not os.path.basename(f).startswith('~$')]

columns_to_delete = [
    'Traffic (%)',
    'Traffic Cost',
    'Competition',
    'Number of Results',
    'Trends',
    'Timestamp',
    'SERP Features by Keyword'
]

for file in files:
    print(f'Processing: {os.path.basename(file)}')
    try:
        df = pd.read_excel(file)

        # Step 1: Delete unnecessary columns
        cols_to_drop = [col for col in columns_to_delete if col in df.columns]
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)
            print(f'  Deleted columns: {cols_to_drop}')

        # Step 2: Sort by URL, Traffic, Search Volume
        df = df.sort_values(by=['URL', 'Traffic', 'Search Volume'], ascending=[True, False, False])
        print('  Sorted by URL, Traffic, Search Volume')

        # Step 3: Remove rows where Position >= 50
        rows_before = len(df)
        df = df[df['Position'] < 50]
        print(f'  Removed {rows_before - len(df)} rows with Position >= 50')

        # Step 4: Keep only top 15 rows per URL
        rows_before = len(df)
        df = df.groupby('URL', sort=False).head(15)
        print(f'  Kept top 15 per URL (removed {rows_before - len(df)} rows)')

        # Save
        df.to_excel(file, index=False)
        print(f'  Saved! Final row count: {len(df)}')

    except PermissionError:
        print('  SKIPPED - file is open in another program')
    except Exception as e:
        print(f'  ERROR: {e}')

print('\nDone!')
```

## Usage

User can invoke with: `/semrush-keyword-cleanup`

Make sure all Excel files to process are in the current working directory and are closed (not open in Excel).

## Requirements

- Python with pandas and openpyxl installed
- Excel files must be SEMrush organic positions exports with standard column names
