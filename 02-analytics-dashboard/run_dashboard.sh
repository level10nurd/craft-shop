#!/bin/bash

# Craft Contemporary Analytics Dashboard Startup Script

echo "🚀 Starting Craft Contemporary Analytics Dashboard..."

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "❌ Error: .env file not found in parent directory"
    echo "Please ensure your .env file is configured with Supabase credentials"
    echo "Example .env content:"
    echo "SUPABASE_URL=https://your-project.supabase.co"
    echo "SUPABASE_SERVICE_ROLE_KEY=your-service-role-key"
    echo "DASHBOARD_PASSWORD=craft2025"
    exit 1
fi

# Navigate to source directory
cd src

# Start Streamlit application
echo "📊 Launching dashboard on http://localhost:8501"
echo "🔑 Default password: craft2025"
echo ""
echo "Press Ctrl+C to stop the dashboard"

streamlit run main.py --server.port 8501 --server.address localhost