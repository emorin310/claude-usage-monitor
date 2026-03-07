---
name: claude-usage-monitor
description: Install, launch, and manage the Claude Usage Monitor dashboard — a real-time token usage visualizer for claude.ai Max subscribers. Use when user asks to monitor Claude token usage, view session activity, check rate limits, or install the usage dashboard.
---

# Claude Usage Monitor

Real-time token usage dashboard for claude.ai Max subscribers. Displays live session activity, token rates, 5-hour/7-day/monthly rate-limit gauges, and model breakdowns — served as a local web app at http://localhost:3847.

## Installation

1. Clone or download from https://github.com/emorin310/claude-usage-monitor
2. Run the installer:

```bash
cd claude-usage-monitor
npm install
./install.sh
```

This installs a macOS LaunchAgent that starts the dashboard automatically on login.

## Configuration

1. Get your session key from claude.ai (Chrome DevTools → Application → Cookies → sessionKey)
2. Get your org ID: `grep injectedOrgId ~/.claude/fetch-claude-usage.swift`
3. Add both to `.env`:

```
CLAUDE_SESSION_KEY=sk-ant-sid02-...
CLAUDE_ORG_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

4. Restart: `./stop.sh && ./start.sh`

## Usage

- Open dashboard: `open http://localhost:3847`
- View logs: `tail -f logs/server.log`
- Stop: `./stop.sh`
- Uninstall: `./uninstall.sh`

## What It Shows

| Gauge | Source |
|---|---|
| 5-Hour Utilization | claude.ai API — rolling rate limit |
| 7-Day Utilization | claude.ai API — weekly per-model breakdown |
| Monthly Credits | claude.ai API — extra credit consumption |
| Token Rate | Local JSONL logs — 10-min rolling chart |
| Active Sessions | Local JSONL logs — per-session breakdown |

## Requirements

- macOS with Node.js 18+ (`brew install node`)
- claude.ai Max subscription
- Claude Code installed (provides the JSONL session logs)
