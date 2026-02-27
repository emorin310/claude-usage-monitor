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

### Implementation Options:

**Option 1: Browser Screenshot (Preferred)**
1. Parse IMDB data for poster URL, ratings, cast
2. Fill HTML template with movie data  
3. Use browser tool to render HTML as image
4. Send image via message tool

**Option 2: Local HTML + Screenshot Tool**
1. Create HTML file in workspace
2. Use headless browser (wkhtmltoimage, playwright, etc.)
3. Generate PNG of card

**Option 3: Canvas/Image Generation Library**
1. Use Python PIL/Pillow or similar
2. Programmatically draw card elements
3. Composite poster image with text/graphics

### Demo Implementation:
```bash
# Install playwright for headless screenshots
npm install -g playwright
playwright install chromium

# Generate card
node scripts/generate-movie-card.js "Life as a House" > /tmp/movie-card.png
```

### Current Status:
- ✅ HTML template created and styled
- ✅ IMDB data parsing working  
- 🔄 Browser tool integration (auth issue to resolve)
- 📋 Alternative: Create standalone card generator script

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