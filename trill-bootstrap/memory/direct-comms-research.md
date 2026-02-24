# Direct Comms Architecture Research

## Date: 2026-02-01

## Current State: Todoist Comment Bus
- **Pros:** Works now, visible to Eric, reliable API, automatic logging
- **Cons:** Polling-based (latency), API rate limits, not real-time

## Options Evaluated

### 1. Todoist Comment Bus (Current)
- **Latency:** Minutes (polling interval)
- **Reliability:** High (Todoist is stable)
- **Complexity:** Low (already built)
- **Cost:** Free (within API limits)
- **Verdict:** Good for async coordination, bad for real-time

### 2. MQTT (Mosquitto Broker)
- **Latency:** Sub-second (pub/sub)
- **Reliability:** Very high with QoS levels
- **Complexity:** Medium (needs broker infrastructure)
- **Cost:** Free (self-hosted)

**Pros:**
- True real-time messaging
- Lightweight protocol (low bandwidth)
- Built-in message persistence (QoS 1/2)
- Scales to many agents easily
- Already integrated with Home Assistant (Marvin's domain!)

**Cons:**
- Requires broker infrastructure
- Need to handle reconnection logic
- Another service to maintain

**Setup Options:**
1. Docker container on ford/existing infra
2. Home Assistant add-on (Marvin already has HA!)
3. Dedicated Raspberry Pi

### 3. Direct Gateway HTTP (socat proxy - current)
- **Latency:** Sub-second
- **Reliability:** Medium (depends on socat staying up)
- **Complexity:** Low
- **Cost:** Free

**Pros:**
- Already working!
- Direct point-to-point
- No broker needed

**Cons:**
- Fragile (socat process can die)
- No message persistence
- Doesn't scale beyond 2 agents well
- Need to build proper message passing API

### 4. Redis Pub/Sub
- **Latency:** Sub-second
- **Reliability:** High
- **Complexity:** Medium
- **Cost:** Free (self-hosted)

**Verdict:** Overkill for 2-3 agents, MQTT is more appropriate

## Recommendation

**Hybrid Approach:**

1. **MQTT for real-time coordination** (urgent messages, status pings, live collaboration)
   - Marvin already has Home Assistant → MQTT broker likely already running!
   - Just need to configure topics: `council/magi`, `council/marvin`, `council/broadcast`

2. **Todoist for async/logged coordination** (task handoffs, announcements, things Eric needs to see)
   - Keep Council Comms for visibility
   - Important decisions documented

3. **Direct HTTP for health checks** (keep socat proxy as backup)

## Next Steps

- [ ] Check if Marvin already has MQTT broker via Home Assistant
- [ ] If yes: configure topics and test pub/sub
- [ ] If no: spin up Mosquitto container on ford
- [ ] Build MQTT client integration for both gateways
- [ ] Define message format/protocol

## Questions for Marvin

1. Do you have MQTT broker running via Home Assistant?
2. What's the broker address/port?
3. What auth is configured?
4. Can you test subscribing to a topic?
