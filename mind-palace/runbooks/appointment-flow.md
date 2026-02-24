# Runbook: Appointment Detection & Handling

## Trigger Sources
- iMessage via BlueBubbles
- Gmail via gmail-check.py cron

## Detection Patterns

Watch for:
- "appointment" / "appt" + date/time
- "confirmed for" / "scheduled for" + date/time
- "reminder" + date/time
- Medical provider mentions (dentist, chiro, doctor) with times
- Business confirmation format: date + time + location

## Workflow (AUTONOMOUS - No Confirmation Needed!)

```
1. DETECT appointment in message/email
   ↓
2. PARSE details:
   - Title/Provider
   - Date
   - Time
   - Location (if available)
   - Phone (if available)
   ↓
3. CHECK: Is it in the future?
   - Past → Log and skip silently
   - Future → Continue
   ↓
4. CHECK CALENDAR:
   gcalcli search "[provider/keywords]" "YYYY-MM-DD"
   
   - Already exists → STOP (stay silent, no notification)
   - Not found → Continue to step 5
   ↓
5. AUTO-ADD to BOTH calendars (NO confirmation needed):
   - Personal: emorin310@gmail.com
   - Family: with "- Eric" suffix
   ↓
6. NOTIFY Eric (INFORMATIONAL ONLY):
   "📅 Added: [Event] - [Date] @ [Time]"
   
   DO NOT ask for confirmation!
   DO NOT ask "Add to calendar?"
   Just inform that it's done.
```

## Key Principle

**Automate fully. Confirmations waste time.**

Only ask for input when:
- Time/date is ambiguous and can't be parsed
- There's a conflict with existing event
- Details are incomplete/unclear

Otherwise: detect → add → inform. Done.

## Example Telegram Notification (NEW - Informational)

```
📅 **Added to Calendar**

🦷 Dental Hygiene - Dawson Dental
📆 Sat Jan 31 @ 11:30 AM
📍 541 Hespeler Rd, Cambridge

✅ On both personal & Family calendars.
```

NOT this (old way - asking permission):
```
❌ "Add to calendar? Reply yes to confirm"
```

## gcalcli Commands

```bash
# Check if exists first
gcalcli search "Dental" "2026-01-31"

# Personal calendar
gcalcli add --calendar "emorin310@gmail.com" \
  --title "🦷 Dental Hygiene - Dawson Dental" \
  --where "541 Hespeler Road, Unit 103, Cambridge, ON" \
  --when "Jan 31, 2026 11:30 AM" \
  --duration 60 \
  --description "Phone: (519) 622-3332" \
  --noprompt

# Family calendar (add "- Eric" suffix)
gcalcli add --calendar "Family" \
  --title "🦷 Dental Hygiene - Eric" \
  --where "541 Hespeler Road, Unit 103, Cambridge, ON" \
  --when "Jan 31, 2026 11:30 AM" \
  --duration 60 \
  --noprompt
```

## Edge Cases

- **Past appointment:** Log silently, no notification
- **Already on calendar:** Stay silent (don't even say "already there")
- **Ambiguous time:** Only then ask for clarification
- **Conflict detected:** Notify and ask which to keep

---

*Last updated: 2026-01-29 — Changed to autonomous flow (no confirmations)*
