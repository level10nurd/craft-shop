#!/usr/bin/env python3
"""
Incremental data sync script for Lightspeed to Supabase.
Syncs only modified records since last successful sync timestamp.
Designed to run daily via cron job.
"""

import os
import sys
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Add src to Python path
sys.path.insert(0, os.path.dirname(__file__))

from lightspeed_client import create_lightspeed_client, LightspeedAPIError
from supabase import create_client, Client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('incremental_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_supabase_client() -> Client:
    """Create Supabase client."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
        
    return create_client(url, key)

def get_last_sync_version(supabase: Client, entity_type: str) -> Optional[int]:
    """Get last successful sync version for entity type."""
    try:
        result = supabase.table('sync_state').select('last_version, status').eq('entity_type', entity_type).execute()
        
        if result.data and result.data[0]['status'] == 'success':
            last_version = result.data[0]['last_version']
            if last_version:
                logger.info(f"Found last version for {entity_type}: {last_version}")
                return int(last_version)
        
        logger.info(f"No previous version found for {entity_type}, will fetch all records")
        return None
            
    except Exception as e:
        logger.error(f"Failed to get last sync version for {entity_type}: {e}")
        return None

def log_sync_start(supabase: Client, entity_type: str) -> str:
    """Log sync start and return log ID."""
    try:
        result = supabase.table('sync_log').insert({
            'entity_type': entity_type,
            'action': 'incremental_sync',
            'status': 'started',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }).execute()
        
        log_id = result.data[0]['id']
        logger.info(f"Started incremental sync for {entity_type} (log_id: {log_id})")
        return str(log_id)
        
    except Exception as e:
        logger.error(f"Failed to log sync start for {entity_type}: {e}")
        return None

def log_sync_complete(supabase: Client, log_id: str, entity_type: str, 
                     records_processed: int, records_created: int, duration: float, 
                     status: str = 'completed', error_details: str = None):
    """Log sync completion."""
    try:
        supabase.table('sync_log').update({
            'status': status,
            'duration_seconds': duration,
            'records_processed': records_processed,
            'error_details': error_details
        }).eq('id', log_id).execute()
        
        logger.info(f"Completed {entity_type}: {records_processed} processed, {records_created} upserted")
        
    except Exception as e:
        logger.error(f"Failed to log sync completion for {entity_type}: {e}")

def update_sync_state(supabase: Client, entity_type: str, status: str, highest_version: Optional[int] = None, error_message: str = None):
    """Update sync state table with version tracking."""
    try:
        sync_data = {
            'entity_type': entity_type,
            'last_sync_time': datetime.now(timezone.utc).isoformat(),
            'status': status,
            'error_message': error_message,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        if highest_version is not None:
            sync_data['last_version'] = highest_version
            logger.info(f"Updating {entity_type} to version {highest_version}")
        
        supabase.table('sync_state').upsert(sync_data).execute()
        logger.info(f"Updated sync state for {entity_type}: {status}")
        
    except Exception as e:
        logger.error(f"Failed to update sync state for {entity_type}: {e}")

def get_highest_version(records: List[Dict]) -> Optional[int]:
    """Get the highest version number from a list of records."""
    if not records:
        return None
    
    versions = [record.get('version') for record in records if record.get('version')]
    if versions:
        return max(int(v) for v in versions)
    return None

def transform_customer(customer: Dict) -> Dict:
    """Transform Lightspeed customer to Supabase format."""
    return {
        'id': customer.get('id'),
        'first_name': customer.get('first_name'),
        'last_name': customer.get('last_name'),
        'email': customer.get('email'),
        'phone': customer.get('phone'),
        'created_at': customer.get('created_at'),
        'updated_at': customer.get('updated_at')
    }

def transform_outlet(outlet: Dict) -> Dict:
    """Transform Lightspeed outlet to Supabase format."""
    return {
        'id': outlet.get('id'),
        'name': outlet.get('name'),
        'address': f"{outlet.get('physical_address_1', '')} {outlet.get('physical_address_2', '')}".strip(),
        'phone': outlet.get('phone'),
        'email': outlet.get('email')
    }

def transform_product(product: Dict) -> Dict:
    """Transform Lightspeed product to Supabase format."""
    return {
        'id': product.get('id'),
        'name': product.get('name'),
        'sku': product.get('sku'),
        'price': product.get('price_excluding_tax'),
        'cost': product.get('supply_price'),
        'category_id': None,  # Will need to map from categories
        'brand_id': product.get('brand_id'),
        'created_at': product.get('created_at'),
        'updated_at': product.get('updated_at')
    }

def transform_sale(sale: Dict) -> Dict:
    """Transform Lightspeed sale to Supabase format."""
    # Handle missing customer_id gracefully
    customer_id = sale.get('customer_id')
    if customer_id == '':  # Empty string to None
        customer_id = None
        
    return {
        'id': sale.get('id'),
        'outlet_id': sale.get('outlet_id'),
        'register_id': sale.get('register_id'),
        'user_id': sale.get('user_id'),
        'customer_id': customer_id,  # Allow NULL for missing customers
        'invoice_number': sale.get('invoice_number'),
        'status': sale.get('status'),
        'total_price': sale.get('total_price'),
        'sale_date': sale.get('created_at'),
        'created_at': sale.get('created_at'),
        'updated_at': sale.get('updated_at')
    }

def transform_inventory(inventory: Dict) -> Dict:
    """Transform Lightspeed inventory to Supabase format."""
    return {
        'id': inventory.get('id'),
        'product_id': inventory.get('product_id'),
        'current_amount': inventory.get('current_inventory', 0),
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat()
    }

def extract_line_items_from_sales(lightspeed, after_version: Optional[int]) -> List[Dict]:
    """Extract line items from sales data after given version."""
    logger.info(f"Fetching sales after version {after_version} to extract line items...")
    
    # Fetch sales after last version
    sales_data = lightspeed.get_sales(after_version=after_version)
    logger.info(f"Retrieved {len(sales_data)} sales records")
    
    line_items = []
    
    for sale in sales_data:
        sale_id = sale.get('id')
        sale_line_items = sale.get('line_items', [])
        
        for line_item in sale_line_items:
            transformed_item = {
                'id': line_item.get('id'),
                'sale_id': sale_id,
                'product_id': line_item.get('product_id'),
                'price_total': line_item.get('price_total'),
                'quantity': line_item.get('quantity'),
                'status': line_item.get('status'),
                'total_price': line_item.get('total_price')
            }
            line_items.append(transformed_item)
    
    logger.info(f"Extracted {len(line_items)} line items from {len(sales_data)} sales")
    return line_items

def batch_upsert(supabase: Client, table_name: str, records: List[Dict], batch_size: int = 100) -> int:
    """Upsert records in batches to Supabase."""
    if not records:
        return 0
        
    total_upserted = 0
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            result = supabase.table(table_name).upsert(batch).execute()
            total_upserted += len(result.data)
            logger.info(f"Upserted batch {i//batch_size + 1} of {len(batch)} records to {table_name}")
            
            # Small delay to avoid overwhelming the database
            time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Failed to upsert batch to {table_name}: {e}")
            raise
            
    return total_upserted

def sync_entity_incremental(lightspeed, supabase, entity_type: str) -> bool:
    """Sync a specific entity type incrementally."""
    start_time = time.time()
    log_id = log_sync_start(supabase, entity_type)
    
    try:
        # Get last sync version
        last_version = get_last_sync_version(supabase, entity_type)
        logger.info(f"Last version for {entity_type}: {last_version}")
        
        # Define entity mappings
        entity_config = {
            'customers': {
                'fetch_method': lambda: lightspeed.get_customers(after_version=last_version),
                'transform': transform_customer,
                'table': 'lightspeed_customers'
            },
            'outlets': {
                'fetch_method': lightspeed.get_outlets,  # Outlets rarely change
                'transform': transform_outlet,
                'table': 'lightspeed_outlets'
            },
            'products': {
                'fetch_method': lambda: lightspeed.get_products(after_version=last_version),
                'transform': transform_product,
                'table': 'lightspeed_products'
            },
            'sales': {
                'fetch_method': lambda: lightspeed.get_sales(after_version=last_version),
                'transform': transform_sale,
                'table': 'lightspeed_sales'
            },
            'sale_line_items': {
                'fetch_method': lambda: extract_line_items_from_sales(lightspeed, last_version),
                'transform': lambda item: item,  # Already transformed in fetch_method
                'table': 'lightspeed_sale_line_items'
            },
            'inventory': {
                'fetch_method': lightspeed.get_inventory,  # Inventory is always full sync
                'transform': transform_inventory,
                'table': 'lightspeed_inventory'
            }
        }
        
        if entity_type not in entity_config:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        config = entity_config[entity_type]
        
        # Fetch data from Lightspeed
        logger.info(f"Fetching {entity_type} from Lightspeed (since version: {last_version})...")
        raw_data = config['fetch_method']()
        
        # Skip if no new data
        if not raw_data:
            logger.info(f"No new {entity_type} records found since last sync")
            duration = time.time() - start_time
            if log_id:
                log_sync_complete(supabase, log_id, entity_type, 0, 0, duration)
            update_sync_state(supabase, entity_type, 'success')
            return True
        
        logger.info(f"Retrieved {len(raw_data)} {entity_type} records from Lightspeed")
        
        # Transform data
        logger.info(f"Transforming {entity_type} data...")
        transformed_data = [config['transform'](item) for item in raw_data]
        
        # Upsert to Supabase
        logger.info(f"Upserting {entity_type} to Supabase...")
        records_upserted = batch_upsert(supabase, config['table'], transformed_data)
        
        # Get highest version from fetched data
        highest_version = get_highest_version(raw_data)
        
        # Log completion
        duration = time.time() - start_time
        if log_id:
            log_sync_complete(supabase, log_id, entity_type, len(raw_data), records_upserted, duration)
        
        # Update sync state with new version
        update_sync_state(supabase, entity_type, 'success', highest_version)
        
        logger.info(f"✅ Successfully synced {entity_type}: {len(raw_data)} records in {duration:.2f}s (version: {highest_version})")
        return True
        
    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)
        
        logger.error(f"❌ Failed to sync {entity_type}: {error_msg}")
        
        # Log failure
        if log_id:
            log_sync_complete(supabase, log_id, entity_type, 0, 0, duration, 'failed', error_msg)
        
        # Update sync state
        update_sync_state(supabase, entity_type, 'failed', error_msg)
        
        return False

def main():
    """Main incremental sync function."""
    load_dotenv('.env.local')
    
    print("🔄 Starting Incremental Data Sync")
    print("=" * 40)
    
    try:
        # Initialize clients
        logger.info("Initializing API clients...")
        lightspeed = create_lightspeed_client()
        supabase = create_supabase_client()
        
        # Test connections
        logger.info("Testing API connections...")
        if not lightspeed.test_connection():
            raise Exception("Failed to connect to Lightspeed API")
        
        logger.info("✅ API connections successful")
        
        # Sync entities (order matters for dependencies)
        entities = ['outlets', 'customers', 'products', 'sales', 'sale_line_items', 'inventory']
        success_count = 0
        
        for entity_type in entities:
            logger.info(f"\n🔄 Syncing {entity_type}...")
            if sync_entity_incremental(lightspeed, supabase, entity_type):
                success_count += 1
                print(f"✅ {entity_type.title()} sync completed")
            else:
                print(f"❌ {entity_type.title()} sync failed")
        
        # Summary
        total_count = len(entities)
        logger.info(f"\n🎉 Incremental sync complete: {success_count}/{total_count} succeeded")
        
        if success_count == total_count:
            print("\n🎉 All syncs successful! Check your dashboard at http://127.0.0.1:5001")
        else:
            print(f"\n⚠️  {total_count - success_count} syncs failed. Check logs for details.")
        
        return success_count == total_count
        
    except Exception as e:
        logger.error(f"Fatal error during sync: {e}")
        print(f"\n❌ Sync failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)