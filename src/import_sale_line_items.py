#!/usr/bin/env python3
"""
Import sale line items specifically.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv('.env.local')

from historical_import import import_entity, create_lightspeed_client, create_supabase_client

def main():
    print("🛒 Importing Sale Line Items")
    print("=" * 35)
    
    try:
        lightspeed = create_lightspeed_client()
        supabase = create_supabase_client()
        
        # Import sale line items
        success = import_entity(lightspeed, supabase, 'sale_line_items')
        
        if success:
            print("✅ Sale line items import successful!")
        else:
            print("❌ Sale line items import failed - check logs")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()