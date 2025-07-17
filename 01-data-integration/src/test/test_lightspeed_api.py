#!/usr/bin/env python3
"""
Test script to verify Lightspeed API connection and explore available data.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

load_dotenv('.env.local')

from lightspeed_client import create_lightspeed_client, LightspeedAPIError

def test_api_connection():
    """Test basic API connectivity."""
    print("🔍 Testing Lightspeed API Connection")
    print("=" * 50)
    
    try:
        client = create_lightspeed_client()
        print(f"✅ Client created with base URL: {client.base_url}")
        
        # Test connection
        if client.test_connection():
            print("✅ API connection successful!")
            return client
        else:
            print("❌ API connection failed")
            return None
            
    except Exception as e:
        print(f"❌ Error creating client: {e}")
        return None

def explore_outlets(client):
    """Explore outlet data structure."""
    print("\n🏪 Exploring Outlets")
    print("-" * 30)
    
    try:
        outlets = client.get_outlets()
        print(f"✅ Found {len(outlets)} outlets")
        
        if outlets:
            print("\n📊 Sample outlet structure:")
            sample = outlets[0]
            for key, value in sample.items():
                print(f"  {key}: {value}")
                
        return outlets
        
    except LightspeedAPIError as e:
        print(f"❌ Error fetching outlets: {e}")
        return []

def explore_customers(client):
    """Explore customer data structure."""
    print("\n👥 Exploring Customers (first 5)")
    print("-" * 30)
    
    try:
        # Fetch just first page to explore structure
        response = client._make_request('2.0/customers', {'per_page': 5})
        customers = response.get('data', response)
        
        if isinstance(customers, list):
            print(f"✅ Found {len(customers)} customers (sample)")
            
            if customers:
                print("\n📊 Sample customer structure:")
                sample = customers[0]
                for key, value in sample.items():
                    print(f"  {key}: {value}")
        else:
            print("⚠️  Unexpected customer data structure")
            print(f"Response: {customers}")
            
    except LightspeedAPIError as e:
        print(f"❌ Error fetching customers: {e}")

def explore_products(client):
    """Explore product data structure."""
    print("\n📦 Exploring Products (first 5)")
    print("-" * 30)
    
    try:
        response = client._make_request('2.0/products', {'per_page': 5})
        products = response.get('data', response)
        
        if isinstance(products, list):
            print(f"✅ Found {len(products)} products (sample)")
            
            if products:
                print("\n📊 Sample product structure:")
                sample = products[0]
                for key, value in sample.items():
                    print(f"  {key}: {value}")
        else:
            print("⚠️  Unexpected product data structure")
            print(f"Response: {products}")
            
    except LightspeedAPIError as e:
        print(f"❌ Error fetching products: {e}")

def main():
    """Main test function."""
    # Test API connection
    client = test_api_connection()
    
    if not client:
        print("\n❌ Cannot proceed without API connection")
        return
        
    # Explore data structures
    outlets = explore_outlets(client)
    explore_customers(client)
    explore_products(client)
    
    print("\n🎉 API exploration complete!")
    print("\nNext steps:")
    print("1. Review the data structures above")
    print("2. Run the historical import script")
    print("3. Check your dashboard for sync status")

if __name__ == "__main__":
    main()