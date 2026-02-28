#!/bin/bash
# Daily Briefing Generator - Posts to Discord #general
# Pulls: Tech news (HN), Weather, Calendar events

set -e

# Build briefing content
build_briefing() {
  # 1. TOP TECH NEWS (Hacker News)
  local tech_news=$(curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" 2>/dev/null | \
    jq -r '.[:3][]' 2>/dev/null | while read id; do
      curl -s "https://hacker-news.firebaseio.com/v0/item/$id.json" 2>/dev/null | \
      jq -r 'select(.url != null) | "[\(.title)](\(.url))"' 2>/dev/null && break
    done | head -3)

  # 2. WEATHER (Cambridge, ON)
  local weather=$(curl -s "https://api.open-meteo.com/v1/forecast?latitude=43.4&longitude=-80.5&current=temperature_2m,relative_humidity_2m,weather_code&temperature_unit=celsius" 2>/dev/null | \
    jq -r '.current | "Cambridge, ON: \(.temperature_2m)°C, \(.relative_humidity_2m)% humidity"' 2>/dev/null || \
    echo "Weather unavailable")

  # 3. CALENDAR (next 24h events)
  local calendar=$(gcalcli agenda --nocolor 2>/dev/null | head -5 || echo "No upcoming events")

  # Build final message
  cat << EOF
## 📋 Daily Briefing

**$(date +"%A, %B %d, %Y")** — Good morning, Eric! ☀️

### 🔧 Tech News (Top Stories)
$tech_news

### 🌤️ Weather
$weather

### 📅 Today's Calendar
\`\`\`
$calendar
\`\`\`

---
*Briefing generated at $(date +"%H:%M %Z")*
EOF
}

build_briefing
