# Craft Contemporary Database Architecture

## Overview
This document outlines the database architecture for syncing data from Lightspeed Retail POS to Supabase, designed to support Craft Contemporary's retail operations.

## Architecture Diagram
```
┌─────────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Lightspeed API    │────▶│  Python Sync     │────▶│   Supabase DB  │
│  (Source of Truth) │     │    Service       │     │  (PostgreSQL)   │
└─────────────────────┘     └──────────────────┘     └─────────────────┘
                                   │
                                   ▼
                            ┌──────────────┐
                            │   Sync Log   │
                            │  & Metadata  │
                            └──────────────┘
```

## Database Schema

### Core Tables

#### 1. Products
```sql
CREATE TABLE products (
    id UUID PRIMARY KEY,                          -- Lightspeed product_id
    handle VARCHAR(255),                          -- Product handle/slug
    name VARCHAR(255) NOT NULL,
    description TEXT,
    brand_id UUID,
    supplier_id UUID,
    product_type_id UUID,
    sku VARCHAR(255),
    supply_price DECIMAL(10, 2),
    retail_price DECIMAL(10, 2),
    tax_id UUID,
    is_active BOOLEAN DEFAULT true,
    track_inventory BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    lightspeed_version BIGINT,                    -- For version tracking
    
    INDEXES:
    - idx_products_sku ON (sku)
    - idx_products_active ON (is_active)
    - idx_products_updated ON (updated_at)
);
```

#### 2. Inventory
```sql
CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id),
    outlet_id UUID NOT NULL,
    current_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    reorder_point DECIMAL(10, 2),
    reorder_amount DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(product_id, outlet_id),
    
    INDEXES:
    - idx_inventory_product ON (product_id)
    - idx_inventory_outlet ON (outlet_id)
    - idx_inventory_low_stock ON (current_amount, reorder_point)
);
```

#### 3. Product Categories
```sql
CREATE TABLE product_categories (
    id UUID PRIMARY KEY,                          -- Lightspeed category_id
    name VARCHAR(255) NOT NULL,
    parent_id UUID REFERENCES product_categories(id),
    position INTEGER,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    INDEXES:
    - idx_categories_parent ON (parent_id)
    - idx_categories_name ON (name)
);

CREATE TABLE product_category_mappings (
    product_id UUID REFERENCES products(id),
    category_id UUID REFERENCES product_categories(id),
    PRIMARY KEY (product_id, category_id)
);
```

#### 4. Sales
```sql
CREATE TABLE sales (
    id UUID PRIMARY KEY,                          -- Lightspeed sale_id
    outlet_id UUID NOT NULL,
    register_id UUID NOT NULL,
    user_id UUID,
    customer_id UUID,
    invoice_number VARCHAR(50),
    receipt_number VARCHAR(50),
    short_code VARCHAR(20),
    status VARCHAR(50),                           -- CLOSED, LAYBY, SAVED, etc.
    sale_date TIMESTAMP WITH TIME ZONE NOT NULL,
    total_price DECIMAL(10, 2),
    total_tax DECIMAL(10, 2),
    total_discount DECIMAL(10, 2),
    total_loyalty DECIMAL(10, 2),
    note TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    lightspeed_version BIGINT,
    
    INDEXES:
    - idx_sales_date ON (sale_date)
    - idx_sales_status ON (status)
    - idx_sales_customer ON (customer_id)
    - idx_sales_outlet ON (outlet_id)
    - idx_sales_invoice ON (invoice_number)
);
```

#### 5. Sale Line Items
```sql
CREATE TABLE sale_line_items (
    id UUID PRIMARY KEY,                          -- Lightspeed line_item_id
    sale_id UUID NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    quantity DECIMAL(10, 2) NOT NULL,
    unit_price DECIMAL(10, 2),
    unit_cost DECIMAL(10, 2),
    unit_discount DECIMAL(10, 2),
    unit_tax DECIMAL(10, 2),
    total_price DECIMAL(10, 2),
    total_cost DECIMAL(10, 2),
    total_discount DECIMAL(10, 2),
    total_tax DECIMAL(10, 2),
    status VARCHAR(50),
    sequence INTEGER,
    is_return BOOLEAN DEFAULT false,
    note TEXT,
    
    INDEXES:
    - idx_line_items_sale ON (sale_id)
    - idx_line_items_product ON (product_id)
);
```

#### 6. Customers
```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY,                          -- Lightspeed customer_id
    customer_code VARCHAR(100),
    email VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company_name VARCHAR(255),
    phone VARCHAR(50),
    mobile VARCHAR(50),
    customer_group_id UUID,
    loyalty_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    INDEXES:
    - idx_customers_email ON (email)
    - idx_customers_code ON (customer_code)
    - idx_customers_name ON (last_name, first_name)
);
```

#### 7. Suppliers
```sql
CREATE TABLE suppliers (
    id UUID PRIMARY KEY,                          -- Lightspeed supplier_id
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE
);
```

#### 8. Brands
```sql
CREATE TABLE brands (
    id UUID PRIMARY KEY,                          -- Lightspeed brand_id
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE
);
```

### Sync Management Tables

#### 9. Sync Log
```sql
CREATE TABLE sync_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sync_type VARCHAR(50) NOT NULL,              -- 'historical', 'incremental'
    entity_type VARCHAR(50) NOT NULL,            -- 'products', 'sales', etc.
    status VARCHAR(50) NOT NULL,                 -- 'started', 'completed', 'failed'
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    records_processed INTEGER DEFAULT 0,
    records_created INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_deleted INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB,                              -- Additional sync details
    
    INDEXES:
    - idx_sync_log_date ON (started_at)
    - idx_sync_log_status ON (status)
    - idx_sync_log_entity ON (entity_type)
);
```

#### 10. Sync State
```sql
CREATE TABLE sync_state (
    entity_type VARCHAR(50) PRIMARY KEY,
    last_sync_timestamp TIMESTAMP WITH TIME ZONE,
    last_successful_sync TIMESTAMP WITH TIME ZONE,
    last_version BIGINT,                         -- For version-based sync
    metadata JSONB
);
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

## Future Considerations

### Potential Enhancements
1. **Real-time sync** via webhooks (if Lightspeed supports)
2. **Data warehousing** for advanced analytics
3. **Cache layer** for frequently accessed data
4. **Event streaming** for downstream systems
5. **Multi-outlet** data segregation
6. **Archival strategy** for old transactions

### Scalability Plans
- Implement connection pooling
- Consider read replicas for reporting
- Add materialized views for complex queries
- Implement data retention policies

## Conclusion
This architecture provides a robust foundation for syncing Lightspeed POS data to Supabase, with considerations for performance, maintainability, and future growth. The design prioritizes data integrity while keeping the implementation simple and reliable.