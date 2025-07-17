# Lightweight PRD: Craft Contemporary Data Sync

## Overview
Simple script to sync data from Lightspeed Retail POS to Supabase database.

## Core Requirements

### 1. Data Sync
- One-time historical import of all Lightspeed data
- Daily sync script to update changed records
- Focus on essential data: products, inventory, categories, sales

### 2. Technical Approach
- Python script using Lightspeed API and Supabase client
- Simple cron job for daily runs
- Basic logging to track sync status
- Store last sync timestamp to fetch only new/modified data

### 3. Implementation Details

#### Setup
- API credentials in `.env` file
- Simple config file for field mappings
- Basic error handling with retries

#### Historical Import
- Script to pull all data with pagination
- Direct insert into Supabase tables
- Progress output to console

#### Daily Sync
- Check last sync timestamp
- Fetch modified records from Lightspeed
- Upsert into Supabase
- Update sync timestamp

### 4. Success Criteria
- All historical data imported
- Daily sync runs without manual intervention
- Basic logs show what was synced

### 5. Timeline
- Week 1: Setup and historical import script
- Week 2: Daily sync script and testing
- Week 3: Deploy and monitor

### 6. Tools/Stack
- Python 3.x
- `requests` for Lightspeed API
- `supabase-py` for Supabase
- `python-dotenv` for config
- `cron` for scheduling

### 7. Nice-to-haves (if time permits)
- Email notification on sync failures
- Simple web dashboard to check sync status
- Dry-run mode for testing

---

**Note**: This is a personal tool - prioritizing simplicity and reliability over scalability or advanced features.