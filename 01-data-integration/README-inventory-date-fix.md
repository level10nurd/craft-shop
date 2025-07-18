# Inventory Date Tracking Fix

## Problem Solved
The inventory sync was only capturing Supabase sync timestamps (`created_at`, `updated_at`) instead of the actual dates from Lightspeed when inventory records were created/updated. This prevented historical inventory analysis over time.

## Solution Overview
Added new fields to track Lightspeed dates separately from Supabase sync dates:

- `lightspeed_created_at` - When inventory record was created in Lightspeed
- `lightspeed_updated_at` - When inventory record was last updated in Lightspeed  
- `created_at` - When record was synced to Supabase (unchanged)
- `updated_at` - When record was last synced to Supabase (unchanged)

## Implementation Steps

### 1. Apply Database Schema Changes
Run the SQL migration in your Supabase SQL editor:

```bash
# The SQL is in: 01-data-integration/script/add_lightspeed_dates_to_inventory.sql
```

### 2. Run Migration Script (Optional)
To backfill existing inventory records with proper Lightspeed dates:

```bash
cd 01-data-integration/script
python migrate_inventory_dates.py
```

### 3. Updated Transform Functions
The sync functions now capture Lightspeed dates:

**Before:**
```python
def transform_inventory(inventory: Dict) -> Dict:
    return {
        'id': inventory.get('id'),
        'product_id': inventory.get('product_id'),
        'current_amount': inventory.get('current_inventory', 0),
        'created_at': datetime.now(timezone.utc).isoformat(),  # ❌ Wrong
        'updated_at': datetime.now(timezone.utc).isoformat()   # ❌ Wrong
    }
```

**After:**
```python
def transform_inventory(inventory: Dict) -> Dict:
    return {
        'id': inventory.get('id'),
        'product_id': inventory.get('product_id'),
        'current_amount': inventory.get('current_inventory', 0),
        'lightspeed_created_at': inventory.get('created_at'),    # ✅ Lightspeed date
        'lightspeed_updated_at': inventory.get('updated_at'),    # ✅ Lightspeed date
        'created_at': datetime.now(timezone.utc).isoformat(),   # ✅ Supabase sync date
        'updated_at': datetime.now(timezone.utc).isoformat()    # ✅ Supabase sync date
    }
```

## Usage for Historical Analysis

Now you can query inventory history using the Lightspeed dates:

```sql
-- See inventory changes over time
SELECT 
    product_id,
    current_amount,
    lightspeed_updated_at,
    created_at as sync_date
FROM lightspeed_inventory 
WHERE lightspeed_updated_at >= '2024-01-01'
ORDER BY lightspeed_updated_at DESC;

-- Track inventory levels by month
SELECT 
    DATE_TRUNC('month', lightspeed_updated_at) as month,
    product_id,
    AVG(current_amount) as avg_inventory
FROM lightspeed_inventory
GROUP BY month, product_id
ORDER BY month DESC;
```

## Files Modified

1. **Database Schema:** `script/add_lightspeed_dates_to_inventory.sql`
2. **Incremental Sync:** `src/incremental_sync.py` - `transform_inventory()` function
3. **Historical Import:** `src/initial-setup/historical_import.py` - `transform_inventory()` function  
4. **Migration Script:** `script/migrate_inventory_dates.py`

## Next Steps

1. Run the SQL migration in Supabase
2. Test with a small inventory sync to verify the new fields are populated
3. Run the migration script to backfill existing data (optional but recommended)
4. Update your analytics queries to use `lightspeed_updated_at` for historical analysis

## Testing

Test the fix by running an incremental sync and checking that new inventory records have both sets of dates:

```bash
cd 01-data-integration/src
python incremental_sync.py
```

Then verify in Supabase that inventory records have:
- `lightspeed_created_at` and `lightspeed_updated_at` from Lightspeed API
- `created_at` and `updated_at` as sync timestamps 