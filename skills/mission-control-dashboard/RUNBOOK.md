# Mission Control Dashboard - Runbook

## Service Details
- **URL:** http://192.168.1.132:3002
- **Process:** `mega-dark-dashboard-dragdrop.js`
- **Tier:** 1 (Critical Infrastructure)
- **Owner:** Marvin Jr.

## Management Commands
```bash
# Status / Start / Stop / Restart
systemctl --user status mission-control
systemctl --user start mission-control
systemctl --user stop mission-control
systemctl --user restart mission-control

# Logs (live)
journalctl --user -u mission-control -f

# App log
tail -f ~/clawd/skills/mission-control-dashboard/mission-control.log

# Health check log
cat ~/clawd/skills/mission-control-dashboard/health-check.log
```

## Architecture
- **Supervision:** systemd user service (auto-restart on crash, 5s delay)
- **Monitoring:** Cron health check every 5 min (`mission-control-health.sh`)
- **Lingering:** Enabled — survives SSH logout
- **Restart limits:** 5 restarts per 5 minutes before giving up

## Troubleshooting
1. **Dashboard unreachable:** Check `systemctl --user status mission-control`
2. **Repeated crashes:** Check logs for stack traces, look at restart count
3. **Port conflict:** `ss -tlnp | grep 3002`
4. **Node issues:** Verify `node -v`, check `node_modules` integrity
5. **After reboot:** Service auto-starts via `enable` + `linger`

## Recovery
If systemd service is in failed state:
```bash
systemctl --user reset-failed mission-control
systemctl --user start mission-control
```
