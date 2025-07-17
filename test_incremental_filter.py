#!/usr/bin/env python3
"""
Test script to check if Lightspeed API filtering actually works.
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

sys.path.insert(0, 'src')
from lightspeed_client import create_lightspeed_client

load_dotenv('.env.local')

def test_filtering():
    print("🧪 Testing Lightspeed API incremental filtering...")
    
    lightspeed = create_lightspeed_client()
    
    # Test with a recent timestamp (last hour)
    recent_time = datetime.now(timezone.utc) - timedelta(hours=1)
    print(f"Testing with timestamp: {recent_time}")
    
    # Test customers
    print("\n📝 Testing customers filter...")
    customers = lightspeed.get_customers(since=recent_time)
    print(f"Found {len(customers)} customers modified in last hour")
    
    # Test products  
    print("\n📦 Testing products filter...")
    products = lightspeed.get_products(since=recent_time)
    print(f"Found {len(products)} products modified in last hour")
    
    # Test sales
    print("\n💰 Testing sales filter...")
    sales = lightspeed.get_sales(since=recent_time)
    print(f"Found {len(sales)} sales modified in last hour")
    
    # Compare with no filter
    print("\n🔍 Testing without filter (should be much more)...")
    all_customers = lightspeed.get_customers()
    print(f"Total customers without filter: {len(all_customers)}")
    
    print("\n📊 Summary:")
    print(f"Filtered customers: {len(customers)}")
    print(f"Total customers: {len(all_customers)}")
    print(f"Filter working? {'✅ YES' if len(customers) < len(all_customers) else '❌ NO - same count!'}")

if __name__ == "__main__":
    test_filtering()