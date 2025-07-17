-- Add missing last_version column to sync_state table
ALTER TABLE public.sync_state 
ADD COLUMN IF NOT EXISTS last_version BIGINT;