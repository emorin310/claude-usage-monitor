# Marvin Down Incident - 2026-02-23

## Timeline

### 08:00 UTC - Initial Detection
- Eric reported Marvin appears to be down in Discord #general
- Magi began health checks

### 08:05 UTC - Diagnosis Complete
**Status:** CONFIRMED DOWN

**Tests Performed:**
- ✅ Host ping: 192.168.1.201 responds (3.12ms, 0.545ms)
- ❌ Gateway API: `curl http://192.168.1.201:18790/health` - connection failed (timeout)
- ❌ SSH access: Host key verification failed / auth issues

**Likely Causes (in order of probability):**
1. OpenClaw gateway service stopped (most common)
2. Socat proxy died (forwards 18790 -> localhost:18789)
3. Context bloat crash (Marvin has history of >200k token crashes)

### 08:05 UTC - Alerts Sent
- **Todoist:** Health check request posted to Council Handoffs (ID: 6frPQFwgCmJgGvjQ)
- **Discord:** Alert posted to #system-alerts (1475399203793666059)
- **Discord:** Status posted to #council-comms (1475399300421914766)

## Recovery Options

### Option 1: Wait for Marvin Response
- Monitor Todoist Handoffs thread for response
- Marvin may self-recover or respond via alternative means

### Option 2: SSH Recovery (blocked)
Need SSH key setup:
```bash
# When SSH access available:
ssh marvin@marvinbot "systemctl --user restart clawdbot-gateway"
ssh marvin@marvinbot "systemctl --user status clawdbot-gateway"
```

### Option 3: Physical/Remote Access
- Eric may need to check marvinbot directly
- Possible system reboot required

## Historical Context

**Previous Incidents:**
- 2026-02-01: Context bloat crash (207,091 tokens > 200k limit)
- 2026-01-31: Multiple crashes due to session file bloat
- Recovery usually involves: stop gateway → stash large sessions → restart

**Recovery Scripts Available:**
- `~/clawd-magi/scripts/recover-marvin.sh`
- Recovery runbooks in marvin.md

## Status: MONITORING

**Next Actions:**
1. Monitor Todoist/Discord for Marvin response (30 min timeout)
2. If no response, escalate to Eric for manual intervention
3. Document any recovery steps taken

## Notes
- Marvin handles: backups, network infra, Home Assistant, security
- No immediate business impact, but backup/monitoring may be affected
- Good test of multi-agent coordination protocols

---

**Incident Owner:** Magi
**Detection:** Eric manual report
**Response Time:** <5 minutes
**Status:** Active monitoring phase