-- Add last_version column to sync_state table for version-based incremental sync
ALTER TABLE sync_state ADD COLUMN IF NOT EXISTS last_version BIGINT DEFAULT NULL;

-- Add comment explaining the column
COMMENT ON COLUMN sync_state.last_version IS 'Highest version number from last successful sync for version-based pagination';