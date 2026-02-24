// Complete Browser Storage Capture
// Run this in Chrome console while logged into Zehrs

console.log('🔍 COMPLETE BROWSER STORAGE CAPTURE');
console.log('=' * 40);

const storageData = {
    timestamp: new Date().toISOString(),
    url: window.location.href,
    
    // Cookies
    cookies: document.cookie,
    
    // Local Storage
    localStorage: {},
    
    // Session Storage  
    sessionStorage: {},
    
    // IndexedDB (if accessible)
    indexedDB: [],
    
    // Window properties that might contain auth
    windowAuth: {}
};

// Capture localStorage
try {
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        const value = localStorage.getItem(key);
        storageData.localStorage[key] = value;
    }
    console.log(`✅ LocalStorage: ${Object.keys(storageData.localStorage).length} items`);
} catch (e) {
    console.log('❌ LocalStorage access denied');
}

// Capture sessionStorage
try {
    for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        const value = sessionStorage.getItem(key);
        storageData.sessionStorage[key] = value;
    }
    console.log(`✅ SessionStorage: ${Object.keys(storageData.sessionStorage).length} items`);
} catch (e) {
    console.log('❌ SessionStorage access denied');
}

// Look for auth-related window properties
const authProperties = ['auth', 'token', 'user', 'session', 'login', 'customer', 'jwt', 'bearer'];
for (const prop in window) {
    if (authProperties.some(term => prop.toLowerCase().includes(term))) {
        try {
            storageData.windowAuth[prop] = window[prop];
        } catch (e) {
            storageData.windowAuth[prop] = '[Access Denied]';
        }
    }
}

// Look for common JWT/auth patterns
const authPatterns = [
    /eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+/g, // JWT
    /Bearer\s+[A-Za-z0-9_-]+/g, // Bearer tokens
    /[A-Za-z0-9]{20,}/g // Long tokens
];

const allText = JSON.stringify(storageData);
let foundTokens = [];

authPatterns.forEach((pattern, i) => {
    const matches = allText.match(pattern);
    if (matches) {
        foundTokens.push(...matches.slice(0, 5)); // First 5 matches only
    }
});

if (foundTokens.length > 0) {
    storageData.detectedTokens = foundTokens;
    console.log(`🎯 Found ${foundTokens.length} potential tokens`);
}

// Try to access Chrome extension data
try {
    chrome.storage.local.get(null, (result) => {
        storageData.extensionStorage = result;
        console.log(`🔌 Extension storage: ${Object.keys(result).length} items`);
    });
} catch (e) {
    console.log('❌ Extension storage not accessible');
}

// Final output
console.log('\n=== COMPLETE BROWSER DATA ===');
console.log(JSON.stringify(storageData, null, 2));

// Create download
try {
    const blob = new Blob([JSON.stringify(storageData, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'zehrs-browser-storage.json';
    a.click();
    console.log('📥 Download started: zehrs-browser-storage.json');
} catch (e) {
    console.log('❌ Download failed - copy the JSON above');
}

// Make data available globally
window.zehrsStorageData = storageData;
console.log('✅ Data saved to window.zehrsStorageData');