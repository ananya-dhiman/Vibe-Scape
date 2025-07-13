#!/usr/bin/env python3
"""
Test script for TripAdvisor scraper functionality
"""

import requests
import json

def test_tripadvisor_scraper():
    """Test the TripAdvisor scraper through the fallback service"""
    
    # Test data with Ahmedabad restaurants
    test_data = {
        "city": "Ahmedabad",
        "category": "restaurant",
        "vibe_tags": ["traditional"],
        "min_results": 3
    }
    
    # Make request to the fallback endpoint
    url = "http://localhost:5000/api/fallback/search"
    
    try:
        print("🔍 Testing TripAdvisor Scraper through Fallback Service...")
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
            print(f"Reddit reviews scraped: {result.get('reddit_reviews_scraped', 0)}")
            print(f"TripAdvisor reviews scraped: {result.get('tripadvisor_reviews_scraped', 0)}")
            
            # Show sample place with reviews
            places = result.get('places', [])
            if places:
                print(f"\n📋 Sample place with reviews:")
                sample_place = places[0]
                print(f"  Name: {sample_place.get('original', {}).get('name', 'N/A')}")
                print(f"  Category: {sample_place.get('original', {}).get('category', 'N/A')}")
                print(f"  City: {sample_place.get('original', {}).get('city', 'N/A')}")
                
                # Show reviews from both sources
                reviews = sample_place.get('reviews', [])
                if reviews:
                    print(f"  Total Reviews: {len(reviews)}")
                    
                    # Group reviews by source
                    reddit_reviews = [r for r in reviews if r.get('source') == 'reddit']
                    tripadvisor_reviews = [r for r in reviews if r.get('source') == 'tripadvisor']
                    
                    print(f"    Reddit reviews: {len(reddit_reviews)}")
                    print(f"    TripAdvisor reviews: {len(tripadvisor_reviews)}")
                    
                    # Show sample reviews
                    for i, review in enumerate(reviews[:3]):
                        source = review.get('source', 'unknown')
                        content = review.get('content', '')[:100]
                        print(f"    Review {i+1} ({source}): {content}...")
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

def test_direct_tripadvisor_scraper():
    """Test the TripAdvisor scraper directly"""
    
    try:
        print("\n🔍 Testing TripAdvisor Scraper Directly...")
        
        # Import and test the scraper
        from scraper.tripadvisor_scraper import TripAdvisorScraper
        
        scraper = TripAdvisorScraper()
        
        # Test with a known Ahmedabad restaurant
        place_name = "Agashiye"
        city = "Ahmedabad"
        
        print(f"Testing scraper for: {place_name} in {city}")
        
        reviews = scraper.search_place_reviews(place_name, city, max_results=3)
        
        print(f"✅ Found {len(reviews)} TripAdvisor reviews")
        
        for i, review in enumerate(reviews):
            print(f"  Review {i+1}:")
            print(f"    Source: {review.get('source')}")
            print(f"    Rating: {review.get('rating', 'N/A')}")
            print(f"    Reviewer: {review.get('reviewer_name', 'N/A')}")
            print(f"    Date: {review.get('review_date', 'N/A')}")
            print(f"    Content: {review.get('content', '')[:100]}...")
            print()
            
    except Exception as e:
        print(f"❌ Error testing TripAdvisor scraper: {e}")

if __name__ == "__main__":
    print("🚀 Starting TripAdvisor Scraper Tests")
    print("=" * 60)
    
    # Test through fallback service
    test_tripadvisor_scraper()
    
    # Test direct scraper
    test_direct_tripadvisor_scraper()
    
    print("\n" + "=" * 60)
    print("🏁 All tests completed!") 