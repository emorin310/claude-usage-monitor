# Claude Usage Monitor

A real-time token usage dashboard for **claude.ai Max** subscribers. Watches your local Claude Code session logs and the claude.ai API to show live token consumption, rate, model breakdown, and rate-limit utilization.

![Dashboard](docs/screenshot.png)

## Features

- **5-Hour Utilization** — live ring gauge from the claude.ai rate-limit API
- **7-Day Utilization** — weekly consumption gauge with per-model breakdown
- **Monthly Credits** — extra credit usage gauge with days-until-reset
- **Token Rate** — 10-minute rolling bar chart (real-time, 30s buckets)
- **Model Share** — doughnut chart of token consumption by model
- **Active Sessions** — all Claude Code sessions with prompt, model, token counts, sparklines, and sortable columns

## Requirements

- macOS
- [Node.js](https://nodejs.org) (v18+) — install via `brew install node`
- A **claude.ai Max** subscription (for rate-limit gauges)

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/claude-usage-monitor.git
cd claude-usage-monitor
npm install
cp .env.example .env
```

Edit `.env` and add your credentials (see [Configuration](#configuration)), then:

```bash
./start.sh       # start in background + open dashboard
./stop.sh        # stop
```

Dashboard runs at **http://localhost:3847**

## Install as Auto-Start (Recommended)

Installs as a macOS LaunchAgent — starts automatically on login, no terminal needed:

```bash
./install.sh
```

To uninstall:

```bash
./uninstall.sh
```

## Configuration

Copy `.env.example` to `.env` and fill in:

```env
CLAUDE_SESSION_KEY=sk-ant-sid02-...
CLAUDE_ORG_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### Getting your Session Key

1. Open [claude.ai](https://claude.ai) in Chrome while logged in
2. Open DevTools (`Cmd+Option+I`)
3. Go to **Application → Cookies → https://claude.ai**
4. Copy the value of the `sessionKey` cookie

> Session keys expire periodically. If the gauges show `—`, refresh the key.

### Getting your Org ID

```bash
grep injectedOrgId ~/.claude/fetch-claude-usage.swift
```

Or find it in the `lastActiveOrg` cookie on claude.ai.

### Optional Settings

```env
PORT=3847           # default port
USAGE_POLL_MS=30000 # how often to poll the claude.ai API (ms)
```

## How It Works

- **Session data** — watches `~/.claude/projects/**/*.jsonl` in real-time using [chokidar](https://github.com/paulmillr/chokidar). These JSONL files are written by Claude Code and contain per-turn token usage, model names, and session IDs.
- **Rate-limit gauges** — polls `https://claude.ai/api/organizations/{orgId}/usage` every 30 seconds using your session cookie. Returns `five_hour`, `seven_day`, and `extra_usage` (monthly credits).
- **Real-time push** — a WebSocket server broadcasts state updates to the dashboard whenever files change or the API is polled.

The tool itself uses **zero tokens** — it only reads local files and polls a stats endpoint.

## Token Fields Tracked

| Field | Description |
|---|---|
| `input_tokens` | Prompt tokens sent |
| `output_tokens` | Completion tokens generated |
| `cache_read_input_tokens` | Tokens served from prompt cache |
| `cache_creation_input_tokens` | Tokens written to prompt cache |

## License

MIT
