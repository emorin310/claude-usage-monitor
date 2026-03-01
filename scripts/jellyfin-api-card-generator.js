#!/usr/bin/env node

const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');
const https = require('https');

const CARDS_DIR = '/mnt/bigstore/@Shared Files/movie-cards';
const JELLYFIN_SERVER = 'https://jellyfin.ericmorin.online';
const JELLYFIN_API_KEY = 'c5b4d7fc157b49778470414e5944b0b2';

async function searchJellyfinMovie(title, year) {
  try {
    // Try public API first - search for items without authentication
    const searchUrl = `${JELLYFIN_SERVER}/Items?SearchTerm=${encodeURIComponent(title)}&IncludeItemTypes=Movie&recursive=true&Fields=BasicSyncInfo,CanDelete,Container,PrimaryImageAspectRatio,ProductionYear`;
    
    console.log(`Searching Jellyfin for: ${title} (${year})`);
    console.log(`Search URL: ${searchUrl}`);
    
    const response = await fetch(searchUrl, {
      headers: {
        'X-Emby-Token': JELLYFIN_API_KEY,
        'Accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      console.log(`Jellyfin search failed: ${response.status} ${response.statusText}`);
      return null;
    }
    
    const data = await response.json();
    console.log(`Jellyfin search results: ${data.Items?.length || 0} items found`);
    
    if (!data.Items || data.Items.length === 0) {
      return null;
    }
    
    // Find the best match by title and year
    const movie = data.Items.find(item => 
      item.ProductionYear == year && 
      item.Name.toLowerCase().includes(title.toLowerCase())
    ) || data.Items[0]; // Fallback to first result
    
    if (movie) {
      console.log(`Found movie: ${movie.Name} (${movie.ProductionYear})`);
      
      // Construct poster URL
      let posterUrl = null;
      if (movie.ImageTags?.Primary) {
        posterUrl = `${JELLYFIN_SERVER}/Items/${movie.Id}/Images/Primary?maxHeight=600&quality=90&tag=${movie.ImageTags.Primary}&api_key=${JELLYFIN_API_KEY}`;
      }
      
      return {
        id: movie.Id,
        name: movie.Name,
        year: movie.ProductionYear,
        posterUrl: posterUrl,
        overview: movie.Overview || '',
        originalMovie: movie
      };
    }
    
    return null;
    
  } catch (error) {
    console.log(`Jellyfin API error: ${error.message}`);
    return null;
  }
}

async function generateMovieCard(movieData, jellyfinData = null) {
  // Ensure cards directory exists
  await fs.mkdir(CARDS_DIR, { recursive: true }).catch(() => {});
  
  // Generate filename from movie title and year
  const safeTitle = movieData.title.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase();
  const filename = `${safeTitle}-${movieData.year}-card.png`;
  const outputPath = path.join(CARDS_DIR, filename);

  // Use Jellyfin poster if available, otherwise fallback
  const posterUrl = jellyfinData?.posterUrl || '';
  const posterStyle = posterUrl ? 
    `background: url('${posterUrl}') center/cover;` :
    `background: linear-gradient(135deg, #4a5568 0%, #2d3748 50%, #1a202c 100%);
     display: flex;
     align-items: center;
     justify-content: center;
     font-size: 72px;
     color: #a0aec0;`;

  const htmlTemplate = `<!DOCTYPE html>
<html>
<head>
<style>
body {
  margin: 0;
  padding: 20px;
  background: #000;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.movie-card {
  width: 800px;
  height: 400px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f172a 100%);
  border-radius: 20px;
  display: flex;
  overflow: hidden;
  color: white;
  box-shadow: 0 20px 40px rgba(0,0,0,0.5);
}
.poster {
  width: 270px;
  height: 400px;
  ${posterStyle}
  position: relative;
  border-right: 2px solid rgba(255,255,255,0.1);
}
.poster.fallback::before {
  content: "🎬";
  text-shadow: 0 4px 8px rgba(0,0,0,0.5);
}
.content {
  padding: 30px;
  flex: 1;
  position: relative;
  display: flex;
  flex-direction: column;
}
.title {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 8px;
  background: linear-gradient(45deg, #fff, #e2e8f0);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.year {
  opacity: 0.7;
  font-size: 28px;
}
.meta {
  font-size: 16px;
  opacity: 0.8;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.rating-badge {
  background: #374151;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
}
.score-section {
  display: flex;
  align-items: center;
  margin-bottom: 25px;
}
.score-circle {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, #10b981 0deg, #10b981 ${movieData.scorePercentage * 3.6}deg, #374151 ${movieData.scorePercentage * 3.6}deg, #374151 360deg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  position: relative;
}
.score-inner {
  width: 50px;
  height: 50px;
  background: #1f2937;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
}
.synopsis {
  font-size: 15px;
  line-height: 1.5;
  opacity: 0.9;
  margin-bottom: 20px;
  flex-grow: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
}
.cast-crew {
  font-size: 14px;
  opacity: 0.8;
  margin-bottom: 20px;
}
.buttons {
  display: flex;
  gap: 15px;
  align-items: center;
}
.play-btn {
  background: linear-gradient(45deg, #3b82f6, #1e40af);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
}
.link-btn {
  color: #60a5fa;
  text-decoration: none;
  font-size: 14px;
  opacity: 0.8;
}
.media-type {
  position: absolute;
  top: 15px;
  right: 15px;
  background: rgba(0,0,0,0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}
.jellyfin-sourced {
  position: absolute;
  bottom: 15px;
  left: 15px;
  background: rgba(168, 85, 247, 0.2);
  color: #a855f7;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: bold;
}
</style>
</head>
<body>
<div class="movie-card">
  <div class="poster${posterUrl ? '' : ' fallback'}">
    ${jellyfinData ? '<div class="jellyfin-sourced">JELLYFIN</div>' : ''}
  </div>
  <div class="content">
    <div class="media-type">${movieData.type || 'MOVIE'}</div>
    <div class="title">${movieData.title} <span class="year">(${movieData.year})</span></div>
    <div class="meta">
      <span class="rating-badge">${movieData.rating}</span>
      <span>${movieData.year} • ${movieData.genre} • ${movieData.runtime}</span>
    </div>
    <div class="score-section">
      <div class="score-circle">
        <div class="score-inner">${movieData.score}</div>
      </div>
      <div>
        <div style="font-weight: bold; font-size: 16px;">User Score</div>
        <div style="font-size: 14px; opacity: 0.7;">${movieData.reviewCount}</div>
      </div>
    </div>
    <div class="synopsis">${jellyfinData?.overview || movieData.plot}</div>
    <div class="cast-crew">
      <strong>${movieData.director}</strong><br/>
      Cast: ${movieData.cast}
    </div>
    <div class="buttons">
      <button class="play-btn">▶ Play</button>
      <a href="${movieData.jellyfinUrl}" class="link-btn">Jellyfin</a>
      <a href="${movieData.imdbUrl}" class="link-btn">IMDB</a>
    </div>
  </div>
</div>
</body>
</html>`;

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-web-security']
  });

  const page = await browser.newPage();
  await page.setContent(htmlTemplate);
  await page.setViewport({ width: 840, height: 440 });

  // Wait for images to load
  await new Promise(resolve => setTimeout(resolve, 3000));

  await page.screenshot({
    path: outputPath,
    clip: { x: 0, y: 0, width: 840, height: 440 },
    type: 'png'
  });

  await browser.close();
  
  console.log(`Movie card generated: ${outputPath}`);
  return outputPath;
}

// CLI usage with Life as a House data
if (require.main === module) {
  const args = process.argv.slice(2).reduce((acc, arg, i, arr) => {
    if (arg.startsWith('--')) {
      const key = arg.substring(2);
      if (arr[i + 1] && !arr[i + 1].startsWith('--')) {
        acc[key] = arr[i + 1];
      } else {
        acc[key] = true; // Handle boolean flags
      }
    }
    return acc;
  }, {});

  const movieData = {
    title: args.title,
    year: args.year,
    rating: args.officialRating, // Use officialRating for display
    genre: args.genres,
    runtime: `${Math.floor(args.runtime / 60)}h ${args.runtime % 60}m`, // Convert minutes back to "Hh Mm"
    score: parseFloat(args.communityRating).toFixed(1), // Format to one decimal
    scorePercentage: Math.round(parseFloat(args.communityRating) * 10),
    reviewCount: "N/A", // Not provided by current API, set default
    plot: args.overview,
    director: "N/A", // Not provided by current API, set default
    cast: "N/A",     // Not provided by current API, set default
    jellyfinUrl: args.playUrl, // This should be the direct play URL
    imdbUrl: "https://imdb.com/find?q=" + encodeURIComponent(args.title + " " + args.year), // Dynamic IMDB search
    type: "MOVIE"
  };

  const jellyfinData = {
    id: args.jellyfinId,
    name: args.title,
    year: args.year,
    posterUrl: `${args.jellyfinUrl.split('/#/details')[0]}/Items/${args.jellyfinId}/Images/Primary?maxHeight=600&quality=90&tag=${args.posterTag}&api_key=${args.apiKey}`,
    overview: args.overview,
    originalMovie: {
      ServerId: args.jellyfinUrl.split('serverId=')[1],
    }
  };

  generateMovieCard(movieData, jellyfinData)
    .then(path => console.log(`Card saved to: ${path}`))
    .catch(console.error);
}

module.exports = { generateMovieCard, searchJellyfinMovie, CARDS_DIR };