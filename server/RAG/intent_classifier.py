import logging
from typing import Dict, Any, Optional
from .openrouter_client import openrouter_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntentClassifier:
    def __init__(self):
        self.client = openrouter_client
    
    def classify_intent(self, user_query: str) -> Dict[str, Any]:
        """
        Classify user intent as either 'place_search', 'place_detail', or 'simple_response'
        
        Args:
            user_query: The user's input query
            
        Returns:
            Dictionary with intent classification and structured data
        """
        try:
            prompt = f"""
You are an intent classifier for a place discovery system. Analyze the user query and determine the intent.

User Query: "{user_query}"

Classify the intent as either:
1. "place_search" - User wants to search for places (e.g., "coffee shops in Delhi", "restaurants near me", "parks in Mumbai")
2. "place_detail" - User wants details about a specific place (e.g., "tell me about Starbucks", "what's at Central Park", "info about Joe's Pizza")
3. "simple_response" - User wants a simple text response (e.g., "hello", "how are you", "what can you do")

Respond with a JSON object in this exact format:
{{
    "intent": "place_search" or "place_detail" or "simple_response",
    "confidence": 0.0-1.0,
    "extracted_data": {{
        "place_name": "specific place name if mentioned",
        "city": "city name if mentioned", 
        "category": "restaurant/coffee/park/etc if mentioned",
        "vibe_tags": ["tag1", "tag2"] if mentioned,
        "search_terms": ["term1", "term2"] for place_search,
        "response_text": "simple response text for simple_response"
    }}
}}

Examples:
- "coffee shops in Delhi" → place_search with city=Delhi, category=coffee
- "tell me about Starbucks" → place_detail with place_name=Starbucks
- "hello" → simple_response with response_text="Hello! How can I help you find places today?"
- "what can you do" → simple_response with response_text="I can help you search for places and get details about specific locations!"
"""

            response = self.client.generate_json(prompt)
            
            # Try to parse JSON response
            import json
            try:
                result = response
                logger.info(f"Intent classification: {result.get('intent')} (confidence: {result.get('confidence', 0)})")
                return result
            except Exception as e:
                logger.error(f"Failed to parse JSON response: {e}")
                # Fallback classification
                return self._fallback_classification(user_query)
                
        except Exception as e:
            logger.error(f"Error in intent classification: {e}")
            return self._fallback_classification(user_query)
    
    def _fallback_classification(self, user_query: str) -> Dict[str, Any]:
        """
        Fallback classification using simple keyword matching
        """
        query_lower = user_query.lower()
        
        # Keywords that suggest simple_response intent
        simple_keywords = ['hello', 'hi', 'hey', 'how are you', 'what can you do', 'help', 'thanks', 'thank you']
        
        # Keywords that suggest place_detail intent
        detail_keywords = ['tell me about', 'what is', 'what\'s at', 'info about', 'details of', 'about']
        
        # Keywords that suggest place_search intent  
        search_keywords = ['find', 'search', 'near me', 'in', 'around', 'coffee', 'restaurant', 'park', 'shop']
        
        # Check for simple_response keywords first
        for keyword in simple_keywords:
            if keyword in query_lower:
                return {
                    "intent": "simple_response",
                    "confidence": 0.8,
                    "extracted_data": {
                        "place_name": None,
                        "city": None,
                        "category": None,
                        "vibe_tags": [],
                        "search_terms": [],
                        "response_text": self._generate_simple_response(user_query)
                    }
                }
        
        # Check for place_detail keywords
        for keyword in detail_keywords:
            if keyword in query_lower:
                return {
                    "intent": "place_detail",
                    "confidence": 0.7,
                    "extracted_data": {
                        "place_name": self._extract_place_name(user_query),
                        "city": None,
                        "category": None,
                        "vibe_tags": [],
                        "search_terms": []
                    }
                }
        
        # Default to place_search
        return {
            "intent": "place_search", 
            "confidence": 0.6,
            "extracted_data": {
                "place_name": None,
                "city": self._extract_city(user_query),
                "category": self._extract_category(user_query),
                "vibe_tags": [],
                "search_terms": user_query.split()
            }
        }
    
    def _generate_simple_response(self, query: str) -> str:
        """Generate a simple response based on the query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! How can I help you find places today?"
        elif any(word in query_lower for word in ['how are you']):
            return "I'm doing great! Ready to help you discover amazing places. What are you looking for?"
        elif any(word in query_lower for word in ['what can you do', 'help']):
            return "I can help you search for places and get details about specific locations! Try asking me to find coffee shops in Delhi or tell me about a specific place."
        elif any(word in query_lower for word in ['thanks', 'thank you']):
            return "You're welcome! Let me know if you need help finding more places."
        else:
            return "I'm here to help you discover places! You can ask me to search for places or get details about specific locations."
    
    def _extract_place_name(self, query: str) -> Optional[str]:
        """Extract place name from query"""
        # Simple extraction - could be enhanced
        words = query.split()
        if len(words) >= 3:
            # Look for capitalized words that might be place names
            for i, word in enumerate(words):
                if word[0].isupper() and i > 0:
                    return word
        return None
    
    def _extract_city(self, query: str) -> Optional[str]:
        """Extract city name from query"""
        cities = ['delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata', 'hyderabad', 'pune', 'ahmedabad']
        query_lower = query.lower()
        for city in cities:
            if city in query_lower:
                return city.title()
        return None
    
    def _extract_category(self, query: str) -> Optional[str]:
        """Extract category from query"""
        categories = {
            'coffee': ['coffee', 'cafe', 'starbucks'],
            'restaurant': ['restaurant', 'food', 'dining', 'eat'],
            'park': ['park', 'garden', 'outdoor'],
            'bar': ['bar', 'pub', 'nightlife'],
            'shopping': ['mall', 'shop', 'store', 'shopping']
        }
        
        query_lower = query.lower()
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return category
        return None 