#!/usr/bin/env python3
"""
Test script for TomTom search and store functionality
"""

import requests
import json

def test_tomtom_search_and_store():
    """Test the new search-and-store endpoint"""
    
    # Test data
    test_data = {
        "query": "coffee",
        "location": "Delhi", 
        "limit": 5
    }
    
    # Make request to the new endpoint
    url = "http://localhost:5000/api/tomtom/search-and-store"
    
    try:
        print("🔍 Testing TomTom search and store functionality...")
        print(f"Request data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Message: {result.get('message')}")
            print(f"Inserted count: {result.get('inserted_count')}")
            print(f"Total found: {result.get('total_found')}")
            print(f"Query: {result.get('query')}")
            print(f"Location: {result.get('location')}")
            
            if result.get('inserted_ids'):
                print(f"Inserted IDs: {result.get('inserted_ids')}")
        else:
            print("❌ Error!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the Flask server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_tomtom_search_only():
    """Test the regular search endpoint for comparison"""
    
    url = "http://localhost:5000/api/tomtom/search"
    params = {
        "query": "coffee",
        "location": "Delhi",
        "limit": 3
    }
    
    try:
        print("\n🔍 Testing TomTom search only (for comparison)...")
        
        response = requests.get(url, params=params)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Search successful!")
            print(f"Found {result.get('count')} places")
            print(f"Sample place: {json.dumps(result.get('places', [])[0] if result.get('places') else {}, indent=2)}")
        else:
            print("❌ Search failed!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the Flask server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🚀 Starting TomTom Search and Store Tests")
    print("=" * 50)
    
    # Test search and store
    test_tomtom_search_and_store()
    
    # Test search only for comparison
    test_tomtom_search_only()
    
    print("\n" + "=" * 50)
    print("�� Tests completed!") 