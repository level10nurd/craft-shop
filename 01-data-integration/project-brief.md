# Craft Contemporary Data Integration Service

## Project Overview
Build a data synchronization service between Lightspeed Retail POS and Supabase for Craft Contemporary.

## Key Requirements
1. **Historical Import**: One-time import of all existing Lightspeed data
2. **Nightly Updates**: Automated daily sync of new/modified data
3. **Data Sources**: Lightspeed Retail API
4. **Data Target**: Supabase database

## Technical Considerations
- API rate limiting and pagination
- Error handling and retry logic
- Data transformation and mapping
- Scheduling for nightly runs
- Monitoring and alerting
- Idempotent operations to prevent duplicates

## Success Criteria
- Complete historical data import
- Reliable nightly synchronization
- Data integrity maintained
- Audit trail of sync operations