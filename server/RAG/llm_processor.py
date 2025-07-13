import json
from typing import List, Dict, Optional
from datetime import datetime
from .openrouter_client import openrouter_client

class LLMProcessor:
    def __init__(self):
        self.client = openrouter_client
        
    def process_place_reviews(self, place_name: str, place_category: str, reviews: List[Dict]) -> Dict:
        """
        Process reviews for a place to extract vibe tags, summary, and emojis
        
        Args:
            place_name: Name of the place
            place_category: Category of the place (e.g., 'cafe', 'restaurant')
            reviews: List of review dictionaries with 'content' field
            
        Returns:
            Dictionary with processed data: summary, vibe_tags, emojis
        """
        try:
            # Combine all reviews into a single text
            combined_reviews = "\n\n".join([review.get('content', '') for review in reviews])
            
            if not combined_reviews.strip():
                return self._get_default_processing(place_name, place_category)
            
            # Create prompt for LLM processing
            prompt = self._create_processing_prompt(place_name, place_category, combined_reviews)
            
            # Call OpenRouter API
            response = self.client.generate_content(prompt)
            
            # Parse the response
            result_text = response
            print(f"🔍 Raw OpenRouter response for {place_name}: {result_text[:200]}...")
            processed_data = self._parse_llm_response(result_text)
            
            print(f"✅ Processed {place_name}: {len(processed_data.get('vibe_tags', []))} vibe tags, {len(processed_data.get('emojis', []))} emojis")
            return processed_data
            
        except Exception as e:
            print(f"❌ Error processing reviews for {place_name}: {e}")
            
            # Try fallback with different temperature if OpenRouter fails
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                try:
                    print(f"🔄 Trying fallback with lower temperature for {place_name}")
                    response = self.client.generate_content(prompt, temperature=0.1)
                    
                    result_text = response
                    processed_data = self._parse_llm_response(result_text)
                    print(f"✅ Fallback successful for {place_name}")
                    return processed_data
                    
                except Exception as fallback_error:
                    print(f"❌ Fallback also failed for {place_name}: {fallback_error}")
            
            print(f"🔄 Using rule-based processing for {place_name} (free alternative)")
            result = self._get_default_processing(place_name, place_category)
            print(f"✅ Rule-based result for {place_name}: {result}")
            return result
    
    def _create_processing_prompt(self, place_name: str, place_category: str, reviews: str) -> str:
        """Create the prompt for LLM processing"""
        return f"""
You are a helpful assistant that analyzes reviews to extract vibe information about places.

Analyze the following reviews for {place_name} (a {place_category}) and extract:

1. A concise summary (2-3 sentences) of the overall vibe and experience
2. 3-5 vibe tags that describe the atmosphere (e.g., "cozy", "aesthetic", "vibrant", "quiet", "romantic")
3. 2-3 relevant emojis that represent the place

Reviews:
{reviews[:2000]}  # Limit to avoid token limits

Please respond in this exact JSON format:
{{
    "summary": "Brief summary of the place's vibe and experience",
    "vibe_tags": ["tag1", "tag2", "tag3"],
    "emojis": ["emoji1", "emoji2"]
}}

Only return the JSON, no additional text.
"""
    
    def _parse_llm_response(self, response_text: str) -> Dict:
        """Parse the LLM response into structured data"""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                print(f"🔍 Extracted JSON: {json_str}")
                data = json.loads(json_str)
                
                result = {
                    "summary": data.get("summary", ""),
                    "vibe_tags": data.get("vibe_tags", []),
                    "emojis": data.get("emojis", [])
                }
                print(f"✅ Parsed successfully: {result}")
                return result
            else:
                print(f"❌ No JSON found in response: {response_text}")
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"❌ Error parsing LLM response: {e}")
            print(f"🔄 Falling back to rule-based processing...")
            return self._get_default_processing("", "")
    
    def _get_default_processing(self, place_name: str, place_category: str) -> Dict:
        """Return default processing when LLM fails - completely free alternative"""
        
        # Simple rule-based processing as free alternative
        name_lower = place_name.lower()
        category_lower = place_category.lower()
        
        # Generate vibe tags based on place name and category
        vibe_tags = []
        if any(word in name_lower for word in ['coffee', 'cafe', 'brew']):
            vibe_tags.extend(['cozy', 'caffeinated'])
        if any(word in name_lower for word in ['restaurant', 'dining', 'bistro']):
            vibe_tags.extend(['dining', 'culinary'])
        if any(word in name_lower for word in ['bar', 'pub', 'tavern']):
            vibe_tags.extend(['social', 'nightlife'])
        if any(word in name_lower for word in ['park', 'garden']):
            vibe_tags.extend(['outdoor', 'nature'])
        
        # Add category-based tags
        if category_lower == 'cafe':
            vibe_tags.extend(['cozy', 'caffeinated', 'social'])
        elif category_lower == 'restaurant':
            vibe_tags.extend(['dining', 'culinary', 'social', 'aesthetic'])
        elif category_lower == 'bar':
            vibe_tags.extend(['nightlife', 'social', 'vibrant'])
        else:
            vibe_tags.extend(['local', 'accessible'])
        
        # Generate emojis based on category
        emojis = []
        if category_lower == 'cafe':
            emojis = ['☕', '🪑']
        elif category_lower == 'restaurant':
            emojis = ['🍽️', '👨‍🍳']
        elif category_lower == 'bar':
            emojis = ['🍺', '🎉']
        else:
            emojis = ['📍', '🏪']
        
        # Generate simple summary
        summary = f"A {place_category} in the area. {place_name} offers a local experience with mixed reviews from visitors."
        
        return {
            "summary": summary,
            "vibe_tags": list(set(vibe_tags))[:5],  # Remove duplicates, limit to 5
            "emojis": emojis[:3]  # Limit to 3 emojis
        }
    
    def process_multiple_places(self, places_with_reviews: Dict[str, List[Dict]], city: str) -> Dict[str, Dict]:
        """
        Process multiple places with their reviews
        
        Args:
            places_with_reviews: Dictionary mapping place names to their reviews
            city: City where places are located
            
        Returns:
            Dictionary mapping place names to their processed data
        """
        results = {}
        
        for place_name, reviews in places_with_reviews.items():
            print(f"🧠 Processing LLM for: {place_name}")
            
            # Extract category from place name (this would ideally come from the place data)
            category = self._infer_category_from_name(place_name)
            
            processed_data = self.process_place_reviews(place_name, category, reviews)
            results[place_name] = processed_data
            
        return results
    
    def _infer_category_from_name(self, place_name: str) -> str:
        """Infer category from place name (basic implementation)"""
        name_lower = place_name.lower()
        
        if any(word in name_lower for word in ['cafe', 'coffee', 'brew']):
            return 'cafe'
        elif any(word in name_lower for word in ['restaurant', 'dining', 'bistro']):
            return 'restaurant'
        elif any(word in name_lower for word in ['bar', 'pub', 'tavern']):
            return 'bar'
        elif any(word in name_lower for word in ['park', 'garden']):
            return 'park'
        else:
            return 'place' 