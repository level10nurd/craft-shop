#!/bin/bash
# Setup script for daily incremental sync cron job
# Run this script to install the cron job for automated daily syncs

set -e

PROJECT_DIR="/Users/daltonallen/Documents/projects/00-active/craft-shop"
PYTHON_PATH="/usr/bin/python3"
SCRIPT_PATH="$PROJECT_DIR/01-data-integration/src/incremental_sync.py"
LOG_PATH="$PROJECT_DIR/cron_sync.log"

echo "🔧 Setting up daily sync cron job..."

# Make script executable
chmod +x "$SCRIPT_PATH"

# Create cron job entry
CRON_ENTRY="0 2 * * * cd $PROJECT_DIR && $PYTHON_PATH $SCRIPT_PATH >> $LOG_PATH 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "incremental_sync.py"; then
    echo "⚠️  Cron job already exists. Removing old entry..."
    crontab -l 2>/dev/null | grep -v "incremental_sync.py" | crontab -
fi

# Add new cron job
echo "Adding cron job: Daily sync at 2:00 AM"
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo "✅ Cron job installed successfully!"
echo ""
echo "📅 Schedule: Daily at 2:00 AM"
echo "📄 Logs: $LOG_PATH"
echo "🔍 View current cron jobs: crontab -l"
echo "❌ Remove cron job: crontab -e (then delete the line)"
echo ""
echo "🧪 Test sync manually: cd $PROJECT_DIR && python3 01-data-integration/src/incremental_sync.py"