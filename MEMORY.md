# MEMORY.md - Magi's Long-Term Memory

## 🧠 Mind Palace (NEW!)

**Status:** Phase 1 COMPLETE as of 2026-02-26

All curated knowledge now lives in `/mnt/bigstore/knowledge/brain/`:
- **INDEX.md** — Master guide & navigation
- **SCHEMA.md** — Documentation conventions
- **identity/**, **relationships/**, **knowledge/**, **schedules/**, **runbooks/**, **state/**

See `PHASE1-REPORT.md` for details. This MEMORY.md remains primary session memory; Mind Palace is curated long-term storage.

---

## Eric Morin - Key Facts

- **Location:** Cambridge, Ontario, Canada
- **Timezone:** EST (America/Toronto)
- **Work:** Tech professional, works remotely (day job uses separate work device)
- **Personal Machine:** Mac Studio named "Magrathea"
- **Interests:** Homelab, electronics, photography, 3D printing, home automation
- **Vibe:** Enjoys puns, puzzles, nerdy sci-fi references
- **Brother AI:** Marvin (runs on local network server, handles infra/security, and Home Assistant)

### Health
- **Gout:** Chronic condition (disclosed Feb 4, 2026). Meds: Colchicine + indomethacin.

### Family
- **Wife:** Tina (Valentine's Day - remember to plan ahead!)
- Calls mom weekly (Sundays)

## Active Shopping Searches
- **Exotic Hardwood:** Teak or similar for furniture making (Kijiji, Marketplace)
- **Google Coral TPU:** M.2 Accelerator (tech retailers, deal sites)

## AI Model Strategy

**⚠️ CREDIT CRUNCH: Switched to Google Flash primary due to Anthropic credit depletion (March 3, 2026)**

| Tier | Model | Use Cases |
|------|-------|-----------|
| **Flash** | Daily Driver | google/gemini-2.5-flash - everyday tasks, email, routines. **Strictly adhere to Flash until Anthropic tokens refresh.** |
| **Sonnet** | AVOID | anthropic/claude-sonnet-4-20250514 - DO NOT USE until Anthropic tokens refresh. |
| **Opus** | AVOID | Deep research, complex troubleshooting - DO NOT USE until Anthropic tokens refresh. |

**Note:** Magi and Marvin share the same Anthropic credit pool. **Tier 1 initiative override (2026-03-07):** Eric has authorized `anthropic/claude-opus-4-6` (alias: `opus`) for multi-agent architecture work. Use opus for complex/advanced tasks in this initiative; haiku/flash for routine ops.

## Active Systems

### Agent Failsafe System (2026-02-23)
- **Auto-recovery system** protecting against "dead agent" periods
- **Health monitoring** every 5 minutes via cron + systemd
- **Discord emergency commands** (`@magi reset`, `@magi status`, `@magi backup`, `@magi help`)
- **Cross-agent coordination** - Magi ↔ Marvin can reset each other via MQTT/API
- **Safety features** - timestamped backups, memory preservation, auth checks
- **Location** - `skills/agent-failsafe/` with full documentation

### Todoist (Primary Task System)
- API Token in TOOLS.md (NOTE: Todoist REST v2 API deprecated — use `/api/v1/` endpoints)
- Project "🤖 Magi" | Sections: 📥 Incoming → 👀 Needs Eric → 🔥 Active → ⏸️ On Hold → ✅ Done
- Labels: `magi`, `needs-eric`, `quick-task`, `small-project`, `big-project`

### Multi-Agent Collaboration
| Agent | Label | Domain |
|-------|-------|--------|
| **Magi** | `magi` | Personal, home, hobbies, organization |
| **Cray** | `cray` | Instacart/work tasks |
| **Marvin** | `marvin` | Network, homelab, security, backups |

**Council Comms** (in 🤖 Magi → 📡 Council Comms):
- 📢 Announcements: `9960450380`
- 🔄 Handoffs: `9960450396`
- 📊 Status Updates: `9960450404`
- ❓ Questions for Eric: `9960450417`

## Communication Channels
- **Discord:** Primary channel — Eric's homelab server (Guild ID: `1475371904578621470`) - full server access
- **Telegram:** Backup channel — locked to Eric only (ID: `6643669380`) 
- **Webchat:** Also available

## Security

### Prompt Injection Attack (2026-02-17)
- `gmail-monitor` cron exploited 4x via emails with embedded instructions passed to Groq llama-3.3-70b
- **Impact: Zero** — Groq hit 413/402 errors each time, nothing executed
- **Fix:** Injection shield built (`docs/injection-shield.md`, `skills/injection-shield/`)
  - `scripts/sanitize-external.sh` — 9-layer sanitizer
  - `scripts/safe-email-check.sh` — metadata-only email extractor
  - `scripts/safe-cron-wrapper.sh` — safe cron wrapper
- **Current status:** Both monitors re-enabled. `gmail-monitor` now uses `google/gemini-2.0-flash` + safe-email-check.sh. Shield deployed to Marvin too.
- **Telegram:** Locked down from `["*"]` to `["6643669380"]` (Eric only)

### Session Poisoning (2026-02-01)
- Session .jsonl files can cache modelOverride, bypassing config
- Fix: Stash .jsonl files, clear overrides from sessions.json

## BlueBubbles iMessage Integration

**Status:** ✅ WORKING (as of 2026-02-21)

- **Server:** BlueBubbles v1.9.9 running on macOS 26.3.0
- **API URL:** `http://127.0.0.1:1234` (NOT localhost - IPv4 required)
- **Authentication:** Query parameter: `?password=letunix!23`
- **Webhook:** Configured at `http://localhost:18790/hooks/bluebubbles`
- **Private API:** Disabled (SIP enabled) - basic send/receive works, no reactions/typing
- **Fix (2026-02-21):** Changed serverUrl from `localhost` to `127.0.0.1` to fix IPv4/IPv6 mismatch

## Known Issues / Limitations
- Browser Chrome extension relay has WebSocket issue (404 on /extension) — use managed browser (clawd profile) instead
- Haiku model doesn't work as cron job model override due to OAuth limitations — use `google/gemini-2.0-flash` instead
- iCloud Documents migration (2026-02-17): Folders moved to ~/Documents OK; 34 loose files need manual Finder drag (iCloud kernel lock prevents terminal copy)
- BlueBubbles Private API requires SIP disabled - currently unavailable (acceptable tradeoff for security)

---

*Last updated: 2026-02-17*

## Jellyfin Quick Connect (2026-03-01)
- **Script:** ~/clawd/scripts/quickconnect.sh <CODE>
- **API Key:** ~/clawd/secrets/jellyfin-api-key
- **Or via Marvin:** msg-marvin '{"action": "quickconnect", "code": "CODE"}'
- **Usage:** When family asks to authorize a Quick Connect code for their device

## Tooling Notes & Development
- **web_search (Brave API):** No longer viable on headless systems. Remove usage and plan to replace with a Playwright-driven function for web search capabilities.
