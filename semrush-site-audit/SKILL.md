---
name: semrush-site-audit
description: Run a full SEMrush technical site audit for a client domain. Use this skill whenever the user asks to run a site audit, SEMrush audit, technical SEO audit, or crawl a website in SEMrush. Also use when the user asks to check site health, find SEO errors, or create a new SEMrush project for a domain. The skill finds the correct Chrome profile by email, launches Chrome with remote debugging, creates the SEMrush project, configures audit settings, starts the audit, waits for it to finish, captures the Issues tab screenshot, and saves it to the working directory.
allowed-tools: Bash, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__computer, mcp__claude-in-chrome__read_page, mcp__claude-in-chrome__find, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__get_page_text, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__list_pages, mcp__chrome-devtools__navigate_page
---

# SEMrush Site Audit Skill

Run a complete SEMrush technical site audit for any client domain, from project creation through to a saved screenshot of the Issues tab.

## Configuration

Only one thing needed from the user before running:

| Variable | Description | Example |
|---|---|---|
| `TARGET_DOMAIN` | The domain to audit | `rockymountainpoolbuilders.com` |

The SEMrush account email is always **team@outriderdigital.com** — no need to ask.

## Step 1 — Find the Chrome Profile and Launch

The profile directory name (`Profile 1`, `Profile 2`, etc.) differs between machines, so look it up by the fixed email rather than hardcoding it. This single script finds the profile and launches Chrome with remote debugging in one step:

```powershell
$chromeData = Join-Path $env:LOCALAPPDATA "Google\Chrome\User Data"
$targetEmail = "team@outriderdigital.com"

$profileDir = Get-ChildItem $chromeData -Directory |
  Where-Object { $_.Name -match '^(Default|Profile \d+)$' } |
  ForEach-Object {
    $prefs = Join-Path $_.FullName "Preferences"
    if (Test-Path $prefs) {
      $json = Get-Content $prefs -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
      $email = $json.account_info[0].email
      if (-not $email) { $email = $json.profile.gaia_info_email }
      if ($email -eq $targetEmail) { $_.Name }
    }
  } | Select-Object -First 1

if (-not $profileDir) { Write-Error "Chrome profile for $targetEmail not found"; exit 1 }

Write-Host "Using profile: $profileDir"
Start-Process "chrome.exe" -ArgumentList "--profile-directory=`"$profileDir`"", "--remote-debugging-port=9222", "https://www.semrush.com/siteaudit/"
Start-Sleep -Seconds 4
```

**If `chrome.exe` is not in PATH**, use the full path: `C:\Program Files\Google\Chrome\Application\chrome.exe`

**Port conflict:** If another Chrome instance is already using port 9222, close it first or it will silently fail to enable debugging on the new window.

## Step 3 — Connect to the Chrome Tab

Use `mcp__claude-in-chrome__tabs_context_mcp` to get the current tab list and identify the SEMrush tab.

> **Note:** The claude-in-chrome extension must be installed in the team@outriderdigital.com Chrome profile. If the SEMrush tab doesn't appear in the tab list, the extension is not active in that profile — use the PowerShell navigation fallback at the bottom of this skill.

## Step 4 — Create a New SEMrush Project

Navigate to `https://www.semrush.com/siteaudit/` in the Chrome tab.

On the Site Audit dashboard:
1. Click **"+ Create project"** or **"Set up Site Audit"**
2. Enter `TARGET_DOMAIN` — domain only, no `https://`
3. Click **"Create project"**

If a project for this domain already exists, click into it instead.

## Step 5 — Configure Audit Settings

In the settings dialog, configure each of these — do not accept defaults without verifying:

| Setting | Value |
|---|---|
| **Crawl scope** | All website (including subdomains) |
| **Limit pages to crawl** | 1,000 |
| **Crawl speed** | 1 URL per 2 seconds (slow/polite) |
| **Schedule** | **Once** — always change this from any recurring default |
| **Allow/disallow** | Leave as default unless user specifies otherwise |

**Why "Once"?** A recurring schedule silently burns SEMrush crawl credits every week. Always confirm it's set to "Once" before clicking Start.

Use `mcp__claude-in-chrome__computer` with `screenshot` to verify the settings visually before proceeding.

## Step 6 — Start the Audit

Click **"Start Site Audit"**. The page will show "Preparing to crawl..." then "Auditing site... Please wait or come back later."

Note the page URL — it contains the project ID you can use to return directly.

## Step 7 — Wait for the Audit to Complete

Poll for completion every 30–60 seconds using `mcp__claude-in-chrome__computer` screenshot:
- Look for the progress bar reaching 100%
- Or the "View issues" / "Issues" button becoming active
- Or a final crawled page count appearing

Tell the user the audit is running and give an estimated wait (small sites < 5 min, large sites up to 20+ min).

## Step 8 — Open the Issues Tab

Once complete:
1. Click the completed audit to open it
2. Click the **"Issues"** tab
3. Wait for the list to fully load
4. Scroll to confirm **Errors**, **Warnings**, and **Notices** sections are all visible

Take a screenshot before proceeding to confirm you're on the right tab.

## Step 9 — Read and Document the Issues

Use `mcp__claude-in-chrome__get_page_text` or `mcp__claude-in-chrome__read_page` to extract the content. Report findings in this format:

```
Audit Results: [domain]
- Site Health: [X]%
- Pages crawled: [N]/1,000
- AI Search Health: [X]% (if shown)

Errors ([N] total):
1. [Issue name] — [N] pages

Warnings ([N] total):
1. [Issue name] — [N] pages

Notices ([N] total):
1. [Issue name] — [N] pages
```

## Step 10 — Capture and Save the Screenshot

Use **chrome-devtools MCP** `take_screenshot` with a `filePath` to save directly to disk. This works because Chrome was launched with `--remote-debugging-port=9222` in Step 2:

```
mcp__chrome-devtools__take_screenshot
  filePath: semrush-issues.png   ← saved relative to current working directory
  format: png
  fullPage: false                ← viewport screenshot; use true for very long issue lists
```

The tool response will confirm the absolute path where the file was saved.

**Why chrome-devtools MCP over PowerShell?** It captures via the DevTools Protocol directly — pixel-perfect at native resolution, unaffected by overlapping windows, screen DPI scaling, or whether Chrome is in the foreground.

### Fallback: PowerShell CopyFromScreen

Use this only if Chrome was not launched with `--remote-debugging-port=9222`:

```powershell
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
Add-Type @'
using System; using System.Runtime.InteropServices;
public class CC {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out R r);
}
public struct R { public int Left, Top, Right, Bottom; }
'@
$w = Get-Process | Where-Object { $_.Name -eq 'chrome' -and $_.MainWindowHandle -ne 0 } | Select-Object -First 1
[CC]::ShowWindow($w.MainWindowHandle, 3) | Out-Null   # SW_MAXIMIZE
[CC]::SetForegroundWindow($w.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 800
$r = New-Object R
[CC]::GetWindowRect($w.MainWindowHandle, [ref]$r) | Out-Null
$bmp = New-Object System.Drawing.Bitmap($r.Right - $r.Left, $r.Bottom - $r.Top)
$gfx = [System.Drawing.Graphics]::FromImage($bmp)
$gfx.CopyFromScreen($r.Left, $r.Top, 0, 0, $bmp.Size)
$bmp.Save((Join-Path (Get-Location) "semrush-issues.png"))
$gfx.Dispose(); $bmp.Dispose()
```

Maximize Chrome first so the Issues list isn't cut off below the fold.

## Step 11 — Verify the Screenshot

Open the saved file to confirm it looks right:

```
mcp__chrome-devtools__navigate_page
  type: url
  url: file:///[absolute-path-to-semrush-issues.png]
```

Then take an inline screenshot with `mcp__chrome-devtools__take_screenshot` (no filePath) to visually confirm.

The screenshot should show:
- SEMrush logo in the header
- "Issues" tab active/selected
- Errors section with red indicators
- Warnings section with amber indicators

## Deliverables

1. **`semrush-issues.png`** — saved in the working directory root
2. **Audit summary** — structured list of all errors, warnings, notices with counts
3. **Site health score** — overall percentage from SEMrush

## Common Issues

| Problem | Solution |
|---|---|
| Profile not found for email | Run the profile discovery script in Step 1 manually and share the output |
| Chrome opens but SEMrush tab not in claude-in-chrome | Extension not installed in that profile; use PowerShell navigation fallback |
| SEMrush shows "You need to sign in" | Session expired; user must log in manually, then re-run from Step 2 |
| Audit runs on a schedule (not once) | Verify Schedule = "Once" in settings before clicking Start |
| `chrome.exe` not found | Use full path: `C:\Program Files\Google\Chrome\Application\chrome.exe` |
| chrome-devtools MCP can't connect | Chrome must be launched with `--remote-debugging-port=9222`; check for port conflicts |
| chrome-devtools MCP shows wrong/unauthenticated page | `--profile-directory` flag was missing at launch; restart Chrome with both flags |

## PowerShell Navigation Fallback

If the claude-in-chrome extension is not active in the launched Chrome profile, control the browser via SendKeys:

```powershell
Add-Type -AssemblyName System.Windows.Forms
$w = Get-Process | Where-Object { $_.Name -eq 'chrome' -and $_.MainWindowHandle -ne 0 } | Select-Object -First 1
[System.Windows.Forms.SetForegroundWindow]::... # bring to front
[System.Windows.Forms.SendKeys]::SendWait("^l")
Start-Sleep -Milliseconds 300
[System.Windows.Forms.SendKeys]::SendWait("https://www.semrush.com/siteaudit/")
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
```

This is a last resort — prefer claude-in-chrome MCP navigation when the extension is available.
