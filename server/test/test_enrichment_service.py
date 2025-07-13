import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from services.fallback_service import FallbackService
from services.llm_processor import LLMProcessor

class TestFallbackServiceWithLLM(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_mongo = Mock()
        self.fallback_service = FallbackService(self.mock_mongo)
    
    def test_transform_and_store_places_with_llm(self):
        """Test transforming and storing places with LLM processing"""
        # Mock TomTom place data
        tomtom_places = [
            {
                "id": "test_id_123",
                "name": "Test Cafe",
                "category": "cafe",
                "address": "123 Test St",
                "locality": "Test City",
                "city": "Test City",
                "country": "Test Country",
                "coordinates": {"type": "Point", "coordinates": [77.2090, 28.6139]}
            }
        ]
        
        # Mock Reddit reviews
        reddit_reviews = {
            "Test Cafe": [
                {
                    "source": "reddit",
                    "content": "Great coffee and atmosphere!",
                    "url": "https://reddit.com/test"
                }
            ]
        }
        
        # Mock LLM processed data
        processed_data = {
            "Test Cafe": {
                "summary": "A cozy cafe with great coffee",
                "vibe_tags": ["cozy", "aesthetic", "quiet"],
                "emojis": ["☕", "🪑"]
            }
        }
        
        # Mock bulk_insert_places
        with patch('services.fallback_service.bulk_insert_places', return_value=["new_id"]):
            stored_places = self.fallback_service._transform_and_store_places_with_llm(
                tomtom_places, reddit_reviews, processed_data
            )
        
        # Assertions
        self.assertEqual(len(stored_places), 1)
        place = stored_places[0]
        self.assertEqual(place["original"]["name"], "Test Cafe")
        self.assertEqual(place["original"]["category"], "cafe")
        self.assertEqual(place["processed"]["vibe_tags"], ["cozy", "aesthetic", "quiet"])
        self.assertEqual(place["processed"]["emojis"], ["☕", "🪑"])
        self.assertEqual(place["processed"]["summary"], "A cozy cafe with great coffee")
        self.assertEqual(len(place["reviews"]), 1)
    
    def test_search_places_with_fallback_and_gemini_llm(self):
        """Test the complete search flow with Gemini LLM integration"""
        # Mock existing places
        mock_existing_places = [
            {"_id": "existing1", "original": {"name": "Existing Cafe", "city": "Delhi", "category": "cafe"}}
        ]
        
        # Mock TomTom places
        mock_tomtom_places = [
            {"name": "New Cafe", "id": "new1", "category": "cafe"}
        ]
        
        # Mock Reddit reviews
        mock_reddit_reviews = {
            "New Cafe": [
                {"source": "reddit", "content": "Great place!"}
            ]
        }
        
        # Mock Gemini LLM processed data
        mock_processed_data = {
            "New Cafe": {
                "summary": "A great cafe with cozy atmosphere",
                "vibe_tags": ["great", "cozy", "aesthetic"],
                "emojis": ["☕", "🪑"]
            }
        }
        
        # Mock the various service calls
        with patch.object(self.fallback_service, '_search_existing_places', return_value=mock_existing_places), \
             patch.object(self.fallback_service.tomtom_service, 'search_places', return_value=mock_tomtom_places), \
             patch.object(self.fallback_service.reddit_scraper, 'scrape_multiple_places', return_value=mock_reddit_reviews), \
             patch.object(self.fallback_service.llm_processor, 'process_multiple_places', return_value=mock_processed_data), \
             patch.object(self.fallback_service, '_transform_and_store_places_with_llm', return_value=[{"name": "New Cafe"}]):
            
            result = self.fallback_service.search_places_with_fallback(
                city="Delhi",
                category="cafe",
                vibe_tags=["cozy"],
                min_results=5
            )
            
            self.assertTrue(result["success"])
            self.assertEqual(result["source"], "database_and_tomtom")
            self.assertTrue(result["fallback_used"])
            self.assertIn("places", result)

class TestLLMProcessor(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.llm_processor = LLMProcessor()
    
    def test_infer_category_from_name(self):
        """Test category inference from place name"""
        # Test cafe detection
        self.assertEqual(self.llm_processor._infer_category_from_name("Starbucks"), "cafe")
        self.assertEqual(self.llm_processor._infer_category_from_name("Coffee House"), "cafe")
        
        # Test restaurant detection
        self.assertEqual(self.llm_processor._infer_category_from_name("McDonald's"), "restaurant")
        self.assertEqual(self.llm_processor._infer_category_from_name("Fine Dining"), "restaurant")
        
        # Test bar detection
        self.assertEqual(self.llm_processor._infer_category_from_name("The Pub"), "bar")
        
        # Test default
        self.assertEqual(self.llm_processor._infer_category_from_name("Random Place"), "place")
    
    def test_get_default_processing(self):
        """Test default processing when LLM fails"""
        result = self.llm_processor._get_default_processing("Test Place", "cafe")
        
        self.assertIn("summary", result)
        self.assertIn("vibe_tags", result)
        self.assertIn("emojis", result)
        self.assertEqual(result["vibe_tags"], ["mixed", "local", "accessible"])

if __name__ == '__main__':
    unittest.main() 