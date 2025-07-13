import logging
from typing import Dict, Any, List, Optional
from .intent_classifier import IntentClassifier
from .llm_processor import LLMProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NOTE: OpenRouter is disabled for frontend testing - using rule-based processing only

class FlowController:
    def __init__(self, mongo=None):
        self.intent_classifier = IntentClassifier()
        self.llm_processor = LLMProcessor()
        self.mongo = mongo
        self._fallback_service = None
    
    @property
    def fallback_service(self):
        if self._fallback_service is None:
            from services.fallback_service import FallbackService
            self._fallback_service = FallbackService(self.mongo)
        return self._fallback_service
    
    def process_query(self, user_query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point for processing user queries
        
        Args:
            user_query: The user's input query
            user_id: Optional user ID for personalized responses
            
        Returns:
            Dictionary with response data and metadata
        """
        try:
            logger.info(f"Processing query: {user_query}")
            
            # Step 1: Classify intent
            intent_result = self.intent_classifier.classify_intent(user_query)
            intent = intent_result.get('intent')
            confidence = intent_result.get('confidence', 0)
            extracted_data = intent_result.get('extracted_data', {})
            
            logger.info(f"Intent classified as: {intent} (confidence: {confidence})")
            
            # Step 2: Route based on intent
            if intent == "place_search":
                return self._handle_place_search(extracted_data, user_id, confidence)
            elif intent == "place_detail":
                return self._handle_place_detail(extracted_data, user_id, confidence)
            elif intent == "simple_response":
                return self._handle_simple_response(extracted_data, user_id, confidence)
            else:
                return self._handle_unknown_intent(user_query)
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "success": False,
                "error": "Failed to process query",
                "response": "I'm sorry, I couldn't understand your request. Please try again."
            }
    
    def _handle_place_search(self, extracted_data: Dict[str, Any], user_id: Optional[str], confidence: float = 0) -> Dict[str, Any]:
        """
        Handle place_search intent - search for places based on criteria
        """
        try:
            city = extracted_data.get('city', 'Delhi')  # Default to Delhi
            category = extracted_data.get('category')
            vibe_tags = extracted_data.get('vibe_tags', [])
            search_terms = extracted_data.get('search_terms', [])
            
            logger.info(f"Searching places in {city}, category: {category}")
            
            # Use fallback service to search for places
            if not self.fallback_service:
                return {
                    "success": False,
                    "error": "Fallback service not available",
                    "response": "Search service is not available right now."
                }
            
            search_result = self.fallback_service.search_places_with_fallback(
                city=city,
                category=category or "restaurant",  # Default category
                vibe_tags=vibe_tags,
                min_results=5
            )
            
            search_results = search_result.get('places', [])
            
            if not search_results:
                return {
                    "success": True,
                    "intent": "place_search",
                    "response": f"I couldn't find any places matching your criteria in {city}. Try different search terms or location.",
                    "places": [],
                    "metadata": {
                        "city": city,
                        "category": category,
                        "results_count": 0
                    }
                }
            
            # Process places with LLM for enrichment (only if not already processed)
            enriched_places = []
            for place in search_results:
                try:
                    # Check if place already has processed data
                    processed_data = place.get('processed', {})
                    has_vibe_tags = processed_data.get('vibe_tags', [])
                    has_summary = processed_data.get('summary', '')
                    
                    if has_vibe_tags and has_summary:
                        # Place already has LLM processing, use existing data
                        logger.info(f"✅ Place {place.get('name')} already has processed data, skipping LLM")
                        enriched_place = {
                            'name': place.get('name', ''),
                            'category': place.get('category', ''),
                            'vibe_tags': has_vibe_tags,
                            'emojis': processed_data.get('emojis', []),
                            'summary': has_summary,
                            'reviews': place.get('reviews', [])
                        }
                    else:
                        # Place needs LLM processing
                        logger.info(f"🧠 Processing place {place.get('name')} with LLM")
                        enriched_place = self.llm_processor.process_place_reviews(
                            place_name=place.get('name', ''),
                            place_category=place.get('category', ''),
                            reviews=place.get('reviews', [])
                        )
                        # Add place name and category to enriched data
                        enriched_place['name'] = place.get('name', '')
                        enriched_place['category'] = place.get('category', '')
                        enriched_place['reviews'] = place.get('reviews', [])
                    
                    enriched_places.append(enriched_place)
                except Exception as e:
                    logger.error(f"Error enriching place {place.get('name')}: {e}")
                    enriched_places.append(place)  # Use original if enrichment fails
            
            return {
                "success": True,
                "intent": "place_search",
                "response": f"I found {len(enriched_places)} places in {city} that match your criteria.",
                "places": enriched_places,
                "metadata": {
                    "city": city,
                    "category": category,
                    "results_count": len(enriched_places),
                    "confidence": confidence
                }
            }
            
        except Exception as e:
            logger.error(f"Error in place search: {e}")
            return {
                "success": False,
                "error": "Failed to search for places",
                "response": "I'm sorry, I couldn't search for places right now. Please try again later."
            }
    
    def _handle_place_detail(self, extracted_data: Dict[str, Any], user_id: Optional[str], confidence: float = 0) -> Dict[str, Any]:
        """
        Handle place_detail intent - get detailed information about a specific place
        """
        try:
            place_name = extracted_data.get('place_name')
            
            if not place_name:
                return {
                    "success": False,
                    "error": "No place name provided",
                    "response": "Please specify which place you'd like to know more about."
                }
            
            logger.info(f"Getting details for place: {place_name}")
            
            # Search for the specific place
            if not self.fallback_service:
                return {
                    "success": False,
                    "error": "Fallback service not available",
                    "response": "Search service is not available right now."
                }
            
            place_result = self.fallback_service.search_places_with_fallback(
                city="Delhi",  # Could be enhanced to detect city
                category="restaurant",  # Default category
                vibe_tags=[],
                min_results=1
            )
            
            place_results = place_result.get('places', [])
            
            if not place_results:
                return {
                    "success": True,
                    "intent": "place_detail",
                    "response": f"I couldn't find any information about {place_name}. Please check the spelling or try a different place.",
                    "place": None,
                    "metadata": {
                        "place_name": place_name,
                        "found": False
                    }
                }
            
            # Get the first (most relevant) result
            place = place_results[0]
            
            # Check if place already has processed data
            processed_data = place.get('processed', {})
            has_vibe_tags = processed_data.get('vibe_tags', [])
            has_summary = processed_data.get('summary', '')
            
            if has_vibe_tags and has_summary:
                # Place already has LLM processing, use existing data
                logger.info(f"✅ Place {place.get('name')} already has processed data, skipping LLM")
                enriched_place = {
                    'name': place.get('name', ''),
                    'category': place.get('category', ''),
                    'vibe_tags': has_vibe_tags,
                    'emojis': processed_data.get('emojis', []),
                    'summary': has_summary,
                    'reviews': place.get('reviews', [])
                }
            else:
                # Place needs LLM processing
                logger.info(f"🧠 Processing place {place.get('name')} with LLM")
                try:
                    enriched_place = self.llm_processor.process_place_reviews(
                        place_name=place.get('name', ''),
                        place_category=place.get('category', ''),
                        reviews=place.get('reviews', [])
                    )
                    # Add place name and category to enriched data
                    enriched_place['name'] = place.get('name', '')
                    enriched_place['category'] = place.get('category', '')
                    enriched_place['reviews'] = place.get('reviews', [])
                except Exception as e:
                    logger.error(f"Error enriching place details: {e}")
                    enriched_place = place
            
            # Generate a summary response
            summary = self._generate_place_summary(enriched_place)
            
            return {
                "success": True,
                "intent": "place_detail",
                "response": summary,
                "place": enriched_place,
                "metadata": {
                    "place_name": place_name,
                    "found": True,
                    "confidence": confidence
                }
            }
            
        except Exception as e:
            logger.error(f"Error in place detail: {e}")
            return {
                "success": False,
                "error": "Failed to get place details",
                "response": "I'm sorry, I couldn't get details for that place right now. Please try again later."
            }
    
    def _handle_simple_response(self, extracted_data: Dict[str, Any], user_id: Optional[str], confidence: float = 0) -> Dict[str, Any]:
        """
        Handle simple_response intent - return a basic text response
        """
        try:
            response_text = extracted_data.get('response_text', 'Hello! How can I help you find places today?')
            
            return {
                "success": True,
                "intent": "simple_response",
                "response": response_text,
                "places": [],
                "metadata": {
                    "confidence": confidence,
                    "response_type": "simple_text"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in simple response: {e}")
            return {
                "success": False,
                "error": "Failed to generate simple response",
                "response": "Hello! How can I help you find places today?"
            }
    
    def _handle_unknown_intent(self, user_query: str) -> Dict[str, Any]:
        """
        Handle unknown or unclear intent
        """
        return {
            "success": False,
            "error": "Unknown intent",
            "response": "I'm not sure what you're looking for. You can ask me to search for places (like 'coffee shops in Delhi') or get details about a specific place (like 'tell me about Starbucks')."
        }
    
    def _generate_place_summary(self, place: Dict[str, Any]) -> str:
        """
        Generate a natural language summary of a place
        """
        name = place.get('name', 'This place')
        category = place.get('category', 'place')
        vibe_tags = place.get('vibe_tags', [])
        emojis = place.get('emojis', [])
        
        summary_parts = [f"Here's what I found about {name}:"]
        
        if category:
            summary_parts.append(f"It's a {category}.")
        
        if vibe_tags:
            vibe_text = ", ".join(vibe_tags)
            summary_parts.append(f"The vibe is: {vibe_text}.")
        
        if emojis:
            emoji_text = " ".join(emojis)
            summary_parts.append(f"Represented by: {emoji_text}")
        
        # Add review summary if available
        reviews = place.get('reviews', [])
        if reviews:
            summary_parts.append(f"It has {len(reviews)} reviews from various sources.")
        
        return " ".join(summary_parts) 