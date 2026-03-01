# Media Request Skill - Magi Edition

*Updated 2026-02-28: Now uses shared filesystem inter-bot messaging*

Fast, local media library queries for family requests.

## Language Rules (CRITICAL)
- **Default:** English language versions ONLY
- **Foreign films:** Require explicit user approval BEFORE requesting
- **Subtitles:** Only acceptable for foreign language films with user approval
- **When in doubt:** Ask! "This is a French film — want the original with subtitles, or should I look for an English dub?"

**Before requesting any non-English content, confirm with user:**
> "This film is in [language]. Would you like me to request it with subtitles, or would you prefer an English dubbed version if available?"

## Quality Rules (IMPORTANT)
**Movies:**
- Minimum: 1080p (no 720p or lower)
- File size: 2GB - 20GB
- Over 20GB requires user approval
- 4K requires user confirmation before downloading

**TV Shows:**
- Minimum: 720p

**Always Reject:**
- Telesync, CAM, HDCAM, TS, TC copies
- Foreign language audio (unless user explicitly approved)
- Files with "sample" in name (auto-remove)

**Naming:** Clean, standard format (no junk/release tags)

## Environment Variables
```bash
export RADARR_URL="http://10.15.40.89:7878"
export RADARR_KEY="9357c52a8209410cbfabb2cdad6480bf"
export SONARR_URL="http://10.15.40.89:8989"
export SONARR_KEY="09998432e0ec46e590ac9ff9235b4229"
export JELLYFIN_URL="http://192.168.1.96:8096"
export JELLYFIN_KEY="c5b4d7fc157b49778470414e5944b0b2"
export JELLYFIN_PUBLIC="https://jellyfin.ericmorin.online"
```

## Commands Magi Can Run Directly (Read-Only)

### Search Library
```bash
./search-library.sh "movie name" [movie|tv|all]
```
Returns: titles, poster URLs, Jellyfin play links, IMDB links

### Search TMDB (for things not in library)
```bash
./search-tmdb.sh "movie name" [movie|tv]
```
Returns: TMDB results with posters, IMDB links, "inLibrary" flag

### Library Stats
```bash
./library-stats.sh
```
Returns: movie/TV counts, storage size

### Weekly Watch Stats
```bash
./weekly-stats.sh [days]
```
Returns: plays, top watched, recently added

### Quick Connect Auth
```bash
./jellyfin-quickconnect.sh <code>
```
Authorizes Jellyfin login code

## Commands to Route Through Marvin (Write Operations)

### Request Movie
Send via inter-bot system:
```bash
msg-marvin '{"action": "request_movie", "title": "Movie Name", "year": 2024, "requestedBy": "Username"}'
```

Or as JSON to `/mnt/bigstore/interbot/marvin-inbox/`:
```json
{
  "action": "request_movie",
  "title": "Movie Name",
  "year": 2024,
  "requestedBy": "Username"
}
```

Marvin will:
1. Add to Radarr
2. Track download progress
3. Notify Magi when complete via `/mnt/bigstore/interbot/magi-inbox/`

### Check Status
```bash
msg-marvin '{"action": "check_status", "radarrId": 711}'
```

### Search (via Marvin)
```bash
msg-marvin '{"action": "search", "query": "movie title", "type": "movie"}'
```

### Weekly Stats (via Marvin)
```bash
msg-marvin '{"action": "weekly_stats", "days": 7}'
```

### Ping (test connectivity)
```bash
msg-marvin '{"action": "ping"}'
```

## Inter-Bot Communication

**Transport:** Shared filesystem (bigstore NFS)

```
/mnt/bigstore/interbot/
├── marvin-inbox/   # Magi writes here to reach Marvin
├── magi-inbox/     # Marvin writes here to reach Magi
└── processed/      # Archive
```

**Send to Marvin:**
```bash
~/bin/msg-marvin "Your message or JSON here"
# OR
~/bin/interbot-send marvin '{"action": "request_movie", ...}'
```

**Check for responses:**
```bash
~/bin/interbot-check
```

**Processing:** Cron runs every 15 seconds, injects messages into OpenClaw session.

## Example Responses from Marvin

### Request Received
```json
{
  "event": "request_received",
  "status": "ADDED",
  "title": "Paddington",
  "year": 2014,
  "radarrId": 711,
  "message": "Added to download queue"
}
```

### Download Complete
```json
{
  "event": "download_complete",
  "title": "Paddington",
  "year": 2014,
  "quality": "1080p BluRay",
  "jellyfinId": "abc123",
  "playUrl": "https://jellyfin.ericmorin.online/web/...#!/details?id=abc123"
}
```

### Download Failed
```json
{
  "event": "download_failed",
  "title": "Paddington",
  "reason": "No releases found on indexers"
}
```

## User Flow Examples

**"Do we have Paddington?"**
→ Run `search-library.sh "Paddington"`
→ Return poster + "Yes! [Play in Jellyfin]"

**"Can we watch Arrival?"**
→ Run `search-library.sh "Arrival"`
→ If NOT_FOUND: Run `search-tmdb.sh "Arrival"`
→ Show poster + "Not in library. Want me to request it?"
→ If yes: `msg-marvin '{"action": "request_movie", ...}'`

**"What did we watch this week?"**
→ Run `weekly-stats.sh 7`
→ Format top watched list

**"I need to log in" + code**
→ Run `jellyfin-quickconnect.sh <code>`
→ "You're in!"

---

*Previous: MQTT via HA Mosquitto - deprecated 2026-02-28*
