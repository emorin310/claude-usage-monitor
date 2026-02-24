# Magi Failsafe System

## What It Does
Monitors Magi's health every 15 minutes. If quota limits are hit, automatically switches to Gemini Flash (free tier) and notifies you.

## Setup (System Cron - Recommended)

Add this to your system crontab (runs independently of Clawdbot):

```bash
# Edit crontab
crontab -e

# Add this line (runs every 15 minutes):
*/15 * * * * /Users/eric/clawd-magi/scripts/failsafe-model-switch.sh

# Or for more frequent checks (every 5 min during work hours):
*/5 9-18 * * 1-5 /Users/eric/clawd-magi/scripts/failsafe-model-switch.sh
```

## Manual Test

Test the script manually:
```bash
/Users/eric/clawd-magi/scripts/failsafe-model-switch.sh
```

Check logs:
```bash
tail -f /Users/eric/clawd-magi/logs/failsafe.log
```

## Alternative: Clawdbot Cron

If you prefer Clawdbot to manage it (less reliable if Clawdbot itself is down):

```bash
clawdbot cron add \
  --schedule "*/15 * * * *" \
  --command "/Users/eric/clawd-magi/scripts/failsafe-model-switch.sh" \
  --description "Magi quota failsafe"
```

## What Triggers It

- API quota errors
- Rate limit errors  
- Timeout on health check (>10s)
- Any response failure

## Recovery

Once quotas reset, manually switch back:
```bash
clawdbot session model --session main --model default
```

Or wait - I'll eventually notice and switch myself back during off-peak hours.
