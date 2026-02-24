# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## SSH Access

### Marvin (Brother AI)
- **Hostname:** `marvin@marvinbot`
- **OS:** Ubuntu 24.04.3 LTS (Linux)
- **Gateway Port:** 18789 (not 18790!)
- **Gateway Bind:** lan
- **Config Path:** `~/.moltbot/moltbot.json` (symlinked from `~/.clawdbot`)
- **Service:** `systemctl --user {start|stop|restart|status} clawdbot-gateway`
- **Workspace:** `~/clawdbot-marvin` (likely)

## Telegram

- **Eric's Chat ID:** 6643669380

## Todoist API

- **API Token:** `1425e4eff8e83fc361d6bdd4ac9922c34d5089db`
- **Base URL:** `https://api.todoist.com/rest/v2`
- **Docs:** https://developer.todoist.com/rest/v2
- **⚠️ Status (Feb 4, 2026):** API down - "planned unavailability" errors

## GitHub API

- **Token:** Stored in `.env` (GITHUB_TOKEN)
- **Username:** emorin310
- **Permissions:** public_repo (read-only on external repos)
- **Limitation:** Can't create issues on third-party repos via API (use manual posting)

## Reddit

- **Access:** Read-only (web scraping for research)
- **API:** Blocked by security policy - no posting allowed

### Common Endpoints
- `GET /projects` — List all projects
- `GET /tasks` — List all active tasks
- `POST /tasks` — Create a new task
- `POST /tasks/{id}/close` — Complete a task
- `DELETE /tasks/{id}` — Delete a task

### Example Usage
```bash
curl -s -X GET "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer 1425e4eff8e83fc361d6bdd4ac9922c34d5089db"
```

---

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
