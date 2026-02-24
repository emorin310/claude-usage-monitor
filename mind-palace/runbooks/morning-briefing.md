# Runbook: Morning Briefing

## Overview

Daily briefing delivered via Telegram to start Eric's day with everything he needs to know.

## Schedule

| Phase | Time | Action |
|-------|------|--------|
| Research | 7:00 AM | Gather & curate all data |
| Delivery | 8:00 AM | Send formatted briefing to Telegram |

## Data to Gather

### 1. Weather (Cambridge, Ontario)
- Current conditions
- High/low temperatures
- Notable alerts or precipitation

### 2. Tasks Due Today
```bash
curl -s -H "Authorization: Bearer $TODOIST_TOKEN" \
  "https://api.todoist.com/rest/v2/tasks?filter=today"
```

### 3. Calendar Events
```bash
gcalcli agenda "today" "tomorrow" --nocolor
```

### 4. Tech & AI News
Search for:
- AI/LLM developments (Claude, GPT, Gemini)
- Home Assistant updates
- Notable tech product announcements

### 5. 3D Printing News
Search for:
- Bambu Lab announcements
- MakerWorld trending models
- New filament releases
- Notable prints or techniques

## Curation Guidelines

Based on Eric's interests (see `relationships/eric.md`):

**Prioritize:**
- AI assistant & automation news
- Home lab / UniFi / Tailscale updates
- Bambu Lab P1S-relevant content
- Fusion360 / CAD news
- Local Ontario weather alerts

**Deprioritize:**
- Generic tech news without AI/homelab angle
- Consumer gadget reviews
- Enterprise-only announcements

## Delivery Format

### Telegram Message (chat ID: 6643669380)

```
☀️ **Good Morning, Eric!**

📅 **Thursday, January 30, 2026**

---

🌤️ **Weather** — Cambridge, ON
Today: -5°C → 2°C, light snow pm
Tomorrow: Clearing, -8°C

---

✅ **Tasks Due Today** (3)
• [ ] Submit IC scorecard
• [ ] Review Caper metrics
• [ ] Call Mom (Sunday reminder prep)

---

📆 **Calendar**
• 10:00 AM — Stand-up (Work)
• 2:00 PM — Dentist (Dawson Dental)

---

🤖 **Tech/AI Highlights**
• Claude 3.5 update: improved agentic tool use
• Home Assistant 2025.2 released with Matter improvements

---

🖨️ **3D Printing**
• Bambu announces new high-flow nozzle kit
• MakerWorld trending: articulated dragon print

---

Have a great day! 🚀
```

## Error Handling

- **Weather API down:** Skip section, note "Weather unavailable"
- **Todoist API error:** Skip tasks, mention "Todoist unreachable"
- **No calendar events:** Show "📆 Nothing scheduled — free day!"
- **No news found:** Show "🤖 Nothing notable today"

## Post-Delivery

1. Log briefing sent to `memory/YYYY-MM-DD.md`
2. If any critical items found, note in daily log

---

*Last updated: 2026-01-29*
