// Zehrs Grocery Assistant - Background Script
// Captures authentication tokens and API calls

let capturedTokens = {};
let cartData = {};

// Listen for API requests to capture auth tokens
chrome.webRequest.onBeforeSendHeaders.addListener(
  function(details) {
    // Capture requests to PC Express API
    if (details.url.includes('api.pcexpress.ca')) {
      
      // Extract auth headers
      const authHeaders = {};
      details.requestHeaders.forEach(header => {
        const name = header.name.toLowerCase();
        if (name.includes('authorization') || 
            name.includes('x-auth') || 
            name.includes('bearer') ||
            name.includes('session') ||
            name.includes('token')) {
          authHeaders[header.name] = header.value;
        }
      });
      
      // Store captured tokens
      if (Object.keys(authHeaders).length > 0) {
        capturedTokens = {
          ...capturedTokens,
          ...authHeaders,
          captured_at: new Date().toISOString(),
          url: details.url,
          method: details.method
        };
        
        // Save to storage
        chrome.storage.local.set({
          'zehrs_tokens': capturedTokens
        });
        
        console.log('Captured auth tokens:', authHeaders);
      }
    }
  },
  {urls: ["https://api.pcexpress.ca/*"]},
  ["requestHeaders"]
);

// Listen for cart data responses
chrome.webRequest.onCompleted.addListener(
  function(details) {
    if (details.url.includes('/cart') && details.statusCode === 200) {
      // Cart data successfully loaded
      chrome.storage.local.set({
        'cart_access': {
          url: details.url,
          timestamp: new Date().toISOString(),
          status: 'success'
        }
      });
      
      console.log('Cart access detected:', details.url);
    }
  },
  {urls: ["https://api.pcexpress.ca/*/cart*"]}
);

// Extension icon clicked
chrome.action.onClicked.addListener((tab) => {
  // Open popup or perform action
  if (tab.url.includes('zehrs.ca')) {
    // Send message to content script
    chrome.tabs.sendMessage(tab.id, {action: "captureCart"});
  }
});

// Handle messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'saveCartData') {
    chrome.storage.local.set({
      'cart_data': {
        ...request.data,
        captured_at: new Date().toISOString()
      }
    });
    sendResponse({status: 'saved'});
  }
  
  if (request.action === 'getTokens') {
    chrome.storage.local.get(['zehrs_tokens'], (result) => {
      sendResponse({tokens: result.zehrs_tokens || {}});
    });
    return true; // Keep message channel open
  }
});