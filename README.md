# Craft Contemporary - Data & Analytics Platform

Multi-phase project to transform Lightspeed POS data into actionable business insights for executive leadership.

## Project Phases

### ✅ Phase 1: Data Integration (`01-data-integration/`)
**Status: COMPLETED**
- Sync Lightspeed Retail POS data to Supabase
- Historical import + daily incremental updates
- Monitoring and logging system

### 🚧 Phase 2: Analytics Dashboard (`02-analytics-dashboard/`)
**Status: IN PROGRESS** 
- Streamlit executive dashboard
- Real-time business insights
- Strategic decision-making tools

## Quick Start
- **Run data sync**: `./setup_cron.sh` (sets up daily automation)
- **Manual sync**: `python3 01-data-integration/src/incremental_sync.py`
- **Development tools**: See `dev-setup/` directory

## Project Structure
```
├── 01-data-integration/    # Completed sync system
├── 02-analytics-dashboard/ # Dashboard development  
├── dev-setup/             # Development utilities
├── requirements.txt       # Python dependencies
└── setup_cron.sh         # Automated sync setup
```