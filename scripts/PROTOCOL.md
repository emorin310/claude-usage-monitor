# Media Request Protocol

## Transport: MQTT via Home Assistant Mosquitto
- **Broker:** 192.168.1.151:1883
- **Credentials:** mqtt / letx
- **Topics:**
  - Magi → Marvin: `bots/marvin/inbox`
  - Marvin → Magi: `bots/magi/inbox`

## Magi → Marvin

### Request Movie
```json
{
  "action": "request_movie",
  "title": "Paddington",
  "year": 2014,           // optional
  "requestedBy": "Eric",  // for notification
  "replySession": "maggie-family"  // session to notify
}
```

### Check Status
```json
{
  "action": "check_status",
  "radarrId": 711
}
```

### Search Library
```json
{
  "action": "search",
  "query": "monty python",
  "type": "movie"  // movie, tv, or all
}
```

### Library Stats
```json
{
  "action": "stats"
}
```

## Marvin → Maggie

### Immediate Response (after request)
```json
{
  "event": "request_received",
  "status": "ADDED|EXISTS|NOT_FOUND|ERROR",
  "title": "Paddington",
  "year": 2014,
  "radarrId": 711,
  "message": "Added to download queue",
  "requestedBy": "Eric"
}
```

### Download Complete (async notification)
```json
{
  "event": "download_complete",
  "title": "Paddington",
  "year": 2014,
  "radarrId": 711,
  "quality": "1080p BluRay",
  "jellyfinId": "abc123",
  "message": "Paddington (2014) is ready to watch! 🍿",
  "requestedBy": "Eric"
}
```

### Download Failed
```json
{
  "event": "download_failed",
  "title": "Paddington",
  "radarrId": 711,
  "reason": "No releases found",
  "requestedBy": "Eric"
}
```

## Flow

1. User tells Maggie: "Can we watch Paddington?"
2. Maggie sends `sessions_send` to Marvin with `request_movie` payload
3. Marvin runs `request-movie.sh`, replies with `request_received`
4. Maggie tells user: "Looking for Paddington, I'll let you know when it's ready"
5. [Async] Radarr downloads, fires webhook to Marvin
6. Marvin verifies in Jellyfin, sends `download_complete` to Maggie
7. Maggie tells user: "Paddington is ready to watch! 🍿"
