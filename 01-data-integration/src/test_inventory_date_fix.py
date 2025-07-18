#!/usr/bin/env python3
"""
Test script to verify the inventory date fix is working correctly.

This script:
1. Fetches a small sample of inventory data from Lightspeed
2. Transforms it using the updated function
3. Inserts a test record into Supabase
4. Verifies that both Lightspeed and Supabase dates are captured correctly
"""

import os
import sys
import logging
from datetime import datetime, timezone
from typing import Dict, List

# Add the src directory to the path
sys.path.append(os.path.dirname(__file__))

from supabase import create_client, Client
from lightspeed_client import create_lightspeed_client
from incremental_sync import transform_inventory

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_supabase_client() -> Client:
    """Create a Supabase client using environment variables."""
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables")
    
    return create_client(supabase_url, supabase_key)

def test_inventory_sync():
    """Test the inventory sync with the new date fields."""
    logger.info("🧪 Starting inventory date fix test...")
    
    try:
        # Create clients
        supabase = create_supabase_client()
        lightspeed = create_lightspeed_client()
        
        # Test connections
        logger.info("Testing API connections...")
        if not lightspeed.test_connection():
            raise Exception("Failed to connect to Lightspeed API")
        logger.info("✅ Lightspeed API connection successful")
        
        # Fetch a small sample of inventory data
        logger.info("Fetching sample inventory data from Lightspeed...")
        inventory_data = lightspeed.get_inventory()
        
        if not inventory_data:
            logger.warning("No inventory data found in Lightspeed")
            return False
        
        logger.info(f"Retrieved {len(inventory_data)} inventory records from Lightspeed")
        
        # Test with first 3 records to keep it small
        test_records = inventory_data[:3]
        
        logger.info("🔍 Analyzing sample records...")
        for i, record in enumerate(test_records):
            logger.info(f"Record {i+1}:")
            logger.info(f"  ID: {record.get('id')}")
            logger.info(f"  Product ID: {record.get('product_id')}")
            logger.info(f"  Current Amount: {record.get('current_inventory', 0)}")
            logger.info(f"  Lightspeed Created: {record.get('created_at')}")
            logger.info(f"  Lightspeed Updated: {record.get('updated_at')}")
            
            # Transform the record
            transformed = transform_inventory(record)
            logger.info(f"  Transformed record has {len(transformed)} fields:")
            for key, value in transformed.items():
                logger.info(f"    {key}: {value}")
            logger.info("")
        
        # Test inserting one record
        logger.info("🚀 Testing database insert...")
        test_record = test_records[0]
        transformed_record = transform_inventory(test_record)
        
        # Add a test suffix to the ID to avoid conflicts
        test_id = f"{transformed_record['id']}_test_{int(datetime.now().timestamp())}"
        transformed_record['id'] = test_id
        
        logger.info(f"Inserting test record with ID: {test_id}")
        
        # Insert the test record
        result = supabase.table('lightspeed_inventory').upsert(transformed_record).execute()
        
        if result.data:
            logger.info("✅ Test record inserted successfully!")
            
            # Verify the record was inserted with correct dates
            verify_result = supabase.table('lightspeed_inventory').select('*').eq('id', test_id).execute()
            
            if verify_result.data:
                inserted_record = verify_result.data[0]
                logger.info("🔍 Verifying inserted record:")
                logger.info(f"  ID: {inserted_record.get('id')}")
                logger.info(f"  Product ID: {inserted_record.get('product_id')}")
                logger.info(f"  Current Amount: {inserted_record.get('current_amount')}")
                logger.info(f"  Lightspeed Created: {inserted_record.get('lightspeed_created_at')}")
                logger.info(f"  Lightspeed Updated: {inserted_record.get('lightspeed_updated_at')}")
                logger.info(f"  Supabase Created: {inserted_record.get('created_at')}")
                logger.info(f"  Supabase Updated: {inserted_record.get('updated_at')}")
                
                # Check if we have both sets of dates
                has_lightspeed_dates = bool(inserted_record.get('lightspeed_created_at') or inserted_record.get('lightspeed_updated_at'))
                has_supabase_dates = bool(inserted_record.get('created_at') and inserted_record.get('updated_at'))
                
                if has_lightspeed_dates and has_supabase_dates:
                    logger.info("✅ SUCCESS: Both Lightspeed and Supabase dates captured correctly!")
                    
                    # Clean up test record
                    supabase.table('lightspeed_inventory').delete().eq('id', test_id).execute()
                    logger.info("🧹 Test record cleaned up")
                    
                    return True
                else:
                    logger.error("❌ FAILURE: Missing date fields")
                    logger.error(f"  Has Lightspeed dates: {has_lightspeed_dates}")
                    logger.error(f"  Has Supabase dates: {has_supabase_dates}")
                    return False
            else:
                logger.error("❌ Failed to verify inserted record")
                return False
        else:
            logger.error("❌ Failed to insert test record")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def main():
    """Run the test."""
    logger.info("=" * 60)
    logger.info("INVENTORY DATE FIX TEST")
    logger.info("=" * 60)
    
    success = test_inventory_sync()
    
    logger.info("=" * 60)
    if success:
        logger.info("🎉 TEST PASSED! The inventory date fix is working correctly.")
        logger.info("✅ You can now proceed with backfilling existing data.")
        logger.info("💡 Next step: Run the migration script to backfill existing records")
    else:
        logger.info("❌ TEST FAILED! Please check the errors above and fix before proceeding.")
    logger.info("=" * 60)

if __name__ == "__main__":
    main() 