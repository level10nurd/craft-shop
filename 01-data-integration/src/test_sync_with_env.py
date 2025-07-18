#!/usr/bin/env python3
"""
Script to test the inventory date fix by running incremental sync with proper environment setup.
"""

import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv('.env.local')

# Now import and run the sync
from incremental_sync import main as run_incremental_sync

if __name__ == "__main__":
    print("🔄 Testing Inventory Date Fix with Real Sync")
    print("=" * 50)
    
    # Verify environment is loaded
    if not os.environ.get('SUPABASE_URL'):
        print("❌ Environment variables not loaded properly")
        exit(1)
    
    print("✅ Environment variables loaded")
    print("🚀 Running incremental sync to test inventory date fix...")
    print()
    
    try:
        run_incremental_sync()
        print()
        print("=" * 50)
        print("✅ Sync completed! Check Supabase for new inventory records with both:")
        print("   - lightspeed_created_at / lightspeed_updated_at (from Lightspeed)")
        print("   - created_at / updated_at (from sync time)")
        print("=" * 50)
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        exit(1) 