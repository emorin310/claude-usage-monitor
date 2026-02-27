#!/usr/bin/env node

const https = require('https');
const { execSync } = require('child_process');

// Configuration
const SONARR_URL = 'http://192.168.1.89:8989';
const SONARR_API_KEY = '09998432e0ec46e590ac9ff9235b4229';
const TMDB_API_KEY = process.env.TMDB_API_KEY;

if (!TMDB_API_KEY) {
    console.error('❌ Error: TMDB_API_KEY environment variable not set');
    process.exit(1);
}

// Utility functions
function makeRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
        const req = https.request(url, options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    resolve({ statusCode: res.statusCode, body: JSON.parse(data) });
                } catch (e) {
                    resolve({ statusCode: res.statusCode, body: data });
                }
            });
        });
        
        req.on('error', reject);
        if (options.body) req.write(options.body);
        req.end();
    });
}

function makeSonarrRequest(endpoint, method = 'GET', body = null) {
    const url = `${SONARR_URL}/api/v3${endpoint}`;
    const options = {
        method,
        headers: {
            'X-Api-Key': SONARR_API_KEY,
            'Content-Type': 'application/json'
        }
    };
    
    if (body) options.body = JSON.stringify(body);
    return makeRequest(url, options);
}

async function searchTMDB(query, year = null) {
    const searchQuery = encodeURIComponent(query);
    const yearParam = year ? `&first_air_date_year=${year}` : '';
    const url = `https://api.themoviedb.org/3/search/tv?api_key=${TMDB_API_KEY}&query=${searchQuery}${yearParam}`;
    
    try {
        const response = await makeRequest(url);
        if (response.statusCode === 200 && response.body.results?.length > 0) {
            return response.body.results[0]; // Return best match
        }
        return null;
    } catch (error) {
        console.error('❌ TMDB search failed:', error.message);
        return null;
    }
}

async function getTVDetails(tmdbId) {
    const url = `https://api.themoviedb.org/3/tv/${tmdbId}?api_key=${TMDB_API_KEY}`;
    try {
        const response = await makeRequest(url);
        return response.statusCode === 200 ? response.body : null;
    } catch (error) {
        console.error('❌ Failed to get TV details:', error.message);
        return null;
    }
}

async function checkIfSeriesExists(tmdbId) {
    try {
        const response = await makeSonarrRequest('/series');
        if (response.statusCode === 200) {
            const existingSeries = response.body.find(series => series.tmdbId === tmdbId);
            return existingSeries;
        }
        return null;
    } catch (error) {
        console.error('❌ Error checking existing series:', error.message);
        return null;
    }
}

async function getQualityProfiles() {
    try {
        const response = await makeSonarrRequest('/qualityprofile');
        return response.statusCode === 200 ? response.body : [];
    } catch (error) {
        console.error('❌ Error getting quality profiles:', error.message);
        return [];
    }
}

async function getLanguageProfiles() {
    try {
        const response = await makeSonarrRequest('/languageprofile');
        return response.statusCode === 200 ? response.body : [];
    } catch (error) {
        console.error('❌ Error getting language profiles:', error.message);
        return [];
    }
}

async function getRootFolders() {
    try {
        const response = await makeSonarrRequest('/rootfolder');
        return response.statusCode === 200 ? response.body : [];
    } catch (error) {
        console.error('❌ Error getting root folders:', error.message);
        return [];
    }
}

async function addSeriesToSonarr(seriesData, qualityProfileId, languageProfileId, rootFolderPath) {
    const payload = {
        title: seriesData.name,
        year: new Date(seriesData.first_air_date).getFullYear(),
        tmdbId: seriesData.id,
        titleSlug: seriesData.name.toLowerCase().replace(/[^a-z0-9]+/g, '-'),
        monitored: true,
        seasonFolder: true,
        qualityProfileId: qualityProfileId,
        languageProfileId: languageProfileId,
        rootFolderPath: rootFolderPath,
        addOptions: {
            searchForMissingEpisodes: true,
            searchForCutoffUnmetEpisodes: false
        },
        seriesType: rootFolderPath.includes('anime') ? 'anime' : 'standard'
    };

    try {
        const response = await makeSonarrRequest('/series', 'POST', payload);
        return { success: response.statusCode === 201, response };
    } catch (error) {
        console.error('❌ Error adding series to Sonarr:', error.message);
        return { success: false, error: error.message };
    }
}

async function requestTVShow(titleOrId, year = null, isAnime = false) {
    const typeLabel = isAnime ? '🎌 anime' : '📺 TV show';
    console.log(`${typeLabel}: ${titleOrId}${year ? ` (${year})` : ''}`);
    
    let seriesData;
    
    // Check if input is a TMDB ID
    if (titleOrId.toString().match(/^\d+$/)) {
        console.log('📋 Fetching series by TMDB ID...');
        seriesData = await getTVDetails(titleOrId);
    } else {
        console.log('🔍 Searching TMDB...');
        seriesData = await searchTMDB(titleOrId, year);
    }
    
    if (!seriesData) {
        return {
            status: 'SEARCH_FAILED',
            message: `No TMDB results found for "${titleOrId}"`,
            suggestions: `Try searching with a different title or include the year`
        };
    }
    
    console.log(`✅ Found: ${seriesData.name} (${seriesData.first_air_date?.substring(0, 4)})`);
    
    // Check if series already exists in Sonarr
    const existingSeries = await checkIfSeriesExists(seriesData.id);
    if (existingSeries) {
        return {
            status: 'EXISTS',
            title: seriesData.name,
            year: seriesData.first_air_date?.substring(0, 4),
            sonarrId: existingSeries.id,
            monitored: existingSeries.monitored,
            seasons: existingSeries.seasons?.length || 0,
            message: `TV show already exists in Sonarr`
        };
    }
    
    // Get configuration from Sonarr
    console.log('⚙️ Getting Sonarr configuration...');
    const [qualityProfiles, languageProfiles, rootFolders] = await Promise.all([
        getQualityProfiles(),
        getLanguageProfiles(),
        getRootFolders()
    ]);
    
    if (qualityProfiles.length === 0 || languageProfiles.length === 0 || rootFolders.length === 0) {
        return {
            status: 'API_ERROR',
            message: 'Failed to retrieve Sonarr configuration'
        };
    }
    
    // Use default profiles or first available
    const qualityProfile = qualityProfiles.find(p => p.name === 'HD-1080p') || qualityProfiles[0];
    const languageProfile = isAnime 
        ? languageProfiles.find(p => p.name === 'Japanese') || languageProfiles.find(p => p.name === 'Any') || languageProfiles[0]
        : languageProfiles.find(p => p.name === 'English') || languageProfiles[0];
    
    // Select root folder: /anime for anime, /tv for regular shows
    const rootFolder = isAnime 
        ? rootFolders.find(f => f.path.includes('anime')) || rootFolders[1] 
        : rootFolders.find(f => f.path === '/tv') || rootFolders[0];
    
    console.log(`📁 Using quality profile: ${qualityProfile.name}`);
    console.log(`🌐 Using language profile: ${languageProfile.name}`);
    console.log(`📂 Using root folder: ${rootFolder.path}`);
    
    // Add series to Sonarr
    console.log('➕ Adding series to Sonarr...');
    const addResult = await addSeriesToSonarr(
        seriesData, 
        qualityProfile.id, 
        languageProfile.id, 
        rootFolder.path
    );
    
    if (addResult.success) {
        return {
            status: 'SUCCESS',
            type: isAnime ? 'anime' : 'tv',
            title: seriesData.name,
            year: seriesData.first_air_date?.substring(0, 4),
            tmdbId: seriesData.id,
            sonarrId: addResult.response.body.id,
            qualityProfile: qualityProfile.name,
            languageProfile: languageProfile.name,
            monitored: true,
            seasons: seriesData.number_of_seasons || 0,
            episodes: seriesData.number_of_episodes || 0,
            poster: seriesData.poster_path ? `https://image.tmdb.org/t/p/w500${seriesData.poster_path}` : null,
            overview: seriesData.overview,
            status: seriesData.status,
            message: 'TV show added to Sonarr successfully and search started'
        };
    } else {
        return {
            status: 'ADD_FAILED',
            message: `Failed to add TV show to Sonarr: ${addResult.error || 'Unknown error'}`,
            seriesData
        };
    }
}

// Main execution
async function main() {
    const args = process.argv.slice(2);
    const isAnime = args.includes('--anime');
    const filteredArgs = args.filter(a => a !== '--anime');
    
    if (filteredArgs.length === 0 || args.includes('--help')) {
        console.log(`
📺 Media Request - TV Show / Anime Script

Usage:
  node request-tv.js "TV Show Title"
  node request-tv.js "TV Show Title" 2022
  node request-tv.js --tmdb-id 1396
  node request-tv.js --anime "Anime Title"

Options:
  --anime     Add to anime library (separate from TV shows)
  --tmdb-id   Use TMDB ID directly

Examples:
  node request-tv.js "Breaking Bad"
  node request-tv.js "The Office" 2005
  node request-tv.js --anime "Attack on Titan"
  node request-tv.js --anime "Demon Slayer" 2019
        `);
        return;
    }
    
    let title, year;
    
    if (filteredArgs[0] === '--tmdb-id') {
        title = filteredArgs[1];
    } else {
        title = filteredArgs[0];
        year = filteredArgs[1] ? parseInt(filteredArgs[1]) : null;
    }
    
    try {
        const result = await requestTVShow(title, year, isAnime);
        console.log('\n' + '='.repeat(50));
        console.log(JSON.stringify(result, null, 2));
        
        // Exit with appropriate code
        process.exit(result.status === 'SUCCESS' ? 0 : 1);
    } catch (error) {
        console.error('❌ Fatal error:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { requestTVShow };