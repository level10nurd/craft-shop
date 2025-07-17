-- Sync monitoring infrastructure tables for Lightspeed to Supabase sync
-- Run these statements in Supabase SQL Editor or your preferred PostgreSQL client

-- 1. sync_state table: Tracks last sync timestamps and status for each entity type
CREATE TABLE IF NOT EXISTS sync_state (
    entity_type TEXT PRIMARY KEY,
    last_sync_time TIMESTAMPTZ,
    status TEXT DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. sync_log table: Detailed history of all sync operations  
CREATE TABLE IF NOT EXISTS sync_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    entity_type TEXT NOT NULL,
    action TEXT NOT NULL,
    status TEXT NOT NULL,
    duration_seconds NUMERIC,
    records_processed INTEGER DEFAULT 0,
    error_details TEXT,
    metadata JSONB
);

-- 3. lightspeed_inventory table: Following existing lightspeed_* patterns
CREATE TABLE IF NOT EXISTS lightspeed_inventory (
    id TEXT PRIMARY KEY,
    product_id TEXT,
    current_amount NUMERIC DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sync_log_timestamp ON sync_log (timestamp);
CREATE INDEX IF NOT EXISTS idx_sync_log_entity_type ON sync_log (entity_type);
CREATE INDEX IF NOT EXISTS idx_sync_log_status ON sync_log (status);
CREATE INDEX IF NOT EXISTS idx_lightspeed_inventory_product_id ON lightspeed_inventory (product_id);

-- Initialize sync_state with the 6 entity types
INSERT INTO sync_state (entity_type, status) VALUES 
    ('customers', 'never_synced'),
    ('outlets', 'never_synced'),
    ('products', 'never_synced'),
    ('sales', 'never_synced'),
    ('sale_line_items', 'never_synced'),
    ('inventory', 'never_synced')
ON CONFLICT (entity_type) DO NOTHING;