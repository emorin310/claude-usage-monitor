# Multi-Agent Setup Guide (OpenClaw)

*Lessons learned from Magi's setup — March 7, 2026*

## Overview

One OpenClaw gateway can host multiple isolated agents that communicate via `sessions_spawn` and `sessions_send`. Each agent has its own workspace, identity, sessions, and model.

## Quick Setup

### 1. Create the Agent

```bash
# Create workspace and register in one shot
mkdir -p ~/new-agent
openclaw agents add new-agent \
  --non-interactive \
  --workspace ~/new-agent \
  --model google/gemini-2.5-flash
```

### 2. Give It Identity

Create these files in the workspace:
- `IDENTITY.md` — name, emoji, vibe
- `SOUL.md` — personality, boundaries, purpose
- `AGENTS.md` — operating instructions
- `USER.md` — who it serves

### 3. Enable Cross-Agent Spawning

**This is the key step most people miss.** The main agent needs permission to spawn other agents:

```bash
# Allow main agent to spawn any other agent
openclaw config set agents.list '[
  {
    "id": "main",
    "workspace": "/path/to/main/workspace",
    "subagents": { "allowAgents": ["*"] }
  },
  {
    "id": "new-agent",
    "workspace": "/path/to/new-agent"
  }
]'
```

Or to allow only specific agents: `"allowAgents": ["new-agent", "other-agent"]`

### 4. Enable Agent-to-Agent Messaging (optional)

For cross-agent session history and direct messaging:

```bash
openclaw config set tools.agentToAgent '{"enabled": true, "allow": ["main", "new-agent"]}'
```

### 5. Restart Gateway

```bash
systemctl --user daemon-reload && systemctl --user restart openclaw-gateway.service
```

### 6. Verify

```bash
openclaw agents list --bindings
```

From the main agent, `agents_list` should show all agents with `allowAny: true`.

### 7. Test Comms

From the main agent session, spawn a test:
```
sessions_spawn(agentId="new-agent", runtime="subagent", mode="run", task="Say hello")
```

## Architecture (No Channel Adapters Needed)

Sub-agents don't need their own Discord/Telegram bots. The main agent acts as the relay:

```
Discord ←→ Magi (main) ←→ Beeb (subagent)
                        ←→ Marvin Jr. (subagent)
                        ←→ Any future agent
```

Sub-agents communicate via `sessions_spawn` / `sessions_send`. Main agent relays results to Discord.

## ⚠️ Pitfalls & Gotchas

### 1. `subagents.allowAgents` vs `tools.agentToAgent`

These are **different things**:
- **`subagents.allowAgents`** (per-agent in `agents.list[]`) → controls `sessions_spawn` with a different `agentId`. **Required for cross-agent spawning.**
- **`tools.agentToAgent`** (global in `tools`) → controls cross-agent session history/messaging visibility.

You need BOTH for full inter-agent comms. Most importantly, you need `subagents.allowAgents` on the parent agent.

### 2. systemd Drop-In Overrides

**The #1 time waster.** Check for drop-in override files:

```bash
ls ~/.config/systemd/user/openclaw-gateway.service.d/
```

If `env.conf` (or any `.conf`) exists there, it **overrides** env vars from the main service file. This means:
- `openclaw gateway install --force` updates the service file
- But the drop-in silently injects old values on top

**Fix:** Remove stale `OPENCLAW_GATEWAY_TOKEN` from any drop-in files, or delete the drop-in entirely if not needed.

### 3. Gateway Token Sync

Three places must agree:
1. **Config file:** `gateway.auth.token` + `gateway.remote.token`
2. **Service file:** `Environment=OPENCLAW_GATEWAY_TOKEN=...`
3. **Drop-in overrides:** Any `.conf` in `openclaw-gateway.service.d/`

If any mismatch → `unauthorized: gateway token mismatch` on subagent spawn (even if the main session works fine).

**Simplest approach:** Don't use gateway tokens at all for local-only setups:
```bash
openclaw config unset gateway.auth.token
openclaw config unset gateway.remote.token
# Remove from drop-ins too
```

### 4. Always `daemon-reload` Before Restart

```bash
# WRONG — uses cached service file
systemctl --user restart openclaw-gateway.service

# RIGHT — re-reads service file first
systemctl --user daemon-reload && systemctl --user restart openclaw-gateway.service
```

### 5. `openclaw config get` Redacts Tokens

Running `openclaw config get gateway.auth.token` returns `__OPENCLAW_REDACTED__`. Don't pipe this into `config set` — you'll set the literal string as your token.

### 6. Agent Restarts Kill Your Session

When you restart the gateway from within an agent session, the session dies mid-command. Config changes that require restart can't be verified from inside. Either:
- Have the human run restarts from SSH
- Use `openclaw gateway install --force && systemctl --user daemon-reload && systemctl --user restart openclaw-gateway.service` as a single SSH command

## SSH Emergency Aliases

Add to `~/.openclaw/aliases.sh` (sourced in `.bashrc`):

```bash
# Model switching (emergency override)
magi-opus()   { openclaw config set agents.defaults.model.primary anthropic/claude-opus-4-6 && systemctl --user restart openclaw-gateway.service; }
magi-sonnet() { openclaw config set agents.defaults.model.primary anthropic/claude-sonnet-4-6 && systemctl --user restart openclaw-gateway.service; }
magi-gemini() { openclaw config set agents.defaults.model.primary google/gemini-2.5-flash && systemctl --user restart openclaw-gateway.service; }
magi-haiku()  { openclaw config set agents.defaults.model.primary anthropic/claude-haiku-4-5-20251001 && systemctl --user restart openclaw-gateway.service; }
```

## Debugging Checklist

If subagent spawn fails with token mismatch:

1. **Check live process token:** `cat /proc/$(pgrep -f openclaw-gatewa | head -1)/environ | tr '\0' '\n' | grep GATEWAY_TOKEN`
2. **Check service file:** `grep TOKEN ~/.config/systemd/user/openclaw-gateway.service`
3. **Check drop-ins:** `cat ~/.config/systemd/user/openclaw-gateway.service.d/*.conf 2>/dev/null | grep TOKEN`
4. **Check config:** `openclaw config get gateway`
5. **All must match** (or all be absent for no-token local mode)

## Reference

- Docs: https://docs.openclaw.ai/concepts/multi-agent.md
- Config keys: `agents.list[].subagents.allowAgents`, `tools.agentToAgent`
- CLI: `openclaw agents add|list|bind|delete`
