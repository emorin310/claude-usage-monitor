---
name: media-request
description: Search Jellyfin library for movies/TV shows, return poster cards with play links. Request new content via Marvin for Radarr/Sonarr download.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🎬"
    requires:
      bins: ["curl", "jq"]
      env: ["JELLYFIN_KEY", "RADARR_KEY"]
---

# Media Request Skill - Magi Edition

Fast, local media library queries for family requests.

## Quick Reference

### Search Library (Check if we have it)
```bash
source ~/.bashrc
cd ~/clawd/skills/media-request/scripts
./search-library.sh "movie name" [movie|tv|all]
```

### Search TMDB (Find new content)
```bash
./search-tmdb.sh "movie name" [movie|tv]
```

### Library Stats
```bash
./library-stats.sh
```

### Quick Connect Auth
```bash
./jellyfin-quickconnect.sh <code>
```

## Response Format

When user asks for a movie/show:

1. **Check library first** with search-library.sh
2. If FOUND: Return a card like:
   ```
   🎬 **Paddington** (2014)
   ✅ In Library | 1080p | 1.4 GB
   
   [▶️ Watch on Jellyfin](https://jellyfin.ericmorin.online/web/...)
   [📊 IMDB](https://www.imdb.com/title/...)
   ```

3. If NOT FOUND: Search TMDB, then offer to request:
   ```
   🎬 **Movie Name** (2024)
   ❌ Not in library
   
   Want me to request it? (Marvin will add to Radarr)
   ```

4. If user confirms, send MQTT to Marvin:
   ```bash
   ~/clawd/scripts/mqtt/send-to-marvin.sh "REQUEST_MOVIE: Title (Year) - requested by Username"
   ```

## Quality Rules
- Movies: Minimum 1080p, 2-20GB preferred
- TV: Minimum 720p  
- Reject: CAM, TS, TC, telesync copies

## Environment (in ~/.bashrc)
- JELLYFIN_URL, JELLYFIN_KEY, JELLYFIN_PUBLIC
- RADARR_URL, RADARR_KEY
- SONARR_URL, SONARR_KEY
- TMDB_API_KEY
