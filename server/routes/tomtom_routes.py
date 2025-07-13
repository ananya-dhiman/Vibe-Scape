from flask import Blueprint, request, jsonify, current_app
from services.tomtom_service import TomTomService
from controllers.place_controller import bulk_insert_places
import os

# Create Blueprint
tomtom_bp = Blueprint('tomtom', __name__)

# Initialize TomTom service
tomtom_service = TomTomService()

@tomtom_bp.route('/search', methods=['GET'])
def search_places():
    """
    Search for places using TomTom API
    """
    try:
        # Get query parameters
        query = request.args.get('query', '')
        location = request.args.get('location', '')
        limit = int(request.args.get('limit', 10))
        
        # Validate required parameters
        if not query or not location:
            return jsonify({
                'error': 'Missing required parameters: query and location'
            }), 400
        
        # Search for places
        places = tomtom_service.search_places(query, location, limit)
        
        if places is None:
            return jsonify({
                'error': 'Failed to search places'
            }), 500
        
        return jsonify({
            'success': True,
            'places': places,
            'count': len(places),
            'query': query,
            'location': location
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@tomtom_bp.route('/search-and-store', methods=['POST'])
def search_and_store_places():
    """
    Search for places using TomTom API and store them in the database
    """
    try:
        # Get request data
        data = request.get_json()
        query = data.get('query', '')
        location = data.get('location', '')
        limit = int(data.get('limit', 10))
        
        # Validate required parameters
        if not query or not location:
            return jsonify({
                'error': 'Missing required parameters: query and location'
            }), 400
        
        # Search for places from TomTom
        tomtom_places = tomtom_service.search_places(query, location, limit)
        
        if tomtom_places is None:
            return jsonify({
                'error': 'Failed to search places from TomTom'
            }), 500
        
        # Transform TomTom data to match our database schema
        places_to_insert = []
        for place in tomtom_places:
            # Map TomTom data to our schema, leaving processed and akl fields empty
            place_doc = {
                "original": {
                    "fsq_id": place.get("fsq_id", ""),  # Using TomTom ID as fsq_id
                    "name": place.get("name", ""),
                    "category": place.get("category", ""),
                    "address": place.get("address", ""),
                    "locality": place.get("locality", ""),
                    "city": place.get("city", ""),
                    "country": place.get("country", ""),
                    "photo_url": place.get("photo_url", ""),
                    "coordinates": place.get("coordinates", {})
                },
                "processed": {
                    "vibe_tags": [],  # Empty - will be filled later
                    "emojis": [],     # Empty - will be filled later
                    "summary": "",    # Empty - will be filled later
                    "citations": []   # Empty - will be filled later
                },
                "reviews": [],  # Empty - will be filled later
                # created_at and updated_at will be set by the controller
            }
            places_to_insert.append(place_doc)
        
        # Use bulk insert to store places in database
        inserted_ids = bulk_insert_places(current_app.mongo, places_to_insert)
        
        return jsonify({
            'success': True,
            'message': f'Successfully stored {len(inserted_ids)} places in database',
            'inserted_count': len(inserted_ids),
            'inserted_ids': inserted_ids,
            'total_found': len(tomtom_places),
            'query': query,
            'location': location
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@tomtom_bp.route('/details/<place_id>', methods=['GET'])
def get_place_details(place_id):
    """
    Get detailed information about a specific place
    """
    try:
        # Get place details
        details = tomtom_service.get_place_details(place_id)
        
        if details is None:
            return jsonify({
                'error': 'Place not found or failed to get details'
            }), 404
        
        return jsonify({
            'success': True,
            'place': details
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@tomtom_bp.route('/test', methods=['GET'])
def test_service():
    """
    Test endpoint to verify TomTom service is working
    """
    try:
        # Test with mock data
        places = tomtom_service.search_places("coffee", "Delhi", 3)
        
        if places:
            return jsonify({
                'success': True,
                'message': 'TomTom service is working!',
                'sample_places': places[:2],  # Return first 2 places as sample
                'total_found': len(places)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'TomTom service returned no results'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'TomTom service error: {str(e)}'
        }), 500 