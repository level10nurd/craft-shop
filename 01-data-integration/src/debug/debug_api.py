#!/usr/bin/env python3
"""
Debug script to test Lightspeed API connection with more detailed error info.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')

def debug_api_connection():
    """Debug API connection with detailed error information."""
    base_url = os.environ.get('LIGHTSPEED_BASE_URL')
    bearer_token = os.environ.get('LIGHTSPEED_BEARER_TOKEN')
    
    print("🔍 Debugging Lightspeed API Connection")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print(f"Token (first 10 chars): {bearer_token[:10]}...")
    
    # Test different endpoints and API versions
    test_endpoints = [
        "api/2.0/outlets",
        "api/outlets", 
        "api/2.0/customers",
        "outlets",
        "customers"
    ]
    
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    for endpoint in test_endpoints:
        url = f"{base_url.rstrip('/')}/{endpoint}"
        print(f"\n🔗 Testing: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10, params={'per_page': 1})
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Success!")
                try:
                    data = response.json()
                    print(f"   📄 Response type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"   🔑 Keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"   📊 Items count: {len(data)}")
                except:
                    print(f"   📄 Response (first 200 chars): {response.text[:200]}")
                break
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   💥 Exception: {e}")
    
    # Test with different authentication methods
    print(f"\n🔐 Testing different auth methods")
    
    # Try without Bearer prefix
    alt_headers = {
        'Authorization': bearer_token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    url = f"{base_url.rstrip('/')}/api/2.0/outlets"
    try:
        response = requests.get(url, headers=alt_headers, timeout=10, params={'per_page': 1})
        print(f"   Without 'Bearer' prefix: {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    debug_api_connection()