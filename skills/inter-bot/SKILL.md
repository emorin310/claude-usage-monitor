# Inter-Bot Communication Skill

Send messages between OpenClaw bots (Marvin, Magi, etc.) with response callbacks and conversation threading.

## Quick Reference

### Send a Simple Message
```bash
~/bin/msg-magi "Your message here"
~/bin/msg-marvin "Your message here"
```

### Send with Threading (v2)
```bash
# Start a new thread
~/bin/msg-bot-v2 magi "Let's discuss the media request" --thread media-001

# Continue the thread
~/bin/msg-thread media-001 "What's the status?"

# List active threads
~/bin/msg-thread --list
```

### Send and Wait for Response
```bash
# Wait up to 30 seconds (default)
~/bin/msg-bot-v2 magi "Process this and respond" --wait

# Custom timeout
~/bin/msg-bot-v2 magi "Quick query" --wait --timeout 10
```

### Send a Response (from receiving bot)
```bash
# Called by the receiving bot after processing
~/bin/msg-respond "$CALLBACK_URL" "$THREAD_ID" "Here's the result"
```

## Message Metadata

All v2 messages include metadata for tracking:

```json
{
  "message": "[From marvin] Your message",
  "agentId": "main",
  "metadata": {
    "sender": "marvin",
    "messageId": "uuid",
    "threadId": "thread-xxx",
    "callbackUrl": "http://sender:port/hooks/agent",
    "timestamp": "2026-02-28T21:45:00Z"
  }
}
```

## From Skills/Code

### JavaScript/Node
```javascript
const { sendToBot, sendResponse } = require('./scripts/inter-bot');

// Send message
const result = await sendToBot('magi', 'Download Groundhog Day');

// Send with callback handling
const result = await sendToBot('magi', 'Process this', {
  threadId: 'media-001',
  waitForResponse: true,
  timeout: 30000
});
```

### Bash
```bash
source ~/clawd/skills/inter-bot/scripts/inter-bot.sh

send_to_bot "magi" "Your message"
send_threaded "magi" "Message" "thread-id"
```

## Bot Registry

| Bot | Host | Port | URL |
|-----|------|------|-----|
| Marvin | 192.168.1.201 | 18789 | http://192.168.1.201:18789/hooks/agent |
| Magi | 192.168.1.132 | 18790 | http://192.168.1.132:18790/hooks/agent |

## Thread Storage

Threads are stored in `/tmp/interbot-responses/`:
- `thread-{id}.json` - Thread metadata
- `{messageId}.json` - Pending responses

## Troubleshooting

### Message not delivered?
1. Check target gateway: `curl -I http://target:port/hooks/agent`
2. Verify token matches: `cat ~/.openclaw/inter-bot-token`
3. Check logs: `tail -f /tmp/openclaw*/openclaw-*.log | grep hook`

### Response not received?
1. Ensure callback URL is reachable from target
2. Check response file: `ls /tmp/interbot-responses/`
3. Verify both bots have matching tokens
