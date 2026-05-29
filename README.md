# Shared Claude Code Skills

Shared Claude Code skills for the team.

## Skills included

| Slash command | Description |
|---|---|
| `/create-content-brain` | Creates a comprehensive content style guide (ContentBrain) for a client |
| `/create-service-page-b2b` | End-to-end B2B service page creation from scratch |
| `/optimize-service-page` | Optimize an existing service page for SEO and keyword compliance |
| `/local-biz-mockup` | Generate a full mockup website for a local business |
| `/local-seo-audit` | Comprehensive local SEO and Google Maps audit with HTML report |

## Installation

Clone this repo directly into your Claude Code skills directory:

```bash
# Mac/Linux
git clone https://github.com/teamoutriderdigital/claude-skills-shared.git ~/.claude/skills-shared

# Then symlink each skill into your skills folder:
ln -s ~/.claude/skills-shared/create-content-brain ~/.claude/skills/create-content-brain
ln -s ~/.claude/skills-shared/create-service-page-b2b ~/.claude/skills/create-service-page-b2b
ln -s ~/.claude/skills-shared/optimize-service-page ~/.claude/skills/optimize-service-page
ln -s ~/.claude/skills-shared/local-biz-mockup ~/.claude/skills/local-biz-mockup
ln -s ~/.claude/skills-shared/local-seo-audit ~/.claude/skills/local-seo-audit
```

```powershell
# Windows (PowerShell as Administrator)
git clone https://github.com/teamoutriderdigital/claude-skills-shared.git "$env:USERPROFILE\.claude\skills-shared"

# Then symlink each skill:
$src = "$env:USERPROFILE\.claude\skills-shared"
$dst = "$env:USERPROFILE\.claude\skills"
New-Item -ItemType Junction -Path "$dst\create-content-brain"    -Target "$src\create-content-brain"
New-Item -ItemType Junction -Path "$dst\create-service-page-b2b" -Target "$src\create-service-page-b2b"
New-Item -ItemType Junction -Path "$dst\optimize-service-page"   -Target "$src\optimize-service-page"
New-Item -ItemType Junction -Path "$dst\local-biz-mockup"        -Target "$src\local-biz-mockup"
New-Item -ItemType Junction -Path "$dst\local-seo-audit"         -Target "$src\local-seo-audit"
```

## Updating

```bash
cd ~/.claude/skills-shared && git pull
```

Slash commands update automatically — no re-linking needed.
