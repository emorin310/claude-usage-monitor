# Media Request Protocol

## Transport: Shared Filesystem (bigstore NFS)
*Updated 2026-02-28: Migrated from MQTT to filesystem-based inter-bot messaging*

- **Shared Path:** `/mnt/bigstore/interbot/`
- **Magi → Marvin:** Write to `marvin-inbox/`
- **Marvin → Magi:** Write to `magi-inbox/`
- **Processing:** Cron every 15 seconds via `interbot-processor`

### Sending Commands
```bash
# From Magi
msg-marvin '{"action": "request_movie", "title": "Paddington", "year": 2014}'

# From Marvin
msg-magi '{"event": "download_complete", "title": "Paddington"}'
```

## Magi → Marvin

### Request Movie
```json
{
  "action": "request_movie",
  "title": "Paddington",
  "year": 2014,
  "requestedBy": "Eric",
  "replySession": "maggie-family"
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
  "type": "movie"
}
```

### Search TMDB (not in library)
```json
{
  "action": "search_tmdb",
  "query": "new movie",
  "type": "movie"
}
```

### Library Stats
```json
{
  "action": "stats"
}
```

### Weekly Stats
```json
{
  "action": "weekly_stats",
  "days": 7
}
```

### Quick Connect (Jellyfin)
```json
{
  "action": "quickconnect",
  "code": "123456"
}
```

### Ping (test connectivity)
```json
{
  "action": "ping"
}
```

## Marvin → Magi

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

1. User tells Magi: "Can we watch Paddington?"
2. Magi runs `msg-marvin '{"action": "request_movie", ...}'`
3. Marvin's interbot-processor injects message → handled by `interbot-handler.sh`
4. Marvin runs `request-movie.sh`, replies via `notify-magi.sh`
5. Magi tells user: "Looking for Paddington, I'll let you know when it's ready"
6. [Async] Radarr downloads, fires webhook to Marvin
7. Marvin verifies in Jellyfin, sends `download_complete` to Magi
8. Magi tells user: "Paddington is ready to watch! 🍿"

## Scripts (Marvin side)

| Script | Purpose |
|--------|---------|
| `interbot-handler.sh` | Route incoming requests to appropriate handlers |
| `notify-magi.sh` | Send responses back to Magi |
| `request-movie.sh` | Add movie to Radarr |
| `check-download.sh` | Check download progress |
| `search-library.sh` | Search Jellyfin library |
| `search-tmdb.sh` | Search TMDB for movies |
| `weekly-stats.sh` | Generate viewing stats |

## Previous Transport (deprecated)
~~MQTT via Home Assistant Mosquitto (bots/marvin/inbox ↔ bots/magi/inbox)~~
Deprecated 2026-02-28 due to trust/auth issues with external webhook injection.
