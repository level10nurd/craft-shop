#!/usr/bin/env python3
"""
Historical data import script for Lightspeed to Supabase sync.
Imports all historical data for customers, outlets, products, sales, and inventory.
"""

import os
import sys
import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lightspeed_client import create_lightspeed_client, LightspeedAPIError
from supabase import create_client, Client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('historical_import.log'),
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

def log_sync_start(supabase: Client, entity_type: str) -> str:
    """Log sync start and return log ID."""
    try:
        result = supabase.table('sync_log').insert({
            'entity_type': entity_type,
            'action': 'historical_import',
            'status': 'started',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }).execute()
        
        log_id = result.data[0]['id']
        logger.info(f"Started historical import for {entity_type} (log_id: {log_id})")
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
        
        logger.info(f"Completed {entity_type}: {records_processed} processed, {records_created} created")
        
    except Exception as e:
        logger.error(f"Failed to log sync completion for {entity_type}: {e}")

def update_sync_state(supabase: Client, entity_type: str, status: str, error_message: str = None):
    """Update sync state table."""
    try:
        supabase.table('sync_state').upsert({
            'entity_type': entity_type,
            'last_sync_time': datetime.now(timezone.utc).isoformat(),
            'status': status,
            'error_message': error_message,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }).execute()
        
        logger.info(f"Updated sync state for {entity_type}: {status}")
        
    except Exception as e:
        logger.error(f"Failed to update sync state for {entity_type}: {e}")

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
        'lightspeed_created_at': inventory.get('created_at'),
        'lightspeed_updated_at': inventory.get('updated_at'),
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat()
    }

def batch_upsert(supabase: Client, table_name: str, records: List[Dict], batch_size: int = 100) -> int:
    """Upsert records in batches to Supabase."""
    total_created = 0
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            result = supabase.table(table_name).upsert(batch).execute()
            total_created += len(result.data)
            logger.info(f"Upserted batch {i//batch_size + 1} of {len(batch)} records to {table_name}")
            
            # Small delay to avoid overwhelming the database
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Failed to upsert batch to {table_name}: {e}")
            raise
            
    return total_created

def import_entity(lightspeed, supabase, entity_type: str) -> bool:
    """Import a specific entity type."""
    start_time = time.time()
    log_id = log_sync_start(supabase, entity_type)
    
    try:
        # Define entity mappings
        entity_config = {
            'customers': {
                'fetch_method': lightspeed.get_customers,
                'transform': transform_customer,
                'table': 'lightspeed_customers'
            },
            'outlets': {
                'fetch_method': lightspeed.get_outlets,
                'transform': transform_outlet,
                'table': 'lightspeed_outlets'
            },
            'products': {
                'fetch_method': lightspeed.get_products,
                'transform': transform_product,
                'table': 'lightspeed_products'
            },
            'sales': {
                'fetch_method': lightspeed.get_sales,
                'transform': transform_sale,
                'table': 'lightspeed_sales'
            },
            'sale_line_items': {
                'fetch_method': lambda: lightspeed._get_paginated_data('2.0/sale_line_items'),
                'transform': lambda item: {
                    'id': item.get('id'),
                    'sale_id': item.get('sale_id'),
                    'product_id': item.get('product_id'),
                    'price_total': item.get('price_total'),
                    'quantity': item.get('quantity'),
                    'status': item.get('status'),
                    'total_price': item.get('total_price')
                },
                'table': 'lightspeed_sale_line_items'
            },
            'inventory': {
                'fetch_method': lightspeed.get_inventory,
                'transform': transform_inventory,
                'table': 'lightspeed_inventory'
            }
        }
        
        if entity_type not in entity_config:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        config = entity_config[entity_type]
        
        # Fetch data from Lightspeed
        logger.info(f"Fetching {entity_type} from Lightspeed...")
        raw_data = config['fetch_method']()
        logger.info(f"Retrieved {len(raw_data)} {entity_type} records from Lightspeed")
        
        # Transform data
        logger.info(f"Transforming {entity_type} data...")
        transformed_data = [config['transform'](item) for item in raw_data]
        
        # Upsert to Supabase
        logger.info(f"Upserting {entity_type} to Supabase...")
        records_created = batch_upsert(supabase, config['table'], transformed_data)
        
        # Log completion
        duration = time.time() - start_time
        if log_id:
            log_sync_complete(supabase, log_id, entity_type, len(raw_data), records_created, duration)
        
        # Update sync state
        update_sync_state(supabase, entity_type, 'success')
        
        logger.info(f"✅ Successfully imported {entity_type}: {len(raw_data)} records in {duration:.2f}s")
        return True
        
    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)
        
        logger.error(f"❌ Failed to import {entity_type}: {error_msg}")
        
        # Log failure
        if log_id:
            log_sync_complete(supabase, log_id, entity_type, 0, 0, duration, 'failed', error_msg)
        
        # Update sync state
        update_sync_state(supabase, entity_type, 'failed', error_msg)
        
        return False

def main():
    """Main import function."""
    load_dotenv('.env.local')
    
    print("🚀 Starting Historical Data Import")
    print("=" * 50)
    
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
        
        # Import entities in order (dependencies first)
        entities = ['outlets', 'customers', 'products', 'sales', 'inventory']
        success_count = 0
        
        for entity_type in entities:
            logger.info(f"\n📦 Importing {entity_type}...")
            if import_entity(lightspeed, supabase, entity_type):
                success_count += 1
                print(f"✅ {entity_type.title()} import completed")
            else:
                print(f"❌ {entity_type.title()} import failed")
        
        # Summary
        total_count = len(entities)
        logger.info(f"\n🎉 Historical import complete: {success_count}/{total_count} succeeded")
        
        if success_count == total_count:
            print("\n🎉 All imports successful! Check your dashboard at http://127.0.0.1:5001")
        else:
            print(f"\n⚠️  {total_count - success_count} imports failed. Check logs for details.")
        
        return success_count == total_count
        
    except Exception as e:
        logger.error(f"Fatal error during import: {e}")
        print(f"\n❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)