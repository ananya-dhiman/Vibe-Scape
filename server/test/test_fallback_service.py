#!/usr/bin/env python3
"""
Test script for the complete fallback service functionality
"""

import requests
import json

def test_fallback_search():
    """Test the fallback search endpoint"""
    
    # Test data matching your requirements
    test_data = {
        "city": "Delhi",
        "category": "cafe", 
        "vibe_tags": ["aesthetic"],
        "min_results": 5
    }
    
    # Make request to the fallback endpoint
    url = "http://localhost:5000/api/fallback/search"
    
    try:
        print("🔍 Testing Fallback Search Service...")
        print(f"Request data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Message: {result.get('message')}")
            print(f"Source: {result.get('source')}")
            print(f"Count: {result.get('count')}")
            print(f"Fallback used: {result.get('fallback_used')}")
            print(f"TomTom fetched: {result.get('tomtom_fetched', 0)}")
            print(f"Reviews scraped: {result.get('reviews_scraped', 0)}")
            
            # Show sample place if available
            places = result.get('places', [])
            if places:
                print(f"\n📋 Sample place:")
                sample_place = places[0]
                print(f"  Name: {sample_place.get('original', {}).get('name', 'N/A')}")
                print(f"  Category: {sample_place.get('original', {}).get('category', 'N/A')}")
                print(f"  City: {sample_place.get('original', {}).get('city', 'N/A')}")
                
                # Show reviews if available
                reviews = sample_place.get('reviews', [])
                if reviews:
                    print(f"  Reviews: {len(reviews)} Reddit reviews found")
                    for i, review in enumerate(reviews[:2]):  # Show first 2 reviews
                        print(f"    Review {i+1}: {review.get('content', '')[:100]}...")
                else:
                    print(f"  Reviews: No reviews found")
            else:
                print("❌ No places returned")
        else:
            print("❌ Error!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the Flask server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_fallback_test_endpoint():
    """Test the fallback test endpoint"""
    
    url = "http://localhost:5000/api/fallback/test"
    
    try:
        print("\n🧪 Testing Fallback Test Endpoint...")
        
        response = requests.get(url)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Test successful!")
            print(f"Message: {result.get('message')}")
            print(f"Test data: {result.get('test_data')}")
            
            # Show test result summary
            test_result = result.get('result', {})
            print(f"Test result count: {test_result.get('count', 0)}")
            print(f"Test result source: {test_result.get('source', 'unknown')}")
        else:
            print("❌ Test failed!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the Flask server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_different_scenarios():
    """Test different search scenarios"""
    
    scenarios = [
        {
            "name": "Cafe with aesthetic vibe",
            "data": {
                "city": "Delhi",
                "category": "cafe",
                "vibe_tags": ["aesthetic"],
                "min_results": 3
            }
        },
        {
            "name": "Restaurant with cozy vibe", 
            "data": {
                "city": "Mumbai",
                "category": "restaurant",
                "vibe_tags": ["cozy"],
                "min_results": 2
            }
        },
        {
            "name": "Park with peaceful vibe",
            "data": {
                "city": "Delhi", 
                "category": "park",
                "vibe_tags": ["peaceful"],
                "min_results": 4
            }
        }
    ]
    
    url = "http://localhost:5000/api/fallback/search"
    
    for scenario in scenarios:
        try:
            print(f"\n🔍 Testing: {scenario['name']}")
            print(f"Data: {json.dumps(scenario['data'], indent=2)}")
            
            response = requests.post(url, json=scenario['data'])
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result.get('count')} places found")
                print(f"   Source: {result.get('source')}")
                print(f"   Fallback used: {result.get('fallback_used')}")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error in scenario {scenario['name']}: {e}")

if __name__ == "__main__":
    print("🚀 Starting Fallback Service Tests")
    print("=" * 60)
    
    # Test main fallback search
    test_fallback_search()
    
    # Test fallback test endpoint
    test_fallback_test_endpoint()
    
    # Test different scenarios
    test_different_scenarios()
    
    print("\n" + "=" * 60)
    print("🏁 All tests completed!") 