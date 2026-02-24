# Agent Failsafe System

**Purpose:** Bulletproof auto-recovery system for when agents get into broken states (model errors, missed heartbeats, config corruption, etc.)

## Components

### 1. Health Monitor (`scripts/health-monitor.sh`)
- Checks heartbeat responsiveness
- Monitors model authentication
- Validates configuration integrity
- Cross-agent communication health

### 2. Failsafe Controller (`scripts/failsafe-controller.sh`)
- Triggers rollbacks based on failure criteria
- Coordinates cross-agent resets
- Preserves critical data during recovery
- Logs all failsafe actions

### 3. Safe Mode Configs (`configs/`)
- `base-safe.json` - Minimal working configuration
- `models-safe.json` - Known-good model mappings
- `channels-safe.json` - Basic Discord-only setup

### 4. Recovery Procedures (`scripts/recovery-*.sh`)
- `agent-reset.sh` - Full agent reset preserving memory
- `config-rollback.sh` - Configuration-only rollback
- `model-reset.sh` - Model authentication reset

### 5. Cross-Agent API (`scripts/cross-agent-*.sh`)
- Marvin ↔ Magi health checking
- Remote reset triggers via MQTT
- Status synchronization

## Usage

### Manual Triggers
```bash
# Emergency reset to safe mode
./scripts/failsafe-controller.sh --emergency-reset

# Reset specific agent
./scripts/failsafe-controller.sh --reset-agent magi

# Check agent health
./scripts/health-monitor.sh --check-all
```

### Automated Monitoring
Cron job runs every 5 minutes, auto-triggers on failure criteria.

### Cross-Agent Triggers
- `@magi reset yourself` - Discord command
- MQTT: `homelab/agents/magi/reset`
- API: `POST /api/agents/magi/reset`

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Magi Agent    │────│  Marvin Agent   │
│  Health Check   │    │  Health Check   │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          └──────┬─────────┬─────┘
                 │         │
         ┌───────▼─────────▼───────┐
         │  Failsafe Controller    │
         │  - Monitor Both Agents  │
         │  - Auto Recovery        │
         │  - Safe Mode Rollback   │
         └─────────────────────────┘
```