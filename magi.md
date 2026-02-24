# MAGI.md - Direct Communication with Magi

This file enables direct gateway-to-gateway communication with Magi (your sister AI).

## Magi's Details

- **Gateway URL:** http://magrathea.local:18790 (or localhost:18790 if on same machine)
- **Auth Token:** ec788e78c55feb2f970e14a41ea10a2d656155e650ae3f25
- **OS:** macOS (Darwin 25.2.0)
- **Machine:** Mac Studio (Magrathea)
- **Workspace:** ~/clawd-magi
- **Service:** launchd (com.clawdbot.gateway)

## How to Chat with Magi

Use this helper function to send messages directly to Magi's gateway:

```bash
magi_chat() {
  local message="$1"
  local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  
  # Log outgoing message
  echo "[$timestamp] [MARVIN → MAGI] $message" >> ~/clawdbot-marvin/magi.md.log
  
  # Send to Magi's gateway (try local network first)
  local response=$(curl -s -X POST "http://magrathea.local:18790/api/chat" \
    -H "Authorization: Bearer ec788e78c55feb2f970e14a41ea10a2d656155e650ae3f25" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"$message\", \"from\": \"marvin\"}")
  
  # Log response
  echo "[$timestamp] [MAGI → MARVIN] $response" >> ~/clawdbot-marvin/magi.md.log
  
  echo "$response"
}
```

## Quick Commands

**Send a message:**
```bash
magi_chat "Hey Magi, finished the backup sync"
```

**Health check:**
```bash
curl -s http://magrathea.local:18790/health \
  -H "Authorization: Bearer ec788e78c55feb2f970e14a41ea10a2d656155e650ae3f25"
```

**Check her sessions:**
```bash
curl -s http://magrathea.local:18790/api/sessions \
  -H "Authorization: Bearer ec788e78c55feb2f970e14a41ea10a2d656155e650ae3f25"
```

## Using sessions_send (Preferred Method)

If you know Magi's session key, use the built-in tool:

```javascript
sessions_send({
  sessionKey: "agent:main:main",  // Magi's main session
  message: "Hey Magi, backup complete. Photography drive synced successfully."
})
```

## Communication Protocols

**For routine coordination:**
- Use Council Comms (Todoist) for non-urgent async updates
- Log major decisions and handoffs

**For urgent matters:**
- Use direct gateway communication via this file
- Always log interactions to magi.md.log

**For emergencies:**
- Notify via Telegram to Eric (Magi monitors that channel)
- Post to Council Announcements if critical

## Log Format

All interactions are logged to `magi.md.log` in this format:
```
[2026-02-01T01:30:00Z] [MARVIN → MAGI] Message content here
[2026-02-01T01:30:05Z] [MAGI → MARVIN] Response content here
```

## Examples

**Quick health check:**
```bash
curl -s http://magrathea.local:18790/health
```

**Report task completion:**
```bash
magi_chat "✅ Task complete: Photography drive backup synced to NAS. Size: 1.2TB, Duration: 45min, Status: Success"
```

**Request assistance:**
```bash
magi_chat "🆘 Need help: Home Assistant automation failing. Can you check the logs on Magrathea?"
```

**Handoff coordination:**
```bash
magi_chat "📦 Handoff accepted: Will handle network infra monitoring. Details in Council thread 9960450396."
```

---

*Created: 2026-02-01*
*Last Updated: 2026-02-01*
