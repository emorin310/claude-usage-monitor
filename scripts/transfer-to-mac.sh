#!/bin/bash

# Transfer Grocery Automation to Mac Script
# Run this from the VM to package everything for Mac transfer

echo "📦 PREPARING GROCERY AUTOMATION FOR MAC TRANSFER"
echo "=" * 50

MAC_USER=${1:-eric}
MAC_HOST=${2:-192.168.1.100}  # Replace with actual Mac IP

# Create transfer directory
TRANSFER_DIR="/tmp/grocery-automation-transfer"
mkdir -p "$TRANSFER_DIR"/{scripts,extension,data}

echo "📂 Copying essential files..."

# Copy key scripts
cp /home/magi/clawd/scripts/auth-token-harvester.py "$TRANSFER_DIR/scripts/"
cp /home/magi/clawd/scripts/vm-auth-harvest.py "$TRANSFER_DIR/scripts/"
cp /home/magi/clawd/scripts/pcexpress-api-tester.py "$TRANSFER_DIR/scripts/"
cp /home/magi/clawd/scripts/quick-cart-check.py "$TRANSFER_DIR/scripts/"

# Copy extension
cp -r /home/magi/clawd/scripts/zehrs-extension "$TRANSFER_DIR/"

# Copy current grocery data
cp -r /home/magi/clawd/grocery-data "$TRANSFER_DIR/"

# Copy instructions
cp /home/magi/clawd/LOCAL_SETUP_INSTRUCTIONS.md "$TRANSFER_DIR/"

# Create credentials template
cat > "$TRANSFER_DIR/secrets.env" << 'EOF'
ZEHRS_EMAIL=emorin310@gmail.com
ZEHRS_PASSWORD=opusER123!
EOF

# Create Mac setup script
cat > "$TRANSFER_DIR/setup-mac.sh" << 'EOF'
#!/bin/bash

echo "🖥️ Setting up Zehrs Grocery Automation on Mac"
echo "=" * 45

# Install prerequisites
echo "📦 Installing prerequisites..."
pip3 install playwright aiohttp

# Install browsers
echo "🌐 Installing Chrome browser for Playwright..."
python3 -m playwright install chromium

# Make scripts executable
chmod +x scripts/*.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 QUICK START:"
echo "1. Run: python3 scripts/auth-token-harvester.py"
echo "2. Complete login in browser window"
echo "3. Tokens will be captured automatically"
echo ""
echo "🔌 EXTENSION INSTALL:"
echo "1. Open Chrome → chrome://extensions/"
echo "2. Enable Developer Mode"
echo "3. Click 'Load unpacked' → select 'zehrs-extension' folder"
echo "4. Use extension while browsing Zehrs normally"
EOF

chmod +x "$TRANSFER_DIR/setup-mac.sh"

# Create archive
echo "🗜️ Creating transfer archive..."
cd /tmp
tar -czf grocery-automation-$(date +%Y%m%d_%H%M%S).tar.gz grocery-automation-transfer/

echo "📁 Files ready in: /tmp/grocery-automation-*.tar.gz"
echo ""
echo "📤 TO TRANSFER TO MAC:"
echo "scp /tmp/grocery-automation-*.tar.gz $MAC_USER@$MAC_HOST:~/Downloads/"
echo ""
echo "📥 ON MAC:"
echo "cd ~/Downloads"
echo "tar -xzf grocery-automation-*.tar.gz"
echo "cd grocery-automation-transfer"
echo "./setup-mac.sh"
echo ""
echo "🎯 Then run: python3 scripts/auth-token-harvester.py"