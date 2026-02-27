# Jellyfin Media Request Skill

## Workflow for Movie/TV/Anime Requests

When Eric asks about any movie, TV show, or anime video, follow this exact sequence:

### 1. Immediate Response
**Always respond first with:** "Let me check on that for you..."

### 2. Check Homelab Collection
Search the media collection at `/mnt/bigstore/MEDIA/` for the requested title:
```bash
# Search movies
find /mnt/bigstore/MEDIA/movies -iname "*[TITLE]*" 2>/dev/null

# Search TV shows
find /mnt/bigstore/MEDIA/tv -iname "*[TITLE]*" 2>/dev/null

# Search anime
find /mnt/bigstore/MEDIA/anime -iname "*[TITLE]*" 2>/dev/null
```

**If ambiguous results:** Present possible matches and ask user to choose or restate.

### 3. If Not Found
Tell user: "There is not an immediate match in the collection. Let me look it up on IMDB..."

### 4. IMDB Search
Use web_search to find the title on IMDB:
```
web_search query="[TITLE] site:imdb.com"
```

Present result: "I believe this is the title you meant: [TITLE WITH YEAR]. Do you want me to request download?"

### 5. Download Request to Marvin
If user confirms, send IMDB title code to Marvin:

**Format:** `MEDIA_REQUEST: [IMDB_ID] - [TITLE] ([YEAR])`

Wait 15 seconds for Marvin's confirmation.

### 6. User Confirmation
Provide Marvin's response back to Eric.

## Visual Card Generation

When displaying media files, create a rich visual card using HTML/CSS:

### Required Elements:
- **Poster art** (from IMDB or movie database)
- **Title & Year** (large, prominent)
- **Rating badge** (age rating like R, PG-13)
- **Genre & Runtime**
- **User score with visual progress bar**
- **Plot synopsis** (2-3 lines max)
- **Key cast/crew**
- **Action buttons** (Play, Jellyfin link)
- **IMDB link**

### Card Generation Process:
1. **Extract poster URL** from IMDB page or use movie database API
2. **Create HTML template** with movie data
3. **Use browser tool** to render and screenshot the card:
   ```javascript
   // Create styled HTML card
   browser(action="open", targetUrl="data:text/html,<html>...")
   browser(action="screenshot", type="png")
   ```
4. **Send image** using message tool with media parameter

### HTML Card Template:
```html
<!DOCTYPE html>
<html>
<head>
<style>
.movie-card {
  width: 600px;
  height: 300px;
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  border-radius: 15px;
  display: flex;
  overflow: hidden;
  font-family: 'Segoe UI', Arial, sans-serif;
  color: white;
}
.poster {
  width: 200px;
  height: 300px;
  background-size: cover;
  background-position: center;
}
.content {
  padding: 20px;
  flex: 1;
  position: relative;
}
.title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
}
.meta {
  font-size: 14px;
  opacity: 0.8;
  margin-bottom: 15px;
}
.rating-badge {
  background: #666;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.score {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}
.score-circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: conic-gradient(#00d4aa 0deg, #00d4aa [PERCENTAGE]deg, #333 [PERCENTAGE]deg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}
.synopsis {
  font-size: 13px;
  line-height: 1.4;
  opacity: 0.9;
  margin-bottom: 15px;
}
.cast {
  font-size: 12px;
  opacity: 0.7;
}
.buttons {
  position: absolute;
  bottom: 20px;
  right: 20px;
}
.play-btn {
  background: #0066cc;
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}
</style>
</head>
<body>
<div class="movie-card">
  <div class="poster" style="background-image: url('[POSTER_URL]')"></div>
  <div class="content">
    <div class="title">[TITLE] <span style="opacity: 0.7">([YEAR])</span></div>
    <div class="meta">
      <span class="rating-badge">[RATING]</span>
      [YEAR] • [GENRE] • [RUNTIME]
    </div>
    <div class="score">
      <div class="score-circle">
        <span style="font-weight: bold; font-size: 14px;">[SCORE]</span>
      </div>
      <div>
        <div style="font-weight: bold;">User Score</div>
        <div style="font-size: 12px; opacity: 0.7;">[REVIEW_COUNT] reviews</div>
      </div>
    </div>
    <div class="synopsis">[PLOT]</div>
    <div class="cast"><strong>[DIRECTOR]</strong><br/>Cast: [MAIN_ACTORS]</div>
    <div class="buttons">
      <button class="play-btn">▶ Play</button>
    </div>
  </div>
</div>
</body>
</html>
```

### Implementation Status: ✅ COMPLETE

**Card Generation System:**
1. **Puppeteer-based generator** (`scripts/jellyfin-card-generator.js`)
2. **Shared storage location** (`/mnt/bigstore/@Shared Files/movie-cards/`)
3. **Auto-naming** (safe filenames based on title + year)
4. **Fallback support** (placeholder poster if image fails)

### Usage:
```bash
# Generate card for any movie
node scripts/jellyfin-card-generator.js "Movie Title" "Year"

# Auto-generates filename: movie-title-year-card.png
# Saves to: /mnt/bigstore/@Shared Files/movie-cards/
```

### Card Features:
- ✅ Movie poster from IMDB/external sources
- ✅ Visual progress circle for user scores
- ✅ Gradient backgrounds and professional styling
- ✅ Cast, director, synopsis, runtime info
- ✅ Play button + Jellyfin/IMDB links
- ✅ Media type indicator (MOVIE/TV/ANIME)
- ✅ Responsive text truncation
- ✅ Fallback design for missing posters

### Integration:
When implementing the 6-step workflow, call:
```javascript
const { generateMovieCard, searchJellyfinMovie } = require('./scripts/jellyfin-api-card-generator.js');

// Get Jellyfin data first, then generate card with real poster
const jellyfinData = await searchJellyfinMovie(title, year);
const cardPath = await generateMovieCard(movieData, jellyfinData);
// Send cardPath via message tool
```

### Jellyfin API Configuration:
- **Server:** https://jellyfin.ericmorin.online
- **API Key:** Configured in script (c5b4d7fc157b49778470414e5944b0b2)
- **Poster Source:** Real artwork from Jellyfin media server
- **Authentication:** X-Emby-Token header for API access

### Jellyfin Link Best Practices:
- **Use proper URL format** - `#/details?id=${movieId}&serverId=${serverId}`
- **Include serverId parameter** - Lets Jellyfin handle encoding based on session preferences
- **Avoid old URL format** - `index.html#!/details` can force specific transcoding
- **Current approach:** Direct movie links with serverId for optimal playback

## Media Collection Paths
- **Movies:** `/mnt/bigstore/MEDIA/movies/`
- **TV Shows:** `/mnt/bigstore/MEDIA/tv/`
- **Anime:** `/mnt/bigstore/MEDIA/anime/`
- **Jellyfin Server:** `https://jellyfin.ericmorin.online`

## Marvin Communication
- **Channel:** MQTT or direct API
- **Format:** Structured request with IMDB ID
- **Timeout:** 15 seconds for confirmation
- **Fallback:** If no response, inform Eric of request status

---

*This skill ensures consistent, professional media discovery and request handling.*