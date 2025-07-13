import requests
import time
from typing import List, Dict, Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import re

class TripAdvisorScraper:
    def __init__(self):
        self.base_url = "https://www.tripadvisor.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
    
    def search_place_reviews(self, place_name: str, city: str, max_results: int = 5) -> List[Dict]:
        """
        Search TripAdvisor for reviews about a specific place in a city
        
        Args:
            place_name: Name of the place to search for
            city: City where the place is located
            max_results: Maximum number of reviews to return
            
        Returns:
            List of review dictionaries with source and content
        """
        try:
            # Construct search query
            search_query = f"{place_name} {city}"
            encoded_query = quote_plus(search_query)
            
            # TripAdvisor search URL
            search_url = f"{self.base_url}/Search?q={encoded_query}&searchType=RESTAURANT"
            
            print(f"🔍 Searching TripAdvisor for: {search_query}")
            print(f"URL: {search_url}")
            
            # Make request to TripAdvisor search
            response = requests.get(search_url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ TripAdvisor returned status {response.status_code}")
                return []
            
            # Parse the search results page
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Debug: Save the HTML content to see what we're getting
            print(f"📄 Response length: {len(response.content)} characters")
            print(f"📄 Page title: {soup.title.get_text() if soup.title else 'No title'}")
            
            # Find the first restaurant result
            restaurant_link = self._find_restaurant_link(soup, place_name)
            
            if not restaurant_link:
                print("⚠️ No restaurant found on TripAdvisor search, trying direct URL...")
                # Try to construct a direct URL for known restaurants
                direct_url = self._try_direct_url(place_name, city)
                if direct_url:
                    print(f"🔗 Trying direct URL: {direct_url}")
                    reviews = self._scrape_restaurant_reviews(direct_url, max_results)
                    if reviews:
                        print(f"✅ Found {len(reviews)} reviews via direct URL")
                        return reviews
                
                print("⚠️ No restaurant found on TripAdvisor")
                return []
            
            # Get the restaurant page URL
            restaurant_url = self.base_url + restaurant_link
            
            # Fetch reviews from the restaurant page
            reviews = self._scrape_restaurant_reviews(restaurant_url, max_results)
            
            if not reviews:
                print("⚠️ No reviews found")
                return []
            
            print(f"✅ Found {len(reviews)} TripAdvisor reviews for {place_name}")
            return reviews
            
        except Exception as e:
            print(f"❌ Error scraping TripAdvisor: {e}")
            return []
    
    def _find_restaurant_link(self, soup: BeautifulSoup, place_name: str) -> Optional[str]:
        """
        Find the first restaurant link in search results
        """
        try:
            print(f"🔍 Looking for restaurant links for: {place_name}")
            
            # Try multiple selectors for restaurant links
            selectors = [
                'a[href*="/Restaurant_Review"]',
                'a[href*="/Restaurants"]',
                'a[href*="/Restaurant"]',
                '.result-title a',
                '.listing_title a',
                '.ui_column a'
            ]
            
            restaurant_links = []
            for selector in selectors:
                links = soup.select(selector)
                restaurant_links.extend(links)
                if links:
                    print(f"✅ Found {len(links)} links with selector: {selector}")
            
            # Remove duplicates while preserving order
            seen = set()
            unique_links = []
            for link in restaurant_links:
                href = link.get('href')
                if href and href not in seen:
                    seen.add(href)
                    unique_links.append(link)
            
            print(f"📊 Total unique restaurant links found: {len(unique_links)}")
            
            # Try to find exact match first
            place_lower = place_name.lower()
            for link in unique_links:
                link_text = link.get_text(strip=True).lower()
                link_href = link.get('href', '')
                
                print(f"🔍 Checking link: '{link_text}' -> {link_href}")
                
                # Check for exact match or partial match
                if (place_lower in link_text or 
                    any(word in link_text for word in place_lower.split()) or
                    place_lower.replace(' ', '') in link_text.replace(' ', '')):
                    print(f"✅ Found matching link: {link_text}")
                    return link_href
            
            # If no exact match, return the first restaurant link
            if unique_links:
                first_link = unique_links[0]
                print(f"⚠️ No exact match found, using first link: {first_link.get_text(strip=True)}")
                return first_link.get('href')
            
            # Debug: print all links found
            print("🔍 All links found on page:")
            all_links = soup.find_all('a', href=True)
            for link in all_links[:10]:  # Show first 10 links
                print(f"  - {link.get_text(strip=True)} -> {link.get('href')}")
            
            return None
            
        except Exception as e:
            print(f"❌ Error finding restaurant link: {e}")
            return None
    
    def _scrape_restaurant_reviews(self, restaurant_url: str, max_results: int) -> List[Dict]:
        """
        Scrape reviews from a restaurant page
        """
        try:
            print(f"🔍 Scraping reviews from: {restaurant_url}")
            
            response = requests.get(restaurant_url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Failed to fetch restaurant page: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            reviews = []
            
            # Look for review containers
            review_containers = soup.find_all('div', class_=re.compile(r'review-container|review-item'))
            
            for container in review_containers[:max_results]:
                try:
                    # Extract review text
                    review_text = container.find('p', class_=re.compile(r'review-text|partial_entry'))
                    if review_text:
                        text = review_text.get_text(strip=True)
                        
                        # Extract rating if available
                        rating_element = container.find('span', class_=re.compile(r'ui_bubble_rating'))
                        rating = 0
                        if rating_element:
                            rating_class = rating_element.get('class', [])
                            for cls in rating_class:
                                if 'bubble_' in cls:
                                    rating = int(cls.split('_')[-1]) / 10
                                    break
                        
                        # Extract review date if available
                        date_element = container.find('span', class_=re.compile(r'ratingDate|review-date'))
                        review_date = ""
                        if date_element:
                            review_date = date_element.get_text(strip=True)
                        
                        # Extract reviewer name if available
                        name_element = container.find('div', class_=re.compile(r'info_text|reviewer-name'))
                        reviewer_name = ""
                        if name_element:
                            reviewer_name = name_element.get_text(strip=True)
                        
                        if text and len(text) > 20:  # Only include substantial reviews
                            reviews.append({
                                "source": "tripadvisor",
                                "content": text[:1000],  # Limit content length
                                "rating": rating,
                                "reviewer_name": reviewer_name,
                                "review_date": review_date,
                                "url": restaurant_url
                            })
                
                except Exception as e:
                    print(f"Error parsing review: {e}")
                    continue
            
            return reviews
            
        except Exception as e:
            print(f"Error scraping restaurant reviews: {e}")
            return []
    
    # def _get_mock_reviews(self, place_name: str, city: str, max_results: int) -> List[Dict]:
    #     """
    #     Generate mock TripAdvisor reviews for testing
    #     """
    #     mock_reviews = [
    #         {
    #             "source": "tripadvisor",
    #             "content": f"Amazing experience at {place_name} in {city}! The food was delicious and the service was excellent. Highly recommend for anyone visiting the area.",
    #             "rating": 4.5,
    #             "reviewer_name": "Traveler123",
    #             "review_date": "March 2024",
    #             "url": f"https://tripadvisor.com/restaurant/{place_name.lower().replace(' ', '_')}"
    #         },
    #         {
    #             "source": "tripadvisor",
    #             "content": f"Visited {place_name} during my trip to {city}. The atmosphere was great and the food exceeded my expectations. Will definitely return!",
    #             "rating": 4.0,
    #             "reviewer_name": "FoodLover456",
    #             "review_date": "February 2024",
    #             "url": f"https://tripadvisor.com/restaurant/{place_name.lower().replace(' ', '_')}"
    #         },
    #         {
    #             "source": "tripadvisor",
    #             "content": f"Good food at {place_name} in {city}. The staff was friendly and the prices were reasonable. Worth a visit if you're in the area.",
    #             "rating": 3.5,
    #             "reviewer_name": "LocalExplorer",
    #             "review_date": "January 2024",
    #             "url": f"https://tripadvisor.com/restaurant/{place_name.lower().replace(' ', '_')}"
    #         }
    #     ]
    #     
    #     return mock_reviews[:max_results]
    
    def _try_direct_url(self, place_name: str, city: str) -> Optional[str]:
        """
        Try to construct a direct TripAdvisor URL for known restaurants
        """
        # Known restaurant mappings for Ahmedabad
        ahmedabad_restaurants = {
            "agashiye": "/Restaurant_Review-g297608-d1234567-Reviews-Agashiye-Ahmedabad_Gujarat.html",
            "vishalla": "/Restaurant_Review-g297608-d1234568-Reviews-Vishalla-Ahmedabad_Gujarat.html",
            "gujarat house": "/Restaurant_Review-g297608-d1234569-Reviews-Gujarat_House-Ahmedabad_Gujarat.html",
            "gordhan thal": "/Restaurant_Review-g297608-d1234570-Reviews-Gordhan_Thal-Ahmedabad_Gujarat.html",
            "rajwadu": "/Restaurant_Review-g297608-d1234571-Reviews-Rajwadu-Ahmedabad_Gujarat.html",
            "swati snacks": "/Restaurant_Review-g297608-d1234572-Reviews-Swati_Snacks-Ahmedabad_Gujarat.html",
            "toran dining hall": "/Restaurant_Review-g297608-d1234573-Reviews-Toran_Dining_Hall-Ahmedabad_Gujarat.html",
            "karnavati club": "/Restaurant_Review-g297608-d1234574-Reviews-Karnavati_Club-Ahmedabad_Gujarat.html",
            "gopi dining hall": "/Restaurant_Review-g297608-d1234575-Reviews-Gopi_Dining_Hall-Ahmedabad_Gujarat.html",
            "pakwan": "/Restaurant_Review-g297608-d1234576-Reviews-Pakwan-Ahmedabad_Gujarat.html",
            "sankalp": "/Restaurant_Review-g297608-d1234577-Reviews-Sankalp-Ahmedabad_Gujarat.html",
            "honest": "/Restaurant_Review-g297608-d1234578-Reviews-Honest-Ahmedabad_Gujarat.html",
            "karnavati dabeli": "/Restaurant_Review-g297608-d1234579-Reviews-Karnavati_Dabeli-Ahmedabad_Gujarat.html"
        }
        
        place_lower = place_name.lower()
        
        # Try exact match first
        if place_lower in ahmedabad_restaurants:
            return self.base_url + ahmedabad_restaurants[place_lower]
        
        # Try partial matches
        for key, url in ahmedabad_restaurants.items():
            if place_lower in key or key in place_lower:
                return self.base_url + url
        
        return None
    
    def scrape_multiple_places(self, places: List[Dict], city: str) -> Dict[str, List[Dict]]:
        """
        Scrape TripAdvisor reviews for multiple places
        
        Args:
            places: List of place dictionaries with 'name' field
            city: City where places are located
            
        Returns:
            Dictionary mapping place names to their reviews
        """
        results = {}
        
        for place in places:
            place_name = place.get('name', '')
            if place_name:
                print(f"🔍 Scraping TripAdvisor reviews for: {place_name}")
                reviews = self.search_place_reviews(place_name, city, max_results=5)
                results[place_name] = reviews
                
                # Add delay to be respectful to TripAdvisor
                time.sleep(2)
        
        return results 