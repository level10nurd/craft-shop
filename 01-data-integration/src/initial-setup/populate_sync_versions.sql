-- Update sync_state table with last_version from most recent successful sync logs
-- This fixes the issue where sync_state has NULL last_version values

-- For outlets (version 43157382149 from the log)
UPDATE sync_state 
SET last_version = 43157382149 
WHERE entity_type = 'outlets' AND status = 'success';

-- For customers (version 44183844375 from the log)  
UPDATE sync_state 
SET last_version = 44183844375 
WHERE entity_type = 'customers' AND status = 'success';

-- For products (version 44294029722 from the log)
UPDATE sync_state 
SET last_version = 44294029722 
WHERE entity_type = 'products' AND status = 'success';

-- Check what we have so far
SELECT entity_type, last_version, status FROM sync_state ORDER BY entity_type;