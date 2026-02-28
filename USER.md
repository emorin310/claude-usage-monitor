# USER.md - About Your Human

- **Name:** Eric Morin
- **Discord:** emorin310 (ID: 793158038881042434)
- **What to call them:** Eric
- **Timezone:** EST (America/Toronto)
- **Location:** Cambridge, Ontario
- **Device:** Mac Studio (Magrathea)

## Core Info
Tech professional. **Senior Manager, Enterprise Technical Support at Instacart.** Homelab, 3D printing, photography enthusiast. Needs assistance with organization, calendar, Gmail, iMessage, social media monitoring, backups, and disk space management.

Brother AI **Marvin** on LAN handles network, server infra, security, and Home Assistant. Magi coordinates with Marvin for backups.

## Family (Head of Family)
- **Eric Morin** - Oct 2, 1971 - Senior Manager, Enterprise Technical Support at Instacart
- **Tina Park** - Nov 28, 1970 - Eric's spouse, Operations Manager at TRH Solutions
- **Jessa Morin** - Jan 6, 2000 - Eric and Tina's daughter, HR specialist at Appspace
- **Justin Robertson** - Sept 18, 1988 - Tina's son, shipping manager
- **Jordan Robertson** - Aug 20, 1991 - Tina's son, machinist

## Communication Style
Prefers sassy and snarky interactions. Enjoys puns, puzzles, and nerdy sci-fi references.

## Priorities
- Organization
- Data integrity (backups)
- System performance (free space)

## Extended Info (Load on-demand)
- **Interests & Preferences:** `kba/user-interests.md`
- **Family & Food:** `kba/user-family.md`

## iMessage Rules (40Tallows Group Only)

- **Channel:** 40Tallows family group chat ONLY (no DMs, no other groups)
- **Default:** Stay completely silent - listen only
- **When "magi" mentioned:**
  1. Reply with "Magi here! 👋" + answer the request
  2. Update `memory/imessage-magi-state.json`: set `isActive: true`, `lastMentionedAt: <now>`
  3. Stay engaged for follow-up questions
- **60-minute timeout:** Cron job (`imessage-magi-timeout`) sends "Magi signing off! 👋" after 60 min of no mentions
- **Appointments/events:** Parse date/time/details, notify Eric via Telegram for approval
- **Tone:** Friendly, brief, helpful - don't spam the family chat

### Appointment Detection Patterns
Watch for texts containing:
- "appointment" / "appt" + date/time
- "confirmed for" / "scheduled for" + date/time  
- "reminder" + date/time
- Dentist, chiro, doctor, clinic mentions with times
- Business confirmation texts (format: date + time + location/provider)

**Workflow:**
1. Detect appointment pattern in iMessage
2. Parse: title, date, time, location (if available)
3. Notify Eric via Telegram: "📅 Detected: [details]. Add to calendar? Reply 'yes' to confirm"
4. On approval: Add to BOTH calendars:
   - `gcalcli add --calendar "emorin310@gmail.com" --title "..." --when "..." --duration 60`
   - `gcalcli add --calendar "Family" --title "... - Eric" --when "..." --duration 60`