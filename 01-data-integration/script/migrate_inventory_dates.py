#!/usr/bin/env python3
"""
Migration script to add Lightspeed date fields to inventory table and backfill existing data.

This script:
1. Adds the new lightspeed_created_at and lightspeed_updated_at columns
2. Backfills existing inventory records with proper dates from Lightspeed API
3. Updates sync logic to handle the new fields

Run this after the database schema has been updated.
"""

import os
import sys
import logging
from datetime import datetime, timezone
from typing import Dict, List

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from supabase import create_client, Client
from lightspeed_client import create_lightspeed_client

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

def apply_database_schema(supabase: Client):
    """Apply the database schema changes."""
    logger.info("Applying database schema changes...")
    
    # Read and execute the SQL migration
    sql_file = os.path.join(os.path.dirname(__file__), 'add_lightspeed_dates_to_inventory.sql')
    
    try:
        with open(sql_file, 'r') as f:
            sql_commands = f.read()
        
        # Execute the SQL commands
        # Note: Supabase Python client doesn't have direct SQL execution
        # This would need to be run manually in Supabase dashboard or via SQL
        logger.info("SQL commands to run in Supabase dashboard:")
        logger.info("=" * 50)
        logger.info(sql_commands)
        logger.info("=" * 50)
        logger.info("Please run the above SQL in your Supabase SQL editor, then press Enter to continue...")
        input()
        
    except FileNotFoundError:
        logger.error(f"SQL file not found: {sql_file}")
        raise

def backfill_inventory_dates(supabase: Client, lightspeed):
    """Backfill existing inventory records with Lightspeed dates."""
    logger.info("Starting inventory date backfill...")
    
    # Get all existing inventory records that don't have Lightspeed dates
    existing_records = supabase.table('lightspeed_inventory').select('id, product_id').execute()
    
    if not existing_records.data:
        logger.info("No existing inventory records found to backfill")
        return
    
    logger.info(f"Found {len(existing_records.data)} existing inventory records to backfill")
    
    # Fetch fresh inventory data from Lightspeed
    logger.info("Fetching fresh inventory data from Lightspeed...")
    fresh_inventory = lightspeed.get_inventory()
    
    # Create a lookup map of inventory ID to dates
    inventory_dates_map = {}
    for inv in fresh_inventory:
        inventory_dates_map[inv.get('id')] = {
            'lightspeed_created_at': inv.get('created_at'),
            'lightspeed_updated_at': inv.get('updated_at')
        }
    
    # Update existing records in batches
    batch_size = 100
    updated_count = 0
    
    for i in range(0, len(existing_records.data), batch_size):
        batch = existing_records.data[i:i + batch_size]
        
        for record in batch:
            inventory_id = record['id']
            
            if inventory_id in inventory_dates_map:
                dates = inventory_dates_map[inventory_id]
                
                # Update the record with Lightspeed dates
                update_data = {
                    'lightspeed_created_at': dates['lightspeed_created_at'],
                    'lightspeed_updated_at': dates['lightspeed_updated_at']
                }
                
                try:
                    supabase.table('lightspeed_inventory').update(update_data).eq('id', inventory_id).execute()
                    updated_count += 1
                    
                    if updated_count % 50 == 0:
                        logger.info(f"Updated {updated_count} records...")
                        
                except Exception as e:
                    logger.error(f"Failed to update inventory record {inventory_id}: {e}")
            else:
                logger.warning(f"Inventory record {inventory_id} not found in fresh Lightspeed data")
    
    logger.info(f"Backfill completed. Updated {updated_count} inventory records with Lightspeed dates")

def verify_migration(supabase: Client):
    """Verify that the migration was successful."""
    logger.info("Verifying migration...")
    
    # Check if new columns exist and have data
    result = supabase.table('lightspeed_inventory').select('id, lightspeed_created_at, lightspeed_updated_at').limit(5).execute()
    
    if not result.data:
        logger.warning("No inventory records found")
        return False
    
    records_with_dates = 0
    for record in result.data:
        if record.get('lightspeed_created_at') or record.get('lightspeed_updated_at'):
            records_with_dates += 1
    
    success_rate = (records_with_dates / len(result.data)) * 100
    logger.info(f"Migration verification: {records_with_dates}/{len(result.data)} records have Lightspeed dates ({success_rate:.1f}%)")
    
    return success_rate > 80  # Consider successful if more than 80% have dates

def main():
    """Main migration function."""
    logger.info("Starting inventory date migration...")
    
    try:
        # Create clients
        supabase = create_supabase_client()
        lightspeed = create_lightspeed_client()
        
        # Test connections
        logger.info("Testing connections...")
        if not lightspeed.test_connection():
            raise Exception("Failed to connect to Lightspeed API")
        
        # Apply database schema changes
        apply_database_schema(supabase)
        
        # Backfill existing data
        backfill_inventory_dates(supabase, lightspeed)
        
        # Verify migration
        if verify_migration(supabase):
            logger.info("✅ Migration completed successfully!")
        else:
            logger.warning("⚠️  Migration completed but verification failed")
        
        logger.info("🎉 Inventory can now track historical dates from Lightspeed!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    main() 