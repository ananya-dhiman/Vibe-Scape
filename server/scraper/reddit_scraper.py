import requests
import json
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import quote_plus
from .review_refiner import create_review_refiner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedditScraper:
    def __init__(self, use_llm_refinement: bool = False, max_iterations: int = 2, min_relevant_reviews: int = 3):
        self.base_url = "https://www.reddit.com/search.json"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.use_llm_refinement = use_llm_refinement
        if use_llm_refinement:
            self.review_refiner = create_review_refiner(max_iterations=max_iterations, min_relevant_reviews=min_relevant_reviews)
    
    def search_place_reviews(self, place_name: str, city: str, max_results: int = 5) -> List[Dict]:
        """
        Search Reddit for reviews about a specific place in a city
        
        Args:
            place_name: Name of the place to search for
            city: City where the place is located
            max_results: Maximum number of reviews to return
            
        Returns:
            List of review dictionaries with source and content
        """
        try:
            # Construct search query
            search_query = f'"{place_name}" "{city}" review'
            encoded_query = quote_plus(search_query)
            
            # Reddit search URL
            url = f"{self.base_url}?q={encoded_query}&sort=relevance&t=all&limit={max_results}"
            
            print(f"🔍 Searching Reddit for: {search_query}")
            print(f"URL: {url}")
            
            # Make request to Reddit
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Reddit API returned status {response.status_code}")
                return self._get_mock_reviews(place_name, city, max_results)
            
            data = response.json()
            
            # Extract posts from Reddit response
            reviews = []
            if 'data' in data and 'children' in data['data']:
                for post in data['data']['children']:
                    post_data = post.get('data', {})
                    
                    # Extract post content
                    title = post_data.get('title', '')
                    selftext = post_data.get('selftext', '')
                    url = post_data.get('url', '')
                    
                    # Combine title and text for content
                    content = f"{title}\n\n{selftext}".strip()
                    
                    if content and len(content) > 50:  # Only include substantial content
                        reviews.append({
                            "source": "reddit",
                            "content": content[:1000],  # Limit content length
                            "url": url,
                            "score": post_data.get('score', 0),
                            "created_utc": post_data.get('created_utc', 0)
                        })
            
            # If no real reviews found, use mock data
            if not reviews:
                print("⚠️ No Reddit reviews found, using mock data")
                return self._get_mock_reviews(place_name, city, max_results)
            
            # Sort by score and limit results
            reviews.sort(key=lambda x: x.get('score', 0), reverse=True)
            reviews = reviews[:max_results]
            
            print(f"✅ Found {len(reviews)} Reddit reviews for {place_name}")
            
            # Apply LLM refinement if enabled
            if self.use_llm_refinement and reviews:
                logger.info(f"Applying LLM refinement to {len(reviews)} reviews for {place_name}")
                refined_reviews = self._refine_reviews_with_llm(reviews, place_name, city)
                return refined_reviews
            
            return reviews
            
        except Exception as e:
            print(f"❌ Error scraping Reddit: {e}")
            return self._get_mock_reviews(place_name, city, max_results)
    
    def _get_mock_reviews(self, place_name: str, city: str, max_results: int) -> List[Dict]:
        """
        Generate mock Reddit reviews for testing
        """
        mock_reviews = [
            {
                "source": "reddit",
                "content": f"Just visited {place_name} in {city} and it was amazing! The atmosphere is perfect for studying and the coffee is top-notch. Highly recommend for anyone looking for a cozy spot.",
                "url": "https://reddit.com/r/delhi/comments/mock1",
                "score": 45,
                "created_utc": 1640995200
            },
            {
                "source": "reddit", 
                "content": f"Been to {place_name} multiple times now. The staff is super friendly and the food quality is consistently good. Great place to hang out with friends in {city}.",
                "url": "https://reddit.com/r/delhi/comments/mock2",
                "score": 32,
                "created_utc": 1640995200
            },
            {
                "source": "reddit",
                "content": f"Honest review of {place_name}: The location is convenient and the prices are reasonable for {city}. However, it can get quite crowded during peak hours.",
                "url": "https://reddit.com/r/delhi/comments/mock3", 
                "score": 28,
                "created_utc": 1640995200
            }
        ]
        
        return mock_reviews[:max_results]
    
    def _fetch_more_reviews(self, place_name: str, city: str, max_results: int = 10) -> List[Dict]:
        """
        Fetch additional reviews with different search strategies.
        """
        try:
            # Try different search strategies
            search_variations = [
                f'"{place_name}" review',
                f'"{place_name}" {city}',
                f'{place_name} experience',
                f'{place_name} visit'
            ]
            
            all_reviews = []
            
            for search_query in search_variations:
                encoded_query = quote_plus(search_query)
                url = f"{self.base_url}?q={encoded_query}&sort=relevance&t=all&limit={max_results}"
                
                logger.info(f"Fetching more reviews with query: {search_query}")
                
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'data' in data and 'children' in data['data']:
                        for post in data['data']['children']:
                            post_data = post.get('data', {})
                            
                            title = post_data.get('title', '')
                            selftext = post_data.get('selftext', '')
                            url = post_data.get('url', '')
                            
                            content = f"{title}\n\n{selftext}".strip()
                            
                            if content and len(content) > 50:
                                review_dict = {
                                    "source": "reddit",
                                    "content": content[:1000],
                                    "url": url,
                                    "score": post_data.get('score', 0),
                                    "created_utc": post_data.get('created_utc', 0)
                                }
                                
                                # Avoid duplicates
                                if not any(r.get('content') == content for r in all_reviews):
                                    all_reviews.append(review_dict)
                
                time.sleep(1)  # Be respectful to Reddit
            
            logger.info(f"Fetched {len(all_reviews)} additional reviews")
            return all_reviews
            
        except Exception as e:
            logger.error(f"Error fetching more reviews: {e}")
            return []
    
    def _refine_reviews_with_llm(self, reviews: List[Dict], place_name: str, city: str) -> List[Dict]:
        """
        Use LLM to refine and filter reviews for relevance.
        """
        if not self.use_llm_refinement or not self.review_refiner:
            return reviews
        
        # Extract review content for LLM processing
        review_contents = [review.get('content', '') for review in reviews]
        
        # Use the review refiner to filter relevant reviews
        relevant_contents = self.review_refiner.refine_reviews_with_llm(
            initial_reviews=review_contents,
            place_name=place_name,
            place_type="place",  # Could be enhanced to detect place type
            fetch_more_reviews_func=self._fetch_more_reviews,
            city=city
        )
        
        # Map back to original review dictionaries
        refined_reviews = []
        for content in relevant_contents:
            # Find the original review dict that matches this content
            for review in reviews:
                if review.get('content', '') == content:
                    refined_reviews.append(review)
                    break
        
        logger.info(f"LLM refinement: {len(reviews)} -> {len(refined_reviews)} relevant reviews")
        return refined_reviews
    
    def scrape_multiple_places(self, places: List[Dict], city: str) -> Dict[str, List[Dict]]:
        """
        Scrape Reddit reviews for multiple places
        
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
                print(f"🔍 Scraping Reddit reviews for: {place_name}")
                reviews = self.search_place_reviews(place_name, city, max_results=5)
                results[place_name] = reviews
                
                # Add small delay to be respectful to Reddit
                time.sleep(1)
        
        return results 