#!/usr/bin/env python3
"""
Simple test script to verify the inventory date fix is working correctly.
This version avoids Unicode characters that cause encoding issues in PowerShell.
"""

import os
import sys
import logging
from datetime import datetime, timezone

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

def test_schema_changes():
    """Test that the new columns exist in the database."""
    logger.info("Testing database schema changes...")
    
    try:
        supabase = create_supabase_client()
        
        # Try to select the new columns
        result = supabase.table('lightspeed_inventory').select('id, lightspeed_created_at, lightspeed_updated_at').limit(1).execute()
        
        logger.info("SUCCESS: New columns exist in database")
        return True
        
    except Exception as e:
        logger.error(f"FAILED: Schema test failed - {e}")
        return False

def test_transform_function():
    """Test that the transform function includes new fields."""
    logger.info("Testing transform function...")
    
    # Create a sample Lightspeed inventory record
    sample_record = {
        'id': 'test_123',
        'product_id': 'prod_456',
        'current_inventory': 10,
        'created_at': '2024-01-15T10:30:00Z',
        'updated_at': '2024-01-16T14:20:00Z'
    }
    
    # Transform it
    transformed = transform_inventory(sample_record)
    
    logger.info("Transformed record fields:")
    for key, value in transformed.items():
        logger.info(f"  {key}: {value}")
    
    # Check if it has the required fields
    required_fields = ['id', 'product_id', 'current_amount', 'lightspeed_created_at', 'lightspeed_updated_at', 'created_at', 'updated_at']
    missing_fields = [field for field in required_fields if field not in transformed]
    
    if missing_fields:
        logger.error(f"FAILED: Missing fields: {missing_fields}")
        return False
    
    # Check if Lightspeed dates are preserved
    if transformed['lightspeed_created_at'] != sample_record['created_at']:
        logger.error("FAILED: Lightspeed created_at not preserved")
        return False
        
    if transformed['lightspeed_updated_at'] != sample_record['updated_at']:
        logger.error("FAILED: Lightspeed updated_at not preserved")
        return False
    
    logger.info("SUCCESS: Transform function working correctly")
    return True

def test_lightspeed_api():
    """Test that we can fetch inventory data from Lightspeed."""
    logger.info("Testing Lightspeed API connection...")
    
    try:
        lightspeed = create_lightspeed_client()
        
        if not lightspeed.test_connection():
            logger.error("FAILED: Cannot connect to Lightspeed API")
            return False
        
        logger.info("Fetching sample inventory data...")
        inventory_data = lightspeed.get_inventory()
        
        if not inventory_data:
            logger.warning("WARNING: No inventory data found")
            return False
        
        logger.info(f"Found {len(inventory_data)} inventory records")
        
        # Check first record structure
        first_record = inventory_data[0]
        logger.info("Sample record from Lightspeed:")
        logger.info(f"  ID: {first_record.get('id')}")
        logger.info(f"  Product ID: {first_record.get('product_id')}")
        logger.info(f"  Current Inventory: {first_record.get('current_inventory')}")
        logger.info(f"  Created At: {first_record.get('created_at')}")
        logger.info(f"  Updated At: {first_record.get('updated_at')}")
        
        logger.info("SUCCESS: Lightspeed API working correctly")
        return True
        
    except Exception as e:
        logger.error(f"FAILED: Lightspeed API test failed - {e}")
        return False

def main():
    """Run all tests."""
    logger.info("="*50)
    logger.info("INVENTORY DATE FIX TEST")
    logger.info("="*50)
    
    tests = [
        ("Database Schema", test_schema_changes),
        ("Transform Function", test_transform_function),
        ("Lightspeed API", test_lightspeed_api)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning {test_name} test...")
        if test_func():
            passed += 1
            logger.info(f"PASS: {test_name}")
        else:
            logger.info(f"FAIL: {test_name}")
    
    logger.info("="*50)
    logger.info(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("ALL TESTS PASSED! Ready to proceed with backfill.")
    else:
        logger.info("SOME TESTS FAILED! Please fix issues before proceeding.")
    
    logger.info("="*50)
    
    return passed == total

if __name__ == "__main__":
    main() 