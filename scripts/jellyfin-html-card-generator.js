#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');

const CARDS_DIR = '/mnt/bigstore/@Shared Files/movie-cards';
const JELLYFIN_SERVER = 'https://jellyfin.ericmorin.online';
const JELLYFIN_API_KEY = 'c5b4d7fc157b49778470414e5944b0b2';

async function searchJellyfinMovie(title, year) {
  try {
    const searchUrl = `${JELLYFIN_SERVER}/Items?SearchTerm=${encodeURIComponent(title)}&IncludeItemTypes=Movie&recursive=true&Fields=BasicSyncInfo,CanDelete,Container,PrimaryImageAspectRatio,ProductionYear`;
    
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
    
    if (!data.Items || data.Items.length === 0) {
      return null;
    }
    
    const movie = data.Items.find(item => 
      item.ProductionYear == year && 
      item.Name.toLowerCase().includes(title.toLowerCase())
    ) || data.Items[0];
    
    if (movie) {
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
        jellyfinUrl: `${JELLYFIN_SERVER}/web/#/details?id=${movie.Id}&serverId=${movie.ServerId}`,
        originalMovie: movie
      };
    }
    
    return null;
    
  } catch (error) {
    console.log(`Jellyfin API error: ${error.message}`);
    return null;
  }
}

async function generateInteractiveMovieCard(movieData, jellyfinData = null) {
  // Ensure cards directory exists
  await fs.mkdir(CARDS_DIR, { recursive: true }).catch(() => {});
  
  // Generate filename from movie title and year
  const safeTitle = movieData.title.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase();
  const htmlFilename = `${safeTitle}-${movieData.year}-card.html`;
  const htmlOutputPath = path.join(CARDS_DIR, htmlFilename);

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

  const htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${movieData.title} (${movieData.year}) - Movie Card</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: #000;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
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
            position: relative;
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
            text-decoration: none;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .play-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
        }
        .link-btn {
            color: #60a5fa;
            text-decoration: none;
            font-size: 14px;
            opacity: 0.8;
            padding: 8px 12px;
            border-radius: 6px;
            transition: background-color 0.2s, opacity 0.2s;
        }
        .link-btn:hover {
            background-color: rgba(96, 165, 250, 0.1);
            opacity: 1;
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
        .found-in-collection {
            position: absolute;
            top: 50px;
            right: 15px;
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            padding: 4px 8px;
            border-radius: 4px;
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
            <div class="found-in-collection">✓ IN COLLECTION</div>
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
                <a href="${jellyfinData?.jellyfinUrl || movieData.jellyfinUrl}" class="play-btn" target="_blank">
                    ▶ Play in Jellyfin
                </a>
                <a href="${movieData.imdbUrl}" class="link-btn" target="_blank">IMDB</a>
                <a href="${JELLYFIN_SERVER}/web/" class="link-btn" target="_blank">Jellyfin Server</a>
            </div>
        </div>
    </div>
</body>
</html>`;

  await fs.writeFile(htmlOutputPath, htmlContent);
  console.log(`Interactive movie card generated: ${htmlOutputPath}`);
  return htmlOutputPath;
}

// CLI usage
if (require.main === module) {
  const movieData = {
    title: "Life as a House",
    year: "2001",
    rating: "R",
    genre: "Drama",
    runtime: "2h 5m",
    score: "74",
    scorePercentage: 74,
    reviewCount: "47K reviews",
    plot: "When a man is diagnosed with terminal cancer, he takes custody of his misanthropic teenage son. Together they embark on building a house - and rebuilding their relationship.",
    director: "Irwin Winkler",
    cast: "Kevin Kline, Hayden Christensen, Kristin Scott Thomas",
    jellyfinUrl: "https://jellyfin.ericmorin.online",
    imdbUrl: "https://imdb.com/title/tt0264796/",
    type: "MOVIE"
  };

  searchJellyfinMovie(movieData.title, movieData.year)
    .then(jellyfinData => {
      console.log('Jellyfin data:', jellyfinData);
      return generateInteractiveMovieCard(movieData, jellyfinData);
    })
    .then(path => console.log(`Interactive card saved to: ${path}`))
    .catch(console.error);
}

module.exports = { generateInteractiveMovieCard, searchJellyfinMovie, CARDS_DIR };