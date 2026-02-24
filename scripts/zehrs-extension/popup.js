// Zehrs Assistant Popup Script

document.addEventListener('DOMContentLoaded', function() {
  const captureBtn = document.getElementById('captureCart');
  const exportTokensBtn = document.getElementById('exportTokens');
  const exportCartBtn = document.getElementById('exportCart');
  const statusDiv = document.getElementById('status');
  const authStatusDiv = document.getElementById('authStatus');
  const cartStatusDiv = document.getElementById('cartStatus');
  
  // Update status display
  function updateStatus(message, type = 'info') {
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
  }
  
  // Load stored data on popup open
  chrome.storage.local.get(['zehrs_tokens', 'cart_data'], (result) => {
    // Update auth status
    if (result.zehrs_tokens && Object.keys(result.zehrs_tokens).length > 0) {
      authStatusDiv.innerHTML = `✅ Tokens captured<br><small>Last: ${new Date(result.zehrs_tokens.captured_at).toLocaleString()}</small>`;
    } else {
      authStatusDiv.textContent = '❌ No tokens captured';
    }
    
    // Update cart status  
    if (result.cart_data) {
      const itemCount = result.cart_data.cart?.items?.length || 0;
      cartStatusDiv.innerHTML = `✅ ${itemCount} items captured<br><small>Last: ${new Date(result.cart_data.captured_at).toLocaleString()}</small>`;
    } else {
      cartStatusDiv.textContent = '❌ No cart data';
    }
  });
  
  // Capture cart button
  captureBtn.addEventListener('click', function() {
    updateStatus('Capturing cart data...', 'info');
    captureBtn.disabled = true;
    
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      const tab = tabs[0];
      
      if (!tab.url.includes('zehrs.ca')) {
        updateStatus('Please navigate to Zehrs.ca first', 'error');
        captureBtn.disabled = false;
        return;
      }
      
      chrome.tabs.sendMessage(tab.id, {action: 'captureCart'}, function(response) {
        if (chrome.runtime.lastError) {
          updateStatus('Error: Please refresh the Zehrs page', 'error');
        } else if (response) {
          updateStatus(`Captured ${response.items} cart items!`, 'success');
          
          // Refresh display
          setTimeout(() => {
            location.reload();
          }, 1000);
        }
        captureBtn.disabled = false;
      });
    });
  });
  
  // Export tokens button
  exportTokensBtn.addEventListener('click', function() {
    chrome.storage.local.get(['zehrs_tokens'], (result) => {
      if (result.zehrs_tokens) {
        const data = JSON.stringify(result.zehrs_tokens, null, 2);
        downloadFile('zehrs_tokens.json', data);
        updateStatus('Tokens exported!', 'success');
      } else {
        updateStatus('No tokens to export', 'error');
      }
    });
  });
  
  // Export cart button
  exportCartBtn.addEventListener('click', function() {
    chrome.storage.local.get(['cart_data'], (result) => {
      if (result.cart_data) {
        const data = JSON.stringify(result.cart_data, null, 2);
        downloadFile('zehrs_cart.json', data);
        updateStatus('Cart data exported!', 'success');
      } else {
        updateStatus('No cart data to export', 'error');
      }
    });
  });
  
  // Function to download data as file
  function downloadFile(filename, data) {
    const blob = new Blob([data], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    
    chrome.downloads.download({
      url: url,
      filename: filename,
      saveAs: true
    });
  }
  
  // Check if we're on Zehrs.ca
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    const tab = tabs[0];
    
    if (!tab.url.includes('zehrs.ca')) {
      captureBtn.disabled = true;
      updateStatus('Navigate to Zehrs.ca to capture data', 'info');
    }
  });
});