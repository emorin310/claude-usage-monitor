#!/usr/bin/env node

const https = require('https');
const http = require('http');

// Configuration
const RADARR_URL = 'http://192.168.1.89:7878';
const RADARR_API_KEY = '9357c52a8209410cbfabb2cdad6480bf';
const SONARR_URL = 'http://192.168.1.89:8989';
const SONARR_API_KEY = '09998432e0ec46e590ac9ff9235b4229';
const JELLYFIN_URL = 'http://192.168.1.89:8096';

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

async function testRadarr() {
    try {
        const url = `${RADARR_URL}/api/v3/system/status`;
        const options = { headers: { 'X-Api-Key': RADARR_API_KEY } };
        const response = await makeRequest(url, options);
        
        if (response.statusCode === 200) {
            console.log('✅ Radarr Connection: SUCCESS');
            console.log(`   Version: ${response.body.version}`);
            console.log(`   App Name: ${response.body.appName}`);
            
            // Get movie count
            const moviesResponse = await makeRequest(`${RADARR_URL}/api/v3/movie`, options);
            if (moviesResponse.statusCode === 200) {
                console.log(`   Movies in Library: ${moviesResponse.body.length}`);
            }
            
            // Get quality profiles
            const profilesResponse = await makeRequest(`${RADARR_URL}/api/v3/qualityprofile`, options);
            if (profilesResponse.statusCode === 200) {
                console.log(`   Quality Profiles: ${profilesResponse.body.map(p => p.name).join(', ')}`);
            }
            
            return true;
        } else {
            console.log('❌ Radarr Connection: FAILED');
            console.log(`   Status Code: ${response.statusCode}`);
            return false;
        }
    } catch (error) {
        console.log('❌ Radarr Connection: ERROR');
        console.log(`   Error: ${error.message}`);
        return false;
    }
}

async function testSonarr() {
    try {
        const url = `${SONARR_URL}/api/v3/system/status`;
        const options = { headers: { 'X-Api-Key': SONARR_API_KEY } };
        const response = await makeRequest(url, options);
        
        if (response.statusCode === 200) {
            console.log('✅ Sonarr Connection: SUCCESS');
            console.log(`   Version: ${response.body.version}`);
            console.log(`   App Name: ${response.body.appName}`);
            
            // Get series count
            const seriesResponse = await makeRequest(`${SONARR_URL}/api/v3/series`, options);
            if (seriesResponse.statusCode === 200) {
                console.log(`   Series in Library: ${seriesResponse.body.length}`);
            }
            
            // Get quality profiles
            const profilesResponse = await makeRequest(`${SONARR_URL}/api/v3/qualityprofile`, options);
            if (profilesResponse.statusCode === 200) {
                console.log(`   Quality Profiles: ${profilesResponse.body.map(p => p.name).join(', ')}`);
            }
            
            return true;
        } else {
            console.log('❌ Sonarr Connection: FAILED');
            console.log(`   Status Code: ${response.statusCode}`);
            return false;
        }
    } catch (error) {
        console.log('❌ Sonarr Connection: ERROR');
        console.log(`   Error: ${error.message}`);
        return false;
    }
}

async function testJellyfin() {
    try {
        const url = `${JELLYFIN_URL}/System/Info/Public`;
        const response = await makeRequest(url);
        
        if (response.statusCode === 200) {
            console.log('✅ Jellyfin Connection: SUCCESS');
            console.log(`   Version: ${response.body.Version}`);
            console.log(`   Server Name: ${response.body.ServerName}`);
            return true;
        } else {
            console.log('❌ Jellyfin Connection: FAILED');
            console.log(`   Status Code: ${response.statusCode}`);
            return false;
        }
    } catch (error) {
        console.log('❌ Jellyfin Connection: ERROR');
        console.log(`   Error: ${error.message}`);
        return false;
    }
}

async function testTMDB() {
    const TMDB_API_KEY = process.env.TMDB_API_KEY;
    
    if (!TMDB_API_KEY) {
        console.log('⚠️  TMDB API Key: NOT SET');
        console.log('   Set TMDB_API_KEY environment variable to test TMDB connection');
        return false;
    }
    
    try {
        const url = `https://api.themoviedb.org/3/configuration?api_key=${TMDB_API_KEY}`;
        const response = await makeRequest(url);
        
        if (response.statusCode === 200) {
            console.log('✅ TMDB Connection: SUCCESS');
            console.log(`   Base URL: ${response.body.images.base_url}`);
            return true;
        } else {
            console.log('❌ TMDB Connection: FAILED');
            console.log(`   Status Code: ${response.statusCode}`);
            return false;
        }
    } catch (error) {
        console.log('❌ TMDB Connection: ERROR');
        console.log(`   Error: ${error.message}`);
        return false;
    }
}

async function main() {
    console.log('🧪 Media Request Skill - Connection Tests');
    console.log('='.repeat(50));
    console.log();
    
    const [radarrOk, sonarrOk, jellyfinOk, tmdbOk] = await Promise.all([
        testRadarr(),
        testSonarr(),
        testJellyfin(),
        testTMDB()
    ]);
    
    console.log();
    console.log('📊 Summary:');
    console.log(`   Radarr: ${radarrOk ? '✅' : '❌'}`);
    console.log(`   Sonarr: ${sonarrOk ? '✅' : '❌'}`);
    console.log(`   Jellyfin: ${jellyfinOk ? '✅' : '❌'}`);
    console.log(`   TMDB: ${tmdbOk ? '✅' : '⚠️'}`);
    
    const allOk = radarrOk && sonarrOk && jellyfinOk && tmdbOk;
    console.log();
    console.log(`🎯 Overall Status: ${allOk ? 'READY' : 'NEEDS CONFIGURATION'}`);
    
    if (!tmdbOk) {
        console.log();
        console.log('💡 Next Steps:');
        console.log('   1. Get a free TMDB API key from https://www.themoviedb.org/settings/api');
        console.log('   2. Set the environment variable: export TMDB_API_KEY="your_key_here"');
        console.log('   3. Re-run this test to verify full functionality');
    }
}

if (require.main === module) {
    main();
}