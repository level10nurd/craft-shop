#!/usr/bin/env python3
"""
Test script to verify Flask server is responding.
"""

import requests
import time

def test_connection():
    """Test if Flask server is responding."""
    url = "http://127.0.0.1:5001"
    
    print(f"🔍 Testing connection to {url}")
    
    try:
        response = requests.get(f"{url}/health", timeout=5)
        print(f"✅ Health check successful: {response.status_code}")
        print(f"📊 Response: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - server not running")
        return False
    except requests.exceptions.Timeout:
        print("❌ Connection timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_login_page():
    """Test if login page loads."""
    url = "http://127.0.0.1:5001"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 or response.status_code == 302:
            print(f"✅ Login page accessible: {response.status_code}")
            return True
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login page error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Flask Dashboard Connection")
    print("=" * 50)
    
    # Test health endpoint
    health_ok = test_connection()
    
    if health_ok:
        # Test login page
        login_ok = test_login_page()
        
        if login_ok:
            print("\n🎉 All tests passed!")
            print("🌐 Dashboard should be accessible at: http://127.0.0.1:5001")
            print("🔑 Login password: craft2025")
        else:
            print("\n⚠️  Health check passed but login page failed")
    else:
        print("\n❌ Server not responding. Make sure Flask app is running:")
        print("   python3 run_app.py")