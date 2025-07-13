import requests
import json
from typing import List, Dict, Optional

class TomTomService:
    def __init__(self, api_key: Optional[str] = None):
        # Set API key (can be passed in or set via environment variable)
        import os
        self.api_key = api_key or os.getenv("TOMTOM_API_KEY")
        self.base_url = "https://api.tomtom.com/search/2"
        self.headers = {
            "Accept": "application/json"
        }
    
    def set_api_key(self, api_key: str):
        """Set the TomTom API key"""
        self.api_key = api_key
    
    def search_places(self, query: str, location: str, limit: int = 50) -> Optional[List[Dict]]:
        """
        Search for places based on user query and location.
        
        Args:
            query: User search query (e.g., "cool cafes", "peaceful parks")
            location: Location to search in (e.g., "Delhi", "Mumbai")
            limit: Maximum number of results to return
            
        Returns:
            List of place data matching our schema
        """
       
        if not self.api_key:
            print("⚠️  No API key provided, using mock data")
            return self._get_mock_places(query, location, limit)
        
        try:
            # First, geocode the location to get coordinates
            location_coords = self._geocode_location(location)
            if not location_coords:
                print(f"Could not geocode location: {location}, using default coordinates")
                # Use default coordinates for Delhi
                location_coords = {"lat": 28.6139, "lon": 77.2090}
            
            # TomTom Places Search endpoint
            url = f"{self.base_url}/poiSearch/{query}.json"
            
            # API parameters
            params = {
                "key": self.api_key,
                "lat": location_coords['lat'],
                "lon": location_coords['lon'],
                "radius": 5000,  # 5km radius
                "limit": min(limit, 50),
                "idxSet": "POI"  # Points of Interest
            }
            
            # Debug: Print the request details
            print(f"Making request to: {url}")
            print(f"Headers: {self.headers}")
            print(f"Params: {params}")
            
            # Make API call
            response = requests.get(url, headers=self.headers, params=params)
            
            # Debug: Print response details
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            if response.status_code != 200:
                print(f"Response text: {response.text}")
                return self._get_mock_places(query, location, limit)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract and format places from TomTom response
            places = []
            if 'results' in data:
                for item in data['results']:
                    formatted_place = self._format_place_data(item)
                    if formatted_place:
                        # Get additional details for this place
                        place_id = item.get('id')
                        if place_id:
                            details = self._get_place_details(place_id)
                            if details:
                                        # Merge additional details
                                        formatted_place.update({
                                            "photo_url": details.get("photo_url", ""),
                                            "description": details.get("description", ""),
                                            "attributes": details.get("attributes", {})
                                    })
                        places.append(formatted_place)
            
            # If no places found, return mock data
            if not places:
                print("No places found from API, using mock data")
                return self._get_mock_places(query, location, limit)
            
            return places
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching places from TomTom API: {e}")
            return self._get_mock_places(query, location, limit)
        except Exception as e:
            print(f"Error processing TomTom response: {e}")
            return self._get_mock_places(query, location, limit)
    
    def _geocode_location(self, location: str) -> Optional[Dict]:
        """
        Geocode a location string to get coordinates using TomTom Geocoding API.
        """
        try:
            url = "https://api.tomtom.com/search/2/geocode"
            params = {
                "query": location,
                "key": self.api_key
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' in data and len(data['results']) > 0:
                position = data['results'][0]['position']
                return {
                    "lat": position['lat'],
                    "lon": position['lon']
                }
            
            return None
            
        except Exception as e:
            print(f"Error geocoding location: {e}")
            return None
    
    def _get_mock_places(self, query: str, location: str, limit: int) -> List[Dict]:
        """
        Generate mock place data for testing without API calls.
        """
        mock_places = []
        query_lower = query.lower()
        
        # Generate different mock data based on query
        if "cafe" in query_lower or "coffee" in query_lower:
            mock_places = [
                {
                    "fsq_id": f"tomtom_cafe_{i}",
                    "name": f"TomTom Coffee Shop {i}",
                    "category": "Coffee Shop",
                    "address": f"{100 + i} Main Street, {location}",
                    "locality": location,
                    "city": location,
                    "country": "India",
                    "photo_url": f"https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [77.2090 + (i * 0.01), 28.6139 + (i * 0.01)]
                    },
                    "attributes": {
                        "tomtom_id": f"tomtom_cafe_{i}",
                        "category": "cafe,coffee_shop",
                        "phone": f"+91-123456789{i}",
                        "website": f"https://tomtomcafe{i}.com",
                        "opening_hours": "9 AM - 10 PM"
                    },
                    "description": f"A cozy coffee shop with great atmosphere and delicious coffee. Perfect for working or relaxing with friends."
                }
                for i in range(1, min(limit + 1, 6))
            ]
        elif "restaurant" in query_lower or "food" in query_lower:
            # Comprehensive mock data for restaurants in Ahmedabad
            ahmedabad_restaurants = [
                {
                    "fsq_id": "ahm_rest_001",
                    "name": "Peshwari",
                    "category": "Restaurant",
                    "address": "15 CG Road, Navrangpura, Ahmedabad",
                    "locality": "Navrangpura",
                    "city": "Ahmedabad",
                    "country": "India",
                    "photo_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [72.5714, 23.0225]
                    },
                    "attributes": {
                        "tomtom_id": "ahm_rest_001",
                        "category": "restaurant,gujarati",
                        "phone": "+91-79-26401234",
                        "website": "https://gujarathouse.com",
                        "opening_hours": "11 AM - 11 PM"
                    },
                    "description": "Authentic Gujarati thali restaurant serving traditional dishes like dhokla, thepla, and kadhi."
                },
                {
                    "fsq_id": "ahm_rest_002",
                    "name": "Timpani Restaurant",
                    "category": "Restaurant",
                    "address": "Manek Chowk, Old City, Ahmedabad",
                    "locality": "Old City",
                    "city": "Ahmedabad",
                    "country": "India",
                    "photo_url": "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [72.5800, 23.0250]
                    },
                    "attributes": {
                        "tomtom_id": "ahm_rest_002",
                        "category": "restaurant,street_food",
                        "phone": "+91-79-25501234",
                        "website": "",
                        "opening_hours": "6 PM - 2 AM"
                    },
                    "description": "Famous street food destination with vendors serving pav bhaji, dahi puri, and other local delicacies."
                },
                {
                    "fsq_id": "ahm_rest_003",
                    "name": "Rajwadu",
                    "category": "Restaurant",
                    "address": "Vasna, Ahmedabad",
                    "locality": "Vasna",
                    "city": "Ahmedabad",
                    "country": "India",
                    "photo_url": "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [72.5600, 23.0100]
                    },
                    "attributes": {
                        "tomtom_id": "ahm_rest_003",
                        "category": "restaurant,traditional",
                        "phone": "+91-79-26601234",
                        "website": "https://vishalla.com",
                        "opening_hours": "7 PM - 11 PM"
                    },
                    "description": "Traditional Gujarati dining experience with earthen pots and village-style seating."
                },
                {
                    "fsq_id": "ahm_rest_004",
                    "name": "Agashiye",
                    "category": "Restaurant",
                    "address": "House of MG, Opp. Sidi Saiyed Mosque, Ahmedabad",
                    "locality": "Old City",
                    "city": "Ahmedabad",
                    "country": "India",
                    "photo_url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [72.5750, 23.0270]
                    },
                    "attributes": {
                        "tomtom_id": "ahm_rest_004",
                        "category": "restaurant,fine_dining",
                        "phone": "+91-79-25501234",
                        "website": "https://houseofmg.com/agashiye",
                        "opening_hours": "12 PM - 3 PM, 7 PM - 11 PM"
                    },
                    "description": "Rooftop restaurant offering traditional Gujarati cuisine with a modern twist."
                },
                {
                    "fsq_id": "ahm_rest_005",
                    "name": "Bayleaf",
                    "category": "Restaurant",
                    "address": "Satellite, Ahmedabad",
                    "locality": "Satellite",
                    "city": "Ahmedabad",
                    "country": "India",
                    "photo_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [72.5900, 23.0300]
                    },
                    "attributes": {
                        "tomtom_id": "ahm_rest_005",
                        "category": "restaurant,thali",
                        "phone": "+91-79-26701234",
                        "website": "https://gordhanthal.com",
                        "opening_hours": "11 AM - 11 PM"
                    },
                    "description": "Popular thali restaurant known for unlimited Gujarati thali with variety of dishes."
                },
                {
                    "fsq_id": "ahm_rest_006",
                    "name": "Rajwadu",
                    "category": "Restaurant",
                    "address": "Sarkhej-Gandhinagar Highway, Ahmedabad",
                    "locality": "Sarkhej",
                    "city": "Ahmedabad",
                    "country": "India",
                    "photo_url": "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [72.5000, 23.0000]
                    },
                    "attributes": {
                        "tomtom_id": "ahm_rest_006",
                        "category": "restaurant,traditional",
                        "phone": "+91-79-26801234",
                        "website": "https://rajwadu.com",
                        "opening_hours": "12 PM - 4 PM, 7 PM - 11 PM"
                    },
                    "description": "Traditional Rajasthani and Gujarati cuisine in a heritage setting with live folk music."
                },
                {
                    "fsq_id": "ahm_rest_007",
                    "name": "Swati Snacks",
                    "category": "Restaurant",
                    "address": "Law Garden, Ahmedabad",
                    "locality": "Law Garden",
                    "city": "Ahmedabad",
                    "country": "India",
                    "photo_url": "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [72.5850, 23.0200]
                    },
                    "attributes": {
                        "tomtom_id": "ahm_rest_007",
                        "category": "restaurant,snacks",
                        "phone": "+91-79-26901234",
                        "website": "https://swatisnacks.com",
                        "opening_hours": "8 AM - 11 PM"
                    },
                    "description": "Famous for Gujarati snacks like khandvi, dhokla, and handvo. Popular breakfast spot."
                },
                {
                    "fsq_id": "ahm_rest_008",
                    "name": "Toran Dining Hall",
                    "category": "Restaurant",
                    "address": "CG Road, Ahmedabad",
                    "locality": "Navrangpura",
                    "city": "Ahmedabad",
                    "country": "India",
                    "photo_url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [72.5720, 23.0230]
                    },
                    "attributes": {
                        "tomtom_id": "ahm_rest_008",
                        "category": "restaurant,vegetarian",
                        "phone": "+91-79-27001234",
                        "website": "https://torandining.com",
                        "opening_hours": "11 AM - 11 PM"
                    },
                    "description": "Pure vegetarian restaurant serving traditional Gujarati and North Indian cuisine."
                },
                {
                    "fsq_id": "ahm_rest_009",
                    "name": "Karnavati Club",
                    "category": "Restaurant",
                    "address": "Satellite, Ahmedabad",
                    "locality": "Satellite",
                    "city": "Ahmedabad",
                    "country": "India",
                    "photo_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [72.5950, 23.0350]
                    },
                    "attributes": {
                        "tomtom_id": "ahm_rest_009",
                        "category": "restaurant,club",
                        "phone": "+91-79-27101234",
                        "website": "https://karnavaticlub.com",
                        "opening_hours": "7 AM - 11 PM"
                    },
                    "description": "Exclusive club restaurant with multi-cuisine options and elegant dining experience."
                },
                {
                    "fsq_id": "ahm_rest_010",
                    "name": "Gopi Dining Hall",
                    "category": "Restaurant",
                    "address": "Lal Darwaja, Ahmedabad",
                    "locality": "Lal Darwaja",
                    "city": "Ahmedabad",
                    "country": "India",
                    "photo_url": "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [72.5800, 23.0250]
                    },
                    "attributes": {
                        "tomtom_id": "ahm_rest_010",
                        "category": "restaurant,traditional",
                        "phone": "+91-79-27201234",
                        "website": "",
                        "opening_hours": "11 AM - 11 PM"
                    },
                    "description": "Historic restaurant serving authentic Gujarati thali since 1960s."
                },
                {
                    "fsq_id": "ahm_rest_011",
                    "name": "Pakwan",
                    "category": "Restaurant",
                    "address": "Satellite, Ahmedabad",
                    "locality": "Satellite",
                    "city": "Ahmedabad",
                    "country": "India",
                    "photo_url": "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [72.6000, 23.0400]
                    },
                    "attributes": {
                        "tomtom_id": "ahm_rest_011",
                        "category": "restaurant,indian",
                        "phone": "+91-79-27301234",
                        "website": "https://pakwan.com",
                        "opening_hours": "11 AM - 11 PM"
                    },
                    "description": "Multi-cuisine restaurant known for North Indian and Mughlai dishes."
                },
                {
                    "fsq_id": "ahm_rest_012",
                    "name": "Sankalp",
                    "category": "Restaurant",
                    "address": "CG Road, Ahmedabad",
                    "locality": "Navrangpura",
                    "city": "Ahmedabad",
                    "country": "India",
                    "photo_url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [72.5740, 23.0240]
                    },
                    "attributes": {
                        "tomtom_id": "ahm_rest_012",
                        "category": "restaurant,south_indian",
                        "phone": "+91-79-27401234",
                        "website": "https://sankalp.com",
                        "opening_hours": "7 AM - 11 PM"
                    },
                    "description": "Famous South Indian restaurant serving dosas, idlis, and other South Indian delicacies."
                },
                {
                    "fsq_id": "ahm_rest_013",
                    "name": "Honest",
                    "category": "Restaurant",
                    "address": "Satellite, Ahmedabad",
                    "locality": "Satellite",
                    "city": "Ahmedabad",
                    "country": "India",
                    "photo_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [72.6050, 23.0450]
                    },
                    "attributes": {
                        "tomtom_id": "ahm_rest_013",
                        "category": "restaurant,fast_food",
                        "phone": "+91-79-27501234",
                        "website": "https://honest.com",
                        "opening_hours": "8 AM - 12 AM"
                    },
                    "description": "Popular fast food chain known for pav bhaji, vada pav, and other street food items."
                },
                {
                    "fsq_id": "ahm_rest_014",
                    "name": "Karnavati Dabeli",
                    "category": "Restaurant",
                    "address": "Law Garden, Ahmedabad",
                    "locality": "Law Garden",
                    "city": "Ahmedabad",
                    "country": "India",
                    "photo_url": "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [72.5870, 23.0210]
                    },
                    "attributes": {
                        "tomtom_id": "ahm_rest_014",
                        "category": "restaurant,street_food",
                        "phone": "+91-79-27601234",
                        "website": "",
                        "opening_hours": "4 PM - 11 PM"
                    },
                    "description": "Famous for authentic Kutch dabeli, a popular Gujarati street food."
                },
                {
                    "fsq_id": "ahm_rest_015",
                    "name": "Gujarat High Court Canteen",
                    "category": "Restaurant",
                    "address": "High Court, Ahmedabad",
                    "locality": "High Court",
                    "city": "Ahmedabad",
                    "country": "India",
                    "photo_url": "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [72.5700, 23.0260]
                    },
                    "attributes": {
                        "tomtom_id": "ahm_rest_015",
                        "category": "restaurant,canteen",
                        "phone": "+91-79-27701234",
                        "website": "",
                        "opening_hours": "9 AM - 5 PM"
                    },
                    "description": "Historic canteen serving simple Gujarati meals to lawyers and visitors."
                }
            ]
            
            # Return restaurants based on location and limit
            if "ahmedabad" in location.lower() or "ahm" in location.lower():
                return ahmedabad_restaurants[:min(limit, len(ahmedabad_restaurants))]
            else:
                # For other locations, use generic restaurant data
                mock_places = [
                    {
                        "fsq_id": f"tomtom_restaurant_{i}",
                        "name": f"TomTom Restaurant {i}",
                        "category": "Restaurant",
                        "address": f"{200 + i} Food Street, {location}",
                        "locality": location,
                        "city": location,
                        "country": "India",
                        "photo_url": f"https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&h=300&fit=crop",
                        "coordinates": {
                            "type": "Point",
                            "coordinates": [77.2090 + (i * 0.01), 28.6139 + (i * 0.01)]
                        },
                        "attributes": {
                            "tomtom_id": f"tomtom_restaurant_{i}",
                            "category": "restaurant,food",
                            "phone": f"+91-987654321{i}",
                            "website": f"https://tomtomrestaurant{i}.com",
                            "opening_hours": "11 AM - 11 PM"
                        },
                        "description": f"Authentic local cuisine with a modern twist. Known for their signature dishes and warm hospitality."
                    }
                    for i in range(1, min(limit + 1, 6))
                ]
                return mock_places
        elif "park" in query_lower:
            mock_places = [
                {
                    "fsq_id": f"tomtom_park_{i}",
                    "name": f"TomTom Park {i}",
                    "category": "Park",
                    "address": f"{300 + i} Park Road, {location}",
                    "locality": location,
                    "city": location,
                    "country": "India",
                    "photo_url": f"https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [77.2090 + (i * 0.01), 28.6139 + (i * 0.01)]
                    },
                    "attributes": {
                        "tomtom_id": f"tomtom_park_{i}",
                        "category": "park,leisure",
                        "phone": "",
                        "website": "",
                        "opening_hours": "6 AM - 8 PM"
                    },
                    "description": f"A beautiful green space perfect for morning walks, evening strolls, and family picnics. Features walking trails and children's play area."
                }
                for i in range(1, min(limit + 1, 6))
            ]
        else:
            # Generic places
            mock_places = [
                {
                    "fsq_id": f"tomtom_place_{i}",
                    "name": f"TomTom Place {i}",
                    "category": "General",
                    "address": f"{400 + i} Generic Street, {location}",
                    "locality": location,
                    "city": location,
                    "country": "India",
                    "photo_url": f"https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&h=300&fit=crop",
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [77.2090 + (i * 0.01), 28.6139 + (i * 0.01)]
                    },
                    "attributes": {
                        "tomtom_id": f"tomtom_place_{i}",
                        "category": "amenity,general",
                        "phone": f"+91-555555555{i}",
                        "website": f"https://tomtomplace{i}.com",
                        "opening_hours": "10 AM - 6 PM"
                    },
                    "description": f"A wonderful place to visit with something for everyone. Popular among locals and tourists alike."
                }
                for i in range(1, min(limit + 1, 6))
            ]
        
        return mock_places
    
    def _format_place_data(self, item: Dict) -> Optional[Dict]:
        """
        Format TomTom API response to match our schema.
        """
        try:
            position = item.get('position', {})
            address = item.get('address', {})
            
            return {
                "fsq_id": item.get("id", ""),  # Using TomTom ID as fsq_id for compatibility
                "name": item.get("poi", {}).get("name", ""),
                "category": item.get("poi", {}).get("categorySet", [{}])[0].get("name", "General"),
                "address": address.get("freeformAddress", ""),
                "locality": address.get("municipality", ""),
                "city": address.get("municipality", ""),
                "country": address.get("country", ""),
                "photo_url": "",  # Will be populated from details
                "coordinates": {
                    "type": "Point",
                    "coordinates": [
                        position.get("lon", 0),
                        position.get("lat", 0)
                    ]
                },
                "attributes": {
                    "tomtom_id": item.get("id", ""),
                    "category": item.get("poi", {}).get("categorySet", [{}])[0].get("id", ""),
                    "phone": item.get("poi", {}).get("phone", ""),
                    "website": item.get("poi", {}).get("url", ""),
                    "opening_hours": item.get("poi", {}).get("openingHours", {}).get("text", "")
                },
                "description": item.get("poi", {}).get("description", ""),
            }
        except Exception as e:
            print(f"Error formatting place data: {e}")
            return None
    
    def _get_place_details(self, place_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific place.
        """
        try:
            # TomTom Place Details endpoint
            url = f"{self.base_url}/poiDetails/{place_id}.json"
            
            params = {
                "key": self.api_key
            }
            
            # Make API call
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Format the detailed place data
            return self._format_detailed_place_data(data)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching place details from TomTom API: {e}")
            return None
        except Exception as e:
            print(f"Error processing place details: {e}")
            return None
    
    def _format_detailed_place_data(self, data: Dict) -> Optional[Dict]:
        """
        Format detailed TomTom API response to match our schema.
        """
        try:
            poi = data.get('poi', {})
            address = data.get('address', {})
            position = data.get('position', {})
            
            return {
                "fsq_id": data.get("id", ""),
                "name": poi.get("name", ""),
                "category": poi.get("categorySet", [{}])[0].get("name", "General"),
                "address": address.get("freeformAddress", ""),
                "locality": address.get("municipality", ""),
                "city": address.get("municipality", ""),
                "country": address.get("country", ""),
                "photo_url": "",  # TomTom doesn't provide photos in basic API
                "coordinates": {
                    "type": "Point",
                    "coordinates": [
                        position.get("lon", 0),
                        position.get("lat", 0)
                    ]
                },
                "description": poi.get("description", ""),
                "attributes": {
                    "tomtom_id": data.get("id", ""),
                    "category": poi.get("categorySet", [{}])[0].get("id", ""),
                    "phone": poi.get("phone", ""),
                    "website": poi.get("url", ""),
                    "opening_hours": poi.get("openingHours", {}).get("text", ""),
                    "email": poi.get("email", "")
                },
                "hours": poi.get("openingHours", {}).get("text", ""),
                "phone": poi.get("phone", ""),
                "website": poi.get("url", ""),
                "price": "",
                "rating": 0,
                "tips": []
            }
        except Exception as e:
            print(f"Error formatting detailed place data: {e}")
            return None
    
    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific place.
        """
        # Check if API key is available
        if not self.api_key:
            print("⚠️  No API key provided, using mock data")
            return self._get_mock_place_details(place_id)
        
        try:
            return self._get_place_details(place_id)
        except Exception as e:
            print(f"Error getting place details: {e}")
            return self._get_mock_place_details(place_id)
    
    def _get_mock_place_details(self, place_id: str) -> Dict:
        """
        Generate mock detailed place data for testing.
        """
        return {
            "fsq_id": place_id,
            "name": f"TomTom Detailed Place {place_id}",
            "category": "General",
            "address": "123 TomTom Street, Test City",
            "locality": "Test City",
            "city": "Test City",
            "country": "India",
            "photo_url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&h=300&fit=crop",
            "coordinates": {
                "type": "Point",
                "coordinates": [77.2090, 28.6139]
            },
            "description": "A wonderful TomTom place with great atmosphere and excellent service. Highly recommended by visitors.",
            "attributes": {
                "tomtom_id": place_id,
                "category": "amenity,general",
                "phone": "+91-1234567890",
                "website": "https://tomtom.com",
                "opening_hours": "9 AM - 10 PM",
                "email": "info@tomtom.com"
            },
            "hours": "9 AM - 10 PM",
            "phone": "+91-1234567890",
            "website": "https://tomtom.com",
            "price": "",
            "rating": 4.5,
            "tips": [
                "Great atmosphere!",
                "Highly recommended",
                "Best in the area"
            ]
        } 