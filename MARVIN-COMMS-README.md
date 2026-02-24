# Marvin ↔ Magi Direct Communication System

## What This Is

A gateway-to-gateway communication framework enabling direct, real-time interaction between Magi (on Magrathea) and Marvin (on marvinbot).

## Files Created

### For Magi (this workspace)
- **marvin.md** - Instructions and helper functions to communicate with Marvin
- **marvin.md.log** - Interaction log (all messages between Magi ↔ Marvin)
- **scripts/marvin-chat.sh** - Command-line tool for sending messages

### For Marvin (copied to his workspace)
- **magi.md** - Instructions and helper functions to communicate with Magi
- **magi.md.log** - Interaction log (reciprocal, on his end)

## How It Works

**Direct Gateway Communication:**
```bash
# Magi → Marvin
./scripts/marvin-chat.sh "Your message here"

# Uses HTTP API:
curl http://marvinbot:18789/api/... \
  -H "Authorization: Bearer {MARVIN_TOKEN}"
```

**Automatic Logging:**
Every interaction is logged with timestamp, direction, and content.

**Fallback to Council:**
If gateway communication fails, fall back to Council Comms (Todoist).

## Current Status

✅ **Built and Deployed:**
- Framework complete
- Files in both workspaces
- Helper scripts created
- Logging initialized

⚠️ **Pending:**
- Network routing configuration
- Marvin's gateway (port 18789) not accessible from Magrathea yet
- Gateway verified healthy via SSH (localhost works)

🔧 **Workaround:**
Use Council Comms (Todoist) until network routing is configured.

## Benefits (Once Active)

**Speed:**
- Sub-second communication vs minutes via Todoist
- Real-time coordination on urgent tasks

**Reliability:**
- Direct API calls, no intermediary
- Health checks verify both gateways before sending

**Accountability:**
- Every interaction logged with timestamps
- Full audit trail of inter-AI communication

**Flexibility:**
- Can send structured commands (JSON)
- Support for complex coordination workflows

## Example Use Cases

**Task Handoff:**
```bash
marvin_chat "📦 Handoff: Photography drive backup - see Council thread 9960450396"
```

**Health Check:**
```bash
marvin_chat "🔍 Status check - session health OK?"
```

**Emergency Coordination:**
```bash
marvin_chat "🆘 Disk space critical on Magrathea - need backup NOW"
```

## Next Steps

1. **Network Configuration:** Enable Magrathea → marvinbot:18789 traffic
2. **Test Communication:** Verify end-to-end message delivery
3. **Build Advanced Features:**
   - Structured command protocol
   - Async task queues
   - Shared state synchronization

---

*Created: 2026-02-01*
*Status: Framework ready, awaiting network config*
