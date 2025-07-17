-- Update sales sync_state to allow incremental sync
UPDATE sync_state 
SET 
    last_version = 0,
    status = 'success',
    updated_at = NOW()
WHERE entity_type = 'sales';