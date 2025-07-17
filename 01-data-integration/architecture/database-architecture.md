# Craft Contemporary Database Architecture - IMPLEMENTED SCHEMA

## Overview
This document outlines the **actual implemented** database architecture for syncing data from Lightspeed Retail POS to Supabase. This reflects the working production system.

## Architecture Diagram
```
┌─────────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Lightspeed API    │────▶│  Python Sync     │────▶│   Supabase DB  │
│  (Source of Truth) │     │    Service       │     │  (PostgreSQL)   │
└─────────────────────┘     └──────────────────┘     └─────────────────┘
                                   │
                                   ▼
                            ┌──────────────┐
                            │ sync_state + │
                            │   sync_log   │
                            └──────────────┘
                                   │
                                   ▼
                            ┌──────────────┐
                            │ Flask Status │
                            │  Dashboard   │
                            └──────────────┘
```

## Database Schema - ACTUAL IMPLEMENTATION

### Core Lightspeed Data Tables

#### 1. lightspeed_products
```sql
CREATE TABLE lightspeed_products (
    id TEXT PRIMARY KEY,                          -- Lightspeed product_id
    -- Additional fields populated by sync process
    -- (Schema simplified from Lightspeed API response)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 2. lightspeed_inventory
```sql
CREATE TABLE lightspeed_inventory (
    id TEXT PRIMARY KEY,
    product_id TEXT,
    current_amount NUMERIC DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 3. lightspeed_customers
```sql
CREATE TABLE lightspeed_customers (
    id TEXT PRIMARY KEY,                          -- Lightspeed customer_id
    -- Additional fields populated by sync process
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 4. lightspeed_sales
```sql
CREATE TABLE lightspeed_sales (
    id TEXT PRIMARY KEY,                          -- Lightspeed sale_id
    -- Additional fields populated by sync process
    -- Note: Some foreign key constraints removed for sync reliability
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 5. lightspeed_sale_line_items
```sql
CREATE TABLE lightspeed_sale_line_items (
    id TEXT PRIMARY KEY,                          -- Lightspeed line_item_id
    sale_id TEXT,                                 -- References lightspeed_sales(id)
    -- Additional fields populated by sync process
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 6. lightspeed_outlets
```sql
CREATE TABLE lightspeed_outlets (
    id TEXT PRIMARY KEY,                          -- Lightspeed outlet_id
    -- Additional fields populated by sync process
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Implementation Note
All `lightspeed_*` tables contain additional fields that are populated dynamically from the Lightspeed API responses. The exact schema varies based on the API data structure for each entity type.

### Sync Management Tables - CORE INFRASTRUCTURE

#### 7. sync_log - Operational History
```sql
CREATE TABLE sync_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    entity_type TEXT NOT NULL,                   -- 'customers', 'outlets', 'products', 'sales', 'sale_line_items', 'inventory'
    action TEXT NOT NULL,                        -- 'incremental_sync', 'historical_import'
    status TEXT NOT NULL,                        -- 'started', 'completed', 'failed'
    duration_seconds NUMERIC,
    records_processed INTEGER DEFAULT 0,
    error_details TEXT,
    metadata JSONB
);

-- Performance indexes
CREATE INDEX idx_sync_log_timestamp ON sync_log (timestamp);
CREATE INDEX idx_sync_log_entity_type ON sync_log (entity_type);
CREATE INDEX idx_sync_log_status ON sync_log (status);
```

#### 8. sync_state - Current Status Tracking
```sql
CREATE TABLE sync_state (
    entity_type TEXT PRIMARY KEY,
    last_sync_time TIMESTAMPTZ,
    status TEXT DEFAULT 'pending',               -- 'success', 'failed', 'pending', 'never_synced'
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_version BIGINT                          -- For Lightspeed version-based sync
);

-- Initialize with the 6 entity types
INSERT INTO sync_state (entity_type, status) VALUES 
    ('customers', 'never_synced'),
    ('outlets', 'never_synced'),
    ('products', 'never_synced'),
    ('sales', 'never_synced'),
    ('sale_line_items', 'never_synced'),
    ('inventory', 'never_synced')
ON CONFLICT (entity_type) DO NOTHING;
```

### Supporting Tables

#### 11. Outlets
```sql
CREATE TABLE outlets (
    id UUID PRIMARY KEY,                          -- Lightspeed outlet_id
    name VARCHAR(255) NOT NULL,
    physical_address TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE
);
```

#### 12. Registers
```sql
CREATE TABLE registers (
    id UUID PRIMARY KEY,                          -- Lightspeed register_id
    outlet_id UUID REFERENCES outlets(id),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE
);
```

#### 13. Users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,                          -- Lightspeed user_id
    username VARCHAR(255),
    email VARCHAR(255),
    display_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE
);
```

#### 14. Taxes
```sql
CREATE TABLE taxes (
    id UUID PRIMARY KEY,                          -- Lightspeed tax_id
    name VARCHAR(255) NOT NULL,
    rate DECIMAL(5, 4),
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE
);
```

## Data Sync Strategy

### 1. Historical Import
- Process all entities in dependency order:
  1. Reference data: outlets, taxes, users, brands, suppliers
  2. Product-related: product_categories, products
  3. Customers
  4. Inventory
  5. Sales and line items
- Use pagination to handle large datasets
- Implement retry logic for API rate limits

### 2. Incremental Sync
- Use `updated_at` timestamps where available
- For sales, use `sale_date` with a buffer period
- Track sync state per entity type
- Handle deletions via `deleted_at` timestamps

### 3. Version Control
- Store Lightspeed version numbers where provided
- Use for conflict resolution and audit trails

## Indexes and Performance

### Key Indexes
1. **Time-based queries**: All `updated_at`, `created_at`, `sale_date` fields
2. **Lookup queries**: SKU, customer email, invoice numbers
3. **Reporting queries**: Product categories, date ranges, customer segments
4. **Inventory queries**: Low stock alerts, outlet-specific views

### Partitioning Strategy
- Consider partitioning `sales` and `sale_line_items` by month for large datasets
- Archive old data after defined retention period

## Security Considerations

### Row-Level Security (RLS)
```sql
-- Example RLS policy for multi-tenant access
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

CREATE POLICY outlet_isolation ON products
    FOR ALL
    USING (outlet_id = current_setting('app.current_outlet_id')::uuid);
```

### Audit Trail
- Track all modifications via updated_at timestamps
- Maintain sync_log for data lineage
- Consider trigger-based audit table for sensitive data

## Maintenance Views

### 1. Daily Sales Summary
```sql
CREATE VIEW daily_sales_summary AS
SELECT 
    DATE(sale_date) as sale_date,
    outlet_id,
    COUNT(*) as transaction_count,
    SUM(total_price) as total_revenue,
    SUM(total_tax) as total_tax,
    SUM(total_discount) as total_discount
FROM sales
WHERE status = 'CLOSED'
AND deleted_at IS NULL
GROUP BY DATE(sale_date), outlet_id;
```

### 2. Low Stock Alert
```sql
CREATE VIEW low_stock_products AS
SELECT 
    p.id,
    p.name,
    p.sku,
    i.outlet_id,
    i.current_amount,
    i.reorder_point
FROM inventory i
JOIN products p ON i.product_id = p.id
WHERE i.current_amount <= i.reorder_point
AND p.track_inventory = true
AND p.is_active = true;
```

### 3. Sync Health Dashboard
```sql
CREATE VIEW sync_health AS
SELECT 
    entity_type,
    last_sync_timestamp,
    last_successful_sync,
    CASE 
        WHEN last_successful_sync < NOW() - INTERVAL '25 hours' THEN 'ALERT'
        WHEN last_successful_sync < NOW() - INTERVAL '2 hours' THEN 'WARNING'
        ELSE 'OK'
    END as sync_status
FROM sync_state;
```

## Migration Scripts

### Initial Schema Creation
```sql
-- Run in order:
-- 1. Create reference tables (outlets, taxes, users, etc.)
-- 2. Create product-related tables
-- 3. Create transaction tables
-- 4. Create sync management tables
-- 5. Create indexes
-- 6. Create views
-- 7. Set up RLS policies if needed
```

## Monitoring and Alerts

### Key Metrics to Monitor
1. **Sync Performance**
   - Records per second
   - API response times
   - Error rates

2. **Data Quality**
   - Missing references
   - Duplicate records
   - Data staleness

3. **Business Metrics**
   - Daily transaction volumes
   - Inventory levels
   - Customer growth

## Next Phase: Analytics Dashboard

This data integration system serves as the foundation for **Phase 2: Analytics Dashboard** (see `../02-analytics-dashboard/`), which will provide executive-level business insights through a Streamlit interface.

### Data Available for Analytics
- **Complete sales history** in `lightspeed_sales` and `lightspeed_sale_line_items`
- **Product catalog** with inventory levels
- **Customer database** for segmentation analysis
- **Multi-outlet data** for location-based insights

## Implementation Notes

This system successfully transformed Craft Contemporary's data infrastructure from:
- **Before**: Data locked in Lightspeed POS system
- **After**: Complete data sync to Supabase with monitoring dashboard

**Result**: Foundation established for data-driven decision making and executive analytics dashboard development.

---
**Document Status**: ✅ UPDATED - Reflects actual production implementation  
**Last Updated**: 2025-07-17  
**System Status**: Production ready with daily sync operations