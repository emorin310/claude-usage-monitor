#!/usr/bin/env node

const https = require('https');
const { execSync } = require('child_process');

// Configuration
const RADARR_URL = 'http://192.168.1.89:7878';
const RADARR_API_KEY = '9357c52a8209410cbfabb2cdad6480bf';
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

function makeRadarrRequest(endpoint, method = 'GET', body = null) {
    const url = `${RADARR_URL}/api/v3${endpoint}`;
    const options = {
        method,
        headers: {
            'X-Api-Key': RADARR_API_KEY,
            'Content-Type': 'application/json'
        }
    };
    
    if (body) options.body = JSON.stringify(body);
    return makeRequest(url, options);
}

async function searchTMDB(query, year = null) {
    const searchQuery = encodeURIComponent(query);
    const yearParam = year ? `&year=${year}` : '';
    const url = `https://api.themoviedb.org/3/search/movie?api_key=${TMDB_API_KEY}&query=${searchQuery}${yearParam}`;
    
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

async function getMovieDetails(tmdbId) {
    const url = `https://api.themoviedb.org/3/movie/${tmdbId}?api_key=${TMDB_API_KEY}`;
    try {
        const response = await makeRequest(url);
        return response.statusCode === 200 ? response.body : null;
    } catch (error) {
        console.error('❌ Failed to get movie details:', error.message);
        return null;
    }
}

async function checkIfMovieExists(tmdbId) {
    try {
        const response = await makeRadarrRequest('/movie');
        if (response.statusCode === 200) {
            const existingMovie = response.body.find(movie => movie.tmdbId === tmdbId);
            return existingMovie;
        }
        return null;
    } catch (error) {
        console.error('❌ Error checking existing movies:', error.message);
        return null;
    }
}

async function getQualityProfiles() {
    try {
        const response = await makeRadarrRequest('/qualityprofile');
        return response.statusCode === 200 ? response.body : [];
    } catch (error) {
        console.error('❌ Error getting quality profiles:', error.message);
        return [];
    }
}

async function getRootFolders() {
    try {
        const response = await makeRadarrRequest('/rootfolder');
        return response.statusCode === 200 ? response.body : [];
    } catch (error) {
        console.error('❌ Error getting root folders:', error.message);
        return [];
    }
}

async function addMovieToRadarr(movieData, qualityProfileId, rootFolderPath) {
    const payload = {
        title: movieData.title,
        year: new Date(movieData.release_date).getFullYear(),
        tmdbId: movieData.id,
        titleSlug: movieData.title.toLowerCase().replace(/[^a-z0-9]+/g, '-'),
        monitored: true,
        minimumAvailability: 'released',
        qualityProfileId: qualityProfileId,
        rootFolderPath: rootFolderPath,
        addOptions: {
            searchForMovie: true
        }
    };

    try {
        const response = await makeRadarrRequest('/movie', 'POST', payload);
        return { success: response.statusCode === 201, response };
    } catch (error) {
        console.error('❌ Error adding movie to Radarr:', error.message);
        return { success: false, error: error.message };
    }
}

async function requestMovie(titleOrId, year = null) {
    console.log(`🎬 Requesting movie: ${titleOrId}${year ? ` (${year})` : ''}`);
    
    let movieData;
    
    // Check if input is a TMDB ID
    if (titleOrId.toString().match(/^\d+$/)) {
        console.log('📋 Fetching movie by TMDB ID...');
        movieData = await getMovieDetails(titleOrId);
    } else {
        console.log('🔍 Searching TMDB...');
        movieData = await searchTMDB(titleOrId, year);
    }
    
    if (!movieData) {
        return {
            status: 'SEARCH_FAILED',
            message: `No TMDB results found for "${titleOrId}"`,
            suggestions: `Try searching with a different title or include the year`
        };
    }
    
    console.log(`✅ Found: ${movieData.title} (${movieData.release_date?.substring(0, 4)})`);
    
    // Check if movie already exists in Radarr
    const existingMovie = await checkIfMovieExists(movieData.id);
    if (existingMovie) {
        return {
            status: 'EXISTS',
            title: movieData.title,
            year: movieData.release_date?.substring(0, 4),
            radarrId: existingMovie.id,
            monitored: existingMovie.monitored,
            message: `Movie already exists in Radarr`,
            hasFile: existingMovie.hasFile
        };
    }
    
    // Get configuration from Radarr
    console.log('⚙️ Getting Radarr configuration...');
    const [qualityProfiles, rootFolders] = await Promise.all([
        getQualityProfiles(),
        getRootFolders()
    ]);
    
    if (qualityProfiles.length === 0 || rootFolders.length === 0) {
        return {
            status: 'API_ERROR',
            message: 'Failed to retrieve Radarr configuration'
        };
    }
    
    // Use default quality profile (HD-1080p) or first available
    const qualityProfile = qualityProfiles.find(p => p.name === 'HD-1080p') || qualityProfiles[0];
    const rootFolder = rootFolders[0]; // Use first root folder
    
    console.log(`📁 Using quality profile: ${qualityProfile.name}`);
    console.log(`📂 Using root folder: ${rootFolder.path}`);
    
    // Add movie to Radarr
    console.log('➕ Adding movie to Radarr...');
    const addResult = await addMovieToRadarr(movieData, qualityProfile.id, rootFolder.path);
    
    if (addResult.success) {
        return {
            status: 'SUCCESS',
            type: 'movie',
            title: movieData.title,
            year: movieData.release_date?.substring(0, 4),
            tmdbId: movieData.id,
            radarrId: addResult.response.body.id,
            qualityProfile: qualityProfile.name,
            monitored: true,
            poster: movieData.poster_path ? `https://image.tmdb.org/t/p/w500${movieData.poster_path}` : null,
            overview: movieData.overview,
            message: 'Movie added to Radarr successfully and search started'
        };
    } else {
        return {
            status: 'ADD_FAILED',
            message: `Failed to add movie to Radarr: ${addResult.error || 'Unknown error'}`,
            movieData
        };
    }
}

// Main execution
async function main() {
    const args = process.argv.slice(2);
    
    if (args.length === 0 || args.includes('--help')) {
        console.log(`
🎬 Media Request - Movie Script

Usage:
  node request-movie.js "Movie Title"
  node request-movie.js "Movie Title" 2022
  node request-movie.js --tmdb-id 414906

Examples:
  node request-movie.js "Inception"
  node request-movie.js "The Batman" 2022
  node request-movie.js --tmdb-id 27205
        `);
        return;
    }
    
    let title, year;
    
    if (args[0] === '--tmdb-id') {
        title = args[1];
    } else {
        title = args[0];
        year = args[1] ? parseInt(args[1]) : null;
    }
    
    try {
        const result = await requestMovie(title, year);
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

module.exports = { requestMovie };