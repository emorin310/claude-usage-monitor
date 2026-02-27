#!/usr/bin/env node

const https = require('https');
const http = require('http');

// Configuration
const RADARR_URL = 'http://192.168.1.89:7878';
const RADARR_API_KEY = '9357c52a8209410cbfabb2cdad6480bf';
const SONARR_URL = 'http://192.168.1.89:8989';
const SONARR_API_KEY = '09998432e0ec46e590ac9ff9235b4229';
const JELLYFIN_URL = 'http://192.168.1.89:8096';

// Utility functions
function makeRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
        const protocol = url.startsWith('https:') ? https : http;
        const req = protocol.request(url, options, (res) => {
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

function makeRadarrRequest(endpoint) {
    const url = `${RADARR_URL}/api/v3${endpoint}`;
    const options = {
        headers: { 'X-Api-Key': RADARR_API_KEY }
    };
    return makeRequest(url, options);
}

function makeSonarrRequest(endpoint) {
    const url = `${SONARR_URL}/api/v3${endpoint}`;
    const options = {
        headers: { 'X-Api-Key': SONARR_API_KEY }
    };
    return makeRequest(url, options);
}

function makeJellyfinRequest(endpoint) {
    const url = `${JELLYFIN_URL}${endpoint}`;
    return makeRequest(url);
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function formatDuration(minutes) {
    if (minutes < 60) return `${minutes} minutes`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
}

async function getRadarrQueue() {
    try {
        const response = await makeRadarrRequest('/queue');
        return response.statusCode === 200 ? response.body.records : [];
    } catch (error) {
        console.error('❌ Error fetching Radarr queue:', error.message);
        return [];
    }
}

async function getSonarrQueue() {
    try {
        const response = await makeSonarrRequest('/queue');
        return response.statusCode === 200 ? response.body.records : [];
    } catch (error) {
        console.error('❌ Error fetching Sonarr queue:', error.message);
        return [];
    }
}

async function getRadarrMovies() {
    try {
        const response = await makeRadarrRequest('/movie');
        return response.statusCode === 200 ? response.body : [];
    } catch (error) {
        console.error('❌ Error fetching Radarr movies:', error.message);
        return [];
    }
}

async function getSonarrSeries() {
    try {
        const response = await makeSonarrRequest('/series');
        return response.statusCode === 200 ? response.body : [];
    } catch (error) {
        console.error('❌ Error fetching Sonarr series:', error.message);
        return [];
    }
}

async function searchJellyfinLibrary(query) {
    try {
        const encodedQuery = encodeURIComponent(query);
        const response = await makeJellyfinRequest(`/Items?searchTerm=${encodedQuery}&Recursive=true&IncludeItemTypes=Movie,Series`);
        
        if (response.statusCode === 200 && response.body.Items) {
            return response.body.Items.filter(item => 
                item.Name.toLowerCase().includes(query.toLowerCase())
            );
        }
        return [];
    } catch (error) {
        console.error('❌ Error searching Jellyfin:', error.message);
        return [];
    }
}

async function checkAllActiveDownloads() {
    console.log('📊 Checking all active downloads...\n');
    
    const [radarrQueue, sonarrQueue] = await Promise.all([
        getRadarrQueue(),
        getSonarrQueue()
    ]);
    
    const allDownloads = [];
    
    // Process Radarr queue
    for (const item of radarrQueue) {
        const downloadInfo = {
            type: 'movie',
            title: item.movie?.title || 'Unknown Movie',
            year: item.movie?.year,
            status: getDownloadStatus(item),
            progress: item.sizeleft !== undefined ? 
                ((item.size - item.sizeleft) / item.size * 100) : 0,
            eta: item.timeleft || 'Unknown',
            quality: item.quality?.quality?.name || 'Unknown',
            size: formatBytes(item.size || 0),
            downloaded: formatBytes((item.size - item.sizeleft) || 0),
            downloadClient: item.downloadClient,
            indexer: item.indexer,
            id: item.movieId
        };
        
        if (item.statusMessages?.length > 0) {
            downloadInfo.warnings = item.statusMessages.map(msg => msg.title);
        }
        
        allDownloads.push(downloadInfo);
    }
    
    // Process Sonarr queue
    for (const item of sonarrQueue) {
        const downloadInfo = {
            type: 'tv',
            title: item.series?.title || 'Unknown Series',
            year: item.series?.year,
            episode: item.episode ? `S${item.episode.seasonNumber?.toString().padStart(2, '0')}E${item.episode.episodeNumber?.toString().padStart(2, '0')} - ${item.episode.title}` : 'Unknown Episode',
            status: getDownloadStatus(item),
            progress: item.sizeleft !== undefined ? 
                ((item.size - item.sizeleft) / item.size * 100) : 0,
            eta: item.timeleft || 'Unknown',
            quality: item.quality?.quality?.name || 'Unknown',
            size: formatBytes(item.size || 0),
            downloaded: formatBytes((item.size - item.sizeleft) || 0),
            downloadClient: item.downloadClient,
            indexer: item.indexer,
            id: item.seriesId
        };
        
        if (item.statusMessages?.length > 0) {
            downloadInfo.warnings = item.statusMessages.map(msg => msg.title);
        }
        
        allDownloads.push(downloadInfo);
    }
    
    return allDownloads;
}

function getDownloadStatus(queueItem) {
    if (queueItem.status === 'completed') return 'COMPLETED';
    if (queueItem.status === 'downloading') return 'DOWNLOADING';
    if (queueItem.status === 'queued') return 'QUEUED';
    if (queueItem.status === 'paused') return 'PAUSED';
    if (queueItem.status === 'failed') return 'FAILED';
    if (queueItem.status === 'warning') return 'WARNING';
    return queueItem.status?.toUpperCase() || 'UNKNOWN';
}

async function checkSpecificItem(query, fullCheck = false) {
    console.log(`🔍 Searching for: ${query}\n`);
    
    const [movies, series] = await Promise.all([
        getRadarrMovies(),
        getSonarrSeries()
    ]);
    
    // Search in movies
    const matchingMovies = movies.filter(movie => 
        movie.title.toLowerCase().includes(query.toLowerCase())
    );
    
    // Search in series  
    const matchingSeries = series.filter(series => 
        series.title.toLowerCase().includes(query.toLowerCase())
    );
    
    const results = [];
    
    // Process matching movies
    for (const movie of matchingMovies) {
        const movieInfo = {
            type: 'movie',
            title: movie.title,
            year: movie.year,
            radarrId: movie.id,
            tmdbId: movie.tmdbId,
            monitored: movie.monitored,
            hasFile: movie.hasFile,
            status: movie.hasFile ? 'AVAILABLE' : (movie.monitored ? 'MONITORED' : 'UNMONITORED'),
            qualityProfile: movie.qualityProfileId,
            path: movie.path
        };
        
        if (movie.movieFile) {
            movieInfo.fileInfo = {
                size: formatBytes(movie.movieFile.size),
                quality: movie.movieFile.quality?.quality?.name,
                resolution: movie.movieFile.quality?.quality?.resolution,
                dateAdded: movie.movieFile.dateAdded
            };
        }
        
        // Check download queue for this movie
        const queueItem = (await getRadarrQueue()).find(q => q.movieId === movie.id);
        if (queueItem) {
            movieInfo.downloadStatus = {
                status: getDownloadStatus(queueItem),
                progress: queueItem.sizeleft !== undefined ? 
                    ((queueItem.size - queueItem.sizeleft) / queueItem.size * 100) : 0,
                eta: queueItem.timeleft,
                downloadClient: queueItem.downloadClient
            };
        }
        
        // Full check includes Jellyfin verification
        if (fullCheck && movie.hasFile) {
            const jellyfinItems = await searchJellyfinLibrary(movie.title);
            movieInfo.jellyfinStatus = {
                found: jellyfinItems.length > 0,
                items: jellyfinItems.map(item => ({
                    id: item.Id,
                    name: item.Name,
                    year: item.ProductionYear,
                    library: item.ParentId
                }))
            };
        }
        
        results.push(movieInfo);
    }
    
    // Process matching series
    for (const series of matchingSeries) {
        const seriesInfo = {
            type: 'tv',
            title: series.title,
            year: series.year,
            sonarrId: series.id,
            tmdbId: series.tmdbId,
            monitored: series.monitored,
            status: series.status,
            seasons: series.seasons?.length || 0,
            totalEpisodes: series.statistics?.episodeCount || 0,
            availableEpisodes: series.statistics?.episodeFileCount || 0,
            path: series.path
        };
        
        // Check download queue for this series
        const queueItems = (await getSonarrQueue()).filter(q => q.seriesId === series.id);
        if (queueItems.length > 0) {
            seriesInfo.downloadStatus = queueItems.map(q => ({
                episode: q.episode ? `S${q.episode.seasonNumber?.toString().padStart(2, '0')}E${q.episode.episodeNumber?.toString().padStart(2, '0')}` : 'Unknown',
                status: getDownloadStatus(q),
                progress: q.sizeleft !== undefined ? 
                    ((q.size - q.sizeleft) / q.size * 100) : 0,
                eta: q.timeleft,
                downloadClient: q.downloadClient
            }));
        }
        
        // Full check includes Jellyfin verification
        if (fullCheck && series.statistics?.episodeFileCount > 0) {
            const jellyfinItems = await searchJellyfinLibrary(series.title);
            seriesInfo.jellyfinStatus = {
                found: jellyfinItems.length > 0,
                items: jellyfinItems.map(item => ({
                    id: item.Id,
                    name: item.Name,
                    year: item.ProductionYear,
                    library: item.ParentId
                }))
            };
        }
        
        results.push(seriesInfo);
    }
    
    return results;
}

async function checkByIds(radarrId = null, sonarrId = null) {
    const results = [];
    
    if (radarrId) {
        try {
            const response = await makeRadarrRequest(`/movie/${radarrId}`);
            if (response.statusCode === 200) {
                const movie = response.body;
                results.push({
                    type: 'movie',
                    title: movie.title,
                    year: movie.year,
                    radarrId: movie.id,
                    monitored: movie.monitored,
                    hasFile: movie.hasFile,
                    status: movie.hasFile ? 'AVAILABLE' : 'MISSING'
                });
            }
        } catch (error) {
            console.error('❌ Error fetching movie by ID:', error.message);
        }
    }
    
    if (sonarrId) {
        try {
            const response = await makeSonarrRequest(`/series/${sonarrId}`);
            if (response.statusCode === 200) {
                const series = response.body;
                results.push({
                    type: 'tv',
                    title: series.title,
                    year: series.year,
                    sonarrId: series.id,
                    monitored: series.monitored,
                    status: series.status,
                    seasons: series.seasons?.length || 0,
                    availableEpisodes: series.statistics?.episodeFileCount || 0,
                    totalEpisodes: series.statistics?.episodeCount || 0
                });
            }
        } catch (error) {
            console.error('❌ Error fetching series by ID:', error.message);
        }
    }
    
    return results;
}

// Main execution
async function main() {
    const args = process.argv.slice(2);
    
    if (args.includes('--help')) {
        console.log(`
📊 Media Request - Status Checker

Usage:
  node check-status.js                    # Check all active downloads
  node check-status.js "Title"            # Check specific movie/show
  node check-status.js --radarr-id 123    # Check by Radarr ID
  node check-status.js --sonarr-id 456    # Check by Sonarr ID
  node check-status.js --full-check       # Include Jellyfin verification
  node check-status.js "Title" --full-check

Examples:
  node check-status.js
  node check-status.js "Inception"
  node check-status.js "Breaking Bad" --full-check
        `);
        return;
    }
    
    try {
        let results;
        const fullCheck = args.includes('--full-check');
        
        if (args.includes('--radarr-id')) {
            const radarrId = args[args.indexOf('--radarr-id') + 1];
            results = await checkByIds(parseInt(radarrId), null);
        } else if (args.includes('--sonarr-id')) {
            const sonarrId = args[args.indexOf('--sonarr-id') + 1];
            results = await checkByIds(null, parseInt(sonarrId));
        } else if (args.length > 0 && !args[0].startsWith('--')) {
            const query = args[0];
            results = await checkSpecificItem(query, fullCheck);
        } else {
            results = await checkAllActiveDownloads();
        }
        
        console.log('\n' + '='.repeat(60));
        if (Array.isArray(results) && results.length > 0) {
            results.forEach((result, index) => {
                console.log(`\n📋 Result ${index + 1}:`);
                console.log(JSON.stringify(result, null, 2));
            });
        } else {
            console.log('\n📭 No results found or no active downloads.');
        }
        
        process.exit(0);
    } catch (error) {
        console.error('❌ Fatal error:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { 
    checkAllActiveDownloads, 
    checkSpecificItem, 
    checkByIds 
};