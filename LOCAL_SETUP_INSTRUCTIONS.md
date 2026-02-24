# Zehrs Authentication - Local Setup Instructions

## 🖥️ Run on Your Mac Studio (Magrathea)

### Step 1: Install Prerequisites
```bash
# Install Python and pip (if not already installed)
brew install python

# Install Playwright
pip install playwright aiohttp

# Install browser
playwright install chromium
```

### Step 2: Create Working Directory
```bash
mkdir ~/grocery-automation
cd ~/grocery-automation
```

### Step 3: Copy Scripts from VM
```bash
# Copy the authentication harvester
scp magi@your-vm:/home/magi/clawd/scripts/auth-token-harvester.py .
scp magi@your-vm:/home/magi/clawd/scripts/vm-auth-harvest.py .

# Copy the API tester  
scp magi@your-vm:/home/magi/clawd/scripts/pcexpress-api-tester.py .
```

### Step 4: Create Credentials File
```bash
# Create secrets.env
cat > secrets.env << 'EOF'
ZEHRS_EMAIL=emorin310@gmail.com
ZEHRS_PASSWORD=opusER123!
EOF
```

### Step 5: Run the Interactive Harvester
```bash
# This will open a visible browser window for you to complete login
python auth-token-harvester.py
```

**What will happen:**
1. Browser window opens to Zehrs sign-in
2. You manually log in (handle any CAPTCHAs)
3. Script captures authentication tokens automatically
4. Tokens saved to `api_tokens.json`

### Step 6: Test API Access
```bash
# Test the captured tokens
python pcexpress-api-tester.py
```

---

## 🎯 PERMANENT SOLUTION - Browser Extension

Since you'll need this frequently, here's a better approach:

### Chrome Extension Setup (Recommended)

#### Step 1: Copy Extension Files
```bash
# Copy the extension folder to your Mac
scp -r magi@your-vm:/home/magi/clawd/scripts/zehrs-extension ~/grocery-automation/
```

#### Step 2: Install Extension
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right toggle)
3. Click "Load unpacked"
4. Select the `zehrs-extension` folder
5. Extension icon should appear in toolbar

#### Step 3: Use Extension
1. **Log into Zehrs normally** in your browser
2. **Visit your cart page** (`https://www.zehrs.ca/en/cart`)
3. **Click the extension icon** in toolbar
4. **Click "Capture Cart Now"** 
5. **Export data** using the buttons

#### Step 4: Sync with VM
```bash
# Copy captured data back to VM
scp ~/Downloads/zehrs_tokens.json magi@your-vm:/home/magi/clawd/grocery-data/
scp ~/Downloads/zehrs_cart.json magi@your-vm:/home/magi/clawd/grocery-data/cart/
```

### ✅ Extension Benefits:
- **No automation needed** - works with your normal browsing
- **Automatic capture** - detects cart changes in background  
- **No CAPTCHA issues** - uses your real login session
- **Always up-to-date** - captures latest cart whenever you shop
- **One-click export** - easy data transfer to VM

---

## 🔄 AUTOMATED SYNC SOLUTION

### Option B: Automated Data Sync