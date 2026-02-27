---
name: jellyfin-download
description: Coordinated media request system between Magi (user-facing) and Marvin (download management). Magi checks Jellyfin, Marvin handles Radarr/Sonarr/SABnzbd downloads with real-time status updates.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🎬"
    requires:
      bins: ["curl", "jq", "node"]
      env: ["RADARR_KEY", "SONARR_KEY", "SABNZBD_KEY"]
---

# Jellyfin Download Skill

Coordinated media request workflow between **Magi** (user-facing) and **Marvin** (download backend).

## Overview

```
User → Magi                          Marvin
  │                                    │
  ├─► "Do we have Inception?"          │
  │                                    │
  ├─► [CHECK JELLYFIN - FAST]          │
  │   └─► FOUND? Return card + link    │
  │   └─► NOT FOUND? ──────────────────┼─► MQTT: Request with IMDB ID
  │                                    │
  │                                    ├─► Search Radarr/Sonarr
  │                                    │   └─► NOT FOUND? ──► MQTT: "Not available"
  │                                    │   └─► FOUND? Add to queue
  │                                    │
  │   ◄────────────────────────────────┼─► MQTT: "Found! Starting download"
  │                                    │
  │                                    ├─► Monitor SABnzbd (every 30s)
  │                                    │   └─► No start in 5min? Retry (max 3x)
  │                                    │   └─► Progress updates to Magi
  │                                    │
  │   ◄────────────────────────────────┼─► MQTT: "Download complete!"
  │                                    │
  ├─► "It's ready! [Play Link]"        │
```

---

## Part 1: Magi's Role (User-Facing)

### Step 1: Check Jellyfin First (FAST)

When a user asks for a movie/show/anime:

```bash
source ~/clawd/skills/media-request/env.sh
cd ~/clawd/skills/media-request/scripts
./search-library.sh "Title Name" [movie|tv|all]
```

**If FOUND:** Return a beautiful card immediately:
```
🎬 **Inception** (2010)
✅ In Library | 1080p | 8.2 GB

[▶️ Watch Now](https://jellyfin.ericmorin.online/web/index.html#/details?id=xxx)
[📊 IMDB](https://www.imdb.com/title/tt1375666/)
```

**If NOT FOUND:** Proceed to Step 2.

### Step 2: Search TMDB for Details

```bash
./search-tmdb.sh "Title Name" [movie|tv]
```

This returns IMDB ID, poster, and metadata needed for the request.

### Step 3: Ask User to Confirm

```
🎬 **Inception** (2010)
❌ Not in library

⭐ 8.4/10 | Action, Sci-Fi
📝 "Cobb, a skilled thief who commits corporate espionage..."

Would you like me to request this download?
```

### Step 4: Send Request to Marvin

If user confirms, send MQTT message with IMDB code:

```bash
~/clawd/scripts/mqtt/send-to-marvin.sh "DOWNLOAD_REQUEST|movie|tt1375666|Inception|2010|RequestedBy:Username"
```

**Message Format:**
```
DOWNLOAD_REQUEST|<type>|<imdb_id>|<title>|<year>|RequestedBy:<username>
```

- `type`: movie, tv, anime
- `imdb_id`: IMDB ID (tt1375666 format)
- `title`: Human-readable title
- `year`: Release year
- `RequestedBy`: Who requested it

### Step 5: Wait for Marvin's Response

Magi will receive MQTT updates:
- `DOWNLOAD_STARTED|<title>|ETA: ~2 hours`
- `DOWNLOAD_PROGRESS|<title>|45%|Speed: 15MB/s`
- `DOWNLOAD_COMPLETE|<title>|<jellyfin_play_url>`
- `DOWNLOAD_FAILED|<title>|Reason: Not found on indexers`

Relay these to the user naturally.

---

## Part 2: Marvin's Role (Download Backend)

### Step 1: Receive Request via MQTT

Listen on `bots/marvin/inbox` for messages matching:
```
DOWNLOAD_REQUEST|<type>|<imdb_id>|<title>|<year>|RequestedBy:<username>
```

### Step 2: Search Radarr/Sonarr

**For Movies (Radarr):**
```bash
# Search by IMDB ID
curl -s "http://10.15.40.89:7878/api/v3/movie/lookup?term=imdb:tt1375666" \
  -H "X-Api-Key: 9357c52a8209410cbfabb2cdad6480bf"
```

**For TV/Anime (Sonarr):**
```bash
# Search by IMDB ID
curl -s "http://10.15.40.89:8989/api/v3/series/lookup?term=imdb:tt1375666" \
  -H "X-Api-Key: 09998432e0ec46e590ac9ff9235b4229"
```

### Step 3: Respond Immediately

**If NOT FOUND in Radarr/Sonarr:**
```bash
~/clawd/scripts/mqtt/send-to-magi.sh "DOWNLOAD_FAILED|Inception|Reason: Not found on indexers. Try a different title or check spelling."
```

**If FOUND:** Add to download queue and notify:
```bash
# Add movie to Radarr
curl -X POST "http://10.15.40.89:7878/api/v3/movie" \
  -H "X-Api-Key: 9357c52a8209410cbfabb2cdad6480bf" \
  -H "Content-Type: application/json" \
  -d '{"tmdbId": 27205, "qualityProfileId": 1, "rootFolderPath": "/movies", "addOptions": {"searchForMovie": true}}'

# Notify Magi
~/clawd/scripts/mqtt/send-to-magi.sh "DOWNLOAD_STARTED|Inception (2010)|Searching indexers..."
```

### Step 4: Monitor SABnzbd (Every 30 Seconds)

**Spawn a sub-agent or background task to monitor:**

```bash
# Check SABnzbd queue
curl -s "http://10.15.40.89:8080/api?mode=queue&apikey=<SABNZBD_KEY>&output=json"
```

**Monitoring Logic:**

```
START monitoring
SET retries = 0
SET max_retries = 3
SET start_timeout = 300 (5 minutes)
SET check_interval = 30 (seconds)

LOOP every check_interval:
  1. Query SABnzbd queue for the title
  
  2. IF download found in queue:
     - Get percentage, speed, ETA
     - Send progress update to Magi every 2 minutes (or on significant change)
     - IF percentage == 100%:
       - Wait 60s for post-processing
       - Verify in Jellyfin
       - Send DOWNLOAD_COMPLETE to Magi
       - EXIT
  
  3. IF download NOT in queue AND time < start_timeout:
     - Continue waiting (indexer search in progress)
  
  4. IF download NOT in queue AND time >= start_timeout:
     - retries += 1
     - IF retries <= max_retries:
       - Trigger new search in Radarr/Sonarr
       - Send "Retry attempt {retries}/3" to Magi
       - Reset start_timeout timer
     - ELSE:
       - Send DOWNLOAD_FAILED to Magi
       - EXIT
```

### Step 5: Progress Updates to Magi

**Every 2 minutes (or on 25% milestones):**
```bash
~/clawd/scripts/mqtt/send-to-magi.sh "DOWNLOAD_PROGRESS|Inception (2010)|67%|Speed: 22MB/s|ETA: 12min"
```

### Step 6: Completion Notification

When download completes and appears in Jellyfin:

```bash
# Get Jellyfin play URL
JELLYFIN_ID=$(curl -s "http://192.168.1.96:8096/Items?searchTerm=Inception&IncludeItemTypes=Movie&Recursive=true" \
  -H "X-Emby-Token: c5b4d7fc157b49778470414e5944b0b2" | jq -r '.Items[0].Id')

PLAY_URL="https://jellyfin.ericmorin.online/web/index.html#/details?id=${JELLYFIN_ID}"

~/clawd/scripts/mqtt/send-to-magi.sh "DOWNLOAD_COMPLETE|Inception (2010)|${PLAY_URL}"
```

---

## API Reference

### Radarr
- **URL:** http://10.15.40.89:7878
- **API Key:** 9357c52a8209410cbfabb2cdad6480bf
- **Docs:** /api/v3/movie, /api/v3/queue

### Sonarr  
- **URL:** http://10.15.40.89:8989
- **API Key:** 09998432e0ec46e590ac9ff9235b4229
- **Docs:** /api/v3/series, /api/v3/queue

### SABnzbd
- **URL:** http://10.15.40.89:8080
- **API Key:** Check container config
- **Queue:** /api?mode=queue&output=json
- **History:** /api?mode=history&output=json

### Jellyfin
- **URL:** http://192.168.1.96:8096
- **Public:** https://jellyfin.ericmorin.online
- **API Key:** c5b4d7fc157b49778470414e5944b0b2

### MQTT
- **Broker:** 192.168.1.151:1883
- **Credentials:** mqtt / letx
- **Marvin inbox:** bots/marvin/inbox
- **Magi inbox:** bots/magi/inbox

---

## Message Protocol

### Magi → Marvin

| Message | Format |
|---------|--------|
| Download Request | `DOWNLOAD_REQUEST\|<type>\|<imdb_id>\|<title>\|<year>\|RequestedBy:<user>` |
| Cancel Request | `DOWNLOAD_CANCEL\|<imdb_id>` |
| Status Check | `DOWNLOAD_STATUS\|<imdb_id>` |

### Marvin → Magi

| Message | Format |
|---------|--------|
| Started | `DOWNLOAD_STARTED\|<title>\|<message>` |
| Progress | `DOWNLOAD_PROGRESS\|<title>\|<percent>%\|Speed: <speed>\|ETA: <eta>` |
| Complete | `DOWNLOAD_COMPLETE\|<title>\|<jellyfin_url>` |
| Failed | `DOWNLOAD_FAILED\|<title>\|Reason: <reason>` |
| Not Found | `DOWNLOAD_NOTFOUND\|<title>\|<suggestions>` |

---

## Quality Rules

**Movies:**
- Minimum: 1080p (no 720p or lower)
- Preferred: 2GB - 20GB file size
- Over 20GB: Requires user approval
- 4K: Requires explicit user request

**TV Shows / Anime:**
- Minimum: 720p
- Preferred: 1080p when available

**Always Reject:**
- CAM, Telesync, HDCAM, TS, TC copies
- Foreign audio (unless requested)
- Sample files

---

## Retry Logic

```
Attempt 1: Initial search triggered by Radarr/Sonarr
           Wait up to 5 minutes for download to appear in SABnzbd

Attempt 2: If no download after 5 min, trigger manual search
           Wait another 5 minutes

Attempt 3: Final attempt with manual search
           Wait 5 minutes

FAILURE:   After 3 failed attempts (15 min total), notify Magi
           "Unable to find a suitable release. The title may not be 
           available on current indexers. Try again later or check 
           if the title/year is correct."
```

---

## Example Flow

**User:** "Hey Magi, can we watch Dune?"

**Magi:** 
1. Runs `search-library.sh "Dune" movie`
2. NOT_FOUND
3. Runs `search-tmdb.sh "Dune" movie`
4. Shows: "Dune (2021) - Not in library. Want me to request it?"

**User:** "Yes please!"

**Magi:** 
5. Sends: `DOWNLOAD_REQUEST|movie|tt1160419|Dune|2021|RequestedBy:Eric`
6. Tells user: "I've asked Marvin to find it. I'll let you know when it's ready!"

**Marvin:**
7. Receives request, searches Radarr
8. Found! Adds to queue, triggers search
9. Sends: `DOWNLOAD_STARTED|Dune (2021)|Searching indexers...`
10. Spawns monitor sub-agent

**Marvin (monitor):**
11. Checks SABnzbd every 30s
12. Download found at 0% → sends progress
13. At 50% → `DOWNLOAD_PROGRESS|Dune (2021)|50%|Speed: 18MB/s|ETA: 25min`
14. At 100% → waits for post-processing
15. Verifies in Jellyfin
16. Sends: `DOWNLOAD_COMPLETE|Dune (2021)|https://jellyfin.ericmorin.online/web/...`

**Magi:**
17. Receives completion
18. Tells user: "🎬 **Dune (2021)** is ready! [▶️ Watch Now](https://...)"

---

## Scripts Location

- **Magi:** `~/clawd/skills/media-request/scripts/`
- **Marvin:** `~/clawd/skills/media-request/scripts/` + `~/clawd/skills/jellyfin-download/scripts/`

---

*Created: 2026-02-27*
*Authors: Marvin & Eric*
