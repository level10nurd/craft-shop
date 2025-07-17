#!/usr/bin/env python3
"""
Complete the sale line items import by checking what's missing.
"""

import os
import sys
import logging
from datetime import datetime, timezone
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv('.env.local')

from lightspeed_client import create_lightspeed_client
from supabase import create_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def get_existing_line_item_ids(supabase):
    """Get all existing line item IDs from database."""
    logger.info("Fetching existing line item IDs...")
    
    all_ids = set()
    page_size = 1000
    start = 0
    
    while True:
        result = supabase.table('lightspeed_sale_line_items').select('id').range(start, start + page_size - 1).execute()
        
        if not result.data:
            break
            
        batch_ids = {item['id'] for item in result.data}
        all_ids.update(batch_ids)
        
        logger.info(f"Loaded {len(batch_ids)} IDs (total: {len(all_ids)})")
        
        if len(result.data) < page_size:
            break
            
        start += page_size
    
    logger.info(f"Found {len(all_ids)} existing line item IDs")
    return all_ids

def extract_missing_line_items(lightspeed, existing_ids):
    """Extract line items that aren't in the database yet."""
    logger.info("Fetching sales and extracting missing line items...")
    
    # Get first few pages to test
    sales_data = lightspeed._get_paginated_data('2.0/sales')
    logger.info(f"Retrieved {len(sales_data)} sales records")
    
    missing_line_items = []
    total_found = 0
    
    for sale in sales_data:
        sale_id = sale.get('id')
        line_items = sale.get('line_items', [])
        
        for line_item in line_items:
            total_found += 1
            line_item_id = line_item.get('id')
            
            if line_item_id not in existing_ids:
                transformed_item = {
                    'id': line_item_id,
                    'sale_id': sale_id,
                    'product_id': line_item.get('product_id'),
                    'price_total': line_item.get('price_total'),
                    'quantity': line_item.get('quantity'),
                    'status': line_item.get('status'),
                    'total_price': line_item.get('total_price')
                }
                missing_line_items.append(transformed_item)
    
    logger.info(f"Found {len(missing_line_items)} missing line items out of {total_found} total")
    return missing_line_items

def batch_upsert(supabase, records, batch_size=100):
    """Upsert missing records."""
    if not records:
        logger.info("No records to upsert")
        return 0
        
    total_created = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            result = supabase.table('lightspeed_sale_line_items').upsert(batch).execute()
            total_created += len(result.data)
            logger.info(f"Upserted batch {i//batch_size + 1} of {len(batch)} records")
        except Exception as e:
            logger.error(f"Failed to upsert batch: {e}")
            raise
            
    return total_created

def update_sync_status(supabase, records_processed, records_created):
    """Update sync status."""
    try:
        # Update sync_state
        supabase.table('sync_state').upsert({
            'entity_type': 'sale_line_items',
            'last_sync_time': datetime.now(timezone.utc).isoformat(),
            'status': 'success',
            'error_message': None,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }).execute()
        
        logger.info("Updated sync state to success")
        
    except Exception as e:
        logger.error(f"Failed to update sync status: {e}")

def main():
    print("🔄 Completing Sale Line Items Import")
    print("=" * 40)
    
    try:
        lightspeed = create_lightspeed_client()
        supabase = create_supabase_client()
        
        # Get existing line item IDs
        existing_ids = get_existing_line_item_ids(supabase)
        
        # Extract missing line items
        missing_items = extract_missing_line_items(lightspeed, existing_ids)
        
        if missing_items:
            # Upsert missing items
            records_created = batch_upsert(supabase, missing_items)
            print(f"✅ Added {records_created} missing line items")
        else:
            print("✅ All line items are already imported!")
            records_created = 0
        
        # Update sync status
        update_sync_status(supabase, len(existing_ids) + len(missing_items), records_created)
        
        # Final count
        final_result = supabase.table('lightspeed_sale_line_items').select('*', count='exact').execute()
        print(f"📊 Total sale line items now: {final_result.count}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    main()