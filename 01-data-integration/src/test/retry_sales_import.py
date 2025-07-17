#!/usr/bin/env python3
"""
Retry sales import only - fix for foreign key constraint issue.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv('.env.local')

from historical_import import import_entity, create_lightspeed_client, create_supabase_client

def main():
    print("🔄 Retrying Sales Import")
    print("=" * 30)
    
    try:
        lightspeed = create_lightspeed_client()
        supabase = create_supabase_client()
        
        # Import only sales with fixed transform
        success = import_entity(lightspeed, supabase, 'sales')
        
        if success:
            print("✅ Sales import successful!")
        else:
            print("❌ Sales import failed - check logs")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()