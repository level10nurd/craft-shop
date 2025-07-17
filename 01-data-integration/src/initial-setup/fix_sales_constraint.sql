-- Remove foreign key constraints that are blocking sales import
-- Run this in Supabase SQL Editor

-- Drop foreign key constraint on customer_id in sales table
ALTER TABLE lightspeed_sales DROP CONSTRAINT IF EXISTS lightspeed_sales_customer_id_fkey;

-- Drop foreign key constraint on outlet_id in sales table (might also be an issue)
ALTER TABLE lightspeed_sales DROP CONSTRAINT IF EXISTS lightspeed_sales_outlet_id_fkey;

-- Also check sale_line_items table constraints
ALTER TABLE lightspeed_sale_line_items DROP CONSTRAINT IF EXISTS lightspeed_sale_line_items_sale_id_fkey;
ALTER TABLE lightspeed_sale_line_items DROP CONSTRAINT IF EXISTS lightspeed_sale_line_items_product_id_fkey;