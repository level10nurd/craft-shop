-- Add Lightspeed date fields to inventory table for historical tracking
-- This addresses the issue where inventory records only had Supabase sync dates,
-- not the actual dates from Lightspeed for historical inventory analysis

-- Add new columns for Lightspeed dates
ALTER TABLE lightspeed_inventory 
ADD COLUMN IF NOT EXISTS lightspeed_created_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS lightspeed_updated_at TIMESTAMPTZ;

-- Add an index for historical queries
CREATE INDEX IF NOT EXISTS idx_lightspeed_inventory_lightspeed_updated_at 
ON lightspeed_inventory (lightspeed_updated_at);

-- Add a comment explaining the columns
COMMENT ON COLUMN lightspeed_inventory.lightspeed_created_at IS 'Date when inventory record was created in Lightspeed (for historical tracking)';
COMMENT ON COLUMN lightspeed_inventory.lightspeed_updated_at IS 'Date when inventory record was last updated in Lightspeed (for historical tracking)';
COMMENT ON COLUMN lightspeed_inventory.created_at IS 'Date when record was synced to Supabase';
COMMENT ON COLUMN lightspeed_inventory.updated_at IS 'Date when record was last synced to Supabase'; 