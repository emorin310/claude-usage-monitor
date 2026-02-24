#!/usr/bin/env python3
"""
Email Receipt Parser - Alternative Data Source
Parse Zehrs purchase history from email receipts
"""

import re
import json
from datetime import datetime
import email
from email.mime.text import MIMEText

class EmailReceiptParser:
    def __init__(self):
        self.data_dir = "/home/magi/clawd/grocery-data"
        
    def parse_zehrs_receipt(self, email_text):
        """Parse a Zehrs receipt from email text"""
        
        # Common Zehrs receipt patterns
        patterns = {
            'order_number': r'Order #(\d+)',
            'date': r'Order Date: ([^\n]+)',
            'total': r'Total: \$(\d+\.\d{2})',
            'items': r'(\d+)\s+(.+?)\s+\$(\d+\.\d{2})',
            'store': r'Zehrs Markets\s+([^\n]+)',
            'subtotal': r'Subtotal: \$(\d+\.\d{2})',
            'tax': r'Tax: \$(\d+\.\d{2})',
            'delivery_fee': r'Delivery Fee: \$(\d+\.\d{2})'
        }
        
        receipt_data = {
            'source': 'email_receipt',
            'parsed_at': datetime.now().isoformat(),
            'items': [],
            'totals': {}
        }
        
        for field, pattern in patterns.items():
            matches = re.findall(pattern, email_text, re.IGNORECASE)
            
            if field == 'items':
                # Parse individual items
                for qty, name, price in matches:
                    receipt_data['items'].append({
                        'quantity': int(qty),
                        'name': name.strip(),
                        'price': float(price),
                        'total': float(price) * int(qty)
                    })
            else:
                receipt_data[field] = matches[0] if matches else None
        
        return receipt_data
    
    def create_sample_data(self):
        """Create sample receipt data for testing"""
        sample_receipts = [
            {
                'order_number': '12345678',
                'date': '2026-02-15',
                'store': 'Zehrs Markets - Cambridge',
                'items': [
                    {'quantity': 1, 'name': '2% Milk 4L', 'price': 6.49, 'total': 6.49},
                    {'quantity': 2, 'name': 'Whole Wheat Bread', 'price': 3.99, 'total': 7.98},
                    {'quantity': 12, 'name': 'Large Eggs', 'price': 4.99, 'total': 4.99},
                    {'quantity': 1, 'name': 'Chicken Breast 1kg', 'price': 12.99, 'total': 12.99},
                    {'quantity': 3, 'name': 'Bananas 1kg', 'price': 1.99, 'total': 5.97}
                ],
                'subtotal': 38.42,
                'tax': 0.65,
                'delivery_fee': 3.99,
                'total': 43.06,
                'source': 'sample_data'
            },
            {
                'order_number': '12345679', 
                'date': '2026-02-10',
                'store': 'Zehrs Markets - Cambridge',
                'items': [
                    {'quantity': 1, 'name': 'Ground Beef 454g', 'price': 8.99, 'total': 8.99},
                    {'quantity': 2, 'name': 'Pasta Sauce', 'price': 2.49, 'total': 4.98},
                    {'quantity': 1, 'name': 'Spaghetti 900g', 'price': 1.99, 'total': 1.99},
                    {'quantity': 1, 'name': 'Cheddar Cheese 400g', 'price': 6.99, 'total': 6.99},
                    {'quantity': 6, 'name': 'Yogurt Cups', 'price': 0.99, 'total': 5.94}
                ],
                'subtotal': 28.89,
                'tax': 0.46,
                'delivery_fee': 3.99,
                'total': 33.34,
                'source': 'sample_data'
            }
        ]
        
        # Save sample data
        for i, receipt in enumerate(sample_receipts):
            filename = f"{self.data_dir}/purchases/receipt_sample_{i+1}.json"
            with open(filename, 'w') as f:
                json.dump(receipt, f, indent=2)
            print(f"💾 Sample receipt saved: {filename}")
        
        return sample_receipts
    
    def analyze_purchase_history(self):
        """Analyze purchase patterns from receipt data"""
        import os
        import glob
        
        receipt_files = glob.glob(f"{self.data_dir}/purchases/receipt_*.json")
        
        if not receipt_files:
            print("❌ No receipt files found. Creating samples...")
            self.create_sample_data()
            receipt_files = glob.glob(f"{self.data_dir}/purchases/receipt_*.json")
        
        all_receipts = []
        for file_path in receipt_files:
            try:
                with open(file_path, 'r') as f:
                    receipt = json.load(f)
                    all_receipts.append(receipt)
            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
        
        if not all_receipts:
            print("❌ No valid receipts to analyze")
            return
        
        # Analysis
        total_orders = len(all_receipts)
        total_spent = sum(float(r.get('total', 0)) for r in all_receipts)
        
        # Item frequency analysis
        item_frequency = {}
        item_spending = {}
        
        for receipt in all_receipts:
            for item in receipt.get('items', []):
                name = item['name'].lower()
                item_frequency[name] = item_frequency.get(name, 0) + item['quantity']
                item_spending[name] = item_spending.get(name, 0) + item['total']
        
        # Top items by frequency and spending
        top_by_frequency = sorted(item_frequency.items(), key=lambda x: x[1], reverse=True)
        top_by_spending = sorted(item_spending.items(), key=lambda x: x[1], reverse=True)
        
        print("📊 PURCHASE HISTORY ANALYSIS")
        print("=" * 45)
        print(f"📦 Total Orders: {total_orders}")
        print(f"💰 Total Spent: ${total_spent:.2f}")
        print(f"📈 Average Order: ${total_spent/total_orders:.2f}")
        
        print("\\n🔥 Most Frequently Bought:")
        for item, freq in top_by_frequency[:5]:
            print(f"  {freq}x - {item.title()}")
        
        print("\\n💸 Highest Spending Categories:")  
        for item, spent in top_by_spending[:5]:
            print(f"  ${spent:.2f} - {item.title()}")
        
        # Generate shopping recommendations
        staples = [item for item, freq in top_by_frequency if freq >= 2]
        
        analysis_report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_orders': total_orders,
                'total_spent': total_spent,
                'average_order': total_spent/total_orders if total_orders > 0 else 0
            },
            'top_items_by_frequency': top_by_frequency[:10],
            'top_items_by_spending': top_by_spending[:10], 
            'recommended_staples': staples,
            'receipts_analyzed': len(all_receipts)
        }
        
        report_file = f"{self.data_dir}/purchase_analysis_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(analysis_report, f, indent=2)
        
        print(f"\\n📋 Recommended Staples ({len(staples)} items):")
        for staple in staples[:10]:
            print(f"  • {staple.title()}")
        
        print(f"\\n💾 Full analysis saved: {report_file}")
        
        return analysis_report

def main():
    parser = EmailReceiptParser()
    
    print("📧 EMAIL RECEIPT PARSER")
    print("=" * 30)
    print("Alternative approach to grocery automation")
    print("Works with email receipts instead of live API")
    print()
    
    # For now, create and analyze sample data
    print("📊 Analyzing purchase history...")
    analysis = parser.analyze_purchase_history()
    
    print("\\n🎯 NEXT STEPS:")
    print("1. Export actual Zehrs receipt emails")
    print("2. Parse them with this tool")  
    print("3. Build automated shopping lists")
    print("4. Track spending patterns over time")
    print("\\n💡 This approach works without API access!")

if __name__ == "__main__":
    main()