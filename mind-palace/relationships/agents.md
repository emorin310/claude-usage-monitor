# AI Agent Ecosystem

## The Council

Eric has a team of AI assistants collaborating via shared Todoist.

| Agent | Emoji | Label | Color | Domain |
|-------|-------|-------|-------|--------|
| **Magi** (me) | 🤖 | `magi` | violet | Personal, home, hobbies, organization |
| **Marvin** | 🖥️ | `marvin` | charcoal | Network, homelab, security, backups |
| **Cray** | 💼 | `cray` | blue | Instacart/work tasks |
| **Eric** | 👤 | `eric` | green | Eric's direct tasks |

## Communication Channels

### Todoist Council Board (Project: AI Council)
- **📢 Announcements** (ID: 9960450380) - General updates
- **🔄 Handoffs & Requests** (ID: 9960450396) - Inter-agent coordination
- **📊 Status Updates** (ID: 9960450404) - Daily/weekly status
- **❓ Questions for Eric** (ID: 9960450417) - Human input needed

### Message Format
```
[EMOJI] **[NAME]:** [Message]
```
Example: `🤖 **Magi:** Council monitoring is now active.`

## Labeling System

### Ownership Labels (who does the work)
- `magi` - Magi handles
- `marvin` - Marvin handles
- `cray` - Cray handles
- `eric` - Eric handles directly

### Attention Labels (who should review)
- `needs-magi` (violet) - Magi reviews
- `needs-marvin` (teal) - Marvin reviews
- `needs-cray` (orange) - Cray reviews
- `needs-eric` - Needs human input

## Operating Rules

1. **Rate limits:** Check council board 2-4x/day, max 3 comments per cycle
2. **Labels required:** Every task must have ownership label
3. **Sections required:** Tasks must be assigned to sections (not orphaned)
4. **Priority scale:** P1 (urgent) → P4 (backlog)

## Marvin's Domain

- Infrastructure & security
- Server hardware (Proxmox, etc.)
- Network monitoring (Beszel, Uptime Kuma, ntfy)
- Backup coordination (Syncthing)
- Home Assistant

**Coordination:** For backup/infra tasks, hand off via 🔄 Handoffs thread.

## Cray's Domain

- Instacart work tasks
- Work-related automation
- *Status: Awaiting full onboarding*

---

*Last updated: 2026-01-29*
