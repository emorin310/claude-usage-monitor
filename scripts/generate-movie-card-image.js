#!/usr/bin/env node

const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

async function generateMovieCardImage(movieData, outputPath) {
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
  background: url('${movieData.posterUrl}') center/cover;
  position: relative;
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
</style>
</head>
<body>
<div class="movie-card">
  <div class="poster"></div>
  <div class="content">
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
    <div class="synopsis">${movieData.plot}</div>
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
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setContent(htmlTemplate);
  await page.setViewport({ width: 840, height: 440 });

  await page.screenshot({
    path: outputPath,
    clip: { x: 0, y: 0, width: 840, height: 440 },
    type: 'png'
  });

  await browser.close();
  return outputPath;
}

// Movie data for "Life as a House"
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
  posterUrl: "https://m.media-amazon.com/images/M/MV5BMTgxOTY4Mjc0MF5BMl5BanBnXkFtZTYwNTc0MDQ3._V1_SX300.jpg",
  jellyfinUrl: "https://jellyfin.ericmorin.online",
  imdbUrl: "https://imdb.com/title/tt0264796/"
};

// Generate the card
if (require.main === module) {
  const outputPath = process.argv[2] || '/mnt/bigstore/@Shared Files/movie-cards/life-as-a-house-card.png';
  
  generateMovieCardImage(movieData, outputPath)
    .then(path => {
      console.log(`Movie card generated: ${path}`);
    })
    .catch(console.error);
}

module.exports = { generateMovieCardImage };