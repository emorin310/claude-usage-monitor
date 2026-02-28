#!/bin/bash
# Daily Briefing Generator - Ultra-compact, visual-first
# Posts to Discord #general at 8 AM EST

# 1. TOP TECH NEWS (Hacker News - 2 stories max, compressed)
TECH=$(curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" 2>/dev/null | \
  jq -r '.[:2][]' 2>/dev/null | while read id; do
    curl -s "https://hacker-news.firebaseio.com/v0/item/$id.json" 2>/dev/null | \
    jq -r 'select(.url != null) | "[\(.title | .[0:60])](\(.url))"' 2>/dev/null
  done | head -2)

# 2. WEATHER (Cambridge, ON) - Ultra compact icons
WEATHER=$(curl -s "https://api.open-meteo.com/v1/forecast?latitude=43.4&longitude=-80.5&current=temperature_2m,relative_humidity_2m,weather_code&temperature_unit=celsius" 2>/dev/null | \
  jq -r '.current | "🌡️ \(.temperature_2m)°C  💧 \(.relative_humidity_2m)%"' 2>/dev/null || \
  echo "🌤️ Check weather.gc.ca")

# 3. CALENDAR (next event only)
CALENDAR=$(gcalcli agenda --nocolor 2>/dev/null | head -1 | sed 's/^[[:space:]]*//g' || echo "📅 No events")

# Build ultra-compact briefing
cat << EOF
**📋 Daily Briefing** — $(date +"%a, %b %d")

🔧 **Tech**
$TECH

🌤️ **Weather** — Cambridge, ON
$WEATHER

📅 **Next Event**
$CALENDAR
EOF
