#!/usr/bin/env python3
"""
Simple script to run the Flask app with better error handling.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

try:
    from app import app
    print("✅ Flask app imported successfully")
    print(f"✅ Environment loaded: SUPABASE_URL={os.environ.get('SUPABASE_URL')[:30]}...")
    print(f"✅ Dashboard password: {os.environ.get('DASHBOARD_PASSWORD')}")
    
    print("\n🚀 Starting Flask development server on http://127.0.0.1:5001")
    print("📝 Login with password: craft2025")
    print("🔄 Press Ctrl+C to stop\n")
    
    app.run(debug=False, host='127.0.0.1', port=5001, threaded=True)
    
except Exception as e:
    print(f"❌ Error starting Flask app: {e}")
    sys.exit(1)