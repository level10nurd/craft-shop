-- First check what's in sync_state for sales
SELECT entity_type, last_version, status FROM sync_state WHERE entity_type = 'sales';

-- If sales sync_state doesn't exist, create it
INSERT INTO sync_state (entity_type, status, last_version, last_sync_time, created_at, updated_at) 
VALUES ('sales', 'success', 0, NOW(), NOW(), NOW())
ON CONFLICT (entity_type) DO NOTHING;

-- Update with a reasonable version number (we'll need to find the actual highest version from recent sales)
-- For now, set to 0 so it only fetches recent sales, then update after the first real incremental sync
UPDATE sync_state 
SET last_version = 0, status = 'success', updated_at = NOW() 
WHERE entity_type = 'sales';