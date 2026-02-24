#!/bin/bash

# Grocery Setup Script
# Initialize the complete grocery automation system

echo "🛒 Setting up Grocery Automation System..."
echo "=========================================="

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p /home/magi/clawd/grocery-data/{purchases,favorites,promotions,cart}

# Initialize favorites with common staples
echo "⭐ Setting up default favorites..."
cat > /home/magi/clawd/grocery-data/favorites/staples.json << EOF
{
  "items": [
    "milk",
    "bread", 
    "eggs",
    "cheese",
    "chicken",
    "bananas",
    "yogurt",
    "butter",
    "onions",
    "potatoes"
  ],
  "auto_check_frequency": "weekly",
  "last_updated": "$(date -Iseconds)"
}
EOF

# Initialize favorites
cat > /home/magi/clawd/grocery-data/favorites/favorites.json << EOF
{
  "items": [
    "avocados",
    "salmon",
    "olive oil",
    "tomatoes",
    "spinach",
    "strawberries"
  ],
  "last_updated": "$(date -Iseconds)"
}
EOF

# Create quick access scripts
echo "🔧 Creating quick access commands..."

# Quick price check script
cat > /home/magi/clawd/check-prices << 'EOF'
#!/bin/bash
cd /home/magi/clawd
source playwright-env/bin/activate
python scripts/zehrs-master.py smart-shop
EOF

# Quick search script  
cat > /home/magi/clawd/search-item << 'EOF'
#!/bin/bash
if [ $# -eq 0 ]; then
    echo "Usage: ./search-item <product name>"
    exit 1
fi

cd /home/magi/clawd
source playwright-env/bin/activate
python scripts/zehrs-master.py search "$*"
EOF

# Add to favorites script
cat > /home/magi/clawd/add-favorite << 'EOF'
#!/bin/bash
if [ $# -eq 0 ]; then
    echo "Usage: ./add-favorite <item1> [item2] ..."
    exit 1
fi

cd /home/magi/clawd
source playwright-env/bin/activate  
python scripts/zehrs-master.py favorites add "$@"
EOF

# Make scripts executable
chmod +x /home/magi/clawd/{check-prices,search-item,add-favorite}

echo ""
echo "✅ Setup Complete!"
echo ""
echo "🎯 GROCERY SYSTEM READY!"
echo "========================"
echo ""
echo "📂 Data Structure:"
echo "  /home/magi/clawd/grocery-data/"
echo "  ├── favorites/     (your preferred items)"
echo "  ├── promotions/    (current deals & sales)"
echo "  ├── purchases/     (shopping history)"
echo "  └── cart/         (current cart items)"
echo ""
echo "⚡ Quick Commands:"
echo "  ./check-prices     - Check all staples & favorites"
echo "  ./search-item milk - Search for specific item"
echo "  ./add-favorite X   - Add item to favorites"
echo ""
echo "🛠️ Full Commands:"
echo "  python scripts/zehrs-master.py smart-shop"
echo "  python scripts/zehrs-master.py promotions" 
echo "  python scripts/zehrs-master.py favorites list"
echo "  python scripts/zehrs-master.py staples add coffee"
echo ""
echo "📊 Default Staples Added:"
echo "  milk, bread, eggs, cheese, chicken, bananas, yogurt, butter, onions, potatoes"
echo ""
echo "⭐ Default Favorites Added:"
echo "  avocados, salmon, olive oil, tomatoes, spinach, strawberries"
echo ""
echo "🚀 Test the system:"
echo "  cd /home/magi/clawd && python scripts/grocery-demo.py"
echo ""
EOF