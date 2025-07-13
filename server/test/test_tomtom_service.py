#!/usr/bin/env python3
"""
Test script for TomTomService with mock data
"""

import os
import sys
from services.tomtom_service import TomTomService

def test_tomtom_service():
    """Test the TomTomService with and without API key"""
    
    print("🚀 Testing TomTomService")
    print("=" * 50)
    
    # Test without API key (will use mock data)
    print("\n🔧 Testing WITHOUT API key (mock data mode)...")
    service_no_key = TomTomService()
    
    test_queries = [
        ("coffee", "Delhi", 3),
        ("restaurant", "Mumbai", 3),
        ("park", "Bangalore", 3)
    ]
    
    for query, location, limit in test_queries:
        print(f"\n🔍 Testing: '{query}' in '{location}' (limit: {limit})")
        
        try:
            places = service_no_key.search_places(query, location, limit)
            
            if places:
                print(f"✅ Found {len(places)} places (mock data)")
                
                # Show first result in detail
                if len(places) > 0:
                    first_place = places[0]
                    print(f"\n📋 First result:")
                    print(f"   Name: {first_place.get('name')}")
                    print(f"   Category: {first_place.get('category')}")
                    print(f"   Address: {first_place.get('address')}")
                    print(f"   Photo: {'✅' if first_place.get('photo_url') else '❌'}")
                    print(f"   Description: {first_place.get('description', 'N/A')[:50]}...")
                    
                    # Test place details
                    place_id = first_place.get('fsq_id')
                    if place_id:
                        details = service_no_key.get_place_details(place_id)
                        if details:
                            print(f"   Phone: {details.get('phone', 'N/A')}")
                            print(f"   Website: {details.get('website', 'N/A')}")
            else:
                print("❌ No places found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test with API key if available
    api_key = os.getenv("TOMTOM_API_KEY")
    if api_key:
        print(f"\n🔧 Testing WITH API key...")
        service_with_key = TomTomService(api_key)
        
        try:
            places = service_with_key.search_places("coffee", "Delhi", 2)
            if places:
                print(f"✅ Found {len(places)} places from real API")
                print(f"   First place: {places[0].get('name')}")
            else:
                print("❌ No places found from API")
        except Exception as e:
            print(f"❌ API Error: {e}")
    else:
        print(f"\n⚠️  No TOMTOM_API_KEY found")
        print("   To test with real API, set: export TOMTOM_API_KEY='your_key'")
    
    print("\n✅ Test completed!")

def test_api_endpoints():
    """Test the API endpoints"""
    
    print("\n🌐 Testing API Endpoints:")
    print("=" * 50)
    
    # Simulate API calls
    service = TomTomService()
    
    # Test search endpoint
    print("\n🔍 Testing /search endpoint...")
    places = service.search_places("coffee", "Delhi", 3)
    
    if places:
        print(f"✅ Search endpoint working - found {len(places)} places")
        
        # Test details endpoint
        if len(places) > 0:
            place_id = places[0].get('fsq_id')
            print(f"\n🔍 Testing /details/{place_id} endpoint...")
            
            details = service.get_place_details(place_id)
            if details:
                print(f"✅ Details endpoint working")
                print(f"   Place: {details.get('name')}")
                print(f"   Phone: {details.get('phone', 'N/A')}")
            else:
                print("❌ Details endpoint failed")
    else:
        print("❌ Search endpoint failed")

def show_usage_example():
    """Show how to use the service"""
    
    print("\n📖 Usage Example:")
    print("=" * 50)
    
    example_code = '''
# Initialize service (works with or without API key)
from services.tomtom_service import TomTomService

# Without API key - uses mock data
service = TomTomService()

# With API key - uses real API
service = TomTomService("your_tomtom_api_key")

# Search for places (same interface as Foursquare)
places = service.search_places("coffee", "Delhi", 10)

# Get detailed info for a specific place
if places:
    place_id = places[0].get('fsq_id')
    details = service.get_place_details(place_id)

# API Endpoints:
# GET /tomtom/search?query=coffee&location=Delhi&limit=10
# GET /tomtom/details/<place_id>
# GET /tomtom/test

# Mock data includes:
# ✅ Realistic place names and addresses
# ✅ High-quality Unsplash photos
# ✅ Rich descriptions and attributes
# ✅ Phone numbers and websites
# ✅ Opening hours and categories
'''
    
    print(example_code)

if __name__ == "__main__":
    test_tomtom_service()
    test_api_endpoints()
    show_usage_example() 