#!/usr/bin/env python3
"""
Extract sale line items from sales data that includes nested line_items.
"""

import os
import sys
import time
import logging
from datetime import datetime, timezone
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv('.env.local')

from lightspeed_client import create_lightspeed_client, LightspeedAPIError
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_supabase_client() -> Client:
    """Create Supabase client."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def fetch_sales_with_line_items(lightspeed):
    """Fetch sales data that includes line_items."""
    logger.info("Fetching sales with line_items included...")
    
    # Fetch sales with line_items included in the response
    sales_data = lightspeed._get_paginated_data('2.0/sales')
    logger.info(f"Retrieved {len(sales_data)} sales records")
    
    return sales_data

def extract_line_items_from_sales(sales_data):
    """Extract line items from sales data."""
    logger.info("Extracting line items from sales...")
    
    all_line_items = []
    
    for sale in sales_data:
        sale_id = sale.get('id')
        line_items = sale.get('line_items', [])
        
        for line_item in line_items:
            transformed_item = {
                'id': line_item.get('id'),
                'sale_id': sale_id,
                'product_id': line_item.get('product_id'),
                'price_total': line_item.get('price_total'),
                'quantity': line_item.get('quantity'),
                'status': line_item.get('status'),
                'total_price': line_item.get('total_price')
            }
            all_line_items.append(transformed_item)
    
    logger.info(f"Extracted {len(all_line_items)} line items")
    return all_line_items

def batch_upsert(supabase: Client, table_name: str, records, batch_size: int = 100):
    """Upsert records in batches."""
    total_created = 0
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            result = supabase.table(table_name).upsert(batch).execute()
            total_created += len(result.data)
            logger.info(f"Upserted batch {i//batch_size + 1} of {len(batch)} records to {table_name}")
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            logger.error(f"Failed to upsert batch to {table_name}: {e}")
            raise
            
    return total_created

def log_sync_activity(supabase: Client, entity_type: str, records_processed: int, records_created: int):
    """Log the sync activity."""
    try:
        # Log to sync_log
        supabase.table('sync_log').insert({
            'entity_type': entity_type,
            'action': 'extract_from_sales',
            'status': 'completed',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'records_processed': records_processed,
            'duration_seconds': 0
        }).execute()
        
        # Update sync_state
        supabase.table('sync_state').upsert({
            'entity_type': entity_type,
            'last_sync_time': datetime.now(timezone.utc).isoformat(),
            'status': 'success',
            'error_message': None,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }).execute()
        
        logger.info(f"Logged sync activity for {entity_type}")
        
    except Exception as e:
        logger.error(f"Failed to log sync activity: {e}")

def main():
    print("🛒 Extracting Sale Line Items from Sales Data")
    print("=" * 50)
    
    try:
        # Initialize clients
        lightspeed = create_lightspeed_client()
        supabase = create_supabase_client()
        
        # Fetch sales with nested line items
        sales_data = fetch_sales_with_line_items(lightspeed)
        
        # Extract line items
        line_items = extract_line_items_from_sales(sales_data)
        
        if not line_items:
            print("❌ No line items found in sales data")
            return False
        
        # Upsert line items to database
        logger.info("Upserting line items to Supabase...")
        records_created = batch_upsert(supabase, 'lightspeed_sale_line_items', line_items)
        
        # Log the sync activity
        log_sync_activity(supabase, 'sale_line_items', len(line_items), records_created)
        
        print(f"✅ Successfully extracted and imported {len(line_items)} sale line items!")
        print(f"📊 Created {records_created} records in lightspeed_sale_line_items table")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to extract sale line items: {e}")
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)