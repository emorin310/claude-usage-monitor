#!/usr/bin/env python3
"""
Zehrs Cart Assistant - Hybrid Approach
Works with manual cart data + provides intelligent assistance
"""

import json
import os
from datetime import datetime

class ZehrsCartAssistant:
    def __init__(self):
        self.data_dir = "/home/magi/clawd/grocery-data"
        self.current_cart = self.load_current_cart()
        self.favorites = self.load_favorites()
        self.staples = self.load_staples()
    
    def load_current_cart(self):
        """Load the current cart data"""
        cart_file = f"{self.data_dir}/cart/live_cart_20260222_221041.json"
        try:
            with open(cart_file, 'r') as f:
                return json.load(f)
        except:
            return {"items": [], "cart_summary": {"item_count": 0, "subtotal": "$0.00"}}
    
    def load_favorites(self):
        """Load favorites list"""
        try:
            with open(f"{self.data_dir}/favorites/favorites.json", 'r') as f:
                data = json.load(f)
                return data.get('items', [])
        except:
            return []
    
    def load_staples(self):
        """Load staples list"""
        try:
            with open(f"{self.data_dir}/favorites/staples.json", 'r') as f:
                data = json.load(f)
                return data.get('items', [])
        except:
            return []
    
    def update_cart_manually(self, items_text):
        """Update cart from manual description"""
        print("🛒 MANUAL CART UPDATE")
        print("=" * 30)
        
        # Parse items text (flexible format)
        items = []
        lines = items_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 3:
                # Try to extract name and price
                import re
                price_match = re.search(r'\$[\d,]+\.\d{2}', line)
                
                if price_match:
                    price = price_match.group()
                    name = line.replace(price, '').strip()
                else:
                    price = "Price not specified"
                    name = line
                
                items.append({
                    "name": name,
                    "price": price,
                    "source": "manual_update"
                })
        
        # Calculate total if possible
        total = 0
        for item in items:
            try:
                price_val = float(item["price"].replace('$', '').replace(',', ''))
                total += price_val
            except:
                pass
        
        cart_data = {
            "timestamp": datetime.now().isoformat(),
            "method": "manual_update",
            "items": items,
            "cart_summary": {
                "item_count": len(items),
                "subtotal": f"${total:.2f}" if total > 0 else "Total not calculated"
            }
        }
        
        # Save updated cart
        cart_file = f"{self.data_dir}/cart/manual_cart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(cart_file, 'w') as f:
            json.dump(cart_data, f, indent=2)
        
        print(f"✅ Cart updated with {len(items)} items")
        print(f"💾 Saved to: {cart_file}")
        
        self.current_cart = cart_data
        return cart_data
    
    def analyze_current_cart(self):
        """Analyze the current cart"""
        print("🔍 CURRENT CART ANALYSIS")
        print("=" * 35)
        
        if not self.current_cart.get("items"):
            print("📭 No current cart data")
            return
        
        items = self.current_cart["items"]
        
        print(f"📦 Items in cart: {len(items)}")
        print(f"💰 Subtotal: {self.current_cart.get('cart_summary', {}).get('subtotal', 'Unknown')}")
        print()
        
        print("🛒 Current Items:")
        for i, item in enumerate(items, 1):
            name = item.get("name", "Unknown item")
            price = item.get("price", "No price")
            print(f"  {i}. {name} - {price}")
        
        print()
        
        # Compare with favorites and staples
        cart_items_lower = [item.get("name", "").lower() for item in items]
        
        # Check which favorites are in cart
        fav_in_cart = []
        fav_missing = []
        for fav in self.favorites:
            if any(fav.lower() in cart_item for cart_item in cart_items_lower):
                fav_in_cart.append(fav)
            else:
                fav_missing.append(fav)
        
        # Check which staples are in cart  
        staples_in_cart = []
        staples_missing = []
        for staple in self.staples:
            if any(staple.lower() in cart_item for cart_item in cart_items_lower):
                staples_in_cart.append(staple)
            else:
                staples_missing.append(staple)
        
        print("📊 SHOPPING PATTERN ANALYSIS:")
        print(f"⭐ Favorites in cart: {len(fav_in_cart)}/{len(self.favorites)}")
        if fav_in_cart:
            print(f"   ✅ Getting: {', '.join(fav_in_cart)}")
        
        print(f"🥛 Staples in cart: {len(staples_in_cart)}/{len(self.staples)}")  
        if staples_in_cart:
            print(f"   ✅ Getting: {', '.join(staples_in_cart)}")
        
        print()
        
        # Suggest missing items
        if staples_missing:
            print("💡 MISSING STAPLES (might want to add):")
            for staple in staples_missing[:5]:  # Top 5
                print(f"   • {staple}")
        
        if fav_missing:
            print("💡 MISSING FAVORITES (might want to add):")
            for fav in fav_missing[:3]:  # Top 3
                print(f"   • {fav}")
    
    def suggest_cart_changes(self):
        """Suggest changes to cart"""
        print("\n🎯 CART OPTIMIZATION SUGGESTIONS:")
        print("-" * 40)
        
        # Based on current cart analysis
        items = self.current_cart.get("items", [])
        
        if len(items) < 5:
            print("📦 Small cart - consider adding staples for efficiency:")
            missing_staples = [s for s in self.staples[:5] 
                             if not any(s.lower() in item.get("name", "").lower() 
                                      for item in items)]
            for staple in missing_staples:
                print(f"   + {staple}")
        
        # Price analysis (if we have prices)
        total_estimated = 0
        priced_items = 0
        for item in items:
            try:
                price_str = item.get("price", "")
                if "$" in price_str:
                    price = float(price_str.replace("$", "").replace(",", ""))
                    total_estimated += price
                    priced_items += 1
            except:
                pass
        
        if priced_items > 0:
            avg_price = total_estimated / priced_items
            print(f"💰 Average item price: ${avg_price:.2f}")
            
            if avg_price > 10:
                print("   💡 High average - mix in some lower-cost staples?")
            elif avg_price < 5:
                print("   ✅ Good value shopping!")
    
    def interactive_mode(self):
        """Interactive cart management"""
        print("🛒 ZEHRS CART ASSISTANT")
        print("=" * 30)
        print("Commands:")
        print("  view - Show current cart")
        print("  update - Update cart manually") 
        print("  analyze - Analyze shopping patterns")
        print("  suggest - Get suggestions")
        print("  quit - Exit")
        print()
        
        while True:
            try:
                command = input("Cart Assistant > ").strip().lower()
                
                if command == 'quit':
                    break
                elif command == 'view':
                    self.view_current_cart()
                elif command == 'update':
                    print("Enter your cart items (one per line, include prices if known):")
                    print("Example: Chicken Breast $12.99")
                    print("Press Enter twice when done:")
                    
                    items_text = ""
                    while True:
                        line = input()
                        if line == "":
                            break
                        items_text += line + "\n"
                    
                    if items_text.strip():
                        self.update_cart_manually(items_text)
                        
                elif command == 'analyze':
                    self.analyze_current_cart()
                elif command == 'suggest':
                    self.suggest_cart_changes()
                else:
                    print("Unknown command. Try: view, update, analyze, suggest, quit")
                
                print()
                
            except KeyboardInterrupt:
                break
        
        print("👋 Cart Assistant closed")
    
    def view_current_cart(self):
        """Display current cart"""
        if not self.current_cart.get("items"):
            print("📭 No cart data available")
            return
        
        items = self.current_cart["items"]
        print(f"🛒 Current Cart ({len(items)} items):")
        for i, item in enumerate(items, 1):
            name = item.get("name", "Unknown")
            price = item.get("price", "No price")
            print(f"  {i}. {name} - {price}")
        
        subtotal = self.current_cart.get("cart_summary", {}).get("subtotal", "Unknown")
        print(f"\n💰 Subtotal: {subtotal}")

def main():
    assistant = ZehrsCartAssistant()
    
    print("🎯 ZEHRS CART ASSISTANT - HYBRID APPROACH")
    print("=" * 50)
    print("This tool helps you manage your Zehrs cart even without API access!")
    print()
    
    # Show current status
    assistant.analyze_current_cart()
    assistant.suggest_cart_changes()
    
    print("\n🔧 WHAT THIS TOOL CAN DO:")
    print("✅ Track your cart contents manually")
    print("✅ Analyze vs your favorites/staples") 
    print("✅ Suggest missing items")
    print("✅ Calculate totals and averages")
    print("✅ Track shopping patterns")
    print()
    
    # Start interactive mode
    assistant.interactive_mode()

if __name__ == "__main__":
    main()