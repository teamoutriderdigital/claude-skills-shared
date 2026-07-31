# semrush-site-audit

Automates a full SEMrush technical site audit — from launching Chrome to saving a screenshot of the Issues tab — using Claude Code with browser MCP tools.

---

## What It Does

1. Finds the correct Chrome profile for `team@outriderdigital.com` automatically
2. Launches Chrome with that profile and remote debugging enabled
3. Creates a new SEMrush Site Audit project for the target domain
4. Configures audit settings (1,000 pages, 1 URL/2 sec, run once)
5. Starts the audit and polls until complete
6. Opens the Issues tab and extracts all errors, warnings, and notices
7. Saves a screenshot of the Issues tab to the working directory as `semrush-issues.png`

---

## Usage

```
/semrush-site-audit rockymountainpoolbuilders.com
```

Or just invoke the skill and Claude will ask for the domain:

```
/semrush-site-audit
```

---

## Prerequisites

### 1. Operating System
- **Windows only** — the skill uses PowerShell and `$env:LOCALAPPDATA` to locate Chrome profiles. Does not work on macOS or Linux without modification.

### 2. Google Chrome
- Chrome must be installed (not just Brave or Edge)
- The `team@outriderdigital.com` Google account must be signed in to a Chrome profile
- That profile must have an active SEMrush session (logged in at semrush.com)

> To verify: open Chrome, switch to the team@outriderdigital.com profile, go to semrush.com — you should land on the dashboard without being asked to log in.

### 3. SEMrush Paid Account
- A paid SEMrush subscription is required to run Site Audits
- The account must be accessible via `team@outriderdigital.com`

### 4. Claude Code
- Claude Code CLI must be installed and running
- The skill lives at `~/.claude/skills/semrush-site-audit/SKILL.md`

---

## MCP Dependencies

Two MCP servers must be configured and active in Claude Code:

### claude-in-chrome (Browser Extension MCP)
- **Purpose:** Navigates and interacts with SEMrush in the browser (clicking buttons, reading page content, taking inline screenshots for verification)
- **What it is:** A Chrome/Brave browser extension that exposes browser control to Claude Code via MCP
- **Install:** Add the claude-in-chrome extension to the Chrome profile being used (`team@outriderdigital.com` profile)
- **Required tools used:** `tabs_context_mcp`, `tabs_create_mcp`, `navigate`, `computer`, `read_page`, `get_page_text`, `find`
- **Without it:** Navigation falls back to PowerShell SendKeys (less reliable)

### chrome-devtools (CDP MCP)
- **Purpose:** Saves screenshots directly to disk via the Chrome DevTools Protocol
- **What it is:** An MCP server that connects to Chrome's remote debugging port (`localhost:9222`)
- **Requirement:** Chrome must be launched with `--remote-debugging-port=9222` (the skill does this automatically)
- **Required tools used:** `take_screenshot` (with `filePath`), `list_pages`, `navigate_page`
- **Without it:** Falls back to PowerShell `CopyFromScreen` for screenshots

> Both MCPs must appear in your Claude Code MCP configuration (`~/.claude/settings.json` or equivalent).

---

## Port Requirement

The chrome-devtools MCP connects to **port 9222**. This port must be free when the skill launches Chrome.

If Chrome is already running **without** `--remote-debugging-port=9222`, the devtools MCP will not be able to connect to the authenticated session. Close any existing Chrome windows first, or the skill will fall back to PowerShell for screenshots.

---

## File Output

| File | Description |
|---|---|
| `semrush-issues.png` | Screenshot of the SEMrush Issues tab, saved in the current working directory root |

---

## Fallbacks

| Situation | Fallback |
|---|---|
| claude-in-chrome extension not in Chrome profile | PowerShell SendKeys for navigation |
| Chrome launched without `--remote-debugging-port=9222` | PowerShell `CopyFromScreen` for screenshots |
| `chrome.exe` not in PATH | Use full path: `C:\Program Files\Google\Chrome\Application\chrome.exe` |

---

## Limitations

- **Windows only** (PowerShell + Windows API used for profile discovery and fallback screenshots)
- **Requires active SEMrush session** — if the session expires, the user must log in manually
- **One audit at a time** — running multiple audits simultaneously may cause port conflicts
- **Port 9222 must be free** — conflict if another Chrome instance already uses it
