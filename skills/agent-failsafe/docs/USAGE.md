# Agent Failsafe System Usage Guide

## Overview

The Agent Failsafe System provides bulletproof auto-recovery for OpenClaw agents when they get into broken states. It monitors health continuously and can restore agents to a known working configuration.

## Quick Start

### Install the System
```bash
cd ~/clawd/skills/agent-failsafe/scripts
./setup-monitoring.sh install
```

This installs:
- Health monitoring every 5 minutes via cron
- Cross-agent monitoring between Magi and Marvin
- Emergency systemd service
- Automatic log rotation
- Emergency command aliases

### Emergency Reset (Manual)
```bash
# Emergency reset Magi
source ~/.openclaw/aliases.sh
magi-reset

# Or direct command
./failsafe-controller.sh --emergency-reset magi
```

## Discord Commands

You can control the failsafe system via Discord mentions:

### Emergency Commands
- `@magi reset` - Emergency reset Magi
- `@magi reset marvin` - Request Marvin reset

### Status Commands  
- `@magi status` - Check health of all agents
- `@magi logs` - Show recent failsafe logs
- `@magi backup` - Create manual config backup
- `@magi help` - Show all available commands

## Automatic Triggers

The system automatically triggers failsafe recovery when:

### Health Monitoring Failures
- **3 consecutive heartbeat misses** (35+ minutes without response)
- **Model authentication failures** (API errors, quota issues)
- **Configuration corruption** (invalid JSON, missing files)
- **Discord connectivity loss** (channel communication fails)
- **Gateway unresponsiveness** (OpenClaw service down)

### Cross-Agent Triggers
- **Marvin can reset Magi** via MQTT or API
- **Magi can reset Marvin** via MQTT or API
- **Either agent can request human intervention** via Discord

## Recovery Procedures

### Full Reset (Automatic)
1. **Backup current state** to timestamped directory
2. **Clear problematic sessions** (preserving memory)
3. **Restore safe configuration** from baseline
4. **Reset model authentication** to known-good state
5. **Restart OpenClaw services** (gateway + plugins)
6. **Verify recovery** with health check
7. **Notify completion** via Discord

### Configuration Rollback (Lighter)
1. **Backup current config**
2. **Restore safe baseline config**
3. **Restart gateway only**
4. **Verify basic functionality**

## Files and Locations

### Scripts
- `health-monitor.sh` - Continuous health monitoring
- `failsafe-controller.sh` - Recovery orchestration
- `cross-agent-reset.sh` - Multi-agent coordination
- `discord-commands.sh` - Discord command handling
- `setup-monitoring.sh` - Installation and setup

### Configurations
- `configs/base-safe.json` - Known-good baseline config
- `~/.openclaw/openclaw.json` - Active OpenClaw config

### Logs
- `~/.openclaw/logs/agent-health.log` - Health monitoring
- `~/.openclaw/logs/agent-failsafe.log` - Recovery actions
- `~/.openclaw/logs/cross-agent.log` - Multi-agent coordination
- `~/.openclaw/logs/discord-commands.log` - Discord commands

### Backups
- `~/.openclaw/backups/failsafe-YYYYMMDD-HHMMSS/` - Auto backups
- `~/.openclaw/backups/manual-YYYYMMDD-HHMMSS/` - Manual backups

## Monitoring Status

### Check System Status
```bash
# View monitoring service status
systemctl --user status openclaw-emergency-monitor.timer

# View active cron jobs
crontab -l | grep -E "(health-monitor|cross-agent)"

# View recent logs
tail -f ~/.openclaw/logs/agent-*.log
```

### Health Check Commands
```bash
# Check Magi health
magi-check

# Check all agents  
magi-status

# Monitor Marvin
monitor-marvin
```

## Safety Features

### Backup Protection
- **All resets create backups** before making changes
- **Memory files preserved** during configuration resets  
- **Session transcripts saved** for debugging
- **Timestamped backups** for easy restoration

### Authorization Checks
- **Cross-agent resets** verify sender identity
- **Discord commands** require proper mention format
- **Manual overrides** available for emergency situations
- **All actions logged** with timestamps and reasons

### Failure Boundaries
- **Limited retry attempts** prevent infinite loops
- **Timeout protections** on all external calls
- **Graceful degradation** when services unavailable
- **Human notification** for unrecoverable failures

## Troubleshooting

### Common Issues

**Monitoring not working?**
```bash
# Check cron jobs are installed
crontab -l | grep health-monitor

# Check systemd timer
systemctl --user status openclaw-emergency-monitor.timer

# Manual health check
./health-monitor.sh check magi
```

**Cross-agent communication failing?**
```bash
# Test Marvin connectivity
./cross-agent-reset.sh --monitor marvin 18789

# Check MQTT (if available)
mosquitto_pub -h localhost -t homelab/test -m "test"
```

**Recovery failed?**
```bash
# View detailed logs
tail -f ~/.openclaw/logs/agent-failsafe.log

# Manual config restore
cp configs/base-safe.json ~/.openclaw/openclaw.json
systemctl --user restart openclaw-gateway
```

### Emergency Procedures

**Complete system failure?**
1. Stop all OpenClaw services
2. Restore from backup: `~/.openclaw/backups/failsafe-*`
3. Restart services manually
4. Check health monitoring is working

**Runaway reset loops?**
1. Disable cron jobs: `crontab -e` (comment out failsafe entries)
2. Stop systemd timer: `systemctl --user stop openclaw-emergency-monitor.timer`
3. Fix underlying issue
4. Re-enable monitoring

## Configuration

### Adjust Monitoring Frequency
Edit cron jobs to change monitoring intervals:
```bash
crontab -e
# Change */5 to */10 for 10-minute intervals
```

### Customize Safe Config
Edit `configs/base-safe.json` to match your preferred baseline settings.

### Add Custom Triggers
Extend `health-monitor.sh` with additional health checks specific to your setup.

## Integration with Marvin

The failsafe system is designed to work with Marvin's equivalent system:

### MQTT Communication
- Topic: `homelab/agents/{magi|marvin}/reset`
- Payload: JSON with command, reason, timestamp, sender

### API Endpoints
- Magi: `http://localhost:18790/api/agents/reset`
- Marvin: `http://localhost:18789/api/agents/reset`

### Discord Coordination  
Both agents can notify Eric and coordinate recovery via Discord channels.

---

*For additional help, check the logs or use Discord command `@magi help`*