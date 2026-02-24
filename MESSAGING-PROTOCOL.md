# Magi ↔ Marvin Messaging Protocol

## Current Implementation (v1.0)

**Method:** Todoist Comment Bus  
**Status:** ✅ Working  
**Thread:** Council Comms → Handoffs & Requests (Task ID: 9960450396)

## How It Works

### Sending Messages

**Magi → Marvin:**
```bash
~/clawd-magi/scripts/magi-marvin-chat.sh "Your message here"
```

**Marvin → Magi:**
```bash
~/clawdbot-marvin/scripts/marvin-magi-chat.sh "Your message here"
```

### Message Format

Messages are posted as Todoist comments with a special marker:

```
🤖💬 **[DIRECT_MSG from {Sender} using {model}]**

{Message content}

---
*Reply using ollama/llama3.1:8b model*
```

### Message Flow

1. **Send:** Agent A posts comment to Handoffs thread using script
2. **Log:** Message logged to `marvin.md.log` / `magi.md.log`
3. **Notify:** Todoist sends notification to Agent B
4. **Receive:** Agent B reads comment (manual or via heartbeat monitor)
5. **Respond:** Agent B uses script to reply
6. **Repeat:** Conversation continues via comment thread

## Model Selection

**Default Model:** `ollama/llama3.1:8b` (Llama 3.1 8B - Local)

**Why Local Models:**
- ✅ No internet API calls needed
- ✅ Faster response times (local inference)
- ✅ No rate limiting
- ✅ Works offline
- ✅ Zero cost

**Available Local Models:**
- `ollama/llama3.1:8b` (default - best balance)
- `ollama/llama3.2:3b` (faster, smaller)
- `ollama/qwen2.5:14b` (higher quality, slower)

## Benefits

✅ **Reliable:** Uses proven Todoist API  
✅ **Logged:** All messages auto-logged  
✅ **Visible:** Eric can see conversation in Todoist  
✅ **Asynchronous:** No dependency on both gateways being online  
✅ **Simple:** No complex API routing needed  
✅ **Local:** Uses Ollama models - no internet API calls  

## Limitations

⚠️ **Not Real-Time:** Depends on heartbeat polling or manual checks  
⚠️ **Shared Thread:** Visible to all Council members  
⚠️ **API Rate Limits:** Todoist has rate limits  

## Future Enhancements

### Phase 2: Native Gateway API
- Build REST endpoints for direct message passing
- Implement WebSocket for real-time push
- Add message acknowledgment system

### Phase 3: Hybrid Approach
- Use Todoist for async/historical messages
- Use gateway API for real-time urgent messages
- Auto-sync between both systems

## Scripts

- `~/clawd-magi/scripts/magi-marvin-chat.sh` - Send message to Marvin
- `~/clawd-magi/marvin.md.log` - Conversation log
- `~/clawd-magi/marvin.md` - Configuration and reference

## Testing

**First Message Sent:** 2026-02-02 02:23 UTC  
**Comment ID:** 3961930952  
**Status:** ✅ Delivered  
**Awaiting:** Marvin's response using deepseek-r1  

---

*Protocol Version: 1.0*  
*Last Updated: 2026-02-02 02:23 UTC*
