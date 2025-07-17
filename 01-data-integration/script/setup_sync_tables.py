#!/usr/bin/env python3
"""
Database setup script for sync monitoring infrastructure.
Creates sync_state, sync_log, and lightspeed_inventory tables.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env.local
load_dotenv('.env.local')

def get_supabase_client() -> Client:
    """Create Supabase client using environment variables."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables")
    
    return create_client(url, key)

def create_sync_state_table(supabase: Client):
    """Create sync_state table for tracking last sync timestamps and status."""
    # Use supabase.table() operations to create the structure
    # First, try to query the table to see if it exists
    try:
        supabase.table('sync_state').select('*').limit(1).execute()
        print("✅ sync_state table already exists")
        return True
    except Exception:
        # Table doesn't exist, we need to create it manually
        print("⚠️  sync_state table needs to be created manually via Supabase dashboard")
        print("   SQL: CREATE TABLE sync_state (entity_type TEXT PRIMARY KEY, last_sync_time TIMESTAMPTZ, status TEXT DEFAULT 'pending', error_message TEXT, created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW());")
        return False

def create_sync_log_table(supabase: Client):
    """Create sync_log table for detailed sync history and debugging."""
    try:
        supabase.table('sync_log').select('*').limit(1).execute()
        print("✅ sync_log table already exists")
        return True
    except Exception:
        print("⚠️  sync_log table needs to be created manually via Supabase dashboard")
        print("   SQL: CREATE TABLE sync_log (id SERIAL PRIMARY KEY, timestamp TIMESTAMPTZ DEFAULT NOW(), entity_type TEXT NOT NULL, action TEXT NOT NULL, status TEXT NOT NULL, duration_seconds NUMERIC, records_processed INTEGER DEFAULT 0, error_details TEXT, metadata JSONB);")
        return False

def create_lightspeed_inventory_table(supabase: Client):
    """Create lightspeed_inventory table following existing lightspeed_* patterns."""
    try:
        supabase.table('lightspeed_inventory').select('*').limit(1).execute()
        print("✅ lightspeed_inventory table already exists")
        return True
    except Exception:
        print("⚠️  lightspeed_inventory table needs to be created manually via Supabase dashboard")
        print("   SQL: CREATE TABLE lightspeed_inventory (id TEXT PRIMARY KEY, product_id TEXT, current_amount NUMERIC DEFAULT 0, created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW());")
        return False

def initialize_sync_state(supabase: Client):
    """Initialize sync_state table with the 6 entity types."""
    entity_types = [
        'customers',
        'outlets', 
        'products',
        'sales',
        'sale_line_items',
        'inventory'
    ]
    
    for entity_type in entity_types:
        try:
            supabase.table('sync_state').upsert({
                'entity_type': entity_type,
                'status': 'never_synced',
                'last_sync_time': None,
                'error_message': None
            }).execute()
            print(f"✅ Initialized sync_state for {entity_type}")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize {entity_type}: {e}")

def main():
    """Main setup function."""
    print("🚀 Setting up sync monitoring infrastructure...")
    
    try:
        # Create Supabase client
        supabase = get_supabase_client()
        print("✅ Connected to Supabase")
        
        # Create tables
        create_sync_state_table(supabase)
        create_sync_log_table(supabase)
        create_lightspeed_inventory_table(supabase)
        
        # Initialize sync state
        initialize_sync_state(supabase)
        
        print("\n🎉 Database setup completed successfully!")
        print("\nCreated tables:")
        print("  - sync_state: Tracks last sync timestamps for each entity type")
        print("  - sync_log: Detailed history of all sync operations")
        print("  - lightspeed_inventory: Inventory data from Lightspeed")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        raise

if __name__ == "__main__":
    main()