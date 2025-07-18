#!/usr/bin/env python3
"""
Test script to verify inventory date backfill works with existing data.
This tests the fix without needing live Lightspeed API access.
"""

import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv('.env.local')

# Fix Supabase URL if missing protocol
supabase_url = os.environ.get('SUPABASE_URL', '')
if supabase_url and not supabase_url.startswith('http'):
    supabase_url = f'https://{supabase_url}'
    os.environ['SUPABASE_URL'] = supabase_url

from supabase import create_client

def create_supabase_client():
    """Create a Supabase client using environment variables."""
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables")
    
    return create_client(supabase_url, supabase_key)

def test_inventory_table_structure():
    """Test that the new columns exist and check existing data."""
    print("🔍 Testing inventory table structure...")
    
    try:
        supabase = create_supabase_client()
        
        # Check existing inventory records
        result = supabase.table('lightspeed_inventory').select('*').limit(5).execute()
        
        if not result.data:
            print("⚠️  No existing inventory records found")
            return False
        
        print(f"✅ Found {len(result.data)} existing inventory records")
        
        # Check structure of first record
        first_record = result.data[0]
        print("\n📊 Current inventory record structure:")
        for key, value in first_record.items():
            print(f"   {key}: {value}")
        
        # Check if new columns exist
        has_lightspeed_created = 'lightspeed_created_at' in first_record
        has_lightspeed_updated = 'lightspeed_updated_at' in first_record
        
        print(f"\n🔍 Schema check:")
        print(f"   lightspeed_created_at column: {'✅ EXISTS' if has_lightspeed_created else '❌ MISSING'}")
        print(f"   lightspeed_updated_at column: {'✅ EXISTS' if has_lightspeed_updated else '❌ MISSING'}")
        
        if has_lightspeed_created and has_lightspeed_updated:
            print("✅ NEW COLUMNS EXIST! The database schema update worked.")
            
            # Check if any records already have Lightspeed dates
            records_with_lightspeed_dates = 0
            for record in result.data:
                if record.get('lightspeed_created_at') or record.get('lightspeed_updated_at'):
                    records_with_lightspeed_dates += 1
            
            print(f"\n📈 Data status:")
            print(f"   Records with Lightspeed dates: {records_with_lightspeed_dates}/{len(result.data)}")
            
            if records_with_lightspeed_dates == 0:
                print("💡 Ready for backfill - no records have Lightspeed dates yet")
            else:
                print("✅ Some records already have Lightspeed dates!")
            
            return True
        else:
            print("❌ NEW COLUMNS MISSING! Run the SQL migration first.")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run the test."""
    print("🧪 Testing Inventory Date Fix - Database Structure")
    print("=" * 60)
    
    success = test_inventory_table_structure()
    
    print("=" * 60)
    if success:
        print("🎉 DATABASE STRUCTURE TEST PASSED!")
        print("✅ Ready to proceed with inventory sync or backfill")
        print("\n💡 Next steps:")
        print("   1. Try running inventory sync when Lightspeed API is available")
        print("   2. Or run backfill script to update existing records")
    else:
        print("❌ DATABASE STRUCTURE TEST FAILED!")
        print("🔧 Please check the issues above before proceeding")
    print("=" * 60)

if __name__ == "__main__":
    main() 