from typing import List, Dict, Optional
from flask_pymongo import PyMongo
from services.tomtom_service import TomTomService
from RAG.llm_processor import LLMProcessor
from scraper.reddit_scraper import RedditScraper
from scraper.tripadvisor_scraper import TripAdvisorScraper
from controllers.place_controller import bulk_insert_places
from datetime import datetime, timezone

class FallbackService:
    def __init__(self, mongo: PyMongo):
        self.mongo = mongo
        self.tomtom_service = TomTomService()
        self.llm_processor = LLMProcessor()
        self.reddit_scraper = RedditScraper()
        self.tripadvisor_scraper = TripAdvisorScraper()
    
    def search_places_with_fallback(self, city: str, category: str, vibe_tags: List[str], min_results: int = 5) -> Dict:
        """
        Search for places with fallback logic:
        1. First check existing database for matches
        2. If < min_results, fetch from TomTom and scrape Reddit reviews
        3. Store new places with reviews in database
        
        Args:
            city: City to search in
            category: Category to search for (e.g., "cafe")
            vibe_tags: List of vibe tags to match
            min_results: Minimum number of results required
            
        Returns:
            Dictionary with search results and status
        """
        try:
            print(f"🔍 Searching for {category} places in {city} with vibe tags: {vibe_tags}")
            
            # Step 1: Search existing database
            existing_places = self._search_existing_places(city, category, vibe_tags)
            print(f"📊 Found {len(existing_places)} existing places matching criteria")
            
            # If we have enough results, return them
            if len(existing_places) >= min_results:
                print(f"✅ Found {len(existing_places)} places (≥ {min_results}), returning existing results")
                return {
                    "success": True,
                    "source": "database",
                    "places": existing_places,
                    "count": len(existing_places),
                    "fallback_used": False
                }
            
            # Step 2: Fetch additional places from TomTom
            print(f"⚠️ Only {len(existing_places)} places found, fetching from TomTom...")
            tomtom_places = self._fetch_tomtom_places(city, category, min_results - len(existing_places))
            
            if not tomtom_places:
                print("❌ No TomTom places found")
                return {
                    "success": True,
                    "source": "database_only",
                    "places": existing_places,
                    "count": len(existing_places),
                    "fallback_used": False
                }
            
            # Step 3: Scrape Reddit reviews for TomTom places (TripAdvisor temporarily disabled)
            print(f"🔍 Scraping Reddit reviews for {len(tomtom_places)} TomTom places...")
            reddit_reviews = self.reddit_scraper.scrape_multiple_places(tomtom_places, city)
            
            # TripAdvisor scraping temporarily disabled due to blocking issues
            print(f"⚠️ TripAdvisor scraping temporarily disabled")
            tripadvisor_reviews = {}
            
            # Step 4: Process reviews with LLM to extract vibe tags, summaries, and emojis
            print(f"🧠 Processing reviews with LLM...")
            processed_data = self.llm_processor.process_multiple_places(reddit_reviews, city)
            print(f"📊 LLM processed data keys: {list(processed_data.keys())}")
            for place_name, data in processed_data.items():
                print(f"   {place_name}: {len(data.get('vibe_tags', []))} tags, {len(data.get('emojis', []))} emojis")
            
            # Step 5: Transform and store places with reviews and LLM processing
            places_with_reviews = self._transform_and_store_places_with_llm(tomtom_places, reddit_reviews, processed_data)
            
            # Step 5: Combine existing and new places
            all_places = existing_places + places_with_reviews
            
            print(f"✅ Total places after fallback: {len(all_places)}")
            
            return {
                "success": True,
                "source": "database_and_tomtom",
                "places": all_places,
                "count": len(all_places),
                "fallback_used": True,
                "tomtom_fetched": len(tomtom_places),
                "reddit_reviews_scraped": len(reddit_reviews),
                "tripadvisor_reviews_scraped": 0  # Temporarily disabled
            }
            
        except Exception as e:
            print(f"❌ Error in fallback service: {e}")
            return {
                "success": False,
                "error": str(e),
                "places": [],
                "count": 0
            }
    
    def _search_existing_places(self, city: str, category: str, vibe_tags: List[str]) -> List[Dict]:
        """
        Search existing database for places matching criteria
        """
        if not self.mongo or self.mongo.db is None:
            print("⚠️ MongoDB connection not available")
            return []
            
        query = {
            "original.city": city,
            "original.category": {"$regex": category, "$options": "i"}
        }
        
        # Add vibe tags filter if provided
        if vibe_tags:
            query["processed.vibe_tags"] = {"$in": vibe_tags}
        
        places = list(self.mongo.db.places.find(query))
        
        # Convert ObjectIds to strings for JSON serialization
        for place in places:
            if '_id' in place:
                place['_id'] = str(place['_id'])
        
        return places
    
    def _fetch_tomtom_places(self, city: str, category: str, limit: int) -> List[Dict]:
        """
        Fetch places from TomTom API
        """
        try:
            # Map category to TomTom search query
            search_query = self._map_category_to_query(category)
            
            places = self.tomtom_service.search_places(search_query, city, limit)
            return places if places else []
            
        except Exception as e:
            print(f"❌ Error fetching TomTom places: {e}")
            return []
    
    def _combine_reviews(self, reddit_reviews: Dict[str, List[Dict]], tripadvisor_reviews: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """
        Combine reviews from Reddit and TripAdvisor sources
        """
        combined_reviews = {}
        
        # Get all unique place names
        all_places = set(reddit_reviews.keys()) | set(tripadvisor_reviews.keys())
        
        for place_name in all_places:
            combined_reviews[place_name] = []
            
            # Add Reddit reviews
            if place_name in reddit_reviews:
                combined_reviews[place_name].extend(reddit_reviews[place_name])
            
            # Add TripAdvisor reviews
            if place_name in tripadvisor_reviews:
                combined_reviews[place_name].extend(tripadvisor_reviews[place_name])
        
        return combined_reviews
    
    def _map_category_to_query(self, category: str) -> str:
        """
        Map our category to TomTom search query
        """
        category_mapping = {
            "cafe": "cafe coffee",
            "restaurant": "restaurant food",
            "park": "park",
            "bar": "bar pub",
            "museum": "museum",
            "shopping": "shopping mall",
            "gym": "gym fitness",
            "library": "library",
            "theater": "theater cinema"
        }
        
        return category_mapping.get(category.lower(), category)
    
    def _transform_and_store_places_with_llm(self, tomtom_places: List[Dict], reddit_reviews: Dict[str, List[Dict]], processed_data: Dict[str, Dict]) -> List[Dict]:
        """
        Transform TomTom places and store them with Reddit reviews and LLM processing
        """
        places_to_insert = []
        
        for place in tomtom_places:
            place_name = place.get("name", "")
            reviews = reddit_reviews.get(place_name, [])
            
            # Get LLM processed data for this place
            llm_data = processed_data.get(place_name, {})
            
            # Transform to our database schema with LLM processing
            place_doc = {
                "original": {
                    "fsq_id": place.get("fsq_id", ""),
                    "name": place_name,
                    "category": place.get("category", ""),
                    "address": place.get("address", ""),
                    "locality": place.get("locality", ""),
                    "city": place.get("city", ""),
                    "country": place.get("country", ""),
                    "photo_url": place.get("photo_url", ""),
                    "coordinates": place.get("coordinates", {})
                },
                "processed": {
                    "vibe_tags": llm_data.get("vibe_tags", []), 
                    "emojis": llm_data.get("emojis", []),     
                    "summary": llm_data.get("summary", ""),    
                    "citations": []   
                },
                "reviews": reviews,  # Reddit reviews
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            places_to_insert.append(place_doc)
        
        # Store in database using bulk insert
        if places_to_insert:
            inserted_ids = bulk_insert_places(self.mongo, places_to_insert)
            print(f"💾 Stored {len(inserted_ids)} new places with Reddit reviews and LLM processing")
            
            # Return the stored places (without ObjectIds for JSON serialization)
            stored_places = []
            for place in places_to_insert:
                place_copy = place.copy()
                # Remove MongoDB-specific fields for response
                place_copy.pop('_id', None)
                stored_places.append(place_copy)
            
            return stored_places
        
        return []
    
    def _transform_and_store_places(self, tomtom_places: List[Dict], reddit_reviews: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Transform TomTom places and store them with Reddit reviews (legacy method)
        """
        places_to_insert = []
        
        for place in tomtom_places:
            place_name = place.get("name", "")
            reviews = reddit_reviews.get(place_name, [])
            
            # Transform to our database schema
            place_doc = {
                "original": {
                    "fsq_id": place.get("fsq_id", ""),
                    "name": place_name,
                    "category": place.get("category", ""),
                    "address": place.get("address", ""),
                    "locality": place.get("locality", ""),
                    "city": place.get("city", ""),
                    "country": place.get("country", ""),
                    "photo_url": place.get("photo_url", ""),
                    "coordinates": place.get("coordinates", {})
                },
                "processed": {
                    "vibe_tags": [], 
                    "emojis": [],     
                    "summary": "",    
                    "citations": []   
                },
                "reviews": reviews,  # Reddit reviews
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            places_to_insert.append(place_doc)
        
        # Store in database using bulk insert
        if places_to_insert:
            inserted_ids = bulk_insert_places(self.mongo, places_to_insert)
            print(f"💾 Stored {len(inserted_ids)} new places with Reddit reviews")
            
            # Return the stored places (without ObjectIds for JSON serialization)
            stored_places = []
            for place in places_to_insert:
                place_copy = place.copy()
                # Remove MongoDB-specific fields for response
                place_copy.pop('_id', None)
                stored_places.append(place_copy)
            
            return stored_places
        
        return [] 