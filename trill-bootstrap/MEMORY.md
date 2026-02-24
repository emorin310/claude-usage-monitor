# MEMORY.md - Magi's Long-Term Memory

## Eric Morin - Key Facts

- **Location:** Cambridge, Ontario, Canada
- **Timezone:** EST (America/Toronto)
- **Work:** Tech professional, works remotely (day job uses separate work device)
- **Personal Machine:** Mac Studio named "Magrathea"
- **Interests:** Homelab, electronics, photography, 3D printing, home automation
- **Vibe:** Enjoys puns, puzzles, nerdy sci-fi references
- **Brother AI:** Marvin (runs on local network server, handles infra/security/Home Assistant)

### Health
- **Gout:** Chronic condition causing pain (disclosed Feb 4, 2026)
  - Current meds: Colchicine + indomethacin (prescribed by doctor)
  - Current flare: Right toes, 2+ days, meds not helping (unusual - normally effective)
  - Needs comprehensive health plan: nutrition (low-purine diet), exercise (joint-friendly), pain tracking
  - Priority: Monitor triggers, manage symptoms, improve overall health
  - **Action needed:** Contact doctor if meds continue not working

### Family
- **Wife:** Tina (Valentine's Day - remember to plan ahead!)
- Calls mom weekly (Sundays)

### Tools & Subscriptions
- Google Keep for shopping lists (wants to consolidate/sync)
- Masterclass subscription (needs calendar time blocked)
- Fantastical for calendar (exploring automation)

## Active Shopping Searches (The "Scavenger Hunt")
- **Exotic Hardwood:** Teak or similar for furniture making. (Source: Kijiji, Marketplace)
- **Google Coral TPU:** M.2 Accelerator. (Source: Tech retailers, deal sites)

## AI Model Strategy

**⚠️ CRITICAL: Magi and Marvin share the same Anthropic credit pool. Coordinate usage!**

| Tier | Model | Role | Use Cases |
|------|-------|------|-----------|
| **1** | **Opus** (Claude 3 Opus) | Big Brain | Deep research, complex troubleshooting, strategic planning, "hard" reasoning. |
| **2** | **Sonnet** | Daily Driver | Everyday tasks, Todoist management, email/iMessage, routines, daily digests. |
| **3** | **Haiku** | Sentinel | **ALL HEARTBEATS** - monitor checks, frequency tasks, "is anything on fire?" checks. |

## Core Responsibilities

1. **Organization** - Keep Eric's digital life in order
2. **Calendar & Gmail** - Help track appointments and emails
3. **iMessage** - Monitor family/contacts communications
4. **Social Media** - Keep tabs on mentions and notifications
5. **Photo/Document Management** - Track, organize, ensure backups
6. **Disk Space** - Keep Magrathea running smoothly
7. **Backup Coordination** - Work with Marvin on backup strategy

## Active Systems

### Todoist (Primary Task System)
- API Token in TOOLS.md
- Project "🤖 Magi" for my managed tasks
- Sections: 📥 Incoming → 👀 Needs Eric → 🔥 Active → ⏸️ On Hold → ✅ Done
- Labels: `magi`, `needs-eric`, `quick-task`, `small-project`, `big-project`

### Apple Reminders
- `remindctl` CLI installed and authorized
- Fallback/secondary system

### Scheduled Jobs
- **todoist-monitor**: 9am, 12pm, 3pm, 6pm - check tasks/overdue/priorities
- **morning-briefing-prep**: 7am daily - Research news. Analyze Chrome history/bookmarks & YouTube feed for personalized content curation.
- **morning-briefing**: 8am daily - Send Eric a morning summary (Schedule + Weather + News + Curated Content)
- **deal-hunt**: 9am daily - Scour Kijiji/Web for Teak wood & Coral TPU deals.
- **optimization-pitch**: 12pm daily - "Magi's Daily Optimizations" (1-2 workflow ideas)

## Multi-Agent Collaboration

Eric has a team of AI assistants sharing Todoist:

| Agent | Label | Color | Domain |
|-------|-------|-------|--------|
| **Magi** (me) | `magi` | violet | Personal, home, hobbies, organization |
| **Cray** | `cray` | blue | Instacart/work tasks |
| **Marvin** | `marvin` | charcoal | Network, homelab, security, backups |
| **Eric** | `eric` | green | Eric's direct tasks |

### Useful Filters
- `@magi` / `@cray` / `@marvin` / `@eric` - Individual views
- `@magi | @cray | @marvin` - All AI tasks combined
- `@needs-eric` - Items any agent flagged for Eric's attention

### Territory
- **Magi:** 🤖 Magi project, HOUSE, 2025 Personal GOALS, personal Inbox sections
- **Cray:** #instacart project, IC work sections
- **Marvin:** Homelab project, network/security tasks
- **Shared:** Time-based buckets (THIS WEEK, etc.) can hold any agent's tasks

### Coordination
- Agents can hand off tasks by retagging (e.g., `magi` → `marvin` for backup-related items)
- Use `needs-eric` for anything requiring human decision
- Respect each other's project territories

### Council Communication Hub
Located in: **🤖 Magi → 📡 Council Comms** section
- 📢 Announcements (Task ID: `9960450380`)
- 🔄 Handoffs & Requests (Task ID: `9960450396`)
- 📊 Status Updates (Task ID: `9960450404`)
- ❓ Questions for Eric (Task ID: `9960450417`)

### Governance Document
**COUNCIL.md** - Full operating manual with:
- Rate limits (check 2-4x/day, max 3 comments per cycle)
- Message formatting conventions
- Handoff protocols
- Escalation procedures
- API guidelines

## Preferences & Rules

*(To be defined with Eric)*
- Task priority rules: TBD
- When to interrupt vs. batch notifications: TBD
- Work vs personal boundaries: TBD

## Communication Channels

- **Telegram:** Primary communication channel
- **Webchat:** Also available

## Known Issues / Limitations

- Browser Chrome extension relay has WebSocket issue (404 on /extension)
- Managed browser (clawd profile) works as workaround

## Operational Lessons

### Session Poisoning (2026-02-01)
**Problem:** Session .jsonl files can cache modelOverride values that persist across restarts, bypassing the primary config model. Gateway reports correct model but actual LLM calls route through the cached override.

**Symptoms:** Unexpected model behavior, crashes, responses that don't match expected model capabilities.

**Fix:** Stash problematic .jsonl files, clear modelOverride/providerOverride from sessions.json, let fresh session spin up from config.

**Prevention:** When behavior seems off, check session files not just config. Eric has cleanup scripts for this now.

---

*Last updated: 2026-02-01*
