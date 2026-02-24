// Zehrs Grocery Assistant - Content Script
// Captures cart data and page information

// Function to extract cart data from the page
function extractCartData() {
  const cartData = {
    items: [],
    total: '',
    subtotal: '',
    timestamp: new Date().toISOString(),
    url: window.location.href
  };
  
  // Try multiple selectors for cart items
  const itemSelectors = [
    '[data-testid="cart-item"]',
    '.cart-item',
    '.line-item',
    '[class*="CartItem"]'
  ];
  
  let items = [];
  for (const selector of itemSelectors) {
    items = document.querySelectorAll(selector);
    if (items.length > 0) break;
  }
  
  items.forEach((item, index) => {
    const itemData = {
      index: index + 1,
      name: '',
      price: '',
      quantity: '',
      total: ''
    };
    
    // Extract item name
    const nameSelectors = ['h3', '.item-name', '.product-name', '[data-testid="product-title"]'];
    for (const sel of nameSelectors) {
      const nameEl = item.querySelector(sel);
      if (nameEl) {
        itemData.name = nameEl.textContent.trim();
        break;
      }
    }
    
    // Extract price
    const priceMatch = item.textContent.match(/\$\d+\.\d{2}/g);
    if (priceMatch) {
      itemData.price = priceMatch[0];
      if (priceMatch.length > 1) {
        itemData.total = priceMatch[priceMatch.length - 1];
      }
    }
    
    // Extract quantity
    const qtyMatch = item.textContent.match(/qty:?\s*(\d+)/i) || 
                    item.textContent.match(/quantity:?\s*(\d+)/i);
    if (qtyMatch) {
      itemData.quantity = qtyMatch[1];
    }
    
    if (itemData.name || itemData.price) {
      cartData.items.push(itemData);
    }
  });
  
  // Extract totals
  const totalSelectors = ['.total', '.cart-total', '[data-testid="total"]'];
  for (const selector of totalSelectors) {
    const totalEl = document.querySelector(selector);
    if (totalEl) {
      const totalMatch = totalEl.textContent.match(/\$\d+\.\d{2}/);
      if (totalMatch) {
        cartData.total = totalMatch[0];
      }
    }
  }
  
  // If no structured cart found, look for any price information
  if (cartData.items.length === 0) {
    const bodyText = document.body.textContent;
    const prices = bodyText.match(/\$\d+\.\d{2}/g);
    
    if (prices && prices.length > 0) {
      cartData.items.push({
        name: 'Cart detected but structure unclear',
        price: prices[0],
        note: `Found ${prices.length} prices on page`
      });
    }
  }
  
  return cartData;
}

// Function to extract user account info
function extractAccountInfo() {
  const accountInfo = {
    loggedIn: false,
    email: '',
    name: '',
    timestamp: new Date().toISOString()
  };
  
  // Check for login indicators
  const loginIndicators = [
    'Sign Out',
    'Logout', 
    'My Account',
    'Profile'
  ];
  
  for (const indicator of loginIndicators) {
    if (document.body.textContent.includes(indicator)) {
      accountInfo.loggedIn = true;
      break;
    }
  }
  
  // Try to extract email/name if visible
  const emailMatch = document.body.textContent.match(/[\w\.-]+@[\w\.-]+\.\w+/);
  if (emailMatch) {
    accountInfo.email = emailMatch[0];
  }
  
  return accountInfo;
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'captureCart') {
    const cartData = extractCartData();
    const accountInfo = extractAccountInfo();
    
    // Send data to background script
    chrome.runtime.sendMessage({
      action: 'saveCartData',
      data: {
        cart: cartData,
        account: accountInfo,
        page_url: window.location.href,
        page_title: document.title
      }
    });
    
    // Also log to console
    console.log('Captured cart data:', cartData);
    console.log('Account info:', accountInfo);
    
    sendResponse({status: 'captured', items: cartData.items.length});
  }
});

// Auto-capture when on cart page
if (window.location.href.includes('/cart')) {
  // Wait for page to load
  setTimeout(() => {
    const cartData = extractCartData();
    if (cartData.items.length > 0) {
      chrome.runtime.sendMessage({
        action: 'saveCartData',
        data: {
          cart: cartData,
          account: extractAccountInfo(),
          auto_captured: true
        }
      });
    }
  }, 3000);
}

// Monitor for cart updates
let lastCartItemCount = 0;
setInterval(() => {
  if (window.location.href.includes('zehrs.ca')) {
    const cartData = extractCartData();
    if (cartData.items.length !== lastCartItemCount) {
      lastCartItemCount = cartData.items.length;
      
      // Cart changed - capture update
      chrome.runtime.sendMessage({
        action: 'saveCartData', 
        data: {
          cart: cartData,
          change_detected: true,
          timestamp: new Date().toISOString()
        }
      });
    }
  }
}, 10000); // Check every 10 seconds